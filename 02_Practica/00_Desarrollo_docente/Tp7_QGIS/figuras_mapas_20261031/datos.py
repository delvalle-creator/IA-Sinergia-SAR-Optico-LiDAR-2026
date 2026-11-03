import numpy as np, rasterio, geopandas as gpd, pickle
from rasterio.warp import reproject, Resampling
from rasterio.features import rasterize
U='/mnt/user-data/uploads/'
T7=U+'CURSOS_CEREGEO_2026/02_Practica/Tp7_Barrancas_deslizamientos/'
with rasterio.open(T7+'05_Resultados/02_Rasters/E1_deformacion_confirmada.tif') as s:
    tr,crs,W,H=s.transform,s.crs,s.width,s.height
print(crs,tr,W,H)
def lee(p,rs,band=1,nod=None,src_crs=None):
    o=np.full((H,W),np.nan,'f4')
    with rasterio.open(p) as s:
        a=s.read(band).astype('f4'); nd=s.nodata if nod is None else nod
        if nd is not None and not np.isnan(nd): a[a==nd]=np.nan
        reproject(a,o,src_transform=s.transform,src_crs=src_crs or s.crs,dst_transform=tr,dst_crs=crs,resampling=rs,src_nodata=np.nan,dst_nodata=np.nan)
    return o
lad=gpd.read_file(T7+'04_Tablas_de_trabajo/E1_ladera_reparada.gpkg').to_crs(crs)
ref=gpd.read_file(T7+'04_Tablas_de_trabajo/E1_zona_referencia.gpkg').to_crs(crs)
m_lad=rasterize([(g,1) for g in lad.geometry],(H,W),transform=tr)>0
m_ring=rasterize([(g,1) for g in ref.geometry],(H,W),transform=tr)>0
print('ladera',m_lad.sum(),'anillo',m_ring.sum())
D=U+'CURSOS_CEREGEO_2026/02_Practica/00_COMUN/09_Herramientas/desarrollo_docente/Tp7/'
X=U+'DIAMANTE/COSMO/InSAR HI/subset_CSKS_SCS_HI_HH_RD_15-191018_Stack_ifg_dinsar_flt_TC.data/'
ph=lee(D+'E1_X_Unw_Phase_snaphu_15-19Oct2018.tif',Resampling.average)
comp=lee(D+'E1_X_componentes_snaphu_15-19Oct2018.tif',Resampling.mode)
xd=-0.03123*ph/(4*np.pi); xd[~(np.nan_to_num(comp)>0)]=np.nan
xc=lee(X+'coh_15Oct2018_19Oct2018_HH.img',Resampling.average,src_crs='EPSG:4326'); xc[~(xc>0)]=np.nan
H3=U+'CURSOS_CEREGEO_2026/02_Practica/00_COMUN/08_Originales_crudos/HYP3/E1_DIAMANTE_BARRANCA/S1BB_20181012T092149_20181024T092149_VVP012_INT40_G_weF_AF13/S1BB_20181012T092149_20181024T092149_VVP012_INT40_G_weF_AF13_'
cd=lee(H3+'los_disp.tif',Resampling.nearest); cc=lee(H3+'corr.tif',Resampling.nearest); cc[~(cc>0)]=np.nan
pickle.dump(dict(xd=xd,xc=xc,cd=cd,cc=cc,m_lad=m_lad,m_ring=m_ring,tr=tr,crs=str(crs)),open('datos.pkl','wb'))
print('X coh lad %.3f'%np.nanmean(xc[m_lad]), 'C coh lad %.3f'%np.nanmean(cc[m_lad]))
print('%% lad coh X %.1f C %.1f'%(100*np.mean((np.nan_to_num(xc)>=.3)[m_lad]),100*np.mean((np.nan_to_num(cc)>=.3)[m_lad])))
