# Transcripciones de cartas ENR 6.2 / 6.4 (imagen) — leídas visualmente
# tipos: poly (vértices), circle (centro, radio NM), dme (centro VOR, decl W en grados, segmentos)
CH = {}
CH["SKD36"] = dict(kind="dme_pts", src="ENR 6.2-3", lo="GND", up="10000 FT AGL", center="ZIP",
    pts=[("N04°59'05\"","W073°55'10\""),("N04°59'57\"","W073°54'50\""),("N04°59'41\"","W073°53'52\""),("N04°58'38\"","W073°54'16\"")],
    segs=["arc4.5","line","arc5.5","line"], rem="Protección infraestructura energética. TWR Flaminio Suárez 118.8 MHz")
CH["SKD37"] = dict(kind="dme_rad", src="ENR 6.2-5", lo="GND", up="4500 FT AGL", center="EJA", decl=7+1/60,
    rad=[(322,4.5),(300,4.5),(300,6),(322,6)], segs=["arc","line","arc","line"], rem="Protección infraestructura energética")
CH["SKD41"] = dict(kind="circle", src="ENR 6.2-7", lo="GND", up="FL 200", c=("N04°53'00\"","W075°19'00\""), r=6,
    rem="Zona de actividad volcánica (Nevado del Ruiz). La carta indica FL-200; el ENR 5.1 dice 20000 FT AGL")
CH["SKP28"] = dict(kind="circle", src="ENR 6.2-13", lo="GND", up="9000 FT AGL", center="TQS", r=10, rem="Zona Militar de Defensa Nacional")
CH["SKP31"] = dict(kind="circle", src="ENR 6.2-19", lo="GND", up="14000 FT AMSL", center="PAL", r=7, rem="Zona Militar de Defensa Nacional")
CH["SKP32"] = dict(kind="circle", src="ENR 6.2-21", lo="GND", up="8000 FT AMSL", c=("N03°27'30\"","W076°30'00\""), r=3, rem="Zona Militar de Defensa Nacional")
CH["SKP35"] = dict(kind="dme_rad", src="ENR 6.2-23", lo="GND", up="12000 FT AMSL", center="ZIP", decl=6+32/60,
    rad=[(204,4.8),(184,4.8),(184,6.8),(204,6.8)], segs=["arc","line","arc","line"], rem="Zona Militar de Defensa Nacional")
CH["SKP48"] = dict(kind="circle", src="ENR 6.2-25", lo="GND", up="12500 FT AMSL", c=("N05°31'43\"","W068°40'36\""), r=10, rem="Zona Militar de Defensa Nacional. Centro en ARP SKUA")
CH["SKR1"] = dict(kind="poly", src="ENR 6.2-27", lo="500 FT AMSL", up="3500 FT AMSL",
    pts=[("N11°07'10\"","W074°45'12\""),("N11°07'10\"","W074°39'12\""),("N11°03'09\"","W074°39'12\""),("N11°03'10\"","W074°45'12\"")], rem="Zona militar de instrucción. 12 h, VMC, activación a solicitud de la FAC")
CH["SKR5 N"] = dict(kind="poly", grp="SKR5", sub="Norte", src="ENR 6.2-29", lo="GND", up="6500 FT AMSL",
    pts=[("N04°03'50\"","W076°21'48\""),("N04°01'50\"","W076°12'48\""),("N03°53'30\"","W076°19'23.11\""),("N03°51'32.85\"","W076°18'8.16\""),("N03°47'50\"","W076°18'40\""),("N03°47'50\"","W076°30'48\"")],
    rem="Zona Militar de Seguridad y Defensa Nacional. Guabito Información 129.0 MHz")
CH["SKR5 NC"] = dict(kind="poly", grp="SKR5", sub="Norte – Corredor", src="ENR 6.2-29", lo="GND", up="5000 FT AMSL",
    pts=[("N03°47'50\"","W076°28'18\""),("N03°47'50\"","W076°23'18\""),("N03°31'20\"","W076°29'18\""),("N03°31'20\"","W076°34'18\"")],
    rem="Corredor de SKR5 Norte. Guabito Información 129.0 MHz")
CH["SKR5 S"] = dict(kind="poly", grp="SKR5", sub="Sur", src="ENR 6.2-31", lo="GND", up="8000 FT AMSL",
    pts=[("N03°31'20\"","W076°34'18\""),("N03°31'20\"","W076°29'18\""),("N03°10'35\"","W076°29'18\""),("N03°10'35\"","W076°15'33\""),("N02°36'50\"","W076°29'48\""),("N02°36'50\"","W076°51'48\"")],
    rem="Zona militar de instrucción. Guabito Información 129.0 MHz")
