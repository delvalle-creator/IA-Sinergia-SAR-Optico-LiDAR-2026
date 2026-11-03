# Tp6: mapas con escala gráfica y norte FUERA del mapa (estilo Tp2: estilo_mapas_tp2.py)
import numpy as np, rasterio, matplotlib, sys, re, os
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, Patch, FancyArrow
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap, BoundaryNorm, LogNorm
from rasterio.warp import reproject, Resampling, transform_bounds
from rasterio.transform import from_origin
plt.rcParams['font.family'] = 'Liberation Serif'; plt.rcParams['font.size'] = 10
U = '/mnt/user-data/uploads/02_Practica/'
T6 = U + 'Tp6_Inundaciones/'; G = T6 + '02_Subsets_SNAP_QGIS/'; Q = G + 'QGIS_GeoTIFF/'; R = T6 + '05_Resultados/02_Rasters/'
OUT = '/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp6/maps/'
os.makedirs(OUT, exist_ok=True)
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
coma = FuncFormatter(lambda v, _: ('%g' % v).replace('.', ','))
CRS = 'EPSG:32721'
ref = rasterio.open(R + 'B_variante_C_20231104.tif')
T20 = ref.transform; SH = (ref.height, ref.width)
FULL = (ref.bounds.left, ref.bounds.right, ref.bounds.bottom, ref.bounds.top)
CON = (398000, 412000, 6519000, 6533000)          # Concordia 14 x 14 km
BAN = (396000, 404000, 6521000, 6529000)          # bañado 8 x 8 km
NOD = '#ffffff'

def leer(f, b=1):
    with rasterio.open(f) as s:
        a = s.read(b).astype('f4')
        if s.nodata is not None and np.isfinite(s.nodata): a[a == s.nodata] = np.nan
    return a

def a_grilla(f, b=1, T=T20, sh=SH, rs=Resampling.nearest):
    o = np.full(sh, np.nan, 'f4')
    with rasterio.open(f) as s:
        a = s.read(b).astype('f4')
        if s.nodata is not None and np.isfinite(s.nodata): a[a == s.nodata] = np.nan
        reproject(a, o, src_transform=s.transform, src_crs=s.crs, dst_transform=T, dst_crs=CRS, resampling=rs,
                  src_nodata=np.nan, dst_nodata=np.nan)
    return o

JRC = a_grilla(Q + 'B_CONCORDIA_JRC_GSW_ocurrencia.tif')
PERM = JRC >= 90

def frame(ax, ext, left=True, bottom=True, step=10000, lab=True):
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.xaxis.set_major_locator(MultipleLocator(step)); ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.tick_params(labelsize=9.5)
    for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    if not left: ax.set_yticklabels([])
    if not bottom: ax.set_xticklabels([])
    if lab and bottom: ax.set_xlabel('Este (m)', fontsize=10)
    if lab and left: ax.set_ylabel('Norte (m), EPSG:32721', fontsize=10)

