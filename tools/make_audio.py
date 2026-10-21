#!/usr/bin/env python3
"""Turn scripts/*.json into episodes/*.mp3 with Taiwanese Mandarin and American English voices.

Each script is {"title", "description", "pub", "queue": [[kind, value], ...]} where kind is
"zh" (Taiwanese Mandarin), "en" (American English, normal speed), "en-slow" (same voice, slower)
or "pause" (value in milliseconds). A script is rebuilt only when its content changes
(audio-manifest.json keeps a hash per script). Afterwards the feed and index page are rebuilt.

Requires: ffmpeg, pip install edge-tts numpy
"""
import asyncio
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import wave

import edge_tts
import numpy as np

SR = 24000
VOICES = {"zh": "zh-TW-HsiaoChenNeural", "en": "en-US-AriaNeural", "en-slow": "en-US-AriaNeural"}
RATES = {"zh": "+0%", "en": "+0%", "en-slow": "-25%"}

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)


def split_text(text, kind):
    if kind == "zh":
        parts = re.findall(r"[^。！？!?；;\n]+[。！？!?；;]?", text)
    else:
        parts = re.findall(r"[^.!?]+[.!?]*\s*", text)
    parts = [p.strip() for p in parts if p.strip()]
    return parts or [text]


def silence(ms):
    return np.zeros(int(SR * ms / 1000), dtype=np.float32)


async def synth(text, kind, voices, retries=5):
    last = None
    for attempt in range(retries):
        path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                path = f.name
            await edge_tts.Communicate(text, voices[kind], rate=RATES[kind]).save(path)
            raw = subprocess.run(
                ["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ar", str(SR), "-ac", "1", "-"],
                capture_output=True, check=True).stdout
            arr = np.frombuffer(raw, dtype=np.float32)
            if arr.size < SR * 0.1:
                raise RuntimeError("empty audio")
            return arr
        except Exception as e:  # network or service hiccup: back off and retry
            last = e
            print(f"retry {attempt + 1}: {kind} {text[:24]!r}: {e}", flush=True)
            await asyncio.sleep(2 * (attempt + 1))
        finally:
            if path and os.path.exists(path):
                os.unlink(path)
    raise SystemExit(f"TTS failed for {text[:40]!r}: {last}")


async def build_audio(script, out_mp3):
    voices = dict(VOICES)
    ov = script.get("voices", {})
    voices["zh"] = ov.get("zh", voices["zh"])
    voices["en"] = voices["en-slow"] = ov.get("en", voices["en"])
    chunks = []
    for kind, value in script["queue"]:
        if kind == "pause":
            chunks.append(silence(value))
            continue
        base = "zh" if kind == "zh" else "en"
        for part in split_text(value, base):
            chunks.append(await synth(part, kind, voices))
            chunks.append(silence(250))
    pcm = np.concatenate(chunks)
    pcm = pcm / max(1e-6, float(np.abs(pcm).max())) * 0.9
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "a.wav")
        with wave.open(wav, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((pcm * 32767).astype(np.int16).tobytes())
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                        "-codec:a", "libmp3lame", "-b:a", "96k", "-ar", "44100", out_mp3], check=True)
    return len(pcm) / SR


def main():
    manifest = {}
    if os.path.exists("audio-manifest.json"):
        manifest = json.load(open("audio-manifest.json", encoding="utf-8"))
    episodes = json.load(open("episodes.json", encoding="utf-8")) if os.path.exists("episodes.json") else []
    os.makedirs("episodes", exist_ok=True)
    changed = 0
    for path in sorted(glob.glob("scripts/*.json")):
        stem = os.path.splitext(os.path.basename(path))[0]
        raw = open(path, "rb").read()
        digest = hashlib.sha256(raw).hexdigest()
        out = f"episodes/{stem}.mp3"
        if manifest.get(stem) == digest and os.path.exists(out):
            continue
        script = json.loads(raw.decode("utf-8"))
        print("building", stem, flush=True)
        dur = asyncio.run(build_audio(script, out))
        entry = {"id": stem, "title": script["title"], "description": script["description"],
                 "file": out, "duration": int(dur), "pub": script["pub"]}
        episodes = [e for e in episodes if e["id"] != stem] + [entry]
        manifest[stem] = digest
        changed += 1
    json.dump(episodes, open("episodes.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(manifest, open("audio-manifest.json", "w", encoding="utf-8"), indent=2)
    subprocess.run([sys.executable, "tools/build_feed.py"], check=True)
    print("episodes built:", changed)


main()
