import re, json, sys
sys.path.insert(0, "/home/claude/build")
from geo import parse_lateral, ring_to_geo, alt_ft, circle, arc_points

# ---------------- ENR 5.5 deportivas ----------------
s = json.load(open("/home/claude/raw/enr.json"))["ENR 5.5"].split("\n")
feats, omit = [], []
group = ""
for i, l in enumerate(s):
    c = l.split(" | ")
    if len(c) == 1 or (len(c) < 4):
        # encabezado de grupo (primera mitad, en español)
        h = c[0]
        m = re.match(r"(ZONA[S]? DE [^A-Z]*?[A-ZÁÉÍÓÚÑ0-9 \-–()/]+?)(?= PARAGLIDING| GLIDER|$)", h)
        if m and len(c) == 1: group = m.group(1).strip()
        continue
    first = c[0]
    if "Desde" not in first and "Circulo" not in first: continue
    k = first.find("Desde") if "Desde" in first else first.find("Circulo")
    name = first[:k].strip() or group.title()
    pts, notes = parse_lateral(first)
    if pts is None:
        omit.append({"name": name, "source": "ENR 5.5", "reason": notes}); continue
    v = c[1]
    m = re.match(r"\s*([\d.,]+ FT (?:AMSL|AGL))\s+(SFC|GND)", v)
    if not m:
        omit.append({"name": name, "source": "ENR 5.5", "reason": "límite vertical no legible: " + v}); continue
    up, lo = m.group(1), m.group(2)
    uf, ur = alt_ft(up)
    kind = "Planeadores" if "PLANEADOR" in group.upper() else ("Paramotor" if "PARAMOTOR" in name.upper() else "Parapente")
    feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring_to_geo(pts)]},
                  "properties": {"type": "DEP", "name": name if name.upper().startswith("Z") else f"{group.title()} – {name}",
                                 "group": group.title(), "class": "", "upper": up, "lower": lo, "upper_ft": uf, "upper_ref": ur,
                                 "lower_ft": 0, "lower_ref": "GND", "unit": c[2].strip()[:160],
                                 "callsign": kind, "freq": "", "remarks": c[3].strip()[:300] if len(c) > 3 else "",
                                 "geomNotes": notes, "source": "AIP ENR 5.5"}})

# ---------------- Zonas SK (cartas ENR 6.2 con texto extraíble) ----------------
def P(d, m, s_, h):  # grados minutos segundos
    v = d + m / 60 + s_ / 3600
    return -v if h in "SW" else v

SK = []
def sk(ident, typ, name, lo, up, ring, src, rem=""):
    SK.append((ident, typ, name, lo, up, ring, src, rem))

# SKR10 Palanquero – polígono P1..P5
sk("SKR10", "R", "PALANQUERO", "GND", "UNL", [
    (P(74,34,42,"W"), P(6,29,38,"N")), (P(73,56,0,"W"), P(6,53,38,"N")), (P(74,11,48,"W"), P(5,27,50,"N")),
    (P(74,44,24,"W"), P(5,15,14,"N")), (P(74,52,30,"W"), P(5,23,26,"N"))], "ENR 6.2-41", "Zona Militar de Defensa Nacional. Palanquero Control 127.9 MHz")
# SKR47 Riohacha
sk("SKR47", "R", "RIOHACHA", "GND", "6500 FT AMSL", [
    (P(73,4,20,"W"), P(11,27,38,"N")), (P(73,3,9,"W"), P(11,22,28,"N")), (P(73,6,51,"W"), P(11,20,46,"N")),
    (P(73,9,50,"W"), P(11,21,18,"N")), (P(73,10,7,"W"), P(11,24,10,"N"))], "ENR 6.2-75", "Reserva natural de fauna. TWR Almirante Padilla 118.4 MHz")
# SKR49 Tibú – círculo 1 NM
sk("SKR49", "R", "TIBU", "GND", "2000 FT AMSL", circle((P(72,42,22,"W"), P(8,38,20,"N")), 1), "ENR 6.2-77", "Restricción de drones / RPAS / UAS")
# SKR40 Bogotá
sk("SKR40", "R", "BOGOTA", "GND", "18500 FT AMSL", [
    (P(74,4,52,"W"), P(4,37,32,"N")), (P(74,4,13,"W"), P(4,36,40,"N")), (P(74,3,20,"W"), P(4,36,20,"N")),
    (P(74,4,7,"W"), P(4,34,16,"N")), (P(74,5,17,"W"), P(4,34,16,"N")), (P(74,6,27,"W"), P(4,35,1,"N"))], "ENR 6.2-69", "Seguridad Nacional. CCOFA FAC 133.5 MHz")
