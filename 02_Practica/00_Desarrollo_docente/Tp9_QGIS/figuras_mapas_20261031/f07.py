import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
plt.rcParams['font.family']='Liberation Serif'; FS=11
med={'m':[1.77,-1.64,-1.60],'c':[1.63,-1.40,-0.45],'t':[1.74,-1.59,-1.13]}
iqr={'m':[(0.70,2.63),(-3.09,-0.47),(-2.95,0.09)],'c':[(0.03,2.85),(-3.60,0.49),(-2.53,1.38)],'t':[(0.39,2.68),(-3.27,-0.03),(-2.85,0.62)]}
lab={'m':'Monte confirmado (14 cuadrados)','c':'Ciudad (12 cuadrados)','t':'Las dos zonas (lo que aplica Tp9_01)'}
col={'m':'#1b9e4b','c':'#7b3294','t':'#555555'}
fig,ax=plt.subplots(figsize=(16/2.54,6.6/2.54))
x=np.arange(3); w=0.26
for k,(z,off) in enumerate(zip('mct',(-w,0,w))):
    y=np.array(med[z]); lo=np.array([a for a,b in iqr[z]]); hi=np.array([b for a,b in iqr[z]])
    ax.bar(x+off,y,w,color=col[z],label=lab[z],edgecolor='black',lw=0.4)
    ax.errorbar(x+off,y,yerr=[y-lo,hi-y],fmt='none',ecolor='black',elinewidth=0.8,capsize=2.5)
ax.axhline(0,color='black',lw=0.6); 
for v in (-1,1): ax.axhline(v,color='gray',lw=0.7,ls=':')
ax.set_xticks(x); ax.set_xticklabels(['ALOS-1 HH 2011','NISAR HH 2026','NISAR HV 2026'],fontsize=FS)
ax.set_ylabel('Desfase respecto de\nALOS-2 2021 (dB)',fontsize=FS); ax.tick_params(labelsize=FS)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f'{v:+g}'.replace('-','−') if v else '0'))
ax.set_ylim(-4,3.2)
ax.legend(fontsize=FS-1,loc='upper left',bbox_to_anchor=(1.01,1),frameon=False)
for s in ('top','right'): ax.spines[s].set_visible(False)
fig.savefig('Tp9_Figura_07.png',dpi=300,bbox_inches='tight',pad_inches=0.04)