CH["SKR6"] = dict(kind="poly", src="ENR 6.2-33", lo="GND", up="17500 FT AGL",
    pts=[("N03°04'55\"","W074°20'00\""),("N03°18'47\"","W074°07'03\""),("N03°18'47\"","W073°22'06\""),("N02°41'03\"","W073°00'00\""),("N01°45'00\"","W073°00'00\""),("N01°45'00\"","W074°20'00\"")],
    rem="Zona Militar de Defensa Nacional. La Macarena TWR 118.2 MHz")
CH["SKR7"] = dict(kind="poly", src="ENR 6.2-35", lo="9000 FT AMSL", up="FL 190",
    pts=[("N04°17'50\"","W072°58'38\""),("N05°04'20\"","W071°39'03\""),("N03°26'20\"","W071°39'03\""),("N03°54'50\"","W072°58'38\"")],
    rem="Zona Militar de Defensa Nacional. Tornado Control 134.0 MHz")
CH["SKR8"] = dict(kind="poly", src="ENR 6.2-37", lo="GND", up="7000 FT AMSL",
    pts=[(a,b) for a,b in [("N11°32'14\"","W074°00'45\""),("N11°26'17\"","W073°29'45\""),("N12°02'00\"","W072°24'00\""),("N12°23'00\"","W072°18'30\""),("N12°39'36\"","W071°40'31\""),("N12°29'13\"","W071°25'39\""),("N12°00'21\"","W071°01'38\""),("N11°49'15\"","W071°26'01\""),("N11°39'55\"","W071°58'37\""),
         ("N11°09'29\"","W072°15'30\""),("N11°09'50\"","W072°21'10\""),("N11°07'40\"","W072°28'10\""),("N11°05'11\"","W072°30'29\""),("N11°04'03\"","W072°30'29\""),("N10°54'14\"","W072°37'13\""),("N10°53'50\"","W072°39'23\""),("N10°31'15\"","W072°51'58\""),("N10°31'15\"","W074°00'45\"")]],
    rem="Zona Militar de Defensa Nacional. DRACO 126.7 MHz")
CH["SKR9"] = dict(kind="poly", src="ENR 6.2-39", lo="GND", up="11500 FT AMSL",
    pts=[("N04°11'41\"","W074°48'12\""),("N04°18'15\"","W074°41'59\""),("N04°20'19\"","W074°43'45\""),("N04°30'38\"","W074°34'12\""),("N03°52'08\"","W074°34'27\""),("N03°52'08\"","W074°50'32\""),("N04°03'48\"","W074°51'04\"")],
    segs={3:("GIR",26)}, rem="Zona Militar de Defensa Nacional. APP Melgar 120.0 MHz. Arco de 26 DME de GIR entre P-4 y P-5")
CH["SKR11"] = dict(kind="poly", src="ENR 6.2-43", lo="9000 FT AMSL", up="FL 190",
    pts=[("N10°44'42\"","W074°13'20\""),("N10°40'20\"","W073°21'30\""),("N09°38'41\"","W073°53'47\""),("N10°04'15\"","W074°15'01\""),("N10°37'59\"","W074°14'28\"")],
    segs={1:("BAQ",90),4:("BAQ",38)}, rem="Zona Militar de Defensa Nacional. DRACO 126.7 MHz. Arcos DME de BAQ (90 NM y 38 NM)")
CH["SKR16"] = dict(kind="union", src="ENR 6.2-47", lo="GND", up="4500 FT AMSL",
    circle=(("N09°24'04\"","W075°41'28\""),5), pts=[("N09°26'48\"","W075°45'39\""),("N09°31'37\"","W075°50'49\""),("N09°34'42\"","W075°47'04\""),("N09°28'42\"","W075°43'20\""),("N09°24'04\"","W075°41'28\"")],
    rem="Zona Militar de Defensa Nacional. Base Naval Coveñas 126.2 MHz")
CH["SKR17"] = dict(kind="poly", src="ENR 6.2-49", lo="GND", up="2000 FT AMSL",
    pts=[("N10°24'02\"","W075°36'12\""),("N10°24'02\"","W075°33'42\""),("N10°26'50\"","W075°33'42\""),("N10°24'02\"","W075°32'12\""),("N10°19'10\"","W075°32'12\""),("N10°19'10\"","W075°36'12\"")],
    rem="Zona Militar de Defensa Nacional. TWR Rafael Núñez 118.3 MHz")
CH["SKR18"] = dict(kind="poly", src="ENR 6.2-51", lo="GND", up="5500 FT AMSL",
    pts=[("N04°14'37\"","W077°16'24\""),("N04°04'35\"","W077°09'44\""),("N03°49'32\"","W077°17'49\""),("N03°49'32\"","W077°29'51\"")],
    segs={1:("BUN",None),3:("BUN",None)}, rem="Zona Militar de Defensa Nacional. TWR Juanchaco 120.5 MHz. Arcos DME de BUN; el texto dice 18 DME en ambos, la carta rotula el exterior como 30 DME: se usó la distancia real de los vértices")
