"""语音转文字（STT）后端实现。

支持的识别方式：
1. faster-whisper（本地 CPU/GPU 推理，无需 Ollama）
2. 预留给云端 STT 的扩展点

核心逻辑：
- 接收音频字节流（webm/wav/mp3 等浏览器录制格式）
- 使用 faster-whisper 本地模型转录
- 返回识别文本

依赖：
- pip install faster-whisper
- 首次使用会自动下载模型（默认 base 模型约 140MB）

优化历程：
- 第1轮：segfault 修复 + VAD + 中文强制 + 防幻觉
- 第2轮：beam_size + best_of + repetition_penalty + 温度调度
- 第3轮：cpu_threads 物理核心优化 + OMP_NUM_THREADS + 音频预处理
- 第4轮修复：hallucination_silence_threshold + suppress_blank + no_speech_threshold 0.8
  + hotwords 独立参数 + speech_pad_ms 400 + max_initial_timestamp
- 第5轮修复：移除 hotwords（base 模型下污染输出）+ no_speech_threshold 回调 0.6
  + speech_pad_ms 回调 200 + initial_prompt 改为短词表软引导
  + 保留 hallucination_silence_threshold/suppress_blank/suppress_tokens/max_initial_timestamp
- 第6轮修复：后处理幻觉过滤层（业界三层防御的第三层）
  基于搜索到的业界实践实现：
  - scribe-transcribe 的 HALLUCINATION_PATTERNS 正则列表 + TAIL_WINDOW 尾部扫描
  - Hermes 的 WHISPER_HALLUCINATIONS 精确匹配集合 + 重复模式正则
  - Vexa 的135短语黑名单（英语循环幻觉）
  - arXiv:2501.11378 学术统计（thank you 24.76%、thanks for watching 10.32%）
  - Whisper 幻觉根因：YouTube 训练数据导致"静音=片尾语"映射
- 第7轮修复：误伤防护 + 强幻觉短语分级
  审核发现：黑名单中"谢谢""感谢""音乐"等 2-3 字短词若参与尾部截断，
  会误伤"非常感谢你的帮助""这段音乐很好听"等正常文本。
  修复：普通短词仅做整段精确匹配；新增 _HALLUCINATION_STRONG_ZH 强幻觉集合
  （"请订阅""请点赞"等请求式结束语，正常正文几乎不会以这些结尾），
  即使 2-3 字也始终参与尾部截断，兼顾误伤防护与幻觉拦截。
"""
import logging
import multiprocessing
import os
import re
import tempfile
import threading
from typing import BinaryIO

# 第1轮修复：ctranslate2 在 Windows 上模型加载阶段会 segfault (Exit Code 139)
# 根因：CUDA allocator 在模型清理时触发 native crash
# 解决：设置 CT2_CUDA_ALLOCATOR=cub_caching 避免崩溃（issue #71 workaround）
# 必须在 import ctranslate2/faster_whisper 之前设置
if "CT2_CUDA_ALLOCATOR" not in os.environ:
    os.environ["CT2_CUDA_ALLOCATOR"] = "cub_caching"

