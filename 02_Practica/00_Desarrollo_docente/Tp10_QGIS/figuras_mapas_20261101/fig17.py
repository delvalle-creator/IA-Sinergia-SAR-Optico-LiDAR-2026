import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
plt.rcParams['font.family']='Liberation Serif'
df=pd.read_csv('/mnt/user-data/uploads/02_Practica/Tp10_Impacto_urbano/08_Orange/datos/Tp10_C_pixeles_velocidad.csv')
order=['24 Areas urbanas','3 Bosques cerrados','4 Bosques abiertos','15 Pastura','19 Cultivos temporarios','12 Herbaceas','11 Herbaceas inundables','25 Otras areas no vegetadas']
nom={'24 Areas urbanas':'24 Áreas urbanas','12 Herbaceas':'12 Herbáceas','11 Herbaceas inundables':'11 Herbáceas inundables','25 Otras areas no vegetadas':'25 Otras áreas no vegetadas'}
print(df.MapBiomas_2025.value_counts())
data=[df.loc[df.MapBiomas_2025==c,'velocidad_mm_ano'].values for c in order]
for c,d in zip(order,data): print(c,len(d),np.median(d),np.percentile(d,(25,75)))
FS=12
fig,ax=plt.subplots(figsize=(9.2,4.6))
bp=ax.boxplot(data[::-1],orientation='horizontal',whis=1.5,showfliers=False,widths=0.6,medianprops=dict(color='#d35400',lw=2.5),boxprops=dict(lw=1),whiskerprops=dict(lw=1),capprops=dict(lw=1))
lab=[f'{nom.get(c,c)} (n = {len(d):,})'.replace(',','.') for c,d in zip(order,data)][::-1]
ax.set_yticks(range(1,len(order)+1)); ax.set_yticklabels(lab,fontsize=FS)
ax.axvline(0,color='black',lw=0.8); ax.set_xlim(-75,35); ax.grid(axis='x',alpha=0.3)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v,_: f'{v:.0f}'.replace('-','−'))); ax.tick_params(axis='x',labelsize=FS)
ax.set_xlabel('Velocidad vertical (mm/año)\ncajas de 25 a 75 %, bigotes hasta 1,5 veces el rango intercuartil, sin valores extremos',fontsize=FS)
fig.tight_layout(); fig.savefig('Tp10_Figura_17.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
