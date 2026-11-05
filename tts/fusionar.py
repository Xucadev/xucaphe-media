"""Pasa las traducciones de una copia de cola.json (argumento) a la cola.json actual, por id.
Lo usa traducir.yml para no pisar los cambios que el publicador hizo mientras se traducía."""
import json, sys
mia = {e["id"]: e for e in json.load(open(sys.argv[1]))}
cola = json.load(open("cola.json"))
n = 0
for e in cola:
    loc = (mia.get(e["id"], {}).get("youtube") or {}).get("localizations")
    if e.get("youtube") and loc and not e["youtube"].get("localizations"):
        e["youtube"]["localizations"] = loc
        n += 1
json.dump(cola, open("cola.json", "w"), ensure_ascii=False, indent=1)
print("fusionadas", n)
