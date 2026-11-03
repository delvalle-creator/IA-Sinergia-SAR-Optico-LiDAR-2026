import pickle, numpy as np, rasterio, geopandas as gpd
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family']='Liberation Serif'
D=pickle.load(open('plan.pkl','rb')); CRS='EPSG:32721'
Q='/mnt/user-data/uploads/CURSOS_CEREGEO_2026/02_Practica/Tp7_Barrancas_deslizamientos/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/E1_DIAMANTE_BARRANCA_'
x0,y0,x1,y1=D['aoi'].buffer(150).bounds; PX=2
T=from_origin(x0,y1,PX,PX); sh=(int((y1-y0)/PX),int((x1-x0)/PX))
def L(p,b):
    o=np.full(sh,np.nan,'f4')
    with rasterio.open(p) as s:
        a=s.read(b).astype('f4'); 
        if s.nodata is not None: a[a==s.nodata]=np.nan
        reproject(a,o,src_transform=s.transform,src_crs=s.crs,dst_transform=T,dst_crs=CRS,resampling=Resampling.bilinear,src_nodata=np.nan,dst_nodata=np.nan)
    return o
rgb=[L(Q+'CBERS4A_DIAMANTE_20260926_pansharpened_2m.tif',b) for b in (4,3,2)]
def st(a): lo,hi=np.nanpercentile(a,[2,98]); return np.clip((a-lo)/(hi-lo),0,1)
img=np.nan_to_num(np.dstack([st(a) for a in rgb]),nan=1)
ign=L(Q+'IGN_MDE_5m.tif',1); mos=L(Q+'IGN_MDE_mosaico2018.tif',1); mos[mos<=0]=np.nan; ign=np.where(np.isfinite(ign),ign,mos)
G=D['G']
def z(x,y): r=int((y1-y)/PX); c=int((x-x0)/PX); return ign[r,c]
G['cota_IGN_m']=[round(float(z(x,y)),1) for x,y in zip(G.x,G.y)]
print(G[['id','posicion','cota_IGN_m','dist_grieta_m']].to_string())
pickle.dump(G,open('G.pkl','wb'))
fig,ax=plt.subplots(figsize=(13,11)); ext=(x0,x1,y0,y1)
ax.imshow(img,extent=ext)
X=np.linspace(x0,x1,sh[1]); Y=np.linspace(y1,y0,sh[0])
cs=ax.contour(X,Y,ign,levels=range(10,70,5),colors='yellow',linewidths=.4,alpha=.7)
gpd.GeoSeries([D['aoi']],crs=CRS).boundary.plot(ax=ax,color='white',lw=2)
for l in D['lines']: ax.plot(*l.xy,color='cyan',lw=.8)
ax.plot(*D['ob'].xy,color='magenta',lw=2)
F=D['F']; ax.scatter(F.x[F.tipo=='nadir'],F.y[F.tipo=='nadir'],s=3,c='cyan')
for _,g in G.iterrows():
    m='^' if g.tipo=='control' else 's'
    ax.scatter(g.x,g.y,marker=m,s=110,c='red' if g.tipo=='control' else 'orange',edgecolor='k',zorder=6)
    ax.text(g.x+12,g.y+12,g.id,fontsize=9,color='w',weight='bold',zorder=7,bbox=dict(fc='k',alpha=.5,ec='none',pad=1))
gr=gpd.read_file('/mnt/user-data/uploads/DIAMANTE/GRIETAS/grietadte.shp').to_crs(CRS)
gr.plot(ax=ax,color='white',lw=6,zorder=5); gr.plot(ax=ax,color='red',lw=3.5,zorder=5)
ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_xticks([]); ax.set_yticks([])
plt.savefig('chk_mapa.png',dpi=80,bbox_inches='tight')
