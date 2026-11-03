# Tp5: mapas del Desarrollo con escala y norte FUERA del mapa (29/10/2026).
# Redibuja desde los rasteres del practico; estilo de estilo_mapas_tp2.py.
import sys, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, Patch, FancyArrow
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, BoundaryNorm
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
import xml.etree.ElementTree as ET
import os
plt.rcParams['font.family'] = 'Liberation Serif'; plt.rcParams['font.size'] = 10
U = '/mnt/user-data/uploads/CURSOS_CEREGEO_2026/02_Practica/'
T = U + 'Tp5_Incendios/'; G = T + '02_Subsets_SNAP_QGIS/'; QG = G + 'QGIS_GeoTIFF/'; RGB = G + 'RGB_copol_cruzada_cociente/'
SAO = G + 'SAOCOM_gamma0/RGB_copol_cruzada_cociente/'; RAS = T + '05_Resultados/02_Rasters/'
PL = U + '00_COMUN/08_Originales_crudos/PLANETARY/A1_DELTA_QUEMAS/sentinel-2-l2a/'
OUT = os.environ.get('OUT_MAPAS', '/tmp/maps/')
import os; os.makedirs(OUT, exist_ok=True)
SITIO = (223640, 246920, 6304880, 6337680)
NO = (224000, 236000, 6318000, 6330000)
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
WHITE = (1, 1, 1)


def warp(f, bands, ext=SITIO, res=20, cat=False, nodata=None):
    r = rasterio.open(f); x0, x1, y0, y1 = ext
    nx, ny = int(round((x1 - x0) / res)), int(round((y1 - y0) / res)); Tt = from_origin(x0, y1, res, res)
    out = np.full((len(bands), ny, nx), np.nan, 'f4')
    nd = r.nodata if nodata is None else nodata
    kw = {}
    if r.crs is None:
        g, c = r.gcps; kw = dict(gcps=g, src_crs=c)
    else:
        kw = dict(src_transform=r.transform, src_crs=r.crs)
    for i, b in enumerate(bands):
        a = r.read(b).astype('f4')
        if nd is not None and not (isinstance(nd, float) and np.isnan(nd)):
            a[a == nd] = np.nan
        reproject(a, out[i], dst_transform=Tt, dst_crs='EPSG:32721', src_nodata=np.nan, dst_nodata=np.nan,
                  resampling=Resampling.nearest if cat else Resampling.bilinear, **kw)
    return out


def rgb8(f, ext=SITIO, res=20):
    a = warp(f, (1, 2, 3), ext, res)
    m = np.isnan(a).any(0) | (np.nan_to_num(a) == 0).all(0)
    im = np.clip(np.nan_to_num(a) / 255., 0, 1); im = np.moveaxis(im, 0, -1); im[m] = WHITE
    return im


def s2(f, ext=SITIO, res=20):
    a = warp(f, (10, 8, 3), ext, res) / 10000.
    lo = np.array([0.10, 0.08, 0.02])[:, None, None]; hi = np.array([0.35, 0.25, 0.14])[:, None, None]
    m = np.isnan(a).any(0)
    im = np.moveaxis(np.clip((np.nan_to_num(a) - lo) / (hi - lo), 0, 1), 0, -1); im[m] = WHITE
    return im


def classes(a, pal):
    """pal: list of (value, color). Devuelve imagen RGB; sin dato en blanco."""
    im = np.ones(a.shape + (3,))
    for v, c in pal:
        im[a == v] = matplotlib.colors.to_rgb(c)
    return im


# ---------- maquetacion
MAXH = {'F02': 9.6, 'F03': 13.0, 'F04': 13.4, 'F05': 14.0, 'F06': 8.3, 'F07': 11.8, 'F08': 13.9, 'F09': 13.9, 'F11': 13.0,
        'F12': 12.4, 'F16': 12.0, 'F17': 13.3, 'F24': 12.0, 'F25': 13.4, 'F29': 14.0, 'F30': 12.3}
MAXH_CUR = [14.8]


