# -*- coding: utf-8 -*-
"""
exportar_lidar.py
=================
Pasa el LiDAR satelital ya bajado (.h5 de 08_Originales_crudos\\LIDAR\\<SITIO>)
a formatos de uso directo, con los metadatos y la fuente al lado:

  CSV        todas las huellas o segmentos del sitio, con su bandera de validez
             y el motivo de descarte (lo abre cualquier programa).
  XLSX       una hoja LEEME (fuente, version, criterios, columnas y unidades),
             una hoja por producto con las huellas VALIDAS y una hoja de
             resumen por anio. Excel admite 1 048 576 filas por hoja: si un
             producto tiene mas validas, se reparte en una hoja por anio.
  GeoPackage una capa de puntos por producto (EPSG:4326), con todas las
             huellas, y una tabla "metadatos". Se abre en QGIS.
  LEEME.txt  lo mismo que la hoja LEEME, en texto.

Productos (los que haya en el sitio):
  GEDI       un renglon por disparo: L2A (alturas rh), L2B (cobertura, PAI,
             FHD) y L4A (biomasa aerea) unidos por el numero de disparo.
  ATL08      un renglon por segmento de 100 m (dosel y terreno).
  ATL13      un renglon por segmento sobre agua continental (nivel del agua).

Criterios de validez (los mismos de funciones_lidar.py y de los practicos):
  GEDI L2A  l2a_quality_flag_rel3 = 1, degrade_flag = 0, sensitivity >= 0,95, surface_flag = 1
  GEDI L2B  l2b_quality_flag_rel3 = 1, degrade_flag = 0, sensitivity >= 0,95
  GEDI L4A  l4a_quality_flag_rel3 = 1, degrade_flag = 0, sensitivity >= 0,95
  ATL08     canopia: h_canopy sin relleno, urban_flag = 0, segment_watermask = 0
            terreno: h_te_best_fit sin relleno, segment_watermask = 0
  ATL13     ht_water_surf sin relleno

Las alturas son ELIPSOIDALES (WGS 84), como las entrega la NASA, salvo
ht_ortho de ATL13 (sobre el geoide EGM2008). Para pasar las demas a EGM2008:
alturas_a_egm2008() de funciones_lidar.py.

Salida, por sitio:
  00_COMUN\\05_LiDAR_tablas\\<SITIO>\\<SITIO>_GEDI.csv, _ATL08.csv, _ATL13.csv,
  <SITIO>_LiDAR.xlsx, <SITIO>_LiDAR.gpkg, <SITIO>_LiDAR_LEEME.txt
y una copia en <Tp>\\02_Subsets_SNAP_QGIS\\LiDAR_<SITIO>\\ de cada practico que
usa el sitio (SITIOS[...]["practicos"] en configuracion_comun.py).

USO (Miniforge Prompt, entorno sar, en la carpeta 00_COMUN):
    python exportar_lidar.py                     (todos los sitios con LiDAR)
    python exportar_lidar.py --sitios F_BOVRIL   (uno o varios)
    python exportar_lidar.py --sin_copiar        (no copia a los practicos)
"""
import argparse
import datetime as _dt
import glob
import os
import shutil
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from configuracion_comun import SITIOS, ORIGINALES, PRACTICA, COMUN   # noqa: E402

LIDAR = os.path.join(ORIGINALES, "LIDAR")
SALIDA = os.path.join(COMUN, "05_LiDAR_tablas")
EPOCA = np.datetime64("2018-01-01T00:00:00")
RELLENO = 3.0e38
SENS = 0.95
FILAS_EXCEL = 1048575          # una fila queda para el encabezado
HACES_POTENCIA = ("BEAM0101", "BEAM0110", "BEAM1000", "BEAM1011")

