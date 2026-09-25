# -*- coding: utf-8 -*-
"""验证「整批性故障 → 优雅收尾 → 续跑」这条链路（用假端点，不依赖真配额）。

目的：排除故障之前就把续跑逻辑验证通过，避免恢复后又踩坑。

⚠ **必须在临时目录里跑**：早期版本忘了覆盖 ``data_dir``，于是 Settings 落到
真实的 ``data/compendium_rag/``，收尾的 rmtree 把 698 块真实抽取缓存删了
（云端已付费的产物）。现在加了硬断言：data_dir 必须在本脚本自己的临时目录下，
否则直接拒绝运行。
"""
from __future__ import annotations

import asyncio
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import Settings  # noqa: E402
from compendium_rag.extract import (PROMPT_VERSION, ExtractionCache,  # noqa: E402
                                    cache_key)

REAL_DATA_DIR = (ROOT / "data" / "compendium_rag").resolve()


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="cmprag_resume_test_"))
    s = Settings(
        data_dir=tmp / "kb",                     # ← 关键：绝不碰真实数据目录
        llm_base_url="http://127.0.0.1:9/v1",    # 必然连接失败
        llm_api_key="dummy",
        llm_model="test-model",
        llm_concurrency=8,
        llm_max_retries=3,
        llm_timeout=2.0,
    )

    # 硬保险：data_dir 不得指向真实目录
    resolved = s.data_dir.resolve()
    assert REAL_DATA_DIR not in resolved.parents and resolved != REAL_DATA_DIR, \
        f"拒绝运行：data_dir 指向真实数据目录 {s.data_dir}"
    print(f"临时数据目录 = {s.data_dir}")

    try:
        s.ensure_dirs()
        chunks = P.load_chunks(s)[:40]
        print(f"测试块数 = {len(chunks)}  端点 = {s.llm_base_url}")

        cache = ExtractionCache(s.cache_dir)
        for c in chunks[:10]:
            cache.put_raw(cache_key(c, s.llm_model, PROMPT_VERSION),
                          {"entities": [{"name": "维尔汀", "type": "角色"}],
                           "relations": []})
        print("预置缓存 = 10 块")

        t0 = time.time()
        results, rep = asyncio.run(P.extract_all(s, chunks))
        dt = time.time() - t0
        sumry = P.extraction_summary(results)
        print(f"\n耗时 {dt:.1f}s")
        print(f"报告：缓存命中={rep.cache_hits} "
              f"待抽取={rep.stages['extract']['todo']} "
              f"成功={rep.extracted} 失败={rep.failed}")
        print(f"usage：{rep.usage}")

        ok_cached = sum(1 for c in chunks[:10] if results.get(c.chunk_id)
                        and results[c.chunk_id].ok)
        assert rep.cache_hits == 10, "缓存命中数不对"
        assert ok_cached == 10, "缓存块未被正确复用"
        print(f"\n预置的 10 块被正确复用：{ok_cached}/10")

        calls = rep.usage.get("calls", 0)
        retries = rep.usage.get("retries", 0)
        print(f"网关调用={calls}  重试={retries}（空转时会是 30 块 × 3 次 = 90）")
        assert retries <= 3, f"仍在空转重试：{retries} 次"
        print("✅ 未空转：整批性故障被快速识别并收尾")

        results2, rep2 = asyncio.run(P.extract_all(s, chunks))
        assert rep2.cache_hits == 10, "二次运行的缓存命中应一致"
        print("✅ 重跑幂等：缓存命中仍为 10")
        return 0
    finally:
        # 只删自己创建的临时目录（并再次确认不是真实目录）
        assert REAL_DATA_DIR not in tmp.resolve().parents
        shutil.rmtree(tmp, ignore_errors=True)
        print("清理临时数据完成")


if __name__ == "__main__":
    sys.exit(main())

