# -*- coding: utf-8 -*-
"""
Tp10_06_dominio_huella_S.py   [SE CORRE]   Tp10, paso 11 (comparación de variantes en la huella de NovaSAR)
==========================================================================================================
La variante multisensor con S clasifica solo en la franja de NovaSAR (39 % del sitio); las otras
cuatro, en todo el sitio. Comparar su comisión con la de las demas mezcla dos cosas: el efecto de
la banda S y el cambio de superficie. Este programa evalua las cinco variantes en la MISMA
superficie, la huella de NovaSAR, de dos maneras:

  A. Estimación de dominio: con la muestra de cada variante, solo los puntos que caen en la huella,
     y el estimador de Olofsson (Tp4_03) con el área de cada estrato dentro de la huella.
  B. Misma muestra: los 142 puntos sorteados para la variante con S (todos en la huella) evaluan
     los cinco mapas con el estimador por estratos de Stehman (2014), usando los estratos del mapa
     con S. Es la comparación más justa: mismos puntos, misma superficie.

USO
    python Tp10_06_dominio_huella_S.py
SALIDA
    05_Resultados/04_Tablas/tabla_de_variantes_urbano_huella_S.csv
"""
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))
sys.path.insert(0, os.path.join(_d, "Tp4_Validacion", "03_Scripts"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402
import geopandas as gpd                                               # noqa: E402
import rasterio                                                       # noqa: E402

from configuracion_comun import ruta_tp                               # noqa: E402
from funciones_comunes import Bitacora                                # noqa: E402
from Tp4_03_exactitud_y_area import estimar                           # noqa: E402

VARIANTES = [("Óptico solo", "optico"), ("SAR solo (C)", "C"), ("SAR multibanda", "SAR_multibanda"),
             ("Multisensor", "multisensor"), ("Multisensor con S", "multisensor_con_S")]


def puntos(v):
    carpeta = ruta_tp("Tp4", "04_Tablas_de_trabajo")
    pts = gpd.read_file(os.path.join(carpeta, "B_CONCORDIA_variante_%s_puntos_a_etiquetar.gpkg" % v))
    llave = pd.read_csv(os.path.join(carpeta, "B_CONCORDIA_variante_%s_llave_NO_ABRIR.csv" % v), encoding="utf-8-sig")
    t = pts.merge(llave, on="id")
    t = t[t.clase_ref.notna()].copy()
    t["clase_ref"] = t.clase_ref.astype(float).astype(int)
    return t


def razon(y, x, h, N):
    """Estimador de razon por estratos (Stehman 2014, ec. 27-28): R = sum N_h ybar_h / sum N_h xbar_h."""
    Y = X = V = 0.0
    for k, Nk in N.items():
        s = h == k
        Y += Nk * y[s].mean()
        X += Nk * x[s].mean()
    R = Y / X if X > 0 else np.nan
    for k, Nk in N.items():
        s = h == k
        n = s.sum()
        if n > 1:
            d = y[s] - R * x[s]
            V += Nk ** 2 * (1 - n / Nk) * d.var(ddof=1) / n
    return R, 1.96 * np.sqrt(V) / X if X > 0 else np.nan


def main():
    log = Bitacora(ruta_tp("Tp10", "05_Resultados", "06_Control_calidad"), "Tp10_06_dominio_huella_S")
    mapas = {}
    for _, v in VARIANTES:
        with rasterio.open(ruta_tp("Tp10", "05_Resultados", "02_Rasters", "B_CONCORDIA_variante_%s.tif" % v)) as s:
            mapas[v] = s.read(1)
            tr = s.transform
            area_px = abs(s.res[0] * s.res[1]) / 10000.0
    D = np.all([mapas[v] > 0 for _, v in VARIANTES], axis=0)
    A = D.sum() * area_px
    log("Huella de NovaSAR con dato en las cinco variantes: %.0f ha (%.1f %% del sitio)" % (A, 100 * D.mean()))
    log("")
    log("A. ESTIMACIÓN DE DOMINIO (cada variante con sus propios puntos dentro de la huella)")
    filas = []
    for nombre, v in VARIANTES:
        t = puntos(v)
        f, c = rasterio.transform.rowcol(tr, t.geometry.x.values, t.geometry.y.values)
        t = t[D[np.array(f), np.array(c)]]
        n = np.zeros((2, 2))
        for _, r in t.iterrows():
            n[int(r.clase_mapa) - 1, int(r.clase_ref) - 1] += 1
        pix = [int(((mapas[v] == k) & D).sum()) for k in (1, 2)]
        cl, g, _ = estimar(n, pix, area_px, ["urbano", "no_urbano"], ["urbano", "no_urbano"])
        q = cl.iloc[0]
        filas.append({"metodo": "A dominio", "variante": nombre, "puntos": int(n.sum()),
                      "exactitud_global": "%.3f +/- %.3f" % (g["exactitud_global"], g["IC95_global"]),
                      "comision": "%.3f +/- %.3f" % (q.comision, q.IC95_usuario),
                      "omision": "%.3f +/- %.3f" % (q.omision, q.IC95_productor),
                      "area_urbana_estimada_ha": "%.0f +/- %.0f" % (q.area_estimada_ha, q.IC95_area_ha),
                      "area_urbana_mapa_ha": "%.0f" % (pix[0] * area_px)})
    log(pd.DataFrame(filas).drop(columns="metodo").to_string(index=False))
    log("")
    log("B. MISMA MUESTRA (142 puntos de la variante con S, estratos del mapa con S, Stehman 2014)")
    t = puntos("multisensor_con_S")
    f, c = rasterio.transform.rowcol(tr, t.geometry.x.values, t.geometry.y.values)
    f, c = np.array(f), np.array(c)
    h = mapas["multisensor_con_S"][f, c].astype(int)
    N = {k: int(((mapas["multisensor_con_S"] == k) & D).sum()) for k in (1, 2)}
    ref = (t.clase_ref.values == 1).astype(float)
    filasB = []
    for nombre, v in VARIANTES:
        m = (mapas[v][f, c] == 1).astype(float)
        ok = (m == ref).astype(float)
        uno = np.ones_like(ref)
        g, ig = razon(ok, uno, h, N)
        u, iu = razon(m * ref, m, h, N)
        p, ip = razon(m * ref, ref, h, N)
        a, ia = razon(ref, uno, h, N)
        filasB.append({"metodo": "B misma muestra", "variante": nombre, "puntos": len(ref),
                       "exactitud_global": "%.3f +/- %.3f" % (g, ig),
                       "comision": "%.3f +/- %.3f" % (1 - u, iu),
                       "omision": "%.3f +/- %.3f" % (1 - p, ip),
                       "area_urbana_estimada_ha": "%.0f +/- %.0f" % (a * A, ia * A),
                       "area_urbana_mapa_ha": "%.0f" % (((mapas[v] == 1) & D).sum() * area_px)})
    log(pd.DataFrame(filasB).drop(columns=["metodo", "area_urbana_estimada_ha"]).to_string(index=False))
    log("Área urbana estimada en la huella (es la misma para los cinco mapas: sale de la referencia): %s ha"
        % filasB[0]["area_urbana_estimada_ha"])
    out = ruta_tp("Tp10", "05_Resultados", "04_Tablas", "tabla_de_variantes_urbano_huella_S.csv")
    pd.DataFrame(filas + filasB).to_csv(out, index=False, encoding="utf-8-sig")
    log("Tabla:", out)
    log.cerrar()


if __name__ == "__main__":
    main()