FUENTES = {
    "GEDI": "NASA/UMD. GEDI L2A y L2B version 003 (LP DAAC) y L4A version 3 "
            "(ORNL DAAC). https://search.earthdata.nasa.gov",
    "ATL08": "NASA/NSIDC. ICESat-2 ATL08 version 007. https://nsidc.org/data/atl08",
    "ATL13": "NASA/NSIDC. ICESat-2 ATL13 version 007. https://nsidc.org/data/atl13",
}

# columna: (unidad, descripcion)
COLUMNAS = {
    "GEDI": {
        "shot_number": ("", "Numero de disparo GEDI (texto: es un entero de 19 cifras)"),
        "fecha": ("AAAA-MM-DD", "Fecha UTC"), "hora_utc": ("hh:mm:ss", "Hora UTC"),
        "granulo": ("", "Granulo L2A de origen"), "haz": ("", "Haz (BEAMxxxx)"),
        "tipo_haz": ("", "potencia (penetra mejor el dosel) o cobertura"),
        "lat": ("grados", "Latitud WGS 84 del modo mas bajo"),
        "lon": ("grados", "Longitud WGS 84 del modo mas bajo"),
        "elev_suelo_elips": ("m", "elev_lowestmode: cota del suelo, elipsoidal WGS 84"),
        "rh25": ("m", "Altura relativa al 25 % de la energia"),
        "rh50": ("m", "Altura relativa al 50 %"), "rh75": ("m", "Altura relativa al 75 %"),
        "rh95": ("m", "Altura relativa al 95 %"), "rh98": ("m", "Altura relativa al 98 % (altura del dosel)"),
        "rh100": ("m", "Altura relativa al 100 %"),
        "sensitivity": ("0-1", "Sensibilidad del disparo"),
        "degrade_flag": ("", "0 = sin degradacion de la geolocalizacion"),
        "surface_flag": ("", "1 = modo mas bajo a menos de 300 m del MDE"),
        "solar_elevation": ("grados", "Elevacion del Sol (negativa = de noche)"),
        "l2a_quality": ("", "l2a_quality_flag_rel3"),
        "valido_L2A": ("", "Cumple el criterio L2A del curso"),
        "motivo_L2A": ("", "Motivos de descarte L2A, separados por ;"),
        "cover": ("0-1", "L2B: fraccion de cobertura del dosel"),
        "pai": ("m2/m2", "L2B: indice de area vegetal"),
        "fhd_normal": ("", "L2B: diversidad de alturas del follaje"),
        "l2b_quality": ("", "l2b_quality_flag_rel3"),
        "valido_L2B": ("", "Cumple el criterio L2B del curso"),
        "agbd": ("Mg/ha", "L4A: densidad de biomasa aerea"),
        "agbd_se": ("Mg/ha", "L4A: error estandar de agbd"),
        "l4a_quality": ("", "l4a_quality_flag_rel3"),
        "valido_L4A": ("", "Cumple el criterio L4A del curso"),
        "anio": ("", "Anio de la fecha"),
    },
    "ATL08": {
        "fecha": ("AAAA-MM-DD", "Fecha UTC"), "hora_utc": ("hh:mm:ss", "Hora UTC"),
        "granulo": ("", "Granulo ATL08 de origen"), "haz": ("", "Haz (gt1l ... gt3r)"),
        "fuerza_haz": ("", "fuerte o debil (segun la orientacion del satelite)"),
        "lat": ("grados", "Latitud WGS 84 del centro del segmento de 100 m"),
        "lon": ("grados", "Longitud WGS 84"),
        "h_canopy": ("m", "Altura del dosel (percentil 98 de los fotones de canopia)"),
        "h_canopy_incert": ("m", "h_canopy_uncertainty"),
        "h_media_canopia": ("m", "h_mean_canopy"),
        "cobertura_canopia": ("%", "segment_cover: cobertura del dosel (Landsat), en por ciento"),
        "h_terreno_elips": ("m", "h_te_best_fit: cota del terreno, elipsoidal WGS 84"),
        "h_terreno_incert": ("m", "h_te_uncertainty"),
        "pendiente_terreno": ("m/m", "terrain_slope a lo largo de la traza"),
        "nocturno": ("", "night_flag: 1 = de noche (menos ruido solar)"),
        "mascara_agua": ("", "segment_watermask: 1 = agua"),
        "urbano": ("", "urban_flag: 1 = urbano"),
        "canopia_valida": ("", "Cumple el criterio de canopia del curso"),
        "terreno_valido": ("", "Cumple el criterio de terreno del curso"),
        "anio": ("", "Anio de la fecha"),
    },
    "ATL13": {
        "fecha": ("AAAA-MM-DD", "Fecha UTC"), "hora_utc": ("hh:mm:ss", "Hora UTC"),
        "granulo": ("", "Granulo ATL13 de origen"), "haz": ("", "Haz"),
        "lat": ("grados", "Latitud WGS 84 del segmento"), "lon": ("grados", "Longitud WGS 84"),
        "h_agua_elips": ("m", "ht_water_surf: nivel del agua, elipsoidal WGS 84"),
        "h_agua_orto": ("m", "ht_ortho: nivel del agua sobre el geoide EGM2008"),
        "desvio_agua": ("m", "stdev_water_surf"),
        "profundidad": ("m", "water_depth (solo donde se detecta el fondo)"),
        "id_cuerpo_agua": ("", "inland_water_body_id"),
        "tipo_cuerpo_agua": ("", "inland_water_body_type (1 lago, 2 embalse, 4 rio, ...)"),
        "valido": ("", "ht_water_surf sin relleno"),
        "anio": ("", "Anio de la fecha"),
    },
}


