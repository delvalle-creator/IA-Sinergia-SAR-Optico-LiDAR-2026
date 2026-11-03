import pickle, numpy as np, rasterio, geopandas as gpd, os
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle, Polygon as MPoly
plt.rcParams['font.family']='Liberation Serif'; plt.rcParams['font.size']=11
CRS='EPSG:32721'; OUT='/home/claude/dron/out'
D=pickle.load(open('plan.pkl','rb')); E=pickle.load(open('plan2.pkl','rb')); X=pickle.load(open('exp.pkl','rb'))
LN,DL,G=E['LN'],E['DL'],E['G']; c,v,nrm=D['c'],D['v'],D['nrm']
def P(s,t): return c+s*v+t*nrm
Q='/mnt/user-data/uploads/CURSOS_CEREGEO_2026/02_Practica/Tp7_Barrancas_deslizamientos/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/E1_DIAMANTE_BARRANCA_'
x0,y0,x1,y1=D['aoi'].buffer(120).bounds; PX=2
T=from_origin(x0,y1,PX,PX); sh=(int((y1-y0)/PX),int((x1-x0)/PX))
def L(p,b,box=None):
    o=np.full(sh,np.nan,'f4')
    with rasterio.open(p) as s:
        a=s.read(b).astype('f4')
        if s.nodata is not None: a[a==s.nodata]=np.nan
        reproject(a,o,src_transform=s.transform,src_crs=s.crs,dst_transform=T,dst_crs=CRS,resampling=Resampling.bilinear,src_nodata=np.nan,dst_nodata=np.nan)
    return o
rgb=[L(Q+'CBERS4A_DIAMANTE_20260926_pansharpened_2m.tif',b) for b in (4,3,2)]
def st(a): lo,hi=np.nanpercentile(a,[2,98]); return np.clip((a-lo)/(hi-lo),0,1)
img=np.nan_to_num(np.dstack([st(a) for a in rgb]),nan=1)
ign=L(Q+'IGN_MDE_5m.tif',1); mos=L(Q+'IGN_MDE_mosaico2018.tif',1); mos[mos<=0]=np.nan; ign=np.where(np.isfinite(ign),ign,mos)
gr=gpd.read_file('/mnt/user-data/uploads/DIAMANTE/GRIETAS/grietadte.shp').to_crs(CRS)
fr=gpd.read_file('/mnt/user-data/outputs/t7h/E1_cicatriz_y_deposito.gpkg',layer='formas').to_crs(CRS)
COL=['#00e5ff','#76ff03','#ffea00','#ff9100']
def base(ax,ext):
    ax.imshow(img,extent=(x0,x1,y0,y1))
    Xg=np.linspace(x0,x1,sh[1]); Yg=np.linspace(y1,y0,sh[0])
    ax.contour(Xg,Yg,ign,levels=range(10,70,5),colors='#fff59d',linewidths=.35,alpha=.6)
    ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3]); ax.set_aspect('equal')
    ax.ticklabel_format(useOffset=False,style='plain'); ax.tick_params(labelsize=8)
    ax.set_xlabel('Este UTM 21S (m)',fontsize=9); ax.set_ylabel('Norte UTM 21S (m)',fontsize=9)
def escala(ax,ext,L=200):
    xa=ext[0]+0.05*(ext[1]-ext[0]); ya=ext[2]+0.05*(ext[3]-ext[2])
    ax.add_patch(Rectangle((xa,ya),L,8,fc='k',ec='w',lw=.8,zorder=9)); ax.add_patch(Rectangle((xa+L/2,ya),L/2,8,fc='w',ec='k',lw=.8,zorder=9))
    ax.text(xa+L/2,ya+16,'%d m'%L,ha='center',color='w',fontsize=9,weight='bold',zorder=9)
    xn=ext[1]-0.06*(ext[1]-ext[0]); yn=ext[3]-0.12*(ext[3]-ext[2])
    ax.annotate('N',xy=(xn,yn+0.07*(ext[3]-ext[2])),xytext=(xn,yn),ha='center',color='w',weight='bold',fontsize=12,arrowprops=dict(arrowstyle='-|>',color='w',lw=2),zorder=9)
