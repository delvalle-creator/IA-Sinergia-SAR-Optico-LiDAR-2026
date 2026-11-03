import pickle, numpy as np, pandas as pd, geopandas as gpd, rasterio, os, json
from shapely.geometry import LineString, Point, Polygon
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from pyproj import Transformer
CRS='EPSG:32721'; OUT='/home/claude/dron/out'; os.makedirs(OUT,exist_ok=True)
D=pickle.load(open('plan.pkl','rb')); G=D['G'].copy()
c,v,nrm,az=D['c'],D['v'],D['nrm'],D['az']; aoi=D['aoi']
def P(s,t): return c+s*v+t*nrm
Q='/mnt/user-data/uploads/CURSOS_CEREGEO_2026/02_Practica/Tp7_Barrancas_deslizamientos/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/E1_DIAMANTE_BARRANCA_'
x0,y0,x1,y1=aoi.buffer(260).bounds; PX=2
T=from_origin(x0,y1,PX,PX); sh=(int((y1-y0)/PX),int((x1-x0)/PX))
def L(p,b):
    o=np.full(sh,np.nan,'f4')
    with rasterio.open(p) as s:
        a=s.read(b).astype('f4')
        if s.nodata is not None: a[a==s.nodata]=np.nan
        reproject(a,o,src_transform=s.transform,src_crs=s.crs,dst_transform=T,dst_crs=CRS,resampling=Resampling.bilinear,src_nodata=np.nan,dst_nodata=np.nan)
    return o
ign=L(Q+'IGN_MDE_5m.tif',1); mos=L(Q+'IGN_MDE_mosaico2018.tif',1); mos[mos<=0]=np.nan; ign=np.where(np.isfinite(ign),ign,mos)
print('pct agua',np.nanpercentile(ign,[1,5,10]))
ZRIO=10.0; ign=np.where(np.isfinite(ign),ign,ZRIO)
def zat(x,y):
    r=int((y1-y)/PX); cc=int((x-x0)/PX)
    if 0<=r<sh[0] and 0<=cc<sh[1]: return float(ign[r,cc])
    return np.nan
def zline(p0,p1,n=200):
    xs=np.linspace(p0[0],p1[0],n); ys=np.linspace(p0[1],p1[1],n)
    z=np.array([zat(a,b) for a,b in zip(xs,ys)]); return z
# ---------- camara DJI Mavic 2 Pro (Hasselblad L1D-20c) ----------
SW,SH,FL,PWpx,PHpx=13.2,8.8,10.26,5472,3648
H=80.0; LAT,FR=0.70,0.80; VEL=4.0
gsd=H*SW/(FL*PWpx)*100; fw=H*SW/FL; fh=H*SH/FL
sp=fw*(1-LAT); ph=fh*(1-FR)
print('GSD %.2f cm  huella %.1f x %.1f m  lineas cada %.1f m  fotos cada %.1f m  intervalo %.1f s'%(gsd,fw,fh,sp,ph,ph/VEL))
# despegue sugerido: meseta, cerca de CHK01 (estable, > 100 m de la grieta)
def dist(a,b): return float(np.hypot(*(np.asarray(a)-np.asarray(b))))
gr=gpd.read_file('/mnt/user-data/uploads/DIAMANTE/GRIETAS/grietadte.shp').to_crs(CRS).union_all()
chk1=G[G.id=='CHK01'].iloc[0]; HOME=np.array([chk1.x+15,chk1.y-15]); Z0=round(zat(*HOME),1)
print('despegue',HOME,'cota',Z0,'dist grieta',round(Point(*HOME).distance(gr)))

