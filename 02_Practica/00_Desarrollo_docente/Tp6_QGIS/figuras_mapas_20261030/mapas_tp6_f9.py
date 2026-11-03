# Tp6, Figura 9: NovaSAR-1 banda S del 13/09/2023, sigma0 HH (a) y Sentinel-1 del 04/11/2023 en RGB VV-VH-VV/VH (b).
# NovaSAR: GRD a 2,5 m en geometria de radar; sigma0 = DN^2 / 100000 (constante de calibracion del producto),
# promedio de la intensidad en bloques de 8 x 8 (20 m), dB, y ubicacion con los 84 puntos de control (GCP) a
# UTM 21S a 20 m. Estiramiento 2-98 % en gris. Mismo recuadro que el Sentinel-1 del sitio.
# Norte en el esquinero superior derecho, escala grafica horizontal al costado. 30/10/2026.
# Uso: python mapas_tp6_f9.py <B_CONCORDIA_NovaSAR1_S_20230913.tif> <B_CONCORDIA_S1_C_20231104_RGB_8bit.tif> <salida.png>
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
plt.rcParams['font.family'] = 'Liberation Serif'
fn, fs, out = sys.argv[1:4]
CM = 1 / 2.54; F = 4
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
rs = rasterio.open(fs); assert rs.crs.to_epsg() == 32721
h, w = rs.height // F, rs.width // F
s1 = rs.read([1, 2, 3], out_shape=(3, h, w), resampling=Resampling.average).astype('f4')
b = rs.bounds; ext = (b.left, b.right, b.bottom, b.top)
im1 = np.moveaxis(s1 / 255., 0, -1); im1[(s1 == 0).all(0)] = 1
# NovaSAR
rn = rasterio.open(fn); gcps, gcrs = rn.gcps
dn = rn.read(1).astype('f8'); m = dn > 0
K = 8; H0, W0 = (dn.shape[0] // K) * K, (dn.shape[1] // K) * K
s0 = (dn[:H0, :W0] ** 2 / 1e5).reshape(H0 // K, K, W0 // K, K)
mm = m[:H0, :W0].reshape(H0 // K, K, W0 // K, K)
num = (s0 * mm).sum((1, 3)); cnt = mm.sum((1, 3))
db = np.where(cnt > K * K / 2, 10 * np.log10(np.maximum(num / np.maximum(cnt, 1), 1e-6)), np.nan).astype('f4')
from rasterio.control import GroundControlPoint
g2 = [GroundControlPoint(row=g.row / K, col=g.col / K, x=g.x, y=g.y) for g in gcps]
res = 20.0; W = int((ext[1] - ext[0]) / res); H = int((ext[3] - ext[2]) / res)
tr = from_origin(ext[0], ext[3], res, res)
nv = np.full((H, W), np.nan, 'f4')
reproject(db, nv, gcps=g2, src_crs=gcrs, dst_transform=tr, dst_crs='EPSG:32721', resampling=Resampling.bilinear,
          src_nodata=np.nan, dst_nodata=np.nan)
lo, hi = np.nanpercentile(nv, [2, 98])
g = np.clip((nv - lo) / (hi - lo), 0, 1); im0 = np.dstack([g, g, g]); im0[~np.isfinite(nv)] = 1
cob = 100 * np.isfinite(nv).mean()
Wcm, Hcm = 25.4, 10.6
L, T, B, gap, R = 2.0, 0.7, 1.15, 0.5, 3.4
ph = Hcm - T - B; asp = (ext[1] - ext[0]) / (ext[3] - ext[2]); pw = ph * asp
Wcm = L + 2 * pw + gap + R
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM)); axs = []
for k, (im, t) in enumerate([(im0, '(a) NovaSAR-1 S, 13/09/2023, σ$^0$ HH'), (im1, '(b) Sentinel-1, 04/11/2023')]):
    ax = fig.add_axes([(L + k * (pw + gap)) / Wcm, B / Hcm, pw / Wcm, ph / Hcm])
    ax.imshow(im, extent=ext, interpolation='bilinear')
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_xticks([390000, 400000, 410000]); ax.set_yticks([6520000, 6530000, 6540000, 6550000])
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.tick_params(labelsize=10, length=3)
    for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    if k: ax.set_yticklabels([])
    else: ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10.5, labelpad=6)
    ax.set_xlabel('Este, UTM 21S (m)', fontsize=10.5, labelpad=2)
    ax.set_title(t, fontsize=11.5, pad=4); axs.append(ax)
bb = axs[-1].get_position()
xn = 1 - 0.9 / Wcm
fig.add_artist(FancyArrow(xn, bb.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                          head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, bb.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
Lm = 10000; fw = Lm / (ext[1] - ext[0]) * bb.width; xs = bb.x1 + 0.45 / Wcm; ys = bb.y0 + 0.5 / Hcm; hh = 0.2 / Hcm
sa = fig.add_axes([xs, ys, fw, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
for vv, t in ((0, '0'), (0.5, '5'), (1, '10 km')):
    fig.text(xs + vv * fw, ys + hh + 0.1 / Hcm, t, ha='center', va='bottom', fontsize=10.5)
fig.savefig(out, dpi=220); plt.close(fig)
print('cobertura NovaSAR en el recuadro: %.0f %%; estiramiento %.1f a %.1f dB; ancho %.2f cm' % (cob, lo, hi, Wcm))
