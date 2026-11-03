# -*- coding: utf-8 -*-
"""
Tp1_05_buscar_lidar.py   [SE CORRE]   paso 5 del Tp1
====================================================
LiDAR satelital sobre un sitio: GEDI L2A (version 003) e ICESat-2 ATL08
(version 007). Hace tres cosas, en este orden:

  1. BUSCA en NASA Earthdata los granulos que cruzan el sitio en la ventana
     pedida y los lista (no pide cuenta).
  2. Con --descargar, los BAJA a ORIGINALES\\LIDAR\\<SITIO>\\<producto>\\
     (pide la cuenta de NASA Earthdata: la misma de ASF). Un granulo GEDI
     pesa entre 0,2 y 3 GB y trae TODA la orbita: casi nada cae en el sitio.
  3. CUENTA, en los .h5 que haya en esa carpeta, cuantas huellas o segmentos
     caen dentro del sitio y cuantos sobreviven a los filtros de calidad, con
     el motivo de cada descarte (00_COMUN/funciones_lidar.py).

Lo que hay que tener presente
  - GEDI no tiene datos entre el 17/03/2023 y el 26/04/2024 (la mision estuvo
    guardada en la Estacion Espacial). Una busqueda en esa ventana devuelve
    cero granulos y NO es un error: se declara.
  - Ni GEDI ni ICESat-2 forman imagen: muestrean. El resultado de este paso
    es un NUMERO de huellas validas por sitio, que decide si el LiDAR puede
    entrar como referencia (Tp3, Tp5, Tp9) o solo como ilustracion.

SALIDA
  Tp1_Convergencia/05_Resultados/04_Tablas/lidar_granulos_<SITIO>.csv
  Tp1_Convergencia/05_Resultados/04_Tablas/lidar_conteo_<SITIO>.csv
        por producto: huellas, validas y los MOTIVOS de descarte con su cantidad
  Tp1_Convergencia/05_Resultados/04_Tablas/lidar_fechas_validas_<SITIO>.csv
        las fechas con al menos una huella valida en el sitio (las unicas que entran a la matriz del Tp1_07)
  Tp1_Convergencia/05_Resultados/03_Vectores/lidar_<SITIO>.gpkg
        capas gedi_l2a y atl08: TODAS las huellas del sitio, con "valido" y "motivo", y
        "plausible" = False en las validas con mas de 50 m (control de plausibilidad: revisar)

USO (Miniforge Prompt, entorno sar):
    python Tp1_05_buscar_lidar.py --sitio C_FEDERAL --desde 2019-04-01 --hasta 2026-09-30
    python Tp1_05_buscar_lidar.py --sitio C_FEDERAL --desde 2024-05-01 --hasta 2025-07-31 --descargar
    python Tp1_05_buscar_lidar.py --sitio C_FEDERAL --solo_contar
"""
import argparse
import warnings

# Aviso de earthaccess sobre DataGranule.size (cambia en su version 1.0): no afecta.
warnings.filterwarnings("ignore", message=".*DataGranule.size.*", category=FutureWarning)
import glob
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import pandas as pd                                                   # noqa: E402

from configuracion_comun import SITIOS, ORIGINALES, ruta_tp           # noqa: E402
from funciones_comunes import Bitacora                                # noqa: E402
from funciones_lidar import leer_gedi_l2a, leer_atl08, a_geopackage   # noqa: E402

