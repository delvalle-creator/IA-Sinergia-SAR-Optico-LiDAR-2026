"""Figura 16 del Desarrollo del Tp3 (antes fig15.py): mismo contenido, escala y norte fuera del mapa."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp3/sc')
from com import *
import pandas as pd
cap, T = cubo()
rgb = np.nan_to_num(np.dstack([st(cap['OPT_S2_B04']), st(cap['OPT_S2_B03']), st(cap['OPT_S2_B02'])]), nan=1)
H, Wd = rgb.shape[:2]; ext = [T.c, T.c + Wd * 20, T.f - H * 20, T.f]
t = pd.read_csv(W + '04_Tablas_de_trabajo/A2_IBICUY_huellas_con_cubo.csv', encoding='utf-8-sig', low_memory=False)
g = t[t.producto == 'gedi_l2a']; a = t[t.producto == 'atl08']
fig = plt.figure(figsize=(8.7, 5.75))
ax = fig.add_axes([0.085, 0.2, 0.42, 0.72]); ax.imshow(rgb, extent=ext)
clases = [(0, 3, '#ffffb2', '< 3 m'), (3, 5, '#fecc5c', '3–5 m'), (5, 10, '#fd8d3c', '5–10 m'), (10, 1e9, '#e31a1c', '10 m o más')]
gp = g[g.plausible == 1]; hs = []
for lo, hi, c, lab in clases:
    s = gp[(gp.rh98 >= lo) & (gp.rh98 < hi)]
    hs.append(ax.scatter(s.x, s.y, s=1.4 if lo < 3 else 3.5, c=c, lw=0, label='GEDI rh98 %s (%s)' % (lab, num(len(s))), zorder=3 if lo < 3 else 4))
hs.append(ax.scatter(a.x, a.y, s=1.4, c='#00bcd4', lw=0, label='ICESat-2 ATL08 (%s)' % num(len(a)), zorder=3))
np_ = g[g.plausible == 0]
hs.append(ax.scatter(np_.x, np_.y, s=10, marker='x', c='#7b1fa2', lw=0.7, label='GEDI no plausible (%s)' % num(len(np_)), zorder=5))
ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ejes_utm(ax)
ax.set_title('(a) Huellas válidas sobre Sentinel-2 (16/09/2026)')
ax2 = fig.add_axes([0.66, 0.53, 0.33, 0.39])
yy = range(2019, 2027)
c1 = [(g.fecha_lidar.str[:4].astype(int) == y).sum() for y in yy]; c2 = [(a.fecha_lidar.str[:4].astype(int) == y).sum() for y in yy]
x = np.arange(len(yy)); ax2.bar(x - 0.2, c1, 0.4, color='#e31a1c', label='GEDI L2A'); ax2.bar(x + 0.2, c2, 0.4, color='#00bcd4', label='ICESat-2 ATL08')
ax2.set_xticks(x); ax2.set_xticklabels([str(y)[2:] if False else str(y) for y in yy], rotation=90); ax2.set_ylabel('Huellas válidas'); ax2.set_xlabel('Año de la huella')
ax2.yaxis.set_major_formatter(fmt(0)); ax2.grid(axis='y', alpha=.3)
ax2.set_title('(b) Huellas válidas por año')
escala_norte(fig, ax, 5000, '5 km')
fig.canvas.draw(); tb = ax2.get_tightbbox(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
l2 = fig.legend(*ax2.get_legend_handles_labels(), loc='upper left', bbox_to_anchor=(0.6, tb.y0 - 0.01), ncol=2, frameon=False, fontsize=10.5)
fig.canvas.draw(); lb = l2.get_window_extent().transformed(fig.transFigure.inverted())
fig.legend(handles=hs, title='Huellas en (a)', loc='upper left', bbox_to_anchor=(0.6, lb.y0 - 0.01), ncol=1, markerscale=4, frameon=False, fontsize=10.5, title_fontsize=10.5, alignment='left')
guardar(fig, 'F16.png')
print('ok', len(gp), len(np_))
