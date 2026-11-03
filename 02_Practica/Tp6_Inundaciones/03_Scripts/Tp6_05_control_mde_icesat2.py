# -*- coding: utf-8 -*-
"""
Tp6_05_control_mde_icesat2.py   [SE CORRE]   Tp6, paso 6 de la guia - control del MDE
============================================================================
"Verificar el MDE con elevaciones de terreno de ICESat-2" (diapositiva 29).

La profundidad de Tp6_04 depende del MDE. Aqui se lo compara con la altura
de TERRENO que mide ICESat-2 (ATL08, h_te_best_fit) en segmentos de 100 m:

  1. Solo segmentos con terreno valido, fuera de agua (segment_watermask = 0)
     y, si se pide, solo de haces fuertes (--solo_fuertes).
  2. ATL08 da alturas ELIPSOIDALES; el Copernicus DEM, sobre el geoide
     EGM2008. Se convierte ATL08 a EGM2008 con PROJ (si falta la grilla del
     geoide, el programa se detiene en lugar de comparar mal).
  3. El MDE se promedia en los CINCO pixeles de 20 m que cubre el segmento de
     100 m a lo largo de la traza (casi norte-sur), en lugar de tomar un solo
     pixel; la columna y la fila se calculan con np.floor (astype(int) trunca
     hacia cero y corre un pixel los puntos del borde).
  4. Se informa sesgo (MDE - ICESat-2), desvio y raiz del error cuadratico
     (RMSE), separados por clase:
       --clases control    la cobertura de control del Tp4 (la de antes);
       --clases mapbiomas  MapBiomas 2023 (herbaceas inundables, herbaceas,
                           cultivos, monte, plantaciones...): la cobertura de
                           control solo tiene unos pocos poligonos sorteados de
                           pastura, y MapBiomas cubre todo el sitio;
       --clases ambas      escribe las dos tablas.
     En monte el MDE mide la copa: el sesgo positivo alli es esperable.
  5. --mde copdem (por defecto) o fabdem: FABDEM v1-2 es el Copernicus DEM sin
     arboles ni edificios (subset del practico, sin internet).
  6. Con --excluir_evento se dejan afuera los segmentos tomados entre el
     01/10/2023 y el 30/06/2024: durante la crecida ICESat-2 puede medir agua
     o suelo saturado en lugar del terreno.

ENTRADA  Tp1_Convergencia/05_Resultados/03_Vectores/lidar_B_CONCORDIA.gpkg (capa atl08)
SALIDA   Tp6_Inundaciones/05_Resultados/04_Tablas/B_control_mde_icesat2.csv            (cobertura de control)
         Tp6_Inundaciones/05_Resultados/04_Tablas/B_control_mde_icesat2_mapbiomas.csv  (MapBiomas 2023)
USO      python Tp6_05_control_mde_icesat2.py --pixel 20
         python Tp6_05_control_mde_icesat2.py --pixel 20 --clases ambas --excluir_evento
"""
import argparse
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import ruta_tp                               # noqa: E402
from funciones_comunes import grilla_sitio, copdem, leer_en_grilla, Bitacora  # noqa: E402
from funciones_lidar import alturas_a_egm2008                          # noqa: E402

# ------------------------------------------------------------------ PARAMETROS
SITIO = "B_CONCORDIA"
VENTANA_EVENTO = ("2023-10-01", "2024-06-30")   # segmentos que pueden medir agua o suelo saturado
N_MINIMO = 5                                    # grupos con menos segmentos no se informan
NOMBRES_MAPBIOMAS = {3: "bosque cerrado", 4: "bosque abierto", 6: "bosque inundable", 9: "silvicultura",
                     11: "herbaceas inundables", 12: "herbaceas", 15: "pastura", 19: "cultivos temporarios",
                     24: "areas urbanas", 25: "otras areas no vegetadas", 33: "rios, lagunas y lagos",
                     36: "cultivos perennes"}


def tabla_por_clase(sp, columna, nombres=None):
    """Sesgo, desvio, RMSE y mediana de MDE - ICESat-2 por clase (y para todos)."""
    res = []
    grupos = [("todos", sp)] + [(("clase %d" % k) if not nombres else ("%d %s" % (k, nombres.get(int(k), ""))),
                                 sp[sp[columna] == k]) for k in sorted(sp[columna].dropna().unique()) if k > 0]
    for etiqueta, d in grupos:
        x = d.dif_m.dropna()
        if len(x) < N_MINIMO:
            continue
        res.append({"grupo": etiqueta, "n": len(x), "sesgo_m": round(x.mean(), 2),
                    "desvio_m": round(x.std(), 2), "RMSE_m": round(float(np.sqrt((x ** 2).mean())), 2),
                    "mediana_m": round(x.median(), 2)})
    return pd.DataFrame(res)


