# Tp6, Figura 12: agua de inundacion en banda C el 04/11/2023, el 28/11/2023 y el 14/05/2024, desde
# B_agua_C_por_fecha_20m.tif (salida de Tp6_01_serie_agua_C.py, una banda 1/0 por fecha) y el agua permanente
# JRC >= 90 % reproyectada a la misma grilla. Coordenadas UTM 21S en metros, una sola flecha norte en el esquinero
# superior derecho y escala grafica horizontal al costado. 30/10/2026.
# Uso: python mapas_tp6_f12.py <B_agua_C_por_fecha_20m.tif> <B_CONCORDIA_JRC_GSW_ocurrencia.tif> <salida.png>
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap
from rasterio.warp import reproject, Resampling
plt.rcParams['font.family'] = 'Liberation Serif'
fa, fj, out = sys.argv[1:4]
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
r = rasterio.open(fa); dsc = list(r.descriptions); b = r.bounds
ext = (b.left, b.right, b.bottom, b.top)
rj = rasterio.open(fj); jrc = np.full((r.height, r.width), np.nan, 'f4')
reproject(rj.read(1).astype('f4'), jrc, src_transform=rj.transform, src_crs=rj.crs, dst_transform=r.transform,
          dst_crs=r.crs, resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
perm = jrc >= 90
cm = ListedColormap(['#f0f0f0', '#1f6fb4', '#a9a9a9'])
fechas = [('agua_20231104', '(a) 04/11/2023'), ('agua_20231128', '(b) 28/11/2023'), ('agua_20240514', '(c) 14/05/2024')]
Wcm, Hcm = 25.4, 10.4
L, T, B, gap, R = 2.0, 0.7, 2.0, 0.35, 2.9
ph = Hcm - T - B; asp = (ext[1] - ext[0]) / (ext[3] - ext[2]); pw = ph * asp
tot = L + 3 * pw + 2 * gap + R
if tot > Wcm:
    pw = (Wcm - L - R - 2 * gap) / 3; ph = pw / asp; Hcm = ph + T + B
x0 = (Wcm - (L + 3 * pw + 2 * gap + R)) / 2 + L
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM)); axs = []
for k, (bn, t) in enumerate(fechas):
    a = r.read(dsc.index(bn) + 1)
    cl = np.where(a == 1, 1, 0); cl[perm] = 2
    ha = (a == 1).sum() * 400 / 1e4
    ax = fig.add_axes([(x0 + k * (pw + gap)) / Wcm, B / Hcm, pw / Wcm, ph / Hcm])
    ax.imshow(cl, extent=ext, cmap=cm, vmin=0, vmax=2, interpolation='nearest')
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_xticks([390000, 400000, 410000]); ax.set_yticks([6520000, 6530000, 6540000, 6550000])
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.tick_params(labelsize=10, length=3)
    for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    if k: ax.set_yticklabels([])
    else: ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10.5, labelpad=6)
    ax.set_xlabel('Este, UTM 21S (m)', fontsize=10.5, labelpad=2)
    ax.set_title('%s: %s ha' % (t, '{:,.0f}'.format(ha).replace(',', '.')), fontsize=11.5, pad=4); axs.append(ax)
bb = axs[-1].get_position()
xn = 1 - 0.9 / Wcm
fig.add_artist(FancyArrow(xn, bb.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                          head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, bb.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
Lm = 10000; fw = Lm / (ext[1] - ext[0]) * bb.width; xs = bb.x1 + 0.4 / Wcm; ys = bb.y0 + 0.5 / Hcm; hh = 0.2 / Hcm
sa = fig.add_axes([xs, ys, fw, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
for vv, t in ((0, '0'), (0.5, '5'), (1, '10 km')):
    fig.text(xs + vv * fw, ys + hh + 0.1 / Hcm, t, ha='center', va='bottom', fontsize=10.5)
hs = [Patch(fc='#1f6fb4', ec='black', lw=0.5, label='Agua de inundación'),
      Patch(fc='#a9a9a9', ec='black', lw=0.5, label='Agua permanente (JRC ≥ 90 %, excluida)'),
      Patch(fc='#f0f0f0', ec='black', lw=0.5, label='Sin agua de inundación')]
fig.legend(handles=hs, loc='lower center', ncol=3, fontsize=10.5, frameon=False, bbox_to_anchor=(0.5, 0.0))
fig.savefig(out, dpi=220); plt.close(fig)
print('alto %.2f cm' % Hcm)
