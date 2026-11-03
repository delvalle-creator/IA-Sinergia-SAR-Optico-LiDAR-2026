# -*- coding: utf-8 -*-
"""
Tp2_02_rgb_copol_cruzada_cociente.py   [SE CORRE]   Tp2, paso 5 de la guia
==================================================================
Arma, para cada sensor de polarizacion dual de la pila de Tp2_01, la
composicion RGB que el curso usa SIEMPRE para el radar dual:

    R = copolarizada (VV o HH)         en dB
    G = cruzada (VH o HV; con BIOMASS, VH)  en dB
    B = cociente copolarizada/cruzada  en dB  (= copol_dB - cruz_dB)

Como se interpreta (presentacion 02, diapositiva 48 y 76):
    verde o amarillo   volumen: vegetacion, monte, pajonal (cruzada alta)
    magenta o blanco   doble rebote: ciudad, troncos sobre agua
    azul o violeta     cociente alto: suelo desnudo, agua rizada por viento
    negro              reflexion especular: agua calma

Con BIOMASS (banda P) se promedian antes las intensidades en una ventana de
5 x 5 pixeles, en lineal: con una sola mirada, el moteado (speckle) de la banda P
tapa los detalles. Las demas bandas no se promedian.

El estiramiento es 2-98 % por canal y se calcula sobre el sitio. Es SOLO
para ver: el GeoTIFF RGB es de 8 bits y no se usa para medir nada. Las
mediciones se hacen siempre sobre la pila en lineal.

Dos maneras de estirar (opcion --rango_fijo):
  - por escena (por defecto): cada RGB usa sus percentiles 2 y 98. Sirve para
    MIRAR una escena, pero el brillo no se compara entre RGB de sensores distintos.
  - con --rango_fijo: los mismos limites para todos los sensores (copolarizada
    de -25 a 0 dB, cruzada de -32 a -8 dB, cociente de 0 a 15 dB, los mismos de los
    _RGB_8bit.tif de 02_Subsets_SNAP_QGIS). Sirve para COMPARAR sensores; los archivos llevan el sufijo _rango_fijo.

La figura PNG lleva coordenadas UTM 21 S (km), barra de escala y flecha de
norte; la cita de la fuente va al pie, tomada de <SITIO>_pila_bandas.csv
(organismo, sensor, producto y fecha), cortada en renglones para que no se
salga de la figura.

Los sensores de una sola polarizacion (NovaSAR HH) se exportan en gris (dB).

SALIDA (por sensor y fecha)
  Tp2_SAR_multibanda/05_Resultados/02_Rasters/<SITIO>_RGB_<sensor>.tif   (8 bits, 3 bandas)
  Tp2_SAR_multibanda/05_Resultados/05_Graficos/<SITIO>_RGB_<sensor>.png  (con la cita "Fuente" al pie)

USO
    python Tp2_02_rgb_copol_cruzada_cociente.py --sitio A2_IBICUY
    python Tp2_02_rgb_copol_cruzada_cociente.py --sitio A2_IBICUY --rango_fijo
"""
import argparse
import os
import re
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import SITIOS, ruta_tp                       # noqa: E402
from funciones_comunes import leer_tif, lin_a_db, Bitacora            # noqa: E402

# HH con VH: para BIOMASS, cuyo canal HV trae interferencia de radiofrecuencia sin corregir en el producto de
# origen; en retrodispersion HV y VH miden lo mismo, y el VH llega limpio (ver NOTAS_TECNICAS.md).
PARES = [("VV", "VH"), ("HH", "HV"), ("HH", "VH")]
# Limites fijos para comparar sensores, en dB: los mismos de 00_COMUN/armar_subsets.py (RANGOS_RGB), con
# los que se hicieron los _RGB_8bit.tif de 02_Subsets_SNAP_QGIS. Asi un mismo color quiere decir lo mismo
# en los RGB de este script y en los que vienen hechos.
RANGO_FIJO = {"copol": (-25.0, 0.0), "cruzada": (-32.0, -8.0), "cociente": (0.0, 15.0)}   # dB


def estirar(x, p0=2, p1=98, limites=None):
    """Lleva x (dB) a 1-255. Con 'limites' usa ese rango fijo; si no, los percentiles p0 y p1."""
    v = x[np.isfinite(x)]
    if v.size == 0:
        return np.zeros(x.shape, "uint8"), (np.nan, np.nan)
    lo, hi = limites if limites is not None else np.percentile(v, [p0, p1])
    y = np.clip((x - lo) / (hi - lo + 1e-12), 0, 1)
    y = np.where(np.isfinite(x), y * 254 + 1, 0)       # 0 queda reservado a "sin dato"
    return y.astype("uint8"), (lo, hi)


