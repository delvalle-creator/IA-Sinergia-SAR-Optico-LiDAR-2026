"""Figura 24 del Tp4: aciertos del ensayo por fuente del píxel y por confianza, con el intervalo de Wilson del 95 %."""
import sys; sys.path.insert(0, '/mnt/user-data/outputs/tp3_mapas/scripts')
from com import *
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h
A = [('JRC', 10, 10), ('polígonos\nsorteados', 42, 50), ('MapBiomas\nrecortado', 8, 10)]
B = [('alta', 35, 36), ('media', 18, 24), ('baja', 7, 10)]
fig, axs = plt.subplots(1, 2, figsize=(10.6, 3.7), sharey=True); fig.subplots_adjust(left=0.08, right=0.99, top=0.85, bottom=0.22, wspace=0.06)
for ax, D, t in ((axs[0], A, 'a) Por fuente del píxel en el mapa de control'), (axs[1], B, 'b) Por confianza de la etiqueta')):
    for i, (l, k, n) in enumerate(D):
        p, lo, hi = wilson(k, n); print(l, round(p, 2), round(lo, 2), round(hi, 2))
        ax.bar(i, p, 0.55, color='#9e9e9e', ec='black', lw=0.8)
        ax.errorbar(i, p, yerr=[[p - lo], [hi - p]], color='black', capsize=6, lw=1.4)
        ax.text(i, 1.01, num(p, 2), ha='center', va='bottom', fontsize=11, transform=ax.get_xaxis_transform())
    ax.set_xticks(range(3)); ax.set_xticklabels(['%s\n%d de %d' % d for d in D], fontsize=11)
    ax.set_ylim(0, 1.04); ax.set_title(t, loc='left', pad=20); ax.grid(axis='y', alpha=0.3); ax.yaxis.set_major_formatter(fmt(1))
axs[0].set_ylabel('Proporción de aciertos\n(en conteos)')
fig.text(0.53, 0.0, 'Barras: intervalo de Wilson del 95 % (proporción en conteos, no ponderada por área).', ha='center', fontsize=10.5)
fig.savefig('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/hueco/t3f8/T4F24.png', dpi=250, bbox_inches='tight', pad_inches=0.05)
