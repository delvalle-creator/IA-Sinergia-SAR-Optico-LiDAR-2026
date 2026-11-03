# -*- coding: utf-8 -*-
"""Recuento de disparos (GEDI) y segmentos (ICESat-2) de cada sitio: total y validos.

Uso (Miniforge Prompt, entorno sar, en la carpeta 00_COMUN):
    python contar_lidar.py

Lee los .h5 de 08_Originales_crudos\\LIDAR\\<SITIO>\\<PRODUCTO> (solo la carpeta,
no las subcarpetas) y cuenta lo que cae dentro del recuadro del sitio.
Escribe en 08_Originales_crudos\\LIDAR:
    recuento_lidar.csv          un renglon por sitio y producto
    recuento_lidar_por_anio.csv lo mismo, separado por anio
    recuento_lidar_avance.txt   avance (se puede mirar mientras corre)

Criterios de validez (los mismos de funciones_lidar.py y de los practicos):
  GEDI L2A : l2a_quality_flag_rel3 = 1, degrade_flag = 0, sensitivity >= 0,95, surface_flag = 1
  GEDI L2B : l2b_quality_flag_rel3 = 1, degrade_flag = 0, sensitivity >= 0,95
  GEDI L4A : l4a_quality_flag_rel3 = 1, degrade_flag = 0, sensitivity >= 0,95
  ATL08    : canopia valida = h_canopy sin relleno, urban_flag = 0, segment_watermask = 0
             terreno valido = h_te_best_fit sin relleno, segment_watermask = 0
  ATL13    : ht_water_surf sin relleno
  ATL22    : solo se cuentan los granulos
"""
import glob
import os
import time

import h5py
import numpy as np
import pandas as pd

from configuracion_comun import SITIOS, ORIGINALES

LIDAR = os.path.join(ORIGINALES, "LIDAR")
RELLENO = 3.0e38
SENS = 0.95
EPOCA = np.datetime64("2018-01-01T00:00:00")
AVANCE = os.path.join(LIDAR, "recuento_lidar_avance.txt")


