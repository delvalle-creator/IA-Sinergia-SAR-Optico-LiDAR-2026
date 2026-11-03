# Tp5, Figura 13: serie de 20 pasadas Sentinel-1 VH (orbita 68) y altura del Parana en Rosario.
# Rehecha el 30/10/2026 con letra del tamano del texto (11-12 pt al tamano de impresion, 24 cm de ancho).
# Las alturas del Parana son las lecturas y extremos citados en los informes del INA y de Puertos (ver Fuente).
import sys, csv, datetime as dt, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.dates as mdates
plt.rcParams['font.family'] = 'Liberation Serif'
CSV = sys.argv[1] if len(sys.argv) > 1 else 'A1_serie_VH_sentinel1_2020.csv'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'serie_VH_y_rio_Parana.png'
D = lambda s: dt.datetime.strptime(s, '%Y-%m-%d')
f, nq, q = [], [], []
for r in csv.DictReader(open(CSV)):
    f.append(D(r['t'])); nq.append(float(r['VH_no_quemado_dB'])); q.append(float(r['VH_quemado_ago_sep_dB']))
rio = [('2020-07-16', 1.00), ('2020-07-24', 1.45), ('2020-07-30', 0.90), ('2020-08-17', 0.30), ('2020-08-31', 1.10),
       ('2020-09-10', 1.50), ('2020-09-30', 0.80), ('2020-10-05', 1.40), ('2020-10-07', 1.10)]
prom = [('2020-07-01', '2020-07-31', 1.00), ('2020-08-01', '2020-08-31', 0.62), ('2020-09-01', '2020-09-30', 1.14)]
sens = [('2020-07-15', 'S2'), ('2020-07-16', 'S1'), ('2020-07-21', 'SC'), ('2020-09-26', 'S1'), ('2020-10-13', 'S2'), ('2020-10-25', 'SC')]
CM = 1 / 2.54
fig, (a, b) = plt.subplots(2, 1, figsize=(24 * CM, 13.0 * CM), sharex=True, gridspec_kw=dict(height_ratios=[2.2, 1], hspace=0.12))
fig.subplots_adjust(left=0.085, right=0.985, top=0.86, bottom=0.215)
a.plot(f, nq, '-o', color='#2e7d40', ms=4, lw=1.6, label='no quemado en 2020 (MapBiomas Fuego)')
a.plot(f, q, '-s', color='#c0392b', ms=4, lw=1.6, label='quemado en agosto y septiembre')
for s in ('2020-06-16', '2020-09-02', '2020-09-26', '2020-10-20', '2020-10-26'):
    i = f.index(D(s)); a.annotate(D(s).strftime('%d/%m'), (f[i], nq[i]), xytext=(0, 5), textcoords='offset points', ha='center', fontsize=11)
a.set_ylim(-24, -12); a.set_yticks(range(-24, -11, 2)); a.set_ylabel(r'$\gamma^{0}$ VH (dB)', fontsize=12)
a.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: ('%g' % v).replace('-', '−')))
for d_, t in sens:
    for ax in (a, b): ax.axvline(D(d_), color='0.4', ls=':', lw=1)
etq = [('2020-07-13 12', 'S2 · S1'), ('2020-07-22 12', 'SC'), ('2020-09-26', 'S1'), ('2020-10-13', 'S2'), ('2020-10-25', 'SC')]
for d_, t in etq:
    x = dt.datetime.strptime(d_, '%Y-%m-%d %H') if ' ' in d_ else D(d_)
    a.text(x, -11.75, t, ha='center', va='bottom', fontsize=11, color='0.3')
b.axvspan(D('2020-08-29'), D('2020-09-02'), color='#7fb3d5', alpha=0.5, label='lluvia de fines de agosto (más de 35 mm en Rosario)')
b.plot([D(x) for x, _ in rio], [v for _, v in rio], '-o', color='#1f4e9c', ms=4, lw=1.6, label='Paraná en Rosario: lecturas y extremos citados')
for i, (x0, x1, v) in enumerate(prom):
    b.plot([D(x0), D(x1)], [v, v], color='#a9bfdc', lw=3.5, label='promedio mensual' if i == 0 else None)
b.set_ylim(0, 1.9); b.set_yticks([0, 0.5, 1, 1.5]); b.set_ylabel('altura (m)', fontsize=12)
b.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: ('%.1f' % v).replace('.', ',')))
b.xaxis.set_major_locator(mdates.MonthLocator()); b.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
b.set_xlim(D('2020-06-10'), D('2020-10-31'))
for ax in (a, b):
    ax.tick_params(labelsize=11); ax.grid(alpha=0.3)
h1, l1 = a.get_legend_handles_labels(); h2, l2 = b.get_legend_handles_labels()
fig.legend(h1, l1, loc='upper center', bbox_to_anchor=(0.53, 1.0), ncol=2, frameon=False, fontsize=11)
fig.legend(h2, l2, loc='lower center', bbox_to_anchor=(0.53, 0.0), ncol=2, frameon=False, fontsize=11)
fig.savefig(OUT, dpi=220); print(OUT)
