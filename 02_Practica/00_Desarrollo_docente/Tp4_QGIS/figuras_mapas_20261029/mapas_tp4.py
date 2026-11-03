# Tp4: mapas con escala y norte FUERA del área del mapa (estilo de estilo_mapas_tp2.py)
import numpy as np, rasterio, geopandas as gpd, pandas as pd, matplotlib, glob, sys, re
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, Patch, FancyArrow
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap
import matplotlib.patheffects as pe
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
plt.rcParams['font.family'] = 'Liberation Serif'; plt.rcParams['font.size'] = 10
U = '/mnt/user-data/uploads/02_Practica/'
Q1 = U + 'Tp1_Convergencia/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/'
S4 = U + 'Tp4_Validacion/02_Subsets_SNAP_QGIS/'
T4 = U + 'Tp4_Validacion/04_Tablas_de_trabajo/'
OUT = '/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp4m/maps/'
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
FULL = (380780, 419280, 6514300, 6559010)
NOD = (1, 1, 1)
CCOL = {1: '#1f4e9e', 2: '#7fd1d6', 3: '#1a7a33', 4: '#a0602b', 5: '#f2e3a0', 6: '#d9b38c', 7: '#e31a1c'}


def grid(ext, res):
    x0, x1, y0, y1 = ext
    return int(round((x1 - x0) / res)), int(round((y1 - y0) / res)), from_origin(x0, y1, res, res)


def warp(f, band, ext, res, rs=Resampling.nearest, dtype='f4', fill=0):
    r = rasterio.open(f); nx, ny, T = grid(ext, res)
    a = np.full((ny, nx), fill, dtype)
    reproject(rasterio.band(r, band), a, dst_transform=T, dst_crs='EPSG:32721', resampling=rs,
              src_nodata=r.nodata, dst_nodata=fill)
    return a


def s2_rgb(ext, res=20, aclarar=0.0):
    f = Q1 + 'B_CONCORDIA_S2_20231104.tif'
    b = [warp(f, k, ext, res, Resampling.average) for k in (3, 2, 1)]
    a = np.stack(b, -1); m = (a == 0).all(-1)
    v = a[~m]
    lo, hi = np.percentile(v, 2, axis=0), np.percentile(v, 98, axis=0)
    out = np.clip((a - lo) / (hi - lo), 0, 1) ** 0.9
    out = out * (1 - aclarar) + aclarar
    out[m] = NOD
    return out


def frame(ax, ext, left=True, bottom=True, step=None):
    if step:
        ax.xaxis.set_major_locator(MultipleLocator(step)); ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.tick_params(labelsize=9.5)
    for l in ax.get_yticklabels(): l.set_rotation(90); l.set_va('center')
    if not left: ax.set_yticklabels([])
    if not bottom: ax.set_xticklabels([])


def escala_norte(fig, ax, L, txt, y, axn=None, dx_in=0.16):
    """Barra de escala FUERA del mapa, bajo el primer panel; flecha norte FUERA, a la derecha
    del borde superior del panel de más a la derecha (esquinero superior derecho)."""
    fig.canvas.draw()
    W, H = fig.get_size_inches()
    b = ax.get_position(); ext = ax.get_xlim(); frac = L / (ext[1] - ext[0]) * b.width
    x0 = b.x0; h = 0.05 / H
    sa = fig.add_axes([x0, y, frac, h]); sa.set_xlim(0, 1); sa.set_ylim(0, 1); sa.axis('off')
    sa.add_patch(Rectangle((0, 0), 0.5, 1, fc='black', ec='black', lw=0.8))
    sa.add_patch(Rectangle((0.5, 0), 0.5, 1, fc='white', ec='black', lw=0.8))
    fig.text(x0, y + h + 0.03 / H, '0', ha='center', va='bottom', fontsize=10)
    fig.text(x0 + frac, y + h + 0.03 / H, txt, ha='center', va='bottom', fontsize=10)
    bn = (axn or ax).get_position(); xn = bn.x1 + dx_in / W; yt = bn.y1
    fig.add_artist(FancyArrow(xn, yt - 0.42 / H, 0, 0.28 / H, width=0.016 / W, head_width=0.11 / W,
                              head_length=0.12 / H, length_includes_head=True, color='black',
                              transform=fig.transFigure))
    fig.text(xn, yt - 0.10 / H, 'N', ha='center', va='bottom', fontsize=11, fontweight='bold')


