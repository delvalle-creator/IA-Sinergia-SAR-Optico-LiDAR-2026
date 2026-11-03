# -*- coding: utf-8 -*-
"""
datos_crudos.py   [YA VIENE HECHO]   lo corre el docente antes del curso
=====================================================================
Reune en UNA carpeta, 00_COMUN\\08_Originales_crudos ("datos crudos"), los
productos originales que usan los once practicos, tal como los entrega cada
proveedor y sin modificarlos. Asi el aula no depende de la red ni de que los
discos E: y F: esten conectados.

Cada parte se corre por separado (la red y el espacio en disco mandan):

  estado            que hay ya en la carpeta, cuanto pesa y cuanto disco queda
  copiar_locales    copia las escenas del archivo del docente (NovaSAR,
                    COSMO-SkyMed, Sentinel-1, SAOCOM, NISAR) que cubren cada
                    sitio, segun el inventario del Tp1_02
  icesat2           ICESat-2 ATLAS: ATL08 (vegetacion y terreno), ATL13 (agua
                    continental), ATL22 (nivel medio de cada cuerpo de agua en
                    cada pasada; solo las pasadas que ya tienen ATL13), ATL24
                    (batimetria costera y somera) y, si se pide, ATL03 (fotones)
  gedi              GEDI L2A (alturas), L2B (cobertura del dosel, PAI, perfil
                    vertical PAVD y diversidad de alturas FHD) y L4A (biomasa por
                    huella): con --confirmar guarda SOLO el recorte de cada sitio
  nisar             NISAR L2 GCOV banda L (ASF); la banda S de ISRO se baja a mano
                    (la del 30/09/2026 sobre Ibicuy ya esta en NISAR_DELTA\\BANDA_S_ISRO)
  biomass           BIOMASS banda P (ESA MAAP), con la ficha de 90 dias
  cci               ESA CCI Biomass (biomasa aerea, 100 m): recorte por sitio
  cci_resumen       tabla de biomasa CCI por sitio y anio, con su desvio
  planetary         recortes de Sentinel-2, Sentinel-1 RTC, ALOS-2, DEM y JRC
                    del Planetary Computer para las fechas de cada evento
  cbers             CBERS-4A WPM (INPE, 2 m pancromatica + 8 m multiespectral): sin --confirmar
                    busca las pasadas cercanas a cada fecha de cada zona y deja vistas
                    rapidas para elegir la despejada; con --confirmar baja los recortes de
                    las elegidas en CBERS4A\\cbers_elegidas.csv
  embeddings        AlphaEarth Foundations Satellite Embedding (Google y Google DeepMind):
                    64 dimensiones por pixel de 10 m, anual (2017-2025), recorte de cada
                    sitio en los anios de las fechas del curso (copia de Source Cooperative)
  landsat           Landsat 8 y 9 Coleccion 2 Nivel 2 (reflectancia y temperatura
                    de superficie, Planetary Computer): para cada fecha Sentinel-2
                    de los practicos, la pasada Landsat mas cercana con el sitio
                    despejado, con sus metadatos MTL y ANG

NADA SE BORRA NI SE SOBRESCRIBE: si un archivo ya esta con el mismo tamano,
se saltea. Toda descarga o copia grande muestra primero el total y pide
--confirmar.

CREDENCIALES (nunca en el codigo)
  NASA Earthdata  (ICESat-2, GEDI, ASF): archivo .netrc o la pregunta del programa
  ESA MAAP        (BIOMASS): variables BIOMASS_TOKEN y BIOMASS_CLIENT_SECRET

ESTRUCTURA QUE ESCRIBE
  08_Originales_crudos\\
      LOCALES\\<sensor>\\<escena>               copias del archivo del docente
      LIDAR\\<SITIO>\\ATL08|ATL13|ATL22|ATL24|ATL03|GEDI02_A|GEDI02_B|GEDI_L4A\\   granulos .h5
      BIOMASS\\<coleccion>\\<producto>\\      productos de ESA MAAP (una vez)
      CCI_BIOMASS\\v7.0\\<SITIO>\\               recortes GeoTIFF (agb y agb_sd)
      PLANETARY\\<SITIO>\\<coleccion>\\<fecha>\\  recortes GeoTIFF nativos
      INVENTARIO_datos_crudos.csv               que se bajo o copio, de donde y cuando

USO (Miniforge Prompt)
    conda activate sar
    cd /d D:\\CURSOS_CEREGEO_2026\\02_Practica\\00_COMUN
    python datos_crudos.py estado
    python datos_crudos.py copiar_locales --sitios B_CONCORDIA F_BOVRIL           (muestra el total)
    python datos_crudos.py copiar_locales --sitios B_CONCORDIA F_BOVRIL --confirmar
    python datos_crudos.py icesat2 --sitios B_CONCORDIA --productos ATL08 ATL13 --confirmar
    python datos_crudos.py gedi --sitios C_FEDERAL --productos L2A L2B L4A --confirmar --harmony
    python datos_crudos.py icesat2 --sitios A1_DELTA_QUEMAS A2_IBICUY --productos ATL22 --desde 2018-10-14
    python datos_crudos.py nisar --sitios DELTA_NISAR B_CONCORDIA C_FEDERAL
    python datos_crudos.py nisar --sitios DELTA_NISAR --desde 2026-09-01 --hasta 2026-09-30 --confirmar
    python datos_crudos.py biomass --sitios todos --confirmar
    python datos_crudos.py cci --sitios todos --anios 2010 2015 2020 2021 2024
    python datos_crudos.py landsat                     (muestra la escena elegida para cada fecha)
    python datos_crudos.py landsat --confirmar
    python datos_crudos.py cbers                       (vistas para elegir la escena despejada)
    python datos_crudos.py cbers --confirmar           (baja las elegidas en CBERS4A\\cbers_elegidas.csv)
    python datos_crudos.py cci_resumen --sitios todos
    python datos_crudos.py planetary --sitios B_CONCORDIA --desde 2023-11-01 --hasta 2023-11-08 --confirmar
"""
import argparse
import warnings

# Aviso de earthaccess sobre DataGranule.size (cambia en su version 1.0): no afecta.
warnings.filterwarnings("ignore", message=".*DataGranule.size.*", category=FutureWarning)
import datetime as _dt
import glob
import math
import re
import os
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

import configuracion_comun as cc                                     # noqa: E402
from configuracion_comun import (SITIOS, ORIGINALES, LOCALES, PRACTICA, ruta_tp)  # noqa: E402

# Raices del archivo del docente y nombre de su copia en LOCALES (la misma
# estructura de carpetas: configuracion_comun.py usa la copia si falta el disco)
RAICES = [("NISAR_DELTA", cc.NISAR_DELTA), ("NOVASAR", cc.NOVASAR),
          ("CURSO_2023", cc.ORIGINALES_2023), ("COSMO_DIAMANTE", cc.COSMO_DIAMANTE)]


def destino_local(ruta):
    """Ubicacion de la copia: LOCALES/<RAIZ>/<ruta relativa a esa raiz>."""
    r = os.path.normcase(os.path.abspath(ruta))
    for nombre, raiz in RAICES:
        rz = os.path.normcase(os.path.abspath(raiz))
        if r.startswith(rz + os.sep):
            return os.path.join(LOCALES, nombre, os.path.relpath(os.path.abspath(ruta), os.path.abspath(raiz)))
    return os.path.join(LOCALES, "OTROS", os.path.basename(ruta.rstrip("\\/")))

INVENTARIO = os.path.join(ORIGINALES, "INVENTARIO_datos_crudos.csv")

# Productos de LiDAR (nombre corto y version en NASA CMR)
ICESAT2 = {"ATL08": "007", "ATL13": "007", "ATL22": "004", "ATL24": "002", "ATL03": "007"}
# GEDI: L2A y L2B en version 003 y L4A en version 3, que es la que se calcula sobre
# el L2A 003 (la 2.1 sale del L2A 002 y termina el 09/07/2025). Verificado en NASA CMR
# el 17/10/2026: GEDI02_B 003 (LP DAAC) y GEDI_L4A_AGB_Density_V3_2508 (ORNL DAAC).
GEDI = {"L2A": ("GEDI02_A", "003"), "L2B": ("GEDI02_B", "003"),
        "L4A": ("GEDI_L4A_AGB_Density_V3_2508", "3")}
CARPETA_GEDI = {"L2A": "GEDI02_A", "L2B": "GEDI02_B", "L4A": "GEDI_L4A"}
# Latitud y longitud de cada disparo dentro del haz. En la version 003 estan en la raiz
# del haz (BEAMxxxx/lat_lowestmode) en los tres productos; en versiones anteriores del
# L2B estaban en geolocation/. Se prueba primero la raiz y despues geolocation/.
LATLON_GEDI = (("lat_lowestmode", "lon_lowestmode"),
               ("geolocation/lat_lowestmode", "geolocation/lon_lowestmode"))

# Fechas por defecto de cada sitio para LiDAR y recortes: las del practico que lo usa
VENTANAS = {
    "A1_DELTA_QUEMAS": ("2019-04-01", "2021-06-30"),
    "A2_IBICUY": ("2024-04-26", "2026-09-30"),
    "B_CONCORDIA": ("2023-06-01", "2024-07-31"),
    "C_FEDERAL": ("2019-04-01", "2025-12-31"),
    "D_LAPAZ_VILLAGUAY": ("2019-04-01", "2026-09-30"),
    "E_PARANA_DIAMANTE": ("2019-04-01", "2026-09-30"),
    "E1_DIAMANTE_BARRANCA": ("2018-10-14", "2026-09-30"),
    "F_BOVRIL": ("2022-09-01", "2024-03-31"),
    "DELTA_NISAR": ("2024-04-26", "2026-09-30"),
}

CCI_BASE = "https://dap.ceda.ac.uk/neodc/esacci/biomass/data/agb/maps"
CCI_CITA = ("Santoro, M. y Cartus, O. (2026). ESA Biomass Climate Change Initiative (Biomass_cci): "
            "Global datasets of forest above-ground biomass for the years 2005-2012 and 2015-2024, v7.0. "
            "NERC EDS Centre for Environmental Data Analysis. https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903")


# ------------------------------------------------------------ utilidades
def tam(n):
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or u == "TB":
            return "%.1f %s" % (n, u)
        n /= 1024.0


def peso(ruta):
    if os.path.isfile(ruta):
        return os.path.getsize(ruta)
    total = 0
    for d, _, fs in os.walk(ruta):
        for f in fs:
            try:
                total += os.path.getsize(os.path.join(d, f))
            except OSError:
                pass
    return total


def libre(ruta):
    os.makedirs(ruta, exist_ok=True)
    return shutil.disk_usage(ruta).free


def anotar(filas):
    """Agrega filas al inventario de datos crudos (fuente, destino, fecha de la copia)."""
    if not filas:
        return
    os.makedirs(ORIGINALES, exist_ok=True)
    nuevo = pd.DataFrame(filas)
    if os.path.exists(INVENTARIO):
        nuevo = pd.concat([pd.read_csv(INVENTARIO, encoding="utf-8-sig"), nuevo], ignore_index=True)
        nuevo = nuevo.drop_duplicates(subset=["destino"], keep="last")
    nuevo.to_csv(INVENTARIO, index=False, encoding="utf-8-sig")


def sitios_de(lista):
    if not lista or lista == ["todos"]:
        return list(SITIOS)
    malos = [s for s in lista if s not in SITIOS]
    if malos:
        sys.exit("Sitios desconocidos: %s. Validos: %s" % (", ".join(malos), ", ".join(SITIOS)))
    return lista


def ahora():
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M")


# ------------------------------------------------------------ estado
def cmd_estado(a):
    print("Carpeta de datos crudos: %s" % ORIGINALES)
    if not os.path.isdir(ORIGINALES):
        print("  todavia no existe.")
    else:
        for d in sorted(os.listdir(ORIGINALES)):
            r = os.path.join(ORIGINALES, d)
            if os.path.isdir(r):
                print("  %-14s %10s" % (d, tam(peso(r))))
    print("Espacio libre en ese disco: %s" % tam(libre(ORIGINALES)))
    if os.path.exists(INVENTARIO):
        t = pd.read_csv(INVENTARIO, encoding="utf-8-sig")
        print("Inventario: %d entradas" % len(t))
        print(t.groupby("tipo").size().to_string())


# ------------------------------------------------------------ copiar locales
def cmd_copiar_locales(a):
    inv = ruta_tp("Tp1", "05_Resultados", "04_Tablas", "inventario_local.csv")
    if not os.path.exists(inv):
        sys.exit("Falta %s: correr antes Tp1_02_inventario_local.py (sabe que escena cubre que sitio)." % inv)
    t = pd.read_csv(inv, encoding="utf-8-sig")
    t = t[t.sitio.isin(sitios_de(a.sitios))]
    t = t[pd.to_numeric(t["cobertura_huella_%"], errors="coerce").fillna(0) > 0]
    if a.sensores:
        t = t[t.sensor.isin(a.sensores)]
    if not a.incluir_nisar:
        t = t[t.sensor != "NISAR"]
    # Se copia la carpeta entera del producto, no solo el archivo de la imagen, para no
    # perder metadatos, vistas rapidas, KML ni anotaciones que vienen al lado:
    #   COSMO-SkyMed: ...\EL<fecha>_<hora>_<id>\CSKx_...h5  -> la carpeta EL...
    #   NovaSAR-1:    ...\NovaSAR_01_<n>_grd_<fecha>_HH\NovaSAR_01_<n>_grd_13_... -> la de afuera
    def _carpeta_producto(r):
        madre = os.path.dirname(r.rstrip("\\/"))
        nombre = os.path.basename(madre)
        if nombre.startswith("EL") or nombre.startswith("NovaSAR_"):
            return madre
        return r
    t = t.assign(ruta=t.ruta.map(lambda r: _carpeta_producto(r) if isinstance(r, str) else r))
    rutas = sorted(set(t.ruta.dropna()))
    plan = []
    for r in rutas:
        if not os.path.exists(r):
            print("  NO ESTA (disco desconectado?): %s" % r)
            continue
        if os.path.normcase(os.path.abspath(r)).startswith(os.path.normcase(os.path.abspath(ORIGINALES)) + os.sep):
            continue  # ya esta dentro de los datos crudos (p. ej. NISAR bajado con el subcomando nisar)
        sensor = t.loc[t.ruta == r, "sensor"].iloc[0]
        plan.append((r, destino_local(r), sensor, peso(r)))
    # MapBiomas (bosques 2023 recortados a las escenas NovaSAR), en la carpeta madre de NovaSAR
    for f in sorted(glob.glob(os.path.join(os.path.dirname(cc.NOVASAR), "Bosques_MapBiomas_2023_*.tif"))):
        plan.append((f, os.path.join(LOCALES, "MAPBIOMAS", os.path.basename(f)), "MapBiomas", peso(f)))
    # COSMO-SkyMed de Diamante completo (grietas, MDE del IGN, productos InSAR)
    if a.cosmo_completo and os.path.isdir(cc.COSMO_DIAMANTE):
        plan.append((cc.COSMO_DIAMANTE, os.path.join(LOCALES, "COSMO_DIAMANTE"), "COSMO-SkyMed (carpeta)",
                     peso(cc.COSMO_DIAMANTE)))
    total = sum(p[3] for p in plan)
    ya = sum(p[3] for p in plan if os.path.exists(p[1]) and peso(p[1]) == p[3])
    print("Escenas que cubren los sitios: %d, %s en total (%s ya copiado)." % (len(plan), tam(total), tam(ya)))
    for r, d, s, n in plan:
        print("  %-12s %10s  %s" % (s, tam(n), r))
    print("Espacio libre en destino: %s" % tam(libre(ORIGINALES)))
    if not a.confirmar:
        print("\nNo se copio nada. Revise la lista y vuelva a correr con --confirmar.")
        return
    if total - ya > libre(ORIGINALES):
        sys.exit("No alcanza el espacio en disco.")
    filas = []
    for r, d, s, n in plan:
        if os.path.exists(d) and peso(d) == n:
            continue
        print("Copiando %s ..." % os.path.basename(r))
        if os.path.isdir(r):
            shutil.copytree(r, d, dirs_exist_ok=True)
        else:
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(r, d)
        ok = peso(d) == n
        print("   %s" % ("ok" if ok else "TAMANO DISTINTO: revisar"))
        filas.append({"tipo": "local", "sensor": s, "origen": r, "destino": d, "bytes": n,
                      "verificado": ok, "cuando": ahora(), "fuente": "Archivo del docente"})
    anotar(filas)


