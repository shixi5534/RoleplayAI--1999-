# -*- coding: utf-8 -*-
"""采样探测每个音频的主语言（不强制 language，交给 whisper 判断）。"""
import json
import os
import subprocess
import sys

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
TMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_probe")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def duration(path):
    p = run([FF, "-hide_banner", "-i", path])
    import re
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", p.stderr or "")
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def sample(path, start, length, out):
    run([FF, "-hide_banner", "-nostats", "-y", "-ss", f"{start:.2f}",
         "-t", f"{length:.2f}", "-i", path, "-vn", "-ac", "1", "-ar", "16000",
         "-c:a", "pcm_s16le", out])
    return out


def main():
    model_size = sys.argv[1] if len(sys.argv) > 1 else "base"
    from faster_whisper import WhisperModel
    print(f"loading model {model_size} ...", flush=True)
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    os.makedirs(TMP, exist_ok=True)

    result = {}
    for name in ["full_voice.mp4", "zh_voice.mp4", "skin_voice.mp4"]:
        path = os.path.join(AUDIO, name)
        if not os.path.isfile(path):
            print("missing", name)
            continue
        dur = duration(path)
        # 在 10%/40%/70% 三处各取 25s
        votes = []
        for frac in (0.10, 0.40, 0.70):
            st = max(0.0, dur * frac - 12)
            wav = sample(path, st, 25, os.path.join(TMP, f"{name}_{int(frac*100)}.wav"))
            _, info = model.transcribe(wav, beam_size=1)
            votes.append((round(info.language_probability, 3), info.language))
            print(f"  {name} @{int(frac*100)}% -> {info.language} "
                  f"p={info.language_probability:.3f}", flush=True)
        langs = {}
        for p, lg in votes:
            langs[lg] = langs.get(lg, 0) + 1
        main_lang = max(langs.items(), key=lambda kv: kv[1])[0]
        result[name] = {"duration": round(dur, 1), "votes": votes, "main": main_lang}
        print(f"[{name}] dur={dur:.1f}s MAIN={main_lang} votes={votes}", flush=True)

    with open(os.path.join(os.path.dirname(TMP), "lang_probe.json"), "w",
              encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("saved lang_probe.json")


if __name__ == "__main__":
    main()
