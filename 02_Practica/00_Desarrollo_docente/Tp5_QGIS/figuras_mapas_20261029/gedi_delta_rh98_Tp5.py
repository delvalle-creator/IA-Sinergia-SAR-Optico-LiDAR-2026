# Tp5, Figura 28: delta rh98 por celda de 100 m (misma estacion antes y despues) segun altura previa y clase de la V4,
# desde A1_delta_rh98_por_celda.csv (Tp5_04). Rehecha el 30/10/2026 con letra del tamano del texto.
import sys, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Liberation Serif'
d = pd.read_csv(sys.argv[1], encoding='utf-8-sig'); alto = d.median_antes >= 3
G = [('< 3 m\nquemado V4', ~alto & (d.clase_mapa == 1), '#e8996f'),
     ('< 3 m\nno quemado V4', ~alto & (d.clase_mapa == 2), '#9cc68e'),
     ('≥ 3 m\nquemado V4', alto & (d.clase_mapa == 1), '#c0392b'),
     ('≥ 3 m\nno quemado V4', alto & (d.clase_mapa == 2), '#2e7d40'),
     ('≥ 3 m\nsin dato en V4', alto & d.clase_mapa.isna(), '#a6a6a6')]
CM = 1 / 2.54
fig, ax = plt.subplots(figsize=(19 * CM, 10.5 * CM)); fig.subplots_adjust(left=0.1, right=0.98, top=0.97, bottom=0.22)
dat = [d.delta_rh98_m[s].values for _, s, _ in G]
bp = ax.boxplot(dat, widths=0.55, patch_artist=True, medianprops=dict(color='black', lw=1.6),
                flierprops=dict(marker='o', ms=3, mfc='none', mec='0.4'))
for b, (_, _, c) in zip(bp['boxes'], G): b.set_facecolor(c)
f = lambda v: ('%.2f' % v).replace('.', ',').replace('-', '−')
for i, x in enumerate(dat):
    ax.text(i + 1.32, pd.Series(x).median(), f(pd.Series(x).median()), va='center', fontsize=11, fontweight='bold')
ax.axhline(0, color='0.5', ls='--', lw=0.8)
ax.set_xticks(range(1, 6)); ax.set_xticklabels(['%s\n(n = %d)' % (g, len(x)) for (g, _, _), x in zip(G, dat)], fontsize=11)
ax.set_xlim(0.5, 5.75); ax.set_ylim(-2, 2); ax.set_ylabel('Δrh98 (m)', fontsize=12); ax.tick_params(axis='y', labelsize=11)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: ('%.1f' % v).replace('.', ',').replace('-', '−')))
ax.grid(axis='y', alpha=0.3)
fig.savefig(sys.argv[2], dpi=220); print([len(x) for x in dat])