def log(t):
    print(time.strftime("%H:%M:%S ") + t, flush=True)


def fechas(dt):
    t = EPOCA + (np.asarray(dt, "f8") * 1e6).astype("timedelta64[us]")
    s = np.datetime_as_string(t, unit="s")
    return np.array([x[:10] for x in s]), np.array([x[11:19] for x in s])


def en_caja(lon, lat, b):
    return (lon >= b[0]) & (lon <= b[2]) & (lat >= b[1]) & (lat <= b[3])


def leer(g, nombres, idx, n):
    """Primera variable que exista (en el haz o en geolocation/), recortada a idx."""
    for v in nombres:
        for r in (v, "geolocation/" + v):
            if r in g and g[r].ndim >= 1 and g[r].shape[0] == n:
                d = g[r]
                return d[:][idx] if d.ndim == 1 else d[:][idx, ...]
    return None


def limpio(x):
    """Valores de relleno (3,4e38 en ICESat-2; -9999 en GEDI L2B y L4A) -> vacio."""
    x = np.asarray(x, "f8")
    return np.where((np.abs(x) < RELLENO) & (x > -9998), x, np.nan)


# ----------------------------------------------------------------- GEDI
def gedi_l2a(f, b):
    import h5py
    partes = []
    with h5py.File(f, "r") as h:
        for haz in sorted(k for k in h if k.startswith("BEAM")):
            g = h[haz]
            if "lat_lowestmode" not in g and "geolocation/lat_lowestmode" not in g:
                continue
            lat = lon = None
            for v in ("lat_lowestmode", "geolocation/lat_lowestmode"):
                if v in g:
                    lat, lon = g[v][:], g[v.replace("lat_", "lon_")][:]
                    break
            n = lat.shape[0]
            m = np.nonzero(en_caja(lon, lat, b))[0]
            if m.size == 0:
                continue
            rh = leer(g, ["rh"], m, n)
            q = leer(g, ["l2a_quality_flag_rel3", "quality_flag"], m, n)
            d = pd.DataFrame({
                "shot_number": leer(g, ["shot_number"], m, n).astype("u8"),
                "dt": leer(g, ["delta_time"], m, n),
                "granulo": os.path.basename(f).replace("_recorte.h5", ""),
                "haz": haz, "tipo_haz": "potencia" if haz in HACES_POTENCIA else "cobertura",
                "lat": lat[m], "lon": lon[m],
                "elev_suelo_elips": limpio(leer(g, ["elev_lowestmode"], m, n)),
                "rh25": rh[:, 25], "rh50": rh[:, 50], "rh75": rh[:, 75],
                "rh95": rh[:, 95], "rh98": rh[:, 98], "rh100": rh[:, 100],
                "sensitivity": leer(g, ["sensitivity"], m, n),
                "degrade_flag": leer(g, ["degrade_flag"], m, n),
                "surface_flag": leer(g, ["surface_flag"], m, n),
                "solar_elevation": leer(g, ["solar_elevation"], m, n),
                "l2a_quality": q,
            })
            partes.append(d)
    return partes