def main():
    import geopandas as gpd

    ap = argparse.ArgumentParser()
    ap.add_argument("--pixel", type=int, default=20)
    ap.add_argument("--solo_fuertes", action="store_true")
    ap.add_argument("--clases", choices=["control", "mapbiomas", "ambas"], default="control",
                    help="estratos del control: cobertura de control del Tp4, MapBiomas 2023 o las dos")
    ap.add_argument("--mde", choices=["copdem", "fabdem"], default="copdem",
                    help="modelo que se controla: Copernicus DEM (por defecto) o FABDEM v1-2 del subset del practico")
    ap.add_argument("--excluir_evento", action="store_true",
                    help="deja afuera los segmentos del %s al %s" % VENTANA_EVENTO)
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp6", "05_Resultados", "06_Control_calidad"), "Tp6_05_control_mde")
    gp = ruta_tp("Tp1", "05_Resultados", "03_Vectores", "lidar_%s.gpkg" % SITIO)
    if not os.path.exists(gp):
        sys.exit("Falta %s (Tp1_05 con --descargar)." % gp)
    s = gpd.read_file(gp, layer="atl08")
    s = s[s.terreno_valido.astype(bool)]
    if a.solo_fuertes:
        s = s[s.fuerza_haz == "fuerte"]
    if a.excluir_evento:
        f = pd.to_datetime(s.fecha)
        fuera = ~((f >= VENTANA_EVENTO[0]) & (f <= VENTANA_EVENTO[1]))
        log("Segmentos tomados durante el evento (%s a %s), excluidos: %d" % (VENTANA_EVENTO + (int((~fuera).sum()),)))
        s = s[fuera.values]
    log("Segmentos ATL08 con terreno valido: %d" % len(s))
    s = s.assign(h_te_egm08=alturas_a_egm2008(s.lon.values, s.lat.values, s.h_te_best_fit_elips.values))
    g = grilla_sitio(SITIO, pixel=a.pixel)
    if a.mde == "fabdem":
        mde = leer_en_grilla(ruta_tp("Tp6", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", "B_CONCORDIA_FABDEM_v1-2.tif"), g, "bilinear")
        log("Modelo controlado: FABDEM v1-2 (terreno; Hawker et al., 2022)")
    else:
        mde, _ = copdem(SITIO, g)
        log("Modelo controlado: Copernicus DEM GLO-30 (superficie)")
    suf = "" if a.mde == "copdem" else "_fabdem"
    T = g["transform"]
    sp = s.to_crs(g["crs"])
    col = np.floor((sp.geometry.x - T.c) / T.a).astype(int)
    fil = np.floor((sp.geometry.y - T.f) / T.e).astype(int)
    ok = (col >= 0) & (col < g["width"]) & (fil >= 0) & (fil < g["height"])
    sp = sp[ok]
    # promedio del MDE en los 5 pixeles de 20 m que cubre el segmento de 100 m (traza casi norte-sur)
    filas5 = np.stack([np.clip(fil[ok].values + k, 0, g["height"] - 1) for k in (-2, -1, 0, 1, 2)])
    with np.errstate(all="ignore"):
        sp["mde_m"] = np.nanmean(mde[filas5, col[ok].values[None, :]], axis=0)
    sp["dif_m"] = sp.mde_m - sp.h_te_egm08
    os.makedirs(ruta_tp("Tp6", "05_Resultados", "04_Tablas"), exist_ok=True)
    if a.clases in ("control", "ambas"):
        cc = ruta_tp("Tp4", "02_Subsets_SNAP_QGIS", "%s_cobertura_control_%dm.tif" % (SITIO, a.pixel))
        if os.path.exists(cc):
            c = leer_en_grilla(cc, g, "nearest")
            sp["clase_control"] = c[fil[ok], col[ok]]
        else:
            sp["clase_control"] = np.nan
        t = tabla_por_clase(sp, "clase_control")
        log.titulo("Por clase de la cobertura de control del Tp4")
        log(t.to_string(index=False))
        t.to_csv(ruta_tp("Tp6", "05_Resultados", "04_Tablas", "B_control_mde_icesat2%s.csv" % suf), index=False, encoding="utf-8-sig")
    if a.clases in ("mapbiomas", "ambas"):
        mb = ruta_tp("Tp6", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", "B_CONCORDIA_MapBiomas_cobertura_1985_2025.tif")
        m = leer_en_grilla(mb, g, "nearest", banda=2023 - 1985 + 1)
        sp["clase_mapbiomas"] = m[fil[ok], col[ok]]
        t = tabla_por_clase(sp, "clase_mapbiomas", NOMBRES_MAPBIOMAS)
        log.titulo("Por clase de MapBiomas 2023")
        log(t.to_string(index=False))
        t.to_csv(ruta_tp("Tp6", "05_Resultados", "04_Tablas", "B_control_mde_icesat2_mapbiomas%s.csv" % suf), index=False,
                 encoding="utf-8-sig")
    log("Si el sesgo en suelo desnudo, pastura o herbaceas supera 1 m, la profundidad de Tp6_04 hereda ese sesgo")
    log("y, en cada pixel, un error del orden del RMSE de la clase.")
    log.cerrar("responder las preguntas del Tp6")


if __name__ == "__main__":
    main()