# 第3轮优化：OpenMP 线程数匹配物理核心数
# 搜索发现：CTranslate2 默认 cpu_threads=0 时使用4线程，不自动适配硬件
# 超线程反而降低性能，应使用物理核心数 (cpu_count // 2)
if "OMP_NUM_THREADS" not in os.environ:
    _physical_cores = max(1, multiprocessing.cpu_count() // 2)
    os.environ["OMP_NUM_THREADS"] = str(_physical_cores)

from ...config import Settings

logger = logging.getLogger(__name__)

# ── 延迟加载模型单例 ──
_whisper_model = None
_whisper_model_name: str | None = None
# 模型加载锁：两个并发首请求同时满足 _whisper_model is None 时，
# 各自加载会重复加载 140MB+ 模型（内存翻倍、旧句柄泄漏）。
# STT 解码跑在 executor 线程，这里用普通线程锁即可。
_whisper_lock = threading.Lock()


def _get_whisper_model(model_name: str, model_path_override: str = ""):
    """延迟加载 faster-whisper 模型（单例缓存，线程安全）。

    Args:
        model_name: 模型大小名（tiny/base/small/medium/large-v3）
        model_path_override: 本地模型目录路径（优先于 model_name）

    Returns:
        faster_whisper.WhisperModel 实例
    """
    global _whisper_model, _whisper_model_name  # noqa: PLW0603

    cache_key = model_path_override or model_name
    if _whisper_model is not None and _whisper_model_name == cache_key:
        return _whisper_model

    with _whisper_lock:
        # 双检：等锁期间可能已被其它线程加载
        if _whisper_model is not None and _whisper_model_name == cache_key:
            return _whisper_model
        try:
            from faster_whisper import WhisperModel
        except ImportError as e:
            raise RuntimeError(
                "faster-whisper 未安装，请执行: pip install faster-whisper"
            ) from e

        # 模型路径解析：
        # - 优先用 model_path_override（本地路径，避免 HuggingFace 下载问题）
        # - 如果 model_name 本身就是有效目录路径，直接使用
        # - 否则回退到 faster-whisper 内置下载逻辑（需要网络）
        if model_path_override and os.path.isdir(model_path_override):
            model_path = model_path_override
        elif os.path.isdir(model_name):
            model_path = model_name
        else:
            model_path = model_name  # faster-whisper 内置下载

        logger.info("加载 faster-whisper 模型: %s (路径: %s)", model_name, model_path)
        # device="cpu" 兼容性最好；compute_type="int8" 减少内存占用
        # 第3轮优化：cpu_threads 设置为物理核心数
        # 搜索发现：默认 cpu_threads=0 时 CTranslate2 使用4线程，不自动适配硬件
        # 测试数据：4核CPU下，4物理核心4.4s vs 1线程14.4s vs 8虚拟线程6.5s
        # 超线程反而降低性能，应使用物理核心数 (cpu_count // 2)
        _cpu_threads = max(1, multiprocessing.cpu_count() // 2)
        logger.info("STT CPU 线程数: %d (物理核心数)", _cpu_threads)
        _whisper_model = WhisperModel(
            model_path,
            device="cpu",
            compute_type="int8",
            num_workers=1,
            cpu_threads=_cpu_threads,
        )
        _whisper_model_name = cache_key
        return _whisper_model


# ──────────────────────────────────────────────────────────────────────
# 第6轮修复：后处理幻觉过滤层
# ──────────────────────────────────────────────────────────────────────
# 搜索发现的业界三层防御架构：
#   1. VAD 预过滤（第1轮已实现：Silero VAD）
#   2. 推理时参数抑制（第3-5轮已实现：condition_on_previous_text=False、
#      temperature=0.0、compression_ratio_threshold、log_prob_threshold、
#      no_speech_threshold、hallucination_silence_threshold）
#   3. 后处理模式匹配过滤（本层，第6轮实现）
#
# 幻觉根因（arXiv:2501.11378）：
#   Whisper 训练数据包含海量 YouTube 视频，结尾静音段配对"感谢观看"
#   "请订阅"等字幕文本，导致模型学到"低音频信息=输出片尾语"的映射。
#   学术统计：非语音幻觉输出频率最高的是"thank you"(24.76%)、
#   "thanks for watching"(10.32%)。
#
# 本实现综合以下开源项目经验：
# - scribe-transcribe：HALLUCINATION_PATTERNS 正则列表 + TAIL_WINDOW 尾部扫描
# - Hermes：WHISPER_HALLUCINATIONS 精确匹配集合 + 重复模式正则
# - Vexa：135个英语循环幻觉短语黑名单
# - claudelab.net：no_speech_prob + avg_logprob 双信号检测法（已在推理层使用）
# ──────────────────────────────────────────────────────────────────────

# 中文常见幻觉短语（精确匹配，来自 scribe-transcribe + Hermes + 第4/5轮实测）
_HALLUCINATION_PHRASES_ZH = frozenset({
    # 字幕组署名类
    "字幕", "字幕组", "字幕制作", "字幕翻译", "字幕压制",
    "提供字幕", "字幕由", "翻译制作",
    # 结束语类（YouTube 片尾映射，arXiv:2501.11378 统计最高频）
    "谢谢观看", "感谢观看", "谢谢收听", "感谢收听",
    "订阅频道", "关注频道", "点赞订阅", "一键三连",
    "谢谢大家", "感谢大家", "谢谢", "感谢",
    "再见", "拜拜",
    # 第4/5轮实测残留的幻觉
    "我认识了这些东西", "认识了这些东西",
    "作词作曲", "作词", "作曲",
    # 其他常见中文幻觉
    "请勿转载", "未经允许", "版权所有",
    "音乐", "音效", "背景音乐",
    "掌声", "笑声", "欢呼声",
    "广告", "赞助", "推广",
})

# 强幻觉短语（第7轮审核新增）：请求式结束语，正常正文几乎不会以这些结尾，
# 因此即使只有 2-3 字也始终参与尾部截断（防止"你好谢谢观看请订阅"漏网）。
# 区别于普通黑名单中的"谢谢""感谢"等礼貌语——后者可能正常出现在正文尾部，
# 仅做整段精确匹配，避免误伤"非常感谢你的帮助"这类正常文本。
_HALLUCINATION_STRONG_ZH = frozenset({
    "请订阅", "请关注", "请点赞", "请分享",
    "欢迎订阅", "记得订阅", "记得点赞",
})

# 英文常见幻觉短语（来自 Vexa 135短语黑名单 + arXiv:2501.11378 高频统计）
_HALLUCINATION_PHRASES_EN = frozenset({
    # 高频（arXiv:2501.11378 统计 top-2）
    "thank you", "thanks for watching", "thanks", "thank",
    "thanks for listening", "thank you for watching",
    # YouTube 片尾语
    "please subscribe", "subscribe", "don't forget to subscribe",
    "like and subscribe", "hit subscribe", "subscribe for more",
    "please like", "please share", "leave a like",
    "smash that like button", "hit the bell",
    # 字幕署名
    "subtitles by", "subtitle", "subtitles",
    "transcribed by", "transcription by",
    "amara.org", "opensubtitles",
    # 环境标记
    "[music]", "[applause]", "[laughter]", "[noise]",
    "[sound]", "[audio]", "[background music]",
    "(music)", "(applause)", "(laughter)",
    "music", "applause", "laughter",
    # 循环短语（Vexa 黑名单高频）
    "you", "the", "and", "so", "the end", "bye",
    "okay", "ok", "yeah", "uh",
})

# 正则模式：字幕署名格式（scribe-transcribe HALLUCINATION_PATTERNS）
_RE_SUBTITLE_CREDIT_ZH = re.compile(
    r"字幕[:：]?\s*[\u4e00-\u9fa5\w]{0,20}"
    r"|字幕组[:：]?\s*[\u4e00-\u9fa5\w]{0,20}"
    r"|翻译[:：]\s*[\u4e00-\u9fa5\w]{0,20}"
    r"|压制[:：]\s*[\u4e00-\u9fa5\w]{0,20}"
)
_RE_SUBTITLE_CREDIT_EN = re.compile(
    r"(?i)subtitles?\s+by\s+[\w\s\.]{0,30}"
    r"|transcribed\s+by\s+[\w\s\.]{0,30}"
    r"|translation\s+by\s+[\w\s\.]{0,30}"
    r"|amara\.org"
)

# 正则模式：环境标记 [xxx] / 【xxx】 / (xxx) 包裹的非语音内容
_RE_ENVIRONMENT_TAG = re.compile(
    r"[\[【\(][\s\w]*(?:music|applause|laughter|noise|sound|audio|音乐|掌声|笑声|音效|背景音)[\s\w]*[\]】\)]",
    re.IGNORECASE,
)

# 正则模式：英文循环短语（Hermes 重复模式检测）
# 匹配 thank you/thanks/bye/ok/the end 等重复2次以上的模式
_RE_REPEAT_PATTERN_EN = re.compile(
    r"(?i)^(?:thank\s+you|thanks|bye|you|ok|the\s+end|so|yeah|\.)+$"
)

# 正则模式：单字符重复（如 "。。。""啊啊啊" 等3次以上无意义重复）
_RE_CHAR_REPEAT = re.compile(r"(.)\1{4,}")


def _filter_hallucinations(text: str) -> str:
    """后处理幻觉过滤层（第6轮修复核心）。

    基于业界三层防御架构的第三层：模式匹配过滤。
    在推理参数抑制之后，对最终文本做清洗。

    过滤策略（按优先级）：
    1. 精确匹配黑名单短语 → 整体清空或移除匹配部分
    2. 正则匹配字幕署名/环境标记 → 移除匹配部分
    3. 重复模式检测（英文循环短语/单字符重复）→ 整体清空
    4. 尾部幻觉扫描：只检查尾部，因为 Whisper 幻觉几乎总在尾部

    Args:
        text: faster-whisper 原始识别文本

    Returns:
        过滤后的文本（可能为空字符串，表示整段为幻觉）
    """
    if not text or not text.strip():
        return text

    original = text.strip()
    logger.debug("幻觉过滤输入: %s", original[:100])

    # ── 步骤1：整体精确匹配（整段就是幻觉）──
    # 场景：识别结果只有"谢谢观看""thank you"等纯幻觉
    lower = original.lower()
    if (
        original in _HALLUCINATION_PHRASES_ZH
        or original in _HALLUCINATION_STRONG_ZH
        or lower in _HALLUCINATION_PHRASES_EN
    ):
        logger.info("幻觉过滤：整段匹配黑名单，清空 ('%s')", original[:50])
        return ""

    if _RE_REPEAT_PATTERN_EN.match(original):
        logger.info("幻觉过滤：英文循环模式，清空 ('%s')", original[:50])
        return ""

    # ── 步骤2：移除文本中的幻觉片段（保留有效内容）──
    cleaned = original

    # 2a. 移除字幕署名
    cleaned = _RE_SUBTITLE_CREDIT_ZH.sub("", cleaned)
    cleaned = _RE_SUBTITLE_CREDIT_EN.sub("", cleaned)

    # 2b. 移除环境标记 [music]【音乐】等
    cleaned = _RE_ENVIRONMENT_TAG.sub("", cleaned)

    # 2c. 移除单字符重复（"。。。""啊啊啊啊啊"等）
    cleaned = _RE_CHAR_REPEAT.sub("", cleaned)

    # ── 步骤3：尾部幻觉扫描（TAIL_WINDOW 算法）──
    # scribe-transcribe 实践：Whisper 幻觉几乎总在尾部连续块中
    # 策略：扫描文本尾部，如果尾部子串匹配黑名单短语，则截断
    # 这里用简单实现：检查文本是否以黑名单短语结尾
    tail_cleaned = _strip_tail_hallucination(cleaned)
    if tail_cleaned != cleaned:
        logger.info("幻觉过滤：尾部截断 '%s' → '%s'", cleaned[:50], tail_cleaned[:50])
        cleaned = tail_cleaned

    # ── 步骤4：二次精确匹配（清理后可能变成纯幻觉）──
    # 注意：只 strip 空白，保留结尾标点（句号等是正常文本的一部分）
    cleaned = cleaned.strip(" \n\r\t")
    if not cleaned:
        return ""

    lower_cleaned = cleaned.lower()
    if (
        cleaned in _HALLUCINATION_PHRASES_ZH
        or cleaned in _HALLUCINATION_STRONG_ZH
        or lower_cleaned in _HALLUCINATION_PHRASES_EN
    ):
        logger.info("幻觉过滤：清理后整段匹配黑名单，清空 ('%s')", cleaned[:50])
        return ""

    if _RE_REPEAT_PATTERN_EN.match(cleaned):
        logger.info("幻觉过滤：清理后英文循环模式，清空 ('%s')", cleaned[:50])
        return ""

    logger.debug("幻觉过滤输出: %s", cleaned[:100])
    return cleaned


def _strip_tail_hallucination(text: str) -> str:
    """移除文本尾部的幻觉片段。

    扫描策略：从尾部向前逐字检查，如果文本以某个黑名单短语结尾，
    则移除该短语，继续检查新的尾部，直到尾部不再匹配任何黑名单。

    这样可以处理"有效文本+谢谢观看+请订阅"这种尾部连续幻觉。

    Args:
        text: 待检查的文本

    Returns:
        移除尾部幻觉后的文本
    """
    result = text
    max_iterations = 10  # 防止无限循环
    # 按长度降序排序，优先匹配最长短语（避免"认识了这些东西"先于
    # "我认识了这些东西"匹配导致残留"我"的子串问题）
    # 强幻觉短语（"请订阅""请点赞"等请求式结束语）即使 2-3 字也始终参与尾部截断，
    # 与普通短语合并后统一按长度降序匹配。
    zh_all = _HALLUCINATION_PHRASES_ZH | _HALLUCINATION_STRONG_ZH
    zh_phrases_sorted = sorted(zh_all, key=len, reverse=True)
    en_phrases_sorted = sorted(_HALLUCINATION_PHRASES_EN, key=len, reverse=True)
    # 只对长度 >= 4 的普通短语做尾部截断：
    # "谢谢""感谢""音乐"等 2-3 字短词可能正常出现在正文（如"非常感谢"、
    # "谢谢你的帮助"），作为尾部截断会误伤。短词仅用于整段精确匹配清空。
    zh_tail_phrases = [p for p in zh_phrases_sorted if len(p) >= 4 or p in _HALLUCINATION_STRONG_ZH]
    en_tail_phrases = [p for p in en_phrases_sorted if len(p) >= 4]
    for _ in range(max_iterations):
        stripped = result.rstrip(" ，。、！？.,!? \n\r\t")
        if not stripped:
            return ""

        # 整段恰好等于幻觉短语 → 直接清空
        # （如"谢谢观看"去除尾部标点后整段就是黑名单内容）
        if (
            stripped in _HALLUCINATION_PHRASES_ZH
            or stripped in _HALLUCINATION_STRONG_ZH
            or stripped.lower() in _HALLUCINATION_PHRASES_EN
        ):
            return ""

        removed = False

        # 检查中文短语结尾（最长优先，仅 >= 4 字）
        for phrase in zh_tail_phrases:
            if stripped.endswith(phrase) and len(stripped) > len(phrase):
                # 截断幻觉短语，并清理截断点残留的尾标点
                # （如"好的，分享就到这里，谢谢大家" → 截断后清理逗号）
                result = stripped[: -len(phrase)].rstrip(" ，、；：！？.,!?")
                removed = True
                break

        if removed:
            continue

        # 检查英文短语结尾（不区分大小写，最长优先，仅 >= 4 字符）
        lower_stripped = stripped.lower()
        for phrase in en_tail_phrases:
            if lower_stripped.endswith(phrase) and len(stripped) > len(phrase):
                result = stripped[: -len(phrase)].rstrip(" ，、；：！？.,!?")
                removed = True
                break

        if not removed:
            break

    return result


async def transcribe_audio(
    audio_data: BinaryIO,
    settings: Settings,
) -> str:
    """转录音频为文本。

    Args:
        audio_data: 音频字节流（支持 webm/wav/mp3/ogg 等浏览器录制格式）
        settings: 全局配置（用于获取 whisper_model 等）

    Returns:
        识别出的文本内容

    Raises:
        RuntimeError: STT 后端未启用或调用失败
    """
    if not settings.stt_backend_enabled:
        raise RuntimeError("STT 后端未启用，请设置 ROLEPLAY_STT_BACKEND_ENABLED=true")

    # faster-whisper 模型名（tiny/base/small/medium/large-v3）
    model_name = settings.whisper_model or "base"
    model_path_override = getattr(settings, "whisper_model_path", "") or ""

    try:
        model = _get_whisper_model(model_name, model_path_override)
    except RuntimeError:
        raise
    except Exception as e:
        logger.error("Whisper 模型加载失败: %s", e)
        raise RuntimeError(f"Whisper 模型加载失败: {e}") from e

    # faster-whisper 需要文件路径，写入临时文件
    audio_bytes = audio_data.read() if hasattr(audio_data, "read") else audio_data
    if isinstance(audio_bytes, str):
        audio_bytes = audio_bytes.encode()

    tmp_path = None
    try:
        # 写入临时文件
        fd, tmp_path = tempfile.mkstemp(suffix=".webm")
        os.write(fd, audio_bytes)
        os.close(fd)

        # 第5轮修复：基于第4轮测试结果（平均相似度仅69%，hotwords 污染输出）
        # ──────────────────────────────────────────────────────────────
        # 第4轮测试发现的严重问题：
        #
        # 问题1：hotwords 污染输出（最严重）
        #   现象：测试1原文"你好，这是第四轮修复..."，识别尾部却出现"语音 识别 合成 转录"，
        #         这正是 hotwords 参数的内容！测试2/3/4 同样受污染。
        #   根因：base 模型（142MB）的 hotwords 实现有缺陷，热词会直接注入到解码输出，
        #         而非仅作为概率偏置。CSDN 文档指出"含非ASCII字符时总字符数≤15"，
        #         我的热词已超 15 字符限制，触发异常行为。
        #   搜索发现：theneuralbase 文档说 hotwords 是"decoding bias not search instruction"，
        #         但在 base+int8+cpu 组合下，这个软偏置会变成硬输出。
        #   修复：彻底移除 hotwords 参数。base 模型太小，hotwords 弊大于利。
        #         专有名词识别改用 initial_prompt 软引导（短词表 < 50 字符）。
        #
        # 问题2：no_speech_threshold=0.8 过于激进
        #   现象：测试4"静音段不应产生任何幻觉文本"识别为"进阴段 不影产生任何换绝文本"，
        #         整句被严重误识别，相似度仅47.1%。
        #   根因：no_speech_threshold=0.8 导致模型在低信噪比段落过度自信地乱猜，
        #         因为阈值过高意味着"即使 no_speech_prob 达到 0.7 也强行输出文本"。
        #   修复：回调到 0.6（官方默认值），在静音拒绝和误识别之间取平衡。
        #
        # 问题3：speech_pad_ms=400 过长（次要）
        #   现象：可能导致段间内容重叠，尾部出现拼凑感。
        #   修复：回调到 200（第3轮值），200 是 Silero VAD 社区主流推荐。
        #
        # 保留有效的第4轮参数：
        #   - hallucination_silence_threshold=2.0（官方反幻觉，第4轮验证有效）
        #   - suppress_blank=True + suppress_tokens=[-1]（抑制噪音 token）
        #   - max_initial_timestamp=1.0（限制前导静音误读）
        #   - condition_on_previous_text=False（防重复循环）
        import asyncio

        # 第5轮：initial_prompt 改为短词表软引导（< 50 字符，base 模型适用）
        # 搜索发现：theneuralbase 文档建议 "5-50 critical domain terms"，且
        # "Use larger models (medium/large) for initial_prompt to be effective; on 'tiny' the bias effect is minimal"
        # base 模型介于 tiny 和 small 之间，initial_prompt 仍有一定效果但不宜过长。
        # 只放最关键的领域术语，避免引导偏差。
        enhanced_prompt = "以下是普通话简体中文的语音转写。迭代，语音识别，语音合成。"
        # 第5轮：移除 hotwords 参数（base 模型下污染输出）

        # 转录 + 拼接整体放进 executor：faster-whisper 的 transcribe() 返回 generator，
        # 真正的 CPU 密集解码发生在迭代 segments 时；若把 "".join 放事件循环线程，
        # 并发 STT 会阻塞整个服务。因此 lambda 内完成全部工作，只返回最终文本。
        def _transcribe_and_join() -> str:
            segments, _info = model.transcribe(
                tmp_path,
                language="zh",
                beam_size=5,
                best_of=3,
                patience=1,
                repetition_penalty=1.1,
                no_repeat_ngram_size=2,
                temperature=0.0,
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                    speech_pad_ms=200,  # 第5轮：400→200，避免段间重叠
                    max_speech_duration_s=20,
                    threshold=0.5,
                ),
                condition_on_previous_text=False,
                word_timestamps=True,
                suppress_blank=True,
                suppress_tokens=[-1],
                max_initial_timestamp=1.0,
                no_speech_threshold=0.6,  # 第5轮：0.8→0.6，避免低信噪比下乱猜
                compression_ratio_threshold=2.4,
                log_prob_threshold=-1.0,
                hallucination_silence_threshold=2.0,
                initial_prompt=enhanced_prompt,
                # 第5轮：移除 hotwords（base 模型下污染输出）
            )
            return "".join(seg.text for seg in segments).strip()

        text = await asyncio.get_running_loop().run_in_executor(None, _transcribe_and_join)
        logger.info("STT 识别结果(过滤前): %s", text[:80] if text else "(空)")

        # 第6轮修复：后处理幻觉过滤
        # 基于业界三层防御架构的第三层，在推理参数抑制之后做模式匹配过滤
        # 综合来源：scribe-transcribe HALLUCINATION_PATTERNS + Hermes 集合 + Vexa 黑名单
        text = _filter_hallucinations(text)
        logger.info("STT 识别结果(过滤后): %s", text[:80] if text else "(空)")
        return text

    except Exception as e:
        logger.error("STT 转录异常: %s", e)
        raise RuntimeError(f"STT 转录异常: {e}") from e
    finally:
        # 清理临时文件
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
