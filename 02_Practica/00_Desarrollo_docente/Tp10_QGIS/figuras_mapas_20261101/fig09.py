import numpy as np, rasterio, geopandas as gpd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow
from matplotlib.lines import Line2D
from rasterio.windows import from_bounds
plt.rcParams['font.family']='Liberation Serif'
U='/mnt/user-data/uploads/02_Practica/Tp10_Impacto_urbano/'
SITIO=(380780,419280,6514300,6559000); Z=(396000,412000,6520000,6534000); FS=12
r=rasterio.open(U+'02_Subsets_SNAP_QGIS/B_CONCORDIA_compuestos_2026-09-16_20m.tif')
def rgb(ext,f):
    w=from_bounds(*[ext[0],ext[2],ext[1],ext[3]],r.transform)
    a=np.stack([r.read(r.descriptions.index(b)+1,window=w,out_shape=(int(w.height/f),int(w.width/f))) for b in ('B04','B03','B02')]).astype('f4')
    a=np.clip((a-0.0128)/(0.1455-0.0128),0,1); a[~np.isfinite(a)]=1; return a.transpose(1,2,0)
g=gpd.read_file(U+'04_Tablas_de_trabajo/entrenamiento_mapbiomas_B_CONCORDIA.gpkg')
CL=[(1,'urbano','#c00000'),(2,'vegetación leñosa','#1b6e2a'),(3,'herbáceas y cultivos','#b6d96a'),(4,'agua','#2f5fd0'),(5,'suelo desnudo y otras no vegetadas','#e39a30')]
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
W=9.4; H=4.75
fig=plt.figure(figsize=(W,H))
ha=0.70; y0=0.235
wa=ha*H/W*(SITIO[1]-SITIO[0])/(SITIO[3]-SITIO[2]); wz=ha*H/W*(Z[1]-Z[0])/(Z[3]-Z[2])
axs=[]
for k,(ext,x,step,tit,ms,f) in enumerate(((SITIO,0.07,10000,'(a) El sitio',1.2,2),(Z,0.07+wa+0.08,4000,'(b) Concordia y Salto',4,1))):
    ax=fig.add_axes([x,y0,wa if k==0 else wz,ha]); ax.imshow(rgb(ext,f),extent=ext,interpolation='nearest')
    for c,l,col in CL:
        s=g[g.codigo==c]; ax.scatter(s.geometry.x,s.geometry.y,s=ms,c=col,edgecolors='none' if k==0 else 'black',linewidths=0.25,rasterized=True)
    ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3])
    ax.xaxis.set_major_locator(MultipleLocator(step)); ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.xaxis.set_major_formatter(FuncFormatter(fk)); ax.yaxis.set_major_formatter(FuncFormatter(fk))
    ax.tick_params(labelsize=FS,length=3,pad=2); ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS); ax.set_ylabel('Norte (km)',fontsize=FS) if k==0 else None
    ax.set_title(tit,fontsize=FS,pad=4); axs.append(ax)
axs[0].add_patch(Rectangle((Z[0],Z[2]),Z[1]-Z[0],Z[3]-Z[2],fill=False,ec='black',lw=1.3))
axs[1].text(410500,6522800,'Salto\n(sin MapBiomas)',ha='center',fontsize=FS-1,bbox=dict(fc='white',ec='0.5',lw=0.5,pad=2))
b0=axs[0].get_position(); b1=axs[1].get_position()
xn=b1.x1+0.03; yt=b1.y1
fig.add_artist(FancyArrow(xn,yt-0.17,0,0.13,width=0.0025,head_width=0.014,head_length=0.04,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.03,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
def escala(b,ext,L,lab,ys=0.09,hb=0.022):
    frac=L/(ext[1]-ext[0])*b.width; xs=b.x1-frac-0.03
    sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
    for q in range(2): sa.add_patch(Rectangle((q*0.5,0),0.5,1,fc=['black','white'][q],ec='black',lw=0.8))
    fig.text(xs-0.006,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(xs+frac+0.006,ys+hb/2,lab,ha='left',va='center',fontsize=FS)
escala(b0,SITIO,10000,'10 km'); escala(b1,Z,4000,'4 km')
fig.legend(handles=[Line2D([],[],ls='',marker='o',ms=8,mfc=c,mec='none',label=l) for _,l,c in CL],loc='lower left',bbox_to_anchor=(b0.x0-0.04,-0.01),ncol=5,fontsize=FS-1,frameon=False,handletextpad=0.2,columnspacing=1.0)
fig.savefig('Tp10_Figura_09.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
