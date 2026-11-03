"""Figura 19 del Tp4: aciertos de MapBiomas 2025 por confianza de la etiqueta, con el intervalo de Wilson del 95 %."""
import sys; sys.path.insert(0, '/mnt/user-data/outputs/tp3_mapas/scripts')
from com import *
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h
D = [('alta', 22, 27), ('media', 12, 27), ('baja', 1, 16)]
fig, ax = plt.subplots(figsize=(8.0, 3.4)); fig.subplots_adjust(left=0.1, right=0.98, top=0.95, bottom=0.2)
for i, (l, k, n) in enumerate(D):
    p, lo, hi = wilson(k, n)
    ax.bar(i, p, 0.55, color='#9e9e9e', ec='black', lw=0.8)
    ax.errorbar(i, p, yerr=[[p - lo], [hi - p]], color='black', capsize=6, lw=1.4)
    ax.text(i + 0.3, p, num(p, 2), va='center', ha='left', fontsize=11)
    print(l, round(p, 3), round(lo, 3), round(hi, 3))
ax.set_xticks(range(3)); ax.set_xticklabels(['%s\n%d de %d' % d for d in D], fontsize=11)
ax.set_ylim(0, 1.05); ax.yaxis.set_major_formatter(fmt(1)); ax.set_ylabel('Proporción de aciertos\n(en conteos)')
ax.set_xlabel('Confianza de la etiqueta; barras: intervalo de Wilson del 95 %'); ax.grid(axis='y', alpha=0.3); ax.set_xlim(-0.6, 2.8)
fig.savefig('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/hueco/t3f8/T4F19.png', dpi=250, bbox_inches='tight', pad_inches=0.05)
