"""Figura 4 del Tp4: polígonos urbanos sobre el Pléiades Neo de CONAE (render de QGIS 3.44.8, 2,47 m/píxel)."""
import sys; sys.path.insert(0, '/mnt/user-data/outputs/tp3_mapas/scripts')  # com.py de las figuras del Tp3
from com import *
from PIL import Image
im = np.asarray(Image.open('/mnt/user-data/uploads/02_Practica/00_Desarrollo_docente/Tp4_QGIS/figuras_mapas_20261029/Tp4_fig04_pleiades_urbanos.png').convert('RGB'))
x0, x1, y0, y1 = 403427.88, 409852.12, 6525090.0, 6528270.0
H, W = im.shape[:2]; px = (x1 - x0) / W
xc = 407650; c = int((xc - x0) / px)
im = im[:, :c]
fig, ax = plt.subplots(figsize=(8.6, 6.2))
ax.imshow(im, extent=[x0, xc, y0, y1])
ax.set_xlim(x0, xc); ax.set_ylim(y0, y1)
ejes_utm(ax, paso_km=1)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: num(v / 1000, 0)))
escala_norte(fig, ax, 1000, '1 km')
OUT2 = '/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/hueco/t3f8/'
fig.savefig(OUT2 + 'T4F04.png', dpi=250, bbox_inches='tight', pad_inches=0.06); print('ok')
