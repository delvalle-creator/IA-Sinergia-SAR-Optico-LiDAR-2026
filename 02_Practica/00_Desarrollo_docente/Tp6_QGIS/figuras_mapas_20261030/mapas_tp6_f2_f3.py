# Tp6, Figuras 2 y 3: Sentinel-2 del 04/11/2023 (B11-B8A-B4 y color natural) y Sentinel-1 en RGB VV-VH-VV/VH
# (23/10, 04/11, 16/11/2023) con coordenadas UTM 21S, escala grafica al costado y norte en el esquinero superior
# derecho, fuera de los mapas. 30/10/2026.
# Uso: python mapas_tp6_f2_f3.py <S2_20231104.tif> <S1_20231023_RGB.tif> <S1_20231104_RGB.tif> <S1_20231116_RGB.tif> <carpeta_salida>
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow
from rasterio.enums import Resampling
plt.rcParams['font.family'] = 'Liberation Serif'
s2, s1a, s1b, s1c, out = sys.argv[1:6]
CM = 1 / 2.54; F = 4
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
def leer(f, bands):
    r = rasterio.open(f); h, w = r.height // F, r.width // F
    a = r.read(bands, out_shape=(len(bands), h, w), resampling=Resampling.average).astype('f4')
    b = r.bounds; return a, (b.left, b.right, b.bottom, b.top)
def estirar(a, nod=0):
    m = (a == nod).all(0); o = np.zeros(a.shape[1:] + (3,), 'f4')
    for i in range(3):
        v = a[i][~m]; lo, hi = np.percentile(v, [2, 98]); o[..., i] = np.clip((a[i] - lo) / (hi - lo), 0, 1)
    o[m] = 1; return o
def figura(ims, titulos, Wcm, Hcm, nombre, step=10000):
    n = len(ims); ext = ims[0][1]
    L, R, T, B, gap = 2.0, 3.4, 0.7, 1.15, 0.35
    ph = Hcm - T - B; asp = (ext[1] - ext[0]) / (ext[3] - ext[2]); pw = ph * asp
    tot = L + n * pw + (n - 1) * gap + R
    if tot > Wcm:
        pw = (Wcm - L - R - (n - 1) * gap) / n; ph = pw / asp; Hcm = ph + T + B
    x0 = (Wcm - (L + n * pw + (n - 1) * gap + R)) / 2 + L
    fig = plt.figure(figsize=(Wcm * CM, Hcm * CM)); axs = []
    for k, ((im, e), t) in enumerate(zip(ims, titulos)):
        ax = fig.add_axes([(x0 + k * (pw + gap)) / Wcm, B / Hcm, pw / Wcm, ph / Hcm])
        ax.imshow(im, extent=e, interpolation='bilinear')
        ax.set_xlim(e[0], e[1]); ax.set_ylim(e[2], e[3])
        ax.xaxis.set_major_locator(MultipleLocator(step)); ax.yaxis.set_major_locator(MultipleLocator(step))
        ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
        ax.tick_params(labelsize=10, length=3)
        for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
        if k: ax.set_yticklabels([])
        else: ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10.5, labelpad=6)
        ax.set_xlabel('Este, UTM 21S (m)', fontsize=10.5, labelpad=2)
        ax.set_title(t, fontsize=11.5, pad=4); axs.append(ax)
    b = axs[-1].get_position(); xr = b.x1 + 0.45 / Wcm
    # norte: esquinero superior derecho, fuera del mapa
    fig.add_artist(FancyArrow(xr + 0.6 / Wcm, b.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                              head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
    fig.text(xr + 0.6 / Wcm, b.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
    # escala grafica HORIZONTAL al costado derecho, abajo (10 km)
    Lm = 10000; fw = Lm / (ext[1] - ext[0]) * b.width; xs = b.x1 + 0.4 / Wcm; ys = b.y0 + 0.5 / Hcm; hh = 0.2 / Hcm
    sa = fig.add_axes([xs, ys, fw, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
    sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
    for v, t in ((0, '0'), (0.5, '5'), (1, '10 km')):
        fig.text(xs + v * fw, ys + hh + 0.1 / Hcm, t, ha='center', va='bottom', fontsize=10.5)
    fig.savefig(out + nombre, dpi=220); plt.close(fig); print(nombre, Wcm, Hcm)
a, e = leer(s2, [9, 8, 3]); f2a = estirar(a)
a, _ = leer(s2, [3, 2, 1]); f2b = estirar(a)
figura([(f2a, e), (f2b, e)], ['(a) B11, B8A, B4', '(b) Color natural (B4, B3, B2)'], 24.5, 14.4, 'Tp6_F02.png')
ims = []
for f in (s1a, s1b, s1c):
    a, e1 = leer(f, [1, 2, 3]); im = np.moveaxis(a / 255., 0, -1); im[(a == 0).all(0)] = 1; ims.append((np.clip(im, 0, 1), e1))
figura(ims, ['(a) 23/10/2023', '(b) 04/11/2023', '(c) 16/11/2023'], 25.4, 13.0, 'Tp6_F03.png')