def seguir(p0,p1,Hagl,WS):
    """waypoints cada ~WS m; altura = Hagl sobre el maximo del terreno en una ventana"""
    Lg=dist(p0,p1); n=max(2,int(np.ceil(Lg/WS))+1); u=(p1-p0)/Lg; w=np.array([-u[1],u[0]])
    wps=[]
    for k in range(n):
        q=p0+u*Lg*k/(n-1); zz=[]
        for a in np.linspace(-WS/2-10,WS/2+10,15):
            for b in (-15,0,15):
                zz.append(zat(*(q+u*a+w*b)))
        wps.append((q,round(Hagl+np.nanmax(zz)-Z0)))
    # control: perfil fino interpolado
    agl=[]
    for k in range(n-1):
        for f in np.linspace(0,1,20):
            q=wps[k][0]*(1-f)+wps[k+1][0]*f; a=wps[k][1]*(1-f)+wps[k+1][1]*f
            agl.append(a+Z0-zat(*q))
    return wps,np.nanmin(agl),np.nanmax(agl)
def alt_en(wps,p):
    Q=np.array([q for q,_ in wps]); A=np.array([a for _,a in wps]); d=np.hypot(*(Q-p).T); k=np.argsort(d)[:2]; w=1/(d[k]+1e-6); return round(float((A[k]*w).sum()/w.sum()))
L0,L1=-400,400; W=170; EXT=30
ts=list(np.arange(-W,W+0.1,sp));
if ts[-1]<W-1: ts.append(W)
lines=[]
for i,t in enumerate(ts):
    s0,s1=(L0-EXT,L1+EXT) if i%2==0 else (L1+EXT,L0-EXT)
    p0,p1=P(s0,t),P(s1,t); z=zline(p0,p1)
    zmax=float(np.nanmax(z)); zmed=float(np.nanmedian(z)); zmin=float(np.nanmin(z))
    wps,amin,amax=seguir(p0,p1,H,40)
    lines.append(dict(n=i+1,t=t,s0=s0,s1=s1,p0=p0,p1=p1,zmin=zmin,zmed=zmed,zmax=zmax,wps=wps,alt_min=min(a for _,a in wps),alt_max=max(a for _,a in wps),agl_min=amin,agl_max=amax,
                      rumbo=round(az if s1>s0 else (az+180)%360,1),largo=abs(s1-s0)))
LN=pd.DataFrame(lines)
print(LN[['n','t','zmin','zmax','alt_min','alt_max','agl_min','agl_max','rumbo']].round(1).to_string())
# misiones de 3 lineas
mis=[];
for k in range(0,len(LN),3): mis.append(list(LN.n[k:k+3]))
# fotos nadir
fot=[]
for _,l in LN.iterrows():
    d=1 if l.s1>l.s0 else -1
    for s in np.arange(l.s0,l.s1+d,ph*d):
        p=P(s,l.t); A_=alt_en(l.wps,p); fot.append(dict(mision=[m for m,ll in enumerate(mis) if l.n in ll][0]+1,linea=int(l.n),x=p[0],y=p[1],alt_desp_m=A_,agl_m=round(A_+Z0-zat(*p),1),gimbal=-90,rumbo=l.rumbo,tipo='nadir'))
# oblicua: sobre el rio, camara -35 mirando la barranca
tob=W+30; Hob=70
zw=np.nanmedian(zline(P(L0,tob),P(L1,tob))); alt_ob=round(Hob+zw-Z0)
rumbo_ob=round(np.degrees(np.arctan2(-nrm[0],-nrm[1]))%360,1)
nob=len(mis)+1
for s in np.arange(L0,L1+1,10):
    p=P(s,tob); fot.append(dict(mision=nob,linea=99,x=p[0],y=p[1],alt_desp_m=alt_ob,agl_m=round(alt_ob+Z0-zw,1),gimbal=-35,rumbo=rumbo_ob,tipo='oblicua'))
