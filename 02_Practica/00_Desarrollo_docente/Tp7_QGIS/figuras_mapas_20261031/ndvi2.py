import numpy as np, geopandas as gpd, pickle
from rasterio.features import rasterize
from scipy import ndimage as ndi
T7='/mnt/user-data/uploads/CURSOS_CEREGEO_2026/02_Practica/Tp7_Barrancas_deslizamientos/'
a,trw,crs=pickle.load(open('cb.pkl','rb')); sh=a.shape[1:]
r,n=a[3],a[4]; ok=(r>0)&(n>0)
nd=np.where(ok,(n-r)/(n+r),np.nan)
frm=gpd.read_file(T7+'04_Tablas_de_trabajo/E1_cicatriz_y_deposito.gpkg',layer='formas').to_crs(crs)
zon=gpd.read_file(T7+'04_Tablas_de_trabajo/E1_zonas_ladera.gpkg').to_crs(crs)
print(frm.tipo.tolist())
dep=rasterize([(g,1) for g in frm[frm.tipo=='deposito'].geometry],sh,transform=trw)>0
cic=rasterize([(g,1) for g in frm[frm.tipo=='cicatriz'].geometry],sh,transform=trw)>0
esc=rasterize([(g,1) for g in zon[zon.zona=='escarpa'].geometry],sh,transform=trw)>0
pie=rasterize([(g,1) for g in zon[zon.zona=='pie'].geometry],sh,transform=trw)>0
for sig in (0,1.5):
    v=ndi.gaussian_filter(np.nan_to_num(nd,nan=0),sig) if sig else nd
    tal=(esc|pie)&~dep&~cic&ok
    print('sig',sig,'claro med %.3f n %d'%(np.nanmedian(v[dep&ok]),(dep&ok).sum()),'talud(esc+pie) %.3f'%np.nanmedian(v[tal]),'escarpa %.3f'%np.nanmedian(v[esc&~dep&~cic&ok]))
pickle.dump(dict(nd=nd,dep=dep,cic=cic,esc=esc,pie=pie,ok=ok),open('nd.pkl','wb'))
