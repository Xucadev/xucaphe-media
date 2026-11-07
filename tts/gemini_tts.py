"""Genera audios con Gemini TTS a partir de tts/pedido.json -> tts/salida/<id>.wav (GitHub Actions)."""
import base64, json, os, sys, time, urllib.request, wave
KEY = os.environ.get("GEMINI_API_KEY", "")
if not KEY:
    sys.exit("Falta el secreto GEMINI_API_KEY")
MODELOS = ["gemini-3.1-flash-tts-preview", "gemini-2.5-flash-preview-tts"]
pedido = json.load(open("tts/pedido.json"))
os.makedirs("tts/salida", exist_ok=True)
log = []
for item in pedido["items"]:
    ok = False
    for m in pedido.get("modelos", MODELOS):
        body = {"contents": [{"parts": [{"text": item["texto"]}]}],
                # contenido educativo de prevención de estafas: el filtro por defecto bloquea relatos de fraudes y amenazas
                "safetySettings": [{"category": c, "threshold": pedido.get("umbral", "BLOCK_ONLY_HIGH")} for c in
                                   ("HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT")],
                "generationConfig": {"responseModalities": ["AUDIO"],
                                     "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": item.get("voz", "Orus")}}}}}
        req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                                     data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=480))
            c0 = (r.get("candidates") or [{}])[0]
            if "content" not in c0:
                raise RuntimeError(f"sin audio: finishReason={c0.get('finishReason')} feedback={json.dumps(r.get('promptFeedback', {}))[:200]}")
            pcm = base64.b64decode(r["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            with wave.open(f"tts/salida/{item['id']}.wav", "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
            log.append(f"OK {item['id']} {m} {len(pcm)/48000:.1f}s"); ok = True; break
        except urllib.error.HTTPError as e:
            log.append(f"ERR {item['id']} {m} {e.code} {e.read().decode()[:300]}")
        except Exception as e:
            log.append(f"ERR {item['id']} {m} {e}")
        time.sleep(2)
    time.sleep(7)
open("tts/salida/log.txt", "w").write("\n".join(log) + "\n")
print("\n".join(log))