def guardar(fig, n):
    fig.savefig(OUT + n, dpi=300); plt.close(fig); print(n)


halo = [pe.withStroke(linewidth=2.2, foreground='white')]

# ------------------------------------------------------------------ Figura 3: sorteo de polígonos
def fig3():
    s = gpd.read_file(T4 + 'puntos_sorteo_control_B_CONCORDIA.gpkg')
    W, H = 16 * CM, 12.4 * CM
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.105, 0.17, 0.46, 0.80])
    ax.imshow(s2_rgb(FULL, 20, 0.30), extent=FULL, interpolation='bilinear')
    u = s[s.etapa == '1 extension']; e = s[s.etapa != '1 extension']
    e = e[~e.resultado.str.startswith('no mirado')]
    ua = u[u.resultado.str.startswith('acepta')]; ub = u[u.resultado.str.startswith('borde')]; uc = u[u.resultado == 'clase completa']
    ea = e[e.resultado.str.startswith('acepta')]; ed = e[~e.resultado.str.startswith('acepta')]
    kw = dict(zorder=3, linewidths=0.9)
    ax.scatter(ub.x, ub.y, s=14, facecolors='none', edgecolors='#333333', **kw)
    ax.scatter(uc.x, uc.y, s=14, facecolors='#9e9e9e', edgecolors='#333333', **kw)
    ax.scatter(ed.x, ed.y, s=16, marker='^', facecolors='none', edgecolors='#b2182b', **kw)
    ax.scatter(ua.x, ua.y, s=34, facecolors='#ffd400', edgecolors='black', zorder=4, linewidths=1.0)
    ax.scatter(ea.x, ea.y, s=40, marker='^', facecolors='#ff7f00', edgecolors='black', zorder=4, linewidths=1.0)
    frame(ax, FULL, step=10000)
    ax.set_xlabel('Este (m)'); ax.set_ylabel('Norte (m), UTM 21S (EPSG:32721)')
    h1 = [Line2D([], [], ls='', marker='o', ms=7, mfc='#ffd400', mec='black', label='aceptado (%d)' % len(ua)),
          Line2D([], [], ls='', marker='o', ms=4.5, mfc='none', mec='#333333', label='borde, mezcla o\ncubierta dudosa (%d)' % len(ub)),
          Line2D([], [], ls='', marker='o', ms=4.5, mfc='#9e9e9e', mec='#333333', label='su clase ya estaba\ncompleta (%d)' % len(uc))]
    h2 = [Line2D([], [], ls='', marker='^', ms=7.5, mfc='#ff7f00', mec='black', label='aceptado (%d)' % len(ea)),
          Line2D([], [], ls='', marker='^', ms=5, mfc='none', mec='#b2182b', label='descartado (%d)' % len(ed))]
    l1 = fig.legend(handles=h1, title='1) %d puntos uniformes\nen el sitio (semilla 20261022)' % len(u),
                    loc='upper left', bbox_to_anchor=(0.64, 0.86), frameon=False, fontsize=10, title_fontsize=10,
                    alignment='left', handletextpad=0.4)
    l1.get_title().set_fontweight('bold')
    l2 = fig.legend(handles=h2, title='2) Sorteo dentro del estrato\nde MapBiomas (humedal, monte\ny suelo desnudo: %d puntos\nmirados)' % len(e),
                    loc='upper left', bbox_to_anchor=(0.64, 0.50), frameon=False, fontsize=10, title_fontsize=10,
                    alignment='left', handletextpad=0.4)
    l2.get_title().set_fontweight('bold')
    fig.text(0.645, 0.10, 'Fondo: Sentinel-2B,\n04/11/2023, RGB\nB4-B3-B2, aclarado.', fontsize=10, va='bottom')
    escala_norte(fig, ax, 5000, '5 km', y=0.035)
    guardar(fig, 'F03.png')


