# -*- coding: utf-8 -*-
"""Poligonos de PRUEBA de la capa de entrenamiento del Tp9 (Federal) hechos sobre la imagen de alta resolucion
CBERS-4A WPM fusionada a 2 m (02/08/2021 y 05/09/2026), con sorteo al azar y revision visual (22/10/2026).
Reemplazan a los de ESA WorldCover 2021 (poligonos_prueba_worldcover_Tp9.py), que salian de un mapa de 10 m.

No son verdad de campo: sirven para probar que Tp9_03 arma el mapa y como borrador que el grupo corrige.

1) Mascara de copas a 2 m (una por fecha): un pixel es copa si el brillo visible suavizado (media de azul, verde
   y rojo, filtro gaussiano de 0,7 px) es menor que su percentil 22 en la imagen y el NDVI >= 0,30. Se escribe en
   Tp9_Deforestacion/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/C_FEDERAL_copa_CBERS4A_2m_<fecha>.tif (1 copa, 0 no, 255 sin
   dato) si no existe. Su fraccion en cada pixel de 20 m de la pila (C_pila_temporal_20m.tif) es la que se uso para
   estratificar.
2) Sorteo: 100 puntos uniformes en la parte de la pila cubierta por las dos imagenes CBERS (semilla 20261022). Cada
   punto se miro en fichas de 300 m de 2021 y 2026 con el cuadrado de 60 m al centro y se etiqueto a ojo:
     3 monte estable      copas en ~20 % o mas del cuadro en las dos fechas, sin cambio visible
     4 no bosque estable  sin copas (< ~5 %) en las dos fechas: pastura, cultivo, campo o construido
     2 degradacion        monte en las dos fechas con una picada o apertura nueva visible en 2026
     1 perdida            monte en 2021 y suelo desnudo en 2026
     0 descartado         mezcla, arbustal ralo (5 a 20 % de copas), borde, rebrote o cambio dudoso
   Resultado: 32 monte, 10 no bosque, 1 degradacion, 0 perdida y 57 descartados.
3) Completado estratificado (semilla 20261023, a mas de 300 m de los puntos ya usados): 14 puntos del estrato de
   monte (fraccion de copa >= 0,35 en las dos fechas, sin cambio) y 30 del de no bosque (< 0,03 en las dos), con la
   misma revision a ojo: 6 y 16 aceptados.
4) Cambios: se buscaron aperturas nuevas comparando el brillo de 2026 (> percentil 99,5) con el de 2021 (< percentil
   90) a 2 m, en lugares con copas alrededor en 2021. La mayoria eran caminos que ya estaban (mas claros en 2026) o
   cauces secos. Confirmados a ojo: 2 picadas nuevas en el monte (degradacion) y 2 desmontes (perdida): un claro
   junto a un puesto y un camino nuevo de unos 25 m de ancho. Los contornos de perdida salen de esa mascara de 2 m
   (perdida_CBERS_2m.gpkg); los demas poligonos son cuadrados de 60 m (3 x 3 pixeles de la pila).
   Entre 2021 y 2026, dentro de la ventana CBERS (16 x 16 km del centro de Federal), casi no hubo desmonte: por eso
   hay tan pocos poligonos de perdida y degradacion. El grupo agrega los suyos (ver la guia del Tp9).

Entradas: desarrollo_docente/sorteos/Tp9/Tp9_puntos_revisados_CBERS.csv (todos los puntos mirados, con su clase a
ojo) y perdida_CBERS_2m.gpkg. Escribe Tp9_Deforestacion/04_Tablas_de_trabajo/entrenamiento_C_prueba_CBERS.gpkg (capa
"entrenamiento", campos codigo, clase, criterio, origen).
"""
import csv
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
from configuracion_comun import ruta_tp, EPSG  # noqa: E402

import geopandas as gpd  # noqa: E402
import rasterio  # noqa: E402
from shapely.geometry import box  # noqa: E402

