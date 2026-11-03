# -*- coding: utf-8 -*-
"""
Tp2_04_control_zona_estable.py   [SE CORRE]   Tp2, paso 8 de la guia
======================================================================
El control de calidad del Tp2 (presentacion 01, diapositiva 25):

    "una zona estable conserva gamma0 entre fechas (diferencia menor que 1 dB)"

Una zona estable es una superficie que no cambio entre las dos fechas: el
interior de una ciudad, una ruta, una playa de estacionamiento. Si alli dos
productos del MISMO sensor y la MISMA polarizacion difieren mas de 1 dB, el
problema no es el paisaje: es la calibracion, la normalizacion (sigma0 contra
gamma0), la orbita o el corregistro.

Se compara cada par de bandas de la pila que sean del mismo sensor y la
misma polarizacion, de fechas distintas Y DE LA MISMA PASADA Y TRAZA (columnas
"pasada" y "traza" de <SITIO>_pila_bandas.csv), o el par que se pida con --a y
--b (por ejemplo, el gamma0 de Sentinel-1 hecho en SNAP contra el RTC del
Planetary Computer del mismo dia). En una zona estable urbana el doble rebote
depende de la direccion de mirada: entre una pasada ascendente y una
descendente la diferencia es de GEOMETRIA, no de calibracion, y ese par no se
usa como control (se informa que se salto). Si la pasada de alguna de las dos
no se conoce (productos de SNAP con --extra), el par se evalua y se marca
"geometria no verificada".

Las medias se calculan en LINEAL y se informan en dB. Tambien se informa la
dispersion de la diferencia pixel a pixel (desviacion estandar, en dB): con
speckle sin filtrar es grande aunque las medias coincidan.

Diferencia POR POLIGONO (agregado el 27/10/2026). Los pixeles de un poligono no
son observaciones independientes: con cuatro poligonos, lo que de verdad se
repite son cuatro diferencias. Por eso, ademas de la diferencia de medias de
todos los pixeles, se informa la diferencia de cada poligono, la menor y la mayor,
y un intervalo del 95 % por remuestreo de poligonos (bootstrap: se sortean 2.000
veces cuatro poligonos con reposicion, con semilla fija, y se toman los
percentiles 2,5 y 97,5 de la diferencia). Con cuatro poligonos el intervalo es
orientativo, no una prueba.

El umbral de 1 dB. Es del orden de la exactitud radiometrica absoluta que
especifican las misiones: 1 dB (3 sigma) para Sentinel-1 y una calibracion
absoluta de 1 dB para NISAR. Una diferencia mayor que eso entre dos productos de
una zona que no cambio no se explica por la calibracion del sensor.

Que zona usar para cada par (--clase acepta una o varias clases):
  - entre FECHAS (por ejemplo NISAR 18 y 30/09): la zona estable urbana, que no
    cambia con la humedad ni con la vegetacion (por defecto, --clase estable);
  - entre PROCESADORES de la misma adquisicion (RTC frente a SNAP del mismo dia):
    la escena es la misma, y cualquier cubierta homogenea y distribuida sirve.
    Lo urbano es la PEOR eleccion: reflectores puntuales, sensibles al filtro de
    speckle y a un corrimiento de 15 m. Use, por ejemplo,
    --clase monte_o_bosque pajonal agua_calma

ENTRADA: los poligonos de clase "estable" (u otras, con --clase) de cubiertas_<SITIO>.gpkg (guia, paso 6).

SALIDA
  Tp2_SAR_multibanda/05_Resultados/04_Tablas/<SITIO>_control_zona_estable.csv
     una fila por par y por clase, con la diferencia de medias, el desvio pixel
     a pixel, la diferencia de cada poligono, su minimo y maximo y el intervalo
     por remuestreo de poligonos.
  Con --sufijo X el archivo y la bitacora llevan _X al final y no pisan los de
  otra corrida (por ejemplo --sufijo NISAR o --sufijo C_S1_vs_SNAP_VV).

USO
    python Tp2_04_control_zona_estable.py --sitio A2_IBICUY --sufijo NISAR
    python Tp2_04_control_zona_estable.py --sitio A2_IBICUY --a C_S1_gamma0_VV --b C_SNAP_gamma0_VV --sufijo C_S1_vs_SNAP_VV
    python Tp2_04_control_zona_estable.py --sitio A2_IBICUY --a C_S1_gamma0_VV --b C_SNAP_gamma0_VV ^
           --clase monte_o_bosque pajonal agua_calma --sufijo C_S1_vs_SNAP_VV_homogeneas
"""
import argparse
import itertools
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
from funciones_comunes import (leer_tif, grilla_de_tif, lin_a_db,      # noqa: E402
                               media_lineal_db, Bitacora)

