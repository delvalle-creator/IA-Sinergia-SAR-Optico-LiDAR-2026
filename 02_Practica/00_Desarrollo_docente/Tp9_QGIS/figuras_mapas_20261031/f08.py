import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow, Patch
plt.rcParams['font.family']='Liberation Serif'; FS=11
r=rasterio.open('/mnt/user-data/uploads/CURSOS_CEREGEO_2026/02_Practica/Tp9_Deforestacion/02_Subsets_SNAP_QGIS/C_pila_temporal_20m.tif')
hv26=r.read(5).astype('f4'); hv21=r.read(2).astype('f4'); b=r.bounds; E=(b.left,b.right,b.bottom,b.top)
z=~(np.isfinite(hv26)&np.isfinite(hv21)&(hv26>0)&(hv21>0))
def s(a): return np.clip((a-0.004)/(0.05-0.004),0,1)
rgb=np.dstack([s(hv26),s(hv21),s(hv21)]); rgb[z]=1
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
W,H=7.2,4.6
fig=plt.figure(figsize=(W,H))
h=0.86; w=h*H/W*(E[1]-E[0])/(E[3]-E[2]); ax=fig.add_axes([0.1,0.1,w,h])
ax.imshow(rgb,extent=E,interpolation='nearest'); ax.set_xlim(E[0],E[1]); ax.set_ylim(E[2],E[3])
for a_ in (ax.xaxis,ax.yaxis): a_.set_major_locator(MultipleLocator(10000)); a_.set_major_formatter(FuncFormatter(fk))
ax.tick_params(labelsize=FS,length=3,pad=2); ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS); ax.set_ylabel('Norte (km)',fontsize=FS)
bb=ax.get_position()
# flecha norte arriba a la derecha fuera del mapa
xn=bb.x1+0.04; yt=bb.y1
fig.add_artist(FancyArrow(xn,yt-0.16,0,0.13,width=0.004,head_width=0.02,head_length=0.045,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.025,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
# leyenda al costado
hs=[Patch(fc='#00e5e5',ec='black',lw=0.5,label='Cian: el HV bajó (2026 < 2021)'),Patch(fc='#e00000',ec='black',lw=0.5,label='Rojo: el HV subió (2026 > 2021)'),Patch(fc='#bdbdbd',ec='black',lw=0.5,label='Gris: sin cambio\n(claro = monte, oscuro = lote)')]
fig.legend(handles=hs,loc='center left',bbox_to_anchor=(bb.x1+0.015,bb.y0+bb.height*0.45),fontsize=FS,frameon=False,handlelength=1.4)
# escala horizontal al costado, abajo
L=10000; frac=L/(E[1]-E[0])*bb.width; xs=bb.x1+0.04; ys=bb.y0+0.01; hb=0.02
sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for i in range(2): sa.add_patch(Rectangle((i*0.5,0),0.5,1,fc=['black','white'][i],ec='black',lw=0.8))
fig.text(xs,ys+hb+0.012,'0',ha='center',va='bottom',fontsize=FS); fig.text(xs+frac,ys+hb+0.012,'10 km',ha='center',va='bottom',fontsize=FS)
fig.savefig('Tp9_Figura_08.png',dpi=300,bbox_inches='tight',pad_inches=0.04)
