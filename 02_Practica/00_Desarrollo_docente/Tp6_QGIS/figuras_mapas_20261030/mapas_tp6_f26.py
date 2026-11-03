# Tp6, Figura 26: agua de inundacion en banda C el 04/11/2023 y el 14/05/2024 (bandas agua_20231104 y agua_20240514 de
# B_agua_C_por_fecha_20m.tif, salida de Tp6_01_serie_agua_C.py): donde coinciden las dos crecidas y donde aparece solo una.
# Agua permanente JRC >= 90 % en gris. Coordenadas UTM 21S en m, norte en el esquinero superior derecho, escala grafica
# horizontal al costado y leyenda al costado. 30/10/2026.
# Uso: python mapas_tp6_f26.py <B_agua_C_por_fecha_20m.tif> <B_CONCORDIA_JRC_GSW_ocurrencia.tif> <salida.png> [alto_cm]
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap
from rasterio.warp import reproject, Resampling
plt.rcParams['font.family'] = 'Liberation Serif'
fa, fj, out = sys.argv[1:4]
Hcm = float(sys.argv[4]) if len(sys.argv) > 4 else 10.0
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
r = rasterio.open(fa); d = list(r.descriptions); b = r.bounds; ext = (b.left, b.right, b.bottom, b.top)
n = r.read(d.index('agua_20231104') + 1) == 1; m = r.read(d.index('agua_20240514') + 1) == 1
rj = rasterio.open(fj); jrc = np.full(n.shape, np.nan, 'f4')
reproject(rj.read(1).astype('f4'), jrc, src_transform=rj.transform, src_crs=rj.crs, dst_transform=r.transform,
          dst_crs=r.crs, resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
cl = np.zeros(n.shape, 'u1'); cl[n & m] = 1; cl[n & ~m] = 2; cl[m & ~n] = 3; cl[jrc >= 90] = 4
cols = ['#f0f0f0', '#1a2a80', '#e6a100', '#3a8fd0', '#a9a9a9']
ha = lambda k: '{:,.0f}'.format((cl == k).sum() * 0.04).replace(',', '.')
L, T, B, R = 2.0, 0.7, 1.15, 9.6
ph = Hcm - T - B; pw = ph * (ext[1] - ext[0]) / (ext[3] - ext[2]); Wcm = L + pw + R
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM))
ax = fig.add_axes([L / Wcm, B / Hcm, pw / Wcm, ph / Hcm])
ax.imshow(cl, extent=ext, cmap=ListedColormap(cols), vmin=0, vmax=4, interpolation='nearest')
ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
ax.set_xticks([390000, 400000, 410000]); ax.set_yticks([6520000, 6530000, 6540000, 6550000])
ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
ax.tick_params(labelsize=10, length=3)
for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10.5, labelpad=6); ax.set_xlabel('Este, UTM 21S (m)', fontsize=10.5, labelpad=2)
p = ax.get_position()
hs = [Patch(fc=cols[1], ec='black', lw=0.5, label='Agua de inundación en las dos crecidas: %s ha' % ha(1)),
      Patch(fc=cols[2], ec='black', lw=0.5, label='Sólo el 04/11/2023: %s ha' % ha(2)),
      Patch(fc=cols[3], ec='black', lw=0.5, label='Sólo el 14/05/2024: %s ha' % ha(3)),
      Patch(fc=cols[4], ec='black', lw=0.5, label='Agua permanente (JRC ≥ 90 %, excluida)'),
      Patch(fc=cols[0], ec='black', lw=0.5, label='Sin agua de inundación')]
fig.legend(handles=hs, loc='center left', bbox_to_anchor=(p.x1 + 0.3 / Wcm, p.y0 + 0.55 * p.height), fontsize=10.5, frameon=False, labelspacing=0.7)
xn = 1 - 0.9 / Wcm
fig.add_artist(FancyArrow(xn, p.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                          head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, p.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
Lm = 10000; fw = Lm / (ext[1] - ext[0]) * p.width; xs = p.x1 + 0.4 / Wcm; ys = p.y0 + 0.3 / Hcm; hh = 0.2 / Hcm
sa = fig.add_axes([xs, ys, fw, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
for vv, t in ((0, '0'), (0.5, '5'), (1, '10 km')):
    fig.text(xs + vv * fw, ys + hh + 0.1 / Hcm, t, ha='center', va='bottom', fontsize=10.5)
fig.savefig(out, dpi=220); plt.close(fig)
print('ancho %.2f; ambas %s, nov %s, mayo %s' % (Wcm, ha(1), ha(2), ha(3)))