def layout(Wcm, n, ext, top=0.95, bottom_extra=0.0, ylab=True, maxH=None, title_lines=1):
    maxH = maxH or MAXH_CUR[0]
    L = 1.75 if ylab else 0.5; R = 1.15; gap = 0.35
    tH = 0.25 + 0.5 * title_lines
    bot = 1.05 + 1.05 + bottom_extra        # rotulos x + escala + leyenda
    asp = (ext[3] - ext[2]) / (ext[1] - ext[0])
    pw = (Wcm - L - R - gap * (n - 1)) / n
    ph = pw * asp
    if ph + tH + bot > maxH:
        ph = maxH - tH - bot; pw = ph / asp
    Hcm = ph + tH + bot
    used = L + n * pw + (n - 1) * gap + R; off = (Wcm - used) / 2
    fig = plt.figure(figsize=(Wcm * CM, Hcm * CM))
    axs = []
    for k in range(n):
        x = (off + L + k * (pw + gap)) / Wcm; y = bot / Hcm
        axs.append(fig.add_axes([x, y, pw / Wcm, ph / Hcm]))
    fig._geo = dict(W=Wcm, H=Hcm, bot=bot, bottom_extra=bottom_extra, pw=pw)
    return fig, axs


def frame(ax, ext, left=True, step=None):
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect('equal')
    if step:
        ax.xaxis.set_major_locator(MultipleLocator(step)); ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.tick_params(labelsize=9, length=3)
    for l in ax.get_yticklabels():
        l.set_rotation(90); l.set_va('center')
    if not left:
        ax.set_yticklabels([])


def show(ax, im, ext, k, title, step, **kw):
    ax.imshow(im, extent=ext, interpolation='nearest', **kw)
    if step in (5000, 10000):
        step = 5000 if ax.figure._geo['pw'] >= 8.5 else 10000
    frame(ax, ext, left=(k == 0), step=step)
    if title:
        ax.set_title(title, fontsize=10.5, pad=4)
    ax.set_xlabel('Este, UTM 21S (m)', fontsize=10, labelpad=2)
    if k == 0:
        ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10, labelpad=2)


def escala_norte(fig, ax, Lm, txt, axn=None):
    """Barra de escala FUERA del mapa, bajo el primer panel; norte FUERA, en el esquinero superior derecho."""
    g = fig._geo; W, H = g['W'], g['H']
    b = ax.get_position(); ext = ax.get_xlim(); frac = Lm / (ext[1] - ext[0]) * b.width
    y = (g['bottom_extra'] + 0.25) / H; h = 0.18 / H; x0 = b.x0
    sa = fig.add_axes([x0, y, frac, h]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
    sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8))
    sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
    fig.text(x0, y + h + 0.08 / H, '0', ha='center', va='bottom', fontsize=10)
    fig.text(x0 + frac, y + h + 0.08 / H, txt, ha='center', va='bottom', fontsize=10)
    bn = (axn or ax).get_position(); xn = bn.x1 + 0.55 / W; yt = bn.y1
    fig.add_artist(FancyArrow(xn, yt - 1.25 / H, 0, 0.85 / H, width=0.06 / W, head_width=0.32 / W,
                              head_length=0.32 / H, length_includes_head=True, color='black',
                              transform=fig.transFigure))
    fig.text(xn, yt - 0.38 / H, 'N', ha='center', va='bottom', fontsize=11, fontweight='bold')


def leyenda(fig, items, ncol, y_cm=None, x=0.5):
    g = fig._geo
    h = [Patch(facecolor=c, edgecolor='#555555', lw=0.8, label=t) for t, c in items]
    yy = (g['bottom_extra'] - 0.1) / g['H'] if y_cm is None else y_cm / g['H']
    fig.legend(handles=h, loc='upper center', bbox_to_anchor=(x, yy), ncol=ncol, frameon=False, fontsize=10,
               handlelength=1.6, columnspacing=1.4, handletextpad=0.5)


def barra(fig, mappable, label, x0, x1, ticks=None, fmt=None):
    g = fig._geo; H = g['H']
    cax = fig.add_axes([x0, (g['bottom_extra'] - 0.55) / H, x1 - x0, 0.3 / H])
    cb = fig.colorbar(mappable, cax=cax, orientation='horizontal', ticks=ticks)
    cb.ax.tick_params(labelsize=10)
    if fmt:
        cb.ax.xaxis.set_major_formatter(FuncFormatter(fmt))
    cb.set_label(label, fontsize=10, labelpad=2)
    return cb


coma = lambda v, _: ('%g' % v).replace('.', ',').replace('-', '−')


