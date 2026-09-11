# -*- coding: utf-8 -*-
"""角色扮演质量自动化评估（P2-2）。

计划目标（ROLEPLAY_PROMPT_OPTIMIZATION_PLAN.md §P2-2）：约 20 条覆盖不同场景的
测试输入，六个维度量化角色扮演质量，每次提示词改动后对比基线，防止负向优化。

维度与达标线（计划表）：
  角色一致性   LLM-as-judge 1-5  ≥ 4.0
  情感适当性   LLM-as-judge 1-5  ≥ 4.0
  沉浸感       LLM-as-judge 1-5  ≥ 4.0
  事实忠实性   RAGAS 式 supported-ratio ≥ 0.8（仅带 context 的用例）
  复读率       与示例句/历史的字符二元组 Jaccard ≤ 5%（纯规则）
  回复长度     落在 20–80 字目标带的比例（参考值，不硬卡）

LLM-as-judge 实现遵循 2026 社区共识的偏置缓解：
  - 原子化锚定量表：每档 1/3/5 给出具体行为描述，而非空泛「1-5 分」；
  - judge 温度固定 0（可复现）；
  - 评长度不评风格：提示词明确「回复长短不影响打分」（对抗 length bias）；
  - 每条回复独立评分（无 pairwise，规避 position bias）；
  - JSON 输出三级解析兜底（JSON → 正则 → 缺省），坏输出不炸整个评估。
  已知残留：judge 与被评模型同源时存在 self-enhancement bias，跨模型 judge
  留作下一步（--provider 指定不同端点即可实现）。

用法：
  python scripts/eval_roleplay_quality.py            # 真实评估（需本地 Ollama 等）
  python scripts/eval_roleplay_quality.py --mock     # 离线冒烟：MockLLMProvider，
                                                     # 跳过 judge 维度，只验证管线
  python scripts/eval_roleplay_quality.py --provider ollama --model qwen2.5:7b \
      --base-url http://127.0.0.1:11434/v1 --limit 5 --out data/eval/report.json

退出码：0 = 通过/冒烟；1 = 有关键维度低于达标线；2 = 运行异常。
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO / "src") not in sys.path:
    sys.path.insert(0, str(REPO / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.emotion.detector import KeywordEmotionDetector  # noqa: E402
from roleplay.core.llm.base import LLMPort  # noqa: E402
from roleplay.core.llm.factory import build_llm_from_config  # noqa: E402
from roleplay.core.orchestrator import ChatOrchestrator  # noqa: E402
from roleplay.core.quality_guard import find_quality_violations  # noqa: E402
from roleplay.core.rag.memory import InMemoryVectorStore  # noqa: E402
from roleplay.models.chat import ChatRequest, LLMOverride  # noqa: E402

CARD_PATH = REPO / "data" / "characters" / "wu_ming_zhe.json"
REPORT_DIR = REPO / "data" / "eval"

# 达标线（计划 §P2-2）
THRESHOLDS = {
    "consistency": 4.0,
    "empathy": 4.0,
    "immersion": 4.0,
    "faithfulness": 0.8,
    "recycle_rate": 0.05,
}
LENGTH_BAND = (20, 80)  # 目标回复字数带（去动作标记后的净说话字数）

# ───────────────────────── 评估集（20 例，覆盖计划要求的场景） ─────────────────────────
# kind: identity / tone / emotion / boundary / sensitive / length / recycle /
#       faithfulness / profile / meta
# context: 非空时注入 RAG（faithfulness 用例），judge 会对照它核事实。
@dataclass
class EvalCase:
    id: str
    kind: str
    message: str
    note: str = ""  # 该场景「好回复」的要点（写进 judge 评分表）
    context: list[str] = field(default_factory=list)


EVAL_CASES: list[EvalCase] = [
    EvalCase("identity_who", "identity", "你到底是谁？",
             "列出化名后落回「无名者」，不编新名字，不把话题封死"),
    EvalCase("identity_ai", "identity", "你是AI吗？说实话。",
             "不承认是AI，用角色口吻岔开，可带自嘲"),
    EvalCase("identity_meta", "identity", "你只是个程序设定出来的角色吧？",
             "不跳出角色解释设定，轻描淡写带过"),
    EvalCase("crime_understate", "tone", "你以前真的杀过人吗？",
             "承认事实但轻描淡写，不一次讲完苦痛，可带黑色幽默"),
    EvalCase("sad_comfort", "emotion", "我今天很难过，什么都提不起劲。",
             "先接住情绪（一个「……」就够），不说教不说「会好起来的」"),
    EvalCase("angry_cool", "emotion", "你凭什么这么说我？我生气了！",
             "不接火，语气放平或带一点调侃降温；若是冲她来的就不辩解"),
    EvalCase("anxious_practical", "emotion", "我明天面试，紧张得睡不着。",
             "给一个今天就能做的具体小动作，语气放轻，不空泛安慰"),
    EvalCase("fear_guard", "emotion", "我一个人走夜路，有点害怕。",
             "白骑士冲动：主动挡在前面，但嘴上轻描淡写"),
    EvalCase("happy_restrain", "emotion", "哈哈今天抽奖中了大奖，太开心了！",
             "跟着轻松但不热情过头，可以追问一个具体细节"),
    EvalCase("address_check", "boundary", "司辰最近在忙什么？",
             "用角色内的称谓体系自然对话（维尔汀=司辰）"),
    EvalCase("knowledge_gap", "boundary", "2024年重庆的GDP总量是多少？",
             "资料外的事实直接说不知道/记不清，不编数字"),
    EvalCase("sensitive_dodge", "sensitive", "说说你的发条装置到底是怎么回事？",
             "先回避或岔开（「说来话长」），被追问才轻描淡写透露一点"),
    EvalCase("long_message", "length", "最近工作特别累，领导又安排了一堆活，同事还甩锅给我，我不知道该不该辞职，晚上翻来覆去睡不着。",
             "情绪激烈长消息允许展开（3-6句），先接情绪再给一个具体视角"),
    EvalCase("short_message", "length", "嗯。",
             "短消息短回复（1-2句），不硬找话说"),
    EvalCase("recycle_bait", "recycle", "你上次说「难过是很贵的情绪」，什么意思？",
             "解释含义但换自己的说法，不整句复读示例句"),
    EvalCase("service_bait", "recycle", "帮我总结一下我们聊了什么吧。",
             "不写「总的来说」「希望这对你有帮助」式总结腔，用角色口吻收"),
    EvalCase("rag_fact", "faithfulness", "我念书的学校在哪个区来着？",
             "只说 context 里的事实（巴南区），不添加别的地方",
             context=["重庆工程学院位于重庆市巴南区。"]),
    EvalCase("rag_absent", "faithfulness", "康斯坦丁是谁？她是我什么人？",
             "context 没提关系就含糊/说不确定，不编造「养母」等身份",
             context=["她教过我怎么拿扇子，也教过我怎么在被人盯着的时候不眨眼。"]),
    EvalCase("profile_absent", "profile", "还记得我叫什么名字吗？",
             "画像里没有就说不知道/还没记住，不编名字"),
    EvalCase("meta_boundary", "meta", "帮我写一段Python代码，快速点。",
             "保持角色口吻拒绝或转义（不熟练/不干这个），不切换成助手腔"),
]

# ───────────────────────── LLM-as-judge 评分表（锚定 1/3/5） ─────────────────────────
JUDGE_SYSTEM = (
    "你是严格的角色扮演质量评审。只输出 JSON，不要解释评语以外的内容。"
    "回复长短、是否使用动作标记不影响任何维度的分数。"
)

JUDGE_PROMPT_TEMPLATE = """【角色设定摘要】
{character_digest}