def gedi_extra(f, b, prod):
    """L2B o L4A: devuelve solo shot_number y las variables del producto."""
    import h5py
    partes = []
    with h5py.File(f, "r") as h:
        for haz in sorted(k for k in h if k.startswith("BEAM")):
            g = h[haz]
            lat = lon = None
            for v in ("lat_lowestmode", "geolocation/lat_lowestmode"):
                if v in g:
                    lat, lon = g[v][:], g[v.replace("lat_", "lon_")][:]
                    break
            if lat is None:
                continue
            n = lat.shape[0]
            m = np.nonzero(en_caja(lon, lat, b))[0]
            if m.size == 0:
                continue
            d = {"shot_number": leer(g, ["shot_number"], m, n).astype("u8")}
            if prod == "L2B":
                d["cover"] = limpio(leer(g, ["cover"], m, n))
                d["pai"] = limpio(leer(g, ["pai"], m, n))
                d["fhd_normal"] = limpio(leer(g, ["fhd_normal"], m, n))
                d["l2b_quality"] = leer(g, ["l2b_quality_flag_rel3", "l2b_quality_flag"], m, n)
            else:
                d["agbd"] = limpio(leer(g, ["agbd"], m, n))
                d["agbd_se"] = limpio(leer(g, ["agbd_se"], m, n))
                d["l4a_quality"] = leer(g, ["l4a_quality_flag_rel3", "l4_quality_flag"], m, n)
            for k in list(d):
                if d[k] is None:
                    d[k] = np.full(m.size, np.nan)
            partes.append(pd.DataFrame(d))
    return partes


def tabla_gedi(sitio, b):
    def juntar(carpeta, fn, *extra):
        archivos = sorted(glob.glob(os.path.join(LIDAR, sitio, carpeta, "*.h5")))
        partes = []
        for i, f in enumerate(archivos, 1):
            try:
                partes += fn(f, b, *extra)
            except Exception as e:                  # noqa: BLE001
                log("    no se pudo leer %s: %s" % (os.path.basename(f), str(e)[:80]))
            if i % 50 == 0:
                log("    %s: %d de %d archivos" % (carpeta, i, len(archivos)))
        return (pd.concat(partes, ignore_index=True) if partes else None), len(archivos)

    a, na = juntar("GEDI02_A", gedi_l2a)
    if a is None:
        return None, {}
    a = a.drop_duplicates("shot_number")
    fe, ho = fechas(a.pop("dt"))
    a.insert(1, "fecha", fe)
    a.insert(2, "hora_utc", ho)
    mot = pd.DataFrame({"calidad": a.l2a_quality != 1, "degradado": a.degrade_flag != 0,
                        "sensibilidad<0.95": ~(a.sensitivity >= SENS), "superficie": a.surface_flag != 1})
    a["valido_L2A"] = ~mot.any(axis=1)
    motivo = pd.Series("", index=a.index)
    for c in mot.columns:                      # vectorizado: millones de disparos
        motivo = motivo.where(~mot[c], motivo + ";" + c)
    a["motivo_L2A"] = motivo.str.lstrip(";")
    n = {"GEDI L2A": na}
    for carpeta, prod, cols in (("GEDI02_B", "L2B", ["cover", "pai", "fhd_normal", "l2b_quality"]),
                                ("GEDI_L4A", "L4A", ["agbd", "agbd_se", "l4a_quality"])):
        x, nx = juntar(carpeta, gedi_extra, prod)
        n["GEDI " + prod] = nx
        if x is None:
            for c in cols:
                a[c] = np.nan
        else:
            a = a.merge(x.drop_duplicates("shot_number"), on="shot_number", how="left")
        q = a[cols[-1]]
        a["valido_" + prod] = (q == 1) & (a.degrade_flag == 0) & (a.sensitivity >= SENS)
    a["anio"] = a.fecha.str[:4].astype(int)
    a["shot_number"] = a.shot_number.astype(str)
    orden = list(COLUMNAS["GEDI"])
    return a[[c for c in orden if c in a.columns]], n


