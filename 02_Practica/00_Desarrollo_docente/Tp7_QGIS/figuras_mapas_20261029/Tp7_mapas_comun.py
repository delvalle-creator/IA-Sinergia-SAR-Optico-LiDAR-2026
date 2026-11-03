# Tp7: base comun para rehacer los mapas con escala y norte FUERA del mapa (29/10/2026).
import numpy as np, rasterio, geopandas as gpd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, Patch, FancyArrow
from matplotlib.lines import Line2D
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
plt.rcParams['font.family'] = 'Liberation Serif'; plt.rcParams['font.size'] = 10
plt.rcParams['axes.unicode_minus'] = True

U = '/mnt/user-data/uploads/02_Practica/'
TP = U + 'Tp7_Barrancas_deslizamientos/'
Q = TP + '02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/E1_DIAMANTE_BARRANCA_'
RGBD = TP + '02_Subsets_SNAP_QGIS/RGB_copol_cruzada_cociente/E1_DIAMANTE_BARRANCA_'
TAB = TP + '04_Tablas_de_trabajo/'
RAS = TP + '05_Resultados/02_Rasters/'
FIG = U + '00_COMUN/09_Herramientas/desarrollo_docente/Tp7/'
HY = U + '00_COMUN/08_Originales_crudos/HYP3/E1_DIAMANTE_BARRANCA/'
P0 = 'S1BB_20180918T092148_20180930T092148_VVP012_INT40_G_weF_D357'
P1 = 'S1BB_20181012T092149_20181024T092149_VVP012_INT40_G_weF_AF13'
XTC = '/mnt/user-data/uploads/DIAMANTE/COSMO/InSAR HI/subset_CSKS_SCS_HI_HH_RD_15-191018_Stack_ifg_dinsar_flt_TC.data/'
OUT = '/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp7/maps/'
CRS = 'EPSG:32721'
SITIO = (149978, 162280, 6438567, 6452312)
BAR = (154300, 157400, 6444600, 6448050)
CIC = (155170, 155570, 6446225, 6446625)
CM = 1 / 2.54

lad = gpd.read_file(TAB + 'E1_ladera_reparada.gpkg').to_crs(CRS)
lad = lad[lad.geometry.area > 1e5]   # el rectangulo de la ladera (las otras piezas son restos de 0 a 160 m2)
ref = gpd.read_file(TAB + 'E1_zona_referencia.gpkg').to_crs(CRS)
frm = gpd.read_file(TAB + 'E1_cicatriz_y_deposito.gpkg', layer='formas').to_crs(CRS)
gri = gpd.read_file('/mnt/user-data/uploads/DIAMANTE/GRIETAS/grietadte.shp').to_crs(CRS)
C_CIC, C_DEP = '#ffa500', '#1eb4f0'

def coma(fmt='%g'):
    return FuncFormatter(lambda v, _: (fmt % v).replace('-', '−').replace('.', ','))
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
milesd = FuncFormatter(lambda v, _: ('{:,.1f}'.format(v).replace(',', 'X').replace('.', ',').replace('X', '.')) if v % 1 else '{:,.0f}'.format(v).replace(',', '.'))

def warp(path, band, ext, res, rs=Resampling.bilinear, crs=CRS, src_crs=None, nod='auto', cero=False, gcps=False):
    x0, x1, y0, y1 = ext
    nx, ny = int(round((x1 - x0) / res)), int(round((y1 - y0) / res))
    T = from_origin(x0, y1, res, res)
    o = np.full((ny, nx), np.nan, 'f4')
    with rasterio.open(path) as s:
        a = s.read(band).astype('f4')
        nd = s.nodata if nod == 'auto' else nod
        if nd is not None and not np.isnan(nd): a[a == nd] = np.nan
        if cero: a[a <= 0] = np.nan
        kw = dict(src_transform=s.transform, src_crs=src_crs or s.crs)
        if gcps:
            g, gc = s.gcps; kw = dict(gcps=g, src_crs=gc)
        reproject(a, o, dst_transform=T, dst_crs=crs, resampling=rs, src_nodata=np.nan, dst_nodata=np.nan, **kw)
    return o

def st(a, lo=None, hi=None, p=(2, 98)):
    if lo is None: lo, hi = np.nanpercentile(a, p)
    return np.clip((a - lo) / (hi - lo), 0, 1)

