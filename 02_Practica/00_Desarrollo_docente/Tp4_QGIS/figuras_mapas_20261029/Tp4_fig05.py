"""Figura 5 del Tp4: polígono de suelo desnudo del aserradero y cantera sobre Esri World Imagery (render de QGIS 3.44.8)."""
import sys; sys.path.insert(0, '/mnt/user-data/outputs/tp3_mapas/scripts')  # com.py de las figuras del Tp3
from com import *
from PIL import Image
im = np.asarray(Image.open('/mnt/user-data/uploads/02_Practica/00_Desarrollo_docente/Tp4_QGIS/figuras_mapas_20261029/Tp4_fig05_esri_aserradero.png').convert('RGB'))
x0, x1, y0, y1 = 404450, 405570, 6534090, 6535210
fig, ax = plt.subplots(figsize=(6.0, 6.0))
ax.imshow(im, extent=[x0, x1, y0, y1])
ax.add_patch(Rectangle((404980, 6534620), 60, 60, fill=False, ec='yellow', lw=2.2))
ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
ax.xaxis.set_major_locator(MultipleLocator(250)); ax.yaxis.set_major_locator(MultipleLocator(250))
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: num(v / 1000, 2))); ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: num(v / 1000, 2)))
ax.set_xlabel('Este UTM 21 S (km)'); ax.set_ylabel('Norte UTM 21 S (km)')
escala_norte(fig, ax, 250, '250 m')
fig.savefig('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/hueco/t3f8/T4F05.png', dpi=250, bbox_inches='tight', pad_inches=0.06); print('ok')
