"""Construye las zonas transcritas de las cartas ENR 6.2 / 6.4 (imagen) a GeoJSON."""
import re, json, sys
sys.path.insert(0, "/home/claude/build")
from geo import G, NM, arc_points, circle, ring_to_geo, alt_ft
from shapely.geometry import Polygon
from charts import CH, DEP

# VOR/DME del ENR 4.1 (coordenadas y declinación de estación, grados W)
VOR = {"ZIP": ("050105N", "0735912W", 8), "EJA": ("070143N", "0734820W", 8), "TQS": ("004432N", "0751401W", 7),
       "PAL": ("052914N", "0743938W", 8), "GIR": ("041132N", "0745156W", 7), "BAQ": ("104743N", "0745137W", 8),
       "BUN": ("034931N", "0765943W", 6), "FLA": ("013516N", "0753410W", 7), "TOL": ("041521N", "0743826W", 8)}


def dms6(s):
    lat = int(s[0][:2]) + int(s[0][2:4]) / 60 + int(s[0][4:6]) / 3600
    lon = int(s[1][:3]) + int(s[1][3:5]) / 60 + int(s[1][5:7]) / 3600
    return (-lon, lat)


def vor(k): return dms6(VOR[k][:2])


def P(t):
    la, lo = t
    m1 = re.match(r"([NS])(\d+)°(\d+)'([\d.]+)", la); m2 = re.match(r"([EW])(\d+)°(\d+)'([\d.]+)", lo)
    lat = int(m1.group(2)) + int(m1.group(3)) / 60 + float(m1.group(4)) / 3600
    lon = int(m2.group(2)) + int(m2.group(3)) / 60 + float(m2.group(4)) / 3600
    return (-lon if m2.group(1) == "W" else lon, -lat if m1.group(1) == "S" else lat)


def short_arc(c, a, b, r):
    az1 = G.inv(c[0], c[1], a[0], a[1])[0] % 360; az2 = G.inv(c[0], c[1], b[0], b[1])[0] % 360
    return arc_points(c, a, b, ((az2 - az1) % 360) <= 180, r)


def build(z):
    k = z["kind"]
    if k == "circle":
        c = P(z["c"]) if "c" in z else vor(z["center"])
        return circle(c, z["r"])
    if k in ("poly", "dme_pts"):
        pts = [P(p) for p in z["pts"]]
        segs = z.get("segs", {})
        if isinstance(segs, list):  # dme_pts: lista por vértice
            segs = {i: (z["center"], float(s[3:])) for i, s in enumerate(segs) if s.startswith("arc")}
        out = []
        for i, p in enumerate(pts):
            out.append(p)
            if i in segs:
                c, r = segs[i]; nxt = pts[(i + 1) % len(pts)]
                out += short_arc(vor(c), p, nxt, r)
        return out
    if k == "dme_rad":
        c = vor(z["center"]); decl = VOR[z["center"]][2]
        pts = [G.fwd(c[0], c[1], (rad - decl) % 360, d * NM)[:2] for rad, d in z["rad"]]
        out = []
        for i, p in enumerate(pts):
            out.append(p)
            if z["segs"][i] == "arc":
                out += short_arc(c, p, pts[(i + 1) % len(pts)], z["rad"][i][1])
        return out
    if k == "union":
        (cc, r) = z["circle"]
        g = Polygon(circle(P(cc), r)).union(Polygon([P(p) for p in z["pts"]]))
        return list(g.exterior.coords)[:-1]
    if k == "diff":
        g = Polygon(circle(vor(z["center"]), z["r"])).difference(Polygon(circle(vor(z["cut"][0]), z["cut"][1], 180)))
        if g.geom_type == "MultiPolygon": g = max(g.geoms, key=lambda q: q.area)
        return list(g.exterior.coords)[:-1]
    if k == "diff2":
        a, b = [P(p) for p in z["cutpts"]]; r = z["cutr"] * NM
        # centro del arco de corte: el punto a distancia r de ambos, al lado opuesto del centro principal
        import numpy as np
        main = P(z["c"]); best = None
        for az in np.arange(0, 360, 0.05):
            x, y, _ = G.fwd(a[0], a[1], az, r)
            d = G.inv(x, y, b[0], b[1])[2]
            if abs(d - r) < 15:
                far = G.inv(x, y, main[0], main[1])[2]
                if best is None or far > best[0]: best = (far, (x, y))
        cut = Polygon(circle(best[1], z["cutr"], 180))
        g = Polygon(circle(main, z["r"])).difference(cut)
        if g.geom_type == "MultiPolygon": g = max(g.geoms, key=lambda q: q.area)
        return list(g.exterior.coords)[:-1]
    raise ValueError(k)


