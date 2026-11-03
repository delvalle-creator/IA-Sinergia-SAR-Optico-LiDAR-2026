# Tp6, Figura 15: histograma del MNDWI = (B03 - B11)/(B03 + B11) del Sentinel-2 del 04/11/2023 a 20 m, sin nubes,
# en todo el sitio (a, escala logaritmica) y por ocurrencia de agua JRC (b), con el umbral manual de 0.
# Reflectancias del GeoTIFF del curso (10 m, L2A, reflectancia = (DN - 1000)/10000 por la linea de base 05.09); B03 y B11 se promedian en bloques de 2 x 2 (20 m). Nubes, sombras y
# sin dato (SCL 0, 3, 8, 9, 10) se excluyen. Letras Times a tamano de texto. 30/10/2026.
# Uso: python grafico_tp6_f15.py <B_CONCORDIA_S2_20231104.tif> <B_CONCORDIA_JRC_GSW_ocurrencia.tif> <salida.png>
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from rasterio.warp import reproject, Resampling
from rasterio.transform import Affine
plt.rcParams['font.family'] = 'Liberation Serif'
fs, fj, out = sys.argv[1:4]
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
coma = FuncFormatter(lambda v, _: ('%g' % v).replace('.', ','))
r = rasterio.open(fs); d = list(r.descriptions)
H, W = (r.height // 2) * 2, (r.width // 2) * 2
def b20(n, f=np.mean):
    a = r.read(d.index(n) + 1)[:H, :W].astype('f4'); a = np.where(a > 0, (a - 1000) / 10000, np.nan)  # L2A base 05.09: BOA_ADD_OFFSET = -1000
    return a.reshape(H // 2, 2, W // 2, 2)
b3, b11 = np.nanmean(b20('B03'), (1, 3)), np.nanmean(b20('B11'), (1, 3))
scl = r.read(d.index('SCL') + 1)[:H, :W].reshape(H // 2, 2, W // 2, 2)
malo = np.isin(scl, [0, 3, 8, 9, 10]).any((1, 3))
mndwi = np.where(malo | ~(b3 + b11 > 0), np.nan, (b3 - b11) / (b3 + b11))
tr = r.transform * Affine.scale(2)
rj = rasterio.open(fj); jrc = np.full(mndwi.shape, np.nan, 'f4')
reproject(rj.read(1).astype('f4'), jrc, src_transform=rj.transform, src_crs=rj.crs, dst_transform=tr, dst_crs=r.crs,
          resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
v = np.isfinite(mndwi)
print('validos %.1f %%; MNDWI > 0: %.1f %% de los validos' % (100 * v.mean(), 100 * np.mean(mndwi[v] > 0)))
bins = np.linspace(-0.8, 0.8, 161)
fig = plt.figure(figsize=(25.0 * CM, 6.0 * CM))
a = fig.add_axes([2.6 / 25, 1.85 / 6.0, 9.4 / 25, 3.5 / 6.0]); bx = fig.add_axes([14.4 / 25, 1.85 / 6.0, 9.4 / 25, 3.5 / 6.0])
a.hist(np.clip(mndwi[v], -0.8, 0.8), bins=bins, color='#1f3a73')
a.set_yscale('log'); a.set_yticks([10, 1000, 100000]); a.yaxis.set_major_formatter(miles)
a.set_ylabel('Píxeles (escala log.)', fontsize=10.5); a.set_title('(a) Todo el sitio', fontsize=11.5, pad=4)
grupos = [(jrc >= 90, 'Agua permanente (JRC ≥ 90 %)', '#08306b'), ((jrc >= 1) & (jrc < 90), 'JRC 1 a 89 %', '#41b6c4'),
          (jrc == 0, 'JRC = 0 (tierra)', '#b8860b')]
for m, lab, c in grupos:
    bx.hist(np.clip(mndwi[v & m], -0.8, 0.8), bins=bins, density=True, histtype='step', lw=1.6, color=c, label=lab)
bx.set_ylabel('Densidad', fontsize=10.5); bx.set_title('(b) Por ocurrencia de agua JRC', fontsize=11.5, pad=4)
for ax in (a, bx):
    ax.axvline(0, color='#d95f02', lw=1.6); ax.set_xlim(-0.85, 0.85); ax.set_xlabel('MNDWI', fontsize=10.5, labelpad=2)
    ax.xaxis.set_major_formatter(coma); ax.tick_params(labelsize=10); ax.grid(alpha=0.3, lw=0.5)
a.text(0.02, 0.97, 'umbral manual: 0', transform=a.get_xaxis_transform(), color='#d95f02', fontsize=10.5, va='top')
h, l = bx.get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=3, fontsize=10.5, frameon=False, bbox_to_anchor=(0.5, 0.0))
fig.savefig(out, dpi=220); plt.close(fig)