def armar(n, ext, Wcm, tit_lin=1, cbar=False, leg_cm=0.0, L=1.45, R=1.05, g=0.35, extra_der=0.0, xlab=True, zc_extra=0.0):
    """Figura en cm: n paneles iguales; abajo, en orden: rotulos x, escala, barras de color, leyenda."""
    asp = (ext[3] - ext[2]) / (ext[1] - ext[0])
    pw = (Wcm - L - R - extra_der - (n - 1) * g) / n; ph = pw * asp
    T = 0.2 + 0.45 * tit_lin
    zx = 1.0 if xlab else 0.6
    zs = 0.85; zc = (1.45 + zc_extra) if cbar else 0.0
    H = T + ph + zx + zs + zc + leg_cm + 0.15
    fig = plt.figure(figsize=(Wcm * CM, H * CM))
    axs = []
    for k in range(n):
        x = L + k * (pw + g)
        axs.append(fig.add_axes([x / Wcm, (H - T - ph) / H, pw / Wcm, ph / H]))
    lay = dict(W=Wcm, H=H, pw=pw, ph=ph, L=L, g=g,
               y_esc=(H - T - ph - zx - zs + 0.18) / H,            # base de la barra de escala
               y_cb=(H - T - ph - zx - zs - 0.55) / H,              # base de la barra de color
               y_leg=(leg_cm + 0.15) / H)                           # techo de la zona de leyenda
    return fig, axs, lay

def marco(ax, ext, step, left=True, xlab='Este (m)', ylab='Norte (m)', fmt=miles):
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect('auto')
    ax.xaxis.set_major_locator(MultipleLocator(step)); ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.xaxis.set_major_formatter(fmt); ax.yaxis.set_major_formatter(fmt)
    ax.tick_params(labelsize=9, length=3)
    for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    ax.set_xlabel(xlab, fontsize=10, labelpad=2)
    if left: ax.set_ylabel(ylab, fontsize=10, labelpad=3)

    else: ax.set_yticklabels([]); ax.set_ylabel('')

def escala_norte(fig, lay, ax, axn, L, txt):
    """Escala FUERA, bajo el primer panel; flecha norte FUERA, en el esquinero superior derecho del panel derecho."""
    fig.canvas.draw()
    b = ax.get_position(); ext = ax.get_xlim(); frac = L / (ext[1] - ext[0]) * b.width
    y = lay['y_esc']; h = 0.16 / lay['H']
    sa = fig.add_axes([b.x0, y, frac, h]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
    sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8)); sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
    fig.text(b.x0, y + h + 0.06 / lay['H'], '0', ha='center', va='bottom', fontsize=10)
    fig.text(b.x0 + frac, y + h + 0.06 / lay['H'], txt, ha='center', va='bottom', fontsize=10)
    bn = axn.get_position(); xn = bn.x1 + 0.5 / lay['W']; yt = bn.y1
    fig.add_artist(FancyArrow(xn, yt - 1.55 / lay['H'], 0, 1.05 / lay['H'], width=0.07 / lay['W'], head_width=0.36 / lay['W'],
                              head_length=0.38 / lay['H'], length_includes_head=True, color='black', transform=fig.transFigure))
    fig.text(xn, yt - 0.45 / lay['H'], 'N', ha='center', va='bottom', fontsize=11, fontweight='bold')

def cbar(fig, lay, im, axs_bajo, label, ticks=None, fmt=None, frac=0.92, ext='neither'):
    b0 = axs_bajo[0].get_position(); b1 = axs_bajo[-1].get_position()
    w = (b1.x1 - b0.x0) * frac; x = b0.x0 + (b1.x1 - b0.x0 - w) / 2
    ca = fig.add_axes([x, lay['y_cb'], w, 0.32 / lay['H']])
    cb = fig.colorbar(im, cax=ca, orientation='horizontal', ticks=ticks, extend=ext)
    cb.ax.tick_params(labelsize=9.5, length=2.5)
    if fmt: cb.ax.xaxis.set_major_formatter(fmt)
    cb.set_label(label, fontsize=10, labelpad=2)
    return cb

def leyenda(fig, lay, handles, ncol, x=0.5, loc='upper center'):
    fig.legend(handles=handles, loc=loc, bbox_to_anchor=(x, lay['y_leg']), ncol=ncol, frameon=False, fontsize=10,
               handlelength=2.2, columnspacing=1.6, handletextpad=0.6, borderaxespad=0.1)

def lin(c, lab, lw=2.2): return Line2D([], [], color=c, lw=lw, label=lab)

def capas(ax, ladera=None, anillo=False, grieta=True, formas=False, lw=1.8, gw=(4.5, 2.6)):
    if anillo: ref.boundary.plot(ax=ax, color='cyan', lw=1.3, zorder=4)
    if ladera: lad.boundary.plot(ax=ax, color=ladera, lw=lw, zorder=5)
    if formas:
        frm[frm.tipo == 'cicatriz'].boundary.plot(ax=ax, color=C_CIC, lw=lw, zorder=6)
        frm[frm.tipo == 'deposito'].boundary.plot(ax=ax, color=C_DEP, lw=lw, zorder=6)
    if grieta:
        gri.plot(ax=ax, color='white', lw=gw[0], zorder=7, capstyle='round'); gri.plot(ax=ax, color='red', lw=gw[1], zorder=8, capstyle='round')

def guardar(fig, n):
    fig.savefig(OUT + n, dpi=300); plt.close(fig); print('ok', n)
