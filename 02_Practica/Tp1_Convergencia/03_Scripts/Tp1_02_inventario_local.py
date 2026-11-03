# -*- coding: utf-8 -*-
"""
Tp1_02_inventario_local.py   [SE CORRE]   paso 2 del Tp1
========================================================
Inventario VERIFICADO de las escenas que el curso ya tiene en disco:

  NovaSAR-1, banda S, 6 m, HH   -> carpeta NOVASAR de configuracion_comun.py
  NISAR GCOV, banda L (NASA)    -> NISAR_DELTA\\BANDA_L_NASA
  NISAR GCOV, banda S (ISRO)    -> NISAR_DELTA\\BANDA_S_ISRO
  NISAR GCOV de Concordia y Federal (banda L) -> 08_Originales_crudos\\NISAR

Para cada escena y cada sitio informa DOS cifras, una al lado de la otra:

  cobertura_huella_%    cuanto del sitio toca el poligono que declara el
                        producto (lo que diria un catalogo);
  pixeles_validos_%     cuantos pixeles del sitio traen dato REAL, contados
                        uno por uno (a 100 m para que sea rapido).

La diferencia entre las dos es el centro del Tp1: la huella es todo lo que
TOCA el rectangulo; el dato es lo que lo CUBRE. En NISAR, ademas, el borde de
la franja trae muestras invalidas que la mascara del producto marca con 0.

Las fechas salen de los METADATOS de cada producto (RawDataStartTime en
NovaSAR, zeroDopplerStartTime en NISAR), nunca de la fecha del archivo.

SALIDA
  Tp1_Convergencia/05_Resultados/04_Tablas/inventario_local.csv
  Tp1_Convergencia/05_Resultados/06_Control_calidad/Tp1_02_inventario_local.log

USO (Miniforge Prompt, entorno sar):
    python Tp1_02_inventario_local.py
    python Tp1_02_inventario_local.py --sitios B_CONCORDIA F_BOVRIL
"""
import argparse
import glob
import os
import re
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402
from shapely import wkt                                               # noqa: E402
from shapely.geometry import MultiPoint, box                          # noqa: E402

from configuracion_comun import (SITIOS, NOVASAR, NOVASAR_ESCENAS,     # noqa: E402
                                 NISAR_DELTA, ORIGINALES, ruta_tp)
from funciones_comunes import (grilla_sitio, novasar_sigma0,          # noqa: E402
                               novasar_carpeta_grd, nisar_gcov_en_grilla,
                               Bitacora)

PIXEL_CONTEO = 100.0   # m: conteo rapido de pixeles validos


def huella_novasar(carpeta_grd):
    """Poligono (WGS 84) de las cuatro esquinas que trae el GRD como GCP."""
    import rasterio

    with rasterio.open(os.path.join(carpeta_grd, "image_HH.tif")) as src:
        gcps, _ = src.gcps
    return MultiPoint([(g.x, g.y) for g in gcps]).convex_hull


def metadato_novasar(carpeta_grd, etiqueta):
    with open(os.path.join(carpeta_grd, "metadata.xml"), encoding="utf-8", errors="ignore") as f:
        m = re.search(r"<%s>([^<]+)<" % etiqueta, f.read())
    return m.group(1).strip() if m else ""


def info_nisar(ruta_h5):
    import h5py

    banda = "SSAR" if os.path.basename(ruta_h5).startswith("NISAR_S") else "LSAR"
    with h5py.File(ruta_h5, "r") as h:
        idn = h["science/%s/identification" % banda]
        dec = lambda k: (idn[k][()].decode() if isinstance(idn[k][()], bytes) else str(idn[k][()]))
        pol = wkt.loads(dec("boundingPolygon"))
        t0 = dec("zeroDopplerStartTime")
        terms = h["science/%s/GCOV/grids/frequencyA/listOfCovarianceTerms" % banda][()]
        terms = [t.decode() if isinstance(t, bytes) else str(t) for t in terms]
        dx = float(np.diff(h["science/%s/GCOV/grids/frequencyA/xCoordinates" % banda][:2])[0])
        return {"banda": banda, "huella": pol, "fecha": t0[:10], "hora": t0[11:16],
                "pasada": dec("orbitPassDirection"), "track": dec("trackNumber"),
                "frame": dec("frameNumber"), "terminos": "+".join(terms),
                "pixel_m": abs(dx), "version": dec("productVersion")}


