# -*- coding: utf-8 -*-
"""
Tp7_04_icesat2_20m_cicatriz.py   [SE CORRE]   Tp7, paso 6 de la guia (complemento del control en QGIS)
=========================================================================================
Copia, para el alumno, de icesat2_20m_cicatriz.py del desarrollo del docente (22/10/2026).

QUE HACE
  ATL08 trae, ademas de la cota del terreno de cada segmento de 100 m, la cota cada 20 m
  (land_segments/terrain/h_te_best_fit_20m: cinco valores por segmento). Este programa:
    1. lee esos puntos en los granulos ATL08 v007 que pasan a menos de ~1 km de la cicatriz;
    2. los pasa de altura elipsoidal a SRVN16 (para el IGN) y a EGM2008 (para el GLO-30), con las
       ondulaciones que ya trae la tabla LiDAR del sitio (columnas N_ar16 y N_egm2008);
    3. los compara con el IGN 5 m (2013) en el mismo lugar y resta el sesgo del IGN medido en
       terreno llano CERCANO (pendiente < 3 %, cota > 15 m, a mas de 300 m de la cicatriz). Se usa
       el sesgo local y no el de todo el sitio (Tabla 5) porque el corrimiento del IGN varia en el
       espacio;
    4. mide el error en laderas SIN evento (pendiente > 15 %, a mas de 200 m de las formas):
       percentiles 10 y 90, que son el rango contra el que se juzga cada punto de la cicatriz;
    5. dibuja las transectas que cruzan la cicatriz y el deposito.

  Todas las cotas de ICESat-2 son POSTERIORES al comienzo del deslizamiento (el satelite se lanzo
  el 15/09/2018) y se comparan contra el IGN de 2013: una diferencia no se atribuye solo a 2018.

ENTRADAS
  00_COMUN/08_Originales_crudos/LIDAR/E1_DIAMANTE_BARRANCA/ATL08/*.h5 (granulos ATL08 v007)
  02_Subsets_SNAP_QGIS/LiDAR_E1_DIAMANTE_BARRANCA/E1_DIAMANTE_BARRANCA_ATL08.csv (ondulaciones)
  02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/E1_DIAMANTE_BARRANCA_IGN_MDE_5m.tif, _CopernicusDEM30.tif
  04_Tablas_de_trabajo/E1_cicatriz_y_deposito.gpkg (capa formas) y la grieta (COSMO_DIAMANTE/GRIETAS)

SALIDAS
  05_Resultados/04_Tablas/E1_atl08_20m_cicatriz.csv
  05_Resultados/05_Graficos/E1_icesat2_20m_transectas.png
  05_Resultados/06_Control_calidad/Tp7_04_icesat2_20m.log

USO
    python Tp7_04_icesat2_20m_cicatriz.py
"""
import glob
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import ORIGINALES, COSMO_DIAMANTE, ruta_tp   # noqa: E402
from funciones_comunes import Bitacora                                # noqa: E402

# ------------------------------------------------------------ PARAMETROS
SITIO = "E1_DIAMANTE_BARRANCA"
VENTANA_GRADOS = 0.012        # medio lado de la caja de busqueda alrededor de la cicatriz
PEND_LLANO = 3.0              # % : terreno llano para el sesgo local
DIST_LLANO = 300.0            # m : el llano tiene que estar a mas de esto de la cicatriz
PEND_LADERA = 15.0            # % : laderas sin evento para el error
DIST_LADERA = 200.0           # m : ... a mas de esto de las formas
CRS = "EPSG:32721"


