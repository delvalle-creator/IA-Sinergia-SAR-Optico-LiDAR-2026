# Tp7 Figura 18 (31/10/2026): embeddings AlphaEarth en EPSG:32721, letras de 10 pt, norte y escala fuera
import sys; sys.path.insert(0, '.')
from comun import *
import rasterio as rio
from rasterio.transform import array_bounds
def emb(a):
    with rio.open(Q + 'AlphaEarth_embeddings_%d_10m.tif' % a) as s:
        x = s.read().astype('f4'); T = s.transform; crs = s.crs
    nod = (x == -128).any(0); v = np.sign(x)*(x/127.5)**2; n = np.linalg.norm(v, axis=0); n[n == 0] = 1; v = v/n; v[:, nod] = np.nan
    return v, T, crs
A, T, crs = emb(2018); Bv, _, _ = emb(2025); sim = (A*Bv).sum(0).astype('f4'); del A, Bv
with rio.open('sim_tmp.tif', 'w', driver='GTiff', height=sim.shape[0], width=sim.shape[1], count=1, dtype='float32', crs=crs, transform=T, nodata=np.nan) as o: o.write(sim, 1)
c = frm[frm.tipo == 'cicatriz'].union_all().centroid; R_ = 700
Z = (c.x - R_, c.x + R_, c.y - R_, c.y + R_)
s21 = warp('sim_tmp.tif', 1, Z, 10, rs=Resampling.nearest, nod=None)
def rgb(a): return np.dstack([np.clip(warp(Q + 'AlphaEarth_embeddings_%d_10m_CP1_CP2_CP3_RGB_8bit.tif' % a, b, Z, 10, rs=Resampling.nearest, nod=None)/255., 0, 1) for b in (1, 2, 3)])
ph = float(sys.argv[1]) if len(sys.argv) > 1 else 6.0; pw = ph
L, T_, B = 1.45, 1.05, 1.05
g, cbg, cbw, cbl, legw = 0.35, 0.2, 0.3, 1.35, 4.4
W = L + 3*pw + 2*g + cbg + cbw + cbl + legw
H = T_ + ph + B; y0 = B/H
fig = plt.figure(figsize=(W*CM, H*CM))
axs = [fig.add_axes([(L + k*(pw + g))/W, y0, pw/W, ph/H]) for k in range(3)]
axs[0].imshow(np.nan_to_num(rgb(2018), nan=1), extent=Z, interpolation='nearest'); axs[1].imshow(np.nan_to_num(rgb(2025), nan=1), extent=Z, interpolation='nearest')
im = axs[2].imshow(s21, extent=Z, cmap='magma', vmin=0.4, vmax=1, interpolation='nearest')
for k, (ax, t) in enumerate(zip(axs, ['(a) Embeddings 2018,\nCP1-CP2-CP3', '(b) Embeddings 2025,\nCP1-CP2-CP3', '(c) Semejanza 2018–2025\n(coseno)'])):
    capas(ax, formas=True, lw=1.8, gw=(4.5, 2.6)); marco(ax, Z, 500, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
for l in axs[0].get_yticklabels(): l.set_rotation(90); l.set_va('center')
axs[0].set_ylabel('Norte (m), EPSG:32721')
xc = L + 3*pw + 2*g + cbg
ca = fig.add_axes([xc/W, y0, cbw/W, ph/H]); cb = fig.colorbar(im, cax=ca, ticks=[.4, .5, .6, .7, .8, .9, 1]); cb.ax.yaxis.set_major_formatter(coma())
cb.ax.tick_params(labelsize=9.5); cb.set_label('coseno; 1 = sin cambio', fontsize=10)
xl = (xc + cbw + cbl)/W
fig.legend(handles=[lin(C_CIC, 'cicatriz'), lin(C_DEP, 'depósito'), lin('red', 'grieta relevada\nen 2018', 3.5)],
           loc='center left', bbox_to_anchor=(xl, y0 + 0.5*ph/H), frameon=False, fontsize=10, handlelength=1.6, labelspacing=0.6, borderaxespad=0)
xn = (W - 0.5)/W
fig.add_artist(FancyArrow(xn, (H - 1.55)/H, 0, 1.05/H, width=0.07/W, head_width=0.36/W, head_length=0.38/H, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, (H - 0.45)/H, 'N', ha='center', va='bottom', fontsize=11, fontweight='bold')
frac = 500/(Z[1]-Z[0])*pw/W; xs = xl + 0.1/W; ys = y0 + 0.05/H; hh = 0.16/H
sa = fig.add_axes([xs, ys, frac, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
fig.text(xs, ys + hh + 0.06/H, '0', ha='center', va='bottom', fontsize=10); fig.text(xs + frac, ys + hh + 0.06/H, '500 m', ha='center', va='bottom', fontsize=10)
fig.savefig('F18_32721.png', dpi=300); print('W x H', round(W, 2), round(H, 2))
