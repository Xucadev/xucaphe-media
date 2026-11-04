"""Rellena youtube.localizations (en, pt) de las entradas futuras de cola.json con Gemini (texto, plan gratis).
# v2
Se ejecuta en GitHub Actions con el secreto GEMINI_API_KEY. Máximo LIMITE entradas por corrida."""
import json, os, sys, time, urllib.request
from datetime import datetime, timezone
KEY = os.environ.get("GEMINI_API_KEY") or sys.exit("Falta GEMINI_API_KEY")
MODELOS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
LIMITE = int(os.environ.get("LIMITE", "40"))
cola = json.load(open("cola.json"))
ahora = datetime.now(timezone.utc)
hechas = 0
for e in cola:
    y = e.get("youtube")
    if not y or y.get("localizations") or datetime.fromisoformat(e["fecha"]) < ahora:
        continue
    prompt = ("Traduce el título y la descripción de este YouTube Short de ciberseguridad (español de RD) a inglés (en) "
              "y portugués de Brasil (pt). Mantén emojis, hashtags traducidos al idioma, cifras y la línea de aviso de IA. "
              "No añadas nada. Responde SOLO JSON: {\"en\":{\"title\":...,\"description\":...},\"pt\":{...}}. "
              "El título sin '#shorts' y como máximo 90 caracteres; añade ' #shorts' al final.\n\n"
              f"TÍTULO: {y['title']}\n\nDESCRIPCIÓN:\n{y['description']}")
    for m in MODELOS:
        body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}}
        req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                                     data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=120))
            t = json.loads(r["candidates"][0]["content"]["parts"][0]["text"])
            if all(t.get(k, {}).get("title") and t[k].get("description") for k in ("en", "pt")):
                y["localizations"] = {k: t[k] for k in ("en", "pt")}
                hechas += 1
                print("OK", e["id"], m)
                break
        except Exception as ex:
            print("ERR", e["id"], m, str(ex)[:200])
        time.sleep(3)
    if hechas >= LIMITE:
        break
    time.sleep(4)
json.dump(cola, open("cola.json", "w"), ensure_ascii=False, indent=1)
print("traducidas", hechas)
