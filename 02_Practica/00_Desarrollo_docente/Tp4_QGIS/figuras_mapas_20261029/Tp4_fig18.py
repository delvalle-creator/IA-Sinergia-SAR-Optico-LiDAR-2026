"""Figura 18 del Tp4: matriz de error de MapBiomas 2025 en conteos, con W_i y la proporción de área estimada (valores de Tp4_03)."""
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
plt.rcParams['font.family'] = 'Liberation Serif'
col = ['agua', 'humedal', 'monte', 'plantación', 'herbáceo,\ncultivo y\npastura', 'suelo\ndesnudo', 'urbano', 'otra\n(túneles)', 'W$_i$ (área\ndel estrato)']
fil = ['agua', 'humedal', 'monte', 'plantación', 'herbáceo, cultivo\ny pastura', 'suelo desnudo', 'urbano']
M = [[10,0,0,0,0,0,0,0,'0,089'],[1,1,3,0,5,0,0,0,'0,044'],[0,1,2,3,4,0,0,0,'0,120'],[0,0,2,8,0,0,0,0,'0,242'],
     [0,1,0,2,5,0,2,0,'0,461'],[1,0,0,2,2,2,2,1,'0,010'],[0,0,1,0,2,0,7,0,'0,035']]
P = ['0,094','0,062','0,089','0,324','0,309','0,002','0,118','0,001','1,000']
W, H = 22/2.54, 9.4/2.54
fig = plt.figure(figsize=(W, H)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(-0.05, 10.75); ax.set_ylim(10.2, 0); ax.axis('off')
x0 = [0, 1.9] + [1.9 + 0.97 * k for k in range(1, 10)]
def cell(r, c, t, bold=False, fc=None, fs=11):
    xa = x0[c]; xb = x0[c + 1] if c + 1 < len(x0) else 10.6
    if fc: ax.add_patch(Rectangle((xa, r), xb - xa, 1, fc=fc, ec='none'))
    ax.text((xa + xb) / 2, r + 0.5, t, ha='center', va='center', fontsize=fs, fontweight='bold' if bold else 'normal', linespacing=1.0)
ax.add_patch(Rectangle((0, 0), 10.6, 1.6, fc='#e6e6e6', ec='none'))
for c, t in enumerate(['Mapa \\ referencia'] + col): 
    xa = x0[c]; xb = x0[c + 1] if c + 1 < len(x0) else 10.6
    ax.text((xa + xb) / 2, 0.8, t, ha='center', va='center', fontsize=10.5, fontweight='bold', linespacing=1.0)
for r, (f, row) in enumerate(zip(fil, M)):
    y = 1.6 + r * 1.0
    cell(y, 0, f, bold=True, fs=10.5)
    for c, v in enumerate(row):
        cell(y, c + 1, str(v), bold=(c == r), fc='#fadadd' if c == r else None)
    ax.plot([0, 10.6], [y + 1, y + 1], color='#999999', lw=0.6)
y = 1.6 + 7
ax.add_patch(Rectangle((0, y), 10.6, 1.6, fc='#e6e6e6', ec='none'))
ax.text(0.95, y + 0.8, 'Proporción de\nárea estimada (p·j)', ha='center', va='center', fontsize=10.5, fontweight='bold', linespacing=1.0)
for c, v in enumerate(P): cell(y + 0.3, c + 1, v)
for yy in (0, 1.6, y, y + 1.6): ax.plot([0, 10.6], [yy, yy], color='black', lw=1.0)
fig.savefig('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/hueco/t3f8/T4F18.png', dpi=250); print('ok')
