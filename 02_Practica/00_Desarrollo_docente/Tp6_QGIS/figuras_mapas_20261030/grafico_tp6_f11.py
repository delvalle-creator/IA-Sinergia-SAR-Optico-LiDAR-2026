# Tp6, Figura 11: agua de inundacion en banda C por fecha (orbita 68), oct-2023 a jun-2024, desde la tabla
# Tp6_C_serie_agua.csv (salida de Tp6_01_serie_agua_C.py). Fechas de cobertura parcial con cruz. Lineas: fecha del
# umbral (04/11/2023) y alturas del rio publicadas (02/12/2023 y 12/05/2024). Letras Times a tamano de texto. 30/10/2026.
# Uso: python grafico_tp6_f11.py <Tp6_C_serie_agua.csv> <salida.png>
import sys, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
plt.rcParams['font.family'] = 'Liberation Serif'
f, out = sys.argv[1:3]
d = pd.read_csv(f, parse_dates=['fecha'])
CM = 1 / 2.54
miles = FuncFormatter(lambda v, _: '{:,.0f}'.format(v).replace(',', '.'))
fig = plt.figure(figsize=(25.0 * CM, 9.0 * CM))
ax = fig.add_axes([2.3 / 25, 1.75 / 9, 22.2 / 25, 7.05 / 9])
c = d[d.cobertura == 'completa']; p = d[d.cobertura != 'completa']
ax.plot(c.fecha, c.agua_temporal_ha, '-o', color='#1f3a73', lw=1.6, ms=6, label='Fecha con el sitio completo')
ax.plot(p.fecha, p.agua_temporal_ha, 'x', color='#d62728', ms=9, mew=2.2, ls='none', label='Fecha con 2 a 20 % del sitio (un solo cuadro)')
for x, t, ha, dx in [('2023-11-04', '04/11/2023:\nS1 y S2 del\nmismo día', 'left', 2), ('2023-12-02', '02/12/2023: 13,44 m\nen el puerto (medida)', 'left', 2),
                     ('2024-05-12', '12/05/2024: 13,7 m\nen el puerto (medida)', 'right', -2)]:
    xd = pd.Timestamp(x); ax.axvline(xd, color='gray', ls='--', lw=1.2)
    y = 1450 if x == '2023-11-04' else 4780
    ax.text(xd + pd.Timedelta(days=dx), y, t, ha=ha, va='top', fontsize=10.5)
ax.set_ylim(0, 4900); ax.set_xlim(pd.Timestamp('2023-09-28'), pd.Timestamp('2024-07-03'))
ax.yaxis.set_major_formatter(miles); ax.set_ylabel('Agua de inundación (ha)', fontsize=11)
ax.xaxis.set_major_locator(mdates.MonthLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
ax.tick_params(labelsize=10.5); ax.grid(alpha=0.3, lw=0.5)
fig.legend(loc='lower center', ncol=2, fontsize=10.5, frameon=False, bbox_to_anchor=(0.5, 0.0))
fig.savefig(out, dpi=220); plt.close(fig)
