# Reemplaza en Desarrollo_del_Tp5.docx sólo el binario de las imágenes de los mapas rehechos
# y ajusta wp:extent / a:ext conservando el ancho (cx). Salida en /tmp; luego cp sobre el original.
import re, zipfile, sys, os
from PIL import Image
SRC, FIGS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
NEW = [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 16, 17, 24, 25, 29, 30]
z = zipfile.ZipFile(SRC)
d = z.read('word/document.xml').decode('utf8')
rels = z.read('word/_rels/document.xml.rels').decode('utf8')
rid = {re.search(r'Id="([^"]+)"', m).group(1): re.search(r'Target="([^"]+)"', m).group(1)
       for m in re.findall(r'<Relationship [^>]*>', rels)}
b0 = d.find('<w:body>')
spans = [(m.start() + b0, m.end() + b0) for m in re.finditer(r'<w:p(?: [^>]*)?>.*?</w:p>|<w:tbl>.*?</w:tbl>', d[b0:], re.S)]
P = [d[a:b] for a, b in spans]
txt = lambda p: re.sub(r'<[^>]+>', '', p).strip()
rep = {}
for n in NEW:
    ic = [i for i, p in enumerate(P) if txt(p).startswith('Figura %d. ' % n)]
    assert len(ic) == 1, (n, ic)
    j = ic[0] - 1
    while '<pic:pic' not in P[j]: j -= 1
    assert ic[0] - j <= 2, n
    p = P[j]; embeds = re.findall(r'r:embed="([^"]+)"', p); assert len(embeds) == 1, n
    target = 'word/' + rid[embeds[0]]
    assert target.lower().endswith('.png') and target not in rep, (n, target)
    # el medio no debe estar usado por otra imagen
    assert sum(1 for q in re.findall(r'r:embed="([^"]+)"', d) if rid[q] == rid[embeds[0]]) == 1, n
    im = Image.open(os.path.join(FIGS, 'Tp5_F%02d.png' % n))
    cx = int(re.search(r'<wp:extent cx="(\d+)"', p).group(1)); cy = int(cx * im.height / im.width)
    if cy > 15 * 360000:
        cy = 15 * 360000; cx = int(cy * im.width / im.height)
    p2 = re.sub(r'<wp:extent cx="\d+" cy="\d+"/>', '<wp:extent cx="%d" cy="%d"/>' % (cx, cy), p)
    p2, k = re.subn(r'(<a:xfrm[^>]*>\s*<a:off[^>]*/>\s*)<a:ext cx="\d+" cy="\d+"/>', r'\g<1><a:ext cx="%d" cy="%d"/>' % (cx, cy), p2)
    assert k == 1, n
    P[j] = p2; rep[target] = os.path.join(FIGS, 'Tp5_F%02d.png' % n)
    print('Figura %d -> %s  %.1f x %.1f cm' % (n, target, cx / 360000, cy / 360000))
out = d[:spans[0][0]]
for k, (a, b) in enumerate(spans):
    out += P[k]; out += d[b:spans[k + 1][0]] if k + 1 < len(spans) else d[b:]
zo = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
for it in z.infolist():
    if it.filename == 'word/document.xml':
        zo.writestr(it, out.encode('utf8'))
    elif it.filename in rep:
        zo.writestr(it, open(rep[it.filename], 'rb').read())
    else:
        zo.writestr(it, z.read(it.filename))
zo.close(); print('escrito', OUT, len(rep), 'imagenes')
