import numpy as np, rasterio as r, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow
from rasterio.warp import reproject, Resampling
from scipy import ndimage
plt.rcParams['font.family']='Liberation Serif'; FS=11
U='/mnt/user-data/uploads/CURSOS_CEREGEO_2026/02_Practica/Tp9_Deforestacion/02_Subsets_SNAP_QGIS/'
p=r.open(U+'C_pila_temporal_20m.tif')
def db(x): return 10*np.log10(np.where(x>0,x,np.nan))
def ag(ruta):
    s=r.open(ruta); o=np.full(p.shape,np.nan); a=s.read(1).astype('f8'); a[a<=0]=np.nan
    reproject(a,o,src_transform=s.transform,src_crs=s.crs,dst_transform=p.transform,dst_crs=p.crs,resampling=Resampling.bilinear,src_nodata=np.nan,dst_nodata=np.nan); return o
SA=U+'SAOCOM_gamma0/QGIS_GeoTIFF/C_FEDERAL_SAOCOM_L_%s_QP_gamma0_Gamma0_HV.tif'
dS=db(ag(SA%'20260911'))-db(ag(SA%'20210804')); dL=db(p.read(5).astype('f8'))-db(p.read(2).astype('f8'))
rS=dS-np.nanmedian(dS); rL=dL-np.nanmedian(dL)
def sm(x):
    m=np.isfinite(x); v=ndimage.uniform_filter(np.where(m,x,0),3); w=ndimage.uniform_filter(m.astype(float),3)
    o=v/np.maximum(w,1e-9); o[~m]=np.nan; return o
b=p.bounds; E=(b.left,b.right,b.bottom,b.top)
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
def fn(v,_): return ('%g'%v).replace('-','−').replace('.',',')
W,H=9.6,4.3
fig=plt.figure(figsize=(W,H))
h=0.74; w=h*H/W*(E[1]-E[0])/(E[3]-E[2]); y=0.22
cm=plt.get_cmap('RdBu').copy(); cm.set_bad('white')
axs=[]
for k,(arr,t) in enumerate([(sm(rS),'(a) SAOCOM: 11/09/2026 frente a 04/08/2021'),(sm(rL),'(b) NISAR 2026 frente a ALOS-2 2021')]):
    ax=fig.add_axes([0.065+k*(w+0.02),y,w,h]); im=ax.imshow(arr,extent=E,cmap=cm,vmin=-6,vmax=6,interpolation='nearest')
    ax.set_xlim(E[0],E[1]); ax.set_ylim(E[2],E[3])
    for a_ in (ax.xaxis,ax.yaxis): a_.set_major_locator(MultipleLocator(10000)); a_.set_major_formatter(FuncFormatter(fk))
    ax.tick_params(labelsize=FS,length=3,pad=2); ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS)
    if k==0: ax.set_ylabel('Norte (km)',fontsize=FS)
    else: ax.set_yticklabels([])
    ax.set_title(t,fontsize=FS,pad=3); axs.append(ax)
b1=axs[1].get_position()
b0_=axs[0].get_position(); cax=fig.add_axes([b0_.x0+0.05,0.05,b1.x1-b0_.x0-0.1,0.03]); cb=fig.colorbar(im,cax=cax,orientation='horizontal',ticks=[-6,-4,-2,0,2,4,6],format=FuncFormatter(fn)); cb.ax.tick_params(labelsize=FS)
cb.set_label('ΔHV menos la mediana del sitio (dB); rojo = el HV bajó',fontsize=FS)
# panel c
ax3=fig.add_axes([0.805,0.25,0.19,0.69])
cl=['Pérdida','Degradación','Monte\nestable','No bosque\nestable']; sv=[66.5,13.1,2.7,7.6]; nv=[96.3,54.1,9.6,9.9]
yy=np.arange(4)[::-1]; bh=0.38
b_=ax3.barh(yy+bh/2,sv,bh,color='#7b3294',label='SAOCOM'); c_=ax3.barh(yy-bh/2,nv,bh,color='#e66101',label='NISAR frente a ALOS-2')
for rr,v in list(zip(b_,sv))+list(zip(c_,nv)): ax3.text(v+2,rr.get_y()+rr.get_height()/2,('%.1f'%v).replace('.',','),ha='left',va='center',fontsize=FS-1)
ax3.set_yticks(yy); ax3.set_yticklabels(cl,fontsize=FS); ax3.set_xlim(0,125); ax3.set_xticks([0,25,50,75,100]); ax3.tick_params(labelsize=FS)
ax3.set_xlabel('% de píxeles con ΔHV\nrelativo < −3 dB',fontsize=FS); ax3.set_title('(c) Por clase del mapa',fontsize=FS,pad=3)
for s_ in ('top','right'): ax3.spines[s_].set_visible(False)
ax3.legend(fontsize=FS-1,frameon=False,loc='upper center',bbox_to_anchor=(0.3,-0.3))
# escala y norte
b0=axs[0].get_position(); L=10000; frac=L/(E[1]-E[0])*b0.width; ys=-0.08; hb=0.025
sa=fig.add_axes([b0.x0,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for i in range(2): sa.add_patch(Rectangle((i*0.5,0),0.5,1,fc=['black','white'][i],ec='black',lw=0.8))
fig.text(b0.x0-0.005,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(b0.x0+frac+0.005,ys+hb/2,'10 km',ha='left',va='center',fontsize=FS)
xn=b1.x1-0.08; yt=b1.y1
fig.add_artist(FancyArrow(xn+0.10,yt-0.16,0,0.13,width=0.003,head_width=0.013,head_length=0.045,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn+0.10,yt-0.025,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
fig.savefig('Tp9_Figura_17.png',dpi=300,bbox_inches='tight',pad_inches=0.04)
k=np.isfinite(rS); print('mediana dS',np.nanmedian(dS),'dL',np.nanmedian(dL))
