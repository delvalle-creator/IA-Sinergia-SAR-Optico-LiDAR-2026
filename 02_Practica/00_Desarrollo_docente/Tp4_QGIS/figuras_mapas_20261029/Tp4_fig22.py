"""Figura 22 del Tp4: área estimada / área del mapa por clase de MapBiomas 2025, con el IC del 95 % (salida de Tp4_03)."""
import sys; sys.path.insert(0, '/mnt/user-data/outputs/tp3_mapas/scripts')
from com import *
import pandas as pd
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
d = pd.read_csv('/mnt/user-data/uploads/02_Practica/Tp4_Validacion/08_Orange/datos/Tp4_C_mapbiomas_exactitud_y_area.csv')
L = ['agua', 'humedal', 'monte', 'plantación', 'herbáceo,\ncultivo y\npastura', 'suelo\ndesnudo', 'urbano']
r = (d.area_estimada_ha / d.area_mapa_ha).values; lo = np.clip(d.area_estimada_ha - d.IC95_area_ha, 0, None) / d.area_mapa_ha; hi = (d.area_estimada_ha + d.IC95_area_ha) / d.area_mapa_ha
fuera = (lo > 1) | (hi < 1)
fig, ax = plt.subplots(figsize=(8.6, 4.3)); fig.subplots_adjust(left=0.1, right=0.98, top=0.9, bottom=0.27)
x = np.arange(7)
ax.bar(x, r, 0.6, color=np.where(fuera, '#d62728', '#9e9e9e'), ec='black', lw=0.8)
ax.errorbar(x, r, yerr=[r - lo, hi - r], fmt='none', ecolor='black', capsize=5, lw=1.3)
ax.axhline(1, ls='--', color='black', lw=1)
for i in range(7): ax.text(i, 1.01, num(r[i], 2), ha='center', va='bottom', fontsize=10.5, transform=ax.get_xaxis_transform())
ax.set_xticks(x); ax.set_xticklabels(L, fontsize=10.5); ax.set_ylabel('Área estimada / área del mapa'); ax.yaxis.set_major_formatter(fmt(1)); ax.grid(axis='y', alpha=0.3)
h = [Patch(fc='#d62728', ec='black', label='área del mapa fuera del IC del 95 %'), Patch(fc='#9e9e9e', ec='black', label='área del mapa dentro del IC'),
     Line2D([], [], ls='--', color='black', label='cociente 1 (sin sesgo)')]
fig.legend(handles=h, loc='lower center', ncol=3, frameon=False, fontsize=10.5, bbox_to_anchor=(0.54, 0.0))
print([round(v, 2) for v in r], [round(v, 2) for v in lo], [round(v, 2) for v in hi])
fig.savefig('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/hueco/t3f8/T4F22.png', dpi=250, bbox_inches='tight', pad_inches=0.05)
