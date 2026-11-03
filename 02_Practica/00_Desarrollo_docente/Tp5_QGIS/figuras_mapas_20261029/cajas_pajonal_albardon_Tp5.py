# Tp5, Figura 18: dVH (C), dHV SAOCOM y dHV ALOS-2 en pajonal (CCI AGB 2020 < 15 Mg/ha) y albardon (>= 30 Mg/ha),
# quemado en ago-sep 2020 y no quemado en 2020 (MapBiomas Fuego), sin agua permanente. Cajas P25-P75, linea en la
# mediana, bigotes a 1,5 veces la caja. Rehecha el 30/10/2026 con letra del tamano del texto.
# Uso: python cajas_pajonal_albardon_Tp5.py <indicadores_20m.tif> <MapBiomas_fuego_mes.tif> <CCI_Biomass_v7_AGB.tif> <cobertura_control_20m.tif> <salida.png> [alto_cm]
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from rasterio.warp import reproject, Resampling
plt.rcParams['font.family'] = 'Liberation Serif'
ind, mes, cci, ctl, out = sys.argv[1:6]; H = float(sys.argv[6]) if len(sys.argv) > 6 else 7.0
I = rasterio.open(ind)
def a_grilla(f, b, nd=None):
    s = rasterio.open(f); o = np.full(I.shape, np.nan, 'f4'); x = s.read(b).astype('f4')
    if nd is not None: x[x == nd] = np.nan
    reproject(x, o, src_transform=s.transform, src_crs=s.crs, dst_transform=I.transform, dst_crs=I.crs,
              resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
    return o
m = a_grilla(mes, 22); agb = a_grilla(cci, 3, 65535)
agua = rasterio.open(ctl).read(1) == 1
q = np.isin(m, (8, 9)) & ~agua; nq = (m == 0) & ~agua
paj = agb < 15; alb = agb >= 30
grupos = [('pajonal\nno quemado', paj & nq, '#b5e08a'), ('pajonal\nquemado', paj & q, '#f2b6da'),
          ('albardón\nno quemado', alb & nq, '#4d921e'), ('albardón\nquemado', alb & q, '#c51b7d')]
capas = [(1, '(a) ΔVH banda C (dB)'), (5, '(b) ΔHV SAOCOM, banda L (dB)'), (3, '(c) ΔHV ALOS-2, banda L (dB)')]
CM = 1 / 2.54
fig, axs = plt.subplots(1, 3, figsize=(25 * CM, H * CM))
fig.subplots_adjust(left=0.04, right=0.995, top=0.9, bottom=0.27, wspace=0.16)
coma = lambda v: ('%.1f' % v).replace('.', ',').replace('-', '−')
for ax, (b, tit) in zip(axs, capas):
    x = I.read(b).astype('f4'); x[x == I.nodatavals[b - 1]] = np.nan
    datos = [x[g & np.isfinite(x)] for _, g, _ in grupos]
    bp = ax.boxplot(datos, widths=0.6, showfliers=False, patch_artist=True, medianprops=dict(color='black', lw=1.6))
    for p, (_, _, c) in zip(bp['boxes'], grupos): p.set_facecolor(c)
    for i, d in enumerate(datos):
        md = np.median(d); q3 = np.percentile(d, 75)
        ax.text(i + 1, q3, coma(md), ha='center', va='bottom', fontsize=10.5, fontweight='bold',
                bbox=dict(facecolor='white', edgecolor='none', pad=0.5))
        print(tit, grupos[i][0].replace('\n', ' '), 'mediana %.2f n=%d' % (md, d.size))
    ax.axhline(0, color='0.6', lw=0.8); ax.set_title(tit, fontsize=11.5); ax.set_xlim(0.45, 4.55)
    ax.set_xticks([1, 2, 3, 4]); ax.set_xticklabels(['no\nquemado', 'quemado', 'no\nquemado', 'quemado'], fontsize=10.5)
    for xx, t in ((1.5, 'pajonal'), (3.5, 'albardón')):
        ax.annotate(t, (xx, 0), xycoords=('data', 'axes fraction'), xytext=(0, -38), textcoords='offset points', ha='center', va='top', fontsize=11, fontweight='bold')
    ax.axvline(2.5, color='0.75', lw=0.8)
    ax.tick_params(axis='y', labelsize=10.5)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: ('%g' % v).replace('-', '−')))
    ax.locator_params(axis='y', nbins=5); ax.grid(axis='y', alpha=0.3)
fig.savefig(out, dpi=220); print(out)
