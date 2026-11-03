# Tp6, Figura 4: detalle de 14 x 14 km de Concordia el 04/11/2023: Sentinel-2 B11-B8A-B4 (a), Sentinel-1 RGB
# VV-VH-VV/VH (b) y Sentinel-2 color natural (c); coordenadas UTM 21S, escala horizontal al costado y norte arriba a la
# derecha. 30/10/2026.  Uso: python mapas_tp6_f4.py <mapas_tp6_f2_f3.py> <S2.tif> <S1_20231104_RGB.tif> <salida.png> x0 y0
import sys, importlib.util, numpy as np, rasterio
from rasterio.windows import from_bounds
mp, s2, s1, out, x0, y0 = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5]), float(sys.argv[6])
src = open(mp).read(); src = src[:src.index('a, e = leer(s2')]
ns = {}; sys_argv = sys.argv; sys.argv = ['x', '', '', '', '', '']; exec(src, ns); sys.argv = sys_argv
E = (x0, x0 + 14000, y0, y0 + 14000)
def recorte(f, bands):
    r = rasterio.open(f); w = from_bounds(E[0], E[2], E[1], E[3], r.transform)
    return r.read(bands, window=w).astype('f4')
a = ns['estirar'](recorte(s2, [9, 8, 3])); c = ns['estirar'](recorte(s2, [3, 2, 1]))
b = recorte(s1, [1, 2, 3]); b = np.clip(np.moveaxis(b / 255., 0, -1), 0, 1)
ns['F'] = 1
fig = ns['figura']([(a, E), (b, E), (c, E)], ['(a) Sentinel-2, B11, B8A, B4', '(b) Sentinel-1, VV, VH, VV/VH', '(c) Sentinel-2, color natural'], 25.4, 11.0, out, step=4000, Lm=4000, xt=[398000, 402000, 406000], yt=[6522000, 6526000, 6530000])
