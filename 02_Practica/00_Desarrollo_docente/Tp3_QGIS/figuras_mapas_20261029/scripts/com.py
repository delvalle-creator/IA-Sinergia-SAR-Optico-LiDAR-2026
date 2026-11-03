"""Comun a las figuras del Tp3 rehechas el 29/10/2026: escala y norte FUERA del mapa (estilo de estilo_mapas_tp2.py)."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow
plt.rcParams.update({"font.family": ["Liberation Serif"], "font.size": 11, "axes.titlesize": 11,
                     "axes.labelsize": 11, "legend.fontsize": 10.5, "xtick.labelsize": 10.5, "ytick.labelsize": 10.5})
U = '/mnt/user-data/uploads/02_Practica/'
W = U + 'Tp3_Armonizacion/'
SUB = W + '02_Subsets_SNAP_QGIS/'
Q = SUB + 'QGIS_GeoTIFF/'
OUT = '/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp3/maps/'
SITIO = [286700, 305720, 6252080, 6274680]


def num(v, dec=0):
    if abs(v) < 0.5 * 10 ** (-dec): v = 0.0
    s = ("{:,.%df}" % dec).format(v)
    return s.replace(",", "X").replace(".", ",").replace("X", ".").replace("-", "−")


def fmt(dec=0):
    return FuncFormatter(lambda v, p: num(v, dec))


def ejes_utm(ax, paso_km=5, ylab=True, xlab=True):
    ax.xaxis.set_major_locator(MultipleLocator(paso_km * 1000)); ax.yaxis.set_major_locator(MultipleLocator(paso_km * 1000))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: num(v / 1000, 0)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: num(v / 1000, 0)))
    ax.set_xlabel("Este UTM 21 S (km)" if xlab else ""); ax.set_ylabel("Norte UTM 21 S (km)" if ylab else "")


def cubo():
    import rasterio
    with rasterio.open(SUB + 'A2_IBICUY_cubo_20m.tif') as s:
        cap = {}
        for i, d in enumerate(s.descriptions):
            a = s.read(i + 1).astype('float32'); a[a == s.nodata] = np.nan; cap[d] = a
        T = s.transform
    return cap, T


def st(a, p=(2, 98)):
    lo, hi = np.nanpercentile(a, p); return np.clip((a - lo) / (hi - lo), 0, 1)


def db(a): return 10 * np.log10(np.where(a > 0, a, np.nan))


def escala_norte(fig, ax, L, txt, axn=None, fs=10.5, gap_in=0.18):
    """Barra de escala FUERA del mapa, debajo del primer panel (y de su rotulo del eje X);
    flecha norte FUERA, en el esquinero superior derecho, a la derecha del borde superior del panel de mas a la derecha.
    Devuelve la coordenada y (fraccion de figura) del borde inferior de la escala, para ubicar debajo otras cosas."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    Wi, Hi = fig.get_size_inches()
    b = ax.get_position(); xl = ax.get_xlim(); frac = L / (xl[1] - xl[0]) * b.width
    tb = ax.get_tightbbox(r).transformed(fig.transFigure.inverted())
    h = 0.075 / Hi                       # alto de la barra: 0,075 pulgadas
    ytxt = tb.y0 - gap_in / Hi           # tope de los rotulos de la escala
    y = ytxt - (fs * 1.25 / 72) / Hi - h
    x0 = b.x0
    sa = fig.add_axes([x0, y, frac, h]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
    sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8, clip_on=False))
    sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8, clip_on=False))
    fig.text(x0, y + h + 0.03 / Hi, '0', ha='center', va='bottom', fontsize=fs)
    fig.text(x0 + frac, y + h + 0.03 / Hi, txt, ha='center', va='bottom', fontsize=fs)
    bn = (axn or ax).get_position(); xn = bn.x1 + 0.17 / Wi; yt = bn.y1
    la = 0.42 / Hi
    fig.add_artist(FancyArrow(xn, yt - la - 0.20 / Hi, 0, la, width=0.018 / Wi, head_width=0.13 / Wi, head_length=0.17 / Hi,
                              length_includes_head=True, color='black', transform=fig.transFigure))
    fig.text(xn, yt - 0.02 / Hi, 'N', ha='center', va='top', fontsize=fs + 1, fontweight='bold')
    return y


def guardar(fig, n, dpi=250):
    fig.savefig(OUT + n, dpi=dpi, bbox_inches='tight', pad_inches=0.06); plt.close(fig); print('guardada', n)
