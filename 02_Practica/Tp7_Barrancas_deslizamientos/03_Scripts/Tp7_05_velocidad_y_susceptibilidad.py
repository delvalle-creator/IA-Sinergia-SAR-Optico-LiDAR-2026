# -*- coding: utf-8 -*-
"""
Tp7_05_velocidad_y_susceptibilidad.py   [AMPLIACION, FUERA DE LA EVALUACION]   Tp7, despues del paso 6
=====================================================================================================
Copia, para el alumno, de subsidencia_diamante.py del desarrollo del docente (22/10/2026), con el umbral
de hundimiento corregido (27/10/2026).

QUE HACE
  Recorta a Diamante la velocidad vertical que calcula el Tp10 (Tp10_05_velocidad_subsidencia.py: apilado
  de 120 interferogramas HyP3 de Sentinel-1, junio de 2025 a julio de 2026, 40 m) y arma un mapa
  HIPOTETICO de susceptibilidad a fisuras en viviendas dentro de la zona construida:
    - "cerca del borde": a 150 m o menos del borde de la barranca (talud > 30 % del IGN 5 m junto a la meseta);
    - "hundimiento": velocidad por debajo de (mediana del interior urbano - 2 sigma), con sigma = NMAD de la
      velocidad en el interior urbano (> 300 m del borde). ANTES se usaba -10 mm/ano fijo, que es del orden
      del error de la velocidad: la clase "alta" podia ser ruido.
  Clases: 1 baja (resto de la zona construida), 2 media (una condicion), 3 alta (las dos).

  La velocidad del Tp10 esta referida a la mediana de los pixeles persistentes de la zona construida de
  Parana-Diamante (referencia del Tp10), no a Diamante. Supone movimiento horizontal nulo, y en esta
  barranca el movimiento conocido es sobre todo horizontal: el mapa prioriza una recorrida, no da una
  probabilidad de dano.

ENTRADAS
  Tp10_Impacto_urbano/05_Resultados/02_Rasters/E_PARANA_DIAMANTE_velocidad_vertical.tif (correr antes el Tp10)
  02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/E1_DIAMANTE_BARRANCA_IGN_MDE_5m.tif

SALIDAS
  05_Resultados/02_Rasters/E1_susceptibilidad_fisuras_hipotetica.tif
  05_Resultados/04_Tablas/E1_velocidad_por_franja.csv
  05_Resultados/06_Control_calidad/Tp7_05_velocidad.log

USO
    python Tp7_05_velocidad_y_susceptibilidad.py
"""
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import COSMO_DIAMANTE, ruta_tp               # noqa: E402
from funciones_comunes import Bitacora                                # noqa: E402

# ------------------------------------------------------------ PARAMETROS
X0, X1, Y0, Y1 = 154300, 157400, 6444600, 6448050   # recorte de Diamante, EPSG:32721
PIXEL = 5.0
CRS = "EPSG:32721"
FRANJA = 150.0          # m desde el borde de la barranca
INTERIOR = 300.0        # m: el interior urbano empieza a esta distancia del borde
K_SIGMA = 2.0


