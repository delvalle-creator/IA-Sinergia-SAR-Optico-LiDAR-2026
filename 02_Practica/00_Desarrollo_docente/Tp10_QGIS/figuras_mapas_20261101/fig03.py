import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap, BoundaryNorm
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
plt.rcParams['font.family']='Liberation Serif'
U='/mnt/user-data/uploads/02_Practica/Tp10_Impacto_urbano/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/B_CONCORDIA_MapBiomas_cobertura_1985_2025.tif'
SITIO=(380780,419280,6514300,6559000); PX=30; FS=11
nx=round((SITIO[1]-SITIO[0])/PX); ny=round((SITIO[3]-SITIO[2])/PX)
CL=[(3,'3 Bosques cerrados','#1f8d49'),(4,'4 Bosques abiertos','#7dc975'),(6,'6 Bosques inundables','#007785'),(9,'9 Silvicultura','#7a6c00'),
    (11,'11 Herbáceas inundables','#519799'),(12,'12 Herbáceas','#d6bc74'),(15,'15 Pastura','#edde8e'),(19,'19 Cultivos temporarios','#C27BA0'),
    (24,'24 Áreas urbanas','#d4271e'),(25,'25 Otras áreas no vegetadas','#db4d4f'),(33,'33 Ríos, lagunas, lagos y océano','#2532e4'),(36,'36 Cultivos perennes','#d082de')]
r=rasterio.open(U)
def anio(y):
    b=r.descriptions.index(f'cobertura_{y}')+1; dst=np.zeros((ny,nx),'u1')
    reproject(r.read(b),dst,src_transform=r.transform,src_crs=r.crs,dst_transform=from_origin(SITIO[0],SITIO[3],PX,PX),dst_crs='EPSG:32721',resampling=Resampling.nearest,src_nodata=0,dst_nodata=0)
    return dst
lut=np.zeros(256,'i2'); cols=['#ffffff']
for k,(v,l,c) in enumerate(CL,1): lut[v]=k; cols.append(c)
cmap=ListedColormap(cols); norm=BoundaryNorm(np.arange(-0.5,len(cols)),len(cols))
A={y:anio(y) for y in (1985,2000,2019,2025)}
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
W=8.6; H=4.75
fig=plt.figure(figsize=(W,H))
w=0.215; h=w*W/H*(SITIO[3]-SITIO[2])/(SITIO[1]-SITIO[0]); y0=0.30
for k,(y,x) in enumerate(((1985,0.075),(2025,0.075+w+0.03))):
    ax=fig.add_axes([x,y0,w,h]); ax.imshow(lut[A[y]],extent=SITIO,cmap=cmap,norm=norm,interpolation='nearest')
    ax.set_xlim(SITIO[0],SITIO[1]); ax.set_ylim(SITIO[2],SITIO[3])
    ax.xaxis.set_major_locator(MultipleLocator(10000)); ax.yaxis.set_major_locator(MultipleLocator(10000))
    ax.xaxis.set_major_formatter(FuncFormatter(fk)); ax.yaxis.set_major_formatter(FuncFormatter(fk))
    ax.tick_params(labelsize=FS,length=3,pad=2); ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS)
    if k==0: ax.set_ylabel('Norte (km)',fontsize=FS)
    else: ax.set_yticklabels([])
    ax.set_title(f'({"ab"[k]}) MapBiomas {y}',fontsize=FS,pad=3)
    if k==1: bmap=ax.get_position()
    else: amap=ax.get_position()
# flecha del norte: esquinero superior derecho de los mapas, fuera
xn=bmap.x1+0.03; yt=bmap.y1
fig.add_artist(FancyArrow(xn,yt-0.16,0,0.12,width=0.003,head_width=0.016,head_length=0.04,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.03,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
# escala gráfica horizontal, fuera, bajo los dos mapas
L=10000; frac=L/(SITIO[1]-SITIO[0])*w; ys=y0-0.135; hb=0.02; xs=(amap.x0+bmap.x1)/2-frac/2
sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for i in range(2): sa.add_patch(Rectangle((i*0.5,0),0.5,1,fc=['black','white'][i],ec='black',lw=0.8))
fig.text(xs-0.006,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(xs+frac+0.006,ys+hb/2,'10 km',ha='left',va='center',fontsize=FS)
# (c) superficie por clase, lado argentino
ax=fig.add_axes([0.66,y0,0.32,h]); yrs=[1985,2000,2019,2025]; base=np.zeros(4)
for v,l,c in CL:
    s=np.array([(A[y]==v).sum()*PX*PX/1e4/1000 for y in yrs]); ax.bar(range(4),s,bottom=base,color=c,edgecolor='black',lw=0.4,width=0.7); base+=s
ax.set_xticks(range(4)); ax.set_xticklabels(yrs); ax.tick_params(labelsize=FS)
ax.set_ylabel('Superficie (miles de ha)',fontsize=FS); ax.set_title('(c) Superficie por clase (lado argentino)',fontsize=FS,pad=3)
ax.spines[['top','right']].set_visible(False)
# leyenda oficial, fuera, abajo
fig.legend(handles=[Patch(fc=c,ec='black',lw=0.4,label=l) for v,l,c in CL],loc='lower center',bbox_to_anchor=(0.53,-0.03),ncol=4,fontsize=FS-0.5,frameon=False,handlelength=1.6,columnspacing=1.2)
fig.savefig('Tp10_Figura_03.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok', base)
