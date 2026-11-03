exec(open('mapa.py').read().split("G=D['G']")[0])
from scipy import ndimage as ndi
from shapely.geometry import Point
G=D['G'].copy()
gy,gx=np.gradient(ndi.gaussian_filter(np.nan_to_num(ign,nan=0),2),PX); sl=np.hypot(gx,gy)*100
gr=gpd.read_file('/mnt/user-data/uploads/DIAMANTE/GRIETAS/grietadte.shp').to_crs(CRS).union_all()
aoi=D['aoi'].buffer(-15)
from rasterio.features import rasterize
inaoi=rasterize([(aoi,1)],out_shape=sh,transform=T).astype(bool)
dg=np.full(sh,1e9)
# distancia a la grieta
ii,jj=np.mgrid[0:sh[0]:4,0:sh[1]:4]
meseta=(ign>45)&(sl<10)&inaoi
pie=(ign>9)&(ign<26)&(sl<10)&inaoi
# alejar del borde: >=40 m de talud > 30 %
talud=sl>30
lejos=ndi.distance_transform_edt(~talud)*PX>=15
meseta&=lejos; pie&=lejos
def snap(x,y,m):
    r=int((y1-y)/PX); c=int((x-x0)/PX)
    d=ndi.distance_transform_edt(~m,return_indices=True)[1]
    rr,cc=d[0][r,c],d[1][r,c]; return x0+cc*PX+PX/2, y1-rr*PX-PX/2
dm=ndi.distance_transform_edt(~meseta,return_indices=True)[1]; dp=ndi.distance_transform_edt(~pie,return_indices=True)[1]
nx=[];ny=[]
for _,g in G.iterrows():
    d_=dm if g.posicion=='meseta' else dp
    r=int((y1-g.y)/PX); c=int((g.x-x0)/PX); r=min(max(r,0),sh[0]-1); c=min(max(c,0),sh[1]-1)
    rr,cc=d_[0][r,c],d_[1][r,c]; nx.append(x0+cc*PX+PX/2); ny.append(y1-rr*PX-PX/2)
G['mov_m']=[round(np.hypot(a-x,b-y)) for a,b,x,y in zip(nx,ny,G.x,G.y)]
G['x']=nx; G['y']=ny
G['cota_IGN_m']=[round(float(ign[int((y1-y)/PX),int((x-x0)/PX)]),1) for x,y in zip(G.x,G.y)]
G['dist_grieta_m']=[round(Point(x,y).distance(gr)) for x,y in zip(G.x,G.y)]
print(G[['id','posicion','cota_IGN_m','dist_grieta_m','mov_m']].to_string())
D['G']=G; pickle.dump(D,open('plan.pkl','wb'))
