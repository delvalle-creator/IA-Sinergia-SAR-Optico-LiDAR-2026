"""Reemplaza en el Desarrollo del Tp3 SOLO el binario de las imagenes de los mapas rehechos (29/10/2026) y ajusta
wp:extent y a:ext conservando el ancho actual (cx); alto por la nueva proporcion, tope 15 cm. No toca texto ni estilos.
Uso: python3 reemplazar_en_docx.py ENTRADA.docx CARPETA_FIGURAS SALIDA.docx"""
import re, sys, zipfile, struct
ENT, FIGS, SAL = sys.argv[1], sys.argv[2].rstrip('/\\') + '/', sys.argv[3]
NEW = {3: 'F03', 4: 'F04', 5: 'F05', 7: 'F07', 16: 'F16', 23: 'F23', 24: 'F24', 28: 'F28', 31: 'F31', 32: 'F32', 38: 'F38'}
TOPE = 15 * 360000


def png_wh(b):
    assert b[:8] == b'\x89PNG\r\n\x1a\n'; return struct.unpack('>II', b[16:24])


z = zipfile.ZipFile(ENT)
d = z.read('word/document.xml').decode('utf8')
rels = z.read('word/_rels/document.xml.rels').decode('utf8')
rid = {re.search(r'Id="([^"]+)"', m).group(1): re.search(r'Target="([^"]+)"', m).group(1) for m in re.findall(r'<Relationship [^>]*>', rels)}
b0 = d.find('<w:body>')
spans = [(m.start() + b0, m.end() + b0) for m in re.finditer(r'<w:p(?: [^>]*)?>.*?</w:p>|<w:tbl>.*?</w:tbl>', d[b0:], re.S)]
P = [d[a:b] for a, b in spans]
txt = lambda p: re.sub(r'<[^>]+>', '', p).strip()
usos = {}
for p in P:
    for r in re.findall(r'r:embed="([^"]+)"', p): usos[rid[r]] = usos.get(rid[r], 0) + 1
reemplazos = {}
for n, f in NEW.items():
    ic = [i for i, p in enumerate(P) if re.match(r'Figura %d\.' % n, txt(p))]
    assert len(ic) == 1, (n, ic); ic = ic[0]
    j = ic - 1
    while '<pic:pic' not in P[j]: j -= 1
    assert ic - j <= 2, (n, ic, j)
    p = P[j]; assert p.count('<pic:pic') == 1, n
    tgt = rid[re.search(r'r:embed="([^"]+)"', p).group(1)]
    assert usos[tgt] == 1 and tgt.lower().endswith('.png'), (n, tgt)
    nb = open(FIGS + f + '.png', 'rb').read(); w, h = png_wh(nb)
    cx = int(re.search(r'<wp:extent cx="(\d+)"', p).group(1)); cy = int(round(cx * h / w))
    if cy > TOPE: cy = TOPE; cx = int(round(cy * w / h))
    p2 = re.sub(r'<wp:extent cx="\d+" cy="\d+"/>', '<wp:extent cx="%d" cy="%d"/>' % (cx, cy), p, count=1)
    p2, k = re.subn(r'(<a:xfrm[^>]*>\s*<a:off[^>]*/>\s*)<a:ext cx="\d+" cy="\d+"/>', r'\g<1><a:ext cx="%d" cy="%d"/>' % (cx, cy), p2)
    assert k == 1, n
    P[j] = p2; reemplazos['word/' + tgt] = nb
    print('Figura %d: %s <- %s.png  %.2f x %.2f cm' % (n, tgt, f, cx / 360000, cy / 360000))
out = d[:spans[0][0]]
for k, (a, b) in enumerate(spans):
    out += P[k]; out += d[b:spans[k + 1][0]] if k + 1 < len(spans) else d[b:]
zo = zipfile.ZipFile(SAL, 'w')
for it in z.infolist():
    data = out.encode('utf8') if it.filename == 'word/document.xml' else reemplazos.get(it.filename, None)
    if data is None: data = z.read(it.filename)
    zo.writestr(it, data, compress_type=it.compress_type)
zo.close(); print('escrito', SAL, len(reemplazos), 'imagenes')
