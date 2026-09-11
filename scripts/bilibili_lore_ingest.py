# -*- coding: utf-8 -*-
"""B站视频文案 → 角色知识库（逐视频串行处理，防止爆内存）。

每个视频严格按「下载 → 转写 → 清洗 → 入库 → 删临时文件」一条龙处理完，
才轮到下一个视频：
  1. 抓视频页 HTML，解析 __INITIAL_STATE__（标题/UP主/cid/时长）与
     __playinfo__（纯音频流地址）；
  2. 带 --cookies 登录态时优先拉 B站 CC/AI 字幕（零转写成本），
     否则回退 faster-whisper 本地转写；
  3. 清洗转写文本（去幻觉行/重复行），落盘 data/lore/<角色>/视频文案/；
  4. ingest_file 入库 lore_<角色> 命名空间（doc_id=BV号，重跑先删旧块，幂等）；
  5. 删除临时音频/wav，再处理下一个。

内存控制要点：
  - 只下音频轨（不下载视频画面），单个长视频约几十 MB；
  - whisper 模型进程内只加载一次、常驻复用（峰值内存恒定）；
  - faster-whisper 流式产出分段，不整段载入内存；
  - 每个视频的临时文件用完即删，串行处理绝不并发。

用法（项目根目录执行）：
  python scripts/bilibili_lore_ingest.py --character wu_ming_zhe        # 内置1999清单
  python scripts/bilibili_lore_ingest.py --bvs BV1xxx BV1yyy            # 指定视频
  python scripts/bilibili_lore_ingest.py --list                         # 只看清单元数据
  python scripts/bilibili_lore_ingest.py --cookies cookies.txt          # 带登录态优先取CC字幕
"""
from __future__ import annotations

import argparse
import gc
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "voice_pipeline"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge import (  # noqa: E402
    CharacterStore,
    build_knowledge_base,
    ingest_file,
    lore_namespace,
)

# 复用既有语音管线的音频滤波 / 断句 / 质量打标逻辑
from transcribe_whole import build_af, extract_wav, flag_quality, split_sentences  # noqa: E402

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# 内置清单：与《重返未来：1999》世界观/剧情/阵营/主角团强相关的高密度解说视频
DEFAULT_BVS = [
    "BV1m6421M7bU",  # 荟小荟：一个视频带你看懂重返未来1999（世界观+剧情脉络）
    "BV196ReBxEq9",  # 薯条小叔叔：万字解析，一口气串联1.0-3.x全主线
    "BV1iT421D7S8",  # 银发三千雪满头：一年来1999讲了一个怎样的故事
    "BV1ZT411V72Q",  # 快速了解世界观及专业名词
    "BV1nyUxBFEpU",  # 了解你的重返未来阵营及纲领
    "BV1CaM36bEax",  # 超清晰的暴雨时间线及主要事件大梳理
    "BV1aX4y117Ph",  # 五种神秘学家诞生·血统解析
    "BV12u5M6uEm3",  # 官方PV：无名者「无名无我」
]

TMP_DIR = ROOT / "data" / "lore" / "_bilibili_tmp"
JAR_PATH = TMP_DIR / "bili_cookies.txt"

# whisper 中文常见幻觉/水印行，入库前剔除
HALLUCINATION_PAT = re.compile(
    r"字幕(由|by|组)|请不吝点赞|订阅|转发|打赏|谢谢观看|谢谢收看|明镜|点点栏目"
    r"|下期再见|See you next|Thanks for watching|Subscribe"
)


