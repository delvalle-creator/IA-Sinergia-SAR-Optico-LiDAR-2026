# Tp7 Figura 16 (31/10/2026): las cuatro transectas en una fila, al tamano final (letras de 10 pt).
# Datos y sesgo local de Tp7_04_icesat2_20m_cicatriz.py (E1_atl08_20m_cicatriz.csv).
import sys, numpy as np, pandas as pd, geopandas as gpd, rasterio
from rasterio.warp import transform as wtr
from shapely.geometry import Point
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
plt.rcParams.update({'font.family': 'Liberation Serif', 'font.size': 10, 'axes.unicode_minus': True})
W, H = float(sys.argv[1]), float(sys.argv[2]); CM = 1/2.54
U = '/mnt/user-data/uploads/'; B = U + 'CURSOS_CEREGEO_2026/02_Practica/Tp7_Barrancas_deslizamientos/'
Q = B + '02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/E1_DIAMANTE_BARRANCA_'
g = pd.read_csv(B + '05_Resultados/04_Tablas/E1_atl08_20m_cicatriz.csv')   # tabla del curso (Tp7_04)
g = gpd.GeoDataFrame(g, geometry=gpd.points_from_xy(g.lon, g.lat), crs=4326).to_crs(32721)
BIAS = float((g.dI - g.dIc).dropna().median()); print('sesgo (el de Tp7_04)', BIAS)
a = pd.read_csv(B + '02_Subsets_SNAP_QGIS/LiDAR_E1_DIAMANTE_BARRANCA/E1_DIAMANTE_BARRANCA_ATL08.csv')
a = gpd.GeoDataFrame(a, geometry=gpd.points_from_xy(a.lon, a.lat), crs=4326).to_crs(32721)
f = gpd.read_file(B + '04_Tablas_de_trabajo/E1_cicatriz_y_deposito.gpkg', layer='formas').to_crs(32721)
cic = f[f.tipo == 'cicatriz'].union_all(); dep = f[f.tipo == 'deposito'].union_all()
gr = gpd.read_file(U + 'DIAMANTE/GRIETAS/grietadte.shp').to_crs(32721).union_all()
src = {k: rasterio.open(Q + n + '.tif') for k, n in [('IGN', 'IGN_MDE_5m'), ('IGNm', 'IGN_MDE_mosaico2018'), ('GLO', 'CopernicusDEM30')]}
def samp(k, X, Y):
    s = src[k]; lon, lat = wtr('EPSG:32721', s.crs, list(X), list(Y)); v = np.array([x[0] for x in s.sample(zip(lon, lat))], float)
    if s.nodata is not None: v[v == s.nodata] = np.nan
    if k == 'IGNm': v[v <= 0] = np.nan
    return v
dN = float((a.N_ar16 - a.N_egm2008).median()); print('dN', dN)
tr = [('20240123', '2024-01-23', 'gt3l'), ('20240123', '2024-01-23', 'gt3r'), ('20250511', '2025-05-11', 'gt2l'), ('20250511', '2025-05-11', 'gt2r')]
fig, axs = plt.subplots(1, 4, figsize=(W*CM, H*CM))
coma = FuncFormatter(lambda v, p: ('%g' % v).replace('.', ',').replace('-', '−'))
for k_, (ax, (fc, fe, hz)) in enumerate(zip(axs, tr)):
    s = g[(g.fecha.astype(str) == fc) & (g.haz == hz)].copy()
    P = np.c_[s.geometry.x, s.geometry.y]; v = np.linalg.svd(P - P.mean(0))[2][0]
    if v[1] < 0: v = -v
    t = (P - P.mean(0)) @ v; k0 = np.argmin([Point(p).distance(cic.union(dep)) for p in P]); t0 = t[k0]; t = t - t0
    s['t'] = t; s = s[(s.t > -350) & (s.t < 350)]
    tt = np.arange(-360, 360, 2); X = P.mean(0)[0] + (tt + t0)*v[0]; Y = P.mean(0)[1] + (tt + t0)*v[1]
    ign = samp('IGN', X, Y); ign = np.where(np.isfinite(ign), ign, samp('IGNm', X, Y)); glo = samp('GLO', X, Y) - dN
    inc = np.array([cic.distance(Point(x, y)) < 1 for x, y in zip(X, Y)]); ind = np.array([dep.distance(Point(x, y)) < 1 for x, y in zip(X, Y)])
    for m, col in [(inc, 'orange'), (ind, 'deepskyblue')]:
        if m.any(): ax.axvspan(tt[m].min(), tt[m].max(), color=col, alpha=.3, lw=0)
    dg = np.array([gr.distance(Point(x, y)) for x, y in zip(X, Y)]); kk = np.argmin(dg)
    if dg[kk] < 40: ax.axvline(tt[kk], color='red', lw=2.5)
    ax.plot(tt, ign, color='0.2', lw=1.1); ax.plot(tt, glo, color='tab:orange', lw=1.0, alpha=.85)
    s100 = a[(a.fecha == fe) & (a.haz == hz)]; P1 = np.c_[s100.geometry.x, s100.geometry.y]; t1 = (P1 - P.mean(0)) @ v - t0
    m1 = (t1 > -350) & (t1 < 350)
    ax.scatter(t1[m1], (s100.h_terreno_srvn16 - BIAS)[m1], s=34, marker='s', facecolor='none', edgecolor='tab:purple', lw=1.2, zorder=4)
    ax.scatter(s.t, s.h_srvn16 - BIAS, s=12, c='tab:blue', edgecolor='k', lw=.3, zorder=5)
    tipo = 'fuerte' if s.tipo.iloc[0] == 'strong' else 'débil'
    ax.set_title('(%s) %s/%s/%s, %s (%s)' % ('abcd'[k_], fc[6:], fc[4:6], fc[:4], hz, tipo), pad=3)
    ax.set_xlim(-350, 350); ax.set_xticks([-300, -150, 0, 150, 300]); ax.xaxis.set_major_formatter(coma)
    ax.grid(alpha=.3); ax.tick_params(length=2.5, pad=1.5)
    ax.set_xlabel('distancia, sur → norte (m)', labelpad=1)
    if k_ == 0: ax.set_ylabel('cota SRVN16 (m)', labelpad=2)
h = [Line2D([], [], color='0.2', lw=1.4, label='IGN 5 m (2013)'), Line2D([], [], color='tab:orange', lw=1.4, label='GLO-30 (2011–2015)'),
     Line2D([], [], ls='none', marker='o', ms=5, mfc='tab:blue', mec='k', mew=.4, label='ICESat-2 cada 20 m'),
     Line2D([], [], ls='none', marker='s', ms=6, mfc='none', mec='tab:purple', mew=1.2, label='ICESat-2 cada 100 m'),
     Patch(facecolor='orange', alpha=.3, label='cicatriz'), Patch(facecolor='deepskyblue', alpha=.3, label='depósito'), Line2D([], [], color='red', lw=2.5, label='grieta')]
fig.legend(handles=h, loc='lower center', ncol=7, frameon=False, handlelength=1.4, columnspacing=1.0, handletextpad=0.4, borderaxespad=0.1)
fig.tight_layout(rect=(0, 0.09, 1, 1), w_pad=0.6)
fig.savefig('Tp7_Figura_16.png', dpi=300)
