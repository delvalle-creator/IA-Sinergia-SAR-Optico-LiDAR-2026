import matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
plt.rcParams['font.family']='Liberation Serif'
A=[('C sola',0.375,0.138),('Óptico solo',0.245,0.122),('Multisensor',0.143,0.099),('C + L',0.102,0.086)]
B=[('C sola',0.160,0.147),('Óptico solo',0.111,0.121),('Multisensor',0.105,0.099),('C + L',0.086,0.094),('Multisensor con S',0.060,0.066)]
FS=12; f=FuncFormatter(lambda v,_: f'{v:.1f}'.replace('.',','))
fig,axs=plt.subplots(1,2,figsize=(9.6,3.1))
for ax,D,t in ((axs[0],A,'(a) Todo el sitio (142 puntos por variante)'),(axs[1],B,'(b) Huella de NovaSAR (Tp10_06, dominio)')):
    for i,(n,v,e) in enumerate(D):
        c='#d35400' if n=='Multisensor con S' else '#1f3b73'
        ax.errorbar(v,i,xerr=e,fmt='o',color=c,ms=7,capsize=4,lw=1.4)
        ax.text(v,i+0.22,f'{v:.3f}'.replace('.',','),ha='center',va='bottom',fontsize=FS-1)
    ax.set_yticks(range(len(D))); ax.set_yticklabels([d[0] for d in D],fontsize=FS); ax.set_ylim(-0.6,len(D)-0.25)
    ax.set_xlim(-0.05,0.55); ax.xaxis.set_major_formatter(f); ax.tick_params(axis='x',labelsize=FS); ax.grid(axis='x',alpha=0.3)
    ax.set_xlabel('Comisión de la clase urbano (IC del 95 %)',fontsize=FS); ax.set_title(t,fontsize=FS,pad=4); ax.axvline(0,color='0.5',lw=0.6)
fig.tight_layout(w_pad=2); fig.savefig('Tp10_Figura_19.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
