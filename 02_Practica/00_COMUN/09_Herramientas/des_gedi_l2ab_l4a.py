# -*- coding: utf-8 -*-
"""
des_gedi_l2ab_l4a.py  (herramienta del docente, 00_COMUN/09_Herramientas)
=========================================================================
Une, huella por huella (shot_number), los tres productos GEDI que el curso tiene
recortados en 08_Originales_crudos/LIDAR/<SITIO>:

  GEDI02_A (L2A v003): rh98 y los filtros del curso (funciones_lidar.leer_gedi_l2a)
  GEDI02_B (L2B v003): cover (fraccion de cobertura del dosel), pai (indice de
                       area de plantas), fhd_normal (diversidad de altura del follaje)
  GEDI_L4A (L4A v003): agbd (biomasa aerea, Mg/ha) y agbd_se (su error estandar)

Es lo mismo que hace el complemento GEDIMetrics de QGIS (Cotrina-Sanchez et al.,
2026) con la union por shot_number, pero leyendo los granulos que ya estan en el
disco (sin red). Una huella entra si pasa los filtros del curso en L2A, si su
rh98 es plausible (<= 50 m), si l2b_quality_flag(_rel3) = 1 y si l4a_quality_flag(_rel3) = 1.
Con --mediana_pasada 40 (opcional) tambien se excluyen las pasadas (fechas) cuya rh98 mediana
supera ese valor: es la misma regla de plausibilidad de Tp3_03 (columna plausible).

Uso:
    python des_gedi_l2ab_l4a.py --sitio A2_IBICUY
    python des_gedi_l2ab_l4a.py --sitio A2_IBICUY --mediana_pasada 40   (regla de Tp3_03)
    python des_gedi_l2ab_l4a.py --sitio A1_DELTA_QUEMAS
    python des_gedi_l2ab_l4a.py --sitio C_FEDERAL
"""
import os
import sys
import glob
import argparse

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
COMUN = os.path.dirname(AQUI)
PRACTICA = os.path.dirname(COMUN)
sys.path.insert(0, COMUN)
from configuracion_comun import SITIOS, ORIGINALES        # noqa: E402
from funciones_lidar import leer_gedi_l2a                 # noqa: E402

ALTURA_MAX = 50.0
CONFIG = {
    # sitio: (practico, prefijo, mapa de clases, {codigo: nombre}, periodos)
    "A2_IBICUY": ("Tp3_Armonizacion", "A2_IBICUY", None, None, None),
    "A1_DELTA_QUEMAS": ("Tp5_Incendios", "A1",
                        r"Tp5_Incendios\05_Resultados\02_Rasters\A1_variante_multisensor.tif",
                        {1: "quemado (V4)", 2: "no quemado (V4)"},
                        # la misma estacion (primavera y verano) antes y despues de las quemas de 2020
                        [("antes", "2019-10-01", "2020-03-31"), ("despues", "2020-10-01", "2021-03-31")]),
    "C_FEDERAL": ("Tp9_Deforestacion", "C",
                  r"Tp9_Deforestacion\05_Resultados\02_Rasters\C_perdida_degradacion.tif",
                  {1: "perdida", 2: "degradacion", 3: "monte estable", 4: "no bosque estable"},
                  # los dos periodos del Tp9_02
                  [("periodo 1", "2019-04-01", "2022-12-31"), ("periodo 2", "2024-04-26", "2025-12-31")]),
}
VARS = ["rh98", "cover", "pai", "fhd_normal", "agbd"]


def log(*a):
    print(*a)
    sys.stdout.flush()


def leer_productos(carpeta, patron, bbox, campos, ruta_lat):
    filas = []
    import h5py
    for f in sorted(glob.glob(os.path.join(carpeta, patron))):
        try:
            with h5py.File(f, "r") as h:
                for haz in [k for k in h.keys() if k.startswith("BEAM")]:
                    g = h[haz]
                    pares = [p for p in ruta_lat if p[0] in g]
                    if not pares:
                        continue
                    lat_k, lon_k = pares[0]
                    lat = g[lat_k][:]
                    lon = g[lon_k][:]
                    m = (lon >= bbox[0]) & (lon <= bbox[2]) & (lat >= bbox[1]) & (lat <= bbox[3])
                    if not m.any():
                        continue
                    d = {"shot_number": g["shot_number"][:][m].astype("u8")}
                    for c in campos:
                        # la version 003 agrega _rel3 al nombre de las banderas de calidad
                        k = c + "_rel3" if c + "_rel3" in g else c
                        d[c] = g[k][:][m] if k in g else np.full(m.sum(), np.nan)
                    filas.append(pd.DataFrame(d))
        except OSError as e:
            log("  no se pudo leer", os.path.basename(f), e)
    if not filas:
        return pd.DataFrame(columns=["shot_number"] + campos)
    return pd.concat(filas).drop_duplicates("shot_number")


