# Tp6, Figura 7: CCI Biomass v7, biomasa aerea 2024 (AGB_2024) y su desvio estandar (AGB_SD_2024), Concordia.
# Reproyectado a UTM 21S (vecino mas cercano, 100 m). Cada panel con su barra de colores; norte en el esquinero
# superior derecho y escala grafica horizontal al costado. 30/10/2026.
# Uso: python mapas_tp6_f7.py <B_CONCORDIA_CCI_Biomass_v7_AGB.tif> <salida.png>
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow
from rasterio.warp import calculate_default_transform, reproject, Resampling
plt.rcParams['font.family'] = 'Liberation Serif'
fc, out = sys.argv[1:3]
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
r = rasterio.open(fc); d = list(r.descriptions)
dst = 'EPSG:32721'
tr, w, h = calculate_default_transform(r.crs, dst, r.width, r.height, *r.bounds, resolution=100)
def capa(nombre):
    o = np.full((h, w), np.nan, 'f4')
    reproject(r.read(d.index(nombre) + 1).astype('f4'), o, src_transform=r.transform, src_crs=r.crs, dst_transform=tr,
              dst_crs=dst, resampling=Resampling.nearest, dst_nodata=np.nan)
    return o
agb, sd = capa('AGB_2024'), capa('AGB_SD_2024')
ext = (tr.c, tr.c + w * tr.a, tr.f + h * tr.e, tr.f)
Wcm, Hcm = 25.4, 10.0
L, T, B, gap, R = 2.0, 0.7, 1.15, 2.7, 5.4
ph = Hcm - T - B; asp = (ext[1] - ext[0]) / (ext[3] - ext[2]); pw = ph * asp
x0 = (Wcm - (L + 2 * pw + gap + R)) / 2 + L
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM)); axs = []
spec = [(agb, 'Greens', 150, '(a) Biomasa aérea 2024', 'Mg/ha', [0, 50, 100, 150]),
        (sd, 'Oranges', 60, '(b) Desvío estándar 2024', 'Mg/ha', [0, 20, 40, 60])]
for k, (a, cm, vmax, t, u, tk) in enumerate(spec):
    ax = fig.add_axes([(x0 + k * (pw + gap)) / Wcm, B / Hcm, pw / Wcm, ph / Hcm])
    im = ax.imshow(np.ma.masked_invalid(a), extent=ext, cmap=cm, vmin=0, vmax=vmax, interpolation='nearest')
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_xticks([390000, 400000, 410000]); ax.set_yticks([6520000, 6530000, 6540000, 6550000])
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.tick_params(labelsize=10, length=3)
    for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    if k: ax.set_yticklabels([])
    else: ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10.5, labelpad=6)
    ax.set_xlabel('Este, UTM 21S (m)', fontsize=10.5, labelpad=2)
    ax.set_title(t, fontsize=11.5, pad=4); axs.append(ax)
    p = ax.get_position()
    cax = fig.add_axes([p.x1 + 0.35 / Wcm, p.y0 + 0.3 / Hcm, 0.35 / Wcm, p.height - 1.3 / Hcm])
    cb = fig.colorbar(im, cax=cax, ticks=tk, extend='max'); cb.ax.tick_params(labelsize=10)
    cb.ax.set_title(u, fontsize=10.5, pad=5)
b = axs[-1].get_position(); xr = b.x1 + 2.3 / Wcm
xn = 1 - 0.9 / Wcm
fig.add_artist(FancyArrow(xn, b.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                          head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, b.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
Lm = 10000; fw = Lm / (ext[1] - ext[0]) * b.width; xs = xr; ys = b.y0 + 0.5 / Hcm; hh = 0.2 / Hcm
sa = fig.add_axes([xs, ys, fw, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
for vv, t in ((0, '0'), (0.5, '5'), (1, '10 km')):
    fig.text(xs + vv * fw, ys + hh + 0.1 / Hcm, t, ha='center', va='bottom', fontsize=10.5)
fig.savefig(out, dpi=220); plt.close(fig)
print('AGB p99 %.0f, SD p99 %.0f' % (np.nanpercentile(agb, 99), np.nanpercentile(sd, 99)))
