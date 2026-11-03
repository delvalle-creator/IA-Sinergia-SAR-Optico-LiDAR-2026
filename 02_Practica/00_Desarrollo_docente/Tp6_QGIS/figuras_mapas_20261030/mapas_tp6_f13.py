# Tp6, Figura 13: extension maxima (a), duracion minima en dias (b) y agua en la fecha seca de referencia,
# 22/01/2026, excluida de la inundacion (c), desde B_extension_y_duracion_C_20m.tif (salida de Tp6_01_serie_agua_C.py)
# y el agua permanente JRC >= 90 %. Coordenadas UTM 21S en metros, una sola flecha norte en el esquinero superior
# derecho, escala grafica horizontal al costado. 30/10/2026.
# Uso: python mapas_tp6_f13.py <B_extension_y_duracion_C_20m.tif> <B_CONCORDIA_JRC_GSW_ocurrencia.tif> <salida.png>
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap
from rasterio.warp import reproject, Resampling
plt.rcParams['font.family'] = 'Liberation Serif'
fe, fj, out = sys.argv[1:4]
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
r = rasterio.open(fe); dsc = list(r.descriptions); b = r.bounds
ext = (b.left, b.right, b.bottom, b.top)
rd = lambda n: r.read(dsc.index(n) + 1).astype('f4')
ex, du, sec = rd('extension_maxima'), rd('duracion_min_dias'), rd('agua_en_referencia_seca')
rj = rasterio.open(fj); jrc = np.full((r.height, r.width), np.nan, 'f4')
reproject(rj.read(1).astype('f4'), jrc, src_transform=rj.transform, src_crs=rj.crs, dst_transform=r.transform,
          dst_crs=r.crs, resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
perm = jrc >= 90
GRIS, FONDO = '#a9a9a9', '#f0f0f0'
Wcm, Hcm = 25.4, 11.1
L, T, B, gap, R = 2.0, 0.7, 2.75, 0.35, 2.9
ph = Hcm - T - B; asp = (ext[1] - ext[0]) / (ext[3] - ext[2]); pw = ph * asp
if L + 3 * pw + 2 * gap + R > Wcm:
    pw = (Wcm - L - R - 2 * gap) / 3; ph = pw / asp; Hcm = ph + T + B
x0 = (Wcm - (L + 3 * pw + 2 * gap + R)) / 2 + L
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM)); axs = []
cmd = plt.get_cmap('Blues').copy()
for k, t in enumerate(['(a) Extensión máxima', '(b) Duración mínima (días)', '(c) Agua el 22/01/2026 (excluida)']):
    ax = fig.add_axes([(x0 + k * (pw + gap)) / Wcm, B / Hcm, pw / Wcm, ph / Hcm])
    if k == 0:
        cl = np.where(ex == 1, 1, 0); cl[perm] = 2
        ax.imshow(cl, extent=ext, cmap=ListedColormap([FONDO, '#1f6fb4', GRIS]), vmin=0, vmax=2, interpolation='nearest')
    elif k == 1:
        ax.imshow(np.where(perm, np.nan, 1), extent=ext, cmap=ListedColormap([FONDO]), interpolation='nearest')
        im = ax.imshow(np.ma.masked_where(perm | (du <= 0), du), extent=ext, cmap=cmd, vmin=0, vmax=90, interpolation='nearest')
        ax.imshow(np.ma.masked_where(~perm, np.ones_like(du)), extent=ext, cmap=ListedColormap([GRIS]), interpolation='nearest')
    else:
        cl = np.where(sec == 1, 1, 0); cl[perm] = 2
        ax.imshow(cl, extent=ext, cmap=ListedColormap([FONDO, '#e6550d', GRIS]), vmin=0, vmax=2, interpolation='nearest')
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_xticks([390000, 400000, 410000]); ax.set_yticks([6520000, 6530000, 6540000, 6550000])
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.tick_params(labelsize=10, length=3)
    for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    if k: ax.set_yticklabels([])
    else: ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10.5, labelpad=6)
    ax.set_xlabel('Este, UTM 21S (m)', fontsize=10.5, labelpad=2)
    ax.set_title(t, fontsize=11.5, pad=4); axs.append(ax)
# leyendas debajo de cada panel
p0, p1, p2 = [a.get_position() for a in axs]
fig.legend(handles=[Patch(fc='#1f6fb4', ec='black', lw=0.5, label='Agua alguna vez'),
                    Patch(fc=GRIS, ec='black', lw=0.5, label='Agua permanente')],
           loc='upper left', bbox_to_anchor=(p0.x0 + 0.4 / Wcm, 1.32 / Hcm), fontsize=10.5, frameon=False, borderaxespad=0)
cax = fig.add_axes([p1.x0 + 0.4 / Wcm, 1.02 / Hcm, p1.width - 0.8 / Wcm, 0.3 / Hcm])
cb = fig.colorbar(im, cax=cax, orientation='horizontal', ticks=[0, 30, 60, 90]); cb.ax.tick_params(labelsize=10)
cb.set_label('Días (fechas sin dato = sin agua)', fontsize=10.5, labelpad=1)
fig.legend(handles=[Patch(fc='#e6550d', ec='black', lw=0.5, label='Agua no permanente el 22/01/2026'),
                    Patch(fc=GRIS, ec='black', lw=0.5, label='Agua permanente')],
           loc='upper left', bbox_to_anchor=(p2.x0 + 0.2 / Wcm, 1.32 / Hcm), fontsize=10.5, frameon=False, borderaxespad=0)
xn = 1 - 0.9 / Wcm
fig.add_artist(FancyArrow(xn, p2.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                          head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, p2.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
Lm = 10000; fw = Lm / (ext[1] - ext[0]) * p2.width; xs = p2.x1 + 0.4 / Wcm; ys = p2.y0 + 0.5 / Hcm; hh = 0.2 / Hcm
sa = fig.add_axes([xs, ys, fw, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
for vv, t in ((0, '0'), (0.5, '5'), (1, '10 km')):
    fig.text(xs + vv * fw, ys + hh + 0.1 / Hcm, t, ha='center', va='bottom', fontsize=10.5)
fig.savefig(out, dpi=220); plt.close(fig)
print('alto %.2f cm; ext %.0f ha; >30 d %.0f ha; seca %.0f ha' % (Hcm, (ex == 1).sum() * .04, (du > 30).sum() * .04, (sec == 1).sum() * .04))
