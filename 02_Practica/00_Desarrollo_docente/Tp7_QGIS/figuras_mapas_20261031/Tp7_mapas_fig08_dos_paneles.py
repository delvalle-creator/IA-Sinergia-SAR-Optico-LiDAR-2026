# Tp7 Figura 8 en dos paneles (31/10/2026): fase desenrollada y componentes conexas, al tamano final
import sys; sys.path.insert(0, '.')
from comun import *
from matplotlib.colors import ListedColormap, BoundaryNorm
ph = float(sys.argv[1]) if len(sys.argv) > 1 else 6.0
E = BAR; asp = (E[3]-E[2])/(E[1]-E[0]); pw = ph/asp
L, T, B = 1.45, 0.6, 1.05      # margen izq, titulo, rotulos x
cbw, cbg, g = 0.3, 0.25, 2.3   # ancho barra, separacion barra, separacion entre paneles (incluye rotulos de la barra)
legw = 5.2
W = L + pw + cbg + cbw + g + pw + cbg + cbw + 2.6 + legw
H = T + ph + B
fig = plt.figure(figsize=(W*CM, H*CM))
x1 = L; x2 = L + pw + cbg + cbw + g
y0 = B/H
a1 = fig.add_axes([x1/W, y0, pw/W, ph/H]); a2 = fig.add_axes([x2/W, y0, pw/W, ph/H])
unw = warp(FIG + 'E1_X_Unw_Phase_snaphu_15-19Oct2018.tif', 1, E, 2, rs=Resampling.nearest)
p1, p99 = -2.79, 2.56
im1 = a1.imshow(unw, extent=E, cmap='RdBu', vmin=p1, vmax=p99, interpolation='nearest')
com = warp(FIG + 'E1_X_componentes_snaphu_15-19Oct2018.tif', 1, E, 2, rs=Resampling.nearest)
cmc = ListedColormap(['#bdbdbd', '#1f77b4', '#ff7f0e']); nc = BoundaryNorm([-0.5, 0.5, 1.5, 2.5], 3)
im2 = a2.imshow(np.where(com > 2, 2, com), extent=E, cmap=cmc, norm=nc, interpolation='nearest')
for k, (ax, t) in enumerate(zip((a1, a2), ['(a) Fase desenrollada con SNAPHU', '(b) Componentes conexas de SNAPHU'])):
    capas(ax, ladera='yellow', anillo=True); marco(ax, E, 1000, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
a1.set_ylabel('Norte (m), EPSG:32721')
for ax in (a1, a2): ax.set_yticks([6445500, 6447000])
for l in a1.get_yticklabels(): l.set_rotation(90); l.set_va('center')
c1 = fig.add_axes([(x1+pw+cbg)/W, y0, cbw/W, ph/H]); cb = fig.colorbar(im1, cax=c1, ticks=[-2, -1, 0, 1, 2], extend='both')
cb.ax.yaxis.set_major_formatter(coma()); cb.ax.tick_params(labelsize=9.5); cb.set_label('fase (rad); percentiles 1 y 99', fontsize=10)
c2 = fig.add_axes([(x2+pw+cbg)/W, y0, cbw/W, ph/H]); cb2 = fig.colorbar(im2, cax=c2, ticks=[0, 1, 2])
cb2.ax.set_yticklabels(['0 (sin\nconfianza)', '1', '2']); cb2.ax.tick_params(labelsize=9.5); cb2.set_label('componente conexa', fontsize=10)
# norte arriba a la derecha, fuera de los mapas
xl = (x2 + pw + cbg + cbw + 2.6) / W
fig.add_artist(FancyArrow(xl + 0.3/W, (H - T - 1.5)/H, 0, 1.05/H, width=0.07/W, head_width=0.36/W, head_length=0.38/H,
                          length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xl + 0.3/W, (H - T - 0.4)/H, 'N', ha='center', va='bottom', fontsize=11, fontweight='bold')
# leyenda y escala al costado, debajo del norte
fig.legend(handles=[lin('yellow', 'ladera relevada en 2018'), lin('cyan', 'anillo de referencia'), lin('red', 'grieta relevada en 2018', 3.5)],
           loc='upper left', bbox_to_anchor=(xl - 0.15/W, (H - T - 1.75)/H), frameon=False, fontsize=10, handlelength=2.0)
Lm = 500; frac = Lm/(E[1]-E[0])*pw/W; ys = (B + 0.05)/H; h = 0.16/H
sa = fig.add_axes([xl, ys, frac, h]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
fig.text(xl, ys + h + 0.06/H, '0', ha='center', va='bottom', fontsize=10); fig.text(xl + frac, ys + h + 0.06/H, '500 m', ha='center', va='bottom', fontsize=10)
fig.savefig('F08_dos_paneles.png', dpi=300); print('W x H cm', round(W, 2), round(H, 2))
