"""Figura 20 del Tp4: banda P VH y CCI AGB 2024 por clase de referencia en los 70 puntos de MapBiomas 2025."""
import sys; sys.path.insert(0, '/mnt/user-data/outputs/tp3_mapas/scripts')
from com import *
import pandas as pd
d = pd.read_csv('/mnt/user-data/uploads/02_Practica/Tp4_Validacion/08_Orange/datos/Tp4_C_mapbiomas_puntos_con_llave.csv')
O = ['1 agua', '2 humedal', '3 monte', '4 plantacion', '5 cultivo/pastura', '6 suelo', '7 urbano', '8 otra']
print(sorted(d.clase_ref.unique()))
L = ['agua', 'humedal', 'monte', 'plantación', 'cultivo y pastura', 'suelo desnudo', 'urbano', 'otra (túneles)']
fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.3)); fig.subplots_adjust(left=0.07, right=0.99, top=0.93, bottom=0.2, wspace=0.18)
rng = np.random.default_rng(1)
for ax, col, t, yl in ((axs[0], 'P_VH_dB', 'a) BIOMASS banda P, VH, 22/07/2026', r'Banda P VH, $\gamma^0$ (dB)'), (axs[1], 'CCI_AGB_2024', 'b) CCI Biomass v7, AGB 2024', 'Biomasa aérea (Mg/ha)')):
    data = [d[d.clase_ref == k][col].dropna().values for k in O]
    b = ax.boxplot(data, widths=0.6, whis=(5, 95), showfliers=False, patch_artist=True, medianprops=dict(color='#c0392b', lw=1.8))
    for x in b['boxes']: x.set_facecolor('#e3e3e3')
    for i, v in enumerate(data):
        m = np.median(v); ax.text(i + 1, 1.01, num(m, 1 if col == 'P_VH_dB' else 0), color='#c0392b', ha='center', va='bottom', fontsize=10, transform=ax.get_xaxis_transform())
    ax.set_xticks(range(1, 9)); ax.set_xticklabels(['%s (%d)' % (l, len(v)) for l, v in zip(L, data)], fontsize=10.5, rotation=35, ha='right', rotation_mode='anchor')
    ax.set_title(t, loc='left', pad=20); ax.set_ylabel(yl); ax.grid(axis='y', alpha=0.3); ax.yaxis.set_major_formatter(fmt(0)); ax.set_xlim(0.4, 8.9)
    print(col, [round(float(np.median(v)), 1) for v in data])
fig.text(0.5, -0.06, 'Clase de referencia y, entre paréntesis, número de puntos; línea roja y número arriba: mediana; cajas: cuartiles; bigotes: percentiles 5 y 95.', ha='center', fontsize=10.5)
fig.savefig('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/hueco/t3f8/T4F20.png', dpi=250, bbox_inches='tight', pad_inches=0.05)
