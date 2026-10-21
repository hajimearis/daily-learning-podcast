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
import random
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


async def synth(text, kind, voices, pitches, rates, retries=9):
    last = None
    for attempt in range(retries):
        path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                path = f.name
            await edge_tts.Communicate(text, voices[kind], rate=rates[kind], pitch=pitches[kind]).save(path)
            raw = subprocess.run(
                ["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ar", str(SR), "-ac", "1", "-"],
                capture_output=True, check=True).stdout
            arr = np.frombuffer(raw, dtype=np.float32)
            if arr.size < SR * 0.1:
                raise RuntimeError("empty audio")
            await asyncio.sleep(0.15)
            return arr
        except Exception as e:  # network or service hiccup: back off and retry
            last = e
            print(f"retry {attempt + 1}: {kind} {text[:24]!r}: {e}", flush=True)
            await asyncio.sleep(min(45, 2 ** attempt) + random.random())
        finally:
            if path and os.path.exists(path):
                os.unlink(path)
    raise SystemExit(f"TTS failed for {text[:40]!r}: {last}")


async def build_audio(script, out_mp3):
    voices = dict(VOICES)
    ov = script.get("voices", {})
    voices["zh"] = ov.get("zh", voices["zh"])
    voices["en"] = voices["en-slow"] = ov.get("en", voices["en"])
    pitches = {"zh": "+0Hz", "en": "+0Hz", "en-slow": "+0Hz"}
    po = script.get("pitch", {})
    pitches["zh"] = po.get("zh", "+0Hz")
    pitches["en"] = pitches["en-slow"] = po.get("en", "+0Hz")
    rates = dict(RATES)
    ro = script.get("rate", {})
    rates["zh"] = ro.get("zh", rates["zh"])
    rates["en"] = ro.get("en", rates["en"])
    rates["en-slow"] = ro.get("en-slow", rates["en-slow"])
    chunks = []
    for kind, value in script["queue"]:
        if kind == "pause":
            chunks.append(silence(value))
            continue
        base = "zh" if kind == "zh" else "en"
        for part in split_text(value, base):
            chunks.append(await synth(part, kind, voices, pitches, rates))
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
        fx = ""
        if script.get("fx") == "warm":
            fx = ("highpass=f=60,equalizer=f=110:width_type=h:width=120:g=2.5,"
                  "equalizer=f=260:width_type=q:width=1:g=1,"
                  "acompressor=threshold=0.12:ratio=2:attack=15:release=250:makeup=1.5,")
        elif script.get("fx") == "deep":
            fx = ("highpass=f=70,equalizer=f=110:width_type=h:width=120:g=4,"
                  "equalizer=f=260:width_type=q:width=1:g=1.5,equalizer=f=6500:width_type=h:width=3000:g=-2,"
                  "acompressor=threshold=0.09:ratio=3:attack=10:release=200:makeup=2,")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav, "-af", fx + "loudnorm=I=-16:TP=-1.5:LRA=11",
                        "-codec:a", "libmp3lame", "-b:a", "96k", "-ar", "44100", out_mp3], check=True)
    return len(pcm) / SR


def main():
    manifest = {}
    if os.path.exists("audio-manifest.json"):
        manifest = json.load(open("audio-manifest.json", encoding="utf-8"))
    episodes = json.load(open("episodes.json", encoding="utf-8")) if os.path.exists("episodes.json") else []
    os.makedirs("episodes", exist_ok=True)
    changed = 0
    failed = []
    for path in sorted(glob.glob("scripts/*.json")):
        stem = os.path.splitext(os.path.basename(path))[0]
        raw = open(path, "rb").read()
        digest = hashlib.sha256(raw).hexdigest()
        out = f"episodes/{stem}.mp3"
        if manifest.get(stem) == digest and os.path.exists(out):
            continue
        script = json.loads(raw.decode("utf-8"))
        print("building", stem, flush=True)
        try:
            dur = asyncio.run(build_audio(script, out))
        except SystemExit as e:
            print("FAILED", stem, e, flush=True)
            failed.append(stem)
            continue
        entry = {"id": stem, "title": script["title"], "description": script["description"],
                 "file": out, "duration": int(dur), "pub": script["pub"]}
        episodes = [e for e in episodes if e["id"] != stem] + [entry]
        manifest[stem] = digest
        changed += 1
        json.dump(episodes, open("episodes.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        json.dump(manifest, open("audio-manifest.json", "w", encoding="utf-8"), indent=2)
    json.dump(episodes, open("episodes.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(manifest, open("audio-manifest.json", "w", encoding="utf-8"), indent=2)
    subprocess.run([sys.executable, "tools/build_feed.py"], check=True)
    print("episodes built:", changed, "failed:", failed)
    if failed:
        sys.exit(1)


main()
