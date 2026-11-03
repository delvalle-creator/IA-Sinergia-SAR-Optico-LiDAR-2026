# -*- coding: utf-8 -*-
"""Exporta el NISAR L del 18/09/2026 (traza 010 descendente) para el Tp2 (A2_IBICUY) con las mismas
funciones de armar_subsets.py: .dim, GeoTIFF con _metadatos.txt, RGB y metadatos originales.
No pisa nada: se detiene si el GeoTIFF ya existe. Desarrollo docente, 22/10/2026."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import armar_subsets as A

SITIO = "A2_IBICUY"
NOMBRE = "A2_IBICUY_NISAR_L_20260918"
cfg = {"patron": os.path.join("NISAR_DELTA", "BANDA_L_NASA", "NISAR_L2_PR_GCOV_031_010_D_105_2005_*_20260918T*.h5"),
       "banda": "LSAR", "etiqueta": "NISAR_L_20260918"}
sal = A.ruta_tp("Tp2", "02_Subsets_SNAP_QGIS")
c_dim, c_tif = os.path.join(sal, "SNAP_DIMAP"), os.path.join(sal, "QGIS_GeoTIFF")
c_rgb, c_meta = os.path.join(sal, "RGB_copol_cruzada_cociente"), os.path.join(sal, "Metadatos_originales")
for f in (os.path.join(c_tif, NOMBRE + ".tif"), os.path.join(c_dim, NOMBRE + ".dim")):
    if os.path.exists(f):
        sys.exit("Ya existe %s: no se pisa." % f)
p = A.leer_nisar_gcov(SITIO, cfg, NOMBRE)
print("%s: %d x %d px, bandas %s" % (NOMBRE, p.ancho, p.alto, ", ".join(b["nombre"] for b in p.bandas)))
print(".dim    :", A.escribir_dim(p, c_dim))
print("GeoTIFF :", A.escribir_geotiff(p, c_tif))
print("RGB     :", A.escribir_rgb(p, c_rgb))
A.copiar_meta(p, c_meta)
print("Metadatos originales copiados en", c_meta)
gpt = A.gpt_snap()
if gpt:
    d = os.path.join(c_dim, NOMBRE + ".dim")
    import rasterio
    from rasterio.crs import CRS
    from rasterio.warp import transform as tr
    cx, cy = p.transform * (p.ancho / 2.0, p.alto / 2.0)
    lo, la = tr(CRS.from_wkt(p.crs_wkt), "EPSG:4326", [cx], [cy])
    r = A.control_snap(gpt, [d], os.path.join(sal, "_control_snap_tmp"), (lo[0] - .01, la[0] - .01, lo[0] + .01, la[0] + .01))
    for k, v in r.items():
        print("Control SNAP:", os.path.basename(k), v)