def promedio_5x5(x):
    """Promedio 5 x 5 en lineal, contando solo los pixeles con dato (banda P)."""
    from scipy.ndimage import uniform_filter
    ok = np.isfinite(x) & (x > 0)
    s = uniform_filter(np.where(ok, x, 0).astype("float64"), size=5, mode="nearest")
    c = uniform_filter(ok.astype("float64"), size=5, mode="nearest")
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(ok & (c > 0), s / c, np.nan).astype("float32")


def guardar_rgb(ruta, rgb, perfil):
    import rasterio

    p = perfil.copy()
    p.update(count=3, dtype="uint8", nodata=0, compress="deflate", predictor=1)
    p.pop("BIGTIFF", None)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with rasterio.open(ruta, "w", **p) as d:
        for i in range(3):
            d.write(rgb[i], i + 1)
        d.colorinterp = [__import__("rasterio").enums.ColorInterp.red,
                         __import__("rasterio").enums.ColorInterp.green,
                         __import__("rasterio").enums.ColorInterp.blue]


def cita_legible(fuente):
    """Quita rutas locales (D:\\...) de la cita: deja solo el nombre del archivo."""
    import re as _re
    return _re.sub(r"[A-Za-z]:\\[^ |;,]*\\([^\\ |;,]+)", r"\1", fuente)


def adornos_mapa(ax, transform, alto, ancho):
    """Coordenadas UTM en km, barra de escala y flecha de norte (fuera del dato, sobre fondo blanco)."""
    from matplotlib.ticker import FuncFormatter
    x0, y0 = transform.c, transform.f
    px = transform.a
    ax.set_xlim(0, ancho)
    ax.set_ylim(alto, 0)
    paso_km = 5
    xs = np.arange(np.ceil(x0 / 5000) * 5000, x0 + ancho * px, paso_km * 1000)
    ys = np.arange(np.ceil((y0 - alto * px) / 5000) * 5000, y0, paso_km * 1000)
    ax.set_xticks((xs - x0) / px)
    ax.set_xticklabels(["%d" % (v / 1000) for v in xs], fontsize=8)
    ax.set_yticks((y0 - ys) / px)
    ax.set_yticklabels(["%s" % format(int(v / 1000), ",").replace(",", ".") for v in ys], fontsize=8)
    ax.set_xlabel("Este (km, UTM 21 S)", fontsize=8)
    ax.set_ylabel("Norte (km, UTM 21 S)", fontsize=8)
    # barra de escala de 5 km abajo a la izquierda, sobre un recuadro blanco
    largo = 5000 / px
    xb, yb = ancho * 0.05, alto * 0.95
    ax.add_patch(__import__("matplotlib").patches.Rectangle((xb - ancho * 0.02, yb - alto * 0.045), largo + ancho * 0.06,
                                                            alto * 0.075, color="white", alpha=0.85, zorder=4))
    ax.plot([xb, xb + largo], [yb, yb], color="black", lw=3, zorder=5)
    ax.text(xb + largo / 2, yb - alto * 0.012, "5 km", ha="center", va="bottom", fontsize=8, zorder=6)
    # flecha de norte arriba a la derecha
    xn, yn = ancho * 0.93, alto * 0.05
    ax.add_patch(__import__("matplotlib").patches.Rectangle((xn - ancho * 0.035, yn - alto * 0.01), ancho * 0.07,
                                                            alto * 0.1, color="white", alpha=0.85, zorder=4))
    ax.annotate("N", xy=(xn, yn + alto * 0.005), xytext=(xn, yn + alto * 0.07), ha="center", va="center",
                fontsize=9, fontweight="bold", zorder=6,
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.5))


