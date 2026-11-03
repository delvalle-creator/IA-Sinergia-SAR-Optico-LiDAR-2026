# -*- coding: utf-8 -*-
"""
Tp7_06_embeddings_cambio.py   [AMPLIACION, FUERA DE LA EVALUACION]   Tp7, despues del paso 6
==========================================================================================
Copia, para el alumno, de la parte Tp7 de des_embeddings.py del desarrollo del docente (22/10/2026).

QUE HACE
  Lee los embeddings anuales AlphaEarth de 2018 y 2025 (64 dimensiones por pixel de 10 m, enteros de 8 bits:
  valor = signo(DN) x (DN / 127,5)^2; -128 = sin dato), los normaliza (norma 1) y calcula en cada pixel la
  SEMEJANZA entre los dos anos como el producto escalar (coseno): 1 = sin cambio.
  Resume la semejanza en la cicatriz, el deposito, el resto de la ladera relevada en 2018, el anillo de
  referencia y todo el sitio. Umbral de cambio: el percentil 10 de la semejanza en la ladera (sin las formas);
  el histograma con esa linea queda en 05_Graficos (regla 6).
  El embedding de 2018 resume un ano en que el deslizamiento empezo en septiembre: es mayormente anterior al
  evento. Un cambio de embedding no dice la causa ni la fecha.

ENTRADAS  02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/E1_DIAMANTE_BARRANCA_AlphaEarth_embeddings_<ano>_10m.tif
          04_Tablas_de_trabajo/E1_cicatriz_y_deposito.gpkg, E1_ladera_reparada.gpkg, E1_zona_referencia.gpkg
SALIDAS   05_Resultados/04_Tablas/E1_embeddings_cambio.csv
          05_Resultados/05_Graficos/E1_embeddings_histograma_umbral.png
          05_Resultados/06_Control_calidad/Tp7_06_embeddings.log
USO       python Tp7_06_embeddings_cambio.py
"""
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
from funciones_cambio import umbral_documentado                       # noqa: E402

# ------------------------------------------------------------ PARAMETROS
SITIO = "E1_DIAMANTE_BARRANCA"
ANIOS = (2018, 2025)
PERCENTIL_UMBRAL = 10


def main():
    import geopandas as gpd
    import rasterio
    from rasterio.features import rasterize

    log = Bitacora(ruta_tp("Tp7", "05_Resultados", "06_Control_calidad"), "Tp7_06_embeddings")
    Q = ruta_tp("Tp7", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", SITIO + "_AlphaEarth_embeddings_%d_10m.tif")
    E = []
    for a in ANIOS:
        if not os.path.exists(Q % a):
            sys.exit("Falta %s." % (Q % a))
        with rasterio.open(Q % a) as s:
            x = s.read().astype("f4")
            T, crs, sh = s.transform, s.crs, (s.height, s.width)
        nod = (x == -128).any(0)
        v = np.sign(x) * (x / 127.5) ** 2
        n = np.linalg.norm(v, axis=0)
        n[n == 0] = 1
        v = v / n
        v[:, nod] = np.nan
        log("Embedding %d: %d x %d pixeles de 10 m, %.1f %% con dato" % (a, sh[1], sh[0], 100 * (~nod).mean()))
        E.append(v)
    sim = (E[0] * E[1]).sum(0)
    tab = ruta_tp("Tp7", "04_Tablas_de_trabajo")

    def mascara(nombre, capa=None, tipo=None):
        g = gpd.read_file(os.path.join(tab, nombre), layer=capa) if capa else gpd.read_file(os.path.join(tab, nombre))
        if tipo:
            g = g[g.tipo == tipo]
        g = g.to_crs(crs)
        return rasterize([(x, 1) for x in g.geometry], out_shape=sh, transform=T, all_touched=True).astype(bool)
    mc = mascara("E1_cicatriz_y_deposito.gpkg", "formas", "cicatriz")
    md = mascara("E1_cicatriz_y_deposito.gpkg", "formas", "deposito")
    ml = mascara("E1_ladera_reparada.gpkg")
    mr = mascara("E1_zona_referencia.gpkg")
    ok = np.isfinite(sim)
    v_lad = sim[ml & ~mc & ~md & ok]
    p = float(np.percentile(v_lad, PERCENTIL_UMBRAL))
    u, txt = umbral_documentado(v_lad, "semejanza 2018-2025 en la ladera", ruta_tp("Tp7", "05_Resultados", "05_Graficos",
                                "E1_embeddings_histograma_umbral.png"), metodo="manual", manual=p, signo="<")
    log("Umbral de cambio = percentil %d de la ladera: %.3f (%s)" % (PERCENTIL_UMBRAL, u, txt))
    filas = []
    for nom, m in (("Cicatriz (CBERS-4A)", mc), ("Deposito (CBERS-4A)", md), ("Ladera relevada en 2018", ml & ~mc & ~md),
                   ("Anillo de referencia", mr), ("Todo el sitio", ok)):
        v = sim[m & ok]
        filas.append({"zona": nom, "pixeles_10m": int(v.size), "semejanza_mediana": round(float(np.median(v)), 3),
                      "percentil_10": round(float(np.percentile(v, 10)), 3), "%_bajo_umbral": round(100 * float((v < u).mean()), 1)})
        log("%-25s %8d pixeles; semejanza mediana %.3f; %.0f %% por debajo del umbral"
            % (nom, v.size, filas[-1]["semejanza_mediana"], filas[-1]["%_bajo_umbral"]))
    out = ruta_tp("Tp7", "05_Resultados", "04_Tablas", "E1_embeddings_cambio.csv")
    pd.DataFrame(filas).to_csv(out, index=False, encoding="utf-8-sig")
    log("Tabla: %s" % out)
    log("Un cambio de embedding no identifica causa ni fecha: en el anillo, el rio y la costa cambian por el nivel del agua.")
    log.cerrar()


if __name__ == "__main__":
    main()