# ------------------------------------------------------------------ Figura 6: mapa de control (30/10/2026: leyendas a la derecha, figura más baja)
def fig6():
    W, H = 16 * CM, 10.4 * CM
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.105, 0.17, 0.42, 0.79])
    ax.imshow(s2_rgb(FULL, 20, 0.0), extent=FULL, interpolation='bilinear')
    f = S4 + 'B_CONCORDIA_cobertura_control_20m.tif'
    c = warp(f, 1, FULL, 20); fu = warp(f, 2, FULL, 20)
    ov = np.zeros(c.shape + (4,))
    for k, (cl, fc) in enumerate([(1, 2), (3, 3)]):
        m = (c == cl) & (fu == fc)
        col = matplotlib.colors.to_rgb(CCOL[cl]); ov[m, :3] = col; ov[m, 3] = 1
    ax.imshow(ov, extent=FULL, interpolation='nearest')
    p = gpd.read_file(T4 + 'control_digitalizado_B_CONCORDIA_desarrollo.gpkg', layer='control')
    ce = p.geometry.centroid
    for cod, x, y in zip(p.codigo, ce.x, ce.y):
        ax.scatter([x], [y], s=34, marker='s', facecolors=CCOL[int(cod)], edgecolors='black', linewidths=1.0, zorder=3)
    frame(ax, FULL, step=10000)
    ax.set_xlabel('Este (m)', fontsize=10); ax.set_ylabel('Norte (m), UTM 21S (EPSG:32721)', fontsize=10)
    h1 = [Patch(fc=CCOL[1], label='Agua permanente (JRC,\nocurrencia ≥ 90 %)'),
          Patch(fc=CCOL[3], label='Monte nativo (MapBiomas\nrecortado con las copas de 2 m)')]
    l1 = fig.legend(handles=h1, title='Mapa de control, 20 m', loc='upper left', bbox_to_anchor=(0.60, 0.90),
                    frameon=False, fontsize=10, title_fontsize=10, alignment='left', handlelength=1.4, handletextpad=0.5)
    l1.get_title().set_fontweight('bold')
    nom = {1: 'agua_permanente', 2: 'humedal_pajonal', 3: 'monte_nativo', 4: 'plantacion_forestal',
           5: 'cultivo_pastura', 6: 'suelo_desnudo', 7: 'urbano'}
    cnt = p.codigo.value_counts()
    h2 = [Line2D([], [], ls='', marker='s', ms=7, mfc=CCOL[k], mec='black', label='%s (%d)' % (nom[k], cnt[k])) for k in nom]
    l2 = fig.legend(handles=h2, title='Polígonos sorteados (cantidad),\nsímbolo de tamaño fijo', loc='upper left',
                    bbox_to_anchor=(0.60, 0.56), frameon=False, fontsize=10, title_fontsize=10,
                    alignment='left', handletextpad=0.4, labelspacing=0.3)
    l2.get_title().set_fontweight('bold')
    escala_norte(fig, ax, 5000, '5 km', y=0.035, dx_in=0.13)
    guardar(fig, 'F06.png')