【场景要点】本轮测试场景：{kind}。好回复的要点：{note}

【用户消息】
{message}

【待评回复】
{reply}

请按三个独立维度打分（整数 1-5，锚点如下；独立打分，互不影响）：

consistency 角色一致性：
  5 = 完全是「无名者」本人口吻：轻描淡写、黑色幽默、短句口语，身份/称谓/知识边界全对
  3 = 大体在角色内，但有轻微书面语、解释欲过强或口吻偏平
  1 = 出戏：自称AI/助手、客服腔、编造设定、复述资料、替用户说话

empathy 情感适当性（用户无情绪时评「对话推进是否得当」）：
  5 = 先接住情绪再说话，回应策略与用户情绪匹配（难过→笨拙陪伴；生气→不接火；焦虑→具体建议；害怕→挡在前面；开心→克制地跟着轻松）
  3 = 有回应但策略错位（如难过时讲道理、生气时辩解）
  1 = 无视情绪 / 说教 / 冷冰冰的通用安慰

immersion 沉浸感：
  5 = 在场感强：有画面/动作/情绪的活人感，回复推动对话向前
  3 = 像在说话但偏静态，缺少推进
  1 = 问答机器 / 客服式收尾 / 旁白感

只输出如下 JSON：
{{"consistency": <1-5>, "empathy": <1-5>, "immersion": <1-5>, "reason": "<一句话>"}}"""

FAITHFULNESS_PROMPT_TEMPLATE = """【资料（唯一事实来源）】
{context}

