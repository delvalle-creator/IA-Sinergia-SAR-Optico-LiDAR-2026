import numpy as np, rasterio, geopandas as gpd, time
U='/mnt/user-data/uploads/02_Practica/'
r=rasterio.open(U+'00_COMUN/09_Herramientas/desarrollo_docente/Tp10/B_CONCORDIA_AE_2025_20m.tif')
A=r.read().astype('f4'); nod=(A==-128).all(0)
A=np.sign(A)*(A/127.5)**2; A/=np.linalg.norm(A,axis=0,keepdims=True)+1e-9
g=gpd.read_file(U+'Tp10_Impacto_urbano/04_Tablas_de_trabajo/entrenamiento_mapbiomas_B_CONCORDIA.gpkg')
rows,cols=rasterio.transform.rowcol(r.transform,g.geometry.x.values,g.geometry.y.values); rows=np.clip(rows,0,A.shape[1]-1); cols=np.clip(cols,0,A.shape[2]-1)
Xs=A[:,rows,cols].T; ys=g.codigo.values; ok=np.isfinite(Xs).all(1)&~nod[rows,cols]; Xs=Xs[ok]; ys=ys[ok]; print(len(ys))
def clasif(sub):
    H,W=sub.shape[1:]; X=sub.reshape(64,-1).T; out=np.zeros(len(X),'u1'); t=time.time()
    for i in range(0,len(X),8000):
        S=X[i:i+8000]@Xs.T; idx=np.argpartition(-S,5,axis=1)[:,:5]; lab=ys[idx]
        out[i:i+8000]=np.array([np.bincount(l,minlength=6).argmax() for l in lab])
    print('t',time.time()-t); return out.reshape(H,W)
full=clasif(A[:,::3,::3]); full[nod[::3,::3]]=0
# zoom 396000-412000, 6520000-6534000
r0,c0=rasterio.transform.rowcol(r.transform,396000,6534000); r1,c1=rasterio.transform.rowcol(r.transform,412000,6520000)
z=clasif(A[:,r0:r1,c0:c1]); z[nod[r0:r1,c0:c1]]=0
np.savez_compressed('knn.npz',full=full,z=z,r0=r0,c0=c0,r1=r1,c1=c1)
print('urb ha sitio(60m)',(full==1).sum()*0.36,'zoom',(z==1).sum()*0.04)
