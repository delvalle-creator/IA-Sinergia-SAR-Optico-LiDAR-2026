# -*- coding: utf-8 -*-
"""
Tp8_02_textura_S_y_C.py   [SE CORRE]   Tp8, paso 3 de la guia - SINERGIA: rugosidad en S frente a C
=======================================================================================
Sinergia: rugosidad y textura en S (NovaSAR, resolucion de 6 m) frente a C (Sentinel-1 IW:
pixel de 10 m, resolucion de unos 20 x 22 m). Guia teorico-practica general, seccion 11.4.

La rugosidad del suelo (terrones, surcos, bordes de carcava) cambia la
retrodispersion; la TEXTURA espacial (cuanto varia la senal entre pixeles
vecinos) describe esa rugosidad mejor que el valor medio. Se calcula para
cada banda POR SEPARADO y se comparan:

  S  NovaSAR-1 GRD HH, escena --novasar (por defecto 47974, 14/09/2023; archivo
     del curso), sigma0, llevado a la grilla de --pixel promediando potencia.
     La resolucion nativa es 6 m: con --pixel 6 se ve el detalle que se pierde
     a 10 m (y la banda C queda remuestreada mas fina que su pixel: se declara)
  C  Sentinel-1 RTC VV y VH (pixel de 10 m, resolucion de unos 20 x 22 m) de la pasada
     mas cercana a --fecha_c, en +/- 6 dias (Planetary Computer). --fecha_c es la fecha
     BUSCADA: en Bovril, con --fecha_c 2023-09-14 se usa la pasada del 17/09/2023.

Textura = coeficiente de variacion local en una ventana de --ventana pixeles:
    CV = desvio(potencia) / media(potencia)
En potencia (lineal), no en dB. El speckle solo ya da un CV: en INTENSIDAD (potencia),
1 para una vista y 1/raiz(L) para L vistas; en AMPLITUD, 0,52 para una vista. Al reves,
un CV medido en una zona homogenea da el numero equivalente de vistas: ENL = 1/CV^2. Los productos del curso son multivista o estan filtrados
(NovaSAR de 6 m, Sentinel-1 RTC), asi que en una superficie homogenea el CV queda
MENOR que 1, y eso es lo normal, no una senal de filtrado excesivo. Lo que indica
heterogeneidad real (bordes, carcavas, alambrados) es un CV MAYOR que el de una
zona homogenea (lote grande con cultivo parejo, sin bordes) del mismo producto: por eso
se compara contra ella y no contra 1. El agua no sirve de piso: en banda S queda cerca del
ruido del instrumento y su CV no es el del speckle.

PISO DE SPECKLE (--zonas_homogeneas, agregado el 27/10/2026). Si se pasa un GeoPackage con
poligonos de zonas homogeneas (por ejemplo 04_Tablas_de_trabajo/zonas_homogeneas.gpkg), el
script calcula en ellos el CV de cada banda con la MISMA ventana y lo escribe como ultima fila
de F_textura_por_frecuencia.csv ("piso", minimo a maximo de las medianas por poligono).

SNAP tiene ademas la textura de Haralick (Raster > Image Analysis > Texture
Analysis > Grey Level Co-occurrence Matrix): se usa en clase sobre el mismo
recorte para comparar con este CV, que es mas simple de interpretar.

SALIDA
  Tp8_Erosion_suelos/02_Subsets_SNAP_QGIS/F_textura_S_C_<pixel>m.tif
  Tp8_Erosion_suelos/05_Resultados/04_Tablas/F_textura_por_frecuencia.csv

USO
    python Tp8_02_textura_S_y_C.py --pixel 10 --fecha_c 2023-09-14 --ventana 5
    python Tp8_02_textura_S_y_C.py --puntos_enlace todos --desplazamiento -80 20 --zonas_homogeneas ../04_Tablas_de_trabajo/zonas_homogeneas.gpkg
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
from configuracion_comun import NOVASAR_ESCENAS                       # noqa: E402
from funciones_comunes import (grilla_sitio, novasar_sigma0, s1_rtc_mas_cercana, fecha_item,  # noqa: E402
                               s1_rtc, leer_en_grilla, guardar_tif, Bitacora, fuente_mpc)

# ----------------------------------------------------------------- PARAMETROS
SITIO = "F_BOVRIL"
DIAS_S1 = 6                    # tolerancia para buscar la pasada de Sentinel-1 alrededor de --fecha_c


def cv_local(x, ventana):
    from scipy import ndimage

    ok = np.isfinite(x)
    v = np.where(ok, x, 0.0).astype("float64")
    n = ndimage.uniform_filter(ok.astype("float64"), ventana)
    m = ndimage.uniform_filter(v, ventana) / np.where(n > 0, n, np.nan)
    m2 = ndimage.uniform_filter(v * v, ventana) / np.where(n > 0, n, np.nan)
    sd = np.sqrt(np.maximum(m2 - m * m, 0))
    return np.where(ok & (n > 0.6), sd / m, np.nan).astype("float32")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pixel", type=float, default=10.0)
    ap.add_argument("--fecha_c", default="2023-09-14")
    ap.add_argument("--novasar", default="47974")
    ap.add_argument("--ventana", type=int, default=5)
    ap.add_argument("--anio", type=int, default=2023, help="anio de la frecuencia de suelo desnudo de Tp8_01")
    ap.add_argument("--desplazamiento", type=float, nargs=2, default=(0.0, 0.0), metavar=("DX", "DY"),
                    help="CORRECCION que se aplica a NovaSAR, en m: DX positivo = mover al este, DY positivo = "
                         "mover al norte. Si la banda S esta corrida 80 m al este y 20 m al sur, se corrige "
                         "moviendola 80 m al oeste y 20 m al norte: --desplazamiento -80 20")
    ap.add_argument("--puntos_enlace", choices=("esquinas", "todos"), default="esquinas",
                    help="georreferencia de NovaSAR: 'esquinas' (4 GCP del image_HH.tif, ajuste afin) o "
                         "'todos' (84 puntos de enlace del metadata.xml)")
    ap.add_argument("--zonas_homogeneas", default=None,
                    help="GeoPackage con poligonos de zonas homogeneas para medir el piso de speckle (opcional)")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp8", "05_Resultados", "06_Control_calidad"), "Tp8_02_textura")
    g = grilla_sitio(SITIO, pixel=a.pixel)
    capas, fuentes = {}, []
    s0, k = novasar_sigma0(a.novasar, g, desplazamiento_m=tuple(a.desplazamiento), puntos_enlace=a.puntos_enlace)
    log("NovaSAR georreferenciado con %s." % ("los 4 puntos de esquina del image_HH.tif (ajuste afin de la franja)"
        if a.puntos_enlace == "esquinas" else "los 84 puntos de enlace del metadata.xml"))
    if a.desplazamiento == (0.0, 0.0) or list(a.desplazamiento) == [0.0, 0.0]:
        log("AVISO: NovaSAR sin correccion de georreferencia. Mida el desfase en QGIS (paso 2) y pase")
        log("--desplazamiento DX DY antes de comparar texturas por lote. DX y DY son la CORRECCION:")
        log("DX positivo = mover al este, DY positivo = mover al norte.")
        log("Con las 4 esquinas el corrimiento es de cientos de metros y cambia de norte a sur (guia, 11.3);")
        log("con --puntos_enlace todos queda chico y rigido: medalo y apliquelo con los mismos puntos de enlace.")
    else:
        log("Desplazamiento aplicado (correccion): %+.0f m este, %+.0f m norte" % tuple(a.desplazamiento))
    capas["S_NovaSAR_sigma0_HH"] = s0
    capas["S_CV_HH"] = cv_local(s0, a.ventana)
    fecha_s = NOVASAR_ESCENAS.get(a.novasar, ("",))[0]
    fuentes.append("SSTL - CSIRO. NovaSAR-1 Stripmap GRD HH, escena %s, %s, sigma0 = DN^2/%.0e. "
                   "Archivo del curso; CSIRO NovaSAR Data Hub: https://data.novasar.csiro.au" % (a.novasar, fecha_s, k))
    log("Calibracion: sigma0 = DN^2 / CalibrationConstant, con CalibrationConstant = %.0e (metadata.xml)" % k)
    log("S NovaSAR %s: %.1f %% del sitio con dato; CV mediano %.2f"
        % (a.novasar, 100 * np.isfinite(s0).mean(), np.nanmedian(capas["S_CV_HH"])))
    try:
        it = s1_rtc_mas_cercana(SITIO, a.fecha_c, dias=DIAS_S1)
        if it is not None:
            f, h = fecha_item(it)
            for p in ("vv", "vh"):
                x = s1_rtc(it, p, g)
                capas["C_S1_gamma0_%s" % p.upper()] = x
                capas["C_CV_%s" % p.upper()] = cv_local(x, a.ventana)
            fuentes.append(fuente_mpc("ESA - Copernicus", "Sentinel-1 IW GRD RTC", f, h))
            log("C Sentinel-1 %s (pasada mas cercana a --fecha_c %s, +/- %d dias): CV mediano VV %.2f, VH %.2f"
                % (f, a.fecha_c, DIAS_S1, np.nanmedian(capas["C_CV_VV"]), np.nanmedian(capas["C_CV_VH"])))
            dias = abs((np.datetime64(f) - np.datetime64(fecha_s or a.fecha_c)).astype(int))
            log("Diferencia de fecha S-C: %d dias (lluvia entre fechas cambia la humedad y la retrodispersion)." % dias)
        else:
            log("Sin Sentinel-1 RTC +/- 6 dias de %s: la comparacion S-C queda sin banda C." % a.fecha_c)
    except Exception as e:                           # noqa: BLE001
        log("No se pudo consultar el Planetary Computer (%s). Se sigue solo con la banda S." % str(e)[:100])
    guardar_tif(ruta_tp("Tp8", "02_Subsets_SNAP_QGIS", "F_textura_S_C_%dm.tif" % a.pixel), capas, g,
                " | ".join(fuentes), "Retrodispersion lineal y coeficiente de variacion local (ventana %d)" % a.ventana)

    fr = ruta_tp("Tp8", "02_Subsets_SNAP_QGIS", "F_frecuencia_suelo_desnudo_%d_%dm.tif" % (a.anio, a.pixel))
    if os.path.exists(fr):
        freq = leer_en_grilla(fr, g, "nearest", banda=1)
        filas = []
        for lo, hi, txt in ((0, 0, "nunca"), (1, 2, "1-2 meses"), (3, 5, "3-5 meses"), (6, 12, ">= 6 meses")):
            m = (freq >= lo) & (freq <= hi)
            fila = {"suelo_desnudo": txt, "pixeles": int(m.sum())}
            for c in [k for k in capas if "_CV_" in k]:
                fila[c] = round(float(np.nanmedian(capas[c][m])), 3) if m.any() else np.nan
            filas.append(fila)
        if a.zonas_homogeneas:
            import geopandas as gpd
            zg = gpd.read_file(a.zonas_homogeneas).to_crs(g["crs"])
            from rasterio import features
            zid = features.rasterize(((geo, i + 1) for i, geo in enumerate(zg.geometry)),
                                     out_shape=(g["height"], g["width"]), transform=g["transform"], fill=0, dtype="int32")
            fila = {"suelo_desnudo": "piso (%d zonas homogeneas, min a max)" % len(zg), "pixeles": int((zid > 0).sum())}
            for c in [k for k in capas if "_CV_" in k]:
                med = [np.nanmedian(capas[c][zid == i + 1]) for i in range(len(zg))]
                fila[c] = "%.3f a %.3f" % (np.nanmin(med), np.nanmax(med))
                log("Piso de speckle %s: %.3f a %.3f (mediana %.3f; ENL = 1/CV^2 = %.0f vistas)"
                    % (c, np.nanmin(med), np.nanmax(med), np.nanmedian(med), 1 / np.nanmedian(med) ** 2))
            filas.append(fila)
        t = pd.DataFrame(filas)
        log.titulo("Textura (CV mediano) segun la frecuencia de suelo desnudo de Tp8_01")
        log(t.to_string(index=False))
        out = ruta_tp("Tp8", "05_Resultados", "04_Tablas", "F_textura_por_frecuencia.csv")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        t.to_csv(out, index=False, encoding="utf-8-sig")
    else:
        log("Falta la frecuencia de suelo desnudo (Tp8_01): la tabla de comparacion no se arma.")
    log.cerrar("python Tp8_03_susceptibilidad.py --pixel %d --anio %d" % (a.pixel, a.anio))


if __name__ == "__main__":
    main()
