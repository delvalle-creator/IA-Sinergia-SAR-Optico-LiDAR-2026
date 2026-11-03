# Tp6, Figura 18: SAOCOM-1B banda L sobre Concordia. (a) cambio de la HH (gamma0 en dB) entre el 10/10 y el 11/11/2023;
# (b) candidatos a agua bajo vegetacion de la regla relativa a la clase lenosa (L_HH_doble_rebote, en rojo) y agua de
# inundacion en C o en el optico del 04/11/2023 (azul), sobre la HH del 11/11 en grises. Datos: los HH gamma0 a 20 m del
# curso y B_agua_por_sensor_con_L_SAOCOM_relativo_clase_20m.tif (salida de Tp6_02_sinergia_agua.py). Coordenadas UTM 21S
# en metros, un norte en el esquinero superior derecho, escala grafica horizontal al costado. 30/10/2026.
# Uso: python mapas_tp6_f18.py <HH_20231010.tif> <HH_20231111.tif> <relativo_clase.tif> <salida.png> [alto_cm]
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow, Patch
from rasterio.warp import reproject, Resampling
plt.rcParams['font.family'] = 'Liberation Serif'
f1, f2, fr, out = sys.argv[1:5]
Hcm = float(sys.argv[5]) if len(sys.argv) > 5 else 9.5
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
rr = rasterio.open(fr); dsc = list(rr.descriptions); b = rr.bounds
ext = (b.left, b.right, b.bottom, b.top)
def hh(f):
    s = rasterio.open(f); o = np.full((rr.height, rr.width), np.nan, 'f4')
    reproject(s.read(1).astype('f4'), o, src_transform=s.transform, src_crs=s.crs, dst_transform=rr.transform, dst_crs=rr.crs,
              resampling=Resampling.average, src_nodata=np.nan, dst_nodata=np.nan)
    o[o <= 0] = np.nan; return 10 * np.log10(o)
d1, d2 = hh(f1), hh(f2); dd = d2 - d1
c = rr.read(dsc.index('C_Sentinel1_VV') + 1); o = rr.read(dsc.index('Optico_MNDWI') + 1); l = rr.read(dsc.index('L_HH_doble_rebote') + 1)
L, T, B, gap, R = 2.0, 0.7, 3.0, 0.35, 3.0
ph = Hcm - T - B; asp = (ext[1] - ext[0]) / (ext[3] - ext[2]); pw = ph * asp
Wcm = L + 2 * pw + gap + R
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM)); axs = []
for k, t in enumerate(['(a) Cambio de la HH en banda L', '(b) Regla relativa en leñosas']):
    ax = fig.add_axes([(L + k * (pw + gap)) / Wcm, B / Hcm, pw / Wcm, ph / Hcm])
    if k == 0:
        im = ax.imshow(dd, extent=ext, cmap='RdBu_r', vmin=-6, vmax=6, interpolation='nearest')
    else:
        ax.imshow(d2, extent=ext, cmap='gray', vmin=-22, vmax=0, interpolation='nearest')
        ov = np.zeros(dd.shape + (4,), 'f4')
        ov[(c == 1) | (o == 1)] = (0.13, 0.47, 0.95, 1); ov[l == 1] = (0.89, 0.0, 0.0, 1)
        ax.imshow(ov, extent=ext, interpolation='nearest')
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
cax = fig.add_axes([p0.x0 + 0.3 / Wcm, 1.25 / Hcm, p0.width - 0.6 / Wcm, 0.3 / Hcm])
cb = fig.colorbar(im, cax=cax, orientation='horizontal', ticks=[-6, -3, 0, 3, 6]); cb.ax.tick_params(labelsize=10)
cb.ax.set_xticklabels(['−6', '−3', '0', '+3', '+6'])
cb.set_label('ΔHH, 11/11 − 10/10/2023 (dB)', fontsize=10.5, labelpad=1)
fig.legend(handles=[Patch(fc=(0.13, 0.47, 0.95), ec='black', lw=0.5, label='Agua en C o en el óptico, 04/11/2023'),
                    Patch(fc=(0.89, 0, 0), ec='black', lw=0.5, label='ΔHH − 2,59 dB ≥ 3 dB en monte o plantación'),
                    Patch(fc='0.55', ec='black', lw=0.5, label='Fondo: HH del 11/11/2023 (−22 a 0 dB)')],
           loc='upper left', bbox_to_anchor=(p1.x0, 1.95 / Hcm), fontsize=10.5, frameon=False, borderaxespad=0, labelspacing=0.3)
xn = 1 - 0.9 / Wcm
fig.add_artist(FancyArrow(xn, p1.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                          head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, p1.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
Lm = 10000; fw = Lm / (ext[1] - ext[0]) * p1.width; xs = p1.x1 + 0.4 / Wcm; ys = p1.y0 + 0.5 / Hcm; hh_ = 0.2 / Hcm
sa = fig.add_axes([xs, ys, fw, hh_]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
for vv, t in ((0, '0'), (0.5, '5'), (1, '10 km')):
    fig.text(xs + vv * fw, ys + hh_ + 0.1 / Hcm, t, ha='center', va='bottom', fontsize=10.5)
fig.savefig(out, dpi=220); plt.close(fig)
print('ancho %.2f; mediana dHH %.2f dB; candidatos L %.1f %% (%.0f ha)' % (Wcm, np.nanmedian(dd), 100 * np.mean(l == 1), (l == 1).sum() * .04))