UMBRAL_DB = 1.0          # exactitud radiometrica absoluta del orden de 1 dB (Sentinel-1 y NISAR)
N_REMUESTREOS = 2000     # sorteos del intervalo por remuestreo de poligonos
SEMILLA = 20261022       # semilla fija: el intervalo sale igual en cada corrida


def main():
    import geopandas as gpd
    from rasterio import features

    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", required=True, choices=list(SITIOS.keys()))
    ap.add_argument("--a", default="")
    ap.add_argument("--b", default="")
    ap.add_argument("--clase", nargs="+", default=["estable"],
                    help="clase o clases de cubiertas_<SITIO>.gpkg donde se compara (por defecto: estable)")
    ap.add_argument("--sufijo", default="", help="se agrega al nombre de la tabla y de la bitacora")
    a = ap.parse_args()
    suf = ("_" + a.sufijo) if a.sufijo else ""
    log = Bitacora(ruta_tp("Tp2", "05_Resultados", "06_Control_calidad"), "Tp2_04_%s%s" % (a.sitio, suf))

    pila = ruta_tp("Tp2", "02_Subsets_SNAP_QGIS", "%s_pila_gamma0_lineal.tif" % a.sitio)
    capas, _, _ = leer_tif(pila)
    g = grilla_de_tif(pila)
    vec = ruta_tp("Tp2", "04_Tablas_de_trabajo", "cubiertas_%s.gpkg" % a.sitio)
    if not os.path.exists(vec):
        log("Falta %s: correr antes Tp2_03 (crea la capa) y digitalizar la clase '%s' (guia, paso 6)."
            % (vec, ", ".join(a.clase)))
        log.cerrar()
        return
    pol = gpd.read_file(vec, layer="cubiertas").to_crs(g["crs"])
    todas = pol
    pol = pol[pol["clase"].isin(a.clase)].reset_index(drop=True)
    if pol.empty:
        log("No hay poligonos de clase %s en %s. Clases que si hay: %s."
            % (", ".join(a.clase), vec, ", ".join(sorted(todas["clase"].unique()))))
        log.cerrar()
        return
    # Cada poligono con su numero (1, 2, ... en el orden de la capa): la diferencia se calcula tambien por poligono.
    idp = features.rasterize(((geom, i + 1) for i, geom in enumerate(pol.geometry)),
                             out_shape=(g["height"], g["width"]), transform=g["transform"],
                             fill=0, dtype="int32")
    rng = np.random.default_rng(SEMILLA)

    geom = {}
    tabla_b = pila.replace("_pila_gamma0_lineal.tif", "_pila_bandas.csv")
    if os.path.exists(tabla_b):
        tb = pd.read_csv(tabla_b, encoding="utf-8-sig", dtype=str).fillna("")
        for _, r in tb.iterrows():
            geom[r.banda] = (r.get("pasada", ""), r.get("traza", ""))

    def misma_geometria(x, y):
        gx, gy = geom.get(x, ("", "")), geom.get(y, ("", ""))
        if not all(gx) or not all(gy):
            return None                        # no se sabe
        return gx == gy

    if a.a and a.b:
        pares = [(a.a, a.b)]
    else:
        base = lambda n: re.sub(r"_\d{8}$", "", n)          # noqa: E731
        pares = []
        for x, y in itertools.combinations(capas, 2):
            if base(x) != base(y):
                continue
            if misma_geometria(x, y) is False:
                log("%s vs %s: pasadas distintas (%s%s / %s%s): la diferencia seria de geometria, "
                    "no de calibracion. NO se usa como control." % (x, y, *geom[x], *geom[y]))
                continue
            pares.append((x, y))
    if not pares:
        log("No hay en la pila dos fechas del mismo sensor, polarizacion y pasada. Pida el par con --a y --b.")
    filas = []
    for x, y in pares:
        for clase in a.clase:
            ids = [i for i in range(len(pol)) if pol.loc[i, "clase"] == clase]
            m = np.isin(idp, [i + 1 for i in ids])
            ok = m & np.isfinite(capas[x]) & np.isfinite(capas[y])
            n = int(ok.sum())
            if n < 50:
                log("%s vs %s, clase %s: solo %d pixeles en comun; no se evalua." % (x, y, clase, n))
                continue
            dmed = media_lineal_db(capas[x][ok]) - media_lineal_db(capas[y][ok])
            dpix = lin_a_db(capas[x][ok]) - lin_a_db(capas[y][ok])
            # diferencia de cada poligono (medias en lineal, diferencia en dB)
            dpol, sx, sy = [], [], []
            for i in ids:
                k = (idp == i + 1) & np.isfinite(capas[x]) & np.isfinite(capas[y])
                if k.sum() < 10:
                    continue
                sx.append(np.nanmean(capas[x][k])); sy.append(np.nanmean(capas[y][k]))
                dpol.append(10 * np.log10(sx[-1]) - 10 * np.log10(sy[-1]))
            dpol, sx, sy = np.array(dpol), np.array(sx), np.array(sy)
            if dpol.size >= 2:
                # remuestreo de poligonos: se sortean len(dpol) poligonos con reposicion y se recalcula la
                # diferencia de las medias lineales de los poligonos sorteados
                idx = rng.integers(0, dpol.size, size=(N_REMUESTREOS, dpol.size))
                boot = 10 * np.log10(sx[idx].mean(axis=1)) - 10 * np.log10(sy[idx].mean(axis=1))
                ic = (float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5)))
            else:
                ic = (np.nan, np.nan)
            veredicto = "CUMPLE" if abs(dmed) < UMBRAL_DB else "NO CUMPLE: revisar calibracion, normalizacion u orbita"
            mg = misma_geometria(x, y)
            if mg is None:
                veredicto += " (geometria no verificada: falta la pasada de alguna banda)"
            elif mg is False:
                veredicto += " (OJO: pasadas distintas, pedido con --a y --b: puede ser geometria)"
            filas.append({"banda_a": x, "banda_b": y, "clase": clase, "n_pixeles": n, "n_poligonos": int(dpol.size),
                          "pasada_traza_a": "".join(geom.get(x, ("", ""))), "pasada_traza_b": "".join(geom.get(y, ("", ""))),
                          "diferencia_media_dB": round(dmed, 2),
                          "desvio_pixel_a_pixel_dB": round(float(np.nanstd(dpix)), 2),
                          "diferencia_por_poligono_dB": " ; ".join("%+.2f" % v for v in dpol),
                          "diferencia_poligono_min_dB": round(float(dpol.min()), 2) if dpol.size else np.nan,
                          "diferencia_poligono_max_dB": round(float(dpol.max()), 2) if dpol.size else np.nan,
                          "ic95_remuestreo_poligonos_dB": "%+.2f a %+.2f" % ic if np.isfinite(ic[0]) else "",
                          "umbral_dB": UMBRAL_DB, "veredicto": veredicto})
            # Dos renglones: el resumen y, debajo, la diferencia de cada poligono con su intervalo.
            log("%-28s - %-28s %-14s n=%5d  dif. media %+5.2f dB  desvio %4.2f dB  -> %s"
                % (x, y, clase, n, dmed, np.nanstd(dpix), veredicto))
            log("      por poligono: %s dB   IC 95 %% (remuestreo de %d poligonos): %s dB"
                % (" / ".join("%+.2f" % v for v in dpol), dpol.size,
                   filas[-1]["ic95_remuestreo_poligonos_dB"] or "sin dato"))
    out = ruta_tp("Tp2", "05_Resultados", "04_Tablas", "%s_control_zona_estable%s.csv" % (a.sitio, suf))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pd.DataFrame(filas).to_csv(out, index=False, encoding="utf-8-sig")
    log("")
    log("Tabla:", out)
    log.cerrar("responder las preguntas del Tp2 y pasar al Tp3")


if __name__ == "__main__":
    main()