def guardar(fig, n):
    fig.savefig(OUT + n, dpi=180); plt.close(fig); print(n)


todo = sys.argv[1:] or ['F02', 'F03', 'F04', 'F05', 'F06', 'F07', 'F08', 'F09', 'F11', 'F12', 'F16', 'F17', 'F24', 'F25', 'F29', 'F30']


def dos_rgb(n, W, ims, titles, step=5000):
    fig, axs = layout(W, len(ims), SITIO)
    for k, (ax, im, t) in enumerate(zip(axs, ims, titles)):
        show(ax, im, SITIO, k, t, step)
    escala_norte(fig, axs[0], 5000, '5 km', axn=axs[-1])
    guardar(fig, n)


if 'F02' in todo:
    MAXH_CUR[0] = MAXH['F02']
    dos_rgb('F02.png', 13.7, [s2(QG + 'A1_DELTA_QUEMAS_S2_20200715.tif'), s2(QG + 'A1_DELTA_QUEMAS_S2_20201013.tif')],
            ['(a) Sentinel-2, 15/07/2020', '(b) Sentinel-2, 13/10/2020'], step=10000)
if 'F03' in todo:
    MAXH_CUR[0] = MAXH['F03']
    dos_rgb('F03.png', 19.6, [rgb8(RGB + 'A1_DELTA_QUEMAS_S1_C_20200716_RGB_8bit.tif'), rgb8(RGB + 'A1_DELTA_QUEMAS_S1_C_20200926_RGB_8bit.tif')],
            ['(a) Sentinel-1, 16/07/2020', '(b) Sentinel-1, 26/09/2020'])
if 'F04' in todo:
    MAXH_CUR[0] = MAXH['F04']
    dos_rgb('F04.png', 20.2, [rgb8(SAO + 'A1_DELTA_QUEMAS_SAOCOM_L_20200721_QP_gamma0_RGB_8bit.tif'), rgb8(SAO + 'A1_DELTA_QUEMAS_SAOCOM_L_20201025_QP_gamma0_RGB_8bit.tif')],
            ['(a) SAOCOM-1A, 21/07/2020', '(b) SAOCOM-1A, 25/10/2020'])
if 'F05' in todo:
    MAXH_CUR[0] = MAXH['F05']
    dos_rgb('F05.png', 21.5, [rgb8(RGB + 'A1_DELTA_QUEMAS_ALOS2_L_mosaico2019_RGB_8bit.tif'), rgb8(RGB + 'A1_DELTA_QUEMAS_ALOS2_L_mosaico2020_RGB_8bit.tif')],
            ['(a) ALOS-2, mosaico 2019', '(b) ALOS-2, mosaico 2020'])

if 'F06' in todo:
    MAXH_CUR[0] = MAXH['F06']
    ims = [s2(QG + 'A1_DELTA_QUEMAS_S2_20200715.tif', NO, 10), s2(QG + 'A1_DELTA_QUEMAS_S2_20201013.tif', NO, 10),
           rgb8(RGB + 'A1_DELTA_QUEMAS_S1_C_20200716_RGB_8bit.tif', NO, 10), rgb8(RGB + 'A1_DELTA_QUEMAS_S1_C_20200926_RGB_8bit.tif', NO, 10)]
    fig, axs = layout(25.7, 4, NO)
    for k, (ax, im, t) in enumerate(zip(axs, ims, ['(a) S2 15/07', '(b) S2 13/10', '(c) S1 16/07', '(d) S1 26/09'])):
        show(ax, im, NO, k, t, None)
        ax.set_xticks([226000, 230000, 234000]); ax.set_yticks([6320000, 6324000, 6328000])
        if k: ax.set_yticklabels([])
        else:
            for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    escala_norte(fig, axs[0], 2000, '2 km', axn=axs[-1])
    guardar(fig, 'F06.png')

