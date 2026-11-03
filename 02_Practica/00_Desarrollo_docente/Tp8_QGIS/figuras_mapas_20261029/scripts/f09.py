exec(open('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp8/comun.py').read())
E9 = (265150, 265550, 6528750, 6529150)


def est(a, p=(2, 98)):
    v = a[np.isfinite(a)]; lo, hi = np.percentile(v, p); return np.clip((a - lo) / (hi - lo), 0, 1)


b8 = leer(G + 'F_BOVRIL_S2_20230910.tif', E9, 7)
hh = leer(SUB + 'F_textura_S_C_10m_todos_sin_corregir.tif', E9, 1); hh[hh <= 0] = np.nan; hh = 10 * np.log10(hh)
fig = plt.figure(figsize=(9.45, 4.6))
a1 = fig.add_axes([0.11, 0.2, 0.34, 0.72]); a2 = fig.add_axes([0.575, 0.2, 0.34, 0.72])
a1.imshow(est(b8), extent=E9, cmap='gray', interpolation='nearest')
a2.imshow(est(hh), extent=E9, cmap='gray', interpolation='nearest')
frame(a1, E9, 100, 1); frame(a2, E9, 100, 1)
a1.set_title('(a) Sentinel-2 B08, 10/09/2023', fontsize=10.5)
a2.set_title('(b) NovaSAR-1 HH (dB), 84 puntos, sin corregir', fontsize=10.5)
for ax in (a1, a2):
    ax.plot(265225, 6528905, marker='+', color='red', ms=18, mew=2.5)
a2.plot(265305, 6528885, marker='x', color='#33ff33', ms=14, mew=3)
a2.annotate('', xy=(265301, 6528886), xytext=(265225, 6528905),
            arrowprops=dict(arrowstyle='-|>', color='yellow', lw=2, mutation_scale=14, shrinkA=0, shrinkB=0))
a2.text(265290, 6528970, 'dx = +80 m\ndy = −20 m', fontsize=10, ha='center', va='center',
        bbox=dict(fc='white', ec='none', alpha=0.85, pad=1.5))
for ax in (a1, a2):
    for l in ax.get_xticklabels():
        pass
barra(fig, a1, 100, '100 m', y=0.035)
norte(fig, a2)
guardar(fig, 'F09.png')
