# -*- coding: utf-8 -*-
"""Zonas de CBERS-4A WPM (2 m pancromatica + 8 m multiespectral) del curso.

El pansharpening a 2 m de un sitio entero pesa demasiado (Federal, 38 x 44 km, seria de 418 millones de
pixeles por banda), asi que se trabaja en zonas de unos 12 a 20 km: el casco urbano con capa Pléiades de
CONAE (para mirarlas juntas) o una ventana central del sitio. Cada zona tiene las fechas objetivo (las
Sentinel-2 del practico) y los practicos que la usan.
"""
ZONAS = {
    # caja: oeste, sur, este, norte (WGS84)
    "CONCORDIA": dict(caja=(-58.10739, -31.46685, -57.96937, -31.27755), sitio="B_CONCORDIA",
                      fechas={"20231104": ["Tp1", "Tp6"], "20260916": ["Tp10"]},
                      nota="casco urbano de Concordia y General Roca (la capa Pléiades Neo 2023 de CONAE)"),
    "GRAN_PARANA": dict(caja=(-60.595, -31.800, -60.445, -31.675), sitio="E_PARANA_DIAMANTE",
                        fechas={"20260916": ["Tp10"]},
                        nota="Paraná, San Benito y Oro Verde, 14 x 14 km (dentro de la capa Pléiades 2022 de CONAE)"),
    "DIAMANTE": dict(caja=(-60.71, -32.135, -60.575, -32.015), sitio="E1_DIAMANTE_BARRANCA",
                     fechas={"20260916": ["Tp7"]},
                     nota="sitio E1 completo: la ciudad y la barranca (contiene la capa Pléiades 2022 de CONAE)"),
    "FEDERAL": dict(caja=(-58.905, -30.860, -58.735, -30.715), sitio="C_FEDERAL",
                    fechas={"20210806": ["Tp9"], "20260916": ["Tp9"]},
                    nota="ventana central del sitio C, 16 x 16 km, sobre el monte (el casco urbano queda afuera)"),
    "IBICUY": dict(caja=(-59.20820, -33.78935, -59.09782, -33.68766), sitio="A2_IBICUY",
                   fechas={"20260916": ["Tp2", "Tp3"]},
                   nota="localidad de Ibicuy y su entorno (la capa Pléiades 2023 de CONAE)"),
    "BOVRIL": dict(caja=(-59.53, -31.42, -59.40, -31.29), sitio="F_BOVRIL",
                   fechas={"20230910": ["Tp8"]},
                   nota="sitio F completo (Bovril no tiene capa Pléiades de CONAE)"),
    "DELTA_A1": dict(caja=(-59.905, -33.269, -59.775, -33.161), sitio="A1_DELTA_QUEMAS",
                     fechas={"20200715": ["Tp5"], "20201013": ["Tp5"]},
                     nota="ventana central del sitio A1, 12 x 12 km, en las islas quemadas"),
}
# WPM: banda 0 pancromatica 2 m; 1 a 4 multiespectrales 8 m
BANDAS_WPM = {"BAND0": ("PAN", "pancromática, 450-900 nm, 2 m"), "BAND1": ("B1_azul", "azul, 450-520 nm, 8 m"),
              "BAND2": ("B2_verde", "verde, 520-590 nm, 8 m"), "BAND3": ("B3_rojo", "rojo, 630-690 nm, 8 m"),
              "BAND4": ("B4_IRC", "infrarrojo cercano, 770-890 nm, 8 m")}
COLECCION = "CB4A-WPM-L4-DN-1"
STAC = "https://data.inpe.br/bdc/stac/v1"
CITA = ("INPE / CAST, CBERS-4A cámara WPM, producto L4 (ortorrectificado, números digitales), licencia CC BY 4.0. "
        "Catálogo STAC del INPE, colección CB4A-WPM-L4-DN-1, https://data.inpe.br/stac/browser/collections/"
        "CB4A-WPM-L4-DN-1")