NAMES = {"SKD36": "CHIA", "SKD37": "BARRANCABERMEJA", "SKD41": "MANIZALES", "SKP28": "TRES ESQUINAS", "SKP31": "PALANQUERO",
         "SKP32": "CALI", "SKP35": "CHIA", "SKP48": "MARANDUA", "SKR1": "BARRANQUILLA", "SKR5": "VALLE DEL CAUCA", "SKR6": "LA MACARENA",
         "SKR7": "VILLAVICENCIO", "SKR8": "RIOHACHA", "SKR9": "MELGAR", "SKR11": "BARRANQUILLA", "SKR16": "COVEÑAS", "SKR17": "CARTAGENA",
         "SKR18": "JUANCHACO", "SKR19": "MEDELLIN", "SKR23": "BARRANQUILLA", "SKR24": "BARRANQUILLA", "SKR25": "MATUNTUGO", "SKR26": "MARANDUA",
         "SKR27": "TRES ESQUINAS", "SKR33": "TUNJA", "SKR39": "GIRARDOT", "SKR44": "AMAZONIA PARQUES NACIONALES", "SKR45": "BOGOTA (CAN)", "SKR50": "CUCUTA"}
REF = {"SKD36": 8389, "SKD37": 414, "SKP28": 800, "SKR6": 790, "29": 4221, "31": 9842}  # elevación de referencia (ft) para límites AGL
feats = []
for ident, z in CH.items():
    ring = build(z)
    grp = z.get("grp", ident.split()[0])
    grp = grp + " " + NAMES.get(grp, "") if NAMES.get(grp) else grp
    typ = "SK" + grp[2]
    uf, ur = alt_ft(z["up"]); lf, lr = alt_ft(z["lo"])
    feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring_to_geo(ring)]},
                  "properties": {"type": typ, "name": ident, "grp": grp, "sub": z.get("sub", ""), "class": "",
                                 "upper": z["up"], "lower": z["lo"], "upper_ft": uf, "upper_ref": ur, "lower_ft": lf, "lower_ref": lr,
                                 "unit": "", "callsign": "", "freq": "", "remarks": z.get("rem", ""), "geomNotes": [],
                                 "source": "AIP " + z["src"] + " (carta)", "tr": True, "ad_elev_ft": REF.get(ident, 0)}})
for num, z in DEP.items():
    ring = [P(p) for p in z["pts"]]
    uf, ur = alt_ft(z["up"])
    feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring_to_geo(ring)]},
                  "properties": {"type": "DEP", "name": z["name"], "grp": z["name"], "sub": "", "class": "G",
                                 "upper": z["up"], "lower": "GND", "upper_ft": uf, "upper_ref": ur, "lower_ft": 0, "lower_ref": "GND",
                                 "unit": "", "callsign": "Aviación deportiva", "freq": "", "remarks": z["rem"], "geomNotes": [],
                                 "source": "AIP " + z["src"] + " (carta)", "tr": True, "ad_elev_ft": REF.get(num, 0)}})
json.dump({"type": "FeatureCollection", "features": feats}, open("/home/claude/build/charts.geojson", "w"), ensure_ascii=False)
for f in feats:
    p = f["properties"]; r = f["geometry"]["coordinates"][0]
    xs = [x for x, y in r]; ys = [y for x, y in r]
    print(f"{p['name']:45} {p['lower']:>13}-{p['upper']:<14} pts={len(r):3}  lon {min(xs):.3f}..{max(xs):.3f} lat {min(ys):.3f}..{max(ys):.3f}  area={Polygon(r).area*12300:.0f}km2")
