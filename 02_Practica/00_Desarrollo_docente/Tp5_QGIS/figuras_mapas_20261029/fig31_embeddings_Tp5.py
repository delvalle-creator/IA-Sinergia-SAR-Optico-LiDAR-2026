# Tp5, Figura 31: embeddings AlphaEarth 2020 (CP1-CP2-CP3), quemado segun kNN con 20 + 20 muestras de MapBiomas Fuego
# 2020 (mismo calculo y semilla que des_embeddings.py) y variante multisensor del Tp5. Rehecha el 30/10/2026 con
# coordenadas, escala y norte fuera del mapa y letra del tamano del texto.
# Uso: python fig31_embeddings_Tp5.py <des_embeddings.py> <mapas_tp5.py> <carpeta QGIS_GeoTIFF> <A1_variante_multisensor.tif> <salida.png>
import sys, os, importlib.util, types
de, mp, qgd, v4, out = sys.argv[1:6]
src = open(de, encoding='utf-8').read(); src = src[:src.index('\nif TP ==')] if '\nif TP ==' in src else src
cut = src.index('POS = [a for a in sys.argv')
pre = src[:cut]
E_ = types.ModuleType('e'); sys.argv = ['x', 'Tp5', '/tmp']; exec(compile(src.split('\nif TP')[0] if False else src[:src.index('# Argumentos posicionales')], 'de', 'exec'), E_.__dict__)
import numpy as np
E_.RNG = np.random.default_rng(2026); E_.LOG = []; E_.log = lambda s: print(s)
spec = importlib.util.spec_from_file_location('m', mp); sys.argv = ['x', 'NINGUNA']; m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
f = 3
q = lambda n: os.path.join(qgd, n)
for fn in ('leer_emb', 'leer_rgb', 'a_grilla', 'knn', 'sorteo', 'metricas'):
    pass
src_funcs = open(de, encoding='utf-8').read()
s0 = src_funcs.index('def leer_emb'); s1 = src_funcs.index('def guardar')
ns = dict(np=np, os=os, log=E_.log, RNG=E_.RNG)
exec('import rasterio\nfrom rasterio.warp import reproject, Resampling\nfrom rasterio.transform import Affine\nimport re\n' + src_funcs[s0:s1], ns)
E, T, crs, sh = ns['leer_emb'](q('A1_DELTA_QUEMAS_AlphaEarth_embeddings_2020_10m.tif'), f)
ref = ns['a_grilla'](q('A1_DELTA_QUEMAS_MapBiomas_fuego_anual_1999_2025.tif'), 22, T, crs, sh, nod=255)
otro = ns['a_grilla'](v4, 1, T, crs, sh)
ok = np.isfinite(E).all(0) & np.isfinite(ref)
R = ref[ok].astype(int); X = E[:, ok].T
si = ns['sorteo'](R, [0, 1]); resto = np.ones(len(R), bool); resto[si] = False
okall = np.isfinite(E).all(0); Xall = E[:, okall].T
pall = ns['knn'](Xall, X[si], R[si]); pm = np.full(sh, np.nan); pm[okall] = pall
oa, _ = ns['metricas'](R[resto], pm[ok][resto], [0, 1])
ev = (otro == 1); val = np.isfinite(otro) & okall
print('OA %.1f dentro %.1f fuera %.1f' % (100 * oa, 100 * (pm[ev & okall] == 1).mean(), 100 * (pm[val & ~ev] == 1).mean()))
ext = (T.c, T.c + T.a * sh[1], T.f + T.e * sh[0], T.f)
rgb = ns['leer_rgb'](q('A1_DELTA_QUEMAS_AlphaEarth_embeddings_2020_10m_CP1_CP2_CP3_RGB_8bit.tif'), f)
c1 = '#d4271e'
m.MAXH_CUR[0] = 13.5
fig, axs = m.layout(25.4, 3, ext, bottom_extra=1.6)
axs[0].imshow(rgb, extent=ext, interpolation='nearest'); m.frame(axs[0], ext, True, 10000)
axs[1].imshow(pm, extent=ext, cmap=ListedColormap(['#f0f0f0', c1]), vmin=0, vmax=1, interpolation='nearest')
axs[2].imshow(np.where(val, ev.astype(float), np.nan), extent=ext, cmap=ListedColormap(['#f0f0f0', c1]), vmin=0, vmax=1, interpolation='nearest')
for k, (ax, t) in enumerate(zip(axs, ['(a) Embeddings, CP1-CP2-CP3', '(b) kNN con embeddings', '(c) Variante multisensor V4'])):
    m.frame(ax, ext, k == 0, 10000); ax.set_title(t, fontsize=11, pad=4)
    ax.set_xlabel('Este, UTM 21S (m)', fontsize=10, labelpad=2)
    if k == 0: ax.set_ylabel('Norte, UTM 21S (m)', fontsize=10, labelpad=2)
m.escala_norte(fig, axs[0], 5000, '5 km', axn=axs[2])
g = fig._geo
for ax, lab in ((axs[1], 'Quemado 2020 (kNN)'), (axs[2], 'Quemado 15/07–13/10 (V4)')):
    b = ax.get_position()
    fig.legend(handles=[Patch(color=c1, label=lab), Patch(facecolor='#f0f0f0', edgecolor='0.5', label='No quemado')],
               loc='upper center', bbox_to_anchor=((b.x0 + b.x1) / 2, (g['bottom_extra'] - 0.05) / g['H']), ncol=1, frameon=False, fontsize=10.5)
fig.savefig(out, dpi=200); print(out)
from PIL import Image, ImageChops
im = Image.open(out).convert('RGB'); b = ImageChops.difference(im, Image.new('RGB', im.size, 'white')).getbbox()
im.crop((max(0, b[0] - 15), max(0, b[1] - 15), min(im.width, b[2] + 15), min(im.height, b[3] + 15))).save(out)
