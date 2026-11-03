import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap
from rasterio.windows import from_bounds
plt.rcParams['font.family']='Liberation Serif'
U='/mnt/user-data/uploads/02_Practica/'
Z=(396000,412000,6520000,6534000); FS=12
s=rasterio.open(U+'00_COMUN/09_Herramientas/desarrollo_docente/Tp10/B_CONCORDIA_S2_20260904_10m.tif')
w=from_bounds(Z[0],Z[2],Z[1],Z[3],s.transform)
s2=np.stack([s.read(b,window=w) for b in (3,2,1)]).astype('f4'); s2=np.clip((s2-0.0128)/(0.1455-0.0128),0,1).transpose(1,2,0)
s2=0.55*s2+0.45  # aclarado para que se lean las clases
e=rasterio.open(U+'Tp10_Impacto_urbano/05_Resultados/02_Rasters/B_CONCORDIA_expansion_2019_2026.tif')
we=from_bounds(Z[0],Z[2],Z[1],Z[3],e.transform); c=e.read(1,window=we)
lut=np.full(7,np.nan); lut[1]=0; lut[2]=1; lut[4]=2; lut[5]=3
ci=np.where((c>=1)&(c<=5),lut[np.clip(c,0,6).astype(int)],np.nan)
cols=['#6e6e6e','#e00000','#1f6fe0','#ffd21f']; cm=ListedColormap(cols)
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
W=9.6; H=4.6
fig=plt.figure(figsize=(W,H))
ha=0.74; y0=0.17; wz=ha*H/W*(Z[1]-Z[0])/(Z[3]-Z[2])
ax=fig.add_axes([0.075,y0,wz,ha]); ax.imshow(s2,extent=Z,interpolation='nearest'); ax.imshow(ci,extent=Z,cmap=cm,vmin=-0.5,vmax=3.5,interpolation='nearest')
for lab,(x,y) in (('B',(399655,6528919)),('C',(410846,6524786))):
    ax.add_patch(Rectangle((x-300,y-300),600,600,fill=False,ec='black',lw=1.4))
    ax.text(x+350,y+350,lab,fontsize=FS,fontweight='bold',bbox=dict(fc='white',ec='black',lw=0.6,pad=1.5))
ax.set_xlim(Z[0],Z[1]); ax.set_ylim(Z[2],Z[3]); ax.set_xticks([400000,404000,408000]); ax.set_yticks([6522000,6526000,6530000])
ax.xaxis.set_major_formatter(FuncFormatter(fk)); ax.yaxis.set_major_formatter(FuncFormatter(fk)); ax.tick_params(labelsize=FS)
ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS); ax.set_ylabel('Norte (km)',fontsize=FS)
ax.set_title('(a) Concordia y Salto sobre Sentinel-2 del 04/09/2026',fontsize=FS,pad=4)
b=ax.get_position()
xn=b.x1+0.03; yt=b.y1
fig.add_artist(FancyArrow(xn,yt-0.17,0,0.13,width=0.0025,head_width=0.014,head_length=0.04,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.03,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
L=4000; frac=L/(Z[1]-Z[0])*wz; xs=b.x0+(b.width-frac)/2; ys=0.0; hb=0.022
sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for q in range(2): sa.add_patch(Rectangle((q*0.5,0),0.5,1,fc=['black','white'][q],ec='black',lw=0.8))
fig.text(xs-0.006,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(xs+frac+0.006,ys+hb/2,'4 km',ha='left',va='center',fontsize=FS)
# (b) barras
bx=fig.add_axes([b.x1+0.13,y0+0.33,0.30,ha-0.33])
v=[4360.7,38.6,11.0,2510.2]; et=['1','2','4','5']
bars=bx.bar(range(4),v,color=cols,edgecolor='black',lw=0.6)
for i,val in enumerate(v): bx.text(i,val+90,f'{val:,.1f}'.replace(',','X').replace('.',',').replace('X','.'),ha='center',va='bottom',fontsize=FS-1)
bx.set_xticks(range(4)); bx.set_xticklabels(et,fontsize=FS); bx.set_xlabel('Clase',fontsize=FS); bx.set_ylabel('Superficie (ha)',fontsize=FS)
bx.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f'{v:,.0f}'.replace(',','.'))); bx.tick_params(labelsize=FS); bx.set_ylim(0,5200)
bx.set_title('(b) Superficie por clase',fontsize=FS,pad=4); bx.spines[['top','right']].set_visible(False)
labs=['1 urbano en las dos fechas','2 nuevo urbano','4 urbano sólo en 2019 (revisar)','5 sin decidir']
fig.legend(handles=[Patch(fc=c,ec='0.3',lw=0.5,label=l) for c,l in zip(cols,labs)]+[Patch(fc='white',ec='0.3',lw=0.5,label='3 no urbano (sin color en a)')],
           loc='upper left',bbox_to_anchor=(b.x1+0.075,y0+0.235),fontsize=FS-1,frameon=False,handlelength=1.3,labelspacing=0.25)
fig.text(b.x1+0.085,y0-0.155,'B y C: manchas de la clase 2 de la Figura 14\n(A queda al este del recorte).',fontsize=FS-1,va='bottom')
fig.savefig('Tp10_Figura_13.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
