# -*- coding: utf-8 -*-
"""
Tp6_03_fusion_y_variantes.py   [SE CORRE]   Tp6, paso 3 de la guia - FUSION DE DECISION
===============================================================================
"Fusion de decisiones: agua C union agua L union agua optica, con reglas
escritas" (presentacion 01, diapositiva 29, paso 3).

Por que decision (y no pixel): optico, C y L llegan con nubes, fechas y pixeles
distintos; cada uno decide "agua / no agua" con su propia fisica, y se combinan
las decisiones. Las reglas, escritas:

  R1  agua de inundacion si C dice agua (agua abierta, cualquier cielo)
  R2  o si L dice doble rebote (agua bajo vegetacion), si hay banda L
  R3  o si el optico dice agua Y el pixel no tiene nube
  R4  nunca donde JRC marca agua permanente (ya aplicado en los pasos 1 y 2)
  R5  nunca donde ya habia agua en la fecha SECA de referencia (banda
      agua_en_referencia_seca de Tp6_01): lagunas estacionales, banados y
      arrozales con agua con el rio en nivel normal no son inundacion

Variantes para el Tp4 (codigos: 1 = agua de inundacion, 2 = no):
  B_variante_optico.tif       solo optico (las nubes quedan sin dato)
  B_variante_C.tif            solo C
  B_variante_CL.tif           C union L (si hay L)
  B_variante_multisensor.tif  R1 + R2 + R3

SALIDA  Tp6_Inundaciones/05_Resultados/02_Rasters/B_variante_*.tif
USO     python Tp6_03_fusion_y_variantes.py --pixel 20
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
from funciones_comunes import leer_tif, grilla_de_tif, guardar_tif, Bitacora  # noqa: E402
from funciones_cambio import fusion_decision                          # noqa: E402


def a_codigos(m):
    return np.where(np.isfinite(m), np.where(m == 1, 1, 2), np.nan).astype("float32")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pixel", type=int, default=20)
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp6", "05_Resultados", "06_Control_calidad"), "Tp6_03_fusion")
    ruta = ruta_tp("Tp6", "05_Resultados", "02_Rasters", "B_agua_por_sensor_%dm.tif" % a.pixel)
    m, _, tags = leer_tif(ruta)
    g = grilla_de_tif(ruta)
    f = tags.get("FUENTE", "")
    R = lambda n: ruta_tp("Tp6", "05_Resultados", "02_Rasters", n)      # noqa: E731
    seca = np.zeros((g["height"], g["width"]), bool)
    ext = R("B_extension_y_duracion_C_%dm.tif" % a.pixel)
    if os.path.exists(ext):
        e, _, _ = leer_tif(ext)
        if "agua_en_referencia_seca" in e:
            seca = e["agua_en_referencia_seca"] == 1
    if seca.any():
        log("R5: %.1f ha con agua en la fecha seca de referencia: no son inundacion en ninguna variante."
            % (seca.sum() * a.pixel ** 2 / 1e4))
        m = {k: np.where(seca & np.isfinite(v), 0, v).astype("float32") for k, v in m.items()}
    else:
        log("AVISO: sin la banda agua_en_referencia_seca de Tp6_01 (o sin escena seca): las variantes son AGUA")
        log("       TEMPORAL (incluyen lagunas estacionales y banados), no solo inundacion. Declararlo.")
    ha = lambda x: np.nansum(x == 1) * a.pixel ** 2 / 1e4                # noqa: E731
    if "Optico_MNDWI" in m:
        v = a_codigos(m["Optico_MNDWI"])
        guardar_tif(R("B_variante_optico.tif"), {"clase": v}, g, f, "Solo optico (MNDWI). 1 agua, 2 no")
        log("Optico solo      %10.1f ha de agua   (%.1f %% del sitio sin dato por nubes)" % (ha(v), 100 * np.isnan(v).mean()))
    v = a_codigos(m["C_Sentinel1_VV"])
    guardar_tif(R("B_variante_C.tif"), {"clase": v}, g, f, "Solo banda C (VV). 1 agua, 2 no")
    log("C solo           %10.1f ha" % ha(v))
    if "L_HH_doble_rebote" in m:
        u, _ = fusion_decision({"C": m["C_Sentinel1_VV"], "L": m["L_HH_doble_rebote"]}, "union")
        guardar_tif(R("B_variante_CL.tif"), {"clase": a_codigos(u)}, g, f, "C union L (doble rebote). 1 agua, 2 no")
        log("C union L        %10.1f ha" % ha(a_codigos(u)))
    u, votos = fusion_decision(m, "union")
    v = a_codigos(u)
    guardar_tif(R("B_variante_multisensor.tif"), {"clase": v, "sensores_que_votaron": votos.astype("float32")}, g, f,
                "Fusion de decision R1+R2+R3 (union de %s). 1 agua, 2 no" % ", ".join(m))
    log("Multisensor      %10.1f ha   (union de %s)" % (ha(v), ", ".join(m)))
    log("")
    log("La union maximiza la deteccion y tambien la comision: el Tp4 dira cuanto.")
    log.cerrar("Tp4_02/Tp4_03 por variante; despues python Tp6_04_profundidad.py --pixel %d" % a.pixel)


if __name__ == "__main__":
    main()
