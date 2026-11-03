# -*- coding: utf-8 -*-
"""
funciones_lidar.py
==================
Lectura y filtrado de los dos LiDAR satelitales del curso, directamente de los
granulos .h5 que entrega NASA Earthdata:

  GEDI L2A (version 003)      huellas de 25 m, 1064 nm, desde la Estacion
                              Espacial (entre 51,6 grados N y S).
  ICESat-2 ATL08 (version 007) segmentos de 100 m a lo largo de la traza,
                              6 haces en 3 pares, 532 nm, huella de ~11 m.

Lo que importa entender (y por que este archivo existe)
-------------------------------------------------------
El LiDAR satelital NO forma una imagen: muestrea por huellas o segmentos. Un
granulo trae decenas de miles de disparos de todo el recorrido orbital, y casi
todos caen fuera del sitio o no sirven (nubes, sensibilidad baja, pendiente).
Por eso cada funcion devuelve TODOS los disparos que caen en el sitio, con la
columna "valido" y, cuando no lo es, el "motivo" del descarte. Contar cuantos
se descartan y por que es parte del practico (Tp1 y Tp3).

Filtros de GEDI L2A (se aplican en este orden)
  1. bandera de calidad = 1. En la version 003 el campo se llama
     l2a_quality_flag_rel3; en la 002 se llamaba quality_flag. Se usa el
     que exista y se informa cual.
  2. degrade_flag = 0 (sin degradacion de la geolocalizacion o del apuntamiento).
  3. sensitivity >= 0,95 (umbral habitual; en vegetacion densa puede subirse
     a 0,98 y se declara).
  4. surface_flag = 1 (el modo mas bajo esta a menos de 300 m del MDE).
  5. agua: land_cover_data/landsat_water_persistence < 50 (porcentaje de
     anos Landsat con agua en ese punto, que viene dentro del L2A). GEDI no
     trae una mascara de agua propia como ATL08 (segment_watermask): sin este
     filtro, una huella sobre el rio o el embalse puede quedar "valida". Si el
     granulo no trae el campo, no se filtra y la columna agua_persistencia
     queda vacia (se informa).
  Opcional: solo haces de potencia (BEAM0101, BEAM0110, BEAM1000, BEAM1011),
  que penetran mejor el dosel denso.

Filtros de ATL08 (por segmento de 100 m)
  canopia valida : h_canopy < 3,4e38 (valor de relleno), urban_flag = 0,
                   segment_watermask = 0
  terreno valido : h_te_best_fit < 3,4e38, segment_watermask = 0
  Se informa ademas si el haz es fuerte o debil (orbit_info/sc_orient) y si
  la adquisicion es nocturna (night_flag), que tiene menos ruido solar.

Fechas: GEDI y ATL08 cuentan delta_time en segundos desde el 1 de enero de
2018 (epoca de los dos productos). Se convierte con esa epoca; la diferencia
con UTC (segundos intercalares) es de segundos y no afecta a ninguna fecha.

Alturas de terreno: elev_lowestmode (GEDI) y h_te_best_fit (ATL08) son
ALTURAS ELIPSOIDALES (WGS 84). El Copernicus DEM esta referido al geoide
EGM2008. Antes de comparar hay que convertir (ver alturas_a_egm2008).
"""
import os
import datetime as _dt

import numpy as np

EPOCA = _dt.datetime(2018, 1, 1)
RELLENO = 3.0e38   # umbral: el valor de relleno de ATL08 es 3.4028235e38; todo lo que lo supere es relleno
HACES_POTENCIA_GEDI = ("BEAM0101", "BEAM0110", "BEAM1000", "BEAM1011")


def _fecha(delta_t):
    t = EPOCA + _dt.timedelta(seconds=float(delta_t))
    return t.strftime("%Y-%m-%d"), t.strftime("%H:%M:%S")


def _en_caja(lon, lat, bbox):
    lon0, lat0, lon1, lat1 = bbox
    return (lon >= lon0) & (lon <= lon1) & (lat >= lat0) & (lat <= lat1)