# ------------------------------------------------------------ NASA (ICESat-2 y GEDI)
def _fecha_granulo(g):
    """Fecha de inicio de un granulo de earthaccess (AAAA-MM-DD), o "" si no la trae."""
    try:
        return str(g["umm"]["TemporalExtent"]["RangeDateTime"]["BeginningDateTime"])[:10]
    except Exception:                                # noqa: BLE001
        return ""


def _bajar_nasa(pedidos, a, tipo):
    import earthaccess

    plan = []
    for sitio, corto, ver, carpeta in pedidos:
        d0, d1 = (a.desde, a.hasta) if a.desde else VENTANAS[sitio]
        try:
            gran = earthaccess.search_data(short_name=corto, version=ver,
                                           bounding_box=SITIOS[sitio]["bbox"], temporal=(d0, d1))
        except Exception as e:                       # noqa: BLE001
            print("  %s %s: la busqueda fallo (%s)" % (sitio, corto, str(e)[:100]))
            continue
        if corto == "ATL22":
            # El ATL22 es el promedio, por cuerpo de agua, de cada pasada del ATL13. En el
            # catalogo cada granulo trae la huella de media orbita, asi que la busqueda por
            # sitio devuelve casi todas las pasadas del hemisferio. Se dejan solo las
            # pasadas (traza RGT + ciclo) que ya tienen ATL13 en el sitio.
            pasadas = {os.path.basename(f).split("_")[2][:6]
                       for f in glob.glob(os.path.join(ORIGINALES, "LIDAR", sitio, "ATL13", "ATL13_*.h5"))}
            antes = len(gran)
            gran = [g for g in gran if os.path.basename(g.data_links()[0]).split("_")[2][:6] in pasadas]
            print("  %s ATL22: %d granulos en el catalogo, %d con ATL13 del sitio (%d pasadas ATL13)."
                  % (sitio, antes, len(gran), len(pasadas)))
        mb = sum(float(g.size() or 0) for g in gran)
        print("  %-22s %-32s v%-4s %s a %s: %4d granulos, %8.0f MB" % (sitio, corto, ver, d0, d1, len(gran), mb))
        plan.append((sitio, corto, ver, carpeta, gran, mb))
    total = sum(p[5] for p in plan)
    print("Total: %.1f GB. Espacio libre: %s" % (total / 1024.0, tam(libre(ORIGINALES))))
    # La busqueda queda en una tabla para revisarla sin depender de la pantalla.
    os.makedirs(ORIGINALES, exist_ok=True)
    resumen = os.path.join(ORIGINALES, "busqueda_%s.csv" % tipo)
    pd.DataFrame([{"sitio": p[0], "producto": p[1], "version": p[2], "granulos": len(p[4]),
                   "MB": round(p[5]), "primero": min((_fecha_granulo(g) for g in p[4]), default=""),
                   "ultimo": max((_fecha_granulo(g) for g in p[4]), default=""), "cuando": ahora()} for p in plan]
                 ).to_csv(resumen, index=False, encoding="utf-8-sig")
    print("Tabla de la busqueda: %s" % resumen)
    if not a.confirmar:
        print("\nNo se bajo nada. Vuelva a correr con --confirmar (o acote --desde y --hasta).")
        return
    if not earthaccess.login(persist=True).authenticated:
        sys.exit("No se pudo autenticar en NASA Earthdata.")
    filas = []
    for sitio, corto, ver, carpeta, gran, mb in plan:
        if not gran:
            continue
        os.makedirs(carpeta, exist_ok=True)
        print("Bajando %s %s a %s ..." % (sitio, corto, carpeta))
        for intento in range(3):
            try:
                earthaccess.download(gran, carpeta, threads=2)
                break
            except Exception as e:                   # noqa: BLE001
                print("   interrupcion (%s); reintento %d/3" % (str(e)[:80], intento + 1))
        n = len(glob.glob(os.path.join(carpeta, "*.h5")))
        filas.append({"tipo": tipo, "sensor": corto, "origen": "NASA Earthdata (CMR) v%s" % ver,
                      "destino": carpeta, "bytes": peso(carpeta), "verificado": n >= len(gran),
                      "cuando": ahora(), "fuente": "NASA. %s v%s. https://search.earthdata.nasa.gov" % (corto, ver)})
    anotar(filas)


def cmd_icesat2(a):
    pedidos = [(s, p, ICESAT2[p], os.path.join(ORIGINALES, "LIDAR", s, p))
               for s in sitios_de(a.sitios) for p in a.productos]
    if "ATL24" in a.productos:
        print("AVISO: ATL24 es batimetria costera. En el Delta y el Rio de la Plata la turbidez suele")
        print("impedir ver el fondo: puede no haber granulos o haberlos sin fondo detectado.")
    if "ATL03" in a.productos:
        print("AVISO: ATL03 (fotones) pesa del orden de 1 a 2 GB por granulo. Solo para la barranca (E1).")
    _bajar_nasa(pedidos, a, "icesat2")


# Variables que se copian al recorte de cada haz (las que existan en el granulo).
# Son las que leen funciones_lidar.leer_gedi_l2a y los practicos, mas algunas de control.
VARIABLES_GEDI = {
    "GEDI02_A": ["lat_lowestmode", "lon_lowestmode", "shot_number", "delta_time", "quality_flag",
                 "l2a_quality_flag_rel3", "degrade_flag", "sensitivity", "surface_flag", "rh",
                 "elev_lowestmode", "elev_highestreturn", "solar_elevation", "digital_elevation_model",
                 "num_detectedmodes", "selected_algorithm", "beam", "channel",
                 "land_cover_data/landsat_water_persistence", "land_cover_data/urban_proportion"],
    # (de cada lista se copian solo las variables que existan en el granulo)
    # L2B: cobertura (cover), indice de area vegetal (pai), perfiles cada 5 m (cover_z,
    # pai_z, pavd_z), diversidad de alturas del follaje (fhd_normal) y control de calidad.
    "GEDI02_B": ["lat_lowestmode", "lon_lowestmode", "elev_lowestmode", "delta_time", "shot_number", "beam",
                 "channel", "l2b_quality_flag_rel3", "l2a_quality_flag_rel3", "l2b_quality_flag",
                 "algorithmrun_flag", "l2_algrunflag", "sensitivity",
                 "surface_flag", "num_detectedmodes", "selected_l2a_algorithm", "selected_rg_algorithm",
                 "cover", "cover_z", "pai", "pai_z", "pavd_z", "fhd_normal", "rh100", "dz", "omega",
                 "pgap_theta", "rhov", "rhog", "rossg", "leaf_off_flag", "stale_return_flag",
                 "geolocation/lat_lowestmode", "geolocation/lon_lowestmode", "geolocation/elev_lowestmode",
                 "geolocation/elev_highestreturn", "geolocation/height_lastbin", "geolocation/height_bin0",
                 "geolocation/delta_time", "geolocation/degrade_flag", "geolocation/solar_elevation",
                 "geolocation/digital_elevation_model", "land_cover_data/landsat_treecover",
                 "land_cover_data/modis_treecover", "land_cover_data/pft_class", "land_cover_data/region_class"],
    "GEDI_L4A_AGB_Density_V3_2508": [
                 "lat_lowestmode", "lon_lowestmode", "shot_number", "delta_time", "agbd", "agbd_se",
                 "agbd_pi_lower", "agbd_pi_upper", "agbd_t", "agbd_t_se", "l4a_quality_flag_rel3",
                 "l2a_quality_flag_rel3", "l4_quality_flag", "l2_quality_flag",
                 "degrade_flag", "sensitivity", "surface_flag", "solar_elevation", "elev_lowestmode",
                 "predict_stratum", "land_cover_data/pft_class", "land_cover_data/region_class",
                 "land_cover_data/landsat_treecover"],
}


def _recortar_granulo_gedi(fobj, nombre, corto, bbox, destino):
    """Lee un granulo GEDI por la red (sin bajarlo entero) y escribe un .h5 chico
    con la MISMA estructura (BEAMxxxx/<variable>) pero solo con los disparos del
    sitio. Devuelve la cantidad de disparos guardados (0 = el granulo no toca el sitio)."""
    import h5py

    lon0, lat0, lon1, lat1 = bbox
    n_total = 0
    salida = None
    with h5py.File(fobj, "r") as h:
        for haz in sorted(k for k in h.keys() if k.startswith("BEAM")):
            g = h[haz]
            par = [t for t in LATLON_GEDI if t[0] in g]
            if not par:
                continue
            vlat, vlon = par[0]
            lat = g[vlat][:]
            cand = np.nonzero((lat >= lat0) & (lat <= lat1))[0]
            if cand.size == 0:
                continue
            i0, i1 = int(cand[0]), int(cand[-1]) + 1
            lon = g[vlon][i0:i1]
            latv = lat[i0:i1]
            sel = np.nonzero((lon >= lon0) & (lon <= lon1) & (latv >= lat0) & (latv <= lat1))[0]
            if sel.size == 0:
                continue
            if salida is None:
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                salida = h5py.File(destino + ".parcial", "w")
                salida.attrs["granulo_original"] = nombre
                salida.attrs["recorte_bbox_lon0_lat0_lon1_lat1"] = np.array(bbox, "f8")
                salida.attrs["recortado_por"] = "datos_crudos.py gedi (solo los disparos del sitio)"
                salida.attrs["cuando"] = ahora()
            go = salida.create_group(haz)
            for var in VARIABLES_GEDI[corto]:
                if var not in g:
                    continue
                d = g[var]
                if d.ndim == 0 or d.shape[0] != lat.shape[0]:
                    continue
                datos = d[i0:i1][sel] if d.ndim == 1 else d[i0:i1, ...][sel, ...]
                go.create_dataset(var, data=datos, compression="gzip")
                for k, v in d.attrs.items():
                    try:
                        go[var].attrs[k] = v
                    except Exception:                # noqa: BLE001
                        pass
            n_total += int(sel.size)
    if salida is not None:
        salida.close()
        os.replace(destino + ".parcial", destino)
    return n_total


def cmd_gedi(a):
    pedidos = []
    for s in sitios_de(a.sitios):
        for p in a.productos:
            corto, ver = GEDI[p]
            pedidos.append((s, corto, ver, os.path.join(ORIGINALES, "LIDAR", s, CARPETA_GEDI[p])))
    print("GEDI no adquirio entre el 17/03/2023 y el 26/04/2024.")
    if not a.desde:
        # Para GEDI se pide por defecto TODA la mision: lo que importa es juntar la
        # mayor cantidad de disparos por sitio (el filtro de calidad descarta muchos).
        a.desde, a.hasta = "2019-04-01", _dt.date.today().isoformat()
        print("Fechas: toda la mision (%s a %s). Se acota con --desde y --hasta." % (a.desde, a.hasta))
    if a.granulo_completo or not a.confirmar:
        if not a.granulo_completo:
            print("Cada granulo GEDI es una orbita entera (L2A ~1,2 GB). Con --confirmar NO se bajan enteros:")
            print("se lee cada granulo por la red y se guarda solo el recorte del sitio (unos pocos MB).")
        _bajar_nasa(pedidos, a, "gedi")
        return
    if a.harmony:
        _recortes_gedi_harmony(pedidos, a)
    else:
        _recortes_gedi(pedidos, a)


def _base_granulo(nombre):
    """Nombre del granulo hasta la version (..._V003 o ..._V002), sin sufijos."""
    m = re.search(r"(GEDI0\d_[AB]_.*?_V\d{3})", os.path.basename(nombre))
    return m.group(1) if m else os.path.splitext(os.path.basename(nombre))[0]


def _disparos_en_h5(ruta):
    import h5py
    try:
        with h5py.File(ruta, "r") as h:
            n = 0
            for k in h.keys():
                if not k.startswith("BEAM"):
                    continue
                for v in ("lat_lowestmode", "geolocation/lat_lowestmode"):   # L2A y L4A / L2B
                    if v in h[k]:
                        n += h[k][v].shape[0]
                        break
            return n
    except Exception:                                # noqa: BLE001
        return -1


def _buscar_nasa(funcion, **kw):
    """Busqueda en el catalogo de la NASA que no corta la corrida. Si la sesion de
    NASA Earthdata vencio (pasa en corridas largas), inicia sesion de nuevo y repite.
    Si falla por otro motivo, avisa y devuelve None para seguir con el pedido siguiente."""
    import earthaccess
    for intento in range(3):
        try:
            return funcion(**kw)
        except Exception as e:                       # noqa: BLE001
            txt = str(e)
            if ("expired" in txt.lower() or "401" in txt or "Unauthorized" in txt) and intento < 2:
                print("  La sesion de NASA Earthdata vencio: se inicia una nueva y se sigue.")
                try:
                    earthaccess.login(strategy="netrc", persist=True)
                except Exception:                    # noqa: BLE001
                    earthaccess.login(persist=True)
                continue
            print("  La busqueda en NASA fallo (%s). Se sigue con el pedido siguiente;" % txt[:120])
            print("  al repetir el mismo comando se vuelve a intentar.")
            return None
    return None


