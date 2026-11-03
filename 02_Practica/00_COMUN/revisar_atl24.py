# -*- coding: utf-8 -*-
"""Revisa si los granulos ATL24 bajados de un sitio traen fotones de fondo (batimetria).

Uso (Miniforge Prompt, entorno sar, en la carpeta 00_COMUN):
    python revisar_atl24.py A2_IBICUY

Clases de class_ph en ATL24: 40 = fondo (batimetria), 41 = superficie del agua,
1 = sin clasificar. Solo se cuentan los fotones dentro del recuadro del sitio.
Escribe LIDAR\\<SITIO>\\revision_ATL24.csv y un resumen en pantalla.
"""
import glob
import os
import sys

import h5py
import numpy as np
import pandas as pd

from configuracion_comun import SITIOS, ORIGINALES

sitio = sys.argv[1] if len(sys.argv) > 1 else "A2_IBICUY"
lon0, lat0, lon1, lat1 = SITIOS[sitio]["bbox"]
carpeta = os.path.join(ORIGINALES, "LIDAR", sitio, "ATL24")
filas = []
for f in sorted(glob.glob(os.path.join(carpeta, "ATL24_*.h5"))):
    with h5py.File(f, "r") as h:
        for haz in sorted(k for k in h.keys() if k.startswith("gt")):
            g = h[haz]
            if not all(v in g for v in ("lat_ph", "lon_ph", "class_ph")):
                continue
            lat = g["lat_ph"][:]
            lon = g["lon_ph"][:]
            m = (lat >= lat0) & (lat <= lat1) & (lon >= lon0) & (lon <= lon1)
            if not m.any():
                continue
            c = g["class_ph"][:][m]
            fondo = c == 40
            fila = {"granulo": os.path.basename(f), "haz": haz, "fotones_sitio": int(m.sum()),
                    "superficie_41": int((c == 41).sum()), "fondo_40": int(fondo.sum())}
            if "low_confidence_flag" in g:
                fila["fondo_40_confiable"] = int((fondo & (g["low_confidence_flag"][:][m] == 0)).sum())
            if fondo.any() and "ortho_h" in g and "surface_h" in g:
                prof = g["surface_h"][:][m][fondo] - g["ortho_h"][:][m][fondo]
                fila["prof_mediana_m"] = round(float(np.median(prof)), 2)
                fila["prof_max_m"] = round(float(np.max(prof)), 2)
            filas.append(fila)
t = pd.DataFrame(filas)
salida = os.path.join(ORIGINALES, "LIDAR", sitio, "revision_ATL24.csv")
t.to_csv(salida, index=False, encoding="utf-8-sig")
print("Granulos revisados: %d" % len(glob.glob(os.path.join(carpeta, "ATL24_*.h5"))))
if t.empty:
    print("Ningun foton ATL24 cae dentro del sitio.")
else:
    print("Haces con fotones en el sitio: %d" % len(t))
    print("Fotones en el sitio: %d; superficie: %d; fondo: %d"
          % (t.fotones_sitio.sum(), t.superficie_41.sum(), t.fondo_40.sum()))
print("Tabla: %s" % salida)