def escala_norte(fig, ax, L, txt, y=0.035, axn=None, fs=10):
    """Barra de escala FUERA del mapa, bajo el primer panel; flecha norte FUERA, en el esquinero superior derecho."""
    fig.canvas.draw()
    b = ax.get_position(); ext = ax.get_xlim(); frac = L / (ext[1] - ext[0]) * b.width
    W, H = fig.get_size_inches()
    x0 = b.x0; h = 0.045 / H
    sa = fig.add_axes([x0, y, frac, h]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
    sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
    fig.text(x0, y + h + 0.03 / H, '0', ha='center', va='bottom', fontsize=fs); fig.text(x0 + frac, y + h + 0.03 / H, txt, ha='center', va='bottom', fontsize=fs)
    bn = (axn or ax).get_position(); xn = bn.x1 + 0.17 / W; yt = bn.y1
    fig.add_artist(FancyArrow(xn, yt - 0.62 / H, 0, 0.42 / H, width=0.012 / W, head_width=0.11 / W, head_length=0.16 / H,
                              length_includes_head=True, color='black', transform=fig.transFigure))
    fig.text(xn, yt - 0.16 / H, 'N', ha='center', va='bottom', fontsize=fs + 1, fontweight='bold')

def escala_recuadro(fig, ax, L, txt, y, fs=10):
    fig.canvas.draw(); b = ax.get_position(); ext = ax.get_xlim(); frac = L / (ext[1] - ext[0]) * b.width
    W, H = fig.get_size_inches(); h = 0.045 / H; x0 = b.x1 - frac
    sa = fig.add_axes([x0, y, frac, h]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
    sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
    fig.text(x0, y + h + 0.03 / H, '0', ha='center', va='bottom', fontsize=fs); fig.text(x0 + frac, y + h + 0.03 / H, txt, ha='center', va='bottom', fontsize=fs)
    fig.text(x0 - 0.1 / W, y + h / 2, 'Recuadro:', ha='right', va='center', fontsize=fs)

def guardar(fig, n):
    fig.savefig(OUT + n, dpi=300); plt.close(fig); print(n)

def cat(ax, arr, cols, ext=FULL):
    """arr con códigos 0..n-1 (nan = sin dato)"""
    cm = ListedColormap(cols); norm = BoundaryNorm(np.arange(len(cols) + 1) - 0.5, len(cols))
    ax.imshow(arr, cmap=cm, norm=norm, extent=FULL, interpolation='nearest')

def patch(c, l): return Patch(facecolor=c, edgecolor='0.4', lw=0.8, label=l)

AZ, GR, SA = '#2171b5', '#b0b0b0', '#eeeeee'
def agua_perm(a):
    m = np.where(a == 1, 0, 2).astype('f4'); m[PERM] = 1; return m

QUE = sys.argv[1:] or ['6', '12', '13', '14', '16', '17', '18', '19', '23', '25', '26', '27', '36']

# ---------------- Figura 12: agua C tres fechas
if '12' in QUE:
    f = G + 'B_agua_C_por_fecha_20m.tif'; d = list(rasterio.open(f).descriptions)
    fig, axs = plt.subplots(1, 3, figsize=(25.6 * CM, 11.6 * CM)); fig.subplots_adjust(left=0.065, right=0.955, top=0.93, bottom=0.25, wspace=0.07)
    for k, (ax, b, t) in enumerate(zip(axs, ['agua_20231104', 'agua_20231128', 'agua_20240514'], ['(a) 04/11/2023', '(b) 28/11/2023', '(c) 14/05/2024'])):
        a = leer(f, d.index(b) + 1); ha = np.nansum(a == 1) * 0.04
        cat(ax, agua_perm(a), [AZ, GR, SA]); frame(ax, FULL, left=k == 0)
        ax.set_title('%s: %s ha' % (t, '{:,.0f}'.format(ha).replace(',', '.')), fontsize=10.5)
    fig.legend(handles=[patch(AZ, 'agua de inundación'), patch(GR, 'agua permanente (JRC ≥ 90 %, excluida)'), patch(SA, 'sin agua de inundación')],
               loc='lower center', bbox_to_anchor=(0.62, 0.0), ncol=3, frameon=False, fontsize=10)
    escala_norte(fig, axs[0], 10000, '10 km', y=0.04, axn=axs[2])
    guardar(fig, 'F12.png')

# ---------------- Figura 13: extensión, duración, referencia seca
if '13' in QUE:
    f = R + 'B_extension_y_duracion_C_20m.tif'
    ext = leer(f, 1); dur = leer(f, 4); seca = leer(f, 3)
    fig, axs = plt.subplots(1, 3, figsize=(25.7 * CM, 13.0 * CM)); fig.subplots_adjust(left=0.065, right=0.955, top=0.935, bottom=0.30, wspace=0.07)
    cat(axs[0], agua_perm(ext), [AZ, GR, SA])
    dd = dur.copy(); dd[PERM] = np.nan
    im = axs[1].imshow(dd, cmap='Blues', vmin=0, vmax=90, extent=FULL, interpolation='nearest')
    m = np.where(seca == 1, 0, 2).astype('f4'); m[PERM] = 1; cat(axs[2], m, ['#e6550d', GR, SA])
    for k, (ax, t) in enumerate(zip(axs, ['(a) extensión máxima', '(b) duración (días)', '(c) agua el 22/01/2026 (excluida)'])):
        frame(ax, FULL, left=k == 0); ax.set_title(t, fontsize=10.5)
    fig.canvas.draw()
    b0, b1, b2 = [a.get_position() for a in axs]
    fig.legend(handles=[patch(AZ, 'agua alguna vez'), patch(GR, 'agua permanente')], loc='upper center', bbox_to_anchor=((b0.x0 + b0.x1) / 2 + 0.03, 0.17), ncol=1, frameon=False, fontsize=10)
    fig.legend(handles=[patch('#e6550d', 'agua no permanente el 22/01/2026'), patch(GR, 'agua permanente')], loc='upper center', bbox_to_anchor=((b2.x0 + b2.x1) / 2, 0.17), ncol=1, frameon=False, fontsize=10)
    cax = fig.add_axes([b1.x0 + 0.02, 0.135, b1.width - 0.04, 0.025])
    cb = fig.colorbar(im, cax=cax, orientation='horizontal'); cb.ax.tick_params(labelsize=9.5)
    cb.set_label('duración mínima, días (fechas sin dato = sin agua)', fontsize=10)
    escala_norte(fig, axs[0], 10000, '10 km', y=0.035, axn=axs[2])
    guardar(fig, 'F13.png')

# ---------------- Figura 14: duración mínima, Concordia
if '14' in QUE:
    dur = leer(R + 'B_extension_y_duracion_C_20m.tif', 4); dur[PERM] = np.nan
    fig = plt.figure(figsize=(13.6 * CM, 15.0 * CM))
    ax = fig.add_axes([0.15, 0.31, 0.64, 0.61])
    im = ax.imshow(dur, cmap='Blues', vmin=0, vmax=90, extent=FULL, interpolation='nearest')
    frame(ax, CON, step=4000); ax.set_title('Duración mínima del agua de inundación, Concordia', fontsize=10.5)
    fig.canvas.draw(); b = ax.get_position()
    cax = fig.add_axes([b.x0, 0.175, b.width, 0.022]); cb = fig.colorbar(im, cax=cax, orientation='horizontal')
    cb.set_label('días (fechas sin dato = sin agua);\nen blanco el cauce (agua permanente, excluida)', fontsize=10); cb.ax.tick_params(labelsize=9.5)
    escala_norte(fig, ax, 2000, '2 km', y=0.02)
    guardar(fig, 'F14.png')

# ---------------- Figura 16: agua por sensor
if '16' in QUE:
    f = R + 'B_agua_por_sensor_20231104_20m.tif'
    fig, axs = plt.subplots(1, 2, figsize=(14.9 * CM, 10.6 * CM)); fig.subplots_adjust(left=0.09, right=0.92, top=0.93, bottom=0.28, wspace=0.07)
    for k, (ax, b, t) in enumerate(zip(axs, [1, 2], ['(a) C: VV < −15 dB', '(b) óptico: MNDWI > 0'])):
        a = leer(f, b); m = agua_perm(a); m[np.isnan(a) & ~PERM] = np.nan
        cat(ax, m, [AZ, GR, SA]); frame(ax, FULL, left=k == 0); ax.set_title(t, fontsize=10.5)
    fig.legend(handles=[patch(AZ, 'agua'), patch(GR, 'agua permanente (excluida)'), patch(SA, 'sin agua')], loc='lower center', bbox_to_anchor=(0.6, 0.0), ncol=3, frameon=False, fontsize=10, columnspacing=1.0, handlelength=1.6)
    escala_norte(fig, axs[0], 10000, '10 km', y=0.075, axn=axs[1])
    guardar(fig, 'F16.png')

# ---------------- Figura 17: coincidencias
if '17' in QUE:
    f = R + 'B_agua_por_sensor_20m.tif'
    c = leer(f, 1); o = leer(f, 2)
    m = np.full(SH, 4, 'f4')
    m[(c == 1) & (o == 1)] = 0; m[(c == 1) & (o != 1)] = 1; m[(c != 1) & (o == 1)] = 2; m[PERM] = 3
    cols = ['#2166ac', '#e6550d', '#4daf2a', GR, '#f2f2f2']
    fig = plt.figure(figsize=(15.3 * CM, 11.4 * CM))
    a1 = fig.add_axes([0.085, 0.33, 0.38, 0.6]); a2 = fig.add_axes([0.525, 0.33, 0.38, 0.6])
    cat(a1, m, cols); cat(a2, m, cols)
    a1.set_aspect('equal'); a2.set_aspect('equal')
    frame(a1, FULL); frame(a2, CON, step=4000, lab=False); a2.set_xlabel('Este (m)', fontsize=10)
    a1.add_patch(Rectangle((CON[0], CON[2]), CON[1] - CON[0], CON[3] - CON[2], fill=False, ec='k', lw=1.0, ls='--'))
    a1.set_title('(a) sitio', fontsize=10.5); a2.set_title('(b) Concordia (recuadro)', fontsize=10.5)
    fig.legend(handles=[patch(cols[0], 'agua para C y para el óptico'), patch(cols[1], 'sólo C'), patch(cols[2], 'sólo el óptico'), patch(GR, 'agua permanente (excluida)')],
               loc='lower center', bbox_to_anchor=(0.6, 0.0), ncol=2, frameon=False, fontsize=10, columnspacing=1.0, handlelength=1.6)
    escala_norte(fig, a1, 10000, '10 km', y=0.155, axn=a2)
    escala_recuadro(fig, a2, 2000, '2 km', y=0.155)
    guardar(fig, 'F17.png')

# ---------------- Figura 18: SAOCOM
if '18' in QUE:
    S = U + 'Tp1_Convergencia/02_Subsets_SNAP_QGIS/SAOCOM_gamma0/QGIS_GeoTIFF/B_CONCORDIA_SAOCOM_L_%s_QP_gamma0_Gamma0_HH.tif'
    h1 = a_grilla(S % '20231010', rs=Resampling.average); h2 = a_grilla(S % '20231111', rs=Resampling.average)
    h1[h1 <= 0] = np.nan; h2[h2 <= 0] = np.nan
    d1 = 10 * np.log10(h1); d2 = 10 * np.log10(h2); dd = d2 - d1
    print('mediana dHH sitio %.2f; sin perm %.2f' % (np.nanmedian(dd), np.nanmedian(dd[~PERM])))
    f = R + 'B_agua_por_sensor_con_L_SAOCOM_relativo_clase_20m.tif'
    c = leer(f, 1); o = leer(f, 2); l = leer(f, 3)
    fig, axs = plt.subplots(1, 2, figsize=(20.4 * CM, 14.6 * CM)); fig.subplots_adjust(left=0.07, right=0.94, top=0.935, bottom=0.35, wspace=0.07)
    im = axs[0].imshow(dd, cmap='RdBu_r', vmin=-6, vmax=6, extent=FULL, interpolation='nearest')
    axs[1].imshow(d2, cmap='gray', vmin=-22, vmax=0, extent=FULL, interpolation='nearest')
    ov = np.full(SH + (4,), 0, 'f4')
    ov[(c == 1) | (o == 1)] = (0.13, 0.47, 0.95, 1)
    ov[l == 1] = (0.89, 0.0, 0.0, 1)
    axs[1].imshow(ov, extent=FULL, interpolation='nearest')
    axs[0].set_title('(a) cambio de HH en banda L (mediana del sitio +3,1 dB)', fontsize=10.5)
    axs[1].set_title('(b) regla relativa en leñosas y agua en C u óptico', fontsize=10.5)
    for k, ax in enumerate(axs): frame(ax, FULL, left=k == 0)
    fig.canvas.draw(); b0 = axs[0].get_position(); b1 = axs[1].get_position()
    cax = fig.add_axes([b0.x0 + 0.02, 0.215, b0.width - 0.04, 0.025]); cb = fig.colorbar(im, cax=cax, orientation='horizontal')
    cb.set_label(r'ΔHH = γ$^0$ 11/11/2023 − γ$^0$ 10/10/2023 (dB)', fontsize=10); cb.ax.tick_params(labelsize=9.5)
    fig.legend(handles=[Patch(color=(0.13, 0.47, 0.95), label='agua de inundación en C o en el óptico, 04/11/2023'),
                        Patch(color=(0.89, 0, 0), label='ΔHH − 2,59 dB ≥ 3 dB en monte o plantación\n(umbral efectivo 5,6 dB)'),
                        Patch(color='0.55', label='fondo: SAOCOM HH 11/11/2023 (−22 a 0 dB)')],
               loc='upper left', bbox_to_anchor=(b1.x0 - 0.01, 0.26), ncol=1, frameon=False, fontsize=10)
    escala_norte(fig, axs[0], 10000, '10 km', y=0.035, axn=axs[1])
    guardar(fig, 'F18.png')

# ---------------- Figura 19: variantes
if '19' in QUE:
    fig, axs = plt.subplots(1, 3, figsize=(22.0 * CM, 10.6 * CM)); fig.subplots_adjust(left=0.075, right=0.95, top=0.92, bottom=0.27, wspace=0.07)
    for k, (ax, n, t) in enumerate(zip(axs, ['optico', 'C', 'multisensor'], ['(a) óptico solo', '(b) SAR solo (C)', '(c) multisensor (unión)'])):
        a = leer(R + 'B_variante_%s_20231104.tif' % n, 1); ha = np.nansum(a == 1) * 0.04
        m = agua_perm(a); m[np.isnan(a) & ~PERM] = np.nan
        cat(ax, m, [AZ, GR, SA]); frame(ax, FULL, left=k == 0)
        ax.set_title('%s: %s ha' % (t, '{:,.0f}'.format(ha).replace(',', '.')), fontsize=10.5)
    fig.legend(handles=[patch(AZ, 'agua de inundación'), patch(GR, 'agua permanente (excluida)'), patch(SA, 'no')], loc='lower center', bbox_to_anchor=(0.62, 0.0), ncol=3, frameon=False, fontsize=10)
    escala_norte(fig, axs[0], 10000, '10 km', y=0.05, axn=axs[2])
    guardar(fig, 'F19.png')

# ---------------- Figura 26: dos crecidas
if '26' in QUE:
    f = G + 'B_agua_C_por_fecha_20m.tif'; d = list(rasterio.open(f).descriptions)
    a = leer(f, d.index('agua_20231104') + 1) == 1; b = leer(f, d.index('agua_20240514') + 1) == 1
    m = np.full(SH, 4, 'f4'); m[a & b] = 0; m[a & ~b] = 1; m[~a & b] = 2; m[PERM] = 3
    ha = lambda x: '{:,.0f}'.format(x.sum() * 0.04).replace(',', '.')
    cols = ['#16257f', '#e6a817', '#2b8cc4', GR, SA]
    fig = plt.figure(figsize=(11.0 * CM, 15.0 * CM))
    ax = fig.add_axes([0.16, 0.385, 0.70, 0.565])
    cat(ax, m, cols); frame(ax, FULL); ax.set_title('04/11/2023 y 14/05/2024', fontsize=10.5)
    fig.legend(handles=[patch(cols[0], 'agua de inundación en las dos crecidas: %s ha' % ha(a & b)), patch(cols[1], 'sólo el 04/11/2023: %s ha' % ha(a & ~b)),
                        patch(cols[2], 'sólo el 14/05/2024: %s ha' % ha(~a & b)), patch(GR, 'agua permanente (JRC ≥ 90 %, excluida)'), patch(SA, 'sin agua de inundación')],
               loc='lower left', bbox_to_anchor=(0.03, 0.0), ncol=1, frameon=False, fontsize=10)
    escala_norte(fig, ax, 10000, '10 km', y=0.24)
    guardar(fig, 'F26.png')

# ---------------- Figura 6: MapBiomas 2023
if '6' in QUE:
    from pyproj import Transformer
    f = Q + 'B_CONCORDIA_MapBiomas_cobertura_1985_2025.tif'
    raw = rasterio.open(f).read(2023 - 1985 + 1)
    pal = {}
    for v, lab, col in re.findall(r'value="(\d+)" label="([^"]+)" color="(#[0-9A-Fa-f]{6})"', open(Q + 'B_CONCORDIA_MapBiomas_cobertura_1985_2025.qml', encoding='utf-8').read()):
        for a_, b_ in (("Herbaceas", "Herbáceas"), ("herbacea", "herbácea"), ("Rios", "Ríos"), ("oceano", "océano"), ("Areas", "Áreas"), ("areas", "áreas"), ("Vegetacion", "Vegetación")):
            lab = lab.replace(a_, b_)
        pal[int(v)] = (lab, col)
    v, c = np.unique(raw[raw > 0], return_counts=True); pc = 100 * c / c.sum()
    orden = [int(x) for x, p in sorted(zip(v, pc), key=lambda t: -t[1])]
    pcs = dict(zip([int(x) for x in v], pc))
    print({k: round(pcs[k], 1) for k in orden})
    tr = Transformer.from_crs(4326, 32721, always_xy=True)
    xs, ys = tr.transform([-58.25, -57.90, -58.25, -57.90], [-31.50, -31.50, -31.10, -31.10])
    E6 = (min(xs), max(xs), min(ys), max(ys))
    res = 30; T = from_origin(E6[0], E6[3], res, res); sh = (int((E6[3] - E6[2]) / res), int((E6[1] - E6[0]) / res))
    o = np.zeros(sh, 'u1')
    with rasterio.open(f) as s:
        reproject(raw, o, src_transform=s.transform, src_crs=s.crs, dst_transform=T, dst_crs=CRS, resampling=Resampling.nearest, src_nodata=0, dst_nodata=0)
    rgb = np.ones(sh + (3,))
    for k in orden:
        h = pal[k][1].lstrip('#'); rgb[o == k] = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    fig = plt.figure(figsize=(14.1 * CM, 15.0 * CM))
    ax = fig.add_axes([0.2, 0.425, 0.62, 0.525])
    ax.imshow(rgb, extent=(E6[0], E6[0] + sh[1] * res, E6[3] - sh[0] * res, E6[3]), interpolation='nearest')
    frame(ax, E6); ax.set_title('MapBiomas Argentina, cobertura 2023', fontsize=10.5)
    hs = [Patch(facecolor=pal[k][1], edgecolor='0.4', lw=0.6, label='%s (%s %%)' % (pal[k][0], ('%.1f' % pcs[k]).replace('.', ','))) for k in orden if pcs[k] >= 0.1]
    fig.legend(handles=hs, title='Clase (porcentaje de la parte argentina del sitio)', loc='upper center', bbox_to_anchor=(0.5, 0.275), ncol=2, frameon=False, fontsize=9.5, title_fontsize=10, columnspacing=1.0, handlelength=1.5)
    escala_norte(fig, ax, 10000, '10 km', y=0.31)
    guardar(fig, 'F06.png')

# ---------------- Figura 23: profundidad en el bañado
if '23' in QUE:
    s = rasterio.open(Q + 'B_CONCORDIA_S2_20231104.tif')
    w = rasterio.windows.from_bounds(BAN[0], BAN[2], BAN[1], BAN[3], s.transform)
    rgb = np.stack([s.read(b, window=w).astype('f4') for b in (3, 2, 1)], -1)
    lo = np.percentile(rgb[rgb > 0], 1); hi = np.percentile(rgb[rgb > 0], 99.5)
    rgb = np.clip((rgb - lo) / (hi - lo), 0, 1) ** 0.85
    ms = leer(R + 'B_variante_multisensor_20231104.tif', 1) == 1
    fig, axs = plt.subplots(1, 2, figsize=(19.2 * CM, 12.4 * CM)); fig.subplots_adjust(left=0.08, right=0.93, top=0.93, bottom=0.33, wspace=0.07)
    for k, (ax, n, t) in enumerate(zip(axs, ['B_profundidad_multisensor_20231104_20m.tif', 'B_profundidad_multisensor_20231104_fabdem_20m.tif'], ['(a) con el Copernicus DEM (superficie)', '(b) con FABDEM (terreno desnudo)'])):
        ax.imshow(rgb, extent=BAN, interpolation='nearest')
        p = leer(R + n, 1); sr = leer(R + n, 3)
        pp = np.where(ms & (p > 0), p, np.nan)
        im = ax.imshow(pp, cmap='Blues', vmin=0, vmax=3, extent=FULL, interpolation='nearest')
        ng = np.zeros(SH + (4,), 'f4'); ng[ms & np.isfinite(sr) & (sr <= 0)] = (1.0, 0.5, 0.0, 1)
        ax.imshow(ng, extent=FULL, interpolation='nearest')
        frame(ax, BAN, left=k == 0, step=2000); ax.set_title(t, fontsize=10.5)
        ax.set_xticks([397000, 399000, 401000, 403000]); ax.xaxis.set_major_formatter(miles)
    fig.canvas.draw(); b0 = axs[0].get_position(); b1 = axs[1].get_position()
    cax = fig.add_axes([b0.x0 + 0.03, 0.2, b0.width - 0.06, 0.028]); cb = fig.colorbar(im, cax=cax, orientation='horizontal')
    cb.ax.xaxis.set_major_formatter(coma); cb.set_label('profundidad plausible (m)', fontsize=10); cb.ax.tick_params(labelsize=9.5)
    fig.legend(handles=[Patch(color=(1, 0.5, 0), label='profundidad negativa o nula\n(cota del MDE ≥ cota del borde)')], loc='upper left', bbox_to_anchor=(b1.x0, 0.25), frameon=False, fontsize=10)
    escala_norte(fig, axs[0], 2000, '2 km', y=0.04, axn=axs[1])
    guardar(fig, 'F23.png')

# ---------------- Figura 25: MDE y ATL08
if '25' in QUE:
    import pandas as pd
    from pyproj import Transformer
    dem = a_grilla(Q + 'B_CONCORDIA_CopernicusDEM30.tif', rs=Resampling.bilinear)
    a = pd.read_csv(G + 'LiDAR_B_CONCORDIA/B_CONCORDIA_ATL08.csv')
    v = a[(a.terreno_valido.astype(str) == 'True') & (a.mascara_agua == 0)]
    print('ATL08 validos fuera de agua', len(v), 'uno de diez', len(v.iloc[::10]))
    v10 = v.iloc[::10]
    x, y = Transformer.from_crs(4326, 32721, always_xy=True).transform(v10.lon.values, v10.lat.values)
    fig, axs = plt.subplots(1, 2, figsize=(16.6 * CM, 12.0 * CM)); fig.subplots_adjust(left=0.09, right=0.92, top=0.93, bottom=0.33, wspace=0.07)
    for k, ax in enumerate(axs):
        im = ax.imshow(dem, cmap='RdYlGn_r', vmin=5, vmax=70, extent=FULL, interpolation='nearest'); frame(ax, FULL, left=k == 0)
    axs[1].scatter(x, y, s=0.6, c='#6a00a8', lw=0, alpha=0.8)
    axs[0].set_title('(a) Copernicus DEM GLO-30', fontsize=10.5); axs[1].set_title('(b) segmentos ATL08 (uno de cada diez)', fontsize=10.5)
    fig.canvas.draw(); b0 = axs[0].get_position(); b1 = axs[1].get_position()
    cax = fig.add_axes([b0.x0 + 0.02, 0.19, b0.width - 0.04, 0.028]); cb = fig.colorbar(im, cax=cax, orientation='horizontal')
    cb.set_label('cota, m (EGM2008)', fontsize=10); cb.ax.tick_params(labelsize=9.5)
    fig.legend(handles=[Line2D([], [], ls='', marker='o', ms=4, color='#6a00a8', label='segmento ATL08 de 100 m con terreno\nválido (%s de %s)' % ('{:,}'.format(len(v10)).replace(',', '.'), '{:,}'.format(len(v)).replace(',', '.')))],
               loc='upper left', bbox_to_anchor=(b1.x0 - 0.02, 0.25), frameon=False, fontsize=10, handletextpad=0.3)
    escala_norte(fig, axs[0], 10000, '10 km', y=0.04, axn=axs[1])
    guardar(fig, 'F25.png')

# ---------------- Figura 27: SNAP vs RTC
if '27' in QUE:
    T10 = from_origin(FULL[0], FULL[3], 10, 10); sh10 = (4471, 3850)
    fa = G + 'S1_procesado_desde_crudo/RGB_copol_cruzada_cociente/B_CONCORDIA_S1_20231104_gamma0_desde_crudo_RGB_dB.tif'
    fb = G + 'RGB_copol_cruzada_cociente/B_CONCORDIA_S1_C_20231104_RGB_dB.tif'
    def rgbdb(f):
        bs = [a_grilla(f, b, T=T10, sh=sh10) for b in (1, 2, 3)]
        out = np.stack([np.clip((bs[0] + 22) / 24, 0, 1), np.clip((bs[1] + 28) / 22, 0, 1), np.clip(bs[2] / 14, 0, 1)], -1)
        out[~np.isfinite(bs[0])] = 1
        return out, bs[0]
    A, va = rgbdb(fa); B, vb = rgbdb(fb)
    E27 = (FULL[0], FULL[1], FULL[3] - 4471 * 10, FULL[3])
    fig = plt.figure(figsize=(25.6 * CM, 11.0 * CM))
    a1 = fig.add_axes([0.06, 0.27, 0.27, 0.65]); a2 = fig.add_axes([0.345, 0.27, 0.27, 0.65]); a3 = fig.add_axes([0.725, 0.27, 0.19, 0.6])
    for k, (ax, im_, t) in enumerate([(a1, A, '(a) γ$^0$ procesado en SNAP desde el GRDH'), (a2, B, '(b) γ$^0$ RTC del Planetary Computer')]):
        ax.imshow(im_, extent=E27, interpolation='nearest'); frame(ax, FULL, left=k == 0); ax.set_title(t, fontsize=10.5)
    ok = np.isfinite(va) & np.isfinite(vb); xa = vb[::2, ::2][ok[::2, ::2]]; ya = va[::2, ::2][ok[::2, ::2]]
    h = a3.hist2d(xa, ya, bins=200, range=[[-30, 5], [-30, 5]], cmap='magma', norm=LogNorm())
    a3.plot([-30, 5], [-30, 5], color='c', lw=1); a3.axvline(-15, color='w', ls='--', lw=0.8, ymax=15 / 35); a3.axhline(-15, color='w', ls='--', lw=0.8, xmax=15 / 35)
    a3.set_xlabel('RTC, γ$^0$ VV (dB)', fontsize=10); a3.set_ylabel('SNAP desde el GRDH, γ$^0$ VV (dB)', fontsize=10); a3.set_title('(c) VV píxel a píxel (10 m)', fontsize=10.5)
    a3.tick_params(labelsize=9.5); a3.set_aspect('equal')
    fig.canvas.draw(); b3 = a3.get_position()
    cax = fig.add_axes([b3.x1 + 0.01, b3.y0, 0.012, b3.height]); cb = fig.colorbar(h[3], cax=cax)
    cb.set_label('píxeles (uno de cada cuatro)', fontsize=10); cb.ax.tick_params(labelsize=9.5)
    cb.ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.')))
    fig.text(0.2, 0.045, 'RGB: R = VV, G = VH, B = VV/VH, en dB (rangos: VV −22 a 2; VH −28 a −6; VV/VH 0 a 14)', ha='left', va='bottom', fontsize=10)
    escala_norte(fig, a1, 10000, '10 km', y=0.04, axn=a2)
    guardar(fig, 'F27.png')

# ---------------- Figura 36: embeddings
if '36' in QUE:
    KNN = sys.argv[-1] if sys.argv[-1].endswith('.npy') else 'knn_b.npy'
    s = rasterio.open(Q + 'B_CONCORDIA_AlphaEarth_embeddings_2023_10m_CP1_CP2_CP3_RGB_8bit.tif')
    Hh, Ww = s.height // 4, s.width // 4
    cp = np.dstack([x / 255. for x in s.read(out_shape=(3, Hh, Ww), resampling=Resampling.nearest).astype('f4')])
    E4 = (FULL[0], FULL[0] + Ww * 40, FULL[3] - 10 - Hh * 40 + 10, FULL[3] - 10)
    E4 = (s.bounds.left, s.bounds.left + Ww * 40, s.bounds.top - Hh * 40, s.bounds.top)
    kb = np.load(OUT + '../' + KNN) if not os.path.isabs(KNN) else np.load(KNN)
    c1 = '#2532e4'
    fig, axs = plt.subplots(1, 3, figsize=(22.0 * CM, 12.0 * CM)); fig.subplots_adjust(left=0.075, right=0.95, top=0.885, bottom=0.33, wspace=0.07)
    axs[0].imshow(cp, extent=E4, interpolation='nearest')
    axs[1].imshow(kb, cmap=ListedColormap(['#f0f0f0', c1]), vmin=0, vmax=1, extent=E4, interpolation='nearest')
    a = leer(R + 'B_variante_C_20231104.tif', 1); m = agua_perm(a)
    cat(axs[2], m, [c1, GR, '#f0f0f0'])
    for k, (ax, t) in enumerate(zip(axs, ['(a) embeddings AlphaEarth 2023,\nCP1-CP2-CP3', '(b) agua según kNN\ncon los embeddings', '(c) agua de inundación en\nbanda C, 04/11/2023'])):
        frame(ax, FULL, left=k == 0); ax.set_title(t, fontsize=10.5)
    fig.canvas.draw(); bs = [a_.get_position() for a_ in axs]
    fig.text((bs[0].x0 + bs[0].x1) / 2, 0.2, 'colores sin significado fijo', ha='center', va='top', fontsize=10)
    fig.legend(handles=[patch(c1, 'agua (kNN)'), patch('#f0f0f0', 'tierra (kNN)')], loc='upper center', bbox_to_anchor=((bs[1].x0 + bs[1].x1) / 2, 0.215), frameon=False, fontsize=10)
    fig.legend(handles=[patch(c1, 'agua de inundación (variante C)'), patch(GR, 'agua permanente (JRC ≥ 90 %)'), patch('#f0f0f0', 'sin agua de inundación')], loc='upper center', bbox_to_anchor=((bs[2].x0 + bs[2].x1) / 2 - 0.02, 0.215), frameon=False, fontsize=10)
    escala_norte(fig, axs[0], 10000, '10 km', y=0.035, axn=axs[2])
    guardar(fig, 'F36.png')
