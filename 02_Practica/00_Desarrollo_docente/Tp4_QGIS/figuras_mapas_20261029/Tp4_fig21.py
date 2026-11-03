"""Figura 21 del Tp4: exactitud del usuario y del productor de MapBiomas 2025 por clase (salida de Tp4_03)."""
import sys; sys.path.insert(0, '/mnt/user-data/outputs/tp3_mapas/scripts')
from com import *
import pandas as pd
d = pd.read_csv('/mnt/user-data/uploads/02_Practica/Tp4_Validacion/08_Orange/datos/Tp4_C_mapbiomas_exactitud_y_area.csv')
L = ['agua', 'humedal', 'monte', 'plantación', 'herbáceo,\ncultivo y\npastura', 'suelo\ndesnudo', 'urbano']
def wilson(k, n, z=1.96):
    p = k / n; dd = 1 + z * z / n; c = (p + z * z / (2 * n)) / dd; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / dd
    return c - h, c + h
fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.4), sharey=True); fig.subplots_adjust(left=0.07, right=0.99, top=0.93, bottom=0.24, wspace=0.06)
x = np.arange(7)
for ax, c, ic, t in ((axs[0], 'exactitud_usuario', 'IC95_usuario', 'a) Exactitud del usuario (1 − comisión)'), (axs[1], 'exactitud_productor', 'IC95_productor', 'b) Exactitud del productor (1 − omisión)')):
    v = d[c].values; e = d[ic].values; lo = np.clip(v - e, 0, 1); hi = np.clip(v + e, 0, 1)
    ax.bar(x, v, 0.6, color='#9e9e9e', ec='black', lw=0.8)
    ax.errorbar(x, v, yerr=[v - lo, hi - v], fmt='none', ecolor='black', capsize=5, lw=1.3)
    for i in range(7): ax.text(i, 1.01, num(v[i], 2), fontsize=10.5, ha='center', va='bottom', transform=ax.get_xaxis_transform())
    if c == 'exactitud_usuario':
        for i in range(7):
            a, b = wilson(round(v[i] * 10), 10)
            ax.plot([i - 0.18, i + 0.18], [a, a], color='#d62728', lw=2); ax.plot([i - 0.18, i + 0.18], [b, b], color='#d62728', lw=2)
    ax.set_xticks(x); ax.set_xticklabels(L, fontsize=10.5); ax.set_ylim(0, 1.04); ax.set_title(t, loc='left', pad=20); ax.grid(axis='y', alpha=0.3)
    ax.yaxis.set_major_formatter(fmt(1))
axs[0].set_ylabel('Exactitud (0 a 1)')
from matplotlib.lines import Line2D
h = [Line2D([], [], color='black', marker='_', ms=10, lw=1.3, label='IC del 95 % (aproximación normal, truncado en 0 y 1)'),
     Line2D([], [], color='#d62728', lw=2, label='intervalo de Wilson del usuario (95 %)')]
fig.legend(handles=h, loc='lower center', ncol=2, frameon=False, fontsize=10.5, bbox_to_anchor=(0.5, 0.0))
fig.savefig('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/hueco/t3f8/T4F21.png', dpi=250, bbox_inches='tight', pad_inches=0.05)
