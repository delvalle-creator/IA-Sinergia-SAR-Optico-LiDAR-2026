import numpy as np, rasterio, geopandas as gpd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.lines import Line2D
plt.rcParams['font.family']='Liberation Serif'
U='/mnt/user-data/uploads/02_Practica/Tp10_Impacto_urbano/'
r=rasterio.open(U+'05_Resultados/02_Rasters/E_PARANA_DIAMANTE_velocidad_vertical.tif'); b=r.bounds; EXT=(b.left,b.right,b.bottom,b.top)
v=r.read(1).astype('f4'); v[v==-9999]=np.nan; dsp=r.read(3).astype('f4'); dsp[dsp==-9999]=np.nan
ref=gpd.read_file(U+'04_Tablas_de_trabajo/referencia_estable_E.gpkg'); ctl=gpd.read_file(U+'04_Tablas_de_trabajo/control_estable_E.gpkg')
Z=(161000,174000,6476000,6487000); FS=14
cmv=plt.get_cmap('RdBu').copy(); cmv.set_bad('#d9d9d9'); cmd=plt.get_cmap('viridis').copy(); cmd.set_bad('#d9d9d9')
def fk(x,_): return f'{x/1000:,.0f}'.replace(',','.')
neg=FuncFormatter(lambda x,_: f'{x:,.0f}'.replace(',','.').replace('-','−'))
W=10.2; H=5.6
fig=plt.figure(figsize=(W,H))
ha=0.78; y0=0.14; wa=ha*H/W*(EXT[1]-EXT[0])/(EXT[3]-EXT[2]); wz=0.43; hz=wz*W/H*(Z[3]-Z[2])/(Z[1]-Z[0])
ax1=fig.add_axes([0.075,y0,wa,ha]); ax2=fig.add_axes([0.075+wa+0.02,y0,wa,ha]); ax3=fig.add_axes([0.075+2*wa+0.09,y0+ha-hz,wz,hz])
im1=ax1.imshow(v,extent=EXT,cmap=cmv,vmin=-30,vmax=30,interpolation='nearest')
im2=ax2.imshow(dsp,extent=EXT,cmap=cmd,vmin=0,vmax=1000,interpolation='nearest')
ax3.imshow(v,extent=EXT,cmap=cmv,vmin=-30,vmax=30,interpolation='nearest')
ref.boundary.plot(ax=ax3,color='black',lw=1.4); 
for ax,ms in ((ax1,7),(ax3,9)): ax.scatter(ctl.geometry.x,ctl.geometry.y,marker='^',s=ms**2,c='yellow',edgecolors='black',linewidths=0.8,zorder=5)
ax1.add_patch(Rectangle((Z[0],Z[2]),Z[1]-Z[0],Z[3]-Z[2],fill=False,ec='black',lw=1.3)); ax1.text(Z[0]-300,Z[3]+500,'(c)',fontsize=FS-1,ha='right')
for k,(ax,ext,st,tit) in enumerate(((ax1,EXT,10000,'(a) Velocidad vertical'),(ax2,EXT,10000,'(b) Dispersión entre pares'),(ax3,Z,4000,'(c) Casco de Paraná ampliado'))):
    ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3])
    ax.xaxis.set_major_locator(MultipleLocator(st)); ax.yaxis.set_major_locator(MultipleLocator(st))
    ax.xaxis.set_major_formatter(FuncFormatter(fk)); ax.yaxis.set_major_formatter(FuncFormatter(fk)); ax.tick_params(labelsize=FS,length=3,pad=2)
    ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS); ax.set_title(tit,fontsize=FS,pad=4)
    if k==1: ax.set_yticklabels([])
    else: ax.set_ylabel('Norte (km)',fontsize=FS)
b1=ax1.get_position(); b2=ax2.get_position(); b3=ax3.get_position()
for im,bb,lab,tk in ((im1,b1,'Velocidad (mm/año;\nnegativo = hundimiento)',[-30,-15,0,15,30]),(im2,b2,'Dispersión (mm/año)',[0,500,1000])):
    cax=fig.add_axes([bb.x0,0.02,bb.width,0.022]); cb=fig.colorbar(im,cax=cax,orientation='horizontal',ticks=tk,extend='both' if im is im1 else 'max')
    cb.ax.tick_params(labelsize=FS-1); cb.ax.xaxis.set_major_formatter(neg); cb.set_label(lab,fontsize=FS-1,labelpad=1)
# norte
xn=b3.x1+0.03; yt=b3.y1
fig.add_artist(FancyArrow(xn,yt-0.16,0,0.12,width=0.0025,head_width=0.014,head_length=0.04,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.03,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
def esc(x,y,frac,lab,tag,hb=0.02):
    sa=fig.add_axes([x,y,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
    for q in range(2): sa.add_patch(Rectangle((q*0.5,0),0.5,1,fc=['black','white'][q],ec='black',lw=0.8))
    fig.text(x-0.006,y+hb/2,tag+'   0',ha='right',va='center',fontsize=FS); fig.text(x+frac+0.006,y+hb/2,lab,ha='left',va='center',fontsize=FS)
esc(b3.x0+0.06,b3.y0-0.155,4000/(Z[1]-Z[0])*b3.width,'4 km','(c)')
esc(b3.x0+0.06,b3.y0-0.215,10000/(EXT[1]-EXT[0])*b1.width,'10 km','(a) y (b)')
h=[Patch(fc='white',ec='black',lw=1.4,label='zona de referencia (6 cuadrados de 120 m)'),Line2D([],[],ls='',marker='^',ms=9,mfc='yellow',mec='black',label='15 puntos de control'),
   Patch(fc='#d9d9d9',ec='0.5',lw=0.5,label='sin velocidad (coherencia insuficiente)'),Patch(fc='white',ec='black',lw=1.3,label='(c): área ampliada')]
fig.legend(handles=h,loc='upper left',bbox_to_anchor=(b3.x0-0.01,b3.y0-0.25),fontsize=FS-1,frameon=False,handlelength=1.4)
fig.savefig('Tp10_Figura_16.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