PATRONES = [
    # (expresion sobre el nombre, sensor, banda, lambda_cm)
    (r"(S1[AB])_IW_(SLC|GRDH)_+1S(DV|SV)_(\d{8})T(\d{4})", "Sentinel-1", "C", 5.6),
    (r"CSKS(\d)_(SCS|GEC|DGM)_B_(HI|S2|PP)_\w{2}_(HH|VV|HV|VH|CO)_\w{2}_\w{2}_(\d{8})(\d{4})", "COSMO-SkyMed", "X", 3.1),
]


def huella_archivo(ruta):
    """Huella declarada (WGS 84) de un producto del archivo, o None.

    Sentinel-1: manifest.safe (dentro del .zip o de la carpeta .SAFE).
    COSMO-SkyMed y SAOCOM: el .kml que acompana al producto.
    """
    import zipfile
    from shapely.geometry import Polygon

    texto = None
    try:
        if ruta.endswith(".zip") and os.path.basename(ruta).startswith("S1"):
            with zipfile.ZipFile(ruta) as z:
                man = [n for n in z.namelist() if n.endswith("manifest.safe")]
                if man:
                    texto = z.read(man[0]).decode("utf-8", "ignore")
            m = re.search(r"<gml:coordinates>([^<]+)</gml:coordinates>", texto or "")
            if m:
                pares = [tuple(map(float, p.split(","))) for p in m.group(1).split()]
                return Polygon([(lon, lat) for lat, lon in pares])
        if ruta.endswith(".SAFE"):
            with open(os.path.join(ruta, "manifest.safe"), encoding="utf-8", errors="ignore") as f:
                m = re.search(r"<gml:coordinates>([^<]+)</gml:coordinates>", f.read())
            if m:
                pares = [tuple(map(float, p.split(","))) for p in m.group(1).split()]
                return Polygon([(lon, lat) for lat, lon in pares])
        carpeta = ruta if os.path.isdir(ruta) else os.path.dirname(ruta)
        kmls = []
        for sub in ("", "Images"):            # SAOCOM guarda su .kml en Images/
            c = os.path.join(carpeta, sub)
            if os.path.isdir(c):
                kmls += [os.path.join(c, k) for k in os.listdir(c) if k.lower().endswith(".kml")]
        if ruta.endswith(".h5"):
            propio = ruta[:-3] + ".kml"
            kmls = [propio] + kmls if os.path.exists(propio) else kmls
        for k in kmls:
            with open(k, encoding="utf-8", errors="ignore") as f:
                for bloque in re.findall(r"<coordinates>([^<]+)</coordinates>", f.read()):
                    fichas = bloque.split()
                    if len(fichas) >= 3:          # "lon,lat[,z] lon,lat[,z] ..."
                        pts = [tuple(map(float, p.split(",")[:2])) for p in fichas]
                    else:                         # COSMO: "lon,lat,z,lon,lat,z,..." sin espacios
                        v = [float(x) for x in bloque.replace(" ", "").split(",") if x]
                        pts = [(v[i], v[i + 1]) for i in range(0, len(v) - 2, 3)]
                    if len(pts) >= 3:
                        return Polygon(pts)
    except Exception:                                # noqa: BLE001
        return None
    return None


