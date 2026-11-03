# -*- coding: utf-8 -*-
"""
Tp10_03_expansion_urbana.py   [SE CORRE]   Tp10, paso 7 de la guía
=========================================================================
Producto del práctico: "mapa de expansión urbana" (diapositiva 33).

DETECCIÓN DE CAMBIOS POR COMPARACIÓN POSTERIOR A LA CLASIFICACIÓN (post-classification comparison)
  1. COMPUESTO DE TEMPORADA en cada año: Sentinel-1 RTC (media lineal de hasta 5 pasadas de la
     MISMA órbita relativa, porque el doble rebote depende de la dirección de mirada) y Sentinel-2
     L2A (mediana de los píxeles sin nube de hasta 5 escenas), en +/- --dias de cada fecha. Las dos
     fechas caen en la misma estación (primavera).
  2. CLASIFICACIÓN DE CADA AÑO con el mismo método: una fusión de rasgos Sentinel-1 + Sentinel-2
     (Random Forest con las mismas capas) y entrenamiento de MapBiomas del año correspondiente
     (píxeles estables, en proporción al paisaje).
  3. CAMBIO SÓLO SI ES CONFIABLE: un píxel cambia (clases 2 y 4) si en las dos fechas la clase
     ganadora tiene probabilidad >= --p_min, y si el cambio forma una mancha de al menos --umm
     píxeles conectados. Lo demás queda "sin decidir" (clase 5), a la vista.
  La regla de cambio no fusiona sensores: compara dos decisiones (una por fecha).
  ASIMETRÍA DE LA REGLA: la probabilidad mínima se exige sólo para declarar un cambio (clases 2 y
  4); las clases 1 y 3 (sin cambio) no la exigen. La matriz de transiciones (CSV) separa lo
  confiable de lo no confiable en las cuatro combinaciones urbano 2019 × urbano 2026.
  (El historial de versiones está en NOTAS_TECNICAS.md.)

Clases del mapa de expansión
  1 urbano en las dos fechas   2 NUEVO urbano (expansión)   3 no urbano en las dos fechas
  4 urbano en la base y no en la final (revisar)   5 sin decidir (probabilidad baja o mancha chica)

POR QUE 2019: la coleccion sentinel-2-l2a del Planetary Computer es homogenea desde 2019, y la
órbita 68 de Sentinel-1 RTC sobre Concordia empieza el 14/10/2019.

SALIDA
  05_Resultados/02_Rasters/<SITIO>_expansion_<base>_<final>.tif (clase, urbano_base, urbano_final,
  probabilidad_base, probabilidad_final), 04_Tablas/<SITIO>_expansion_superficies.csv y
  04_Tablas/<SITIO>_expansion_matriz_transiciones.csv (urbano 2019 × urbano 2026 × confiable)

USO
    python Tp10_03_expansion_urbana.py --sitio B_CONCORDIA
"""
import argparse
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import ruta_tp                               # noqa: E402
from funciones_comunes import (grilla_sitio, lin_a_db, guardar_tif, Bitacora, fuente_mpc,  # noqa: E402
                               s1_rtc_compuesto, s2_compuesto, entrenamiento_mapbiomas)
from funciones_cambio import indice_normalizado, fusion_pixel_o_rasgo, figura_mapa  # noqa: E402

CLASES = {1: "urbano en ambas fechas", 2: "nuevo urbano", 3: "no urbano", 4: "urbano solo en la base (revisar)",
          5: "sin decidir"}


def cv_local(x, ventana=5):
    from scipy import ndimage

    ok = np.isfinite(x)
    v = np.where(ok, x, 0.0).astype("float64")
    n = ndimage.uniform_filter(ok.astype("float64"), ventana)
    m = ndimage.uniform_filter(v, ventana) / np.where(n > 0, n, np.nan)
    m2 = ndimage.uniform_filter(v * v, ventana) / np.where(n > 0, n, np.nan)
    return np.where(ok & (n > 0.6), np.sqrt(np.maximum(m2 - m * m, 0)) / m, np.nan).astype("float32")


