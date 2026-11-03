import numpy as np, pickle, rasterio
from rasterio.warp import reproject, Resampling
d=pickle.load(open('datos.pkl','rb')); tr=d['tr']; H,W=d['m_lad'].shape
U='/mnt/user-data/uploads/CURSOS_CEREGEO_2026/02_Practica/Tp7_Barrancas_deslizamientos/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/E1_DIAMANTE_BARRANCA_MapBiomas_cobertura_1985_2025.tif'
def nmad(v): v=v[np.isfinite(v)]; return 1.4826*np.median(np.abs(v-np.median(v)))
with rasterio.open(U) as s:
    agua=np.zeros((H,W),bool)
    occ=np.zeros((H,W),'f4')
    for b in range(1,s.count+1):
        o=np.zeros((H,W),'f4'); reproject(s.read(b).astype('f4'),o,src_transform=s.transform,src_crs=s.crs,dst_transform=tr,dst_crs=d['crs'],resampling=Resampling.nearest)
        occ+= (o==33)
    occ=100*occ/s.count
for thr in (50,):
    agua=occ>=thr
    m_ref=d['m_ring']&~agua
    print('agua MB>=%d'%thr,(d['m_ring']&agua).sum(),'ref',m_ref.sum())
    for k,(ds,c) in {'X':(d['xd'],d['xc']),'C':(d['cd'],d['cc'])}.items():
        ok=np.isfinite(ds)&np.isfinite(c)&(c>=.3)
        r=np.nanmedian(ds[ok&m_ref]); rel=ds-r
        v=rel[ok&m_ref]; print(k,'NMAD %.2f mm std %.2f'%(1000*nmad(v),1000*np.nanstd(v)),'med lad %.2f p5 %.2f'%(1000*np.nanmedian(rel[ok&d['m_lad']]),1000*np.nanpercentile(rel[ok&d['m_lad']],5)))
pickle.dump(m_ref,open('mref.pkl','wb'))
