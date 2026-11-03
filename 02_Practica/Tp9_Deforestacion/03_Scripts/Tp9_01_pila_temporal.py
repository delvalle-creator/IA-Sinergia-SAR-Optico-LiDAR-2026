# -*- coding: utf-8 -*-
"""
Tp9_01_pila_temporal.py   [SE CORRE]   Tp9, paso 1 de la guia - Deforestacion y degradacion
===================================================================================
Pregunta: donde se perdio monte y donde se degrado bajo el dosel.
Sitio: C_FEDERAL (Espinal). La banda P (BIOMASS de Federal) la evalua Tp9_02, parte B.

Arma la pila MULTITEMPORAL y MULTIBANDA en una grilla de 20 m. Se elige 20 m
porque es el pixel de NISAR GCOV; el mosaico de ALOS-2 es de 25 m y se lleva a
20 m promediando potencia (se declara: no agrega detalle que no tiene):

  L  ALOS-1 PALSAR FBS 13/03/2011 (RTC de ASF, 12,5 m)    --alos1_hh [--alos1_hv]
     (FBS es de UNA polarizacion: HH. El HV de 2011 solo existe en escenas FBD;
      si no se consigue, la comparacion 2011 se hace en HH y se declara.)
  L  ALOS-2 mosaico 2021 (JAXA, Planetary Computer)       automatico
  L  NISAR GCOV 17/09/2026 (ASF, bajado con Tp1_04)       --nisar_h5
  C  Sentinel-1 RTC 10/08/2021 y 14/09/2026              automatico (orbita 68 en las dos)
  S  NovaSAR-1 22/12/2023 (escena 50896, cubre el 51 % del sitio)  automatico
  O  Sentinel-2 NDVI 06/08/2021 y 16/09/2026              automatico

CALIBRACION CRUZADA (guia teorico-practica, seccion 12.3)
  ALOS-1, ALOS-2 y NISAR son tres instrumentos distintos. Antes de restar
  sus gamma0 se mide el desfase en ZONAS ESTABLES (monte que el grupo confirma
  sin cambio, clase 3, y urbano, clase 7, de la cobertura de control) y se corrige:
     desfase = mediana(gamma0_referencia_dB - gamma0_otro_dB) en zona estable
  La referencia es ALOS-2 2021. El desfase SE CORRIGE: no es el limite de
  deteccion. Lo que limita la interpretacion es el RESIDUO que queda despues
  de corregir, y se mide en controles INDEPENDIENTES de los usados para
  calibrar: los cuadrados de la zona estable se reparten al azar en dos mitades
  (semilla fija, --semilla); con una mitad se calcula el desfase y en la otra
  se mide el residuo (y al reves). Se informa por separado en monte (3), en
  ciudad (7) y en las dos, con el rango intercuartil. El cambio minimo
  interpretable es aproximadamente el percentil 75 del residuo absoluto.
  El desfase que se APLICA a la pila sigue siendo el de las dos zonas juntas.

SALIDA
  Tp9_Deforestacion/02_Subsets_SNAP_QGIS/C_pila_temporal_<pixel>m.tif
  Tp9_Deforestacion/05_Resultados/04_Tablas/C_calibracion_cruzada.csv

USO
    python Tp9_01_pila_temporal.py --pixel 20 --alos1_hh D:\\...\\AP_27336_FBS_F6560_RT1_HH.tif ^
        --nisar_h5 D:\\...\\NISAR_L2_PR_GCOV_030_161_A_162_2005_DHDH_A_20260917T095508_....h5
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
from funciones_comunes import (grilla_sitio, buscar_stac, fecha_item, s1_rtc, alos2_mosaico, agrupar_por_pasada,  # noqa: E402
                               nisar_gcov_en_grilla, novasar_sigma0, s2_reflectancia,
                               s2_mascara_valida, leer_en_grilla, lin_a_db, db_a_lin,
                               guardar_tif, Bitacora, fuente_mpc)
from funciones_cambio import indice_normalizado                       # noqa: E402

SITIO = "C_FEDERAL"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pixel", type=float, default=20.0)
    ap.add_argument("--alos1_hh", default="")
    ap.add_argument("--alos1_hv", default="")
    ap.add_argument("--nisar_h5", default="")
    ap.add_argument("--fechas_c", nargs="*", default=["2021-08-10", "2026-09-14"])
    ap.add_argument("--fechas_opt", nargs="*", default=["2021-08-06", "2026-09-16"])
    ap.add_argument("--anio_alos2", default="2021")
    ap.add_argument("--novasar", default="50896")
    ap.add_argument("--solo_urbano", action="store_true")
    ap.add_argument("--desplazamiento", type=float, nargs=2, default=(0.0, 0.0), metavar=("DX", "DY"),
                    help="correccion de NovaSAR en m (Tp3_02): DX positivo = este, DY positivo = norte")
    ap.add_argument("--puntos_enlace", choices=("esquinas", "todos"), default="esquinas",
                    help="georreferencia de NovaSAR: esquinas (4 GCP del image_HH.tif, ajuste afin) o "
                         "todos (84 puntos de enlace del metadata.xml)")
    ap.add_argument("--semilla", type=int, default=20261027,
                    help="semilla del reparto de los cuadrados estables en dos mitades (calibrar / controlar)")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp9", "05_Resultados", "06_Control_calidad"), "Tp9_01_pila")
    g = grilla_sitio(SITIO, pixel=a.pixel)
    capas, fu = {}, []

    def poner(n, x, f):
        if x is not None and np.isfinite(x).mean() > 0.05:
            capas[n] = x.astype("float32")
            fu.append(f)
            log("  %-26s %5.1f %% con dato" % (n, 100 * np.isfinite(x).mean()))

    log.titulo("Banda L")
    its = buscar_stac("alos-palsar-mosaic", SITIO, "%s-01-01" % a.anio_alos2, "%s-12-31" % a.anio_alos2)
    for pol in ("HH", "HV"):
        acc = None
        for it in its:
            x = alos2_mosaico(it, pol, g)
            acc = x if acc is None else np.where(np.isnan(acc), x, acc)
        poner("L_ALOS2_%s_%s" % (a.anio_alos2, pol), acc,
              fuente_mpc("JAXA", "ALOS-2 PALSAR-2 mosaico anual 25 m", a.anio_alos2))
    if a.alos1_hh:
        poner("L_ALOS1_2011_HH", leer_en_grilla(a.alos1_hh, g, "average"),
              "JAXA - ASF DAAC. ALOS PALSAR FBS RTC 12,5 m (ASF: https://search.asf.alaska.edu)")
    if a.alos1_hv:
        poner("L_ALOS1_2011_HV", leer_en_grilla(a.alos1_hv, g, "average"),
              "JAXA - ASF DAAC. ALOS PALSAR FBD RTC 12,5 m")
    if a.nisar_h5:
        for t, p in (("HHHH", "HH"), ("HVHV", "HV")):
            try:
                poner("L_NISAR_2026_%s" % p, nisar_gcov_en_grilla(a.nisar_h5, g, t, "LSAR"),
                      "NASA - ISRO. NISAR L2 GCOV %s. ASF DAAC: https://search.asf.alaska.edu" % os.path.basename(a.nisar_h5))
            except ValueError as e:
                log("  NISAR: %s" % e)

    log.titulo("Banda C")
    for f in a.fechas_c:
        it = buscar_stac("sentinel-1-rtc", SITIO, f, f)
        if it:
            it = agrupar_por_pasada(it)        # todos los cuadros de la pasada, unidos
            ff, hh = fecha_item(it[0])
            for p in ("vv", "vh"):
                poner("C_S1_%s_%s" % (ff[:4], p.upper()), s1_rtc(it[0], p, g),
                      fuente_mpc("ESA - Copernicus", "Sentinel-1 IW GRD RTC", ff, hh))
        else:
            log("  Sin Sentinel-1 RTC el %s" % f)

    log.titulo("Banda S")
    try:
        s0, k = novasar_sigma0(a.novasar, g, desplazamiento_m=tuple(a.desplazamiento), puntos_enlace=a.puntos_enlace)
        log("  NovaSAR georreferenciado con %s." % ("los 4 puntos de esquina del image_HH.tif"
            if a.puntos_enlace == "esquinas" else "los puntos de enlace del metadata.xml"))
        if list(a.desplazamiento) == [0.0, 0.0]:
            log("  AVISO: NovaSAR sin --desplazamiento. Con las 4 esquinas el desfase es de cientos de metros;")
            log("  con --puntos_enlace todos queda chico: midalo en QGIS y paselo con --desplazamiento DX DY.")
        poner("S_NovaSAR_2023_sigma0_HH", s0, "SSTL - CSIRO. NovaSAR-1 GRD HH escena %s (22/12/2023), sigma0 = DN^2/%.0e" % (a.novasar, k))
    except Exception as e:                           # noqa: BLE001
        log("  NovaSAR: %s" % str(e)[:120])

    log.titulo("Optico")
    for f in a.fechas_opt:
        its2 = buscar_stac("sentinel-2-l2a", SITIO, f, f)
        if not its2:
            log("  Sin Sentinel-2 el %s" % f)
            continue
        nd = None
        for it in its2:
            v, _, _ = s2_mascara_valida(it, g)
            x = np.where(v, indice_normalizado(s2_reflectancia(it, "B08", g), s2_reflectancia(it, "B04", g)), np.nan)
            nd = x if nd is None else np.where(np.isnan(nd), x, nd)
        ff, hh = fecha_item(its2[0])
        poner("O_NDVI_%s" % ff[:4], nd, fuente_mpc("ESA - Copernicus", "Sentinel-2 MSI L2A, NDVI", ff, hh))

    # ---------------------------------------------------- calibracion cruzada
    log.titulo("Calibracion cruzada de la banda L en zona estable")
    cc = ruta_tp("Tp4", "02_Subsets_SNAP_QGIS", "%s_cobertura_control_%dm.tif" % (SITIO, a.pixel))
    filas = []
    if os.path.exists(cc):
        ctrl = leer_en_grilla(cc, g, "nearest", banda=1)
        # Zona estable: urbano (7) y los poligonos de monte que el grupo CONFIRMO sin cambio
        # 2011-2026 en la imagen de muy alta resolucion (cargados como clase 3 en el control).
        # Si el monte del control no se confirmo, usar solo urbano: --solo_urbano.
        estable = np.isin(ctrl, [7] if a.solo_urbano else [3, 7])
        try:                                         # banda 2 = fuente_control (1 = digitalizado por el grupo)
            fte = leer_en_grilla(cc, g, "nearest", banda=2)
            no_conf = (ctrl == 3) & (fte != 1)
            if no_conf.any() and not a.solo_urbano:
                log("Monte de la cobertura de control que NO digitalizo el grupo (MapBiomas): %d pixeles, "
                    "fuera de la zona estable (no esta confirmado sin cambio)." % no_conf.sum())
                estable &= ~no_conf
        except Exception:                            # noqa: BLE001
            pass
        log("Zona estable: clases %s de la cobertura de control: %d pixeles"
            % ("7 (urbano)" if a.solo_urbano else "3 (monte confirmado) y 7 (urbano)", estable.sum()))
        if estable.sum() < 100:
            log("Menos de 100 pixeles estables: NO se calibra y se declara.")
        # cada cuadrado estable con su numero (para repartirlos en dos mitades)
        from scipy import ndimage
        cuad, ncuad = ndimage.label(estable)
        rng = np.random.default_rng(a.semilla)
        mitad = np.zeros(ncuad + 1, int)
        for c in (3, 7):
            ids = np.unique(cuad[estable & (ctrl == c)])
            ids = ids[ids > 0]
            rng.shuffle(ids)
            mitad[ids[: len(ids) // 2]] = 1
            mitad[ids[len(ids) // 2:]] = 2
        log("Cuadrados estables: %d, repartidos al azar en dos mitades (semilla %d) para medir el residuo."
            % (ncuad, a.semilla))
        for pol in ("HH", "HV"):
            ref = "L_ALOS2_%s_%s" % (a.anio_alos2, pol)
            if ref not in capas:
                continue
            for otro in [k for k in capas if k.startswith("L_") and k.endswith(pol) and k != ref]:
                ok = estable & np.isfinite(capas[ref]) & np.isfinite(capas[otro])
                if ok.sum() < 100:
                    continue
                d = lin_a_db(capas[ref]) - lin_a_db(capas[otro])
                desf = float(np.nanmedian(d[ok]))
                for zona, cl in (("monte (3)", [3]), ("ciudad (7)", [7]), ("las dos", [3, 7])):
                    k = ok & np.isin(ctrl, cl)
                    if k.sum() < 20:
                        continue
                    kA, kB = k & (mitad[cuad] == 1), k & (mitad[cuad] == 2)
                    res = np.concatenate([d[kB] - np.median(d[kA]), d[kA] - np.median(d[kB])]) \
                        if kA.sum() and kB.sum() else np.array([np.nan])
                    q25, q50, q75 = np.percentile(d[k], [25, 50, 75])
                    p75 = float(np.nanpercentile(np.abs(res), 75))
                    filas.append({"referencia": ref, "producto": otro, "zona": zona, "desfase_dB": round(q50, 2),
                                  "RIC_desfase_dB": "%+.2f a %+.2f" % (q25, q75), "pixeles_estables": int(k.sum()),
                                  "residuo_p75_abs_dB": round(p75, 2),
                                  "aplicado": "si" if zona == "las dos" else "no (solo se informa)",
                                  "aviso": "cambio minimo interpretable ~ %.1f dB (p75 del residuo absoluto en la otra mitad)" % p75})
                    log("  %-22s %-11s desfase %+.2f dB (RIC %+.2f a %+.2f); residuo en controles independientes: p75 |res| = %.2f dB"
                        % (otro, zona, q50, q25, q75, p75))
                capas[otro] = capas[otro] * db_a_lin(desf)
                log("  %-22s respecto de %s: desfase aplicado %+.2f dB (corregido)" % (otro, ref, desf))
        log("El desfase se corrige; lo que limita la interpretacion es el residuo (columna residuo_p75_abs_dB).")
        log("Si el desfase difiere entre monte y ciudad, un ajuste unico no vale para todo el sitio: declararlo.")
    else:
        log("No hay cobertura de control (Tp4_01 para C_FEDERAL): NO se calibra y se declara.")
    tabla = ruta_tp("Tp9", "05_Resultados", "04_Tablas", "C_calibracion_cruzada.csv")
    os.makedirs(os.path.dirname(tabla), exist_ok=True)
    pd.DataFrame(filas).to_csv(tabla, index=False, encoding="utf-8-sig")
    out = ruta_tp("Tp9", "02_Subsets_SNAP_QGIS", "C_pila_temporal_%dm.tif" % a.pixel)
    guardar_tif(out, capas, g, " | ".join(sorted(set(fu))), "Pila temporal multibanda (radar lineal, NDVI)")
    log("")
    log("Pila:", out, "(%d capas)" % len(capas))
    log.cerrar("python Tp9_02_sinergia_estratos.py --pixel %d" % a.pixel)


if __name__ == "__main__":
    main()