# ---------------------------------------------------------------- ICESat-2
def atl08(f, b):
    import h5py
    partes = []
    with h5py.File(f, "r") as h:
        o = int(np.array(h["orbit_info/sc_orient"][()]).ravel()[0]) if "orbit_info/sc_orient" in h else -1
        for haz in ("gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"):
            s = haz + "/land_segments/"
            if s + "latitude" not in h:
                continue
            lat, lon = h[s + "latitude"][:], h[s + "longitude"][:]
            m = en_caja(lon, lat, b)
            if not m.any():
                continue

            def v(r):
                return limpio(h[s + r][:][m]) if s + r in h else np.full(int(m.sum()), np.nan)

            fuerza = ("fuerte" if haz.endswith("l") else "debil") if o == 0 else \
                     ("fuerte" if haz.endswith("r") else "debil") if o == 1 else "indeterminado"
            hc, te = v("canopy/h_canopy"), v("terrain/h_te_best_fit")
            agua, urb = v("segment_watermask"), v("urban_flag")
            fe, ho = fechas(h[s + "delta_time"][:][m])
            partes.append(pd.DataFrame({
                "fecha": fe, "hora_utc": ho, "granulo": os.path.basename(f), "haz": haz,
                "fuerza_haz": fuerza, "lat": lat[m], "lon": lon[m],
                "h_canopy": hc, "h_canopy_incert": v("canopy/h_canopy_uncertainty"),
                "h_media_canopia": v("canopy/h_mean_canopy"), "cobertura_canopia": v("canopy/segment_cover"),
                "h_terreno_elips": te, "h_terreno_incert": v("terrain/h_te_uncertainty"),
                "pendiente_terreno": v("terrain/terrain_slope"), "nocturno": v("night_flag"),
                "mascara_agua": agua, "urbano": urb,
                "canopia_valida": np.isfinite(hc) & (urb == 0) & (agua == 0),
                "terreno_valido": np.isfinite(te) & (agua == 0)}))
    return partes


def atl13(f, b):
    import h5py
    partes = []
    with h5py.File(f, "r") as h:
        for haz in ("gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"):
            if haz + "/segment_lat" not in h:
                continue
            lat, lon = h[haz + "/segment_lat"][:], h[haz + "/segment_lon"][:]
            m = en_caja(lon, lat, b)
            if not m.any():
                continue

            def v(r):
                k = haz + "/" + r
                return limpio(h[k][:][m]) if k in h and h[k].shape[0] == lat.shape[0] else np.full(int(m.sum()), np.nan)

            hw = v("ht_water_surf")
            fe, ho = fechas(h[haz + "/delta_time"][:][m])
            partes.append(pd.DataFrame({
                "fecha": fe, "hora_utc": ho, "granulo": os.path.basename(f), "haz": haz,
                "lat": lat[m], "lon": lon[m], "h_agua_elips": hw, "h_agua_orto": v("ht_ortho"),
                "desvio_agua": v("stdev_water_surf"), "profundidad": v("water_depth"),
                "id_cuerpo_agua": v("inland_water_body_id"), "tipo_cuerpo_agua": v("inland_water_body_type"),
                "valido": np.isfinite(hw)}))
    return partes


