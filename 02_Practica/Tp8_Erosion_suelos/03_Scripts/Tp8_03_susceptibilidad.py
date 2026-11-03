# -*- coding: utf-8 -*-
"""
Tp8_03_susceptibilidad.py   [SE CORRE]   Tp8, paso 5 de la guia - FUSION DE RASGOS
=========================================================================
Fusion de rasgos: suelo desnudo + textura SAR + pendiente -> susceptibilidad
(guia teorico-practica general, seccion 11.6).

RASGOS (todos en la grilla de 10 m)
  meses_suelo_desnudo   optico (Tp8_01)
  S_CV_HH               textura en banda S (Tp8_02)
  C_CV_VV, C_CV_VH      textura en banda C (Tp8_02), si hubo escena
  pendiente_grados      del FABDEM v1-2 (el Copernicus DEM GLO-30 con el monte y
                        los edificios quitados). La pendiente se calcula en la grilla
                        de 30 m del MDE y DESPUES se lleva a 10 m (bilineal): calcularla
                        sobre el MDE ya interpolado a 10 m crea facetas y pendientes de
                        borde que no existen. A 30 m la pendiente fina de una carcava NO
                        se resuelve: describe la ladera. No se usa el GLO-30 directo
                        porque es un modelo de SUPERFICIE (el borde de un monte da una
                        "pendiente" falsa). Con --mde se puede pasar otro MDE.

ENTRENAMIENTO (lo digitaliza el grupo en QGIS)
  Tp8_Erosion_suelos/04_Tablas_de_trabajo/entrenamiento_F.gpkg, capa "entrenamiento",
  campo "codigo": 1 erosion activa o carcava   2 suelo estable (lote, pastura, monte)

VARIANTES (agregado el 27/10/2026)
  --rasgos      lista de rasgos que entran (por defecto, todos). Con el MISMO Random Forest
                y las MISMAS muestras se comparan, por ejemplo:
                  optico + pendiente:      --rasgos meses_suelo_desnudo pendiente_grados --nombre_variante opt_pend
                  optico + pendiente + SAR: (todos)                                       --nombre_variante opt_pend_sar
                La diferencia entre las dos, validada en el Tp4, es lo que aporto el radar.
  --equilibrar  si (por defecto) o no. Con "si" cada clase entra con el mismo numero de
                pixeles y class_weight="balanced": el modelo supone que la erosion ocupa
                lo mismo que lo estable, la probabilidad de la clase rara queda INFLADA y
                el umbral 0,5 marca de mas.
  --umbral      probabilidad minima para "susceptible" (0,5). Un umbral mas alto (0,8 o 0,9)
                compensa en parte el entrenamiento equilibrado.
  --mascara_urbana  quita de las DOS variantes (la optica y la del Random Forest) las areas
                urbanas (clase 24 de MapBiomas del --anio): techos y calles de tierra estan
                desnudos todo el ano y no son erosion.

RESULTADO
  Probabilidad de la clase 1 = indice de SUSCEPTIBILIDAD (0 a 1), y un mapa
  binario con --umbral para validar en el Tp4 (1 = susceptible, 2 = no).
  La importancia dice cuanto uso el modelo cada rasgo, no cuanto mejora el mapa:
  para eso hay que comparar variantes con y sin el sensor (--rasgos) en el Tp4.

SALIDA (sin --nombre_variante, los nombres de siempre)
  Tp8_Erosion_suelos/05_Resultados/02_Rasters/F_susceptibilidad[_<variante>].tif
  Tp8_Erosion_suelos/05_Resultados/02_Rasters/F_variante_multisensor[_<variante>].tif
  Tp8_Erosion_suelos/05_Resultados/02_Rasters/F_variante_optico.tif    (solo frecuencia >= 6 meses)

USO
    python Tp8_03_susceptibilidad.py --pixel 10
    python Tp8_03_susceptibilidad.py --rasgos meses_suelo_desnudo pendiente_grados --nombre_variante opt_pend
    python Tp8_03_susceptibilidad.py --equilibrar no --nombre_variante sin_equilibrar
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
from funciones_comunes import grilla_sitio, leer_tif, leer_en_grilla, copdem, guardar_tif, Bitacora  # noqa: E402
from funciones_cambio import leer_entrenamiento, fusion_pixel_o_rasgo  # noqa: E402

# ----------------------------------------------------------------- PARAMETROS
SITIO = "F_BOVRIL"
SEMILLA = 2026                 # semilla fija del Random Forest: misma corrida, mismo mapa
PIXEL_MDE = 30                 # la pendiente se calcula en la grilla nativa del MDE
CLASE_URBANA_MAPBIOMAS = 24


def pendiente(mde, pixel):
    """Pendiente en grados por diferencias centradas (np.gradient)."""
    gy, gx = np.gradient(mde, pixel)
    return np.degrees(np.arctan(np.hypot(gx, gy))).astype("float32")


def pendiente_30m_a_grilla(ruta_mde, g):
    """Pendiente calculada a 30 m y llevada despues a la grilla de trabajo (bilineal)."""
    from rasterio.warp import reproject
    from rasterio.enums import Resampling

    g30 = grilla_sitio(SITIO, pixel=PIXEL_MDE)
    p30 = pendiente(leer_en_grilla(ruta_mde, g30, "bilinear"), PIXEL_MDE)
    out = np.full((g["height"], g["width"]), np.nan, dtype="float32")
    reproject(p30, out, src_transform=g30["transform"], src_crs=g30["crs"], dst_transform=g["transform"],
              dst_crs=g["crs"], src_nodata=np.nan, dst_nodata=np.nan, resampling=Resampling.bilinear)
    return out


def main():
    import geopandas as gpd

    ap = argparse.ArgumentParser(description="Susceptibilidad a la erosion por fusion de rasgos (Random Forest).")
    ap.add_argument("--pixel", type=int, default=10)
    ap.add_argument("--umbral", type=float, default=0.5, help="probabilidad minima para 'susceptible'")
    ap.add_argument("--anio", type=int, default=2023)
    ap.add_argument("--mde", default=ruta_tp("Tp8", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", "F_BOVRIL_FABDEM_v1-2.tif"),
                    help="MDE de TERRENO para la pendiente (por defecto el FABDEM recortado al sitio)")
    ap.add_argument("--rasgos", nargs="+", default=None,
                    help="rasgos que entran (por defecto todos): meses_suelo_desnudo pendiente_grados S_CV_HH C_CV_VV C_CV_VH")
    ap.add_argument("--equilibrar", choices=("si", "no"), default="si",
                    help="si: mismo numero de pixeles por clase (infla la clase rara); no: como vienen")
    ap.add_argument("--nombre_variante", default="", help="sufijo de los archivos de salida (para no pisar la corrida base)")
    ap.add_argument("--mascara_urbana", action="store_true",
                    help="quitar de las dos variantes la clase 24 (areas urbanas) de MapBiomas del --anio")
    a = ap.parse_args()
    suf = ("_" + a.nombre_variante) if a.nombre_variante else ""
    log = Bitacora(ruta_tp("Tp8", "05_Resultados", "06_Control_calidad"), "Tp8_03_susceptibilidad" + suf)
    g = grilla_sitio(SITIO, pixel=a.pixel)
    fr, _, t1 = leer_tif(ruta_tp("Tp8", "02_Subsets_SNAP_QGIS", "F_frecuencia_suelo_desnudo_%d_%dm.tif" % (a.anio, a.pixel)))
    tx, _, t2 = leer_tif(ruta_tp("Tp8", "02_Subsets_SNAP_QGIS", "F_textura_S_C_%dm.tif" % a.pixel))
    if os.path.exists(a.mde):
        pend = pendiente_30m_a_grilla(a.mde, g)
        fuente_mde = "FABDEM v1-2 (Hawker et al., 2022, https://doi.org/10.1088/1748-9326/ac4d4f)" \
            if "FABDEM" in os.path.basename(a.mde) else os.path.basename(a.mde)
        log("Pendiente: %s (terreno, sin monte ni edificios), calculada a %d m y llevada a %d m."
            % (os.path.basename(a.mde), PIXEL_MDE, a.pixel))
    else:
        mde, _ = copdem(SITIO, g)
        pend = pendiente(mde, a.pixel)
        fuente_mde = "Copernicus DEM GLO-30 (Planetary Computer)"
        log("AVISO: no esta %s; la pendiente sale del Copernicus DEM GLO-30, que es de SUPERFICIE:" % a.mde)
        log("       los bordes de monte dan pendientes falsas. Declararlo.")
    todos = {"meses_suelo_desnudo": fr["meses_suelo_desnudo"], "pendiente_grados": pend}
    todos.update({k: v for k, v in tx.items() if "_CV_" in k})
    if a.rasgos:
        faltan = [r for r in a.rasgos if r not in todos]
        if faltan:
            raise SystemExit("Estos rasgos no existen: %s. Los disponibles son: %s" % (", ".join(faltan), ", ".join(todos)))
        rasgos = {k: todos[k] for k in a.rasgos}
    else:
        rasgos = todos
    urbano = np.zeros((g["height"], g["width"]), bool)
    if a.mascara_urbana:
        ruta_mb = ruta_tp("Tp8", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", "F_BOVRIL_MapBiomas_cobertura_1985_2025.tif")
        mb = leer_en_grilla(ruta_mb, g, "nearest", banda=a.anio - 1985 + 1)
        urbano = mb == CLASE_URBANA_MAPBIOMAS
        log("Mascara urbana: clase %d de MapBiomas %d, %.1f ha quitadas de las dos variantes."
            % (CLASE_URBANA_MAPBIOMAS, a.anio, urbano.sum() * a.pixel ** 2 / 1e4))
    fuente = " | ".join([t1.get("FUENTE", ""), t2.get("FUENTE", ""), fuente_mde])
    R = lambda n: ruta_tp("Tp8", "05_Resultados", "02_Rasters", n)      # noqa: E731
    opt = np.where(np.isfinite(fr["meses_suelo_desnudo"]),
                   np.where((fr["meses_suelo_desnudo"] >= 6) & ~urbano, 1, 2), np.nan).astype("float32")
    if not a.nombre_variante or a.mascara_urbana:
        guardar_tif(R("F_variante_optico%s.tif" % suf), {"clase": opt}, g, fuente,
                    "Solo optico: suelo desnudo >= 6 meses%s. 1 susceptible, 2 no"
                    % (" (sin areas urbanas)" if a.mascara_urbana else ""))

    ent = ruta_tp("Tp8", "04_Tablas_de_trabajo", "entrenamiento_F.gpkg")
    if not os.path.exists(ent):
        os.makedirs(os.path.dirname(ent), exist_ok=True)
        gpd.GeoDataFrame({"codigo": pd.Series(dtype="int32"), "clase": pd.Series(dtype="str")},
                         geometry=gpd.GeoSeries([], crs=EPSG), crs=EPSG).to_file(ent, layer="entrenamiento", driver="GPKG", engine="pyogrio", geometry_type="Polygon")
        log("Se creo la capa de entrenamiento vacia: %s (1 erosion/carcava, 2 estable)." % ent)
        log.cerrar("digitalizar los poligonos en QGIS (paso 4) y volver a correr")
        return
    y = leer_entrenamiento(ent, g)
    equilibrar = a.equilibrar == "si"
    mapa, prob, info = fusion_pixel_o_rasgo(rasgos, y, semilla=SEMILLA, equilibrar=equilibrar)
    # probabilidad de la clase 1 (no de la ganadora)
    p1 = np.where(mapa == 1, prob, 1 - prob).astype("float32")
    p1[urbano] = np.where(np.isfinite(p1[urbano]), 0.0, np.nan)
    log("Rasgos: %s" % ", ".join(rasgos))
    n1, n2 = int((y == 1).sum()), int((y == 2).sum())
    if equilibrar:
        log("Entrenamiento EQUILIBRADO (%d pixeles de erosion y %d estables; mismo peso por clase):" % (n1, n2))
        log("   la probabilidad de la clase rara queda INFLADA y el umbral %.2f marca de mas." % a.umbral)
    else:
        log("Entrenamiento SIN equilibrar: %d pixeles de erosion y %d estables, como vienen de los poligonos." % (n1, n2))
        log("   Ojo: los poligonos tampoco estan en la proporcion del paisaje (la erosion ocupa mucho menos).")
    log("Exactitud fuera de bolsa (OPTIMISTA): %.3f" % info["exactitud_fuera_de_bolsa_OPTIMISTA"])
    for k, v in sorted(info["importancia"].items(), key=lambda kv: -kv[1]):
        log("   importancia %-22s %.3f" % (k, v))
    log("La importancia dice cuanto uso el modelo cada rasgo, no cuanto mejora el mapa.")
    guardar_tif(R("F_susceptibilidad%s.tif" % suf), {"susceptibilidad": p1}, g, fuente,
                "Probabilidad de erosion activa (Random Forest de rasgos: %s; equilibrar=%s)" % (", ".join(rasgos), a.equilibrar))
    bin_ = np.where(np.isfinite(p1), np.where(p1 >= a.umbral, 1, 2), np.nan).astype("float32")
    guardar_tif(R("F_variante_multisensor%s.tif" % suf), {"clase": bin_}, g, fuente,
                "Random Forest (%s): susceptibilidad >= %.2f. 1 susceptible, 2 no" % (", ".join(rasgos), a.umbral))
    dominio = np.isfinite(p1).sum() * a.pixel ** 2 / 1e4
    log("Superficie susceptible (p >= %.2f): %.1f ha de %.1f ha con todos los rasgos; solo optico (>= 6 meses): %.1f ha"
        % (a.umbral, np.nansum(bin_ == 1) * a.pixel ** 2 / 1e4, dominio, np.nansum(opt == 1) * a.pixel ** 2 / 1e4))
    for u in (0.5, 0.8, 0.9):
        log("   con umbral %.1f: %.1f ha" % (u, np.nansum(p1 >= u) * a.pixel ** 2 / 1e4))
    log.cerrar("Tp4_02 y Tp4_03 con F_variante_optico y F_variante_multisensor%s; responder las preguntas del Tp8" % suf)


if __name__ == "__main__":
    main()
