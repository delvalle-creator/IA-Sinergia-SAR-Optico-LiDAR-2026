# -*- coding: utf-8 -*-
"""
pleiades_conae_wms.py - Capas Pléiades / Pléiades Neo de CONAE (proyecto Impactar) para QGIS.

CONAE publica, para gobiernos locales, mosaicos RGB color real de Pléiades (0,5 m) y Pléiades Neo
(0,3 m) de 2022-2023, sólo como servicio de mapas (WMS/WMTS, sin descarga de datos). Este programa
escribe, sin conectarse a la red:

  00_COMUN\\10_Alta_resolucion_CONAE\\
      CONAE_Impactar_conexion_WMS_QGIS.xml   conexión para QGIS (Administrar conexiones > Cargar)
      <LOCALIDAD>_<AÑO>_Pleiades_CONAE.xml    una capa por localidad (archivo GDAL WMS: se arrastra a QGIS)
      LEEME.md
  <Tp>\\02_Subsets_SNAP_QGIS\\Pleiades_CONAE_WMS\\   las capas de las localidades de ese práctico + LEEME.md

Las capas necesitan internet. Son para mirar y digitalizar (referencia), no para calcular: no traen
infrarrojo ni reflectancia, y la fecha exacta no está publicada (sólo el año).

Uso: python pleiades_conae_wms.py      (desde 00_COMUN, entorno sar)
"""
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from configuracion_comun import COMUN, ruta_tp   # noqa: E402

WMS = "https://geotematico01.conae.gov.ar/geoserver/wms"
VISOR = "https://geoportal.conae.gov.ar/mapstore/visor-alta.html#/viewer/openlayers/geoservicios_impactar"
CATALOGO = "https://catalogos.conae.gov.ar/catalogo/catalogoGeoServiciosOGC.html"

# capa: (titulo, satelite, oeste, este, sur, norte)  -- caja de la capa en el GetCapabilities de CONAE (20/10/2026)
CAPAS = {
    "EntreRios_Concordia_2023": ("Concordia y General Roca, 2023", "Pléiades Neo",
                                 -58.10739, -57.96937, -31.46685, -31.27755),
    "EntreRios_GranParana_2022": ("Gran Paraná (Paraná, Oro Verde, San Benito, Colonia Avellaneda, Sauce Montrull, "
                                  "Sauce Pinto), 2022", "Pléiades", -60.58622, -60.33976, -31.85766, -31.69070),
    "EntreRios_Diamante_2022": ("Diamante, 2022", "Pléiades", -60.66451, -60.59340, -32.09432, -32.03260),
    "EntreRios_Federal_2022": ("Federal, 2022", "Pléiades", -58.80863, -58.76209, -30.97337, -30.92339),
    "EntreRios_LaPaz_2022": ("La Paz, 2022", "Pléiades", -59.66559, -59.56946, -30.78034, -30.71515),
    "EntreRios_Villaguay_2023": ("Villaguay, 2023", "Pléiades Neo", -59.08134, -58.99067, -31.90704, -31.80539),
    "EntreRios_Ibicuy_2023": ("Ibicuy, 2023", "Pléiades", -59.20820, -59.09782, -33.78935, -33.68766),
    "EntreRios_Victoria_2022": ("Victoria, 2022", "Pléiades", -60.19250, -60.09286, -32.66011, -32.57580),
    "EntreRios_VillaParanacito_2022": ("Villa Paranacito, 2022", "Pléiades", -58.67721, -58.64249, -33.73098,
                                       -33.69378),
}
PRACTICOS = {
    "Tp1": ["EntreRios_Concordia_2023"],
    "Tp2": ["EntreRios_Ibicuy_2023"],
    "Tp3": ["EntreRios_Ibicuy_2023"],
    "Tp4": list(CAPAS),
    "Tp6": ["EntreRios_Concordia_2023"],
    "Tp7": ["EntreRios_Diamante_2022", "EntreRios_GranParana_2022"],
    "Tp9": ["EntreRios_Federal_2022", "EntreRios_LaPaz_2022", "EntreRios_Villaguay_2023"],
    "Tp10": ["EntreRios_Concordia_2023", "EntreRios_GranParana_2022", "EntreRios_Diamante_2022"],
    "Tp11": list(CAPAS),
}
SIN_CAPA = {"Tp5": "las quemas del Delta (A1) son en islas, lejos de las localidades con capa (Victoria y Villa "
                   "Paranacito no caen en el sitio)",
            "Tp8": "Bovril no tiene capa en el servicio de CONAE"}


def merc(lon, lat):
    r = 6378137.0
    return r * math.radians(lon), r * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def gdal_wms(capa):
    _, sat, o, e, s, n = CAPAS[capa]
    x0, y0 = merc(o, s)
    x1, y1 = merc(e, n)
    # 0,5 m en el terreno = 0,5 / cos(lat) en Mercator (0,3 m para Pléiades Neo)
    lat = math.radians((s + n) / 2)
    res = (0.3 if "Neo" in sat else 0.5) / math.cos(lat)
    return ("<GDAL_WMS>\n"
            "  <Service name=\"WMS\">\n"
            "    <Version>1.1.1</Version>\n"
            "    <ServerUrl>%s?</ServerUrl>\n"
            "    <SRS>EPSG:3857</SRS>\n"
            "    <ImageFormat>image/png</ImageFormat>\n"
            "    <Transparent>TRUE</Transparent>\n"
            "    <Layers>Localidades:%s</Layers>\n"
            "    <Styles></Styles>\n"
            "  </Service>\n"
            "  <DataWindow>\n"
            "    <UpperLeftX>%.2f</UpperLeftX>\n    <UpperLeftY>%.2f</UpperLeftY>\n"
            "    <LowerRightX>%.2f</LowerRightX>\n    <LowerRightY>%.2f</LowerRightY>\n"
            "    <SizeX>%d</SizeX>\n    <SizeY>%d</SizeY>\n"
            "  </DataWindow>\n"
            "  <Projection>EPSG:3857</Projection>\n"
            "  <BandsCount>4</BandsCount>\n"
            "  <BlockSizeX>512</BlockSizeX>\n  <BlockSizeY>512</BlockSizeY>\n"
            "  <ZeroBlockHttpCodes>204,404</ZeroBlockHttpCodes>\n"
            "  <Cache/>\n"
            "</GDAL_WMS>\n" % (WMS, capa, x0, y1, x1, y0, round((x1 - x0) / res), round((y1 - y0) / res)))


