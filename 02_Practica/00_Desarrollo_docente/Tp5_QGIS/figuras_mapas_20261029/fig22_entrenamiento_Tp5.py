# Tp5, Figura 22: poligonos de entrenamiento sorteados (entrenamiento_A1.gpkg) sobre Sentinel-2 B12-B8A-B4:
# (a) todo el sitio el 13/10/2020 con el recuadro del detalle; (b) y (c) detalle de 5 km el 15/07 y el 13/10.
# Rehecha el 30/10/2026: letra del tamano del texto, escala y norte fuera del mapa, poligonos visibles en el detalle.
# Uso: python fig22_entrenamiento_Tp5.py <mapas_tp5.py> <S2_20200715.tif> <S2_20201013.tif> <entrenamiento_A1.gpkg> <salida.png>
import sys, importlib.util
mp, f1, f2, gp, out = sys.argv[1:6]
sys.argv = ['x', 'NINGUNA']
spec = importlib.util.spec_from_file_location('m', mp); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
import numpy as np, geopandas as gpd, matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
SIT = m.SITIO; DET = (224000, 229000, 6314200, 6319200)
COL = {1: '#7f0000', 2: '#f4a261', 3: '#b5e48c', 4: '#1f78b4'}
NOM = {1: '1 severidad alta', 2: '2 severidad baja', 3: '3 no quemado', 4: '4 agua'}
g = gpd.read_file(gp)
CM = m.CM; W, H = 25.4, 12.4
fig = plt.figure(figsize=(W * CM, H * CM))
bot = 3.0 / H; top = 0.75 / H; ph = 1 - bot - top
asp_s = (SIT[3] - SIT[2]) / (SIT[1] - SIT[0])
L = 1.9; gap = 0.5; R = 1.5
hcm = min(ph * H, (W - L - 2 * gap - R) / (1 / asp_s + 2)); wa = hcm / asp_s; wd = hcm
H = hcm + 3.0 + 0.75; fig.set_size_inches(W * CM, H * CM); bot = 3.0 / H; ph = hcm / H
x0 = L
axa = fig.add_axes([x0 / W, bot, wa / W, ph]); xb = x0 + wa + gap
axb = fig.add_axes([xb / W, bot, wd / W, ph]); axc = fig.add_axes([(xb + wd + gap) / W, bot, wd / W, ph])
fig._geo = dict(W=W, H=H, bot=bot * H, bottom_extra=0.85, pw=wa)
def poligonos(ax, lw):
    for c in (1, 2, 3, 4):
        s = g[g.codigo == c]
        if len(s):
            s.boundary.plot(ax=ax, color='white', linewidth=lw + 1.6)
            s.boundary.plot(ax=ax, color=COL[c], linewidth=lw)
def marco(ax, ext, k, t, ticks):
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect('equal')
    ax.set_xticks(ticks[0]); ax.set_yticks(ticks[1])
    ax.xaxis.set_major_formatter(m.miles); ax.yaxis.set_major_formatter(m.miles)
    ax.tick_params(labelsize=9.5, length=3)
    for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    if k: ax.set_yticklabels([]); ax.set_ylabel('')
    else: ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10, labelpad=2)
    ax.set_xlabel('Este, UTM 21S (m)', fontsize=10, labelpad=2); ax.set_title(t, fontsize=11, pad=4)
axa.imshow(m.s2(f2), extent=SIT, interpolation='nearest'); poligonos(axa, 1.0)
axa.add_patch(Rectangle((DET[0], DET[2]), DET[1] - DET[0], DET[3] - DET[2], fill=False, ec='yellow', lw=2))
marco(axa, SIT, 0, '(a) Sitio, S2 13/10/2020', ([230000, 240000], [6310000, 6320000, 6330000]))
for k, (ax, f, t) in enumerate(((axb, f1, '(b) Detalle, S2 15/07/2020'), (axc, f2, '(c) Detalle, S2 13/10/2020'))):
    ax.imshow(m.s2(f, DET, 10), extent=DET, interpolation='nearest'); poligonos(ax, 2.2)
    marco(ax, DET, 1, t, ([225000, 227000], [6315000, 6317000, 6319000]))
    for s in ax.spines.values(): s.set_edgecolor('yellow'); s.set_linewidth(2)
# escala del sitio bajo (a) y del detalle bajo (b); norte arriba a la derecha
m.escala_norte(fig, axa, 5000, '5 km', axn=axc)
bb = axb.get_position(); frac = 1000 / (DET[1] - DET[0]) * bb.width
y = (0.85 + 0.25) / H; h = 0.18 / H
sa = fig.add_axes([bb.x0, y, frac, h]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
fig.text(bb.x0, y + h + 0.08 / H, '0', ha='center', va='bottom', fontsize=10)
fig.text(bb.x0 + frac, y + h + 0.08 / H, '1 km', ha='center', va='bottom', fontsize=10)
hs = [Patch(facecolor='none', edgecolor=COL[c], lw=2, label=NOM[c]) for c in (1, 2, 3, 4)]
hs.append(Patch(facecolor='none', edgecolor='yellow', lw=2, label='recuadro del detalle'))
fig.legend(handles=hs, loc='upper center', bbox_to_anchor=(0.5, 0.75 / H), ncol=5, frameon=False, fontsize=10.5, handlelength=1.6, columnspacing=1.4)
fig.savefig(out, dpi=200); print(out)
dentro = g[(g.centroid.x > DET[0]) & (g.centroid.x < DET[1]) & (g.centroid.y > DET[2]) & (g.centroid.y < DET[3])]
print('en el detalle:', dentro.codigo.value_counts().to_dict())