# SKD46 Melgar – círculo 2 NM
sk("SKD46", "D", "MELGAR", "GND", "8000 FT AMSL", circle((P(74,36,3,"W"), P(4,17,6,"N")), 2), "ENR 6.2-11", "Activación mediante NOTAM. APP Melgar 120.0 MHz")
# SKP30 Tolemaida – círculo 4 NM centrado en VOR/DME TOL (coordenada del VOR no figura en el texto de la carta)
# -> se omite (ver nota)
# SKP29 / SKR12 Apiay – P1..P5 con arcos DME VVC (centro VVC sin coordenada en la carta) -> trazado recto entre vértices publicados
vvc = None
apiay = [(P(73,29,39,"W"), P(4,6,0,"N")), (P(73,29,17,"W"), P(4,1,3,"N")), (P(73,35,38,"W"), P(3,58,4,"N")),
         (P(73,36,45,"W"), P(4,6,23,"N")), (P(73,30,42,"W"), P(4,6,23,"N"))]
# SKD43 Florencia
sk("SKD43", "D", "FLORENCIA", "GND", "6500 FT AMSL", None, "ENR 6.2-9", "Activación por NOTAM; durante activación se suspende el CTR FLA")


from geo import G
def short_arc(center, a, b, r):
    az1=G.inv(center[0],center[1],a[0],a[1])[0]%360; az2=G.inv(center[0],center[1],b[0],b[1])[0]%360
    cw=((az2-az1)%360)<=180
    return arc_points(center,a,b,cw,r)
VVC=(P(73,22,56,"W"),P(4,4,0,"N")); FLA=(P(75,34,10,"W"),P(1,35,16,"N")); TOL=(P(74,38,26,"W"),P(4,15,21,"N"))
p1,p2,p3,p4,p5=apiay
apiay_ring=[p1]+short_arc(VVC,p1,p2,7)+[p2,p3]+short_arc(VVC,p3,p4,14)+[p4,p5]
sk("SKP29","P","APIAY","GND","10500 FT AMSL",apiay_ring,"ENR 6.2-15","Zona Militar de Defensa Nacional. Arcos DME centrados en VOR/DME VVC (ENR 4.1)")
sk("SKR12","R","APIAY","10500 FT AMSL","17500 FT AMSL",apiay_ring,"ENR 6.2-45","Zona Militar de Defensa Nacional. Arcos DME centrados en VOR/DME VVC (ENR 4.1)")
f1=(P(75,33,34.97,"W"),P(1,30,16.33,"N")); f2=(P(75,30,37.24,"W"),P(1,31,42.45,"N")); f3=(P(75,25,39.89,"W"),P(1,26,45.83,"N")); f4=(P(75,32,46.43,"W"),P(1,23,19.14,"N"))
SK[:]=[x for x in SK if x[0]!="SKD43"]
sk("SKD43","D","FLORENCIA","GND","6500 FT AMSL",[f1]+short_arc(FLA,f1,f2,5)+[f2,f3]+short_arc(FLA,f3,f4,12)+[f4],"ENR 6.2-9","Activación por NOTAM; durante activación se suspende el CTR FLA. Arcos DME centrados en VOR/DME FLA (ENR 4.1)")
sk("SKP30","P","TOLEMAIDA","GND","8500 FT AMSL",circle(TOL,4),"ENR 6.2-17","Zona Militar de Defensa Nacional. Círculo de 4 NM centrado en VOR/DME TOL (ENR 4.1)")

for ident, typ, name, lo, up, ring, src, rem in SK:
    if ring is None: continue
    uf, ur = alt_ft(up); lf, lr = alt_ft(lo)
    feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring_to_geo(ring)]},
                  "properties": {"type": "SK" + typ, "name": f"{ident} {name}", "class": "", "upper": up, "lower": lo,
                                 "upper_ft": uf, "upper_ref": ur, "lower_ft": lf, "lower_ref": lr, "unit": "", "callsign": "",
                                 "freq": "", "remarks": rem, "geomNotes": [], "source": "AIP " + src}})

json.dump({"type": "FeatureCollection", "features": feats}, open("/home/claude/build/dep_sk.geojson", "w"), ensure_ascii=False)
json.dump(omit, open("/home/claude/build/omit_dep.json", "w"), ensure_ascii=False, indent=1)
for f in feats:
    p = f["properties"]; print(p["type"], p["name"][:60], p["lower"], p["upper"], len(f["geometry"]["coordinates"][0]))
print(omit)

# ---------------- Zonas deportivas ENR 6.4 (cartas con texto extraíble) ----------------
def D(s):
    m = re.match(r"([NS])(\d+)°(\d+)'([\d.]+)\"?\s*([EW])(\d+)°(\d+)'([\d.]+)", s.replace(" ", ""))
    lat = P(int(m.group(2)), int(m.group(3)), float(m.group(4)), m.group(1))
    lon = P(int(m.group(6)), int(m.group(7)), float(m.group(8)), m.group(5))
    return (lon, lat)
