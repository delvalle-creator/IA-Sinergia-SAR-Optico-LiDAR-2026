"""Figura 38 del Desarrollo del Tp3 (antes emb_indep.py + fig36.py): embeddings AlphaEarth, semejanza al prototipo de
bosque cerrado (20 pixeles de la clase 3 sorteados con semilla 2026) y bosques cerrados de MapBiomas 2025.
Mismo contenido; una sola escala y una sola flecha norte, fuera de los mapas."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp3/sc')
from com import *
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import Affine
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
# ---- semejanza (identico a emb_indep.py)
RNG = np.random.default_rng(2026); f = 2
with rasterio.open(Q + 'A2_IBICUY_AlphaEarth_embeddings_2025_10m.tif') as s:
    H, Wd = s.height // f, s.width // f
    a = s.read(out_shape=(64, H, Wd), resampling=Resampling.nearest).astype(np.float32)
    T = s.transform * Affine.scale(s.width / Wd, s.height / H); crs = s.crs
nod = (a == -128).any(0); v = np.sign(a) * (a / 127.5) ** 2; n = np.linalg.norm(v, axis=0); n[n == 0] = 1; v /= n; v[:, nod] = np.nan
del a
mb = np.full((H, Wd), np.nan, np.float32)
with rasterio.open(Q + 'A2_IBICUY_MapBiomas_cobertura_1985_2025.tif') as s:
    x = s.read(41).astype(np.float32)
    if s.nodata is not None: x[x == s.nodata] = np.nan
    reproject(x, mb, src_transform=s.transform, src_crs=s.crs, dst_transform=T, dst_crs=crs, resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
ok = np.isfinite(v).all(0) & np.isfinite(mb) & (mb > 0); ref = mb.copy(); ref[~ok] = np.nan
w = np.flatnonzero((ref == 3).ravel()); smp = RNG.choice(w, 20, replace=False)
Ef = v.reshape(64, -1); proto = np.nanmean(Ef[:, smp], axis=1); proto /= np.linalg.norm(proto)
okall = np.isfinite(v).all(0)
sim = np.full((H, Wd), np.nan); sim.ravel()[okall.ravel()] = proto @ Ef[:, okall.ravel()]
best = (0, 0)
for t in np.arange(0.5, 0.99, 0.01):
    p = sim >= t; y = ref == 3; tp = (p & y & ok).sum(); f1 = 2 * tp / ((p & ok).sum() + (y & ok).sum())
    if f1 > best[1]: best = (t, f1)
print('control: umbral %.2f F1 %.3f (bitacora: 0.98, 0.47)' % best)
ext = [T.c, T.c + Wd * T.a, T.f + H * T.e, T.f]
# ---- figura (ancho en el Word: 17,7 cm)
plt.rcParams.update({"font.size": 10, "axes.titlesize": 10, "axes.labelsize": 10, "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "legend.fontsize": 9.5})
FW, FHt = 7.0, 4.9; pw = 1.92; ph = pw * (ext[3] - ext[2]) / (ext[1] - ext[0]); gap = 0.22; x0 = 0.62; y0 = 1.5
fig = plt.figure(figsize=(FW, FHt))
axs = [fig.add_axes([(x0 + k * (pw + gap)) / FW, y0 / FHt, pw / FW, ph / FHt]) for k in range(3)]
# (a) como en la figura actual (rama sin el RGB 8 bit de fig36.py): CP1-CP3 del embedding sin normalizar, 2-98 %
with rasterio.open(Q + 'A2_IBICUY_AlphaEarth_embeddings_2025_10m.tif') as s:
    a = s.read(out_shape=(64, H, Wd), resampling=Resampling.nearest).astype(np.float32)
nd = (a == -128).any(0); vv = np.sign(a) * (a / 127.5) ** 2; del a
X = vv.reshape(64, -1).T; okc = ~nd.ravel(); Xm = X[okc] - X[okc].mean(0)
rng = np.random.default_rng(2026); idx = rng.choice(len(Xm), min(200000, len(Xm)), replace=False)
_, _, Vt = np.linalg.svd(Xm[idx], full_matrices=False); P = Xm @ Vt[:3].T
cprgb = np.zeros((H * Wd, 3))
for k in range(3):
    lo, hi = np.percentile(P[:, k], 2), np.percentile(P[:, k], 98); cprgb[okc, k] = np.clip((P[:, k] - lo) / (hi - lo), 0, 1)
axs[0].imshow(cprgb.reshape(H, Wd, 3), extent=ext); axs[0].set_title('(a) Embeddings 2025:\ncomponentes principales\n1, 2 y 3')
im = axs[1].imshow(sim, extent=ext, cmap='viridis', vmin=0.3, vmax=1)
axs[1].contour((np.isfinite(sim) & (sim >= 0.98)).astype(float), levels=[0.5], colors='white', linewidths=0.4, extent=ext, origin='upper')
axs[1].set_title('(b) Semejanza al prototipo\nde bosque cerrado')
m = np.full(ref.shape, np.nan); m[np.isfinite(ref)] = 0; m[ref == 3] = 1
mm = np.where(np.isnan(m), 2, m)
axs[2].imshow(mm, extent=ext, cmap=ListedColormap(['#eeeeee', '#1f8d49', '#ffffff']), vmin=-0.5, vmax=2.5, interpolation='nearest')
axs[2].contour(np.isnan(m).astype(float), levels=[0.5], colors='0.4', linewidths=0.5, extent=ext, origin='upper')
axs[2].set_title('(c) MapBiomas 2025:\nbosques cerrados')
for k, a_ in enumerate(axs):
    a_.set_xlim(ext[0], ext[1]); a_.set_ylim(ext[2], ext[3]); ejes_utm(a_, 5, k == 0)
    a_.xaxis.set_major_locator(MultipleLocator(10000))
    if k: a_.set_yticklabels([])
yb = escala_norte(fig, axs[0], 5000, '5 km', axn=axs[2], fs=10)
b = axs[1].get_position()
cax = fig.add_axes([b.x0, yb, b.width * 2 + (gap / FW), 0.11 / FHt])
cb = fig.colorbar(im, cax=cax, orientation='horizontal'); cb.set_label('(b) coseno (1 = igual al prototipo)'); cb.ax.xaxis.set_major_formatter(fmt(1))
fig.canvas.draw(); cbb = cax.get_tightbbox(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
fig.legend(handles=[Patch(color='#1f8d49', label='3 Bosques cerrados (leyenda oficial de MapBiomas)'), Patch(color='#eeeeee', label='Otras clases de MapBiomas'),
                    Patch(facecolor='#ffffff', edgecolor='0.4', label='Fuera de la cobertura de MapBiomas'),
                    Line2D([], [], color='white', marker='s', markerfacecolor='white', markeredgecolor='k', lw=0, markersize=9, label='Contorno blanco en (b): semejanza ≥ 0,98')],
           loc='upper left', bbox_to_anchor=(x0 / FW - 0.01, min(cbb.y0, yb) - 0.04), ncol=2, frameon=False)
guardar(fig, 'F38.png', dpi=300)
