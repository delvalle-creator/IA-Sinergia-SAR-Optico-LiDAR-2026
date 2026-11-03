import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap
from rasterio.windows import from_bounds
plt.rcParams['font.family']='Liberation Serif'
U='/mnt/user-data/uploads/02_Practica/'
Z=(394000,416500,6515000,6537500); FS=11
s=rasterio.open(U+'00_COMUN/09_Herramientas/desarrollo_docente/Tp10/B_CONCORDIA_S2_20260904_10m.tif')
w=from_bounds(Z[0],Z[2],Z[1],Z[3],s.transform)
s2=np.stack([s.read(b,window=w,out_shape=(1125,1125)) for b in (3,2,1)]).astype('f4')
s2=np.clip((s2-0.0128)/(0.1455-0.0128),0,1).transpose(1,2,0); s2=0.6*s2+0.4
e=rasterio.open(U+'Tp10_Impacto_urbano/05_Resultados/02_Rasters/B_CONCORDIA_expansion_2019_2026.tif')
c=e.read(1,window=from_bounds(Z[0],Z[2],Z[1],Z[3],e.transform))
lut=np.full(7,np.nan); lut[1]=0; lut[2]=1; lut[4]=2; lut[5]=3
ci=np.where((c>=1)&(c<=5),lut[np.clip(c,0,6).astype(int)],np.nan)
cols=['#6e6e6e','#e00000','#1f6fe0','#ffd21f']; cm=ListedColormap(cols)
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
W=9.45; H=5.6
fig=plt.figure(figsize=(W,H))
hm=0.80; y0=0.12; wm=hm*H/W
ax=fig.add_axes([0.085,y0,wm,hm])
ax.imshow(s2,extent=Z,interpolation='bilinear')
ci[(ci==1)|(ci==2)]=np.nan
ax.imshow(ci,extent=Z,cmap=cm,vmin=-0.5,vmax=3.5,interpolation='nearest')
from scipy import ndimage
for k,col in ((4,'#1f6fe0'),(2,'#e00000')):
    g0=ndimage.binary_dilation(c==k,iterations=6)
    ax.imshow(np.where(g0,1.0,np.nan),extent=Z,cmap=ListedColormap(['black']),vmin=0,vmax=2,interpolation='nearest')
    g=ndimage.binary_dilation(c==k,iterations=5)
    ax.imshow(np.where(g,1.0,np.nan),extent=Z,cmap=ListedColormap([col]),vmin=0,vmax=2,interpolation='nearest')
ax.set_xlim(Z[0],Z[1]); ax.set_ylim(Z[2],Z[3])
ax.set_xticks(range(396000,416001,4000)); ax.set_yticks(range(6516000,6537001,4000))
ax.xaxis.set_major_formatter(FuncFormatter(fk)); ax.yaxis.set_major_formatter(FuncFormatter(fk)); ax.tick_params(labelsize=FS)
ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS,labelpad=2); ax.set_ylabel('Norte (km, UTM 21 S)',fontsize=FS)
ax.set_title('Expansión urbana 2019–2026, Concordia (Argentina) y Salto (Uruguay)',fontsize=FS+1,fontweight='bold',pad=5)
b=ax.get_position(); xc=b.x1+0.035
# norte: esquinero superior derecho, fuera del mapa
xn=0.975; yt=b.y1+0.03
fig.add_artist(FancyArrow(xn,yt-0.15,0,0.11,width=0.0025,head_width=0.016,head_length=0.04,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.03,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
# escala horizontal, fuera del mapa
L=5000; frac=L/(Z[1]-Z[0])*wm; xs=b.x0+(b.width-frac)/2; ys=0.0; hb=0.02
sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for q in range(2): sa.add_patch(Rectangle((q*0.5,0),0.5,1,fc=['black','white'][q],ec='black',lw=0.8))
fig.text(xs-0.006,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(xs+frac+0.006,ys+hb/2,'5 km',ha='left',va='center',fontsize=FS)
labs=['1 urbano en las dos fechas (4.360,7 ha)','2 nuevo urbano (38,6 ha)*','4 urbano sólo en 2019, a revisar (11,0 ha)*','5 sin decidir (2.510,2 ha)','3 no urbano (sin color)']
NOTA=1
fig.legend(handles=[Patch(fc=c,ec='0.3',lw=0.5,label=l) for c,l in zip(cols,labs[:4])],title='Clases del mapa de cambio',title_fontsize=FS,
           loc='upper left',bbox_to_anchor=(xc-0.008,b.y1+0.01),fontsize=FS,frameon=False,handlelength=1.4,labelspacing=0.25,alignment='left')
fig.text(xc,b.y1-0.205,'3 no urbano: sin color (se ve el fondo)\n* manchas agrandadas 100 m para que se vean',fontsize=FS,va='top')
txt=[('Método:','Random Forest por año (Sentinel-1 +\nSentinel-2) y comparación posterior a la\nclasificación; cambio sólo si p ≥ 0,60 en las\ndos fechas y mancha ≥ 5 píxeles de 20 m.'),
     ('Fechas:','Sentinel-1 RTC, órbita 68: 14/10–13/11/2019\ny 20/09–14/10/2026. Sentinel-2 L2A: 06/10–\n20/11/2019 y 14/09–19/10/2026. Fondo:\nSentinel-2 del 04/09/2026.'),
     ('Exactitud:','el cambio NO está validado. El mapa\nurbano de 2026 (multisensor) tiene exactitud\ndel usuario 0,857 ± 0,099 (IC del 95 %),\nque no se traslada al cambio.'),
     ('Fuente:','ESA – Copernicus, Sentinel-1 y Sentinel-2,\nMicrosoft Planetary Computer; MapBiomas\nArgentina, Col. 3. Elaboración propia (Tp10_03).')]
y=b.y1-0.325
for k,t in txt:
    tt=fig.text(xc,y,k+' '+t,fontsize=FS,va='top',linespacing=1.15)
    y-=0.026*(t.count('\n')+1)*1.15/0.6*0.6+0.03
fig.savefig('Tp10_Figura_21.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