class BiliHttp:
    """B站 HTTP 客户端：subprocess 调 curl。

    为什么不用 urllib/requests：B站 WAF 会按 TLS 指纹拦 Python 客户端
    （页码 200 但返回风控页 / API 直接 412），curl 的指纹可正常通过；
    同时用 curl 原生 cookie jar 维持 buvid3 登录态。
    """

    def __init__(self, cookie_file: str | None = None, timeout: int = 30):
        self.exe = shutil.which("curl")
        if not self.exe:
            raise RuntimeError("找不到 curl，请确认 PATH 中有 curl.exe")
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        if cookie_file:
            _merge_cookie_file(cookie_file)  # 用户登录态并入 jar（Netscape 格式）
        elif not JAR_PATH.exists():
            JAR_PATH.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
        self.timeout = timeout

    def get(self, url: str, retries: int = 3, out: Path | None = None,
            timeout: int | None = None) -> str | None:
        """GET：out 给定时流式落盘（下载音频），否则返回响应文本。"""
        to = str(timeout or self.timeout)
        last: Exception | None = None
        for i in range(retries):
            cmd = [self.exe, "-sS", "--compressed", "-m", to,
                   "-b", str(JAR_PATH), "-c", str(JAR_PATH),
                   "-A", UA,
                   "-H", "Referer: https://www.bilibili.com/",
                   "-H", "Accept-Language: zh-CN,zh;q=0.9",
                   "-L", url] + (["-o", str(out)] if out else [])
            p = subprocess.run(cmd, capture_output=not out, text=True,
                               encoding="utf-8", errors="replace")
            if p.returncode == 0 and (out is None or Path(out).stat().st_size > 0):
                return p.stdout if out is None else None
            last = RuntimeError(f"curl rc={p.returncode} {p.stderr[-200:] if p.stderr else ''}")
            time.sleep(2 * (i + 1))
        raise RuntimeError(f"GET 失败 {url}: {last}")

    def get_json(self, url: str, retries: int = 3) -> dict:
        return json.loads(self.get(url, retries=retries))


def _merge_cookie_file(user_file: str) -> None:
    """把用户导出的 Netscape cookie（如含 SESSDATA 的登录态）并进工作 jar。"""
    src = Path(user_file)
    if not src.is_file():
        raise FileNotFoundError(f"cookie 文件不存在：{src}")
    if JAR_PATH.is_file():
        JAR_PATH.unlink()
    lines, seen = [], set()
    for line in src.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 7:
            key = (parts[0], parts[5])
            if key not in seen:
                seen.add(key)
                lines.append(line)
    JAR_PATH.write_text("# Netscape HTTP Cookie File\n" + "\n".join(lines) + "\n",
                        encoding="utf-8")


def bootstrap() -> BiliHttp:
    """建客户端 + 首页握手：让 B站向 jar 下发 buvid3/b_nut 基础 cookie。"""
    cli = BiliHttp()
    try:
        cli.get("https://www.bilibili.com/", retries=2)
    except RuntimeError as e:
        print(f"[warn] 首页握手异常（可忽略）：{e}", flush=True)
    return cli


