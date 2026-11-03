# Tp6, Figura 5: ocurrencia de agua JRC 1984-2021 (a) y cobertura de control a 20 m del Tp4 (b), Concordia.
# Coordenadas UTM 21S, norte en el esquinero superior derecho, escala grafica horizontal al costado. 30/10/2026.
# Uso: python mapas_tp6_f5.py <B_CONCORDIA_JRC_GSW_ocurrencia.tif> <B_CONCORDIA_cobertura_control_20m.tif> <salida.png>
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap, BoundaryNorm
from rasterio.warp import reproject, Resampling
plt.rcParams['font.family'] = 'Liberation Serif'
fj, fc, out = sys.argv[1:4]
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
rc = rasterio.open(fc); cob = rc.read(1); b = rc.bounds
ext = (b.left, b.right, b.bottom, b.top)
rj = rasterio.open(fj); jrc = np.full(cob.shape, np.nan, 'f4')
reproject(rj.read(1).astype('f4'), jrc, src_transform=rj.transform, src_crs=rj.crs, dst_transform=rc.transform,
          dst_crs=rc.crs, resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
# (a) ocurrencia: 0 % en gris muy claro, 1-100 % de celeste a azul oscuro
cj = plt.get_cmap('Blues')(np.linspace(0.25, 1, 256)); cmj = ListedColormap(cj); cmj.set_under('#f2efe9'); cmj.set_bad('white')
# (b) clases de control
clases = [(1, 'agua', '#1f78b4'), (2, 'humedal', '#a6cee3'), (3, 'monte', '#1b7837'), (4, 'plantación', '#a6611a'),
          (5, 'cultivo_pastura', '#f0e442'), (6, 'suelo desnudo', '#bdbdbd'), (7, 'urbano', '#d7191c')]
lut = ['#f7f7f7'] + [c for _, _, c in clases]
cmc = ListedColormap(lut); nrm = BoundaryNorm(np.arange(-0.5, 8.5, 1), 8)
cobm = np.where(cob < 0, 0, cob)
# dilatar 1 pixel las clases chicas para que se vean a esta escala (solo visual)
from scipy.ndimage import grey_dilation
for v in (2, 4, 5, 6, 7):
    m = grey_dilation((cob == v).astype('u1'), size=(5, 5)) > 0
    cobm = np.where(m & (cobm != 1), v, cobm)

Wcm, Hcm = 25.4, 10.8
L, T, B, gap = 2.0, 0.7, 1.15, 3.6
ph = Hcm - T - B; asp = (ext[1] - ext[0]) / (ext[3] - ext[2]); pw = ph * asp
R = 4.6
x0 = (Wcm - (L + 2 * pw + gap + R)) / 2 + L
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM)); axs = []
xt = [390000, 400000, 410000]; yt = [6520000, 6530000, 6540000, 6550000]
for k, t in enumerate(['(a) JRC, ocurrencia de agua 1984–2021', '(b) Cobertura de control a 20 m']):
    ax = fig.add_axes([(x0 + k * (pw + gap)) / Wcm, B / Hcm, pw / Wcm, ph / Hcm])
    if k == 0: imj = ax.imshow(np.ma.masked_invalid(jrc), extent=ext, cmap=cmj, vmin=0.5, vmax=100, interpolation='nearest')
    else: ax.imshow(cobm, extent=ext, cmap=cmc, norm=nrm, interpolation='nearest')
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_xticks(xt); ax.set_yticks(yt)
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.tick_params(labelsize=10, length=3)
    for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    if k: ax.set_yticklabels([])
    else: ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10.5, labelpad=6)
    ax.set_xlabel('Este, UTM 21S (m)', fontsize=10.5, labelpad=2)
    ax.set_title(t, fontsize=11.5, pad=4); axs.append(ax)
# barra de colores de (a) entre los dos mapas
pa = axs[0].get_position()
cax = fig.add_axes([pa.x1 + 0.45 / Wcm, pa.y0 + 0.6 / Hcm, 0.35 / Wcm, pa.height - 1.2 / Hcm])
cb = fig.colorbar(imj, cax=cax, ticks=[1, 25, 50, 75, 100]); cb.ax.tick_params(labelsize=10)
cb.ax.set_title('%', fontsize=10.5, pad=4)
fig.add_artist(Rectangle((cax.get_position().x0, cax.get_position().y0 - 0.55 / Hcm), 0.35 / Wcm, 0.35 / Hcm,
                         fc='#f2efe9', ec='black', lw=0.6, transform=fig.transFigure))
fig.text(cax.get_position().x0 + 0.5 / Wcm, cax.get_position().y0 - 0.38 / Hcm, '0', fontsize=10, va='center')
# norte y escala a la derecha de (b)
b2 = axs[1].get_position(); xr = b2.x1 + 0.45 / Wcm
fig.add_artist(FancyArrow(xr + 0.6 / Wcm, b2.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                          head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xr + 0.6 / Wcm, b2.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
# leyenda de clases
hs = [Patch(fc=c, ec='black', lw=0.5, label=n) for _, n, c in clases]
fig.legend(handles=hs, loc='center left', bbox_to_anchor=(xr - 0.1 / Wcm, b2.y0 + 0.55 * b2.height), fontsize=10,
           frameon=False, handlelength=1.2, handleheight=1.0, labelspacing=0.35, borderaxespad=0)
Lm = 10000; fw = Lm / (ext[1] - ext[0]) * b2.width; xs = b2.x1 + 0.4 / Wcm; ys = b2.y0 + 0.5 / Hcm; hh = 0.2 / Hcm
sa = fig.add_axes([xs, ys, fw, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
for v, t in ((0, '0'), (0.5, '5'), (1, '10 km')):
    fig.text(xs + v * fw, ys + hh + 0.1 / Hcm, t, ha='center', va='bottom', fontsize=10.5)
fig.savefig(out, dpi=220); plt.close(fig)
print('JRC>=90 % en el sitio:', round(100 * np.nanmean(jrc >= 90), 1), '%')
