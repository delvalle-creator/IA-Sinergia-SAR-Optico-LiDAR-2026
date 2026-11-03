# -*- coding: utf-8 -*-
"""
Tp3_03_lidar_en_el_cubo.py   [SE CORRE]   Tp3, paso 4 de la guia
========================================================
Extrae los valores de cada capa del cubo en las huellas GEDI y en los
segmentos ATL08 validos (presentacion 01 del curso, paso 4).

El LiDAR no se rasteriza: se lleva cada capa del cubo a la huella. Para cada
huella VALIDA del Tp1 (capas gedi_l2a y atl08 de lidar_<SITIO>.gpkg):

  GEDI  : media de los pixeles cuyo centro cae a menos de 12,5 m + medio
          pixel del centro de la huella (la huella mide 25 m de diametro).
  ATL08 : media de los pixeles cuyo centro cae dentro de un RECTANGULO
          orientado con la traza: 100 m a lo largo de la traza por 14 m de
          ancho (el segmento de ATL08), cada lado agrandado en medio pixel.
          El acimut de la traza se calcula entre segmentos consecutivos del
          mismo haz del mismo granulo.

Radar: media en LINEAL (y su equivalente en dB en otra columna). Optico:
media de reflectancias. Se guarda cuantos pixeles entraron en cada media y
la diferencia de dias entre la huella y cada capa: una huella de 2019 junto
a un radar de 2026 no describe el mismo bosque.

PLAUSIBILIDAD (columna "plausible", 1 = se usa, 0 = no)
  Una huella GEDI es NO plausible si su rh98 supera ALTURA_MAXIMA_M (50 m) o
  si la mediana de rh98 de toda su pasada (fecha) supera MEDIANA_PASADA_M
  (40 m): en el Delta no hay monte de esa altura, y una pasada entera con
  alturas imposibles es un error del producto que los indicadores de calidad
  no detectaron. Para ATL08 se aplica el mismo limite de 50 m a h_canopy.
  La columna "motivo_no_plausible" dice por que. Los pasos siguientes (Tp3_04,
  Orange y los Tp5 a Tp10) usan solo las huellas con plausible = 1.

SALIDA
  Tp3_Armonizacion/04_Tablas_de_trabajo/<SITIO>_huellas_con_cubo.csv
  Tp3_Armonizacion/05_Resultados/03_Vectores/<SITIO>_huellas_con_cubo.gpkg

USO
    python Tp3_03_lidar_en_el_cubo.py --sitio A2_IBICUY --pixel 20
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

from configuracion_comun import SITIOS, ruta_tp                       # noqa: E402
from funciones_comunes import leer_tif, lin_a_db, Bitacora            # noqa: E402

# ----------------------------------------------------------------- PARAMETROS
RADIO_GEDI_M = 12.5            # radio de la huella GEDI (25 m de diametro)
LARGO_ATL08_M = 100.0          # largo del segmento ATL08 a lo largo de la traza
ANCHO_ATL08_M = 14.0           # ancho de la huella del haz de ICESat-2 (unos 14 m)
ALTURA_MAXIMA_M = 50.0         # rh98 o h_canopy por encima de esto: no plausible en el Delta
MEDIANA_PASADA_M = 40.0        # pasada GEDI con mediana de rh98 por encima de esto: toda la pasada no plausible


def acimut_atl08(pts):
    """Acimut (radianes, desde el este, antihorario) de la traza de cada segmento ATL08,
    calculado entre segmentos consecutivos del mismo haz del mismo granulo."""
    az = pd.Series(np.nan, index=pts.index)
    for _, g in pts.groupby(["granulo", "haz"]):
        if len(g) < 2:
            continue
        g = g.sort_values("_y")
        dx = np.gradient(g["_x"].to_numpy())
        dy = np.gradient(g["_y"].to_numpy())
        az.loc[g.index] = np.arctan2(dy, dx)
    # un haz con un solo segmento: se usa la mediana del granulo (todas las trazas son casi paralelas)
    if az.isna().any():
        az = az.fillna(az.median() if az.notna().any() else np.pi / 2)
    return az


def main():
    import geopandas as gpd

    ap = argparse.ArgumentParser(description="Lleva el cubo del Tp3 a cada huella LiDAR valida.")
    ap.add_argument("--sitio", required=True, choices=list(SITIOS.keys()))
    ap.add_argument("--pixel", type=int, default=20)
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp3", "05_Resultados", "06_Control_calidad"), "Tp3_03_%s" % a.sitio)

    cubo = ruta_tp("Tp3", "02_Subsets_SNAP_QGIS", "%s_cubo_%dm.tif" % (a.sitio, a.pixel))
    if not os.path.exists(cubo):
        log("No encuentro el cubo %s: use el mismo --pixel que en el paso 1." % cubo)
        log.cerrar()
        return
    capas, perfil, _ = leer_tif(cubo)
    bandas = pd.read_csv(cubo.replace(".tif", "_bandas.csv"), encoding="utf-8-sig")
    fecha_capa = dict(zip(bandas.capa, bandas.fecha))
    T = perfil["transform"]
    pix = T.a
    alto, ancho = perfil["height"], perfil["width"]
    gpkg = ruta_tp("Tp1", "05_Resultados", "03_Vectores", "lidar_%s.gpkg" % a.sitio)
    if not os.path.exists(gpkg):
        log("No existe %s: correr antes Tp1_05_buscar_lidar.py (paso 0) con los granulos bajados." % gpkg)
        log.cerrar()
        return
    import pyogrio
    capas_lidar = [c[0] for c in pyogrio.list_layers(gpkg)]

    filas = []
    for capa in ("gedi_l2a", "atl08"):
        if capa not in capas_lidar:
            continue
        pts = gpd.read_file(gpkg, layer=capa).to_crs(perfil["crs"])
        col_ok = "valido" if capa == "gedi_l2a" else "canopia_valida"
        pts = pts[pts[col_ok].astype(bool)].copy()
        pts["_x"], pts["_y"] = pts.geometry.x, pts.geometry.y
        if capa == "gedi_l2a":
            r = RADIO_GEDI_M + pix / 2.0
            rp = int(np.ceil(r / pix))
            log("%s: %d huellas validas; circulo de %.1f m de radio + medio pixel (hasta %d pixeles de %.0f m alrededor)"
                % (capa, len(pts), RADIO_GEDI_M, rp, pix))
            med_pasada = pts.groupby("fecha").rh98.transform("median")
            mot = np.where(med_pasada > MEDIANA_PASADA_M, "pasada con rh98 mediano > %.0f m" % MEDIANA_PASADA_M,
                           np.where(pts.rh98 > ALTURA_MAXIMA_M, "rh98 > %.0f m" % ALTURA_MAXIMA_M, ""))
        else:
            pts["_az"] = acimut_atl08(pts)
            semilargo, semiancho = LARGO_ATL08_M / 2 + pix / 2.0, ANCHO_ATL08_M / 2 + pix / 2.0
            rp = int(np.ceil(semilargo / pix))
            log("%s: %d segmentos validos; rectangulo de %.0f x %.0f m orientado con la traza + medio pixel por lado"
                % (capa, len(pts), LARGO_ATL08_M, ANCHO_ATL08_M))
            mot = np.where(pts.h_canopy > ALTURA_MAXIMA_M, "h_canopy > %.0f m" % ALTURA_MAXIMA_M, "")
        pts["motivo_no_plausible"] = mot
        for _, p in pts.iterrows():
            col, fil = ~T * (p._x, p._y)
            c0, f0 = int(col), int(fil)
            fila = {"producto": capa, "fecha_lidar": p["fecha"], "x": p._x, "y": p._y}
            fila.update({k: p[k] for k in ("rh98", "rh50", "h_canopy", "elev_lowestmode_elips",
                                          "h_te_best_fit_elips") if k in p})
            fila["plausible"] = int(p.motivo_no_plausible == "")
            fila["motivo_no_plausible"] = p.motivo_no_plausible
            ff, cc = np.mgrid[f0 - rp:f0 + rp + 1, c0 - rp:c0 + rp + 1]
            xc = T.c + (cc + 0.5) * pix - p._x
            yc = T.f - (ff + 0.5) * pix - p._y
            if capa == "gedi_l2a":
                adentro = np.hypot(xc, yc) <= r
            else:
                ca, sa = np.cos(p._az), np.sin(p._az)
                largo = xc * ca + yc * sa            # coordenada a lo largo de la traza
                transv = -xc * sa + yc * ca          # coordenada transversal
                adentro = (np.abs(largo) <= semilargo) & (np.abs(transv) <= semiancho)
            dentro = adentro & (ff >= 0) & (ff < alto) & (cc >= 0) & (cc < ancho)
            if not dentro.any():
                continue
            for nombre, arr in capas.items():
                v = arr[ff[dentro], cc[dentro]]
                v = v[np.isfinite(v)]
                es_radar = not nombre.startswith(("OPT_", "MDE_"))
                fila[nombre] = float(v.mean()) if v.size else np.nan
                if es_radar:
                    fila[nombre + "_dB"] = float(lin_a_db(np.array([v.mean()]))[0]) if v.size else np.nan
                fila["n_" + nombre] = int(v.size)
                try:
                    fila["dias_" + nombre] = abs((pd.Timestamp(p["fecha"]) - pd.Timestamp(fecha_capa.get(nombre))).days)
                except (ValueError, TypeError):
                    fila["dias_" + nombre] = np.nan
            filas.append(fila)
    t = pd.DataFrame(filas)
    out = ruta_tp("Tp3", "04_Tablas_de_trabajo", "%s_huellas_con_cubo.csv" % a.sitio)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    t.to_csv(out, index=False, encoding="utf-8-sig")
    if len(t):
        g = gpd.GeoDataFrame(t, geometry=gpd.points_from_xy(t.x, t.y), crs=perfil["crs"])
        gp = ruta_tp("Tp3", "05_Resultados", "03_Vectores", "%s_huellas_con_cubo.gpkg" % a.sitio)
        os.makedirs(os.path.dirname(gp), exist_ok=True)
        g.to_file(gp, layer="huellas", driver="GPKG")
        log("Huellas con valores del cubo: %d   ->  %s" % (len(t), out))
        log.titulo("Plausibilidad (columna plausible)")
        for prod, sub in t.groupby("producto"):
            log("  %-9s %6d huellas: %6d plausibles, %4d no plausibles" % (
                prod, len(sub), int(sub.plausible.sum()), int((sub.plausible == 0).sum())))
        for m, n in t.loc[t.plausible == 0, "motivo_no_plausible"].value_counts().items():
            log("     %-40s %d" % (m, n))
        log("Los pasos siguientes usan solo plausible = 1.")
        npx = [c for c in t.columns if c.startswith("n_") and "NISAR_gamma0_HV_20260930" in c]
        if npx:
            log.titulo("Pixeles por huella (%s)" % npx[0][2:])
            for prod, sub in t.groupby("producto"):
                v = sub[npx[0]]
                log("  %-9s promedio %.2f  minimo %d  maximo %d  moda %d (%.0f %% de las huellas)" % (
                    prod, v.mean(), v.min(), v.max(), v.mode().iloc[0], 100 * (v == v.mode().iloc[0]).mean()))
        dias = [c for c in t.columns if c.startswith("dias_")]
        if dias:
            log.titulo("Diferencia de dias LiDAR-sensor (mediana por capa, huellas plausibles)")
            tp = t[t.plausible == 1]
            for c in dias:
                log("   %-34s %s" % (c[5:], tp[c].median()))
    else:
        log("Ninguna huella valida cae dentro del cubo.")
    log.cerrar("python Tp3_04_contexto_y_huellas.py --sitio %s --pixel %d" % (a.sitio, a.pixel))


if __name__ == "__main__":
    main()
