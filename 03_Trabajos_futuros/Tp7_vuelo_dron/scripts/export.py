import pickle, numpy as np, pandas as pd, geopandas as gpd, os
from pyproj import Transformer
from shapely.geometry import Point
CRS='EPSG:32721'; OUT='/home/claude/dron/out'; os.makedirs(OUT,exist_ok=True)
E=pickle.load(open('plan2.pkl','rb')); D=pickle.load(open('plan.pkl','rb'))
LN,DL,F,G,R=E['LN'],E['DL'],E['F'],E['G'],E['R']
tr=Transformer.from_crs(CRS,'EPSG:4326',always_xy=True)
def ll(p): lo,la=tr.transform(p[0],p[1]); return la,lo
c,v,nrm=D['c'],D['v'],D['nrm']
def P(s,t): return c+s*v+t*nrm
# ---------------- Litchi CSV ----------------
hdr=['latitude','longitude','altitude(m)','heading(deg)','curvesize(m)','rotationdir','gimbalmode','gimbalpitchangle']
for k in range(1,16): hdr+=['actiontype%d'%k,'actionparam%d'%k]
hdr+=['altitudemode','speed(m/s)','poi_latitude','poi_longitude','poi_altitude(m)','poi_altitudemode','photo_timeinterval','photo_distinterval']
def wp(p,alt,head,pitch,vel,dint):
    la,lo=ll(p); r=[round(la,7),round(lo,7),alt,head,0,0,2,pitch]
    for k in range(15): r+=[-1,0]
    r+=[0,vel,0,0,0,0,-1,dint]; return r
def mision_csv(nombre,lineas,pitch,vel,dint):
    rows=[]
    for li,l in enumerate(lineas):
        for k,(q,a) in enumerate(l['wps']):
            last_of_line=k==len(l['wps'])-1
            rows.append(wp(q,int(a),l['rumbo'],pitch,vel,-1 if last_of_line else round(dint,1)))
    df=pd.DataFrame(rows,columns=hdr); df.to_csv(os.path.join(OUT,nombre),index=False,lineterminator='\r\n')
    return len(df)
nwp={}
for k,m in enumerate(E['mis']):
    nwp[k+1]=mision_csv('Litchi_M%d_nadir_80m_lineas_%s.csv'%(k+1,'-'.join(map(str,m))),[LN[LN.n==n].iloc[0] for n in m],-90,E['VEL'],E['ph'])
# oblicua: waypoints cada 100 m a altura constante
L0,L1=-400,400; tob=E['tob']
obl=dict(rumbo=round((E['az'])%360,1),wps=[(P(s,tob),E['alt_ob']) for s in np.arange(L0,L1+1,100)])
# en la oblicua el dron vuela de costado: rumbo del dron hacia la barranca
rows=[]
for k,(q,a) in enumerate(obl['wps']):
    rows.append(wp(q,int(a),E['rumbo_ob'],-35,3.0,-1 if k==len(obl['wps'])-1 else 10))
pd.DataFrame(rows,columns=hdr).to_csv(os.path.join(OUT,'Litchi_M%d_oblicua_barranca.csv'%E['nob']),index=False,lineterminator='\r\n'); nwp[E['nob']]=len(rows)
d1=[r for _,r in DL.iterrows() if r.n<=5]; d2=[r for _,r in DL.iterrows() if r.n>5]
nwp[E['ndet']]=mision_csv('Litchi_M%d_detalle_grieta_40m_a.csv'%E['ndet'],d1,-90,3.0,E['phd'])
nwp[E['ndet']+1]=mision_csv('Litchi_M%d_detalle_grieta_40m_b.csv'%(E['ndet']+1),d2,-90,3.0,E['phd'])
R['waypoints']=R.mision.map(nwp); print(R.to_string())
# ---------------- CSV fotos y GCP ----------------
tr2=Transformer.from_crs(CRS,'EPSG:22185',always_xy=True)   # POSGAR 2007 faja 5 (referencia local)
F2=F.copy(); F2['id']=['F%04d'%(i+1) for i in range(len(F2))]
F2[['id','mision','linea','tipo','lat','lon','x','y','alt_desp_m','agl_m','gimbal','rumbo']].round({'lat':7,'lon':7,'x':1,'y':1}).rename(columns={'x':'E_UTM21S','y':'N_UTM21S','alt_desp_m':'alt_sobre_despegue_m','agl_m':'alt_sobre_terreno_m','gimbal':'gimbal_grados','rumbo':'rumbo_grados'}).to_csv(os.path.join(OUT,'Puntos_de_foto.csv'),index=False,lineterminator='\r\n')
G2=G.copy()
G2['E_POSGAR07_f5'],G2['N_POSGAR07_f5']=tr2.transform(G2.x.values,G2.y.values)
G2=G2[['id','tipo','posicion','lat','lon','x','y','E_POSGAR07_f5','N_POSGAR07_f5','cota_IGN_m','dist_grieta_m']].rename(columns={'x':'E_UTM21S','y':'N_UTM21S','cota_IGN_m':'cota_IGN_aprox_m'})
G2.round({'lat':7,'lon':7,'E_UTM21S':1,'N_UTM21S':1,'E_POSGAR07_f5':1,'N_POSGAR07_f5':1}).to_csv(os.path.join(OUT,'Puntos_de_control_GCP.csv'),index=False,lineterminator='\r\n')
# ---------------- KML ----------------
gr=gpd.read_file('/mnt/user-data/uploads/DIAMANTE/GRIETAS/grietadte.shp').to_crs('EPSG:4326')
fr=gpd.read_file('/mnt/user-data/outputs/t7h/E1_cicatriz_y_deposito.gpkg',layer='formas').to_crs('EPSG:4326')
def coords(pts,alt=None):
    return ' '.join('%.7f,%.7f,%s'%(lo,la,0 if alt is None else alt) for lo,la in pts)
