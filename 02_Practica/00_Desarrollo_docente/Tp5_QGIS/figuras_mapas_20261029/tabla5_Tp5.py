# Tp5, Tabla 5: mediana de cada indicador por estructura (CCI AGB 2020) y por quema (MapBiomas Fuego 2020), sin agua
# permanente; misma seleccion de pixeles que la Figura 18. Recalculada el 30/10/2026 con el indicadores_20m.tif actual.
# Uso: python tabla5_Tp5.py <indicadores_20m.tif> <MapBiomas_fuego_mes.tif> <CCI_Biomass_v7_AGB.tif> <cobertura_control_20m.tif> <salida.csv>
import sys, csv, numpy as np, rasterio
from rasterio.warp import reproject, Resampling
ind, mes, cci, ctl, out = sys.argv[1:6]
I = rasterio.open(ind)
def a_grilla(f, b, nd=None):
    s = rasterio.open(f); o = np.full(I.shape, np.nan, 'f4'); x = s.read(b).astype('f4')
    if nd is not None: x[x == nd] = np.nan
    reproject(x, o, src_transform=s.transform, src_crs=s.crs, dst_transform=I.transform, dst_crs=I.crs,
              resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
    return o
m = a_grilla(mes, 22); agb = a_grilla(cci, 3, 65535); agua = rasterio.open(ctl).read(1) == 1
q = np.isin(m, (8, 9)) & ~agua; nq = (m == 0) & ~agua
cap = {}
for b, n in ((1, 'dVH_C'), (2, 'dVV_C'), (5, 'dHV_SAOCOM'), (3, 'dHV_ALOS2'), (8, 'dNBR')):
    x = I.read(b).astype('f4'); x[x == I.nodatavals[b - 1]] = np.nan; cap[n] = x
filas = []
for en, e in (('pajonal (< 15 Mg/ha)', agb < 15), ('albardón (≥ 30 Mg/ha)', agb >= 30)):
    for gn, g in (('quemado ago-sep', q), ('no quemado 2020', nq)):
        s = e & g
        f = dict(estrato=en, grupo=gn, pixeles=int((s & np.isfinite(cap['dVH_C'])).sum()))
        for n, x in cap.items(): f[n] = round(float(np.nanmedian(x[s])), 2)
        filas.append(f); print(f)
with open(out, 'w', newline='', encoding='utf-8-sig') as fh:
    w = csv.DictWriter(fh, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)
