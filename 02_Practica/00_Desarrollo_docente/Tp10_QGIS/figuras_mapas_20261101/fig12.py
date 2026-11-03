import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
plt.rcParams['font.family']='Liberation Serif'
df=pd.read_csv('/mnt/user-data/uploads/02_Practica/Tp10_Impacto_urbano/08_Orange/datos/Tp10_A_pixeles_entrenamiento.csv')
print(df.clase.value_counts().to_dict())
FS=12
CL=[('1','urbano','#c00000'),('2','vegetación leñosa','#1b6e2a'),('3','herbáceas y cultivos','#9ccc4a'),('4','agua','#3a6fd8'),('5','suelo desnudo y otras','#e0a040')]
neg=FuncFormatter(lambda v,_: f'{v:.0f}'.replace('-','−'))
fig,ax=plt.subplots(figsize=(8.6,4.3))
h=[]
for c,l,col in CL:
    s=df[df.clase.str.startswith(c+' ')]
    ax.scatter(s.C_VV_dB,s.L_HH_dB,s=10,c=col,alpha=0.65,edgecolors='none')
    mx,my=s.C_VV_dB.median(),s.L_HH_dB.median()
    lab=f'{l}\n(medianas {mx:.1f} y {my:.1f} dB)'.replace('.',',').replace('-','−')
    h.append(Line2D([],[],ls='',marker='o',ms=8,mfc=col,mec='none',label=lab)); print(lab)
ax.axhline(0,color='black',ls='--',lw=0.9); ax.text(-24.5,0.6,'umbral de L HH: 0 dB',fontsize=FS-1)
ax.set_xlabel('C VV, compuesto Sentinel-1 (dB)',fontsize=FS); ax.set_ylabel('L HH, NISAR (dB)',fontsize=FS)
ax.tick_params(labelsize=FS); ax.xaxis.set_major_formatter(neg); ax.yaxis.set_major_formatter(neg); ax.grid(alpha=0.25)
ax.legend(handles=h,loc='upper left',bbox_to_anchor=(1.01,1.0),fontsize=FS-1,frameon=False,handletextpad=0.3,labelspacing=0.9)
fig.tight_layout(); fig.savefig('Tp10_Figura_12.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
