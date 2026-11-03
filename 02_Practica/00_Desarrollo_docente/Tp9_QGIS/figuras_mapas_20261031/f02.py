import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
plt.rcParams['font.family']='Liberation Serif'
U='/mnt/user-data/uploads/CURSOS_CEREGEO_2026/02_Practica/Tp9_Deforestacion/02_Subsets_SNAP_QGIS/'
SITIO=(306320,345320,6569760,6614720); FS=11; PX=20
nx=int((SITIO[1]-SITIO[0])/PX); ny=int((SITIO[3]-SITIO[2])/PX); dtr=from_origin(SITIO[0],SITIO[3],PX,PX)
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
def a_grilla(path,bands,res=Resampling.average,nod=0):
    r=rasterio.open(path); out=[]
    for b in bands:
        dst=np.zeros((ny,nx),'f4')
        src=r.read(b).astype('f4')
        if r.crs is None:
            g,gc=r.gcps; reproject(src,dst,gcps=g,src_crs=gc,dst_transform=dtr,dst_crs='EPSG:32721',resampling=Resampling.bilinear,src_nodata=nod,dst_nodata=0)
        else:
            reproject(src,dst,src_transform=r.transform,src_crs=r.crs,dst_transform=dtr,dst_crs='EPSG:32721',resampling=res,src_nodata=nod,dst_nodata=0)
        out.append(dst)
    return np.stack(out)
def rgb8(path):
    a=a_grilla(path,[1,2,3]); z=(a==0).all(0)
    o=(a/255.).transpose(1,2,0); o[z]=1; return o
# (a) Sentinel-2 color natural, estiramiento 2-98 % común
a=a_grilla(U+'QGIS_GeoTIFF/C_FEDERAL_S2_20260916.tif',[3,2,1]); m=(a==0).all(0); a=(a-1000)/10000
lo,hi=np.percentile(a[:,~m],(2,98)); s2=np.clip((a-lo)/(hi-lo),0,1).transpose(1,2,0); s2[m]=1
R='RGB_copol_cruzada_cociente/C_FEDERAL_'
s1=rgb8(U+R+'S1_C_20260914_RGB_8bit.tif'); al=rgb8(U+R+'ALOS2_L_mosaico2021_RGB_8bit.tif')
ni=rgb8(U+R+'NISAR_L_20260917_RGB_8bit.tif'); bp=rgb8(U+R+'BIOMASS_P_20260812_RGB_8bit.tif')
fh=a_grilla(U+'QGIS_GeoTIFF/C_FEDERAL_BIOMASS_P_FH_20260728_0809_sin_agua.tif',[1,3],res=Resampling.nearest,nod=np.nan)
fhv=np.where((fh[0]>0)&(fh[1]<0.5),fh[0],np.nan)
print('FH', np.nanpercentile(fhv,(1,50,99)), np.unique(fh[1])[:5])
W=7.4; H=5.9
fig=plt.figure(figsize=(W,H))
w=0.235; h=w*W/H*(SITIO[3]-SITIO[2])/(SITIO[1]-SITIO[0]); gx=0.075; x0=[0.085,0.085+w+gx,0.085+2*(w+gx)]
yrow=[0.535,0.08]
tit=['(a) Sentinel-2, 16/09/2026\ncolor natural','(b) Sentinel-1 C, 14/09/2026\nR = VV, G = VH, B = VV/VH','(c) ALOS-2 L, mosaico 2021\nR = HH, G = HV, B = HH/HV',
     '(d) NISAR L, 17/09/2026\nR = HH, G = HV, B = HH/HV','(e) BIOMASS P, 12/08/2026\nR = HH, G = VH, B = HH/VH','(f) BIOMASS, altura FH\n28/07 a 09/08/2026']
axs=[]
for k,img in enumerate([s2,s1,al,ni,bp,None]):
    ax=fig.add_axes([x0[k%3],yrow[k//3],w,h])
    if img is None:
        cmap=plt.get_cmap('viridis').copy(); cmap.set_bad('white')
        im=ax.imshow(fhv,extent=SITIO,cmap=cmap,vmin=0,vmax=14,interpolation='nearest')
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
b=axs[5].get_position()
cax=fig.add_axes([b.x1+0.012,b.y0,0.016,b.height]); cb=fig.colorbar(im,cax=cax,ticks=[0,2,4,6,8,10,12,14]); cb.ax.tick_params(labelsize=FS); cb.set_label('Altura FH (m)',fontsize=FS)
# escala gráfica horizontal fuera del mapa, debajo de la fila inferior (centrada bajo el panel e)
b=axs[4].get_position(); L=10000; frac=L/(SITIO[1]-SITIO[0])*b.width
ys=-0.04; hb=0.018; xs=b.x0+(b.width-frac)/2
sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for i in range(2): sa.add_patch(Rectangle((i*0.5,0),0.5,1,fc=['black','white'][i],ec='black',lw=0.8))
fig.text(xs-0.006,ys+hb/2,'0',ha='right',va='center',fontsize=FS)
fig.text(xs+frac+0.006,ys+hb/2,'10 km',ha='left',va='center',fontsize=FS)
# flecha del norte única, esquinero superior derecho, fuera del mapa
bn=axs[2].get_position(); xn=bn.x1+0.035; yt=bn.y1
fig.add_artist(FancyArrow(xn,yt-0.13,0,0.10,width=0.003,head_width=0.018,head_length=0.035,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.025,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
fig.savefig('Tp9_Figura_02.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