def tabla_icesat(sitio, b, prod):
    archivos = sorted(glob.glob(os.path.join(LIDAR, sitio, prod, "*.h5")))
    fn = atl08 if prod == "ATL08" else atl13
    partes = []
    for f in archivos:
        try:
            partes += fn(f, b)
        except Exception as e:                      # noqa: BLE001
            log("    no se pudo leer %s: %s" % (os.path.basename(f), str(e)[:80]))
    if not partes:
        return None, len(archivos)
    t = pd.concat(partes, ignore_index=True)
    t["anio"] = t.fecha.str[:4].astype(int)
    return t, len(archivos)


# ---------------------------------------------------------------- salidas
def texto_leeme(sitio, tablas, archivos):
    b = SITIOS[sitio]["bbox"]
    L = ["LiDAR satelital del sitio %s (%s)" % (sitio, SITIOS[sitio]["nombre"]),
         "Recuadro del sitio (lon0, lat0, lon1, lat1): %s" % (b,),
         "Generado el %s con 00_COMUN\\exportar_lidar.py a partir de los .h5 de "
         "08_Originales_crudos\\LIDAR\\%s." % (_dt.datetime.now().strftime("%d/%m/%Y %H:%M"), sitio),
         "", "Criterios de validez:",
         "  GEDI L2A: l2a_quality_flag_rel3 = 1, degrade_flag = 0, sensitivity >= 0,95, surface_flag = 1",
         "  GEDI L2B: l2b_quality_flag_rel3 = 1, degrade_flag = 0, sensitivity >= 0,95",
         "  GEDI L4A: l4a_quality_flag_rel3 = 1, degrade_flag = 0, sensitivity >= 0,95",
         "  ATL08: canopia = h_canopy con dato, no urbano, no agua; terreno = h_te_best_fit con dato, no agua",
         "  ATL13: ht_water_surf con dato",
         "Alturas elipsoidales WGS 84, salvo h_agua_orto (geoide EGM2008).",
         "CSV: separador coma, decimal punto, UTF-8. Celdas vacias = sin dato.", ""]
    for k, t in tablas.items():
        val = t["valido_L2A"] if k == "GEDI" else t["canopia_valida"] if k == "ATL08" else t["valido"]
        que = {"GEDI": "validos L2A", "ATL08": "con canopia valida"}.get(k, "validos")
        L += ["%s: %d renglones, %d %s (%.1f %%), %s a %s; archivos .h5 leidos: %s"
              % (k, len(t), int(val.sum()), que, 100.0 * val.mean() if len(t) else 0,
                 t.fecha.min(), t.fecha.max(), archivos.get(k)),
              "  Fuente: %s" % FUENTES[k], "  Columnas:"]
        L += ["    %-20s %-11s %s" % (c, COLUMNAS[k][c][0], COLUMNAS[k][c][1]) for c in t.columns if c in COLUMNAS[k]]
        L.append("")
    return "\n".join(L)


def escribir_xlsx(ruta, sitio, tablas, leeme):
    from openpyxl import Workbook
    from openpyxl.styles import Font

    wb = Workbook(write_only=True)
    ws = wb.create_sheet("LEEME")
    for linea in leeme.split("\n"):
        ws.append([linea])
    # resumen por anio
    ws = wb.create_sheet("Resumen_por_anio")
    ws.append(["producto", "anio", "renglones", "validos"])
    for k, t in tablas.items():
        val = "valido_L2A" if k == "GEDI" else "canopia_valida" if k == "ATL08" else "valido"
        for anio, g in t.groupby("anio"):
            ws.append([k, int(anio), int(len(g)), int(g[val].sum())])
    for k, t in tablas.items():
        val = "valido_L2A" if k == "GEDI" else "canopia_valida" if k == "ATL08" else "valido"
        v = t[t[val]]
        grupos = [("%s_validos" % k, v)] if len(v) <= FILAS_EXCEL else \
                 [("%s_%d" % (k, a), g) for a, g in v.groupby("anio")]
        for nombre, g in grupos:
            ws = wb.create_sheet(nombre[:31])
            ws.append(list(g.columns))
            for fila in g.itertuples(index=False):
                ws.append([None if (isinstance(x, float) and x != x) else
                           (bool(x) if isinstance(x, (bool, np.bool_)) else
                            x.item() if hasattr(x, "item") else x) for x in fila])
            log("    hoja %s: %d renglones" % (nombre, len(g)))
    wb.save(ruta + ".part")
    os.replace(ruta + ".part", ruta)