# ------------------------------------------------------------------ Figura 7: monte recortado
def fig7():
    E = (394720, 396720, 6523305, 6524805)
    res = 2
    cb = U + 'Tp10_Impacto_urbano/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/B_CONCORDIA_CBERS4A_CONCORDIA_20260715_pansharpened_2m.tif'
    a = np.stack([warp(cb, k, E, res, Resampling.nearest) for k in (4, 3, 2)], -1)
    m = (a == 0).all(-1); v = a[~m]
    lo, hi = np.percentile(v, 1, axis=0), np.percentile(v, 99, axis=0)
    rgb = np.clip((a - lo) / (hi - lo), 0, 1) ** 0.9; rgb[m] = NOD
    mb = np.zeros(rgb.shape[:2], 'f4')
    for f in sorted(glob.glob(U + '00_COMUN/08_Originales_crudos/LOCALES/MAPBIOMAS/Bosques_MapBiomas_2023_*.tif')):
        t = warp(f, 1, E, res); mb = np.where(t > 0, 1, mb)
    f = S4 + 'B_CONCORDIA_cobertura_control_20m.tif'
    c = warp(f, 1, E, res); fu = warp(f, 2, E, res); monte = (c == 3) & (fu == 3)
    copa = warp(S4 + 'B_CONCORDIA_copa_CBERS4A_2m_20260715.tif', 1, E, res, fill=255) == 1
    W, H = 25.4 * CM, 7.0 * CM
    fig = plt.figure(figsize=(W, H))
    axs = [fig.add_axes([0.065 + k * 0.213, 0.268, 0.205, 0.559]) for k in range(3)]
    GREEN = matplotlib.colors.to_rgb('#1fa64a'); MAG = matplotlib.colors.to_rgb('#ff00ff')
    tit = ['a) Bosque de MapBiomas 30 m,\nsin recortar', 'b) El mismo bosque recortado\ncon las copas de 2 m', 'c) Máscara de copas de 2 m']
    for k, (ax, msk, col, al) in enumerate(zip(axs, [mb > 0, monte, copa], [GREEN, GREEN, MAG], [0.75, 0.85, 0.9])):
        ax.imshow(rgb, extent=E, interpolation='nearest')
        ov = np.zeros(msk.shape + (4,)); ov[msk, :3] = col; ov[msk, 3] = al
        ax.imshow(ov, extent=E, interpolation='nearest')
        frame(ax, E, left=k == 0, step=500); ax.set_title(tit[k], fontsize=10.5, loc='left')
        ax.set_xlabel('Este (m)'); ax.yaxis.set_major_locator(matplotlib.ticker.FixedLocator([6523500, 6524500]))
    axs[0].set_ylabel('Norte (m), UTM 21S')
    h = [Patch(fc='#1fa64a', alpha=0.8, label='monte del mapa\nde control'), Patch(fc='#ff00ff', label='copa (píxel de 2 m)')]
    lg = fig.legend(handles=h, title='Leyenda', loc='upper left', bbox_to_anchor=(0.745, 0.86), frameon=False,
                    fontsize=10, title_fontsize=10.5, alignment='left')
    lg.get_title().set_fontweight('bold')
    fig.text(0.75, 0.10, 'Fondo de los tres\npaneles: CBERS-4A\nWPM, 15/07/2026,\nfusionado a 2 m,\nRGB B3-B2-B1.', fontsize=10, va='bottom')
    escala_norte(fig, axs[0], 500, '500 m', y=0.022, axn=axs[2])
    guardar(fig, 'F07.png')