def _recortes_gedi_harmony(pedidos, a):
    """Recorte hecho en los servidores de NASA (Harmony, trajectory subsetter):
    NASA corta cada granulo al sitio y solo se baja el recorte. Mucho mas rapido
    que leer los granulos por la red desde aca."""
    import datetime as dt
    import earthaccess
    try:
        from harmony import BBox, Client, Collection, Request
    except ImportError:
        sys.exit("Falta harmony-py:  conda install -c conda-forge harmony-py   (o  pip install harmony-py)")

    if not earthaccess.login(persist=True).authenticated:
        sys.exit("No se pudo autenticar en NASA Earthdata.")
    cliente = Client()                               # usa el mismo .netrc / _netrc
    filas = []
    for sitio, corto, ver, carpeta in pedidos:
        d0, d1 = (a.desde, a.hasta) if a.desde else VENTANAS[sitio]
        col = _buscar_nasa(earthaccess.search_datasets, short_name=corto, version=ver)
        if col is None:
            continue
        if not col:
            print("  %s %s: no se encontro la coleccion en CMR" % (sitio, corto))
            continue
        cid = col[0]["meta"]["concept-id"]
        os.makedirs(carpeta, exist_ok=True)
        # Harmony antepone el numero de trabajo al nombre: se normaliza a <granulo>_recorte.h5
        for f in glob.glob(os.path.join(carpeta, "*_recorte.h5")):
            limpio = os.path.join(carpeta, _base_granulo(f) + "_recorte.h5")
            if f != limpio and not os.path.exists(limpio):
                os.replace(f, limpio)
        sin = os.path.join(carpeta, "_granulos_sin_disparos_en_el_sitio.txt")
        vacios = {_base_granulo(x) for x in (open(sin, encoding="utf-8").read().split() if os.path.exists(sin) else [])}
        hechos = {_base_granulo(f) for f in glob.glob(os.path.join(carpeta, "*.h5"))}
        gran = _buscar_nasa(earthaccess.search_data, short_name=corto, version=ver,
                            bounding_box=SITIOS[sitio]["bbox"], temporal=(d0, d1))
        if gran is None:
            continue
        # Se pide cada granulo por su identificador de CMR (concept-id), no por el nombre:
        # el nombre que Harmony busca no siempre coincide con el del archivo (en el L4A
        # lleva delante "GEDI_L4A_AGB_Density_V2_1."), y por eso rechazaba esos pedidos.
        pend = [(os.path.basename(g.data_links()[0]), g["meta"]["concept-id"]) for g in gran]
        pend = [t for t in pend if _base_granulo(t[0]) not in hechos and _base_granulo(t[0]) not in vacios]
        print("\n%s %s: %d granulos, %d por recortar en NASA (Harmony)." % (sitio, corto, len(gran), len(pend)))
        if not pend:
            continue
        lon0, lat0, lon1, lat1 = SITIOS[sitio]["bbox"]
        tmp = os.path.join(carpeta, "_harmony")
        os.makedirs(tmp, exist_ok=True)
        # Se pide por tandas, solo lo que falta. Lo que Harmony rechace queda anotado
        # y se recorta despues sin --harmony.
        sin_harmony = os.path.join(carpeta, "_granulos_que_harmony_no_proceso.txt")
        if os.path.exists(sin_harmony):
            os.remove(sin_harmony)               # se reintentan: la lista se rehace en esta corrida
        cola = [pend[k:k + a.tanda] for k in range(0, len(pend), a.tanda)]
        hechas = 0
        rechazos = 0
        while cola:
            tanda = cola.pop(0)
            nombres = [t[0] for t in tanda]
            req = Request(collection=Collection(id=cid), spatial=BBox(lon0, lat0, lon1, lat1),
                          granule_id=[t[1] for t in tanda], skip_preview=True, ignore_errors=True)
            try:
                try:
                    job = cliente.submit(req)
                except Exception as e0:              # noqa: BLE001
                    if "401" in str(e0) or "expired" in str(e0).lower() or "Unauthorized" in str(e0):
                        print("  La sesion de Harmony vencio: se inicia una nueva y se reintenta la tanda.")
                        cliente = Client()
                        job = cliente.submit(req)
                    else:
                        raise
            except Exception as e:                   # noqa: BLE001
                # Harmony no acepta la tanda: se anota entera (sin partirla, para no
                # hacer cientos de pedidos) y se completa despues sin --harmony.
                with open(sin_harmony, "a", encoding="utf-8") as fh:
                    fh.write("\n".join(nombres) + "\n")
                rechazos += 1
                print("  Harmony no proceso una tanda de %d granulos (%s). Quedan para completar sin --harmony."
                      % (len(nombres), str(e)[:60]))
                if rechazos >= 3 and hechas == 0:
                    print("  Harmony rechaza todo este producto: se pasa al siguiente.")
                    with open(sin_harmony, "a", encoding="utf-8") as fh:
                        fh.write("\n".join(x[0] for t in cola for x in t) + "\n")
                    cola = []
                continue
            hechas += len(nombres)
            print("  Tanda de %d granulos (%d de %d): trabajo %s. NASA esta recortando..."
                  % (len(nombres), hechas, len(pend), job))
            try:
                cliente.wait_for_processing(job, show_progress=True)
                futuros = list(cliente.download_all(job, directory=tmp, overwrite=False))
            except Exception as e:                   # noqa: BLE001
                print("    El trabajo %s fallo (%s); esos granulos quedan pendientes." % (job, str(e)[:80]))
                continue
            for fut in futuros:
                try:
                    ruta = fut.result()
                except Exception as e:               # noqa: BLE001
                    print("    descarga fallida: %s" % str(e)[:90])
                    continue
                if not str(ruta).lower().endswith(".h5"):
                    continue
                base = _base_granulo(ruta)
                n = _disparos_en_h5(ruta)
                if n <= 0:
                    with open(sin, "a", encoding="utf-8") as fh:
                        fh.write(base + "\n")
                    os.remove(ruta)
                    print("    %s: sin disparos en el sitio" % base)
                    continue
                final = os.path.join(carpeta, base + "_recorte.h5")
                os.replace(ruta, final)
                print("    %s: %d disparos" % (base, n))
        if os.path.exists(sin_harmony):
            print("  Algunos granulos no los proceso Harmony (lista en %s)." % sin_harmony)
            print("  Para completarlos: repetir el mismo comando SIN --harmony (lee solo esos, por la red).")
        n_rec = len(glob.glob(os.path.join(carpeta, "*_recorte.h5")))
        filas.append({"tipo": "gedi", "sensor": corto, "origen": "NASA Harmony (trajectory subsetter), v%s" % ver,
                      "destino": carpeta, "bytes": peso(carpeta), "verificado": True, "cuando": ahora(),
                      "fuente": "NASA. %s v%s. Recorte con NASA Harmony. https://harmony.earthdata.nasa.gov" % (corto, ver),
                      "sitios": "%s: %d recortes" % (sitio, n_rec)})
        print("%s %s: %d recortes en %s" % (sitio, corto, n_rec, carpeta))
    anotar(filas)


def _recortes_gedi(pedidos, a):
    """Recorte por sitio leyendo los granulos por la red (earthaccess.open)."""
    import earthaccess
    from concurrent.futures import ThreadPoolExecutor, as_completed

    if not earthaccess.login(persist=True).authenticated:
        sys.exit("No se pudo autenticar en NASA Earthdata.")
    fs = earthaccess.get_fsspec_https_session()
    filas = []
    for sitio, corto, ver, carpeta in pedidos:
        d0, d1 = (a.desde, a.hasta) if a.desde else VENTANAS[sitio]
        gran = _buscar_nasa(earthaccess.search_data, short_name=corto, version=ver,
                            bounding_box=SITIOS[sitio]["bbox"], temporal=(d0, d1))
        if gran is None:
            continue
        sin = os.path.join(carpeta, "_granulos_sin_disparos_en_el_sitio.txt")
        vacios = {_base_granulo(x) for x in (open(sin, encoding="utf-8").read().split() if os.path.exists(sin) else [])}
        hechos = {_base_granulo(f) for f in glob.glob(os.path.join(carpeta, "*_recorte.h5"))}
        pend = []
        for g in gran:
            nombre = os.path.basename(g.data_links()[0])
            destino = os.path.join(carpeta, _base_granulo(nombre) + "_recorte.h5")
            if _base_granulo(nombre) in vacios or _base_granulo(nombre) in hechos:
                continue
            pend.append((g, nombre, destino))
        print("\n%s %s: %d granulos, %d por recortar (los demas ya estan)." % (sitio, corto, len(gran), len(pend)))
        if not pend:
            continue
        os.makedirs(carpeta, exist_ok=True)

        def uno(t):
            g, nombre, destino = t
            err = ""
            for intento in range(3):
                try:
                    # Bloques grandes en memoria: cada lectura por la red trae a.bloque_mb MB
                    # de una vez, en lugar de muchos pedidos chicos (eso es lo que lo hacia lento).
                    url = g.data_links(access="external")[0]
                    with fs.open(url, "rb", block_size=a.bloque_mb * 2 ** 20, cache_type="blockcache") as f:
                        n = _recortar_granulo_gedi(f, nombre, corto, SITIOS[sitio]["bbox"], destino)
                    return nombre, n, ""
                except Exception as e:               # noqa: BLE001
                    err = str(e)[:90]
            return nombre, -1, err

        hechos = 0
        print("  Leyendo por la red; cada granulo tarda de 1 a varios minutos. Se informa al terminar cada uno.")
        with ThreadPoolExecutor(max_workers=a.hilos) as ex:
            for fut in as_completed([ex.submit(uno, t) for t in pend]):
                nombre, n, err = fut.result()
                hechos += 1
                if n > 0:
                    print("  [%d/%d] %s: %d disparos" % (hechos, len(pend), nombre, n))
                elif n == 0:
                    with open(sin, "a", encoding="utf-8") as fh:
                        fh.write(nombre + "\n")
                    print("  [%d/%d] %s: sin disparos en el sitio" % (hechos, len(pend), nombre))
                else:
                    print("  [%d/%d] %s: FALLO (%s); se reintenta al volver a correr" % (hechos, len(pend), nombre, err))
        n_rec = len(glob.glob(os.path.join(carpeta, "*_recorte.h5")))
        filas.append({"tipo": "gedi", "sensor": corto, "origen": "NASA Earthdata v%s (recorte por sitio leido por la red)" % ver,
                      "destino": carpeta, "bytes": peso(carpeta), "verificado": True, "cuando": ahora(),
                      "fuente": "NASA. %s v%s. https://search.earthdata.nasa.gov" % (corto, ver),
                      "sitios": "%s: %d recortes" % (sitio, n_rec)})
        print("%s %s: %d recortes en %s" % (sitio, corto, n_rec, carpeta))
    anotar(filas)


# ------------------------------------------------------------ NISAR GCOV (ASF)
SITIOS_DELTA = ("DELTA_NISAR", "A1_DELTA_QUEMAS", "A2_IBICUY")


def _bytes_asf(prop):
    """Tamano del archivo principal de un resultado de ASF. En NISAR, 'bytes' no es
    un numero sino un diccionario {archivo: {'bytes': n, 'format': ...}}."""
    b = prop.get("bytes", 0) or 0
    if isinstance(b, dict):
        nombre = os.path.basename(str(prop.get("url", "")))
        if nombre in b:
            b = b[nombre]
        else:
            candidatos = [v for k, v in b.items() if str(k).lower().endswith(".h5")] or list(b.values())
            b = max(candidatos, key=lambda v: float(v.get("bytes", 0) if isinstance(v, dict) else v or 0), default=0)
        if isinstance(b, dict):
            b = b.get("bytes", 0)
    try:
        return int(float(b or 0))
    except (TypeError, ValueError):
        return 0


def cmd_nisar(a):
    """NISAR L2 GCOV (banda L, NASA) desde ASF. La banda S (ISRO) no esta en ASF:
    se baja a mano del portal Bhoonidhi y se guarda en NISAR_DELTA\\BANDA_S_ISRO.

    Un mismo producto suele cubrir varios sitios (Concordia y Federal comparten
    trazas): se lista y se baja UNA sola vez. La lista completa queda en
    08_Originales_crudos\\NISAR_busqueda.csv para elegir fechas con calma."""
    import asf_search as asf
    try:                                              # CMR a veces tarda mas de 30 s
        asf.constants.INTERNAL.CMR_TIMEOUT = 120
    except AttributeError:
        pass
    from shapely.geometry import box, shape

    sys.path.insert(0, os.path.join(PRACTICA, "Tp1_Convergencia", "03_Scripts"))
    prods = {}                                       # fileID -> {"r": resultado, "sitios": {sitio: cobertura}}
    for s in sitios_de(a.sitios):
        caja = box(*SITIOS[s]["bbox"])
        try:
            res = asf.search(dataset="NISAR", processingLevel="GCOV", intersectsWith=caja.wkt,
                             start=a.desde, end=a.hasta, maxResults=500)
        except Exception as e:                       # noqa: BLE001
            print("  %s: la busqueda en ASF fallo (%s)" % (s, str(e)[:120]))
            continue
        vistos = set()
        for r in res:
            cob = 100.0 * shape(r.geometry).intersection(caja).area / caja.area
            if cob < a.cobertura_min:
                continue
            fid = str(r.properties.get("fileID") or r.properties.get("sceneName") or os.path.basename(str(r.properties.get("url", ""))))
            fid = fid.rsplit(".", 1)[0] if fid.lower().endswith((".h5", ".zip")) else fid
            d = prods.setdefault(fid, {"r": r, "sitios": {}})
            d["sitios"][s] = max(cob, d["sitios"].get(s, 0))
            vistos.add(fid)
        print("%s: %d productos GCOV con huella >= %.0f %% del sitio" % (s, len(vistos), a.cobertura_min))

    filas = []
    for fid, d in prods.items():
        p = d["r"].properties
        partes = fid.split("_")
        pol = next((x for x in partes if x in ("DHDH", "SHSH", "DVDV", "SVSV", "QPQP", "QDQD", "CLCL")), "")
        filas.append({"fecha": str(p.get("startTime"))[:10],
                      "orbita": "asc" if str(p.get("flightDirection", "")).upper().startswith("A") else "desc",
                      "track": str(p.get("pathNumber", "")), "frame": str(p.get("frameNumber", "")),
                      "pol": pol, "MB": round(_bytes_asf(p) / 1e6), "fileID": fid,
                      "sitios": " ".join("%s:%.0f%%" % (k, v) for k, v in sorted(d["sitios"].items())),
                      "delta": any(k in SITIOS_DELTA for k in d["sitios"])})
    t = pd.DataFrame(filas)
    if t.empty:
        print("No hay productos para esos sitios y fechas.")
        return
    t = t.sort_values(["fecha", "track"]).reset_index(drop=True)
    os.makedirs(ORIGINALES, exist_ok=True)
    lista = os.path.join(ORIGINALES, "NISAR_busqueda.csv")
    t.to_csv(lista, index=False, encoding="utf-8-sig")

    print("\nResumen por traza (un producto puede servir a varios sitios):")
    for (tr, fr, orb), g in t.groupby(["track", "frame", "orbita"]):
        print("  track %-4s frame %-4s %-4s %2d fechas (%s a %s)  sitios: %s"
              % (tr, fr, orb, len(g), g.fecha.min(), g.fecha.max(),
                 " ".join(sorted({x.split(":")[0] for v in g.sitios for x in v.split()}))))

    sel = t
    if a.fechas:
        sel = sel[sel.fecha.isin(a.fechas)]
    if a.tracks:
        sel = sel[sel.track.isin([str(x) for x in a.tracks])]
    if a.fechas or a.tracks:
        print("\nSeleccion (%d de %d):" % (len(sel), len(t)))
        for _, f in sel.iterrows():
            print("  %s %-4s track %-4s frame %-4s %-5s %5d MB  %s" % (f.fecha, f.orbita, f.track, f.frame, f.pol, f.MB, f.sitios))
    print("\nLista completa: %s" % lista)
    print("Total %s: %d productos, %.1f GB. Espacio libre: %s"
          % ("seleccionado" if (a.fechas or a.tracks) else "sin seleccionar", len(sel), sel.MB.sum() / 1e3, tam(libre(ORIGINALES))))
    if not a.confirmar:
        print("No se bajo nada. Elegir con --fechas AAAA-MM-DD ... y/o --tracks N ..., y repetir con --confirmar.")
        return
    if not (a.fechas or a.tracks):
        sys.exit("Para bajar hay que elegir --fechas o --tracks: bajar todo serian %.0f GB." % (t.MB.sum() / 1e3))
    from Tp1_04_buscar_asf import sesion_asf

    ses = sesion_asf(print)
    filas_inv = []
    for _, f in sel.iterrows():
        r = prods[f.fileID]["r"]
        d = (os.path.join(ORIGINALES, "NISAR_DELTA", "BANDA_L_NASA") if f.delta
             else os.path.join(ORIGINALES, "NISAR"))
        os.makedirs(d, exist_ok=True)
        url = r.properties.get("url", "")
        nombre = os.path.basename(url) or f.fileID
        final = os.path.join(d, nombre)
        esperado = _bytes_asf(r.properties)
        if os.path.exists(final) and (not esperado or os.path.getsize(final) == esperado):
            print("Ya esta: %s" % nombre)
            continue
        print("Bajando %s (%d MB) ..." % (nombre, f.MB))
        r.download(path=d, session=ses)
        ok = os.path.exists(final) and (not esperado or os.path.getsize(final) == esperado)
        print("   %s" % ("ok" if ok else "REVISAR: el tamano no coincide"))
        filas_inv.append({"tipo": "nisar", "sensor": "NISAR L2 GCOV banda L", "origen": url,
                          "destino": final, "bytes": os.path.getsize(final) if os.path.exists(final) else 0,
                          "verificado": ok, "cuando": ahora(), "sitios": f.sitios,
                          "fuente": "NASA - ISRO. NISAR L2 GCOV. ASF DAAC: https://search.asf.alaska.edu"})
    anotar(filas_inv)


