import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow, Patch
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
plt.rcParams['font.family']='Liberation Serif'; FS=11
U='/mnt/user-data/uploads/CURSOS_CEREGEO_2026/02_Practica/Tp9_Deforestacion/'
V=(306340,309640,6589300,6593300); PX=10
nx=int((V[1]-V[0])/PX); ny=int((V[3]-V[2])/PX); dtr=from_origin(V[0],V[3],PX,PX)
def g(path,bands,res=Resampling.bilinear,nod=None):
    r=rasterio.open(path); out=[]
    for b in bands:
        d=np.zeros((ny,nx),'f4'); reproject(r.read(b).astype('f4'),d,src_transform=r.transform,src_crs=r.crs,dst_transform=dtr,dst_crs='EPSG:32721',resampling=res,src_nodata=nod,dst_nodata=0); out.append(d)
    return np.stack(out)
def est(a):
    m=(a>0).all(0); o=np.zeros(a.shape[1:]+(3,))
    for i in range(3):
        lo,hi=np.percentile(a[i][m],(2,98)); o[...,i]=np.clip((a[i]-lo)/(hi-lo),0,1)
    o[~m]=1; return o
l8=est(g(U+'02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/C_FEDERAL_L8_20210807.tif',[4,3,2],nod=0))
s2=est(g(U+'02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/C_FEDERAL_S2_20260916.tif',[3,2,1],nod=0))
p=g(U+'02_Subsets_SNAP_QGIS/C_pila_temporal_20m.tif',[5,2],res=Resampling.nearest)
def s(a): return np.clip((a-0.004)/(0.05-0.004),0,1)
ch=np.dstack([s(p[0]),s(p[1]),s(p[1])])
c=g(U+'05_Resultados/02_Rasters/C_perdida_degradacion.tif',[1],res=Resampling.nearest)[0]
COL={1:'#d7191c',2:'#fdae61',3:'#1a9641',4:'#e6e6e6'}
mp=np.ones((ny,nx,3))
for k,h in COL.items(): mp[c==k]=matplotlib.colors.to_rgb(h)
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.') if abs(v/1000-round(v/1000))<1e-6 else ''
W,H=9.6,3.5
fig=plt.figure(figsize=(W,H)); w=0.205; h=w*W/H*(V[3]-V[2])/(V[1]-V[0]); y=0.2; gx=0.03
tit=['(a) Landsat 8, 07/08/2021','(b) Sentinel-2, 16/09/2026','(c) R = NISAR HV 2026,\nG y B = ALOS-2 HV 2021','(d) Mapa multisensor']
axs=[]
for k,img in enumerate([l8,s2,ch,mp]):
    ax=fig.add_axes([0.07+k*(w+gx),y,w,h]); ax.imshow(img,extent=V,interpolation='nearest')
    ax.set_xlim(V[0],V[1]); ax.set_ylim(V[2],V[3])
    for a_ in (ax.xaxis,ax.yaxis): a_.set_major_locator(MultipleLocator(1000)); a_.set_major_formatter(FuncFormatter(fk))
    ax.tick_params(labelsize=FS,length=3,pad=2); ax.set_xlabel('Este (km)',fontsize=FS)
    if k==0: ax.set_ylabel('Norte (km, UTM 21 S)',fontsize=FS)
    else: ax.set_yticklabels([])
    ax.set_title(tit[k],fontsize=FS,pad=3); axs.append(ax)
b=axs[0].get_position(); frac=1000/(V[1]-V[0])*b.width; ys=-0.02; hb=0.03
sa=fig.add_axes([b.x0,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for i in range(2): sa.add_patch(Rectangle((i*0.5,0),0.5,1,fc=['black','white'][i],ec='black',lw=0.8))
fig.text(b.x0-0.005,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(b.x0+frac+0.005,ys+hb/2,'1 km',ha='left',va='center',fontsize=FS)
hs=[Patch(fc=COL[k],ec='black',lw=0.5,label=l) for k,l in zip((1,2,3,4),('1 pérdida','2 degradación','3 monte estable','4 no bosque estable'))]
b3=axs[3].get_position()
fig.legend(handles=hs,loc='upper center',bbox_to_anchor=((axs[1].get_position().x0+b3.x1)/2,ys+0.06),ncol=4,fontsize=FS,frameon=False)
xn=b3.x1+0.025; yt=b3.y1
fig.add_artist(FancyArrow(xn,yt-0.24,0,0.2,width=0.003,head_width=0.014,head_length=0.065,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.04,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
fig.savefig('Tp9_Figura_15.png',dpi=300,bbox_inches='tight',pad_inches=0.04)
