# -*- coding: utf-8 -*-
"""Describe la estructura y la cobertura de los granulos ATL24 de un sitio.
Uso: python diagnostico_atl24.py A2_IBICUY
Escribe LIDAR\\<SITIO>\\diagnostico_ATL24.txt"""
import glob, os, sys
import h5py
import numpy as np
from configuracion_comun import SITIOS, ORIGINALES

sitio = sys.argv[1] if len(sys.argv) > 1 else "A2_IBICUY"
lon0, lat0, lon1, lat1 = SITIOS[sitio]["bbox"]
carpeta = os.path.join(ORIGINALES, "LIDAR", sitio, "ATL24")
out = open(os.path.join(ORIGINALES, "LIDAR", sitio, "diagnostico_ATL24.txt"), "w", encoding="utf-8")
out.write("bbox sitio lon %.2f..%.2f lat %.2f..%.2f\n" % (lon0, lon1, lat0, lat1))
primero = True
for f in sorted(glob.glob(os.path.join(carpeta, "ATL24_*.h5"))):
    out.write("\n== %s\n" % os.path.basename(f))
    with h5py.File(f, "r") as h:
        out.write("grupos raiz: %s\n" % list(h.keys()))
        if primero:
            def ver(n, o):
                if isinstance(o, h5py.Dataset):
                    out.write("   %s %s %s\n" % (n, o.shape, o.dtype))
            h.visititems(ver)
            primero = False
        for haz in sorted(k for k in h.keys() if k.startswith("gt")):
            g = h[haz]
            if "lat_ph" not in g:
                out.write(" %s: sin lat_ph; contiene %s\n" % (haz, list(g.keys())[:15]))
                continue
            lat = g["lat_ph"][:]; lon = g["lon_ph"][:]
            m = (lat >= lat0) & (lat <= lat1) & (lon >= lon0) & (lon <= lon1)
            cl = g["class_ph"][:] if "class_ph" in g else np.array([])
            u, n = np.unique(cl, return_counts=True)
            out.write(" %s: %d fotones, lat %.3f..%.3f lon %.3f..%.3f, en sitio %d, clases %s\n"
                      % (haz, lat.size, np.nanmin(lat) if lat.size else 0, np.nanmax(lat) if lat.size else 0,
                         np.nanmin(lon) if lon.size else 0, np.nanmax(lon) if lon.size else 0,
                         int(m.sum()), dict(zip(u.tolist(), n.tolist()))))
out.close()
print("Listo: diagnostico_ATL24.txt")
