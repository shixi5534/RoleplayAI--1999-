# -*- coding: utf-8 -*-
"""剧情层候选重排（reranker）。

为什么需要（2026-09-16 通道归因实测）
    90 道缺口题中 **89 道是"融合失败"**——候选池里有证据块，但没进 final 的前几块。
    图传播通道每题产生约 17 块候选，而 final 只有 6~8 个位置；证据块被 RRF 压到底部。
    参数消融（max_edges / weight_semantic / node_specificity / max_hops）与
    **候选生成量上调**（semantic_top / mention cap / edges / chapter_top，见 IDEAS_LOG【23】）
    对 ``inject_pass`` **均无实质收益** ⇒ 瓶颈是"排序"，不是"候选量"。

    v2 证据（同日 23:20，`diag_rank_distribution.py`）：产品按 2400 字符装配只装得下
    约 2 块 ⇒ 证据块必须排进**前 2 名**才算数。当前分布：
    第 1 名 82 题｜第 2 名 42 题｜**第 3~8 名 76 题**｜无覆盖块 100 题。
    重排的理论可动靶子 = 76 + 26（第 9~30 名）= 102 题。

两个后端
    1. ``PlotReranker``（listwise LLM）—— **已验证无效**：
       qwen2.5:1.5b 全量 300 题 inject_pass 62.00% → 60.33%（−1.67 pt），
       失败模式是**把证据块往后挪**（小模型排序能力不足以纠正现有名次）。
    2. ``CrossEncoderReranker``（专用 Cross-Encoder）—— 本模块新增，主力方案。

设计要点
    - **安全降级**：任何异常（加载失败/推理异常/超时）→ **原序返回**，
      绝不拖垮主检索链路（与项目既有 fallback 风格一致）。
    - **零回归默认**：未显式开启时不构造对象，行为与改动前逐位一致。
    - ONNX 路线而非 torch：本机无 torch/transformers（只有 onnxruntime + tokenizers），
      且 HF 官方不可达（Tunnel 502）需走 hf-mirror 镜像。
"""
from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

_PROMPT = """你是一个检索结果重排器。给定一个「问题」和若干「候选资料片段」，
请判断每个片段能否帮助回答该问题，并按**相关度从高到低**排序。

只输出片段编号，用英文逗号分隔，不要输出任何解释。例如：3,1,4,2

问题：{query}

候选片段：
{items}

排序结果（只输出编号，如 3,1,4,2）："""


class CrossEncoderReranker:
    """ONNX Cross-Encoder 重排器（bge-reranker 系列，onnxruntime + tokenizers 实现）。

    与 ``PlotReranker`` 接口一致：``rerank(query, items, top_k=)``，失败一律原序降级。

    为什么不用 torch/transformers：本机没装（也不打算为一个实验动生产 venv 的依赖），
    HF 官方还不可达。ONNX 变体由 Xenova 导出，架构与原版一致。

    用法：
        CrossEncoderReranker(model_dir="models/bge-reranker-base-onnx",
                             onnx_file="onnx/model_int8.onnx")
    """

    def __init__(self, model_dir: str, onnx_file: str = "onnx/model_int8.onnx",
                 max_len: int = 512, max_chars: int = 1200,
                 intra_threads: int = 0) -> None:
        self.model_dir = model_dir
        self.onnx_file = onnx_file
        self.max_len = int(max_len)
        self.max_chars = int(max_chars)
        self.intra_threads = int(intra_threads)
        self._session = None
        self._tokenizer = None
        self._err: str | None = None

    # —— 延迟加载（失败只记一次，之后直接降级）——
    def _ensure(self) -> bool:
        if self._session is not None:
            return True
        if self._err is not None:
            return False
        try:
            from pathlib import Path

            import numpy as np
            import onnxruntime as ort
            from tokenizers import Tokenizer

            root = Path(self.model_dir)
            tok_path = root / "tokenizer.json"
            onnx_path = root / self.onnx_file
            if not tok_path.is_file():
                raise FileNotFoundError(f"tokenizer.json 不在 {root}")
            if not onnx_path.is_file():
                raise FileNotFoundError(f"{self.onnx_file} 不在 {root}")

            self._tokenizer = Tokenizer.from_file(str(tok_path))
            opts = ort.SessionOptions()
            if self.intra_threads > 0:
                opts.intra_op_num_threads = self.intra_threads
            self._session = ort.InferenceSession(
                str(onnx_path), opts, providers=["CPUExecutionProvider"])
            # 记录输入名，不同导出版本可能是 input_ids/attention_mask/token_type_ids 的子集
            self._input_names = [i.name for i in self._session.get_inputs()]
            self._np = np
            logger.info("Cross-Encoder 已加载：%s（输入 %s）",
                        onnx_path.name, ",".join(self._input_names))
            return True
        except Exception as exc:  # noqa: BLE001
            self._err = f"{type(exc).__name__}: {exc}"
            logger.warning("Cross-Encoder 加载失败（%s），重排降级为原序", self._err)
            return False

    def available(self) -> bool:
        return self._ensure()

    @property
    def last_error(self) -> str | None:
        return self._err

    def score_pair(self, query: str, text: str) -> float:
        """打分单个 (query, doc) 对；失败抛异常由调用方管。"""
        enc = self._tokenizer.encode(query, text)
        ids, type_ids = enc.ids, enc.type_ids
        ids = ids[: self.max_len]
        type_ids = type_ids[: self.max_len]
        mask = [1] * len(ids)
        np = self._np
        feed = {
            "input_ids": np.array([ids], dtype=np.int64),
            "attention_mask": np.array([mask], dtype=np.int64),
        }
        if "token_type_ids" in self._input_names:
            feed["token_type_ids"] = np.array([type_ids], dtype=np.int64)
        # 只喂模型真正声明的输入，避免多余键报错
        feed = {k: v for k, v in feed.items() if k in self._input_names}
        out = self._session.run(None, feed)[0]
        return float(np.asarray(out).reshape(-1)[0])

    def rerank(self, query: str, items: list, *, top_k: int | None = None) -> list:
        """``items``: ``[(score, chunk, extra)]``；返回同结构的新列表（失败原序）。"""
        if not query or len(items) <= 1 or not self._ensure():
            return items
        try:
            texts = []
            for _s, chunk, _m in items:
                t = " ".join(str(getattr(chunk, "text", "") or "").split())
                texts.append(t[: self.max_chars])
            scored = [(self.score_pair(query, t), i) for i, t in enumerate(texts)]
            scored.sort(key=lambda x: -x[0])
            out = [items[i] for _s, i in scored]
        except Exception as exc:  # noqa: BLE001
            logger.warning("Cross-Encoder 推理失败（%s），保持原序", exc)
            return items
        return out[:top_k] if top_k else out


