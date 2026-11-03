# Tp5, Figura 15: los cuatro histogramas que guarda Tp5_02 (99 % central; las barras de los extremos acumulan
# el 0,5 % de cada lado) con el umbral manual. Rehecha el 30/10/2026 en una fila, con letra del tamano del texto.
# Uso: python histogramas_Tp5_02.py <A1_DELTA_QUEMAS_indicadores_20m.tif> <salida.png>
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Liberation Serif'
I = rasterio.open(sys.argv[1])
capas = [(1, '(a) ΔVH banda C (dB)', 1.0, '< 1'), (3, '(b) ΔHV ALOS-2 (dB)', -2.0, '< −2'),
         (5, '(c) ΔHV SAOCOM (dB)', 1.0, '< 1'), (8, '(d) dNBR Sentinel-2', 0.15, '> 0,15')]
CM = 1 / 2.54
fig, axs = plt.subplots(1, 4, figsize=(25.5 * CM, 7.4 * CM))
fig.subplots_adjust(left=0.075, right=0.99, top=0.82, bottom=0.12, wspace=0.3)
miles = matplotlib.ticker.FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
coma = matplotlib.ticker.FuncFormatter(lambda v, _: ('%g' % v).replace('.', ',').replace('-', '−'))
for k, (ax, (b, tit, u, ut)) in enumerate(zip(axs, capas)):
    x = I.read(b).astype('f8'); x = x[(x != I.nodatavals[b - 1]) & np.isfinite(x)]
    lo, hi = np.percentile(x, [0.5, 99.5]); xc = np.clip(x, lo, hi)
    ax.hist(xc, np.linspace(lo, hi, 150), color='#1f3a73')
    ax.axvline(u, color='#e67e22', lw=1.8)
    ax.set_title(tit + '\numbral ' + ut, fontsize=11)
    ax.tick_params(labelsize=10.5); ax.xaxis.set_major_formatter(coma); ax.yaxis.set_major_formatter(miles)
    ax.locator_params(axis='x', nbins=5); ax.locator_params(axis='y', nbins=4)
    if k == 0: ax.set_ylabel('píxeles', fontsize=11)
    print(tit, 'rango %.2f a %.2f, n=%d' % (lo, hi, x.size))
fig.savefig(sys.argv[2], dpi=220); print(sys.argv[2])
