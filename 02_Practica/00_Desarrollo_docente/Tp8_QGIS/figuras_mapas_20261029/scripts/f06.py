exec(open('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp8/comun.py').read())
FR = SUB + 'F_frecuencia_suelo_desnudo_2023_10m.tif'
CB = G + 'F_BOVRIL_CBERS4A_BOVRIL_20230615_pansharpened_2m.tif'


def clases(ext):
    m = leer(FR, ext, 1)
    c = np.full(m.shape, -1, int)
    ok = (m > -9000) & np.isfinite(m)
    c[ok & (m == 0)] = 0; c[ok & (m >= 1) & (m <= 2)] = 1; c[ok & (m >= 3) & (m <= 5)] = 2; c[ok & (m >= 6)] = 3
    return c


def rgbclases(c, alpha=None):
    out = np.ones(c.shape + (4,))
    for k, col in enumerate(FCOL):
        out[c == k, :3] = matplotlib.colors.to_rgb(col)
    if alpha is not None:
        out[..., 3] = 0; out[c >= 1, 3] = alpha
    return out


def cbers(ext, p=(2, 98), gamma=1.0):
    a = leer(CB, ext, [4, 3, 2])
    m = (a == 0).all(0)
    out = np.zeros(a.shape[1:] + (3,))
    for i in range(3):
        v = a[i][~m]; lo, hi = np.percentile(v, p)
        out[..., i] = np.clip((a[i] - lo) / (hi - lo), 0, 1) ** gamma
    out[m] = 0.5
    return out


if __name__ == '__main__':
    fig = plt.figure(figsize=(9.45, 4.9))
    a1 = fig.add_axes([0.09, 0.27, 0.36, 0.66]); a2 = fig.add_axes([0.575, 0.27, 0.36, 0.66])
    a1.imshow(rgbclases(clases(SITIO)), extent=SITIO, interpolation='nearest')
    a1.add_patch(Rectangle((DET[0], DET[2]), 3000, 3000, fill=False, ec='black', lw=1.5))
    frame(a1, SITIO, 2000, 0); a1.set_title('(a) Meses con suelo desnudo en 2023', fontsize=10.5)
    a2.imshow(cbers(DET), extent=DET, interpolation='nearest')
    a2.imshow(rgbclases(clases(DET), 0.4), extent=DET, interpolation='nearest')
    frame(a2, DET, 500, 1); a2.set_title('(b) Detalle de 3 × 3 km sobre CBERS-4A de 2 m', fontsize=10.5)
    h = [Patch(fc=c, ec='0.3', lw=0.5, label=l) for c, l in zip(FCOL, FLAB)]
    fig.legend(handles=h, loc='lower center', bbox_to_anchor=(0.55, 0.0), ncol=4, frameon=False, fontsize=10)
    barra(fig, a1, 2000, '2 km', y=0.10, etiqueta='(a)')
    barra(fig, a2, 500, '500 m', y=0.10, etiqueta='(b)')
    norte(fig, a2)
    guardar(fig, 'F06.png')
