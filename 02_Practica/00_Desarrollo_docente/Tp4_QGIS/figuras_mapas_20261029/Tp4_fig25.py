"""Figura 25 del Tp4: los diez desacuerdos del ensayo (Data Table de Tp4_A), con letra de 11 pt."""
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
plt.rcParams['font.family'] = 'Liberation Serif'
H = ['id', 'clase del mapa', 'clase de referencia', 'confianza', 'fuente del píxel', 'observación']
R = [(6,'2 humedal','5 cultivo','baja','polígono sorteado','pastizal ribereño'),(16,'5 cultivo','4 plantac.','media','polígono sorteado','lote con árboles jóvenes en hileras'),
     (30,'2 humedal','5 cultivo','media','polígono sorteado','pastizal ribereño'),(31,'5 cultivo','3 monte','media','polígono sorteado','isleta de monte en pastizal'),
     (32,'3 monte','4 plantac.','alta','MapBiomas recortado','plantación en hileras'),(39,'5 cultivo','4 plantac.','baja','polígono sorteado','lote con árboles jóvenes'),
     (49,'5 cultivo','4 plantac.','baja','polígono sorteado','lote con árboles jóvenes'),(51,'3 monte','4 plantac.','media','MapBiomas recortado','plantación de pinos (borde con un canal)'),
     (58,'2 humedal','5 cultivo','media','polígono sorteado','pastizal ribereño'),(62,'2 humedal','5 cultivo','media','polígono sorteado','pastizal ribereño')]
X = [0, 0.7, 2.4, 4.3, 5.6, 7.9, 12.6]
W, Hh = 22/2.54, 8.6/2.54
fig = plt.figure(figsize=(W, Hh)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 12.6); ax.set_ylim(11.6, 0); ax.axis('off')
ax.add_patch(Rectangle((0, 0), 12.6, 1.2, fc='#e6e6e6', ec='none'))
for c, t in enumerate(H): ax.text((X[c]+X[c+1])/2, 0.6, t, ha='center', va='center', fontsize=11, fontweight='bold')
for r, row in enumerate(R):
    y = 1.2 + r * 1.04
    for c, v in enumerate(row):
        ax.text((X[c]+X[c+1])/2 if c < 5 else X[c] + 0.15, y + 0.52, str(v), ha='center' if c < 5 else 'left', va='center', fontsize=11,
                fontweight='bold' if (c == 3 and v == 'alta') else 'normal')
    ax.plot([0, 12.6], [y + 1.04, y + 1.04], color='#999999', lw=0.6)
for yy in (0, 1.2): ax.plot([0, 12.6], [yy, yy], color='black', lw=1)
ax.plot([0, 12.6], [1.2 + 10 * 1.04, 1.2 + 10 * 1.04], color='black', lw=1)
fig.savefig('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/hueco/t3f8/T4F25.png', dpi=250, bbox_inches='tight', pad_inches=0.03); print('ok')
