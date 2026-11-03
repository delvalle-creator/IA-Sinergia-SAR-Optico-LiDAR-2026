import numpy as np, rasterio, geopandas as gpd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow
from rasterio.windows import from_bounds
plt.rcParams['font.family']='Liberation Serif'
U='/mnt/user-data/uploads/02_Practica/'
S2=rasterio.open(U+'Tp10_Impacto_urbano/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/B_CONCORDIA_S2_20260916.tif')
CB=rasterio.open(U+'Tp10_Impacto_urbano/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/B_CONCORDIA_CBERS4A_CONCORDIA_20260715_pansharpened_2m.tif')
rev=gpd.read_file(U+'Tp4_Validacion/04_Tablas_de_trabajo/B_CONCORDIA_revision_humana_etiquetas_puntos_a_revisar.gpkg')
fr=gpd.read_file(U+'Tp4_Validacion/04_Tablas_de_trabajo/B_CONCORDIA_variante_multisensor_franja_1km_puntos_a_etiquetar.gpkg')
def xy(src,o):
    g=(rev[rev.orden==o] if src=='rev' else fr[fr.id==o]).geometry.iloc[0]; return g.x,g.y
C={1:'urbano',2:'no urbano',0:'nube'}
casos=[('a','rev',2,'A: urbano (alta); B: urbano (alta)','Consenso: urbano; IA: no urbano'),
       ('b','rev',1,'A: no urbano (alta); B: no urbano (alta)','Consenso: no urbano; IA: no urbano'),
       ('c','rev',56,'A: urbano (media); B: no urbano (media)','Consenso: urbano; IA: no urbano'),
       ('d','rev',13,'A: urbano (media); B: no urbano (alta)','Consenso: no urbano; IA: no urbano'),
       ('e','rev',9,'A: nube; B: nube','Consenso: no interpretable; IA: urbano'),
       ('f','fr',5,'A: urbano (media); B: urbano (baja)','Consenso: urbano (franja de 1 km)')]
GL={}
for b in (1,2,3,7):
    v=S2.read(b,out_shape=(S2.height//8,S2.width//8)).astype('f4'); v=v[v>0]; GL[b]=np.percentile(v,(2,98))
def chip(r,bands,x,y,h):
    w=from_bounds(x-h,y-h,x+h,y+h,r.transform); a=np.stack([r.read(b,window=w,boundless=True,fill_value=0) for b in bands]).astype('f4')
    if r is S2:
        v=a[a>0]; lo,hi=np.percentile(v,(1,99.5)); a=np.clip((a-lo)/(hi-lo),0,1)**0.9
        return a.transpose(1,2,0)
    for q in range(3):
        v=a[q][a[q]>0]
        if v.size: lo,hi=np.percentile(v,(2,98)); a[q]=np.clip((a[q]-lo)/(hi-lo+1e-6),0,1)
    return a.transpose(1,2,0)
def inCB(x,y,h): b=CB.bounds; return b.left<x-h and x+h<b.right and b.bottom<y-h and y+h<b.top
FS=11.5
fig=plt.figure(figsize=(9.8,8.6))
pw=0.135; gx=0.008; cw=3*pw+2*gx; colx=[0.04,0.04+cw+0.06]; ph=pw*9.8/8.6; rowh=ph+0.115; ytop=0.955
for k,(l,src,o,t1,t2) in enumerate(casos):
    x,y=xy(src,o); cx=colx[k%2]; yy=ytop-(k//2+1)*rowh+0.06
    if inCB(x,y,60): imgs=[(chip(CB,(4,3,2),x,y,60),60,'A: CBERS-4A 2 m\n(120 m)')]
    else: imgs=[(chip(S2,(3,2,1),x,y,100),100,'A: Sentinel-2 10 m\n(200 m)')]
    imgs+=[(chip(S2,(3,2,1),x,y,150),150,'B: Sentinel-2\n(300 m)'),(chip(S2,(7,3,2),x,y,150),150,'B: Sentinel-2 8-4-3\n(300 m)')]
    for j,(im,h,tt) in enumerate(imgs):
        ax=fig.add_axes([cx+j*(pw+gx),yy,pw,ph]); ax.imshow(im,extent=(-h,h,-h,h),interpolation='nearest'); ax.set_xticks([]); ax.set_yticks([])
        ax.add_patch(Rectangle((-10,-10),20,20,fill=False,ec='red',lw=1.6)); ax.set_title(tt,fontsize=FS-1.5,pad=2)
    lab=f'({l}) Punto {o}' if src=='rev' else f'({l}) Franja, punto {o}'
    fig.text(cx+cw/2,yy-0.012,f'{lab} — {t1}\n{t2}',ha='center',va='top',fontsize=FS-1)
xn=colx[1]+cw+0.03
fig.add_artist(FancyArrow(xn,ytop-0.11,0,0.08,width=0.0025,head_width=0.013,head_length=0.03,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,ytop-0.025,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
fig.savefig('Tp10_Figura_18.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