def asignar_sitios(fila, huella):
    """Una fila por sitio que la huella toca (o una sola, sin sitio)."""
    if huella is None or not huella.is_valid:
        return [dict(fila, sitio="", **{"cobertura_huella_%": ""})]
    salida = []
    for s, d in SITIOS.items():
        caja = box(*d["bbox"])
        cob = 100.0 * huella.intersection(caja).area / caja.area
        if cob > 0:
            salida.append(dict(fila, sitio=s, **{"cobertura_huella_%": round(cob, 1)}))
    return salida or [dict(fila, sitio="ninguno", **{"cobertura_huella_%": 0.0})]


def escanear_archivos(log):
    """Lista los productos del archivo 2023 y de COSMO 2018 por sus METADATOS de nombre.

    Aqui no se cuentan pixeles: son productos en geometria de radar (SLC,
    L1A) que recien tienen coordenadas despues de procesarlos en SNAP (Tp2).
    Se informa fecha, modo y polarizacion, y la huella declarada (KML) cuando
    el producto la trae.
    """
    from configuracion_comun import ORIGINALES_2023, COSMO_DIAMANTE

    filas, vistos = [], set()
    for raiz in (ORIGINALES_2023, COSMO_DIAMANTE):
        log.titulo("Archivo de escenas en %s" % raiz)
        if not os.path.isdir(raiz):
            log("NO EXISTE en este equipo. Se omite y se deja constancia.")
            continue
        for carpeta, subdirs, archivos in os.walk(raiz):
            if ".data" in carpeta or ".SAFE" in carpeta:
                subdirs[:] = []
                continue
            for nombre in subdirs + archivos:
                for patron, sensor, banda, lam in PATRONES:
                    m = re.search(patron, nombre)
                    if not m or not (nombre.endswith((".zip", ".h5")) or nombre.endswith(".SAFE")):
                        continue
                    if sensor == "Sentinel-1":
                        f = m.group(4)
                        hhmm = m.group(5)
                        clave = (sensor, m.group(2), f, m.group(5))
                        modo = "IW %s %s" % (m.group(2), "VV+VH" if m.group(3) == "DV" else "VV")
                        pols = "VV+VH" if m.group(3) == "DV" else "VV"
                        # el nombre no trae la pasada; Sentinel-1 es heliosincronico (06 y 18 h locales):
                        # sobre Entre Rios la pasada de la manana (~09 UTC) es descendente y la de la noche
                        # (~22-23 UTC) ascendente
                        pasada = "descendente (por la hora)" if 6 <= int(hhmm[:2]) <= 15 else "ascendente (por la hora)"
                    else:
                        f = m.group(5)
                        hhmm = m.group(6)
                        clave = (sensor, m.group(3), f, m.group(6))
                        modo = {"HI": "HIMAGE (Stripmap, 3 m)", "S2": "Spotlight-2 (1 m)",
                                "PP": "PingPong"}.get(m.group(3), m.group(3)) + " " + m.group(2)
                        pols = m.group(4)
                        # en el nombre de COSMO-SkyMed, despues de la polarizacion: lado de mirada y pasada
                        # (R/L y A/D), p. ej. _VV_RD_ = mira a la derecha, descendente
                        ld = re.search(r"_(?:HH|VV|HV|VH|CO)_[RL]([AD])_", nombre)
                        pasada = {"A": "ascendente", "D": "descendente"}.get(ld.group(1), "") if ld else ""
                    if clave in vistos:
                        continue           # la misma escena en dos carpetas
                    vistos.add(clave)
                    fecha = "%s-%s-%s" % (f[:4], f[4:6], f[6:8])
                    ruta = os.path.join(carpeta, nombre)
                    nuevas = asignar_sitios(
                        {"sensor": sensor, "banda": banda, "lambda_cm": lam,
                         "producto": modo, "escena": nombre, "fecha": fecha,
                         "hora_utc": "%s:%s" % (hhmm[:2], hhmm[2:4]), "pasada": pasada, "modo": modo,
                         "polarizaciones": pols, "pixel_m": "",
                         "pixeles_validos_%": "", "ruta": ruta}, huella_archivo(ruta))
                    filas += nuevas
                    log("  %-12s %s  %s  %s  -> %s" % (sensor, fecha, modo, nombre[:50],
                        ", ".join("%s %s %%" % (n["sitio"], n["cobertura_huella_%"]) for n in nuevas)))
            # SAOCOM-1A: cada pedido es una carpeta con su .xemt
            for a in archivos:
                if a.endswith(".xemt") and "SAR_EOSSP__CORE_L1A" in a:
                    with open(os.path.join(carpeta, a), encoding="utf-8", errors="ignore") as fx:
                        t = fx.read()
                    ini = re.search(r"<startTime>([^<]+)<", t)
                    pol = re.search(r"<acquiredPols>([^<]+)<", t)
                    pas = re.search(r"<OrbitDirection>([^<]+)<", t)
                    modo = re.search(r"<acqMode>([^<]+)<", t)
                    fecha = ini.group(1)[:10] if ini else ""
                    nuevas = asignar_sitios(
                        {"sensor": "SAOCOM-1A", "banda": "L", "lambda_cm": 23.5,
                         "producto": "L1A SLC %s" % (modo.group(1) if modo else ""),
                         "escena": os.path.basename(carpeta), "fecha": fecha,
                         "hora_utc": ini.group(1)[11:16] if ini else "",
                         "pasada": pas.group(1).lower() if pas else "",
                         "modo": modo.group(1) if modo else "",
                         "polarizaciones": pol.group(1) if pol else "",
                         "pixel_m": "", "pixeles_validos_%": "", "ruta": carpeta},
                        huella_archivo(carpeta))
                    filas += nuevas
                    log("  %-12s %s  %s %s  %s  -> %s" % (
                        "SAOCOM-1A", fecha, modo.group(1) if modo else "", pol.group(1) if pol else "",
                        os.path.basename(carpeta),
                        ", ".join("%s %s %%" % (n["sitio"], n["cobertura_huella_%"]) for n in nuevas)))
    return filas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitios", nargs="*", default=list(SITIOS.keys()))
    args = ap.parse_args()

    log = Bitacora(ruta_tp("Tp1", "05_Resultados", "06_Control_calidad"), "Tp1_02_inventario_local")
    filas = []

    # ----------------------------------------------------------- NovaSAR-1
    log.titulo("NovaSAR-1 (banda S, HH, 6 m) en %s" % NOVASAR)
    if not os.path.isdir(NOVASAR):
        log("NO EXISTE la carpeta de NovaSAR en este equipo. Se omite y se deja constancia.")
    else:
        for escena, (fecha_cfg, hora_cfg, _) in NOVASAR_ESCENAS.items():
            try:
                carpeta = novasar_carpeta_grd(escena)
            except FileNotFoundError as e:
                log("  %s: %s" % (escena, e))
                continue
            huella = huella_novasar(carpeta)
            t0 = metadato_novasar(carpeta, "RawDataStartTime")
            modo = metadato_novasar(carpeta, "OperationalModeName")
            for s in args.sitios:
                caja = box(*SITIOS[s]["bbox"])
                cob = 100.0 * huella.intersection(caja).area / caja.area
                if cob == 0:
                    continue
                g = grilla_sitio(s, pixel=PIXEL_CONTEO)
                sig, _ = novasar_sigma0(escena, g)
                val = 100.0 * np.isfinite(sig).mean()
                filas.append({"sensor": "NovaSAR-1", "banda": "S", "lambda_cm": 9.4,
                              "producto": "GRD HH (sigma0 = DN^2/1E+05)", "escena": escena,
                              "fecha": t0[:10], "hora_utc": t0[11:16],
                              "pasada": {"DESCENDING": "descendente", "ASCENDING": "ascendente"}.get(
                                  metadato_novasar(carpeta, "Pass_Direction").upper(), "sin dato"),
                              "modo": modo, "polarizaciones": "HH", "pixel_m": 6,
                              "sitio": s, "cobertura_huella_%": round(cob, 1),
                              "pixeles_validos_%": round(val, 1), "ruta": carpeta})
                log("  %s %s  %-18s huella %5.1f %%   pixeles con dato %5.1f %%"
                    % (escena, t0[:10], s, cob, val))
                if t0[:10] != fecha_cfg:
                    log("     AVISO: la fecha del metadato (%s) no coincide con la de la "
                        "configuracion (%s). Manda el metadato." % (t0[:10], fecha_cfg))

    # ------------------------------------------------------------- NISAR
    for carpeta, nombre in ((os.path.join(NISAR_DELTA, "BANDA_L_NASA"), "L"),
                            (os.path.join(NISAR_DELTA, "BANDA_S_ISRO"), "S"),
                            (os.path.join(ORIGINALES, "NISAR"), "L")):
        log.titulo("NISAR GCOV banda %s en %s" % (nombre, carpeta))
        if not os.path.isdir(carpeta):
            log("NO EXISTE en este equipo. Se omite y se deja constancia.")
            continue
        for h5 in sorted(glob.glob(os.path.join(carpeta, "*.h5"))):
            if "COMPAT" in h5.upper():
                continue          # copias de compatibilidad para SNAP: no son otra escena
            inf = info_nisar(h5)
            for s in args.sitios:
                caja = box(*SITIOS[s]["bbox"])
                cob = 100.0 * inf["huella"].intersection(caja).area / caja.area
                if cob == 0:
                    continue
                g = grilla_sitio(s, pixel=PIXEL_CONTEO)
                try:
                    hh = nisar_gcov_en_grilla(h5, g, "HHHH", inf["banda"])
                    val = 100.0 * np.isfinite(hh).mean()
                except ValueError:
                    val = 0.0
                filas.append({"sensor": "NISAR", "banda": nombre,
                              "lambda_cm": 24.0 if nombre == "L" else 9.4,
                              "producto": "L2 GCOV gamma0 (frecuencia A) v%s" % inf["version"],
                              "escena": os.path.basename(h5)[:-3], "fecha": inf["fecha"],
                              "hora_utc": inf["hora"], "pasada": inf["pasada"].lower(),
                              "modo": "track %s frame %s" % (inf["track"], inf["frame"]),
                              "polarizaciones": inf["terminos"], "pixel_m": inf["pixel_m"],
                              "sitio": s, "cobertura_huella_%": round(cob, 1),
                              "pixeles_validos_%": round(val, 1), "ruta": h5})
                log("  %s %s %-18s huella %5.1f %%   pixeles con dato %5.1f %%"
                    % (inf["fecha"], os.path.basename(h5)[:34], s, cob, val))

    # ------------------------------------------- archivo 2023 y COSMO 2018
    filas += escanear_archivos(log)

    df = pd.DataFrame(filas)
    salida = ruta_tp("Tp1", "05_Resultados", "04_Tablas", "inventario_local.csv")
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    df.to_csv(salida, index=False, encoding="utf-8-sig")
    log.titulo("Resumen")
    if len(df):
        cob = pd.to_numeric(df["cobertura_huella_%"], errors="coerce")
        val = pd.to_numeric(df["pixeles_validos_%"], errors="coerce")
        enganosas = df[(cob >= 50) & (val < 10)]
        log("%d escenas o combinaciones escena-sitio inventariadas." % len(df))
        log("%d tocan el sitio con la huella (>= 50 %%) pero casi no traen dato "
            "(< 10 %%): un catalogo las daria como utiles y no lo son." % len(enganosas))
        for _, f in enganosas.iterrows():
            log("   %s %s %s: huella %.0f %%, dato %.0f %%"
                % (f["sensor"], f["fecha"], f["sitio"], f["cobertura_huella_%"], f["pixeles_validos_%"]))
    log("Tabla:", salida)
    log.cerrar("python Tp1_03_buscar_optico_y_C.py --sitio B_CONCORDIA --desde 2023-10-01 --hasta 2023-11-30")


if __name__ == "__main__":
    main()