Z64 = [
 ("Zona Parapente 26 (Zipacón)", "10500 FT AMSL", ["N04°47'28\" W074°22'18\"","N04°47'03\" W074°22'10\"","N04°46'08\" W074°22'30\"","N04°45'30\" W074°22'36\"","N04°45'36\" W074°23'07\"","N04°47'24\" W074°22'55\""], "ENR 6.4-39", "Bogotá Radio 126.9 MHz. Entre salida y puesta del sol, VMC"),
 ("Zona Parapente 27 (Barbosa)", "8500 FT AMSL", ["N06°30'45.36\" W075°21'33.37\"","N06°26'55.76\" W075°21'57.66\"","N06°28'57.4\" W075°19'34.83\"","N06°28'55.03\" W075°23'41.32\""], "ENR 6.4-41", "Requiere autorización TWR Olaya Herrera 118.0 MHz"),
 ("Zona Aviación Deportiva 28 (Cúcuta)", "500 FT AMSL", ["N08°21'27\" W072°28'37\"","N08°21'20\" W072°24'51\"","N08°19'44\" W072°25'23\"","N08°10'19\" W072°23'44\"","N08°09'30\" W072°27'48\"","N08°12'33\" W072°27'55\""], "ENR 6.4-43", "Controlado por Camilo Daza TWR 118.1 MHz"),
 ("Zona Paramotor 32 (Tocaima)", "2000 FT AMSL", ["N04°29'40.60\" W074°39'04.90\"","N04°27'18.00\" W074°38'20.30\"","N04°23'33.90\" W074°42'04.56\"","N04°24'12.47\" W074°44'33.16\""], "ENR 6.4-51", "Coordinación TWR Santiago Vila 118.4 / Melgar APP 120.0. 1100-2300 UTC"),
 ("Zona Paramotor 33 (Tatacoa)", "2000 FT AMSL", ["N03°14'14.50\" W075°11'21.50\"","N03°13'56.10\" W075°06'19.10\"","N03°13'01.30\" W075°11'24.70\""], "ENR 6.4-53", "Coordinación TWR Benito Salas / Neiva APP 127.10"),
 ("Zona Parapente 34 (San Rafael)", "7500 FT AMSL", ["N06°18'27.00\" W075°08'30.00\"","N06°18'48.00\" W075°01'06.00\"","N06°16'24.00\" W075°00'38.00\"","N06°14'11.00\" W075°06'57.00\"","N06°14'49.00\" W075°09'07.00\""], "ENR 6.4-55", "Escucha Medellín APP Norte 126.1 MHz. 1300-2230 UTC"),
 ("Zona Parapente 35 (Balboa)", "9500 FT AMSL", ["N02°04'22.00\" W077°12'51.00\"","N02°04'37.00\" W077°06'13.00\"","N01°54'41.00\" W077°14'50.00\"","N01°56'15.00\" W077°18'24.00\""], "ENR 6.4-57", "Escucha TWR Guillermo León Valencia 118.45 MHz"),
 ("Zona Parapente/Paramotor 36 (Ricaurte)", "2000 FT AMSL", ["N04°18'21.00\" W074°45'21.00\"","N04°19'01.00\" W074°42'38.00\"","N04°18'15.00\" W074°41'59.00\"","N04°16'23.40\" W074°43'45.00\"","N04°16'26.00\" W074°44'46.15\""], "ENR 6.4-59", "Escucha Santiago Vila 118.4 MHz"),
 ("Zona Parapente 37 (Ipiales)", "9500 FT AMSL", ["N01°17'33.00\" W077°32'46.00\"","N01°17'27.00\" W077°27'48.00\"","N01°07'02.00\" W077°22'28.00\"","N01°02'38.00\" W077°29'45.00\"","N01°09'43.00\" W077°34'52.00\""], "ENR 6.4-61", "Escucha APP Andes 126.7 / TWR San Luis 118.3"),
 ("Zona Parapente 38 (Turmequé)", "10000 FT AMSL", ["N05°25'45.08\" W073°28'17.52\"","N05°21'08.73\" W073°25'34.25\"","N05°15'24.03\" W073°33'45.45\"","N05°17'55.73\" W073°36'49.19\""], "ENR 6.4-63", "Escucha Bogotá Información 126.9 MHz"),
]
for name, up, pts, src, rem in Z64:
    uf, ur = alt_ft(up)
    feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring_to_geo([D(p) for p in pts])]},
                  "properties": {"type": "DEP", "name": name, "group": "Zonas ENR 6.4", "class": "G", "upper": up, "lower": "GND",
                                 "upper_ft": uf, "upper_ref": ur, "lower_ft": 0, "lower_ref": "GND", "unit": "", "callsign": "Parapente/Paramotor",
                                 "freq": "", "remarks": rem, "geomNotes": [], "source": "AIP " + src}})
json.dump({"type": "FeatureCollection", "features": feats}, open("/home/claude/build/dep_sk.geojson", "w"), ensure_ascii=False)
print("total", len(feats))
