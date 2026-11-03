# -*- coding: utf-8 -*-
"""
Tp10_05_velocidad_subsidencia.py   [SE CORRE]   Tp10, paso 10 de la guía: velocidad vertical
=============================================================================================
Producto de la presentación 01, diapositiva 33: «Subsidencia: serie InSAR en banda C» y
«Control: puntos de referencia estables con velocidad cercana a cero».

QUÉ ENTRA
  La carpeta con los pares de HyP3 ya descomprimidos (los arma Tp10_04; en clase YA VIENEN
  HECHOS). De cada par se usan tres archivos:
     *_vert_disp.tif   desplazamiento vertical (m), positivo = ascenso, suponiendo que no
                       hay movimiento horizontal
     *_los_disp.tif    desplazamiento en la línea de visión (m), sólo para verificar el signo
     *_corr.tif        coherencia (0 a 1)

QUÉ SE CALCULA: APILADO DE TASAS (no es una inversión SBAS)
     velocidad = suma(desplazamientos) / suma(intervalos)        [mm/año]
  en cada píxel, con los pares coherentes (coherencia >= --coh_min) en ese píxel.
  Ponderación: dividir la SUMA de los desplazamientos por la SUMA de los intervalos equivale a
  promediar la tasa de cada par (desplazamiento / intervalo) pesándola por su intervalo: un par
  de 48 días pesa cuatro veces más que uno de 12 días. Así los pares largos, que acumulan más
  deformación frente al mismo ruido atmosférico, mandan más en el resultado.
  Una inversión SBAS (MintPy, LiCSBAS) resolvería el desplazamiento de cada fecha a partir de
  toda la red; el apilado da sólo la velocidad media del período, que es lo que pide el práctico.
  Un píxel tiene velocidad sólo si es coherente en al menos --frac_min (0,9) de los pares que lo
  cubren (y en no menos de --min_pares). En campos, islas y bañados la coherencia aparece y
  desaparece, y el apilado acumula el sesgo de fase de la vegetación y de la humedad del suelo
  (Ansari, De Zan y Parizzi, 2021, https://doi.org/10.1109/TGRS.2020.3003421), no deformación.

REFERENCIA
  Cada interferograma tiene una constante arbitraria (el desenrollado empieza en cualquier
  punto). Antes de sumar, a cada par se le resta la mediana de la zona de referencia:
     --referencia <gpkg>  polígonos estables (edificios grandes antiguos, puentes); o, si no se
                          da, la mediana de los píxeles coherentes en forma sostenida
                          (coherentes en al menos --frac_ref de los pares). Se declara en la
                          bitácora: si toda esa zona se mueve, eso queda escondido.

CONTROL EN PUNTOS ESTABLES (--control <gpkg de puntos>)
  Se informan la media, el desvío y el ERROR DE LA MEDIA (desvío / raíz de n). Criterio:
  la referencia se acepta si |media| < 2 × error de la media (la media no se distingue de 0
  al 95 %). Comparar la media con el desvío, como en la versión anterior, es un criterio
  débil: el desvío no achica con más puntos y casi cualquier media lo cumple.

CONTROL DE SALTOS DE DESENROLLADO (por par)
  Un error de desenrollado mueve una zona entera un ciclo de fase: λ/2 = 2,8 cm en la línea
  de visión de Sentinel-1 (media longitud de onda; unos 35 mm en vertical con el factor 1,25 que
  usa HyP3 en esta geometría). En cada par se cuenta qué parte de los píxeles coherentes queda a
  más de --salto_mm (por defecto 35 mm) de la mediana de ese par. Los pares con más de --frac_salto (por defecto 0,2) de píxeles así se marcan como
  «sospechosos» en la tabla de pares. Con --descartar_saltos no entran en la velocidad.

SEÑAL ESTACIONAL
  La ventana de los 120 pares (01/06/2025 a 03/07/2026) es de 13 meses: una señal estacional
  (humedad del suelo, contracción de arcillas) no se cancela en un período que no es un número
  entero de años. Se declara.

SALIDA
  Tp10_Impacto_urbano/05_Resultados/02_Rasters/<SITIO>_velocidad_vertical.tif
      bandas velocidad_mm_por_anio, pares_validos, dispersion_entre_pares_mm_por_anio (cuánto
      varían las tasas de cada par; NO es el error de la velocidad)
  Tp10_Impacto_urbano/05_Resultados/04_Tablas/<SITIO>_pares_usados.csv (con la fracción de
      píxeles con salto y la marca de par sospechoso)

USO (desde 03_Scripts, en el Miniforge Prompt, con el entorno sar)
    python Tp10_05_velocidad_subsidencia.py --sitio E_PARANA_DIAMANTE --carpeta ..\\02_Subsets_SNAP_QGIS\\HyP3_E_PARANA_DIAMANTE\\QGIS_GeoTIFF --referencia ..\\04_Tablas_de_trabajo\\referencia_estable_E.gpkg --control ..\\04_Tablas_de_trabajo\\control_estable_E.gpkg

(El historial de versiones de este programa está en NOTAS_TECNICAS.md.)
"""
import argparse
import glob
import os
import re
import sys