SORTEO = os.path.join(AQUI, "desarrollo_docente", "sorteos", "Tp9")
CLASES = {1: "perdida", 2: "degradacion", 3: "monte estable", 4: "no bosque estable"}
CRIT = {3: "copas >= ~20 % del cuadro en 2021 y 2026, sin cambio visible (CBERS-4A 2 m)",
        4: "sin copas (< ~5 %) en 2021 y 2026: pastura, cultivo, campo o construido (CBERS-4A 2 m)",
        2: "monte en 2021 y 2026 con picada o apertura nueva visible en 2026 (CBERS-4A 2 m)"}
ORIGEN = {"sorteo_100": "sorteo al azar, punto %s de 100", "estrato_monte": "completado estratificado (estrato monte), %s",
          "estrato_no_bosque": "completado estratificado (estrato no bosque), %s",
          "apertura_nueva": "busqueda de aperturas nuevas 2021-2026 (%s), confirmada a ojo"}


def mascara_copas(fecha):
    from scipy.ndimage import gaussian_filter
    dst = ruta_tp("Tp9", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", "C_FEDERAL_copa_CBERS4A_2m_%s.tif" % fecha)
    if os.path.exists(dst):
        print("Ya existe:", dst)
        return
    src = ruta_tp("Tp9", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", "C_FEDERAL_CBERS4A_FEDERAL_%s_pansharpened_2m.tif" % fecha)
    with rasterio.open(src) as s:
        b, g, r, nir = [s.read(i).astype("float32") for i in (2, 3, 4, 5)]
        perfil = dict(driver="GTiff", width=s.width, height=s.height, count=1, dtype="uint8", crs=s.crs,
                      transform=s.transform, nodata=255, compress="deflate")
    val = b > 0
    vis = gaussian_filter((b + g + r) / 3, 0.7)
    ndvi = (nir - r) / np.maximum(nir + r, 1)
    u = np.percentile(vis[val], 22)
    c = (vis < u) & (ndvi >= 0.30) & val
    with rasterio.open(dst, "w", **perfil) as o:
        o.write(np.where(val, c.astype("uint8"), 255).astype("uint8"), 1)
        o.set_band_description(1, "copa (1) segun CBERS-4A 2 m: visible < p22 y NDVI >= 0,30")
    print("Mascara de copas %s: umbral %.1f, copa %.1f %%. Escrita: %s" % (fecha, u, 100 * c.sum() / val.sum(), dst))


def main():
    for f in ("20210802", "20260905"):
        mascara_copas(f)
    with rasterio.open(ruta_tp("Tp9", "02_Subsets_SNAP_QGIS", "C_pila_temporal_20m.tif")) as s:
        T, crs = s.transform, s.crs
    filas = []
    with open(os.path.join(SORTEO, "Tp9_puntos_revisados_CBERS.csv"), encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter=";"):
            cod = int(r["codigo"])
            if cod == 0:
                continue
            c, f_ = ~T * (float(r["x_utm21s"]), float(r["y_utm21s"]))
            x, y = T * (int(c) + 0.5, int(f_) + 0.5)
            filas.append({"codigo": cod, "clase": CLASES[cod], "criterio": CRIT[cod],
                          "origen": ORIGEN[r["tanda"]] % r["id"], "geometry": box(x - 30, y - 30, x + 30, y + 30)})
    p = gpd.read_file(os.path.join(SORTEO, "perdida_CBERS_2m.gpkg"), layer="perdida").to_crs(crs)
    for _, r in p.iterrows():
        filas.append({"codigo": 1, "clase": CLASES[1], "criterio": r["descripcion"] +
                      " (contorno de la mascara de cambio a 2 m, CBERS-4A)",
                      "origen": "busqueda de aperturas nuevas 2021-2026, confirmada a ojo", "geometry": r.geometry})
    g = gpd.GeoDataFrame(filas, crs=crs).to_crs(EPSG)
    g["codigo"] = g["codigo"].astype("int64")
    sal = ruta_tp("Tp9", "04_Tablas_de_trabajo", "entrenamiento_C_prueba_CBERS.gpkg")
    if os.path.exists(sal):
        os.remove(sal)
    g.to_file(sal, layer="entrenamiento", driver="GPKG", engine="pyogrio")
    for k, n in CLASES.items():
        print("Clase %d %-18s %3d poligonos" % (k, n, (g["codigo"] == k).sum()))
    print("Escrito: %s (%d poligonos)" % (sal, len(g)))


if __name__ == "__main__":
    main()
