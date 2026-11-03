exec(open('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp8/comun.py').read())
import re
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from matplotlib.colors import ListedColormap, BoundaryNorm
from pyproj import Geod
f = G + 'F_BOVRIL_MapBiomas_cobertura_1985_2025.tif'
qml = open(G + 'F_BOVRIL_MapBiomas_cobertura_1985_2025.qml', encoding='utf8').read()
PAL = {int(v): (l, c) for v, l, c in re.findall(r'value="(\d+)" label="([^"]+)" color="(#[0-9A-Fa-f]{6})"', qml)}
NOMBRE = {3: '3 Bosques cerrados', 4: '4 Bosques abiertos', 6: '6 Bosques inundables', 9: '9 Silvicultura',
          11: '11 Herbáceas inundables', 12: '12 Herbáceas', 15: '15 Pastura', 19: '19 Cultivos temporarios',
          24: '24 Áreas urbanas', 25: '25 Otras áreas no vegetadas', 36: '36 Cultivos perennes'}
r = rasterio.open(f); A = r.read(); anios = list(range(1985, 2026))
lat = r.bounds.top - (np.arange(r.height) + 0.5) * r.res[1]; d = r.res[0]; g = Geod(ellps='WGS84')
pa = np.array([abs(g.polygon_area_perimeter([0, d, d, 0], [la - d / 2, la - d / 2, la + d / 2, la + d / 2])[0]) for la in lat]) / 1e4
clases = sorted(NOMBRE)
sup = {c: [float((pa[:, None] * (A[k] == c)).sum()) / 1000 for k in range(len(anios))] for c in clases}


def utm(b, res=10):
    x0, x1, y0, y1 = SITIO; nx, ny = int((x1 - x0) / res), int((y1 - y0) / res)
    o = np.zeros((ny, nx), 'u1')
    reproject(A[b], o, src_transform=r.transform, src_crs=r.crs, dst_transform=from_origin(x0, y1, res, res),
              dst_crs='EPSG:32721', resampling=Resampling.nearest, src_nodata=0, dst_nodata=0)
    return o


lut = np.zeros((256, 4)); lut[:, :] = 1
for v, (l, c) in PAL.items():
    lut[v, :3] = matplotlib.colors.to_rgb(c)
fig = plt.figure(figsize=(9.45, 4.15))
a1 = fig.add_axes([0.075, 0.31, 0.235, 0.63]); a2 = fig.add_axes([0.335, 0.31, 0.235, 0.63])
a3 = fig.add_axes([0.665, 0.31, 0.32, 0.63])
for ax, b, t in ((a1, 0, '(a) MapBiomas 1985'), (a2, 40, '(b) MapBiomas 2025')):
    m = utm(b); ax.imshow(lut[m], extent=SITIO, interpolation='nearest')
    frame(ax, SITIO, 2000, 0, left=ax is a1); ax.set_title(t, fontsize=10.5)
for c in clases:
    if max(sup[c]) < 0.03: continue
    a3.plot(anios, sup[c], color=PAL[c][1], lw=1.8)
for y in (1985, 2000, 2023, 2025):
    a3.axvline(y, color='0.5', ls=':', lw=0.8)
a3.text(2023, a3.get_ylim()[1] * 0.985, '2023', ha='center', va='top', fontsize=9, color='0.4',
        bbox=dict(fc='white', ec='none', pad=0.5))
a3.set_xticks([1985, 1995, 2000, 2005, 2015, 2025]); a3.set_xlim(1983.5, 2026.5)
a3.yaxis.set_major_formatter(FuncFormatter(lambda v, _: ('%g' % v).replace('.', ',')))
a3.set_xlabel('Año'); a3.set_ylabel('Superficie (miles de ha)'); a3.set_title('(c) Superficie por clase, 1985 a 2025', fontsize=10.5)
a3.tick_params(labelsize=10)
fig.canvas.draw(); b1 = a1.get_position(); p3 = a3.get_position(); a3.set_position([p3.x0, b1.y0, p3.width, b1.height])
h = [Patch(fc=PAL[c][1], ec='0.3', lw=0.5, label=NOMBRE[c]) for c in clases]
fig.legend(handles=h, loc='lower center', bbox_to_anchor=(0.57, 0.0), ncol=4, frameon=False, fontsize=10,
           handlelength=1.6, columnspacing=1.2)
barra(fig, a1, 2000, '2 km', y=0.08)
norte(fig, a2)
guardar(fig, 'F03.png')