def png(ruta, rgb, titulo, fuente, transform=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import textwrap

    img = np.dstack(rgb) if rgb.ndim == 3 else rgb
    alto, ancho = img.shape[:2]
    lineas = textwrap.wrap("Fuente: " + cita_legible(fuente), 110)
    pie = 0.25 + 0.17 * len(lineas)
    fig = plt.figure(figsize=(8, 8 * alto / ancho + 1.0 + pie))
    ax = fig.add_axes([0.1, (pie + 0.6) / fig.get_figheight(), 0.85, 8 * alto / ancho / fig.get_figheight() * 0.85])
    ax.imshow(img, cmap="gray" if img.ndim == 2 else None, interpolation="nearest")
    if transform is not None:
        adornos_mapa(ax, transform, alto, ancho)
    else:
        ax.set_axis_off()
    ax.set_title(titulo, fontsize=11)
    fig.text(0.02, 0.02, "\n".join(lineas), fontsize=8, va="bottom", family=["Arial", "DejaVu Sans"])
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    fig.savefig(ruta, dpi=150, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", required=True, choices=list(SITIOS.keys()))
    ap.add_argument("--rango_fijo", action="store_true",
                    help="mismos limites en dB para todos los sensores (para comparar brillos entre RGB)")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp2", "05_Resultados", "06_Control_calidad"), "Tp2_02_%s" % a.sitio)
    sufijo = "_rango_fijo" if a.rango_fijo else ""
    if a.rango_fijo:
        log("Rango fijo para todos los sensores: copol %s, cruzada %s, cociente %s dB"
            % (RANGO_FIJO["copol"], RANGO_FIJO["cruzada"], RANGO_FIJO["cociente"]))
    pila = ruta_tp("Tp2", "02_Subsets_SNAP_QGIS", "%s_pila_gamma0_lineal.tif" % a.sitio)
    capas, perfil, _ = leer_tif(pila)
    tabla = pd.read_csv(pila.replace("_pila_gamma0_lineal.tif", "_pila_bandas.csv"), encoding="utf-8-sig")
    fuentes = dict(zip(tabla.banda, tabla.fuente))

    hechos = set()
    for nombre in capas:
        for co, cr in PARES:
            if ("_%s" % co) not in nombre:
                continue
            gemela = nombre.replace("_%s" % co, "_%s" % cr)
            if gemela not in capas or nombre in hechos:
                continue
            hechos.update([nombre, gemela])
            etiqueta = re.sub(r"_gamma0|_sigma0", "", nombre.replace("_%s" % co, ""))
            co_l, cr_l = capas[nombre], capas[gemela]
            if "BIOMASS" in nombre:
                co_l, cr_l = promedio_5x5(co_l), promedio_5x5(cr_l)
                log("%-28s banda P: intensidades promediadas 5 x 5 en lineal antes del RGB" % etiqueta)
            co_db, cr_db = lin_a_db(co_l), lin_a_db(cr_l)
            coc_db = co_db - cr_db
            lim = RANGO_FIJO if a.rango_fijo else {"copol": None, "cruzada": None, "cociente": None}
            r, (r0, r1) = estirar(co_db, limites=lim["copol"])
            gch, (g0, g1) = estirar(cr_db, limites=lim["cruzada"])
            b, (b0, b1) = estirar(coc_db, limites=lim["cociente"])
            rgb = np.stack([r, gch, b])
            tif = ruta_tp("Tp2", "05_Resultados", "02_Rasters", "%s_RGB_%s%s.tif" % (a.sitio, etiqueta, sufijo))
            guardar_rgb(tif, rgb, perfil)
            png(tif.replace("02_Rasters", "05_Graficos").replace(".tif", ".png"), rgb,
                "%s  RGB = %s - %s - %s/%s (dB)" % (etiqueta, co, cr, co, cr),
                fuentes.get(nombre, ""), perfil.get("transform"))
            log("%-28s R=%s [%.1f, %.1f] dB  G=%s [%.1f, %.1f] dB  B=%s/%s [%.1f, %.1f] dB"
                % (etiqueta, co, r0, r1, cr, g0, g1, co, cr, b0, b1))
    for nombre in capas:
        if nombre not in hechos:
            gris, (l0, l1) = estirar(lin_a_db(capas[nombre]))
            png(ruta_tp("Tp2", "05_Resultados", "05_Graficos", "%s_gris_%s.png" % (a.sitio, nombre)),
                gris, "%s (dB, una sola polarizacion)" % nombre, fuentes.get(nombre, ""), perfil.get("transform"))
            log("%-28s gris [%.1f, %.1f] dB (una sola polarizacion)" % (nombre, l0, l1))
    log.cerrar("python Tp2_03_respuesta_por_cubierta.py --sitio %s" % a.sitio)


if __name__ == "__main__":
    main()