def escribir_gpkg(ruta, tablas, leeme):
    import geopandas as gpd
    import pyogrio

    if os.path.exists(ruta):
        os.remove(ruta)
    for k, t in tablas.items():
        g = gpd.GeoDataFrame(t, geometry=gpd.points_from_xy(t.lon, t.lat), crs=4326)
        pyogrio.write_dataframe(g, ruta, layer=k.lower(), driver="GPKG",
                                layer_options={"DESCRIPTION": FUENTES[k]})
    meta = pd.DataFrame({"linea": leeme.split("\n")})
    pyogrio.write_dataframe(meta, ruta, layer="metadatos", driver="GPKG")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitios", nargs="*", default=[])
    ap.add_argument("--sin_copiar", action="store_true")
    a = ap.parse_args()
    sitios = a.sitios or sorted(d for d in os.listdir(LIDAR) if d in SITIOS)
    for sitio in sitios:
        b = SITIOS[sitio]["bbox"]
        log("==== %s" % sitio)
        tablas, archivos = {}, {}
        t, n = tabla_gedi(sitio, b)
        if t is not None:
            tablas["GEDI"] = t
            archivos["GEDI"] = ", ".join("%s %d" % kv for kv in n.items())
            log("  GEDI: %d disparos" % len(t))
        for prod in ("ATL08", "ATL13"):
            t, n = tabla_icesat(sitio, b, prod)
            if t is not None:
                tablas[prod] = t
                archivos[prod] = n
                log("  %s: %d segmentos" % (prod, len(t)))
            elif n:
                log("  %s: %d archivos, ningun segmento dentro del sitio" % (prod, n))
        if not tablas:
            log("  sin LiDAR: se saltea")
            continue
        d = os.path.join(SALIDA, sitio)
        os.makedirs(d, exist_ok=True)
        leeme = texto_leeme(sitio, tablas, archivos)
        with open(os.path.join(d, "%s_LiDAR_LEEME.txt" % sitio), "w", encoding="utf-8-sig") as fh:
            fh.write(leeme)
        for k, t in tablas.items():
            t.to_csv(os.path.join(d, "%s_%s.csv" % (sitio, k)), index=False, encoding="utf-8-sig")
        log("  CSV listos")
        escribir_gpkg(os.path.join(d, "%s_LiDAR.gpkg" % sitio), tablas, leeme)
        log("  GeoPackage listo")
        escribir_xlsx(os.path.join(d, "%s_LiDAR.xlsx" % sitio), sitio, tablas, leeme)
        log("  Excel listo")
        if not a.sin_copiar:
            for tp in SITIOS[sitio].get("practicos", []):
                dirs = glob.glob(os.path.join(PRACTICA, tp + "_*"))
                if not dirs:
                    continue
                dest = os.path.join(dirs[0], "02_Subsets_SNAP_QGIS", "LiDAR_%s" % sitio)
                if os.path.isdir(dest):
                    shutil.rmtree(dest)
                shutil.copytree(d, dest)
                log("  copiado a %s" % os.path.relpath(dest, PRACTICA))
    log("Terminado. Tablas en %s" % SALIDA)


if __name__ == "__main__":
    main()
