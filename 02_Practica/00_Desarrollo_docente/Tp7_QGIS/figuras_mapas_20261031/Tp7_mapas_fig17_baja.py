# Tp7 Figura 17 baja (31/10/2026): barra y leyendas al costado, al tamano final (letras de 10 pt)
import sys; sys.path.insert(0, '.')
from comun import *
import matplotlib
from matplotlib.colors import ListedColormap, BoundaryNorm
from scipy import ndimage as ndi
E = BAR; PX = 5
def cbers(ext, res):
    import rasterio as rio
    with rio.open(Q + 'CBERS4A_DIAMANTE_20260926_pansharpened_2m.tif') as s:
        lo, hi = [], []
        for b in (4, 3, 2):
            a = s.read(b, out_shape=(s.height // 8, s.width // 8)).astype('f4'); a = a[a > 0]
            lo.append(a.mean() - 2 * a.std()); hi.append(a.mean() + 2.5 * a.std())
    b = [warp(Q + 'CBERS4A_DIAMANTE_20260926_pansharpened_2m.tif', i, ext, res, nod=0) for i in (4, 3, 2)]
    rgb = np.dstack([st(a, l, h) for a, l, h in zip(b, lo, hi)]); rgb[~np.isfinite(b[0])] = 1; return np.nan_to_num(rgb, nan=1)
vel = warp(U + 'Tp10_Impacto_urbano/05_Resultados/02_Rasters/E_PARANA_DIAMANTE_velocidad_vertical.tif', 1, E, PX, rs=Resampling.nearest)
sus = warp(RAS + 'E1_susceptibilidad_fisuras_hipotetica.tif', 1, E, PX, rs=Resampling.nearest)
ign = warp(Q + 'IGN_MDE_5m.tif', 1, E, PX, rs=Resampling.nearest)
ign = np.where(np.isfinite(ign), ign, warp(Q + 'IGN_MDE_mosaico2018.tif', 1, E, PX, rs=Resampling.nearest, cero=True))
gy, gx = np.gradient(ndi.gaussian_filter(np.nan_to_num(ign, nan=np.nanmin(ign)), 2), PX); pend = np.hypot(gx, gy) * 100
meseta = ign > 40; bajo = (ign < 15) | ~np.isfinite(ign)
borde = (pend > 30) & (ign > 15) & (ndi.distance_transform_edt(~meseta) * PX < 30) & (ndi.distance_transform_edt(~bajo) * PX < 250)
lab, n = ndi.label(borde); tam = ndi.sum(borde, lab, range(1, n + 1)); borde = np.isin(lab, 1 + np.where(tam > 400)[0])
fondo = cbers(E, 2)
ph = float(sys.argv[1]) if len(sys.argv) > 1 else 7.0
asp = (E[3]-E[2])/(E[1]-E[0]); pw = ph/asp
L, T, B = 1.45, 0.65, 1.05
cbg, cbw, cbl, g2, lw_ = 0.2, 0.3, 2.3, 0.35, 6.6
W = L + pw + cbg + cbw + cbl + pw + g2 + lw_
H = T + ph + B; y0 = B/H
xa = L; xb = L + pw + cbg + cbw + cbl
a1 = fig = None
fig = plt.figure(figsize=(W*CM, H*CM))
a1 = fig.add_axes([xa/W, y0, pw/W, ph/H]); a2 = fig.add_axes([xb/W, y0, pw/W, ph/H])
for ax in (a1, a2): ax.imshow(fondo, extent=E, interpolation='bilinear')
a1.imshow(np.clip(vel, -20, 20), extent=E, cmap='RdBu', vmin=-20, vmax=20, alpha=.85, interpolation='nearest')
im = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(-20, 20), cmap='RdBu')
cms = ListedColormap([(1, 1, .75, .45), (1, .6, 0, .65), (.85, 0, 0, .8)])
a2.imshow(np.where(sus > 0, sus, np.nan), extent=E, cmap=cms, norm=BoundaryNorm([.5, 1.5, 2.5, 3.5], 3), interpolation='nearest')
a2.contour(np.linspace(E[0] + PX/2, E[1] - PX/2, borde.shape[1]), np.linspace(E[3] - PX/2, E[2] + PX/2, borde.shape[0]), borde.astype(float), levels=[.5], colors='k', linewidths=.8)
for k, (ax, t) in enumerate(zip((a1, a2), ['(a) Velocidad vertical HyP3, 2025–2026', '(b) Susceptibilidad (HIPOTÉTICA)'])):
    capas(ax, formas=True, lw=1.6, gw=(4, 2.3)); marco(ax, E, 1000, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
    ax.set_yticks([6445500, 6447000])
for l in a1.get_yticklabels(): l.set_rotation(90); l.set_va('center')
a1.set_ylabel('Norte (m), EPSG:32721')
ca = fig.add_axes([(xa + pw + cbg)/W, y0, cbw/W, ph/H])
cb = fig.colorbar(im, cax=ca, ticks=[-20, -10, 0, 10, 20]); cb.ax.yaxis.set_major_formatter(coma()); cb.ax.tick_params(labelsize=9.5)
cb.set_label('velocidad vertical (mm/año);\nrojo = hundimiento', fontsize=10)
xl = (xb + pw + g2)/W; top = (H - T)/H
h = [Patch(facecolor=(.85, 0, 0, .8), label='Alta: ≤ 150 m del borde y\nvelocidad < −13,6 mm/año'),
     Patch(facecolor=(1, .6, 0, .65), label='Media: una de las dos'),
     Patch(facecolor=(1, 1, .75, .9), edgecolor='0.4', lw=.6, label='Baja: resto de la zona\nconstruida'),
     lin('black', 'talud de la barranca', 1.0), lin('red', 'grieta relevada en 2018', 3.5), lin(C_CIC, 'cicatriz'), lin(C_DEP, 'depósito')]
fig.legend(handles=h, loc='upper left', bbox_to_anchor=(xl, top - 1.25/H), frameon=False, fontsize=10, handlelength=1.6, labelspacing=0.45, borderaxespad=0)
xn = (W - 0.5)/W
fig.add_artist(FancyArrow(xn, (H - 1.55)/H, 0, 1.05/H, width=0.07/W, head_width=0.36/W, head_length=0.38/H, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, (H - 0.45)/H, 'N', ha='center', va='bottom', fontsize=11, fontweight='bold')
frac = 500/(E[1]-E[0])*pw/W; xs = xl + 0.1/W; ys = y0 + 0.05/H; hh = 0.16/H
sa = fig.add_axes([xs, ys, frac, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
fig.text(xs, ys + hh + 0.06/H, '0', ha='center', va='bottom', fontsize=10); fig.text(xs + frac, ys + hh + 0.06/H, '500 m', ha='center', va='bottom', fontsize=10)
fig.savefig('F17_baja.png', dpi=300); print('W x H', round(W, 2), round(H, 2))
