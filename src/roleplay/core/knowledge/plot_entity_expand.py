# -*- coding: utf-8 -*-
"""查询侧实体扩展：把「中文描述」补成「正典实体名」再检索。

为什么需要（2026-09-17 实测）
    失分 114 题里 **58.8%（67 题）是「正例不在候选池」**——查询里根本没有实体名，
    而证据块里要匹配的是**英文专名**（Zanetta / troll / Apeiron）。
    把正确答案的实体名拼进查询（作弊上界）可让 `inject_pass` 62.00% → 87.67%；
    用「强模型从正典名单识别实体」实现后实测 **62.00% → 69.00%（+7.00pt，p<0.0001，零倒退）**。

三条护栏（缺一不可，否则不许上线）
    1. **白名单**：输出必须能解析到图谱/正典里的实体，解析不到就丢弃
       —— 绝不允许模型自由发挥。
    2. **失败即不扩展**：任何异常 / 超时 / 空结果 / 未启用 ⇒ 返回**原查询**，
       行为与改动前逐位一致（零回归）。
    3. **独立开关**：默认关闭；且不得复用 `plot_semantic_rerank_*`
       （那三项是「查询 × 实体摘要」的种子护栏，语义完全不同）。

阈值说明
    实测「不设阈值」最优：`low` 档识别率虽只 43.6%，但体量大，
    贡献了总收益的 43%（全档 +7.00pt vs 只 high+mid +4.00pt）。
    识别错误的代价小（多加几个词）、识别正确的收益大 ⇒ 默认不设阈值。

用法（由 PlotGraphRetriever 在开关打开时构造）：
    exp = EntityExpander(identifier=StaticMapIdentifier(path), resolver=resolve)
    new_query = exp.expand("洞穴的囚徒篇里向维尔汀递交钥匙的管家是谁")
"""
from __future__ import annotations

import json
import logging
import urllib.request
from pathlib import Path
from typing import Protocol

logger = logging.getLogger(__name__)

CONF_FLOAT = {"high": 0.9, "mid": 0.7, "low": 0.4}


def norm(s: str) -> str:
    return " ".join(str(s or "").strip().lower().split())


class Identifier(Protocol):
    """实体识别后端接口：给查询与候选名单，返回 [(名字, 置信度)]。"""

    def identify(self, query: str, names: list[str]) -> list[tuple[str, float]]: ...


class NullIdentifier:
    """空后端：永远不产出实体（等价于功能关闭）。"""

    def identify(self, query: str, names: list[str]) -> list[tuple[str, float]]:  # noqa: ARG002
        return []


