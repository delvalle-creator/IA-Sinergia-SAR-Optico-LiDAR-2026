import numpy as np, pandas as pd, geopandas as gpd, rasterio, re, pickle
from rasterio.vrt import WarpedVRT
U='/mnt/user-data/uploads/CURSOS_CEREGEO_2026/02_Practica/'
CL=[0,2,5,8,12,16,60]
r=rasterio.open(U+'Tp9_Deforestacion/02_Subsets_SNAP_QGIS/C_pila_temporal_20m.tif'); T=r.transform
h=gpd.read_file(U+'Tp1_Convergencia/05_Resultados/03_Vectores/lidar_C_FEDERAL.gpkg',layer='gedi_l2a').to_crs(r.crs)
h=h[h.valido.astype(bool)]; h=h[~(h.rh98>60)]
col=((h.geometry.x-T.c)/T.a).astype(int).values; fil=((h.geometry.y-T.f)/T.e).astype(int).values
dn=(col>=0)&(col<r.width)&(fil>=0)&(fil<r.height); h,col,fil=h[dn],col[dn],fil[dn]
print(len(h))
cur={}; cnt={}
for b,n in enumerate(r.descriptions,1):
    if n.startswith('O_'): continue
    arr=r.read(b); v=arr[fil,col].astype('f8'); y=10*np.log10(np.where(v>0,v,np.nan))
    an=int(re.search(r'_(\d{4})_',n+'_').group(1))
    dias=np.abs((pd.to_datetime(h.fecha)-pd.Timestamp('%d-07-01'%an)).dt.days.values)
    ok=np.isfinite(y)&(dias<=730)
    if ok.sum()<20: print(n,'sin'); continue
    gr=pd.Series(y[ok]).groupby(pd.cut(h.rh98.values[ok],CL),observed=False)
    cur[n]=gr.median().values; cnt[n]=gr.count().values; print(n,ok.sum(),np.round(cur[n],2),cnt[n])
src=rasterio.open(U+'Tp9_Deforestacion/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/C_FEDERAL_BIOMASS_P_20260812.tif')
vista=WarpedVRT(src,crs=r.crs)
dias=np.abs((pd.to_datetime(h.fecha)-pd.Timestamp('2026-08-12')).dt.days.values); cerca=dias<=730
m=np.array([x for x in vista.sample(list(zip(h.geometry.x,h.geometry.y)))],'f8')
for b in range(1,src.count+1):
    nm=src.descriptions[b-1] or 'b%d'%b
    if nm.endswith('_db') or 'incidence' in nm or 'cociente' in nm: continue
    v=m[:,b-1]; y=10*np.log10(np.where(v>0,v,np.nan)); ok=np.isfinite(y)&cerca
    if ok.sum()<20: continue
    gr=pd.Series(y[ok]).groupby(pd.cut(h.rh98.values[ok],CL),observed=False)
    cur['P_'+nm]=gr.median().values; cnt['P_'+nm]=gr.count().values; print('P',nm,ok.sum(),np.round(cur['P_'+nm],2),cnt['P_'+nm])
pickle.dump((cur,cnt),open('curvas.pkl','wb'))
