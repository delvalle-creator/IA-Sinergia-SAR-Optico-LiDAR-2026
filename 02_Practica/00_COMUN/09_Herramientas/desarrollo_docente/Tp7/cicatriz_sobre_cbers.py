# -*- coding: utf-8 -*-
"""cicatriz_sobre_cbers.py - Desarrollo del Tp7 (docente, 22/10/2026).
Traza el deposito (claro de vegetacion rala, NDVI < 0,30 entre las cotas 14 y 42 m, al este del camino costero)
y la cicatriz (escarpa entre la grieta y el borde superior del claro) sobre el CBERS-4A WPM del 26/09/2026 (2 m)
y el MDE IGN 5 m. Interpretacion de imagen, a confirmar con fotos de campo.
"""
import rasterio, numpy as np, geopandas as gpd
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
B=r'D:/CURSOS_CEREGEO_2026/02_Practica/Tp7_Barrancas_deslizamientos/'
Q=B+'02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/E1_DIAMANTE_BARRANCA_'
CRS='EPSG:32721'
gr=gpd.read_file(r'F:/HFdV COURSES/CEREGEO/2018/TelSAR/DIAMANTE/GRIETAS/grietadte.shp').to_crs(CRS)
f=gpd.read_file(B+'04_Tablas_de_trabajo/E1_cicatriz_y_deposito.gpkg',layer='formas').to_crs(CRS)
with rasterio.open(Q+'CBERS4A_DIAMANTE_20260926_pansharpened_2m.tif') as s:
    print(s.crs,s.res,s.count,s.dtypes,[s.descriptions])
c=gr.union_all().centroid; R=350
x0,x1,y0,y1=c.x-R,c.x+R,c.y-R,c.y+R
T=from_origin(x0,y1,1,1); sh=(2*R,2*R)
def L(path,bands,rs=Resampling.bilinear):
    out=[]
    with rasterio.open(path) as s:
        for b in bands:
            o=np.full(sh,np.nan,'f4'); a=s.read(b).astype('f4')
            if s.nodata is not None: a[a==s.nodata]=np.nan
            reproject(a,o,src_transform=s.transform,src_crs=s.crs,dst_transform=T,dst_crs=CRS,resampling=rs,src_nodata=np.nan,dst_nodata=np.nan); out.append(o)
    return out
import pickle
with rasterio.open(Q+'CBERS4A_DIAMANTE_20260926_pansharpened_2m.tif') as s: n=s.count
bands=L(Q+'CBERS4A_DIAMANTE_20260926_pansharpened_2m.tif',range(1,n+1))
ign=L(Q+'IGN_MDE_5m.tif',[1])[0]; mos=L(Q+'IGN_MDE_mosaico2018.tif',[1])[0]; mos[mos<=0]=np.nan; ign=np.where(np.isfinite(ign),ign,mos)
pickle.dump((bands,ign,T,(x0,x1,y0,y1)),open('crop.pkl','wb'))

from matplotlib.colors import LightSource
bands,ign,T,(x0,x1,y0,y1)=pickle.load(open('crop.pkl','rb'))
CRS='EPSG:32721'; B=r'D:/CURSOS_CEREGEO_2026/02_Practica/Tp7_Barrancas_deslizamientos/'
gr=gpd.read_file(r'F:/HFdV COURSES/CEREGEO/2018/TelSAR/DIAMANTE/GRIETAS/grietadte.shp').to_crs(CRS)
f=gpd.read_file(B+'04_Tablas_de_trabajo/E1_cicatriz_y_deposito.gpkg',layer='formas').to_crs(CRS)
def st(a,p=(2,98)):
    lo,hi=np.nanpercentile(a,p); return np.clip((a-lo)/(hi-lo),0,1)
rgb=np.dstack([st(bands[3]),st(bands[2]),st(bands[1])]); fc=np.dstack([st(bands[4]),st(bands[3]),st(bands[2])])
pan=st(bands[0],(1,99))
ext=(x0,x1,y0,y1)
hs=LightSource(315,45).hillshade(np.nan_to_num(ign,nan=np.nanmin(ign)),vert_exag=2,dx=1,dy=1)
from scipy import ndimage as ndi
from rasterio.features import shapes, rasterize
from shapely.geometry import shape
nd=(bands[4]-bands[3])/(bands[4]+bands[3])
nds=ndi.gaussian_filter(np.nan_to_num(nd,nan=1),3)
gy,gx=np.gradient(ndi.gaussian_filter(np.nan_to_num(ign,nan=0),3)); slope=np.hypot(gx,gy)*100
# zona de interés: entre la grieta+15 m y 160 m pendiente abajo, a lo largo de la grieta extendida
from shapely.geometry import LineString
line=gr.union_all()
low=(nds<0.30)&(ign<42)&(ign>14)

