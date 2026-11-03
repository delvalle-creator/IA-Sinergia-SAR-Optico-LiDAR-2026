import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
plt.rcParams['font.family']='Liberation Serif'
U='/mnt/user-data/uploads/02_Practica/'; T=U+'Tp10_Impacto_urbano/02_Subsets_SNAP_QGIS/'
C={'A':(402200,6541710),'B':(403800,6530710),'C':(408600,6553190)}
FS=12; HALF=1200
def g(path,bands,ext,px,res=Resampling.bilinear,nod=None,dx=0,dy=0):
    r=rasterio.open(path); n=round((ext[1]-ext[0])/px); out=[]
    for b in bands:
        dst=np.full((n,n),np.nan,'f4'); a=r.read(b).astype('f4')
        kw=dict(dst_transform=from_origin(ext[0]-dx,ext[3]-dy,px,px),dst_crs='EPSG:32721',resampling=res,src_nodata=nod,dst_nodata=np.nan)
        if r.crs is None: reproject(a,dst,gcps=r.gcps[0],src_crs=r.gcps[1],**kw)
        else: reproject(a,dst,src_transform=r.transform,src_crs=r.crs,**kw)
        out.append(dst)
    return np.stack(out)
S2=U+'00_COMUN/09_Herramientas/desarrollo_docente/Tp10/B_CONCORDIA_S2_20260904_10m.tif'
R=T+'RGB_copol_cruzada_cociente/B_CONCORDIA_'
UB=T+'B_CONCORDIA_urbano_por_banda_20m.tif'; NS=T+'QGIS_GeoTIFF/B_CONCORDIA_NovaSAR1_S_20230913_Sigma0_HH_db.tif'
cat_cols=['#ebebeb','#1f6fe0','#2ca02c','#7e57c2','#e8393a','#e366b8','#ff9800','#8b0000']  # code=C+2S+4L
cat_lab={7:'las tres',1:'sólo C',4:'sólo L',2:'sólo S',6:'S y L, no C',3:'C y S, no L',5:'C y L, no S',0:'ninguna'}
fig=plt.figure(figsize=(9.45,6.2))
cols=['Sentinel-2\n04/09/2026','Sentinel-1 C\n14/09/2026','NISAR L\n18/09/2026','NovaSAR S, HH\n13/09/2023','Bandas que\nmarcan urbano']
filas=['A: plantación forestal\nal norte de Concordia','B: barrio arbolado\ndel norte de Concordia','C: plantación forestal\njunto al embalse']
w=0.172; gx=0.012; x0=0.075; hh=w*9.45/6.2; y_top=0.915
for i,k in enumerate('ABC'):
    cx,cy=C[k]; ext=(cx-HALF,cx+HALF,cy-HALF,cy+HALF)
    s2=g(S2,[3,2,1],ext,10,Resampling.average,-9999); lo,hi=0.0128,0.1455; s2=np.clip((s2-lo)/(hi-lo),0,1).transpose(1,2,0)
    s1=np.clip(g(R+'S1_C_20260914_RGB_8bit.tif',[1,2,3],ext,10,nod=0)/255,0,1).transpose(1,2,0)
    ni=np.clip(g(R+'NISAR_L_20260918_RGB_8bit.tif',[1,2,3],ext,10,nod=0)/255,0,1).transpose(1,2,0)
    ns=g(NS,[1],ext,10,nod=np.nan,dx=-40,dy=100)[0]
    m=g(UB,[6,7,8],ext,20,Resampling.nearest,-9999)
    code=(m[0]>0).astype(int)+2*(m[1]>0)+4*(m[2]>0); code=np.where(np.isfinite(m).all(0),code,np.nan)
    y=y_top-(i+1)*hh-i*0.012
    for j,(img,kw) in enumerate(((s2,{}),(s1,{}),(ni,{}),(ns,dict(cmap='gray',vmin=-20,vmax=2)),(code,dict(cmap=ListedColormap(cat_cols),vmin=-0.5,vmax=7.5)))):
        ax=fig.add_axes([x0+j*(w+gx),y,w,hh]); ax.imshow(img,extent=ext,interpolation='nearest',**kw)
        ax.set_xticks([]); ax.set_yticks([])
        if i==0: ax.set_title(cols[j],fontsize=FS-0.5,pad=4)
        if j==0: ax.set_ylabel(filas[i],fontsize=FS-0.5)
last=ax.get_position()
# norte, esquinero superior derecho, fuera
xn=last.x1+0.025; yt=y_top
fig.add_artist(FancyArrow(xn,yt-0.14,0,0.11,width=0.0025,head_width=0.014,head_length=0.035,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.025,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
# leyenda y escala, abajo, fuera
order=[7,1,4,2,6,3,5,0]
fig.legend(handles=[Patch(fc=cat_cols[c],ec='0.4',lw=0.4,label=cat_lab[c]) for c in order],loc='lower left',bbox_to_anchor=(0.04,0.005),ncol=8,fontsize=FS-1,frameon=False,handlelength=1.1,columnspacing=0.7,handletextpad=0.4)
L=1000; frac=L/(2*HALF)*w; xs=last.x1-frac-0.03; ys=0.055; hb=0.018
sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for q in range(2): sa.add_patch(Rectangle((q*0.5,0),0.5,1,fc=['black','white'][q],ec='black',lw=0.8))
fig.text(xs-0.006,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(xs+frac+0.006,ys+hb/2,'1 km',ha='left',va='center',fontsize=FS)
fig.savefig('Tp10_Figura_08.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
