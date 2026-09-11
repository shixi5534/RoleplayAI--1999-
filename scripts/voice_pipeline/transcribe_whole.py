# -*- coding: utf-8 -*-
"""整段听录（v3）：不做 ffmpeg 静音预切分，交给 whisper 内置 VAD 分段。

为什么不用预切分：silencedetect 会把一句台词内部的停顿切成两半（如
"An infiltrator knows how to move with a tide." / "to dance in the ocean of
secrets."），而 BGM 段的过长短又会造成整句漏识别。whisper 自带 VAD 按语义
窗口切分，得到的段落更接近"一句台词"。

用法:
  python transcribe_whole.py --in audio/zh_voice.mp4 --work work/zh_whole \\
      --prefix zh --lang zh --model C:/Users/Lenovo/.cache/whisper/medium
"""
import argparse
import json
import os
import re
import subprocess

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()

def build_af(highpass=100, lowpass=4000):
    """削弱 BGM：只留人声主要频带，再统一响度。

    游戏语音视频普遍垫 BGM，会干扰 whisper 的 VAD（把音乐间隙也算成语音，
    导致分段过长、句子被窗口从中间截断）。收窄到 100Hz~4kHz 的人声带后
    VAD 更接近真实停顿。
    """
    return (f"highpass=f={highpass},lowpass=f={lowpass},"
            "loudnorm=I=-16:TP=-1.5:LRA=11")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def extract_wav(in_path, out_wav, af):
    if os.path.isfile(out_wav) and os.path.getsize(out_wav) > 0:
        return out_wav
    p = run([FF, "-hide_banner", "-nostats", "-y", "-i", in_path,
             "-af", af, "-vn", "-ac", "1", "-ar", "16000",
             "-c:a", "pcm_s16le", out_wav])
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-800:])
    return out_wav


