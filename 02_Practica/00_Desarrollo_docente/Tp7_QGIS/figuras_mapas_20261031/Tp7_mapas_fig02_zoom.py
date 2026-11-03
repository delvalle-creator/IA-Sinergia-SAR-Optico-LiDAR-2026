# Tp7 Figura 2: MapBiomas 2018 del sitio y zoom de la barranca (31/10/2026)
import re, numpy as np, rasterio, geopandas as gpd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, Patch, FancyArrow
from matplotlib.lines import Line2D
from matplotlib.colors import to_rgb
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
plt.rcParams['font.family'] = 'Liberation Serif'; plt.rcParams['font.size'] = 10
U = '/mnt/user-data/uploads/CURSOS_CEREGEO_2026/02_Practica/Tp7_Barrancas_deslizamientos/'
Q = U + '02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/E1_DIAMANTE_BARRANCA_'
CRS = 'EPSG:32721'; CM = 1 / 2.54
SITIO = (149978, 162280, 6438567, 6452312)
BAR = (154300, 157400, 6444600, 6448050)
lad = gpd.read_file(U + '04_Tablas_de_trabajo/E1_ladera_reparada.gpkg').to_crs(CRS); lad = lad[lad.geometry.area > 1e5]
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))

def warp(ext, res):
    x0, x1, y0, y1 = ext; nx, ny = int(round((x1 - x0) / res)), int(round((y1 - y0) / res))
    o = np.zeros((ny, nx), 'f4')
    with rasterio.open(Q + 'MapBiomas_cobertura_1985_2025.tif') as s:
        reproject(s.read(34).astype('f4'), o, src_transform=s.transform, src_crs=s.crs, dst_transform=from_origin(x0, y1, res, res),
                  dst_crs=CRS, resampling=Resampling.nearest, src_nodata=0, dst_nodata=0)
    return o

q = open(Q + 'MapBiomas_cobertura_1985_2025.qml', encoding='utf-8').read()
pal = {int(v): c for v, c in re.findall(r'paletteEntry value="(\d+)" label="[^"]*" color="(#[0-9A-Fa-f]{6})"', q)}
nom = {3: 'Bosques cerrados', 4: 'Bosques abiertos', 6: 'Bosques inundables', 9: 'Silvicultura', 11: 'Herbáceas inundables',
       12: 'Herbáceas', 15: 'Pastura', 19: 'Cultivos temporarios', 24: 'Áreas urbanas', 33: 'Ríos, lagunas, lagos y océano',
       21: 'Mosaico de usos', 22: 'Área sin vegetación', 25: 'Otras áreas no vegetadas', 14: 'Agropecuario', 10: 'Vegetación herbácea y arbustiva'}
def colorear(a, cl):
    rgb = np.ones(a.shape + (3,))
    for c in cl: rgb[a == c] = to_rgb(pal[c])
    return rgb
A = warp(SITIO, 15); Z = warp(BAR, 5)
cl = [c for c in sorted(int(v) for v in np.unique(A[A > 0])) if (A == c).sum() > 50 and c in nom]

W = 25.0; L = 1.45; g = 1.0; pw = 7.6; T = 0.65
ph1 = pw * (SITIO[3] - SITIO[2]) / (SITIO[1] - SITIO[0]); ph2 = pw * (BAR[3] - BAR[2]) / (BAR[1] - BAR[0])
ph = max(ph1, ph2); H = T + ph + 1.0 + 0.95 + 0.1
fig = plt.figure(figsize=(W * CM, H * CM))
ax1 = fig.add_axes([L / W, (H - T - ph1) / H, pw / W, ph1 / H])
ax2 = fig.add_axes([(L + pw + g) / W, (H - T - ph2) / H, pw / W, ph2 / H])
for ax, img, E, st, t in ((ax1, colorear(A, cl), SITIO, 4000, '(a) Sitio, cobertura 2018'), (ax2, colorear(Z, cl), BAR, 1000, '(b) Detalle de la barranca')):
    ax.imshow(img, extent=E, interpolation='nearest'); lad.boundary.plot(ax=ax, color='black', lw=2, zorder=5)
    ax.set_xlim(E[0], E[1]); ax.set_ylim(E[2], E[3]); ax.set_aspect('auto')
    ax.xaxis.set_major_locator(MultipleLocator(st)); ax.yaxis.set_major_locator(MultipleLocator(st))
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles); ax.tick_params(labelsize=9, length=3)
    for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    ax.set_xlabel('Este (m)', fontsize=10, labelpad=2); ax.set_title(t, fontsize=10.5, pad=4)
ax1.set_ylabel('Norte (m), EPSG:32721', fontsize=10, labelpad=3); ax2.set_ylabel('')
ax1.add_patch(Rectangle((BAR[0], BAR[2]), BAR[1] - BAR[0], BAR[3] - BAR[2], fc='none', ec='magenta', lw=1.8, ls='--', zorder=6))
ax2.text(0.97, 0.03, 'MapBiomas, píxel de 30 m', transform=ax2.transAxes, ha='right', va='bottom', fontsize=9,
         bbox=dict(fc='white', ec='none', alpha=0.8, pad=1.5))
fig.canvas.draw()
def escala(ax, Lm, txt):
    b = ax.get_position(); frac = Lm / (ax.get_xlim()[1] - ax.get_xlim()[0]) * b.width
    y = (H - T - ph - 1.0 - 0.95 + 0.25) / H; h = 0.16 / H
    sa = fig.add_axes([b.x0, y, frac, h]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
    sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
    fig.text(b.x0, y + h + 0.06 / H, '0', ha='center', va='bottom', fontsize=10)
    fig.text(b.x0 + frac, y + h + 0.06 / H, txt, ha='center', va='bottom', fontsize=10)
escala(ax1, 2000, '2 km'); escala(ax2, 500, '500 m')
bn = ax2.get_position(); xn = bn.x1 + 0.5 / W; yt = bn.y1 + T * 0.6 / H
fig.add_artist(FancyArrow(xn, yt - 1.55 / H, 0, 1.05 / H, width=0.07 / W, head_width=0.36 / W, head_length=0.38 / H,
                          length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, yt - 0.45 / H, 'N', ha='center', va='bottom', fontsize=11, fontweight='bold')
h = [Patch(facecolor=pal[c], edgecolor='0.4', lw=0.6, label='%d %s' % (c, nom[c])) for c in cl] + \
    [Line2D([], [], color='black', lw=2.2, label='Ladera relevada en 2018'), Line2D([], [], color='magenta', lw=1.8, ls='--', label='Área del detalle (b)')]
fig.legend(handles=h, loc='center left', bbox_to_anchor=(bn.x1 + 1.1 / W, (bn.y0 + bn.y1) / 2), frameon=False, fontsize=10, handlelength=1.8)
fig.savefig('Tp7_Figura_02.png', dpi=300); print('H cm', round(H, 2))
# fraccion de bosque cerrado en el detalle, por columnas cerca del borde