def lla(p): lo,la=tr.transform(p[0],p[1]); return lo,la
K=['<?xml version="1.0" encoding="UTF-8"?>','<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Plan de vuelo dron - Barranca de Diamante</name>']
sty={'aoi':('ffffffff','00ffffff',3),'lin':('ffffff00','',2),'obl':('ffff00ff','',3),'det':('ff00a5ff','',2),'gri':('ff0000ff','',5),'cic':('ff0080ff','4d0080ff',2),'dep':('ffffff00','4dffff00',2)}
for k,(lc,pc,w) in sty.items():
    K.append('<Style id="%s"><LineStyle><color>%s</color><width>%d</width></LineStyle><PolyStyle><color>%s</color></PolyStyle></Style>'%(k,lc,w,pc or '00000000'))
K.append('<Style id="gcp"><IconStyle><color>ff0000ff</color><scale>1.1</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/triangle.png</href></Icon></IconStyle></Style>')
K.append('<Style id="chk"><IconStyle><color>ff00a5ff</color><scale>1.0</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_square.png</href></Icon></IconStyle></Style>')
K.append('<Style id="home"><IconStyle><color>ff00ff00</color><scale>1.3</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/heliport.png</href></Icon></IconStyle></Style>')
K.append('<Style id="foto"><IconStyle><color>ffffff00</color><scale>0.4</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>')
K.append('<Folder><name>Area de vuelo</name><Placemark><name>Area de vuelo (27 ha)</name><styleUrl>#aoi</styleUrl><Polygon><outerBoundaryIs><LinearRing><coordinates>%s</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark></Folder>'%coords([lla(p) for p in D['aoi'].exterior.coords]))
K.append('<Folder><name>Despegue sugerido</name><Placemark><name>Despegue (cota IGN %.1f m)</name><styleUrl>#home</styleUrl><Point><coordinates>%.7f,%.7f,0</coordinates></Point></Placemark></Folder>'%(E['Z0'],*lla(E['HOME'])))
K.append('<Folder><name>Lineas de vuelo nadir 80 m</name>')
for _,l in LN.iterrows():
    m=[k+1 for k,mm in enumerate(E['mis']) if l.n in mm][0]
    K.append('<Placemark><name>Mision %d - linea %d</name><styleUrl>#lin</styleUrl><LineString><altitudeMode>clampToGround</altitudeMode><coordinates>%s</coordinates></LineString></Placemark>'%(m,l.n,coords([lla(q) for q,_ in l.wps])))
K.append('</Folder><Folder><name>Linea oblicua (camara -35 grados)</name><Placemark><name>Mision %d - oblicua</name><styleUrl>#obl</styleUrl><LineString><coordinates>%s</coordinates></LineString></Placemark></Folder>'%(E['nob'],coords([lla(q) for q,_ in obl['wps']])))
K.append('<Folder><name>Detalle de la grieta 40 m</name>')
for _,l in DL.iterrows():
    K.append('<Placemark><name>Mision %d - linea %d</name><styleUrl>#det</styleUrl><LineString><coordinates>%s</coordinates></LineString></Placemark>'%(E['ndet']+(0 if l.n<=5 else 1),l.n,coords([lla(q) for q,_ in l.wps])))
K.append('</Folder><Folder><name>Puntos de control (GCP) y chequeo (CHK)</name>')
for _,g in G.iterrows():
    K.append('<Placemark><name>%s</name><description>%s, %s. Cota IGN aprox. %.1f m. A %d m de la grieta.</description><styleUrl>#%s</styleUrl><Point><coordinates>%.7f,%.7f,0</coordinates></Point></Placemark>'%(g.id,g.tipo,g.posicion,g.cota_IGN_m,g.dist_grieta_m,'gcp' if g.tipo=='control' else 'chk',g.lon,g.lat))
K.append('</Folder><Folder><name>Puntos de foto</name><visibility>0</visibility>')
for _,f in F2.iterrows():
    K.append('<Placemark><name>%s</name><visibility>0</visibility><description>Mision %d, %s, %d m sobre el despegue, gimbal %d</description><styleUrl>#foto</styleUrl><Point><coordinates>%.7f,%.7f,0</coordinates></Point></Placemark>'%(f.id,f.mision,f.tipo,f.alt_desp_m,f.gimbal,f.lon,f.lat))
K.append('</Folder><Folder><name>Referencias del sitio</name>')
for geom in gr.geometry:
    gs=[geom] if geom.geom_type=='LineString' else list(geom.geoms)
    for g_ in gs: K.append('<Placemark><name>Grieta</name><styleUrl>#gri</styleUrl><LineString><coordinates>%s</coordinates></LineString></Placemark>'%coords([(a[0],a[1]) for a in g_.coords]))
for _,r in fr.iterrows():
    gg=r.geometry; polys=[gg] if gg.geom_type=='Polygon' else list(gg.geoms)
    for pg in polys: K.append('<Placemark><name>%s</name><styleUrl>#%s</styleUrl><Polygon><outerBoundaryIs><LinearRing><coordinates>%s</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>'%(('Cicatriz' if r.tipo!='deposito' else 'Deposito'),'dep' if r.tipo=='deposito' else 'cic',coords(list(pg.exterior.coords))))
K.append('</Folder></Document></kml>')
open(os.path.join(OUT,'Plan_vuelo_dron_Diamante.kml'),'w',encoding='utf-8').write('\n'.join(K))
pickle.dump(dict(R=R,obl=obl,F2=F2,G2=G2),open('exp.pkl','wb'))
print(fr.tipo.tolist()); print(os.listdir(OUT))
