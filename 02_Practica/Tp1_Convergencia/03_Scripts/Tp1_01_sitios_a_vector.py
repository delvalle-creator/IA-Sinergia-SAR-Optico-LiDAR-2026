# -*- coding: utf-8 -*-
"""
Tp1_01_sitios_a_vector.py   [SE CORRE]   paso 1 del Tp1
======================================================
Convierte los sitios de la matriz de convergencia (A a F, mas A1, A2, E1 y DELTA_NISAR) (definidos UNA vez en
00_COMUN/configuracion_comun.py) en archivos vectoriales:

  00_COMUN/01_AOI/sitios_curso.gpkg        capa "sitios" (EPSG:4326) y capa
                                           "sitios_utm21s" (EPSG:32721)
  00_COMUN/01_AOI/<SITIO>.geojson          un archivo por sitio, para subir a
                                           los buscadores web (Copernicus
                                           Browser, ASF Vertex, Earthdata
                                           Search, catalogo de CONAE, ESA MAAP)

y muestra la grilla de 10 m de cada sitio: columnas, filas y superficie.

POR QUE ESTE PASO VA PRIMERO
----------------------------
Toda busqueda en un catalogo empieza por un poligono. Si cada grupo dibuja el
suyo a mano, cada uno trabaja sobre un sitio distinto y los resultados no se
pueden comparar. Aqui sale el poligono oficial del curso.

Los sitios marcados "aproximada" se revisan en QGIS sobre la imagen del
evento (paso 1 de la guia del Tp1). Si se corrigen, se corrigen en
configuracion_comun.py y se vuelve a correr este script: nunca se edita el
.geojson a mano.

USO (Miniforge Prompt, entorno sar):
    python Tp1_01_sitios_a_vector.py
"""
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import geopandas as gpd                                          # noqa: E402
from shapely.geometry import box                                 # noqa: E402

from configuracion_comun import SITIOS, AOI_DIR, EPSG, ruta_tp    # noqa: E402
from funciones_comunes import grilla_sitio, Bitacora              # noqa: E402


def main():
    log = Bitacora(ruta_tp("Tp1", "05_Resultados", "06_Control_calidad"), "Tp1_01_sitios")
    os.makedirs(AOI_DIR, exist_ok=True)
    filas = []
    log.titulo("Sitios del curso y su grilla de 10 m (EPSG:%d)" % EPSG)
    for clave, s in SITIOS.items():
        g = grilla_sitio(clave)
        km2 = g["width"] * g["height"] * g["pixel"] ** 2 / 1e6   # m2 -> km2
        filas.append({"sitio": clave, "nombre": s["nombre"], "origen": s["origen"],
                      "practicos": ",".join(s["practicos"]),
                      "columnas": g["width"], "filas": g["height"],
                      "superficie_km2": round(km2, 1), "geometry": box(*s["bbox"])})
        aviso = "   <-- REVISAR en el Tp1, paso 1" if s["origen"] == "aproximada" else ""
        log("%-18s %5d x %5d px  %7.1f km2  origen=%s%s"
            % (clave, g["width"], g["height"], km2, s["origen"], aviso))

    gdf = gpd.GeoDataFrame(filas, crs=4326)
    ruta = os.path.join(AOI_DIR, "sitios_curso.gpkg")
    gdf.to_file(ruta, layer="sitios", driver="GPKG")
    gdf.to_crs(EPSG).to_file(ruta, layer="sitios_utm21s", driver="GPKG")
    for _, f in gdf.iterrows():
        gpd.GeoDataFrame([f], crs=4326).to_file(
            os.path.join(AOI_DIR, f["sitio"] + ".geojson"), driver="GeoJSON")
    log("")
    log("Escrito:", ruta, "(capas sitios y sitios_utm21s)")
    log("Escritos %d archivos .geojson en %s" % (len(gdf), AOI_DIR))
    log.cerrar("python Tp1_02_inventario_local.py")


if __name__ == "__main__":
    main()
