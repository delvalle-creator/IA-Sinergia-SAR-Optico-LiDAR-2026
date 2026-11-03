# -*- coding: utf-8 -*-
"""
Tp2_01_pila_multibanda.py   [SE CORRE]   Tp2, paso 4 de la guia (despues de SNAP)
=========================================================================
Arma, sobre UN sitio, la pila de radar en la grilla comun de 10 m con TODAS
las bandas que haya para ese sitio, en LINEAL y con su nombre normalizado:

  C   Sentinel-1 RTC (Planetary Computer)    gamma0 VV, VH          --fecha_c
  S   NISAR S GCOV (ISRO), archivo local     gamma0 HH, HV          automatico
  S   NovaSAR-1 GRD, archivo local           sigma0 HH (*)          --novasar
  L   NISAR L GCOV (NASA), archivo local     gamma0 HH, HV          automatico
  L   SAOCOM o ALOS procesado en SNAP        gamma0 (GeoTIFF)       --extra
  P   BIOMASS L1B (02_Subsets_SNAP_QGIS)     gamma0 ELIPSOIDAL      --extra "...tif#1" (HH) y "#3" (VH; el HV trae RFI)
                                             (sin normalizacion por terreno: unidad "gamma0E")
  X   COSMO-SkyMed procesado en SNAP         sigma0 (GeoTIFF)       --extra

(*) NovaSAR se entrega calibrado a sigma0 y el curso no tiene un modelo de
    angulo local para normalizarlo a gamma0 fuera de SNAP. Se guarda como
    sigma0 y la banda lo dice en su nombre: S_NovaSAR_sigma0_HH. Mezclar
    sigma0 con gamma0 sin decirlo es uno de los errores de la diapositiva 14.

Los productos procesados en SNAP (SAOCOM, BIOMASS, COSMO, Sentinel-1 propio)
se exportan desde SNAP a GeoTIFF (File > Export > GeoTIFF) y se pasan con
--extra "nombre_de_banda=ruta.tif|sensor|lambda_cm|AAAA-MM-DD|unidad|pasada|traza"
(una vez por banda). Despues de la ruta, todos los campos son opcionales, pero
sensor, longitud de onda y fecha deben ponerse siempre, porque el Tp3 arma con
ellos la tabla de fechas. Los tres ultimos se agregaron el 27/10/2026:
  unidad  gamma0 (por defecto: gamma0 normalizado por el terreno, como SNAP con
          Terrain-Flattening), gamma0E (gamma0 sobre el elipsoide, sin
          normalizacion por terreno: BIOMASS L1B) o sigma0.
  pasada  A (ascendente) o D (descendente).
  traza   numero de orbita relativa o traza (por ejemplo 68, 006).
Si pasada y traza no se escriben, el programa las busca en los metadatos del
GeoTIFF (etiquetas PASS/ORBIT_DIRECTION y RELATIVE_ORBIT/TRACK), y si tampoco
estan, quedan vacias y la bitacora lo avisa. Asi la tabla de bandas dice de donde
salio cada dato: completado a mano en la orden, leido del archivo, o sin dato. El programa los lleva a la
grilla comun promediando en lineal; si el GeoTIFF esta en dB (nombre terminado
en _db), lo pasa a lineal en su grilla original y recien despues promedia.

NovaSAR viene georreferenciado con solo 4 puntos de esquina: la correccion
medida con Tp3_02 se aplica con --desplazamiento DX DY (metros; DX positivo =
hacia el este, DY positivo = hacia el norte).

SALIDA
  Tp2_SAR_multibanda/02_Subsets_SNAP_QGIS/<SITIO>_pila_gamma0_lineal.tif
  Tp2_SAR_multibanda/02_Subsets_SNAP_QGIS/<SITIO>_pila_bandas.csv
       (banda, sensor, longitud de onda, fecha, unidad, fuente)

USO
    python Tp2_01_pila_multibanda.py --sitio A2_IBICUY --fecha_c 2026-09-26
    python Tp2_01_pila_multibanda.py --sitio F_BOVRIL --novasar 47974 --fecha_c 2023-09-17
    python Tp2_01_pila_multibanda.py --sitio A1_DELTA_QUEMAS --fecha_c 2020-07-16 ^
           --extra "L_SAOCOM_gamma0_HH=D:\\...\\SAOCOM_20200721_gamma0_HH.tif|SAOCOM-1A|23.5|2020-07-21"
    python Tp2_01_pila_multibanda.py --sitio A2_IBICUY --fecha_c 2026-09-26 ^
           --extra "P_BIOMASS_gamma0E_HH=D:\\...\\A2_IBICUY_BIOMASS_P_20261005.tif#1|BIOMASS|69.0|2026-10-05|gamma0E|A|006"
    python Tp2_01_pila_multibanda.py --sitio F_BOVRIL --novasar 47974 --fecha_c 2023-09-17 --desplazamiento -92 -484
"""
import argparse
import glob
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import (SITIOS, NISAR_DELTA, NOVASAR_ESCENAS, ORIGINALES,  # noqa: E402
                                 ruta_tp)
