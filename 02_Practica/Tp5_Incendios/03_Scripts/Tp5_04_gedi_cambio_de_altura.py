# -*- coding: utf-8 -*-
"""
Tp5_04_gedi_cambio_de_altura.py   [SE CORRE]   Tp5, paso 6 de la guia - evidencia estructural
=====================================================================================
"Usar el cambio de altura GEDI (delta rh98) como evidencia estructural
independiente" (presentacion 01, diapositiva 28, paso 4).

El problema: GEDI no repite la misma huella. Dos pasadas casi nunca caen en
el mismo lugar. Por eso no se resta huella contra huella: se arma una grilla
de celdas (100 m por defecto), y en cada celda que tenga huellas VALIDAS
antes Y despues del evento se compara la mediana de rh98.

  delta_rh98 = mediana(rh98 despues) - mediana(rh98 antes)    [m]

Despues se cruza con la variante multisensor (Tp5_03): si el mapa dice
"quemado" y la estructura no cambio, o al reves, hay algo que revisar. Es
evidencia INDEPENDIENTE porque no entro en ningun modelo.

Ventanas de tiempo (todas se escriben en la bitácora)
  "antes"   = huellas desde --antes_desde (inclusive) hasta --antes_hasta (exclusive)
  "después" = huellas desde --despues_desde hasta --despues_hasta (las dos inclusive)
  Por defecto, la MISMA estación antes y después del evento: primavera y verano
  2019-2020 (01/10/2019 a 31/03/2020) frente a primavera y verano 2020-2021
  (01/10/2020 a 31/03/2021). Una ventana «después» sin fin mezclaría el rebrote de
  varios años y las quemas de 2022 (corregido el 27/10/2026).

Advertencias que se escriben en la bitácora
  - Un rh98 menor de 3 m sobre terreno llano NO es la altura del pajonal: es el
    piso del instrumento (el ancho del pulso sobre el suelo). Allí el delta
    rh98 no tiene significado estructural.
  - GEDI no adquirió entre el 17/03/2023 y el 26/04/2024; para 2020 hay datos.

ENTRADA  Tp1_Convergencia/05_Resultados/03_Vectores/lidar_A1_DELTA_QUEMAS.gpkg (capa gedi_l2a)
SALIDA   Tp5_Incendios/05_Resultados/04_Tablas/A1_delta_rh98_por_celda.csv
         Tp5_Incendios/05_Resultados/04_Tablas/A1_delta_rh98_por_clase.csv

USO
    python Tp5_04_gedi_cambio_de_altura.py --antes_desde 2019-10-01 --antes_hasta 2020-04-01 ^
        --despues_desde 2020-10-01 --despues_hasta 2021-03-31 --celda 100
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
from funciones_comunes import Bitacora                                # noqa: E402

# ---------------------------------------------------------------- PARÁMETROS
SITIO = "A1_DELTA_QUEMAS"
ANTES_DESDE = "2019-10-01"      # primavera y verano anteriores al evento
ANTES_HASTA = "2020-04-01"      # exclusive
DESPUES_DESDE = "2020-10-01"    # primavera y verano posteriores
DESPUES_HASTA = "2021-03-31"    # inclusive
CELDA_M = 100.0                 # lado de la celda, en metros
MIN_HUELLAS = 2                 # huellas válidas mínimas antes y después en cada celda
PISO_RH98_M = 3.0               # por debajo, el rh98 es el piso del instrumento, no la altura de la vegetación


def main():
    import geopandas as gpd
    import rasterio

    ap = argparse.ArgumentParser(description="Cambio de altura GEDI (delta rh98) por celda, antes y después de las quemas.")
    ap.add_argument("--antes_desde", default=ANTES_DESDE, help="primera fecha de 'antes' (AAAA-MM-DD)")
    ap.add_argument("--antes_hasta", default=ANTES_HASTA, help="fin de 'antes', sin incluir")
    ap.add_argument("--despues_desde", default=DESPUES_DESDE, help="primera fecha de 'después'")
    ap.add_argument("--despues_hasta", default=DESPUES_HASTA, help="última fecha de 'después', incluida")
    ap.add_argument("--celda", type=float, default=CELDA_M)
    ap.add_argument("--min_huellas", type=int, default=MIN_HUELLAS)
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp5", "05_Resultados", "06_Control_calidad"), "Tp5_04_gedi")
    gp = ruta_tp("Tp1", "05_Resultados", "03_Vectores", "lidar_%s.gpkg" % SITIO)
    if not os.path.exists(gp):
        sys.exit("Falta %s: hay que correr antes Tp1_05_buscar_lidar.py --sitio %s --descargar "
                 "(o pedir el archivo al docente)." % (gp, SITIO))
    var = ruta_tp("Tp5", "05_Resultados", "02_Rasters", "A1_variante_multisensor.tif")
    if not os.path.exists(var):
        sys.exit("Falta %s: correr antes Tp5_03_fusion.py con la capa de entrenamiento digitalizada." % var)
    log("GEDI no adquirió entre el 17/03/2023 y el 26/04/2024; para el evento de 2020 hay datos antes y después.")
    log("Ventana 'antes':   %s a %s (sin incluir el último día)" % (a.antes_desde, a.antes_hasta))
    log("Ventana 'después': %s a %s (incluido)" % (a.despues_desde, a.despues_hasta))
    with rasterio.open(var) as src:
        crs = src.crs
    h = gpd.read_file(gp, layer="gedi_l2a").to_crs(crs)
    h = h[h.valido.astype(bool)].copy()
    f = h.fecha.astype(str)
    h["periodo"] = np.select(
        [(f >= a.antes_desde) & (f < a.antes_hasta),
         (f >= a.antes_hasta) & (f < a.despues_desde),
         (f >= a.despues_desde) & (f <= a.despues_hasta)],
        ["antes", "durante", "despues"], default="fuera")
    log("Huellas GEDI válidas: %d (antes %d, durante %d, después %d, fuera de las ventanas %d)"
        % (len(h), (h.periodo == "antes").sum(), (h.periodo == "durante").sum(), (h.periodo == "despues").sum(),
           (h.periodo == "fuera").sum()))
    h = h[h.periodo.isin(["antes", "despues"])].copy()
    h["cx"] = np.floor(h.geometry.x / a.celda).astype(int)
    h["cy"] = np.floor(h.geometry.y / a.celda).astype(int)
    agg = h.groupby(["cx", "cy", "periodo"]).rh98.agg(["median", "count"]).unstack("periodo")
    agg.columns = ["%s_%s" % (x, y) for x, y in agg.columns]
    need = ["median_antes", "median_despues", "count_antes", "count_despues"]
    if not all(c in agg.columns for c in need):
        log("No hay celdas con huellas antes y después. Pruebe una celda más grande (--celda 200) o ventanas "
            "más largas, y dígalo en el informe.")
        log.cerrar()
        return
    agg = agg.dropna(subset=["median_antes", "median_despues"])
    agg = agg[(agg.count_antes >= a.min_huellas) & (agg.count_despues >= a.min_huellas)].reset_index()
    agg["delta_rh98_m"] = agg.median_despues - agg.median_antes
    agg["x"] = (agg.cx + 0.5) * a.celda
    agg["y"] = (agg.cy + 0.5) * a.celda
    # clase de la CELDA: la mayoritaria entre los pixeles del mapa que caen en ella (no el pixel central,
    # uno solo entre 25 a 20 m, que puede no representar a las huellas)
    from rasterio.windows import from_bounds
    vals = []
    with rasterio.open(var) as src:
        banda = src.read(1)
        for cx, cy in zip(agg.cx, agg.cy):
            w = from_bounds(cx * a.celda, cy * a.celda, (cx + 1) * a.celda, (cy + 1) * a.celda, src.transform)
            r0, c0 = max(int(round(w.row_off)), 0), max(int(round(w.col_off)), 0)
            v = banda[r0:r0 + max(int(round(w.height)), 1), c0:c0 + max(int(round(w.width)), 1)].astype("float64")
            if src.nodata is not None:
                v = v[v != src.nodata]
            v = v[np.isfinite(v)]
            if v.size:
                cl, n = np.unique(v, return_counts=True)
                vals.append(float(cl[np.argmax(n)]))
            else:
                vals.append(np.nan)
    agg["clase_mapa"] = np.array(vals, dtype="float64")
    log("Celdas de %.0f m con %d huellas o más antes y después: %d" % (a.celda, a.min_huellas, len(agg)))
    por = agg.groupby("clase_mapa").delta_rh98_m.describe()[["count", "mean", "50%", "std"]]
    por.index = por.index.map({1.0: "quemado (mapa)", 2.0: "no quemado (mapa)"})
    log(por.round(2).to_string())
    bajo = (agg.median_antes < PISO_RH98_M).mean()
    log("%.0f %% de las celdas tiene rh98 previo < %.0f m: ahí GEDI no mide la altura del pajonal, sino el piso del"
        % (100 * bajo, PISO_RH98_M))
    log("instrumento sobre terreno llano; el delta rh98 de esas celdas no tiene significado estructural.")
    alb = agg.median_antes >= PISO_RH98_M
    log("Celdas con rh98 previo >= %.0f m (estructura leñosa): %d; de ellas, %d en lo quemado del mapa."
        % (PISO_RH98_M, int(alb.sum()), int((alb & (agg.clase_mapa == 1)).sum())))
    out = ruta_tp("Tp5", "05_Resultados", "04_Tablas", "A1_delta_rh98_por_celda.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    agg.to_csv(out, index=False, encoding="utf-8-sig")
    por.to_csv(out.replace("por_celda", "por_clase"), encoding="utf-8-sig")
    log("Tabla:", out)
    log.cerrar("python Tp5_05_dominio_comun.py (si no se corrió) y responder las preguntas del Tp5")


if __name__ == "__main__":
    main()
