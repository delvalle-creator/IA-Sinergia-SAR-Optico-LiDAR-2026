# -*- coding: utf-8 -*-
r"""
alturas_lidar_egm2008.py - Cotas LiDAR sobre el geoide EGM2008 y comparacion con FABDEM y Copernicus DEM.

Toma las tablas que ya armo exportar_lidar.py (00_COMUN\\05_LiDAR_tablas\\<SITIO>\\<SITIO>_GEDI.csv y
_ATL08.csv) y les agrega, por disparo GEDI o segmento ATL08:

  elev_suelo_egm2008 / h_terreno_egm2008   cota del suelo LiDAR pasada de elipsoidal WGS 84 a EGM2008
                                           (la referencia vertical de FABDEM y de Copernicus DEM)
  fabdem_m                                 cota de FABDEM v1-2 en ese punto (EGM2008; sin bosque ni edificios)
  copdem_m                                 cota de Copernicus DEM GLO-30 en ese punto (EGM2008; superficie)
  dif_lidar_fabdem                         LiDAR - FABDEM (m)
  dif_lidar_copdem                         LiDAR - Copernicus DEM (m)

No relee los HDF5 de la NASA (eso lo hizo exportar_lidar.py): reescribe CSV, Excel y GeoPackage del sitio
con las columnas nuevas, agrega la explicacion al LEEME del sitio y copia la carpeta a cada practico
(02_Subsets_SNAP_QGIS\\LiDAR_<SITIO>), como exportar_lidar.py.

Geoides: la ondulacion N se interpola (bilineal) en las grillas del docente:
  EGM2008  G:\IA_APLICADA_HIDROGRAFIA_HIDROLOGIA_2026\PERSONAL\DTMs_DEMs\GEOIDES\EGM2008\egm08_25.gtx
  GEOIDE-Ar16 (IGN, SRVN16)  ...\GEOIDES\SRVN16\ar_ign_GEOIDE-Ar16.tif
(o las rutas de las variables CURSO_SAR_GEOIDE_EGM2008 y CURSO_SAR_GEOIDE_AR16). Cota = h elipsoidal - N.
Si no esta la grilla EGM2008, se usa alturas_a_egm2008() de funciones_lidar.py (PROJ, us_nga_egm08_25).

USO (Miniforge Prompt, entorno sar):
    cd /d D:\\CURSOS_CEREGEO_2026\\02_Practica\\00_COMUN
    python alturas_lidar_egm2008.py                      (todos los sitios con tablas)
    python alturas_lidar_egm2008.py --sitios C_FEDERAL
"""
import argparse
import glob
import os
import shutil
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from configuracion_comun import SITIOS, ORIGINALES, PRACTICA   # noqa: E402
import exportar_lidar as EL                                     # noqa: E402
from funciones_lidar import alturas_a_egm2008                   # noqa: E402

FABDEM = os.environ.get("CURSO_SAR_FABDEM",
                        os.path.join(os.path.expanduser("~"), ".snap", "auxdata", "dem", "FABDEM",
                                     "FABDEM_v1-2_Entre_Rios.tif"))
_GEOIDES = r"G:\IA_APLICADA_HIDROGRAFIA_HIDROLOGIA_2026\PERSONAL\DTMs_DEMs\GEOIDES"
GEOIDE_EGM2008 = os.environ.get("CURSO_SAR_GEOIDE_EGM2008", os.path.join(_GEOIDES, "EGM2008", "egm08_25.gtx"))
GEOIDE_AR16 = os.environ.get("CURSO_SAR_GEOIDE_AR16", os.path.join(_GEOIDES, "SRVN16", "ar_ign_GEOIDE-Ar16.tif"))
FUENTE_EGM2008 = ("NGA. Earth Gravitational Model 2008 (EGM2008), grilla de ondulacion de 2,5' (egm08_25.gtx). "
                  "https://earth-info.nga.mil")
FUENTE_AR16 = ("IGN Argentina. Modelo de geoide GEOIDE-Ar16, POSGAR 2007 (EPSG:5342) -> SRVN16 (EPSG:9255), "
               "CC BY 4.0. https://www.ign.gob.ar/NuestrasActividades/Geodesia/Geoide-Ar16")