# ======================================================================= GEDI
def leer_gedi_l2a(ruta_h5, bbox, sensibilidad_min=0.95, solo_potencia=False):
    """Disparos GEDI L2A dentro de bbox (lon0, lat0, lon1, lat1).

    Devuelve un DataFrame con una fila por disparo y las columnas:
    granulo, haz, tipo_haz, shot_number, fecha, hora, lon, lat,
    elev_lowestmode_elips, rh50, rh98, rh100, sensitivity, bandera_calidad,
    campo_calidad, degrade_flag, surface_flag, solar_elevation,
    agua_persistencia, valido, motivo
    """
    import h5py
    import pandas as pd

    filas = []
    nombre = os.path.basename(ruta_h5)
    with h5py.File(ruta_h5, "r") as h:
        haces = [k for k in h.keys() if k.startswith("BEAM")]
        for haz in haces:
            g = h[haz]
            if "lat_lowestmode" not in g:
                continue
            lat = g["lat_lowestmode"][:]
            lon = g["lon_lowestmode"][:]
            m = _en_caja(lon, lat, bbox)
            if not m.any():
                continue
            idx = np.nonzero(m)[0]
            campo = ("l2a_quality_flag_rel3" if "l2a_quality_flag_rel3" in g
                     else "quality_flag")
            q = g[campo][:][idx]
            deg = g["degrade_flag"][:][idx]
            sen = g["sensitivity"][:][idx]
            sup = g["surface_flag"][:][idx] if "surface_flag" in g else np.ones(idx.size, "u1")
            rh = g["rh"][idx[0]:idx[-1] + 1, :][idx - idx[0], :]
            dt = g["delta_time"][:][idx]
            elev = g["elev_lowestmode"][:][idx]
            sol = g["solar_elevation"][:][idx]
            shot = g["shot_number"][:][idx]
            campo_agua = "land_cover_data/landsat_water_persistence"
            agua = (g[campo_agua][:][idx].astype(float) if campo_agua in g
                    else np.full(idx.size, np.nan))
            tipo = "potencia" if haz in HACES_POTENCIA_GEDI else "cobertura"
            for j in range(idx.size):
                motivos = []
                if q[j] != 1:
                    motivos.append("calidad")
                if deg[j] != 0:
                    motivos.append("degradado")
                if not (sen[j] >= sensibilidad_min):
                    motivos.append("sensibilidad<%.2f" % sensibilidad_min)
                if sup[j] != 1:
                    motivos.append("superficie")
                if 50 <= agua[j] <= 100:            # 0-100 %; 255 = sin dato
                    motivos.append("agua")
                if solo_potencia and tipo != "potencia":
                    motivos.append("haz_cobertura")
                f, hr = _fecha(dt[j])
                filas.append({
                    "granulo": nombre, "haz": haz, "tipo_haz": tipo,
                    "shot_number": str(shot[j]), "fecha": f, "hora": hr,
                    "lon": float(lon[idx[j]]), "lat": float(lat[idx[j]]),
                    "elev_lowestmode_elips": float(elev[j]),
                    "rh50": float(rh[j, 50]), "rh98": float(rh[j, 98]),
                    "rh100": float(rh[j, 100]),
                    "sensitivity": float(sen[j]), "bandera_calidad": int(q[j]),
                    "campo_calidad": campo, "degrade_flag": int(deg[j]),
                    "surface_flag": int(sup[j]), "solar_elevation": float(sol[j]),
                    "agua_persistencia": float(agua[j]),
                    "valido": not motivos, "motivo": ";".join(motivos),
                })
    return pd.DataFrame(filas)


# ===================================================================== ATL08
def leer_atl08(ruta_h5, bbox):
    """Segmentos ATL08 de 100 m dentro de bbox, con banderas de canopia y terreno.

    Columnas: granulo, haz, fuerza_haz, fecha, hora, lon, lat, nocturno,
    h_canopy, h_te_best_fit_elips, h_te_uncertainty, canopia_valida,
    terreno_valido, motivo_canopia, motivo_terreno
    """
    import h5py
    import pandas as pd

    filas = []
    nombre = os.path.basename(ruta_h5)
    with h5py.File(ruta_h5, "r") as h:
        # sc_orient: 0 = hacia atras -> los haces IZQUIERDOS son los fuertes;
        #            1 = hacia adelante -> los DERECHOS son los fuertes;
        #            2 = transicion (no se clasifica).
        orient = int(np.array(h["orbit_info/sc_orient"][()]).ravel()[0]) if "orbit_info/sc_orient" in h else -1
        for haz in ("gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"):
            base = haz + "/land_segments/"
            if base + "latitude" not in h:
                continue
            lat = h[base + "latitude"][:]
            lon = h[base + "longitude"][:]
            m = _en_caja(lon, lat, bbox)
            if not m.any():
                continue
            if orient == 0:
                fuerza = "fuerte" if haz.endswith("l") else "debil"
            elif orient == 1:
                fuerza = "fuerte" if haz.endswith("r") else "debil"
            else:
                fuerza = "indeterminado"
            dt = h[base + "delta_time"][:][m]
            hc = h[base + "canopy/h_canopy"][:][m]
            te = h[base + "terrain/h_te_best_fit"][:][m]
            teu = (h[base + "terrain/h_te_uncertainty"][:][m]
                   if base + "terrain/h_te_uncertainty" in h else np.full(m.sum(), np.nan))
            agua = h[base + "segment_watermask"][:][m] if base + "segment_watermask" in h else np.zeros(m.sum())
            urb = h[base + "urban_flag"][:][m] if base + "urban_flag" in h else np.zeros(m.sum())
            noche = h[base + "night_flag"][:][m] if base + "night_flag" in h else np.full(m.sum(), -1)
            lo, la = lon[m], lat[m]
            for j in range(lo.size):
                mc, mt = [], []
                if not (hc[j] < RELLENO):
                    mc.append("sin_canopia")
                if urb[j] != 0:
                    mc.append("urbano")
                if agua[j] != 0:
                    mc.append("agua")
                    mt.append("agua")
                if not (te[j] < RELLENO):
                    mt.append("sin_terreno")
                f, hr = _fecha(dt[j])
                filas.append({
                    "granulo": nombre, "haz": haz, "fuerza_haz": fuerza,
                    "fecha": f, "hora": hr, "lon": float(lo[j]), "lat": float(la[j]),
                    "nocturno": int(noche[j]),
                    "h_canopy": float(hc[j]) if hc[j] < RELLENO else np.nan,
                    "h_te_best_fit_elips": float(te[j]) if te[j] < RELLENO else np.nan,
                    "h_te_uncertainty": float(teu[j]) if np.isfinite(teu[j]) and teu[j] < RELLENO else np.nan,
                    "canopia_valida": not mc, "terreno_valido": not mt,
                    "motivo_canopia": ";".join(mc), "motivo_terreno": ";".join(mt),
                })
    return pd.DataFrame(filas)


