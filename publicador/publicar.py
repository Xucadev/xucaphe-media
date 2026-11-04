"""Publica los reels de cola.json en YouTube, Instagram y Facebook con las APIs oficiales.

Lo ejecuta GitHub Actions cada 15 minutos. Para cada entrada cuya fecha ya llegó, sube el
vídeo a cada red pendiente y apunta el resultado en cola.json (se hace commit después).

Modo prueba:  python publicador/publicar.py --probar   (solo comprueba credenciales)

Secretos (variables de entorno):
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
  META_PAGE_TOKEN, FB_PAGE_ID, IG_USER_ID
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent.parent
COLA = RAIZ / "cola.json"
GRAPH = "https://graph.facebook.com/v25.0"
MAX_INTENTOS = 3
MAX_RETRASO_H = 12  # si una red se conecta tarde, no se publican de golpe los reels atrasados
ENV = os.environ.get


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- YouTube

def yt_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": ENV("YT_CLIENT_ID"), "client_secret": ENV("YT_CLIENT_SECRET"),
        "refresh_token": ENV("YT_REFRESH_TOKEN"), "grant_type": "refresh_token"}, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]


def youtube(item, video: Path):
    d = item["youtube"]
    tok = yt_token()
    meta = {
        "snippet": {"title": d["title"][:100], "description": d["description"], "tags": d.get("tags", []),
                    "categoryId": "28", "defaultLanguage": "es", "defaultAudioLanguage": "es"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False,
                   "containsSyntheticMedia": True},
    }
    # Títulos y descripciones traducidos (los rellena tts/traducir.py): YouTube los muestra en el idioma del espectador
    if d.get("localizations"):
        meta["localizations"] = {k: {"title": v["title"][:100], "description": v["description"]} for k, v in d["localizations"].items()}
    size = video.stat().st_size
    r = requests.post(
        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status" + (",localizations" if d.get("localizations") else ""),
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)},
        data=json.dumps(meta), timeout=60)
    r.raise_for_status()
    with open(video, "rb") as f:
        up = requests.put(r.headers["Location"], data=f,
                          headers={"Authorization": f"Bearer {tok}", "Content-Type": "video/mp4"}, timeout=600)
    up.raise_for_status()
    return f"https://youtube.com/shorts/{up.json()['id']}"


# ---------------------------------------------------------------- Instagram

def instagram(item, video: Path):
    d = item["instagram"]
    tok, ig = ENV("META_PAGE_TOKEN"), ENV("IG_USER_ID")
    params = {"media_type": "REELS", "upload_type": "resumable", "caption": d["caption"], "access_token": tok}
    if d.get("trial"):
        params["trial_params"] = json.dumps({"graduation_strategy": "MANUAL"})
    else:
        params["share_to_feed"] = "true"
    r = requests.post(f"{GRAPH}/{ig}/media", data=params, timeout=60)
    r.raise_for_status()
    c = r.json()
    size = video.stat().st_size
    with open(video, "rb") as f:
        up = requests.post(c["uri"], data=f, timeout=600, headers={
            "Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(size)})
    up.raise_for_status()
    for _ in range(60):  # hasta 10 min de procesado
        s = requests.get(f"{GRAPH}/{c['id']}", params={"fields": "status_code,status", "access_token": tok}, timeout=30).json()
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram no procesó el vídeo: {s}")
        time.sleep(10)
    else:
        raise RuntimeError("Instagram tardó demasiado en procesar el vídeo")
    p = requests.post(f"{GRAPH}/{ig}/media_publish", data={"creation_id": c["id"], "access_token": tok}, timeout=60)
    p.raise_for_status()
    mid = p.json()["id"]
    link = requests.get(f"{GRAPH}/{mid}", params={"fields": "permalink", "access_token": tok}, timeout=30).json()
    return link.get("permalink", mid)


# ---------------------------------------------------------------- Facebook

def facebook(item, video: Path):
    d = item["facebook"]
    tok, page = ENV("META_PAGE_TOKEN"), ENV("FB_PAGE_ID")
    r = requests.post(f"{GRAPH}/{page}/video_reels", data={"upload_phase": "start", "access_token": tok}, timeout=60)
    r.raise_for_status()
    s = r.json()
    size = video.stat().st_size
    with open(video, "rb") as f:
        up = requests.post(s["upload_url"], data=f, timeout=600, headers={
            "Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(size)})
    up.raise_for_status()
    fin = requests.post(f"{GRAPH}/{page}/video_reels", data={
        "upload_phase": "finish", "video_id": s["video_id"], "video_state": "PUBLISHED",
        "title": d.get("title", ""), "description": d["description"], "access_token": tok}, timeout=60)
    fin.raise_for_status()
    return f"https://www.facebook.com/reel/{s['video_id']}"


REDES = {"youtube": youtube, "instagram": instagram, "facebook": facebook}
SECRETOS = {"youtube": ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"],
            "instagram": ["META_PAGE_TOKEN", "IG_USER_ID"],
            "facebook": ["META_PAGE_TOKEN", "FB_PAGE_ID"]}


def configurada(red):
    return all(ENV(k) for k in SECRETOS[red])


def probar():
    ok = True
    if configurada("youtube"):
        try:
            tok = yt_token()
            ch = requests.get("https://www.googleapis.com/youtube/v3/channels", params={"part": "snippet", "mine": "true"},
                              headers={"Authorization": f"Bearer {tok}"}, timeout=30).json()
            if ch.get("items"):
                log("YouTube OK:", ch["items"][0]["snippet"]["title"])
            else:
                log("YouTube OK: el token funciona (con permiso de subida; no tiene permiso para leer el nombre del canal)")
        except Exception as e:  # noqa: BLE001
            ok = False
            log("YouTube ERROR:", e)
    else:
        log("YouTube: todavía sin configurar (faltan secretos)")
    if configurada("facebook"):
        r = requests.get(f"{GRAPH}/{ENV('FB_PAGE_ID')}", params={"fields": "name,instagram_business_account",
                                                                  "access_token": ENV("META_PAGE_TOKEN")}, timeout=30).json()
        log("Facebook:", r)
        ok = ok and "error" not in r
    else:
        log("Facebook: todavía sin configurar (faltan secretos)")
    if configurada("instagram"):
        r = requests.get(f"{GRAPH}/{ENV('IG_USER_ID')}", params={"fields": "username",
                                                                  "access_token": ENV("META_PAGE_TOKEN")}, timeout=30).json()
        log("Instagram:", r)
        ok = ok and "error" not in r
    else:
        log("Instagram: todavía sin configurar (faltan secretos)")
    return ok


def main():
    if "--probar" in sys.argv:
        sys.exit(0 if probar() else 1)
    cola = json.loads(COLA.read_text())
    ahora = datetime.now(timezone.utc)
    cambios = False
    for item in cola:
        if datetime.fromisoformat(item["fecha"]) > ahora:
            continue
        estado = item.setdefault("estado", {})
        video = RAIZ / item["video"]
        retraso_h = (ahora - datetime.fromisoformat(item["fecha"])).total_seconds() / 3600
        for red, fn in REDES.items():
            if red not in item:
                continue
            e = estado.setdefault(red, {"intentos": 0})
            if e.get("url") or e.get("vencido") or e["intentos"] >= MAX_INTENTOS or not configurada(red):
                continue
            if retraso_h > MAX_RETRASO_H:
                e["vencido"] = True
                log(f"  · {item['id']} en {red}: vencido ({retraso_h:.0f} h tarde), no se publica")
                cambios = True
                COLA.write_text(json.dumps(cola, ensure_ascii=False, indent=1))
                continue
            try:
                log(f"→ {item['id']} en {red}")
                e["url"] = fn(item, video)
                e["publicado"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                e.pop("error", None)
                log(f"  ✔ {e['url']}")
            except Exception as ex:  # noqa: BLE001
                e["intentos"] += 1
                detalle = getattr(getattr(ex, "response", None), "text", "") or str(ex)
                e["error"] = detalle[:500]
                log(f"  ✖ {detalle[:500]}")
            cambios = True
            COLA.write_text(json.dumps(cola, ensure_ascii=False, indent=1))
    if not cambios:
        log("Nada pendiente.")


if __name__ == "__main__":
    main()
