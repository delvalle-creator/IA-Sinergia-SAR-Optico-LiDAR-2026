# Tp6, Figura 23: profundidad plausible de la variante multisensor del 04/11/2023 en el banado al oeste de Concordia
# (detalle de 8 x 8 km: E 396.000-404.000, N 6.521.000-6.529.000) con el Copernicus DEM (a) y con FABDEM (b), sobre el
# Sentinel-2 en color natural; en naranja los pixeles con profundidad negativa o nula (banda profundidad_sin_recortar_m <= 0).
# Datos: B_profundidad_multisensor_20231104[_fabdem]_20m.tif (salida de Tp6_04_profundidad.py). Coordenadas UTM 21S en m,
# una flecha norte en el esquinero superior derecho, escala grafica horizontal al costado. 30/10/2026.
# Uso: python mapas_tp6_f23.py <S2_20231104.tif> <prof_copernicus.tif> <prof_fabdem.tif> <salida.png> [alto_cm]
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow, Patch
from rasterio.windows import from_bounds
plt.rcParams['font.family'] = 'Liberation Serif'
fs, fa, fb, out = sys.argv[1:5]
Hcm = float(sys.argv[5]) if len(sys.argv) > 5 else 10.5
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
coma = FuncFormatter(lambda v, _: ('%g' % v).replace('.', ','))
X0, X1, Y0, Y1 = 396000, 404000, 6521000, 6529000
ext = (X0, X1, Y0, Y1)
s = rasterio.open(fs); d = list(s.descriptions); w = from_bounds(X0, Y0, X1, Y1, s.transform)
a = s.read([d.index(b) + 1 for b in ('B04', 'B03', 'B02')], window=w).astype('f4')
rgb = np.zeros(a.shape[1:] + (3,), 'f4')
for i in range(3):
    v = a[i][a[i] > 0]; lo, hi = np.percentile(v, [2, 98]); rgb[..., i] = np.clip((a[i] - lo) / (hi - lo), 0, 1)
def prof(f):
    r = rasterio.open(f); ww = from_bounds(X0, Y0, X1, Y1, r.transform); dd = list(r.descriptions)
    p = r.read(dd.index('profundidad_sin_recortar_m') + 1, window=ww).astype('f4')
    p[p == r.nodata] = np.nan; return p
L, T, B, gap, R = 2.0, 0.7, 2.6, 0.35, 2.9
ph = Hcm - T - B; pw = ph; Wcm = L + 2 * pw + gap + R
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM)); axs = []
for k, (f, t) in enumerate([(fa, '(a) Copernicus DEM (superficie)'), (fb, '(b) FABDEM (terreno desnudo)')]):
    p = prof(f)
    ax = fig.add_axes([(L + k * (pw + gap)) / Wcm, B / Hcm, pw / Wcm, ph / Hcm])
    ax.imshow(rgb, extent=ext, interpolation='bilinear')
    im = ax.imshow(np.ma.masked_where(~(p > 0), p), extent=ext, cmap='Blues', vmin=0, vmax=3, interpolation='nearest')
    ng = np.zeros(p.shape + (4,), 'f4'); ng[p <= 0] = (1.0, 0.5, 0.0, 1)
    ax.imshow(ng, extent=ext, interpolation='nearest')
    ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1)
    ax.set_xticks([398000, 400000, 402000]); ax.set_yticks([6522000, 6525000, 6528000])
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.tick_params(labelsize=10, length=3)
    for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    if k: ax.set_yticklabels([])
    else: ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10.5, labelpad=6)
    ax.set_xlabel('Este, UTM 21S (m)', fontsize=10.5, labelpad=2)
    ax.set_title(t, fontsize=11.5, pad=4); axs.append(ax)
p0, p1 = [x.get_position() for x in axs]
cax = fig.add_axes([p0.x0 + 0.4 / Wcm, 1.2 / Hcm, p0.width - 0.8 / Wcm, 0.3 / Hcm])
cb = fig.colorbar(im, cax=cax, orientation='horizontal', ticks=[0, 0.5, 1, 1.5, 2, 2.5, 3], extend='max')
cb.ax.xaxis.set_major_formatter(coma); cb.ax.tick_params(labelsize=10)
cb.set_label('Profundidad plausible (m)', fontsize=10.5, labelpad=1)
fig.legend(handles=[Patch(fc=(1.0, 0.5, 0.0), ec='black', lw=0.5, label='Profundidad negativa o nula\n(cota del MDE ≥ cota del borde)')],
           loc='upper left', bbox_to_anchor=(p1.x0 + 0.3 / Wcm, 1.55 / Hcm), fontsize=10.5, frameon=False, borderaxespad=0)
xn = 1 - 0.9 / Wcm
fig.add_artist(FancyArrow(xn, p1.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                          head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, p1.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
Lm = 2000; fw = Lm / (X1 - X0) * p1.width; xs = p1.x1 + 0.4 / Wcm; ys = p1.y0 + 0.4 / Hcm; hh = 0.2 / Hcm
sa = fig.add_axes([xs, ys, fw, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
for vv, t in ((0, '0'), (0.5, '1'), (1, '2 km')):
    fig.text(xs + vv * fw, ys + hh + 0.1 / Hcm, t, ha='center', va='bottom', fontsize=10.5)
fig.savefig(out, dpi=220); plt.close(fig)
print('ancho %.2f' % Wcm)
