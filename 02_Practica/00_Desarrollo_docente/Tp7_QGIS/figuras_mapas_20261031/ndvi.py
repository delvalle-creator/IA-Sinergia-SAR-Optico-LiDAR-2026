import numpy as np, rasterio, geopandas as gpd, pickle
from rasterio.features import rasterize
from rasterio.windows import from_bounds
from scipy import ndimage as ndi
T7='/mnt/user-data/uploads/CURSOS_CEREGEO_2026/02_Practica/Tp7_Barrancas_deslizamientos/'
f=T7+'02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/E1_DIAMANTE_BARRANCA_CBERS4A_DIAMANTE_20260926_pansharpened_2m.tif'
frm=gpd.read_file(T7+'04_Tablas_de_trabajo/E1_cicatriz_y_deposito.gpkg',layer='formas')
zon=gpd.read_file(T7+'04_Tablas_de_trabajo/E1_zonas_ladera.gpkg')
with rasterio.open(f) as s:
    print(s.crs,s.res,s.count,s.descriptions)
    frm=frm.to_crs(s.crs); zon=zon.to_crs(s.crs)
    print(zon.columns.tolist(), zon.iloc[:,0].tolist() if len(zon)<10 else len(zon))
    x0,y0,x1,y1=frm.total_bounds; pad=1500
    w=from_bounds(x0-pad,y0-pad,x1+pad,y1+pad,s.transform)
    a=s.read(window=w).astype('f4'); trw=s.window_transform(w)
r,n=a[2],a[3]   # se ajusta abajo segun descripciones
pickle.dump((a,trw,str(frm.crs)),open('cb.pkl','wb'))