def leer_atl13(ruta_h5, bbox):
    """Alturas de la superficie del agua de ICESat-2 ATL13 (aguas continentales) en bbox.

    ATL13 promedia los fotones sobre cuerpos de agua de una base de datos de
    lagos, rios y embalses (en el sitio B: rio Uruguay y embalse de Salto
    Grande; en A y E: rio Parana). Columnas: granulo, haz, fecha, hora, lon,
    lat, h_agua_elips (ht_water_surf, elipsoidal WGS 84), h_agua_orto
    (ht_ortho, sobre EGM2008, si el producto lo trae) y tipo_cuerpo
    (inland_water_body_type). Se lee de forma defensiva: un campo que falta
    queda vacio y no detiene la lectura.
    """
    import h5py
    import pandas as pd

    filas = []
    nombre = os.path.basename(ruta_h5)
    with h5py.File(ruta_h5, "r") as h:
        for haz in ("gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"):
            if haz + "/segment_lat" not in h:
                continue
            lat = h[haz + "/segment_lat"][:]
            lon = h[haz + "/segment_lon"][:]
            m = _en_caja(lon, lat, bbox)
            if not m.any():
                continue

            def campo(n):
                k = haz + "/" + n
                return h[k][:][m].astype("float64") if k in h else np.full(m.sum(), np.nan)

            dt = campo("delta_time")
            hw = campo("ht_water_surf")
            ho = campo("ht_ortho")
            tipo = campo("inland_water_body_type")
            for j in range(int(m.sum())):
                f, hr = _fecha(dt[j]) if np.isfinite(dt[j]) else ("", "")
                filas.append({"granulo": nombre, "haz": haz, "fecha": f, "hora": hr,
                              "lon": float(lon[m][j]), "lat": float(lat[m][j]),
                              "h_agua_elips": hw[j] if hw[j] < RELLENO else np.nan,
                              "h_agua_orto": ho[j] if ho[j] < RELLENO else np.nan,
                              "tipo_cuerpo": tipo[j]})
    return pd.DataFrame(filas)


# ============================================================ ALTURAS
def alturas_a_egm2008(lon, lat, h_elipsoidal):
    """Altura elipsoidal WGS 84 -> altura sobre el geoide EGM2008 (la del Copernicus DEM).

    Usa la grilla del geoide de PROJ (us_nga_egm08_25.tif). Si no esta en el
    equipo, PROJ la baja sola cuando PROJ_NETWORK=ON; si tampoco hay red, la
    funcion FALLA con un mensaje claro en lugar de devolver alturas sin
    convertir (el error seria de unos 15 m en Entre Rios: el ondulamiento del
    geoide alli ronda esa cifra y no se nota a simple vista).
    """
    from pyproj import Transformer
    from pyproj.network import set_network_enabled

    set_network_enabled(True)
    tr = Transformer.from_crs("EPSG:4979", "EPSG:4326+3855", always_xy=True)
    _, _, h = tr.transform(np.asarray(lon), np.asarray(lat), np.asarray(h_elipsoidal))
    h = np.asarray(h, dtype="float64")
    if (not np.all(np.isfinite(h[np.isfinite(np.asarray(h_elipsoidal, dtype="float64"))]))
            or np.allclose(h, np.asarray(h_elipsoidal, dtype="float64"), equal_nan=True)):
        raise RuntimeError(
            "PROJ no aplico el geoide EGM2008 (falta la grilla us_nga_egm08_25.tif). "
            "Con red, ejecute en el Miniforge Prompt:  projsync --file us_nga_egm08_25  "
            "y vuelva a correr el script.")
    return h


def a_geopackage(df, ruta, capa):
    """Guarda un DataFrame con columnas lon y lat como puntos en un GeoPackage."""
    import geopandas as gpd

    os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    gdf = gpd.GeoDataFrame(df.copy(), geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs=4326)
    gdf.to_file(ruta, layer=capa, driver="GPKG")
    return ruta
