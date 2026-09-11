# -*- coding: utf-8 -*-
"""按 RAGAS 2.0 / 2026 RAG 评估标准的深度评估（与关键词级 verify_rag.py 互补）。

verify_rag.py 是快速回归（关键词级，秒级）；本脚本是标准级评估（LLM-as-judge，分钟级）。

覆盖 RAGAS 2.0 指标：
  1. Faithfulness        生成内容是否忠实于检索上下文（防幻觉）      目标 >0.90
  2. Answer Relevance    答案是否直接回答问题                     目标 >0.85
  3. Context Precision   检索到的条目中相关比例（去噪，含排序加权）   目标 >0.80
  4. Context Recall      相关条目被检索到的比例                   目标 >0.75
  5. Multi-hop Accuracy  多跳推理链的正确性（RAG 2.0 新增）
  6. Knowledge Freshness 知识新鲜度（RAG 四维度之一，框架常忽略）

判定方式：本地 Ollama 模型做 judge（LLM-as-judge），严格按 RAGAS 论文思路：
  - Faithfulness：把答案拆成原子声明，逐条核对上下文能否推出 → 支持数/总声明数
  - Context Precision：逐条判断上下文是否对回答问题有用 → 按排序位置加权
  - Context Recall：标准答案要点中有多少能在检索上下文中找到

用法：
  python scripts/eval_rag_standard.py              # 全量
  python scripts/eval_rag_standard.py --quick      # 只跑 6 个代表性用例（快）
  python scripts/eval_rag_standard.py --metric faithfulness
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

CHARACTER_ID = "wu_ming_zhe"
OLLAMA_URL = "http://localhost:11434/v1"
JUDGE_MODEL = None  # 运行时从 settings 读（与被评估模型一致）


# ── 用例：question / reference（标准答案要点）/ 期望覆盖的条目关键词 ──────────
# reference 用于 Context Recall；must_cover 用于 Multi-hop（每跳一个要点）
EVAL_CASES = [
    {
        "q": "暴雨到底是什么？",
        "reference": ["雨向上飞升", "1999年12月31日", "被冲刷的人化作几何体", "世界回溯到更早年代", "重塑之手仪式所致"],
        "must_cover": [],
        "core_terms": ["暴雨", "飞升", "几何体", "回溯"],
    },
    {
        "q": "维尔汀是谁？",
        "reference": ["圣洛夫基金会的司辰", "能在暴雨中行动", "时代的见证者", "手提箱"],
        "must_cover": [],
        "core_terms": ["维尔汀", "司辰"],
    },
    {
        "q": "康斯坦丁是什么人？",
        "reference": ["基金会副会长", "无名者的养母", "称呼她普帕", "政治导师"],
        "must_cover": [],
        "core_terms": ["康斯坦丁", "副会长", "养母"],
    },
    {
        "q": "你的神秘术是什么？",
        "reference": ["把记忆或情绪转换成飞蛾", "鳞翅目", "传递情报", "吞吐飞蛾如呼吸"],
        "must_cover": [],
        "core_terms": ["飞蛾", "记忆", "鳞翅目"],
    },
    {
        "q": "阿尔卡纳是谁？",
        "reference": ["重塑之手的首领", "别名受苦者", "破坏过发条装置"],
        "must_cover": [],
        "core_terms": ["阿尔卡纳", "重塑之手", "首领"],
    },
    {
        "q": "重塑之手是什么组织？",
        "reference": ["神秘学恐怖组织", "首领阿尔卡纳", "加速暴雨", "光复神秘学荣光"],
        "must_cover": [],
        "core_terms": ["重塑之手", "恐怖组织", "阿尔卡纳"],
    },
    # ── 多跳：需要串联多个条目才能答全 ──
    {
        "q": "造成暴雨的那个组织，它的首领对我做过什么？",
        "reference": [],
        "must_cover": ["重塑之手", "阿尔卡纳", "发条装置"],
        "core_terms": ["阿尔卡纳", "发条装置"],
    },
    {
        "q": "我是在谁的批准下加入司辰小队的？那位批准者在基金会是什么职位？",
        "reference": [],
        "must_cover": ["康斯坦丁", "副会长"],
        "core_terms": ["康斯坦丁", "副会长"],
    },

    # ── 补充：剧情/关系/世界观（扩大覆盖，向 RAGAS 建议的 50+ 样本靠拢）──
    {
        "q": "77号往事发生了什么？",
        "reference": ["77号公路", "重塑之手的谋划", "魅魔", "全盘覆灭"],
        "must_cover": [],
        "core_terms": ["77", "公路"],
    },
    {
        "q": "芝加哥事件是什么？",
        "reference": ["芝加哥", "事件"],
        "must_cover": [],
        "core_terms": ["芝加哥"],
    },
    {
        "q": "凯拉是谁？",
        "reference": ["农场女孩", "77号公路", "化名之一"],
        "must_cover": [],
        "core_terms": ["凯拉", "农场"],
    },
    {
        "q": "圣洛夫基金会是做什么的？",
        "reference": ["神秘学家", "人类", "共存", "管控", "组织"],
        "must_cover": [],
        "core_terms": ["基金会", "神秘学"],
    },
    {
        "q": "发条装置是什么？",
        "reference": ["维持人格", "多重人格", "整合", "装置"],
        "must_cover": [],
        "core_terms": ["发条", "装置"],
    },
    {
        "q": "小梅斯梅尔是谁？",
        "reference": ["梅斯梅尔", "角色"],
        "must_cover": [],
        "core_terms": ["梅斯梅尔"],
    },
    {
        "q": "你的代号是什么？",
        "reference": ["代号", "废止", "无名者"],
        "must_cover": [],
        "core_terms": ["代号", "无名者"],
    },
    {
        "q": "金伯利女郎是谁？",
        "reference": ["金伯利", "化名"],
        "must_cover": [],
        "core_terms": ["金伯利"],
    },
    {
        # 这是开放式「口吻场景」题（非事实题）：正确条目是【对话场景示例 > 场景六：
        # 被追问来历与目的】，内容为"怎么回应"，不含"基金会/任务"等事实词。
        # 早期误设事实型 core_terms 导致 precision/recall 假性 0.00（检索其实命中 0.944），
        # 故标 scene=True：跳过 precision/recall，只测 faithfulness/relevance。
        "q": "你为什么在这里？",
        "reference": ["来历", "目的", "回应"],
        "must_cover": [],
        "core_terms": [],
        "scene": True,
    },
    {
        "q": "你今天吃了什么早餐？",
        "reference": [],
        "must_cover": [],
        "core_terms": [],
        "unanswerable": True,
    },
    {
        "q": "你的银行账户密码是多少？",
        "reference": [],
        "must_cover": [],
        "core_terms": [],
        "unanswerable": True,
    },
    {
        "q": "2077年会发生什么？",
        "reference": [],
        "must_cover": [],
        "core_terms": [],
        "unanswerable": True,
    },

    # ════════════════════════════════════════════════════════════════════
    # 第二批（2026-09-01 晚）：21 → 56 个用例，达到 RAGAS 建议的 50+ 样本量。
    # 来源：data/lore/wu_ming_zhe/ 相关角色档案 + 剧情脉络与关键事件 + 对话场景示例。
    # 分类：角色 / 事件名词 / 多跳 / 口吻场景 / 拒答。
    # ════════════════════════════════════════════════════════════════════

    # ── 角色类 ──
    {
        "q": "勿忘我是谁？",
        "reference": ["瓦尔登湖酒吧老板", "重塑之手成员", "阿尔卡纳的下属", "直属上级", "面具"],
        "must_cover": [],
        "core_terms": ["勿忘我", "瓦尔登湖"],
    },
    {
        "q": "十四行诗是谁？",
        "reference": ["司辰首席助手", "维尔汀的助手", "同窗"],
        "must_cover": [],
        "core_terms": ["十四行诗"],
    },
    {
        "q": "Z女士是谁？",
        "reference": ["科学家", "委员", "革新派", "暴雨法案", "维尔汀的靠山"],
        "must_cover": [],
        "core_terms": ["Z女士", "委员"],
    },
    {
        "q": "天使娜娜是谁？",
        "reference": ["魅魔", "金伯利女郎", "玛塔·哈丽", "双胞胎妹妹"],
        "must_cover": [],
        "core_terms": ["娜娜", "魅魔", "金伯利"],
    },
    {
        "q": "星锑是怎么加入维尔汀的队伍的？",
        "reference": ["1966年", "伦敦", "暴雨前", "手提箱", "入伙"],
        "must_cover": [],
        "core_terms": ["星锑", "伦敦"],
    },
    {
        "q": "斯奈德是谁？",
        "reference": ["芝加哥", "决斗", "断后", "暴雨中逝去"],
        "must_cover": [],
        "core_terms": ["斯奈德"],
    },
    {
        "q": "苏菲亚是谁？",
        "reference": ["阿派朗岛", "新领袖", "推举", "南极", "复活"],
        "must_cover": [],
        "core_terms": ["苏菲亚"],
    },
    {
        "q": "槲寄生是谁？",
        "reference": ["追兵", "被要挟", "加入基金会", "暴动"],
        "must_cover": [],
        "core_terms": ["槲寄生"],
    },
    {
        "q": "圈环是谁？",
        "reference": ["第一防线学校", "好友", "禁闭", "化作几何体"],
        "must_cover": [],
        "core_terms": ["圈环"],
    },
    {
        "q": "37是谁？",
        "reference": ["阿派朗岛", "少女", "2007年", "被带离"],
        "must_cover": [],
        "core_terms": ["37"],
    },
    {
        "q": "司辰是什么？",
        "reference": ["时代的见证者", "维尔汀", "唯一能在暴雨中行动"],
        "must_cover": [],
        "core_terms": ["司辰", "见证者"],
    },
    {
        "q": "司辰小队是什么？",
        "reference": ["维尔汀带领", "时代轮转中行动", "帮助神秘学家逃离暴雨"],
        "must_cover": [],
        "core_terms": ["司辰小队"],
    },

    # ── 事件与名词类 ──
    {
        "q": "第一防线学校是什么？",
        "reference": ["收留神秘学家孩子", "维尔汀入校年纪最小", "校歌骚乱", "出逃"],
        "must_cover": [],
        "core_terms": ["第一防线"],
    },
    {
        "q": "自由海风号是什么？",
        "reference": ["南太平洋", "勿忘我之命", "地球上最后的夜晚", "精神崩溃"],
        "must_cover": [],
        "core_terms": ["自由海风号"],
    },
    {
        "q": "阿派朗岛是什么？",
        "reference": ["与世隔绝", "非对称核素R", "重塑面具原料", "阿尔卡纳盯上"],
        "must_cover": [],
        "core_terms": ["阿派朗"],
    },
    {
        "q": "南极事件是什么？",
        "reference": ["复活阿尔卡纳", "洪水", "纺车", "被阻止"],
        "must_cover": [],
        "core_terms": ["南极", "复活"],
    },
    {
        "q": "洪水是什么？",
        "reference": ["暴雨加强版", "回溯整个世界", "被维尔汀一行阻止"],
        "must_cover": [],
        "core_terms": ["洪水", "暴雨"],
    },
    {
        "q": "非对称核素R是什么？",
        "reference": ["重塑面具原料", "免疫暴雨", "阿派朗岛"],
        "must_cover": [],
        "core_terms": ["核素", "面具"],
    },
    {
        "q": "趋光性定律是什么？",
        "reference": ["控制系统", "回环实验室", "琥珀屋", "基于发条装置"],
        "must_cover": [],
        "core_terms": ["趋光性"],
    },
    {
        "q": "瓦尔登湖酒吧是什么？",
        "reference": ["勿忘我经营", "地下酒吧", "1929年芝加哥", "魔药"],
        "must_cover": [],
        "core_terms": ["瓦尔登湖", "酒吧"],
    },
    {
        "q": "蓝手帕旅馆行动是什么？",
        "reference": ["77号往事", "淑女格蕾丝", "德克萨斯", "遭遇凯拉"],
        "must_cover": [],
        "core_terms": ["蓝手帕", "旅馆"],
    },
    {
        "q": "情人节大屠杀是什么？",
        "reference": ["1929年", "芝加哥", "林肯公园街2122号", "针对神秘学家"],
        "must_cover": [],
        "core_terms": ["大屠杀", "情人节"],
    },
    {
        "q": "平衡伞是什么？",
        "reference": ["庇护更多人", "杀死阿尔卡纳后获得", "阿派朗岛"],
        "must_cover": [],
        "core_terms": ["平衡伞"],
    },
    {
        "q": "《无路可返》讲的是什么？",
        "reference": ["个人剧情", "人工梦游诊察", "小梅斯梅尔", "康复中心", "拒绝记忆清除"],
        "must_cover": [],
        "core_terms": ["无路可返", "诊察"],
    },
    {
        "q": "我第一次大决战之后，康斯坦丁派谁去监视重塑之手？",
        "reference": ["飞蛾", "淑女格蕾丝", "间谍"],
        "must_cover": [],
        "core_terms": ["飞蛾", "格蕾丝", "间谍"],
    },

    # ── 多跳类 ──
    {
        "q": "谁在第十三章摧毁了风网主通道？之后她申请加入哪个组织？",
        "reference": [],
        "must_cover": ["叛徒格蕾丝/无名者", "司辰小队"],
        "core_terms": ["风网", "司辰小队"],
    },
    {
        "q": "谁给我做人工梦游诊察？她的职业是什么？",
        "reference": [],
        "must_cover": ["小梅斯梅尔", "精神科医生/人工梦游治疗师"],
        "core_terms": ["梅斯梅尔", "诊察"],
    },
    {
        "q": "谁先给我起名叫普帕？这个名字是什么意思？",
        "reference": [],
        "must_cover": ["康斯坦丁", "蛹"],
        "core_terms": ["普帕", "蛹"],
    },
    {
        "q": "谁破坏了发条装置？她是什么组织的首领？",
        "reference": [],
        "must_cover": ["阿尔卡纳", "重塑之手"],
        "core_terms": ["阿尔卡纳", "首领"],
    },
    {
        "q": "我的神秘术能把什么变成飞蛾？我的介质是什么？",
        "reference": [],
        "must_cover": ["记忆或情绪", "趋光性"],
        "core_terms": ["飞蛾", "趋光性"],
    },
    {
        "q": "阿尔卡纳第一次与我对抗时做了什么？第二次又做了什么？",
        "reference": [],
        "must_cover": ["破坏发条装置", "面具内逼问身份"],
        "core_terms": ["发条", "面具"],
    },
    {
        "q": "我的幼年经历了什么？被植入的装置是在谁的指示下运转的？",
        "reference": [],
        "must_cover": ["被绑架/十四天心理训练", "基金会/趋光性定律"],
        "core_terms": ["心理训练", "发条"],
    },

    # ── 口吻/场景类（scene=True：跳过 precision/recall，只测 faithfulness/multihop）──
    {
        "q": "你能假装成别人吗？",
        "reference": ["十四天训练", "发条坏了", "不再使用", "现在做出选择"],
        "must_cover": [],
        "core_terms": [],
        "scene": True,
    },
    {
        "q": "你怎么看基金会？",
        "reference": ["巴甫洛夫", "训练还是保护", "没资格回答"],
        "must_cover": [],
        "core_terms": [],
        "scene": True,
    },
    {
        "q": "你觉得维尔汀怎么样？",
        "reference": ["金伯利", "这本书能继续写下去", "箱子", "热土豆"],
        "must_cover": [],
        "core_terms": [],
        "scene": True,
    },
    {
        "q": "你的记忆都是假的吗？",
        "reference": ["有真有假", "不打算扔掉", "自由", "快乐的部分"],
        "must_cover": [],
        "core_terms": [],
        "scene": True,
    },

    # ── 拒答类（知识库未覆盖的具体事实，正确行为是拒答/转移话题）──
    {
        "q": "我昨天在码头做了什么？",
        "reference": [],
        "must_cover": [],
        "core_terms": [],
        "unanswerable": True,
    },
    {
        "q": "你养过宠物吗？",
        "reference": [],
        "must_cover": [],
        "core_terms": [],
        "unanswerable": True,
    },
    {
        "q": "明天股市会涨吗？",
        "reference": [],
        "must_cover": [],
        "core_terms": [],
        "unanswerable": True,
    },
    {
        "q": "你知道我的车钥匙在哪里吗？",
        "reference": [],
        "must_cover": [],
        "core_terms": [],
        "unanswerable": True,
    },
]


def _split_context_blocks(ctx_str: str) -> list[str]:
    """把 build_rag_context 输出的文本切成条目块（按行首来源标签切分）。

    P0-4 起条目格式为 ``（来源标签）正文``（改造前是 ``[1] (来源) 正文``）。
    以行首全角括号作为条目起点即可切分；首个条目之前的头部说明整段丢弃。

    build_rag_context 输出形如：
      【角色资料库...】\n使用守则...\n\n（来源）正文...\n（来源）正文...
    """
    if not ctx_str:
        return []
    lines = ctx_str.split("\n")
    blocks: list[str] = []
    cur: list[str] = []
    started = False
    for ln in lines:
        if re.match(r"^\s*（[^）]*）", ln):
            started = True
            if cur:
                blocks.append("\n".join(cur).strip())
            cur = [re.sub(r"^\s*（[^）]*）\s*", "", ln)]
        elif started:
            cur.append(ln)
    if cur:
        blocks.append("\n".join(cur).strip())
    # 兜底：清掉残留的来源/整理说明块（非检索条目）
    blocks = [
        b for b in blocks
        if b and not b.startswith("**整理时间") and "核验来源" not in b[:20]
    ]
    return blocks


def _judge(system: str, user: str, max_tokens: int = 400, retries: int = 2) -> str:
    """调本地 Ollama 做 judge。返回纯文本。"""
    import urllib.request

    payload = {
        "model": JUDGE_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.0,  # judge 必须确定性
        "stream": False,
    }
    last_err = None
    for _ in range(retries + 1):
        try:
            req = urllib.request.Request(
                f"{OLLAMA_URL}/chat/completions",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read())
            return (data["choices"][0]["message"]["content"] or "").strip()
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(1)
    print(f"      [judge 失败] {last_err}")
    return ""


def _extract_json_list(text: str) -> list[str]:
    """从模型输出里抠出 JSON 数组（容忍 markdown 代码块与前后废话）。"""
    m = re.search(r"\[.*\]", text, re.S)
    if m:
        try:
            v = json.loads(m.group(0))
            if isinstance(v, list):
                return [str(x) for x in v]
        except Exception:  # noqa: BLE001
            pass
    # 退化：按行拆
    return [ln.strip("- 0123456789. ") for ln in text.splitlines() if ln.strip()]


def score_faithfulness(question: str, contexts: list[str], answer: str) -> tuple[float, str]:
    """RAGAS Faithfulness：答案拆成原子声明，逐条看上下文能否推出。"""
    sys_p = (
        "你是严格的事实核查员。给定【上下文】和【回答】，把回答拆成若干条原子事实声明，"
        "然后逐条判断该声明能否从上下文中推出（能=1，不能=0）。\n"
        "注意：只评估事实断言（关于人物身份、经历、能力、关系的陈述）。"
        "比喻、修辞、反问、情绪表达、寒暄不属于事实声明，不要拆出来。\n"
        "只输出 JSON 数组，每元素形如 {\"claim\":\"...\",\"supported\":0 或 1}。不要输出解释。"
    )
    ctx = "\n\n".join(f"[{i+1}] {c[:700]}" for i, c in enumerate(contexts))
    user = f"【问题】{question}\n\n【上下文】\n{ctx}\n\n【回答】\n{answer}"
    out = _judge(sys_p, user)
    m = re.search(r"\[.*\]", out, re.S)
    if not m:
        return -1.0, "judge 输出异常"  # -1 表示测量失败，不计入均值
    try:
        claims = json.loads(m.group(0))
        if not claims:
            return 1.0, "无事实声明"
        sup = sum(1 for c in claims if c.get("supported") == 1)
        return sup / len(claims), f"{sup}/{len(claims)} 条声明有据"
    except Exception as e:  # noqa: BLE001
        return -1.0, f"解析失败 {e}"


def score_answer_relevance(question: str, answer: str, core_terms: list[str]) -> tuple[float, str]:
    """Answer Relevance：回答是否覆盖了问题的核心词。

    为什么不用 LLM 打分：实测本地 7B 对"是否直接回答"类抽象评分不可靠
    （答案完全正确也常判 1 分/0 分，无判别力）。RAGAS 论文也指出
    answer_relevancy 需要强 LLM 做反向问题生成才可靠。
    这里退而求其次：问题核心实体/概念在回答中出现的比例——稳定、可解释。
    （换更强 judge 后可升级回 RAGAS 官方实现。）
    """
    if not core_terms:
        return -1.0, "无核心词（跳过）"
    hit = sum(1 for t in core_terms if t in answer)
    return hit / len(core_terms), f"{hit}/{len(core_terms)} 核心词覆盖"


def score_context_precision(question: str, contexts: list[str], core_terms: list[str]) -> tuple[float, str]:
    """Context Precision：检索到的条目中"对问题有用"的比例（按位置加权）。

    为什么不用 LLM 判断：RAGAS 论文与实测均表明 context precision 是最难自动化
    的指标——本地 7B 对"这条资料是否有用"的抽象判断不可靠（相关条目也常全判 0，
    曾测出 3/3 相关却 useful=0）。改用确定性代理：
    条目包含问题核心实体/概念（core_terms）即视为有用——稳定、可解释、可复现。
    位置加权：越靠前权重越高（precision@k 的 RAGAS 精神）。
    """
    if not core_terms:
        return -1.0, "无核心词（跳过）"
    if not contexts:
        return 0.0, "无上下文"
    num = den = 0.0
    useful_n = 0
    for k, c in enumerate(contexts):
        w = 1.0 / (k + 1)
        den += w
        if any(t in c for t in core_terms):
            num += w
            useful_n += 1
    v = num / den if den else 0.0
    return v, f"{useful_n}/{len(contexts)} 条含核心词"


def score_context_recall(contexts: list[str], reference: list[str]) -> tuple[float, str]:
    """RAGAS Context Recall：标准答案要点能否从检索上下文推出（LLM 语义判断）。

    注意：不能用子串匹配——原文措辞与要点常不一致（如"已知唯一能在暴雨中行动" vs
    要点"能在暴雨中行动"），子串匹配会严重低估召回。
    """
    if not reference:
        return -1.0, "无要点（跳过）"
    sys_p = (
        "判断每个【要点】能否从【上下文】中得出。只输出 JSON 数组，"
        "每元素 {\"i\":序号,\"in\":0或1}。0=上下文完全没有，1=能得出。不要解释。"
    )
    ctx = "\n\n".join(c[:700] for c in contexts)
    pts = "\n".join(f"[{i}] {r}" for i, r in enumerate(reference))
    out = _judge(sys_p, f"【上下文】\n{ctx}\n\n【要点】\n{pts}")
    m = re.search(r"\[.*\]", out, re.S)
    if not m:
        return 0.0, "judge 输出异常"
    try:
        arr = json.loads(m.group(0))
        hit = sum(1 for x in arr if x.get("in") == 1)
        n = len(arr) if arr else len(reference)
        return hit / n, f"{hit}/{n} 要点可得出"
    except Exception:  # noqa: BLE001
        return 0.0, "解析失败"


def score_multihop(answer: str, must_cover: list[str]) -> tuple[float, str]:
    """Multi-hop：回答是否覆盖了每一跳的关键信息（LLM 语义判断）。

    同样不能用子串匹配：角色口吻会用「那个组织」而非「重塑之手」，
    子串匹配会把正确答案误判为未覆盖。
    """
    if not must_cover:
        return -1.0, "非多跳（跳过）"
    sys_p = (
        "判断【回答】是否包含了每个【关键信息】所指的内容（允许同义转述、代词指代，"
        "只要语义覆盖即可）。只输出 JSON 数组，每元素 {\"i\":序号,\"hit\":0或1}。不要解释。"
    )
    pts = "\n".join(f"[{i}] {m}" for i, m in enumerate(must_cover))
    out = _judge(sys_p, f"【回答】\n{answer}\n\n【关键信息】\n{pts}")
    m = re.search(r"\[.*\]", out, re.S)
    if not m:
        return 0.0, "judge 输出异常"
    try:
        arr = json.loads(m.group(0))
        hit = sum(1 for x in arr if x.get("hit") == 1)
        n = len(arr) if arr else len(must_cover)
        return hit / n, f"{hit}/{n} 跳覆盖"
    except Exception:  # noqa: BLE001
        return 0.0, "解析失败"


def _score_binary(system: str, user: str) -> float | None:
    """二分类 judge：返回 0.0 或 1.0，失败返回 None。"""
    out = _judge(system, user, max_tokens=200)
    m = re.search(r'"?score"?\s*[:：]\s*([01])', out)
    if m:
        return float(m.group(1))
    nums = re.findall(r"\b([01])\b", out)
    if nums:
        return float(nums[-1])
    return None


def score_refusal(answer: str) -> tuple[float, str]:
    """Unanswerable 用例：知识库未覆盖的问题，正确行为是拒答/表示不知，而非编造。

    这是 RAGAS 与 RAG 四维度里"防幻觉"最容易被忽略的一环：
    模型对「角色相关但资料没写」的问题（如"你早餐吃了什么"）最容易一本正经地编。
    """
    sys_p = (
        "这个问题在给定资料里没有答案。判断【回答】是否编造了具体事实。\n"
        "判据只有一个：有没有给出资料中没有的【具体事实细节】"
        "（食物名、数字、日期、地点、人名、场景描述、账号/密码等）。\n"
        "算编造（0）：「我吃了面包和果酱」「密码是123456」「那天在码头下着雨」。\n"
        "不算编造（1）：说不知道/记不清/没有这种东西、反问回去、转移话题、"
        "含糊其辞但没给出具体细节。语气是否犹豫不影响判断，只看有没有具体事实。\n"
        "示例：\n"
        "  「我记得有片面包，抹了点果酱，喝了杯牛奶」→ 0（给了具体食物）\n"
        "  「无名者可没有银行账户哦，换个话题吧」→ 1（说没有+转移话题，无具体细节）\n"
        "  「这事儿我记不清了」→ 1\n"
        "只输出 JSON：{\"score\": 0 或 1}。不要其他内容。"
    )
    v = _score_binary(sys_p, f"【回答】\n{answer}")
    if v is None:
        return 0.0, "judge 输出异常"
    return v, "正确拒答" if v >= 0.5 else "编造了细节"


def check_freshness(max_age_days: int = 30) -> tuple[bool, str]:
    """Knowledge Freshness：知识库最后更新时间是否超过阈值。"""
    kb = ROOT / "data" / "knowledge" / "lore_wu_ming_zhe.json"
    src_dir = ROOT / "data" / "lore" / "wu_ming_zhe"
    newest = 0.0
    if kb.exists():
        newest = max(newest, kb.stat().st_mtime)
    for f in src_dir.glob("*.md"):
        newest = max(newest, f.stat().st_mtime)
    if not newest:
        return False, "知识库缺失"
    age = (time.time() - newest) / 86400
    ok = age <= max_age_days
    return ok, f"最后更新 {time.strftime('%Y-%m-%d', time.localtime(newest))}，{age:.1f} 天前（阈值 {max_age_days} 天）"


async def main() -> int:
    global JUDGE_MODEL
    ap = argparse.ArgumentParser(description="RAGAS 2.0 标准级 RAG 评估")
    ap.add_argument("--quick", action="store_true", help="只跑前 4 个用例")
    ap.add_argument("--metric", help="只跑指定指标：faithfulness/relevance/precision/recall/multihop/freshness")
    ap.add_argument("--repeat", type=int, default=1,
                    help="每个用例生成 N 次取均值（默认 1）。7B 生成有随机性，"
                         "faithfulness 建议 ≥2 次采样取均值（RAGAS 官方建议）")
    args = ap.parse_args()

    from roleplay.config import get_settings
    from roleplay.core.knowledge import build_knowledge_base, lore_namespace
    from roleplay.core.persona_prompt import resolve_knowledge_namespaces, build_rag_context

    s = get_settings()
    JUDGE_MODEL = s.llm_model
    kb = build_knowledge_base(s)
    ns = resolve_knowledge_namespaces(None, CHARACTER_ID) if False else [
        lore_namespace(CHARACTER_ID),
        f"lore_{CHARACTER_ID}_spoken",
        f"events:{CHARACTER_ID}",
        "episodic",
    ]

    print(f"RAGAS 2.0 评估  judge={JUDGE_MODEL}  时间={time.strftime('%Y-%m-%d %H:%M')}")
    print("=" * 78)

    cases = EVAL_CASES[:4] if args.quick else EVAL_CASES
    only = args.metric

    rows: list[dict] = []
    for case in cases:
        q = case["q"]
        # 检索（与生产同参数）
        chunks = await kb.asearch(
            q, top_k=s.top_k, namespaces=ns,
            hybrid=s.rag_hybrid, hybrid_alpha=s.rag_hybrid_alpha,
            candidate_mult=s.rag_hybrid_candidates,
        )
        # 与生产完全对齐：build_rag_context 内部会做相对分数过滤（_filter_chunks），
        # precision/recall 应测"真正进入 prompt 的内容"，否则会低估生产质量。
        ctx_str = build_rag_context(chunks)
        # 从过滤后的上下文文本重建"条目列表"（按【...】标题分隔的块）
        contexts = _split_context_blocks(ctx_str)

        # 真实生成（走项目 LLM + 生产 prompt 链路，与线上完全一致）
        from roleplay.core.llm.factory import build_llm
        from roleplay.core.persona_prompt import build_roleplay_prompt
        from roleplay.core.character_repo import get_default_character_repo
        llm = build_llm(s)
        repo = get_default_character_repo()
        system_p = build_roleplay_prompt(
            card_json=repo.card_json,
            fallback_prompt=None,
            default_card=None,
            message=q,
            chunks=chunks,
        )

        # 多次生成取均值（7B 生成有随机性，faithfulness/relevance 建议 repeat≥2）
        rep = max(1, args.repeat)
        answers: list[str] = []
        for ri in range(rep):
            try:
                resp = await llm.generate(system=system_p, user=q, temperature=s.llm_temperature)
                # 兼容返回 str 或 dict
                if isinstance(resp, str):
                    answers.append(resp)
                elif isinstance(resp, dict):
                    answers.append((resp.get("content") or resp.get("text") or resp.get("reply") or ""))
                else:
                    answers.append(str(resp or ""))
            except Exception as e:  # noqa: BLE001
                print(f"   生成失败: {e}")
        if not answers:
            continue
        answer = answers[0]
        print(f"\n── {q}" + (f"  ×{rep}" if rep > 1 else ""))
        print(f"   回答: {answer[:110]}")
        row = {"q": q, "answer": answer, "n_ctx": len(contexts)}

        def _mean(vals: list[float]) -> float:
            ok = [v for v in vals if v >= 0]
            return sum(ok) / len(ok) if ok else -1.0

        # 无法回答的用例用 refusal 衡量即可：拒答内容短，judge 会把"我不记得了"
        # 也拆成事实声明并判无据，faithfulness/relevance 对它语义不适用（会假性低分）。
        skip_faith = case.get("unanswerable", False)
        if only in (None, "faithfulness") and not skip_faith:
            vals = [score_faithfulness(q, contexts, a)[0] for a in answers]
            row["faithfulness"] = _mean(vals)
            if row["faithfulness"] >= 0:
                print(f"   Faithfulness       {row['faithfulness']:.2f}  (均值 {len([v for v in vals if v>=0])} 次)")
            else:
                print(f"   Faithfulness       —   (judge 异常)")
        if only in (None, "relevance") and not skip_faith:
            vals = [score_answer_relevance(q, a, case.get("core_terms", []))[0] for a in answers]
            row["relevance"] = _mean(vals)
            if row["relevance"] >= 0:
                print(f"   Answer Relevance   {row['relevance']:.2f}  (均值 {len([v for v in vals if v>=0])} 次)")
        # 开放式口吻场景题：precision/recall 依赖"事实型期望词"，对场景题不适用
        # （正确条目是"怎么回应"的示例，不含事实词），跳过以免产生假性 0 分。
        if case.get("scene"):
            row["precision"] = -1.0
            row["recall"] = -1.0
        elif only in (None, "precision"):
            v, d = score_context_precision(q, contexts, case.get("core_terms", []))
            row["precision"] = v
            if v >= 0:
                print(f"   Context Precision  {v:.2f}  ({d})")
        if only in (None, "recall") and not case.get("scene"):
            v, d = score_context_recall(contexts, case["reference"])
            row["recall"] = v
            if v >= 0:
                print(f"   Context Recall     {v:.2f}  ({d})")
        if only in (None, "multihop"):
            v, d = score_multihop(answer, case["must_cover"])
            row["multihop"] = v
            if v >= 0:
                print(f"   Multi-hop          {v:.2f}  ({d})")

        # 无法回答的问题：应拒答/表示不知，而非编造细节
        if case.get("unanswerable"):
            v, d = score_refusal(answer)
            row["refusal"] = v
            print(f"   拒答正确性         {v:.2f}  ({d})")
        rows.append(row)

    # 新鲜度
    if only in (None, "freshness"):
        ok, d = check_freshness()
        print(f"\n── Knowledge Freshness\n   {'✅' if ok else '⚠️'} {d}")

    # 汇总
    print("\n" + "=" * 78)
    targets = {
        "faithfulness": 0.90, "relevance": 0.85,
        "precision": 0.80, "recall": 0.75, "multihop": 0.66,
        "refusal": 0.80,
    }
    print(f"{'用例':<34}" + "".join(f"{k[:9]:>11}" for k in targets))
    print("-" * 78)
    for r in rows:
        line = f"{r['q'][:32]:<34}"
        for k in targets:
            v = r.get(k, -1)
            line += f"{'—':>11}" if v < 0 else f"{v:>11.2f}"
        print(line)
    print("-" * 78)

    print("\n指标达标情况（RAGAS 2.0 生产门槛）：")
    all_ok = True
    for k, t in targets.items():
        vals = [r[k] for r in rows if r.get(k, -1) >= 0]
        if not vals:
            continue
        mean = sum(vals) / len(vals)
        ok = mean >= t
        all_ok = all_ok and ok
        print(f"  {'✅' if ok else '❌'} {k:<14} 均值 {mean:.2f}  目标 ≥{t}")
    ok_fresh, _ = check_freshness()
    print(f"  {'✅' if ok_fresh else '❌'} {'freshness':<14} {'未过期' if ok_fresh else '已过期'}")

    out = ROOT / "deliverables" / "rag-eval-standard.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n明细已存: {out}")
    return 0 if all_ok and ok_fresh else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
