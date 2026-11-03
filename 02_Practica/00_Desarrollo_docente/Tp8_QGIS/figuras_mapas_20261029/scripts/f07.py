exec(open('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp8/f06.py').read().split("if __name__")[0])
ESTR = None
import json
from scipy import ndimage as ndi
from skimage import measure
C = json.load(open('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp8/centros7.json'))
fs = 8.5
W, H = 7.0, 3.3
fig = plt.figure(figsize=(W, H))
pw = 0.162; ph = pw * W / H; gx = 0.0335; x0 = 0.012
ys = [0.93 - ph, 0.93 - ph - 0.075 - ph]
axs = []
for k, (cx, cy, L) in enumerate(C):
    i, j = (0, k) if k < 5 else (1, k - 5)
    ax = fig.add_axes([x0 + j * (pw + gx), ys[i], pw, ph]); axs.append(ax)
    ext = (cx - L / 2, cx + L / 2, cy - L / 2, cy + L / 2)
    img = cbers(ext)
    ax.imshow(img, extent=ext, interpolation='nearest')
    # contorno de la mancha (6 o mas meses) o del lote (1 a 2 meses) que contiene el centro
    E2 = (ext[0] - 200, ext[1] + 200, ext[2] - 200, ext[3] + 200)
    c = clases(E2); cl = 3 if L == 240 else 1
    lab, n = ndi.label(c == cl, structure=ESTR)
    ny, nx = lab.shape
    yy, xx = np.mgrid[0:ny, 0:nx]
    X = E2[0] + (xx + 0.5) * 10; Yc = E2[3] - (yy + 0.5) * 10
    d = np.where(lab > 0, np.hypot(X - cx, Yc - cy), 1e9)
    comp = lab[np.unravel_index(np.argmin(d), d.shape)]
    m = (lab == comp)
    area = m.sum() * 0.01 + 1e-6
    col = 'red' if cl == 3 else 'darkorange'
    for ct in measure.find_contours(np.pad(m, 1).astype(float), 0.5):
        ax.plot(E2[0] + (ct[:, 1] - 1 + 0.5) * 10, E2[3] - (ct[:, 0] - 1 + 0.5) * 10, color=col, lw=1.3)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(('6 o más meses: %.1f ha' if cl == 3 else '1 a 2 meses: %.1f ha') % area, fontsize=fs, pad=3)
    ax.title.set_text(ax.title.get_text().replace('.', ','))
    if (img == 0.5).all(-1).mean() > 0.2:
        ax.text(cx, cy - L * 0.3, 'fuera de la escena\nCBERS-4A', ha='center', va='center', fontsize=fs - 0.5,
                bbox=dict(fc='white', ec='none', alpha=0.85, pad=1))
    print(k, cx, cy, L, area)
fig.text(x0 + 4 * (pw + gx), ys[1] + ph * 0.5,
         'Contorno rojo: mancha\nde 6 o más meses.\nContorno naranja: lote\nde 1 a 2 meses.\n'
         'Recuadros: 240 × 240 m\n(6 o más meses) y\n600 × 600 m (1 a 2).\nNorte arriba en todos\nlos recuadros.',
         fontsize=fs, va='center', ha='left', linespacing=1.2)
yb = ys[1] - 0.115
barra(fig, axs[5], 100, '100 m', y=yb, fs=fs, h=0.018)
barra(fig, axs[6], 200, '200 m', y=yb, fs=fs, h=0.018)
for ax, t in ((axs[5], 'Recuadros de 240 × 240 m'), (axs[6], 'Recuadros de 600 × 600 m')):
    b = ax.get_position()
    fig.text(b.x0, yb - 0.012, t, fontsize=fs, ha='left', va='top')
norte(fig, axs[4], dx=0.017, largo=0.16, fs=fs + 1.5, hw=0.022, hl=0.045)
guardar(fig, 'F07.png')
