# -*- coding: utf-8 -*-
"""
Tp5_02_sinergia.py   [SE CORRE]   Tp5, paso 2 de la guia - SINERGIA (sin fusionar)
=========================================================================
Cada sensor produce SU mapa de quema con SU umbral, y se los compara. No se
genera un mapa unico: eso es la fusion (Tp5_03). Aqui se responde la pregunta
de la sinergia (presentacion 01, diapositiva 28, pasos 1 y 2):

  - comparar la caída de VH (C), la de HV (L) y el dNBR;
  - evaluar, con los datos del sitio, si el pajonal y el albardón responden
    como predice la física de la dispersión, y explicar las discrepancias.

Para la segunda pregunta hace falta saber dónde hay pajonal y dónde albardón.
Se usa la cobertura de control del Tp4 (Tp4_01) si tiene esas clases. En
A1_DELTA_QUEMAS sólo tiene agua: entonces se separa por estrato de estructura
del CCI Biomass 2020 (pajonal < 15 Mg/ha; albardón >= 30 Mg/ha), en QGIS o en
Orange (08_Orange/Tp5_A), como explica la guía en el paso 2.

Umbrales: Otsu por defecto, con el histograma guardado para justificarlo.
Se pueden fijar a mano y se declara; los valores de partida del práctico son
--u_dvh 1 --u_dhv -2 --u_dhv_saocom 1 --u_dnbr 0.15.
El dNBR de 0,27 es el limite de "severidad moderada-baja" de Key y Benson
(2006), definido para bosques templados: en humedales se CALIBRA con la
referencia, no se adopta.

Control del practico: las lagunas y el agua permanente NO se clasifican
como quema (en el radar el agua calma es oscura y en el optico se confunde
con la ceniza). Se enmascaran con la clase 1 de la cobertura de control.

SALIDA
  Tp5_Incendios/05_Resultados/02_Rasters/A1_quema_por_sensor_<pixel>m.tif   (una banda por sensor, 1/0)
  Tp5_Incendios/05_Resultados/02_Rasters/A1_sensores_que_coinciden_<pixel>m.tif
  Tp5_Incendios/05_Resultados/04_Tablas/A1_sinergia_coincidencias.csv
  Tp5_Incendios/05_Resultados/05_Graficos/histograma_<indicador>.png

USO
    python Tp5_02_sinergia.py --pixel 20
"""
import argparse
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402

from configuracion_comun import ruta_tp                               # noqa: E402
from funciones_comunes import leer_tif, grilla_de_tif, leer_en_grilla, guardar_tif, Bitacora  # noqa: E402
from funciones_cambio import (umbral_documentado, aplicar_umbral,     # noqa: E402
                              tabla_de_coincidencias, figura_mapa)

SITIO = "A1_DELTA_QUEMAS"
INDICADORES = {   # capa: (nombre del sensor, signo de la quema, argumento de umbral manual)
    "dVH_C_dB": ("C_Sentinel1_dVH", "<", "u_dvh"),
    "dHV_L_ALOS2_dB": ("L_ALOS2_dHV", "<", "u_dhv"),
    "dHV_SAOCOM_dB": ("L_SAOCOM_dHV", "<", "u_dhv_saocom"),
    "dNBR": ("Optico_dNBR", ">", "u_dnbr"),
}
TITULOS = {  # títulos en castellano de los histogramas
    "dVH_C_dB": "ΔVH banda C (Sentinel-1), dB",
    "dHV_L_ALOS2_dB": "ΔHV banda L (ALOS-2), dB",
    "dHV_SAOCOM_dB": "ΔHV banda L (SAOCOM-1A), dB",
    "dNBR": "dNBR (Sentinel-2), sin unidad",
}
CONTROL = {1: "agua_permanente", 2: "humedal_pajonal", 3: "monte_nativo", 4: "plantacion_forestal",
           5: "cultivo_pastura", 6: "suelo_desnudo", 7: "urbano", 8: "otra"}


