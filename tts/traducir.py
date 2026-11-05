"""Rellena youtube.localizations (en, pt) de las entradas futuras de cola.json con Gemini (texto, plan gratis).
# v5 — también traduce subtítulos subs/ID.es.srt a subs/ID.en.srt y subs/ID.pt-BR.srt
Se ejecuta en GitHub Actions con el secreto GEMINI_API_KEY. Máximo LIMITE entradas por corrida."""
import json, os, sys, time, urllib.request, functools
print = functools.partial(print, flush=True)
INICIO = time.time()
PRESUPUESTO = 20 * 60  # segundos; Actions corta a los 30 min
from datetime import datetime, timezone
KEY = os.environ.get("GEMINI_API_KEY") or sys.exit("Falta GEMINI_API_KEY")
def modelos():
    """Elige los modelos Flash de texto disponibles hoy (los nombres cambian con el tiempo)."""
    r = json.load(urllib.request.urlopen(urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/models?pageSize=200", headers={"x-goog-api-key": KEY}), timeout=60))
    ok = [m["name"].split("/")[-1] for m in r.get("models", []) if "generateContent" in m.get("supportedGenerationMethods", [])]
    malos = ("tts", "image", "live", "audio", "embedding", "vision", "thinking", "exp", "robotics", "native")
    flash = [m for m in ok if "flash" in m and not any(x in m for x in malos)]
    flash.sort(key=lambda m: ("lite" in m, "preview" in m, [-int(x) for x in __import__("re").findall(r"\d+", m)]))
    print("modelos:", flash[:4])
    return flash[:2] or ok[:2]


MODELOS = modelos()
LIMITE = int(os.environ.get("LIMITE", "40"))
cola = json.load(open("cola.json"))
ahora = datetime.now(timezone.utc)
hechas = 0
def guardar():
    json.dump(cola, open("cola.json", "w"), ensure_ascii=False, indent=1)
for e in cola:
    if time.time() - INICIO > PRESUPUESTO:
        print("tiempo agotado, sigo mañana"); break
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
            r = json.load(urllib.request.urlopen(req, timeout=60))
            t = json.loads(r["candidates"][0]["content"]["parts"][0]["text"])
            if all(t.get(k, {}).get("title") and t[k].get("description") for k in ("en", "pt")):
                y["localizations"] = {k: t[k] for k in ("en", "pt")}
                hechas += 1
                print("OK", e["id"], m, f"{time.time()-INICIO:.0f}s")
                guardar()
                break
        except Exception as ex:
            print("ERR", e["id"], m, str(ex)[:200])
        time.sleep(3)
    if hechas >= LIMITE:
        break
    time.sleep(4)
guardar()
print("traducidas", hechas)

# ---------------------------------------------------------------- subtítulos
import re
from pathlib import Path
SUBS = Path("subs")
LIM_SUBS = int(os.environ.get("LIMITE_SUBS", "40"))
def gemini(prompt):
    for m in MODELOS:
        body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}}
        req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                                     data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=60))
            return json.loads(r["candidates"][0]["content"]["parts"][0]["text"]), m
        except Exception as ex:
            print("ERR subs", m, str(ex)[:200])
        time.sleep(3)
    return None, None
fechas = {e["id"]: e["fecha"] for e in cola}
subs_hechos = 0
for f in sorted(SUBS.glob("*.es.srt")) if SUBS.is_dir() else []:
    rid = f.name[:-len(".es.srt")]
    if time.time() - INICIO > PRESUPUESTO or subs_hechos >= LIM_SUBS:
        print("subtítulos: sigo mañana"); break
    if (SUBS / f"{rid}.en.srt").exists() and (SUBS / f"{rid}.pt-BR.srt").exists():
        continue
    if rid in fechas and datetime.fromisoformat(fechas[rid]) < ahora - __import__("datetime").timedelta(days=2):
        continue
    bloques = [b.split("\n", 2) for b in f.read_text().strip().split("\n\n")]
    lineas = [b[2].strip() for b in bloques]
    t, m = gemini("Traduce estos subtítulos de un Short de ciberseguridad (español de RD) a inglés (en) y portugués de "
                  "Brasil (pt). Una traducción por línea, mismo orden y misma cantidad, cortas y naturales para leer en "
                  "pantalla. Mantén cifras y nombres. Responde SOLO JSON: {\"en\":[...],\"pt\":[...]}.\n\n"
                  + json.dumps(lineas, ensure_ascii=False))
    if not t or any(len(t.get(k) or []) != len(lineas) for k in ("en", "pt")):
        print("ERR subs", rid, "respuesta incompleta"); time.sleep(4); continue
    for k, ext in (("en", "en"), ("pt", "pt-BR")):
        (SUBS / f"{rid}.{ext}.srt").write_text("\n".join(f"{b[0]}\n{b[1]}\n{str(x).strip()}\n" for b, x in zip(bloques, t[k])))
    subs_hechos += 1
    print("OK subs", rid, m, f"{time.time()-INICIO:.0f}s")
    time.sleep(4)
print("subtítulos traducidos", subs_hechos)
