# Tp6, Figura 36: embeddings AlphaEarth 2023 (CP1-CP2-CP3) (a), agua segun kNN con los embeddings, 20 + 20 muestras,
# semilla 2026, grilla de 40 m (b), y agua de inundacion en banda C del 04/11/2023, variante C (c), con el agua
# permanente JRC >= 90 % en gris. Coordenadas UTM 21S en m, un norte en el esquinero superior derecho, escala grafica
# horizontal al costado, leyenda debajo de cada panel. 30/10/2026.
# Uso: python mapas_tp6_f36.py <CP_RGB_8bit.tif> <knn_40m.tif> <B_variante_C_20231104.tif> <JRC_ocurrencia.tif> <salida.png> [alto_cm]
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap
from rasterio.warp import reproject, Resampling
plt.rcParams['font.family'] = 'Liberation Serif'
fcp, fk, fc, fj, out = sys.argv[1:6]
Hcm = float(sys.argv[6]) if len(sys.argv) > 6 else 7.6
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
rk = rasterio.open(fk); b = rk.bounds; ext = (b.left, b.right, b.bottom, b.top)
knn = rk.read(1).astype('f4'); knn[knn == 255] = np.nan
rc = rasterio.open(fcp); F = 4
cp = rc.read(out_shape=(3, rc.height // F, rc.width // F)).transpose(1, 2, 0) / 255.0
cp[(cp == 0).all(2)] = 1
rv = rasterio.open(fc); vc = np.full(knn.shape, np.nan, 'f4')
a = rv.read(1).astype('f4'); a[a == rv.nodata] = np.nan
reproject(a, vc, src_transform=rv.transform, src_crs=rv.crs, dst_transform=rk.transform, dst_crs=rk.crs,
          resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
rj = rasterio.open(fj); jrc = np.full(knn.shape, np.nan, 'f4')
reproject(rj.read(1).astype('f4'), jrc, src_transform=rj.transform, src_crs=rj.crs, dst_transform=rk.transform,
          dst_crs=rk.crs, resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
c3 = np.zeros(knn.shape, 'u1'); c3[vc == 1] = 1; c3[jrc >= 90] = 2
AZ = '#2532e4'
L, T, B, gap, LEG = 1.3, 0.6, 1.05, 0.35, 1.7
ph = Hcm - T - B - LEG; pw = ph * (ext[1] - ext[0]) / (ext[3] - ext[2])
Wcm = L + 3 * pw + 2 * gap + 2.5
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM)); axs = []
tit = ['(a) CP1-CP2-CP3', '(b) Agua según kNN', '(c) Banda C, 04/11/2023']
for k in range(3):
    ax = fig.add_axes([(L + k * (pw + gap)) / Wcm, (B + LEG) / Hcm, pw / Wcm, ph / Hcm])
    if k == 0: ax.imshow(cp, extent=ext, interpolation='bilinear')
    elif k == 1: ax.imshow(knn, extent=ext, cmap=ListedColormap(['#f0f0f0', AZ]), vmin=0, vmax=1, interpolation='nearest')
    else: ax.imshow(c3, extent=ext, cmap=ListedColormap(['#f0f0f0', AZ, '#a9a9a9']), vmin=0, vmax=2, interpolation='nearest')
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_xticks([390000, 410000]); ax.set_yticks([6520000, 6540000])
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.tick_params(labelsize=11, length=3, pad=1.5)
    for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    if k: ax.set_yticklabels([])
    else: ax.set_ylabel('Norte, UTM 21S (m)', fontsize=11, labelpad=2)
    ax.set_xlabel('Este, UTM 21S (m)', fontsize=11, labelpad=1)
    ax.set_title(tit[k], fontsize=11.5, pad=3); axs.append(ax)
legs = [[Patch(fc='white', ec='white', label='Colores sin significado fijo')],
        [Patch(fc=AZ, ec='black', lw=0.5, label='Agua (kNN)'), Patch(fc='#f0f0f0', ec='black', lw=0.5, label='Tierra (kNN)')],
        [Patch(fc=AZ, ec='black', lw=0.5, label='Agua de inundación'), Patch(fc='#a9a9a9', ec='black', lw=0.5, label='Agua permanente (JRC ≥ 90 %)'),
         Patch(fc='#f0f0f0', ec='black', lw=0.5, label='Sin agua de inundación')]]
for ax, h in zip(axs, legs):
    p = ax.get_position()
    fig.legend(handles=h, loc='upper left', bbox_to_anchor=(p.x0 - 0.1 / Wcm, (LEG + 0.05) / Hcm), fontsize=11,
               frameon=False, labelspacing=0.25, handlelength=1.2, handletextpad=0.4, borderaxespad=0, borderpad=0)
p2 = axs[2].get_position(); xn = 1 - 1.0 / Wcm
fig.add_artist(FancyArrow(xn, p2.y1 - 1.25 / Hcm, 0, 0.85 / Hcm, width=0.07 / Wcm, head_width=0.34 / Wcm,
                          head_length=0.34 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, p2.y1 - 0.36 / Hcm, 'N', ha='center', va='bottom', fontsize=13, fontweight='bold')
Lm = 10000; fw = Lm / (ext[1] - ext[0]) * p2.width; xs = p2.x1 + 0.5 / Wcm; ys = p2.y0 + 0.3 / Hcm; hh = 0.18 / Hcm
sa = fig.add_axes([xs, ys, fw, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
for vv, t in ((0, '0'), (1, '10 km')):
    fig.text(xs + vv * fw, ys + hh + 0.08 / Hcm, t, ha='center', va='bottom', fontsize=11)
fig.savefig(out, dpi=250); plt.close(fig)
okv = np.isfinite(knn) & np.isfinite(vc)
ev = vc == 1
print('ancho %.2f; dentro %.1f fuera %.1f tierraJRC0 %.1f' % (Wcm, 100 * np.nanmean(knn[ev & okv]), 100 * np.nanmean(knn[okv & ~ev]), 100 * np.nanmean(knn[okv & ~ev & (jrc == 0)])))