# ------------------------------------------------------------ BIOMASS (banda P)
MAAP_STAC = "https://catalog.maap.eo.esa.int/catalogue/"
MAAP_TOKEN = "https://iam.maap.eo.esa.int/realms/esa-maap/protocol/openid-connect/token"
BIOMASS_CITA = "ESA. BIOMASS (banda P, 435 MHz). ESA MAAP: https://catalog.maap.eo.esa.int"


def _biomass_clave(pid):
    """(tipo, haz, inicio, cuadro) y (linea de base, codigo) de un producto BIOMASS.

    El catalogo publica varias versiones del mismo cuadro y la misma pasada
    (lineas de base 01 y 02, reprocesamientos). Se queda la mas nueva.
    """
    import re

    m = re.match(r"BIO_(\w+?)_(\w\w\w|FH|GN)__(\w\w\w?)_(\d{8}T\d{4})\d\d_\d{8}T\d{6}_T_G\d\d_M(\d\d)_C(\w\w)_T(\d{3})_F(\d{3})_(\d\d)_(\w+)$", pid)
    if not m:
        return (pid,), ("", ""), {}
    g = m.groups()
    datos = {"haz": g[0], "tipo": g[1], "inicio": g[3], "fase_M": g[4], "ciclo_C": g[5],
             "traza": g[6], "cuadro": g[7], "linea_base": g[8]}
    return (g[0], g[1], g[3], g[7]), (g[8], g[9]), datos


class _FichaMaap:
    """Ficha de acceso de ESA MAAP; se renueva sola antes de vencer."""

    def __init__(self, donde=""):
        import time
        self.t = time
        import getpass
        self.tok = os.environ.get("BIOMASS_TOKEN", "").strip()
        # El secreto de cliente "offline-token" es el mismo para todos los usuarios y ESA lo
        # publica en su guia (portal.maap.eo.esa.int, "using the long lasting token"). La ficha
        # personal (BIOMASS_TOKEN) no se guarda nunca: se pide en pantalla si no esta definida.
        self.sec = os.environ.get("BIOMASS_CLIENT_SECRET", "").strip() or "p1eL7uonXs6MDxtGbgKdPVRAmnGxHpVE"
        self.acc, self.vence = None, 0
        # La ficha personal se lee de un archivo de texto en la carpeta del usuario de Windows
        # (fuera de la carpeta del curso, para que no se copie a los estudiantes).
        # --ficha puede ser el archivo o la carpeta donde se lo guardo: en una carpeta se busca
        # el archivo de texto cuyo contenido tiene forma de ficha (empieza con eyJ y tiene tres
        # partes separadas por puntos). Nunca se muestra el contenido.
        import re
        archivo = donde or os.path.join(os.path.expanduser("~"), "ficha_maap.txt")
        if not self.tok and os.path.isdir(archivo):
            carpeta, archivo = archivo, ""
            for f in sorted(glob.glob(os.path.join(carpeta, "*"))):
                if not os.path.isfile(f) or os.path.getsize(f) > 20000:
                    continue
                try:
                    with open(f, encoding="utf-8-sig", errors="ignore") as h:
                        t = "".join(h.read().split()).strip('"\'')
                except OSError:
                    continue
                if re.fullmatch(r"eyJ[\w-]+\.[\w-]+\.[\w-]+", t):
                    archivo = f
                    break
            if not archivo:
                sys.exit("En %s no hay ningun archivo de texto con una ficha de ESA MAAP." % carpeta)
        if not self.tok and os.path.exists(archivo):
            with open(archivo, encoding="utf-8-sig", errors="ignore") as f:
                self.tok = f.read()
            print("Ficha de ESA MAAP leida de %s" % archivo)
        # se quitan espacios, saltos de linea y comillas que se cuelan al copiar
        self.tok = "".join(self.tok.split()).strip('"\'')
        if not self.tok:
            sys.exit("Falta la ficha de ESA MAAP. Generarla en "
                     "https://portal.maap.eo.esa.int/ini/services/auth/token/90dToken.php y guardarla "
                     "con el Bloc de notas en %s (ver BIOMASS\\LEEME.md)." % archivo)
        if self.tok.count(".") != 2:
            sys.exit("El contenido de %s no parece una ficha de ESA MAAP (debe tener tres partes "
                     "separadas por puntos). Copiarla de nuevo, completa." % archivo)
        if not self.tok:
            sys.exit("Sin ficha de ESA MAAP no se puede bajar. Ver BIOMASS\\LEEME.md.")

    def __call__(self):
        import requests
        if self.acc and self.t.time() < self.vence - 60:
            return self.acc
        r = requests.post(MAAP_TOKEN, data={"client_id": "offline-token", "client_secret": self.sec,
                                            "grant_type": "refresh_token", "refresh_token": self.tok},
                          timeout=60)
        if r.status_code != 200:
            sys.exit("ESA MAAP rechazo la ficha (%d): %s. Si dice invalid_grant: la ficha esta "
                     "incompleta o vencida; generar una nueva en el portal, guardarla en "
                     "ficha_maap.txt y repetir." % (r.status_code, r.text[:200]))
        j = r.json()
        self.acc, self.vence = j["access_token"], self.t.time() + int(j.get("expires_in", 300))
        return self.acc


def _biomass_buscar(cat, col, bbox, desde, hasta):
    import time
    for intento in range(4):
        try:
            return list(cat.search(collections=[col], bbox=list(bbox),
                                   datetime="%sT00:00:00Z/%sT23:59:59Z" % (desde, hasta),
                                   max_items=1000).items())
        except Exception as e:                       # noqa: BLE001
            print("   el catalogo respondio con error (%s); reintento en 30 s" % str(e)[:60].replace("\n", " "))
            time.sleep(30)
    raise RuntimeError("ESA MAAP no respondio despues de 4 intentos (%s)" % col)


def cmd_biomass(a):
    """Busca y baja BIOMASS para varios sitios, sin repetir productos.

    Un mismo producto cubre varios sitios: se guarda una sola vez en
    BIOMASS\\<coleccion>\\<producto>\\ y la tabla busqueda_biomass.csv dice
    a que sitios cubre. De cada cuadro y pasada se queda la version mas nueva.
    """
    import requests
    from pystac_client import Client

    desde = a.desde or "2025-04-29"
    hasta = a.hasta or "2026-12-31"
    base = os.path.join(ORIGINALES, "BIOMASS")
    os.makedirs(base, exist_ok=True)
    cat = Client.open(MAAP_STAC)
    elegidos, sitios_por, versiones = {}, {}, 0
    for s in sitios_de(a.sitios):
        for col in a.colecciones:
            items = _biomass_buscar(cat, col, SITIOS[s]["bbox"], desde, hasta)
            print("%-22s %-15s %4d productos en el catalogo" % (s, col, len(items)))
            for it in items:
                versiones += 1
                k, v, _ = _biomass_clave(it.id)
                k = (col,) + k
                if k not in elegidos or v > elegidos[k][0]:
                    elegidos[k] = (v, it)
                sitios_por.setdefault(k, set()).add(s)
    filas = []
    for k, (v, it) in sorted(elegidos.items(), key=lambda x: x[1][1].id):
        _, _, d = _biomass_clave(it.id)
        b = ([it.assets["product"].extra_fields.get("file:size")] if "product" in it.assets
             else [x.extra_fields.get("file:size") for x in it.assets.values()])
        filas.append(dict(coleccion=k[0], producto=it.id,
                          fecha=it.datetime.strftime("%Y-%m-%d") if it.datetime else "",
                          sitios=" ".join(sorted(sitios_por[k])),
                          zip_completo="si" if "product" in it.assets else "no",
                          MB=round(sum(x for x in b if x) / 1e6, 1) if any(b) else "", **d))
    t = pd.DataFrame(filas)
    t.to_csv(os.path.join(base, "busqueda_biomass.csv"), index=False, encoding="utf-8-sig")
    print("\nVersiones en el catalogo: %d. Productos distintos (version mas nueva): %d"
          % (versiones, len(t)))
    for col, g in t.groupby("coleccion"):
        mb = pd.to_numeric(g.MB, errors="coerce")
        print("   %-15s %4d productos  %s  %s a %s" % (col, len(g),
              ("%.1f GB" % (mb.sum() / 1e3)) if mb.notna().any() else "peso no informado",
              g.fecha.min(), g.fecha.max()))
    print("Tabla: %s   Libre en disco: %s" % (os.path.join(base, "busqueda_biomass.csv"), tam(libre(ORIGINALES))))
    if not a.confirmar:
        print("No se bajo nada. Repetir con --confirmar (y la ficha de ESA MAAP) para bajar;"
              " --max N baja solo los N primeros (prueba).")
        return
    ficha = _FichaMaap(a.ficha)
    lista = [elegidos[k][1] for k in sorted(elegidos, key=lambda k: elegidos[k][1].id)]
    if a.max:
        lista = lista[:a.max]
    filas_inv, n = [], 0
    for it in lista:
        n += 1
        col = it.collection_id or "BIOMASS"
        d = os.path.join(base, col)
        os.makedirs(d, exist_ok=True)
        print("[%d/%d] %s" % (n, len(lista), it.id))
        listo = os.path.join(d, it.id, ".completo")
        if os.path.exists(listo):
            print("     ya estaba")
            continue
        if "product" not in it.assets:
            print("     REVISAR: el catalogo no ofrece el producto completo (.zip); no se baja")
            continue
        asset = it.assets["product"]
        z = os.path.join(d, it.id + ".zip")
        esperado = asset.extra_fields.get("file:size")
        ok = False
        import zipfile
        for intento in range(3):
            try:
                if ok and not zipfile.is_zipfile(z):
                    print("     el .zip llego cortado; se baja de nuevo (%d/3)" % (intento + 1))
                    ok = False
                with requests.get(asset.href, headers={"Authorization": "Bearer %s" % ficha()},
                                  stream=True, timeout=900) as r:
                    if r.status_code in (401, 403):
                        ficha.acc = None
                        print("     acceso rechazado (%d); renuevo la ficha" % r.status_code)
                        continue
                    r.raise_for_status()
                    with open(z + ".part", "wb") as f:
                        for trozo in r.iter_content(1 << 20):
                            f.write(trozo)
                os.replace(z + ".part", z)
                ok = (not esperado or os.path.getsize(z) == esperado) and zipfile.is_zipfile(z)
                if ok:
                    break
                print("     el .zip llego cortado o danado; se baja de nuevo (%d/3)" % (intento + 1))
            except Exception as e:                   # noqa: BLE001
                print("     error (%s); reintento" % str(e)[:80])
        if ok:
            import zipfile
            try:
                with zipfile.ZipFile(z) as zf:
                    malo = zf.testzip()
                    if malo:
                        raise RuntimeError("archivo danado dentro del zip: %s" % malo)
                    raiz = os.path.join(d, it.id)
                    nombres = zf.namelist()
                    # el zip trae la carpeta del producto; si no, se la crea
                    destino = d if all(x.startswith(it.id + "/") for x in nombres) else raiz
                    zf.extractall(destino)
                os.makedirs(raiz, exist_ok=True)
                open(listo, "w").close()
                os.remove(z)
                print("     ok (%s, descomprimido)" % tam(esperado or 0))
            except Exception as e:                   # noqa: BLE001
                ok = False
                print("     REVISAR: no se pudo descomprimir (%s); queda el .zip" % str(e)[:80])
        else:
            print("     REVISAR: la descarga no coincide con el tamano del catalogo")
        filas_inv.append({"tipo": "biomass", "sensor": "BIOMASS %s" % col, "origen": asset.href,
                          "destino": os.path.join(d, it.id), "bytes": esperado or 0,
                          "verificado": ok, "cuando": ahora(),
                          "sitios": " ".join(sorted(sitios_por.get((col,) + _biomass_clave(it.id)[0], []))),
                          "fuente": BIOMASS_CITA})
    anotar(filas_inv)


# ------------------------------------------------------------ CCI Biomass
def _cci_listar(url):
    """Lista un directorio de dap.ceda.ac.uk (devuelve nombres)."""
    import re
    import requests

    r = requests.get(url.rstrip("/") + "/?json", timeout=60)
    if r.ok and r.headers.get("content-type", "").startswith("application/json"):
        j = r.json()
        items = j.get("items") or j.get("children") or []
        return [i.get("name") or i.get("path", "").rstrip("/").split("/")[-1] for i in items]
    r = requests.get(url.rstrip("/") + "/", timeout=60)
    r.raise_for_status()
    return sorted(set(re.findall(r'href="([^"?/][^"?]*?)/?"', r.text)))


def _teselas(bbox):
    """Teselas de 10 x 10 grados del CCI que pueden tocar la caja.

    El nombre de la tesela es una esquina (en las versiones publicadas, la
    noroeste). Se proponen las dos convenciones posibles y despues se abre
    cada candidata y se verifica que su extension cubra la caja: un nombre
    mal supuesto no produce un recorte vacio, se descarta.
    """
    lon0, lat0, lon1, lat1 = bbox
    nombres = set()
    for lat in np.arange(np.floor(lat0 / 10) * 10, lat1, 10):
        for lon in np.arange(np.floor(lon0 / 10) * 10, lon1, 10):
            for esquina in (int(lat + 10), int(lat)):
                ns = "N%02d" % esquina if esquina >= 0 else "S%02d" % -esquina
                ew = "E%03d" % int(lon) if lon >= 0 else "W%03d" % int(-lon)
                nombres.add(ns + ew)
    return sorted(nombres)