CH["SKR19"] = dict(kind="poly", src="ENR 6.2-53", lo="GND", up="7500 FT AMSL",
    pts=[("N06°10'25\"","W075°39'25\""),("N06°10'45\"","W075°37'59\""),("N06°08'38\"","W075°37'30\""),("N06°08'18\"","W075°38'55\"")],
    rem="Zona Militar de Seguridad Nacional. TWR Olaya Herrera 118.9 MHz")
CH["SKR23"] = dict(kind="poly", src="ENR 6.2-55", lo="5000 FT AMSL", up="18000 FT AMSL",
    pts=[("N11°05'03\"","W075°22'03\""),("N11°14'30\"","W075°14'57\""),("N10°59'17\"","W075°00'57\""),("N10°55'14\"","W075°04'18\"")],
    segs={0:("BAQ",35),2:("BAQ",15)}, rem="Zona Militar de Instrucción. DRACO 126.7 MHz. 12 h, solo VMC")
CH["SKR24"] = dict(kind="poly", src="ENR 6.2-57", lo="10000 FT AMSL", up="18000 FT AMSL",
    pts=[("N11°22'57\"","W074°52'27\""),("N11°18'01\"","W074°34'08\""),("N11°02'41\"","W074°43'08\""),("N11°04'52\"","W074°52'01\"")],
    segs={0:("BAQ",35),2:("BAQ",17)}, rem="Zona militar. Arcos DME de BAQ (35 y 17 NM), radiales 006° y 037°")
CH["SKR25"] = dict(kind="poly", src="ENR 6.2-59", lo="GND", up="5000 FT AMSL",
    pts=[("N08°08'50\"","W076°52'48\""),("N08°08'50\"","W076°47'48\""),("N08°05'50\"","W076°47'48\""),("N08°05'50\"","W076°52'48\"")],
    rem="Zona Militar de Seguridad Nacional (Golfo de Urabá). 122.9 MHz")
CH["SKR26"] = dict(kind="poly", src="ENR 6.2-61", lo="GND", up="12500 FT AMSL",
    pts=[("N05°40'00\"","W069°30'36\""),("N05°55'00\"","W068°00'00\""),("N04°51'00\"","W068°00'00\""),("N04°35'00\"","W069°30'36\"")],
    rem="Zona Militar de Seguridad Nacional. Marandúa Aproximación 124.1 MHz")
CH["SKR27"] = dict(kind="diff", src="ENR 6.2-63", lo="GND", up="9000 FT AMSL", center="TQS", r=35, cut=("FLA",33),
    rem="Zona Militar de Seguridad Nacional. Círculo de 35 NM centrado en VOR/DME TQS, recortado por el arco de 33 NM de FLA (entre N01°03'35\" W075°43'23\" y N01°18'32\" W075°05'43\")")
CH["SKR33"] = dict(kind="diff2", src="ENR 6.2-65", lo="GND", up="13000 FT AMSL", c=("N05°38'10\"","W073°19'38\""), r=5,
    cutr=2, cutpts=[("N05°33'52\"","W073°22'10\""),("N05°33'19\"","W073°18'36\"")],
    rem="Zona Militar de Seguridad Nacional (INPEC, Tunja). Círculo de 5 NM recortado por un arco de 2 NM centrado en el umbral 23 de SKTJ; el centro del arco se calculó a partir de los dos puntos de corte publicados")
CH["SKR39"] = dict(kind="poly", src="ENR 6.2-67", lo="GND", up="2500 FT AMSL",
    pts=[("N04°15'24\"","W074°52'38\""),("N04°17'10\"","W074°50'52\""),("N04°15'45\"","W074°49'27\""),("N04°13'58\"","W074°51'13\"")],
    rem="Zona militar. TWR Flandes (FAC) 134.7 MHz")
CH["SKR44"] = dict(kind="poly", src="ENR 6.2-71", lo="GND", up="8500 FT AMSL",
    pts=[("N01°42'13\"","W073°13'38\""),("N01°42'13\"","W072°58'29\""),("N00°14'23\"","W071°37'28\""),("S00°07'56\"","W071°32'33\""),("S00°19'12\"","W071°32'33\""),("S00°19'12\"","W071°47'50\""),("N00°00'35\"","W074°02'14\""),("N00°39'03\"","W074°02'14\""),("N00°39'03\"","W073°26'48\""),("N01°25'06\"","W073°26'48\"")],
    rem="Seguridad Nacional / Parques Nacionales (Chiribiquete). Tornado Control 134.0 MHz; autoanuncios 122.9 MHz")
