# Tp6, Figura 10: distribucion de VV (a) y VH (b) del 04/11/2023 en tres grupos de pixeles (muestra de 10.000 por grupo),
# con los umbrales de Otsu (-9,5 dB) y manual (-15 dB) en (a). Letras en Times (Liberation Serif) a tamano de texto. 30/10/2026.
# Uso: python grafico_tp6_f10.py <Tp6_A_muestra_pixeles.csv> <salida.png>
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
plt.rcParams['font.family'] = 'Liberation Serif'; plt.rcParams['axes.unicode_minus'] = True
f, out = sys.argv[1:3]
d = pd.read_csv(f)
CM = 1 / 2.54
coma = FuncFormatter(lambda v, _: ('%.2f' % v).replace('.', ','))
grupos = [('agua permanente (JRC >= 90 %)', 'Agua permanente\n(JRC ≥ 90 %)', '#08306b'),
          ('agua de inundacion segun el optico', 'Agua de inundación\nsegún el óptico', '#41b6c4'),
          ('resto del sitio', 'Resto del sitio', '#b8860b')]
fig = plt.figure(figsize=(25.0 * CM, 5.3 * CM))
bins = np.arange(-32, 6.01, 0.5)
axs = [fig.add_axes([1.9 / 25, 1.2 / 5.3, 7.6 / 25, 3.55 / 5.3]), fig.add_axes([10.6 / 25, 1.2 / 5.3, 7.6 / 25, 3.55 / 5.3])]
for ax, col, t in zip(axs, ['VV_dB', 'VH_dB'], ['(a) VV', '(b) VH']):
    for g, lab, c in grupos:
        ax.hist(d.loc[d.grupo == g, col], bins=bins, density=True, histtype='step', lw=1.6, color=c, label=lab)
    ax.set_xlim(-32, 5); ax.set_ylim(0, 0.30); ax.set_yticks([0, 0.1, 0.2, 0.3]); ax.yaxis.set_major_formatter(coma)
    ax.set_xlabel('dB', fontsize=11, labelpad=2); ax.set_title(t, fontsize=11.5, pad=4)
    ax.tick_params(labelsize=10.5); ax.grid(alpha=0.3, lw=0.5)
axs[0].set_ylabel('Densidad', fontsize=11)
axs[1].set_yticklabels([])
a = axs[0]
a.axvline(-15, color='#d62728', lw=1.4); a.axvline(-9.488, color='#ff7f0e', lw=1.4, ls=':')
a.text(-15.4, 0.285, 'manual −15 dB', color='#d62728', ha='right', va='top', fontsize=10.5)
a.text(-9.0, 0.285, 'Otsu −9,5 dB', color='#ff7f0e', ha='left', va='top', fontsize=10.5)
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, loc='center left', bbox_to_anchor=(18.6 / 25, 0.55), fontsize=10.5, frameon=False, handlelength=1.6, labelspacing=0.8)
fig.savefig(out, dpi=220); plt.close(fig)
