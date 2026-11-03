import numpy as np, geopandas as gpd, pandas as pd
from shapely.geometry import Polygon, LineString, Point
from shapely import affinity
CRS='EPSG:32721'
gr=gpd.read_file('/mnt/user-data/uploads/DIAMANTE/GRIETAS/grietadte.shp').to_crs(CRS).union_all()
f=gpd.read_file('/mnt/user-data/outputs/t7h/E1_cicatriz_y_deposito.gpkg',layer='formas').to_crs(CRS)
a=np.array(gr.coords)[:, :2]; v=a[-1]-a[0]; v=v/np.hypot(*v)          # a lo largo de la barranca
nrm=np.array([-v[1],v[0]])                                      # normal
c=np.array(gr.centroid.coords[0][:2])
# hacia el rio: el deposito esta del lado del rio
dep=np.array(f[f.tipo=="deposito"].union_all().centroid.coords[0][:2])
if (dep-c)@nrm<0: nrm=-nrm                                      # nrm apunta al rio
az=np.degrees(np.arctan2(v[0],v[1]))%360
print('azimut barranca %.1f'%az)
L0,L1=-400,400; W_rio,W_tierra=170,170
def P(s,t): return c+s*v+t*nrm
aoi=Polygon([P(L0,-W_tierra),P(L1,-W_tierra),P(L1,W_rio),P(L0,W_rio)])
print('AOI area ha %.1f'%(aoi.area/1e4))
# camara Mavic 3 Enterprise (4/3, 17.3 x 13.0 mm, f 12.29 mm, 5280 x 3956)
H=80.0; sw,sh_,fl,pw=17.3,13.0,12.29,5280
gsd=H*sw/(fl*pw)*100; fw=H*sw/fl; fh=H*sh_/fl
lat_over,fr_over=0.70,0.80
sp=fw*(1-lat_over); ph=fh*(1-fr_over)
print('GSD %.2f cm, huella %.0f x %.0f m, lineas cada %.1f m, fotos cada %.1f m'%(gsd,fw,fh,sp,ph))
ts=np.arange(-W_tierra,W_rio+0.1,sp)
if ts[-1]<W_rio: ts=np.append(ts,W_rio)
lines=[];fotos=[]
for i,t in enumerate(ts):
    s0,s1=(L0-30,L1+30) if i%2==0 else (L1+30,L0-30)
    lines.append(LineString([P(s0,t),P(s1,t)]))
    ss=np.arange(s0,s1+(1 if s1>s0 else -1),ph*(1 if s1>s0 else -1))
    for s in ss: fotos.append(dict(linea=i+1,x=P(s,t)[0],y=P(s,t)[1],alt_rel_m=H,gimbal=-90,rumbo=round(az if s1>s0 else (az+180)%360,1),tipo='nadir'))
# oblicua: linea sobre el rio, 60 m del pie (t = W_rio+40), camara -35 mirando a la barranca
tob=W_rio+30; Hob=70
ob=LineString([P(L0,tob),P(L1,tob)])
for s in np.arange(L0,L1+1,10):
    fotos.append(dict(linea=99,x=P(s,tob)[0],y=P(s,tob)[1],alt_rel_m=Hob,gimbal=-35,rumbo=round((np.degrees(np.arctan2(-nrm[0],-nrm[1])))%360,1),tipo='oblicua'))
F=pd.DataFrame(fotos); print('fotos nadir %d, oblicuas %d'%((F.tipo=='nadir').sum(),(F.tipo=='oblicua').sum()))
# GCP: meseta (t=-150,-60), pie (t=+150), separados a lo largo
gcp=[]
for s in (-380,-190,0,190,380):
    gcp.append(('GCP',s,-150))
for s in (-300,300): gcp.append(('GCP',s,-60))
for s in (-300,0,300): gcp.append(('GCP',s,150))
chk=[('CHK',-100,-110),('CHK',100,-110),('CHK',-150,150),('CHK',150,150),('CHK',0,-60)]
G=[]
for k,(tipo,s,t) in enumerate(gcp+chk):
    p=P(s,t); G.append(dict(id='%s%02d'%(tipo,k+1 if tipo=='GCP' else k-len(gcp)+1),tipo='control' if tipo=='GCP' else 'chequeo',x=p[0],y=p[1],posicion=('meseta' if t<0 else 'pie de la barranca')))
G=pd.DataFrame(G)
# distancia de cada GCP a la grieta: que ninguno quede sobre el bloque que se mueve (< 60 m detras de la grieta)
G['dist_grieta_m']=[round(Point(x,y).distance(gr)) for x,y in zip(G.x,G.y)]
print(G[['id','posicion','dist_grieta_m']].to_string())
import pickle; pickle.dump(dict(aoi=aoi,lines=lines,ob=ob,F=F,G=G,gsd=gsd,fw=fw,fh=fh,sp=sp,ph=ph,H=H,Hob=Hob,az=az,c=c,v=v,nrm=nrm),open('plan.pkl','wb'))
