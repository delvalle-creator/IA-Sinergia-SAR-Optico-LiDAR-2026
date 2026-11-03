import sys; sys.path.insert(0, '/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp7')
from comun import *
from matplotlib.colors import ListedColormap, BoundaryNorm, LinearSegmentedColormap
from scipy import ndimage as ndi
quien = sys.argv[1:] or ['7', '8', '9', '10', '12', '13', '14', '17', '18']
E = BAR
LEG3 = lambda lc='yellow', lt='ladera relevada en 2018': [lin(lc, lt), lin('cyan', 'anillo de referencia'), lin('red', 'grieta relevada en 2018', 3.5)]

def xfase(res=2):
    a = warp(XTC + 'Phase_ifg_15Oct2018_19Oct2018_HH.img', 1, E, res, rs=Resampling.nearest, src_crs='EPSG:4326', nod=0.0); return a
def ign5(ext, res):
    return warp(Q + 'IGN_MDE_5m.tif', 1, ext, res)
DEM = LinearSegmentedColormap.from_list('dem', ['#006837', '#1a9850', '#a6d96a', '#ffffbf', '#fdae61', '#d73027', '#a50026'])
DEM = plt.get_cmap('RdYlGn_r')

# ---------------- Figura 7
if '7' in quien:
    fig, axs, lay = armar(2, E, 18.8, cbar=True, leg_cm=0.7)
    im0 = axs[0].imshow(xfase(), extent=E, cmap='twilight_shifted', vmin=-np.pi, vmax=np.pi, interpolation='nearest')
    capas(axs[0], ladera='black', anillo=True, lw=2)
    im1 = axs[1].imshow(ign5(E, 5), extent=E, cmap=DEM, vmin=5, vmax=70, interpolation='bilinear')
    capas(axs[1], ladera='yellow', anillo=True, lw=2)
    for k, (ax, t) in enumerate(zip(axs, ['(a) X, fase envuelta 15–19/10/2018', '(b) IGN MDE 5 m (2013)'])):
        marco(ax, E, 1000, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
    axs[0].set_ylabel('Norte (m), EPSG:32721')
    escala_norte(fig, lay, axs[0], axs[1], 500, '500 m')
    cbar(fig, lay, im0, [axs[0]], 'fase envuelta (rad)', ticks=[-3, -2, -1, 0, 1, 2, 3], fmt=coma())
    cbar(fig, lay, im1, [axs[1]], 'cota (m, SRVN16)', ticks=[10, 20, 30, 40, 50, 60, 70])
    leyenda(fig, lay, LEG3('black', 'ladera (en b, amarilla)'), 3)
    guardar(fig, 'F07.png')

# ---------------- Figura 8
if '8' in quien:
    fig, axs, lay = armar(3, E, 22.3, cbar=True, leg_cm=0.7, tit_lin=1)
    im0 = axs[0].imshow(xfase(), extent=E, cmap='twilight_shifted', vmin=-np.pi, vmax=np.pi, interpolation='nearest')
    unw = warp(FIG + 'E1_X_Unw_Phase_snaphu_15-19Oct2018.tif', 1, E, 2, rs=Resampling.nearest)
    p1, p99 = -2.79, 2.56   # percentiles 1 y 99 del recorte (los del texto y la barra originales)
    im1 = axs[1].imshow(unw, extent=E, cmap='RdBu', vmin=p1, vmax=p99, interpolation='nearest')
    com = warp(FIG + 'E1_X_componentes_snaphu_15-19Oct2018.tif', 1, E, 2, rs=Resampling.nearest)
    cmc = ListedColormap(['#bdbdbd', '#1f77b4', '#ff7f0e']); nc = BoundaryNorm([-0.5, 0.5, 1.5, 2.5], 3)
    im2 = axs[2].imshow(np.where(com > 2, 2, com), extent=E, cmap=cmc, norm=nc, interpolation='nearest')
    for k, (ax, t) in enumerate(zip(axs, ['(a) Fase envuelta', '(b) Fase desenrollada con SNAPHU', '(c) Componentes conexas de SNAPHU'])):
        capas(ax, ladera='yellow', anillo=True); marco(ax, E, 1000, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
    axs[0].set_ylabel('Norte (m), EPSG:32721')
    escala_norte(fig, lay, axs[0], axs[2], 500, '500 m')
    cbar(fig, lay, im0, [axs[0]], 'rad', ticks=[-3, -2, -1, 0, 1, 2, 3], fmt=coma())
    cb = cbar(fig, lay, im1, [axs[1]], 'rad (percentiles 1 y 99: %s y %s rad)' % (('%.2f' % p1).replace('.', ',').replace('-', '−'), ('%.2f' % p99).replace('.', ',')), ticks=[-2, -1, 0, 1, 2], fmt=coma())
    cb = cbar(fig, lay, im2, [axs[2]], 'componente conexa', ticks=[0, 1, 2])
    cb.ax.set_xticklabels(['0 (sin confianza)', '1', '2'])
    leyenda(fig, lay, LEG3(), 3)
    guardar(fig, 'F08.png')

# ---------------- Figura 9
if '9' in quien:
    fig, axs, lay = armar(3, E, 25.7, cbar=True, leg_cm=0.7)
    xc = warp(XTC + 'coh_15Oct2018_19Oct2018_HH.img', 1, E, 2, rs=Resampling.nearest, src_crs='EPSG:4326', nod=0.0)
    OCRE = '#f2cfa6'
    axs[0].add_patch(Rectangle((E[0], E[2]), E[1] - E[0], E[3] - E[2], fc=OCRE, ec='none', zorder=0))
    im = axs[0].imshow(xc, extent=E, cmap='gray', vmin=0, vmax=1, interpolation='nearest', zorder=1)
    for ax, p in zip(axs[1:], (P0, P1)):
        c = warp(HY + p + '/' + p + '_corr.tif', 1, E, 10, rs=Resampling.nearest, nod=0.0)
        ax.imshow(c, extent=E, cmap='gray', vmin=0, vmax=1, interpolation='nearest')
    for k, (ax, t) in enumerate(zip(axs, ['(a) X COSMO-SkyMed, 15–19/10/2018', '(b) C Sentinel-1, 18/09–30/09/2018', '(c) C Sentinel-1, 12/10–24/10/2018'])):
        capas(ax, ladera='yellow', anillo=True); marco(ax, E, 1000, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
    axs[0].set_ylabel('Norte (m), EPSG:32721')
    escala_norte(fig, lay, axs[0], axs[2], 500, '500 m')
    cbar(fig, lay, im, [axs[1]], 'coherencia', ticks=[0, .2, .4, .6, .8, 1], fmt=coma(), frac=1.0)
    leyenda(fig, lay, LEG3() + [Patch(facecolor=OCRE, edgecolor='0.5', label='sin dato (fuera de la escena)')], 4)
    guardar(fig, 'F09.png')

# ---------------- Figura 10
if '10' in quien:
    fig, axs, lay = armar(2, E, 15.1, cbar=True, leg_cm=0.7, zc_extra=0.85)
    for ax, p, c0, t in zip(axs, (P0, P1), (0.032, 0.072), ('(a) C, 18/09–30/09/2018', '(b) C, 12/10–24/10/2018')):
        d = warp(HY + p + '/' + p + '_los_disp.tif', 1, E, 10, rs=Resampling.nearest, nod=0.0)
        c = warp(HY + p + '/' + p + '_corr.tif', 1, E, 10, rs=Resampling.nearest, nod=0.0)
        d = np.where(c >= 0.3, (d - c0) * 1000, np.nan)
        im = ax.imshow(d, extent=E, cmap='RdBu', vmin=-15, vmax=15, interpolation='nearest'); ax.set_title(t, fontsize=10.5, pad=4)
    for k, ax in enumerate(axs): capas(ax, ladera='yellow', anillo=True); marco(ax, E, 1000, left=k == 0)
    axs[0].set_ylabel('Norte (m), EPSG:32721')
    escala_norte(fig, lay, axs[0], axs[1], 500, '500 m')
    cb = cbar(fig, lay, im, axs, 'desplazamiento LOS respecto de la mediana local (mm); positivo = acercamiento\nal satélite; blanco = coherencia < 0,3', ticks=[-15, -10, -5, 0, 5, 10, 15], fmt=coma(), frac=0.7)
    lay['y_leg'] -= 0.0
    leyenda(fig, lay, LEG3(), 3)
    guardar(fig, 'F10.png')

# ---------------- Figura 12
if '12' in quien:
    fig, axs, lay = armar(2, E, 15.1, leg_cm=2.6)
    d1 = warp(RAS + 'E1_deformacion_confirmada.tif', 1, E, 10, rs=Resampling.nearest)
    d2 = warp(RAS + 'E1_deformacion_confirmada.tif', 2, E, 10, rs=Resampling.nearest)
    print('F12 valores b1', np.unique(d1[np.isfinite(d1)]), 'b2', np.unique(d2[np.isfinite(d2)]))
    c1 = ListedColormap(['#2166ac', '#e6e6e6', '#b2182b']); axs[0].imshow(d1, extent=E, cmap=c1, norm=BoundaryNorm([-1.5, -.5, .5, 1.5], 3), interpolation='nearest')
    c2 = ListedColormap(['#fff5bf', '#fdbf4f', '#d95f0e']); axs[1].imshow(d2, extent=E, cmap=c2, norm=BoundaryNorm([-.5, .5, 1.5, 2.5], 3), interpolation='nearest')
    for k, (ax, t) in enumerate(zip(axs, ['(a) Deformación confirmada (X y C)', '(b) Bandas con dato coherente (votaron)'])):
        capas(ax, ladera='black', anillo=True, lw=2); marco(ax, E, 1000, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
    axs[0].set_ylabel('Norte (m), EPSG:32721')
    escala_norte(fig, lay, axs[0], axs[1], 500, '500 m')
    P = lambda c, l, e='none': Patch(facecolor=c, edgecolor=e, lw=0.8, label=l)
    h = [P('#b2182b', '(a) +1: las dos detectan el movimiento esperado'), P('#2166ac', '(a) −1: las dos, el contrario'),
         P('#e6e6e6', '(a) 0: decidido, sin deformación', '0.5'), P('white', '(a) sin decidir (falta una banda)', '0.5')]
    fig.legend(handles=h, loc='upper center', bbox_to_anchor=(0.5, lay['y_leg']), ncol=2, frameon=False, fontsize=10, columnspacing=1.2, handlelength=1.8)
    h2 = [P('#fff5bf', '(b) 0 bandas', '0.5'), P('#fdbf4f', '(b) 1 banda'), P('#d95f0e', '(b) 2 bandas')]
    fig.legend(handles=h2, loc='upper center', bbox_to_anchor=(0.5, lay['y_leg'] - 1.15 / lay['H']), ncol=3, frameon=False, fontsize=10, handlelength=1.8)
    fig.legend(handles=LEG3('black'), loc='upper center', bbox_to_anchor=(0.5, lay['y_leg'] - 1.75 / lay['H']), ncol=3, frameon=False, fontsize=10, handlelength=1.8, columnspacing=1.2)
    guardar(fig, 'F12.png')

def cbers(ext, res):
    import rasterio as rio
    with rio.open(Q + 'CBERS4A_DIAMANTE_20260926_pansharpened_2m.tif') as s:
        lo, hi = [], []
        for b in (4, 3, 2):
            a = s.read(b, out_shape=(s.height // 8, s.width // 8)).astype('f4'); a = a[a > 0]
            lo.append(a.mean() - 2 * a.std()); hi.append(a.mean() + 2.5 * a.std())
    b = [warp(Q + 'CBERS4A_DIAMANTE_20260926_pansharpened_2m.tif', i, ext, res, nod=0) for i in (4, 3, 2)]
    rgb = np.dstack([st(a, l, h) for a, l, h in zip(b, lo, hi)]); rgb[~np.isfinite(b[0])] = 1; return np.nan_to_num(rgb, nan=1)

LEGF = [lin(C_CIC, 'cicatriz'), lin(C_DEP, 'depósito'), lin('red', 'grieta relevada en 2018', 3.5)]
# ---------------- Figura 13
if '13' in quien:
    C = CIC
    fig, axs, lay = armar(2, C, 18.2, cbar=True, leg_cm=0.7)
    axs[0].imshow(cbers(C, 1), extent=C, interpolation='bilinear')
    im = axs[1].imshow(ign5(C, 1), extent=C, cmap=DEM, vmin=10, vmax=60, interpolation='bilinear')
    for k, (ax, t) in enumerate(zip(axs, ['(a) CBERS-4A, 26/09/2026, color natural (2 m)', '(b) IGN MDE 5 m (vuelo de 2013)'])):
        capas(ax, formas=True, lw=2.2, gw=(7, 4)); marco(ax, C, 100, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
    axs[0].set_ylabel('Norte (m), EPSG:32721')
    escala_norte(fig, lay, axs[0], axs[1], 100, '100 m')
    cbar(fig, lay, im, [axs[1]], 'cota (m, SRVN16)', ticks=[10, 20, 30, 40, 50, 60])
    leyenda(fig, lay, [lin(C_CIC, 'cicatriz (trazada sobre el CBERS-4A)'), lin(C_DEP, 'depósito (claro con NDVI < 0,30)'), lin('red', 'grieta relevada en 2018', 3.5)], 3)
    guardar(fig, 'F13.png')

# ---------------- Figura 14
if '14' in quien:
    fig, axs, lay = armar(3, E, 25.6, cbar=True, leg_cm=0.7)
    im0 = axs[0].imshow(ign5(E, 5), extent=E, cmap=DEM, vmin=5, vmax=70, interpolation='bilinear')
    axs[1].imshow(warp(Q + 'CopernicusDEM30.tif', 1, E, 10, rs=Resampling.nearest), extent=E, cmap=DEM, vmin=5, vmax=70, interpolation='nearest')
    dz = -warp(FIG + 'E1_dz_GLO30_menos_IGN5m_30m.tif', 1, E, 10, rs=Resampling.nearest)
    im2 = axs[2].imshow(dz, extent=E, cmap='RdBu', vmin=-10, vmax=10, interpolation='nearest')
    Z = (155150, 155650, 6446150, 6446650)
    axs[2].add_patch(Rectangle((Z[0], Z[2]), Z[1] - Z[0], Z[3] - Z[2], fill=False, ec='black', lw=1.3, zorder=9))
    for k, (ax, t) in enumerate(zip(axs, ['(a) IGN 5 m (2013), «después»', '(b) Copernicus GLO-30 (2011–2015), «antes»', '(c) IGN menos GLO-30 a 30 m, sesgo restado'])):
        capas(ax, formas=True, lw=1.6, gw=(4, 2.3)); marco(ax, E, 1000, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
    axs[0].set_ylabel('Norte (m), EPSG:32721')
    # recuadro ampliado, sobre el rio (sin dato del IGN) en el angulo noroeste del panel (c)
    b = axs[2].get_position()
    wi = 0.40 * b.width; hi = wi * lay['W'] / lay['H']
    ia = fig.add_axes([b.x0 + 0.015 * b.width, b.y1 - hi - 0.015 * b.height, wi, hi])
    ia.imshow(dz, extent=E, cmap='RdBu', vmin=-10, vmax=10, interpolation='nearest'); capas(ia, formas=True, lw=1.8, gw=(4.5, 2.6))
    ia.set_xlim(Z[0], Z[1]); ia.set_ylim(Z[2], Z[3]); ia.set_xticks([]); ia.set_yticks([]); ia.set_xlabel(''); ia.set_ylabel('')
    for s_ in ia.spines.values(): s_.set_lw(1.3)
    escala_norte(fig, lay, axs[0], axs[2], 500, '500 m')
    cbar(fig, lay, im0, axs[:2], 'cota (m)', ticks=[10, 20, 30, 40, 50, 60, 70], frac=0.96)
    cbar(fig, lay, im2, [axs[2]], 'dZ = IGN − GLO-30 (m); rojo = el IGN más bajo', ticks=[-10, -5, 0, 5, 10], fmt=coma())
    leyenda(fig, lay, LEGF + [Patch(facecolor='none', edgecolor='black', lw=1.3, label='zona ampliada en el recuadro')], 4)
    guardar(fig, 'F14.png')

# ---------------- Figura 17
if '17' in quien:
    PX = 5
    vel = warp(U + 'Tp10_Impacto_urbano/05_Resultados/02_Rasters/E_PARANA_DIAMANTE_velocidad_vertical.tif', 1, E, PX, rs=Resampling.nearest)
    sus = warp(RAS + 'E1_susceptibilidad_fisuras_hipotetica.tif', 1, E, PX, rs=Resampling.nearest)
    ign = warp(Q + 'IGN_MDE_5m.tif', 1, E, PX, rs=Resampling.nearest)
    ign = np.where(np.isfinite(ign), ign, warp(Q + 'IGN_MDE_mosaico2018.tif', 1, E, PX, rs=Resampling.nearest, cero=True))
    gy, gx = np.gradient(ndi.gaussian_filter(np.nan_to_num(ign, nan=np.nanmin(ign)), 2), PX); pend = np.hypot(gx, gy) * 100
    meseta = ign > 40; bajo = (ign < 15) | ~np.isfinite(ign)
    borde = (pend > 30) & (ign > 15) & (ndi.distance_transform_edt(~meseta) * PX < 30) & (ndi.distance_transform_edt(~bajo) * PX < 250)
    lab, n = ndi.label(borde); tam = ndi.sum(borde, lab, range(1, n + 1)); borde = np.isin(lab, 1 + np.where(tam > 400)[0])
    fondo = cbers(E, 2)
    fig, axs, lay = armar(2, E, 22.0, cbar=True, leg_cm=1.1)
    for ax in axs: ax.imshow(fondo, extent=E, interpolation='bilinear')
    axs[0].imshow(np.clip(vel, -20, 20), extent=E, cmap='RdBu', vmin=-20, vmax=20, alpha=.85, interpolation='nearest')
    im = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(-20, 20), cmap='RdBu')
    cms = ListedColormap([(1, 1, .75, .45), (1, .6, 0, .65), (.85, 0, 0, .8)])
    axs[1].imshow(np.where(sus > 0, sus, np.nan), extent=E, cmap=cms, norm=BoundaryNorm([.5, 1.5, 2.5, 3.5], 3), interpolation='nearest')
    axs[1].contour(np.linspace(E[0] + PX / 2, E[1] - PX / 2, borde.shape[1]), np.linspace(E[3] - PX / 2, E[2] + PX / 2, borde.shape[0]), borde.astype(float), levels=[.5], colors='k', linewidths=.7)
    for k, (ax, t) in enumerate(zip(axs, ['(a) Velocidad vertical HyP3 (120 pares, jun. 2025 – jul. 2026)', '(b) Susceptibilidad a fisuras en viviendas (HIPOTÉTICA)'])):
        capas(ax, formas=True, lw=1.6, gw=(4, 2.3)); marco(ax, E, 1000, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
    axs[0].set_ylabel('Norte (m), EPSG:32721')
    escala_norte(fig, lay, axs[0], axs[1], 500, '500 m')
    cbar(fig, lay, im, [axs[0]], 'velocidad vertical (mm/año); rojo = hundimiento', ticks=[-20, -15, -10, -5, 0, 5, 10, 15, 20], fmt=coma())
    b1 = axs[1].get_position()
    h = [Patch(facecolor=(.85, 0, 0, .8), label='Alta: ≤ 150 m del borde y velocidad < −13,6 mm/año (interior − 2σ)'),
         Patch(facecolor=(1, .6, 0, .65), label='Media: una de las dos condiciones'),
         Patch(facecolor=(1, 1, .75, .9), edgecolor='0.4', lw=.6, label='Baja: resto de la zona construida'),
         lin('black', 'Talud de la barranca (IGN 5 m)', 1.0)]
    fig.legend(handles=h, loc='upper left', bbox_to_anchor=(b1.x0 - 0.02, lay['y_cb'] + 0.95 / lay['H']), ncol=1, frameon=False, fontsize=10, handlelength=1.8, labelspacing=0.3)
    leyenda(fig, lay, [lin('red', 'Grieta relevada en 2018', 3.5), lin(C_CIC, 'Cicatriz'), lin(C_DEP, 'Depósito')], 3)
    guardar(fig, 'F17.png')

# ---------------- Figura 18
if '18' in quien:
    import rasterio as rio
    from rasterio.transform import array_bounds
    def emb(a):
        with rio.open(Q + 'AlphaEarth_embeddings_%d_10m.tif' % a) as s:
            x = s.read().astype('f4'); T = s.transform; sh = (s.height, s.width)
        nod = (x == -128).any(0); v = np.sign(x) * (x / 127.5) ** 2; n = np.linalg.norm(v, axis=0); n[n == 0] = 1; v = v / n; v[:, nod] = np.nan
        return v, T, sh
    A, T, sh = emb(2018); B, _, _ = emb(2025); sim = (A * B).sum(0); del A, B
    w, s_, e, n_ = array_bounds(sh[0], sh[1], T); ext = (w, e, s_, n_)
    C20 = 'EPSG:32720'; f20 = frm.to_crs(C20); g20 = gri.to_crs(C20)
    cx, cy = f20[f20.tipo == 'cicatriz'].union_all().centroid.coords[0]; R_ = 700
    Z = (cx - R_, cx + R_, cy - R_, cy + R_)
    def rgb(a):
        with rio.open(Q + 'AlphaEarth_embeddings_%d_10m_CP1_CP2_CP3_RGB_8bit.tif' % a) as s: return np.dstack([np.clip(x / 255., 0, 1) for x in s.read()[:3].astype('f4')])
    fig, axs, lay = armar(3, Z, 17.8, cbar=True, leg_cm=0.7, g=0.75, tit_lin=2)
    axs[0].imshow(rgb(2018), extent=ext, interpolation='nearest'); axs[1].imshow(rgb(2025), extent=ext, interpolation='nearest')
    im = axs[2].imshow(sim, extent=ext, cmap='magma', vmin=0.4, vmax=1, interpolation='nearest')
    for k, (ax, t) in enumerate(zip(axs, ['(a) Embeddings 2018,\nCP1-CP2-CP3', '(b) Embeddings 2025,\nCP1-CP2-CP3', '(c) Semejanza 2018–2025\n(coseno)'])):
        f20[f20.tipo == 'cicatriz'].boundary.plot(ax=ax, color=C_CIC, lw=1.6, zorder=6); f20[f20.tipo == 'deposito'].boundary.plot(ax=ax, color=C_DEP, lw=1.6, zorder=6)
        g20.plot(ax=ax, color='white', lw=4, zorder=7); g20.plot(ax=ax, color='red', lw=2.3, zorder=8)
        marco(ax, Z, 500, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
    axs[0].set_ylabel('Norte (m), EPSG:32720')
    escala_norte(fig, lay, axs[0], axs[2], 500, '500 m')
    cbar(fig, lay, im, [axs[2]], '1 = sin cambio; bajo = cambio', ticks=[.4, .5, .6, .7, .8, .9, 1], fmt=coma(), frac=1.0)
    leyenda(fig, lay, [lin(C_CIC, 'Cicatriz (CBERS-4A)'), lin(C_DEP, 'Depósito (CBERS-4A)'), lin('red', 'Grieta relevada en 2018', 3.5)], 3)
    guardar(fig, 'F18.png')
