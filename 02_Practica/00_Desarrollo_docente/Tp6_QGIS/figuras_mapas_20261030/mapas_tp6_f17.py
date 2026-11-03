# Tp6, Figura 17: donde coinciden y donde no el radar (banda C, VV < -15 dB) y el optico (MNDWI > 0) el 04/11/2023,
# en todo el sitio (a) y en Concordia, detalle de 14 x 14 km (b), desde B_agua_por_sensor_20231104_20m.tif
# (salida de Tp6_02_sinergia_agua.py) y el agua permanente JRC >= 90 %. Coordenadas UTM 21S en metros, una flecha norte
# en el esquinero superior derecho, una escala grafica horizontal al costado de cada panel (distinta escala). 30/10/2026.
# Uso: python mapas_tp6_f17.py <B_agua_por_sensor_20231104_20m.tif> <B_CONCORDIA_JRC_GSW_ocurrencia.tif> <salida.png> [alto_cm]
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap
from rasterio.warp import reproject, Resampling
plt.rcParams['font.family'] = 'Liberation Serif'
fa, fj, out = sys.argv[1:4]
Hcm = float(sys.argv[4]) if len(sys.argv) > 4 else 9.0
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
r = rasterio.open(fa); dsc = list(r.descriptions); b = r.bounds
ext = (b.left, b.right, b.bottom, b.top)
c = r.read(dsc.index('C_Sentinel1_VV') + 1); o = r.read(dsc.index('Optico_MNDWI') + 1)
rj = rasterio.open(fj); jrc = np.full(c.shape, np.nan, 'f4')
reproject(rj.read(1).astype('f4'), jrc, src_transform=rj.transform, src_crs=rj.crs, dst_transform=r.transform,
          dst_crs=r.crs, resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
cl = np.zeros(c.shape, 'u1')
cl[(c == 1) & (o == 1)] = 1; cl[(c == 1) & (o == 0)] = 2; cl[(c == 0) & (o == 1)] = 3
cl[o == -9999] = 5; cl[jrc >= 90] = 4
cols = ['#f0f0f0', '#1f6fb4', '#e6550d', '#31a354', '#a9a9a9', '#ffffff']
cm = ListedColormap(cols)
det = (398000, 412000, 6519000, 6533000)
L, T, B, R = 2.0, 0.7, 2.1, 3.0
ph = Hcm - T - B
pa = ph * (ext[1] - ext[0]) / (ext[3] - ext[2]); pb = ph
gap = 3.6
Wcm = L + pa + gap + pb + R
fig = plt.figure(figsize=(Wcm * CM, Hcm * CM)); axs = []
for k, (e, t, xt, yt, Lm) in enumerate([(ext, '(a) Sitio', [390000, 400000, 410000], [6520000, 6530000, 6540000, 6550000], 10000),
                                       (det, '(b) Concordia', [400000, 405000, 410000], [6520000, 6525000, 6530000], 4000)]):
    x0 = L if k == 0 else L + pa + gap
    w = pa if k == 0 else pb
    ax = fig.add_axes([x0 / Wcm, B / Hcm, w / Wcm, ph / Hcm])
    ax.imshow(cl, extent=ext, cmap=cm, vmin=0, vmax=5, interpolation='nearest')
    ax.set_xlim(e[0], e[1]); ax.set_ylim(e[2], e[3])
    ax.set_xticks(xt); ax.set_yticks(yt)
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.tick_params(labelsize=10, length=3)
    for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10.5, labelpad=6)
    ax.set_xlabel('Este, UTM 21S (m)', fontsize=10.5, labelpad=2)
    ax.set_title(t, fontsize=11.5, pad=4); axs.append(ax)
    p = ax.get_position()
    fw = Lm / (e[1] - e[0]) * p.width; xs = p.x1 + 0.35 / Wcm; ys = p.y0 + 0.2 / Hcm; hh = 0.2 / Hcm
    sa = fig.add_axes([xs, ys, fw, hh]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
    sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
    for vv, tt in ((0, '0'), (1, '%d km' % (Lm // 1000))):
        fig.text(xs + vv * fw, ys + hh + 0.1 / Hcm, tt, ha='center', va='bottom', fontsize=10.5)
    if k == 0:  # recuadro del detalle
        ax.add_patch(Rectangle((det[0], det[2]), det[1] - det[0], det[3] - det[2], fill=False, ec='black', lw=1.2))
pb_ = axs[-1].get_position()
xn = 1 - 0.9 / Wcm
fig.add_artist(FancyArrow(xn, pb_.y1 - 1.3 / Hcm, 0, 0.9 / Hcm, width=0.07 / Wcm, head_width=0.36 / Wcm,
                          head_length=0.36 / Hcm, length_includes_head=True, color='black', transform=fig.transFigure))
fig.text(xn, pb_.y1 - 0.38 / Hcm, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')
hs = [Patch(fc=cols[1], ec='black', lw=0.5, label='Agua para C y para el óptico'), Patch(fc=cols[2], ec='black', lw=0.5, label='Sólo C'),
      Patch(fc=cols[3], ec='black', lw=0.5, label='Sólo el óptico'), Patch(fc=cols[4], ec='black', lw=0.5, label='Agua permanente (excluida)'),
      Patch(fc=cols[5], ec='black', lw=0.5, label='Nubes')]
fig.legend(handles=hs, loc='lower center', ncol=5, fontsize=10.5, frameon=False, bbox_to_anchor=(0.5, 0.0), columnspacing=1.2, handlelength=1.3)
fig.savefig(out, dpi=220); plt.close(fig)
ha = lambda m: m.sum() * 0.04
print('ancho %.2f cm; ambos %.0f ha, solo C %.0f ha, solo optico %.0f ha' % (Wcm, ha(cl == 1), ha(cl == 2), ha(cl == 3)))