def cmd_cci(a):
    import rasterio
    from rasterio.windows import from_bounds
    from rasterio.merge import merge

    base = "%s/%s" % (CCI_BASE, a.version)
    try:
        sub = _cci_listar(base)
    except Exception as e:                           # noqa: BLE001
        sys.exit("No se pudo listar %s (%s). Revise la conexion o la version (--version)." % (base, str(e)[:100]))
    carpeta_tif = "geotiff" if "geotiff" in sub else next((x for x in sub if "tif" in x.lower()), None)
    if not carpeta_tif:
        sys.exit("No encuentro la carpeta de GeoTIFF en %s: %s" % (base, sub))
    filas = []
    for anio in a.anios:
        url_anio = "%s/%s/%s" % (base, carpeta_tif, anio)
        try:
            archivos = [f for f in _cci_listar(url_anio) if f.endswith(".tif")]
        except Exception as e:                       # noqa: BLE001
            print("  %s: sin listado (%s)" % (anio, str(e)[:80]))
            continue
        for s in sitios_de(a.sitios):
            bbox = SITIOS[s]["bbox"]
            dest = os.path.join(ORIGINALES, "CCI_BIOMASS", a.version, s)
            os.makedirs(dest, exist_ok=True)
            for var in ("AGB", "AGB_SD"):
                salida = os.path.join(dest, "%s_CCI_%s_%s_%s.tif" % (s, var, anio, a.version))
                if os.path.exists(salida):
                    continue
                tes = [f for f in archivos for t in _teselas(bbox)
                       if f.startswith(t) and ("-%s-MERGED" % var) in f]
                if not tes:
                    print("  %s %s %s: no hay tesela %s. Archivos del anio (primeros): %s"
                          % (s, anio, var, ", ".join(_teselas(bbox)), ", ".join(archivos[:4])))
                    continue
                trozos, perfil = [], None
                for f in tes:
                    with rasterio.open("/vsicurl/%s/%s" % (url_anio, f)) as src:
                        b = src.bounds
                        if b.left >= bbox[2] or b.right <= bbox[0] or b.bottom >= bbox[3] or b.top <= bbox[1]:
                            continue                  # la tesela no cubre el sitio
                        w = from_bounds(*bbox, transform=src.transform).round_offsets().round_lengths()
                        w = w.intersection(rasterio.windows.Window(0, 0, src.width, src.height))
                        arr = src.read(1, window=w)
                        perfil = src.profile.copy()
                        perfil.update(width=arr.shape[1], height=arr.shape[0],
                                      transform=src.window_transform(w), compress="deflate", tiled=False)
                        trozos.append((arr, perfil.copy()))
                if not trozos:
                    print("  %s %s %s: ninguna tesela cubre el sitio" % (s, anio, var))
                    continue
                if len(trozos) == 1:
                    arr, perfil = trozos[0]
                else:
                    mem = []
                    from rasterio.io import MemoryFile
                    for arr_i, p_i in trozos:
                        m = MemoryFile()
                        with m.open(**p_i) as d:
                            d.write(arr_i, 1)
                        mem.append(m.open())
                    arr, tr = merge(mem)
                    arr = arr[0]
                    perfil.update(width=arr.shape[1], height=arr.shape[0], transform=tr)
                with rasterio.open(salida, "w", **perfil) as dst:
                    dst.write(arr, 1)
                    dst.update_tags(FUENTE=CCI_CITA, PROCESO="Recorte del sitio %s, sin remuestrear (EPSG:4326, ~100 m)" % s,
                                    VARIABLE="%s en Mg/ha, anio %s" % (var, anio))
                print("  %-22s %s %-6s %s  (%d x %d px)" % (s, anio, var, ", ".join(tes), arr.shape[1], arr.shape[0]))
                filas.append({"tipo": "cci_biomass", "sensor": "CCI Biomass %s" % a.version,
                              "origen": "%s/%s" % (url_anio, ", ".join(tes)), "destino": salida,
                              "bytes": os.path.getsize(salida), "verificado": True, "cuando": ahora(),
                              "fuente": CCI_CITA})
    anotar(filas)


def cmd_cci_resumen(a):
    import rasterio

    filas = []
    for s in sitios_de(a.sitios):
        for f in sorted(glob.glob(os.path.join(ORIGINALES, "CCI_BIOMASS", a.version, s, "%s_CCI_AGB_*.tif" % s))):
            if "_CCI_AGB_SD_" in f:
                continue
            anio = f.split("_")[-2]
            with rasterio.open(f) as src:
                x = src.read(1).astype("float64")
                nd = src.nodata
            fsd = f.replace("_CCI_AGB_", "_CCI_AGB_SD_")
            sd = None
            if os.path.exists(fsd):
                with rasterio.open(fsd) as src:
                    sd = src.read(1).astype("float64")
            ok = np.isfinite(x) & (x >= 0) & ((x != nd) if nd is not None else True)
            con = ok & (x > 0)
            filas.append({
                "sitio": s, "anio": anio, "pixeles": int(ok.sum()),
                "%_con_biomasa": round(100 * con.sum() / max(ok.sum(), 1), 1),
                "agb_media_Mg_ha": round(float(x[ok].mean()), 1) if ok.any() else np.nan,
                "agb_mediana_donde_hay_Mg_ha": round(float(np.median(x[con])), 1) if con.any() else np.nan,
                "agb_p90_Mg_ha": round(float(np.percentile(x[con], 90)), 1) if con.any() else np.nan,
                "sd_media_Mg_ha": round(float(sd[con].mean()), 1) if sd is not None and con.any() else np.nan,
                "%_agb_40_o_mas": round(100 * (ok & (x >= 40)).sum() / max(ok.sum(), 1), 1),
                "sd_relativa_%": round(float(100 * np.nanmean(sd[con] / x[con])), 0) if sd is not None and con.any() else np.nan,
                "sd_relativa_mediana_%": round(float(100 * np.nanmedian(sd[con] / x[con])), 0) if sd is not None and con.any() else np.nan,
            })
    if not filas:
        sys.exit("No hay recortes CCI: correr antes  python datos_crudos.py cci ...")
    t = pd.DataFrame(filas)
    print(t.to_string(index=False))
    out = os.path.join(ORIGINALES, "CCI_BIOMASS", a.version, "resumen_por_sitio.csv")
    t.to_csv(out, index=False, encoding="utf-8-sig")
    print("\nTabla: %s" % out)
    print("Lectura: una sd_relativa mayor que 50 % dice que el mapa no distingue ese valor de cero;")
    print("en el Espinal y en el Delta la biomasa es baja y esa es la zona de mayor error del CCI.")


# ------------------------------------------------------------ Planetary Computer
def _ids_tp1(sitio):
    """Escenas que el Tp1 (paso 3) dejo como candidatas en el sitio.

    Sentinel-2: todas las teselas verificadas de los dias cuyo MOSAICO quedo como
    candidato (un sitio grande necesita todas las teselas del dia). Sentinel-1
    RTC: las pasadas candidatas. Devuelve {coleccion: [ids]} o None si no hay planilla.
    """
    t = ruta_tp("Tp1", "05_Resultados", "04_Tablas", "planilla_MPC_%s.csv" % sitio)
    if not os.path.exists(t):
        return None
    d = pd.read_csv(t, encoding="utf-8-sig", dtype=str).fillna("")
    mos = d[(d.sensor == "Sentinel-2 mosaico del dia") & (d.decision == "candidata")]
    dias = {(r.fecha, r.id.split()[1] if len(r.id.split()) > 1 else "") for r in mos.itertuples()}
    s2 = d[(d.sensor == "Sentinel-2") & (pd.to_numeric(d["pixeles_validos_%"], errors="coerce") > 0)]
    ids_s2 = [r.id for r in s2.itertuples()
              if (r.fecha, r.id.split("_")[3] if r.id.count("_") >= 3 else "") in dias]
    s1 = d[(d.sensor == "Sentinel-1 RTC") & (d.decision == "candidata")]
    return {"sentinel-2-l2a": sorted(set(ids_s2)), "sentinel-1-rtc": sorted(set(s1.id))}


def cmd_planetary(a):
    import json
    import planetary_computer
    import pystac_client
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds

    # Sentinel-2: las 10 bandas de 10 y 20 m (B01 y B09, de 60 m y para la atmosfera, no),
    # la clasificacion de escena (SCL) y los XML de metadatos del producto y del granulo.
    BANDAS = {"sentinel-2-l2a": ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12", "SCL"],
              "sentinel-1-rtc": ["vv", "vh", "hh", "hv"], "alos-palsar-mosaic": ["HH", "HV"],
              "cop-dem-glo-30": ["data"], "jrc-gsw": ["occurrence"]}
    XML = {"sentinel-2-l2a": ["granule-metadata", "product-metadata", "inspire-metadata", "datastrip-metadata"]}
    FIJAS = ("cop-dem-glo-30", "jrc-gsw")
    cat = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
    plan = []
    for s in sitios_de(a.sitios):
        if a.desde_tp1:
            ids = _ids_tp1(s)
            if ids is None:
                print("  %-22s sin planilla del Tp1 (paso 3): se saltea" % s)
                continue
            for col, lista in ids.items():
                items = []
                for k in range(0, len(lista), 50):
                    items += list(cat.search(collections=[col], ids=lista[k:k + 50]).items())
                print("  %-22s %-20s %3d escenas elegidas por el Tp1 (%d fechas)"
                      % (s, col, len(items), len({(x.datetime or _dt.datetime(2000, 1, 1)).date() for x in items})))
                plan += [(s, col, it) for it in items]
            cols = [c for c in a.colecciones if c in FIJAS]
        else:
            cols = a.colecciones
        d0, d1 = (a.desde, a.hasta) if a.desde else VENTANAS[s]
        for col in cols:
            fechas = "1900-01-01/2100-01-01" if col in FIJAS else "%s/%s" % (d0, d1)
            q = {"eo:cloud_cover": {"lt": a.nubes_max}} if col == "sentinel-2-l2a" else None
            items = list(cat.search(collections=[col], bbox=SITIOS[s]["bbox"], datetime=fechas, query=q).items())
            print("  %-22s %-20s %3d escenas" % (s, col, len(items)))
            plan += [(s, col, it) for it in items]
    print("Total: %d escenas. Espacio libre: %s" % (len(plan), tam(libre(ORIGINALES))))
    if not a.confirmar:
        print("\nNo se bajo nada. Vuelva a correr con --confirmar.")
        return
    import requests
    filas = []
    for n, (s, col, it) in enumerate(plan, 1):
        f = (it.datetime or _dt.datetime(2000, 1, 1)).strftime("%Y%m%d")
        dest = os.path.join(ORIGINALES, "PLANETARY", s, col, "%s_%s" % (f, it.id[:60]))
        if os.path.exists(os.path.join(dest, ".completo")):
            continue
        os.makedirs(dest, exist_ok=True)
        it = planetary_computer.sign(it)          # firma nueva por escena: las firmas vencen
        # metadatos completos del catalogo (sensor, orbita, angulos, procesamiento...)
        with open(os.path.join(dest, "item_STAC.json"), "w", encoding="utf-8") as fj:
            json.dump(it.to_dict(), fj, ensure_ascii=False, indent=1)
        for x in XML.get(col, []):
            if x in it.assets:
                try:
                    r = requests.get(it.assets[x].href, timeout=120)
                    if r.ok:
                        with open(os.path.join(dest, "%s.xml" % x), "wb") as fx:
                            fx.write(r.content)
                except Exception as e:               # noqa: BLE001
                    print("   %s %s: %s" % (it.id, x, str(e)[:80]))
        errores = 0
        for b in BANDAS[col]:
            if b not in it.assets:
                continue
            salida = os.path.join(dest, "%s.tif" % b)
            if os.path.exists(salida):
                continue
            try:
                with rasterio.open(it.assets[b].href) as src:
                    caja = transform_bounds("EPSG:4326", src.crs, *SITIOS[s]["bbox"], densify_pts=21)
                    w = from_bounds(*caja, transform=src.transform).round_offsets().round_lengths()
                    w = w.intersection(rasterio.windows.Window(0, 0, src.width, src.height))
                    arr = src.read(1, window=w)
                    p = src.profile.copy()
                    p.update(driver="GTiff", width=arr.shape[1], height=arr.shape[0],
                             transform=src.window_transform(w), compress="deflate", tiled=True,
                             blockxsize=256, blockysize=256)
                    with rasterio.open(salida + ".part", "w", **p) as dst:
                        dst.write(arr, 1)
                        dst.set_band_description(1, b)
                        dst.update_tags(**src.tags())
                        dst.update_tags(1, **src.tags(1))
                        dst.update_tags(FUENTE="Microsoft Planetary Computer, coleccion %s, item %s" % (col, it.id),
                                        FECHA_ADQUISICION=str(it.datetime),
                                        BANDA=b, SITIO=s,
                                        PROCESO="Recorte del sitio %s en la proyeccion y pixel NATIVOS (sin remuestrear)" % s,
                                        METADATOS="item_STAC.json en esta carpeta")
                    os.replace(salida + ".part", salida)
            except Exception as e:                   # noqa: BLE001
                errores += 1
                print("   %s %s: %s" % (it.id, b, str(e)[:80]))
        if not errores:
            open(os.path.join(dest, ".completo"), "w").close()
        filas.append({"tipo": "planetary", "sensor": col, "origen": it.id, "destino": dest,
                      "bytes": peso(dest), "verificado": errores == 0, "cuando": ahora(),
                      "fuente": "Microsoft Planetary Computer, %s" % col, "sitios": s})
        print("  [%d/%d] %s %s %s%s" % (n, len(plan), s, col, it.id, "" if not errores else "  (REVISAR)"))
    anotar(filas)

# ------------------------------------------------------------ Landsat 8 y 9 (Planetary Computer)
# Para cada fecha Sentinel-2 que usan los practicos (armar_subsets.py), la pasada
# Landsat 8 u 9 MAS CERCANA (Coleccion 2, Nivel 2: reflectancia y temperatura de
# superficie) con el sitio despejado segun QA_PIXEL. Landsat 9 da imagenes desde el
# 31/10/2021; antes, solo Landsat 8. Se guarda en
# PLANETARY\<SITIO>\landsat-c2-l2\<AAAAMMDD>_<id>\ y la eleccion en
# PLANETARY\landsat_elegidas.csv (la lee armar_subsets.py).
LANDSAT_FECHAS = {                      # sitio: fechas Sentinel-2 de los practicos (practicos)
    "B_CONCORDIA": {"20231104": "Tp1, Tp6", "20260916": "Tp10"},
    "A2_IBICUY": {"20260916": "Tp2, Tp3"},
    "A1_DELTA_QUEMAS": {"20200715": "Tp5", "20201013": "Tp5"},
    "E1_DIAMANTE_BARRANCA": {"20181004": "Tp7", "20181019": "Tp7"},
    "F_BOVRIL": {"20230910": "Tp8"},
    "C_FEDERAL": {"20210806": "Tp9", "20250924": "Tp9", "20260916": "Tp9"},
}
LANDSAT_BANDAS = ["coastal", "blue", "green", "red", "nir08", "swir16", "swir22", "lwir11",
                  "qa_pixel", "qa_radsat", "qa_aerosol", "qa", "atran", "cdist", "drad", "urad", "trad",
                  "emis", "emsd"]
LANDSAT_META = ["mtl.txt", "mtl.xml", "mtl.json", "ang"]
LANDSAT_ESENCIALES = {"coastal", "blue", "green", "red", "nir08", "swir16", "swir22", "lwir11", "qa_pixel", "qa"}
LANDSAT_CSV = os.path.join(ORIGINALES, "PLANETARY", "landsat_elegidas.csv")


def _qa_sitio(it, sitio):
    """(pixeles del sitio con dato, despejados) segun QA_PIXEL (bit 0 relleno; 6 despejado; 7 agua)."""
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds, Window
    with rasterio.open(it.assets["qa_pixel"].href) as src:
        caja = transform_bounds("EPSG:4326", src.crs, *SITIOS[sitio]["bbox"], densify_pts=21)
        w = from_bounds(*caja, transform=src.transform).round_offsets().round_lengths()
        w = w.intersection(Window(0, 0, src.width, src.height))
        q = src.read(1, window=w).astype("uint16")
    con_dato = (q & 1) == 0
    desp = con_dato & (((q >> 6) & 1) | ((q >> 7) & 1)).astype(bool)
    return int(con_dato.sum()), int(desp.sum())


def _px_sitio(sitio):
    """Pixeles de 30 m que tiene la caja del sitio (para la cobertura)."""
    o, s_, e, n = SITIOS[sitio]["bbox"]
    lat = math.radians((s_ + n) / 2.0)
    return (e - o) * 111320.0 * math.cos(lat) * (n - s_) * 110574.0 / 900.0