def main():
    import geopandas as gpd
    import rasterio
    from rasterio.features import rasterize
    from rasterio.transform import from_origin
    from rasterio.warp import reproject, Resampling
    from scipy import ndimage as ndi

    log = Bitacora(ruta_tp("Tp7", "05_Resultados", "06_Control_calidad"), "Tp7_05_velocidad")
    V = ruta_tp("Tp10", "05_Resultados", "02_Rasters", "E_PARANA_DIAMANTE_velocidad_vertical.tif")
    if not os.path.exists(V):
        sys.exit("Falta %s: correr antes Tp10_05_velocidad_subsidencia.py (Tp10)." % V)
    T = from_origin(X0, Y1, PIXEL, PIXEL)
    sh = (int((Y1 - Y0) / PIXEL), int((X1 - X0) / PIXEL))

    def leer(path, banda=1, rs=Resampling.nearest, cero=False):
        o = np.full(sh, np.nan, "f4")
        with rasterio.open(path) as s:
            a = s.read(banda).astype("f4")
            if s.nodata is not None and not np.isnan(s.nodata):
                a[a == s.nodata] = np.nan
            if cero:
                a[a <= 0] = np.nan
            reproject(a, o, src_transform=s.transform, src_crs=s.crs, dst_transform=T, dst_crs=CRS, resampling=rs,
                      src_nodata=np.nan, dst_nodata=np.nan)
        return o
    vel = leer(V, 1)
    Q = ruta_tp("Tp7", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", "E1_DIAMANTE_BARRANCA_")
    ign = leer(Q + "IGN_MDE_5m.tif", rs=Resampling.bilinear)
    if os.path.exists(Q + "IGN_MDE_mosaico2018.tif"):
        ign = np.where(np.isfinite(ign), ign, leer(Q + "IGN_MDE_mosaico2018.tif", rs=Resampling.bilinear, cero=True))
    # borde de la barranca: talud > 30 % con meseta (> 40 m) a menos de 30 m y bajo (< 15 m) a menos de 250 m
    gy, gx = np.gradient(ndi.gaussian_filter(np.nan_to_num(ign, nan=np.nanmin(ign)), 2), PIXEL)
    pend = np.hypot(gx, gy) * 100
    meseta = ign > 40
    bajo = (ign < 15) | ~np.isfinite(ign)
    borde = (pend > 30) & (ign > 15) & (ndi.distance_transform_edt(~meseta) * PIXEL < 30) & (ndi.distance_transform_edt(~bajo) * PIXEL < 250)
    lab, n = ndi.label(borde)
    tam = ndi.sum(borde, lab, range(1, n + 1))
    borde = np.isin(lab, 1 + np.where(tam > 400)[0])
    dist = ndi.distance_transform_edt(~borde) * PIXEL
    urb = meseta & np.isfinite(vel)          # pixeles persistentes de la meseta: casi siempre construido
    v_int = vel[urb & (dist > INTERIOR)]
    med = float(np.nanmedian(v_int))
    sigma = float(1.4826 * np.nanmedian(np.abs(v_int - med)))
    umbral = med - K_SIGMA * sigma
    log("Interior urbano (> %.0f m del borde): mediana %.1f mm/ano, NMAD %.1f mm/ano." % (INTERIOR, med, sigma))
    log("Umbral de hundimiento = mediana - %.0f sigma = %.1f mm/ano (antes: -10 mm/ano fijo)." % (K_SIGMA, umbral))
    cerca = (dist <= FRANJA) & meseta
    hund = vel < umbral
    cls = np.zeros(sh, "u1")
    cls[urb] = 1
    cls[urb & (cerca | hund)] = 2
    cls[urb & cerca & hund] = 3
    filas = []
    gr = gpd.read_file(os.path.join(COSMO_DIAMANTE, "GRIETAS", "grietadte.shp")).to_crs(CRS)
    mg = rasterize([(gr.union_all().buffer(100), 1)], out_shape=sh, transform=T).astype(bool)
    for nom, m in (("franja <= 150 m del borde", cerca), ("interior > 300 m", meseta & (dist > INTERIOR)), ("a 100 m de la grieta", mg)):
        v = vel[m & np.isfinite(vel)]
        filas.append({"zona": nom, "pixeles_40m": round(v.size / 64, 0), "mediana_mm_ano": round(float(np.median(v)), 1),
                      "%_bajo_umbral": round(float(100 * np.mean(v < umbral)), 1), "%_bajo_-10": round(float(100 * np.mean(v < -10)), 1)})
        log("%-26s mediana %6.1f mm/ano; %4.0f %% por debajo del umbral" % (nom, filas[-1]["mediana_mm_ano"], filas[-1]["%_bajo_umbral"]))
    log("Superficie: alta %.1f ha, media %.1f ha, baja %.1f ha." % ((cls == 3).sum() * PIXEL ** 2 / 1e4, (cls == 2).sum() * PIXEL ** 2 / 1e4,
                                                                   (cls == 1).sum() * PIXEL ** 2 / 1e4))
    pd.DataFrame(filas).to_csv(ruta_tp("Tp7", "05_Resultados", "04_Tablas", "E1_velocidad_por_franja.csv"), index=False, encoding="utf-8-sig")
    out = ruta_tp("Tp7", "05_Resultados", "02_Rasters", "E1_susceptibilidad_fisuras_hipotetica.tif")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with rasterio.open(out, "w", driver="GTiff", height=sh[0], width=sh[1], count=1, dtype="uint8", crs=CRS, transform=T,
                       nodata=0, compress="deflate") as o:
        o.write(cls, 1)
        o.set_band_description(1, "0 sin dato, 1 baja, 2 media, 3 alta (hipotetica; umbral %.1f mm/ano)" % umbral)
        o.update_tags(FUENTE="Velocidad vertical del Tp10 (HyP3, 120 pares Sentinel-1, 2025-2026); IGN MDE 5 m",
                      PROCESO="Susceptibilidad HIPOTETICA: franja de %.0f m del borde y velocidad < %.1f mm/ano" % (FRANJA, umbral))
    log("Raster: %s" % out)
    log("Es una priorizacion exploratoria para recorrer, no una probabilidad de dano: se valida con inspeccion, GNSS y geotecnia.")
    log.cerrar()


if __name__ == "__main__":
    main()
