# -*- coding: utf-8 -*-
"""
Tp9_03_fusion_perdida_degradacion.py   [SE CORRE]   Tp9, paso 4 de la guia - FUSION DE RASGOS
=====================================================================================
Fusion de rasgos: delta HV, delta VH, NDVI y delta rh98 -> perdida,
degradacion o estable (guia teorico-practica, seccion 12.6, paso 4).

RASGOS (calculados de la pila de Tp9_01; los que falten, no entran)
  dHV_L    10 log10(L_2026 / L_2021)  HV NISAR frente a HV ALOS-2 (si no hay HV de
           NISAR se usa HH y el rasgo se llama dHH_L)
  dHH_L_hist 10 log10(L_2021 / L_2011) HH ALOS-2 frente a HH ALOS-1 (cambio historico)
  dVH_C    10 log10(VH_2026 / VH_2021)
  dNDVI    NDVI_2026 - NDVI_2021
  NDVI_actual, HV_L_actual_dB         nivel actual (distingue no-bosque de bosque perdido)

delta_rh98 (GEDI, Tp9_02): por defecto NO entra al modelo, porque solo existe
en las celdas con huellas y el mapa quedaria agujereado; se usa como CONTROL
INDEPENDIENTE (tabla de delta_rh98 por clase del mapa). Con --rh98_como_rasgo
entra como rasgo y el mapa se limita a esas celdas (se declara).

CLASES DE ENTRENAMIENTO (las digitaliza el grupo)
  1 perdida (desmonte de un LOTE: hoy suelo o cultivo donde habia monte)
  2 degradacion (sigue habiendo cobertura arborea pero rala o raleada; incluye
    las APERTURAS LINEALES nuevas: picadas, caminos y cortafuegos)
  3 monte estable    4 no bosque estable (cultivo, pastura, ciudad)
  Tp9_Deforestacion/04_Tablas_de_trabajo/entrenamiento_C.gpkg, capa "entrenamiento", campo "codigo"

VARIANTES PARA EL Tp4 (codigos: 1 = perdida o degradacion, 2 = no)
  C_variante_optico.tif       dNDVI < --u_ndvi (-0,1)
  C_variante_L.tif            dHV_L < --u_hv (-1,5 dB)
  C_variante_multisensor.tif  Random Forest de rasgos, clases 1 y 2 juntas

Control del practico: "cultivos y pasturas no se detectan como perdida": un
cultivo cosechado baja el NDVI y no es desmonte. El rasgo NDVI_actual y la
clase 4 de entrenamiento estan para eso; se verifica en la matriz del Tp4.

ENTRENAMIENTO EQUILIBRADO (por defecto, como en la corrida del desarrollo)
  El Random Forest se entrena con el MISMO numero de pixeles por clase y con
  class_weight="balanced" (funciones_cambio.fusion_pixel_o_rasgo, equilibrar=True).
  Eso equivale a decirle al modelo que la degradacion es tan frecuente como el
  monte estable: infla las clases chicas. Con --sin_equilibrar se usan los
  pixeles en la proporcion en que estan en los poligonos, sin pesos.

OPCIONES PARA COMPARAR (no cambian nada si no se escriben)
  --sin_equilibrar      entrena sin equilibrar las clases
  --sin_historico       no usa dHH_L_hist (cambio 2011-2021): el mapa cubre
                        tambien el rincon sureste sin ALOS-1
  --mascara_monte_2021  las tres variantes valen 2 ("no") fuera del monte de
                        MapBiomas 2021 (clases 3, 4 y 6): se comparan en igualdad
  --entrenamiento RUTA  otra capa de entrenamiento (por defecto entrenamiento_C.gpkg)
  --sufijo TEXTO        agrega TEXTO al nombre de las salidas, para no pisar la
                        corrida principal (por ejemplo --sufijo _sin_equilibrar)

USO     python Tp9_03_fusion_perdida_degradacion.py --pixel 20
        python Tp9_03_fusion_perdida_degradacion.py --pixel 20 --sin_equilibrar --sufijo _sin_equilibrar
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
from funciones_comunes import leer_tif, grilla_de_tif, leer_en_grilla, guardar_tif, lin_a_db, Bitacora  # noqa: E402
from funciones_cambio import cociente_db, leer_entrenamiento, fusion_pixel_o_rasgo, figura_mapa  # noqa: E402

CLASES = {1: "perdida", 2: "degradacion", 3: "monte estable", 4: "no bosque estable"}


def primero(capas, *nombres):
    for n in nombres:
        if n in capas:
            return capas[n], n
    return None, None


def main():
    import geopandas as gpd

    # ---------------------------------------------------- parametros (se cambian al correr)
    ap = argparse.ArgumentParser(description="Tp9, paso 4: Random Forest de rasgos (perdida y degradacion)")
    ap.add_argument("--pixel", type=int, default=20, help="tamano del pixel de la pila, en m")
    ap.add_argument("--u_ndvi", type=float, default=-0.10, help="umbral de la variante solo optico")
    ap.add_argument("--u_hv", type=float, default=-1.5, help="umbral (dB) de la variante solo banda L")
    ap.add_argument("--rh98_como_rasgo", action="store_true", help="usar delta rh98 como rasgo (mapa solo en celdas GEDI)")
    ap.add_argument("--sin_equilibrar", action="store_true",
                    help="entrenar sin equilibrar las clases (por defecto se equilibran: infla las clases chicas)")
    ap.add_argument("--sin_historico", action="store_true", help="no usar el rasgo dHH_L_hist (2011-2021)")
    ap.add_argument("--mascara_monte_2021", action="store_true",
                    help="variantes = 2 ('no') fuera del monte de MapBiomas 2021 (clases 3, 4 y 6)")
    ap.add_argument("--entrenamiento", default=ruta_tp("Tp9", "04_Tablas_de_trabajo", "entrenamiento_C.gpkg"),
                    help="capa de poligonos de entrenamiento")
    ap.add_argument("--sufijo", default="", help="texto que se agrega al nombre de las salidas")
    a = ap.parse_args()
    sf = a.sufijo
    log = Bitacora(ruta_tp("Tp9", "05_Resultados", "06_Control_calidad"), "Tp9_03_fusion" + sf)
    ruta = ruta_tp("Tp9", "02_Subsets_SNAP_QGIS", "C_pila_temporal_%dm.tif" % a.pixel)
    p, _, tags = leer_tif(ruta)
    g = grilla_de_tif(ruta)
    r = {}
    l_new, n1 = primero(p, "L_NISAR_2026_HV", "L_NISAR_2026_HH")
    l_ref, n2 = primero(p, "L_ALOS2_2021_HV" if (n1 or "").endswith("HV") else "L_ALOS2_2021_HH")
    if l_new is not None and l_ref is not None:
        pol = n1[-2:]                                   # HV si hay; si no, HH (y se nota en el nombre)
        r["d%s_L" % pol] = cociente_db(l_ref, l_new)
        r["%s_L_actual_dB" % pol] = lin_a_db(l_new)
        log("d%s_L = %s / %s" % (pol, n1, n2))
        if pol == "HH":
            log("AVISO: sin HV de NISAR, el cambio en L se mide en HH (menos sensible a la biomasa).")
    if "L_ALOS1_2011_HH" in p and "L_ALOS2_2021_HH" in p and not a.sin_historico:
        r["dHH_L_hist"] = cociente_db(p["L_ALOS1_2011_HH"], p["L_ALOS2_2021_HH"])
    vh = sorted([k for k in p if k.startswith("C_S1_") and k.endswith("_VH")])
    if len(vh) >= 2:
        r["dVH_C"] = cociente_db(p[vh[0]], p[vh[-1]])
        log("dVH_C = %s / %s" % (vh[-1], vh[0]))
    nd = sorted([k for k in p if k.startswith("O_NDVI_")])
    if len(nd) >= 2:
        r["dNDVI"] = (p[nd[-1]] - p[nd[0]]).astype("float32")
        r["NDVI_actual"] = p[nd[-1]]
        log("dNDVI = %s - %s" % (nd[-1], nd[0]))
    ruta_rh = ruta_tp("Tp9", "02_Subsets_SNAP_QGIS", "C_delta_rh98_%dm.tif" % a.pixel)
    drh = leer_en_grilla(ruta_rh, g, "nearest", banda=1) if os.path.exists(ruta_rh) else None
    if a.rh98_como_rasgo and drh is not None:
        r["delta_rh98"] = drh
        log("AVISO: delta_rh98 entra como rasgo: el mapa queda SOLO en las celdas con huellas GEDI.")
    if a.sin_historico:
        log("Sin dHH_L_hist (--sin_historico): el cambio 2011-2021 no entra; el mapa cubre tambien el rincon sin ALOS-1.")
    if not r:
        sys.exit("NO SE PUEDE SEGUIR: la pila no tiene pares de fechas para calcular cambios. Revise el paso 1.")
    fuente = tags.get("FUENTE", "")
    R = lambda n: ruta_tp("Tp9", "05_Resultados", "02_Rasters", n)      # noqa: E731
    # mascara de monte 2021 (MapBiomas): fuera del monte, una variante no puede decir "perdida"
    monte21 = None
    if a.mascara_monte_2021:
        mb = ruta_tp("Tp9", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", "C_FEDERAL_MapBiomas_cobertura_1985_2025.tif")
        if os.path.exists(mb):
            c21 = leer_en_grilla(mb, g, "nearest", banda=2021 - 1985 + 1)
            monte21 = np.isin(c21, [3, 4, 6])
            log("Mascara de monte 2021 (MapBiomas 3, 4 y 6): %.1f %% del sitio. Fuera de ella las variantes valen 2 ('no')."
                % (100 * monte21.mean()))
        else:
            log("AVISO: no esta %s: las variantes van SIN mascara de monte." % mb)

    def cod(m):
        """1 = perdida o degradacion, 2 = no, NaN = sin dato; con mascara, 2 fuera del monte 2021."""
        x = np.where(np.isfinite(m), np.where(m, 1, 2), np.nan).astype("float32")
        if monte21 is not None:
            x = np.where(np.isfinite(x) & ~monte21, 2, x).astype("float32")
        return x
    if "dNDVI" in r:
        guardar_tif(R("C_variante_optico%s.tif" % sf), {"clase": cod(r["dNDVI"] < a.u_ndvi)}, g, fuente,
                    "Solo optico: dNDVI < %.2f. 1 perdida/degradacion, 2 no%s"
                    % (a.u_ndvi, " (solo en el monte 2021)" if monte21 is not None else ""))
    dl = next((k for k in ("dHV_L", "dHH_L") if k in r), None)
    if dl:
        guardar_tif(R("C_variante_L%s.tif" % sf), {"clase": cod(r[dl] < a.u_hv)}, g, fuente,
                    "Solo banda L: %s < %.1f dB. 1 perdida/degradacion, 2 no%s"
                    % (dl, a.u_hv, " (solo en el monte 2021)" if monte21 is not None else ""))
    ent = a.entrenamiento
    if not os.path.exists(ent):
        os.makedirs(os.path.dirname(ent), exist_ok=True)
        gpd.GeoDataFrame({"codigo": pd.Series(dtype="int32"), "clase": pd.Series(dtype="str")},
                         geometry=gpd.GeoSeries([], crs=EPSG), crs=EPSG).to_file(ent, layer="entrenamiento", driver="GPKG", engine="pyogrio", geometry_type="Polygon")
        log("Se creo la capa de entrenamiento vacia: %s (%s)" % (ent, "; ".join("%d %s" % kv for kv in CLASES.items())))
        log.cerrar("digitalizar y volver a correr")
        return
    y = leer_entrenamiento(ent, g)
    log("Entrenamiento: %s" % ent)
    log("Entrenamiento equilibrado: %s" % ("NO (pixeles en su proporcion, sin pesos)" if a.sin_equilibrar else
        "SI (mismo numero de pixeles por clase y class_weight='balanced': sobrestima las clases chicas)"))
    try:
        mapa, prob, info = fusion_pixel_o_rasgo(r, y, equilibrar=not a.sin_equilibrar)
    except ValueError as e:
        log("NO SE PUEDE ENTRENAR: %s" % e)
        if a.rh98_como_rasgo:
            log("Con --rh98_como_rasgo solo sirven los poligonos que caen en celdas con huellas GEDI en los dos")
            log("periodos (C_delta_rh98_20m.tif). Ninguno cae ahi: agregue poligonos en esas celdas o corra sin la opcion.")
        log.cerrar("python Tp9_03_fusion_perdida_degradacion.py --pixel %d" % a.pixel)
        return
    log("Rasgos: %s" % ", ".join(r))
    log("Exactitud fuera de bolsa (OPTIMISTA): %.3f" % info["exactitud_fuera_de_bolsa_OPTIMISTA"])
    for k, v in sorted(info["importancia"].items(), key=lambda kv: -kv[1]):
        log("   importancia %-16s %.3f" % (k, v))
    guardar_tif(R("C_perdida_degradacion%s.tif" % sf), {"clase": mapa, "probabilidad": prob}, g, fuente,
                "Random Forest de rasgos. " + "; ".join("%d %s" % kv for kv in CLASES.items()))
    multi = np.where(np.isfinite(mapa), np.where(np.isin(mapa, [1, 2]), 1, 2), np.nan).astype("float32")
    if monte21 is not None:
        multi = np.where(np.isfinite(multi) & ~monte21, 2, multi).astype("float32")
    guardar_tif(R("C_variante_multisensor%s.tif" % sf), {"clase": multi}, g, fuente,
                "Multisensor: perdida + degradacion = 1, resto = 2")
    for c, n in CLASES.items():
        log("   %-18s %9.1f ha" % (n, np.nansum(mapa == c) * a.pixel ** 2 / 1e4))
    if drh is not None and not a.rh98_como_rasgo:
        log.titulo("Control complementario con GEDI: delta rh98 (m) por clase del mapa")
        ok = np.isfinite(drh) & np.isfinite(mapa)
        t = pd.DataFrame({"clase": pd.Series(mapa[ok]).map(CLASES), "delta_rh98_m": drh[ok]})
        res = t.groupby("clase").delta_rh98_m.describe()[["count", "50%", "mean"]].round(2)
        # celdas de 200 m distintas por clase (cada celda repite su valor en muchos pixeles)
        fil, col = np.nonzero(ok)
        paso = max(int(round(200.0 / a.pixel)), 1)
        t["celda"] = (fil // paso) * 100000 + (col // paso)
        res["celdas"] = t.groupby("clase").celda.nunique()
        log(res.to_string())
        log("Se espera: perdida y degradacion con delta negativo; monte estable cerca de 0.")
        log("count = pixeles de %d m, NO observaciones independientes; celdas = celdas GEDI de 200 m distintas." % a.pixel)
        log("Una caida de menos de 3 m no confirma ni descarta nada (es el minimo interpretable del paso 2).")
        res.to_csv(ruta_tp("Tp9", "05_Resultados", "04_Tablas", "C_control_gedi_por_clase%s.csv" % sf), encoding="utf-8-sig")
    figura_mapa(mapa, ruta_tp("Tp9", "05_Resultados", "05_Graficos", "C_perdida_degradacion%s.png" % sf),
                "Perdida y degradacion del monte (fusion de rasgos)", fuente[:300], etiquetas=CLASES, cmap="tab10")
    log.cerrar("Tp4_02/Tp4_03 por variante; responder las preguntas del Tp9")


if __name__ == "__main__":
    main()
