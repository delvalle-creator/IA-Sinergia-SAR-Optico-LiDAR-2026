import sys; sys.path.insert(0, '/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp7')
from comun import *
from matplotlib.colors import ListedColormap, BoundaryNorm, LinearSegmentedColormap
import re
quien = sys.argv[1:] or ['1', '2', '3', '4']

_S2LIM = [np.nanpercentile(warp(Q + 'S2_20181019.tif', i, SITIO, 30, nod=0), (2, 98)) for i in (3, 2, 1)]
def s2nat(ext, res):
    b = [warp(Q + 'S2_20181019.tif', i, ext, res, nod=0) for i in (3, 2, 1)]
    rgb = np.dstack([st(a, l[0], l[1]) for a, l in zip(b, _S2LIM)])
    m = ~np.isfinite(b[0]); rgb[m] = 1; return rgb

def rgb8(path, ext, res, gcps=False, rs=Resampling.bilinear):
    b = [warp(path, i, ext, res, nod=0, rs=rs, gcps=gcps) for i in (1, 2, 3)]
    rgb = np.dstack([np.clip(a / 255., 0, 1) for a in b]); rgb[~np.isfinite(b[0])] = 1; return np.nan_to_num(rgb, nan=1)

def cbers(ext, res):
    import rasterio as rio
    with rio.open(Q + 'CBERS4A_DIAMANTE_20260926_pansharpened_2m.tif') as s:
        lo, hi = [], []
        for b in (4, 3, 2):
            a = s.read(b, out_shape=(s.height // 8, s.width // 8)).astype('f4'); a = a[a > 0]
            lo.append(a.mean() - 2 * a.std()); hi.append(a.mean() + 2.5 * a.std())
    b = [warp(Q + 'CBERS4A_DIAMANTE_20260926_pansharpened_2m.tif', i, ext, res, nod=0) for i in (4, 3, 2)]
    rgb = np.dstack([st(a, l, h) for a, l, h in zip(b, lo, hi)]); rgb[~np.isfinite(b[0])] = 1; return np.nan_to_num(rgb, nan=1)

# ---------------- Figura 1
if '1' in quien:
    E = SITIO
    fig, axs, lay = armar(2, E, 19.3, cbar=False, leg_cm=0.7)
    for k, (ax, im, t) in enumerate(zip(axs, [s2nat(E, 15), rgb8(RGBD + 'S1_C_20181024_RGB_8bit.tif', E, 15)],
                                       ['(a) Sentinel-2, 19/10/2018, color natural', '(b) Sentinel-1 C, 24/10/2018 (VV, VH, VV/VH)'])):
        ax.imshow(im, extent=E, interpolation='bilinear'); capas(ax, ladera='yellow', grieta=False)
        marco(ax, E, 4000, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
    axs[0].set_ylabel('Norte (m), EPSG:32721')
    escala_norte(fig, lay, axs[0], axs[1], 2000, '2 km')
    leyenda(fig, lay, [lin('yellow', 'ladera relevada en 2018 (rectángulo)')], 1)
    guardar(fig, 'F01.png')

# ---------------- Figura 2
if '2' in quien:
    E = SITIO
    q = open(Q + 'MapBiomas_cobertura_1985_2025.qml', encoding='utf-8').read()
    pal = {int(v): c for v, c in re.findall(r'paletteEntry value="(\d+)" label="[^"]*" color="(#[0-9A-Fa-f]{6})"', q)}
    nom = {3: 'Bosques cerrados', 4: 'Bosques abiertos', 6: 'Bosques inundables', 9: 'Silvicultura', 11: 'Herbáceas inundables',
           12: 'Herbáceas', 15: 'Pastura', 19: 'Cultivos temporarios', 24: 'Áreas urbanas', 33: 'Ríos, lagunas, lagos y océano',
           21: 'Mosaico de usos', 22: 'Área sin vegetación', 25: 'Otras áreas no vegetadas', 14: 'Agropecuario', 10: 'Vegetación herbácea y arbustiva'}
    a = warp(Q + 'MapBiomas_cobertura_1985_2025.tif', 34, E, 15, rs=Resampling.nearest, nod=0)
    cl = sorted(int(v) for v in np.unique(a[np.isfinite(a)]))
    cnt = {c: (a == c).sum() for c in cl}; cl = [c for c in cl if cnt[c] > 50 and c in nom]
    rgb = np.ones(a.shape + (3,))
    from matplotlib.colors import to_rgb
    for c in cl: rgb[a == c] = to_rgb(pal[c])
    fig, axs, lay = armar(1, E, 14.6, leg_cm=0.0, R=7.3)
    ax = axs[0]; ax.imshow(rgb, extent=E, interpolation='nearest'); capas(ax, ladera='black', grieta=False, lw=2)
    marco(ax, E, 4000); ax.set_ylabel('Norte (m), EPSG:32721'); ax.set_title('MapBiomas Argentina, cobertura 2018', fontsize=10.5, pad=4)
    h = [Patch(facecolor=pal[c], edgecolor='0.4', lw=0.6, label='%d %s' % (c, nom.get(c, c))) for c in cl] + [lin('black', 'Ladera relevada en 2018')]
    b = ax.get_position()
    fig.legend(handles=h, loc='center left', bbox_to_anchor=(b.x1 + 1.15 / lay['W'], (b.y0 + b.y1) / 2), frameon=False, fontsize=10, handlelength=1.8)
    escala_norte(fig, lay, ax, ax, 2000, '2 km')
    guardar(fig, 'F02.png')

# ---------------- Figura 3
if '3' in quien:
    E = SITIO
    fig, axs, lay = armar(2, E, 17.7, cbar=True, leg_cm=0.7)
    p = rgb8(RGBD + 'BIOMASS_P_20260603_RGB_8bit.tif', E, 15, gcps=True)
    axs[0].imshow(p, extent=E, interpolation='bilinear'); capas(axs[0], ladera='yellow', grieta=False)
    axs[0].set_title('(a) BIOMASS P, 03/06/2026, $\\gamma^0$ HH, VH, HH/VH', fontsize=10.5, pad=4)
    agb = warp(Q + 'CCI_Biomass_v7_AGB.tif', 5, E, 15, rs=Resampling.nearest, nod=None)
    cm = LinearSegmentedColormap.from_list('agb', [(0, '#f7fcf5'), (25 / 150, '#c7e9c0'), (50 / 150, '#74c476'), (100 / 150, '#238b45'), (1, '#00441b')])
    im = axs[1].imshow(agb, extent=E, cmap=cm, vmin=0, vmax=150, interpolation='nearest'); capas(axs[1], ladera='black', grieta=False)
    axs[1].set_title('(b) CCI Biomass v7, AGB 2024', fontsize=10.5, pad=4)
    for k, ax in enumerate(axs): marco(ax, E, 4000, left=k == 0)
    axs[0].set_ylabel('Norte (m), EPSG:32721')
    escala_norte(fig, lay, axs[0], axs[1], 2000, '2 km')
    cbar(fig, lay, im, [axs[1]], 'AGB 2024 (Mg/ha)', ticks=[0, 25, 50, 75, 100, 125, 150])
    leyenda(fig, lay, [lin('yellow', 'ladera relevada en 2018 (en b, en negro)')], 1)
    guardar(fig, 'F03.png')

# ---------------- Figura 4
if '4' in quien:
    E = BAR
    fig, axs, lay = armar(2, E, 17.9, leg_cm=0.7)
    for k, (ax, im, t) in enumerate(zip(axs, [s2nat(E, 5), cbers(E, 2)], ['(a) Sentinel-2, 19/10/2018', '(b) CBERS-4A 2 m, 26/09/2026'])):
        ax.imshow(im, extent=E, interpolation='bilinear'); capas(ax, ladera='yellow', anillo=True)
        marco(ax, E, 1000, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
    axs[0].set_ylabel('Norte (m), EPSG:32721')
    escala_norte(fig, lay, axs[0], axs[1], 500, '500 m')
    leyenda(fig, lay, [lin('yellow', 'ladera (relevamiento 2018)'), lin('cyan', 'anillo de referencia, 500 m'), lin('red', 'grieta relevada en 2018', 3.5)], 3)
    guardar(fig, 'F04.png')
