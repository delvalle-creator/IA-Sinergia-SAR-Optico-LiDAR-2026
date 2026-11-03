import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
plt.rcParams['font.family']='Liberation Serif'
U='/mnt/user-data/uploads/02_Practica/'
SITIO=(380780,419280,6514300,6559000); Z=(396000,412000,6520000,6534000); FS=12
def g(path,bands,ext,px,res=Resampling.nearest,nod=-9999):
    r=rasterio.open(path); nx=round((ext[1]-ext[0])/px); ny=round((ext[3]-ext[2])/px); out=[]
    for b in bands:
        dst=np.full((ny,nx),np.nan,'f4')
        reproject(r.read(b).astype('f4'),dst,src_transform=r.transform,src_crs=r.crs,dst_transform=from_origin(ext[0],ext[3],px,px),dst_crs='EPSG:32721',resampling=res,src_nodata=nod,dst_nodata=np.nan)
        out.append(dst)
    return np.stack(out)
P=U+'Tp10_Impacto_urbano/02_Subsets_SNAP_QGIS/B_CONCORDIA_urbano_por_banda_20m.tif'
A=g(P,[9],SITIO,40)[0]; B=g(P,[9],Z,20)[0]
s2=g(U+'00_COMUN/09_Herramientas/desarrollo_docente/Tp10/B_CONCORDIA_S2_20260904_10m.tif',[3,2,1],Z,10,Resampling.average)
lo,hi=np.nanpercentile(s2,(2,98)); s2=np.clip((np.nan_to_num(s2)-lo)/(hi-lo),0,1).transpose(1,2,0)
cols=['#e6e6e6','#f7d23e','#f26b1d','#8b0000']; cm=ListedColormap(cols); cm.set_bad('white')
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
W=10.0; H=3.62
fig=plt.figure(figsize=(W,H))
def ejes(ax,ext,step,ylab,tit):
    ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3])
    ax.xaxis.set_major_locator(MultipleLocator(step)); ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.xaxis.set_major_formatter(FuncFormatter(fk)); ax.yaxis.set_major_formatter(FuncFormatter(fk))
    ax.tick_params(labelsize=FS,length=3,pad=2); ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS)
    if ylab: ax.set_ylabel('Norte (km)',fontsize=FS)
    ax.set_title(tit,fontsize=FS,pad=4)
    if step==4000: ax.set_xticks([400000,404000,408000]); ax.set_yticks([6522000,6526000,6530000])
ha=0.66; y0=0.28
wa=ha*H/W*(SITIO[1]-SITIO[0])/(SITIO[3]-SITIO[2])*0.86; hA=ha*0.86
wz=ha*H/W*(Z[1]-Z[0])/(Z[3]-Z[2])
ax1=fig.add_axes([0.065,y0,wa,hA]); ax1.imshow(A,extent=SITIO,cmap=cm,vmin=-0.5,vmax=3.5,interpolation='nearest')
ax1.add_patch(Rectangle((Z[0],Z[2]),Z[1]-Z[0],Z[3]-Z[2],fill=False,ec='black',lw=1.2))
ejes(ax1,SITIO,10000,True,'(a) Sitio completo')
x2=0.065+wa+0.055
ax2=fig.add_axes([x2,y0,wz,ha]); ax2.imshow(B,extent=Z,cmap=cm,vmin=-0.5,vmax=3.5,interpolation='nearest')
ejes(ax2,Z,4000,False,'(b) Concordia y Salto')
ax3=fig.add_axes([x2+wz+0.015,y0,wz,ha]); ax3.imshow(s2,extent=Z,interpolation='nearest')
ejes(ax3,Z,4000,False,'(c) Sentinel-2, 04/09/2026'); ax3.set_yticklabels([])
b3=ax3.get_position(); b2=ax2.get_position()
xn=b3.x1+0.025; yt=b3.y1
fig.add_artist(FancyArrow(xn,yt-0.2,0,0.16,width=0.0025,head_width=0.014,head_length=0.05,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.035,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
fig.legend(handles=[Patch(fc=c,ec='0.5',lw=0.4,label=l) for c,l in zip(cols+['white'],['ninguna banda','1 banda','2 bandas','3 bandas','sin dato en alguna banda'])],
           loc='lower left',bbox_to_anchor=(b2.x0-0.01,-0.02),ncol=3,fontsize=FS-1,frameon=False,handlelength=1.3,columnspacing=1.0)
L=4000; frac=L/(Z[1]-Z[0])*wz; xs=b3.x1-frac-0.03; ys=0.025; hb=0.025
sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for i in range(2): sa.add_patch(Rectangle((i*0.5,0),0.5,1,fc=['black','white'][i],ec='black',lw=0.8))
fig.text(xs-0.006,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(xs+frac+0.006,ys+hb/2,'4 km',ha='left',va='center',fontsize=FS)
fig.text(xs+frac/2,ys+hb+0.012,'(b) y (c)',ha='center',va='bottom',fontsize=FS-1)
ba=ax1.get_position(); La=10000; fa=La/(SITIO[1]-SITIO[0])*ba.width; xa=ba.x0+(ba.width-fa)/2
sb=fig.add_axes([xa,ys,fa,hb]); sb.set_xlim(0,1); sb.set_ylim(0,1); sb.axis('off')
for i in range(2): sb.add_patch(Rectangle((i*0.5,0),0.5,1,fc=['black','white'][i],ec='black',lw=0.8))
fig.text(xa-0.006,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(xa+fa+0.006,ys+hb/2,'10 km',ha='left',va='center',fontsize=FS)
fig.text(xa+fa/2,ys+hb+0.012,'(a)',ha='center',va='bottom',fontsize=FS-1)
fig.savefig('Tp10_Figura_07.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