from rasterio.features import shapes
from shapely.geometry import shape, Point
from shapely.ops import unary_union
pans=ndi.gaussian_filter(np.nan_to_num(bands[0],nan=0).astype('f4'),1.5)
road=pans>np.nanpercentile(pans[(ign<30)&(ign>10)],97)
road=ndi.binary_opening(road,iterations=1)
lab_r,_=ndi.label(road); sizes=ndi.sum(road,lab_r,range(1,lab_r.max()+1)); big=np.isin(lab_r,1+np.where(sizes>300)[0])
roadbuf=ndi.distance_transform_edt(~big)<6
low=(nds<0.30)&(ign<42)&(ign>14)&~roadbuf
low=ndi.binary_opening(low,structure=np.ones((5,5)))
lab,n=ndi.label(low); k=lab[int(y1-6446420),int(155340-x0)]; print('k',k)
dep=ndi.binary_fill_holes(lab==k)
P=[shape(g) for g,v in shapes(dep.astype('uint8'),mask=dep,transform=T)]
Dp=unary_union(P).simplify(1.5); print('deposito area %.0f'%Dp.area, Dp.bounds)
pickle.dump((dep,Dp,slope,big),open('dep.pkl','wb'))

dep,Dp,slope,big=pickle.load(open('dep.pkl','rb'))
from scipy import ndimage as ndi
nd=(bands[4]-bands[3])/(bands[4]+bands[3]); nds=ndi.gaussian_filter(np.nan_to_num(nd,nan=1),3)
X=x0+np.arange(ign.shape[1])+.5; Y=y1-np.arange(ign.shape[0])-.5
from shapely.geometry import LineString, box, Polygon
from rasterio.features import shapes
from shapely.geometry import shape
from shapely.ops import unary_union
road=LineString([(155250,6446225),(155264,6446339),(155296,6446405),(155307,6446465),(155339,6446531),(155341,6446625)]).buffer(6)
west=Polygon([(155250,6446225),(155264,6446339),(155296,6446405),(155307,6446465),(155339,6446531),(155341,6446625),(155100,6446625),(155100,6446225)])
D=Dp.intersection(box(155280,6446370,155400,6446466)).difference(road).difference(west)
if D.geom_type!='Polygon': D=max(D.geoms,key=lambda g:g.area)
D=Polygon(D.exterior).simplify(1.5)
crack=gr.union_all()
from shapely.geometry import MultiPoint, Point
pts=[p for p in D.exterior.coords]; dd=[crack.distance(Point(p)) for p in pts]; thr=np.percentile(dd,35)
east=[p for p,q in zip(pts,dd) if q<=thr]
H=unary_union([crack.buffer(5),MultiPoint(east).convex_hull.buffer(0.5)]).convex_hull
C=H.difference(D.buffer(0.01))
# quitar la parte al oeste/frente de la mancha: quedarse con la mayor pieza contigua a la grieta
if C.geom_type!='Polygon': C=max(C.geoms,key=lambda g:g.intersection(crack.buffer(6)).area)
C=C.simplify(1.0)
print('deposito %.0f m2  cicatriz %.0f m2'%(D.area,C.area))
pickle.dump((D,C),open('pol.pkl','wb'))
fig,ax=plt.subplots(1,3,figsize=(24,8.5))
cx,cy=155370,6446425; R=200
for a,(im,cm,kw,t) in zip(ax,[(fc,None,{},'CBERS-4A 26/09/2026, falso color (IRC, R, V)'),(rgb,None,{},'Color natural'),(hs,'gray',{},'IGN 5 m sombreado y pendiente 30 %')]):
    a.imshow(im,extent=ext,cmap=cm); a.set_title(t)
    a.contour(X,Y,slope,levels=[30],colors='magenta',linewidths=.6)
    gpd.GeoSeries([C],crs=CRS).boundary.plot(ax=a,color='yellow',lw=2); gpd.GeoSeries([D],crs=CRS).boundary.plot(ax=a,color='cyan',lw=2)
    f.boundary.plot(ax=a,color='white',lw=.8,ls=':')
    gr.plot(ax=a,color='red',lw=2)
    a.set_xlim(cx-R,cx+R); a.set_ylim(cy-R,cy+R); a.set_xticks([]); a.set_yticks([])
plt.tight_layout(); plt.savefig('v5.png',dpi=60)
