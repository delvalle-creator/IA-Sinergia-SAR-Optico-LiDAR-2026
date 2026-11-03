import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.dates as mdates
from matplotlib.lines import Line2D
plt.rcParams['font.family']='Liberation Serif'
t=pd.read_csv('/mnt/user-data/uploads/02_Practica/Tp10_Impacto_urbano/05_Resultados/04_Tablas/E_PARANA_DIAMANTE_red_sbas.csv')
D=sorted(set(t.fecha_1)|set(t.fecha_2)); pos={D[0]:0.0}
E=[(r.fecha_1,r.fecha_2,abs(r.base_perpendicular_m)) for r in t.itertuples()]
for d in D[1:]:
    known=[(a if b==d else b, bp) for a,b,bp in E if (b==d and a in pos) or (a==d and b in pos)]
    best=None
    for s0 in (1,-1):
        o,bp0=known[0]; c=pos[o]+s0*bp0; err=sum(abs(abs(c-pos[o2])-bp) for o2,bp in known)
        if best is None or err<best[0]: best=(err,c)
    pos[d]=best[1]
ap=t[t.apto=='si'].sort_values(['fecha_1','fecha_2']); used=ap[ap.fecha_2<='2026-07-03']; rest=ap[ap.fecha_2>'2026-07-03']; no=t[t.apto=='no']
print(len(used),len(rest),len(no))
FS=12; dt=lambda s: pd.to_datetime(s)
fig,ax=plt.subplots(figsize=(9.6,3.35))
for df,kw in ((no,dict(color='0.55',ls='--',lw=0.8)),(used,dict(color='#1f3b73',lw=1.0)),(rest,dict(color='#e07b00',lw=1.8))):
    for r in df.itertuples(): ax.plot([dt(r.fecha_1),dt(r.fecha_2)],[pos[r.fecha_1],pos[r.fecha_2]],**kw)
ax.plot([dt(d) for d in D[1:]],[pos[d] for d in D[1:]],'o',color='black',ms=4.5,zorder=5)
ax.plot(dt(D[0]),0,'o',mfc='white',mec='#d00000',mew=1.6,ms=8,zorder=6)
ax.axvline(dt('2026-07-03'),color='#e07b00',ls=':',lw=1)
ax.set_ylabel('Base perpendicular relativa\nal 20/05/2025 (m)',fontsize=FS); ax.set_xlabel('Fecha de adquisición',fontsize=FS)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1,4,7,10]))
M={1:'ene.',4:'abr.',7:'jul.',10:'oct.'}
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"{M[mdates.num2date(v).month]} {mdates.num2date(v).year}"))
ax.tick_params(labelsize=FS); ax.grid(alpha=0.25); ax.set_ylim(-30,480)
h=[Line2D([],[],color='#1f3b73',lw=1.2,label='120 pares usados (01/06/2025 a 03/07/2026)'),Line2D([],[],color='#e07b00',lw=2,label='14 pares aptos que no entraron (posteriores al 03/07/2026)'),
   Line2D([],[],color='0.55',ls='--',lw=1,label='20 pares no aptos (más de 48 días o de 150 m)'),Line2D([],[],ls='',marker='o',color='black',ms=5,label='59 fechas de adquisición'),
   Line2D([],[],ls='',marker='o',mfc='white',mec='#d00000',mew=1.6,ms=8,label='20/05/2025: sin par apto')]
ax.legend(handles=h,loc='upper center',bbox_to_anchor=(0.5,-0.24),ncol=2,fontsize=FS-1,frameon=False,columnspacing=1.5)
fig.savefig('Tp10_Figura_15.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