def flag_quality(text, lang, seg):
    flags = []
    if not text:
        return ["empty"]
    if re.findall(r"(.{2,4}?)\1{2,}", text):
        flags.append("repeat")
    if len(text) < 2:
        flags.append("too_short")
    if lang == "zh" and len(re.findall(r"[一-鿿]", text)) < max(1, len(text) // 4):
        flags.append("lang_mismatch")
    # whisper 官方阈值：压缩比 >2.4 或 平均对数概率 < -1.0 视为低质
    if seg.compression_ratio and seg.compression_ratio > 2.4:
        flags.append("high_compression")
    if seg.avg_logprob < -1.0:
        flags.append("low_conf")
    # 阈值放宽到 0.85：游戏语音垫 BGM，no_speech_prob 普遍偏高，
    # 0.6 会把大量可用台词误标为"可能无语音"
    if seg.no_speech_prob > 0.85:
        flags.append("maybe_no_speech")
    return sorted(set(flags))


SENT_END = (".", "?", "!", "。", "？", "！", "…")


def split_sentences(seg, max_words=45):
    """用词级时间戳把 whisper 的长段切成句子。

    whisper 默认按语音块分段，一段常含 3~5 句；RAG 与语音对齐都需要
    句子级粒度，故按结束标点（中英皆支持）断句，时间戳取首尾词。
    """
    words = list(getattr(seg, "words", None) or [])
    if not words:
        return [{"start": seg.start, "end": seg.end, "text": seg.text.strip()}]
    out, buf = [], []
    for w in words:
        buf.append(w)
        token = w.word.strip()
        hit = token.endswith(SENT_END) or len(buf) >= max_words
        # 避免把 "Mr." / "3.7" 这类误判为句尾
        if hit and token.endswith(".") and len(token) <= 2 and token[:-1].isdigit():
            hit = False
        if hit:
            text = "".join(x.word for x in buf).strip()
            if text:
                out.append({"start": buf[0].start, "end": buf[-1].end,
                            "text": text})
            buf = []
    if buf:
        text = "".join(x.word for x in buf).strip()
        if text:
            out.append({"start": buf[0].start, "end": buf[-1].end, "text": text})
    return out


def merge_fragments(segs, max_gap=3.0):
    """把被 whisper 30s 窗口从中间切断的碎片并回上一句。

    判据：上一段文本不以句末标点结尾，且与本段间隔 <= max_gap 秒。
    """
    out = []
    joiner = " "
    for s in segs:
        if out:
            prev = out[-1]
            gap = s["start"] - prev["end"]
            if not prev["text"].endswith(SENT_END) and gap <= max_gap:
                # whisper 的 word token 常缺句末标点，合并时若下一片以大写
                # 字母开头，补一个句号，避免多句被并成无句读的一长串
                if (s["text"][:1].isupper()
                        and not prev["text"].endswith((",", "，", ";", "、"))):
                    joiner = ". "
                else:
                    joiner = " "
                prev["text"] = (prev["text"] + joiner + s["text"]).strip()
                prev["end"] = s["end"]
                prev["dur"] = round(prev["end"] - prev["start"], 2)
                prev["flags"] = sorted(set(prev["flags"] + s["flags"]))
                continue
        out.append(dict(s))
    for i, s in enumerate(out):
        s["idx"] = i
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--lang", default=None)
    ap.add_argument("--model", required=True)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--compute", default="int8")
    ap.add_argument("--beam", type=int, default=5)
    ap.add_argument("--min-sil-ms", type=int, default=500)
    ap.add_argument("--no-split", action="store_true", help="不做句子级切分")
    ap.add_argument("--merge-gap", type=float, default=3.0)
    ap.add_argument("--highpass", type=int, default=100)
    ap.add_argument("--lowpass", type=int, default=4000)
    a = ap.parse_args()

    os.makedirs(a.work, exist_ok=True)
    wav = os.path.join(a.work, f"{a.prefix}_full_hp{a.highpass}_lp{a.lowpass}.wav")
    af = build_af(a.highpass, a.lowpass)
    print(f"[{a.prefix}] extracting wav  af={af}", flush=True)
    extract_wav(a.inp, wav, af)
    print(f"[{a.prefix}] wav {os.path.getsize(wav)/1e6:.1f}MB", flush=True)

    from faster_whisper import WhisperModel
    print(f"[{a.prefix}] loading {a.model} ...", flush=True)
    model = WhisperModel(a.model, device=a.device, compute_type=a.compute)

    it, info = model.transcribe(
        wav, language=a.lang, beam_size=a.beam,
        condition_on_previous_text=False,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": a.min_sil_ms},
        word_timestamps=not a.no_split,
        temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    print(f"[{a.prefix}] detected={info.language} "
          f"p={info.language_probability:.3f}", flush=True)

    segs = []
    for s in it:
        parts = ([{"start": s.start, "end": s.end, "text": s.text.strip()}]
                 if a.no_split else split_sentences(s))
        for p in parts:
            text = p["text"]
            segs.append({
                "idx": len(segs),
                "start": round(p["start"], 2),
                "end": round(p["end"], 2),
                "dur": round(p["end"] - p["start"], 2),
                "text": text,
                "avg_logprob": round(s.avg_logprob, 3),
                "no_speech_prob": round(s.no_speech_prob, 3),
                "compression_ratio": round(s.compression_ratio, 3),
                "flags": flag_quality(text, a.lang, s),
            })
            if text:
                print(f"  {p['start']:7.2f}-{p['end']:7.2f} {text[:70]}",
                      flush=True)

    if not a.no_split:
        before = len(segs)
        segs = merge_fragments(segs, a.merge_gap)
        print(f"[{a.prefix}] 碎片合并 {before} -> {len(segs)}", flush=True)

    json_path = os.path.join(a.work, f"{a.prefix}_whole.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"source": a.inp, "lang": a.lang, "model": a.model,
                   "detected": info.language,
                   "lang_prob": round(float(info.language_probability), 3),
                   "segments": segs}, f, ensure_ascii=False, indent=1)

    md_path = os.path.join(a.work, f"{a.prefix}_lines.md")
    lines = [f"# {a.prefix} 台词清单（整段听录）", "",
             f"- 源：{os.path.basename(a.inp)} ｜ 指定语言：{a.lang}"
             f" ｜ 检测：{info.language}({info.language_probability:.2f})"
             f" ｜ 模型：{os.path.basename(a.model)}",
             f"- 段落：{len(segs)}", "",
             "| # | 起 | 止 | 时长 | 文本 | 标记 |",
             "|---:|---:|---:|---:|---|---|"]
    for s in segs:
        t = (s["text"] or "").replace("|", "｜").replace("\n", " ")
        lines.append(f"| {s['idx']} | {s['start']:.2f} | {s['end']:.2f} | "
                     f"{s['dur']:.2f} | {t} | {' '.join(s['flags'])} |")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    bad = [s for s in segs if s["flags"]]
    print(f"[{a.prefix}] saved {json_path} / {md_path}")
    print(f"[{a.prefix}] 共 {len(segs)} 段，需复核 {len(bad)} 段")


if __name__ == "__main__":
    main()
