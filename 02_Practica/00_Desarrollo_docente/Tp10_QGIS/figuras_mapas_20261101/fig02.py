import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
plt.rcParams['font.family']='Liberation Serif'; plt.rcParams['mathtext.fontset']='custom'; plt.rcParams['mathtext.rm']='Liberation Serif'; plt.rcParams['mathtext.it']='Liberation Serif:italic'
U='/mnt/user-data/uploads/02_Practica/'
T=U+'Tp10_Impacto_urbano/02_Subsets_SNAP_QGIS/'
SITIO=(380780,419280,6514300,6559000); FS=11; PX=50
nx=int((SITIO[1]-SITIO[0])/PX); ny=int((SITIO[3]-SITIO[2])/PX)
dtr=from_origin(SITIO[0],SITIO[3],PX,PX)
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
def a_grilla(path,bands,res=Resampling.average,nod=0,dx=0,dy=0):
    r=rasterio.open(path); out=[]
    tr=from_origin(SITIO[0]-dx,SITIO[3]-dy,PX,PX)   # dx,dy: corrimiento de la imagen (m E, m N)
    for b in bands:
        dst=np.full((ny,nx),np.nan,'f4'); src=r.read(b).astype('f4')
        if r.crs is None:
            g,gc=r.gcps
            reproject(src,dst,gcps=g,src_crs=gc,dst_transform=tr,dst_crs='EPSG:32721',resampling=Resampling.bilinear,src_nodata=nod,dst_nodata=np.nan)
        else:
            reproject(src,dst,src_transform=r.transform,src_crs=r.crs,dst_transform=tr,dst_crs='EPSG:32721',resampling=res,src_nodata=nod,dst_nodata=np.nan)
        out.append(dst)
    return np.stack(out)
def rgb8(path):
    a=a_grilla(path,[1,2,3]); z=~np.isfinite(a).all(0)|(np.nan_to_num(a)==0).all(0)
    o=np.nan_to_num(a/255.).transpose(1,2,0); o[z]=1; return np.clip(o,0,1)
a=a_grilla(U+'00_COMUN/09_Herramientas/desarrollo_docente/Tp10/B_CONCORDIA_S2_20260904_10m.tif',[3,2,1],nod=-9999)
m=~np.isfinite(a).all(0); lo,hi=np.nanpercentile(a[:,~m],(2,98))
s2=np.clip((np.nan_to_num(a)-lo)/(hi-lo),0,1).transpose(1,2,0); s2[m]=1
R=T+'RGB_copol_cruzada_cociente/B_CONCORDIA_'
s1=rgb8(R+'S1_C_20260914_RGB_8bit.tif'); ni=rgb8(R+'NISAR_L_20260918_RGB_8bit.tif'); bp=rgb8(R+'BIOMASS_P_20260722_RGB_8bit.tif')
ns=a_grilla(T+'QGIS_GeoTIFF/B_CONCORDIA_NovaSAR1_S_20230913_Sigma0_HH_db.tif',[1],nod=np.nan,dx=-40,dy=100)[0]
st=a_grilla(T+'QGIS_GeoTIFF/B_CONCORDIA_L8_20260915_ST_B10_C.tif',[1],nod=np.nan)[0]
print('NovaSAR',np.nanpercentile(ns,(2,98)),'ST',np.nanpercentile(st,(2,98)), np.isfinite(ns).mean())
W=8.6; H=6.05
fig=plt.figure(figsize=(W,H))
w=0.205; h=w*W/H*(SITIO[3]-SITIO[2])/(SITIO[1]-SITIO[0]); gx=0.105
x0=[0.075,0.075+w+gx,0.075+2*(w+gx)]; yrow=[0.545,0.105]
tit=['(a) Sentinel-2, 04/09/2026\ncolor natural','(b) Sentinel-1 C, 14/09/2026\nR = VV, G = VH, B = VV/VH','(c) NISAR L, 18/09/2026\nR = HH, G = HV, B = HH/HV',
     '(d) BIOMASS P, 22/07/2026\nR = HH, G = VH, B = HH/VH','(e) NovaSAR S, HH, 13/09/2023\ncorregida −40 m E, +100 m N','(f) Landsat 8, temperatura\nde superficie, 15/09/2026']
axs=[]; ims={}
for k,img in enumerate([s2,s1,ni,bp,'ns','st']):
    ax=fig.add_axes([x0[k%3],yrow[k//3],w,h])
    if isinstance(img,str):
        if img=='ns':
            cm=plt.get_cmap('gray').copy(); cm.set_bad('white'); ims[k]=ax.imshow(ns,extent=SITIO,cmap=cm,vmin=-22,vmax=2,interpolation='nearest')
        else:
            cm=plt.get_cmap('inferno').copy(); cm.set_bad('white'); ims[k]=ax.imshow(st,extent=SITIO,cmap=cm,vmin=17,vmax=29,interpolation='nearest')
    else: ax.imshow(img,extent=SITIO,interpolation='nearest')
    ax.set_xlim(SITIO[0],SITIO[1]); ax.set_ylim(SITIO[2],SITIO[3])
    ax.xaxis.set_major_locator(MultipleLocator(10000)); ax.yaxis.set_major_locator(MultipleLocator(10000))
    ax.xaxis.set_major_formatter(FuncFormatter(fk)); ax.yaxis.set_major_formatter(FuncFormatter(fk))
    ax.tick_params(labelsize=FS,length=3,pad=2)
    if k>=3: ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS)
    else: ax.set_xticklabels([])
    if k%3==0: ax.set_ylabel('Norte (km)',fontsize=FS)
    else: ax.set_yticklabels([])
    ax.set_title(tit[k],fontsize=FS,pad=3); axs.append(ax)
for k,lab,tk in ((4,r'$\sigma^0$ HH (dB)',[-20,-15,-10,-5,0]),(5,'°C',[18,20,22,24,26,28])):
    b=axs[k].get_position(); cax=fig.add_axes([b.x1+0.008,b.y0,0.013,b.height])
    cb=fig.colorbar(ims[k],cax=cax,ticks=tk); cb.ax.tick_params(labelsize=FS); cb.set_label(lab,fontsize=FS)
    cb.ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f'{v:.0f}'.replace('-','−')))
# escala gráfica horizontal, fuera, bajo el panel (e)
b=axs[4].get_position(); L=10000; frac=L/(SITIO[1]-SITIO[0])*b.width
ys=0.005; hb=0.016; xs=b.x0+(b.width-frac)/2
sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for i in range(2): sa.add_patch(Rectangle((i*0.5,0),0.5,1,fc=['black','white'][i],ec='black',lw=0.8))
fig.text(xs-0.006,ys+hb/2,'0',ha='right',va='center',fontsize=FS)
fig.text(xs+frac+0.006,ys+hb/2,'10 km',ha='left',va='center',fontsize=FS)
# flecha del norte única, esquinero superior derecho, fuera del mapa
bn=axs[2].get_position(); xn=bn.x1+0.035; yt=bn.y1
fig.add_artist(FancyArrow(xn,yt-0.13,0,0.10,width=0.003,head_width=0.018,head_length=0.035,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.025,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
fig.savefig('Tp10_Figura_02.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
