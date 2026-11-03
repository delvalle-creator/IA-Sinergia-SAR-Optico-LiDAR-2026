"""Figura 11 del Tp4: playa del aserradero y cantera con sus 5 puntos, Esri y Google (renders de QGIS 3.44.8)."""
import sys; sys.path.insert(0, '/mnt/user-data/outputs/tp3_mapas/scripts')
from com import *
from PIL import Image
import matplotlib.patheffects as pe
S = '/mnt/user-data/uploads/02_Practica/00_Desarrollo_docente/Tp4_QGIS/figuras_mapas_20261029/'
E = [404890, 405130, 6534560, 6534740]
P = [(13, 404990, 6534670), (29, 405010, 6534630), (54, 405030, 6534630), (59, 405010, 6534670), (67, 404990, 6534630)]
fig, axs = plt.subplots(1, 2, figsize=(9.3, 3.9)); fig.subplots_adjust(left=0.085, right=0.955, top=0.92, bottom=0.17, wspace=0.08)
for a, (f, t) in zip(axs, (('esri', 'a) Esri World Imagery'), ('google', 'b) Google Satellite'))):
    a.imshow(np.asarray(Image.open(S + 'Tp4_fig11_%s.png' % f).convert('RGB')), extent=E, interpolation='bilinear')
    a.add_patch(Rectangle((404980, 6534620), 60, 60, fill=False, ec='#ffe600', lw=2, ls='--'))
    for i, x, y in P:
        a.add_patch(Rectangle((x - 10, y - 10), 20, 20, fill=False, ec='#ffe600', lw=1.4))
        a.text(x, y, str(i), ha='center', va='center', fontsize=10.5, color='black', fontweight='bold',
               path_effects=[pe.withStroke(linewidth=2.5, foreground='#ffe600')])
    a.set_xlim(E[0], E[1]); a.set_ylim(E[2], E[3]); a.set_title(t, loc='left')
    a.xaxis.set_major_locator(MultipleLocator(100)); a.yaxis.set_major_locator(MultipleLocator(50))
    a.xaxis.set_major_formatter(FuncFormatter(lambda v, p: num(v / 1000, 2))); a.yaxis.set_major_formatter(FuncFormatter(lambda v, p: num(v / 1000, 2)))
    a.set_xlabel('Este UTM 21 S (km)')
axs[0].set_ylabel('Norte UTM 21 S (km)'); axs[1].set_yticklabels([])
escala_norte(fig, axs[0], 50, '50 m', axn=axs[1])
fig.savefig('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/hueco/t3f8/T4F11.png', dpi=250, bbox_inches='tight', pad_inches=0.06); print('ok')
