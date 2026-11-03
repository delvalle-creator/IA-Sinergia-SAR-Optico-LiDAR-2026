import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
plt.rcParams['font.family']='Liberation Serif'
r=rasterio.open('/mnt/user-data/uploads/02_Practica/Tp10_Impacto_urbano/02_Subsets_SNAP_QGIS/B_CONCORDIA_urbano_por_banda_20m.tif')
FS=12
P=[(1,'(a) Banda C, VV (Sentinel-1)','#1f4e9f',-6),(3,'(b) Banda S, HH (NovaSAR-1)','#2e7d32',-3),(4,'(c) Banda L, HH (NISAR)','#8b1e1e',0)]
fig,axs=plt.subplots(1,3,figsize=(8.9,3.2),sharey=False)
neg=FuncFormatter(lambda v,_: f'{v:.0f}'.replace('-','−'))
for ax,(b,t,c,u) in zip(axs,P):
    a=r.read(b); a=a[np.isfinite(a)&(a>0)]; db=10*np.log10(a)
    lo,hi=np.percentile(db,(0.5,99.5)); v=db[(db>=lo)&(db<=hi)]
    pct=(db>u).mean()*100
    ax.hist(v,bins=150,color=c); ax.axvline(u,color='#ff8c00',lw=2)
    ax.set_title(t,fontsize=FS,pad=4); ax.set_xlabel('Retrodispersión (dB)',fontsize=FS)
    ax.tick_params(labelsize=FS); ax.xaxis.set_major_formatter(neg); ax.set_yticks([])
    ax.set_ylim(0,ax.get_ylim()[1]*1.38); ax.text(0.03,0.96,f'umbral {u:.0f} dB\n{pct:.1f} % por encima'.replace('.',',').replace('-','−'),transform=ax.transAxes,ha='left',va='top',fontsize=FS-1,
            bbox=dict(fc='white',ec='0.6',lw=0.6,pad=2.5))
    print(t,round(pct,2))
axs[0].set_ylabel('Píxeles',fontsize=FS)
fig.tight_layout(w_pad=1.2)
fig.savefig('Tp10_Figura_05.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
