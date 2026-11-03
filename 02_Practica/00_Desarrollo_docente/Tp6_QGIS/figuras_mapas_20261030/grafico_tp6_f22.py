# Tp6, Figura 22: seis puntos de la muestra comun vistos por los dos interpretes. Rearma la lamina original
# (Fig_Tp6_dos_interpretes_300dpi.png: recortes de 300 m del Sentinel-2 del 04/11/2023 en color natural y B11-B8-B4, y del
# Landsat 8 del 25/10/2023 en B6-B5-B4) con los rotulos en Times a tamano de texto. 30/10/2026.
# Uso: python grafico_tp6_f22.py <Fig_Tp6_dos_interpretes_300dpi.png> <salida.png>
import sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
plt.rcParams['font.family'] = 'Liberation Serif'
fi, out = sys.argv[1:3]
a = np.asarray(Image.open(fi).convert('RGB'))
C = [(7, 440), (472, 905), (937, 1370), (1565, 1997), (2030, 2462), (2495, 2927)]
R = [(104, 537), (778, 1211), (1453, 1885)]
txt = [('(a) Punto 20: A agua (alta), B agua (alta)', 'Consenso: agua. Mapa: agua de inundación'),
       ('(b) Punto 2: A no agua (alta), B no agua (alta)', 'Consenso: no agua. Mapa: no agua'),
       ('(c) Punto 15: A agua (media), B no agua (media)', 'Consenso: agua. Mapa: agua de inundación'),
       ('(d) Punto 101: A agua (alta), B no agua (media)', 'Consenso: agua. Mapa: agua de inundación'),
       ('(e) Punto 72: A no agua (baja), B agua (media)', 'Consenso: agua. Mapa: no (en la referencia seca)'),
       ('(f) Punto 26: A agua (alta), B nube', 'Consenso: agua. Mapa: agua de inundación')]
tit = ['A: S2 color natural', 'A: S2 B11-B8-B4', 'B: L8 B6-B5-B4']
CM = 1 / 2.54; W, H = 25.0, 13.1
s = 2.85; g = 0.15; gg = 1.6; top = 0.5; lab = 1.0
x0 = (W - (6 * s + 4 * g + gg)) / 2
fig = plt.figure(figsize=(W * CM, H * CM))
for r in range(3):
    for c in range(6):
        k = r * 2 + c // 3
        x = x0 + c * (s + g) + (gg - g if c >= 3 else 0)
        y = H - top - (r + 1) * s - r * (lab + top)
        ax = fig.add_axes([x / W, y / H, s / W, s / H])
        (r0, r1), (c0, c1) = R[r], C[c]
        ax.imshow(a[r0 + 2:r1 - 2, c0 + 2:c1 - 2]); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(tit[c % 3], fontsize=9.5, pad=2)
        if c % 3 == 1:
            fig.text((x + s / 2) / W, (y - 0.12) / H, txt[k][0], ha='center', va='top', fontsize=10.5)
            fig.text((x + s / 2) / W, (y - 0.52) / H, txt[k][1], ha='center', va='top', fontsize=10.5)
fig.savefig(out, dpi=220); plt.close(fig)