def sitio(ax):
    for _,r in fr.iterrows():
        gpd.GeoSeries([r.geometry],crs=CRS).boundary.plot(ax=ax,color='#ff6d00' if r.tipo!='deposito' else '#00b8d4',lw=1.6,ls='--',zorder=4)
    gr.plot(ax=ax,color='white',lw=6,zorder=5); gr.plot(ax=ax,color='red',lw=3.5,zorder=5)
# ---------- Fig 1: plan general ----------
ext=(x0,x1,y0,y1)
fig,ax=plt.subplots(figsize=(10.5,9)); base(ax,ext)
gpd.GeoSeries([D['aoi']],crs=CRS).boundary.plot(ax=ax,color='white',lw=2,zorder=3)
for _,l in LN.iterrows():
    m=[k for k,mm in enumerate(E['mis']) if l.n in mm][0]
    q=np.array([a for a,_ in l.wps]); ax.plot(q[:,0],q[:,1],color=COL[m],lw=1.3,zorder=3)
    p=q[0]; ax.text(p[0],p[1],str(l.n),color='k',fontsize=7,ha='center',va='center',zorder=6,bbox=dict(boxstyle='circle,pad=0.15',fc=COL[m],ec='k',lw=.5))
q=np.array([a for a,_ in X['obl']['wps']]); ax.plot(q[:,0],q[:,1],color='#ff00ff',lw=2.5,zorder=3)
sd0,sd1,td0,td1=E['sd']; box=np.array([P(sd0,td0),P(sd1,td0),P(sd1,td1),P(sd0,td1),P(sd0,td0)]); ax.plot(box[:,0],box[:,1],color='#ffa000',lw=2,ls='-.',zorder=4)
sitio(ax)
for _,g in G.iterrows():
    ax.scatter(g.x,g.y,marker='^' if g.tipo=='control' else 's',s=95,c='red' if g.tipo=='control' else 'orange',edgecolor='k',zorder=7)
    ax.text(g.x+14,g.y+10,g.id,fontsize=8,color='w',weight='bold',zorder=8,bbox=dict(fc='k',alpha=.55,ec='none',pad=.8))
ax.scatter(*E['HOME'],marker='H',s=170,c='#00e676',edgecolor='k',zorder=8)
escala(ax,ext)
h=[Line2D([],[],color='white',lw=2,label='Área de vuelo (27 ha)')]
h+=[Line2D([],[],color=COL[k],lw=2,label='Misión %d: líneas %s (nadir, 80 m)'%(k+1,', '.join(map(str,m)))) for k,m in enumerate(E['mis'])]
h+=[Line2D([],[],color='#ff00ff',lw=2.5,label='Misión 5: pasada oblicua (cámara −35°)'),
    Line2D([],[],color='#ffa000',lw=2,ls='-.',label='Misiones 6 y 7: detalle de la grieta (40 m)'),
    Line2D([],[],color='red',lw=3.5,label='Grieta'),Line2D([],[],color='#ff6d00',lw=1.6,ls='--',label='Cicatriz'),Line2D([],[],color='#00b8d4',lw=1.6,ls='--',label='Depósito'),
    Line2D([],[],marker='^',ls='',mfc='red',mec='k',ms=9,label='Punto de control (GCP)'),Line2D([],[],marker='s',ls='',mfc='orange',mec='k',ms=8,label='Punto de chequeo (CHK)'),
    Line2D([],[],marker='H',ls='',mfc='#00e676',mec='k',ms=11,label='Despegue sugerido'),Line2D([],[],color='#fff59d',lw=1,label='Curvas de nivel IGN cada 5 m')]
