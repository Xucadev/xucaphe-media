"""Transcribe con marcas de tiempo por palabra (faster-whisper) los WAV de tts/alinear.json -> tts/alineado/<id>.json."""
import json, os, wave
import numpy as np
from faster_whisper import WhisperModel
ids = json.load(open("tts/alinear.json"))["ids"]
m = WhisperModel(os.environ.get("MODELO", "small"), device="cpu", compute_type="int8")
os.makedirs("tts/alineado", exist_ok=True)
for i in ids:
    with wave.open(f"tts/salida/{i}.wav") as w:
        sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    t = np.arange(0, len(x) / sr, 1 / 16000)
    x16 = np.interp(t, np.arange(len(x)) / sr, x).astype(np.float32)
    segs, _ = m.transcribe(x16, language="es", word_timestamps=True, vad_filter=False)
    pal = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for s in segs for w in s.words]
    json.dump(pal, open(f"tts/alineado/{i}.json", "w"), ensure_ascii=False)
    print(i, len(pal), "palabras")