def cmd_landsat(a):
    import csv
    import json
    import planetary_computer
    import pystac_client
    import rasterio
    import requests
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds

    cat = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1",
                                    modifier=planetary_computer.sign_inplace)
    sitios = [s for s in sitios_de(a.sitios) if s in LANDSAT_FECHAS]
    elegidas, sin_escena = [], []
    for s in sitios:
        for f_s2, tps in sorted(LANDSAT_FECHAS[s].items()):
            d = _dt.datetime.strptime(f_s2, "%Y%m%d")
            rango = "%s/%s" % ((d - _dt.timedelta(days=a.dias)).strftime("%Y-%m-%d"),
                               (d + _dt.timedelta(days=a.dias)).strftime("%Y-%m-%d"))
            items = []
            for intento in range(5):
                try:
                    items = list(cat.search(collections=["landsat-c2-l2"], bbox=SITIOS[s]["bbox"],
                                            datetime=rango).items())
                    break
                except Exception as e:                       # noqa: BLE001
                    print("   catalogo: %s (reintento %d)" % (str(e)[:80], intento + 1))
                    time.sleep(10 * (intento + 1))
            items = [it for it in items if it.properties.get("platform") in ("landsat-8", "landsat-9")]
            # pasadas = dia + satelite (un sitio puede caer en dos cuadros WRS de la misma pasada)
            grupos = {}
            for it in items:
                grupos.setdefault((it.datetime.strftime("%Y%m%d"), it.properties["platform"]), []).append(it)
            orden = sorted(grupos, key=lambda k: (abs((_dt.datetime.strptime(k[0], "%Y%m%d") - d).days), k[1]))
            mejor = None
            total = _px_sitio(s)
            print("\n%s  Sentinel-2 %s (%s): %d pasadas Landsat 8/9 a +-%d dias"
                  % (s, f_s2, tps, len(orden), a.dias))
            for k in orden:
                n_dato = n_desp = 0
                for it in grupos[k]:
                    try:
                        x, y = _qa_sitio(it, s)
                    except Exception as e:                   # noqa: BLE001
                        print("     %s: QA_PIXEL no se pudo leer (%s)" % (it.id, str(e)[:60]))
                        continue
                    n_dato, n_desp = n_dato + x, n_desp + y      # cuadros WRS de la misma pasada (se solapan poco)
                cob = 100.0 * min(1.0, n_dato / total)
                desp = 100.0 * n_desp / n_dato if n_dato else 0.0
                dias = (_dt.datetime.strptime(k[0], "%Y%m%d") - d).days
                ok = cob >= a.cobertura_min and desp >= a.despejado_min
                print("   %s %s  %+3d dias  cobertura %5.1f %%  despejado %5.1f %%  %s"
                      % (k[0], k[1], dias, cob, desp, "<- ELEGIDA" if ok and mejor is None else ""))
                fila = dict(sitio=s, fecha_s2=f_s2, practicos=tps, fecha_landsat=k[0], plataforma=k[1],
                            dias=dias, cobertura_pct=round(cob, 1), despejado_pct=round(desp, 1),
                            ids=" ".join(it.id for it in grupos[k]))
                if ok and mejor is None:
                    mejor = (fila, grupos[k])
                    break
            if mejor is None:
                print("   NINGUNA con cobertura >= %g %% y despejado >= %g %%: se saltea esta fecha "
                      "(bajar --despejado_min o subir --dias)" % (a.cobertura_min, a.despejado_min))
                sin_escena.append(dict(sitio=s, fecha_s2=f_s2, practicos=tps, fecha_landsat="", plataforma="ninguna",
                                       dias="", cobertura_pct="", despejado_pct="",
                                       ids="sin pasada Landsat 8/9 a +-%d dias con >= %g %% de cobertura y >= %g %% "
                                           "despejado" % (a.dias, a.cobertura_min, a.despejado_min)))
                continue
            elegidas.append(mejor)
    print("\nElegidas: %d escenas. Espacio libre: %s" % (len(elegidas), tam(libre(ORIGINALES))))
    if not a.confirmar:
        print("\nNo se bajo nada. Vuelva a correr con --confirmar.")
        return
    previas = []
    if os.path.exists(LANDSAT_CSV):
        with open(LANDSAT_CSV, encoding="utf-8-sig") as fc:
            previas = [r for r in csv.DictReader(fc)]
    claves = {(f["sitio"], f["fecha_s2"]) for f, _ in elegidas} | {(f["sitio"], f["fecha_s2"]) for f in sin_escena}
    previas = [r for r in previas if (r["sitio"], r["fecha_s2"]) not in claves] + sin_escena
    filas_inv = []
    for n, (fila, its) in enumerate(elegidas, 1):
        s = fila["sitio"]
        errores = 0
        for it in its:
            dest = os.path.join(ORIGINALES, "PLANETARY", s, "landsat-c2-l2", "%s_%s" % (fila["fecha_landsat"], it.id))
            if os.path.exists(os.path.join(dest, ".completo")):
                continue
            os.makedirs(dest, exist_ok=True)
            it = planetary_computer.sign(it)
            with open(os.path.join(dest, "item_STAC.json"), "w", encoding="utf-8") as fj:
                json.dump(it.to_dict(), fj, ensure_ascii=False, indent=1)
            for m in LANDSAT_META:               # metadatos originales de USGS, sin tocar
                if m not in it.assets:
                    continue
                nom = os.path.basename(it.assets[m].href.split("?")[0])
                try:
                    r = requests.get(it.assets[m].href, timeout=120)
                    if r.status_code == 404 and m == "mtl.json":
                        # algunas escenas no tienen el MTL.json en el Planetary Computer: el MTL.xml y
                        # el MTL.txt tienen lo mismo
                        with open(os.path.join(dest, "MTL_json_no_disponible.txt"), "w", encoding="utf-8") as fx:
                            fx.write("El Planetary Computer no tiene el MTL.json de esta escena (404). "
                                     "El MTL.xml y el MTL.txt de USGS tienen los mismos metadatos.\n")
                        continue
                    r.raise_for_status()
                    with open(os.path.join(dest, nom), "wb") as fx:
                        fx.write(r.content)
                except Exception as e:                       # noqa: BLE001
                    errores += 1
                    print("   %s %s: %s" % (it.id, m, str(e)[:80]))
            for b in LANDSAT_BANDAS:
                if b not in it.assets:
                    continue
                nom = os.path.basename(it.assets[b].href.split("?")[0])      # nombre de USGS (..._SR_B4.TIF)
                salida = os.path.join(dest, nom)
                if os.path.exists(salida):
                    continue
                for intento in range(3):             # un 403 suele ser pasajero: se firma de nuevo y se reintenta
                    try:
                        _recortar_landsat(planetary_computer.sign(it.assets[b].href), salida, b, it, s)
                        break
                    except Exception as e:                   # noqa: BLE001
                        if intento == 2:
                            print("   %s %s: %s" % (it.id, b, str(e)[-120:]))
                            if b in LANDSAT_ESENCIALES:
                                errores += 1
                            else:                    # banda auxiliar de la temperatura: se anota y se sigue
                                with open(os.path.join(dest, "bandas_no_disponibles.txt"), "a", encoding="utf-8") as fx:
                                    fx.write("%s (%s): el Planetary Computer no la entrego tras 3 intentos. Es una "
                                             "banda auxiliar del calculo de la temperatura; no la usa ningun "
                                             "practico.\n" % (nom, b))
                        else:
                            time.sleep(5 * (intento + 1))
            if not errores:
                open(os.path.join(dest, ".completo"), "w").close()
            filas_inv.append({"tipo": "planetary", "sensor": "landsat-c2-l2 (%s)" % fila["plataforma"],
                              "origen": it.id, "destino": dest, "bytes": peso(dest), "verificado": errores == 0,
                              "cuando": ahora(), "fuente": "USGS / Microsoft Planetary Computer, landsat-c2-l2",
                              "sitios": s})
        print("  [%d/%d] %s %s %s%s" % (n, len(elegidas), s, fila["fecha_landsat"], fila["plataforma"],
                                       "" if not errores else "  (REVISAR)"))
        previas.append({k: str(v) for k, v in fila.items()})
    _escribir_landsat_csv(previas)
    anotar(filas_inv)
    print("\nEleccion anotada en %s" % LANDSAT_CSV)


def _escribir_landsat_csv(previas):
    import csv
    os.makedirs(os.path.dirname(LANDSAT_CSV), exist_ok=True)
    campos = ["sitio", "fecha_s2", "practicos", "fecha_landsat", "plataforma", "dias", "cobertura_pct",
              "despejado_pct", "ids"]
    with open(LANDSAT_CSV, "w", encoding="utf-8-sig", newline="") as fc:
        w = csv.DictWriter(fc, fieldnames=campos)
        w.writeheader()
        for r in sorted(previas, key=lambda r: (r["sitio"], r["fecha_s2"])):
            w.writerow({k: r.get(k, "") for k in campos})


def _recortar_landsat(href, salida, b, it, s):
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds
    with rasterio.open(href) as src:
        caja = transform_bounds("EPSG:4326", src.crs, *SITIOS[s]["bbox"], densify_pts=21)
        w = from_bounds(*caja, transform=src.transform).round_offsets().round_lengths()
        w = w.intersection(rasterio.windows.Window(0, 0, src.width, src.height))
        arr = src.read(1, window=w)
        p = src.profile.copy()
        p.update(driver="GTiff", width=arr.shape[1], height=arr.shape[0],
                 transform=src.window_transform(w), compress="deflate", tiled=True,
                 blockxsize=256, blockysize=256)
        with rasterio.open(salida + ".part", "w", **p) as dst:
            dst.write(arr, 1)
            dst.set_band_description(1, b)
            dst.update_tags(**src.tags())
            dst.update_tags(1, **src.tags(1))
            dst.update_tags(FUENTE="USGS Landsat Coleccion 2 Nivel 2, Microsoft Planetary Computer, "
                                   "item %s" % it.id,
                            FECHA_ADQUISICION=str(it.datetime), BANDA=b, SITIO=s,
                            PROCESO="Recorte del sitio %s en la proyeccion y pixel NATIVOS "
                                    "(sin remuestrear)" % s,
                            METADATOS="MTL y ANG de USGS e item_STAC.json en esta carpeta")
    os.replace(salida + ".part", salida)


# ------------------------------------------------------------ CBERS-4A WPM (INPE)
# El catalogo no informa nubes: se buscan las pasadas a +-N dias de cada fecha objetivo de cada zona
# (zonas_cbers.py), se dejan vistas rapidas (RGB a 32 m) de las mas cercanas y se elige a ojo.
# La eleccion va en CBERS4A\cbers_elegidas.csv (zona, fecha_objetivo, id); con --confirmar se bajan
# los recortes (pancromatica 2 m y multiespectral 8 m, nativos, alineados) con sus XML originales.
def _cbers_items(zona, f_obj, dias):
    import requests
    from zonas_cbers import ZONAS, COLECCION, STAC
    d = _dt.datetime.strptime(f_obj, "%Y%m%d")
    caja = list(ZONAS[zona]["caja"])
    cuerpo = {"collections": [COLECCION], "bbox": caja, "limit": 500,
              "datetime": "%sT00:00:00Z/%sT23:59:59Z" % ((d - _dt.timedelta(days=dias)).strftime("%Y-%m-%d"),
                                                       (d + _dt.timedelta(days=dias)).strftime("%Y-%m-%d"))}
    for intento in range(5):
        try:
            r = requests.post(STAC + "/search", json=cuerpo, timeout=120)
            r.raise_for_status()
            break
        except Exception as e:                       # noqa: BLE001
            print("   catalogo INPE: %s (reintento %d)" % (str(e)[:80], intento + 1))
            time.sleep(10 * (intento + 1))
    else:
        return []
    out = []
    for it in r.json().get("features", []):
        b = it.get("bbox") or [0, 0, 0, 0]
        cubre = b[0] <= caja[0] and b[1] <= caja[1] and b[2] >= caja[2] and b[3] >= caja[3]
        fecha = it["properties"]["datetime"][:10].replace("-", "")
        out.append(dict(id=it["id"], fecha=fecha, dias=(_dt.datetime.strptime(fecha, "%Y%m%d") - d).days,
                        cubre=cubre, assets={k: v["href"] for k, v in it["assets"].items()}))
    return sorted(out, key=lambda x: (not x["cubre"], abs(x["dias"]), x["id"]))


def _gdal_red():
    os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
    os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif,.TIF,.tiff,.vrt,.xml")
    os.environ.setdefault("GDAL_HTTP_MERGE_CONSECUTIVE_RANGES", "YES")
    os.environ.setdefault("GDAL_HTTP_MAX_RETRY", "5")
    os.environ.setdefault("GDAL_HTTP_RETRY_DELAY", "3")
    os.environ.setdefault("VSI_CACHE", "TRUE")


def _ventana(src, caja):
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds, Window
    c = transform_bounds("EPSG:4326", src.crs, *caja, densify_pts=21)
    w = from_bounds(*c, transform=src.transform).round_offsets().round_lengths()
    return w.intersection(Window(0, 0, src.width, src.height))