def avance(txt):
    print(txt)
    with open(AVANCE, "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + txt + "\n")


def anios(dt):
    t = EPOCA + (np.asarray(dt, "f8") * 1e6).astype("timedelta64[us]")
    return t.astype("datetime64[Y]").astype(int) + 1970


def en_caja(lon, lat, b):
    return (lon >= b[0]) & (lon <= b[2]) & (lat >= b[1]) & (lat <= b[3])


def var(g, nombres, idx, n):
    """Primera variable que exista (en el haz o en su subgrupo geolocation)."""
    for v in nombres:
        for ruta in (v, "geolocation/" + v):
            if ruta in g and g[ruta].ndim == 1 and g[ruta].shape[0] == n:
                return g[ruta][:][idx], ruta
    return None, None


def gedi(ruta, b, prod):
    campos = set()
    bandera = {"L2A": ["l2a_quality_flag_rel3", "quality_flag"],
               "L2B": ["l2b_quality_flag_rel3", "l2b_quality_flag"],
               "L4A": ["l4a_quality_flag_rel3", "l4_quality_flag"]}[prod]
    salida = []
    with h5py.File(ruta, "r") as h:
        for haz in (k for k in h.keys() if k.startswith("BEAM")):
            g = h[haz]
            lat = lon = None
            for v in ("lat_lowestmode", "geolocation/lat_lowestmode"):
                if v in g:
                    lat = g[v][:]
                    lon = g[v.replace("lat_", "lon_")][:]
                    break
            if lat is None:
                continue
            n = lat.shape[0]
            m = np.nonzero(en_caja(lon, lat, b))[0]
            if m.size == 0:
                continue
            q, cq = var(g, bandera, m, n)
            deg, _ = var(g, ["degrade_flag"], m, n)
            sen, _ = var(g, ["sensitivity"], m, n)
            ok = np.ones(m.size, bool)
            ok &= (q == 1) if q is not None else False
            if deg is not None:
                ok &= deg == 0
            if sen is not None:
                ok &= sen >= SENS
            if prod == "L2A":
                sup, _ = var(g, ["surface_flag"], m, n)
                if sup is not None:
                    ok &= sup == 1
            dt, _ = var(g, ["delta_time"], m, n)
            a = anios(dt) if dt is not None else np.zeros(m.size, int)
            salida.append(pd.DataFrame({"anio": a, "valido": ok}))
            campos.add(cq)
    return salida, campos


def atl08(ruta, b):
    salida = []
    with h5py.File(ruta, "r") as h:
        for haz in ("gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"):
            s = haz + "/land_segments/"
            if s + "latitude" not in h:
                continue
            m = en_caja(h[s + "longitude"][:], h[s + "latitude"][:], b)
            if not m.any():
                continue
            k = int(m.sum())
            hc = h[s + "canopy/h_canopy"][:][m]
            te = h[s + "terrain/h_te_best_fit"][:][m]
            agua = h[s + "segment_watermask"][:][m] if s + "segment_watermask" in h else np.zeros(k)
            urb = h[s + "urban_flag"][:][m] if s + "urban_flag" in h else np.zeros(k)
            salida.append(pd.DataFrame({"anio": anios(h[s + "delta_time"][:][m]),
                                        "valido": (hc < RELLENO) & (urb == 0) & (agua == 0),
                                        "terreno": (te < RELLENO) & (agua == 0)}))
    return salida


def atl13(ruta, b):
    salida = []
    with h5py.File(ruta, "r") as h:
        for haz in ("gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"):
            if haz + "/segment_lat" not in h:
                continue
            m = en_caja(h[haz + "/segment_lon"][:], h[haz + "/segment_lat"][:], b)
            if not m.any():
                continue
            hw = h[haz + "/ht_water_surf"][:][m]
            salida.append(pd.DataFrame({"anio": anios(h[haz + "/delta_time"][:][m]),
                                        "valido": hw < RELLENO}))
    return salida


PRODUCTOS = [("GEDI02_A", "GEDI L2A"), ("GEDI02_B", "GEDI L2B"), ("GEDI_L4A", "GEDI L4A"),
             ("ATL08", "ICESat-2 ATL08"), ("ATL13", "ICESat-2 ATL13"), ("ATL22", "ICESat-2 ATL22")]

open(AVANCE, "w", encoding="utf-8").close()
avance("Inicio del recuento")
filas, filas_anio = [], []
for sitio in sorted(d for d in os.listdir(LIDAR) if d in SITIOS):
    b = SITIOS[sitio]["bbox"]
    for carpeta, nombre in PRODUCTOS:
        archivos = sorted(glob.glob(os.path.join(LIDAR, sitio, carpeta, "*.h5")))
        if not archivos:
            continue
        partes, errores, con_datos, campos = [], [], 0, set()
        for f in archivos:
            try:
                if carpeta.startswith("GEDI"):
                    p, c = gedi(f, b, {"GEDI02_A": "L2A", "GEDI02_B": "L2B", "GEDI_L4A": "L4A"}[carpeta])
                    campos |= c
                elif carpeta == "ATL08":
                    p = atl08(f, b)
                elif carpeta == "ATL13":
                    p = atl13(f, b)
                else:
                    p = []
                if p:
                    con_datos += 1
                partes += p
            except Exception as e:                    # noqa: BLE001
                errores.append("%s: %s" % (os.path.basename(f), str(e)[:100]))
        t = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame({"anio": [], "valido": []})
        fila = {"sitio": sitio, "producto": nombre, "archivos": len(archivos),
                "archivos_con_datos_en_sitio": con_datos if carpeta != "ATL22" else "",
                "total": len(t) if carpeta != "ATL22" else "",
                "validos": int(t["valido"].sum()) if carpeta != "ATL22" else "",
                "pct_validos": round(100 * t["valido"].mean(), 1) if len(t) else "",
                "terreno_valido_ATL08": int(t["terreno"].sum()) if "terreno" in t else "",
                "anio_primero": int(t["anio"].min()) if len(t) else "",
                "anio_ultimo": int(t["anio"].max()) if len(t) else "",
                "campo_calidad": ";".join(sorted(c for c in campos if c)),
                "errores": len(errores)}
        filas.append(fila)
        if len(t):
            for a, g in t.groupby("anio"):
                filas_anio.append({"sitio": sitio, "producto": nombre, "anio": int(a),
                                   "total": len(g), "validos": int(g["valido"].sum())})
        avance("%-22s %-15s archivos %4d  total %9s  validos %9s  errores %d"
               % (sitio, nombre, len(archivos), fila["total"], fila["validos"], len(errores)))
        for e in errores[:5]:
            avance("    error " + e)

pd.DataFrame(filas).to_csv(os.path.join(LIDAR, "recuento_lidar.csv"), index=False, encoding="utf-8-sig")
pd.DataFrame(filas_anio).to_csv(os.path.join(LIDAR, "recuento_lidar_por_anio.csv"), index=False, encoding="utf-8-sig")
avance("Terminado. Tablas: recuento_lidar.csv y recuento_lidar_por_anio.csv")
