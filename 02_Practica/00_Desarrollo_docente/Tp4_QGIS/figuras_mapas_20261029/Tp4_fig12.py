"""Figura 12 del Tp4: seis puntos vistos por el segundo intérprete. Recompone las vistas de la figura original
(Fig_Tp4_segundo_interprete_300dpi.png) con rótulos de 10,5 pt; los píxeles de cada vista no cambian."""
import sys; sys.path.insert(0, '/mnt/user-data/outputs/tp3_mapas/scripts')
from com import *
from PIL import Image
H = '/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/hueco/t3f8/'
im = np.asarray(Image.open(H + 'T4F12_orig.png').convert('RGB'))
X = [(7, 417), (448, 858), (1043, 1453), (1483, 1893), (2078, 2488), (2519, 2929)]
Y = [(99, 509), (738, 1148)]
C2, S10, S843 = 'CBERS-4A, 2 m', 'Sentinel-2, 10 m', 'Sentinel-2 8-4-3'
casos = [('a', 61, C2, 'urbano (alta)', 'urbano (alta)'),
         ('b', 60, S10, 'agua permanente (alta)', 'agua permanente (alta)'),
         ('c', 14, C2, 'humedal/pajonal (media)', 'monte nativo (baja)'),
         ('d', 28, S10, 'plantación forestal (alta)', 'monte nativo (baja)'),
         ('e', 53, C2, 'suelo desnudo (media)', 'plantación forestal (alta)'),
         ('f', 44, S10, 'agua permanente (alta)', 'nube')]
W, Hh = 25 / 2.54, 12.6 / 2.54
fig = plt.figure(figsize=(W, Hh))
cw = 3.75 / 2.54; g = 0.12 / 2.54; gp = (W - 6 * cw - 3 * g) / 2.0
for k, (l, p, t1, e1, e2) in enumerate(casos):
    r, c = divmod(k, 3)
    x0 = c * (2 * cw + g + gp)
    y0 = Hh - (0.55 / 2.54) - cw - r * (cw + 2.15 / 2.54)
    for j, (tt) in enumerate((t1, S843)):
        xs = X[2 * c + j]; ys = Y[r]
        a = fig.add_axes([(x0 + j * (cw + g)) / W, y0 / Hh, cw / W, cw / Hh])
        a.imshow(im[ys[0]:ys[1], xs[0]:xs[1]]); a.set_xticks([]); a.set_yticks([])
        a.set_title(tt, fontsize=10.5, pad=3)
    xc = (x0 + cw + g / 2) / W
    fig.text(xc, (y0 - 0.12 / 2.54) / Hh, '(%s) Punto %d\n1.º intérprete: %s\n2.º intérprete: %s' % (l, p, e1, e2),
             ha='center', va='top', fontsize=10.5, linespacing=1.15)
fig.savefig(H + 'T4F12.png', dpi=250, bbox_inches='tight', pad_inches=0.04); print('ok')
