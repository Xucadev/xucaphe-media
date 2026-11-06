"""Transcribe con marcas de tiempo por palabra (faster-whisper) los WAV de tts/alinear.json -> tts/alineado/<id>.json."""
import json, os
from faster_whisper import WhisperModel
ids = json.load(open("tts/alinear.json"))["ids"]
m = WhisperModel(os.environ.get("MODELO", "small"), device="cpu", compute_type="int8")
os.makedirs("tts/alineado", exist_ok=True)
for i in ids:
    segs, _ = m.transcribe(f"tts/salida/{i}.wav", language="es", word_timestamps=True, vad_filter=False)
    pal = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for s in segs for w in s.words]
    json.dump(pal, open(f"tts/alineado/{i}.json", "w"), ensure_ascii=False)
    print(i, len(pal), "palabras")