def main():
    ap = argparse.ArgumentParser(description="Sinergia: un mapa de quema por sensor y la tabla de coincidencias.")
    ap.add_argument("--pixel", type=int, default=20)
    for _, (_, _, arg) in INDICADORES.items():
        ap.add_argument("--" + arg, type=float, default=None)
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp5", "05_Resultados", "06_Control_calidad"), "Tp5_02_sinergia")
    ind_ruta = ruta_tp("Tp5", "02_Subsets_SNAP_QGIS", "%s_indicadores_%dm.tif" % (SITIO, a.pixel))
    ind, _, tags = leer_tif(ind_ruta)
    g = grilla_de_tif(ind_ruta)

    control = None
    cc = ruta_tp("Tp4", "02_Subsets_SNAP_QGIS", "%s_cobertura_control_%dm.tif" % (SITIO, a.pixel))
    if os.path.exists(cc):
        control = leer_en_grilla(cc, g, "nearest", banda=1)
        control = np.where(np.isfinite(control), control, 0).astype("int32")
        log("Cobertura de control: %s" % cc)
    else:
        log("No hay cobertura de control para %s (Tp4_01): la tabla no se separa por clase y" % SITIO)
        log("el agua permanente NO se enmascara. Declárelo en el informe o corra antes Tp4_01.")

    mapas = {}
    for capa, (sensor, signo, arg) in INDICADORES.items():
        if capa not in ind:
            continue
        manual = getattr(a, arg)
        u, txt = umbral_documentado(ind[capa], TITULOS.get(capa, capa),
                                    ruta_tp("Tp5", "05_Resultados", "05_Graficos", "histograma_%s.png" % capa),
                                    metodo="manual" if manual is not None else "otsu", manual=manual, signo=signo,
                                    etiqueta_y="píxeles", nota_extremos=True, coma_decimal=True)
        m = aplicar_umbral(ind[capa], u, signo)
        if control is not None:
            m = np.where(control == 1, 0, m).astype("float32")       # el agua no se quema
        mapas[sensor] = m
        log("%-18s %s" % (sensor, txt))
    if len(mapas) < 2:
        log("Hace falta al menos dos sensores para la sinergia.")
        log.cerrar()
        return

    tabla, suma = tabla_de_coincidencias(mapas, control, CONTROL)
    log.titulo("Acuerdo entre sensores (sin fusionar)")
    log(tabla.to_string(index=False))
    out = ruta_tp("Tp5", "05_Resultados", "04_Tablas", "A1_sinergia_coincidencias.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tabla.to_csv(out, index=False, encoding="utf-8-sig")
    fuente = tags.get("FUENTE", "")
    guardar_tif(ruta_tp("Tp5", "05_Resultados", "02_Rasters", "A1_quema_por_sensor_%dm.tif" % a.pixel),
                mapas, g, fuente, "Mapa de quema de CADA sensor con su umbral (1 = quemado)")
    guardar_tif(ruta_tp("Tp5", "05_Resultados", "02_Rasters", "A1_sensores_que_coinciden_%dm.tif" % a.pixel),
                {"n_sensores_quema": suma}, g, fuente, "Cuantos sensores marcan quema en cada pixel")
    figura_mapa(suma, ruta_tp("Tp5", "05_Resultados", "05_Graficos", "A1_sensores_que_coinciden.png"),
                "Cantidad de sensores que marcan quema (0 a %d)" % len(mapas),
                "Elaboracion propia con %s" % ", ".join(mapas), cmap="magma")
    log("")
    clases = set(np.unique(control)) - {0} if control is not None else set()
    if clases and clases <= {1}:
        log("La cobertura de control sólo tiene la clase 1 (agua): no hay filas de pajonal ni de monte.")
        log("Sin clases de pajonal y monte: separe por estrato del CCI Biomass 2020 (pajonal < 15 Mg/ha,")
        log("albardón >= 30 Mg/ha), como indica la guía en el paso 2 (QGIS o Orange, Tp5_A).")
    else:
        log("Compare las filas por clase de control: qué sensor marca quema en cada cobertura, y si eso")
        log("coincide o no con lo que predice la física de cada banda. Si no coincide, explíquelo.")
    log.cerrar("python Tp5_03_fusion.py --pixel %d" % a.pixel)


if __name__ == "__main__":
    main()
