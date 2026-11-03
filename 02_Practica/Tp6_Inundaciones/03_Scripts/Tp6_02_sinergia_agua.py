# -*- coding: utf-8 -*-
"""
Tp6_02_sinergia_agua.py   [SE CORRE]   Tp6, paso 2 de la guia - SINERGIA
===============================================================
Cada sensor dice DONDE ve agua el dia del evento (o lo mas cerca posible), y
se comparan SIN fusionar:

  C  Sentinel-1 VV (de Tp6_01, misma fecha que el optico)  agua abierta
  O  Sentinel-2 MNDWI = (B03 - B11)/(B03 + B11) > umbral     agua abierta con cielo despejado
  L  HH de banda L (SAOCOM; --l_evento y --l_referencia)
     aumento de HH >= 3 dB respecto de la referencia seca     agua BAJO la vegetacion (doble rebote)
     Con --l_relativo el aumento se mide respecto de una mediana: si llovio entre las dos
     fechas, TODO el sitio sube (suelo mojado) y un umbral fijo marca la mitad del sitio.
     --l_base elige que mediana se resta: "sitio" (todo el sitio sin agua permanente, la de antes)
     o "clase" (la del monte y las plantaciones FUERA del agua de C y del optico). Con "sitio" se
     resta un cambio dominado por pastos y cultivos (+3,8 y +4,1 dB) y el umbral EFECTIVO en las
     lenosas sube a unos 6 dB; con "clase" se compara cada arbol con los de su propia clase. Con
     --l_solo_lenoso la regla se aplica solo en el monte y las plantaciones de MapBiomas (clases 3,
     4, 6 y 9), que es donde puede haber doble rebote tronco-agua.
  S  NovaSAR-1 HH (13/09/2023, ANTES de la crecida). Este programa NO la lee:
     es dos meses anterior al evento y no puede votar sobre el agua del
     4/11/2023. Se mira en QGIS, como referencia del cauce en banda S, y se
     declara.

Que se aprende de la tabla de acuerdo
  - C y optico deberian coincidir en agua abierta donde no hay nubes.
  - El aumento de HH en L marca agua bajo monte o plantacion (diedro
    tronco-agua) que ni C ni el optico ven: es la complementariedad
    (sinergia), no un error de C. En el pajonal la HH suele BAJAR: el agua
    que tapa el pasto vuelve la superficie un espejo.
  - Donde el optico tiene nubes, no vota: se cuenta aparte.

SALIDA
  Tp6_Inundaciones/05_Resultados/02_Rasters/B_agua_por_sensor_<pixel>m.tif
  Tp6_Inundaciones/05_Resultados/04_Tablas/B_sinergia_agua.csv

USO
    python Tp6_02_sinergia_agua.py --pixel 20 --fecha 2023-11-04
    python Tp6_02_sinergia_agua.py --pixel 20 --fecha 2023-11-04 ^
        --l_evento ..\\02_Subsets_SNAP_QGIS\\SAOCOM_gamma0\\QGIS_GeoTIFF\\B_CONCORDIA_SAOCOM_L_20231111_QP_gamma0_Gamma0_HH.tif ^
        --l_referencia ..\\02_Subsets_SNAP_QGIS\\SAOCOM_gamma0\\QGIS_GeoTIFF\\B_CONCORDIA_SAOCOM_L_20231010_QP_gamma0_Gamma0_HH.tif ^
        --l_relativo --l_solo_lenoso --l_base clase
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
from funciones_comunes import (leer_tif, grilla_de_tif, buscar_stac, fecha_item,  # noqa: E402
                               s2_reflectancia, s2_mascara_valida, leer_en_grilla,
                               jrc_ocurrencia, guardar_tif, Bitacora, fuente_mpc)
from funciones_cambio import (indice_normalizado, cociente_db, umbral_documentado,  # noqa: E402
                              aplicar_umbral, tabla_de_coincidencias)

# ------------------------------------------------------------------ PARAMETROS
SITIO = "B_CONCORDIA"
CLASES_LENOSAS = [3, 4, 6, 9]       # MapBiomas: bosque cerrado, abierto, inundable y silvicultura


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pixel", type=int, default=20)
    ap.add_argument("--fecha", default="2023-11-04")
    ap.add_argument("--u_mndwi", type=float, default=0.0)
    ap.add_argument("--l_evento", default="")
    ap.add_argument("--l_referencia", default="")
    ap.add_argument("--u_doble_rebote", type=float, default=3.0, help="aumento de HH en dB")
    ap.add_argument("--l_relativo", action="store_true", help="aumento respecto de la mediana del sitio")
    ap.add_argument("--l_solo_lenoso", action="store_true", help="solo monte y plantaciones (MapBiomas 3, 4, 6, 9)")
    ap.add_argument("--l_base", choices=["sitio", "clase"], default="sitio",
                    help="con --l_relativo: mediana que se resta (sitio = todo el sitio; clase = lenosas fuera del agua)")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp6", "05_Resultados", "06_Control_calidad"), "Tp6_02_sinergia")
    serie = ruta_tp("Tp6", "02_Subsets_SNAP_QGIS", "B_agua_C_por_fecha_%dm.tif" % a.pixel)
    capas_c, _, tags = leer_tif(serie)
    g = grilla_de_tif(serie)
    clave = "agua_%s" % a.fecha.replace("-", "")
    if clave not in capas_c:
        sys.exit("La serie C no tiene la fecha %s. Fechas: %s" % (a.fecha, ", ".join(k[5:] for k in capas_c)))
    mapas = {"C_Sentinel1_VV": capas_c[clave]}
    fuentes = [tags.get("FUENTE", "")]
    perm, _ = jrc_ocurrencia(SITIO, g)
    perm = perm >= 90

    its = buscar_stac("sentinel-2-l2a", SITIO, a.fecha, a.fecha)
    if its:
        b3 = b11 = None
        validez = None
        for it in its:
            v, _, nub = s2_mascara_valida(it, g)
            x3, x11 = s2_reflectancia(it, "B03", g), s2_reflectancia(it, "B11", g)
            b3 = np.where(v, x3, np.nan) if b3 is None else np.where(np.isnan(b3) & v, x3, b3)
            b11 = np.where(v, x11, np.nan) if b11 is None else np.where(np.isnan(b11) & v, x11, b11)
            log("Sentinel-2 %s: nubes en el sitio %.1f %%" % (it.id[:40], nub))
        mndwi = indice_normalizado(b3, b11)
        u, txt = umbral_documentado(mndwi, "MNDWI %s" % a.fecha,
                                    ruta_tp("Tp6", "05_Resultados", "05_Graficos", "B_histograma_MNDWI.png"),
                                    metodo="manual", manual=a.u_mndwi, signo=">")
        m = aplicar_umbral(mndwi, u, ">")
        mapas["Optico_MNDWI"] = np.where(perm, 0, m).astype("float32")
        f, h = fecha_item(its[0])
        fuentes.append(fuente_mpc("ESA - Copernicus", "Sentinel-2 MSI L2A, MNDWI = (B03-B11)/(B03+B11)", f, h))
        log("Optico: %s" % txt)
    else:
        log("No hay Sentinel-2 el %s: la sinergia queda sin optico (declararlo)." % a.fecha)

    if a.l_evento and a.l_referencia:
        ev = leer_en_grilla(a.l_evento, g, "average")
        rf = leer_en_grilla(a.l_referencia, g, "average")
        dhh = cociente_db(rf, ev)
        med = float(np.nanmedian(np.where(perm, np.nan, dhh)))
        log("Banda L: aumento mediano de HH en el sitio entre las dos fechas: %+.2f dB" % med)
        cob = None
        if a.l_solo_lenoso or a.l_base == "clase":
            mb = ruta_tp("Tp6", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", "B_CONCORDIA_MapBiomas_cobertura_1985_2025.tif")
            if not os.path.exists(mb):
                mb = ruta_tp("Tp10", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", "B_CONCORDIA_MapBiomas_cobertura_1985_2025.tif")
            cob = leer_en_grilla(mb, g, "mode", banda=39)
        if a.l_relativo:
            base = med
            if a.l_base == "clase":
                agua_otros = np.zeros(perm.shape, bool)
                for k in mapas:
                    agua_otros |= (mapas[k] == 1)
                base = float(np.nanmedian(np.where(np.isin(cob, CLASES_LENOSAS) & ~perm & ~agua_otros, dhh, np.nan)))
                log("         mediana del monte y las plantaciones fuera del agua de C y del optico: %+.2f dB" % base)
            dhh = dhh - base
            log("         (--l_relativo, base %s: se resta %+.2f dB; umbral efectivo %.2f dB de aumento)"
                % (a.l_base, base, a.u_doble_rebote + base))
        m = aplicar_umbral(dhh, a.u_doble_rebote, ">")
        if a.l_solo_lenoso:
            m = np.where(np.isin(cob, CLASES_LENOSAS), m, np.where(np.isfinite(m), 0, np.nan))
            log("         (--l_solo_lenoso: solo monte y plantaciones de MapBiomas 2023)")
        mapas["L_HH_doble_rebote"] = np.where(perm, 0, m).astype("float32")
        fuentes.append("Banda L HH procesada en SNAP: %s (evento) y %s (referencia)" % (a.l_evento, a.l_referencia))
        log("Banda L: aumento de HH >= %.1f dB en %.1f %% del sitio (agua bajo vegetacion)"
            % (a.u_doble_rebote, 100 * np.nanmean(m)))
    else:
        log("Sin banda L: el agua bajo vegetacion NO se evalua. Los SAOCOM de CONAE del 10/10 y el 11/11/2023")
        log("estan en 02_Subsets_SNAP_QGIS\\SAOCOM_gamma0 (--l_evento y --l_referencia).")

    if len(mapas) < 2:
        log("Solo hay un sensor: no hay sinergia que medir.")
        log.cerrar()
        return
    tabla, suma = tabla_de_coincidencias(mapas)
    log.titulo("Acuerdo entre sensores el %s (sin fusionar)" % a.fecha)
    log(tabla.to_string(index=False))
    out = ruta_tp("Tp6", "05_Resultados", "04_Tablas", "B_sinergia_agua.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tabla.to_csv(out, index=False, encoding="utf-8-sig")
    guardar_tif(ruta_tp("Tp6", "05_Resultados", "02_Rasters", "B_agua_por_sensor_%dm.tif" % a.pixel),
                mapas, g, " | ".join(fuentes), "Agua (1) de cada sensor, sin agua permanente (JRC >= 90 %)")
    log.cerrar("python Tp6_03_fusion_y_variantes.py --pixel %d" % a.pixel)


if __name__ == "__main__":
    main()