FUENTE_FABDEM = ("Hawker, L. et al. (2022). A 30 m global map of elevation with forests and buildings removed. "
                 "Environ. Res. Lett. 17, 024016. https://doi.org/10.1088/1748-9326/ac4d4f. FABDEM v1-2, "
                 "Universidad de Bristol: https://data.bris.ac.uk/data/dataset/s5hqmjcdj8yo2ibzi9b4ew3sn "
                 "(licencia CC BY-NC-SA 4.0)")
FUENTE_COPDEM = ("ESA / Airbus. Copernicus DEM GLO-30 (Microsoft Planetary Computer). "
                 "https://planetarycomputer.microsoft.com/dataset/cop-dem-glo-30")

NUEVAS = {
    "GEDI": {
        "N_egm2008": ("m", "Ondulacion del geoide EGM2008 en el punto (interpolacion bilineal de egm08_25)"),
        "elev_suelo_egm2008": ("m", "elev_lowestmode - N_egm2008: cota del suelo sobre el geoide EGM2008"),
        "N_ar16": ("m", "Ondulacion del geoide argentino GEOIDE-Ar16 en el punto (interpolacion bilineal)"),
        "elev_suelo_srvn16": ("m", "elev_lowestmode - N_ar16: cota del suelo en el sistema vertical nacional SRVN16"),
        "fabdem_m": ("m", "FABDEM v1-2 en el punto (EGM2008; sin bosque ni edificios)"),
        "copdem_m": ("m", "Copernicus DEM GLO-30 en el punto (EGM2008; superficie con dosel y edificios)"),
        "dif_lidar_fabdem": ("m", "elev_suelo_egm2008 - fabdem_m"),
        "dif_lidar_copdem": ("m", "elev_suelo_egm2008 - copdem_m"),
    },
    "ATL08": {
        "N_egm2008": ("m", "Ondulacion del geoide EGM2008 en el punto (interpolacion bilineal de egm08_25)"),
        "h_terreno_egm2008": ("m", "h_te_best_fit - N_egm2008: cota del terreno sobre el geoide EGM2008"),
        "N_ar16": ("m", "Ondulacion del geoide argentino GEOIDE-Ar16 en el punto (interpolacion bilineal)"),
        "h_terreno_srvn16": ("m", "h_te_best_fit - N_ar16: cota del terreno en el sistema vertical nacional SRVN16"),
        "fabdem_m": ("m", "FABDEM v1-2 en el punto (EGM2008; sin bosque ni edificios)"),
        "copdem_m": ("m", "Copernicus DEM GLO-30 en el punto (EGM2008; superficie con dosel y edificios)"),
        "dif_lidar_fabdem": ("m", "h_terreno_egm2008 - fabdem_m"),
        "dif_lidar_copdem": ("m", "h_terreno_egm2008 - copdem_m"),
    },
}
ELIPS = {"GEDI": ("elev_suelo_elips", "elev_suelo_egm2008", "elev_suelo_srvn16"),
         "ATL08": ("h_terreno_elips", "h_terreno_egm2008", "h_terreno_srvn16")}


def ondulacion(ruta, lon, lat):
    """Ondulacion del geoide N (m) por interpolacion bilineal de una grilla en grados
    (GTX de EGM2008 o GeoTIFF de GEOIDE-Ar16; nodos en los centros de celda)."""
    import rasterio
    from rasterio.windows import Window

    with rasterio.open(ruta) as s:
        t = s.transform
        x0, y0 = t.c + t.a / 2.0, t.f + t.e / 2.0          # centro del primer nodo
        fx = (lon - x0) / t.a
        fy = (lat - y0) / t.e
        c0, c1 = int(np.floor(np.nanmin(fx))) - 1, int(np.ceil(np.nanmax(fx))) + 2
        f0, f1 = int(np.floor(np.nanmin(fy))) - 1, int(np.ceil(np.nanmax(fy))) + 2
        c0, f0 = max(c0, 0), max(f0, 0)
        c1, f1 = min(c1, s.width), min(f1, s.height)
        g = s.read(1, window=Window(c0, f0, c1 - c0, f1 - f0)).astype("float64")
        if s.nodata is not None:
            g[g == s.nodata] = np.nan
    fx, fy = fx - c0, fy - f0
    i, j = np.floor(fy).astype(int), np.floor(fx).astype(int)
    ok = (i >= 0) & (j >= 0) & (i + 1 < g.shape[0]) & (j + 1 < g.shape[1])
    out = np.full(len(lon), np.nan)
    di, dj = fy[ok] - i[ok], fx[ok] - j[ok]
    ii, jj = i[ok], j[ok]
    out[ok] = (g[ii, jj] * (1 - di) * (1 - dj) + g[ii, jj + 1] * (1 - di) * dj
               + g[ii + 1, jj] * di * (1 - dj) + g[ii + 1, jj + 1] * di * dj)
    return out