PRODUCTOS = [("GEDI02_A", "003"), ("ATL08", "007")]
ALTURA_MAX = 50.0   # m: mas alto que cualquier arbol de los sitios del curso (control de plausibilidad)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", required=True, choices=list(SITIOS.keys()))
    ap.add_argument("--desde", default="2019-04-01")
    ap.add_argument("--hasta", default="2026-09-30")
    ap.add_argument("--descargar", action="store_true")
    ap.add_argument("--solo_contar", action="store_true")
    ap.add_argument("--sensibilidad", type=float, default=0.95)
    a = ap.parse_args()

    log = Bitacora(ruta_tp("Tp1", "05_Resultados", "06_Control_calidad"), "Tp1_05_%s" % a.sitio)
    bbox = SITIOS[a.sitio]["bbox"]
    carpeta = os.path.join(ORIGINALES, "LIDAR", a.sitio)

    if not a.solo_contar:
        import earthaccess

        if a.descargar:
            # Sin strategy: earthaccess busca EARTHDATA_TOKEN, despues .netrc,
            # y solo entonces pregunta. persist=True guarda en .netrc.
            auth = earthaccess.login(persist=True)
            if not auth.authenticated:
                sys.exit("No se pudo autenticar en NASA Earthdata.")
        filas = []
        for corto, ver in PRODUCTOS:
            log.titulo("%s version %s  %s a %s" % (corto, ver, a.desde, a.hasta))
            try:
                gran = earthaccess.search_data(short_name=corto, version=ver,
                                               bounding_box=bbox, temporal=(a.desde, a.hasta))
            except Exception as e:                   # noqa: BLE001
                log("  La busqueda fallo: %s" % str(e)[:150])
                log("  Se deja constancia y se sigue con el siguiente producto.")
                continue
            log("  %d granulos cruzan el sitio." % len(gran))
            for g in gran:
                nombre = g["umm"]["GranuleUR"] if "umm" in g else str(g)[:60]
                t = g["umm"]["TemporalExtent"]["RangeDateTime"]["BeginningDateTime"] if "umm" in g else ""
                tam = g.size() if hasattr(g, "size") else ""
                filas.append({"producto": corto, "version": ver, "granulo": nombre,
                              "fecha": t[:10], "tamano_MB": tam})
                log("   %s  %s  %s MB" % (t[:10], nombre[:70], tam))
            if corto == "GEDI02_A" and a.desde <= "2024-04-26" and a.hasta >= "2023-03-17":
                log("  AVISO: la ventana incluye el receso de GEDI (17/03/2023 a 26/04/2024): ")
                log("         en ese lapso no hay huellas y no es un error de la busqueda.")
            if a.descargar and gran:
                destino = os.path.join(carpeta, corto)
                os.makedirs(destino, exist_ok=True)
                log("  Descargando a %s ..." % destino)
                for intento in range(3):
                    try:
                        earthaccess.download(gran, destino, threads=2)
                        break
                    except Exception as e:           # noqa: BLE001
                        log("   interrupcion (%s); reintento %d/3" % (str(e)[:80], intento + 1))
        os.makedirs(ruta_tp("Tp1", "05_Resultados", "04_Tablas"), exist_ok=True)
        pd.DataFrame(filas, columns=["producto", "version", "granulo", "fecha", "tamano_MB"]).to_csv(
            ruta_tp("Tp1", "05_Resultados", "04_Tablas", "lidar_granulos_%s.csv" % a.sitio),
            index=False, encoding="utf-8-sig")

    # ----------------------------------------------------------- conteo
    log.titulo("Conteo de huellas en los .h5 de %s" % carpeta)
    conteo, fechas_validas = [], []
    gpkg = ruta_tp("Tp1", "05_Resultados", "03_Vectores", "lidar_%s.gpkg" % a.sitio)
    gedi = sorted(glob.glob(os.path.join(carpeta, "GEDI02_A", "*.h5")))
    atl = sorted(glob.glob(os.path.join(carpeta, "ATL08", "*.h5")))
    if not gedi and not atl:
        log("  No hay granulos descargados. Correr con --descargar o copiarlos a esa carpeta.")
    if gedi:
        df = pd.concat([leer_gedi_l2a(f, bbox, a.sensibilidad) for f in gedi], ignore_index=True)
        if len(df):
            # Control de plausibilidad (no cambia "valido"): una huella valida con rh98 > ALTURA_MAX
            # no es un arbol en Entre Rios; se marca para revisarla (forma de onda L1B, imagen).
            df["plausible"] = ~(df.valido & (df.rh98 > ALTURA_MAX))
            df["control_plausibilidad"] = ""
            df.loc[~df.plausible, "control_plausibilidad"] = "rh98 > %g m: revisar" % ALTURA_MAX
            a_geopackage(df, gpkg, "gedi_l2a")
            mot = df.loc[~df.valido, "motivo"].str.split(";").explode().value_counts()
            conteo.append({"producto": "GEDI L2A v003", "granulos": len(gedi),
                           "huellas_en_sitio": len(df), "validas": int(df.valido.sum()),
                           "fechas_con_validas": df[df.valido].fecha.nunique(),
                           "descartes": "; ".join("%s=%d" % kv for kv in mot.items()),
                           "otros_datos": "validas dudosas (rh98 > %g m)=%d" % (ALTURA_MAX, (~df.plausible).sum())})
            log("  GEDI L2A: %d huellas validas con rh98 > %g m, marcadas plausible=False para revisar."
                % ((~df.plausible).sum(), ALTURA_MAX))
            log("  GEDI L2A: %d huellas en el sitio, %d validas (%.1f %%)."
                % (len(df), df.valido.sum(), 100.0 * df.valido.mean()))
            for k, v in mot.items():
                log("      descartadas por %-20s %d" % (k, v))
            for fe, n in df[df.valido].groupby("fecha").size().items():
                fechas_validas.append({"producto": "GEDI02_A", "fecha": fe, "huellas_validas": int(n)})
    if atl:
        df = pd.concat([leer_atl08(f, bbox) for f in atl], ignore_index=True)
        if len(df):
            df["plausible"] = ~(df.canopia_valida & (df.h_canopy > ALTURA_MAX))
            df["control_plausibilidad"] = ""
            df.loc[~df.plausible, "control_plausibilidad"] = "h_canopy > %g m: revisar" % ALTURA_MAX
            log("  ATL08: %d segmentos con canopia valida y h_canopy > %g m, marcados plausible=False."
                % ((~df.plausible).sum(), ALTURA_MAX))
            a_geopackage(df, gpkg, "atl08")
            conteo.append({"producto": "ATL08 v007", "granulos": len(atl),
                           "huellas_en_sitio": len(df),
                           "validas": int(df.canopia_valida.sum()),
                           "fechas_con_validas": df[df.canopia_valida].fecha.nunique(),
                           "descartes": "; ".join("%s=%d" % kv for kv in
                                                  df.loc[~df.canopia_valida, "motivo_canopia"]
                                                  .str.split(";").explode().value_counts().items()),
                           "otros_datos": "terreno valido=%d; haces fuertes=%d; nocturnos=%d; canopia valida dudosa (> %g m)=%d"
                           % (df.terreno_valido.sum(), (df.fuerza_haz == "fuerte").sum(),
                              (df.nocturno == 1).sum(), ALTURA_MAX, (~df.plausible).sum())})
            for fe, n in df[df.canopia_valida].groupby("fecha").size().items():
                fechas_validas.append({"producto": "ATL08", "fecha": fe, "huellas_validas": int(n)})
            log("  ATL08: %d segmentos de 100 m en el sitio; %d con canopia valida; %d con terreno valido."
                % (len(df), df.canopia_valida.sum(), df.terreno_valido.sum()))
    tabla = ruta_tp("Tp1", "05_Resultados", "04_Tablas", "lidar_conteo_%s.csv" % a.sitio)
    os.makedirs(os.path.dirname(tabla), exist_ok=True)
    pd.DataFrame(conteo, columns=["producto", "granulos", "huellas_en_sitio", "validas", "fechas_con_validas",
                                  "descartes", "otros_datos"]).to_csv(tabla, index=False, encoding="utf-8-sig")
    # Las fechas con al menos una huella VALIDA en el sitio: es lo unico que entra a la matriz (Tp1_07)
    tabla_f = ruta_tp("Tp1", "05_Resultados", "04_Tablas", "lidar_fechas_validas_%s.csv" % a.sitio)
    pd.DataFrame(fechas_validas, columns=["producto", "fecha", "huellas_validas"]).to_csv(
        tabla_f, index=False, encoding="utf-8-sig")
    log("")
    log("Conteo:", tabla)
    log("Fechas con huellas validas (las que entran a la matriz):", tabla_f)
    if conteo:
        log("Huellas (con su motivo de descarte):", gpkg)
    log.cerrar("python Tp1_06_escenas_por_pedido.py --sitio %s" % a.sitio)


if __name__ == "__main__":
    main()