def clasificar(S, fecha, anio_mb, g, a, log, fuentes, orbita=None):
    f0 = np.datetime64(fecha)
    desde, hasta = str(f0 - a.dias), str(f0 + a.dias)
    s1, n1, f1, orb = s1_rtc_compuesto(S, desde, hasta, g, orbita=orbita)
    s2, n2, us = s2_compuesto(S, desde, hasta, g, excluir=a.excluir)
    if s1 is None or s2 is None or not f1:
        log("  %s: falta %s" % (fecha, "Sentinel-1" if s1 is None or not f1 else "Sentinel-2"))
        return None, None, orb
    capas = {"C_VV_dB": lin_a_db(s1["vv"]), "C_VH_dB": lin_a_db(s1["vh"]), "C_CV_VV": cv_local(s1["vv"])}
    capas.update(s2)
    capas["NDBI"] = indice_normalizado(s2["B11"], s2["B08"]).astype("float32")
    capas["NDVI"] = indice_normalizado(s2["B08"], s2["B04"]).astype("float32")
    capas["MNDWI"] = indice_normalizado(s2["B03"], s2["B11"]).astype("float32")
    rmb = ruta_tp("Tp10", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", "%s_MapBiomas_cobertura_1985_2025.tif" % S)
    y, filas = entrenamiento_mapbiomas(rmb, anio_mb, g, n_total=a.n_entrenamiento)
    mapa, prob, info = fusion_pixel_o_rasgo(capas, y, equilibrar=False)
    ha = g["pixel"] ** 2 / 1e4
    log("  %s: Sentinel-1 órbita %s, %d pasadas (%s a %s); Sentinel-2, %d escenas (%s a %s);"
        % (fecha, orb, len(f1), f1[0], f1[-1], len(us), us[0][0], us[-1][0]))
    log("     entrenamiento MapBiomas %d (estables %d-%d): %s" % (anio_mb, anio_mb - 2, anio_mb,
        ", ".join("%s %d" % (r["clase"], r["pixeles_de_entrenamiento"]) for r in filas)))
    log("     urbano %.0f ha; exactitud fuera de bolsa (OPTIMISTA) %.3f" % (np.sum(mapa == 1) * ha,
                                                                         info["exactitud_fuera_de_bolsa_OPTIMISTA"]))
    fuentes += [fuente_mpc("ESA - Copernicus", "Sentinel-1 IW GRD RTC, media lineal de %d pasadas, órbita %s" % (len(f1), orb),
                           "%s a %s" % (f1[0], f1[-1])),
                fuente_mpc("ESA - Copernicus", "Sentinel-2 MSI L2A, mediana de %d escenas" % len(us), "%s a %s" % (us[0][0], us[-1][0]))]
    return mapa, prob, orb


def main():
    from scipy import ndimage

    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", default="B_CONCORDIA", choices=["B_CONCORDIA", "E_PARANA_DIAMANTE"])
    ap.add_argument("--pixel", type=float, default=20.0, help="20 m: el píxel de la B11")
    ap.add_argument("--base", default="2019-11-01", help="centro de la ventana de la base (órbita 68 desde el 2019-10-14)")
    ap.add_argument("--final", default="2026-10-01")
    ap.add_argument("--dias", type=int, default=30, help="ventana de los compuestos: +/- días")
    ap.add_argument("--anio_mb_base", type=int, default=2019)
    ap.add_argument("--anio_mb_final", type=int, default=2025, help="el último año de MapBiomas")
    ap.add_argument("--p_min", type=float, default=0.6, help="probabilidad mínima de la clase ganadora en cada fecha")
    ap.add_argument("--umm", type=int, default=5, help="unidad mínima de mapeo del cambio, en píxeles conectados")
    ap.add_argument("--n_entrenamiento", type=int, default=20000)
    ap.add_argument("--aviso_clase4", type=float, default=0.2,
                    help="fracción de la clase 2 a partir de la cual la clase 4 dispara el aviso (la de la verificación)")
    ap.add_argument("--excluir", nargs="*", default=["2026-09-04"],
                    help="fechas de Sentinel-2 que no entran al compuesto (la imagen de referencia del Tp4)")
    a = ap.parse_args()
    S = a.sitio
    log = Bitacora(ruta_tp("Tp10", "05_Resultados", "06_Control_calidad"), "Tp10_03_%s" % S)
    g = grilla_sitio(S, pixel=a.pixel)
    fuentes = []
    log("Comparación posterior a la clasificación: Random Forest por año con compuestos de +/- %d días;"
        " cambio si p >= %.2f en las dos fechas y mancha >= %d píxeles" % (a.dias, a.p_min, a.umm))
    m1, p1, orb = clasificar(S, a.final, a.anio_mb_final, g, a, log, fuentes)
    m0, p0, _ = clasificar(S, a.base, a.anio_mb_base, g, a, log, fuentes, orbita=orb)
    if m0 is None or m1 is None:
        log.cerrar()
        return
    ok = np.isfinite(m0) & np.isfinite(m1)
    u0, u1 = (m0 == 1), (m1 == 1)
    seguro = ok & (p0 >= a.p_min) & (p1 >= a.p_min)
    exp = np.full(m0.shape, np.nan, "float32")
    exp[ok] = 5
    exp[ok & u0 & u1] = 1
    exp[ok & ~u0 & ~u1] = 3
    for c, m in ((2, seguro & ~u0 & u1), (4, seguro & u0 & ~u1)):
        lab, n = ndimage.label(m, structure=np.ones((3, 3)))
        if n:
            tam = ndimage.sum(m, lab, index=np.arange(1, n + 1))
            grande = np.isin(lab, np.flatnonzero(tam >= a.umm) + 1)
            exp[grande] = c
    ha = lambda c: float(np.sum(exp == c) * a.pixel ** 2 / 1e4)    # noqa: E731
    t = pd.DataFrame([{"clase": n, "codigo": c, "hectareas": round(ha(c), 1)} for c, n in CLASES.items()])
    log(t.to_string(index=False))
    anios = (np.datetime64(a.final) - np.datetime64(a.base)).astype(int) / 365.25
    base_u = ha(1) + ha(4)
    if base_u > 0:
        log("Crecimiento: %.1f ha nuevas sobre %.1f ha urbanas en la base = %.1f %% en %.1f años (%.2f %% anual)"
            % (ha(2), base_u, 100 * ha(2) / base_u, anios, 100 * ha(2) / base_u / anios))
    if ha(4) > a.aviso_clase4 * ha(2):
        log("AVISO: la clase 4 supera el %.0f %% de la clase 2 (%.1f %%): revisar esas manchas en la imagen y declararlo."
            % (100 * a.aviso_clase4, 100 * ha(4) / max(ha(2), 1e-9)))
    # matriz de transiciones: urbano en la base (sí/no) × urbano en la final (sí/no) × cambio confiable (sí/no)
    filas_m = []
    for b0, b1 in ((True, True), (True, False), (False, True), (False, False)):
        for conf in (True, False):
            m = ok & (u0 == b0) & (u1 == b1) & (seguro == conf)
            filas_m.append({"urbano_base": "sí" if b0 else "no", "urbano_final": "sí" if b1 else "no",
                            "confiable": "sí" if conf else "no", "hectareas": round(float(m.sum() * a.pixel ** 2 / 1e4), 1),
                            **{"clase_%d" % c: round(float((m & (exp == c)).sum() * a.pixel ** 2 / 1e4), 1) for c in CLASES}})
    tm = pd.DataFrame(filas_m)
    log("Matriz de transiciones (ha):")
    log(tm.to_string(index=False))
    log("Asimetría de la regla: p >= %.2f se exige sólo para el cambio (clases 2 y 4), no para las clases 1 y 3." % a.p_min)
    sufijo = "%s_%s" % (a.base[:4], a.final[:4])
    out = ruta_tp("Tp10", "05_Resultados", "02_Rasters", "%s_expansion_%s.tif" % (S, sufijo))
    fuente = " | ".join(fuentes) + " | Proyecto MapBiomas Argentina, Coleccion 3 (entrenamiento), https://argentina.mapbiomas.org"
    guardar_tif(out, {"clase": exp, "urbano_base": np.where(ok, u0, np.nan).astype("float32"),
                      "urbano_final": np.where(ok, u1, np.nan).astype("float32"),
                      "probabilidad_base": p0, "probabilidad_final": p1}, g, fuente,
                "Expansión urbana por comparación posterior a la clasificación (Random Forest por año, compuestos). " +
                "; ".join("%d %s" % kv for kv in CLASES.items()))
    tt = ruta_tp("Tp10", "05_Resultados", "04_Tablas", "%s_expansion_superficies.csv" % S)
    os.makedirs(os.path.dirname(tt), exist_ok=True)
    t.to_csv(tt, index=False, encoding="utf-8-sig")
    tm.to_csv(ruta_tp("Tp10", "05_Resultados", "04_Tablas", "%s_expansion_matriz_transiciones.csv" % S), index=False,
              encoding="utf-8-sig")
    figura_mapa(exp, ruta_tp("Tp10", "05_Resultados", "05_Graficos", "%s_expansion_%s.png" % (S, sufijo)),
                "%s - expansión urbana %s-%s" % (S, a.base[:4], a.final[:4]), fuente[:300],
                etiquetas=CLASES, cmap="tab10")
    log.cerrar("python Tp10_04_pares_sbas.py (subsidencia en E_PARANA_DIAMANTE)")


if __name__ == "__main__":
    main()
