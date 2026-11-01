import re, json, sys
sys.path.insert(0, "/home/claude/build")
from geo import parse_lateral, ring_to_geo, parse_strata, alt_ft

rows = open("/home/claude/raw/enr21.txt").read().split("\n")[:366]
feats, omit = [], []
group = None


def gtype(g):
    for t in ("UTA", "FIR", "TMA", "CTA"):
        if g and g.startswith(t): return t
    return None


for i, l in enumerate(rows):
    c = l.split(" | ")
    if len(c) < 4 or not c[0].strip() or i < 4: continue
    first = c[0]
    if "Desde" not in first and "Circulo" not in first:
        h = first.strip()
        if gtype(h): group = h
        continue
    name = first[: first.find("Desde")].strip()
    # tipo
    t = gtype(name) or gtype(group)
    if name.startswith("SECTOR CENTRAL") or "VILLAVICENCIO E" in name or "VILLAVICENCIO SE" in name:
        t = "FIC"
        disp = name.title()
    else:
        disp = name if gtype(name) else f"{group} – {name}"
    disp = disp.replace("TMA TMA - ", "TMA ")
    nm = name.replace("TMA TMA - ", "TMA ")
    if t == "FIC": grp, sub = disp, ""
    elif gtype(nm) and not (group and gtype(group) == t and nm.startswith(group)): grp, sub = nm, ""
    else: grp, sub = group, (nm[len(group):].strip(" -") if nm.startswith(group) else nm)
    tail = first[first.find("para el punto de origen") + len("para el punto de origen"):] if "para el punto de origen" in first else ""
    pts, notes = parse_lateral(first)
    if pts is None:
        omit.append({"name": disp, "source": "ENR 2.1", "reason": notes}); continue
    strata = parse_strata(tail)
    unit = c[1].strip(); call = c[2].strip(); freq = c[3].strip(); rem = c[4].strip() if len(c) > 4 else ""
    if not strata:
        omit.append({"name": disp, "source": "ENR 2.1", "reason": "sin límites verticales legibles: " + tail[:60]}); continue
    geom = ring_to_geo(pts)
    for k, (up, cls, lo) in enumerate(strata):
        uf, ur = alt_ft(up); lf, lr = alt_ft(lo)
        feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [geom]},
                      "properties": {"type": t, "name": disp, "class": cls or "", "upper": up, "lower": lo,
                                     "upper_ft": uf, "upper_ref": ur, "lower_ft": lf, "lower_ref": lr,
                                     "unit": unit, "callsign": call, "freq": freq, "remarks": rem[:400],
                                     "grp": grp, "sub": sub, "stratum": k + 1, "strata": len(strata), "geomNotes": notes, "source": "AIP ENR 2.1"}})

json.dump({"type": "FeatureCollection", "features": feats}, open("/home/claude/build/enr21.geojson", "w"), ensure_ascii=False)
json.dump(omit, open("/home/claude/build/omit_enr21.json", "w"), ensure_ascii=False, indent=1)
from collections import Counter
print(len(feats), Counter(f["properties"]["type"] for f in feats))
print("omit", omit)
for f in feats:
    p = f["properties"]
    print(f"{p['type']:4} {p['name'][:45]:45} {p['lower']:>9}-{p['upper']:<9} {p['class']} {len(f['geometry']['coordinates'][0])}pts {';'.join(set(p['geomNotes']))[:50]}")
