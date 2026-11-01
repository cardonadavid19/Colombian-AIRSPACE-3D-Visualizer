import re, json, sys
sys.path.insert(0, "/home/claude/build")
from geo import parse_lateral, ring_to_geo, alt_ft, COORD_RE

ad = json.load(open("/home/claude/raw/ad.json"))
feats, airports, omit = [], [], []
ZONE = re.compile(r"((?:ATZ|CTR)\s*-\s*[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9 \-]*?)\s+(?=Desde |Circulo )")
VERT = re.compile(r"(GND|SFC|MSL|\d{3,5}(?: FT)?(?: AMSL| AGL)?)\s+hasta\s+(UNL|\d{3,5}(?: FT)?(?: AMSL| AGL)?)")


def norm_alt(s):
    s = s.strip()
    if re.fullmatch(r"\d+", s): s += " FT"
    return s


for a in ad:
    m = re.match(r"AD 2 (SK[A-Z]{2}) - (.+?) - (.+?)-es-CO\.html", a["f"])
    icao, city, name = m.group(1), m.group(2).title(), m.group(3).title()
    t22 = (a.get("ad22") or "").split("\n")
    p22 = t22[2] if len(t22) > 2 else ""
    arp = re.search(r"(\d{6}(?:\.\d+)?)([NS])\s+(\d{7}(?:\.\d+)?)([EW])", p22)
    elev = re.search(r"Elev:\s*([\d.,]+)\s*FT", p22)
    if not arp:
        omit.append({"name": icao, "source": "AD 2.2", "reason": "sin coordenadas ARP"}); continue
    from geo import dms
    lon = dms(arp.group(3), arp.group(4), 3); lat = dms(arp.group(1), arp.group(2), 2)
    el = float(elev.group(1).replace(",", "")) if elev else 0.0
    t = (a.get("ad217") or "").split("\n")
    p = t[2] if len(t) > 2 else ""
    lat_sec = re.search(r"1 Designación y Límites Laterales (.*?)(?:Designation and Lateral Limits|2 Límites Verticales)", p)
    vert_sec = re.search(r"2 Límites Verticales (.*?) Vertical limits", p)
    cls_sec = re.search(r"3 Clasificación del Espacio Aéreo (.*?) Airspace Classification", p)
    call_sec = re.search(r"4 Distintivo de Llamada ATS Idiomas (.*?) ATS Unit", p)
    hrs_sec = re.search(r"6 Horas de Aplicabilidad (.*?) Hours of Applicability", p)
    has_zone = bool(lat_sec and lat_sec.group(1).strip() not in ("NIL", ""))
    kinds = []
    if has_zone:
        L = lat_sec.group(1)
        heads = list(ZONE.finditer(L))
        if not heads:  # una sola zona sin nombre explícito -> buscar 'CTR'/'ATZ' al inicio
            heads = list(re.finditer(r"((?:ATZ|CTR)[^D]*?)\s+(?=Desde|Circulo)", L))
        zones = []
        for i, h in enumerate(heads):
            body = L[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(L)]
            zones.append((h.group(1).strip(" -"), body))
        verts = VERT.findall(vert_sec.group(1)) if vert_sec else []
        cls_txt = cls_sec.group(1) if cls_sec else ""
        for zi, (zname, body) in enumerate(zones):
            pts, notes = parse_lateral(body)
            if pts is None:
                omit.append({"name": f"{icao} {zname}", "source": "AD 2.17", "reason": notes}); continue
            if zi < len(verts): lo, up = verts[zi]
            elif verts: lo, up = verts[-1]
            else:
                omit.append({"name": f"{icao} {zname}", "source": "AD 2.17", "reason": "sin límites verticales"}); continue
            lo, up = norm_alt(lo), norm_alt(up)
            mcls = re.search(re.escape(zname) + r"\s*-?\s*([A-G])\b", cls_txt) if len(zones) > 1 else re.search(r"\b([A-G])\b", cls_txt)
            cls = mcls.group(1) if mcls else (re.search(r"- ([A-G])$", zname).group(1) if re.search(r"- ([A-G])$", zname) else "D")
            typ = "ATZ" if zname.startswith("ATZ") else "CTR"
            kinds.append(typ)
            uf, ur = alt_ft(up); lf, lr = alt_ft(lo)
            feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring_to_geo(pts)]},
                          "properties": {"type": typ, "name": f"{zname.replace('  ', ' ')} ({icao})", "class": cls,
                                         "upper": up, "lower": lo, "upper_ft": uf, "upper_ref": ur, "lower_ft": lf, "lower_ref": lr,
                                         "ad_elev_ft": round(el), "unit": "TWR " + icao,
                                         "callsign": (call_sec.group(1) if call_sec else "").replace("NIL", "").strip()[:160],
                                         "freq": "", "remarks": (hrs_sec.group(1).replace("NIL", "").strip() if hrs_sec else ""),
                                         "geomNotes": notes, "source": f"AIP AD 2.17 {icao}"}})
    airports.append({"icao": icao, "city": city, "name": name, "lon": round(lon, 6), "lat": round(lat, 6),
                     "elev_ft": round(el), "zones": sorted(set(kinds))})
    if not has_zone:
        omit.append({"name": f"{icao} ({city})", "source": "AD 2.17", "reason": "el AIP publica NIL (sin CTR/ATZ propio)"})

# frecuencias TWR desde AD 2.18
freq = {}
for a in ad:
    icao = a["f"][5:9]
    t = (a.get("ad218") or "").split("\n")
    s = " ".join(t[2:3])
    fr = re.findall(r"TWR[^0-9]{0,40}?(1[1-3]\d\.\d{1,3})\s*MHZ", s, re.I)
    freq[icao] = sorted(set(fr))[:3]
for f in feats:
    ic = f["properties"]["source"][-4:]
    f["properties"]["freq"] = " / ".join(x + " MHz" for x in freq.get(ic, []))
for ap in airports: ap["twr"] = freq.get(ap["icao"], [])

json.dump({"type": "FeatureCollection", "features": feats}, open("/home/claude/build/ad.geojson", "w"), ensure_ascii=False)
json.dump(airports, open("/home/claude/build/airports.json", "w"), ensure_ascii=False, indent=0)
json.dump(omit, open("/home/claude/build/omit_ad.json", "w"), ensure_ascii=False, indent=1)
print(len(feats), "zonas;", len(airports), "aeropuertos")
for f in feats:
    q = f["properties"]
    print(f"{q['type']} {q['name'][:40]:40} {q['lower']:>14} - {q['upper']:<15} {q['class']} {q['freq']} pts={len(f['geometry']['coordinates'][0])}")
print(omit)
