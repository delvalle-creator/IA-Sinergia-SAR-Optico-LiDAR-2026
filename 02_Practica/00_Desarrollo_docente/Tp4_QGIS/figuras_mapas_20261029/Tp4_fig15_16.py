"""Figuras 15 y 16 del Tp4: fichas de los puntos de MapBiomas (25 a 28 y 49 a 52), recompuestas a partir de las
fichas originales (los píxeles no cambian) con encabezados y rótulos de 11 pt, como las Figuras 9 y 10."""
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow
from PIL import Image
import numpy as np, sys
plt.rcParams['font.family'] = 'Liberation Serif'; plt.rcParams['font.size'] = 11
H0 = '/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/hueco/t3f8/'
def ficha(src, pts, out, Wcm=22):
    im = np.asarray(Image.open(H0 + src).convert('RGB'))
    ch = lambda r, j: im[r * 430:r * 430 + 420, 60 + 420 * j:60 + 420 * (j + 1)]
    W = Wcm / 2.54; g = 0.04; gg = 0.16; x0 = 0.10; hdr = 0.40; lab = 0.22; sc = 0.62; c = (W - x0 - 0.42 - 5 * g - (gg - g)) / 6
    H = hdr + 2 * (lab + c) + sc
    fig = plt.figure(figsize=(W, H))
    heads = ['Esri\n300 m', 'Google\n300 m', 'Esri\n1.200 m'] * 2; axes = {}
    for k, p in enumerate(pts):
        col0 = 3 * (k // 2); row = k % 2
        for j in range(3):
            x = x0 + (col0 + j) * (c + g) + (gg - g if col0 + j >= 3 else 0); y = H - hdr - (row + 1) * (lab + c)
            ax = fig.add_axes([x / W, y / H, c / W, c / H]); axes[(col0 + j, row)] = ax
            ax.imshow(ch(k, j)); ax.set_xticks([]); ax.set_yticks([])
            if j == 0: fig.text(x / W, (y + c + 0.03) / H, 'P%03d' % p, fontsize=11, va='bottom', ha='left')
    for col in range(6):
        b = axes[(col, 0)].get_position()
        fig.text((b.x0 + b.x1) / 2, (H - 0.06) / H, heads[col], ha='center', va='top', fontsize=11, fontweight='bold')
    b = axes[(0, 1)].get_position(); frac = 100 / 300 * b.width; y = 0.24 / H; h = 0.05 / H
    sa = fig.add_axes([b.x0, y, frac, h]); sa.axis('off'); sa.set_xlim(0, 1); sa.set_ylim(0, 1)
    sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='k', ec='k', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='w', ec='k', lw=0.8))
    fig.text(b.x0, y + h + 0.03 / H, '0', ha='center', va='bottom', fontsize=11); fig.text(b.x0 + frac, y + h + 0.03 / H, '100 m', ha='center', va='bottom', fontsize=11)
    fig.text(b.x0 + frac + 0.35 / W, y + h / 2, '(vistas de 300 m; la de 1.200 m\nes cuatro veces menor)', va='center', fontsize=11)
    bn = axes[(5, 0)].get_position(); xn = bn.x1 + 0.17 / W; yt = bn.y1
    fig.add_artist(FancyArrow(xn, yt - 0.42 / H, 0, 0.28 / H, width=0.016 / W, head_width=0.11 / W, head_length=0.12 / H, length_includes_head=True, color='black', transform=fig.transFigure))
    fig.text(xn, yt - 0.10 / H, 'N', ha='center', va='bottom', fontsize=11, fontweight='bold')
    fig.savefig(H0 + out, dpi=250); plt.close(fig); print(out, W, H)
ficha('T4F15_orig.png', [25, 26, 27, 28], 'T4F15.png')
ficha('T4F16_orig.png', [49, 50, 51, 52], 'T4F16.png')