def muestrear(rutas, lon, lat):
    """Valor del raster (EPSG:4326) en cada punto, leyendo solo la ventana de los puntos."""
    import rasterio
    from rasterio.windows import from_bounds

    out = np.full(len(lon), np.nan)
    if len(lon) == 0:
        return out
    for r in rutas:
        with rasterio.open(r) as s:
            if s.crs.to_epsg() != 4326:
                raise ValueError("%s no esta en EPSG:4326" % r)
            x0, x1 = np.nanmin(lon), np.nanmax(lon)
            y0, y1 = np.nanmin(lat), np.nanmax(lat)
            w = from_bounds(x0, y0, x1, y1, transform=s.transform).round_offsets().round_lengths()
            w = w.intersection(rasterio.windows.Window(0, 0, s.width, s.height))
            if w.width <= 0 or w.height <= 0:
                continue
            w = rasterio.windows.Window(w.col_off, w.row_off, w.width + 1, w.height + 1).intersection(
                rasterio.windows.Window(0, 0, s.width, s.height))
            a = s.read(1, window=w).astype("float64")
            if s.nodata is not None:
                a[a == s.nodata] = np.nan
            t = s.window_transform(w)
            col = np.floor((lon - t.c) / t.a).astype(int)
            fil = np.floor((lat - t.f) / t.e).astype(int)
            ok = (col >= 0) & (col < a.shape[1]) & (fil >= 0) & (fil < a.shape[0]) & np.isnan(out)
            out[ok] = a[fil[ok], col[ok]]
    return out


def completar(t, k, sitio):
    lon, lat = t["lon"].to_numpy(float), t["lat"].to_numpy(float)
    ce, cg, ca = ELIPS[k]
    h = t[ce].to_numpy(float)
    if os.path.exists(GEOIDE_EGM2008):
        n_egm = ondulacion(GEOIDE_EGM2008, lon, lat)
    else:                                            # sin la grilla propia: PROJ (us_nga_egm08_25)
        n_egm = np.full(len(h), np.nan)
        ok = np.isfinite(h) & np.isfinite(lon) & np.isfinite(lat)
        if ok.any():
            n_egm[ok] = h[ok] - alturas_a_egm2008(lon[ok], lat[ok], h[ok])
    t["N_egm2008"] = n_egm
    t[cg] = h - n_egm
    if os.path.exists(GEOIDE_AR16):
        t["N_ar16"] = ondulacion(GEOIDE_AR16, lon, lat)
        t[ca] = h - t["N_ar16"].to_numpy(float)
    t["fabdem_m"] = muestrear([FABDEM], lon, lat)
    cop = sorted(glob.glob(os.path.join(ORIGINALES, "PLANETARY", sitio, "cop-dem-glo-30", "*", "data.tif")))
    t["copdem_m"] = muestrear(cop, lon, lat) if cop else np.nan
    t["dif_lidar_fabdem"] = t[cg] - t["fabdem_m"]
    t["dif_lidar_copdem"] = t[cg] - t["copdem_m"]
    return t


