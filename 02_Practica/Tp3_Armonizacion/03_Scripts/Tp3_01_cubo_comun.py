# -*- coding: utf-8 -*-
"""
Tp3_01_cubo_comun.py   [SE CORRE]   Tp3, paso 1 de la guia
==================================================
Lleva SAR (pila del Tp2), optico (Sentinel-2 L2A) y, si se pide, el modelo de
elevacion, a UNA grilla y deja escrita la diferencia de fecha entre cada par
de capas. Es la condicion previa de toda fusion (presentacion 01 del curso, los
tres requisitos de la fusion):

    "Antes de combinar: misma grilla, fechas compatibles y una pregunta para
     cada sensor."

Decisiones que el programa toma y DECLARA en la bitacora
  1. La grilla toma el espaciado mas grueso de los productos que se fusionan a
     nivel de pixel (--pixel; aqui 20 m de NISAR GCOV y de B11-B12). Trabajar
     a 10 m inventaria detalle que esos sensores no midieron. Los productos
     mas gruesos que entran igual al cubo (el MDE de 30 m, la banda P de
     BIOMASS de unos 50-60 m en rango de terreno) quedan SOBREMUESTREADOS: el
     programa lo declara capa por capa (columnas resolucion_nativa_m y
     remuestreo de <SITIO>_cubo_<pixel>m_bandas.csv) y no se interpretan en
     detalles menores que su resolucion. Los que no entran (CCI Biomass, FH
     de BIOMASS, MapBiomas) se muestrean en su propia grilla (Tp3_04).
  2. El radar se agrega en LINEAL (promedio de potencia). Nunca en dB.
  3. La reflectancia se agrega promediando; la SCL, por mayoria (modo).
     Los pixeles con nube, sombra o cirro de la SCL quedan sin dato en
     TODAS las bandas opticas. La bitacora informa cuantos pixeles aporta
     cada clase valida, en particular la 7 (sin clasificar, que puede ser
     borde de nube) y la 11 (nieve); con --excluir_scl7 la clase 7 tambien
     queda sin dato.
  4. Las bandas de 20 m de Sentinel-2 (B11, B12) no se "afinan" a 10 m.

SALIDA
  Tp3_Armonizacion/02_Subsets_SNAP_QGIS/<SITIO>_cubo_<pixel>m.tif
  Tp3_Armonizacion/02_Subsets_SNAP_QGIS/<SITIO>_cubo_<pixel>m_bandas.csv
  Tp3_Armonizacion/05_Resultados/04_Tablas/<SITIO>_diferencias_de_fecha.csv

USO
    python Tp3_01_cubo_comun.py --sitio A2_IBICUY --fecha_optico 2026-09-16 --pixel 20
    python Tp3_01_cubo_comun.py --sitio A2_IBICUY --fecha_optico 2026-09-16 --pixel 20 --mde
"""
import argparse
import itertools
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import SITIOS, ruta_tp                       # noqa: E402
from funciones_comunes import (grilla_sitio, leer_en_grilla, buscar_stac,  # noqa: E402
                               fecha_item, s2_reflectancia, copdem,
                               guardar_tif, Bitacora, fuente_mpc, CLASES_SCL_VALIDAS)

BANDAS_S2 = ["B02", "B03", "B04", "B08", "B11", "B12"]

# Resolucion nativa (m) de cada familia de capas, para declarar si quedo agregada, igual o sobremuestreada.
# Banda P de BIOMASS: 6 MHz de ancho de banda -> unos 25 m en rango oblicuo y unos 50-60 m en rango de terreno
# (incidencia de 27 a 29 grados en Ibicuy); el L1B DGM viene muestreado a 25 x 22 m, mas fino que su resolucion.
RESOLUCION_NATIVA_M = [("OPT_S2_B11", 20), ("OPT_S2_B12", 20), ("OPT_S2_", 10), ("L_NISAR_", 20), ("S_NISAR_", 20),
                       ("C_S1_", 20), ("C_SNAP_", 20), ("P_BIOMASS_", 55), ("S_NovaSAR_", 6), ("MDE_GLO30", 30)]


def resolucion_nativa(capa):
    for pref, r in RESOLUCION_NATIVA_M:
        if capa.startswith(pref):
            return r
    return np.nan


