# Tp6, Figura 24: profundidad sin recortar a 0 (banda profundidad_sin_recortar_m de Tp6_04_profundidad.py):
# (a) histograma con el Copernicus DEM y con FABDEM (valores menores de -4 m y mayores de 6 m acumulados en las barras de
# los bordes); (b) distribucion por clase de MapBiomas 2023 (banda 39) con el Copernicus DEM (caja: cuartiles; bigotes:
# percentiles 5 y 95). MapBiomas se pasa a la grilla de 20 m por vecino mas cercano. Letras Times a tamano de texto. 30/10/2026.
# Uso: python grafico_tp6_f24.py <prof_copernicus.tif> <prof_fabdem.tif> <MapBiomas_cobertura_1985_2025.tif> <salida.png>
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from rasterio.warp import reproject, Resampling
plt.rcParams['font.family'] = 'Liberation Serif'
fa, fb, fm, out = sys.argv[1:5]
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
coma = FuncFormatter(lambda v, _: ('%g' % v).replace('.', ',').replace('-', '−'))
def prof(f):
    r = rasterio.open(f); d = list(r.descriptions); a = r.read(d.index('profundidad_sin_recortar_m') + 1).astype('f4')
    a[a == r.nodata] = np.nan; return a, r
pa, r = prof(fa); pb, _ = prof(fb)
m = rasterio.open(fm); mb = np.zeros(pa.shape, 'u1')
reproject(m.read(39), mb, src_transform=m.transform, src_crs=m.crs, dst_transform=r.transform, dst_crs=r.crs,
          resampling=Resampling.nearest, src_nodata=0, dst_nodata=0)
fig = plt.figure(figsize=(25.0 * CM, 9.6 * CM))
a1 = fig.add_axes([2.2 / 25, 1.7 / 9.6, 8.0 / 25, 6.9 / 9.6]); a2 = fig.add_axes([12.0 / 25, 2.6 / 9.6, 12.7 / 25, 6.0 / 9.6])
bins = np.arange(-4, 6.01, 0.1)
for p, lab, c in [(pa, 'Copernicus DEM', '#1f77b4'), (pb, 'FABDEM', '#e6550d')]:
    v = np.clip(p[np.isfinite(p)], -4, 6)
    a1.hist(v, bins=bins, histtype='step', lw=1.5, color=c, label=lab)
a1.axvline(0, color='black', lw=0.8)
a1.yaxis.set_major_formatter(miles); a1.xaxis.set_major_formatter(coma)
a1.set_xlabel('Profundidad sin recortar (m)', fontsize=10.5); a1.set_ylabel('Píxeles de 20 m', fontsize=10.5)
a1.set_title('(a) Histograma (extremos en los bordes)', fontsize=11, pad=4)
a1.legend(fontsize=10, frameon=False, loc='upper right'); a1.tick_params(labelsize=10); a1.grid(alpha=0.3, lw=0.5)
cl = [(11, 'Herb.\ninund.'), (12, 'Herbá-\nceas'), (19, 'Cult.\ntemp.'), (4, 'Bosq.\nabiertos'), (3, 'Bosq.\ncerrados'),
      (24, 'Áreas\nurbanas'), (9, 'Silvi-\ncultura'), (36, 'Cult.\nperennes')]
stats, labs = [], []
for c, n in cl:
    v = pa[(mb == c) & np.isfinite(pa)]
    q5, q25, q50, q75, q95 = np.percentile(v, [5, 25, 50, 75, 95])
    stats.append(dict(med=q50, q1=q25, q3=q75, whislo=q5, whishi=q95, fliers=[]))
    labs.append('%s\n%s' % (n, '{:,}'.format(v.size).replace(',', '.')))
    print(n.replace('\n', ' '), v.size, round(q50, 2))
a2.bxp(stats, showfliers=False, widths=0.6, medianprops=dict(color='#e6550d', lw=1.6))
a2.axhline(0, color='black', lw=0.8)
a2.set_xticks(range(1, len(labs) + 1)); a2.set_xticklabels(labs, fontsize=9.5)
a2.yaxis.set_major_formatter(coma); a2.tick_params(axis='y', labelsize=10)
a2.set_ylabel('Profundidad sin recortar (m)', fontsize=10.5); a2.set_xlabel('Clase y número de píxeles', fontsize=10.5, labelpad=3)
a2.set_title('(b) Por clase de MapBiomas 2023, Copernicus DEM', fontsize=11, pad=4); a2.grid(axis='y', alpha=0.3, lw=0.5)
fig.savefig(out, dpi=220); plt.close(fig)
