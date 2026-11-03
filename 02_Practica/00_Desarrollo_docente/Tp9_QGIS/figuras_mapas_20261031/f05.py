import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
plt.rcParams['font.family']='Liberation Serif'
U='/mnt/user-data/uploads/CURSOS_CEREGEO_2026/02_Practica/Tp9_Deforestacion/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/'
SITIO=(306320,345320,6569760,6614720); FS=11; PX=50
nx=int((SITIO[1]-SITIO[0])/PX); ny=int((SITIO[3]-SITIO[2])/PX); dtr=from_origin(SITIO[0],SITIO[3],PX,PX)
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
def fn(v,_): return f'{v:g}'.replace('-','−')
r=rasterio.open(U+'C_FEDERAL_CCI_Biomass_v7_AGB.tif')
def g(b):
    d=np.full((ny,nx),np.nan,'f4'); reproject(r.read(b).astype('f4'),d,src_transform=r.transform,src_crs=r.crs,dst_transform=dtr,dst_crs='EPSG:32721',resampling=Resampling.nearest,dst_nodata=np.nan); return d
a21=g(4); sd21=g(9); a24=g(5); df=a24-a21
W,H=9.6,3.75
fig=plt.figure(figsize=(W,H))
w=0.215; h=w*W/H*(SITIO[3]-SITIO[2])/(SITIO[1]-SITIO[0]); y=0.17; gx=0.105; x0=[0.075,0.075+w+gx,0.075+2*(w+gx)]
cfg=[(a21,'YlGn',0,50,'(a) Biomasa aérea 2021','Mg/ha',[0,10,20,30,40,50]),(sd21,'Reds',0,25,'(b) Desvío estándar 2021','Mg/ha',[0,5,10,15,20,25]),(df,'RdBu',-40,40,'(c) Diferencia 2024 − 2021','Mg/ha',[-40,-20,0,20,40])]
axs=[]
for k,(arr,cm,lo,hi,t,lab,tk) in enumerate(cfg):
    ax=fig.add_axes([x0[k],y,w,h]); im=ax.imshow(arr,extent=SITIO,cmap=cm,vmin=lo,vmax=hi,interpolation='nearest')
    ax.set_xlim(SITIO[0],SITIO[1]); ax.set_ylim(SITIO[2],SITIO[3])
    ax.xaxis.set_major_locator(MultipleLocator(10000)); ax.yaxis.set_major_locator(MultipleLocator(10000))
    ax.xaxis.set_major_formatter(FuncFormatter(fk)); ax.yaxis.set_major_formatter(FuncFormatter(fk))
    ax.tick_params(labelsize=FS,length=3,pad=2); ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS)
    if k==0: ax.set_ylabel('Norte (km)',fontsize=FS)
    else: ax.set_yticklabels([])
    ax.set_title(t,fontsize=FS,pad=4)
    b=ax.get_position(); cax=fig.add_axes([b.x1+0.008,b.y0,0.012,b.height])
    cb=fig.colorbar(im,cax=cax,ticks=tk,format=FuncFormatter(fn)); cb.ax.tick_params(labelsize=FS); cb.set_label(lab,fontsize=FS)
    axs.append(ax)
b=axs[1].get_position(); L=10000; frac=L/(SITIO[1]-SITIO[0])*b.width; ys=-0.02; hb=0.03; xs=b.x0+(b.width-frac)/2
sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for i in range(2): sa.add_patch(Rectangle((i*0.5,0),0.5,1,fc=['black','white'][i],ec='black',lw=0.8))
fig.text(xs-0.005,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(xs+frac+0.005,ys+hb/2,'10 km',ha='left',va='center',fontsize=FS)
bn=axs[2].get_position(); xn=bn.x1+0.075; yt=bn.y1
fig.add_artist(FancyArrow(xn,yt-0.22,0,0.18,width=0.0025,head_width=0.013,head_length=0.06,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.03,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
fig.savefig('Tp9_Figura_05.png',dpi=300,bbox_inches='tight',pad_inches=0.04)
v=np.isfinite(df); print('dif p5/50/95',np.percentile(df[v],(5,50,95)), 'a21 med',np.nanmedian(a21))
