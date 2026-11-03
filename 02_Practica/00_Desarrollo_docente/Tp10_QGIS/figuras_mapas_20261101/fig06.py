import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
plt.rcParams['font.family']='Liberation Serif'; plt.rcParams['mathtext.fontset']='custom'; plt.rcParams['mathtext.rm']='Liberation Serif'; plt.rcParams['mathtext.it']='Liberation Serif:italic'
U='/mnt/user-data/uploads/02_Practica/Tp10_Impacto_urbano/02_Subsets_SNAP_QGIS/'
EXT=(399000,413000,6519000,6533000); PX=20; FS=12
nx=round((EXT[1]-EXT[0])/PX); ny=round((EXT[3]-EXT[2])/PX); dtr=from_origin(EXT[0],EXT[3],PX,PX)
def g(path,b=1):
    r=rasterio.open(path); dst=np.full((ny,nx),np.nan,'f4'); a=r.read(b).astype('f4'); a[~(a>0)]=np.nan
    reproject(a,dst,src_transform=r.transform,src_crs=r.crs,dst_transform=dtr,dst_crs='EPSG:32721',resampling=Resampling.bilinear,src_nodata=np.nan,dst_nodata=np.nan)
    return 10*np.log10(dst)
SA=U+'SAOCOM_gamma0/QGIS_GeoTIFF/B_CONCORDIA_SAOCOM_L_20260916_QP_gamma0_Gamma0_'
hh=g(SA+'HH.tif'); vv=g(SA+'VV.tif')
r=rasterio.open(U+'B_CONCORDIA_urbano_por_banda_20m.tif'); nhh=g(U+'B_CONCORDIA_urbano_por_banda_20m.tif',r.descriptions.index('L_HH')+1)
d=hh-vv; S=hh>0; N=nhh>0
cat=np.full(hh.shape,np.nan); cat[S&N]=0; cat[S&~N]=1; cat[~S&N]=2
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
neg=FuncFormatter(lambda v,_: f'{v:.0f}'.replace('-','−'))
W=9.75; H=4.6
fig=plt.figure(figsize=(W,H))
w=0.27; h=w*W/H*(EXT[3]-EXT[2])/(EXT[1]-EXT[0]); y0=0.215
ax1=fig.add_axes([0.07,y0,w,h]); im=ax1.imshow(d,extent=EXT,cmap='RdBu_r',vmin=-6,vmax=6,interpolation='nearest')
ax2=fig.add_axes([0.07+w+0.03,y0,w,h]); ax2.imshow(hh,extent=EXT,cmap='gray',vmin=-22,vmax=4,interpolation='nearest')
cols=['#7b3294','#e66101','#2b8cff']; ax2.imshow(cat,extent=EXT,cmap=ListedColormap(cols),vmin=-0.5,vmax=2.5,interpolation='nearest')
for k,(ax,t) in enumerate(((ax1,'(a) SAOCOM 16/09/2026: HH − VV'),(ax2,'(b) Urbano con L HH > 0 dB'))):
    ax.set_xlim(EXT[0],EXT[1]); ax.set_ylim(EXT[2],EXT[3])
    ax.xaxis.set_major_locator(MultipleLocator(4000)); ax.yaxis.set_major_locator(MultipleLocator(4000))
    ax.xaxis.set_major_formatter(FuncFormatter(fk)); ax.yaxis.set_major_formatter(FuncFormatter(fk))
    ax.tick_params(labelsize=FS,length=3,pad=2); ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS); ax.set_title(t,fontsize=FS,pad=4)
    if k==0: ax.set_ylabel('Norte (km)',fontsize=FS)
    else: ax.set_yticklabels([])
b1=ax1.get_position(); b2=ax2.get_position()
cax=fig.add_axes([b1.x0,0.035,b1.width*0.68,0.03]); cb=fig.colorbar(im,cax=cax,orientation='horizontal',ticks=[-6,-4,-2,0,2,4,6])
cb.ax.tick_params(labelsize=FS); cb.ax.xaxis.set_major_formatter(neg); cb.set_label('HH − VV (dB)',fontsize=FS,labelpad=1)
fig.legend(handles=[Patch(fc=c,label=l) for c,l in zip(cols,['SAOCOM y NISAR','sólo SAOCOM (16/09)','sólo NISAR (18/09)'])],
           loc='upper left',bbox_to_anchor=(b2.x0-0.005,0.105),ncol=1,fontsize=FS-1,frameon=False,handlelength=1.4,labelspacing=0.25)
# norte y escala
xn=b2.x1+0.022; yt=b2.y1
fig.add_artist(FancyArrow(xn,yt-0.17,0,0.13,width=0.0025,head_width=0.014,head_length=0.045,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.03,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
L=2000; frac=L/(EXT[1]-EXT[0])*w; xs=b2.x1-frac-0.02; ys=0.155; hb=0.02
xs=b1.x0+b1.width*0.79
sa=fig.add_axes([xs,0.035,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for i in range(2): sa.add_patch(Rectangle((i*0.5,0),0.5,1,fc=['black','white'][i],ec='black',lw=0.8))
fig.text(xs-0.006,0.035+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(xs+frac+0.006,0.035+hb/2,'2 km',ha='left',va='center',fontsize=FS)
# (c) barras horizontales por clase
C=['urbano denso','urbano abierto','vegetación','suelo desnudo','agua']
V={'HH':[4.1,-1.4,-6.5,-10.1,-20.7],'VV':[-2.1,-6.0,-9.9,-11.0,-22.7],'HV':[-13.2,-12.8,-16.3,-20.5,-31.4]}
ax=fig.add_axes([0.825,y0,0.17,h]); y=np.arange(5)[::-1]; hb2=0.27
for j,(p,c) in enumerate(zip(('HH','VV','HV'),('#c0182b','#2a62b8','#4b9a2b'))): ax.barh(y-(j-1)*hb2,V[p],hb2,color=c,label=p)
ax.axvline(0,color='black',lw=0.8); ax.set_yticks(y); ax.set_yticklabels(C,fontsize=FS); ax.tick_params(labelsize=FS)
ax.xaxis.set_major_formatter(neg); ax.set_xlabel(r'$\gamma^0$ mediano (dB)',fontsize=FS); ax.set_xlim(-33,7); ax.set_xticks([-30,-20,-10,0])
ax.set_title('(c) SAOCOM por clase\n(polígonos de la Tabla 3)',fontsize=FS,pad=4); ax.spines[['top','right']].set_visible(False)
ax.legend(loc='upper center',bbox_to_anchor=(0.3,-0.2),ncol=3,fontsize=FS-1,frameon=False,handlelength=1.2,columnspacing=0.8)
fig.savefig('Tp10_Figura_06.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok',np.nanmedian(d))
