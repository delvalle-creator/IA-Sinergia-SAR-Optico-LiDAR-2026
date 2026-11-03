# Tp6, Figura 14: duracion minima del agua de inundacion alrededor de Concordia, detalle de 14 x 14 km
# (E 398.000-412.000, N 6.519.000-6.533.000), desde B_extension_y_duracion_C_20m.tif (banda duracion_min_dias) y el
# agua permanente JRC >= 90 % en gris. Coordenadas UTM 21S en metros, norte en el esquinero superior derecho y escala
# grafica horizontal al costado. 30/10/2026.
# Uso: python mapas_tp6_f14.py <B_extension_y_duracion_C_20m.tif> <B_CONCORDIA_JRC_GSW_ocurrencia.tif> <salida.png> [alto_cm]
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap
from rasterio.warp import reproject, Resampling
from rasterio.windows import from_bounds
plt.rcParams['font.family'] = 'Liberation Serif'
fe, fj, out = sys.argv[1:4]
Hcm = float(sys.argv[4]) if len(sys.argv) > 4 else 9.0
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
X0, X1, Y0, Y1 = 398000, 412000, 6519000, 6533000
r = rasterio.open(fe); dsc = list(r.descriptions)
w = from_bounds(X0, Y0, X1, Y1, r.transform)
du = r.read(dsc.index('duracion_min_dias') + 1, window=w).astype('f4')
tr = r.window_transform(w)
rj = rasterio.open(fj); jrc = np.full(du.shape, np.nan, 'f4')
reproject(rj.read(1).astype('f4'), jrc, src_transform=rj.transform, src_crs=rj.crs, dst_transform=tr,
          dst_crs=r.crs, resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
perm = jrc >= 90
ext = (X0, X1, Y0, Y1)
L, T, B, R = 2.0, 0.7, 1.15, 5.2
ph = Hcm - T - B; pw = ph
Wcm = L + pw + R
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM))
ax = fig.add_axes([L / Wcm, B / Hcm, pw / Wcm, ph / Hcm])
ax.imshow(np.ones_like(du), extent=ext, cmap=ListedColormap(['#f0f0f0']), interpolation='nearest')
im = ax.imshow(np.ma.masked_where(perm | (du <= 0), du), extent=ext, cmap='Blues', vmin=0, vmax=90, interpolation='nearest')
ax.imshow(np.ma.masked_where(~perm, np.ones_like(du)), extent=ext, cmap=ListedColormap(['#a9a9a9']), interpolation='nearest')
ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1)
ax.set_xticks([400000, 405000, 410000]); ax.set_yticks([6520000, 6525000, 6530000])
ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
ax.tick_params(labelsize=10, length=3)
for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10.5, labelpad=6); ax.set_xlabel('Este, UTM 21S (m)', fontsize=10.5, labelpad=2)
p = ax.get_position()
cax = fig.add_axes([p.x1 + 0.4 / Wcm, p.y0 + 3.1 / Hcm, 0.35 / Wcm, p.height - 4.1 / Hcm])
cb = fig.colorbar(im, cax=cax, ticks=[0, 30, 60, 90]); cb.ax.tick_params(labelsize=10)
cb.ax.set_title('Días', fontsize=10.5, pad=5)
fig.legend(handles=[Patch(fc='#a9a9a9', ec='black', lw=0.5, label='Agua permanente\n(JRC ≥ 90 %, excluida)'),
                    Patch(fc='#f0f0f0', ec='black', lw=0.5, label='Sin agua de inundación')],
           loc='lower left', bbox_to_anchor=(p.x1 + 0.3 / Wcm, p.y0 + 0.9 / Hcm), fontsize=10.5, frameon=False, borderaxespad=0)
xn = 1 - 0.9 / Wcm
fig.add_artist(FancyArrow(xn, p.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                          head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, p.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
Lm = 4000; fw = Lm / (X1 - X0) * p.width; xs = p.x1 + 0.4 / Wcm; ys = p.y0 + 0.15 / Hcm; hh = 0.2 / Hcm
sa = fig.add_axes([xs, ys, fw, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
for vv, t in ((0, '0'), (0.5, '2'), (1, '4 km')):
    fig.text(xs + vv * fw, ys + hh + 0.1 / Hcm, t, ha='center', va='bottom', fontsize=10.5)
fig.savefig(out, dpi=220); plt.close(fig)
print('ancho %.2f cm, alto %.2f cm' % (Wcm, Hcm))
