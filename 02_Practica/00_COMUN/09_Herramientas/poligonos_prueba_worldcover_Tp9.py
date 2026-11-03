# -*- coding: utf-8 -*-
"""Poligonos de PRUEBA para la capa de entrenamiento del Tp9 (Federal), sacados de ESA WorldCover 10 m 2021
y de los cambios 2021-2026 de la pila del Tp9 (21/10/2026).

No son verdad de campo: sirven para probar que Tp9_03 arma el mapa. Criterios (grilla de la pila, 20 m):
  3 monte estable      WorldCover 2021 = 10 (cobertura arborea), |dNDVI| < 0,05 y NDVI 2026 >= 0,5
  4 no bosque estable  WorldCover 2021 = 30, 40 o 50 (pastizal, cultivo, construido) y |dNDVI| < 0,10
  1 perdida            WorldCover 2021 = 10, dNDVI <= -0,20 y NDVI 2026 < 0,45 (donde habia monte hoy hay poco verde)
  2 degradacion        WorldCover 2021 = 10, -0,20 < dNDVI <= -0,07 y NDVI 2026 >= 0,45 (sigue verde, pero menos)
Solo se toman centros cuyo entorno cumple entero el criterio: 5 x 5 pixeles (100 x 100 m) en las clases 3 y 4,
3 x 3 (60 x 60 m) en perdida y degradacion, que son pocas y en parches chicos. Cada poligono es el cuadrado de
3 x 3 pixeles (60 x 60 m) alrededor del centro, con al menos 600 m (300 m en perdida y degradacion) entre
poligonos de la misma clase.
dNDVI = O_NDVI_2026 - O_NDVI_2021 de la pila (C_pila_temporal_20m.tif, de Tp9_01).

Escribe Tp9_Deforestacion/04_Tablas_de_trabajo/entrenamiento_C_prueba_WorldCover.gpkg (capa "entrenamiento",
campos codigo, clase, criterio) y un resumen en pantalla.
"""
import glob
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
from configuracion_comun import ruta_tp, EPSG  # noqa: E402
from funciones_comunes import leer_tif  # noqa: E402

import geopandas as gpd  # noqa: E402
import rasterio  # noqa: E402
from rasterio.enums import Resampling  # noqa: E402
from rasterio.warp import reproject  # noqa: E402
from scipy.ndimage import minimum_filter  # noqa: E402
from shapely.geometry import box  # noqa: E402

WC_DIR = os.environ.get("WORLDCOVER_DIR", os.path.join(os.path.expanduser("~"), ".snap", "auxdata", "LandCover",
                                                       "ESA_WorldCover"))
MAX_POR_CLASE, DIST_MIN_M, SEMILLA = 40, 600.0, 2026
CLASES = {1: "perdida", 2: "degradacion", 3: "monte estable", 4: "no bosque estable"}

capas, perfil, _ = leer_tif(ruta_tp("Tp9", "02_Subsets_SNAP_QGIS", "C_pila_temporal_20m.tif"))
T, alto, ancho = perfil["transform"], perfil["height"], perfil["width"]
n21, n26 = capas["O_NDVI_2021"], capas["O_NDVI_2026"]
dndvi = n26 - n21

wc = np.zeros((alto, ancho), "uint8")
tiles = sorted(glob.glob(os.path.join(WC_DIR, "ESA_WorldCover_10m_2021_v200_*_Map.tif")))
for t in tiles:
    tmp = np.zeros((alto, ancho), "uint8")
    with rasterio.open(t) as src:
        reproject(rasterio.band(src, 1), tmp, dst_transform=T, dst_crs=perfil["crs"], resampling=Resampling.mode,
                  dst_nodata=0)
    wc = np.where(wc == 0, tmp, wc)
print("WorldCover 2021: %d teselas leidas; pixeles de la pila con clase: %.1f %%" % (len(tiles), 100 * (wc > 0).mean()))
for c, n in ((10, "arboles"), (20, "arbustal"), (30, "pastizal"), (40, "cultivo"), (50, "construido"), (80, "agua")):
    print("   WorldCover %d %-10s %5.1f %% de Federal" % (c, n, 100 * (wc == c).mean()))

ok = np.isfinite(dndvi)
reglas = {
    3: ok & (wc == 10) & (np.abs(dndvi) < 0.05) & (n26 >= 0.5),
    4: ok & np.isin(wc, (30, 40, 50)) & (np.abs(dndvi) < 0.10),
    1: ok & (wc == 10) & (dndvi <= -0.20) & (n26 < 0.45),
    2: ok & (wc == 10) & (dndvi > -0.20) & (dndvi <= -0.07) & (n26 >= 0.45),
}
crit = {3: "WC10, |dNDVI|<0,05, NDVI26>=0,5", 4: "WC30/40/50, |dNDVI|<0,10",
        1: "WC10, dNDVI<=-0,20, NDVI26<0,45", 2: "WC10, -0,20<dNDVI<=-0,07, NDVI26>=0,45"}
rng = np.random.default_rng(SEMILLA)
filas = []
px = abs(T.a)
for cod, m in reglas.items():
    lado, dist = (5, DIST_MIN_M) if cod in (3, 4) else (3, DIST_MIN_M / 2)
    puro = minimum_filter(m.astype("uint8"), size=lado, mode="constant", cval=0).astype(bool)
    f, c = np.nonzero(puro)
    orden = rng.permutation(len(f))
    elegidos = []
    for i in orden:
        x, y = T * (c[i] + 0.5, f[i] + 0.5)
        if all((x - a) ** 2 + (y - b) ** 2 >= dist ** 2 for a, b in elegidos):
            elegidos.append((x, y))
            filas.append({"codigo": cod, "clase": CLASES[cod], "criterio": crit[cod],
                          "geometry": box(x - 1.5 * px, y - 1.5 * px, x + 1.5 * px, y + 1.5 * px)})
        if len(elegidos) >= MAX_POR_CLASE:
            break
    print("Clase %d %-18s pixeles que cumplen %7d, centros puros %6d, poligonos %d"
          % (cod, CLASES[cod], m.sum(), len(f), len(elegidos)))

g = gpd.GeoDataFrame(filas, crs=perfil["crs"]).to_crs(EPSG)
sal = ruta_tp("Tp9", "04_Tablas_de_trabajo", "entrenamiento_C_prueba_WorldCover.gpkg")
if os.path.exists(sal):
    os.remove(sal)
g.to_file(sal, layer="entrenamiento", driver="GPKG", engine="pyogrio")
print("Escrito: %s (%d poligonos)" % (sal, len(g)))
