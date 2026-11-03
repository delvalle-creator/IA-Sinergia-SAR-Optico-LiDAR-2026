# -*- coding: utf-8 -*-
"""
Tp10_01_doble_rebote_sinergia.py   [SE CORRE]   Tp10, paso 2 de la guía - SINERGIA
==========================================================================
Pregunta del práctico: como crece la ciudad y donde se hunde el terreno.
Sitios: B_CONCORDIA (por defecto) y E_PARANA_DIAMANTE (--sitio).

"Sinergia: doble rebote en C, S y L; comparar el detalle a 6, 10 y 20 m"
(presentación 01, diapositiva 33, paso 1).

QUE SE HACE
  1. Se lee cada banda por separado en la grilla del sitio:
       C  Sentinel-1 RTC VV y VH, la fecha más cercana a --fecha (2026-09-16)
       S  NovaSAR-1 GRD HH, escena 47942 del 13/09/2023 (cubre el 39 % de
          B_CONCORDIA; no cubre Parana)
       L  NISAR GCOV HH y HV del 18/09/2026 (--nisar_h5; bajado con Tp1_04)
  2. Cada banda produce SU mapa de "retrodispersion urbana" (doble rebote:
     pared + calle forman un diedro que devuelve la señal a la antena) con un
     umbral en dB documentado con su histograma.
  3. SINERGIA: tabla de coincidencias entre los tres mapas, sin fusionarlos,
     separada por clase de la cobertura de control si existe (Tp4_01).
  4. DETALLE: el mapa en banda S se repite a 6, 10 y 20 m y se cuentan
     manchas urbanas y relación perimetro/area: cuánto detalle se pierde.
     Antes del umbral se iguala el número de vistas (media en lineal 3 x 3 a 6 m,
     2 x 2 a 10 m, nada a 20 m, que ya promedia ~11 píxeles de 6 m) y se descartan las
     manchas de menos de --umm_m2 (por defecto 1.200 m², tres píxeles de 20 m) en las tres
     escalas: sin eso, a 6 m el speckle fabrica manchas sueltas y el "detalle" que se mide es
     ruido. Con 400 m² (un píxel de 20 m, el valor de la versión anterior) a 20 m no se
     descartaba nada y a 6 m sí, y por eso salían más manchas a 20 m que a 6 m.

POR QUE LOS UMBRALES SON MANUALES POR DEFECTO
  Otsu necesita un histograma con dos modas; la ciudad ocupa pocos píxeles
  del sitio y su moda casi no se ve. Los valores por defecto son un punto de
  partida (C VV > -3 dB, S HH > -3 dB, L HH > -3 dB) que el grupo CONFIRMA
  con el histograma y con los polígonos urbanos del control, y anota.

ADVERTENCIAS QUE VAN A LA BITÁCORA
  - El doble rebote depende de la orientación de las calles respecto de la
    dirección de vuelo: una manzana girada 45 grados puede verse oscura.
  - Las tres bandas NO difieren solo en longitud de onda: C esta en VV (en el
    diedro pared-calle el VV se atenúa por el efecto Brewster; el HH no) y S y
    L en HH; y las pasadas son distintas (Sentinel-1 descendente ~09:13 UTC,
    NISAR descendente ~21:59 UTC, NovaSAR ~01:36 UTC, con distinta dirección de
    mirada respecto de las calles). Una diferencia entre bandas puede ser de
    polarización o de geometría, no de longitud de onda.
  - NovaSAR es de 2023 y C y L de 2026: tres años de diferencia. Lo que
    aparece solo en C y L puede ser crecimiento real.
  - El image_HH.tif de NovaSAR trae sólo 4 puntos de esquina; el metadata.xml trae 84 puntos de
    enlace, que el programa usa por defecto (--puntos_enlace todos). El corrimiento que queda se
    mide con Tp3_02 y se pasa con --desplazamiento DX DY: es lo que hay que MOVER la imagen
    (DX positivo = este, DY positivo = norte).

SALIDA
  Tp10_Impacto_urbano/02_Subsets_SNAP_QGIS/<SITIO>_urbano_por_banda_<pixel>m.tif
  Tp10_Impacto_urbano/05_Resultados/04_Tablas/<SITIO>_coincidencias_urbano.csv
  Tp10_Impacto_urbano/05_Resultados/04_Tablas/<SITIO>_detalle_6_10_20m.csv
  Tp10_Impacto_urbano/05_Resultados/05_Graficos/<SITIO>_hist_*.png

USO
    python Tp10_01_doble_rebote_sinergia.py --nisar_h5 ..\\..\\00_COMUN\\08_Originales_crudos\\NISAR\\NISAR_L2_PR_GCOV_031_010_D_104_2005_DHDH_A_20260918T215921_20260918T215955_P05023_F_F_J_001.h5
    python Tp10_01_doble_rebote_sinergia.py --sitio E_PARANA_DIAMANTE
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
from funciones_comunes import (grilla_sitio, s1_rtc_mas_cercana, fecha_item, s1_rtc,  # noqa: E402
                               novasar_sigma0, nisar_gcov_en_grilla, leer_en_grilla,
                               lin_a_db, guardar_tif, Bitacora, fuente_mpc)
from funciones_cambio import umbral_documentado, aplicar_umbral, tabla_de_coincidencias  # noqa: E402

CONTROL = {1: "agua_permanente", 2: "humedal_pajonal", 3: "monte_nativo", 4: "plantacion_forestal",
           5: "cultivo_pastura", 6: "suelo_desnudo", 7: "urbano", 8: "otra"}


def filtro_speckle_lineal(x, ventana=3):
    """Media movil de ventana x ventana en LINEAL (multivista simple): baja el speckle antes del
    umbral. Los píxeles sin dato no entran en la media."""
    from scipy import ndimage

    ok = np.isfinite(x)
    suma = ndimage.uniform_filter(np.where(ok, x, 0.0).astype("float64"), ventana)
    n = ndimage.uniform_filter(ok.astype("float64"), ventana)
    return np.where(ok & (n > 0), suma / np.where(n > 0, n, 1), np.nan).astype("float32")


def manchas(binario, pixel, area_min_m2=1200.0):
    """Número de manchas urbanas, área media y perimetro/area del mapa binario.
    Se descartan las manchas de menos de area_min_m2 (1.200 m² = tres píxeles de 20 m): así el filtro
    actúa en las tres escalas, se comparan con el mismo tamaño mínimo y un píxel suelto de speckle no
    cuenta como manzana."""
    from scipy import ndimage

    b = np.nan_to_num(binario, nan=0) > 0.5
    etiquetas, n = ndimage.label(b)
    if n:
        tam = ndimage.sum(b, etiquetas, index=np.arange(1, n + 1)) * pixel ** 2
        chicas = np.isin(etiquetas, np.nonzero(tam < area_min_m2)[0] + 1)
        b = b & ~chicas
        etiquetas, n = ndimage.label(b)
    area = b.sum() * pixel ** 2
    borde = b & ~ndimage.binary_erosion(b)
    perimetro = borde.sum() * pixel
    return {"pixel_m": pixel, "superficie_urbana_ha": round(area / 1e4, 1), "manchas": int(n),
            "area_media_ha": round(area / 1e4 / max(n, 1), 2),
            "perimetro_sobre_area_1_km": round(perimetro / area * 1000, 2) if area else np.nan}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", default="B_CONCORDIA", choices=["B_CONCORDIA", "E_PARANA_DIAMANTE"])
    ap.add_argument("--pixel", type=float, default=20.0, help="grilla común para la tabla de coincidencias")
    ap.add_argument("--fecha", default="2026-09-16")
    ap.add_argument("--nisar_h5", default="")
    ap.add_argument("--novasar", default="47942")
    ap.add_argument("--desplazamiento", type=float, nargs=2, default=(0.0, 0.0), metavar=("DX", "DY"))
    ap.add_argument("--puntos_enlace", choices=("esquinas", "todos"), default="todos",
                    help="georreferencia de NovaSAR: esquinas (4 GCP del image_HH.tif) o todos (puntos de enlace del metadata.xml)")
    ap.add_argument("--u_c", type=float, default=-3.0)
    ap.add_argument("--u_s", type=float, default=-3.0)
    ap.add_argument("--u_l", type=float, default=-3.0)
    ap.add_argument("--otsu", action="store_true", help="usar Otsu en lugar de los umbrales manuales")
    ap.add_argument("--umm_m2", type=float, default=1200.0,
                    help="unidad mínima de las manchas del detalle, en m² (1.200 = tres píxeles de 20 m)")
    a = ap.parse_args()
    S = a.sitio
    log = Bitacora(ruta_tp("Tp10", "05_Resultados", "06_Control_calidad"), "Tp10_01_%s" % S)
    g = grilla_sitio(S, pixel=a.pixel)
    capas, mapas, fuentes = {}, {}, []
    G = lambda n: ruta_tp("Tp10", "05_Resultados", "05_Graficos", "%s_hist_%s.png" % (S, n))  # noqa: E731

    def mapa_urbano(nombre, lineal, u_manual):
        db = lin_a_db(lineal)
        u, txt = umbral_documentado(db, nombre + " (dB)", G(nombre), metodo="otsu" if a.otsu else "manual",
                                    manual=u_manual, signo=">")
        log("  %-14s %s" % (nombre, txt))
        return aplicar_umbral(db, u, ">"), u

    log.titulo("Banda C - Sentinel-1")
    try:
        it = s1_rtc_mas_cercana(S, a.fecha, grilla=g)     # la pasada más cercana que cubra el sitio
        if it is not None:
            f, h = fecha_item(it)
            for p in ("vv", "vh"):
                capas["C_%s" % p.upper()] = s1_rtc(it, p, g)
            mapas["C_VV"], _ = mapa_urbano("C_VV", capas["C_VV"], a.u_c)
            fuentes.append(fuente_mpc("ESA - Copernicus", "Sentinel-1 IW GRD RTC", f, h))
            log("  escena del %s %s UTC" % (f, h))
        else:
            log("  Sin Sentinel-1 RTC +/- 6 días de %s" % a.fecha)
    except Exception as e:                           # noqa: BLE001
        log("  No se pudo consultar el Planetary Computer: %s" % str(e)[:120])

    log.titulo("Banda S - NovaSAR-1")
    detalle = []
    try:
        s0, k = novasar_sigma0(a.novasar, g, desplazamiento_m=tuple(a.desplazamiento), puntos_enlace=a.puntos_enlace)
        if np.isfinite(s0).mean() < 0.01:
            raise ValueError("la escena %s no cubre %s" % (a.novasar, S))
        capas["S_HH"] = s0
        mapas["S_HH"], u_s = mapa_urbano("S_HH", s0, a.u_s)
        fuentes.append("SSTL - CSIRO. NovaSAR-1 Stripmap GRD HH, escena %s, sigma0 = DN^2/%.0e. Archivo del curso"
                       % (a.novasar, k))
        log("  %.1f %% del sitio con dato" % (100 * np.isfinite(s0).mean()))
        log("  Georreferencia: %s." % ("4 puntos de esquina del image_HH.tif" if a.puntos_enlace == "esquinas"
                                        else "puntos de enlace del metadata.xml"))
        if list(a.desplazamiento) == [0.0, 0.0]:
            log("  AVISO: sin corrección de georreferencia (--desplazamiento): a 6 m un error de 80 m son 13 píxeles.")
        log.titulo("Detalle: el mismo mapa en banda S a 6, 10 y 20 m")
        log("  Antes del umbral, el mismo número de vistas en las tres escalas (unas 10, como el píxel de 20 m")
        log("  con el que se fijo el umbral): media movil en lineal de 3 x 3 a 6 m y de 2 x 2 a 10 m; a 20 m")
        log("  ninguna (el remuestreo ya promedia unos 11 píxeles de 6 m). Después se descartan las manchas")
        log("  de menos de %.0f m² en las tres escalas." % a.umm_m2)
        ventana_por_pixel = {6.0: 3, 10.0: 2, 20.0: 1}
        for px in (6.0, 10.0, 20.0):
            gp = grilla_sitio(S, pixel=px)
            x, _ = novasar_sigma0(a.novasar, gp, desplazamiento_m=tuple(a.desplazamiento), puntos_enlace=a.puntos_enlace)
            v = ventana_por_pixel[px]
            d = manchas(aplicar_umbral(lin_a_db(filtro_speckle_lineal(x, v) if v > 1 else x), u_s, ">"), px, a.umm_m2)
            detalle.append(d)
            log("  %4.0f m: %9.1f ha urbanas en %6d manchas; perímetro/área %.2f 1/km"
                % (px, d["superficie_urbana_ha"], d["manchas"], d["perimetro_sobre_area_1_km"]))
            del x
    except Exception as e:                           # noqa: BLE001
        log("  NovaSAR: %s" % str(e)[:160])

    log.titulo("Banda L - NISAR")
    if a.nisar_h5:
        try:
            for t, p in (("HHHH", "HH"), ("HVHV", "HV")):
                capas["L_%s" % p] = nisar_gcov_en_grilla(a.nisar_h5, g, t, "LSAR")
            mapas["L_HH"], _ = mapa_urbano("L_HH", capas["L_HH"], a.u_l)
            fuentes.append("NASA - ISRO. NISAR L2 GCOV %s. ASF DAAC: https://search.asf.alaska.edu"
                           % os.path.basename(a.nisar_h5))
        except Exception as e:                       # noqa: BLE001
            log("  NISAR: %s" % str(e)[:160])
    else:
        log("  Sin --nisar_h5: la banda L no entra. Bajar el GCOV del 18/09/2026 con Tp1_04_buscar_asf.py.")

    if len(mapas) < 2:
        log("Hace falta al menos dos bandas para la sinergia.")
        log.cerrar()
        return
    log.titulo("SINERGIA: coincidencias entre bandas (sin fusionar)")
    cc = ruta_tp("Tp4", "02_Subsets_SNAP_QGIS", "%s_cobertura_control_%dm.tif" % (S, a.pixel))
    ctrl = leer_en_grilla(cc, g, "mode", banda=1) if os.path.exists(cc) else None
    t, suma = tabla_de_coincidencias(mapas, ctrl, CONTROL)
    log("La tabla usa SOLO los píxeles con dato en todas las bandas (%d): si entra NovaSAR, es su huella."
        % int(np.isfinite(suma).sum()))
    log(t[t.region.isin(["todo el sitio", "control: urbano"])].to_string(index=False))
    T = lambda n: ruta_tp("Tp10", "05_Resultados", "04_Tablas", n)     # noqa: E731
    os.makedirs(os.path.dirname(T("x")), exist_ok=True)
    t.to_csv(T("%s_coincidencias_urbano.csv" % S), index=False, encoding="utf-8-sig")
    if detalle:
        pd.DataFrame(detalle).to_csv(T("%s_detalle_6_10_20m.csv" % S), index=False, encoding="utf-8-sig")
    capas.update({"mapa_" + k: v for k, v in mapas.items()})
    capas["bandas_que_marcan_urbano"] = suma
    guardar_tif(ruta_tp("Tp10", "02_Subsets_SNAP_QGIS", "%s_urbano_por_banda_%dm.tif" % (S, a.pixel)),
                capas, g, " | ".join(fuentes), "gamma0/sigma0 lineal por banda y mapa urbano por banda (umbral en dB)",
                unidades={"S_HH": "sigma0 lineal (NovaSAR)", "bandas_que_marcan_urbano": "sin unidad (conteo de bandas)"})
    log("")
    log("Para leer la tabla: '%_solo_1' alto en C frente a L suele ser vegetación densa o techos")
    log("metalicos; '%_solo_2' alto en L, edificacion entre arboles (L atraviesa el follaje).")
    log.cerrar("python Tp10_02_fusion_pixel_urbano.py --sitio %s --pixel %d" % (S, a.pixel))


if __name__ == "__main__":
    main()