# detalle de la grieta: 40 m AGL, 220 x 120 m centrada en la grieta
Hd=40; fwd=Hd*SW/FL; fhd=Hd*SH/FL; spd=fwd*(1-LAT); phd=fhd*(1-FR)
gc=np.array(gr.centroid.coords[0][:2]); ga=np.array(gr.coords)[:, :2]
s_g=[(p-c)@v for p in ga]; t_g=[(p-c)@nrm for p in ga]
sd0,sd1=min(s_g)-60,max(s_g)+60; td0,td1=min(t_g)-60,max(t_g)+60
tsd=list(np.arange(td0,td1+0.1,spd))
if tsd[-1]<td1-1: tsd.append(td1)
DL=[]
for i,t in enumerate(tsd):
    s0,s1=(sd0-15,sd1+15) if i%2==0 else (sd1+15,sd0-15)
    z=zline(P(s0,t),P(s1,t)); wps,amin,amax=seguir(P(s0,t),P(s1,t),Hd,30)
    DL.append(dict(n=i+1,t=t,s0=s0,s1=s1,p0=P(s0,t),p1=P(s1,t),zmin=np.nanmin(z),zmax=np.nanmax(z),wps=wps,alt_min=min(a for _,a in wps),alt_max=max(a for _,a in wps),agl_min=amin,agl_max=amax,rumbo=round(az if s1>s0 else (az+180)%360,1),largo=abs(s1-s0)))
DL=pd.DataFrame(DL); ndet=nob+1
for _,l in DL.iterrows():
    d=1 if l.s1>l.s0 else -1
    for s in np.arange(l.s0,l.s1+d,phd*d):
        p=P(s,l.t); A_=alt_en(l.wps,p); fot.append(dict(mision=ndet+(0 if l.n<=5 else 1),linea=int(100+l.n),x=p[0],y=p[1],alt_desp_m=A_,agl_m=round(A_+Z0-zat(*p),1),gimbal=-90,rumbo=l.rumbo,tipo='detalle grieta'))
print(DL[['n','zmin','zmax','alt_min','alt_max','agl_min','agl_max']].round(1).to_string())
print('oblicua alt desp',alt_ob,'agua',zw)
print('detalle: GSD %.2f cm, lineas cada %.1f, fotos cada %.1f'%(Hd*SW/(FL*PWpx)*100,spd,phd))
F=pd.DataFrame(fot)
tr=Transformer.from_crs(CRS,'EPSG:4326',always_xy=True)
F['lon'],F['lat']=tr.transform(F.x.values,F.y.values)
G['lon'],G['lat']=tr.transform(G.x.values,G.y.values)
hl=tr.transform(*HOME)
# ---------- resumen de misiones ----------
R=[]
def resumen(nm,tipo,LLs,vel):
    d=dist(HOME,LLs[0]['p0'])
    for i,l in enumerate(LLs):
        d+=l['largo']
        if i+1<len(LLs): d+=dist(l['p1'],LLs[i+1]['p0'])
    d+=dist(LLs[-1]['p1'],HOME)
    nf=int((F.mision==nm).sum())
    tmin=(d/vel+60+60)/60   # + ascenso/descenso y giros
    R.append(dict(mision=nm,tipo=tipo,lineas=', '.join(str(int(l['n'])) if l['n']<99 else 'O' for l in LLs),dist_km=round(d/1000,2),vel=vel,tiempo_min=round(tmin),fotos=nf))
for k,m in enumerate(mis):
    resumen(k+1,'nadir 80 m',[LN[LN.n==n].iloc[0].to_dict() for n in m],VEL)
ob=dict(n=99,p0=P(L0,tob),p1=P(L1,tob),largo=L1-L0)
resumen(nob,'oblicua -35°',[ob],3.0)
resumen(ndet,'detalle grieta 40 m',[r.to_dict() for _,r in DL.iterrows() if r.n<=5],3.0)
resumen(ndet+1,'detalle grieta 40 m',[r.to_dict() for _,r in DL.iterrows() if r.n>5],3.0)
R=pd.DataFrame(R); print(R.to_string())
pickle.dump(dict(LN=LN,DL=DL,F=F,G=G,R=R,mis=mis,HOME=HOME,Z0=Z0,hl=hl,tob=tob,Hob=Hob,alt_ob=alt_ob,zw=zw,rumbo_ob=rumbo_ob,nob=nob,ndet=ndet,
    gsd=gsd,fw=fw,fh=fh,sp=sp,ph=ph,H=H,VEL=VEL,Hd=Hd,spd=spd,phd=phd,fwd=fwd,fhd=fhd,sd=(sd0,sd1,td0,td1),az=az,ign_box=(x0,y0,x1,y1,PX)),open('plan2.pkl','wb'))
np.save('ign.npy',ign)