def ic_dif_medianas(a, b, n=2000, semilla=2026):
    """IC 95 % bootstrap de mediana(b) - mediana(a), muestras independientes."""
    r = np.random.default_rng(semilla)
    a, b = np.asarray(a), np.asarray(b)
    if len(a) < 5 or len(b) < 5:
        return np.nan, np.nan, np.nan
    d = [np.median(r.choice(b, b.size)) - np.median(r.choice(a, a.size)) for _ in range(n)]
    return np.median(b) - np.median(a), np.percentile(d, 2.5), np.percentile(d, 97.5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", required=True, choices=sorted(CONFIG))
    ap.add_argument("--mediana_pasada", type=float, default=None,
                    help="opcional: excluir tambien las pasadas con rh98 mediano mayor que este valor (Tp3_03 usa 40)")
    a = ap.parse_args()
    tp, pref, mapa, clases, periodos = CONFIG[a.sitio]
    bbox = SITIOS[a.sitio]["bbox"]
    base = os.path.join(ORIGINALES, "LIDAR", a.sitio)
    log("Sitio %s  bbox %s" % (a.sitio, bbox))

    l2a = []
    for f in sorted(glob.glob(os.path.join(base, "GEDI02_A", "*.h5"))):
        l2a.append(leer_gedi_l2a(f, bbox))
    l2a = pd.concat([x for x in l2a if len(x)])
    l2a["shot_number"] = l2a["shot_number"].astype("u8")
    log("GEDI L2A: %d huellas en el sitio, %d validas con los filtros del curso" % (len(l2a), l2a.valido.sum()))

    l2b = leer_productos(os.path.join(base, "GEDI02_B"), "*.h5", bbox,
                         ["cover", "pai", "fhd_normal", "l2b_quality_flag"],
                         [("lat_lowestmode", "lon_lowestmode")])
    log("GEDI L2B: %d huellas en el sitio" % len(l2b))
    l4a = leer_productos(os.path.join(base, "GEDI_L4A"), "*.h5", bbox,
                         ["agbd", "agbd_se", "l4a_quality_flag"], [("lat_lowestmode", "lon_lowestmode")])
    log("GEDI L4A: %d huellas en el sitio" % len(l4a))

    t = l2a.merge(l2b, on="shot_number", how="left").merge(l4a, on="shot_number", how="left")
    for c in ("cover", "pai", "fhd_normal", "agbd", "agbd_se"):
        t.loc[t[c] < 0, c] = np.nan                       # -9999 = sin dato
    t["plausible"] = ~(t.rh98 > ALTURA_MAX)
    if a.mediana_pasada is not None:
        # misma regla que Tp3_03: una pasada (fecha) entera con rh98 mediano alto no es plausible
        med = t[t.valido].groupby("fecha").rh98.median()
        malas = med[med > a.mediana_pasada].index
        t.loc[t.fecha.isin(malas), "plausible"] = False
        log("Pasadas con rh98 mediano > %g m (no plausibles): %s" % (a.mediana_pasada, ", ".join(map(str, malas)) or "ninguna"))
    t["con_l2b"] = t.l2b_quality_flag == 1
    t["con_l4a"] = t.l4a_quality_flag == 1
    t["valida_3"] = t.valido & t.plausible & t.con_l2b & t.con_l4a & t.cover.notna() & t.agbd.notna()
    log("Union por shot_number: %d validas en L2A; %d plausibles; %d ademas con L2B de calidad; %d ademas con L4A de calidad"
        % (t.valido.sum(), (t.valido & t.plausible).sum(), (t.valido & t.plausible & t.con_l2b).sum(), t.valida_3.sum()))
    t["valida_sin_banderas"] = t.valido & t.plausible & t.cover.notna() & t.agbd.notna()
    log("Sin exigir las banderas de L2B y L4A (solo los filtros del curso en L2A y dato en cover y agbd): %d"
        % t.valida_sin_banderas.sum())
    if t.valida_3.sum() >= 100:
        v = t[t.valida_3].copy()
        log("Se analizan las %d huellas validas en los tres productos." % len(v))
    else:
        v = t[t.valida_sin_banderas].copy()
        log("AVISO: menos de 100 huellas pasan las banderas de L2B y L4A; se analizan las %d con los filtros del curso"
            " en L2A y dato en cover y agbd (declararlo)." % len(v))
    v["fecha_dt"] = pd.to_datetime(v.fecha)
    log("Huellas analizadas: %d (%s a %s)" % (len(v), v.fecha.min(), v.fecha.max()))

    carp_t = os.path.join(PRACTICA, tp, "05_Resultados", "04_Tablas")
    carp_v = os.path.join(PRACTICA, tp, "05_Resultados", "03_Vectores")
    os.makedirs(carp_t, exist_ok=True)
    os.makedirs(carp_v, exist_ok=True)

    if mapa:
        import rasterio
        from pyproj import Transformer
        with rasterio.open(os.path.join(PRACTICA, mapa)) as r:
            tr = Transformer.from_crs(4326, r.crs, always_xy=True)
            x, y = tr.transform(v.lon.values, v.lat.values)
            val = np.array([s[0] for s in r.sample(zip(x, y))])
            nod = r.nodata
        v["clase"] = [clases.get(int(c), None) if (nod is None or c != nod) else None for c in val]
        log("Clases del mapa en las huellas: %s" % dict(pd.Series(val).value_counts().sort_index()))

    sp = v[["rh98", "cover", "pai", "fhd_normal", "agbd"]].corr(method="spearman")
    log("")
    log("Spearman con rh98 (huellas analizadas): cover %.2f, pai %.2f, fhd_normal %.2f, agbd %.2f"
        % (sp.loc["rh98", "cover"], sp.loc["rh98", "pai"], sp.loc["rh98", "fhd_normal"], sp.loc["rh98", "agbd"]))

    filas = []
    v["clase_rh98"] = pd.cut(v.rh98, [-1e9, 3, 5, 10, 20, 1e9], labels=["< 3 m", "3-5 m", "5-10 m", "10-20 m", ">= 20 m"])
    log("")
    log("Medianas por clase de rh98:")
    log("  %-9s %6s %6s %6s %6s %8s" % ("clase", "n", "cover", "pai", "fhd", "agbd"))
    for k, g in v.groupby("clase_rh98", observed=True):
        log("  %-9s %6d %6.2f %6.2f %6.2f %8.1f" % (k, len(g), g.cover.median(), g.pai.median(), g.fhd_normal.median(), g.agbd.median()))
        filas.append({"tabla": "por clase de rh98", "grupo": k, "periodo": "todos", "n": len(g),
                      **{x + "_mediana": g[x].median() for x in VARS}})

    if periodos:
        log("")
        log("Por clase del mapa y periodo (medianas; diferencia de medianas con IC 95 % bootstrap, muestras independientes):")
        for cl in [c for c in clases.values()]:
            g = v[v.clase == cl]
            sub = {}
            for nom, d0, d1 in periodos:
                s = g[(g.fecha_dt >= d0) & (g.fecha_dt <= d1)]
                sub[nom] = s
                filas.append({"tabla": "por clase y periodo", "grupo": cl, "periodo": "%s (%s a %s)" % (nom, d0, d1),
                              "n": len(s), **{x + "_mediana": s[x].median() for x in VARS}})
            (n0, s0), (n1, s1) = list(sub.items())
            log("  %s: %s n=%d, %s n=%d" % (cl, n0, len(s0), n1, len(s1)))
            dif = {}
            for x in VARS:
                d, lo, hi = ic_dif_medianas(s0[x].dropna(), s1[x].dropna())
                dif[x] = (d, lo, hi)
                log("     %-10s %8.2f -> %8.2f   diferencia %+.2f [%+.2f, %+.2f]%s" % (
                    x, s0[x].median(), s1[x].median(), d, lo, hi,
                    "" if np.isnan(lo) else ("  (el IC excluye el 0)" if lo > 0 or hi < 0 else "")))
            filas.append({"tabla": "diferencia %s - %s" % (n1, n0), "grupo": cl, "periodo": "",
                          "n": min(len(s0), len(s1)),
                          **{x + "_mediana": dif[x][0] for x in VARS},
                          **{x + "_ic_inf": dif[x][1] for x in VARS},
                          **{x + "_ic_sup": dif[x][2] for x in VARS}})

    salida = os.path.join(carp_t, "%s_gedi_l2ab_l4a_resumen.csv" % pref)
    pd.DataFrame(filas).to_csv(salida, index=False, encoding="utf-8-sig")
    import geopandas as gpd
    gdf = gpd.GeoDataFrame(t.drop(columns=[c for c in ("fecha_dt",) if c in t]).assign(shot_number=t.shot_number.astype(str)),
                           geometry=gpd.points_from_xy(t.lon, t.lat), crs=4326)
    gp = os.path.join(carp_v, "%s_gedi_l2ab_l4a.gpkg" % pref)
    gdf.to_file(gp, layer="gedi_l2a_l2b_l4a", driver="GPKG")
    log("")
    log("Salidas: %s" % salida)
    log("         %s (capa gedi_l2a_l2b_l4a, todas las huellas del sitio con valido, plausible, con_l2b, con_l4a y valida_3)" % gp)


if __name__ == "__main__":
    main()
