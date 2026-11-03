# Tp7 Figura 13 baja (31/10/2026): leyenda y barra de cotas al costado, al tamano final
import sys; sys.path.insert(0, '.')
from comun import *
from matplotlib.colors import LinearSegmentedColormap
ph = float(sys.argv[1]) if len(sys.argv) > 1 else 6.0
C = CIC; DEM = plt.get_cmap('RdYlGn_r')
def cbers(ext, res):
    import rasterio as rio
    with rio.open(Q + 'CBERS4A_DIAMANTE_20260926_pansharpened_2m.tif') as s:
        lo, hi = [], []
        for b in (4, 3, 2):
            a = s.read(b, out_shape=(s.height // 8, s.width // 8)).astype('f4'); a = a[a > 0]
            lo.append(a.mean() - 2 * a.std()); hi.append(a.mean() + 2.5 * a.std())
    b = [warp(Q + 'CBERS4A_DIAMANTE_20260926_pansharpened_2m.tif', i, ext, res, nod=0) for i in (4, 3, 2)]
    rgb = np.dstack([st(a, l, h) for a, l, h in zip(b, lo, hi)]); rgb[~np.isfinite(b[0])] = 1; return np.nan_to_num(rgb, nan=1)
pw = ph
L, T, B = 1.45, 0.6, 1.05
g, cbw, cbl, legw = 0.3, 0.3, 1.25, 4.6
W = L + pw + g + pw + 0.2 + cbw + cbl + legw
H = T + ph + B; y0 = B/H
a1 = fig_ = None
fig = plt.figure(figsize=(W*CM, H*CM))
a1 = fig.add_axes([L/W, y0, pw/W, ph/H]); a2 = fig.add_axes([(L+pw+g)/W, y0, pw/W, ph/H])
a1.imshow(cbers(C, 1), extent=C, interpolation='bilinear')
im = a2.imshow(warp(Q + 'IGN_MDE_5m.tif', 1, C, 1), extent=C, cmap=DEM, vmin=10, vmax=60, interpolation='bilinear')
for k, (ax, t) in enumerate(zip((a1, a2), ['(a) CBERS-4A, 26/09/2026 (2 m)', '(b) IGN MDE 5 m (2013)'])):
    capas(ax, formas=True, lw=2.2, gw=(7, 4)); marco(ax, C, 100, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
a1.set_ylabel('Norte (m), EPSG:32721')
ca = fig.add_axes([(L+pw+g+pw+0.2)/W, y0, cbw/W, ph/H]); cb = fig.colorbar(im, cax=ca, ticks=[10, 20, 30, 40, 50, 60])
cb.ax.tick_params(labelsize=9.5); cb.set_label('cota (m, SRVN16)', fontsize=10)
xl = (L+pw+g+pw+0.2+cbw+cbl)/W
fig.legend(handles=[lin(C_CIC, 'cicatriz'), lin(C_DEP, 'depósito (claro con\nNDVI < 0,30)'), lin('red', 'grieta relevada\nen 2018', 3.5)],
           loc='center left', bbox_to_anchor=(xl, y0 + 0.55*ph/H), frameon=False, fontsize=10, handlelength=1.8, labelspacing=0.7, borderaxespad=0)
xn = (W - 0.5)/W
fig.add_artist(FancyArrow(xn, (H - 1.55)/H, 0, 1.05/H, width=0.07/W, head_width=0.36/W, head_length=0.38/H, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, (H - 0.45)/H, 'N', ha='center', va='bottom', fontsize=11, fontweight='bold')
frac = 100/(C[1]-C[0])*pw/W; xs = xl + 0.1/W; ys = y0 + 0.05/H; h = 0.16/H
sa = fig.add_axes([xs, ys, frac, h]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
fig.text(xs, ys + h + 0.06/H, '0', ha='center', va='bottom', fontsize=10); fig.text(xs + frac, ys + h + 0.06/H, '100 m', ha='center', va='bottom', fontsize=10)
fig.savefig('F13_baja.png', dpi=300); print('W x H', round(W, 2), round(H, 2))
