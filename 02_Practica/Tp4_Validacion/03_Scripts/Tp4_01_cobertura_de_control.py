# -*- coding: utf-8 -*-
"""
Tp4_01_cobertura_de_control.py   [SE CORRE]   Tp4, paso 2 y 4 de la guia
============================================================
El curso NO tiene un mapa de cobertura de control para Entre Rios: se GENERA.
Este programa prepara las piezas y las une; la interpretacion la hace el grupo.

QUE ES (Y QUE NO ES) UN MAPA DE COBERTURA DE CONTROL
  Es un mapa de clases ESTABLES y bien conocidas del sitio (agua permanente,
  monte nativo, ciudad, cultivo, pajonal...) armado con fuentes que NO son
  las imagenes que despues se evaluan. Sirve para tres cosas:
    1. estratificar el muestreo de validacion (Tp4_02);
    2. definir las ZONAS DE CONTROL que piden los practicos: zona estable
       (Tp2), agua permanente que no es inundacion (Tp6), zonas no quemadas
       (Tp5), cultivos que no son deforestacion (Tp9);
    3. comparar un mapa del curso con otro hecho de otra manera.
  NO es la verdad de campo. La exactitud se calcula con la muestra
  etiquetada al azar (Tp4_02 y Tp4_03), nunca contra este mapa.

LAS FUENTES, EN ORDEN DE PRIORIDAD (la primera que tiene dato manda)
  a) Poligonos digitalizados por el grupo sobre imagenes de muy alta
     resolucion (Google o ESRI en QGIS) y su conocimiento del lugar:
       04_Tablas_de_trabajo/control_digitalizado_<SITIO>.gpkg, capa
       "control", campo entero "codigo" (tabla de clases abajo).
  b) Agua permanente: JRC Global Surface Water, ocurrencia >= 90 %
     (1984-2021, Landsat). Pekel et al. (2016).
  c) Monte: bosque de MapBiomas Argentina 2023 (Landsat, 30 m) RECORTADO con la
     mascara de copas hecha sobre la imagen de alta resolucion CBERS-4A de 2 m
     (archivo <SITIO>_copa_CBERS4A_fraccion_20m.tif en 02_Subsets_SNAP_QGIS).
     Un pixel de 20 m queda como monte solo si MapBiomas dice bosque Y la
     imagen de 2 m muestra copas en al menos la mitad del pixel (--copa_min).
     MapBiomas aporta la distincion monte nativo / plantacion (sus plantaciones
     son otra clase); la imagen de 2 m aporta el borde y saca el pasto, las casas
     y los claros que el pixel de 30 m mete adentro. Donde no hay imagen de 2 m
     (o hay nubes) no se pone monte: el control no necesita cubrir todo.
     Con --monte_solo_mapbiomas se rehace la version anterior, sin recorte, para
     comparar. Es un producto de terceros: se acepta como clase "monte" solo si
     el grupo no digitalizo otra cosa.

CLASES (codigo: nombre)
  1 agua_permanente   2 humedal_pajonal   3 monte_nativo   4 plantacion_forestal
  5 cultivo_pastura   6 suelo_desnudo     7 urbano         8 otra

SALIDA
  Tp4_Validacion/02_Subsets_SNAP_QGIS/<SITIO>_cobertura_control_<pixel>m.tif   (0 = sin clase)
  Tp4_Validacion/05_Resultados/04_Tablas/<SITIO>_cobertura_control_resumen.csv (superficie y fuente por clase)

USO
    python Tp4_01_cobertura_de_control.py --sitio B_CONCORDIA --pixel 20
"""
import argparse
import glob
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import SITIOS, EPSG, MAPBIOMAS_BOSQUES, ruta_tp  # noqa: E402
from funciones_comunes import (grilla_sitio, jrc_ocurrencia, leer_en_grilla,  # noqa: E402
                               guardar_tif, Bitacora)

CLASES = {1: "agua_permanente", 2: "humedal_pajonal", 3: "monte_nativo", 4: "plantacion_forestal",
          5: "cultivo_pastura", 6: "suelo_desnudo", 7: "urbano", 8: "otra"}


def plantilla(ruta, log):
    import geopandas as gpd

    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    gpd.GeoDataFrame({"codigo": pd.Series(dtype="int32"), "clase": pd.Series(dtype="str"),
                      "fuente_interpretacion": pd.Series(dtype="str"),
                      "fecha_imagen": pd.Series(dtype="str"), "interprete": pd.Series(dtype="str")},
                     geometry=gpd.GeoSeries([], crs=EPSG), crs=EPSG).to_file(ruta, layer="control", driver="GPKG", engine="pyogrio", geometry_type="Polygon")
    log("Se creo la capa para digitalizar: %s" % ruta)
    log("Campos: codigo (1 a 8), clase, fuente_interpretacion (p. ej. 'ESRI World Imagery'),")
    log("        fecha_imagen (la que muestra la imagen), interprete (quien digitalizo).")


