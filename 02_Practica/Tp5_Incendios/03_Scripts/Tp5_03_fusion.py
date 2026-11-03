# -*- coding: utf-8 -*-
"""
Tp5_03_fusion.py   [SE CORRE]   Tp5, paso 4 de la guia - FUSION y variantes a validar
=============================================================================
Produce las CUATRO variantes que se comparan en el Tp4 (diapositiva 23) y,
con la ultima, el mapa de SEVERIDAD:

  V1  Optico solo        umbral de dNBR (de Tp5_02)               -> un sensor
  V2  SAR solo (C)       umbral de dVH (de Tp5_02)                -> un sensor
  V3  SAR multibanda     FUSION DE DECISION C + L, regla escrita   -> --regla mayoria|union|interseccion
  V4  Multisensor        FUSIÓN DE RASGOS: Random Forest con dVH_C, dVV_C,
                         dHV_L_ALOS2, dHV_SAOCOM, dNBR y RdNBR     -> severidad en 4 clases
                         (con --sin_rdnbr, sin el RdNBR)

Por qué V3 es de decisión y V4 de rasgo: la V3 combina decisiones porque cada
radar se umbraliza en su propio rango (dB distintos en C y en L, con aumentos
generales distintos entre fechas) y la pregunta es binaria; la V4 combina
rasgos porque la severidad es graduada y el modelo tiene que ver los valores,
no sólo el sí o no de cada sensor (presentación 01, diapositiva 12). En las
dos las ventanas de fecha difieren (Sentinel-1 16/07-26/09; SAOCOM 21/07-25/10;
Sentinel-2 15/07-13/10; ALOS-2, mosaicos anuales) y eso se declara: la fusión
de rasgo lo tolera porque entran rasgos derivados (cambios), no bandas.

DOMINIO DE LA V4: sólo clasifica donde hay dato en TODAS las capas. La
bitácora escribe cuántas hectáreas pierde cada capa (franja de SAOCOM, nubes
del óptico y píxeles sin RdNBR, |NBR previo| < 0,05).

ENTRENAMIENTO DE V4 (lo digitaliza el grupo; el programa crea la capa vacia)
  Tp5_Incendios/04_Tablas_de_trabajo/entrenamiento_A1.gpkg, capa "entrenamiento",
  campo entero "codigo":  1 quemado severidad alta   2 quemado severidad baja
                          3 no quemado               4 agua
  Se digitaliza sobre el Sentinel-2 posterior y el RGB radar, LEJOS de los
  puntos de validacion del Tp4 (que todavia no existen: por eso este paso va
  antes del Tp4_02). Validar con los datos de entrenamiento infla la exactitud.

CODIGOS DE LAS VARIANTES (para Tp4_02): 1 = quemado, 2 = no quemado.

SALIDA
  Tp5_Incendios/05_Resultados/02_Rasters/A1_variante_{optico,C,CL,multisensor}.tif
  Tp5_Incendios/05_Resultados/02_Rasters/A1_severidad_multisensor.tif (+ probabilidad)
  Tp5_Incendios/05_Resultados/04_Tablas/A1_importancia_variables.csv

USO
    python Tp5_03_fusion.py --pixel 20 --regla mayoria
    python Tp5_03_fusion.py --pixel 20 --regla mayoria --sin_rdnbr     (variante de control, ver NOTAS)
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

from configuracion_comun import EPSG, ruta_tp                         # noqa: E402
from funciones_comunes import leer_tif, grilla_de_tif, guardar_tif, Bitacora  # noqa: E402
from funciones_cambio import (fusion_decision, fusion_pixel_o_rasgo,  # noqa: E402
                              leer_entrenamiento, figura_mapa)

# ---------------------------------------------------------------- PARÁMETROS
SITIO = "A1_DELTA_QUEMAS"
SEMILLA = 2026                   # semilla del Random Forest (resultado reproducible)
RASGOS = ["dVH_C_dB", "dVV_C_dB", "dHV_L_ALOS2_dB", "dHV_SAOCOM_dB", "dNBR", "RdNBR"]
SEVERIDAD = {1: "quemado alta", 2: "quemado baja", 3: "no quemado", 4: "agua"}


def a_binaria(m):
    """1/0/NaN -> 1 quemado, 2 no quemado, NaN sin dato (codigos del Tp4)."""
    return np.where(np.isfinite(m), np.where(m == 1, 1, 2), np.nan).astype("float32")


def plantilla(ruta, log):
    import geopandas as gpd

    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    gpd.GeoDataFrame({"codigo": pd.Series(dtype="int32"), "clase": pd.Series(dtype="str")},
                     geometry=gpd.GeoSeries([], crs=EPSG), crs=EPSG).to_file(ruta, layer="entrenamiento", driver="GPKG", engine="pyogrio", geometry_type="Polygon")
    log("Se creó la capa de entrenamiento vacía: %s" % ruta)
    log("Códigos: " + ", ".join("%d %s" % kv for kv in SEVERIDAD.items()))


def main():
    ap = argparse.ArgumentParser(description="Variantes V1 a V4 del perímetro y severidad (fusión de decisión y de rasgo).")
    ap.add_argument("--pixel", type=int, default=20)
    ap.add_argument("--regla", default="mayoria", choices=["mayoria", "union", "interseccion"])
    ap.add_argument("--sin_rdnbr", action="store_true",
                    help="V4 sin RdNBR: los archivos de la V4 llevan el sufijo _sin_rdnbr y no pisan los otros")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp5", "05_Resultados", "06_Control_calidad"),
                   "Tp5_03_fusion" + ("_sin_rdnbr" if a.sin_rdnbr else ""))
    ind_ruta = ruta_tp("Tp5", "02_Subsets_SNAP_QGIS", "%s_indicadores_%dm.tif" % (SITIO, a.pixel))
    ind, _, tags = leer_tif(ind_ruta)
    g = grilla_de_tif(ind_ruta)
    sens, _, _ = leer_tif(ruta_tp("Tp5", "05_Resultados", "02_Rasters", "A1_quema_por_sensor_%dm.tif" % a.pixel))
    fuente = tags.get("FUENTE", "")
    R = lambda n: ruta_tp("Tp5", "05_Resultados", "02_Rasters", n)      # noqa: E731

    if "Optico_dNBR" in sens:
        guardar_tif(R("A1_variante_optico.tif"), {"clase": a_binaria(sens["Optico_dNBR"])}, g, fuente,
                    "V1 optico solo: umbral de dNBR. 1 quemado, 2 no quemado")
        log("V1 óptico solo         -> A1_variante_optico.tif")
    if "C_Sentinel1_dVH" in sens:
        guardar_tif(R("A1_variante_C.tif"), {"clase": a_binaria(sens["C_Sentinel1_dVH"])}, g, fuente,
                    "V2 SAR solo banda C: umbral de dVH. 1 quemado, 2 no quemado")
        log("V2 SAR solo (C)        -> A1_variante_C.tif")
    radar = {k: v for k, v in sens.items() if k.startswith(("C_", "L_"))}
    if len(radar) >= 2:
        fus, votos = fusion_decision(radar, a.regla)
        guardar_tif(R("A1_variante_CL.tif"), {"clase": a_binaria(fus), "votos": votos.astype("float32")}, g,
                    fuente, "V3 SAR multibanda: fusion de DECISION (%s) de %s" % (a.regla, ", ".join(radar)))
        log("V3 SAR multibanda      -> A1_variante_CL.tif  (fusión de decisión, regla %s, %s)"
            % (a.regla, " + ".join(radar)))

    ent = ruta_tp("Tp5", "04_Tablas_de_trabajo", "entrenamiento_A1.gpkg")
    if not os.path.exists(ent):
        plantilla(ent, log)
        log("V4 queda pendiente hasta que se digitalice el entrenamiento.")
        log.cerrar("digitalizar el entrenamiento y volver a correr este paso")
        return
    y = leer_entrenamiento(ent, g)
    if (y > 0).sum() == 0:
        log("La capa de entrenamiento está vacía (no se guardaron los polígonos). V4 queda pendiente.")
        log.cerrar()
        return
    rasgos = [k for k in RASGOS if not (a.sin_rdnbr and k == "RdNBR")]
    capas = {k: ind[k] for k in rasgos if k in ind}
    suf = "_sin_rdnbr" if a.sin_rdnbr else ""
    log.titulo("V4 multisensor: FUSIÓN DE RASGOS (Random Forest) con %s" % ", ".join(capas))
    # dominio: cuánto pierde cada capa, en el orden en que se agregan
    ha = a.pixel ** 2 / 1e4
    resto = np.ones(next(iter(capas.values())).shape, bool)
    log("Superficie del sitio: %.0f ha. Hectáreas que quedan después de exigir cada capa:" % (resto.sum() * ha))
    for k in sorted(capas, key=lambda k: -np.isfinite(capas[k]).sum()):
        nuevo = resto & np.isfinite(capas[k])
        log("   %-16s quedan %8.0f ha  (pierde %6.0f ha)" % (k, nuevo.sum() * ha, (resto & ~nuevo).sum() * ha))
        resto = nuevo
    log("La V4 clasifica %.0f ha (%.0f %% del sitio). El recorte no es al azar: sigue la franja de SAOCOM,"
        % (resto.sum() * ha, 100 * resto.mean()))
    log("las nubes del óptico y, si entra el RdNBR, los píxeles con |NBR previo| < 0,05 (pajonal ralo, bajos).")
    mapa, prob, info = fusion_pixel_o_rasgo(capas, y, semilla=SEMILLA)
    log("Píxeles de entrenamiento: %d" % info["pixeles_entrenamiento"])
    log("Exactitud fuera de bolsa: %.3f  <- OPTIMISTA (píxeles vecinos de los mismos polígonos)."
        % info["exactitud_fuera_de_bolsa_OPTIMISTA"])
    log("La exactitud que vale es la del Tp4.")
    for k, v in sorted(info["importancia"].items(), key=lambda kv: -kv[1]):
        log("   importancia %-16s %.3f" % (k, v))
    guardar_tif(R("A1_severidad_multisensor%s.tif" % suf), {"severidad": mapa, "probabilidad": prob}, g, fuente,
                "V4 multisensor: Random Forest de rasgos (%s). Clases: %s"
                % (", ".join(capas), "; ".join("%d %s" % kv for kv in SEVERIDAD.items())))
    binaria = np.where(np.isfinite(mapa), np.where(np.isin(mapa, [1, 2]), 1, 2), np.nan).astype("float32")
    guardar_tif(R("A1_variante_multisensor%s.tif" % suf), {"clase": binaria}, g, fuente,
                "V4 multisensor colapsado a 1 quemado (alta + baja), 2 no quemado (incluye agua)")
    pd.DataFrame([{"variable": k, "importancia": v} for k, v in info["importancia"].items()]).to_csv(
        ruta_tp("Tp5", "05_Resultados", "04_Tablas", "A1_importancia_variables%s.csv" % suf), index=False,
        encoding="utf-8-sig")
    figura_mapa(mapa, ruta_tp("Tp5", "05_Resultados", "05_Graficos", "A1_severidad_multisensor%s.png" % suf),
                "Severidad (Random Forest de rasgos)", fuente[:300], etiquetas=SEVERIDAD, cmap="inferno")
    for c, n in SEVERIDAD.items():
        log("   %-14s %8.1f ha" % (n, np.nansum(mapa == c) * a.pixel ** 2 / 1e4))
    log.cerrar("Tp4_02 y Tp4_03 para cada variante; después Tp4_04 --tp Tp5 --clase quemado")


if __name__ == "__main__":
    main()