if 'F07' in todo:
    MAXH_CUR[0] = MAXH['F07']
    a = warp(QG + 'A1_DELTA_QUEMAS_MapBiomas_cobertura_1985_2025.tif', (36,), cat=True)[0]
    q = ET.parse(QG + 'A1_DELTA_QUEMAS_MapBiomas_cobertura_1985_2025.qml')
    pal = {int(e.get('value')): (e.get('color'), e.get('label')) for e in q.iter('paletteEntry')}
    u, c = np.unique(a[~np.isnan(a)], return_counts=True)
    pres = [int(v) for v, _ in sorted(zip(u, c), key=lambda t: -t[1]) if int(v) in pal]
    print('MapBiomas 2020 clases:', pres)
    acc = {'Herbaceas': 'Herbáceas', 'Rios': 'Ríos', 'oceano': 'océano', 'areas': 'áreas', 'Areas': 'Áreas',
           'vegetacion': 'vegetación', 'Area': 'Área', 'herbacea': 'herbácea'}
    def lab(s):
        for k_, v_ in acc.items():
            s = s.replace(k_, v_)
        return s
    fig, axs = layout(14.0, 1, SITIO, bottom_extra=1.4)
    show(axs[0], classes(a, [(v, pal[v][0]) for v in pres]), SITIO, 0, 'MapBiomas, cobertura 2020', 5000)
    escala_norte(fig, axs[0], 5000, '5 km')
    leyenda(fig, [(lab(pal[v][1]), pal[v][0]) for v in pres], ncol=2)
    guardar(fig, 'F07.png')

