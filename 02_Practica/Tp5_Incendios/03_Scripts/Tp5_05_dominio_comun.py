# -*- coding: utf-8 -*-
"""
Tp5_05_dominio_comun.py   [SE CORRE]   Tp5, paso 5 (comparacion de variantes en una superficie comun)
====================================================================================================
Las cuatro variantes del perímetro no cubren lo mismo: la V4 clasifica sólo donde están las seis
capas (franja de SAOCOM, sin nubes y con RdNBR) y la V1 deja sin dato las nubes. Comparar porcentajes de superficies distintas no las
hace equivalentes. Este programa evalua las cuatro en la INTERSECCION (pixeles con dato en las
cuatro), con los puntos de cada muestra que caen en ella y el estimador de Olofsson (Tp4_03):
el area de cada estrato es la de ese estrato dentro de la interseccion. Es una estimacion de
dominio: el tamano de cada muestra baja (solo cuentan los puntos de la interseccion) y asi se
declara. Despues estima la DIFERENCIA de omision, comision y exactitud global de cada variante
frente al óptico, con su IC del 95 % (se suponen muestras independientes entre variantes: la varianza
de la diferencia es la suma de las dos varianzas).

USO
    python Tp5_05_dominio_comun.py
SALIDA
    05_Resultados/04_Tablas/tabla_de_variantes_quemado_dominio_comun.csv
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

VARIANTES = [("V1 optico solo", "optico"), ("V2 SAR solo (C)", "C"),
             ("V3 SAR multibanda", "CL"), ("V4 multisensor", "multisensor")]


def main():
    if not os.path.exists(ruta_tp("Tp5", "05_Resultados", "02_Rasters", "A1_variante_multisensor.tif")):
        sys.exit("Falta A1_variante_multisensor.tif: corra antes Tp5_03_fusion.py (paso 4) y el Tp4 (paso 5).")
    log = Bitacora(ruta_tp("Tp5", "05_Resultados", "06_Control_calidad"), "Tp5_05_dominio_comun")
    mapas, tr = {}, None
    for _, v in VARIANTES:
        with rasterio.open(ruta_tp("Tp5", "05_Resultados", "02_Rasters", "A1_variante_%s.tif" % v)) as s:
            mapas[v] = s.read(1)
            tr = s.transform
            area_px = abs(s.res[0] * s.res[1]) / 10000.0
    D = np.all([mapas[v] > 0 for _, v in VARIANTES], axis=0)
    A = D.sum() * area_px
    log("Superficie común (píxeles con dato en las cuatro variantes): %.0f ha" % A)
    filas, res = [], {}
    for nombre, v in VARIANTES:
        carpeta = ruta_tp("Tp4", "04_Tablas_de_trabajo")
        pts = gpd.read_file(os.path.join(carpeta, "A1_variante_%s_puntos_a_etiquetar.gpkg" % v), layer="puntos")
        llave = pd.read_csv(os.path.join(carpeta, "A1_variante_%s_llave_NO_ABRIR.csv" % v), encoding="utf-8-sig")
        t = pts.merge(llave, on="id")
        t = t[t.clase_ref.notna()].copy()
        t["clase_ref"] = t.clase_ref.astype(float).astype(int)
        f, c = rasterio.transform.rowcol(tr, t.geometry.x.values, t.geometry.y.values)
        t = t[D[np.array(f), np.array(c)]]
        n = np.zeros((2, 2))
        for _, r in t.iterrows():
            n[int(r.clase_mapa) - 1, int(r.clase_ref) - 1] += 1
        pix = [int(((mapas[v] == k) & D).sum()) for k in (1, 2)]
        cl, g, _ = estimar(n, pix, area_px, ["quemado", "no_quemado"], ["quemado", "no_quemado"])
        q = cl.iloc[0]
        res[v] = q
        res[v + "_g"] = g
        filas.append({"variante": nombre, "puntos_en_la_superficie_comun": int(n.sum()),
                      "exactitud_global": "%.3f +/- %.3f" % (g["exactitud_global"], g["IC95_global"]),
                      "omision": "%.3f +/- %.3f" % (q.omision, q.IC95_productor),
                      "comision": "%.3f +/- %.3f" % (q.comision, q.IC95_usuario),
                      "area_estimada_ha": "%.0f +/- %.0f" % (q.area_estimada_ha, q.IC95_area_ha),
                      "porcentaje_quemado": "%.1f +/- %.1f %%" % (100 * q.area_estimada_ha / A, 100 * q.IC95_area_ha / A)})
    t = pd.DataFrame(filas)
    log(t.to_string(index=False))
    log("")
    log("Diferencia frente a la V1 (óptico solo), IC 95 % (muestras independientes):")
    ref = res["optico"]
    for nombre, v in VARIANTES[1:]:
        q, gq, gr = res[v], res[v + "_g"], res["optico_g"]
        partes = []
        for etiqueta, a, b, ia, ib in (("omision", q.omision, ref.omision, q.IC95_productor, ref.IC95_productor),
                                       ("comision", q.comision, ref.comision, q.IC95_usuario, ref.IC95_usuario),
                                       ("exactitud global", gq["exactitud_global"], gr["exactitud_global"],
                                        gq["IC95_global"], gr["IC95_global"])):
            d = a - b
            e = 1.96 * np.sqrt((ia / 1.96) ** 2 + (ib / 1.96) ** 2)
            partes.append("%s %+.3f +/- %.3f (%s)" % (etiqueta, d, e, "significativa" if abs(d) > e else "no demostrada"))
        log("   %-18s %s" % (nombre, "; ".join(partes)))
    out = ruta_tp("Tp5", "05_Resultados", "04_Tablas", "tabla_de_variantes_quemado_dominio_comun.csv")
    t.to_csv(out, index=False, encoding="utf-8-sig")
    log("Tabla:", out)
    log.cerrar("python Tp5_04_gedi_cambio_de_altura.py (paso 6)")


if __name__ == "__main__":
    main()
