# Tp6, Figura 25: Copernicus DEM GLO-30 (a) y uno de cada diez segmentos ICESat-2 ATL08 con terreno valido sobre el MDE (b).
# MDE del subset del practico reproyectado a UTM 21S a 30 m (bilineal); segmentos de lidar_B_CONCORDIA.gpkg, capa atl08
# (terreno_valido = 1, ya sin los segmentos sobre agua). Coordenadas UTM 21S en m, una flecha norte en el esquinero
# superior derecho y escala grafica horizontal al costado. 30/10/2026.
# Uso: python mapas_tp6_f25.py <B_CONCORDIA_CopernicusDEM30.tif> <lidar_B_CONCORDIA.gpkg> <salida.png> [alto_cm]
import sys, sqlite3, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow
from matplotlib.lines import Line2D
from rasterio.warp import calculate_default_transform, reproject, Resampling
from pyproj import Transformer
plt.rcParams['font.family'] = 'Liberation Serif'
fd, fg, out = sys.argv[1:4]
Hcm = float(sys.argv[4]) if len(sys.argv) > 4 else 11.0
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
r = rasterio.open(fd); dst = 'EPSG:32721'
tr, w, h = calculate_default_transform(r.crs, dst, r.width, r.height, *r.bounds, resolution=30)
dem = np.full((h, w), np.nan, 'f4')
reproject(r.read(1).astype('f4'), dem, src_transform=r.transform, src_crs=r.crs, dst_transform=tr, dst_crs=dst,
          resampling=Resampling.bilinear, src_nodata=np.nan, dst_nodata=np.nan)
ext = (tr.c, tr.c + w * tr.a, tr.f + h * tr.e, tr.f)
c = sqlite3.connect(fg)
ll = np.array(c.execute('select lon, lat from atl08 where terreno_valido = 1 order by fid').fetchall())
n_tot = len(ll); ll = ll[::10]
x, y = Transformer.from_crs('EPSG:4326', dst, always_xy=True).transform(ll[:, 0], ll[:, 1])
L, T, B, gap, R = 2.0, 0.7, 2.7, 0.35, 3.5
ph = Hcm - T - B; asp = (ext[1] - ext[0]) / (ext[3] - ext[2]); pw = ph * asp
Wcm = L + 2 * pw + gap + R
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM)); axs = []
for k, t in enumerate(['(a) Copernicus DEM GLO-30', '(b) Segmentos ATL08 (uno de cada diez)']):
    ax = fig.add_axes([(L + k * (pw + gap)) / Wcm, B / Hcm, pw / Wcm, ph / Hcm])
    im = ax.imshow(dem, extent=ext, cmap='RdYlGn_r', vmin=5, vmax=70, interpolation='bilinear')
    if k: ax.plot(x, y, '.', ms=1.2, color='#3b0a6b', mew=0)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_xticks([390000, 400000, 410000]); ax.set_yticks([6520000, 6530000, 6540000, 6550000])
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.tick_params(labelsize=10, length=3)
    for lb in ax.get_yticklabels(): lb.set_rotation(90); lb.set_va('center')
    if k: ax.set_yticklabels([])
    else: ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10.5, labelpad=6)
    ax.set_xlabel('Este, UTM 21S (m)', fontsize=10.5, labelpad=2)
    ax.set_title(t, fontsize=11.5, pad=4); axs.append(ax)
p0, p1 = [a.get_position() for a in axs]
cax = fig.add_axes([p0.x0 + 0.3 / Wcm, 1.2 / Hcm, p0.width - 0.6 / Wcm, 0.3 / Hcm])
cb = fig.colorbar(im, cax=cax, orientation='horizontal', ticks=[10, 20, 30, 40, 50, 60, 70], extend='both')
cb.ax.tick_params(labelsize=10); cb.set_label('Cota sobre el geoide EGM2008 (m)', fontsize=10.5, labelpad=1)
fig.legend(handles=[Line2D([], [], ls='none', marker='o', ms=4, color='#3b0a6b',
                           label='Segmento ATL08 de 100 m con terreno válido\n(%s de %s)' % ('{:,}'.format(len(ll)).replace(',', '.'), '{:,}'.format(n_tot).replace(',', '.')))],
           loc='upper left', bbox_to_anchor=(p1.x0, 1.75 / Hcm), fontsize=10.5, frameon=False, borderaxespad=0)
xn = 1 - 0.9 / Wcm
fig.add_artist(FancyArrow(xn, p1.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                          head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, p1.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
Lm = 10000; fw = Lm / (ext[1] - ext[0]) * p1.width; xs = p1.x1 + 0.4 / Wcm; ys = p1.y0 + 0.5 / Hcm; hh = 0.2 / Hcm
sa = fig.add_axes([xs, ys, fw, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
for vv, t in ((0, '0'), (0.5, '5'), (1, '10 km')):
    fig.text(xs + vv * fw, ys + hh + 0.1 / Hcm, t, ha='center', va='bottom', fontsize=10.5)
fig.savefig(out, dpi=220); plt.close(fig)
print('ancho %.2f; segmentos %d de %d' % (Wcm, len(ll), n_tot))
