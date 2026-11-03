# Tp5, Figura 14: distribucion de dVH (C), dHV (SAOCOM) y dNBR en lo no quemado y en lo quemado en ago-sep 2020
# (MapBiomas Fuego), sin el agua permanente. Rehecha el 30/10/2026 con letra del tamano del texto.
# Uso: python histogramas_umbral_Tp5.py <indicadores_20m.tif> <MapBiomas_fuego_mes_1999_2025.tif> <cobertura_control_20m.tif> <salida.png>
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from rasterio.warp import reproject, Resampling
plt.rcParams['font.family'] = 'Liberation Serif'
ind, mes, ctl, out = sys.argv[1:5]
I = rasterio.open(ind)
m = np.zeros(I.shape, 'f4'); M = rasterio.open(mes)
reproject(M.read(22).astype('f4'), m, src_transform=M.transform, src_crs=M.crs, dst_transform=I.transform, dst_crs=I.crs,
          resampling=Resampling.nearest, src_nodata=None)
agua = rasterio.open(ctl).read(1) == 1
nq = (m == 0) & ~agua; q = np.isin(m, (8, 9)) & ~agua
capas = [(1, 'ΔVH banda C (dB)', 1.0, (-11, 15)), (5, 'ΔHV SAOCOM banda L (dB)', 1.0, (-11, 16)), (8, 'dNBR Sentinel-2', 0.15, (-0.45, 0.82))]
CM = 1 / 2.54
fig, axs = plt.subplots(1, 3, figsize=(25 * CM, 8.2 * CM))
fig.subplots_adjust(left=0.035, right=0.99, top=0.97, bottom=0.33, wspace=0.12)
coma = matplotlib.ticker.FuncFormatter(lambda v, _: ('%g' % v).replace('.', ',').replace('-', '−'))
for ax, (b, tit, u, rg) in zip(axs, capas):
    x = I.read(b).astype('f4'); x[x == I.nodatavals[b - 1]] = np.nan; ok = np.isfinite(x)
    a, c = x[nq & ok], x[q & ok]
    bins = np.linspace(rg[0], rg[1], 120)
    ax.hist(a, bins, density=True, color='#7fb069', alpha=0.6, label='no quemado en 2020')
    ax.hist(c, bins, density=True, color='#e06c62', alpha=0.6, label='quemado en agosto y septiembre')
    ax.axvline(np.median(a), color='#3d7a2a', ls='--', lw=1.2); ax.axvline(np.median(c), color='#b03a2e', ls='--', lw=1.2)
    ax.axvline(u, color='black', lw=1.8, label='umbral elegido: 1 dB, 1 dB y 0,15')
    ax.set_xlim(rg); ax.set_yticks([]); ax.set_xlabel(tit, fontsize=12); ax.tick_params(labelsize=11)
    ax.xaxis.set_major_formatter(coma)
    print(tit, 'mediana no quemado %.2f, quemado %.2f, n=%d/%d' % (np.median(a), np.median(c), a.size, c.size))
h, l = axs[0].get_legend_handles_labels()
o = [0, 1, 2]
fig.legend([h[i] for i in o], [l[i] for i in o], loc='lower center', ncol=3, frameon=False, fontsize=11, bbox_to_anchor=(0.5, 0.0))
fig.savefig(out, dpi=220); print(out)
