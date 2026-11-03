import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
plt.rcParams['font.family']='Liberation Serif'
U='/mnt/user-data/uploads/02_Practica/Tp10_Impacto_urbano/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/B_CONCORDIA_CCI_Biomass_v7_AGB.tif'
SITIO=(380780,419280,6514300,6559000); PX=50; FS=12
nx=round((SITIO[1]-SITIO[0])/PX); ny=round((SITIO[3]-SITIO[2])/PX)
r=rasterio.open(U)
def banda(n):
    b=r.descriptions.index(n)+1; dst=np.full((ny,nx),np.nan,'f4')
    reproject(r.read(b).astype('f4'),dst,src_transform=r.transform,src_crs=r.crs,dst_transform=from_origin(SITIO[0],SITIO[3],PX,PX),dst_crs='EPSG:32721',resampling=Resampling.nearest,dst_nodata=np.nan)
    return dst
agb=banda('AGB_2024'); sd=banda('AGB_SD_2024'); print(np.nanpercentile(agb,(50,99)),np.nanpercentile(sd,(50,99)))
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
W=9.6; H=5.0
fig=plt.figure(figsize=(W,H))
w=0.33; h=w*W/H*(SITIO[3]-SITIO[2])/(SITIO[1]-SITIO[0]); y0=0.12
axs=[]
for k,(arr,cm,vmax,tit,tk) in enumerate(((agb,'YlGn',130,'(a) CCI Biomass, biomasa aérea 2024',[0,20,40,60,80,100,120]),(sd,'OrRd',60,'(b) Desvío estándar 2024',[0,10,20,30,40,50,60]))):
    x=0.08+k*(w+0.14)
    ax=fig.add_axes([x,y0,w,h]); im=ax.imshow(arr,extent=SITIO,cmap=cm,vmin=0,vmax=vmax,interpolation='nearest')
    ax.set_xlim(SITIO[0],SITIO[1]); ax.set_ylim(SITIO[2],SITIO[3])
    ax.xaxis.set_major_locator(MultipleLocator(10000)); ax.yaxis.set_major_locator(MultipleLocator(10000))
    ax.xaxis.set_major_formatter(FuncFormatter(fk)); ax.yaxis.set_major_formatter(FuncFormatter(fk))
    ax.tick_params(labelsize=FS,length=3,pad=2); ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS)
    if k==0: ax.set_ylabel('Norte (km)',fontsize=FS)
    else: ax.set_yticklabels([])
    ax.set_title(tit,fontsize=FS,pad=4)
    b=ax.get_position(); cax=fig.add_axes([b.x1+0.012,b.y0,0.015,b.height])
    cb=fig.colorbar(im,cax=cax,ticks=tk,extend='max'); cb.ax.tick_params(labelsize=FS); cb.set_label('Mg/ha',fontsize=FS)
    axs.append(ax)
# flecha del norte: esquinero superior derecho, fuera
b=axs[1].get_position(); xn=b.x1+0.115; yt=b.y1
fig.add_artist(FancyArrow(xn,yt-0.17,0,0.13,width=0.0025,head_width=0.016,head_length=0.045,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.03,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
# escala horizontal, fuera, centrada bajo los dos mapas
L=10000; frac=L/(SITIO[1]-SITIO[0])*w; ys=0.0; hb=0.022
xs=(axs[0].get_position().x0+axs[1].get_position().x1)/2-frac/2
sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for i in range(2): sa.add_patch(Rectangle((i*0.5,0),0.5,1,fc=['black','white'][i],ec='black',lw=0.8))
fig.text(xs-0.006,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(xs+frac+0.006,ys+hb/2,'10 km',ha='left',va='center',fontsize=FS)
fig.savefig('Tp10_Figura_04.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
