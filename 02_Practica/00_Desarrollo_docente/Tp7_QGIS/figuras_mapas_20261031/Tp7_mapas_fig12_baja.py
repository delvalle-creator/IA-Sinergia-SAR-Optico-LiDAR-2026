# Tp7 Figura 12 baja (31/10/2026): dos mapas con la leyenda al costado, al tamano final
import sys; sys.path.insert(0, '.')
from comun import *
from matplotlib.colors import ListedColormap, BoundaryNorm
ph = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
E = BAR; asp = (E[3]-E[2])/(E[1]-E[0]); pw = ph/asp
L, T, B = 1.45, 0.6, 1.05
la, lb, g = 5.0, 4.3, 0.25
W = L + pw + g + la + 0.5 + pw + g + lb
H = T + ph + B
fig = plt.figure(figsize=(W*CM, H*CM)); y0 = B/H
xa = L; xb = L + pw + g + la + 0.5
a1 = fig.add_axes([xa/W, y0, pw/W, ph/H]); a2 = fig.add_axes([xb/W, y0, pw/W, ph/H])
d1 = warp(RAS + 'E1_deformacion_confirmada.tif', 1, E, 10, rs=Resampling.nearest)
d2 = warp(RAS + 'E1_deformacion_confirmada.tif', 2, E, 10, rs=Resampling.nearest)
c1 = ListedColormap(['#2166ac', '#e6e6e6', '#b2182b']); a1.imshow(d1, extent=E, cmap=c1, norm=BoundaryNorm([-1.5, -.5, .5, 1.5], 3), interpolation='nearest')
c2 = ListedColormap(['#fff5bf', '#fdbf4f', '#d95f0e']); a2.imshow(d2, extent=E, cmap=c2, norm=BoundaryNorm([-.5, .5, 1.5, 2.5], 3), interpolation='nearest')
for k, (ax, t) in enumerate(zip((a1, a2), ['(a) Deformación confirmada', '(b) Bandas que votaron'])):
    capas(ax, ladera='black', anillo=True, lw=1.8); marco(ax, E, 1000, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
    ax.set_yticks([6445500, 6447000])
for l in a1.get_yticklabels(): l.set_rotation(90); l.set_va('center')
a1.set_ylabel('Norte (m), EPSG:32721')
P = lambda c, l, e='none': Patch(facecolor=c, edgecolor=e, lw=0.8, label=l)
top = (H - T)/H
fig.legend(handles=[P('#b2182b', '+1: las dos detectan\nel movimiento esperado'), P('#2166ac', '−1: las dos, el contrario'),
                    P('#e6e6e6', '0: decidido, sin\ndeformación', '0.5'), P('white', 'sin decidir (falta\nuna banda)', '0.5')],
           loc='upper left', bbox_to_anchor=((xa + pw + g)/W, top), frameon=False, fontsize=10, handlelength=1.5, labelspacing=0.5, borderaxespad=0)
fig.legend(handles=[P('#fff5bf', '0 bandas', '0.5'), P('#fdbf4f', '1 banda'), P('#d95f0e', '2 bandas')],
           loc='upper left', bbox_to_anchor=((xb + pw + g)/W, top - 0.9/H), frameon=False, fontsize=10, handlelength=1.5, borderaxespad=0)
fig.legend(handles=[lin('black', 'ladera relevada\nen 2018'), lin('cyan', 'anillo de referencia'), lin('red', 'grieta relevada', 3.5)],
           loc='lower left', bbox_to_anchor=((xb + pw + g)/W, y0 + 0.55/H), frameon=False, fontsize=10, handlelength=1.6, borderaxespad=0)
# norte arriba a la derecha (fuera)
xn = (W - 0.45)/W
fig.add_artist(FancyArrow(xn, (H - 1.55)/H, 0, 1.05/H, width=0.07/W, head_width=0.36/W, head_length=0.38/H, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, (H - 0.45)/H, 'N', ha='center', va='bottom', fontsize=11, fontweight='bold')
# escala horizontal al costado del mapa (a), abajo
frac = 500/(E[1]-E[0])*pw/W; xs = (xa + pw + g + 0.1)/W; ys = y0 + 0.05/H; h = 0.16/H
sa = fig.add_axes([xs, ys, frac, h]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
fig.text(xs, ys + h + 0.06/H, '0', ha='center', va='bottom', fontsize=10); fig.text(xs + frac, ys + h + 0.06/H, '500 m', ha='center', va='bottom', fontsize=10)
fig.savefig('F12_baja.png', dpi=300); print('W x H', round(W, 2), round(H, 2))
