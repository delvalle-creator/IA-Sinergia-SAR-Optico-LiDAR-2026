exec(open('snap.py').read().split("def snap")[0])
from shapely.geometry import Point
from rasterio.features import rasterize as _rz
_cr=_rz([(gr.buffer(1),1)],out_shape=sh,transform=T).astype(bool)
_dcr=ndi.distance_transform_edt(~_cr)*PX
meseta&=_dcr>80; pie&=_dcr>80
def fps(mask, n, seed_pts=[]):
    rr,cc=np.nonzero(mask[::3,::3]); P=np.c_[x0+cc*3*PX, y1-rr*3*PX]
    sel=list(seed_pts)
    d=np.full(len(P),1e12)
    for s in sel: d=np.minimum(d,np.hypot(*(P-s).T))
    out=[]
    for _ in range(n):
        if not sel: i=np.argmin(P[:,1])  # empezar por el extremo sur
        else: i=np.argmax(d)
        out.append(P[i]); sel.append(P[i]); d=np.minimum(d,np.hypot(*(P-P[i]).T))
    return out
mg=fps(meseta,7); pg=fps(pie,3)
mc=fps(meseta,3,mg+pg); pc=fps(pie,2,mg+pg+mc)
rows=[]
for k,p in enumerate(mg+pg): rows.append(dict(id='GCP%02d'%(k+1),tipo='control',posicion='meseta' if k<7 else 'pie de la barranca',x=p[0],y=p[1]))
for k,p in enumerate(mc+pc): rows.append(dict(id='CHK%02d'%(k+1),tipo='chequeo',posicion='meseta' if k<3 else 'pie de la barranca',x=p[0],y=p[1]))
import pandas as pd
G=pd.DataFrame(rows)
G['cota_IGN_m']=[round(float(ign[int((y1-y)/PX),int((x-x0)/PX)]),1) for x,y in zip(G.x,G.y)]
G['dist_grieta_m']=[round(Point(x,y).distance(gr)) for x,y in zip(G.x,G.y)]
print(G[['id','posicion','cota_IGN_m','dist_grieta_m']].to_string())
D['G']=G; pickle.dump(D,open('plan.pkl','wb'))
