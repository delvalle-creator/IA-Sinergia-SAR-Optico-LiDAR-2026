# -*- coding: utf-8 -*-
"""
Tp1_08_contexto_del_sitio.py   [SE CORRE]   paso 9 del Tp1   (agregado el 21/10/2026)
==========================================================================================
El contexto de biomasa y de uso del suelo del sitio con los productos que el practico ya trae en
02_Subsets_SNAP_QGIS\\QGIS_GeoTIFF: MapBiomas Argentina (cobertura anual 1985-2025, perdida de
vegetacion 1987-2025 y area quemada 1999-2025), ESA CCI Biomass v7 (biomasa aerea 2020 y 2024) y
BIOMASS en banda P (gamma0 HH y VH del L1B y altura del bosque del L2A FH).

No es parte de la matriz de convergencia del paso 7: MapBiomas y el CCI resumen anios, no fechas, y el
BIOMASS es de 2026. Sirven para ubicar el evento en la historia del sitio. El calculo lo hace
00_COMUN/contexto_del_sitio.py, el mismo que usan los otros practicos.

SALIDA
  Tp1_Convergencia/05_Resultados/04_Tablas/<SITIO>_mapbiomas_area_por_clase_y_anio.csv
  Tp1_Convergencia/05_Resultados/04_Tablas/<SITIO>_mapbiomas_perdida_por_anio.csv
  Tp1_Convergencia/05_Resultados/04_Tablas/<SITIO>_mapbiomas_fuego_por_anio.csv
  Tp1_Convergencia/05_Resultados/04_Tablas/<SITIO>_contexto_por_clase.csv
  Tp1_Convergencia/05_Resultados/04_Tablas/<SITIO>_contexto_pixeles_muestra.csv
  Tp1_Convergencia/05_Resultados/05_Graficos/<SITIO>_mapbiomas_area_por_clase.png
  Tp1_Convergencia/05_Resultados/05_Graficos/<SITIO>_mapbiomas_perdida_y_fuego_por_anio.png
  Tp1_Convergencia/05_Resultados/06_Control_calidad/Tp1_08_<SITIO>.log

USO
    python Tp1_08_contexto_del_sitio.py --sitio B_CONCORDIA
"""
import argparse
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

from configuracion_comun import SITIOS, ruta_tp                       # noqa: E402
import contexto_del_sitio                                             # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", default="B_CONCORDIA", choices=list(SITIOS.keys()))
    a = ap.parse_args()
    R = lambda *p: ruta_tp("Tp1", "05_Resultados", *p)              # noqa: E731
    for c in ("04_Tablas", "05_Graficos", "06_Control_calidad"):
        os.makedirs(R(c), exist_ok=True)
    contexto_del_sitio.correr(a.sitio, ruta_tp("Tp1", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF"),
                              R("04_Tablas"), R("05_Graficos"), R("06_Control_calidad"), "Tp1_08_%s" % a.sitio,
                              siguiente="QGIS (grupo Contexto del sitio) y Orange (08_Orange/Tp1_F_contexto_del_sitio.ows)")


if __name__ == "__main__":
    main()