from funciones_comunes import (grilla_sitio, buscar_stac, fecha_item, agrupar_por_pasada,    # noqa: E402
                               s1_rtc, nisar_gcov_en_grilla, novasar_sigma0,
                               leer_en_grilla, leer_db_como_lineal, media_lineal_db,
                               guardar_tif, Bitacora, fuente_mpc)


# Unidades que acepta el quinto campo de --extra (en minusculas) y lo que se escribe en la tabla de bandas.
UNIDADES_EXTRA = {
    "": "gamma0 lineal",                      # por defecto: gamma0 normalizado por el terreno (SNAP, RTC)
    "gamma0": "gamma0 lineal",
    "gamma0e": "gamma0 elipsoidal lineal",    # sobre el elipsoide, sin normalizacion por terreno (BIOMASS L1B)
    "sigma0": "sigma0 lineal",
}


def pasada_traza_de_metadatos(ruta):
    """Busca la pasada (A o D) y la traza en las etiquetas del GeoTIFF. Devuelve ("", "") si no estan."""
    import rasterio

    try:
        with rasterio.open(ruta) as src:
            et = {k.upper(): str(v) for k, v in src.tags().items()}
    except Exception:                         # el archivo no se pudo abrir: lo avisara leer_en_grilla
        return "", ""
    pasada = ""
    for k in ("PASS", "ORBIT_DIRECTION", "ORBITDIRECTION", "PASADA"):
        v = et.get(k, "").strip().upper()
        if v:
            pasada = "A" if v.startswith("A") else ("D" if v.startswith("D") else "")
            break
    traza = ""
    for k in ("RELATIVE_ORBIT", "RELATIVEORBIT", "TRACK", "TRAZA"):
        if et.get(k, "").strip():
            traza = et[k].strip()
            break
    return pasada, traza


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", required=True, choices=list(SITIOS.keys()))
    ap.add_argument("--fecha_c", default="", help="AAAA-MM-DD de Sentinel-1 RTC (Planetary Computer)")
    ap.add_argument("--novasar", default="", help="numero de escena NovaSAR (p. ej. 47974)")
    ap.add_argument("--extra", action="append", default=[],
                    help='"banda=ruta.tif|sensor|lambda_cm|AAAA-MM-DD|unidad|pasada|traza" '
                         '(todo lo que sigue a la ruta es opcional; unidad: gamma0, gamma0E o sigma0)')
    ap.add_argument("--desplazamiento", type=float, nargs=2, default=(0.0, 0.0), metavar=("DX", "DY"),
                    help="correccion de NovaSAR en metros: DX positivo = este, DY positivo = norte (Tp3_02)")
    ap.add_argument("--min_validos", type=float, default=20.0,
                    help="%% minimo de pixeles con dato para incluir una banda")
    a = ap.parse_args()

    log = Bitacora(ruta_tp("Tp2", "05_Resultados", "06_Control_calidad"), "Tp2_01_%s" % a.sitio)
    g = grilla_sitio(a.sitio)
    log("Sitio %s: %d x %d pixeles de 10 m, EPSG de la grilla %s"
        % (a.sitio, g["width"], g["height"], g["crs"]))
    capas, filas = {}, []

    def agregar(nombre, arr, sensor, lam, fecha, unidad, fuente, pasada="", traza=""):
        val = 100.0 * np.isfinite(arr).mean()
        if val < a.min_validos:
            log("  %-26s %5.1f %% con dato  -> NO entra (menos de %.0f %%)" % (nombre, val, a.min_validos))
            return
        if nombre in capas:
            # Dos productos del mismo sensor, banda, polarizacion y dia (p. ej. dos granulos NISAR del
            # 17/09/2026, de 20 m y de 10 m): se queda el de MAS cobertura del sitio, nunca el ultimo leido.
            previo = next(x for x in filas if x["banda"] == nombre)
            if val <= previo["pixeles_validos_%"]:
                log("  %-26s %5.1f %% con dato  -> NO entra: ya hay otra de ese dia con %.1f %% (%s)"
                    % (nombre, val, previo["pixeles_validos_%"], previo["fuente"][:60]))
                return
            log("  %-26s reemplaza a la de %.1f %% de ese mismo dia (esta cubre %.1f %%)"
                % (nombre, previo["pixeles_validos_%"], val))
            filas.remove(previo)
        capas[nombre] = arr
        filas.append({"banda": nombre, "sensor": sensor, "lambda_cm": lam, "fecha": fecha,
                      "pasada": pasada, "traza": traza,
                      "unidad": unidad, "pixeles_validos_%": round(val, 1),
                      "media_dB": round(media_lineal_db(arr), 2), "fuente": fuente})
        log("  %-26s %5.1f %% con dato   media %6.2f dB  (%s, %s)"
            % (nombre, val, media_lineal_db(arr), sensor, fecha))

    # --------------------------------------------------- C: Sentinel-1 RTC
    if a.fecha_c:
        log.titulo("Banda C: Sentinel-1 RTC del %s" % a.fecha_c)
        its = buscar_stac("sentinel-1-rtc", a.sitio, a.fecha_c, a.fecha_c)
        if not its:
            log("  El catalogo no tiene Sentinel-1 RTC ese dia sobre el sitio. Se deja constancia.")
        for it in agrupar_por_pasada(its)[:1]:          # todos los cuadros de esa pasada, unidos
            f, h = fecha_item(it)
            fu = fuente_mpc("ESA - Copernicus", "Sentinel-1 IW GRD RTC (gamma0), %s" % it.id, f, h)
            pas = {"ascending": "A", "descending": "D"}.get(str(it.properties.get("sat:orbit_state", "")), "")
            tra = str(it.properties.get("sat:relative_orbit", ""))
            for pol in ("vv", "vh"):
                agregar("C_S1_gamma0_%s" % pol.upper(), s1_rtc(it, pol, g), "Sentinel-1", 5.6, f, "gamma0 lineal", fu,
                        pas, tra)

    # --------------------------------------------------- NISAR L y S locales
    # Todos los GCOV del disco: los del Delta (NISAR_DELTA) y los que se bajaron aparte para otros
    # sitios (08_Originales_crudos\NISAR: Concordia, Federal, Bovril). Cada uno entra solo si cubre el sitio.
    for carpeta, banda, nb, lam, org in ((os.path.join(NISAR_DELTA, "BANDA_L_NASA"), "LSAR", "L", 24.0, "NASA - ISRO"),
                                         (os.path.join(ORIGINALES, "NISAR"), "LSAR", "L", 24.0, "NASA - ISRO"),
                                         (os.path.join(NISAR_DELTA, "BANDA_S_ISRO"), "SSAR", "S", 9.4, "ISRO - NASA")):
        hs = [h for h in sorted(glob.glob(os.path.join(carpeta, "*.h5"))) if "COMPAT" not in h.upper()]
        if not hs:
            continue
        log.titulo("Banda %s: NISAR GCOV en %s" % (nb, carpeta))
        for h5 in hs:
            nombre = os.path.basename(h5)
            campos = nombre.split("_")
            fecha = campos[11][:8] if len(campos) > 11 else ""
            traza = campos[5] if len(campos) > 7 else ""
            pasada = campos[6] if len(campos) > 7 and campos[6] in ("A", "D") else ""
            fecha = "%s-%s-%s" % (fecha[:4], fecha[4:6], fecha[6:8]) if fecha else ""
            try:
                hh = nisar_gcov_en_grilla(h5, g, "HHHH", banda)
                hv = nisar_gcov_en_grilla(h5, g, "HVHV", banda)
            except ValueError:
                continue
            fu = "%s. NISAR L2 GCOV banda %s, %s, %s. %s" % (
                org, nb, nombre[:-3], fecha,
                "ASF DAAC: https://search.asf.alaska.edu" if nb == "L" else "ISRO Bhoonidhi: https://bhoonidhi.nrsc.gov.in")
            agregar("%s_NISAR_gamma0_HH_%s" % (nb, fecha.replace("-", "")), hh, "NISAR " + nb, lam, fecha, "gamma0 lineal",
                    fu, pasada, traza)
            agregar("%s_NISAR_gamma0_HV_%s" % (nb, fecha.replace("-", "")), hv, "NISAR " + nb, lam, fecha, "gamma0 lineal",
                    fu, pasada, traza)

    # --------------------------------------------------- S: NovaSAR
    if a.novasar:
        log.titulo("Banda S: NovaSAR-1 escena %s" % a.novasar)
        fecha = NOVASAR_ESCENAS.get(a.novasar, ("", ""))[0]
        s0, k = novasar_sigma0(a.novasar, g, desplazamiento_m=tuple(a.desplazamiento))
        if list(a.desplazamiento) == [0.0, 0.0]:
            log("  AVISO: sin --desplazamiento. NovaSAR viene georreferenciado con 4 puntos: medir con Tp3_02.")
        else:
            log("  Desplazamiento aplicado: %+.0f m este, %+.0f m norte (medido con Tp3_02)." % tuple(a.desplazamiento))
        fu = ("SSTL - CSIRO. NovaSAR-1 Stripmap GRD HH, escena %s, %s, sigma0 = DN^2/%.0e. "
              "Archivo del curso; CSIRO: https://data.novasar.csiro.au" % (a.novasar, fecha, k))
        agregar("S_NovaSAR_sigma0_HH", s0, "NovaSAR-1", 9.4, fecha, "sigma0 lineal", fu)

    # --------------------------------------------------- productos de SNAP
    for e in a.extra:
        nombre, resto = e.split("=", 1)
        partes = resto.split("|")
        ruta = partes[0]
        nbanda = 1
        if "#" in ruta:            # "ruta.tif#2": la banda 2 de un GeoTIFF de varias bandas (BIOMASS P: 1 HH, 2 HV, 3 VH, 4 VV)
            ruta, nb = ruta.rsplit("#", 1)
            nbanda = int(nb)
        sensor = partes[1] if len(partes) > 1 else "SNAP"
        lam = float(partes[2]) if len(partes) > 2 and partes[2] else float("nan")
        fecha = partes[3] if len(partes) > 3 else ""
        # Quinto campo: la unidad. Se escribe en la columna "unidad" de la tabla de bandas, para que el
        # lector sepa si el gamma0 esta normalizado por el terreno o solo sobre el elipsoide (objetivo 4).
        clave_u = (partes[4].strip() if len(partes) > 4 else "").lower()
        unidad = UNIDADES_EXTRA.get(clave_u)
        if unidad is None:
            log("  AVISO: unidad '%s' desconocida; use gamma0, gamma0E o sigma0. Se anota tal cual." % partes[4])
            unidad = partes[4].strip() + " lineal"
        # Sexto y septimo campo: pasada y traza. Si no se escriben, se buscan en los metadatos del GeoTIFF.
        pasada = partes[5].strip().upper() if len(partes) > 5 else ""
        traza = partes[6].strip() if len(partes) > 6 else ""
        origen_geom = "escritas en la orden (--extra)" if (pasada or traza) else ""
        if not (pasada and traza):
            p_meta, t_meta = pasada_traza_de_metadatos(ruta)
            if p_meta or t_meta:
                pasada, traza = pasada or p_meta, traza or t_meta
                origen_geom = "leidas de los metadatos del GeoTIFF"
        log.titulo("Producto agregado con --extra: %s (%s, %s cm, %s)" % (nombre, sensor, lam, fecha or "sin fecha"))
        if nombre.lower().endswith("_db"):
            log("  Viene en dB: se pasa a lineal en su grilla original y DESPUES se promedia a la grilla comun.")
            arr = leer_db_como_lineal(ruta, g)
            nombre = nombre[:-3]
        else:
            arr = leer_en_grilla(ruta, g, "average", banda=nbanda)
        if nbanda != 1:
            log("  Banda %d del GeoTIFF." % nbanda)
        if not fecha:
            log("  AVISO: sin fecha. Agregue |sensor|lambda_cm|AAAA-MM-DD despues de la ruta.")
        log("  Unidad: %s." % unidad)
        if pasada or traza:
            log("  Pasada %s, traza %s (%s)." % (pasada or "?", traza or "?", origen_geom))
        else:
            log("  Sin pasada ni traza: no estan en la orden ni en los metadatos. El paso 8 marcara "
                "'geometria no verificada'. Si las conoce, agreguelas: ...|unidad|A o D|traza")
        origen = ("Procesado en SNAP: %s" % ruta) if "SNAP" in sensor.upper() else \
            ("%s, agregado con --extra (banda %d): %s" % (sensor, nbanda, ruta))
        agregar(nombre, arr, sensor, lam, fecha, unidad, origen, pasada, traza)

    if not capas:
        log("")
        log("No se reunio ninguna banda con datos suficientes. Revise el sitio y las fechas.")
        log.cerrar()
        return
    out = ruta_tp("Tp2", "02_Subsets_SNAP_QGIS", "%s_pila_gamma0_lineal.tif" % a.sitio)
    guardar_tif(out, capas, g, " | ".join(sorted(set(f["fuente"] for f in filas))),
                "Pila multibanda en lineal sobre la grilla comun de 10 m (EPSG:32721)")
    pd.DataFrame(filas).to_csv(out.replace("_pila_gamma0_lineal.tif", "_pila_bandas.csv"),
                               index=False, encoding="utf-8-sig")
    log("")
    log("Pila  :", out)
    log("Bandas: %d" % len(capas))
    log.cerrar("python Tp2_02_rgb_copol_cruzada_cociente.py --sitio %s" % a.sitio)


if __name__ == "__main__":
    main()
