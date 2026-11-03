import numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow, Patch
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap
from rasterio.windows import from_bounds
from scipy import ndimage
plt.rcParams['font.family']='Liberation Serif'
U='/mnt/user-data/uploads/02_Practica/'
D=U+'00_COMUN/09_Herramientas/desarrollo_docente/Tp10/'
S19=rasterio.open(D+'B_CONCORDIA_S2_20190921_10m.tif'); S26=rasterio.open(D+'B_CONCORDIA_S2_20260904_10m.tif')
CB=rasterio.open(U+'Tp10_Impacto_urbano/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/B_CONCORDIA_CBERS4A_CONCORDIA_20260715_pansharpened_2m.tif')
EX=rasterio.open(U+'Tp10_Impacto_urbano/05_Resultados/02_Rasters/B_CONCORDIA_expansion_2019_2026.tif')
M=[('A','1,96',413613,6526225),('B','1,28',399655,6528919),('C','1,52',410846,6524786)]
H=600; FS=14.5
def win(r,x,y): return from_bounds(x-H,y-H,x+H,y+H,r.transform)
def s2(r,x,y):
    a=np.stack([r.read(b,window=win(r,x,y)) for b in (3,2,1)]).astype('f4'); a=np.clip((a-0.0128)/(0.1455-0.0128),0,1); return a.transpose(1,2,0)
def cb(x,y):
    b=CB.bounds
    if not (b.left<x-H and x+H<b.right and b.bottom<y-H and y+H<b.top): return None
    a=np.stack([CB.read(k,window=win(CB,x,y)) for k in (4,3,2)]).astype('f4')
    for q in range(3):
        lo,hi=np.percentile(a[q][a[q]>0],(2,98)); a[q]=np.clip((a[q]-lo)/(hi-lo),0,1)
    return a.transpose(1,2,0)
cols=['#6e6e6e','#e00000','#ffffff','#1f6fe0','#ffd21f']; cm=ListedColormap(cols)
fig=plt.figure(figsize=(9.6,7.0))
w=0.195; gx=0.012; x0=0.17; hh=w*9.6/7.0; ytop=0.93
tit=['Sentinel-2\n21/09/2019','Sentinel-2\n04/09/2026','CBERS-4A 2 m\n15/07/2026','Clase de la\nexpansión']
ext=(-H,H,-H,H)
for i,(m,sup,x,y) in enumerate(M):
    c=EX.read(1,window=win(EX,x,y)); lab,n=ndimage.label(c==2); k=lab[lab.shape[0]//2-3:lab.shape[0]//2+4,lab.shape[1]//2-3:lab.shape[1]//2+4]; k=k[k>0]
    mask=np.isin(lab,np.bincount(k).argmax() if k.size else -1) if k.size else (c==2)
    yy=ytop-(i+1)*hh-i*0.015
    for j in range(4):
        ax=fig.add_axes([x0+j*(w+gx),yy,w,hh]); ax.set_xticks([]); ax.set_yticks([])
        if j==0: img=s2(S19,x,y)
        elif j==1: img=s2(S26,x,y)
        elif j==2: img=cb(x,y)
        if j<3:
            if img is None:
                ax.set_facecolor('#f2f2f2'); ax.text(0.5,0.5,'fuera de la\nescena CBERS-4A',ha='center',va='center',fontsize=FS-1,transform=ax.transAxes,color='0.35')
                for s in ax.spines.values(): s.set_edgecolor('0.7')
            else: ax.imshow(img,extent=ext,interpolation='nearest')
        else:
            ci=np.where((c>=1)&(c<=5),c-1,np.nan); ax.imshow(ci,extent=ext,cmap=cm,vmin=-0.5,vmax=4.5,interpolation='nearest')
        if not (j==2 and img is None):
            ax.contour(np.linspace(-H,H,mask.shape[1]),np.linspace(H,-H,mask.shape[0]),mask.astype(float),levels=[0.5],colors='cyan' if j<3 else 'black',linewidths=1.6)
            ax.set_xlim(-H,H); ax.set_ylim(-H,H)
        if i==0: ax.set_title(tit[j],fontsize=FS,pad=4)
    fig.text(x0-0.012,yy+hh/2,f'Mancha {m}\n{sup} ha\nE '+f'{x:,}'.replace(',','.')+'\nN '+f'{y:,}'.replace(',','.'),ha='right',va='center',fontsize=FS-0.5)
last=ytop-3*hh-2*0.015
xn=x0+4*w+3*gx+0.03
fig.add_artist(FancyArrow(xn,ytop-0.12,0,0.09,width=0.0025,head_width=0.014,head_length=0.03,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,ytop-0.022,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
frac=500/(2*H)*w; xs=x0+4*w+3*gx-frac-0.03; ys=last-0.045; hb=0.014
sa=fig.add_axes([xs,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for q in range(2): sa.add_patch(Rectangle((q*0.5,0),0.5,1,fc=['black','white'][q],ec='black',lw=0.8))
fig.text(xs-0.006,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(xs+frac+0.006,ys+hb/2,'500 m',ha='left',va='center',fontsize=FS)
labs=['1 urbano en las dos fechas','2 nuevo urbano','3 no urbano','4 urbano sólo en la base','5 sin decidir']
h=[Patch(fc=c,ec='0.3',lw=0.5,label=l) for c,l in zip(cols,labs)]+[Line2D([],[],color='cyan',lw=2,label='contorno de la mancha (imágenes)'),Line2D([],[],color='black',lw=2,label='contorno de la mancha (clase)')]
fig.legend(handles=h,loc='upper left',bbox_to_anchor=(0.0,last-0.06),ncol=4,fontsize=FS-1.5,frameon=False,handlelength=1.3,columnspacing=0.8)
fig.savefig('Tp10_Figura_14.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print('ok')