def remuestreo(capa, pixel):
    r = resolucion_nativa(capa)
    if not np.isfinite(r):
        return "sin dato"
    if r < pixel:
        return "agregada (promedio)"
    if r == pixel:
        return "igual"
    return "SOBREMUESTREADA: no interpretar detalles menores que %g m" % r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", required=True, choices=list(SITIOS.keys()))
    ap.add_argument("--pixel", type=float, default=20.0)
    ap.add_argument("--fecha_optico", default="")
    ap.add_argument("--mde", action="store_true", help="agregar Copernicus DEM GLO-30")
    ap.add_argument("--excluir_scl7", action="store_true",
                    help="dejar sin dato tambien la clase 7 de la SCL (sin clasificar)")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp3", "05_Resultados", "06_Control_calidad"), "Tp3_01_%s" % a.sitio)
    g = grilla_sitio(a.sitio, pixel=a.pixel)
    log("Grilla comun: %s, pixel %.0f m, %d x %d" % (g["crs"], a.pixel, g["width"], g["height"]))
    log("Regla aplicada: pixel = el espaciado mas grueso de los productos que se fusionan a nivel de pixel")
    log("(NISAR GCOV y B11-B12, 20 m); radar agregado en LINEAL. Los mas gruesos que entran (MDE, banda P)")
    log("quedan sobremuestreados y se declaran abajo.")
    capas, filas = {}, []

    # ------------------------------------------------ radar (pila del Tp2)
    pila = ruta_tp("Tp2", "02_Subsets_SNAP_QGIS", "%s_pila_gamma0_lineal.tif" % a.sitio)
    if os.path.exists(pila):
        import rasterio
        t = pd.read_csv(pila.replace("_pila_gamma0_lineal.tif", "_pila_bandas.csv"), encoding="utf-8-sig")
        with rasterio.open(pila) as src:
            nombres = list(src.descriptions)
        for i, n in enumerate(nombres, start=1):
            arr = leer_en_grilla(pila, g, "average", banda=i)
            capas[n] = arr
            f = t.loc[t.banda == n].iloc[0]
            filas.append({"capa": n, "sensor": f.sensor, "fecha": f.fecha, "unidad": f.unidad,
                          "fuente": f.fuente, "pixeles_validos_%": round(100 * np.isfinite(arr).mean(), 1)})
            log("  radar  %-28s %s  %5.1f %% con dato" % (n, f.fecha, filas[-1]["pixeles_validos_%"]))
    else:
        log("No existe la pila del Tp2 (%s): el cubo se arma sin radar." % pila)

    # ------------------------------------------------ optico Sentinel-2
    if a.fecha_optico:
        its = buscar_stac("sentinel-2-l2a", a.sitio, a.fecha_optico, a.fecha_optico)
        if not its:
            log("No hay Sentinel-2 L2A el %s sobre el sitio." % a.fecha_optico)
        else:
            # Si el sitio cae en dos teselas el mismo dia, se usa la primera que
            # cubre y se rellena con la segunda (misma pasada, misma geometria).
            scl = None
            refl = {b: None for b in BANDAS_S2}
            for it in its:
                s = leer_en_grilla(it.assets["SCL"].href, g, "mode", nodata_origen=0, tipo="uint8").astype("float32")
                s[s == 0] = np.nan
                scl = s if scl is None else np.where(np.isnan(scl), s, scl)
                for b in BANDAS_S2:
                    r = s2_reflectancia(it, b, g, "average")
                    refl[b] = r if refl[b] is None else np.where(np.isnan(refl[b]), r, refl[b])
            validas = [c for c in CLASES_SCL_VALIDAS if not (a.excluir_scl7 and c == 7)]
            valido = np.isin(scl, validas)
            n_scl = np.isfinite(scl).sum()
            log("  SCL: pixeles por clase valida (%% del sitio con dato): " + ", ".join(
                "%d: %.1f %%" % (c, 100 * (scl == c).sum() / max(n_scl, 1)) for c in CLASES_SCL_VALIDAS))
            if a.excluir_scl7:
                log("  La clase 7 (sin clasificar) queda sin dato (--excluir_scl7).")
            else:
                log("  La clase 7 (sin clasificar) se acepta y se declara; para excluirla: --excluir_scl7.")
            f, h = fecha_item(its[0])
            fu = fuente_mpc("ESA - Copernicus", "Sentinel-2 MSI L2A (%s)" % ", ".join(i.id for i in its), f, h)
            for b in BANDAS_S2:
                arr = np.where(valido, refl[b], np.nan).astype("float32")
                capas["OPT_S2_%s" % b] = arr
                filas.append({"capa": "OPT_S2_%s" % b, "sensor": "Sentinel-2", "fecha": f,
                              "unidad": "reflectancia 0-1", "fuente": fu,
                              "pixeles_validos_%": round(100 * np.isfinite(arr).mean(), 1)})
            log("  optico Sentinel-2 %s: %d teselas, %.1f %% de pixeles utiles (SCL)"
                % (f, len(its), 100 * valido.mean()))

    # ------------------------------------------------ MDE
    if a.mde:
        dem, its = copdem(a.sitio, g)
        capas["MDE_GLO30_m"] = dem
        filas.append({"capa": "MDE_GLO30_m", "sensor": "Copernicus DEM GLO-30", "fecha": "2011-2015",
                      "unidad": "m sobre EGM2008",
                      "fuente": fuente_mpc("ESA - Airbus", "Copernicus DEM GLO-30", "2021"),
                      "pixeles_validos_%": round(100 * np.isfinite(dem).mean(), 1)})
        log("  MDE Copernicus GLO-30: %d teselas" % len(its))

    if not capas:
        log("Nada que apilar.")
        log.cerrar()
        return
    out = ruta_tp("Tp3", "02_Subsets_SNAP_QGIS", "%s_cubo_%dm.tif" % (a.sitio, a.pixel))
    guardar_tif(out, capas, g, " | ".join(sorted(set(f["fuente"] for f in filas))),
                "Cubo armonizado: radar agregado en lineal, optico promediado con mascara SCL")
    tb = pd.DataFrame(filas)
    tb["resolucion_nativa_m"] = [resolucion_nativa(c) for c in tb.capa]
    tb["remuestreo"] = [remuestreo(c, a.pixel) for c in tb.capa]
    tb.to_csv(out.replace(".tif", "_bandas.csv"), index=False, encoding="utf-8-sig")
    log.titulo("Resolucion nativa de cada capa frente al pixel de %g m" % a.pixel)
    for r in tb.itertuples(index=False):
        log("  %-28s %5s m  %s" % (r.capa, "%g" % r.resolucion_nativa_m if np.isfinite(r.resolucion_nativa_m) else "?",
                                    r.remuestreo))

    # ------------------------------------------------ diferencias de fecha
    # una fila por (sensor, fecha): dos fechas de NISAR son dos entradas distintas
    fechas = tb.drop_duplicates(["sensor", "fecha"])[["sensor", "fecha"]]
    dd = []
    for (_, x), (_, y) in itertools.combinations(fechas.iterrows(), 2):
        try:
            dias = abs((pd.Timestamp(x.fecha) - pd.Timestamp(y.fecha)).days)
        except (ValueError, TypeError):
            dias = np.nan
        dd.append({"sensor_1": x.sensor, "fecha_1": x.fecha, "sensor_2": y.sensor,
                   "fecha_2": y.fecha, "diferencia_dias": dias})
    dfd = pd.DataFrame(dd)
    tab = ruta_tp("Tp3", "05_Resultados", "04_Tablas", "%s_diferencias_de_fecha.csv" % a.sitio)
    os.makedirs(os.path.dirname(tab), exist_ok=True)
    dfd.to_csv(tab, index=False, encoding="utf-8-sig")
    log.titulo("Diferencia de fecha entre sensores")
    for _, r in dfd.iterrows():
        log("  %-22s %s  <->  %-22s %s : %s dias" % (r.sensor_1, r.fecha_1, r.sensor_2, r.fecha_2, r.diferencia_dias))
    log("")
    log("Cubo  :", out)
    log("Fechas:", tab)
    log.cerrar("python Tp3_02_medir_corregistro.py --sitio %s --pixel %d" % (a.sitio, a.pixel))


if __name__ == "__main__":
    main()