def _extract_json_blob(html: str, var: str) -> dict:
    """从页面里抠出 window.<var>={...} 的完整 JSON 对象（括号配平法）。"""
    key = f"window.{var}="
    i = html.index(key)
    start = html.index("{", i)
    depth = 0
    for j, ch in enumerate(html[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(html[start:j + 1])
    raise ValueError(f"页面里没有完整的 {var}")


def fetch_video_meta(cli: BiliHttp, bvid: str, page: int = 1) -> dict:
    """视频页元数据：标题/UP主/发布日/时长/cid/分P + 最高码率音频流地址。

    多P视频按 ?p=N 取对应分P的 cid 与音频流（playinfo 随 ?p 变化）。
    """
    page_url = f"https://www.bilibili.com/video/{bvid}/" + (f"?p={page}" if page > 1 else "")
    html = ""
    for i in range(3):  # curl 返回码为 0 不代表过风控，需检查页面内容再退避重试
        html = cli.get(page_url) or ""
        if "__INITIAL_STATE__" in html:
            break
        time.sleep(3 * (i + 1))
    if "__INITIAL_STATE__" not in html:
        raise RuntimeError(f"{bvid} 页面被风控（未含 __INITIAL_STATE__），稍后可重跑")
    st = _extract_json_blob(html, "__INITIAL_STATE__")
    vd = st.get("videoData") or {}
    if not vd:
        raise RuntimeError(f"{bvid} 页面解析不到 videoData（可能视频不存在/仅限地区）")
    pages = vd.get("pages") or []
    cur = pages[page - 1] if 1 <= page <= len(pages) else vd
    info = {
        "bvid": bvid,
        "page": page,
        "n_pages": len(pages) or 1,
        "part": (cur.get("part") or "").strip(),
        "title": vd.get("title", bvid),
        "owner": (vd.get("owner") or {}).get("name", ""),
        "pubdate": datetime.fromtimestamp(
            vd.get("pubdate", 0), tz=timezone(timedelta(hours=8))).strftime("%Y-%m-%d"),
        "duration_s": cur.get("duration") or vd.get("duration", 0),
        "desc": (vd.get("desc") or "").strip(),
        "cid": cur.get("cid") or vd.get("cid"),
    }
    try:
        play = _extract_json_blob(html, "__playinfo__")
        auds = play["data"]["dash"]["audio"]
        best = max(auds, key=lambda a: a.get("bandwidth", 0))
        urls = [best["baseUrl"]] + list(best.get("backupUrl") or [])
        info["audio_urls"] = urls  # 主CDN + 备用CDN，下载失败可降级
        info["audio_bandwidth"] = best.get("bandwidth", 0)
    except (KeyError, ValueError):
        info["audio_urls"] = []  # 拿不到音频流时仍可走字幕路径
    return info


def fetch_cc_subtitles(cli: BiliHttp, bvid: str, cid: int) -> list[dict] | None:
    """登录态下优先取 CC/AI 字幕（json 结构 [{from,to,content}]）。未登录多为空。"""
    if not cid:
        return None
    data = cli.get_json(
        f"https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}")
    subs = ((data.get("data") or {}).get("subtitle") or {}).get("subtitles") or []
    if not subs:
        return None
    # 中文优先，其次 ai 中文
    subs.sort(key=lambda s: (0 if str(s.get("lan", "")).startswith(("zh", "ai-zh")) else 1))
    url = subs[0].get("subtitle_url") or ""
    if url.startswith("//"):
        url = "https:" + url
    if not url:
        return None
    body = cli.get_json(url)
    return [{"start": it.get("from", 0), "end": it.get("to", 0),
             "text": (it.get("content") or "").strip()}
            for it in (body.get("body") or []) if it.get("content")]


def download_audio(cli: BiliHttp, urls: list[str], out_path: Path,
                   duration_s: int = 0) -> None:
    """依次尝试 主CDN+备用CDN；单URL重试2次。curl 流式写盘，不经进程内存。"""
    to = max(600, int(duration_s * 5))
    last: Exception | None = None
    for url in urls:
        try:
            cli.get(url, retries=2, out=out_path, timeout=to)
        except RuntimeError as e:
            last = e
            continue
        if out_path.stat().st_size >= 4096:
            return
        last = RuntimeError(f"音频下载异常（{out_path.stat().st_size} 字节）")
    raise RuntimeError(f"所有CDN均失败：{last}")


def _to_hans(text: str) -> str:
    """繁→简归一（whisper medium 偶发整段输出繁体）。zhconv 缺失时原样返回。"""
    try:
        from zhconv import convert
        return convert(text, "zh-cn")
    except ImportError:
        return text


def _is_junk(text: str) -> bool:
    t = text.strip()
    if len(t) < 2:
        return True
    if HALLUCINATION_PAT.search(t):
        return True
    return False


def segments_to_paragraphs(segs: list[dict], para_chars: int = 400) -> str:
    """清洗后的句子 → 连续段落（~400 字一段，便于 RAG 600 字切块）。

    不做跨句合并：whisper 已按标点断句，按顺序直接拼回语流即可；
    跨句合并反而会把无句末标点的片段粘成无标点长串。
    """
    clean: list[str] = []
    for s in segs:
        t = (s.get("text") or "").strip()
        if not t or _is_junk(t):
            continue
        if clean and t == clean[-1]:  # whisper 重复伪影
            continue
        clean.append(t)
    paras, buf, size = [], [], 0
    for t in clean:
        buf.append(t)
        size += len(t)
        if size >= para_chars:
            paras.append("".join(buf))
            buf, size = [], 0
    if buf:
        paras.append("".join(buf))
    return "\n\n".join(paras)


# 幻觉特征标记：BGM/音效段易触发，直接丢弃
DROP_FLAGS = {"empty", "maybe_no_speech", "high_compression"}


def segments_to_paragraphs(segs: list[dict], para_chars: int = 400) -> str:
    """清洗后的句子 → 连续段落（~400 字一段，便于 RAG 600 字切块）。

    不做跨句合并：whisper 已按标点断句，按顺序直接拼回语流即可；
    跨句合并反而会把无句末标点的片段粘成无标点长串。
    """
    clean: list[str] = []
    for s in segs:
        t = (s.get("text") or "").strip()
        if not t or _is_junk(t):
            continue
        if clean and t == clean[-1]:  # whisper 重复伪影
            continue
        if DROP_FLAGS & set(s.get("flags") or []):
            continue
        clean.append(_to_hans(t))  # whisper 简繁输出不稳定，统一归一为简体
    paras, buf, size = [], [], 0
    for t in clean:
        buf.append(t)
        size += len(t)
        if size >= para_chars:
            paras.append("".join(buf))
            buf, size = [], 0
    if buf:
        paras.append("".join(buf))
    return "\n\n".join(paras)


def transcribe_video(audio_path: Path, work_dir: Path, model, lang: str,
                     prefix: str = "bili") -> list[dict]:
    """whisper 转写 → 句子级分段（复用语音管线的断句与质量打标逻辑）。"""
    wav = work_dir / f"{prefix}_full.wav"
    extract_wav(str(audio_path), str(wav), build_af())
    it, info = model.transcribe(
        str(wav), language=lang, beam_size=5,
        condition_on_previous_text=False,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
        word_timestamps=True,
        temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    print(f"    [whisper] 语言检测 {info.language} p={info.language_probability:.2f}",
          flush=True)
    segs: list[dict] = []
    for s in it:
        for p in split_sentences(s):
            segs.append({
                "start": round(p["start"], 2),
                "end": round(p["end"], 2),
                "text": p["text"],
                "flags": flag_quality(p["text"], lang, s),
            })
    print(f"    [whisper] 句子 {len(segs)} 条", flush=True)
    wav.unlink(missing_ok=True)
    return segs


def _slugify(title: str, limit: int = 40) -> str:
    s = re.sub(r"[\\/:*?\"<>|\s【】《》\[\]（）()·—～]+", "_", title).strip("_")
    return s[:limit].strip("_") or "untitled"


def write_transcript_md(out_path: Path, meta: dict, paras: str, method: str,
                        title: str | None = None) -> None:
    dur = meta["duration_s"]
    mmss = f"{dur // 60}:{dur % 60:02d}" if dur else "?"
    url = f"https://www.bilibili.com/video/{meta['bvid']}"
    if meta.get("n_pages", 1) > 1:
        url += f"?p={meta.get('page', 1)}"
    head = [
        f"# {title or meta['title']}",
        "",
        f"- 来源：B站 <{url}>",
        f"- UP主：{meta['owner']} ｜ 发布：{meta['pubdate']} ｜ 时长：{mmss}",
        f"- 提取方式：{method}（机器提取，可能存在少量识别误差）",
        f"- 抓取时间：{datetime.now().strftime('%Y-%m-%d')}",
        "",
        "---",
        "",
    ]
    out_path.write_text("\n".join(head) + paras + "\n", encoding="utf-8")


def _already_ingested(kb, ns: str, doc_id: str) -> bool:
    """该 doc_id 是否已有入库块（用于断点续跑跳过）。"""
    try:
        items = kb.list_items(ns)
    except Exception:  # noqa: BLE001 —— 查询失败按未入库处理，宁重勿漏
        return False
    return any((it.get("meta") or {}).get("doc_id") == doc_id for it in items)


def _ingest_one_page(cli: BiliHttp, kb, ns: str, character_id: str, bvid: str,
                     meta0: dict, page: int, model, lang: str, chunk_size: int,
                     force: bool, no_ingest: bool = False) -> bool:
    """单个分P的 下载→转写→清洗→落盘→入库。返回是否发生了新入库。

    no_ingest（剧情层模式）：只落盘 md、**不写入 lore 向量库**——新转写留给
    scripts/build_plot_graph.py 建剧情图谱，避免 ASR 文本继续稀释 lore 的 top_k 配额。
    """
    meta = meta0 if meta0["n_pages"] == 1 and page == 1 \
        else fetch_video_meta(cli, bvid, page)
    title = meta["title"] + (f"（{meta['part']}）" if meta["part"] else "")
    pdur = meta["duration_s"]
    print(f"  ▶ P{page}/{meta['n_pages']} {meta['part']}（{pdur // 60}:{pdur % 60:02d}）",
          flush=True)

    doc_id = bvid if meta["n_pages"] == 1 else f"{bvid}_p{page}"
    out_path = (ROOT / "data" / "lore" / character_id / "视频文案"
                / f"{doc_id}_{_slugify(title)}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 断点续跑：md 已落盘且块已入库 → 跳过该分P（--force 强制重做）
    # --no-ingest 模式下没有入库记录，只看 md 是否已落盘
    if not force and out_path.is_file() and (no_ingest or _already_ingested(kb, ns, doc_id)):
        print(f"    [skip] {doc_id} 已入库（{out_path.name}），跳过", flush=True)
        return False

    # ① 字幕优先（有登录态才可能非空）
    subs = fetch_cc_subtitles(cli, bvid, meta["cid"])
    if subs:
        print(f"    [sub] 命中B站字幕 {len(subs)} 条，免转写", flush=True)
        paras = segments_to_paragraphs(subs)
        method = "B站CC/AI字幕"
        audio_path = None
    else:
        if not meta.get("audio_urls"):
            print("    [skip] 无字幕也无音频流", flush=True)
            return False
        audio_path = TMP_DIR / f"{doc_id}.m4s"
        print(f"    [dl] 下载纯音频"
              f"（约 {pdur * meta.get('audio_bandwidth', 0) / 8 / 1e6:.0f} MB）...",
              flush=True)
        download_audio(cli, meta["audio_urls"], audio_path, pdur)
        print("    [asr] faster-whisper 转写中 ...", flush=True)
        t0 = time.time()
        segs = transcribe_video(audio_path, TMP_DIR, model, lang, prefix=doc_id)
        paras = segments_to_paragraphs(segs)
        method = "whisper语音转写"
        print(f"    [asr] 转写完成，用时 {time.time() - t0:.0f}s", flush=True)

    if len(paras) < 50:
        print(f"    [skip] 文案过短（{len(paras)} 字），疑似转写失败，不入库", flush=True)
        if audio_path is not None:
            audio_path.unlink(missing_ok=True)
        return False
    write_transcript_md(out_path, meta, paras, method, title)
    if audio_path is not None:
        audio_path.unlink(missing_ok=True)  # 用完即删，绝不留到下一个分P

    if no_ingest:
        print(f"    [plot] 仅落盘（--no-ingest）：{out_path.name}"
              f"，请用 build_plot_graph.py --build-corpus 重建剧情语料", flush=True)
        return True

    # ② 入库：先按 doc_id 清旧块保证幂等，再入新块
    removed = kb.filter_remove(
        ns, lambda it, d=doc_id: (it.get("meta") or {}).get("doc_id") == d)
    url = f"https://www.bilibili.com/video/{bvid}" + \
        (f"?p={page}" if meta["n_pages"] > 1 else "")
    r = ingest_file(kb, out_path, namespace=ns, character_id=character_id,
                    chunk_size=chunk_size, doc_id=doc_id,
                    extra_meta={"url": url, "uploader": meta["owner"],
                                "pubdate": meta["pubdate"],
                                "source_type": "bilibili_transcript"})
    print(f"    [kb] {out_path.name} → {r['stored']} 块"
          + (f"（先移除旧块 {removed}）" if removed else ""), flush=True)
    return True


def process_one(cli: BiliHttp, kb, ns: str, character_id: str, bvid: str, model,
                lang: str, chunk_size: int, list_only: bool,
                force: bool = False, no_ingest: bool = False,
                pages: tuple | None = None) -> bool:
    """单个视频全流程（多P逐分P串行）。返回是否有新入库。"""
    meta0 = fetch_video_meta(cli, bvid)
    dur = meta0["duration_s"]
    print(f"  元数据：{meta0['title']} ｜ {meta0['owner']} ｜ "
          f"{dur // 60}:{dur % 60:02d} ｜ 发布 {meta0['pubdate']}"
          + (f" ｜ 共{meta0['n_pages']}P" if meta0["n_pages"] > 1 else "")
          + (f" ｜ 本进程仅处理 P{pages[0]}-{pages[1]}" if pages else ""), flush=True)
    if list_only:
        return False

    ingested = False
    if meta0["n_pages"] > 1:
        # 旧版把 P1 按 doc_id=bvid 入过库；多P化后 doc_id 变为 <bvid>_p<N>，先清遗留
        removed = kb.filter_remove(
            ns, lambda it: (it.get("meta") or {}).get("doc_id") == bvid)
        if removed:
            print(f"  [kb] 清理旧版整视频块 {removed} 条（doc_id={bvid}）", flush=True)
        for legacy in (ROOT / "data" / "lore" / character_id / "视频文案").glob(
                f"{bvid}_*.md"):
            if "_p" not in legacy.stem[:len(bvid) + 3]:
                legacy.unlink(missing_ok=True)
                print(f"  [fs] 删除旧版分P前文件 {legacy.name}", flush=True)

    # 单P失败只记下并继续下一P，不拖垮整个视频
    failed: list[int] = []
    for page in range(1, meta0["n_pages"] + 1):
        if pages and not (pages[0] <= page <= pages[1]):
            continue  # --pages 范围过滤：多进程拆分同一视频时各管一段
        try:
            ingested = _ingest_one_page(cli, kb, ns, character_id, bvid, meta0,
                                        page, model, lang, chunk_size, force,
                                        no_ingest) \
                or ingested
        except Exception as e:  # noqa: BLE001
            failed.append(page)
            print(f"    [error] P{page}: {e}", flush=True)
        gc.collect()  # 每个分P处理完主动回收，再进下一个
    if failed:
        print(f"  [warn] 失败分P：{failed}（修复后重跑即可断点续传）", flush=True)
    return ingested


def main() -> int:
    ap = argparse.ArgumentParser(description="B站视频文案 → 角色知识库（逐视频串行）")
    ap.add_argument("--character", default="wu_ming_zhe", help="角色 id")
    ap.add_argument("--bvs", nargs="*", help="BV号列表，缺省用内置1999清单")
    ap.add_argument("--list", action="store_true", help="只拉取并显示元数据，不转写不入库")
    ap.add_argument("--lang", default="zh", help="音频语言：zh/en/auto（auto=逐窗自动检测）")
    ap.add_argument("--model", default=r"C:\Users\Lenovo\.cache\whisper\medium")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--compute", default="int8")
    ap.add_argument("--cookies", help="Netscape格式 cookie 文件（登录态可拉CC/AI字幕）")
    ap.add_argument("--gap", type=float, default=2.0, help="视频间休息秒数")
    ap.add_argument("--threads", type=int, default=4, help="whisper CPU线程数")
    ap.add_argument("--force", action="store_true", help="忽略断点续跑，强制重做已入库分P")
    ap.add_argument("--no-ingest", action="store_true",
                    help="只落盘转写 md、不写入 lore 向量库（剧情层模式：留给 build_plot_graph 建图谱）")
    ap.add_argument("--pages", default="",
                    help="仅处理指定分P序号范围，如 40-79 或单个 40（默认全部，用于多进程拆分同一视频）")
    args = ap.parse_args()

    pages = None
    if args.pages:
        parts = args.pages.split("-")
        pages = (int(parts[0]), int(parts[-1]))

    bvs = args.bvs or DEFAULT_BVS
    settings = get_settings()
    ns = lore_namespace(args.character)
    # auto = 不强制语言，交由 whisper 逐窗检测（英配视频必须放开，否则产出乱码中文）
    lang = None if args.lang.lower() in ("auto", "none", "") else args.lang

    cli = bootstrap()
    print(f"[init] 队列 {len(bvs)} 个视频 → 命名空间 {ns}"
          + ("（带登录态，优先CC字幕）" if args.cookies else "（未登录，走whisper转写）")
          + f"｜语言 {'自动检测' if lang is None else lang}", flush=True)

    # whisper 模型只加载一次、常驻复用：内存峰值恒定，且省去逐视频重载
    model = None
    need_model = not args.list
    if need_model:
        from faster_whisper import WhisperModel
        print(f"[init] 加载 whisper 模型 {args.model}（{args.device}/{args.compute}）...",
              flush=True)
        t0 = time.time()
        model = WhisperModel(args.model, device=args.device, compute_type=args.compute,
                             cpu_threads=args.threads)
        print(f"[init] 模型就绪，用时 {time.time() - t0:.0f}s", flush=True)

    kb = build_knowledge_base(settings)
    count0 = kb.count().get(ns, 0)
    ok, fail = 0, 0
    for i, bvid in enumerate(bvs, 1):
        print(f"\n=== [{i}/{len(bvs)}] {bvid} ===", flush=True)
        try:
            if process_one(cli, kb, ns, args.character, bvid, model, lang,
                           settings.chunk_size, list_only=args.list, force=args.force,
                           no_ingest=args.no_ingest, pages=pages):
                ok += 1
        except Exception as e:  # noqa: BLE001 —— 单个视频失败不拖垮整个队列
            fail += 1
            print(f"  [error] {bvid}: {e}", flush=True)
        gc.collect()  # 每个视频处理完主动回收，再进下一个
        if i < len(bvs):
            time.sleep(args.gap)

    if args.list:
        return 0

    # 与 ingest_lore.py 一致：导入后绑定角色卡知识范围（导入即生效）
    store = CharacterStore(settings=settings)
    card = store.get(args.character)
    if card is not None:
        scope = list(dict.fromkeys([ns, "events", "episodic"]))
        store.update(args.character, {"knowledge_scope": scope})
        print(f"\n[card] {args.character}.knowledge_scope = {scope}", flush=True)

    count1 = kb.count().get(ns, 0)
    print(f"\n[done] 成功 {ok} 个 / 失败 {fail} 个；{ns} 块数 {count0} → {count1}",
          flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