MES = ["#313695", "#4575b4", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027", "#a50026", "#67001f"]
MESN = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
FRQ = ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15", "#67000d"]
if 'F08' in todo:
    MAXH_CUR[0] = MAXH['F08']
    m = warp(QG + 'A1_DELTA_QUEMAS_MapBiomas_fuego_mes_1999_2025.tif', (22,), cat=True)[0]
    fq = warp(QG + 'A1_DELTA_QUEMAS_MapBiomas_fuego_frecuencia_1999_2025.tif', (1,), cat=True)[0]
    fig, axs = layout(17.2, 2, SITIO, bottom_extra=2.0)
    show(axs[0], classes(m, list(zip(range(1, 13), MES))), SITIO, 0, '(a) Mes de quema, 2020', 5000)
    show(axs[1], classes(fq, list(zip(range(1, 7), FRQ))), SITIO, 1, '(b) Años con quema, 1999–2025', 5000)
    escala_norte(fig, axs[0], 5000, '5 km', axn=axs[1])
    it = list(zip(MESN, MES)) + [('1 año', FRQ[0]), ('3 años', FRQ[2]), ('6 años', FRQ[5])]
    # orden por columnas como la figura original (3 filas)
    leyenda(fig, it, ncol=5)
    guardar(fig, 'F08.png')

if 'F09' in todo:
    MAXH_CUR[0] = MAXH['F09']
    agb = warp(QG + 'A1_DELTA_QUEMAS_CCI_Biomass_v7_AGB.tif', (3, 8), nodata=65535)
    fig, axs = layout(17.2, 2, SITIO, bottom_extra=1.75)
    im0 = axs[0].imshow(agb[0], extent=SITIO, cmap='Greens', vmin=0, vmax=60, interpolation='nearest')
    show(axs[0], np.zeros((1, 1, 4)), SITIO, 0, '(a) AGB 2020', 5000)
    im1 = axs[1].imshow(agb[1], extent=SITIO, cmap='Oranges', vmin=0, vmax=40, interpolation='nearest')
    show(axs[1], np.zeros((1, 1, 4)), SITIO, 1, '(b) Desvío estándar 2020', 5000)
    escala_norte(fig, axs[0], 5000, '5 km', axn=axs[1])
    b0 = axs[0].get_position(); b1 = axs[1].get_position()
    # una barra bajo cada panel (30/10/2026): AGB en verde y desvío estándar en naranja
    barra(fig, im0, '(a) AGB (Mg/ha)', b0.x0 + 0.01, b0.x1 - 0.01, ticks=[0, 10, 20, 30, 40, 50, 60])
    barra(fig, im1, '(b) Desvío estándar (Mg/ha)', b1.x0 + 0.01, b1.x1 - 0.01, ticks=[0, 10, 20, 30, 40])
    guardar(fig, 'F09.png')

IND = G + 'A1_DELTA_QUEMAS_indicadores_20m.tif'
if 'F11' in todo:
    MAXH_CUR[0] = MAXH['F11']
    d = warp(IND, (1, 5, 3), cat=True)
    fig, axs = layout(20.7, 3, SITIO, bottom_extra=1.75)
    for k, (t) in enumerate(['(a) ΔVH banda C', '(b) ΔHV SAOCOM', '(c) ΔHV ALOS-2']):
        im = axs[k].imshow(d[k], extent=SITIO, cmap='RdBu', vmin=-6, vmax=6, interpolation='nearest')
        show(axs[k], np.zeros((1, 1, 4)), SITIO, k, t, 5000)
    escala_norte(fig, axs[0], 5000, '5 km', axn=axs[2])
    b0 = axs[0].get_position(); b2 = axs[2].get_position(); cx = (b0.x0 + b2.x1) / 2
    barra(fig, im, 'cambio 10·log10(post/pre), dB', cx - 0.25, cx + 0.25, fmt=coma)
    guardar(fig, 'F11.png')

DNBR = LinearSegmentedColormap.from_list('dnbr', [((v + 0.1) / 0.76, c) for v, c in
                                                  [(-0.1, "#1a9850"), (0.1, "#ffffbf"), (0.27, "#fdae61"), (0.44, "#f46d43"), (0.66, "#a50026")]])
if 'F12' in todo:
    MAXH_CUR[0] = MAXH['F12']
    d = warp(IND, (8,), cat=True)[0]
    fig, axs = layout(14.8, 1, SITIO, bottom_extra=1.75)
    im = axs[0].imshow(d, extent=SITIO, cmap=DNBR, vmin=-0.1, vmax=0.66, interpolation='nearest')
    show(axs[0], np.zeros((1, 1, 4)), SITIO, 0, 'dNBR, 15/07 → 13/10/2020', 5000)
    escala_norte(fig, axs[0], 5000, '5 km')
    b = axs[0].get_position()
    barra(fig, im, 'dNBR', b.x0 - 0.06, b.x1 + 0.06, ticks=[-0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6], fmt=coma)
    guardar(fig, 'F12.png')

BIN = [(1, '#d7301f'), (0, '#f0f0f0')]
if 'F16' in todo:
    MAXH_CUR[0] = MAXH['F16']
    d = warp(RAS + 'A1_quema_por_sensor_20m.tif', (1, 2, 3, 4), cat=True)
    fig, axs = layout(25.5, 4, SITIO, bottom_extra=0.8)
    for k, t in enumerate(['(a) C: ΔVH < 1 dB', '(b) ALOS-2: ΔHV < −2 dB', '(c) SAOCOM: ΔHV < 1 dB', '(d) dNBR > 0,15']):
        show(axs[k], classes(d[k], BIN), SITIO, k, t, 10000)
    escala_norte(fig, axs[0], 5000, '5 km', axn=axs[3])
    leyenda(fig, [('quemado', '#d7301f'), ('no quemado', '#f0f0f0')], ncol=2)
    guardar(fig, 'F16.png')

if 'F17' in todo:
    MAXH_CUR[0] = MAXH['F17']
    d = warp(RAS + 'A1_sensores_que_coinciden_20m.tif', (1,), cat=True)[0]
    P = ["#fcfbfd", "#fdd49e", "#fc8d59", "#d7301f", "#7f0000"]
    fig, axs = layout(16.4, 1, SITIO, bottom_extra=0.8)
    show(axs[0], classes(d, list(zip(range(5), P))), SITIO, 0, 'Sensores que marcan quema', 5000)
    escala_norte(fig, axs[0], 5000, '5 km')
    leyenda(fig, [(str(v), P[v]) for v in range(5)], ncol=5)
    guardar(fig, 'F17.png')

if 'F24' in todo:
    MAXH_CUR[0] = MAXH['F24']
    fs = ['A1_variante_optico.tif', 'A1_variante_C.tif', 'A1_variante_CL.tif', 'A1_variante_multisensor.tif']
    fig, axs = layout(25.1, 4, SITIO, bottom_extra=0.8)
    for k, (f, t) in enumerate(zip(fs, ['(a) V1 óptico solo', '(b) V2 SAR solo (C)', '(c) V3 SAR multibanda', '(d) V4 multisensor'])):
        d = warp(RAS + f, (1,), cat=True)[0]
        show(axs[k], classes(d, [(1, '#d7301f'), (2, '#f0f0f0')]), SITIO, k, t, 10000)
    escala_norte(fig, axs[0], 5000, '5 km', axn=axs[3])
    leyenda(fig, [('quemado', '#d7301f'), ('no quemado', '#f0f0f0')], ncol=2)
    guardar(fig, 'F24.png')

if 'F25' in todo:
    MAXH_CUR[0] = MAXH['F25']
    d = warp(RAS + 'A1_severidad_multisensor.tif', (1, 2), cat=True)
    SEV = [(1, "#7f0000"), (2, "#fc8d59"), (3, "#a6d96a"), (4, "#2b83ba")]
    fig, axs = layout(17.2, 2, SITIO, bottom_extra=1.75)
    show(axs[0], classes(d[0], SEV), SITIO, 0, '(a) Severidad dNBR (V4)', 5000)
    im = axs[1].imshow(d[1], extent=SITIO, cmap='viridis', vmin=0.25, vmax=1, interpolation='nearest')
    show(axs[1], np.zeros((1, 1, 4)), SITIO, 1, '(b) Probabilidad de la clase ganadora', 5000)
    escala_norte(fig, axs[0], 5000, '5 km', axn=axs[1])
    b0 = axs[0].get_position(); b1 = axs[1].get_position()
    g = fig._geo
    h = [Patch(facecolor=c, edgecolor='#555555', lw=0.8, label=t) for t, c in
         zip(['1 severidad alta', '2 severidad baja', '3 no quemado', '4 agua'], [c for _, c in SEV])]
    fig.legend(handles=h, loc='upper center', bbox_to_anchor=((b0.x0 + b0.x1) / 2, (g['bottom_extra'] - 0.1) / g['H']),
               ncol=2, frameon=False, fontsize=10, handlelength=1.6, columnspacing=1.2, handletextpad=0.5)
    cb = barra(fig, im, 'probabilidad (la línea blanca marca 0,5)', b1.x0 + 0.02, b1.x1 - 0.02,
               ticks=[0.25, 0.5, 0.75, 1.0], fmt=lambda v, _: ('%.2f' % v).replace('.', ','))
    cb.ax.axvline(0.5, color='white', lw=2)
    guardar(fig, 'F25.png')

if 'F29' in todo:
    MAXH_CUR[0] = MAXH['F29']
    tiles = [PL + '20200816_S2A_MSIL2A_20200816T135121_R024_T21HTD_20200818T134453/',
             PL + '20200816_S2A_MSIL2A_20200816T135121_R024_T20HQJ_20200818T134428/']
    a = np.full((3, int((SITIO[3] - SITIO[2]) / 10), int((SITIO[1] - SITIO[0]) / 10)), np.nan, 'f4')
    for t in tiles:
        for i, b in enumerate(['B04', 'B03', 'B02']):
            x = warp(t + b + '.tif', (1,), SITIO, 10, nodata=0)[0]
            sel = np.isnan(a[i]) & ~np.isnan(x); a[i][sel] = x[sel]
    np.save(OUT + 'f29_rgb.npy', a)
    a = a / 10000.
    # estiramiento de la figura anterior (ajustado sobre ella): 0 a 0,18/0,19/0,17 de reflectancia, gamma 0,7/0,7/0,8
    hi = np.array([0.18, 0.19, 0.17])[:, None, None]; ga = np.array([0.7, 0.7, 0.8])[:, None, None]
    im = np.moveaxis(np.clip(np.nan_to_num(a) / hi, 0, 1) ** ga, 0, -1); im[np.isnan(a).any(0)] = WHITE
    fig, axs = layout(11.5, 1, SITIO, title_lines=0)
    show(axs[0], im, SITIO, 0, None, 5000)
    escala_norte(fig, axs[0], 5000, '5 km')
    guardar(fig, 'F29.png')

if 'F30' in todo:
    MAXH_CUR[0] = MAXH['F30']
    im = rgb8(RGB + 'A1_DELTA_QUEMAS_BIOMASS_P_20260323_RGB_8bit.tif')
    fig, axs = layout(17.6, 1, SITIO)
    show(axs[0], im, SITIO, 0, None, 5000)
    fig.text(0.5, axs[0].get_position().y1 + 0.2 / fig._geo['H'],
             'BIOMASS banda P, 23/03/2026 (R = HH, G = VH, B = HH/VH; promedio 5 × 5, estiramiento 2–98 %)',
             ha='center', va='bottom', fontsize=10.5)
    escala_norte(fig, axs[0], 5000, '5 km')
    guardar(fig, 'F30.png')