class StaticMapIdentifier:
    """静态映射后端：从 JSON 读 `{query: [{"name":..., "conf":"high"}...]}`。

    用途：离线回放（把已标注好的预测灌进来验证组件），以及成本敏感场景下的
    「预生成映射」。**不适合**处理未见过的查询 —— 那种场景要用 :class:`LLMEntityIdentifier`。
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._map: dict[str, list[tuple[str, float]]] = {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            logger.warning("实体扩展静态映射加载失败（%s），本后端将不产出实体", exc)
            data = {}
        for q, picks in (data.get("map") or data).items():
            out: list[tuple[str, float]] = []
            for it in picks or []:
                if isinstance(it, str):
                    out.append((it, 1.0))
                elif isinstance(it, dict) and it.get("name"):
                    out.append((str(it["name"]),
                                float(it.get("conf_num",
                                             CONF_FLOAT.get(str(it.get("conf") or ""), 0.5)))))
            if out:
                self._map[norm(q)] = out

    def identify(self, query: str, names: list[str]) -> list[tuple[str, float]]:  # noqa: ARG002
        return list(self._map.get(norm(query), []))


class LLMEntityIdentifier:
    """LLM 后端：走 OpenAI 兼容接口，给「查询 + 正典名单」，要求返回实体名。

    与本地 qwen2.5:7b 的对比实测：**本地 7b 只有 15.0% 命中率**（不懂该作品设定），
    强模型 62.7%。所以这个后端必须接**懂该作品设定的模型**，否则等于没做。
    """

    def __init__(self, base_url: str, api_key: str, model: str,
                 timeout: float = 20.0, top_k: int = 3, max_names: int = 400) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = float(timeout)
        self.top_k = int(top_k)
        self.max_names = int(max_names)

    def identify(self, query: str, names: list[str]) -> list[tuple[str, float]]:
        roster = "、".join(names[: self.max_names])
        prompt = (
            "以下是《重返未来：1999》的正典角色/组织名单：\n"
            f"{roster}\n\n"
            f"用户问题：{query}\n\n"
            f"请从上面的名单中选出最可能出现在答案里的 {self.top_k} 个名字。"
            "只输出名字，用顿号或逗号分隔；若问题与该作品无关，输出「无」。\n"
            "答案："
        )
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 64,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions", data=body,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self.api_key}"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        raw = str(((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "")
        if "无" == raw.strip():
            return []
        parts = [x.strip() for x in raw.replace("，", ",").replace("、", ",").split(",")]
        return [(x, 1.0) for x in parts[: self.top_k] if x]


class EntityExpander:
    """把识别出的实体名拼到查询尾部；带白名单校验与失败降级。

    白名单来源很关键：**必须是「检索器实际能链接到的名字表」**（图谱正名 + 别名），
    而不是只取正典角色名单——否则 `troll` / `umbrella` 这类**非角色的证据词**
    （它们确实是有效扩展词）会被误挡。
    因此提供 :meth:`bind_store`，由 `PlotGraphRetriever.__init__` 在拿到 store 后调用。
    """

    def __init__(self, identifier: Identifier,
                 resolver=None,               # Callable[[str], str | None]；None 时靠 bind_store 建
                 names: list[str] | None = None,
                 top_k: int = 3,
                 min_conf: float = 0.0,
                 max_append: int = 4,
                 enforce_whitelist: bool = True) -> None:
        self.identifier = identifier
        self.resolver = resolver
        self.names = list(names or [])
        self.top_k = max(1, int(top_k))
        self.min_conf = float(min_conf)
        self.max_append = max(1, int(max_append))
        self.enforce_whitelist = bool(enforce_whitelist)
        self.stats = {"calls": 0, "produced": 0, "appended": 0,
                      "rejected": 0, "errors": 0, "no_resolver": 0}

    # —— 白名单绑定（由检索器在拿到图谱后调用）——
    def bind_store(self, store) -> None:
        """用图谱的 正名+别名 建归一化映射；同时把名单交给 LLM 后端做候选表。"""
        try:
            m: dict[str, str] = {}
            roster: list[str] = []
            for ent in (store.entities() or []):
                name = str((ent or {}).get("name") or "").strip()
                if not name:
                    continue
                canon = name
                m.setdefault(norm(name), canon)
                roster.append(name)
                for a in ((ent or {}).get("aliases") or []):
                    a = str(a).strip()
                    if a:
                        m.setdefault(norm(a), canon)
            self._name_map = m
            if not self.names:
                self.names = roster
            logger.info("实体扩展白名单已绑定：%d 个归一名字 → %d 个正名",
                        len(m), len({v for v in m.values()}))
        except Exception as exc:  # noqa: BLE001
            self._name_map = {}
            logger.warning("实体扩展白名单绑定失败（%s）：将退化为不做白名单校验", exc)

    def _resolve(self, name: str) -> str | None:
        if self.resolver is not None:
            return self.resolver(name)
        if not self.enforce_whitelist:
            return str(name).strip() or None      # 不校验：原样透传
        m = getattr(self, "_name_map", None)
        if not m:
            self.stats["no_resolver"] += 1
            return None                            # 没白名单就不扩展（保守）
        return m.get(norm(name))

    def expand(self, query: str) -> str:
        """返回扩展后的查询。**任何异常都返回原查询**（零回归）。"""
        if not query:
            return query
        try:
            self.stats["calls"] += 1
            picks = self.identifier.identify(query, self.names) or []
            if not picks:
                return query
            self.stats["produced"] += 1
            resolved: list[str] = []
            for name, conf in picks:
                if conf < self.min_conf:
                    continue
                canon = self._resolve(name)
                if not canon:
                    # 白名单不通过 —— 丢弃，绝不让模型自由发挥
                    self.stats["rejected"] += 1
                    continue
                if norm(canon) in {norm(x) for x in resolved}:
                    continue
                resolved.append(canon)
                if len(resolved) >= self.max_append:
                    break
            if not resolved:
                return query
            self.stats["appended"] += 1
            return f"{query} {' '.join(resolved)}"
        except Exception as exc:  # noqa: BLE001 —— 永不拖垮检索
            self.stats["errors"] += 1
            logger.warning("实体扩展失败（%s），按原查询检索", exc)
            return query
