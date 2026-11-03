exec(open('/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp8/f06.py').read().split("if __name__")[0])
LOT = (265150, 265950, 6528950, 6529750)
fs = 9
fig = plt.figure(figsize=(3.6, 3.65))
ax = fig.add_axes([0.2, 0.235, 0.68, 0.68 * 3.6 / 3.65])
ax.imshow(cbers(LOT), extent=LOT, interpolation='nearest')
frame(ax, LOT, 200, 1, fs=fs)
for txt, xt, xy in (('bajo', (265804, 6529595), (265717, 6529436)), ('reguero', (265279, 6529425), (265348, 6529296)),
                    ('reguero', (265664, 6529190), (265625, 6529348)), ('reguero', (265459, 6529020), (265403, 6529159))):
    ax.annotate(txt, xy=xy, xytext=xt, fontsize=fs, ha='center', va='center',
                bbox=dict(fc='white', ec='none', alpha=0.85, pad=1.2),
                arrowprops=dict(arrowstyle='-|>', color='yellow', lw=1.8, mutation_scale=10, shrinkA=6, shrinkB=0))
barra(fig, ax, 100, '100 m', y=0.05, fs=fs)
norte(fig, ax, dx=0.05, largo=0.11, fs=fs + 1, hw=0.035, hl=0.03)
guardar(fig, 'F14.png')
