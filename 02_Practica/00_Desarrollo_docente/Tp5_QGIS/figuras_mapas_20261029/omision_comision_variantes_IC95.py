# Tp5, Figura 27: omision y comision de quemado por variante con IC 95 % (valores de tabla_de_variantes_quemado.csv,
# salida de Tp4_04; Tabla 12). Rehecha el 30/10/2026 con letra del tamano del texto.
import sys, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, numpy as np
plt.rcParams['font.family'] = 'Liberation Serif'
var = ['V1 óptico solo', 'V2 SAR solo (C)', 'V3 SAR multibanda', 'V4 multisensor']
om = [(0.244, 0.099), (0.546, 0.094), (0.778, 0.083), (0.254, 0.103)]
co = [(0.138, 0.090), (0.327, 0.129), (0.630, 0.141), (0.207, 0.105)]
CM = 1 / 2.54
fig, ax = plt.subplots(figsize=(19 * CM, 10.5 * CM)); fig.subplots_adjust(left=0.1, right=0.99, top=0.97, bottom=0.2)
x = np.arange(4); w = 0.36
c = lambda v: ('%.2f' % v).replace('.', ',')
for dx, d, col, lab in ((-w / 2, om, '#c9564b', 'omisión de quemado'), (w / 2, co, '#4a7fb0', 'comisión de quemado')):
    v = [a for a, _ in d]; e = [b for _, b in d]
    ax.bar(x + dx, v, w, color=col, label=lab, yerr=e, capsize=4, error_kw=dict(lw=1.4))
    for xi, a, b in zip(x + dx, v, e): ax.text(xi, a + b + 0.02, c(a), ha='center', va='bottom', fontsize=11)
ax.set_xticks(x); ax.set_xticklabels(var, fontsize=12); ax.set_ylim(0, 1.02)
ax.set_ylabel('proporción (barra de error = IC 95 %)', fontsize=12); ax.tick_params(axis='y', labelsize=11)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: ('%.1f' % v).replace('.', ',')))
ax.grid(axis='y', alpha=0.3)
fig.legend(loc='lower center', ncol=2, frameon=False, fontsize=12, bbox_to_anchor=(0.55, 0.0))
fig.savefig(sys.argv[1], dpi=220); print(sys.argv[1])