CH["SKR45"] = dict(kind="circle", src="ENR 6.2-73", lo="GND", up="1000 FT AMSL", c=("N04°38'40.695\"","W074°05'44.365\""), r=0.5,
    rem="Restricción de drones (CAN, Bogotá). El texto dice 'circunferencia de 1NM'; el dibujo a escala muestra 1 NM de diámetro, por eso se dibujó con radio 0,5 NM")
CH["SKR50"] = dict(kind="poly", src="ENR 6.2-79", lo="GND", up="18000 FT AMSL",
    pts=[("N08°36'47\"","W073°32'10\""),("N09°13'34\"","W073°02'10\""),("N09°03'56\"","W072°59'20\""),("N09°04'02\"","W072°49'40\""),("N08°36'04\"","W072°42'17\""),("N08°21'38\"","W072°27'34\""),("N08°06'32\"","W072°23'04\""),("N08°03'24\"","W072°26'03\""),("N08°27'56\"","W072°44'26\""),("N08°05'52\"","W073°29'22\""),("N08°23'58\"","W073°26'38\"")],
    rem="Zona Militar de Seguridad y Defensa Nacional. URANO 126.3 MHz. El ENR 5.1 dice 18000 FT AGL; la carta, GND/18000'")
DEP = {}
DEP["22"] = dict(name="Zona Parapente 22 (Valle/Risaralda)", src="ENR 6.4-23", up="4500 FT AMSL",
    pts=[("N04°41'52\"","W076°06'00\""),("N04°38'59\"","W075°55'48\""),("N04°34'27\"","W075°57'23\""),("N04°36'49\"","W076°04'10\"")],
    rem="Espacio no controlado. APP Pereira 120.7 / TWR Matecaña 118.7. 1700-2200Z")
DEP["23"] = dict(name="Zona Parapente 23 (Armenia)", src="ENR 6.4-33", up="7500 FT AMSL",
    pts=[("N04°34'19.33\"","W075°38'36.57\""),("N04°33'53.76\"","W075°36'08.28\""),("N04°22'37.05\"","W075°38'56.46\""),("N04°20'04.09\"","W075°43'04.47\""),("N04°19'00.26\"","W075°47'04.88\""),("N04°21'28.99\"","W075°46'29.65\""),("N04°21'45.23\"","W075°43'37.91\""),("N04°24'03.07\"","W075°41'08.05\"")],
    rem="Requiere autorización TWR El Edén 118.5 MHz. Desde 1400 UTC hasta la puesta del sol")
DEP["24"] = dict(name="Zona Parapente 24 (Ibagué)", src="ENR 6.4-35", up="7500 FT AMSL",
    pts=[("N04°29'30.29\"","W075°13'38.45\""),("N04°29'50.37\"","W075°12'36.25\""),("N04°29'15.52\"","W075°12'07.60\""),("N04°27'57.65\"","W075°12'17.36\""),("N04°27'47.71\"","W075°12'19.34\""),("N04°27'44.06\"","W075°12'22.72\""),("N04°28'19.16\"","W075°13'09.39\"")],
    rem="Requiere autorización TWR Perales 118.3 MHz. Entre salida y puesta del sol")
DEP["25"] = dict(name="Zona Aviación Deportiva 25 – Paracaidismo (Xielo)", src="ENR 6.4-37", up="10500 FT AMSL",
    pts=[("N04°24'11.92\"","W074°45'25.66\""),("N04°23'34.56\"","W074°43'01.63\""),("N04°19'44.76\"","W074°44'01.24\""),("N04°20'22.12\"","W074°46'25.27\"")],
    rem="Paracaidismo. Coordinación TWR Santiago Vila 118.4 / BOG Información 126.9 / Melgar APP 120.0")
DEP["29"] = dict(name="Zona Parapente 29 (Pitalito)", src="ENR 6.4-45", up="1000 FT AGL",
    pts=[("N01°54'15.82\"","W076°07'48.66\""),("N01°50'46.07\"","W076°09'46.75\""),("N01°51'37.82\"","W076°14'00.18\""),("N01°53'06.17\"","W076°13'12.98\"")],
    rem="Espacio no controlado; escucha 118.1 MHz Contador Torre. Ojo: el dibujo de la carta no coincide del todo con las coordenadas publicadas (se usaron las coordenadas)")
DEP["31"] = dict(name="Zona Parapente 31 (Laguna de Tota)", src="ENR 6.4-47", up="1500 FT AGL",
    pts=[("N05°30'24.24\"","W072°57'58.52\""),("N05°30'56.73\"","W072°58'28.86\""),("N05°32'51.62\"","W072°56'47.26\""),("N05°32'15.95\"","W072°56'03.33\"")],
    rem="Espacio no controlado; escucha Bucaramanga Aproximación 119.0 MHz; autoanuncios 122.9")
