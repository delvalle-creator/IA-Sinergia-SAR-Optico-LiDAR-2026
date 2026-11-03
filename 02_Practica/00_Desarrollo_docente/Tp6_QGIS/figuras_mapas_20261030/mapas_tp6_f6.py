# Tp6, Figura 6: MapBiomas Argentina, cobertura 2023 (banda 39), Concordia, reproyectada a UTM 21S (vecino mas cercano).
# Leyenda oficial de la Coleccion 3 con el porcentaje de cada clase sobre la parte argentina del sitio.
# Coordenadas UTM 21S, norte en el esquinero superior derecho, escala grafica horizontal al costado. 30/10/2026.
# Uso: python mapas_tp6_f6.py <B_CONCORDIA_MapBiomas_cobertura_1985_2025.tif> <salida.png>
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap
from rasterio.warp import calculate_default_transform, reproject, Resampling
plt.rcParams['font.family'] = 'Liberation Serif'
fm, out = sys.argv[1:3]
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
r = rasterio.open(fm); src = r.read(39)  # cobertura_2023
assert r.descriptions[38] == 'cobertura_2023'
# porcentajes sobre la parte argentina, en la grilla nativa (como en el texto)
v = src[src > 0]; pct = {c: 100 * np.mean(v == c) for c in np.unique(v)}
dst_crs = 'EPSG:32721'
tr, w, h = calculate_default_transform(r.crs, dst_crs, r.width, r.height, *r.bounds, resolution=30)
a = np.zeros((h, w), 'u1')
reproject(src, a, src_transform=r.transform, src_crs=r.crs, dst_transform=tr, dst_crs=dst_crs,
          resampling=Resampling.nearest, src_nodata=0, dst_nodata=0)
ext = (tr.c, tr.c + w * tr.a, tr.f + h * tr.e, tr.f)
# recortar el marco vacio que deja la reproyeccion
ok = np.ones_like(a, bool)
leg = [(12, 'Herbáceas', '#d6bc74'), (9, 'Silvicultura', '#7a6c00'), (36, 'Cultivos perennes', '#d082de'),
       (33, 'Ríos, lagunas, lagos y océano', '#2532e4'), (4, 'Bosques abiertos', '#7dc975'),
       (11, 'Herbáceas inundables', '#519799'), (24, 'Áreas urbanas', '#d4271e'), (3, 'Bosques cerrados', '#1f8d49'),
       (19, 'Cultivos temporarios', '#C27BA0'), (25, 'Otras áreas no vegetadas', '#db4d4f'),
       (6, 'Bosques inundables', '#007785')]
lut = np.ones((256, 4)); lut[0] = (1, 1, 1, 1)
for c, _, col in leg: lut[c] = matplotlib.colors.to_rgba(col)
rgb = lut[a]
Wcm, Hcm = 25.4, 10.6
L, T, B = 2.0, 0.7, 1.15
ph = Hcm - T - B; asp = (ext[1] - ext[0]) / (ext[3] - ext[2]); pw = ph * asp
R = 10.4
Wcm = L + pw + R
x0 = (Wcm - (L + pw + R)) / 2 + L
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM))
ax = fig.add_axes([x0 / Wcm, B / Hcm, pw / Wcm, ph / Hcm])
ax.imshow(rgb, extent=ext, interpolation='nearest')
ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
ax.set_xticks([390000, 400000, 410000]); ax.set_yticks([6520000, 6530000, 6540000, 6550000])
ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
ax.tick_params(labelsize=10, length=3)
for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10.5, labelpad=6); ax.set_xlabel('Este, UTM 21S (m)', fontsize=10.5, labelpad=2)
ax.set_title('MapBiomas Argentina, cobertura 2023', fontsize=11.5, pad=4)
ax.text(0.97, 0.22, 'Uruguay\n(fuera del producto)', transform=ax.transAxes, ha='right', va='center', fontsize=10, style='italic')
b = ax.get_position(); xr = b.x1 + 0.45 / Wcm
hs = [Patch(fc=col, ec='black', lw=0.5, label='%d %s (%s %%)' % (c, n, ('%.1f' % pct.get(c, 0)).replace('.', ',')))
      for c, n, col in leg]
lg = fig.legend(handles=hs, loc='upper left', bbox_to_anchor=(xr, b.y1 - 0.2 / Hcm), fontsize=10.5, frameon=False,
                handlelength=1.2, handleheight=1.0, labelspacing=0.3, borderaxespad=0,
                title='Clase (porcentaje de la parte argentina del sitio)', title_fontsize=10.5)
lg._legend_box.align = 'left'
# norte: esquinero superior derecho de la figura
xn = 1 - 0.9 / Wcm
fig.add_artist(FancyArrow(xn, b.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                          head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, b.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
# escala horizontal al costado, abajo
Lm = 10000; fw = Lm / (ext[1] - ext[0]) * b.width; xs = b.x1 + 0.6 / Wcm; ys = b.y0 + 0.5 / Hcm; hh = 0.2 / Hcm
sa = fig.add_axes([xs, ys, fw, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
for vv, t in ((0, '0'), (0.5, '5'), (1, '10 km')):
    fig.text(xs + vv * fw, ys + hh + 0.1 / Hcm, t, ha='center', va='bottom', fontsize=10.5)
fig.savefig(out, dpi=220); plt.close(fig)
print('parte argentina: %.1f %%' % (100 * np.mean(src > 0)), {int(k): round(float(p), 1) for k, p in pct.items()})
