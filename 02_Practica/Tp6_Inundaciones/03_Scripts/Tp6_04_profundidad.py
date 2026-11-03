# -*- coding: utf-8 -*-
"""
Tp6_04_profundidad.py   [SE CORRE]   Tp6, paso 5 de la guia - profundidad del agua
=========================================================================
"Profundidad: cota del borde menos el MDE" (presentacion 01, diapositiva 29).

Es la idea de FwDET (Floodwater Depth Estimation Tool; Cohen et al., 2018,
version 1.0, y 2019, version 2.0; version para Earth Engine de Peter et al., 2020): la superficie del agua se
supone horizontal LOCALMENTE, a la cota del borde de la mancha. Para cada
pixel inundado:

  1. se buscan los pixeles del BORDE de la mancha (inundados con algun vecino
     SECO CON DATO) y su cota en el MDE. No cuentan como borde los contactos
     con el agua permanente (rio, embalse: JRC >= 90 %) ni con los pixeles sin
     dato: alli la orilla de la mancha no es la orilla de la crecida, y su cota
     (la de la costa del rio, baja) haria la mancha menos profunda de lo que es.
     El agua permanente y el sin dato quedan dentro del dominio del agua, como
     en FwDET v2.0;
  2. se suaviza la cota del borde con una MEDIA movil (--suavizado) para que
     un pixel de borde mal ubicado no fabrique un pozo;
  3. cada pixel inundado toma la cota del borde MAS CERCANO;
  4. profundidad = cota del borde - cota del MDE (los valores negativos se
     llevan a 0 y se cuentan).

Modelo de elevacion (--mde)
  copdem  Copernicus DEM GLO-30, del Planetary Computer (por defecto, como antes).
  fabdem  FABDEM v1-2 (Hawker et al., 2022): el Copernicus DEM con los arboles y
          los edificios quitados, es decir, un modelo de TERRENO. Se lee del
          subset del practico (02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/
          B_CONCORDIA_FABDEM_v1-2.tif): no necesita internet.

Estadisticas que escribe la bitacora
  - las de los valores ORIGINALES (con los negativos), las de los POSITIVOS y
    las de los valores llevados a 0 (las de antes): la mediana con ceros queda
    empujada hacia 0 por el recorte, y conviene ver las tres;
  - cuantos pixeles superan 5 m (casi siempre artefactos de barranca o de un
    borde mal ubicado).

Advertencias que el programa escribe (y que van al informe)
  - El Copernicus DEM es un modelo de SUPERFICIE de radar banda X de
    2011-2015: en el monte de galeria y en las islas con monte mide la copa,
    no el suelo; en el cauce, el espejo de agua.
    Por eso Tp6_05 lo controla con ICESat-2.
  - Donde el MDE ve agua (rio, embalse) la cota es la del espejo de agua
    del dia de la adquisicion, no el fondo.
  - El resultado es una profundidad PLAUSIBLE, no medida: sin un hidrometro o
    una marca de crecida no hay validacion de la profundidad.

SALIDA  Tp6_Inundaciones/05_Resultados/02_Rasters/B_profundidad_<variante>_<pixel>m.tif
USO     python Tp6_04_profundidad.py --pixel 20 --variante multisensor --suavizado 7
        python Tp6_04_profundidad.py --pixel 20 --variante multisensor_20231104 --mde fabdem
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
from funciones_comunes import (leer_tif, grilla_de_tif, copdem, guardar_tif, Bitacora,  # noqa: E402
                               jrc_ocurrencia, leer_en_grilla)

# ------------------------------------------------------------------ PARAMETROS
SITIO = "B_CONCORDIA"
UMBRAL_ARTEFACTO_M = 5.0      # profundidades mayores se cuentan como probables artefactos


def profundidad_fwdet(agua, mde, suavizado=7, excluir=None):
    """agua: bool (inundado); mde: cotas en m; excluir: bool, pixeles que NO son tierra seca
    (agua permanente, sin dato) y por lo tanto no definen borde. Devuelve profundidad (m) y cota de agua."""
    from scipy import ndimage

    if excluir is None:
        excluir = np.zeros(agua.shape, bool)
    seco = ~agua & ~excluir
    borde = agua & ndimage.binary_dilation(seco, structure=np.ones((3, 3)))
    cota_b = np.where(borde & np.isfinite(mde), mde, np.nan)
    if suavizado > 1:
        rel = np.where(np.isfinite(cota_b), cota_b, 0.0)
        cnt = ndimage.uniform_filter(np.isfinite(cota_b).astype("float64"), suavizado)
        med = ndimage.uniform_filter(rel, suavizado) / np.where(cnt > 0, cnt, np.nan)
        cota_b = np.where(np.isfinite(cota_b), med, np.nan)
    sin_borde = ~np.isfinite(cota_b)
    _, (fi, ci) = ndimage.distance_transform_edt(sin_borde, return_indices=True)
    cota_agua = cota_b[fi, ci]
    prof = np.where(agua, cota_agua - mde, np.nan)
    return prof.astype("float32"), np.where(agua, cota_agua, np.nan).astype("float32")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pixel", type=int, default=20)
    ap.add_argument("--variante", default="multisensor")
    ap.add_argument("--suavizado", type=int, default=7)
    ap.add_argument("--mde", choices=["copdem", "fabdem"], default="copdem",
                    help="copdem = Copernicus DEM (superficie, por defecto); fabdem = FABDEM v1-2 (terreno)")
    a = ap.parse_args()
    sufijo = "" if a.mde == "copdem" else "_fabdem"
    log = Bitacora(ruta_tp("Tp6", "05_Resultados", "06_Control_calidad"), "Tp6_04_profundidad" + sufijo)
    ruta = ruta_tp("Tp6", "05_Resultados", "02_Rasters", "B_variante_%s.tif" % a.variante)
    v, _, tags = leer_tif(ruta)
    g = grilla_de_tif(ruta)
    agua = v["clase"] == 1
    sin_dato = ~np.isfinite(v["clase"])
    if a.mde == "fabdem":
        fab = ruta_tp("Tp6", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", "B_CONCORDIA_FABDEM_v1-2.tif")
        if not os.path.exists(fab):
            sys.exit("Falta %s (subset FABDEM del practico)." % fab)
        mde = leer_en_grilla(fab, g, "bilinear")
        nombre_mde = "FABDEM v1-2 (terreno; Hawker et al., 2022)"
    else:
        mde, _ = copdem(SITIO, g)
        nombre_mde = "Copernicus DEM GLO-30 (Planetary Computer)"
    log("Modelo de elevacion: %s" % nombre_mde)
    try:
        ocu, _ = jrc_ocurrencia("B_CONCORDIA", g)
        perm = np.nan_to_num(ocu, nan=0) >= 90
        log("Agua permanente (JRC >= 90 %%): %.1f %% del sitio; no define borde." % (100 * perm.mean()))
    except Exception as e:                                       # noqa: BLE001
        perm = np.zeros(agua.shape, bool)
        log("AVISO: no se pudo leer el JRC (%s): los bordes contra el rio cuentan como orilla" % str(e)[:80])
        log("       y la profundidad junto al cauce queda subestimada. Repetir con conexion.")
    excluir = perm | sin_dato
    log("Pixeles sin dato en la variante: %.1f %% del sitio; no definen borde." % (100 * sin_dato.mean()))
    prof, cota = profundidad_fwdet(agua, mde, a.suavizado, excluir)
    orig = prof[agua & np.isfinite(prof)]                     # valores originales, con los negativos
    neg = int(np.sum(orig < 0))
    prof = np.where(prof < 0, 0, prof).astype("float32")
    log("Pixeles inundados: %d; con profundidad negativa (llevados a 0): %d (%.1f %%)"
        % (agua.sum(), neg, 100 * neg / max(agua.sum(), 1)))
    p = prof[np.isfinite(prof)]
    if p.size:
        log("Profundidad: mediana %.2f m, p90 %.2f m, maximo %.2f m" % (np.median(p), np.percentile(p, 90), p.max()))
        log("   (esa mediana incluye los negativos llevados a 0: el recorte la empuja hacia cero)")
        log("Valores originales, con negativos: mediana %.2f m, p90 %.2f m, minimo %.2f m"
            % (np.median(orig), np.percentile(orig, 90), orig.min()))
        pos = orig[orig > 0]
        if pos.size:
            log("Solo los positivos (%d pixeles): mediana %.2f m, p90 %.2f m" % (pos.size, np.median(pos), np.percentile(pos, 90)))
        log("Pixeles con mas de %.0f m (probables artefactos de barranca o de borde): %d"
            % (UMBRAL_ARTEFACTO_M, int(np.sum(orig > UMBRAL_ARTEFACTO_M))))
    if a.mde == "copdem":
        log("ADVERTENCIA: Copernicus DEM es un modelo de superficie (copa y espejo de agua de 2011-2015).")
    else:
        log("ADVERTENCIA: FABDEM quita arboles y edificios con un modelo estadistico; en el cauce sigue midiendo")
        log("            el espejo de agua de 2011-2015.")
    log("La profundidad es plausible, no medida. Controlar el MDE con ICESat-2 (Tp6_05).")
    sin_recortar = np.where(agua, cota - mde, np.nan).astype("float32")
    guardar_tif(ruta_tp("Tp6", "05_Resultados", "02_Rasters", "B_profundidad_%s%s_%dm.tif" % (a.variante, sufijo, a.pixel)),
                {"profundidad_m": prof, "cota_agua_m": cota, "profundidad_sin_recortar_m": sin_recortar}, g,
                tags.get("FUENTE", "") + " | " + nombre_mde,
                "Profundidad por cota del borde (idea FwDET), suavizado %d pixeles, MDE %s" % (a.suavizado, a.mde))
    log.cerrar("python Tp6_05_control_mde_icesat2.py --pixel %d" % a.pixel)


if __name__ == "__main__":
    main()
