# Tp7 Figura 15 (31/10/2026): ICESat-2 ATL08 menos MDE, al tamano final (letras de 10 pt)
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D
plt.rcParams.update({'font.family': 'Liberation Serif', 'font.size': 10, 'axes.unicode_minus': True})
W, H = float(sys.argv[1]), float(sys.argv[2]); CM = 1/2.54
df = pd.read_csv('/mnt/user-data/uploads/CURSOS_CEREGEO_2026/02_Practica/00_COMUN/09_Herramientas/desarrollo_docente/Tp7/E1_control_mde_icesat2_segmentos.csv')
df = df[df.terreno_valido == True]
D = {'IGN': df.d_ign_srvn, 'GLO-30': df.dif_lidar_copdem, 'FABDEM': df.dif_lidar_fabdem}
COL = {'IGN': '#c0392b', 'GLO-30': '#2e86c1', 'FABDEM': '#28a745'}
coma = FuncFormatter(lambda v, p: ('%g' % v).replace('.', ',').replace('-', '−'))
miles = FuncFormatter(lambda v, p: '{:,.0f}'.format(v).replace(',', '.'))
fig, (a, b) = plt.subplots(1, 2, figsize=(W*CM, H*CM), gridspec_kw={'width_ratios': [1, 1.25]})
bins = np.arange(-10, 6.01, 0.25)
for k, v in D.items():
    v = v.dropna(); a.hist(v[(v >= -10) & (v <= 6)], bins=bins, histtype='step', lw=1.6, color=COL[k])
a.axvline(0, color='black', lw=0.9); a.set_xlim(-10, 6); a.set_xticks(range(-10, 7, 2))
a.set_xlabel('ICESat-2 ATL08 terreno − MDE (m)', labelpad=1); a.set_ylabel('segmentos de 100 m', labelpad=2)
a.xaxis.set_major_formatter(coma); a.yaxis.set_major_formatter(miles); a.set_title('(a) Todo el sitio, 2018–2026', pad=3)
datos, pos, cols, labs = [], [], [], []
for j, z in enumerate(['ladera', 'anillo', 'resto']):
    for i, k in enumerate(D):
        datos.append(D[k][df.zona == z].dropna()); pos.append(j*3.6 + i); cols.append(COL[k]); labs.append(k)
bp = b.boxplot(datos, positions=pos, widths=0.75, showfliers=False, patch_artist=True,
               medianprops=dict(color='black', lw=2.2), whiskerprops=dict(lw=1), capprops=dict(lw=1))
for p, c in zip(bp['boxes'], cols): p.set_facecolor(c); p.set_alpha(0.55); p.set_edgecolor('0.25')
b.axhline(0, color='black', lw=0.9)
b.set_xticks([1, 4.6, 8.2]); b.set_xticklabels(['ladera', 'anillo', 'resto del sitio'])
b.set_ylabel('ICESat-2 − MDE (m)', labelpad=2); b.yaxis.set_major_formatter(coma); b.set_title('(b) Por zona (sin valores extremos)', pad=3)
med = {k: np.median(D[k].dropna()) for k in D}; n = {k: D[k].notna().sum() for k in D}
nom = {'IGN': 'IGN 5 m', 'GLO-30': 'GLO-30', 'FABDEM': 'FABDEM'}
f = lambda x: ('%.2f' % x).replace('.', ',').replace('-', '−')
fig.legend(handles=[Line2D([], [], color=COL[k], lw=2.2, label='%s: mediana %s m (n = %s)' % (nom[k], f(med[k]), '{:,}'.format(n[k]).replace(',', '.'))) for k in D],
           loc='lower center', ncol=3, frameon=False, handlelength=1.4, columnspacing=1.0, borderaxespad=0.1)
fig.tight_layout(rect=(0, 0.07, 1, 1), w_pad=1.5)
fig.savefig('Tp7_Figura_15.png', dpi=300); print(med, n)
