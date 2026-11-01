"""Geometría AIP: coordenadas DMS, arcos geodésicos, círculos y seguimiento de frontera."""
import re, json, math
from pyproj import Geod
from shapely.geometry import Polygon, Point, LineString, shape
from shapely.ops import unary_union

G = Geod(ellps="WGS84")
NM = 1852.0

COORD = r"(\d{6}(?:\.\d+)?)([NS])\s*/\s*(\d{7}(?:\.\d+)?)([EW])"
COORD_RE = re.compile(COORD)


def dms(s, hem, deglen):
    d = int(s[:deglen]); m = int(s[deglen:deglen + 2]); sec = float(s[deglen + 2:])
    v = d + m / 60 + sec / 3600
    return -v if hem in "SW" else v


def parse_coord(m):
    return (dms(m.group(3), m.group(4), 3), dms(m.group(1), m.group(2), 2))  # lon, lat


# ---------- frontera de Colombia ----------
_BORDER = None


def border_ring():
    global _BORDER
    if _BORDER is None:
        fc = json.load(open("/home/claude/raw/ne_10m_admin_0_countries.geojson"))
        col = [f for f in fc["features"] if f["properties"].get("ADM0_A3") == "COL"][0]
        g = shape(col["geometry"])
        polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
        main = max(polys, key=lambda p: p.area)
        _BORDER = list(main.exterior.coords)[:-1]
    return _BORDER


def _nearest(ring, pt):
    best, bi = 1e18, 0
    for i, (x, y) in enumerate(ring):
        d = (x - pt[0]) ** 2 + (y - pt[1]) ** 2
        if d < best:
            best, bi = d, i
    return bi


def border_paths(a, b):
    ring = border_ring(); n = len(ring)
    i, j = _nearest(ring, a), _nearest(ring, b)
    fwd, k = [], i
    while True:
        fwd.append(ring[k])
        if k == j: break
        k = (k + 1) % n
    bwd, k = [], i
    while True:
        bwd.append(ring[k])
        if k == j: break
        k = (k - 1) % n
    return fwd, bwd


# ---------- arcos ----------
def arc_points(center, start, end, clockwise, radius_nm=None, step_deg=3):
    lon0, lat0 = center
    az1, _, d1 = G.inv(lon0, lat0, start[0], start[1])
    az2, _, d2 = G.inv(lon0, lat0, end[0], end[1])
    r = radius_nm * NM if radius_nm else (d1 + d2) / 2
    a1, a2 = az1 % 360, az2 % 360
    if clockwise:
        span = (a2 - a1) % 360
        if span < 1e-6: span = 360
        sgn = 1
    else:
        span = (a1 - a2) % 360
        if span < 1e-6: span = 360
        sgn = -1
    nseg = max(2, int(span / step_deg))
    pts = []
    for s in range(1, nseg):
        az = a1 + sgn * span * s / nseg
        lon, lat, _ = G.fwd(lon0, lat0, az, r)
        pts.append((lon, lat))
    return pts


def circle(center, radius_nm, n=72):
    lon0, lat0 = center
    return [G.fwd(lon0, lat0, 360 * k / n, radius_nm * NM)[:2] for k in range(n)]


# ---------- descripción lateral ----------
ARC_RE = re.compile(r"por un arco de sentido (horario|anti-?horario) de ([\d.,]+)\s*NM de radio centrado en " + COORD, re.I)
BORDER_RE = re.compile(r"siguiendo el l[ií]mite ([^0-9]*?) hasta", re.I)
CIRCLE_RE = re.compile(r"C[ií]rculo con centro en " + COORD + r"[^;]*?con radio de ([\d.,]+)\s*NM", re.I)