ax.legend(handles=h,loc='upper left',bbox_to_anchor=(1.02,1),fontsize=9,frameon=True,facecolor='#d5d5d5',edgecolor='none',framealpha=1,title='Referencias',title_fontproperties={'weight':'bold'})
plt.savefig(OUT+'/f_plan_general.png',dpi=150,bbox_inches='tight'); plt.close()
# ---------- Fig 2: detalle grieta ----------
from shapely.geometry import Polygon as SP; bb=SP(box).buffer(60).bounds
fig,ax=plt.subplots(figsize=(9,8)); ext2=(bb[0],bb[2],bb[1],bb[3]); base(ax,ext2)
for _,l in DL.iterrows():
    q=np.array([a for a,_ in l.wps]); col='#ffa000' if l.n<=5 else '#ffd54f'
    ax.plot(q[:,0],q[:,1],color=col,lw=1.6,zorder=3); ax.scatter(q[:,0],q[:,1],s=10,c=col,edgecolor='k',lw=.3,zorder=4)
    ax.text(q[0,0],q[0,1],str(l.n),fontsize=7,ha='center',va='center',zorder=6,bbox=dict(boxstyle='circle,pad=0.15',fc=col,ec='k',lw=.5))
F=E['F']; fd=F[F.tipo=='detalle grieta']; ax.scatter(fd.x,fd.y,s=4,c='white',zorder=4)
sitio(ax)
for _,g in G.iterrows():
    if ext2[0]<g.x<ext2[1] and ext2[2]<g.y<ext2[3]:
        ax.scatter(g.x,g.y,marker='^' if g.tipo=='control' else 's',s=95,c='red' if g.tipo=='control' else 'orange',edgecolor='k',zorder=7)
        ax.text(g.x+8,g.y+6,g.id,fontsize=8,color='w',weight='bold',zorder=8,bbox=dict(fc='k',alpha=.55,ec='none',pad=.8))
escala(ax,ext2,L=50)
h=[Line2D([],[],color='#ffa000',lw=2,marker='o',ms=4,label='Misión 6: líneas 1 a 5 (waypoints)'),Line2D([],[],color='#ffd54f',lw=2,marker='o',ms=4,label='Misión 7: líneas 6 a 10 (waypoints)'),
   Line2D([],[],marker='o',ls='',mfc='white',mec='white',ms=3,label='Puntos de foto (cada %.1f m)'%E['phd']),
   Line2D([],[],color='red',lw=3.5,label='Grieta'),Line2D([],[],color='#ff6d00',lw=1.6,ls='--',label='Cicatriz'),Line2D([],[],color='#00b8d4',lw=1.6,ls='--',label='Depósito'),
   Line2D([],[],marker='^',ls='',mfc='red',mec='k',ms=9,label='Punto de control (GCP)'),Line2D([],[],marker='s',ls='',mfc='orange',mec='k',ms=8,label='Punto de chequeo (CHK)'),Line2D([],[],color='#fff59d',lw=1,label='Curvas de nivel IGN cada 5 m')]
ax.legend(handles=h,loc='upper left',bbox_to_anchor=(1.02,1),fontsize=9,frameon=True,facecolor='#d5d5d5',edgecolor='none',framealpha=1,title='Referencias',title_fontproperties={'weight':'bold'})
plt.savefig(OUT+'/f_detalle_grieta.png',dpi=150,bbox_inches='tight'); plt.close()
# ---------- Fig 3: perfil transversal ----------
ign_full=np.load('ign.npy'); bx0,by0,bx1,by1,PXb=E['ign_box']
def z(p):
    r=int((by1-p[1])/PXb); cc=int((p[0]-bx0)/PXb); return ign_full[r,cc]
tt=np.arange(-200,251,2); zt=np.array([z(P(0,t)) for t in tt])
fig,ax=plt.subplots(figsize=(11,4.6))
ax.fill_between(tt,0,zt,color='#bcaaa4',zorder=1); ax.plot(tt,zt,color='#5d4037',lw=1.2,zorder=2,label='Terreno (MDE IGN 5 m)')
ax.axhspan(0,10,xmin=0,xmax=1,color='#90caf9',alpha=.5,zorder=0)
Z0=E['Z0']
for _,l in LN.iterrows():
    m=[k for k,mm in enumerate(E['mis']) if l.n in mm][0]
    a=float(np.interp(0,[ (q-c)@v for q,_ in l.wps][::(1 if l.s1>l.s0 else -1)],[aa for _,aa in l.wps][::(1 if l.s1>l.s0 else -1)]))+Z0
    ax.scatter(l.t,a,s=60,c=COL[m],edgecolor='k',zorder=5); ax.text(l.t,a+3,str(l.n),ha='center',fontsize=8)
    ax.plot([l.t,l.t],[z(P(0,l.t)),a],color=COL[m],lw=.6,ls=':',zorder=3)
