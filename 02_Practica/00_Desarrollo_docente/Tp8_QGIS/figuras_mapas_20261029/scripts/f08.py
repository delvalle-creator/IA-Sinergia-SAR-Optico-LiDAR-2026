exec(open('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp8/comun.py').read())
import sys
from scipy import ndimage as ndi
E8 = (264700, 266700, 6527900, 6529900)
SIG = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
PCT = float(sys.argv[2]) if len(sys.argv) > 2 else 80


def bordes(a, sig=SIG, pct=PCT):
    a = np.where(np.isfinite(a), a, np.nanmedian(a))
    s = ndi.gaussian_filter(a, sig)
    m = np.hypot(ndi.sobel(s, 0), ndi.sobel(s, 1))
    return m > np.percentile(m, pct)


b8 = leer(G + 'F_BOVRIL_S2_20230910.tif', E8, 7)
eo = bordes(b8)
fig = plt.figure(figsize=(9.45, 3.95))
xs = [0.085, 0.395, 0.705]; axs = [fig.add_axes([x, 0.28, 0.255, 0.255 * 9.45 / 3.95]) for x in xs]
tit = ['(a) 4 esquinas, sin corregir', '(b) 84 puntos de enlace, sin corregir', '(c) 84 puntos de enlace y −80 m, +20 m']
fs = ['F_textura_S_C_10m_esquinas_sin_corregir.tif', 'F_textura_S_C_10m_todos_sin_corregir.tif', 'F_textura_S_C_10m.tif']
for k, (ax, f, t) in enumerate(zip(axs, fs, tit)):
    hh = leer(SUB + f, E8, 1); hh[hh <= 0] = np.nan; hh = 10 * np.log10(hh)
    es = bordes(hh)
    im = np.zeros(eo.shape + (3,)); im[:] = 0.13
    im[eo & ~es] = (1, 0, 0); im[es & ~eo] = (0, 1, 0); im[es & eo] = (1, 1, 0)
    ax.imshow(im, extent=E8, interpolation='nearest')
    frame(ax, E8, 500, 1, left=k == 0)
    ax.set_title(t, fontsize=10.5)
h = [Patch(fc=c, label=l) for c, l in (('red', 'Bordes de Sentinel-2 B08'), ('lime', 'Bordes de NovaSAR-1 HH'), ('yellow', 'Coinciden'))]
fig.legend(handles=h, loc='lower center', bbox_to_anchor=(0.6, 0.0), ncol=3, frameon=False, fontsize=10)
barra(fig, axs[0], 500, '500 m', y=0.045)
norte(fig, axs[2], dx=0.02)
guardar(fig, 'F08.png')
