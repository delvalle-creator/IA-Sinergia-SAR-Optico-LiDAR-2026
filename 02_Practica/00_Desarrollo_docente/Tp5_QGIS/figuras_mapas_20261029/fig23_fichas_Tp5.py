# Tp5, Figura 23: fichas de 400 m de 12 poligonos de entrenamiento, Sentinel-2 B12-B8A-B4 del 15/07 y del 13/10/2020;
# cuadrado amarillo = poligono de 100 m. Rehecha el 30/10/2026 con rotulos del tamano del texto.
# Uso: python fig23_fichas_Tp5.py <mapas_tp5.py> <S2_20200715.tif> <S2_20201013.tif> <entrenamiento_A1.gpkg> <salida.png>
import sys, importlib.util
mp, f1, f2, gp, out = sys.argv[1:6]
sys.argv = ['x', 'NINGUNA']
spec = importlib.util.spec_from_file_location('m', mp); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
import geopandas as gpd, matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
g = gpd.read_file(gp).set_index('id_sorteo')
ids = ['A000005', 'A000009', 'A000152', 'U013', 'U049', 'B000010', 'U031', 'U050', 'U008', 'U030', 'U056', 'U011']
CL = {1: 'alta', 2: 'baja', 3: 'no quemado', 4: 'agua'}
CM = 1 / 2.54
fig = plt.figure(figsize=(25 * CM, 12.6 * CM))
cw, ch = 0.108, 0.226; gx = 0.006; gp_ = 0.026
for k, i in enumerate(ids):
    r, c = divmod(k, 4)
    x, y = g.loc[i].geometry.centroid.x, g.loc[i].geometry.centroid.y
    ext = (x - 200, x + 200, y - 200, y + 200)
    x0 = 0.017 + c * (2 * cw + gx + gp_); y0 = 1 - (r + 1) * (ch + 0.085) + 0.02
    for j, (f, t) in enumerate(((f1, '15/07'), (f2, '13/10'))):
        ax = fig.add_axes([x0 + j * (cw + gx), y0, cw, ch])
        ax.imshow(m.s2(f, ext, 10), extent=ext, interpolation='nearest')
        ax.add_patch(Rectangle((x - 50, y - 50), 100, 100, fill=False, ec='yellow', lw=1.8))
        ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(t, fontsize=10, pad=2)
    fig.text(x0 + cw + gx / 2, y0 - 0.012, '%s: c%d %s' % (i, g.loc[i].codigo, CL[g.loc[i].codigo]), ha='center', va='top', fontsize=10.5)
fig.savefig(out, dpi=200); print(out)