def main():
    import geopandas as gpd
    import h5py
    import rasterio
    from scipy.spatial import cKDTree

    log = Bitacora(ruta_tp("Tp7", "05_Resultados", "06_Control_calidad"), "Tp7_04_icesat2_20m")
    Q = ruta_tp("Tp7", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", SITIO + "_")
    carpeta = os.path.join(ORIGINALES, "LIDAR", SITIO, "ATL08")
    granulos = sorted(glob.glob(os.path.join(carpeta, "*.h5")))
    if not granulos:
        sys.exit("No encuentro granulos ATL08 en %s. Bajarlos con Tp1_05_buscar_lidar.py --descargar." % carpeta)
    f = gpd.read_file(ruta_tp("Tp7", "04_Tablas_de_trabajo", "E1_cicatriz_y_deposito.gpkg"), layer="formas").to_crs(CRS)
    if f.empty:
        sys.exit("La capa de cicatriz y deposito esta vacia: digitalizar primero (paso 4).")
    cic = f[f.tipo == "cicatriz"].union_all()
    dep = f[f.tipo == "deposito"].union_all()
    c = gpd.GeoSeries([f.union_all().centroid], crs=CRS).to_crs(4326).iloc[0]
    filas = []
    for fn in granulos:
        with h5py.File(fn, "r") as h:
            for b in ("gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"):
                if b + "/land_segments" not in h:
                    continue
                L = h[b + "/land_segments"]
                lat, lon = L["latitude_20m"][:], L["longitude_20m"][:]
                z = L["terrain/h_te_best_fit_20m"][:]
                m = (np.abs(lat - c.y) < VENTANA_GRADOS) & (np.abs(lon - c.x) < VENTANA_GRADOS)
                if not m.any():
                    continue
                tipo = h[b].attrs.get("atlas_beam_type", b"")
                tipo = tipo.decode() if isinstance(tipo, bytes) else str(tipo)
                for i, j in np.argwhere(m):
                    if z[i, j] > 1e30:                      # valor de relleno: sin terreno en ese punto
                        continue
                    filas.append(dict(granulo=os.path.basename(fn), fecha=os.path.basename(fn)[6:14], haz=b, tipo=tipo,
                                      lat=float(lat[i, j]), lon=float(lon[i, j]), h_elips=float(z[i, j])))
    R = pd.DataFrame(filas)
    log("Puntos de 20 m con terreno a menos de %.3f grados de la cicatriz: %d (en %d granulos)."
        % (VENTANA_GRADOS, len(R), R.granulo.nunique()))
    a = pd.read_csv(ruta_tp("Tp7", "02_Subsets_SNAP_QGIS", "LiDAR_" + SITIO, SITIO + "_ATL08.csv"))
    _, k = cKDTree(np.c_[a.lon, a.lat]).query(np.c_[R.lon, R.lat])
    R["h_srvn16"] = R.h_elips - a.N_ar16.values[k]
    R["h_egm"] = R.h_elips - a.N_egm2008.values[k]

    def muestrear(nombre, lon, lat, cero_es_nada=False):
        with rasterio.open(Q + nombre + ".tif") as s:
            v = np.array([x[0] for x in s.sample(zip(lon, lat))], float)
            if s.nodata is not None and not np.isnan(s.nodata):
                v[v == s.nodata] = np.nan
            if cero_es_nada:
                v[v <= 0] = np.nan
        return v
    ign = muestrear("IGN_MDE_5m", R.lon, R.lat)
    if os.path.exists(Q + "IGN_MDE_mosaico2018.tif"):
        ign = np.where(np.isfinite(ign), ign, muestrear("IGN_MDE_mosaico2018", R.lon, R.lat, True))
    g = gpd.GeoDataFrame(R, geometry=gpd.points_from_xy(R.lon, R.lat), crs=4326).to_crs(CRS)
    g["ign"] = ign
    g["glo"] = muestrear("CopernicusDEM30", R.lon, R.lat)
    g["d_cic"] = g.distance(cic)
    g["d_dep"] = g.distance(dep)
    g["dI"] = g.h_srvn16 - g.ign
    g = g.sort_values(["granulo", "haz", "lat"])
    # pendiente local del IGN a lo largo de la traza (puntos cada 20 m)
    g["pend_ign"] = g.groupby(["granulo", "haz"]).ign.transform(lambda s: (s.diff().abs() / 20 * 100).rolling(2, min_periods=1).mean())
    ok = g.dI.notna()
    llano = ok & (g.pend_ign < PEND_LLANO) & (g.ign > 15) & (g.d_cic > DIST_LLANO)
    sesgo = float(g.dI[llano].median())
    log("Sesgo local del IGN (ICESat-2 menos IGN en llano cercano): %+.2f m con %d puntos." % (sesgo, llano.sum()))
    log("   Se usa el sesgo LOCAL y no el de todo el sitio: el corrimiento del IGN varia en el espacio.")
    g["dIc"] = g.dI - sesgo
    lad = ok & (g.pend_ign > PEND_LADERA) & (g.d_cic > DIST_LADERA) & (g.d_dep > DIST_LADERA)
    p10, p50, p90 = g.dIc[lad].quantile([.1, .5, .9])
    log("Laderas sin evento (pendiente > %.0f %%, a mas de %.0f m): %d puntos; percentiles 10, 50 y 90: %+.1f, %+.1f, %+.1f m."
        % (PEND_LADERA, DIST_LADERA, lad.sum(), p10, p50, p90))
    for nombre, m in (("cicatriz (a <= 10 m)", g.d_cic <= 10), ("deposito (a <= 10 m)", g.d_dep <= 10)):
        s = g[m & ok]
        log("%s: %d puntos" % (nombre, len(s)))
        for _, r in s.iterrows():
            fuera = "FUERA del rango de las laderas" if (r.dIc < p10 or r.dIc > p90) else "dentro del rango"
            log("   %s %s (%s): ICESat-2 menos IGN %+.1f m  -> %s" % (r.fecha, r.haz, r.tipo, r.dIc, fuera))
    out = ruta_tp("Tp7", "05_Resultados", "04_Tablas", "E1_atl08_20m_cicatriz.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    g.drop(columns="geometry").to_csv(out, index=False, encoding="utf-8-sig")
    log("Tabla: %s" % out)
    try:
        dibujar(g, a, f, sesgo, Q, log)
    except Exception as e:                                      # noqa: BLE001
        log("AVISO: no se pudo dibujar la figura (%s)." % str(e)[:100])
    log("Lectura: un punto fuera del rango de las laderas sin evento es un INDICIO puntual, no un patron ni un volumen.")
    log.cerrar("responder la pregunta 8")


def dibujar(g, a, f, sesgo, Q, log):
    """Transectas de las trazas que cruzan la cicatriz o el deposito (a menos de 10 m)."""
    import geopandas as gpd
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import rasterio
    from rasterio.warp import transform as wtr
    from shapely.geometry import Point
    import logging
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    plt.rcParams["font.family"] = ["Times New Roman", "Liberation Serif", "DejaVu Serif"]
    cic = f[f.tipo == "cicatriz"].union_all(); dep = f[f.tipo == "deposito"].union_all()
    dN = float((a.N_ar16 - a.N_egm2008).median())             # EGM2008 -> SRVN16 para el GLO-30
    trazas = g[(g.d_cic <= 10) | (g.d_dep <= 10)][["fecha", "haz"]].drop_duplicates().values.tolist()
    if not trazas:
        log("Ninguna traza cruza las formas: no hay figura.")
        return
    src = {"IGN": rasterio.open(Q + "IGN_MDE_5m.tif"), "GLO": rasterio.open(Q + "CopernicusDEM30.tif")}

    def samp(k, X, Y):
        s = src[k]
        lon, lat = wtr(CRS, s.crs, list(X), list(Y))
        v = np.array([x[0] for x in s.sample(zip(lon, lat))], float)
        if s.nodata is not None and not np.isnan(s.nodata):
            v[v == s.nodata] = np.nan
        return v
    n = len(trazas)
    fig, axs = plt.subplots((n + 1) // 2, 2, figsize=(16, 4.8 * ((n + 1) // 2)), squeeze=False)
    for ax, (fe, hz) in zip(axs.flat, trazas):
        s = g[(g.fecha == fe) & (g.haz == hz)].copy()
        P = np.c_[s.geometry.x, s.geometry.y]
        v = np.linalg.svd(P - P.mean(0))[2][0]
        v = -v if v[1] < 0 else v
        t = (P - P.mean(0)) @ v
        k0 = int(np.argmin([Point(p).distance(cic.union(dep)) for p in P]))
        s["t"] = t - t[k0]
        s = s[(s.t > -350) & (s.t < 350)]
        tt = np.arange(-360, 360, 2)
        X = P.mean(0)[0] + (tt + t[k0]) * v[0]
        Y = P.mean(0)[1] + (tt + t[k0]) * v[1]
        ax.plot(tt, samp("IGN", X, Y), color="0.2", lw=1.4, label="IGN 5 m (2013, SRVN16)")
        ax.plot(tt, samp("GLO", X, Y) - dN, color="tab:orange", lw=1.3, label="GLO-30 pasado a SRVN16")
        ax.scatter(s.t, s.h_srvn16 - sesgo, s=28, c="tab:blue", edgecolor="k", lw=.4, zorder=5, label="ICESat-2 cada 20 m (sesgo restado)")
        for m, col, lab in ((np.array([cic.distance(Point(x, y)) < 1 for x, y in zip(X, Y)]), "orange", "cicatriz"),
                            (np.array([dep.distance(Point(x, y)) < 1 for x, y in zip(X, Y)]), "deepskyblue", "deposito")):
            if m.any():
                ax.axvspan(tt[m].min(), tt[m].max(), color=col, alpha=.3, label=lab)
        ax.set_title("%s/%s/%s, haz %s" % (fe[6:], fe[4:6], fe[:4], hz))
        ax.set_xlabel("distancia a lo largo de la traza, sur -> norte (m)")
        ax.set_ylabel("cota SRVN16 (m)")
        ax.grid(alpha=.3)
    axs.flat[0].legend(fontsize=9, loc="lower left")
    fig.tight_layout()
    out = ruta_tp("Tp7", "05_Resultados", "05_Graficos", "E1_icesat2_20m_transectas.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=150)
    log("Figura: %s" % out)


if __name__ == "__main__":
    main()
