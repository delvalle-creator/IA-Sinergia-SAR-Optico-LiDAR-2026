# Tp7 Figura 11 (31/10/2026): histogramas de los umbrales, dibujados al tamano final (letras de 10 pt)
import sys, numpy as np, pickle, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
plt.rcParams.update({'font.family': 'Liberation Serif', 'font.size': 10, 'axes.unicode_minus': True})
W, H = float(sys.argv[1]), float(sys.argv[2]); CM = 1/2.54
d = pickle.load(open('datos.pkl', 'rb')); m_ref = pickle.load(open('mref.pkl', 'rb')); nv = pickle.load(open('ndvi_vals.pkl', 'rb'))
def nmad(v): v = v[np.isfinite(v)]; return 1.4826*np.median(np.abs(v-np.median(v)))
coma = FuncFormatter(lambda v, p: ('%g' % v).replace('.', ',').replace('-', '−'))
miles = FuncFormatter(lambda v, p: '{:,.0f}'.format(v).replace(',', '.'))
OR, VE = '#d9822b', '#2a9d8f'
B = {}
for k, (ds, c) in {'X': (d['xd'], d['xc']), 'C': (d['cd'], d['cc'])}.items():
    ok = np.isfinite(ds) & np.isfinite(c) & (c >= .3)
    rel = 1000*(ds - np.nanmedian(ds[ok & m_ref]))
    B[k] = dict(ref=rel[ok & m_ref], lad=rel[ok & d['m_lad']], coh=c[d['m_lad'] & np.isfinite(c)], s=1000*nmad(rel[ok & m_ref]/1000))
fig, axs = plt.subplots(2, 3, figsize=(W*CM, H*CM))
def fmt(ax, xl, yl='píxeles'):
    ax.set_xlabel(xl, labelpad=1); ax.set_ylabel(yl, labelpad=2); ax.xaxis.set_major_formatter(coma); ax.xaxis.set_major_locator(MaxNLocator(5))
    ax.yaxis.set_major_locator(MaxNLocator(3)); ax.yaxis.set_major_formatter(miles); ax.tick_params(length=2.5, pad=1.5)
for j, k in enumerate('XC'):
    ax = axs[0, j]; b = B[k]
    ax.hist(np.clip(b['ref'], -30, 30), bins=90, color='#1f3b73')
    for x, c, ls in ((10, OR, '-'), (-10, OR, '-'), (2*b['s'], VE, '--'), (-2*b['s'], VE, '--')): ax.axvline(x, color=c, ls=ls, lw=1.6)
    ax.set_xlim(-30, 30); ax.set_title('(%s) %s, referencia: NMAD %s' % ('ab'[j], k, ('%.1f' % b['s']).replace('.', ',') + ' mm'), pad=3)
    fmt(ax, 'desplazamiento LOS (mm)')
ax = axs[0, 2]
for k, c in (('X', '#7b2cbf'), ('C', '#2b9348')):
    ax.hist(np.clip(B[k]['lad'], -30, 30), bins=90, histtype='step', lw=1.4, color=c, density=True, label=k)
for x in (10, -10): ax.axvline(x, color=OR, lw=1.6)
ax.set_xlim(-30, 30); ax.set_title('(c) Despl. en la ladera', pad=3); ax.legend(loc='upper right', frameon=False, handlelength=1.2, borderaxespad=0.2)
fmt(ax, 'desplazamiento LOS (mm)', 'densidad'); ax.yaxis.set_major_formatter(coma)
for j, k in enumerate('XC'):
    ax = axs[1, j]; b = B[k]
    ax.hist(b['coh'], bins=60, range=(0, 1), color='#555555'); ax.axvline(0.3, color=OR, lw=1.6); ax.set_ylim(0, ax.get_ylim()[1]*1.3)
    ax.set_title('(%s) %s: coherencia, ladera' % ('de'[j], k), pad=3)
    pc = 100*np.mean((np.nan_to_num(d['xc' if k=='X' else 'cc'])>=.3)[d['m_lad']])
    ax.text(0.97, 0.95, '%s %% ≥ 0,3' % ('%.1f' % pc).replace('.', ','), transform=ax.transAxes, ha='right', va='top', fontsize=10, bbox=dict(fc='white', ec='none', pad=1))
    fmt(ax, 'coherencia'); ax.set_xlim(0, 1)
ax = axs[1, 2]
ax.hist(nv['tal'], bins=60, range=(-0.1, 0.8), color='#4caf50', alpha=0.8, density=True, label='monte')
ax.hist(nv['cla'], bins=60, range=(-0.1, 0.8), color='#c2185b', alpha=0.7, density=True, label='claro')
ax.text(0.02,0.95,'medianas: claro 0,18; talud 0,33',transform=ax.transAxes,va='top',fontsize=9.5) if False else None
ax.axvline(0.30, color=OR, lw=1.6); ax.set_title('(f) NDVI, CBERS-4A', pad=3); ax.set_ylim(0, ax.get_ylim()[1]*1.7)
ax.legend(loc='upper right', frameon=False, handlelength=1.0, borderaxespad=0.1, labelspacing=0.2)
fmt(ax, 'NDVI', 'densidad'); ax.yaxis.set_major_formatter(coma); ax.set_xlim(-0.1, 0.8)
fig.legend(handles=[Line2D([], [], color=OR, lw=1.8, label='umbral usado (±10 mm; coherencia 0,3; NDVI 0,30)'),
                    Line2D([], [], color=VE, lw=1.8, ls='--', label='±2 NMAD del desplazamiento en la referencia')],
           loc='lower center', ncol=2, frameon=False, borderaxespad=0.1)
fig.tight_layout(rect=(0, 0.09, 1, 1), h_pad=0.4, w_pad=0.8)
fig.savefig('Tp7_Figura_11.png', dpi=300); print({k: round(B[k]['s'], 2) for k in B})