# ------------------------------------------------------------------ Figura 13: MapBiomas 2025 y clases del curso
def fig13():
    qml = open(Q1 + 'B_CONCORDIA_MapBiomas_cobertura_1985_2025.qml', encoding='utf8').read()
    pal = {int(v): (l, c) for v, l, c in re.findall(r'value="(\d+)" label="([^"]+)" color="([^"]+)"', qml)}
    acc = {'Herbaceas': 'Herbáceas', 'Areas urbanas': 'Áreas urbanas', 'Otras areas': 'Otras áreas',
           'Rios, lagunas, lagos y oceano': 'Ríos, lagunas, lagos y océano'}
    mbw = warp(Q1 + 'B_CONCORDIA_MapBiomas_cobertura_1985_2025.tif', 41, FULL, 20, dtype='int16')
    cls = [int(v) for v in np.unique(mbw) if v > 0]
    rgb1 = np.ones(mbw.shape + (3,))
    for v in cls: rgb1[mbw == v] = matplotlib.colors.to_rgb(pal[v][1])
    cu = warp(S4 + 'B_CONCORDIA_mapbiomas_2025_clases_curso_20m.tif', 1, FULL, 20, dtype='int16')
    rgb2 = np.ones(cu.shape + (3,))
    for v, c in CCOL.items(): rgb2[cu == v] = matplotlib.colors.to_rgb(c)
    pts = gpd.read_file(T4 + 'B_CONCORDIA_mapbiomas_2025_clases_curso_20m_puntos_a_etiquetar.gpkg')
    W, H = 25.6 * CM, 10.5 * CM
    fig = plt.figure(figsize=(W, H))
    a1 = fig.add_axes([0.055, 0.23, 0.215, 0.61]); a2 = fig.add_axes([0.55, 0.23, 0.215, 0.61])
    a1.imshow(rgb1, extent=FULL, interpolation='nearest'); a2.imshow(rgb2, extent=FULL, interpolation='nearest')
    a2.scatter(pts.geometry.x, pts.geometry.y, s=16, marker='s', facecolors='#ffff00', edgecolors='black', linewidths=0.9, zorder=3)
    # 30/10/2026: números corridos para que no se tapen (adjustText), con línea de guía al punto
    from adjustText import adjust_text
    tx = [a2.text(x, y, str(int(i)), fontsize=9, path_effects=halo, zorder=4)
          for i, x, y in zip(pts['id'], pts.geometry.x, pts.geometry.y)]
    a2.set_xlim(FULL[0], FULL[1]); a2.set_ylim(FULL[2], FULL[3])
    adjust_text(tx, x=list(pts.geometry.x), y=list(pts.geometry.y), ax=a2, expand=(1.25, 1.35),
                force_text=(0.6, 0.8), force_static=(0.4, 0.5), ensure_inside_axes=True,
                arrowprops=dict(arrowstyle='-', color='black', lw=0.5), max_move=None)
    for k, ax in enumerate([a1, a2]):
        frame(ax, FULL, step=10000); ax.set_xlabel('Este (m)')
        ax.yaxis.set_major_locator(matplotlib.ticker.FixedLocator([6520000, 6535000, 6550000]))
    a1.set_ylabel('Norte (m), UTM 21S')
    a1.set_title('a) MapBiomas Argentina,\ncobertura 2025 (leyenda oficial)', fontsize=10.5, loc='left')
    a2.set_title('b) Clases del curso (Tp4_05)\ny los 70 puntos', fontsize=10.5, loc='left')
    def lab(v):
        l = pal[v][0]
        for k2, r in acc.items(): l = l.replace(k2, r)
        return l
    h1 = [Patch(fc=pal[v][1], ec='none', label=lab(v)) for v in cls] + [Patch(fc='white', ec='#888888', lw=0.6, label='Fuera de la cobertura')]
    l1 = fig.legend(handles=h1, title='MapBiomas 2025', loc='upper left', bbox_to_anchor=(0.285, 0.86), frameon=False,
                    fontsize=9.5, title_fontsize=10, alignment='left', labelspacing=0.25, handlelength=1.4, handletextpad=0.5)
    l1.get_title().set_fontweight('bold')
    nom = {1: '1 agua_permanente', 2: '2 humedal_pajonal', 3: '3 monte_nativo', 4: '4 plantacion_forestal',
           5: '5 herbaceo_cultivo_pastura', 6: '6 suelo_desnudo', 7: '7 urbano'}
    h2 = [Patch(fc=CCOL[k], ec='none', label=nom[k]) for k in nom] + [Patch(fc='white', ec='#888888', lw=0.6, label='Fuera de la cobertura'),
          Line2D([], [], ls='', marker='s', ms=6, mfc='#ffff00', mec='black', label='punto de la muestra\n(cuadrado de 20 m,\nsímbolo de tamaño fijo)')]
    l2 = fig.legend(handles=h2, title='Clases del curso', loc='upper left', bbox_to_anchor=(0.808, 0.72), frameon=False,
                    fontsize=9.5, title_fontsize=10, alignment='left', labelspacing=0.25, handlelength=1.4, handletextpad=0.5)
    l2.get_title().set_fontweight('bold')
    escala_norte(fig, a1, 5000, '5 km', y=0.035, axn=a2)
    guardar(fig, 'F13.png')


# ------------------------------------------------------------------ Figura 14: CCI Biomass 2024
def fig14():
    a = warp(Q1 + 'B_CONCORDIA_CCI_Biomass_v7_AGB.tif', 5, FULL, 50, Resampling.nearest, fill=-1)
    a = np.ma.masked_less(a, 0)
    W, H = 12.9 * CM, 11.9 * CM
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.14, 0.17, 0.56, 0.80])
    im = ax.imshow(a, extent=FULL, cmap='Greens', vmin=0, vmax=100, interpolation='nearest')
    frame(ax, FULL, step=10000); ax.set_xlabel('Este (m)'); ax.set_ylabel('Norte (m), UTM 21S')
    cax = fig.add_axes([0.80, 0.36, 0.035, 0.40])
    cb = fig.colorbar(im, cax=cax); cb.ax.tick_params(labelsize=10)
    fig.text(0.765, 0.80, 'CCI Biomass v7,\nbiomasa aérea\n2024 (Mg/ha)', fontsize=10, fontweight='bold', va='bottom')
    fig.text(0.765, 0.17, 'Valores > 100\nMg/ha con el\ncolor de 100.\nPíxel de unos\n100 m.', fontsize=10, va='bottom')
    escala_norte(fig, ax, 5000, '5 km', y=0.035, dx_in=0.16)
    guardar(fig, 'F14.png')


