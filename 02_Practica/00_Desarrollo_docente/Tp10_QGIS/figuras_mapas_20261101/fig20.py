import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap
plt.rcParams['font.family']='Liberation Serif'
U='/mnt/user-data/uploads/02_Practica/'
K=np.load('knn.npz'); full=K['full'].astype('f4'); z=K['z']
SITIO=(380780,419280,6514300,6559010); Z=(396000,412000,6520000,6534000); FS=12
cp=rasterio.open(U+'Tp10_Impacto_urbano/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/B_CONCORDIA_AlphaEarth_embeddings_2025_10m_CP1_CP2_CP3_RGB_8bit.tif')
rgb=cp.read(out_shape=(3,cp.height//4,cp.width//4)).transpose(1,2,0)/255.
rf=rasterio.open(U+'Tp10_Impacto_urbano/05_Resultados/02_Rasters/B_CONCORDIA_variante_multisensor.tif')
from rasterio.windows import from_bounds
m=rf.read(1,window=from_bounds(Z[0],Z[2],Z[1],Z[3],rf.transform))
h=min(m.shape[0],z.shape[0]); w=min(m.shape[1],z.shape[1]); m=m[:h,:w]; zz=z[:h,:w]
comp=np.full(m.shape,3.0); comp[(m==1)&(zz==1)]=0; comp[(m==1)&(zz!=1)]=1; comp[(m!=1)&(zz==1)]=2; comp[(m==-9999)|(zz==0)]=np.nan
print('acuerdo %',np.nanmean((comp==0)|(comp==3))*100)
cc=['#c00000','#1b6e2a','#b6d96a','#3a6fd8','#e0a040']; cmc=ListedColormap(cc); full[full==0]=np.nan
c3=['#8b0000','#ff8c1a','#1f5fe0','#ececec']; cm3=ListedColormap(c3)
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
W=10.0; H=3.95
fig=plt.figure(figsize=(W,H))
hh=0.61; y0=0.33; wa=hh*H/W*(SITIO[1]-SITIO[0])/(SITIO[3]-SITIO[2]); wz=hh*H/W*(Z[1]-Z[0])/(Z[3]-Z[2])
def ejes(ax,ext,st,ylab,tit):
    ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3])
    if st==4000: ax.set_xticks([400000,404000,408000]); ax.set_yticks([6522000,6526000,6530000])
    else: ax.xaxis.set_major_locator(MultipleLocator(st)); ax.yaxis.set_major_locator(MultipleLocator(st))
    ax.xaxis.set_major_formatter(FuncFormatter(fk)); ax.yaxis.set_major_formatter(FuncFormatter(fk)); ax.tick_params(labelsize=FS,length=3,pad=2)
    ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS); ax.set_title(tit,fontsize=FS,pad=4)
    if ylab: ax.set_ylabel('Norte (km)',fontsize=FS)
    else: ax.set_yticklabels([])
ax1=fig.add_axes([0.065,y0,wa,hh]); ax1.imshow(rgb,extent=SITIO,interpolation='nearest'); ejes(ax1,SITIO,10000,True,'(a) Embeddings 2025:\nCP1-CP2-CP3 en RGB')
ax2=fig.add_axes([0.065+wa+0.015,y0,wa,hh]); ax2.imshow(full,extent=SITIO,cmap=cmc,vmin=0.5,vmax=5.5,interpolation='nearest'); ejes(ax2,SITIO,10000,False,'(b) kNN (k = 5)\ncon los 64 embeddings')
for ax in (ax1,ax2): ax.add_patch(Rectangle((Z[0],Z[2]),Z[1]-Z[0],Z[3]-Z[2],fill=False,ec='black',lw=1.2))
ax3=fig.add_axes([0.065+2*wa+0.08,y0,wz,hh]); ax3.imshow(comp,extent=Z,cmap=cm3,vmin=-0.5,vmax=3.5,interpolation='nearest'); ejes(ax3,Z,4000,True,'(c) Urbano: kNN frente al\nRandom Forest multisensor')
b1=ax1.get_position(); b2=ax2.get_position(); b3=ax3.get_position()
xn=b3.x1+0.03; yt=b3.y1
fig.add_artist(FancyArrow(xn,yt-0.2,0,0.16,width=0.0025,head_width=0.014,head_length=0.05,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.035,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
def esc(xs,frac,lab,tag,ys=0.165,hb=0.022):
    sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
    for q in range(2): sa.add_patch(Rectangle((q*0.5,0),0.5,1,fc=['black','white'][q],ec='black',lw=0.8))
    fig.text(xs-0.006,ys+hb/2,tag+'   0',ha='right',va='center',fontsize=FS); fig.text(xs+frac+0.006,ys+hb/2,lab,ha='left',va='center',fontsize=FS)
fa=10000/(SITIO[1]-SITIO[0])*wa; fz=4000/(Z[1]-Z[0])*wz
esc(b2.x0+(b2.width-fa)/2+0.02,fa,'10 km','(a) y (b)'); esc(b3.x0+0.08,fz,'4 km','(c)')
L1=['urbano','vegetación leñosa','herbáceas y cultivos','agua','suelo desnudo y otras']
L3=['urbano en los dos','sólo Random Forest','sólo kNN','no urbano en los dos']
fig.legend(handles=[Patch(fc=c,ec='0.4',lw=0.4,label=l) for c,l in zip(cc,L1)],loc='lower center',bbox_to_anchor=(0.5,0.035),ncol=5,fontsize=FS-1,frameon=False,handlelength=1.2,columnspacing=1.0)
fig.legend(handles=[Patch(fc=c,ec='0.4',lw=0.4,label=l) for c,l in zip(c3,L3)],loc='lower center',bbox_to_anchor=(0.5,-0.03),ncol=4,fontsize=FS-1,frameon=False,handlelength=1.2,columnspacing=1.0)
fig.savefig('Tp10_Figura_20.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
