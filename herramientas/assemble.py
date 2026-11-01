import json, re
from shapely.geometry import shape, mapping, box

FT = 0.3048
feats = []
for fn in ("enr21", "ad", "dep_sk", "charts"):
    feats += json.load(open(f"/home/claude/build/{fn}.geojson"))["features"]

# ---- quitar estratos "resumen" que contienen a otros del mismo polígono ----
by_poly = {}
for f in feats:
    key = (f["properties"]["name"], json.dumps(f["geometry"]["coordinates"][0][:3]))
    by_poly.setdefault(key, []).append(f)
drop = set()
for key, fs in by_poly.items():
    if len(fs) < 2: continue
    for a in fs:
        pa = a["properties"]
        for b in fs:
            if a is b: continue
            pb = b["properties"]
            if pa["lower_ft"] <= pb["lower_ft"] and pa["upper_ft"] >= pb["upper_ft"] and (pa["lower_ft"], pa["upper_ft"]) != (pb["lower_ft"], pb["upper_ft"]):
                drop.add(id(a)); break
    # duplicados exactos
    seen = set()
    for a in fs:
        k = (a["properties"]["lower_ft"], a["properties"]["upper_ft"])
        if k in seen: drop.add(id(a))
        seen.add(k)
feats = [f for f in feats if id(f) not in drop]
print("estratos descartados por ser resumen/duplicado:", len(drop))


def render_ft(val, ref, elev):
    if ref in ("GND", "MSL"): return 0
    if ref == "AGL": return val + (elev or 0)
    return val


APS = {x["icao"]: x for x in json.load(open("/home/claude/build/airports.json"))}
out = []
for i, f in enumerate(feats):
    p = f["properties"]
    elev = p.get("ad_elev_ft", 0)
    if p.get("source", "").endswith("SKBO") and "AGL" in (p["lower_ref"] + p["upper_ref"]):
        # El AIP mezcla AGL/AMSL en Bogotá; 11500 coincide con la base del TMA Bogotá, así que se dibuja como AMSL
        p["lower_ref"] = p["lower_ref"].replace("AGL", "AMSL"); p["upper_ref"] = p["upper_ref"].replace("AGL", "AMSL")
        p["remarks"] = (p.get("remarks", "") + " Dibujado como AMSL: el AIP indica AGL, pero 11500 ft coincide con la base del TMA Bogotá.").strip()
    lo = render_ft(p["lower_ft"], p["lower_ref"], elev)
    up = render_ft(p["upper_ft"], p["upper_ref"], elev)
    if p["upper_ref"] == "UNL": up = 60000
    if up <= lo: up = lo + 500
    grp, sub = p.get("grp") or p["name"], p.get("sub", "")
    m = re.match(r"(CTR)\s*-\s*([A-ZÁÉÍÓÚÑ ]+?)\s*-\s*SECTOR\s*-\s*(\d+)\s*-\s*[A-G]\s*\((SK..)\)", p["name"])
    if m: sub = f"Sector {m.group(3)}"
    if p["type"] in ("CTR", "ATZ"):
        ic = p["source"][-4:]; ap = APS.get(ic)
        grp = f"{p['type']} {ap['city'] if ap else ic} ({ic})"
    city = grp.split(" ", 1)[1] if " " in grp else ""
    if city and sub.upper().startswith(city.upper()): sub = sub[len(city):].strip(" -–")
    if sub.upper() == city.upper(): sub = ""
    sub = sub.title().replace("Poligono", "Polígono") if sub else ""
    sub = re.sub(r"\b(Ne|Nw|Se|Sw)\b", lambda k: k.group(1).upper(), sub)
    if sub and sub.isdigit(): sub = "Sector " + sub
    ring = f["geometry"]["coordinates"][0]
    c = shape(f["geometry"]).representative_point()
    out.append({
        "id": i, "t": p["type"], "n": p["name"], "gr": re.sub(r"\bSe$", "SE", grp), "sb": sub, "ax": bool(p.get("tr")), "c": p.get("class", ""),
        "lo": p["lower"], "up": p["upper"], "lof": lo, "upf": up,
        "u": p.get("unit", ""), "cs": p.get("callsign", ""), "fq": p.get("freq", ""),
        "r": p.get("remarks", ""), "s": p.get("source", ""), "g": p.get("group", ""),
        "lbl": [round(c.x, 4), round(c.y, 4)],
        "p": [[round(x, 5), round(y, 5)] for x, y in ring],
    })

airports = json.load(open("/home/claude/build/airports.json"))

# ---- cascos urbanos (Natural Earth 10m) dentro de Colombia + San Andrés ----
fc = json.load(open("/home/claude/raw/ne_10m_urban_areas.geojson"))
col = [g for g in json.load(open("/home/claude/raw/ne_10m_admin_0_countries.geojson"))["features"] if g["properties"]["ADM0_A3"] == "COL"][0]
colg = shape(col["geometry"]).buffer(0.05)
urb = []
for g in fc["features"]:
    s = shape(g["geometry"])
    if not s.intersects(box(-82.5, -4.5, -66.5, 13.6)): continue
    if not s.intersects(colg): continue
    s = s.simplify(0.002)
    polys = list(s.geoms) if s.geom_type == "MultiPolygon" else [s]
    for q in polys:
        if q.area < 2e-6: continue
        urb.append([[round(x, 4), round(y, 4)] for x, y in q.exterior.coords])
print("aerospacios:", len(out), "aeropuertos:", len(airports), "manchas urbanas:", len(urb))

pp = json.load(open("/home/claude/raw/ne_10m_populated_places_simple.geojson"))
cities = [{"n": f["properties"]["name"], "p": f["properties"]["pop_max"], "x": round(f["geometry"]["coordinates"][0], 4), "y": round(f["geometry"]["coordinates"][1], 4)}
          for f in pp["features"] if f["properties"]["adm0_a3"] == "COL" and (f["properties"]["pop_max"] >= 50000 or f["properties"]["adm1name"] and f["properties"]["featurecla"].startswith("Admin-1"))]
print("ciudades:", len(cities))
meta = {"airac": "AIRAC AMDT 73/26 — vigente desde 01 OCT 2026", "fuente": "eAIP Colombia (Aerocivil)",
        "generado": "2026-10-31"}
js = ("window.AIRSPACE_META=" + json.dumps(meta, ensure_ascii=False) + ";\n" +
      "window.AIRSPACE=" + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n" +
      "window.AIRPORTS=" + json.dumps(airports, ensure_ascii=False, separators=(",", ":")) + ";\n" +
      "window.URBAN=" + json.dumps(urb, separators=(",", ":")) + ";\n" + "window.CITIES=" + json.dumps(cities, ensure_ascii=False, separators=(",", ":")) + ";\n")
import os
os.makedirs("/home/claude/site/data", exist_ok=True)
open("/home/claude/site/data/data.js", "w").write(js)
# GeoJSON limpio para reutilizar
gj = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [o["p"]]},
     "properties": {k: o[k] for k in ("t", "n", "c", "lo", "up", "u", "cs", "fq", "r", "s")}} for o in out]}
open("/home/claude/site/data/espacio_aereo_colombia.geojson", "w").write(json.dumps(gj, ensure_ascii=False))
print(round(len(js) / 1e6, 2), "MB data.js")
from collections import Counter
print(Counter(o["t"] for o in out))
