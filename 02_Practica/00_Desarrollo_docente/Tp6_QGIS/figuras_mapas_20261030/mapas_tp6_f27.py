# Tp6, Figura 27: Sentinel-1A del 04/11/2023 en RGB copolarizada-cruzada-cociente (R = VV, G = VH, B = VV/VH, en dB,
# rangos fijos: VV -22 a 2, VH -28 a -6, VV/VH 0 a 14): procesado en SNAP desde el GRDH sin procesar (a) y RTC del Planetary
# Computer (b); VV de uno frente al otro, pixel a pixel (c), con el umbral de -15 dB. El de SNAP se lleva a la grilla
# del RTC por promedio (10 m). Coordenadas UTM 21S en m, un norte en el esquinero superior derecho, escala grafica
# horizontal al costado. 30/10/2026.
# Uso: python mapas_tp6_f27.py <SNAP_RGB_dB.tif> <RTC_RGB_dB.tif> <salida.png> [alto_cm]
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow
from matplotlib.colors import LogNorm
from rasterio.warp import reproject, Resampling
plt.rcParams['font.family'] = 'Liberation Serif'
fs, fr, out = sys.argv[1:4]
Hcm = float(sys.argv[4]) if len(sys.argv) > 4 else 10.0
CM = 1 / 2.54; F = 4
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
menos = FuncFormatter(lambda v, _: ('%g' % v).replace('-', '−'))
rr = rasterio.open(fr); b = rr.bounds; ext = (b.left, b.right, b.bottom, b.top)
rtc = rr.read().astype('f4')
rs = rasterio.open(fs); snap = np.full(rtc.shape, np.nan, 'f4')
for i in range(3):
    reproject(rs.read(i + 1).astype('f4'), snap[i], src_transform=rs.transform, src_crs=rs.crs, dst_transform=rr.transform,
              dst_crs=rr.crs, resampling=Resampling.average, src_nodata=np.nan, dst_nodata=np.nan)
rng = [(-22, 2), (-28, -6), (0, 14)]
def rgb(a):
    a = a[:, ::F, ::F]; o = np.zeros(a.shape[1:] + (3,), 'f4')
    for i, (lo, hi) in enumerate(rng): o[..., i] = np.clip((a[i] - lo) / (hi - lo), 0, 1)
    o[~np.isfinite(a).all(0)] = 1; return o
vv_r, vv_s = rtc[0][::2, ::2], snap[0][::2, ::2]
ok = np.isfinite(vv_r) & np.isfinite(vv_s)
L, T, B, gap = 2.0, 0.7, 1.15, 0.6
ph = Hcm - T - B; pw = ph * (ext[1] - ext[0]) / (ext[3] - ext[2])
gs, sc, R = 1.4, ph, 0.6
Wcm = L + 2 * pw + gap + 2.4 + gs + sc + 1.6 + R
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM)); axs = []
for k, (a, t) in enumerate([(snap, '(a) γ$^0$ de SNAP desde el GRDH'), (rtc, '(b) γ$^0$ RTC del Planetary Computer')]):
    ax = fig.add_axes([(L + k * (pw + gap)) / Wcm, B / Hcm, pw / Wcm, ph / Hcm])
    ax.imshow(rgb(a), extent=ext, interpolation='bilinear')
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_xticks([390000, 410000]); ax.set_yticks([6520000, 6535000, 6550000])
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.tick_params(labelsize=10, length=3)
    for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    if k: ax.set_yticklabels([])
    else: ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10.5, labelpad=6)
    ax.set_xlabel('Este, UTM 21S (m)', fontsize=10.5, labelpad=2)
    ax.set_title(t, fontsize=10.5, pad=4); axs.append(ax)
p1 = axs[1].get_position()
xn = p1.x1 + 1.0 / Wcm
fig.add_artist(FancyArrow(xn, p1.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                          head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, p1.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
Lm = 10000; fw = Lm / (ext[1] - ext[0]) * p1.width; xs = p1.x1 + 0.35 / Wcm; ys = p1.y0 + 0.4 / Hcm; hh = 0.2 / Hcm
sa = fig.add_axes([xs, ys, fw, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
for vv, t in ((0, '0'), (1, '10 km')):
    fig.text(xs + vv * fw, ys + hh + 0.1 / Hcm, t, ha='center', va='bottom', fontsize=10.5)
x0c = L + 2 * pw + gap + 2.4 + gs
ac = fig.add_axes([x0c / Wcm, B / Hcm, sc / Wcm, ph / Hcm])
hb = ac.hist2d(vv_r[ok], vv_s[ok], bins=180, range=[[-30, 5], [-30, 5]], cmap='magma', norm=LogNorm(vmin=1), cmin=1)
ac.plot([-30, 5], [-30, 5], color='#1ab0b0', lw=1.2)
ac.axvline(-15, color='white', ls='--', lw=0.8); ac.axhline(-15, color='white', ls='--', lw=0.8)
ac.set_facecolor('white'); ac.set_xlim(-30, 5); ac.set_ylim(-30, 5)
ac.set_xticks([-30, -20, -10, 0]); ac.set_yticks([-30, -20, -10, 0])
ac.xaxis.set_major_formatter(menos); ac.yaxis.set_major_formatter(menos); ac.tick_params(labelsize=10)
ac.set_xlabel('RTC, γ$^0$ VV (dB)', fontsize=10.5, labelpad=2); ac.set_ylabel('SNAP, γ$^0$ VV (dB)', fontsize=10.5, labelpad=2)
ac.set_title('(c) VV píxel a píxel', fontsize=11, pad=4)
pc = ac.get_position()
cax = fig.add_axes([pc.x1 + 0.2 / Wcm, pc.y0, 0.3 / Wcm, pc.height])
cb = fig.colorbar(hb[3], cax=cax); cb.ax.tick_params(labelsize=10)
cb.ax.yaxis.set_major_formatter(miles); cb.set_label('Píxeles (uno de cada cuatro)', fontsize=10.5, labelpad=2)
fig.savefig(out, dpi=220); plt.close(fig)
print('ancho %.2f; corr %.2f' % (Wcm, np.corrcoef(vv_r[ok], vv_s[ok])[0, 1]))
