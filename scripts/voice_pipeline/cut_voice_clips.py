# -*- coding: utf-8 -*-
"""按台词时序表切分语音片段（中英双配音），供宠物前端点击互动播放。

输入：data/voice/wu_ming_zhe/{zh,en}_voice_lines.json（听录+校正产物，含起止时间）
     + 原始音频（zh_voice.mp4 / full_voice.mp4）
输出：frontend/assets/voice/wu_ming_zhe/{zh,en}/NN.mp3
     frontend/assets/voice/wu_ming_zhe/manifest.json
       - clips：两种语言的全部片段，每条带 subtitle:{zh,en}（双语字幕文本）
       - slots：语义槽位 → 两种语言的片段 id 列表

用法（项目根目录）：
  python scripts/voice_pipeline/cut_voice_clips.py
  python scripts/voice_pipeline/cut_voice_clips.py --force   # 重切
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[2]
FF = imageio_ffmpeg.get_ffmpeg_exe()

VOICE_DIR = ROOT / "data" / "voice" / "wu_ming_zhe"
OUT_DIR = ROOT / "frontend" / "assets" / "voice" / "wu_ming_zhe"
DEFAULT_ZH_SRC = VOICE_DIR / "source" / "zh_voice.mp4"
DEFAULT_EN_SRC = VOICE_DIR / "source" / "full_voice.mp4"

# ── 中英逐句对齐表 ──────────────────────────────────────────────────────
# zh idx → en idx 列表（同一套台词的中/英配音，时间轴与分段粒度不同，
# 依据语义人工对齐；空列表表示该句英文版被合并/缺失，字幕只显示中文）。
ZH_EN_ALIGN: dict[int, list[int]] = {
    0: [0, 1], 1: [2, 3, 4, 5, 6], 2: [7, 8], 3: [9], 4: [10, 11, 12],
    5: [13, 14], 6: [15], 7: [16, 17, 18], 8: [19], 9: [20, 21],
    10: [22, 23], 11: [24, 25], 12: [26], 13: [27, 28], 14: [29, 30],
    15: [31, 32, 33], 16: [34, 35], 17: [36, 37, 38], 18: [39], 19: [40],
    20: [41, 42, 43], 21: [], 22: [44, 45, 46], 23: [47], 24: [48],
    25: [49], 26: [50], 27: [51], 28: [52], 29: [53], 30: [54],
    31: [55], 32: [56], 33: [57], 34: [58], 35: [59, 60], 36: [61],
    37: [62, 63], 38: [64], 39: [65], 40: [66, 67], 41: [68], 42: [69],
    43: [70, 71, 72, 73], 44: [74, 75, 76, 77, 78, 79, 80], 45: [81],
    46: [82, 83], 47: [84],
}

# 语义槽位 → zh 台词 idx（en 槽位由对齐表推导）
SLOT_MAP: dict[str, list[int]] = {
    "enter": [0],                        # 进场：初见自我介绍
    "click": [7, 8, 16, 21, 41],         # 点击：问候/文书/飞虫/烟幕弹
    "happy": [5, 9, 10, 18, 20],         # 开心：岛上看看/早餐/自由/淑女仪态
    "sad": [1, 2, 31, 32, 45],           # 低落：求救的回忆/工具的记忆/被遗弃的飞蛾
    "surprise": [27, 37],                # 意外：击败阿卡纳/趋光性定律
    "sleep": [11, 12],                   # 睡眠：失眠往事/劝早点睡
    "idle": [3, 4, 13, 14, 15, 24, 25],  # 待机闲聊：身份/故乡/夜晚/飞虫/观察
    "intel": [34, 35, 36],               # 情报：基金会密文
    "battle": [43, 44],                  # 战斗：闭上眼/至终的仪式
}


def cut_one(src: Path, start: float, dur: float, out: Path) -> bool:
    """按起止时间切单段 mp3（64kbps mono，语音够用）。"""
    pad_head, pad_tail = 0.05, 0.18
    cmd = [FF, "-hide_banner", "-nostats", "-loglevel", "error", "-y",
           "-ss", f"{max(0.0, start - pad_head):.3f}",
           "-t", f"{dur + pad_head + pad_tail:.3f}",
           "-i", str(src),
           "-vn", "-ac", "1", "-b:a", "64k", str(out)]
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode == 0 and out.is_file() and out.stat().st_size > 1000


def load_lang(lang: str) -> list[dict]:
    f = VOICE_DIR / f"{lang}_voice_lines.json"
    data = json.load(open(f, encoding="utf-8"))
    return [s for s in data["segments"] if s.get("text")]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zh-src", default=str(DEFAULT_ZH_SRC))
    ap.add_argument("--en-src", default=str(DEFAULT_EN_SRC))
    ap.add_argument("--force", action="store_true", help="重切已存在的片段")
    a = ap.parse_args()

    texts: dict[str, dict[int, str]] = {"zh": {}, "en": {}}
    clips: list[dict] = []

    # ── 切两种语言的音频 ────────────────────────────────────────────
    for lang, src in (("zh", Path(a.zh_src)), ("en", Path(a.en_src))):
        if not src.is_file():
            print(f"[error] {lang} 源音频不存在：{src}", file=sys.stderr)
            return 1
        segs = load_lang(lang)
        out_dir = OUT_DIR / lang
        out_dir.mkdir(parents=True, exist_ok=True)
        n = 0
        for s in segs:
            idx = s["idx"]
            texts[lang][idx] = s["text"]
            out = out_dir / f"{idx:02d}.mp3"
            if a.force or not out.is_file():
                if not cut_one(src, s["start"], s["dur"], out):
                    print(f"[warn] 切分失败 {lang} idx={idx}，跳过")
                    continue
            n += 1
            clips.append({
                "id": f"{lang}_{idx:02d}",
                "lang": lang,
                "file": f"{lang}/{idx:02d}.mp3",
                "start": s["start"], "end": s["end"],
                "dur": round(s["end"] - s["start"], 2),  # 片段时长（秒），前端字幕计时用
                "text": s["text"],
            })
        print(f"[cut] {lang}: {n} 段 → {out_dir}")

    # ── 双语字幕：zh clip 附对齐英文，en clip 附对齐中文 ─────────────
    en_text = texts["en"]
    zh_text = texts["zh"]
    en_of_zh: dict[int, list[int]] = {}
    zh_of_en: dict[int, int] = {}
    for z, e_ids in ZH_EN_ALIGN.items():
        if z in zh_text:
            en_of_zh[z] = [e for e in e_ids if e in en_text]
            for e in e_ids:
                zh_of_en.setdefault(e, z)
    for c in clips:
        if c["lang"] == "zh":
            z = int(c["id"].split("_")[1])
            en_join = " ".join(en_text[e] for e in en_of_zh.get(z, []))
            c["subtitle"] = {"zh": zh_text.get(z, c["text"]), "en": en_join}
        else:
            e = int(c["id"].split("_")[1])
            z = zh_of_en.get(e)
            c["subtitle"] = {
                "zh": zh_text.get(z, "") if z is not None else "",
                "en": en_text.get(e, c["text"]),
            }

    # ── 槽位映射：zh 按 SLOT_MAP，en 由对齐表推导 ────────────────────
    slots: dict[str, list[str]] = {}
    for name, zh_ids in SLOT_MAP.items():
        ids = [f"zh_{i:02d}" for i in zh_ids if i in zh_text]
        en_ids: list[int] = []
        for i in zh_ids:
            en_ids.extend(en_of_zh.get(i, []))
        # 去重保序
        seen: set[int] = set()
        en_ids = [e for e in en_ids if e in en_text and e not in seen
                  and not seen.add(e)]
        ids += [f"en_{e:02d}" for e in en_ids]
        slots[name] = ids

    manifest = {
        "character": "wu_ming_zhe",
        "version": int(time.time()),  # manifest 生成时间戳（缓存失效/前端校验用）
        "langs": ["zh", "en"],
        "source": {
            "zh": "BV1nYG16hEfh（B站·无名者中配全语音）",
            "en": "BV1e4Gd6LEuz（B站·无名者英配全语音）",
        },
        "pipeline": "faster-whisper medium 听录 → 中英对照校正 → ffmpeg 切分 → 语义对齐",
        "clips": clips,
        "slots": slots,
    }
    out_manifest = OUT_DIR / "manifest.json"
    json.dump(manifest, open(out_manifest, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    total_kb = sum(f.stat().st_size for f in OUT_DIR.rglob("*.mp3")) / 1024
    print(f"[done] clips={len(clips)}（zh {len(zh_text)} / en {len(en_text)}）")
    print(f"[done] manifest → {out_manifest}（总大小 {total_kb:.0f} KB）")
    for name, ids in slots.items():
        print(f"  slot {name}: {ids}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
