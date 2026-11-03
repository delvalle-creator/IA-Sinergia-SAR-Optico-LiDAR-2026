# -*- coding: utf-8 -*-
"""Corrimiento del ALOS-2 ScanSAR (16/11/2023) frente al SAOCOM 11/11/2023 (SNAP) y al Sentinel-1 RTC 16/11/2023."""
import os, sys, glob
import numpy as np
BASE = r"D:\CURSOS_CEREGEO_2026\02_Practica"
sys.path.insert(0, os.path.join(BASE, "00_COMUN"))
from funciones_comunes import grilla_sitio, leer_en_grilla, s1_rtc_mas_cercana, s1_rtc, jrc_ocurrencia  # noqa
from skimage.registration import phase_cross_correlation
g = grilla_sitio("B_CONCORDIA", 20.0)
Q = os.path.join(BASE, "Tp6_Inundaciones", "02_Subsets_SNAP_QGIS")
def db(x):
    x = np.asarray(x, "float64"); return np.where(x > 0, 10 * np.log10(np.where(x > 0, x, 1)), np.nan)
al = db(leer_en_grilla(os.path.join(Q, "ALOS2_gamma0", "QGIS_GeoTIFF", "B_CONCORDIA_ALOS2_L_20231116_WBD_gamma0_Gamma0_HH.tif"), g))
sa = db(leer_en_grilla(glob.glob(os.path.join(Q, "SAOCOM_gamma0", "QGIS_GeoTIFF", "*20231111_QP_gamma0_Gamma0_HH.tif"))[0], g))
s1 = db(s1_rtc(s1_rtc_mas_cercana("B_CONCORDIA", "2023-11-16", dias=1, grilla=g), "vv", g))
jrc, _ = jrc_ocurrencia("B_CONCORDIA", g)
def prep(a):
    b = np.where(np.isfinite(a), a, np.nanmedian(a)); return np.clip(b, -30, 0)
H, W = al.shape
for nombre, ref in (("SAOCOM 11/11 HH (SNAP)", sa), ("Sentinel-1 RTC 16/11 VV", s1), ("JRC ocurrencia (agua)", -jrc / 5.0)):
    print(nombre)
    for (f0, c0) in [(0, 0), (0, W // 2), (H // 2, 0), (H // 2, W // 2), (H // 4, W // 4)]:
        a = prep(al[f0:f0 + H // 2, c0:c0 + W // 2]); b = prep(ref[f0:f0 + H // 2, c0:c0 + W // 2]) if nombre[0] != "J" else np.nan_to_num(ref[f0:f0 + H // 2, c0:c0 + W // 2])
        if np.isfinite(a).mean() < 0.5: continue
        sh, err, _ = phase_cross_correlation(b, a, upsample_factor=10)
        print("   ventana fila %5d col %5d: mover el ALOS-2 %+.1f px en filas (sur +) y %+.1f px en columnas (este +) = %+.0f m, %+.0f m"
              % (f0, c0, sh[0], sh[1], sh[0] * 20, sh[1] * 20))
agua_perm = jrc >= 90
print("Agua permanente (JRC >= 90): %.0f ha; con HH ALOS-2 < -20 dB: %.1f %%; con VV S1 < -18 dB: %.1f %%; con HH SAOCOM < -20 dB: %.1f %%"
      % (agua_perm.sum() * 0.04, 100 * (al[agua_perm] < -20).mean(), 100 * (s1[agua_perm] < -18).mean(), 100 * (sa[agua_perm] < -20).mean()))
