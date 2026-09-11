# -*- coding: utf-8 -*-
"""剧情图谱数据备份归档（只复制，绝不删除/移动源文件）。

背景（B5 空图覆盖事故的善后）：图谱/语料是 LLM 抽取的昂贵产物，重建一轮要
几千次抽取调用；而 ``GraphStore.save()`` 会把损坏文件固化成空图、``--rebuild``
会先删图再建。因此任何**可能写坏盘**的操作之前，都应先跑本脚本留一份快照。

归档内容（默认）：
  data/knowledge/plot_graph_<cid>.json    剧情图谱（实体/边/别名）
  data/knowledge/plot_corpus_<cid>.json   剧情语料（文本 + 元数据）
  data/lore/<cid>/plot_aliases.json       人工双语别名表
  data/lore/<cid>/plot_glossary.json      剧情术语对照表
  data/lore/<cid>/wiki_zh_en.json         wiki 中英对照

可选（``--include-cache``，默认关闭，因为有几千个小文件）：
  data/knowledge/plot_cache/<cid>/        抽取缓存（chunk hash → 抽取结果）

产物：
  data/knowledge/_archive/<YYYYmmdd_HHMMSS>/ 上述文件的副本
  data/knowledge/_archive/<YYYYmmdd_HHMMSS>/INDEX.md  含文件名/字节数/sha256/源路径

用法（项目根目录执行）：
  python scripts/archive_backup.py                        # 默认角色 wu_ming_zhe
  python scripts/archive_backup.py --character wu_ming_zhe
  python scripts/archive_backup.py --include-cache        # 连抽取缓存一起归档
  python scripts/archive_backup.py --archive-dir D:/bak   # 自定义归档根目录

退出码：0 成功（允许部分源文件缺失，缺失项会在 INDEX.md 里标注）；1 失败
（归档根目录不可写，或**一个文件都没复制成功**）。
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402


def _sha256(path: Path) -> str:
    """文件 sha256（分块读，大文件也不会一次性进内存）。"""
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for block in iter(lambda: fp.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _planned_files(settings, character_id: str) -> list[tuple[str, Path]]:
    """待归档清单：[(归档目录内的相对子目录, 源文件绝对路径)]。

    路径与 ``scripts/build_plot_graph.py`` 的 ``_paths()`` 保持同一套配置来源，
    避免两处对落盘位置的认知漂移。
    """
    lore_dir = Path(settings.plot_lore_dir) / character_id
    return [
        ("", Path(settings.plot_graph_dir) / f"plot_graph_{character_id}.json"),
        ("", Path(settings.plot_corpus_dir) / f"plot_corpus_{character_id}.json"),
        ("", lore_dir / "plot_aliases.json"),
        ("", lore_dir / "plot_glossary.json"),
        ("", lore_dir / "wiki_zh_en.json"),
    ]


def _copy_one(src: Path, dst_dir: Path) -> dict:
    """复制单个文件并采集元信息；源文件缺失不算失败，只标记 missing。"""
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    if not src.is_file():
        return {
            "name": src.name,
            "status": "missing",
            "bytes": 0,
            "sha256": "",
            "source": str(src),
            "archived": str(dst),
        }
    shutil.copy2(src, dst)  # copy2：连 mtime 一起带过去，便于人工辨认版本
    return {
        "name": src.name,
        "status": "ok",
        "bytes": dst.stat().st_size,
        "sha256": _sha256(dst),
        "source": str(src),
        "archived": str(dst),
    }


def _copy_tree(src_dir: Path, dst_dir: Path) -> tuple[int, int]:
    """整目录复制（抽取缓存用）。返回 (文件数, 总字节)。"""
    if not src_dir.is_dir():
        return 0, 0
    dst_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    total = 0
    for p in src_dir.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(src_dir)
        dst = dst_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        n += 1
        total += dst.stat().st_size
    return n, total


def _write_index(
    index_path: Path,
    *,
    character_id: str,
    created_at: str,
    archive_dir: Path,
    entries: list[dict],
    cache_info: dict,
) -> None:
    """写 INDEX.md：人工/脚本都能一眼看出归档了什么、校验值是多少。"""
    ok = [e for e in entries if e["status"] == "ok"]
    missing = [e for e in entries if e["status"] != "ok"]
    total_bytes = sum(e["bytes"] for e in ok) + int(cache_info.get("bytes") or 0)
    lines: list[str] = [
        "# 剧情图谱数据备份索引",
        "",
        f"- 角色：`{character_id}`",
        f"- 归档时间：{created_at}",
        f"- 归档目录：`{archive_dir}`",
        f"- 文件数：{len(ok)}（缺失 {len(missing)}）｜总字节：{total_bytes}",
        "- **本目录为只读副本**：脚本只做复制，不删除、不移动任何源文件。",
        "",
        "## 文件清单",
        "",
        "| 文件 | 状态 | 字节 | sha256 | 源路径 |",
        "|---|---|---|---|---|",
    ]
    for e in entries:
        if e["status"] == "ok":
            lines.append(
                f"| `{e['name']}` | ok | {e['bytes']} | `{e['sha256']}` | `{e['source']}` |"
            )
        else:
            lines.append(f"| `{e['name']}` | **缺失** | - | - | `{e['source']}` |")
    if cache_info.get("enabled"):
        lines += [
            "",
            "## 抽取缓存",
            "",
            f"- 源：`{cache_info.get('source')}`",
            f"- 归档：`{cache_info.get('archived')}`",
            f"- 文件数：{cache_info.get('files', 0)}｜总字节：{cache_info.get('bytes', 0)}",
        ]
    lines += [
        "",
        "## 恢复方式",
        "",
        "```bash",
        f"# 把某个文件还原回原位（确认当前文件已损坏时）",
        f"cp <归档目录>/plot_graph_{character_id}.json "
        f"{Path(entries[0]['source']).parent if entries else '.'}/",
        "```",
        "",
        "> 还原前先确认目标文件确实损坏（`GraphStore(path).load_error` 非空，"
        "或文件大小明显异常），不要把好数据覆盖成旧快照。",
    ]
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="剧情图谱数据备份归档（只复制，不删除/移动源文件）"
    )
    ap.add_argument("--character", default="wu_ming_zhe", help="角色 id")
    ap.add_argument(
        "--include-cache",
        action="store_true",
        help="一并归档抽取缓存目录（几千个小文件，默认关闭）",
    )
    ap.add_argument(
        "--archive-dir",
        default="",
        help="归档根目录（默认 data/knowledge/_archive）",
    )
    args = ap.parse_args()

    settings = get_settings()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = Path(args.archive_dir) if args.archive_dir else (
        Path(settings.plot_graph_dir) / "_archive"
    )
    archive_dir = base / stamp
    try:
        archive_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"[error] 归档目录不可创建：{archive_dir}（{exc}）")
        return 1
    if not archive_dir.is_dir():
        print(f"[error] 归档根目录不可写：{archive_dir}")
        return 1

    print(f"[archive] 角色 {args.character} → {archive_dir}")
    entries: list[dict] = []
    for _sub, src in _planned_files(settings, args.character):
        entry = _copy_one(src, archive_dir)
        entries.append(entry)
        if entry["status"] == "ok":
            print(f"[archive] ✓ {entry['name']}（{entry['bytes']} B）")
        else:
            print(f"[archive] - {entry['name']} 缺失，跳过（{src}）")

    cache_info: dict = {"enabled": False}
    if args.include_cache:
        src_cache = Path(settings.plot_cache_dir) / args.character
        dst_cache = archive_dir / "plot_cache" / args.character
        n, total = _copy_tree(src_cache, dst_cache)
        cache_info = {
            "enabled": True,
            "source": str(src_cache),
            "archived": str(dst_cache),
            "files": n,
            "bytes": total,
        }
        print(f"[archive] ✓ 抽取缓存 {n} 个文件（{total} B）")

    copied = [e for e in entries if e["status"] == "ok"]
    if not copied:
        print("[error] 一个文件都没归档成功：请确认角色 id 与数据目录是否正确")
        return 1

    index_path = archive_dir / "INDEX.md"
    _write_index(
        index_path,
        character_id=args.character,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        archive_dir=archive_dir,
        entries=entries,
        cache_info=cache_info,
    )
    print(f"[archive] 索引 → {index_path}")
    print(
        f"[archive] 完成：{len(copied)} 个文件"
        f"（缺失 {len(entries) - len(copied)}）｜源文件均未改动"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