# ------------------------------------------------------------------ Figura 26: puntos del ensayo
def fig26():
    c = pd.read_csv(U + '00_COMUN/09_Herramientas/desarrollo_docente/Tp4M/Tp4_puntos_etiquetados_con_llave.csv')
    c['x'] = c.x_km * 1000; c['y'] = c.y_km * 1000
    si = c[c.coincide == 'si']; no = c[c.coincide == 'no']
    EB = (398800, 406200, 6530800, 6535200); EC = (385300, 387900, 6551750, 6554350)
    W, H = 19.1 * CM, 12.4 * CM
    fig = plt.figure(figsize=(W, H))
    a1 = fig.add_axes([0.085, 0.15, 0.395, 0.80])
    a2 = fig.add_axes([0.555, 0.585, 0.355, 0.355 * W / H * (EB[3] - EB[2]) / (EB[1] - EB[0])])
    hc = 0.30; a3 = fig.add_axes([0.555, 0.15, hc * H / W, hc])
    for ax, ext, res in [(a1, FULL, 20), (a2, EB, 10), (a3, EC, 10)]:
        ax.imshow(s2_rgb(ext, res, 0.30), extent=ext, interpolation='bilinear' if ax is a1 else 'nearest')
    for ax, ms in [(a1, 22), (a2, 40), (a3, 40)]:
        ax.scatter(si.x, si.y, s=ms, c='#2c7bb6', edgecolors='white', linewidths=0.8, zorder=3)
        ax.scatter(no.x, no.y, s=ms * 2.2, marker='X', c='#d7191c', edgecolors='black', linewidths=0.8, zorder=4)
    for ext, t in [(EB, 'b'), (EC, 'c')]:
        a1.add_patch(Rectangle((ext[0], ext[2]), ext[1] - ext[0], ext[3] - ext[2], fill=False, ec='black', lw=1.3, zorder=5))
        a1.text(ext[1] + 300, ext[3] + 200, t, fontsize=11, fontweight='bold', path_effects=halo, zorder=6)
    r31 = no[no.id == 31].iloc[0]
    a1.annotate('31', (r31.x, r31.y), xytext=(-12, -14), textcoords='offset points', fontsize=10, path_effects=halo, zorder=6)
    off = {51: (8, 8), 32: (8, 8), 6: (14, 10), 58: (14, -12), 30: (-24, 6), 62: (-24, -14), 49: (-20, 6), 16: (12, 6), 39: (8, -14)}
    for ax in (a2, a3):
        for _, r in no.iterrows():
            if r.id in off:
                ax.annotate(str(int(r.id)), (r.x, r.y), xytext=off[r.id], textcoords='offset points', fontsize=10, path_effects=halo, zorder=6,
                            arrowprops=dict(arrowstyle='-', lw=0.7, color='black', shrinkA=0, shrinkB=3))
    frame(a1, FULL, step=10000); frame(a2, EB, step=2000); frame(a3, EC, step=1000); a3.yaxis.set_major_locator(matplotlib.ticker.FixedLocator([6552000, 6554000]))
    a1.set_xlabel('Este (m)'); a1.set_ylabel('Norte (m), UTM 21S')
    a1.set_title('a) Sitio B_CONCORDIA', fontsize=10.5, loc='left')
    a2.set_title('b) Oeste y norte de la ciudad', fontsize=10.5, loc='left')
    a3.set_title('c) Noroeste', fontsize=10.5, loc='left')
    h = [Line2D([], [], ls='', marker='o', ms=6, mfc='#2c7bb6', mec='white', label='coincide (%d)' % len(si)),
         Line2D([], [], ls='', marker='X', ms=9, mfc='#d7191c', mec='black', label='no coincide (%d),\ncon su número' % len(no))]
    lg = fig.legend(handles=h, title='Punto de la muestra', loc='upper left', bbox_to_anchor=(0.80, 0.47), frameon=False,
                    fontsize=10, title_fontsize=10.5, alignment='left')
    lg.get_title().set_fontweight('bold')
    fig.text(0.805, 0.16, 'Fondo: Sentinel-2B,\n04/11/2023, RGB\nB4-B3-B2, aclarado.', fontsize=10, va='bottom')
    escala_norte(fig, a1, 5000, '5 km', y=0.035, axn=a2, dx_in=0.16)
    guardar(fig, 'F26.png')


if __name__ == '__main__':
    import os; os.makedirs(OUT, exist_ok=True)
    for n in (sys.argv[1:] or ['3', '6', '7', '13', '14', '26']):
        globals()['fig' + n]()