def parse_lateral(text):
    """Devuelve (lista de (lon,lat), notas) o (None, motivo)."""
    notes = []
    m = CIRCLE_RE.search(text)
    if m and "Desde" not in text[: m.start()]:
        c = (dms(m.group(3), m.group(4), 3), dms(m.group(1), m.group(2), 2))
        return circle(c, float(m.group(5).replace(",", "."))), ["círculo"]
    k = text.find("Desde")
    if k < 0:
        return None, "sin descripción 'Desde' ni círculo"
    body = text[k + 5:]
    e = body.find("para el punto de origen")
    if e < 0:
        return None, "sin cierre 'para el punto de origen'"
    body = body[:e]
    # tokenizar en orden: arcos, fronteras, coordenadas
    toks = []
    used = []
    for mm in ARC_RE.finditer(body):
        toks.append((mm.start(), "arc", mm)); used.append((mm.start(), mm.end()))
    for mm in BORDER_RE.finditer(body):
        toks.append((mm.start(), "border", mm)); used.append((mm.start(), mm.end()))
    for mm in COORD_RE.finditer(body):
        if any(a <= mm.start() < b for a, b in used):
            continue
        toks.append((mm.start(), "pt", mm))
    toks.sort(key=lambda t: t[0])
    pts = []
    pending = None  # ('arc', center, cw, r) | ('border', name)
    for _, kind, mm in toks:
        if kind == "pt":
            p = parse_coord(mm)
            if pending and pts:
                if pending[0] == "arc":
                    pts.extend(arc_points(pending[1], pts[-1], p, pending[2], pending[3]))
                else:
                    pts.append(("BORDER", pts[-1], p))
                pending = None
            if not pts or (isinstance(pts[-1], tuple) and pts[-1] != p):
                pts.append(p)
        elif kind == "arc":
            cw = mm.group(1).lower() == "horario"
            c = (dms(mm.group(5), mm.group(6), 3), dms(mm.group(3), mm.group(4), 2))
            pending = ("arc", c, cw, float(mm.group(2).replace(",", ".")))
            notes.append("arco")
        else:
            pending = ("border", mm.group(1).strip())
            notes.append("frontera: " + mm.group(1).strip())
    real = [p for p in pts if not (len(p) == 3 and p[0] == "BORDER")]
    if not real:
        return None, "sin coordenadas"
    if pending:  # cierra hacia el origen
        if pending[0] == "arc":
            pts.extend(arc_points(pending[1], pts[-1], real[0], pending[2], pending[3]))
        else:
            pts.append(("BORDER", pts[-1], real[0]))
    # resolver tramos de frontera eligiendo la dirección que deja un polígono válido
    border_idx = [i for i, p in enumerate(pts) if len(p) == 3 and p[0] == "BORDER"]
    if border_idx:
        choices = []
        for i in border_idx:
            f, b = border_paths(pts[i][1], pts[i][2])
            choices.append((f[1:-1], b[1:-1]))
        best = None
        import itertools
        for combo in itertools.product(*[(0, 1)] * len(choices)):
            out = []
            ci = 0
            for p in pts:
                if len(p) == 3 and p[0] == "BORDER":
                    out.extend(choices[ci][combo[ci]]); ci += 1
                else:
                    out.append(p)
            poly = Polygon(out)
            score = (poly.is_valid, -poly.length)
            if best is None or score > best[0]:
                best = (score, out)
        pts = best[1]
    return pts, notes


def ring_to_geo(pts):
    # GeoJSON exterior en sentido antihorario y cerrado
    poly = Polygon(pts)
    if not poly.is_valid:
        poly = poly.buffer(0)
        if poly.geom_type == "MultiPolygon":
            poly = max(poly.geoms, key=lambda p: p.area)
    from shapely.geometry.polygon import orient
    poly = orient(poly, 1.0)
    return [[round(x, 6), round(y, 6)] for x, y in poly.exterior.coords]


# ---------- alturas ----------
ALT_RE = re.compile(r"(UNL|GND|SFC|MSL|FL\s*-?\s*\d{2,3}|\d{1,3}(?:[.,]\d{3})+|\d+)\s*(FT|AGL)?\s*(AMSL|AGL|MSL)?", re.I)


def alt_ft(tok):
    """'FL 245' -> (24500,'FL'), '17500 FT' -> (17500,'AMSL'), GND -> (0,'GND'), UNL -> (66000,'UNL')"""
    t = tok.upper().replace(" ", "")
    if t in ("GND", "SFC"): return 0, "GND"
    if t == "MSL": return 0, "MSL"
    if t == "UNL": return 66000, "UNL"
    m = re.match(r"FL-?(\d+)", t)
    if m: return int(m.group(1)) * 100, "FL"
    m = re.match(r"([\d.,]+)FT(AGL|AMSL|MSL)?", t)
    if m:
        v = int(m.group(1).replace(".", "").replace(",", ""))
        return v, (m.group(2) or "AMSL").replace("MSL", "AMSL").replace("AAMSL", "AMSL")
    m = re.match(r"([\d.,]+)AGL", t)
    if m: return int(m.group(1).replace(".", "").replace(",", "")), "AGL"
    return None, None


STRATA_TOK = re.compile(r"(UNL|GND|SFC|FL\s?-?\s?\d{2,3}|\d{3,5}\s?FT(?:\s?(?:AGL|AMSL))?)|\b([A-G])\b")


def parse_strata(text):
    """'FL 245 A 17500 FT 17500 FT D 1500 FT' -> [(upper, cls, lower), ...]"""
    toks = []
    for m in STRATA_TOK.finditer(text):
        if m.group(1): toks.append(("alt", m.group(1)))
        else: toks.append(("cls", m.group(2)))
    out, i = [], 0
    while i < len(toks):
        if toks[i][0] != "alt": i += 1; continue
        up = toks[i][1]; cls = None; j = i + 1
        if j < len(toks) and toks[j][0] == "cls": cls = toks[j][1]; j += 1
        if j < len(toks) and toks[j][0] == "alt":
            out.append((up, cls, toks[j][1])); i = j + 1
        else:
            break
    return out