ao=E['alt_ob']+Z0; ax.scatter(E['tob'],ao,s=90,marker='D',c='#ff00ff',edgecolor='k',zorder=6)
for ang,ls_ in ((35,'-'),(35-23.2,':'),(35+23.2,':')):
    d=(ao-15)/np.tan(np.radians(ang)); ax.plot([E['tob'],E['tob']-d],[ao,15],color='#ff00ff',lw=1 if ls_==':' else 1.6,ls=ls_,zorder=4)
ax.axvline(0,color='red',lw=2,zorder=3); ax.text(2,5,'grieta',color='red',fontsize=10)
ax.scatter([ (E['HOME']-c)@nrm ],[Z0],marker='H',s=120,c='#00e676',edgecolor='k',zorder=6)
ax.text(-195,88,'meseta (ciudad)',fontsize=10); ax.text(170,25,'río Paraná',fontsize=10,color='#0d47a1')
ax.set_xlabel('Distancia perpendicular a la barranca desde la grieta (m); negativo = hacia la ciudad, positivo = hacia el río')
ax.set_ylabel('Cota (m)'); ax.set_ylim(0,165); ax.set_xlim(-200,250); ax.grid(alpha=.3)
h=[Line2D([],[],color='#5d4037',lw=1.5,label='Terreno (MDE IGN 5 m)')]+[Line2D([],[],marker='o',ls='',mfc=COL[k],mec='k',ms=8,label='Líneas de la misión %d'%(k+1)) for k in range(4)]
h+=[Line2D([],[],marker='D',ls='',mfc='#ff00ff',mec='k',ms=8,label='Pasada oblicua y campo visual'),Line2D([],[],marker='H',ls='',mfc='#00e676',mec='k',ms=10,label='Despegue sugerido'),Line2D([],[],color='red',lw=2,label='Grieta')]
ax.legend(handles=h,loc='upper left',bbox_to_anchor=(1.01,1),fontsize=9,frameon=True,facecolor='#d5d5d5',edgecolor='none',framealpha=1,title='Referencias',title_fontproperties={'weight':'bold'})
plt.savefig(OUT+'/f_perfil_alturas.png',dpi=150,bbox_inches='tight'); plt.close()
# ---------- Fig 4: blanco GCP ----------
fig,ax=plt.subplots(figsize=(5.2,3.6)); ax.add_patch(Rectangle((0,0),60,60,fc='white',ec='k',lw=1.5))
ax.add_patch(Rectangle((0,30),30,30,fc='k')); ax.add_patch(Rectangle((30,0),30,30,fc='k'))
ax.plot(30,30,'o',ms=5,mfc='red',mec='red'); ax.annotate('centro: aquí se apoya\nel bastón del GNSS',xy=(30,30),xytext=(66,46),fontsize=10,arrowprops=dict(arrowstyle='->'))
ax.text(30,-7,'60 cm',ha='center',fontsize=10); ax.text(-7,30,'60 cm',va='center',rotation=90,fontsize=10)
ax.text(45,45,'GCP03',ha='center',va='center',fontsize=9,weight='bold')
ax.text(66,14,'a 80 m de altura: %.0f píxeles\npor lado; a 40 m: %.0f píxeles'%(60/E['gsd'],120/E['gsd']),fontsize=10)
ax.set_xlim(-12,118); ax.set_ylim(-12,66); ax.set_aspect('equal'); ax.axis('off')
plt.savefig(OUT+'/f_blanco_gcp.png',dpi=150,bbox_inches='tight'); plt.close()
print('ok')
