# Tp6, Figura 8: BIOMASS banda P L1B DGM del 22/07/2026 en RGB copolarizada-cruzada-cociente (R = HH, G = VH,
# B = HH/VH, en dB; promedio 5 x 5 de las intensidades lineales; estiramiento 2-98 % de la escena) y altura de bosque
# FH del L2A de julio de 2026 con el agua enmascarada. El L1B DGM esta en geometria de rango en el terreno: se
# ubica con sus 121 puntos de control (GCP) y se reproyecta a UTM 21S a 25 m. Recorte comun: caja del sitio.
# Norte en el esquinero superior derecho, escala grafica horizontal al costado. 30/10/2026.
# Uso: python mapas_tp6_f8.py <B_CONCORDIA_BIOMASS_P_20260722.tif> <B_CONCORDIA_BIOMASS_P_FH_20260707_0719_sin_agua.tif> <salida.png>
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow
from rasterio.warp import reproject, Resampling, transform_bounds
from rasterio.transform import from_origin
from scipy.ndimage import uniform_filter
plt.rcParams['font.family'] = 'Liberation Serif'
fp, ff, out = sys.argv[1:4]
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
dst = 'EPSG:32721'
rf = rasterio.open(ff)
x0, y0, x1, y1 = transform_bounds(rf.crs, dst, *rf.bounds)
res = 25.0; W = int((x1 - x0) / res); H = int((y1 - y0) / res); tr = from_origin(x0, y1, res, res)
ext = (x0, x0 + W * res, y1 - H * res, y1)
rp = rasterio.open(fp); d = list(rp.descriptions); gcps, gcrs = rp.gcps
def media(nombre):
    a = rp.read(d.index(nombre) + 1).astype('f8'); m = np.isfinite(a) & (a > 0)
    s = uniform_filter(np.where(m, a, 0), 5); n = uniform_filter(m.astype('f8'), 5)
    o = np.where(n > 0.5, s / np.maximum(n, 1e-9), np.nan); return o.astype('f4')
hh, vh = media('Gamma0_HH'), media('Gamma0_VH')
capas = [10 * np.log10(hh), 10 * np.log10(vh), 10 * np.log10(hh / vh)]
rgb = np.zeros((H, W, 3), 'f4'); val = np.ones((H, W), bool)
for i, c in enumerate(capas):
    lo, hi = np.nanpercentile(c, [2, 98])  # estiramiento 2-98 % de la escena (antes de recortar)
    o = np.full((H, W), np.nan, 'f4')
    reproject(c, o, gcps=gcps, src_crs=gcrs, dst_transform=tr, dst_crs=dst, resampling=Resampling.bilinear,
              src_nodata=np.nan, dst_nodata=np.nan)
    val &= np.isfinite(o); rgb[..., i] = np.clip((o - lo) / (hi - lo), 0, 1)
rgb[~val] = 1
fh = np.full((H, W), np.nan, 'f4')
reproject(rf.read(1), fh, src_transform=rf.transform, src_crs=rf.crs, dst_transform=tr, dst_crs=dst,
          resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
Wcm, Hcm = 25.4, 8.5
L, T, B, gap, R = 2.0, 0.7, 1.15, 0.5, 4.9
ph = Hcm - T - B; asp = (ext[1] - ext[0]) / (ext[3] - ext[2]); pw = ph * asp
Wcm = L + 2 * pw + gap + R
xa = (Wcm - (L + 2 * pw + gap + R)) / 2 + L
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM)); axs = []
for k, t in enumerate(['(a) Banda P, HH, VH, HH/VH', '(b) Altura de bosque FH']):
    ax = fig.add_axes([(xa + k * (pw + gap)) / Wcm, B / Hcm, pw / Wcm, ph / Hcm])
    if k == 0: ax.imshow(rgb, extent=ext, interpolation='bilinear')
    else: im = ax.imshow(np.ma.masked_invalid(fh), extent=ext, cmap='YlGnBu', vmin=0, vmax=40, interpolation='nearest')
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_xticks([390000, 405000]); ax.set_yticks([6520000, 6535000, 6550000])
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.tick_params(labelsize=10, length=3)
    for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    if k: ax.set_yticklabels([])
    else: ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10.5, labelpad=6)
    ax.set_xlabel('Este, UTM 21S (m)', fontsize=10.5, labelpad=2)
    ax.set_title(t, fontsize=11.5, pad=4); axs.append(ax)
b = axs[-1].get_position()
cax = fig.add_axes([b.x1 + 0.35 / Wcm, b.y0 + 0.3 / Hcm, 0.35 / Wcm, b.height - 1.3 / Hcm])
cb = fig.colorbar(im, cax=cax, ticks=[0, 10, 20, 30, 40], extend='max'); cb.ax.tick_params(labelsize=10)
cb.ax.set_title('FH, m', fontsize=10.5, pad=5)
xn = 1 - 0.9 / Wcm
fig.add_artist(FancyArrow(xn, b.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                          head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, b.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
Lm = 10000; fw = Lm / (ext[1] - ext[0]) * b.width; xs = b.x1 + 1.9 / Wcm; ys = b.y0 + 0.5 / Hcm; hh_ = 0.2 / Hcm
sa = fig.add_axes([xs, ys, fw, hh_]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
for vv, t in ((0, "0"), (1, "10 km")):
    fig.text(xs + vv * fw, ys + hh_ + 0.1 / Hcm, t, ha='center', va='bottom', fontsize=10.5)
fig.savefig(out, dpi=220); plt.close(fig)
print('FH sin agua: mediana %.1f m; pixeles validos P %.0f %%' % (np.nanmedian(fh), 100 * val.mean()))