def _vista(it, zona, ruta_png):
    """RGB (bandas 3, 2, 1) del recorte a 32 m, estirado 2-98 %, para elegir a ojo."""
    import rasterio
    from zonas_cbers import ZONAS
    capas = []
    for b in ("BAND3", "BAND2", "BAND1"):
        with rasterio.open(it["assets"][b]) as src:
            w = _ventana(src, ZONAS[zona]["caja"])
            a = src.read(1, window=w, out_shape=(max(1, int(w.height) // 4), max(1, int(w.width) // 4))).astype("float32")
        capas.append(a)
    rgb = np.dstack(capas)
    ok = rgb.sum(2) > 0
    if ok.mean() < 0.5:
        return None, ok.mean()
    for k in range(3):
        lo, hi = np.percentile(rgb[..., k][ok], (2, 98))
        rgb[..., k] = np.clip((rgb[..., k] - lo) / max(hi - lo, 1), 0, 1)
    rgb[~ok] = 0
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.imsave(ruta_png, rgb)
    # brillo relativo del azul: las nubes lo suben (orientativo, la eleccion es a ojo)
    return float(np.percentile(capas[2][ok], 90)), float(ok.mean())


def cmd_cbers(a):
    import csv
    from zonas_cbers import ZONAS
    _gdal_red()
    base = os.path.join(ORIGINALES, "CBERS4A")
    os.makedirs(base, exist_ok=True)
    zonas = list(ZONAS) if a.zonas == ["todas"] else a.zonas
    if not a.confirmar:
        filas = []
        for z in zonas:
            for f_obj in sorted(ZONAS[z]["fechas"]):
                its = [x for x in _cbers_items(z, f_obj, a.dias) if x["cubre"]]
                print("\n%s, fecha objetivo %s (%s): %d pasadas WPM que cubren la zona a +-%d dias"
                      % (z, f_obj, ", ".join(ZONAS[z]["fechas"][f_obj]), len(its), a.dias))
                carpeta = os.path.join(base, "_vistas", "%s_%s" % (z, f_obj))
                os.makedirs(carpeta, exist_ok=True)
                vistos = set()
                for it in its:
                    if it["fecha"] in vistos or len(vistos) >= a.vistas:
                        continue
                    png = os.path.join(carpeta, "%+04d_%s_%s.png" % (it["dias"], it["fecha"], it["id"]))
                    try:
                        brillo, dato = _vista(it, z, png)
                    except Exception as e:                   # noqa: BLE001
                        print("   %s: no se pudo leer (%s)" % (it["id"], str(e)[:80]))
                        continue
                    if brillo is None:
                        print("   %s  %+d dias: la zona cae en el borde de la escena (%.0f %% con dato)"
                              % (it["id"], it["dias"], dato * 100))
                        continue
                    vistos.add(it["fecha"])
                    print("   %s  %+4d dias  azul p90 %6.0f  vista: %s" % (it["id"], it["dias"], brillo,
                                                                         os.path.basename(png)))
                    filas.append(dict(zona=z, fecha_objetivo=f_obj, id=it["id"], fecha=it["fecha"], dias=it["dias"],
                                      azul_p90=round(brillo), vista=os.path.relpath(png, base)))
        with open(os.path.join(base, "cbers_candidatas.csv"), "w", encoding="utf-8-sig", newline="") as fc:
            w = csv.DictWriter(fc, fieldnames=["zona", "fecha_objetivo", "id", "fecha", "dias", "azul_p90", "vista"])
            w.writeheader()
            w.writerows(filas)
        print("\nVistas en %s\\_vistas; lista en cbers_candidatas.csv. Elegir la despejada de cada zona y "
              "fecha en cbers_elegidas.csv y correr con --confirmar." % base)
        return
    eleg = os.path.join(base, "cbers_elegidas.csv")
    if not os.path.exists(eleg):
        sys.exit("Falta %s (zona, fecha_objetivo, id)" % eleg)
    import rasterio
    import requests
    with open(eleg, encoding="utf-8-sig") as fc:
        elegidas = [r for r in csv.DictReader(fc) if r.get("id") and (a.zonas == ["todas"] or r["zona"] in zonas)]
    filas_inv = []
    for n, r in enumerate(elegidas, 1):
        z = r["zona"]
        its = [x for x in _cbers_items(z, r["fecha_objetivo"], a.dias) if x["id"] == r["id"]]
        if not its:
            print("  %s %s: no se encontro %s en el catalogo" % (z, r["fecha_objetivo"], r["id"]))
            continue
        it = its[0]
        dest = os.path.join(base, z, "%s_%s" % (it["fecha"], it["id"]))
        if os.path.exists(os.path.join(dest, ".completo")):
            print("  [%d/%d] %s %s ya bajado" % (n, len(elegidas), z, it["id"]))
            continue
        os.makedirs(dest, exist_ok=True)
        errores = 0
        # ventana multiespectral y la pancromatica alineada (x4)
        with rasterio.open(it["assets"]["BAND1"]) as ms:
            wm = _ventana(ms, ZONAS[z]["caja"])
            tr_ms = ms.window_transform(wm)
        for b in ("BAND0", "BAND1", "BAND2", "BAND3", "BAND4"):
            href = it["assets"][b]
            salida = os.path.join(dest, os.path.basename(href.split("?")[0]))
            if not os.path.exists(salida):
                try:
                    with rasterio.open(href) as src:
                        if b == "BAND0":
                            from rasterio.windows import from_bounds
                            x0, y0 = tr_ms.c, tr_ms.f
                            x1 = x0 + wm.width * tr_ms.a
                            y1 = y0 + wm.height * tr_ms.e
                            w = from_bounds(x0, y1, x1, y0, transform=src.transform).round_offsets().round_lengths()
                        else:
                            w = wm
                        arr = src.read(1, window=w)
                        p = src.profile.copy()
                        p.update(driver="GTiff", width=arr.shape[1], height=arr.shape[0],
                                 transform=src.window_transform(w), compress="deflate", tiled=True,
                                 blockxsize=256, blockysize=256, predictor=2)
                        with rasterio.open(salida + ".part", "w", **p) as dst:
                            dst.write(arr, 1)
                            dst.update_tags(**src.tags())
                            dst.update_tags(FUENTE="INPE, CBERS-4A WPM L4, item %s" % it["id"], ZONA=z,
                                            PROCESO="Recorte de la zona %s en la proyeccion y pixel NATIVOS" % z)
                    os.replace(salida + ".part", salida)
                except Exception as e:                       # noqa: BLE001
                    errores += 1
                    print("   %s %s: %s" % (it["id"], b, str(e)[-120:]))
            x = it["assets"].get(b + "_xml")
            if x:
                try:
                    rx = requests.get(x, timeout=120)
                    rx.raise_for_status()
                    with open(os.path.join(dest, os.path.basename(x.split("?")[0])), "wb") as fx:
                        fx.write(rx.content)
                except Exception as e:                       # noqa: BLE001
                    errores += 1
                    print("   %s %s_xml: %s" % (it["id"], b, str(e)[:80]))
        with open(os.path.join(dest, "item_STAC.json"), "w", encoding="utf-8") as fj:
            import json
            json.dump(dict(id=it["id"], fecha=it["fecha"], assets=it["assets"], zona=z,
                           fecha_objetivo=r["fecha_objetivo"]), fj, ensure_ascii=False, indent=1)
        if not errores:
            open(os.path.join(dest, ".completo"), "w").close()
        filas_inv.append({"tipo": "cbers4a", "sensor": "CBERS-4A WPM L4", "origen": it["id"], "destino": dest,
                          "bytes": peso(dest), "verificado": errores == 0, "cuando": ahora(),
                          "fuente": "INPE, catalogo STAC CB4A-WPM-L4-DN-1", "sitios": z})
        print("  [%d/%d] %s %s %s%s" % (n, len(elegidas), z, it["fecha"], it["id"], "" if not errores else "  (REVISAR)"))
    anotar(filas_inv)


# ------------------------------------------------------------ AlphaEarth Foundations (embeddings anuales)
# Copia publica en Source Cooperative (Taylor Geospatial) del Satellite Embedding de Google: COG de
# 8192 x 8192 px, 64 bandas int8 (A00..A63), en la UTM de cada zona, por anio. Los .tiff estan guardados
# de abajo hacia arriba: se leen por su .vrt, como indica el proveedor. Valor -128 = sin dato.
# Descuantizacion: valor = signo(DN) * (DN / 127,5)^2
AEF_URL = "https://data.source.coop/tge-labs/aef/v1/annual"
AEF_CITA = ("The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind. "
            "CC BY 4.0. Copia en Source Cooperative (Taylor Geospatial): https://source.coop/tge-labs/aef")
# sitio: anios (los de las fechas del curso; 2026 todavia no existe y se usa 2025, el ultimo)
AEF_ANIOS = {
    "A1_DELTA_QUEMAS": [2020],
    "A2_IBICUY": [2025],
    "B_CONCORDIA": [2023, 2025],
    "C_FEDERAL": [2021, 2025],
    "E1_DIAMANTE_BARRANCA": [2018, 2025],
    "E_PARANA_DIAMANTE": [2025],
    "F_BOVRIL": [2023],
}


def _aef_indice(sitios, anios):
    """Archivos del indice que tocan los sitios (se guarda filtrado; el indice completo pesa 800 MB)."""
    import requests
    cache = os.path.join(ORIGINALES, "EMBEDDINGS", "indice_sitios.csv")
    if os.path.exists(cache):
        d = pd.read_csv(cache, dtype=str)
        if set(sitios) <= set(d.sitio) and {str(x) for x in anios} <= set(d.year):
            return d
    print("  Leyendo el indice de Source Cooperative (unos 800 MB, se filtra al vuelo)...")
    filas, cab = [], None
    with requests.get(AEF_URL + "/aef_index.csv", stream=True, timeout=600) as r:
        r.raise_for_status()
        for linea in r.iter_lines(decode_unicode=True):
            if cab is None:
                cab = linea
                continue
            if "20S" not in linea and "21S" not in linea:
                continue
            resto = linea[linea.rfind('"') + 2:].split(",")
            crs, path, year, zona = resto[:4]
            if zona not in ("20S", "21S") or int(year) not in anios:
                continue
            w, s_, e, n = (float(x) for x in resto[8:12])
            for st in sitios:
                o, ss, ee, nn = SITIOS[st]["bbox"]
                if w < ee and e > o and s_ < nn and n > ss:
                    filas.append(dict(sitio=st, year=year, utm_zone=zona, crs=crs, path=path))
    d = pd.DataFrame(filas)
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    d.to_csv(cache, index=False)
    return d.astype(str)


def cmd_embeddings(a):
    import rasterio
    from rasterio.transform import from_origin
    from rasterio.warp import transform_bounds
    _gdal_red()
    sitios = [s for s in (list(AEF_ANIOS) if a.sitios == ["todos"] else a.sitios) if s in AEF_ANIOS]
    anios = sorted({y for s in sitios for y in AEF_ANIOS[s]})
    idx = _aef_indice(sitios, anios)
    plan = []
    for s in sitios:
        o, s_, e, n = SITIOS[s]["bbox"]
        huso = int(((o + e) / 2 + 180) // 6) + 1
        zona = "%dS" % huso
        for y in AEF_ANIOS[s]:
            sel = idx[(idx.sitio == s) & (idx.year == str(y)) & (idx.utm_zone == zona)]
            plan.append((s, y, zona, list(sel.path)))
            print("  %-22s %d  zona %s  %d archivos" % (s, y, zona, len(sel)))
    if not a.confirmar:
        print("\nNo se bajo nada. Vuelva a correr con --confirmar.")
        return
    filas = []
    for s, y, zona, paths in plan:
        dest = os.path.join(ORIGINALES, "EMBEDDINGS", s)
        os.makedirs(dest, exist_ok=True)
        salida = os.path.join(dest, "AEF_%s_%d.tif" % (s, y))
        if os.path.exists(salida):
            print("  %s ya esta" % os.path.basename(salida))
            continue
        if not paths:
            print("  %s %d: sin archivos en el indice" % (s, y))
            continue
        epsg = 32700 + int(zona[:-1])
        # los .tiff estan guardados de abajo hacia arriba (transformacion con alto de pixel positivo); sus
        # .vrt apuntan a /vsis3/ (requiere credenciales de AWS), asi que se lee el .tiff por https con
        # ventanas de pixeles y se da vuelta.
        urls = ["/vsicurl/" + p.replace("s3://us-west-2.opendata.source.coop", "https://data.source.coop")
                for p in paths]
        urls = [u[:-4] + ".tiff" if u.endswith(".vrt") else u for u in urls]
        x0, y0, x1, y1 = transform_bounds("EPSG:4326", "EPSG:%d" % epsg, *SITIOS[s]["bbox"], densify_pts=21)
        with rasterio.open(urls[0]) as src:          # grilla de salida alineada con la de los archivos
            t0 = src.transform
            if abs(abs(t0.a) - 10) > 1e-6 or abs(abs(t0.e) - 10) > 1e-6:
                raise SystemExit("Pixel inesperado en %s: %s" % (urls[0], t0))
        x0 = t0.c + np.floor((x0 - t0.c) / 10) * 10
        y1 = t0.f + np.ceil((y1 - t0.f) / 10) * 10
        ancho, alto = int(np.ceil((x1 - x0) / 10)), int(np.ceil((y1 - y0) / 10))
        tr = from_origin(x0, y1, 10, 10)
        out = np.full((64, alto, ancho), -128, "int8")
        tags = {}
        from rasterio.windows import Window
        for url in urls:
            with rasterio.open(url) as src:
                t = src.transform
                c0 = int(round((x0 - t.c) / 10))
                ca, cb = max(c0, 0), min(c0 + ancho, src.width)
                if t.e < 0:                          # de arriba hacia abajo (normal)
                    f0 = int(round((t.f - y1) / 10))
                    fa, fb = max(f0, 0), min(f0 + alto, src.height)
                    if ca >= cb or fa >= fb:
                        continue
                    bloque = src.read(window=Window(ca, fa, cb - ca, fb - fa)).astype("int8")
                    dest_f = fa - f0
                else:                                # de abajo hacia arriba: fila 0 = la del sur
                    r_sup = int(round((y1 - t.f) / 10)) - 1          # fila del archivo de la 1.a fila de salida
                    r_inf = r_sup - alto + 1
                    ra, rb = max(r_inf, 0), min(r_sup, src.height - 1)
                    if ca >= cb or ra > rb:
                        continue
                    bloque = src.read(window=Window(ca, ra, cb - ca, rb - ra + 1)).astype("int8")[:, ::-1, :]
                    dest_f = r_sup - rb
                tags = src.tags()
                dest_c = ca - c0
                sub = out[:, dest_f:dest_f + bloque.shape[1], dest_c:dest_c + bloque.shape[2]]
                m = (sub[0] == -128) & (bloque[0] != -128)
                sub[:, m] = bloque[:, m]
        if (out[0] != -128).mean() < 0.5:
            print("  %s %d: sólo %.0f %% con dato (revisar)" % (s, y, (out[0] != -128).mean() * 100))
        perfil = dict(driver="GTiff", width=ancho, height=alto, count=64, dtype="int8", nodata=-128,
                      crs="EPSG:%d" % epsg, transform=tr, compress="deflate", tiled=True, blockxsize=256,
                      blockysize=256, interleave="pixel", BIGTIFF="IF_SAFER")
        with rasterio.open(salida + ".part", "w", **perfil) as dst:
            dst.write(out)
            for k in range(64):
                dst.set_band_description(k + 1, "A%02d" % k)
            dst.update_tags(**tags)
            dst.update_tags(FUENTE=AEF_CITA, ANIO=str(y), SITIO=s,
                            DESCUANTIZAR="valor = signo(DN) * (DN / 127.5)**2 ; DN -128 = sin dato",
                            ARCHIVOS_ORIGEN=" ".join(os.path.basename(p) for p in paths),
                            PROCESO="Mosaico y recorte del sitio en la UTM %s, pixel de 10 m nativo" % zona)
        os.replace(salida + ".part", salida)
        filas.append({"tipo": "embeddings", "sensor": "AlphaEarth Foundations (anual)", "origen": " ".join(paths),
                      "destino": salida, "bytes": peso(salida), "verificado": True, "cuando": ahora(),
                      "fuente": AEF_CITA, "sitios": s})
        print("  %s %d: %d x %d px, %.0f %% con dato -> %s" % (s, y, ancho, alto, (out[0] != -128).mean() * 100,
                                                            os.path.basename(salida)))
    anotar(filas)


# ------------------------------------------------------------ Sentinel-1 sin procesar (ASF)
# Productos de nivel 1 TAL COMO LOS ENTREGA ESA (.zip con la carpeta .SAFE), para
# procesarlos en clase en SNAP (orbita, ruido termico, calibracion, speckle,
# correccion del terreno) y comparar con el RTC ya corregido del Planetary Computer.
# Una pasada por sitio, la del mejor par optico-radar del Tp1.
S1_CRUDOS = {
    "B_CONCORDIA": ["S1A_IW_GRDH_1SDV_20231104T091449_20231104T091514_051065_06285B_E987"],   # pico de la crecida; S2 el mismo dia
    "F_BOVRIL": ["S1A_IW_GRDH_1SDV_20230917T091449_20230917T091514_050365_061067_C33B"],      # 3 dias despues de la NovaSAR 47974
    "C_FEDERAL": ["S1C_IW_GRDH_1SDV_20260914T091317_20260914T091342_009441_012C7A_AB47"],     # S2 el mismo dia; 3 dias antes de NISAR y BIOMASS
    # La franja D necesita DOS cuadros consecutivos de la misma pasada: ejercicio de
    # union de cuadros (Slice Assembly) en SNAP antes de calibrar.
    "D_LAPAZ_VILLAGUAY": ["S1C_IW_GRDH_1SDV_20260914T091317_20260914T091342_009441_012C7A_AB47",
                          "S1C_IW_GRDH_1SDV_20260914T091342_20260914T091407_009441_012C7A_4769"],
    "A1_DELTA_QUEMAS": ["S1A_IW_GRDH_1SDV_20200908T091510_20200908T091535_034265_03FB78_6C2A"],  # quemas; S2 el mismo dia
    # Tp2 (paso 1 en SNAP): misma escena que el RTC del Planetary Computer del 26/09/2026 (orbita 68,
    # descendente; el GRD cubre Ibicuy entero), 4 dias antes de los NISAR L y S del 30/09/2026.
    # Nombre real encontrado en ASF el 21/10/2026 (cubre el 100 % de Ibicuy). Si un nombre no esta en ASF,
    # cmd_s1_crudo busca el GRDH de esa pasada (mision, toma, hora) que mas cubre el sitio.
    "A2_IBICUY": ["S1C_IW_GRDH_1SDV_20260926T091407_20260926T091432_009616_013235_EE65"],
}


def _resolver_por_pasada(asf, nombre, sitios):
    """Escena GRDH real a partir de un nombre con el identificador final desconocido (o mal escrito):
    misma mision, toma y orbita absoluta, hora +/- 1 min, la que mas cubre el sitio."""
    import datetime as dt
    from shapely.geometry import box, shape
    mision = {"S1A": "SA", "S1B": "SB", "S1C": "SC", "S1D": "SD"}.get(nombre[:3])
    t0 = dt.datetime.strptime(nombre[17:32], "%Y%m%dT%H%M%S")
    t1 = dt.datetime.strptime(nombre[33:48], "%Y%m%dT%H%M%S")
    clave = nombre[:-5]                                   # todo menos _XXXX
    toma = clave.split("_")[-1]                           # identificador de la toma (datatake)
    mejor = None
    for s in sitios:
        caja = box(*SITIOS[s]["bbox"])
        res = asf.search(platform="SENTINEL-1", processingLevel="GRD_HD", beamMode="IW",
                         intersectsWith=caja.wkt, start=(t0 - dt.timedelta(minutes=1)).isoformat() + "Z",
                         end=(t1 + dt.timedelta(minutes=1)).isoformat() + "Z")
        for r in res:
            n = r.properties["sceneName"]
            if not n.startswith(nombre[:3]) or toma not in n:
                continue
            cub = shape(r.geometry).intersection(caja).area / caja.area
            exacto = n.startswith(clave)
            if mejor is None or (exacto, cub) > (mejor[0], mejor[1]):
                mejor = (exacto, cub, r)
    if mejor is None:
        return None
    print("  %s -> %s (%s; cubre %.0f %% del sitio)" % (nombre, mejor[2].properties["sceneName"],
          "mismo cuadro" if mejor[0] else "OTRO cuadro de la misma pasada", 100 * mejor[1]))
    return mejor[2]



def _zip_sano(ruta):
    import zipfile
    try:
        with zipfile.ZipFile(ruta) as z:
            return any(n.endswith("manifest.safe") for n in z.namelist())
    except Exception:                                # noqa: BLE001
        return False


def _s1_crudo_directo(a, nombres):
    d = os.path.join(ORIGINALES, "S1_CRUDO")
    os.makedirs(d, exist_ok=True)
    for n in sorted(nombres):
        print("  %s  sitios: %s" % (n, ", ".join(nombres[n])))
    print("Libre: %s" % tam(libre(ORIGINALES)))
    if not a.confirmar:
        print("No se bajo nada. Repetir con --confirmar.")
        return
    from Tp1_04_buscar_asf import sesion_asf
    ses = sesion_asf(print)
    filas = []
    for n in sorted(nombres):
        url = "https://datapool.asf.alaska.edu/GRD_HD/S%s/%s.zip" % (n[2], n)
        final = os.path.join(d, n + ".zip")
        if os.path.exists(final) and _zip_sano(final):
            print("Ya esta: %s" % os.path.basename(final))
            continue
        print("Bajando %s ..." % os.path.basename(final))
        ok = False
        for intento in range(1, 4):
            try:
                with ses.get(url, stream=True, timeout=120) as r:
                    r.raise_for_status()
                    largo = int(r.headers.get("Content-Length", 0))
                    with open(final + ".part", "wb") as f:
                        for trozo in r.iter_content(8 * 2 ** 20):
                            f.write(trozo)
                if (not largo or os.path.getsize(final + ".part") == largo) and _zip_sano(final + ".part"):
                    os.replace(final + ".part", final)
                    ok = True
                    break
                print("   descarga incompleta; reintento %d/3" % intento)
            except Exception as e:                   # noqa: BLE001
                print("   interrupcion (%s); reintento %d/3" % (str(e)[:80], intento))
                time.sleep(20 * intento)
        print("   %s" % ("ok (%s)" % tam(os.path.getsize(final)) if ok else "NO SE PUDO BAJAR"))
        filas.append({"tipo": "s1_crudo", "sensor": "Sentinel-1 IW GRDH (nivel 1, sin procesar)",
                      "origen": url, "destino": final, "bytes": os.path.getsize(final) if os.path.exists(final) else 0,
                      "verificado": ok, "cuando": ahora(), "sitios": " ".join(nombres[n]),
                      "fuente": "ESA Copernicus Sentinel-1, distribuido por ASF DAAC: https://search.asf.alaska.edu"})
    anotar(filas)


def cmd_s1_crudo(a):
    import asf_search as asf
    try:                                              # CMR a veces tarda mas de 30 s
        asf.constants.INTERNAL.CMR_TIMEOUT = 120
    except AttributeError:
        pass

    sys.path.insert(0, os.path.join(PRACTICA, "Tp1_Convergencia", "03_Scripts"))
    nombres = {}
    for s in sitios_de(a.sitios):
        for n in S1_CRUDOS.get(s, []):
            nombres.setdefault(n, []).append(s)
    if not nombres:
        sys.exit("Ninguno de esos sitios tiene una pasada Sentinel-1 elegida en S1_CRUDOS.")
    # El catalogo CMR de la NASA a veces responde "500 Internal Server Error". Se reintenta y, si
    # sigue caido, se baja DIRECTO de ASF: con el nombre exacto la direccion es fija
    # (https://datapool.asf.alaska.edu/GRD_HD/S<A|B|C|D>/<nombre>.zip); el tamano se verifica abriendo el .zip.
    res = None
    for intento in range(1, 4):
        try:
            res = asf.granule_search(list(nombres))
            break
        except Exception as e:                       # noqa: BLE001
            print("  Catalogo CMR no responde (%s), intento %d de 3" % (type(e).__name__, intento))
            if intento < 3:
                time.sleep(30 * intento)
    if res is None:
        print("  Se baja directo de ASF por el nombre de cada escena (sin catalogo).")
        _s1_crudo_directo(a, nombres)
        return
    res = [r for r in res if r.properties.get("processingLevel") == "GRD_HD"]
    total = 0
    for r in res:
        mb = _bytes_asf(r.properties) / 1e6
        total += mb
        print("  %s  %6.0f MB  sitios: %s" % (r.properties["sceneName"], mb,
                                            ", ".join(nombres.get(r.properties["sceneName"], []))))
    faltan = set(nombres) - {r.properties["sceneName"] for r in res}
    for n in sorted(faltan):
        print("  NO ESTA EN ASF con ese nombre: %s; se busca la escena de esa pasada sobre el sitio" % n)
        try:
            r = _resolver_por_pasada(asf, n, nombres[n])
        except Exception as e:                       # noqa: BLE001
            print("    la busqueda por pasada fallo (%s)" % str(e)[:80])
            r = None
        if r is None:
            print("  NO ESTA EN ASF: %s" % n)
            continue
        nombres.setdefault(r.properties["sceneName"], nombres[n])
        res.append(r)
        mb = _bytes_asf(r.properties) / 1e6
        total += mb
        print("    nombre real para S1_CRUDOS y procesar_s1_crudo.py: %s (%.0f MB)" % (r.properties["sceneName"], mb))
    print("Total: %.1f GB. Libre: %s" % (total / 1e3, tam(libre(ORIGINALES))))
    if not a.confirmar:
        print("No se bajo nada. Repetir con --confirmar.")
        return
    from Tp1_04_buscar_asf import sesion_asf
    ses = sesion_asf(print)
    d = os.path.join(ORIGINALES, "S1_CRUDO")
    os.makedirs(d, exist_ok=True)
    filas = []
    for r in res:
        url = r.properties.get("url", "")
        final = os.path.join(d, os.path.basename(url))
        esperado = _bytes_asf(r.properties)
        if os.path.exists(final) and (not esperado or os.path.getsize(final) == esperado):
            print("Ya esta: %s" % os.path.basename(final))
            continue
        print("Bajando %s ..." % os.path.basename(final))
        for intento in range(3):
            try:
                r.download(path=d, session=ses)
                break
            except Exception as e:                   # noqa: BLE001
                print("   interrupcion (%s); reintento %d/3" % (str(e)[:80], intento + 1))
        ok = os.path.exists(final) and (not esperado or os.path.getsize(final) == esperado)
        print("   %s" % ("ok" if ok else "REVISAR: el tamano no coincide"))
        filas.append({"tipo": "s1_crudo", "sensor": "Sentinel-1 IW GRDH (nivel 1, sin procesar)",
                      "origen": url, "destino": final, "bytes": os.path.getsize(final) if os.path.exists(final) else 0,
                      "verificado": ok, "cuando": ahora(),
                      "sitios": " ".join(nombres.get(r.properties["sceneName"], [])),
                      "fuente": "ESA Copernicus Sentinel-1, distribuido por ASF DAAC: https://search.asf.alaska.edu"})
    anotar(filas)


# ------------------------------------------------------------ principal
def main():
    ap = argparse.ArgumentParser(description="Datos crudos del curso en 00_COMUN\\08_Originales_crudos")
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("estado")
    p = sp.add_parser("copiar_locales")
    p.add_argument("--sitios", nargs="*", default=["todos"])
    p.add_argument("--sensores", nargs="*", default=[])
    p.add_argument("--incluir_nisar", action="store_true", help="Copia tambien NISAR del Delta si esta en otro disco (pesa mucho; normalmente se baja con el subcomando nisar)")
    p.add_argument("--cosmo_completo", action="store_true",
                   help="copiar la carpeta COSMO-SkyMed de Diamante entera (grietas, MDE IGN, InSAR)")
    p.add_argument("--confirmar", action="store_true")
    for nombre, prods, defecto in (("icesat2", list(ICESAT2), ["ATL08", "ATL13"]), ("gedi", list(GEDI), ["L2A", "L2B", "L4A"])):
        p = sp.add_parser(nombre)
        p.add_argument("--sitios", nargs="*", default=["todos"])
        p.add_argument("--productos", nargs="*", default=defecto, choices=prods)
        p.add_argument("--desde", default="")
        p.add_argument("--hasta", default="")
        p.add_argument("--confirmar", action="store_true")
        if nombre == "gedi":
            p.add_argument("--granulo_completo", action="store_true",
                           help="bajar el granulo entero (~1,2 GB el L2A) en lugar del recorte del sitio")
            p.add_argument("--hilos", type=int, default=4, help="granulos que se leen a la vez")
            p.add_argument("--bloque_mb", type=int, default=16, help="MB que se traen por cada lectura por la red")
            p.add_argument("--harmony", action="store_true",
                           help="que NASA haga el recorte en sus servidores (Harmony) y bajar solo el recorte")
            p.add_argument("--tanda", type=int, default=50, help="granulos por pedido a Harmony")
    p = sp.add_parser("nisar")
    p.add_argument("--sitios", nargs="*", default=["DELTA_NISAR"])
    p.add_argument("--desde", default="2026-07-01")
    p.add_argument("--hasta", default="2026-10-15")
    p.add_argument("--cobertura_min", type=float, default=20.0)
    p.add_argument("--fechas", nargs="*", default=[], help="Fechas a bajar, AAAA-MM-DD")
    p.add_argument("--tracks", nargs="*", default=[], help="Trazas (track) a bajar")
    p.add_argument("--confirmar", action="store_true")
    p = sp.add_parser("biomass")
    p.add_argument("--sitios", nargs="*", default=["todos"])
    p.add_argument("--desde", default="")
    p.add_argument("--hasta", default="")
    p.add_argument("--colecciones", nargs="*", default=["BiomassLevel1b", "BiomassLevel2a", "BiomassLevel2b"])
    p.add_argument("--max", type=int, default=0, help="Bajar solo los N primeros productos (prueba)")
    p.add_argument("--ficha", default="", help="Archivo (o carpeta) con la ficha de ESA MAAP")
    p.add_argument("--confirmar", action="store_true")
    for nombre in ("cci", "cci_resumen"):
        p = sp.add_parser(nombre)
        p.add_argument("--sitios", nargs="*", default=["todos"])
        p.add_argument("--version", default="v7.0")
        p.add_argument("--anios", nargs="*", default=["2010", "2015", "2020", "2021", "2024"])
    p = sp.add_parser("s1_crudo")
    p.add_argument("--sitios", nargs="*", default=["todos"])
    p.add_argument("--confirmar", action="store_true")
    p = sp.add_parser("embeddings")
    p.add_argument("--sitios", nargs="*", default=["todos"])
    p.add_argument("--confirmar", action="store_true")
    p = sp.add_parser("cbers")
    p.add_argument("--zonas", nargs="*", default=["todas"])
    p.add_argument("--dias", type=int, default=60, help="Busca a +- estos dias de cada fecha objetivo")
    p.add_argument("--vistas", type=int, default=8, help="Vistas rapidas por zona y fecha (las mas cercanas)")
    p.add_argument("--confirmar", action="store_true")
    p = sp.add_parser("landsat")
    p.add_argument("--sitios", nargs="*", default=["todos"])
    p.add_argument("--dias", type=int, default=16, help="Busca a +- estos dias de cada fecha Sentinel-2")
    p.add_argument("--despejado_min", type=float, default=80.0, help="%% minimo del sitio sin nubes ni sombras")
    p.add_argument("--cobertura_min", type=float, default=90.0, help="%% minimo del sitio con dato")
    p.add_argument("--confirmar", action="store_true")
    p = sp.add_parser("planetary")
    p.add_argument("--sitios", nargs="*", default=["todos"])
    p.add_argument("--colecciones", nargs="*", default=["sentinel-2-l2a", "sentinel-1-rtc", "cop-dem-glo-30", "jrc-gsw"])
    p.add_argument("--desde", default="")
    p.add_argument("--hasta", default="")
    p.add_argument("--nubes_max", type=float, default=30)
    p.add_argument("--desde_tp1", action="store_true",
                   help="Bajar solo las escenas que el Tp1 (paso 3) dejo como candidatas, mas el MDE y el agua")
    p.add_argument("--confirmar", action="store_true")
    a = ap.parse_args()
    os.makedirs(ORIGINALES, exist_ok=True)
    print("Datos crudos: %s" % ORIGINALES)
    {"estado": cmd_estado, "copiar_locales": cmd_copiar_locales, "icesat2": cmd_icesat2, "gedi": cmd_gedi,
     "biomass": cmd_biomass, "nisar": cmd_nisar, "cci": cmd_cci, "cci_resumen": cmd_cci_resumen,
     "planetary": cmd_planetary, "s1_crudo": cmd_s1_crudo, "landsat": cmd_landsat, "cbers": cmd_cbers, "embeddings": cmd_embeddings}[a.cmd](a)


if __name__ == "__main__":
    main()
