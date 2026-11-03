import numpy as np, rasterio, geopandas as gpd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.lines import Line2D
plt.rcParams['font.family']='Liberation Serif'
U='/mnt/user-data/uploads/02_Practica/Tp10_Impacto_urbano/'
r=rasterio.open(U+'05_Resultados/02_Rasters/E_PARANA_DIAMANTE_velocidad_vertical.tif'); b=r.bounds; EXT=(b.left,b.right,b.bottom,b.top)
v=r.read(1).astype('f4'); v[v==-9999]=np.nan
ref=gpd.read_file(U+'04_Tablas_de_trabajo/referencia_estable_E.gpkg'); ctl=gpd.read_file(U+'04_Tablas_de_trabajo/control_estable_E.gpkg')
Z=(160000,174000,6470000,6490000); FS=11
cmv=plt.get_cmap('RdBu').copy(); cmv.set_bad('#d9d9d9')
def fk(x,_): return f'{x/1000:,.0f}'.replace(',','.')
neg=FuncFormatter(lambda x,_: f'{x:,.0f}'.replace(',','.').replace('-','−'))
W=8.6; H=5.7
fig=plt.figure(figsize=(W,H))
hm=0.82; y0=0.11; wm=hm*H/W*(Z[1]-Z[0])/(Z[3]-Z[2])
ax=fig.add_axes([0.085,y0,wm,hm])
im=ax.imshow(v,extent=EXT,cmap=cmv,vmin=-30,vmax=30,interpolation='nearest')
rc=ref.geometry.centroid
ax.scatter(rc.x,rc.y,marker='s',s=45,c='black',edgecolors='white',linewidths=0.8,zorder=5)
ax.scatter(ctl.geometry.x,ctl.geometry.y,marker='^',s=85,c='yellow',edgecolors='black',linewidths=0.9,zorder=6)
ax.set_xlim(Z[0],Z[1]); ax.set_ylim(Z[2],Z[3])
ax.set_xticks(range(160000,174001,4000)); ax.set_yticks(range(6472000,6490001,4000))
ax.xaxis.set_major_formatter(FuncFormatter(fk)); ax.yaxis.set_major_formatter(FuncFormatter(fk)); ax.tick_params(labelsize=FS)
ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS,labelpad=2); ax.set_ylabel('Norte (km, UTM 21 S)',fontsize=FS)
ax.set_title('Velocidad vertical, Paraná (Entre Ríos), junio 2025 a julio 2026',fontsize=FS+1,fontweight='bold',pad=5,loc='left')
bb=ax.get_position(); xc=bb.x1+0.05
xn=0.975; yt=bb.y1+0.03
fig.add_artist(FancyArrow(xn,yt-0.15,0,0.11,width=0.0025,head_width=0.016,head_length=0.04,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.03,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
L=4000; frac=L/(Z[1]-Z[0])*wm; xs=bb.x0+(bb.width-frac)/2; ys=0.0; hb=0.02
sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for q in range(2): sa.add_patch(Rectangle((q*0.5,0),0.5,1,fc=['black','white'][q],ec='black',lw=0.8))
fig.text(xs-0.006,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(xs+frac+0.006,ys+hb/2,'4 km',ha='left',va='center',fontsize=FS)
h=[Line2D([],[],ls='',marker='s',ms=7,mfc='black',mec='white',label='zona de referencia (6 cuadrados de 120 m)*'),
   Line2D([],[],ls='',marker='^',ms=9,mfc='yellow',mec='black',label='puntos de control (12 en esta vista; 15 en total)'),
   Patch(fc='#d9d9d9',ec='0.5',lw=0.5,label='sin velocidad (coherencia insuficiente)')]
fig.legend(handles=h,loc='upper left',bbox_to_anchor=(xc-0.012,bb.y1+0.01),fontsize=FS,frameon=False,handlelength=1.4,labelspacing=0.3)
fig.text(xc,bb.y1-0.155,'* agrandados para que se vean',fontsize=FS,va='top')
cax=fig.add_axes([xc,bb.y1-0.27,0.36,0.03]); cb=fig.colorbar(im,cax=cax,orientation='horizontal',ticks=[-30,-20,-10,0,10,20,30],extend='both')
cb.ax.tick_params(labelsize=FS); cb.ax.xaxis.set_major_formatter(neg); cb.set_label('Velocidad (mm/año; negativo = hundimiento)',fontsize=FS,labelpad=2)
txt=['Método: apilado de tasas de 120 interferogramas\nHyP3 (Sentinel-1, órbita 141 descendente,\n01/06/2025 a 03/07/2026, píxel de 40 m); no es\nuna inversión SBAS. Velocidad vertical suponiendo\nque no hay movimiento horizontal; dato en el\n8,7 % del sitio.',
     'Control en 15 puntos estables: media −1,5 mm/año,\ndesvío 4,9, error de la media 1,3; cumple\n(1,5 < 2,5). Sin el par del 22/04 al 09/06/2026,\nque tiene saltos de desenrollado, no cumple.\nIncertidumbre de la velocidad no cuantificada.',
     'Fuente: ESA – Copernicus, Sentinel-1 IW SLC;\nASF DAAC HyP3 INSAR_GAMMA. Elaboración\npropia (Tp10_05).']
y=bb.y1-0.39
for t in txt:
    fig.text(xc,y,t,fontsize=FS,va='top',linespacing=1.15); y-=0.0315*(t.count('\n')+1)+0.035
fig.savefig('Tp10_Figura_22.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