CONEXION = ("<!DOCTYPE connections>\n<qgsWMSConnections version=\"1.0\">\n"
            "  <wms name=\"CONAE Impactar (Pleiades y Pleiades Neo)\" url=\"%s\" ignoreGetMapURI=\"false\" "
            "ignoreGetFeatureInfoURI=\"false\" ignoreAxisOrientation=\"false\" invertAxisOrientation=\"false\" "
            "smoothPixmapTransform=\"false\" dpiMode=\"7\" referer=\"\" username=\"\" password=\"\"/>\n"
            "</qgsWMSConnections>\n" % WMS)

FUENTE = ("Fuente: CONAE, proyecto Impactar. Mosaicos RGB color real de Pléiades (0,5 m) y Pléiades Neo (0,3 m), "
          "Airbus Defence and Space, %s. Servicio WMS/WMTS: %s; catálogo: %s; visor: %s")


def leeme(capas, titulo, nota=""):
    t = ["# %s" % titulo, "",
         "Imágenes de muy alta resolución de CONAE (proyecto Impactar), **sólo para mirar y digitalizar**: son "
         "mosaicos RGB color real ya armados, sin infrarrojo ni reflectancia, servidos por internet (WMS). CONAE "
         "no ofrece la descarga de los datos por este servicio; los datos multiespectrales requieren un convenio "
         "con CONAE (atencion.usuario@conae.gov.ar). Cada capa cubre el casco urbano de la localidad; la fecha "
         "exacta no está publicada, sólo el año.", "",
         "**Cómo usarlas en QGIS** (hace falta internet):", "",
         "1. Arrastre el archivo `.xml` de la localidad a la ventana de QGIS (o `Capa > Añadir capa > Añadir capa "
         "ráster…` / `Layer > Add Layer > Add Raster Layer…`). QGIS la abre como una capa ráster común.",
         "2. O cargue la conexión: `Capa > Añadir capa > Añadir capa WMS/WMTS…` (`Add WMS/WMTS Layer…`), botón "
         "`Cargar` (`Load`), archivo `CONAE_Impactar_conexion_WMS_QGIS.xml` de `00_COMUN\\10_Alta_resolucion_CONAE`; "
         "`Conectar` y elija la capa por su nombre.", "",
         "Están en EPSG:3857 (el servicio no ofrece la UTM 21 S); QGIS las reproyecta al vuelo sobre la grilla del "
         "curso.", "",
         "| Archivo | Localidad | Satélite | Capa del servicio |", "|---|---|---|---|"]
    for c in capas:
        tit, sat = CAPAS[c][:2]
        t.append("| `%s_Pleiades_CONAE.xml` | %s | %s | `Localidades:%s` |" % (c.replace("EntreRios_", ""), tit, sat, c))
    if nota:
        t += ["", nota]
    sats = sorted({CAPAS[c][1] for c in capas})
    t += ["", FUENTE % (" y ".join(sats) + ", 2022-2023", WMS, CATALOGO, VISOR), ""]
    return "\n".join(t)


def main():
    base = os.path.join(COMUN, "10_Alta_resolucion_CONAE")
    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, "CONAE_Impactar_conexion_WMS_QGIS.xml"), "w", encoding="utf-8") as f:
        f.write(CONEXION)
    for c in CAPAS:
        with open(os.path.join(base, "%s_Pleiades_CONAE.xml" % c.replace("EntreRios_", "")), "w",
                  encoding="utf-8") as f:
            f.write(gdal_wms(c))
    with open(os.path.join(base, "LEEME.md"), "w", encoding="utf-8") as f:
        f.write(leeme(list(CAPAS), "Pléiades y Pléiades Neo de CONAE en las localidades del curso",
                      "Bovril no tiene capa. Sitios por práctico: " + "; ".join(
                          "%s: %s" % (tp, ", ".join(CAPAS[c][0].split(",")[0] for c in cs))
                          for tp, cs in PRACTICOS.items() if tp not in ("Tp4", "Tp11"))))
    print("Comun: %s (%d capas)" % (base, len(CAPAS)))
    for tp, cs in PRACTICOS.items():
        d = ruta_tp(tp, "02_Subsets_SNAP_QGIS", "Pleiades_CONAE_WMS")
        os.makedirs(d, exist_ok=True)
        for c in cs:
            with open(os.path.join(d, "%s_Pleiades_CONAE.xml" % c.replace("EntreRios_", "")), "w",
                      encoding="utf-8") as f:
                f.write(gdal_wms(c))
        with open(os.path.join(d, "LEEME.md"), "w", encoding="utf-8") as f:
            f.write(leeme(cs, "%s · Pléiades y Pléiades Neo de CONAE" % tp))
        print("%s: %d capas en %s" % (tp, len(cs), d))
    for tp, motivo in SIN_CAPA.items():
        print("%s: sin capa (%s)" % (tp, motivo))


if __name__ == "__main__":
    main()
