# Tp5, Figura 26: fichas de 400 m del etiquetado al azar (Sentinel-2 B12-B8A-B4, 15/07 y 13/10/2020);
# cuadrado amarillo = pixel de 20 m. Rehecha el 30/10/2026 con rotulos del tamano del texto.
# Uso: python fig26_fichas_etiquetado_Tp5.py <mapas_tp5.py> <S2_20200715.tif> <S2_20201013.tif> <etiquetas_711_puntos_con_MapBiomas.csv> <salida.png>
import sys, csv, importlib.util
mp, f1, f2, ce, out = sys.argv[1:6]
sys.argv = ['x', 'NINGUNA']
spec = importlib.util.spec_from_file_location('m', mp); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
E = {r['ficha']: r for r in csv.DictReader(open(ce, encoding='utf-8-sig'))}
ids = ['F005', 'F009', 'F010', 'F012', 'F006', 'F008', 'F015', 'F002', 'F007', 'F016', 'F004', 'F001']
ET = {'1': 'quemado', '2': 'no quemado'}; CF = {'a': 'alta', 'm': 'media', 'b': 'baja'}
CM = 1 / 2.54
fig = plt.figure(figsize=(25 * CM, 12.6 * CM))
cw, ch = 0.108, 0.226; gx = 0.006; gp_ = 0.026
for k, i in enumerate(ids):
    r, c = divmod(k, 4); e = E[i]
    x, y = float(e['x']), float(e['y']); ext = (x - 200, x + 200, y - 200, y + 200)
    x0 = 0.017 + c * (2 * cw + gx + gp_); y0 = 1 - (r + 1) * (ch + 0.085) + 0.02
    for j, (f, t) in enumerate(((f1, '15/07'), (f2, '13/10'))):
        ax = fig.add_axes([x0 + j * (cw + gx), y0, cw, ch])
        ax.imshow(m.s2(f, ext, 10), extent=ext, interpolation='nearest')
        ax.add_patch(Rectangle((x - 10, y - 10), 20, 20, fill=False, ec='yellow', lw=1.8))
        ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(t, fontsize=10, pad=2)
    fig.text(x0 + cw + gx / 2, y0 - 0.012, '%s: %s, conf. %s' % (i, ET[e['bin']], CF[e['conf']]), ha='center', va='top', fontsize=10.5)
fig.savefig(out, dpi=200)
from PIL import Image, ImageChops
im = Image.open(out).convert('RGB'); b = ImageChops.difference(im, Image.new('RGB', im.size, 'white')).getbbox()
im.crop((max(0, b[0] - 10), max(0, b[1] - 10), min(im.width, b[2] + 10), min(im.height, b[3] + 10))).save(out); print(out)