def main():
    import geopandas as gpd
    from rasterio import features

    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", required=True, choices=list(SITIOS.keys()))
    ap.add_argument("--pixel", type=float, default=20.0)
    ap.add_argument("--sin_jrc", action="store_true", help="no consultar JRC (sin internet)")
    ap.add_argument("--copa_min", type=float, default=0.5,
                    help="fraccion minima de copa (imagen de 2 m) para aceptar el monte de MapBiomas")
    ap.add_argument("--monte_solo_mapbiomas", action="store_true",
                    help="version anterior: monte de MapBiomas sin recortar con la imagen de 2 m")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp4", "05_Resultados", "06_Control_calidad"), "Tp4_01_%s" % a.sitio)
    g = grilla_sitio(a.sitio, pixel=a.pixel)
    mapa = np.zeros((g["height"], g["width"]), dtype="int32")
    fuente = np.zeros_like(mapa)          # 1 digitalizado, 2 JRC, 3 MapBiomas

    # a) digitalizado por el grupo
    dig = ruta_tp("Tp4", "04_Tablas_de_trabajo", "control_digitalizado_%s.gpkg" % a.sitio)
    if not os.path.exists(dig):
        plantilla(dig, log)
    else:
        pol = gpd.read_file(dig, layer="control").to_crs(g["crs"])
        pol = pol[pol["codigo"].isin(list(CLASES))]
        if len(pol):
            r = features.rasterize(((geom, int(c)) for geom, c in zip(pol.geometry, pol["codigo"])),
                                   out_shape=mapa.shape, transform=g["transform"], fill=0, dtype="int32")
            mapa = np.where(r > 0, r, mapa)
            fuente = np.where(r > 0, 1, fuente)
            log("a) Digitalizado: %d poligonos, %d pixeles." % (len(pol), (r > 0).sum()))
        else:
            log("a) La capa digitalizada esta vacia: todavia no hay interpretacion propia.")

    # b) agua permanente (JRC)
    if not a.sin_jrc:
        try:
            occ, _ = jrc_ocurrencia(a.sitio, g)
            agua = (occ >= 90) & (mapa == 0)
            mapa[agua] = 1
            fuente[agua] = 2
            log("b) JRC GSW ocurrencia >= 90 %%: %d pixeles de agua permanente agregados." % agua.sum())
        except Exception as e:                       # noqa: BLE001
            log("b) No se pudo leer JRC GSW (%s). Se sigue sin el." % str(e)[:100])

    # c) MapBiomas bosque (archivo del curso), recortado con la mascara de copas de 2 m
    copa = None
    ruta_copa = ruta_tp("Tp4", "02_Subsets_SNAP_QGIS", "%s_copa_CBERS4A_fraccion_20m.tif" % a.sitio)
    if not a.monte_solo_mapbiomas:
        if os.path.exists(ruta_copa):
            copa = np.nan_to_num(leer_en_grilla(ruta_copa, g, "average"), nan=0.0)
            log("c) Mascara de copas de alta resolucion: %s (monte solo si copa >= %.2f)."
                % (os.path.basename(ruta_copa), a.copa_min))
        else:
            log("c) No esta %s: el monte de MapBiomas entra sin recortar (pixel de 30 m)."
                % os.path.basename(ruta_copa))
    else:
        log("c) --monte_solo_mapbiomas: monte de MapBiomas sin recortar (version anterior).")
    tifs = sorted(glob.glob(os.path.join(MAPBIOMAS_BOSQUES, "Bosques_MapBiomas_2023_*.tif")))
    for t in tifs:
        try:
            b = leer_en_grilla(t, g, "mode", tipo="int32")
        except Exception:                            # noqa: BLE001
            continue
        monte = (b > 0) & (mapa == 0)
        if copa is not None:
            n0 = int(monte.sum())
            monte &= copa >= a.copa_min
            log("c) MapBiomas %s: %d pixeles de bosque; %d quedan con copa >= %.2f en la imagen de 2 m."
                % (os.path.basename(t), n0, monte.sum(), a.copa_min))
        if monte.any():
            mapa[monte] = 3
            fuente[monte] = 3
            log("c) MapBiomas %s: %d pixeles de monte agregados (producto de terceros)."
                % (os.path.basename(t), monte.sum()))

    out = ruta_tp("Tp4", "02_Subsets_SNAP_QGIS", "%s_cobertura_control_%dm.tif" % (a.sitio, a.pixel))
    guardar_tif(out, {"clase_control": mapa.astype("float32"), "fuente_control": fuente.astype("float32")}, g,
                "Digitalizacion del grupo sobre imagenes de muy alta resolucion; JRC Global Surface Water "
                "(Pekel et al., 2016), https://global-surface-water.appspot.com; MapBiomas Argentina "
                "coleccion de bosques 2023, https://argentina.mapbiomas.org"
                + ("; recortado con copas de CBERS-4A 2 m (INPE, CC BY 4.0)" if copa is not None else ""),
                "Mapa de cobertura de control (clases estables), prioridad: digitalizado > JRC > MapBiomas")
    filas = []
    for c, n in CLASES.items():
        px = int((mapa == c).sum())
        if px:
            fu = np.bincount(fuente[mapa == c], minlength=4)
            filas.append({"codigo": c, "clase": n, "pixeles": px,
                          "superficie_ha": round(px * a.pixel ** 2 / 1e4, 1),
                          "de_digitalizacion": int(fu[1]), "de_JRC": int(fu[2]), "de_MapBiomas": int(fu[3])})
    t = pd.DataFrame(filas)
    tab = ruta_tp("Tp4", "05_Resultados", "04_Tablas", "%s_cobertura_control_resumen.csv" % a.sitio)
    os.makedirs(os.path.dirname(tab), exist_ok=True)
    t.to_csv(tab, index=False, encoding="utf-8-sig")
    log.titulo("Resumen")
    log(t.to_string(index=False) if len(t) else "Sin clases todavia.")
    log("Sin clase: %.1f %% del sitio (es normal: el control no necesita cubrir todo)."
        % (100.0 * (mapa == 0).mean()))
    log("Mapa:", out)
    log.cerrar("python Tp4_02_muestreo_estratificado.py --mapa <mapa a evaluar>.tif")


if __name__ == "__main__":
    main()