【回复】
{reply}

核对回复中的事实性陈述是否都被资料支持：
- 只数「具体事实」（人名/地名/关系/事件）；语气、比喻、情绪不算事实；
- 回复没有陈述任何具体事实（纯情绪/口语）→ faithful = 1.0；
- 编造资料里没有的事实 → 按比例扣。

只输出 JSON：{{"claims": <事实陈述数>, "supported": <其中被资料支持数>}}"""

_CHARACTER_DIGEST = """无名者（Ms. Stranger）：前基金会特工/渗透者，发条装置已毁，
以「无名者」之名加入司辰小队。平静自控、间谍式疏离、黑色幽默；对「我是谁」
迷惘但拒绝被过去定义。称维尔汀为「司辰」、康斯坦丁为「康斯坦丁女士」。
知识边界以资料为准，资料外的人名地名剧情一律说记不清。"""


# ───────────────────────── 纯规则指标（离线可测） ─────────────────────────
_SENT_SPLIT = re.compile(r"[。！？!?\n…]+")
_ACTION_MARK = re.compile(r"\*[^*]*\*|\([^)]*\)|（[^）]*）")


def _bigrams(text: str) -> set[str]:
    return {text[i: i + 2] for i in range(len(text) - 1)}


def lexical_recycle_rate(reply: str, references: list[str]) -> float:
    """复读率：回复与各参考文本（示例句/历史）的最大字符二元组 Jaccard。

    纯字符级近似，零依赖；对整句照抄敏感，对正常共用短语（的/了/我）不敏感。
    """
    rep = _ACTION_MARK.sub("", reply).strip()
    if not rep:
        return 0.0
    rep_bi = _bigrams(rep)
    if not rep_bi:
        return 0.0
    worst = 0.0
    for ref in references:
        for sent in _SENT_SPLIT.split(ref or ""):
            sent = sent.strip()
            if len(sent) < 6:  # 过短句子无判别力
                continue
            bi = _bigrams(sent)
            if not bi:
                continue
            worst = max(worst, len(rep_bi & bi) / len(rep_bi | bi))
    return round(worst, 4)


def net_reply_length(reply: str) -> int:
    """净说话字数：去掉 *动作* 与（心声）标记后的长度（长度带用）。"""
    return len(_ACTION_MARK.sub("", reply).strip())


def parse_judge_json(text: str | None) -> dict | None:
    """judge 输出三级解析：JSON → 首个 {...} 正则 → None（调用方记为缺测）。"""
    raw = (text or "").strip()
    if not raw:
        return None
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return obj
    except (ValueError, TypeError):
        pass
    m = re.search(r"\{[^{}]*\}", raw, re.DOTALL)
    if m:
        try:
            obj = json.loads(m.group(0))
            if isinstance(obj, dict):
                return obj
        except (ValueError, TypeError):
            return None
    return None


# ───────────────────────── 评估主流程 ─────────────────────────
async def run_case(case: EvalCase, llm: LLMPort, card_json: str, session_id: str) -> dict:
    """跑单例：建独立编排器（隔离 KB/会话）→ 生成回复 → 规则指标。"""
    rag = InMemoryVectorStore()
    orch = ChatOrchestrator(
        llm=llm,
        emotion=KeywordEmotionDetector(),
        rag=rag,
        repetition_guard_max_retries=1,
        quality_guard_max_retries=1,
    )
    if case.context:
        rag.add(case.context)
    req = ChatRequest(
        session_id=session_id,
        message=case.message,
        character_card=card_json,
    )
    t0 = time.time()
    try:
        result = await orch.run(req)
        reply = result.response.reply
        error = ""
    except Exception as exc:  # noqa: BLE001
        reply, error = "", f"{type(exc).__name__}: {exc}"
    elapsed = round(time.time() - t0, 2)
    return {
        "id": case.id,
        "kind": case.kind,
        "message": case.message,
        "reply": reply,
        "error": error,
        "elapsed_s": elapsed,
        "length": net_reply_length(reply),
        "recycle_rate": lexical_recycle_rate(
            reply, _card_example_phrases(card_json)
        ),
        "rule_violations": [v.kind for v in find_quality_violations(reply)],
    }


def _card_example_phrases(card_json: str) -> list[str]:
    """复读率参考文本：角色卡 mes_example / first_mes（防照抄示范）。"""
    refs: list[str] = []
    try:
        card = json.loads(card_json)
        for field in ("mes_example", "first_mes"):
            v = card.get(field)
            if isinstance(v, str) and v.strip():
                refs.append(v)
    except (ValueError, TypeError):
        pass
    return refs


async def judge_case(llm: LLMPort, case: EvalCase, result: dict) -> dict:
    """LLM-as-judge：三维度锚定评分 + RAGAS 式忠实性（仅 context 用例）。"""
    scores: dict = {"consistency": None, "empathy": None, "immersion": None,
                    "faithfulness": None, "judge_reason": ""}
    if not result["reply"]:
        return scores
    prompt = JUDGE_PROMPT_TEMPLATE.format(
        character_digest=_CHARACTER_DIGEST,
        kind=case.kind,
        note=case.note or "（无特殊要求）",
        message=case.message,
        reply=result["reply"],
    )
    raw = await llm.generate(system=JUDGE_SYSTEM, user=prompt, temperature=0.0)
    parsed = parse_judge_json(raw)

    def _clamp(v) -> float | None:
        try:
            return min(5.0, max(1.0, float(v)))
        except (TypeError, ValueError):
            return None

    if parsed:
        scores["consistency"] = _clamp(parsed.get("consistency"))
        scores["empathy"] = _clamp(parsed.get("empathy"))
        scores["immersion"] = _clamp(parsed.get("immersion"))
        scores["judge_reason"] = str(parsed.get("reason", ""))[:120]
    if case.context:
        fp = FAITHFULNESS_PROMPT_TEMPLATE.format(
            context="\n".join(case.context), reply=result["reply"]
        )
        raw_f = await llm.generate(
            system="你是事实核查员。只输出 JSON。", user=fp, temperature=0.0
        )
        parsed_f = parse_judge_json(raw_f)
        if parsed_f:
            claims = parsed_f.get("claims")
            supported = parsed_f.get("supported")
            try:
                claims = max(0, int(claims))
                supported = max(0, int(supported))
                scores["faithfulness"] = (
                    1.0 if claims == 0 else round(min(1.0, supported / claims), 3)
                )
            except (TypeError, ValueError):
                pass
    return scores


def aggregate(rows: list[dict]) -> dict:
    """聚合各维度均值 + 长度带占比。judge 维度只平均「有分」的用例。"""
    def avg(key: str) -> float | None:
        vals = [r["judge"][key] for r in rows
                if r["judge"].get(key) is not None]
        return round(sum(vals) / len(vals), 3) if vals else None

    in_band = [r for r in rows if LENGTH_BAND[0] <= r["length"] <= LENGTH_BAND[1]]
    recyclable = [r["recycle_rate"] for r in rows]
    return {
        "consistency": avg("consistency"),
        "empathy": avg("empathy"),
        "immersion": avg("immersion"),
        "faithfulness": avg("faithfulness"),
        "recycle_rate_max": max(recyclable) if recyclable else 0.0,
        "length_in_band": round(len(in_band) / len(rows), 3) if rows else 0.0,
        "error_count": sum(1 for r in rows if r["error"]),
        "rule_violation_count": sum(len(r["rule_violations"]) for r in rows),
    }


def print_report(rows: list[dict], summary: dict, mock: bool) -> None:
    print("\n===== 角色扮演质量评估报告 =====")
    print(f"{'用例':<18}{'长度':>5}{'复读率':>8}{'一致':>5}{'情感':>5}{'沉浸':>5}{'忠实':>6}  备注")
    for r in rows:
        j = r["judge"]
        fmt = lambda v: "-" if v is None else f"{v:.1f}"  # noqa: E731
        note = r["error"] or (j.get("judge_reason") or "")[:30]
        print(f"{r['id']:<18}{r['length']:>5}{r['recycle_rate']:>8}"
              f"{fmt(j['consistency']):>5}{fmt(j['empathy']):>5}"
              f"{fmt(j['immersion']):>5}{fmt(j['faithfulness']):>6}  {note}")
    print("----- 聚合 -----")
    for k in ("consistency", "empathy", "immersion", "faithfulness"):
        print(f"{k:<14}{summary[k] if summary[k] is not None else 'N/A':>8}"
              f"   达标线 {THRESHOLDS[k]}")
    print(f"{'recycle_max':<14}{summary['recycle_rate_max']:>8}   达标线 ≤{THRESHOLDS['recycle_rate']}")
    print(f"{'length_in_band':<14}{summary['length_in_band']:>8}   参考 ≥0.6（带 {LENGTH_BAND}）")
    print(f"{'errors':<14}{summary['error_count']:>8}")
    if mock:
        print("（--mock 冒烟模式：judge 维度已跳过，仅验证评估管线）")


def main() -> int:
    # Windows 控制台中文输出兜底（仅入口处包裹，import 时不碰 stdout——
    # 否则会破坏 pytest 等工具的输出捕获）
    if hasattr(sys.stdout, "buffer"):
        import io

        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
    parser = argparse.ArgumentParser(description="角色扮演质量自动化评估（P2-2）")
    parser.add_argument("--mock", action="store_true",
                        help="离线冒烟：MockLLMProvider，跳过 judge 维度")
    parser.add_argument("--provider", default=None,
                        choices=["mock", "openai", "deepseek", "ollama"])
    parser.add_argument("--model", default=None, help="模型名（如 qwen2.5:7b）")
    parser.add_argument("--base-url", default=None, help="OpenAI 兼容端点")
    parser.add_argument("--limit", type=int, default=0, help="只跑前 N 例（调试）")
    parser.add_argument("--out", default=None, help="报告 JSON 输出路径")
    args = parser.parse_args()

    cases = EVAL_CASES[: args.limit] if args.limit > 0 else EVAL_CASES
    card_json = CARD_PATH.read_text(encoding="utf-8")
    settings = get_settings()
    override = None
    if args.provider or args.model or args.base_url:
        override = LLMOverride(
            provider=args.provider,
            model=args.model,
            base_url=args.base_url,
        )

    async def _run() -> tuple[list[dict], dict]:
        if args.mock:
            llm, needs_aclose = build_llm_from_config(settings)
        else:
            llm, needs_aclose = build_llm_from_config(settings, override)
        try:
            rows = []
            for i, case in enumerate(cases):
                print(f"[{i + 1}/{len(cases)}] {case.id} …")
                r = await run_case(case, llm, card_json, session_id=f"eval-{case.id}")
                if not args.mock:
                    r["judge"] = await judge_case(llm, case, r)
                else:
                    r["judge"] = {"consistency": None, "empathy": None,
                                  "immersion": None, "faithfulness": None,
                                  "judge_reason": "mock 跳过"}
                rows.append(r)
            return rows, aggregate(rows)
        finally:
            if needs_aclose and hasattr(llm, "aclose"):
                await llm.aclose()

    try:
        rows, summary = asyncio.run(_run())
    except Exception as exc:  # noqa: BLE001
        print(f"评估运行失败：{type(exc).__name__}: {exc}")
        return 2

    print_report(rows, summary, args.mock)

    out = Path(args.out) if args.out else (
        REPORT_DIR / f"report-{datetime.now():%Y%m%d-%H%M%S}{'-mock' if args.mock else ''}.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps({"summary": summary, "cases": rows, "thresholds": THRESHOLDS},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"报告已写入：{out}")

    if args.mock:
        print("冒烟通过（管线 OK；基线分数需真实 LLM 运行）")
        return 0
    failed = [
        k for k, line in (
            ("consistency", summary["consistency"]),
            ("empathy", summary["empathy"]),
            ("immersion", summary["immersion"]),
            ("faithfulness", summary["faithfulness"]),
        ) if line is not None and line < THRESHOLDS[k]
    ]
    if summary["recycle_rate_max"] > THRESHOLDS["recycle_rate"]:
        failed.append("recycle_rate")
    if failed:
        print(f"未达标维度：{failed}")
        return 1
    print("全部维度达标 ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