# Busca la carpeta 00_COMUN subiendo por el árbol de carpetas y la agrega a la ruta de Python.
_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import ORIGINALES, ruta_tp                   # noqa: E402
from funciones_comunes import grilla_sitio, leer_en_grilla, rasterizar, guardar_tif, Bitacora  # noqa: E402
from funciones_cambio import figura_mapa                              # noqa: E402

# Las fechas de cada par salen del nombre original de HyP3 (..._AAAAMMDDThhmmss_AAAAMMDDThhmmss_...).
PATRON = re.compile(r"(\d{8})T\d{6}_(\d{8})T\d{6}")


def main():
    ap = argparse.ArgumentParser(description="Velocidad vertical por apilado de tasas interferométricas (Tp10, paso 10)")
    ap.add_argument("--sitio", default="E_PARANA_DIAMANTE", choices=["E_PARANA_DIAMANTE", "B_CONCORDIA"])
    ap.add_argument("--carpeta", default="", help="carpeta con los pares HyP3 descomprimidos")
    ap.add_argument("--pixel", type=float, default=40.0, help="40 m: el píxel de los interferogramas HyP3")
    ap.add_argument("--coh_min", type=float, default=0.3, help="coherencia mínima de un par en un píxel")
    ap.add_argument("--min_pares", type=int, default=5, help="pares coherentes mínimos para dar velocidad")
    ap.add_argument("--frac_min", type=float, default=0.9, help="fracción mínima de pares coherentes para dar velocidad")
    ap.add_argument("--frac_ref", type=float, default=0.9, help="fracción para la referencia automática")
    ap.add_argument("--referencia", default="", help="polígonos estables (gpkg)")
    ap.add_argument("--control", default="", help="puntos estables de control (gpkg)")
    ap.add_argument("--salto_mm", type=float, default=35.0,
                    help="distancia a la mediana del par (mm, vertical) a partir de la cual un píxel cuenta como salto")
    ap.add_argument("--frac_salto", type=float, default=0.2,
                    help="fracción de píxeles con salto a partir de la cual el par se marca como sospechoso")
    ap.add_argument("--descartar_saltos", action="store_true", help="no usar los pares sospechosos en la velocidad")
    a = ap.parse_args()
    S = a.sitio
    log = Bitacora(ruta_tp("Tp10", "05_Resultados", "06_Control_calidad"), "Tp10_05_%s" % S)
    carpeta = a.carpeta or os.path.join(ORIGINALES, "HYP3", S)
    verts = sorted(glob.glob(os.path.join(carpeta, "**", "*_vert_disp.tif"), recursive=True))
    log("Carpeta: %s; pares con *_vert_disp.tif: %d" % (carpeta, len(verts)))
    if not verts:
        sys.exit("No hay productos HyP3 descomprimidos en %s. Revise la ruta de --carpeta "
                 "(o descomprima los .zip que bajó Tp10_04)." % carpeta)
    g = grilla_sitio(S, pixel=a.pixel)
    # todos_los_tocados: los polígonos estables (un edificio, un puente) suelen ser más chicos que 40 m
    ref = rasterizar(a.referencia, g, todos_los_tocados=True) > 0 if a.referencia else None

    # Primera pasada: en cuántos pares es coherente cada píxel. No todos los pares cubren todo el
    # sitio: el porcentaje se cuenta sobre los pares que cubren cada píxel (en HyP3, coherencia 0 = sin dato).
    ncoh = np.zeros((g["height"], g["width"]), "int32")
    ncov = np.zeros_like(ncoh)
    for v in verts:
        c0 = leer_en_grilla(v.replace("_vert_disp.tif", "_corr.tif"), g, "average")
        cub = np.isfinite(c0) & (c0 > 0)
        ncov += cub.astype("int32")
        ncoh += (cub & (c0 >= a.coh_min)).astype("int32")
    sostenidos = (ncov >= a.min_pares) & (ncoh >= a.frac_ref * ncov)
    log("Pares que cubren cada píxel: mínimo %d, máximo %d de %d"
        % (ncov[ncov > 0].min() if (ncov > 0).any() else 0, ncov.max(), len(verts)))
    log("Píxeles coherentes en forma sostenida (en >= %.0f %% de los pares que los cubren): %.1f %% del sitio"
        % (100 * a.frac_ref, 100 * sostenidos.mean()))
    if ref is None:
        ref = sostenidos
        log("AVISO: sin --referencia; se usa la mediana de los %d píxeles coherentes en forma sostenida (casi"
            " siempre zona construida). Si toda esa zona se mueve, el mapa lo esconde: digitalice una referencia."
            % sostenidos.sum())
        sin_ref = True
    else:
        sin_ref = False
        log("Zona de referencia: %d píxeles de %.0f m" % (ref.sum(), a.pixel))
        if ref.sum() < 10:
            log("AVISO: menos de 10 píxeles de referencia: el ruido de esos pocos píxeles pasa entero a todo")
            log("el mapa. Conviene sumar varias zonas estables separadas entre sí.")

    # Segunda pasada: apilado de tasas y control de saltos de desenrollado por par.
    suma_d = np.zeros((g["height"], g["width"]))
    suma_t = np.zeros_like(suma_d)
    suma_v = np.zeros_like(suma_d)
    suma_v2 = np.zeros_like(suma_d)
    n = np.zeros(suma_d.shape, "int32")
    filas, signos = [], []
    for v in verts:
        m = PATRON.search(os.path.basename(v))
        if not m:
            log("  sin fechas en el nombre: %s (use el nombre original de HyP3)" % os.path.basename(v))
            continue
        t1, t2 = pd.Timestamp(m.group(1)), pd.Timestamp(m.group(2))
        dt = (t2 - t1).days / 365.25
        d = leer_en_grilla(v, g, "average")
        coh = leer_en_grilla(v.replace("_vert_disp.tif", "_corr.tif"), g, "average")
        los_r = v.replace("_vert_disp.tif", "_los_disp.tif")
        if os.path.exists(los_r):
            los = leer_en_grilla(los_r, g, "average")
            ok_s = np.isfinite(los) & np.isfinite(d)
            if ok_s.sum() > 100:
                signos.append(np.corrcoef(los[ok_s], d[ok_s])[0, 1])
        d[(coh < a.coh_min) | ~np.isfinite(coh)] = np.nan
        zona = ref & np.isfinite(d)
        if zona.sum() < 1:
            log("  %s-%s: sin píxeles coherentes en la referencia; par descartado" % (t1.date(), t2.date()))
            continue
        d = d - np.nanmedian(d[zona])
        ok = np.isfinite(d)
        # control de saltos: píxeles coherentes a más de --salto_mm de la mediana del par
        frac_salto = float(np.mean(np.abs(d[ok] - np.nanmedian(d[ok])) * 1000 > a.salto_mm)) if ok.any() else np.nan
        sospechoso = bool(frac_salto > a.frac_salto)
        filas.append({"fecha_1": str(t1.date()), "fecha_2": str(t2.date()), "dias": (t2 - t1).days,
                      "%_coherente": round(100 * ok.mean(), 1), "coherencia_mediana": round(float(np.nanmedian(coh)), 2),
                      "fraccion_pixeles_con_salto": round(frac_salto, 3), "par_sospechoso": "sí" if sospechoso else "no",
                      "usado": "no" if (sospechoso and a.descartar_saltos) else "sí"})
        log("  %s - %s (%3d días): %5.1f %% de píxeles con coherencia >= %.2f; con salto > %.0f mm: %4.1f %%%s"
            % (t1.date(), t2.date(), (t2 - t1).days, 100 * ok.mean(), a.coh_min, a.salto_mm, 100 * frac_salto,
               "  SOSPECHOSO" if sospechoso else ""))
        if sospechoso and a.descartar_saltos:
            continue
        suma_d[ok] += d[ok]
        suma_t[ok] += dt
        suma_v[ok] += d[ok] / dt
        suma_v2[ok] += (d[ok] / dt) ** 2
        n[ok] += 1
    tp = pd.DataFrame(filas)
    log("Pares sospechosos de salto de desenrollado (más del %.0f %% de los píxeles a más de %.0f mm de la mediana): %d de %d%s"
        % (100 * a.frac_salto, a.salto_mm, (tp.par_sospechoso == "sí").sum(), len(tp),
           " (descartados)" if a.descartar_saltos else " (se usan; para descartarlos: --descartar_saltos)"))
    if signos:
        log("Correlación LOS frente a vertical: %.2f (positiva = el LOS positivo es acercamiento al satélite)"
            % np.median(signos))
    usa = (n >= a.min_pares) & (n >= a.frac_min * ncov)
    vel = np.where(usa, 1000 * suma_d / np.where(suma_t > 0, suma_t, np.nan), np.nan).astype("float32")
    # Dispersión de las tasas de cada par (v_i = d_i / dt_i) alrededor de la velocidad apilada
    # (vel = suma d / suma dt): raíz( media(v_i^2) - 2 vel media(v_i) + vel^2 ).
    # Describe cuánto varían los pares (atmósfera, desenrollado); NO es el error estándar de la velocidad.
    nn = np.maximum(n, 1)
    vel_m = vel.astype("float64") / 1000.0
    var = suma_v2 / nn - 2 * vel_m * (suma_v / nn) + vel_m ** 2
    disp = np.where(usa, 1000 * np.sqrt(np.maximum(var, 0)), np.nan).astype("float32")
    log("Píxeles con velocidad (coherentes en >= %.0f %% de los pares que los cubren y en >= %d): %.1f %% del sitio"
        % (100 * a.frac_min, a.min_pares, 100 * usa.mean()))
    log("Velocidad vertical: mediana %.1f mm/año; percentiles 5 y 95: %.1f y %.1f mm/año"
        % (np.nanmedian(vel), np.nanpercentile(vel, 5), np.nanpercentile(vel, 95)))
    if a.control:
        import geopandas as gpd
        pts = gpd.read_file(a.control).to_crs(g["crs"])
        T = g["transform"]
        c = np.floor((pts.geometry.x.values - T.c) / T.a).astype(int)
        f = np.floor((pts.geometry.y.values - T.f) / T.e).astype(int)
        dentro = (c >= 0) & (c < g["width"]) & (f >= 0) & (f < g["height"])
        if (~dentro).any():
            log("AVISO: %d puntos de control caen fuera de la grilla del sitio y no se usan." % (~dentro).sum())
        c, f = c[dentro], f[dentro]
        if ref[f, c].any():
            log("AVISO: %d puntos de control caen DENTRO de la zona de referencia: no son un control"
                " independiente (allí la velocidad es 0 por construcción). Se excluyen." % ref[f, c].sum())
            sel = ~ref[f, c]
            c, f = c[sel], f[sel]
        vc = vel[f, c]
        log.titulo("CONTROL: velocidad en %d puntos estables (no usados como referencia)" % len(vc))
        vok = vc[np.isfinite(vc)]
        if vok.size == 0:
            log("Ningún punto de control tiene velocidad (en la referencia, o con menos de --min_pares pares coherentes).")
        else:
            media, desvio = float(np.mean(vok)), float(np.std(vok, ddof=1)) if vok.size > 1 else np.nan
            em = desvio / np.sqrt(vok.size)
            log("media %.1f mm/año, desvío %.1f, error de la media %.1f, máximo absoluto %.1f; con dato: %d"
                % (media, desvio, em, np.max(np.abs(vok)), vok.size))
            cumple = abs(media) < 2 * em
            log("Criterio: |media| < 2 × error de la media (%.1f < %.1f): %s"
                % (abs(media), 2 * em, "CUMPLE (la media no se distingue de 0)" if cumple else
                   "NO CUMPLE: la referencia no es estable, hay una tendencia orbital o atmosférica, o los puntos se mueven"))
    log("AVISO: la ventana de los pares (%s a %s) no es un número entero de años: una señal estacional"
        " (humedad del suelo, arcillas) puede no cancelarse. Se declara." % (tp.fecha_1.min(), tp.fecha_2.max()))
    out = ruta_tp("Tp10", "05_Resultados", "02_Rasters", "%s_velocidad_vertical.tif" % S)
    fuente = ("ESA - Copernicus, Sentinel-1 IW SLC; interferogramas HyP3 INSAR_GAMMA (ASF DAAC, "
              "https://hyp3-docs.asf.alaska.edu), %d pares" % int((tp.usado == "sí").sum()))
    guardar_tif(out, {"velocidad_mm_por_anio": vel, "pares_validos": n.astype("float32"),
                      "dispersion_entre_pares_mm_por_anio": disp}, g, fuente,
                "Apilado de tasas de desplazamiento vertical (positivo = ascenso), coherencia >= %.2f en >= %.0f %% de los pares; "
                "referencia: %s" % (a.coh_min, 100 * a.frac_min, "píxeles coherentes en forma sostenida" if sin_ref else a.referencia),
                unidades={"velocidad_mm_por_anio": "mm/año", "pares_validos": "número de pares",
                          "dispersion_entre_pares_mm_por_anio": "mm/año"})
    tt = ruta_tp("Tp10", "05_Resultados", "04_Tablas", "%s_pares_usados.csv" % S)
    os.makedirs(os.path.dirname(tt), exist_ok=True)
    tp.to_csv(tt, index=False, encoding="utf-8-sig")
    figura_mapa(np.clip(vel, -20, 20), ruta_tp("Tp10", "05_Resultados", "05_Graficos", "%s_velocidad_vertical.png" % S),
                "%s - velocidad vertical (mm/año, recortada a ± 20)\nazul = ascenso, rojo = hundimiento" % S, fuente, cmap="RdBu")
    log.cerrar("responder las preguntas del Tp10")


if __name__ == "__main__":
    main()
