"""Figuras 24, 28, 31 y 32 del Desarrollo del Tp3 (antes compuestas con el disenador de QGIS, qgis_mapas.py).
Se redibujan con los mismos datos y la misma simbologia del proyecto des_qgis_Tp3_proyecto.py (huellas por clase
de rh98 en violetas, cruces negras, ATL08 celeste; CCI con la rampa Greens 0-100; MapBiomas con el .qml oficial;
FH con la rampa de 0 a 30 m), con escala, norte y leyenda FUERA del mapa."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp3/sc')
from com import *
import pandas as pd, rasterio, re
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, BoundaryNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

RES = 20; X0, X1, Y0, Y1 = SITIO
NX, NY = int((X1 - X0) / RES), int((Y1 - Y0) / RES); TU = from_origin(X0, Y1, RES, RES)


def a_utm(f, band, nodata=None):
    with rasterio.open(f) as s:
        a = s.read(band).astype('float32')
        if nodata is not None: a[a == nodata] = np.nan
        o = np.full((NY, NX), np.nan, 'float32')
        reproject(a, o, src_transform=s.transform, src_crs=s.crs, dst_transform=TU, dst_crs='EPSG:32721',
                  resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
    return o


t = pd.read_csv(W + '04_Tablas_de_trabajo/A2_IBICUY_huellas_con_cubo.csv', encoding='utf-8-sig', low_memory=False,
                usecols=['producto', 'x', 'y', 'rh98', 'plausible'])
gd = t[t.producto == 'gedi_l2a']; at = t[t.producto == 'atl08']
MM = 2.835  # puntos por mm
# reglas del proyecto de QGIS, en el mismo orden de dibujo (la ultima queda arriba)
REG = [("GEDI rh98 < 3 m", gd[(gd.plausible == 1) & (gd.rh98 < 3)], dict(marker='o', c='#dadaeb', edgecolors='#756bb1', linewidths=0.1 * MM), 1.2),
       ("GEDI rh98 3–5 m", gd[(gd.plausible == 1) & (gd.rh98 >= 3) & (gd.rh98 < 5)], dict(marker='o', c='#9e9ac8', linewidths=0), 1.4),
       ("GEDI rh98 5–10 m", gd[(gd.plausible == 1) & (gd.rh98 >= 5) & (gd.rh98 < 10)], dict(marker='o', c='#6a51a3', linewidths=0), 1.6),
       ("GEDI rh98 ≥ 10 m", gd[(gd.plausible == 1) & (gd.rh98 >= 10)], dict(marker='o', c='#3f007d', linewidths=0), 1.9),
       ("GEDI no plausible", gd[gd.plausible == 0], dict(marker='x', c='black', linewidths=0.4 * MM * 0.6), 2.2),
       ("ATL08 (segmento de 100 m)", at, dict(marker='s', c='#00c8ff', linewidths=0), 1.0)]


def huellas(ax, f=0.6):
    for lab, d, kw, mm in REG:
        ax.scatter(d.x, d.y, s=(mm * MM * f) ** 2, zorder=3, **kw)


def h_huellas(f=0.75):
    hs = []
    for lab, d, kw, mm in REG:
        k = dict(kw); ms = mm * MM * f * 1.25
        if k['marker'] == 'x':
            hs.append(Line2D([], [], ls='none', marker='x', color='black', markersize=ms, markeredgewidth=1.2, label=lab))
        else:
            hs.append(Line2D([], [], ls='none', marker=k['marker'], markerfacecolor=k['c'], markeredgecolor=k.get('edgecolors', k['c']),
                             markeredgewidth=0.4, markersize=ms, label=lab))
    return hs


def mapa(fig, rect):
    ax = fig.add_axes(rect); ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1); ax.set_aspect('equal'); return ax


def leyenda(fig, x, ytop, handles, title, fs=10, labelspacing=0.45, **kw):
    lg = fig.legend(handles=handles, title=title, loc='upper left', bbox_to_anchor=(x, ytop), frameon=False, fontsize=fs,
                    title_fontsize=fs + 0.5, alignment='left', handletextpad=0.5, borderaxespad=0, borderpad=0, labelspacing=labelspacing, **kw)
    lg.get_title().set_fontweight('bold')
    fig.canvas.draw(); return lg.get_window_extent().transformed(fig.transFigure.inverted()).y0


def barra(fig, x, ytop, cmap, vmin, vmax, titulo, ticks, fs=10, h_in=1.1):
    Wi, Hi = fig.get_size_inches()
    fig.text(x, ytop, titulo, ha='left', va='top', fontsize=fs + 0.5, fontweight='bold')
    nl = titulo.count('\n') + 1
    yt = ytop - (nl * fs * 1.3 / 72 + 0.08) / Hi
    cax = fig.add_axes([x + 0.02 / Wi, yt - h_in / Hi, 0.16 / Wi, h_in / Hi])
    cb = fig.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin, vmax)), cax=cax)
    cb.set_ticks(ticks); cb.ax.yaxis.set_major_formatter(fmt(0)); cb.ax.tick_params(labelsize=fs)
    return yt - h_in / Hi


# ---------------- datos raster
agb = a_utm(Q + 'A2_IBICUY_CCI_Biomass_v7_AGB.tif', 5)
with rasterio.open(Q + 'A2_IBICUY_CCI_Biomass_v7_AGB.tif') as s: assert s.descriptions[4] == 'AGB_2024'
mb = a_utm(Q + 'A2_IBICUY_MapBiomas_cobertura_1985_2025.tif', 41)
fh = a_utm(Q + 'A2_IBICUY_BIOMASS_P_FH_20251123_1205_sin_agua.tif', 1)
qml = open(Q + 'A2_IBICUY_MapBiomas_cobertura_1985_2025.qml', encoding='utf-8').read()
PAL = {int(v): (l, c) for v, l, c in re.findall(r'value="(\d+)" label="([^"]+)" color="([^"]+)"', qml)}
TILDE = {"Herbaceas": "Herbáceas", "Rios": "Ríos", "oceano": "océano", "areas": "áreas", "Areas": "Áreas"}
PRES = [3, 4, 6, 11, 12, 15, 19, 24, 25, 33]
lut = np.zeros((256, 3)) + 1.0
for v, (l, c) in PAL.items():
    c = c.lstrip('#'); lut[v] = [int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)]
mbi = np.nan_to_num(mb, nan=0).astype(int); mbrgb = lut[mbi]; mbrgb[mbi == 0] = 1.0


def h_mb(fs_wrap=None):
    hs = []
    for v in PRES:
        l = " ".join(TILDE.get(w.rstrip(","), w.rstrip(",")) + ("," if w.endswith(",") else "") for w in PAL[v][0].split(" "))
        if fs_wrap and l in fs_wrap: l = fs_wrap[l]
        hs.append(Patch(facecolor=PAL[v][1], edgecolor='0.3', lw=0.5, label=l))
    hs.append(Patch(facecolor='white', edgecolor='0.3', lw=0.5, label=(fs_wrap or {}).get('fuera', 'Fuera de la cobertura de MapBiomas')))
    return hs


GREENS = plt.get_cmap('Greens')
FHC = LinearSegmentedColormap.from_list('fh', ["#ffffe5", "#d9f0a3", "#78c679", "#238443", "#004529"])
ext = [X0, X1, Y0, Y1]

# ---------------- Figura 24: CCI Biomass AGB 2024 con las huellas (ancho en el Word: 20 cm)
FW, FHt = 7.87, 5.75; pw = 4.05; ph = pw * (Y1 - Y0) / (X1 - X0)
fig = plt.figure(figsize=(FW, FHt))
ax = mapa(fig, [0.72 / FW, 0.62 / FHt, pw / FW, ph / FHt])
ax.imshow(np.ma.masked_invalid(agb), extent=ext, cmap=GREENS, vmin=0, vmax=100, interpolation='nearest')
huellas(ax); ejes_utm(ax)
escala_norte(fig, ax, 5000, '5 km')
xl = (0.72 + pw + 0.62) / FW; ytop = (0.62 + ph - 0.75) / FHt
y = leyenda(fig, xl, ytop, h_huellas(), 'Huellas LiDAR (paso 4)')
barra(fig, xl, y - 0.25 / FHt, GREENS, 0, 100, 'CCI Biomass v7,\nAGB 2024 (Mg/ha)', [0, 20, 40, 60, 80, 100])
guardar(fig, 'F24.png')

# ---------------- Figura 28: MapBiomas 2025 (ancho en el Word: 14 cm)
WR = {'33 Ríos, lagunas, lagos y océano': '33 Ríos, lagunas, lagos\ny océano', 'fuera': 'Fuera de la cobertura\nde MapBiomas'}
FW, FHt = 5.6, 4.6; pw = 2.75; ph = pw * (Y1 - Y0) / (X1 - X0)
plt.rcParams.update({"font.size": 10, "axes.labelsize": 10, "xtick.labelsize": 9.5, "ytick.labelsize": 9.5})
fig = plt.figure(figsize=(FW, FHt))
ax = mapa(fig, [0.62 / FW, 0.62 / FHt, pw / FW, ph / FHt])
ax.imshow(mbrgb, extent=ext, interpolation='nearest'); ejes_utm(ax)
escala_norte(fig, ax, 5000, '5 km', fs=10)
xl = (0.62 + pw + 0.5) / FW
leyenda(fig, xl, (0.62 + ph - 0.72) / FHt, h_mb(WR), 'MapBiomas Argentina,\nColección 3, cobertura 2025\n(leyenda oficial)', fs=9.5, handlelength=1.6)
guardar(fig, 'F28.png')

# ---------------- Figura 31: huellas sobre MapBiomas 2025 (ancho en el Word: 16 cm)
FW, FHt = 6.3, 5.4; pw = 3.0; ph = pw * (Y1 - Y0) / (X1 - X0)
fig = plt.figure(figsize=(FW, FHt))
ax = mapa(fig, [0.62 / FW, 0.62 / FHt, pw / FW, ph / FHt])
ax.imshow(mbrgb, extent=ext, interpolation='nearest'); huellas(ax, 0.5); ejes_utm(ax)
escala_norte(fig, ax, 5000, '5 km', fs=10)
xl = (0.62 + pw + 0.5) / FW
y = leyenda(fig, xl, (0.62 + ph - 0.72) / FHt, h_huellas(0.7), 'Huellas LiDAR (paso 4)', fs=9.5, labelspacing=0.3)
leyenda(fig, xl, y - 0.12 / FHt, h_mb(WR), 'MapBiomas 2025\n(leyenda oficial)', fs=9.5, handlelength=1.6, labelspacing=0.3)
guardar(fig, 'F31.png')
plt.rcParams.update({"font.size": 11, "axes.labelsize": 11, "xtick.labelsize": 10.5, "ytick.labelsize": 10.5})

# ---------------- Figura 32: altura FH de BIOMASS sola y con las huellas (ancho en el Word: 24,7 cm)
FW, FHt = 9.72, 4.75; pw = 3.0; ph = pw * (Y1 - Y0) / (X1 - X0)
fig = plt.figure(figsize=(FW, FHt))
a1 = mapa(fig, [0.72 / FW, 0.66 / FHt, pw / FW, ph / FHt]); a2 = mapa(fig, [(0.72 + pw + 0.2) / FW, 0.66 / FHt, pw / FW, ph / FHt])
for k, a in enumerate((a1, a2)):
    a.imshow(np.ma.masked_invalid(fh), extent=ext, cmap=FHC, vmin=0, vmax=30, interpolation='nearest'); ejes_utm(a, ylab=k == 0)
    if k: a.set_yticklabels([])
huellas(a2, 0.5)
escala_norte(fig, a1, 5000, '5 km', axn=a2)
xl = (0.72 + 2 * pw + 0.2 + 0.62) / FW
y = barra(fig, xl, (0.66 + ph - 0.72) / FHt, FHC, 0, 30, 'BIOMASS L2A FH,\n23/11 a 05/12/2025\nAltura (m); blanco: agua', [0, 10, 20, 30], h_in=0.9)
leyenda(fig, xl, y - 0.25 / FHt, h_huellas(0.7), 'Huellas LiDAR (paso 4),\nsólo a la derecha', fs=10, labelspacing=0.3)
guardar(fig, 'F32.png')