def resumen(t, k):
    valido = "valido_L2A" if k == "GEDI" else "terreno_valido"
    v = t[t[valido] == True] if valido in t else t           # noqa: E712
    L = []
    for c in ("dif_lidar_fabdem", "dif_lidar_copdem"):
        x = v[c].dropna()
        if len(x):
            L.append("    %-18s n = %d  mediana %+.2f m  media %+.2f m  desvio %.2f m  EMC %.2f m"
                     % (c, len(x), x.median(), x.mean(), x.std(), float(np.sqrt((x ** 2).mean()))))
    return L, len(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitios", nargs="*", default=[])
    ap.add_argument("--sin_copiar", action="store_true")
    a = ap.parse_args()
    if not os.path.exists(FABDEM):
        sys.exit("No esta FABDEM en %s (o indique la ruta con la variable CURSO_SAR_FABDEM)" % FABDEM)
    for k, cols in NUEVAS.items():
        EL.COLUMNAS[k].update(cols)
    sitios = a.sitios or sorted(d for d in os.listdir(EL.SALIDA) if d in SITIOS)
    for sitio in sitios:
        d = os.path.join(EL.SALIDA, sitio)
        tablas = {}
        for k in ("GEDI", "ATL08", "ATL13"):
            r = os.path.join(d, "%s_%s.csv" % (sitio, k))
            if os.path.exists(r):
                tablas[k] = pd.read_csv(r, encoding="utf-8-sig", dtype={"shot_number": str}, low_memory=False)
        if not tablas:
            continue
        EL.log("==== %s" % sitio)
        extra = ["COTAS SOBRE EL GEOIDE EGM2008 Y COMPARACION CON MDE (alturas_lidar_egm2008.py)",
                 "  Geoide EGM2008: " + FUENTE_EGM2008 + (" [%s]" % GEOIDE_EGM2008 if os.path.exists(GEOIDE_EGM2008)
                                                          else " [grilla de PROJ us_nga_egm08_25]"),
                 "  Geoide argentino: " + FUENTE_AR16 + (" [%s]" % GEOIDE_AR16 if os.path.exists(GEOIDE_AR16)
                                                         else " [no encontrado: sin columnas SRVN16]"),
                 "  Cota = altura elipsoidal - N. Las alturas LiDAR son WGS 84 y GEOIDE-Ar16 se refiere a POSGAR 2007"
                 " (GRS80): la diferencia entre ambos marcos es de centimetros y no se corrige.",
                 "  FABDEM: " + FUENTE_FABDEM, "  Copernicus DEM: " + FUENTE_COPDEM,
                 "  Diferencias LiDAR - MDE en los puntos validos (L2A valido en GEDI; terreno valido en ATL08):"]
        for k in ("GEDI", "ATL08"):
            if k in tablas:
                tablas[k] = completar(tablas[k], k, sitio)
                L, n = resumen(tablas[k], k)
                EL.log("  %s: %d puntos (%d validos)" % (k, len(tablas[k]), n))
                for x in L:
                    EL.log(x)
                extra += ["  %s (%d puntos %s):" % (k, n, "con terreno valido" if k == "ATL08" else "validos L2A")] + L
        r_leeme = os.path.join(d, "%s_LiDAR_LEEME.txt" % sitio)
        previo = open(r_leeme, encoding="utf-8-sig").read() if os.path.exists(r_leeme) else ""
        previo = previo.split("\nCOTAS SOBRE EL GEOIDE EGM2008")[0].rstrip("\n")
        extra += ["", "  Columnas nuevas:"] + ["    %-20s %-4s %s" % (c, u, desc) for k in NUEVAS if k in tablas
                                              for c, (u, desc) in NUEVAS[k].items()]
        leeme = previo + "\n\n" + "\n".join(extra) + "\n"
        with open(os.path.join(d, "%s_LiDAR_LEEME.txt" % sitio), "w", encoding="utf-8-sig") as fh:
            fh.write(leeme)
        for k, t in tablas.items():
            t.to_csv(os.path.join(d, "%s_%s.csv" % (sitio, k)), index=False, encoding="utf-8-sig")
        EL.log("  CSV listos")
        EL.escribir_gpkg(os.path.join(d, "%s_LiDAR.gpkg" % sitio), tablas, leeme)
        EL.log("  GeoPackage listo")
        EL.escribir_xlsx(os.path.join(d, "%s_LiDAR.xlsx" % sitio), sitio, tablas, leeme)
        EL.log("  Excel listo")
        if not a.sin_copiar:
            for tp in SITIOS[sitio].get("practicos", []):
                dirs = glob.glob(os.path.join(PRACTICA, tp + "_*"))
                if not dirs:
                    continue
                dest = os.path.join(dirs[0], "02_Subsets_SNAP_QGIS", "LiDAR_%s" % sitio)
                if os.path.isdir(dest):
                    shutil.rmtree(dest)
                shutil.copytree(d, dest)
                EL.log("  copiado a %s" % os.path.relpath(dest, PRACTICA))
    EL.log("Terminado.")


if __name__ == "__main__":
    main()