class PlotReranker:
    """基于本地 Ollama LLM 的 listwise 重排器（失败即原序降级）。

    ⚠️ 2026-09-16 全量实测 **负收益**（inject −1.67 pt），保留仅作对照，勿用于生产。
    """

    def __init__(self, model: str, base_url: str = "http://localhost:11434",
                 timeout: float = 30.0, snippet_chars: int = 160) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)
        self.snippet_chars = int(snippet_chars)
        self._available: bool | None = None

    # —— 可用性探测（只探一次）——
    def available(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            names = {str(m.get("name") or "") for m in data.get("models", [])}
            self._available = any(n.split(":")[0] == self.model.split(":")[0] for n in names)
            if not self._available:
                logger.warning("重排模型 %s 不在 ollama 模型列表中，重排降级为原序", self.model)
        except Exception as exc:  # noqa: BLE001
            logger.warning("重排器可用性探测失败（%s），降级为原序", exc)
            self._available = False
        return self._available

    # —— 重排主入口 ——
    def rerank(self, query: str, items: list, *, top_k: int | None = None) -> list:
        """``items``: ``[(score, chunk, extra)]``；返回同结构的新列表（失败原序）。"""
        if not query or len(items) <= 1 or not self.available():
            return items
        try:
            order = self._ask(query, items)
        except Exception as exc:  # noqa: BLE001
            logger.warning("重排调用失败（%s），保持原序", exc)
            return items
        if not order:
            return items
        # 按模型给出的顺序重排；未提及的候选按原序接在后面（保证不丢候选）
        seen = set()
        result = []
        for idx in order:
            if 0 <= idx < len(items) and idx not in seen:
                seen.add(idx)
                result.append(items[idx])
        for i, it in enumerate(items):
            if i not in seen:
                result.append(it)
        return result[:top_k] if top_k else result

    # —— 与 ollama 交互 ——
    def _ask(self, query: str, items: list) -> list[int]:
        lines = []
        for i, (_s, chunk, _m) in enumerate(items):
            text = " ".join(str(getattr(chunk, "text", "") or "").split())
            lines.append(f"[{i + 1}] {text[:self.snippet_chars]}")
        prompt = _PROMPT.format(query=query, items="\n".join(lines))
        body = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0, "num_predict": 32},
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/generate", data=body,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        raw = str(data.get("response") or "")
        nums = [int(n) - 1 for n in re.findall(r"\d+", raw)]
        # 过滤越界，保持出现顺序
        return [n for n in nums if 0 <= n < len(items)]
