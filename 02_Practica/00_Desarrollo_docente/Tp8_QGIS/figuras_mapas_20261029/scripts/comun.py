import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, Patch, FancyArrow
from rasterio.windows import from_bounds
plt.rcParams['font.family'] = 'Liberation Serif'; plt.rcParams['font.size'] = 10
U = '/mnt/user-data/uploads/02_Practica/Tp8_Erosion_suelos/'
SUB = U + '02_Subsets_SNAP_QGIS/'; G = SUB + 'QGIS_GeoTIFF/'; R = U + '05_Resultados/02_Rasters/'
OUT = '/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp8/maps/'
SITIO = (259160, 271870, 6521080, 6535780)
DET = (264000, 267000, 6528000, 6531000)
FCOL = ['#f3efe6', '#fdd49e', '#fc8d59', '#b30000']
FLAB = ['Nunca', '1 a 2 meses (labranza)', '3 a 5 meses', '6 o más meses (persistente)']


def fmt_km(dec):
    def f(v, _):
        s = ('{:,.%df}' % dec).format(v / 1000.)
        return s.replace(',', 'X').replace('.', ',').replace('X', '.')
    return FuncFormatter(f)


def leer(f, ext, bandas=None):
    r = rasterio.open(f)
    w = from_bounds(ext[0], ext[2], ext[1], ext[3], r.transform)
    w = w.round_offsets().round_lengths()
    a = r.read(bandas, window=w, boundless=True, fill_value=0).astype('f4')
    return a


def frame(ax, ext, step, dec, left=True, bottom=True, ylab='Norte (km)', xlab='Este (km, UTM 21 S)', fs=10):
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.xaxis.set_major_locator(MultipleLocator(step)); ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.xaxis.set_major_formatter(fmt_km(dec)); ax.yaxis.set_major_formatter(fmt_km(dec))
    ax.tick_params(labelsize=fs)
    if bottom and xlab: ax.set_xlabel(xlab, fontsize=fs)
    if not bottom: ax.set_xticklabels([])
    if left and ylab: ax.set_ylabel(ylab, fontsize=fs)
    if not left: ax.set_yticklabels([])


def barra(fig, ax, L, txt, y, fs=10, x0=None, h=0.012, etiqueta=None):
    fig.canvas.draw()
    b = ax.get_position(); ext = ax.get_xlim(); frac = L / (ext[1] - ext[0]) * b.width
    x0 = b.x0 if x0 is None else x0
    sa = fig.add_axes([x0, y, frac, h]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
    sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8))
    sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
    fig.text(x0, y + h + 0.008, '0', ha='center', va='bottom', fontsize=fs)
    fig.text(x0 + frac, y + h + 0.008, txt, ha='center', va='bottom', fontsize=fs)
    if etiqueta:
        fig.text(x0 - 0.012, y + h / 2, etiqueta, ha='right', va='center', fontsize=fs)


def norte(fig, axn, dx=0.022, largo=0.085, fs=11, hw=0.014, hl=0.022):
    fig.canvas.draw()
    bn = axn.get_position(); xn = bn.x1 + dx; yt = bn.y1
    fig.add_artist(FancyArrow(xn, yt - largo, 0, largo - 0.025, width=0.0018, head_width=hw, head_length=hl,
                              length_includes_head=True, color='black', transform=fig.transFigure))
    fig.text(xn, yt - 0.02, 'N', ha='center', va='bottom', fontsize=fs, fontweight='bold')


def escala_norte(fig, ax, L, txt, y=0.035, axn=None, fs=10):
    """Barra de escala FUERA del mapa, bajo el primer panel; flecha norte FUERA, en el esquinero superior derecho."""
    barra(fig, ax, L, txt, y, fs)
    norte(fig, axn or ax)


def guardar(fig, n):
    fig.savefig(OUT + n, dpi=300); plt.close(fig); print(n)
