# -*- coding: utf-8 -*-
"""补入库脚本：把 视频文案/ 下"尚未入库"的转写 md 批量写入 lore 向量库。

用途：--no-ingest 进程（B/C）落盘的 md，事后串行补入库。
幂等：doc_id 已在 KB 的直接跳过；doc_id 从文件名解析（BV号 或 BV号_pN）。
元数据（url/uploader/pubdate）从 md 头部"来源/UP主"行解析。
"""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "scripts")
sys.path.insert(0, "src")

from bilibili_lore_ingest import (  # noqa: E402
    ROOT, _already_ingested, ingest_file)
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge import (  # noqa: E402
    build_knowledge_base, lore_namespace)

CHARACTER = "wu_ming_zhe"
MD_DIR = ROOT / "data" / "lore" / CHARACTER / "视频文案"
DOC_ID_RE = re.compile(r"^(BV1[A-Za-z0-9]{9}(?:_p\d+)?)_")


def parse_header(md_path):
    """从 md 头部解析 url / uploader / pubdate。"""
    url = uploader = pubdate = ""
    for line in md_path.read_text(encoding="utf-8").splitlines()[:8]:
        m = re.search(r"https://www\.bilibili\.com/video/\S+?(?=>|$)", line)
        if m and not url:
            url = m.group(0).rstrip("）)")
        if "UP主" in line:
            seg = line.split("UP主：", 1)[-1]
            uploader = seg.split("｜")[0].strip()
            m2 = re.search(r"发布：(\d{4}-\d{2}-\d{2})", line)
            if m2:
                pubdate = m2.group(1)
    return url, uploader, pubdate


def main() -> int:
    settings = get_settings()
    ns = lore_namespace(CHARACTER)
    kb = build_knowledge_base(settings)
    md_files = sorted(MD_DIR.glob("*.md"))
    print(f"扫描 {MD_DIR.name}：共 {len(md_files)} 个 md", flush=True)

    done = skipped = failed = 0
    for md in md_files:
        m = DOC_ID_RE.match(md.name)
        if not m:
            print(f"  [skip] 文件名无 doc_id：{md.name[:60]}", flush=True)
            skipped += 1
            continue
        doc_id = m.group(1)
        if _already_ingested(kb, ns, doc_id):
            skipped += 1
            continue
        bvid = doc_id.split("_p")[0]
        url, uploader, pubdate = parse_header(md)
        url = url or f"https://www.bilibili.com/video/{bvid}"
        try:
            r = ingest_file(kb, md, namespace=ns, character_id=CHARACTER,
                            chunk_size=settings.chunk_size, doc_id=doc_id,
                            extra_meta={"url": url, "uploader": uploader,
                                        "pubdate": pubdate,
                                        "source_type": "bilibili_transcript"})
            done += 1
            print(f"  [kb] {doc_id} → {r['stored']} 块", flush=True)
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"  [error] {doc_id}: {e}", flush=True)

    print(f"完成：新入库 {done} 个文件，跳过 {skipped}，失败 {failed}", flush=True)
    print(f"KB 当前块数：{kb.count().get(ns, 0)}", flush=True)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
