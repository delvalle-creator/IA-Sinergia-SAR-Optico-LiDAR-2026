import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
plt.rcParams['font.family']='Liberation Serif'
U='/mnt/user-data/uploads/02_Practica/Tp10_Impacto_urbano/'
r=rasterio.open(U+'05_Resultados/02_Rasters/B_CONCORDIA_clases_sin_S.tif'); cl=r.read(1)
SITIO=(380780,419280,6514300,6559020); Z=(396000,412000,6520000,6534000); FS=12
mb=rasterio.open(U+'02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/B_CONCORDIA_MapBiomas_cobertura_1985_2025.tif')
m25=np.zeros(cl.shape,'u1')
reproject(mb.read(mb.descriptions.index('cobertura_2025')+1),m25,src_transform=mb.transform,src_crs=mb.crs,dst_transform=r.transform,dst_crs=r.crs,resampling=Resampling.nearest,src_nodata=0,dst_nodata=0)
rf=cl==1; mu=m25==24; hay=m25>0
comp=np.full(cl.shape,np.nan); comp[rf&mu]=0; comp[rf&~mu&hay]=1; comp[~rf&mu]=2; comp[rf&~hay]=3
ha=0.04
print('ambos',(rf&mu).sum()*ha,'solo RF',(rf&~mu&hay).sum()*ha,'solo MB',(~rf&mu).sum()*ha,'uy',(rf&~hay).sum()*ha,'RF',rf.sum()*ha)
cc=['#c00000','#1b6e2a','#b6d96a','#3a6fd8','#e0a040']; cmc=ListedColormap(cc)
clp=np.where(cl>0,cl,np.nan)
c3=['#8b0000','#ff8c1a','#1f5fe0','#8c8c8c']; cm3=ListedColormap(c3)
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
W=10.0; H=3.95
fig=plt.figure(figsize=(W,H))
def ejes(ax,ext,step,ylab,tit,yt=True):
    ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3])
    if step==4000: ax.set_xticks([400000,404000,408000]); ax.set_yticks([6522000,6526000,6530000])
    else: ax.xaxis.set_major_locator(MultipleLocator(step)); ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.xaxis.set_major_formatter(FuncFormatter(fk)); ax.yaxis.set_major_formatter(FuncFormatter(fk))
    ax.tick_params(labelsize=FS,length=3,pad=2); ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS)
    if ylab: ax.set_ylabel('Norte (km)',fontsize=FS)
    if not yt: ax.set_yticklabels([])
    ax.set_title(tit,fontsize=FS,pad=4)
hh=0.61; y0=0.33
wa=hh*H/W*(SITIO[1]-SITIO[0])/(SITIO[3]-SITIO[2])*0.86; hA=hh*0.86; wz=hh*H/W*(Z[1]-Z[0])/(Z[3]-Z[2])
ax1=fig.add_axes([0.065,y0,wa,hA]); ax1.imshow(clp,extent=SITIO,cmap=cmc,vmin=0.5,vmax=5.5,interpolation='nearest')
ax1.add_patch(Rectangle((Z[0],Z[2]),Z[1]-Z[0],Z[3]-Z[2],fill=False,ec='black',lw=1.2)); ejes(ax1,SITIO,10000,True,'(a) El sitio')
x2=0.065+wa+0.055
ax2=fig.add_axes([x2,y0,wz,hh]); ax2.imshow(clp,extent=SITIO,cmap=cmc,vmin=0.5,vmax=5.5,interpolation='nearest'); ejes(ax2,Z,4000,False,'(b) Concordia y Salto')
ax3=fig.add_axes([x2+wz+0.015,y0,wz,hh]); ax3.imshow(comp,extent=SITIO,cmap=cm3,vmin=-0.5,vmax=3.5,interpolation='nearest'); ejes(ax3,Z,4000,False,'(c) Urbano: Random Forest\nfrente a MapBiomas 2025',yt=False)
b3=ax3.get_position(); b2=ax2.get_position(); ba=ax1.get_position()
xn=b3.x1+0.025; yt=b3.y1
fig.add_artist(FancyArrow(xn,yt-0.2,0,0.16,width=0.0025,head_width=0.014,head_length=0.05,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.035,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
L1=['urbano','vegetación leñosa','herbáceas y cultivos','agua','suelo desnudo y otras']
L3=['urbano en los dos','sólo Random Forest','sólo MapBiomas','Random Forest, sin MapBiomas (Uruguay)']
fig.legend(handles=[Patch(fc=c,ec='0.4',lw=0.4,label=l) for c,l in zip(cc,L1)],loc='lower center',bbox_to_anchor=(0.5,0.035),ncol=5,fontsize=FS-1,frameon=False,handlelength=1.2,columnspacing=1.0)
fig.legend(handles=[Patch(fc=c,ec='0.4',lw=0.4,label=l) for c,l in zip(c3,L3)],loc='lower center',bbox_to_anchor=(0.5,-0.03),ncol=4,fontsize=FS-1,frameon=False,handlelength=1.2,columnspacing=1.0)
def esc(xs,frac,lab,tag,ys=0.165,hb=0.022):
    sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
    for q in range(2): sa.add_patch(Rectangle((q*0.5,0),0.5,1,fc=['black','white'][q],ec='black',lw=0.8))
    fig.text(xs-0.006,ys+hb/2,tag+'   0',ha='right',va='center',fontsize=FS); fig.text(xs+frac+0.006,ys+hb/2,lab,ha='left',va='center',fontsize=FS)
fa=10000/(SITIO[1]-SITIO[0])*wa; fz=4000/(Z[1]-Z[0])*wz
esc(ba.x0+(ba.width-fa)/2,fa,'10 km','(a)'); esc(b3.x1-fz-0.04,fz,'4 km','(b) y (c)')
fig.savefig('Tp10_Figura_11.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
