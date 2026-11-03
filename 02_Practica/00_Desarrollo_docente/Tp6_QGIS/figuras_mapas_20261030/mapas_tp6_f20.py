# Tp6, Figura 20: variante multisensor (celeste) sobre el Sentinel-2 del 04/11/2023 en falso color (B11, B8A, B4),
# alrededor de Concordia, detalle de 14 x 14 km (E 398.000-412.000, N 6.519.000-6.533.000). Agua permanente JRC >= 90 %
# en azul oscuro. Coordenadas UTM 21S en metros, norte en el esquinero superior derecho, escala grafica horizontal al
# costado. 30/10/2026.
# Uso: python mapas_tp6_f20.py <B_CONCORDIA_S2_20231104.tif> <B_variante_multisensor_20231104.tif> <B_CONCORDIA_JRC_GSW_ocurrencia.tif> <salida.png> [alto_cm]
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow, Patch
from rasterio.windows import from_bounds
from rasterio.warp import reproject, Resampling
plt.rcParams['font.family'] = 'Liberation Serif'
fs, fm, fj, out = sys.argv[1:5]
Hcm = float(sys.argv[5]) if len(sys.argv) > 5 else 10.5
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
X0, X1, Y0, Y1 = 398000, 412000, 6519000, 6533000
s = rasterio.open(fs); d = list(s.descriptions); w = from_bounds(X0, Y0, X1, Y1, s.transform)
a = s.read([d.index(b) + 1 for b in ('B11', 'B8A', 'B04')], window=w).astype('f4')
rgb = np.zeros(a.shape[1:] + (3,), 'f4')
for i in range(3):
    v = a[i][a[i] > 0]; lo, hi = np.percentile(v, [2, 98]); rgb[..., i] = np.clip((a[i] - lo) / (hi - lo), 0, 1)
m = rasterio.open(fm); wm = from_bounds(X0, Y0, X1, Y1, m.transform); ms = m.read(1, window=wm)
tm = m.window_transform(wm)
jrc = np.full(ms.shape, np.nan, 'f4'); rj = rasterio.open(fj)
reproject(rj.read(1).astype('f4'), jrc, src_transform=rj.transform, src_crs=rj.crs, dst_transform=tm, dst_crs=m.crs,
          resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
ov = np.zeros(ms.shape + (4,), 'f4')
ov[ms == 1] = (0.0, 0.9, 1.0, 1); ov[jrc >= 90] = (0.0, 0.0, 0.75, 1)
ext = (X0, X1, Y0, Y1)
L, T, B, R = 2.0, 0.7, 1.15, 6.4
ph = Hcm - T - B; pw = ph; Wcm = L + pw + R
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM))
ax = fig.add_axes([L / Wcm, B / Hcm, pw / Wcm, ph / Hcm])
ax.imshow(rgb, extent=ext, interpolation='bilinear'); ax.imshow(ov, extent=ext, interpolation='nearest')
ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1)
ax.set_xticks([400000, 405000, 410000]); ax.set_yticks([6520000, 6525000, 6530000])
ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
ax.tick_params(labelsize=10, length=3)
for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10.5, labelpad=6); ax.set_xlabel('Este, UTM 21S (m)', fontsize=10.5, labelpad=2)
p = ax.get_position()
fig.legend(handles=[Patch(fc=(0.0, 0.9, 1.0), ec='black', lw=0.5, label='Variante multisensor'),
                    Patch(fc=(0.0, 0.0, 0.75), ec='black', lw=0.5, label='Agua permanente\n(JRC ≥ 90 %)')],
           loc='center left', bbox_to_anchor=(p.x1 + 0.3 / Wcm, p.y0 + 0.55 * p.height), fontsize=10.5, frameon=False, labelspacing=0.7)
xn = 1 - 0.9 / Wcm
fig.add_artist(FancyArrow(xn, p.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                          head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, p.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
Lm = 4000; fw = Lm / (X1 - X0) * p.width; xs = p.x1 + 0.4 / Wcm; ys = p.y0 + 0.3 / Hcm; hh = 0.2 / Hcm
sa = fig.add_axes([xs, ys, fw, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
for vv, t in ((0, '0'), (0.5, '2'), (1, '4 km')):
    fig.text(xs + vv * fw, ys + hh + 0.1 / Hcm, t, ha='center', va='bottom', fontsize=10.5)
fig.savefig(out, dpi=220); plt.close(fig)
print('ancho %.2f cm' % Wcm)
