# -*- coding: utf-8 -*-
"""
Tp5_01_indicadores.py   [SE CORRE]   Tp5, paso 1 de la guia - Incendios
===============================================================
Pregunta del practico: donde se quemo y con que severidad, aun bajo humo.
Sitio: A1_DELTA_QUEMAS (islas del Delta, quemas de julio a octubre de 2020).

Calcula en la grilla comun los INDICADORES de cada sensor por separado, antes
de cualquier sinergia o fusion:

  Banda C  Sentinel-1   dVH_C, dVV_C = 10 log10(post/pre)     caida = perdida de volumen herbaceo
  Banda L  ALOS-2       dHV_L, dHH_L (mosaicos anuales)        caida = perdida de volumen lenoso
  Banda L  SAOCOM-1A    dHV_SAOCOM (si se procesaron en SNAP)  idem, con fecha precisa
  Óptico   Sentinel-2   NBR_pre, NBR_post, dNBR, RdNBR         severidad (Key y Benson; Miller y Thode)
           NBR = (B08 - B12)/(B08 + B12) por defecto. B8A (865 nm, 20 m) es el infrarrojo cercano
           equivalente al de Landsat con el que se definió el NBR; con --nbr_nir B8A se usa esa banda.
           En la grilla de 20 m las dos dan el mismo mapa de quema en el 96 % de los píxeles (dNBR > 0,15,
           medido el 27/10/2026), por eso se conserva B08, que es la que dio las cifras del curso.

Fuentes y fechas (todas reales):
  Sentinel-1 RTC: Planetary Computer (por fecha). En el archivo del curso estan
     ademas los SLC del 10/07 al 26/09/2020 para procesarlos en SNAP (Tp2).
  ALOS-2: mosaicos anuales JAXA del Planetary Computer (2019 = antes; 2020 =
     después). El mosaico 2020 está también en ORIGINALES_2023\\BURNED AREAS.
     ATENCIÓN: un mosaico anual combina pasadas de varios meses del año; la
     fecha de cada píxel está en su banda "date" (días desde el 24/05/2014,
     convención de JAXA). El script la lee y escribe en la bitácora el rango de
     fechas de la pasada de cada año dentro del sitio. Con --alos2_desde
     AAAA-MM-DD se dejan sin dato los píxeles cuya pasada del año "después" es
     anterior a esa fecha (no pueden ver el fuego).
  SAOCOM-1A: StripMap QP del 21/07/2020 (antes) y 25/10/2020 (después), del
     archivo del curso, llevados a gamma0 con 00_COMUN/procesar_saocom.py:
     Calibration a sigma0, Multilook, Refined Lee y Terrain-Correction en SNAP;
     gamma0 = sigma0 / cos(ángulo de incidencia sobre el elipsoide). SIN
     Terrain-Flattening (con SAOCOM da entre 5 y 10 dB menos que ALOS-2).
  Sentinel-2: Planetary Computer; despues = 13/10/2020 (presentacion 02).

SALIDA
  Tp5_Incendios/02_Subsets_SNAP_QGIS/A1_DELTA_QUEMAS_indicadores_<pixel>m.tif
  Tp5_Incendios/02_Subsets_SNAP_QGIS/A1_DELTA_QUEMAS_indicadores_fuentes.csv

USO
    python Tp5_01_indicadores.py --pixel 20 --c_pre 2020-07-16 --c_post 2020-09-26 ^
        --opt_pre 2020-07-15 --opt_post 2020-10-13 --alos2_pre 2019 --alos2_post 2020 ^
        --saocom_pre_hv ..\\02_Subsets_SNAP_QGIS\\SAOCOM_gamma0\\QGIS_GeoTIFF\\A1_DELTA_QUEMAS_SAOCOM_L_20200721_QP_gamma0_Gamma0_HV.tif ^
        --saocom_post_hv ..\\02_Subsets_SNAP_QGIS\\SAOCOM_gamma0\\QGIS_GeoTIFF\\A1_DELTA_QUEMAS_SAOCOM_L_20201025_QP_gamma0_Gamma0_HV.tif
(Las fechas ópticas exactas salen del Tp1_03 para este sitio: si el 15/07 hubiera
 tenido nubes, se usaría la candidata más cercana y se anotaría.)

OPCIONES AGREGADAS EL 27/10/2026 (con los valores por defecto el resultado es el de antes)
  --c_pre_extra / --c_post_extra   otras fechas Sentinel-1 de la MISMA órbita relativa,
        separadas por comas (p. ej. 2020-07-10 y 2020-10-08): se promedian en LINEAL con
        la fecha principal antes de calcular el cambio. Baja el speckle y hace el ruido
        de la banda C más comparable con el de SAOCOM (Refined Lee). Se declara.
  --nbr_nir B08|B8A    banda del infrarrojo cercano del NBR (por defecto B08).
  --alos2_desde        ver ALOS-2 arriba.
En la bitácora quedan, además, el porcentaje de píxeles sin RdNBR (|NBR previo| < 0,05).
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
from funciones_comunes import (grilla_sitio, buscar_stac, fecha_item, s1_rtc, agrupar_por_pasada,  # noqa: E402
                               alos2_mosaico, s2_reflectancia, s2_mascara_valida,
                               leer_en_grilla, guardar_tif, Bitacora, fuente_mpc)
from funciones_cambio import cociente_db, nbr, rdnbr                  # noqa: E402

# ---------------------------------------------------------------- PARÁMETROS
SITIO = "A1_DELTA_QUEMAS"
NBR_NIR = "B08"            # infrarrojo cercano del NBR: "B08" (842 nm) o "B8A" (865 nm, el equivalente de Landsat)
NBR_MIN_RDNBR = 0.05       # donde |NBR previo| < este valor el RdNBR queda sin dato (funciones_cambio.rdnbr)
ALOS2_ORIGEN_FECHA = "2014-05-24"   # la banda "date" del mosaico JAXA cuenta días desde esta fecha


def s1_promedio(fechas, g, log, orbita):
    """Promedio en LINEAL de varias fechas Sentinel-1 de la misma órbita (VV y VH). Devuelve (vv, vh, cita)."""
    vvs, vhs, citas = [], [], []
    for f in fechas:
        vv, vh, ci = s1_dia(f, g, log, orbita=orbita)
        if vv is not None:
            vvs.append(vv)
            vhs.append(vh)
            citas.append(ci)
    if not vvs:
        return None, None, ""
    log("  Promedio en lineal de %d fechas Sentinel-1 de la órbita %s: %s" % (len(vvs), orbita, ", ".join(fechas)))
    return (np.nanmean(np.stack(vvs), 0).astype("float32"), np.nanmean(np.stack(vhs), 0).astype("float32"),
            " + ".join(citas))


def s1_dia(fecha, g, log, orbita=None):
    its = buscar_stac("sentinel-1-rtc", SITIO, fecha, fecha)
    if orbita is not None:
        its = [it for it in its if it.properties.get("sat:relative_orbit") == orbita]
    if not its:
        log("  Sentinel-1 RTC: no hay escena el %s sobre el sitio%s. Elija otra fecha de la planilla del Tp1_03."
            % (fecha, "" if orbita is None else " en la órbita %s" % orbita))
        return None, None, ""
    pasadas = agrupar_por_pasada(its)
    if len(pasadas) > 1:
        log("  Sentinel-1 RTC del %s: %d pasadas distintas; se usa la primera (órbita %s)."
            % (fecha, len(pasadas), pasadas[0].properties.get("sat:relative_orbit", "")))
    it = pasadas[0]                      # todos los cuadros de esa pasada, unidos
    f, h = fecha_item(it)
    return s1_rtc(it, "vv", g), s1_rtc(it, "vh", g), fuente_mpc(
        "ESA - Copernicus", "Sentinel-1 IW GRD RTC (gamma0), orbita %s" % it.properties.get("sat:relative_orbit", ""), f, h)


def s2_dia(fecha, g, log, nir=NBR_NIR):
    its = buscar_stac("sentinel-2-l2a", SITIO, fecha, fecha)
    if not its:
        log("  Sentinel-2: no hay escena el %s." % fecha)
        return None, ""
    b08 = b12 = None
    for it in its:
        v, _, nub = s2_mascara_valida(it, g)
        x8, x12 = s2_reflectancia(it, nir, g), s2_reflectancia(it, "B12", g)
        b08 = np.where(v, x8, np.nan) if b08 is None else np.where(np.isnan(b08) & v, x8, b08)
        b12 = np.where(v, x12, np.nan) if b12 is None else np.where(np.isnan(b12) & v, x12, b12)
        log("  Sentinel-2 %s %s: nubes en el sitio %.1f %%" % (fecha, it.id[:40], nub))
    f, h = fecha_item(its[0])
    return nbr(b08, b12), fuente_mpc("ESA - Copernicus", "Sentinel-2 MSI L2A", f, h,
                                     "NBR = (%s - B12)/(%s + B12)." % (nir, nir))


def alos_fechas(it, g, log, anio):
    """Lee la banda 'date' del mosaico (días desde ALOS2_ORIGEN_FECHA) en la grilla y escribe el rango en la bitácora."""
    import datetime as dt
    if "date" not in it.assets:
        log("  ALOS-2 %s: el mosaico no trae banda 'date'." % anio)
        return None
    d = leer_en_grilla(it.assets["date"].href, g, "nearest", nodata_origen=1)
    d[(d <= 1) | ~np.isfinite(d)] = np.nan
    if np.isfinite(d).any():
        o = dt.date.fromisoformat(ALOS2_ORIGEN_FECHA)
        p5, p50, p95 = np.nanpercentile(d, [5, 50, 95])
        log("  ALOS-2 %s: fecha de la pasada en el sitio, percentil 5, mediana y 95: %s, %s, %s"
            % (anio, o + dt.timedelta(days=int(p5)), o + dt.timedelta(days=int(p50)), o + dt.timedelta(days=int(p95))))
    return d


def alos_anio(anio, g, log):
    its = buscar_stac("alos-palsar-mosaic", SITIO, "%s-01-01" % anio, "%s-12-31" % anio)
    if not its:
        log("  ALOS-2: el Planetary Computer no devolvio mosaico %s." % anio)
        return None, None, ""
    hh = hv = fe = None
    for it in its:
        a, b = alos2_mosaico(it, "HH", g), alos2_mosaico(it, "HV", g)
        hh = a if hh is None else np.where(np.isnan(hh), a, hh)
        hv = b if hv is None else np.where(np.isnan(hv), b, hv)
        try:
            d = alos_fechas(it, g, log, anio)
        except Exception as e:                     # la banda date es opcional: si falla, se sigue y se dice
            log("  ALOS-2 %s: no se pudo leer la banda 'date' (%s)." % (anio, e))
            d = None
        if d is not None:
            fe = d if fe is None else np.where(np.isnan(fe), d, fe)
    alos_anio.fechas = fe
    return hh, hv, fuente_mpc("JAXA", "ALOS-2 PALSAR-2 mosaico anual 25 m (gamma0 = 10 log10(DN^2) - 83 dB)",
                              str(anio))


def main():
    ap = argparse.ArgumentParser(description="Indicadores de cambio por sensor en la grilla del sitio.")
    ap.add_argument("--pixel", type=float, default=20.0)
    ap.add_argument("--c_pre_extra", default="", help="otras fechas S1 'antes' de la misma órbita, separadas por comas")
    ap.add_argument("--c_post_extra", default="", help="otras fechas S1 'después' de la misma órbita")
    ap.add_argument("--nbr_nir", default=NBR_NIR, choices=["B8A", "B08"])
    ap.add_argument("--alos2_desde", default="", help="AAAA-MM-DD: sin dato donde la pasada ALOS-2 'después' es anterior")
    ap.add_argument("--c_pre", default="2020-07-16")
    ap.add_argument("--c_post", default="2020-09-26")
    ap.add_argument("--opt_pre", default="")
    ap.add_argument("--opt_post", default="2020-10-13")
    ap.add_argument("--alos2_pre", default="2019")
    ap.add_argument("--alos2_post", default="2020")
    ap.add_argument("--saocom_pre_hv", default="")
    ap.add_argument("--saocom_post_hv", default="")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp5", "05_Resultados", "06_Control_calidad"), "Tp5_01_indicadores")
    g = grilla_sitio(SITIO, pixel=a.pixel)
    log("Sitio %s, píxel %.0f m (%d x %d)" % (SITIO, a.pixel, g["width"], g["height"]))
    if a.alos2_pre and a.pixel < 25:
        log("AVISO: el mosaico ALOS-2 es de 25 m y la grilla de %.0f m: los indicadores de banda L"
            " tienen MENOS detalle que el píxel. Declararlo al interpretar (diapositiva 14)." % a.pixel)
    capas, fuentes = {}, []

    log.titulo("Banda C: Sentinel-1 %s -> %s" % (a.c_pre, a.c_post))
    vv0, vh0, f0 = s1_dia(a.c_pre, g, log)
    orb = None
    if f0:
        import re as _re
        m = _re.search(r"orbita (\d+)", f0)
        orb = int(m.group(1)) if m else None
    # la fecha posterior tiene que ser de la MISMA orbita relativa: si no, el cociente mide geometria
    vv1, vh1, f1 = s1_dia(a.c_post, g, log, orbita=orb)
    if orb is not None:
        log("  Pre y post de la misma órbita relativa (%d)." % orb)
    if a.c_pre_extra and vv0 is not None:
        vv0, vh0, f0 = s1_promedio([a.c_pre] + a.c_pre_extra.split(","), g, log, orb)
    if a.c_post_extra and vv1 is not None:
        vv1, vh1, f1 = s1_promedio([a.c_post] + a.c_post_extra.split(","), g, log, orb)
    if vv0 is not None and vv1 is not None:
        capas["dVH_C_dB"] = cociente_db(vh0, vh1)
        capas["dVV_C_dB"] = cociente_db(vv0, vv1)
        fuentes += [("dVH_C_dB / dVV_C_dB", f0 + " | " + f1)]
        log("  dVH mediana %.2f dB, dVV mediana %.2f dB" % (np.nanmedian(capas["dVH_C_dB"]), np.nanmedian(capas["dVV_C_dB"])))

    if a.alos2_pre and a.alos2_post:
        log.titulo("Banda L: ALOS-2 mosaicos %s -> %s" % (a.alos2_pre, a.alos2_post))
        hh0, hv0, fa = alos_anio(a.alos2_pre, g, log)
        hh1, hv1, fb = alos_anio(a.alos2_post, g, log)
        fechas_post = getattr(alos_anio, "fechas", None)
        if a.alos2_desde and fechas_post is not None and hh1 is not None:
            import datetime as dt
            lim = (dt.date.fromisoformat(a.alos2_desde) - dt.date.fromisoformat(ALOS2_ORIGEN_FECHA)).days
            antes = fechas_post < lim
            log("  --alos2_desde %s: %.1f %% del sitio tiene la pasada %s anterior a esa fecha; queda sin dato."
                % (a.alos2_desde, 100 * np.nanmean(antes), a.alos2_post))
            hh1 = np.where(antes, np.nan, hh1)
            hv1 = np.where(antes, np.nan, hv1)
        if hh0 is not None and hh1 is not None:
            capas["dHV_L_ALOS2_dB"] = cociente_db(hv0, hv1)
            capas["dHH_L_ALOS2_dB"] = cociente_db(hh0, hh1)
            fuentes += [("dHV_L_ALOS2_dB / dHH_L_ALOS2_dB", fa + " | " + fb)]
            log("  dHV mediana %.2f dB" % np.nanmedian(capas["dHV_L_ALOS2_dB"]))
            log("  AVISO: cada píxel del mosaico anual ALOS-2 es de una pasada distinta (rango de fechas arriba).")
            log("         Donde la pasada de %s es anterior a las quemas, dHV no puede ver el fuego. Declararlo." % a.alos2_post)

    if a.saocom_pre_hv and a.saocom_post_hv:
        log.titulo("Banda L: SAOCOM-1A (procesado en SNAP)")
        s0 = leer_en_grilla(a.saocom_pre_hv, g, "average")
        s1 = leer_en_grilla(a.saocom_post_hv, g, "average")
        capas["dHV_SAOCOM_dB"] = cociente_db(s0, s1)
        fuentes += [("dHV_SAOCOM_dB", "CONAE. SAOCOM-1A StripMap QP 21/07/2020 y 25/10/2020, gamma0 HV "
                     "procesado en SNAP (00_COMUN/procesar_saocom.py). Archivo del curso SAR CEREGEO 2023.")]
        log("  dHV SAOCOM mediana %.2f dB" % np.nanmedian(capas["dHV_SAOCOM_dB"]))

    if a.opt_pre and a.opt_post:
        log.titulo("Óptico: Sentinel-2 %s -> %s (NBR con %s)" % (a.opt_pre, a.opt_post, a.nbr_nir))
        n0, fo0 = s2_dia(a.opt_pre, g, log, a.nbr_nir)
        n1, fo1 = s2_dia(a.opt_post, g, log, a.nbr_nir)
        if n0 is not None and n1 is not None:
            capas["NBR_pre"], capas["NBR_post"] = n0, n1
            capas["dNBR"] = (n0 - n1).astype("float32")
            capas["RdNBR"] = rdnbr(n0, n1, nbr_min=NBR_MIN_RDNBR)
            fuentes += [("NBR_pre, NBR_post, dNBR, RdNBR", fo0 + " | " + fo1)]
            log("  dNBR mediana %.3f; píxeles con dNBR > 0,27: %.1f %%"
                % (np.nanmedian(capas["dNBR"]), 100 * np.nanmean(capas["dNBR"] > 0.27)))
            con_dnbr = np.isfinite(capas["dNBR"])
            sin_rd = con_dnbr & ~np.isfinite(capas["RdNBR"])
            log("  NBR previo mediana %.3f; píxeles con dNBR pero SIN RdNBR (|NBR previo| < %.2f): %.1f %%"
                % (np.nanmedian(n0), NBR_MIN_RDNBR, 100 * sin_rd.sum() / max(con_dnbr.sum(), 1)))
            log("  Esos píxeles quedan fuera de la V4 (Tp5_03 exige todas las capas). Ver --sin_rdnbr en Tp5_03.")
    elif not a.opt_pre:
        log("Sin --opt_pre no se calcula el dNBR: falta la fecha óptica previa (búsquela con Tp1_03).")

    if not capas:
        log("No se calculó ningún indicador: revise la conexión a internet y las fechas.")
        log.cerrar()
        return
    out = ruta_tp("Tp5", "02_Subsets_SNAP_QGIS", "%s_indicadores_%dm.tif" % (SITIO, a.pixel))
    guardar_tif(out, capas, g, " | ".join(f for _, f in fuentes),
                "Indicadores de cambio por sensor (radar: 10 log10(post/pre) en dB; optico: NBR)")
    pd.DataFrame(fuentes, columns=["capas", "fuente"]).to_csv(
        ruta_tp("Tp5", "02_Subsets_SNAP_QGIS", "%s_indicadores_fuentes.csv" % SITIO), index=False, encoding="utf-8-sig")
    log("")
    log("Indicadores:", out, "(%d capas: %s)" % (len(capas), ", ".join(capas)))
    log.cerrar("python Tp5_02_sinergia.py --pixel %d" % a.pixel)


if __name__ == "__main__":
    main()
