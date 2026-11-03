import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.colors import ListedColormap
plt.rcParams['font.family']='Liberation Serif'
r=rasterio.open('/mnt/user-data/uploads/02_Practica/Tp10_Impacto_urbano/02_Subsets_SNAP_QGIS/B_CONCORDIA_compuestos_2026-09-16_20m.tif')
D=r.descriptions; b=r.bounds; EXT=(b.left,b.right,b.bottom,b.top); FS=12
def rd(n): return r.read(D.index(n)+1,out_shape=(r.height//2,r.width//2)).astype('f4')
def st(a,lo,hi): return np.clip((a-lo)/(hi-lo),0,1)
s2=np.dstack([st(rd(x),0.0128,0.1455) for x in ('B04','B03','B02')]); s2[~np.isfinite(s2).all(2)]=1
vv=rd('C_VV_dB'); vh=rd('C_VH_dB')
s1=np.dstack([st(vv,-20.3,-5.3),st(vh,-24.8,-11.9),st(vv-vh,2.7,9.6)]); s1[~np.isfinite(s1).all(2)]=1
ne=rd('n_escenas_S2')
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
W=9.6; H=3.45
fig=plt.figure(figsize=(W,H))
ha=0.75; y0=0.2; wa=ha*H/W*(EXT[1]-EXT[0])/(EXT[3]-EXT[2]); gx=0.03; x0=0.07
cols=['#c62828','#f4845f','#ffd166','#9ecae1','#3b6fb6']
tit=['(a) Sentinel-2, mediana de 4 escenas\n(14/09 a 06/10/2026), color natural','(b) Sentinel-1, R = VV, G = VH,\nB = VV/VH, media de 5 pasadas','(c) Escenas ópticas sin\nnube por píxel']
axs=[]
for k,img in enumerate((s2,s1,ne)):
    ax=fig.add_axes([x0+k*(wa+gx),y0,wa,ha])
    if k<2: ax.imshow(img,extent=EXT,interpolation='nearest')
    else: im=ax.imshow(img,extent=EXT,cmap=ListedColormap(cols),vmin=-0.5,vmax=4.5,interpolation='nearest')
    ax.set_xlim(EXT[0],EXT[1]); ax.set_ylim(EXT[2],EXT[3])
    ax.xaxis.set_major_locator(MultipleLocator(10000)); ax.yaxis.set_major_locator(MultipleLocator(10000))
    ax.xaxis.set_major_formatter(FuncFormatter(fk)); ax.yaxis.set_major_formatter(FuncFormatter(fk))
    ax.tick_params(labelsize=FS,length=3,pad=2); ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS)
    if k==0: ax.set_ylabel('Norte (km)',fontsize=FS)
    else: ax.set_yticklabels([])
    ax.set_title(tit[k],fontsize=FS,pad=4); axs.append(ax)
b2=axs[2].get_position(); b0=axs[0].get_position()
fig.legend(handles=[Patch(fc=c,ec='0.4',lw=0.4,label=str(i)) for i,c in enumerate(cols)],title='escenas',title_fontsize=FS-1,loc='center left',bbox_to_anchor=(b2.x1+0.005,y0+ha*0.35),fontsize=FS-1,frameon=False,handlelength=1.2)
xn=b2.x1+0.04; yt=b2.y1
fig.add_artist(FancyArrow(xn,yt-0.18,0,0.14,width=0.0025,head_width=0.014,head_length=0.045,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.035,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
L=10000; frac=L/(EXT[1]-EXT[0])*wa; xs=b2.x1-frac-0.02; ys=0.02; hb=0.025
sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for q in range(2): sa.add_patch(Rectangle((q*0.5,0),0.5,1,fc=['black','white'][q],ec='black',lw=0.8))
fig.text(xs-0.006,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(xs+frac+0.006,ys+hb/2,'10 km',ha='left',va='center',fontsize=FS)
fig.savefig('Tp10_Figura_10.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
