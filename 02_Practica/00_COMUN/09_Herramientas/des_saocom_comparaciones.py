# -*- coding: utf-8 -*-
"""
des_saocom_comparaciones.py  (docente)

Rehace las comparaciones con SAOCOM que se citan en los Desarrollos de los
Tp2, Tp3, Tp8, Tp9 y Tp10 y deja una tabla por practico en
<Tp>\\05_Resultados\\04_Tablas\\*_SAOCOM_*.csv. La del Tp6 la hace Tp6_02
(--l_relativo --l_solo_lenoso).

USO (desde 00_COMUN\\09_Herramientas, entorno sar):
    python des_saocom_comparaciones.py
    python des_saocom_comparaciones.py --base D:\\CURSOS_CEREGEO_2026\\02_Practica --solo Tp9

Los SAOCOM (gamma0 lineal, 20 m) se llevan a la grilla de cada practico con
interpolacion bilineal. Toda comparacion en dB se hace sobre medianas de dB;
las medias por poligono del Tp2 se promedian en lineal, como en Tp2_03.
"""
import argparse, os
import numpy as np, pandas as pd, rasterio as r, geopandas as gpd
from rasterio.warp import reproject, Resampling
from rasterio.features import rasterize
from scipy import ndimage

def db(x):
    x = np.asarray(x, dtype="f8")
    return 10 * np.log10(np.where(x > 0, x, np.nan))

def a_grilla(ruta, ref, metodo=Resampling.bilinear, banda=1):
    s = r.open(ruta)
    o = np.full(ref.shape, np.nan)
    a = s.read(banda).astype("f8")
    if metodo != Resampling.nearest:
        a[a <= 0] = np.nan
    reproject(a, o, src_transform=s.transform, src_crs=s.crs, dst_transform=ref.transform,
              dst_crs=ref.crs, resampling=metodo, src_nodata=np.nan, dst_nodata=np.nan)
    return o

def sao(B, tp, nombre, pol):
    return os.path.join(B, tp, "02_Subsets_SNAP_QGIS", "SAOCOM_gamma0", "QGIS_GeoTIFF",
                        "%s_Gamma0_%s.tif" % (nombre, pol))

def guardar(B, tp, nombre, t):
    d = os.path.join(B, tp, "05_Resultados", "04_Tablas"); os.makedirs(d, exist_ok=True)
    f = os.path.join(d, nombre); t.to_csv(f, index=False, encoding="utf-8-sig"); print("  ->", f)
    print(t.to_string(index=False)); print()

def tp10(B):
    print("== Tp10: SAOCOM 16/09/2026 frente a NISAR 18/09/2026 (B_CONCORDIA)")
    T = os.path.join(B, "Tp10_Impacto_urbano")
    u = r.open(os.path.join(T, "02_Subsets_SNAP_QGIS", "B_CONCORDIA_urbano_por_banda_20m.tif"))
    U = {n: u.read(i + 1).astype("f8") for i, n in enumerate(u.descriptions)}
    nom = "B_CONCORDIA_SAOCOM_L_20260916_QP_gamma0"
    HH, HV, VV = [db(a_grilla(sao(B, "Tp10_Impacto_urbano", nom, p), u)) for p in ("HH", "HV", "VV")]
    nhh, nhv = db(U["L_HH"]), db(U["L_HV"])
    filas = []
    m = np.isfinite(HH) & np.isfinite(nhh); m2 = np.isfinite(HV) & np.isfinite(nhv)
    filas.append(dict(medida="HH SAOCOM - NISAR, mediana (dB)", valor=np.median(HH[m] - nhh[m])))
    filas.append(dict(medida="HH r de Pearson (dB)", valor=np.corrcoef(HH[m], nhh[m])[0, 1]))
    filas.append(dict(medida="HV SAOCOM - NISAR, mediana (dB)", valor=np.median(HV[m2] - nhv[m2])))
    filas.append(dict(medida="HV r de Pearson (dB)", valor=np.corrcoef(HV[m2], nhv[m2])[0, 1]))
    S, N = HH > 0, nhh > 0
    cc = a_grilla(os.path.join(B, "Tp4_Validacion", "02_Subsets_SNAP_QGIS", "B_CONCORDIA_cobertura_control_20m.tif"), u, Resampling.nearest)
    for nombre, k in [("sitio", m), ("control urbano (7)", m & (cc == 7)), ("control monte (3)", m & (cc == 3))]:
        filas += [dict(medida="%% %s urbano SAOCOM (HH > 0 dB)" % nombre, valor=100 * S[k].mean()),
                  dict(medida="%% %s urbano NISAR (HH > 0 dB)" % nombre, valor=100 * N[k].mean()),
                  dict(medida="%% %s urbano en los dos" % nombre, valor=100 * (S & N)[k].mean())]
    tr = gpd.read_file(os.path.join(T, "04_Tablas_de_trabajo", "entrenamiento_B_CONCORDIA.gpkg")).to_crs(u.crs)
    lab = rasterize(((g, c) for g, c in zip(tr.geometry, tr.codigo)), out_shape=u.shape, transform=u.transform, fill=0)
    for c, cl in tr[["codigo", "clase"]].drop_duplicates().sort_values("codigo").values:
        k = lab == c
        filas += [dict(medida="%s: %% urbano SAOCOM / NISAR" % cl, valor="%.1f / %.1f" % (100 * S[k].mean(), 100 * N[k].mean())),
                  dict(medida="%s: mediana HH, VV, HV, HH-VV (dB)" % cl,
                       valor="%.1f, %.1f, %.1f, %.1f" % tuple(np.nanmedian(x[k]) for x in (HH, VV, HV, HH - VV)))]
    t = pd.DataFrame(filas); t["valor"] = [("%.2f" % v) if isinstance(v, float) else v for v in t.valor]
    guardar(B, "Tp10_Impacto_urbano", "B_CONCORDIA_SAOCOM_frente_a_NISAR.csv", t)

def tp9(B):
    print("== Tp9: cambio de HV SAOCOM 2021-2026 frente a NISAR 2026 / ALOS-2 2021 (C_FEDERAL)")
    T = os.path.join(B, "Tp9_Deforestacion")
    p = r.open(os.path.join(T, "02_Subsets_SNAP_QGIS", "C_pila_temporal_20m.tif"))
    P = {n: p.read(i + 1).astype("f8") for i, n in enumerate(p.descriptions)}
    dS = db(a_grilla(sao(B, "Tp9_Deforestacion", "C_FEDERAL_SAOCOM_L_20260911_QP_gamma0", "HV"), p)) - \
         db(a_grilla(sao(B, "Tp9_Deforestacion", "C_FEDERAL_SAOCOM_L_20210804_QP_gamma0", "HV"), p))
    dL = db(P["L_NISAR_2026_HV"]) - db(P["L_ALOS2_2021_HV"])
    mS, mL = np.nanmedian(dS), np.nanmedian(dL)
    rS, rL = dS - mS, dL - mL
    cl = r.open(os.path.join(T, "05_Resultados", "02_Rasters", "C_perdida_degradacion.tif")).read(1)
    filas = [dict(clase="todo el sitio (mediana del cambio, dB)", SAOCOM=mS, NISAR_ALOS2=mL)]
    for c, n in [(1, "perdida"), (2, "degradacion"), (3, "monte estable"), (4, "no bosque estable")]:
        k = cl == c
        filas.append(dict(clase="%s: %% con caida relativa > 3 dB" % n, SAOCOM=100 * np.nanmean(rS[k] < -3), NISAR_ALOS2=100 * np.nanmean(rL[k] < -3)))
        filas.append(dict(clase="%s: mediana relativa (dB)" % n, SAOCOM=np.nanmedian(rS[k]), NISAR_ALOS2=np.nanmedian(rL[k])))
    pt = pd.read_csv(os.path.join(T, "08_Orange", "datos", "Tp9_C_puntos_etiquetados.csv"))
    fi = ((p.transform.f - pt.y) / p.transform.a).astype(int); co = ((pt.x - p.transform.c) / p.transform.a).astype(int)
    pt["rS"] = rS[fi, co]; pt["rL"] = dL[fi, co] - mL
    for g, s in pt.groupby("referencia"):
        filas.append(dict(clase="puntos '%s' (%d): con caida relativa > 3 dB" % (g, len(s)), SAOCOM=float((s.rS < -3).sum()), NISAR_ALOS2=float((s.rL < -3).sum())))
    t = pd.DataFrame(filas).round(2)
    guardar(B, "Tp9_Deforestacion", "C_SAOCOM_cambio_HV_por_clase.csv", t)

def tp8(B):
    print("== Tp8: SAOCOM 11/09/2023 por frecuencia de suelo desnudo (F_BOVRIL)")
    T = os.path.join(B, "Tp8_Erosion_suelos")
    f = r.open(os.path.join(T, "02_Subsets_SNAP_QGIS", "F_frecuencia_suelo_desnudo_2023_10m.tif")); F = f.read(1)
    nom = "F_BOVRIL_SAOCOM_L_20230911_QP_gamma0"
    HH, HV, VV = [db(a_grilla(sao(B, "Tp8_Erosion_suelos", nom, q), f, Resampling.nearest)) for q in ("HH", "HV", "VV")]
    grupos = {"nunca": F == 0, "1 a 2 meses": (F >= 1) & (F <= 2), "3 a 5 meses": (F >= 3) & (F <= 5), "6 o mas meses": F >= 6}
    e = gpd.read_file(os.path.join(T, "04_Tablas_de_trabajo", "entrenamiento_F.gpkg")).to_crs(f.crs)
    lab = rasterize(((g, c) for g, c in zip(e.geometry, e.codigo)), out_shape=F.shape, transform=f.transform, fill=0)
    grupos["poligonos de surcos o carcavas (1)"] = lab == 1
    grupos["poligonos estables o labrados (2)"] = lab == 2
    filas = [dict(grupo=n, pixeles=int((k & np.isfinite(HH)).sum()), HH=np.nanmedian(HH[k]), VV=np.nanmedian(VV[k]), HV=np.nanmedian(HV[k]),
                  HH_menos_VV=np.nanmedian((HH - VV)[k])) for n, k in grupos.items()]
    guardar(B, "Tp8_Erosion_suelos", "F_SAOCOM_por_frecuencia_suelo_desnudo.csv", pd.DataFrame(filas).round(2))

def tp2_tp3(B, franja_m=2500):
    from skimage.registration import phase_cross_correlation
    print("== Tp2: SAOCOM 24/09/2026 frente a NISAR 30/09/2026 (A2_IBICUY), sin %d m del borde del haz" % franja_m)
    T = os.path.join(B, "Tp2_SAR_multibanda")
    p = r.open(os.path.join(T, "02_Subsets_SNAP_QGIS", "A2_IBICUY_pila_gamma0_lineal.tif")); D = list(p.descriptions)
    cap = lambda n: p.read(D.index(n) + 1).astype("f8")
    nom = "A2_IBICUY_SAOCOM_L_20260924_QP_gamma0"
    HH, HV, VV = [a_grilla(sao(B, "Tp2_SAR_multibanda", nom, q), p) for q in ("HH", "HV", "VV")]
    lejos = ndimage.distance_transform_edt(np.isfinite(HH)) * p.transform.a > franja_m
    def sm(x, n=5):
        m = np.isfinite(x); v = ndimage.uniform_filter(np.where(m, x, 0), n); w = ndimage.uniform_filter(m.astype(float), n)
        return np.where(w > .5, v / np.where(w > 0, w, 1), np.nan)
    filas = [dict(medida="% del sitio con dato SAOCOM", valor=100 * np.isfinite(HH).mean()),
             dict(medida="% del sitio con dato lejos del borde", valor=100 * lejos.mean())]
    for a, b, n in [(HH, cap("L_NISAR_gamma0_HH_20260930"), "HH"), (HV, cap("L_NISAR_gamma0_HV_20260930"), "HV")]:
        x, y = db(sm(a)), db(sm(b)); m = np.isfinite(x) & np.isfinite(y) & lejos
        filas += [dict(medida="%s r (50 m)" % n, valor=np.corrcoef(x[m], y[m])[0, 1]), dict(medida="%s SAOCOM - NISAR mediana (dB)" % n, valor=np.median(x[m] - y[m]))]
    cub = gpd.read_file(os.path.join(T, "04_Tablas_de_trabajo", "cubiertas_A2_IBICUY.gpkg")).to_crs(p.crs)
    cls = list(dict.fromkeys(cub.clase))
    lab = rasterize(((g, cls.index(c) + 1) for g, c in zip(cub.geometry, cub.clase)), out_shape=p.shape, transform=p.transform, fill=0)
    for i, c in enumerate(cls):
        k = (lab == i + 1) & lejos & np.isfinite(HH)
        if k.sum():
            filas.append(dict(medida="%s (%d px lejos del borde): HH, HV, VV, HH-VV (dB, media lineal)" % (c, k.sum()),
                              valor="%.1f, %.1f, %.1f, %.1f" % (db(np.mean(HH[k])), db(np.mean(HV[k])), db(np.mean(VV[k])), db(np.mean(HH[k])) - db(np.mean(VV[k])))))
        else:
            filas.append(dict(medida="%s: todos sus pixeles caen en la franja del borde" % c, valor=""))
    t = pd.DataFrame(filas); t["valor"] = [("%.2f" % v) if isinstance(v, float) else v for v in t.valor]
    guardar(B, "Tp2_SAR_multibanda", "A2_IBICUY_SAOCOM_frente_a_NISAR.csv", t)

    print("== Tp3: corregistro de SAOCOM HV (mismo metodo que Tp3_02)")
    T3 = os.path.join(B, "Tp3_Armonizacion")
    c = r.open(os.path.join(T3, "02_Subsets_SNAP_QGIS", "A2_IBICUY_cubo_20m.tif")); D3 = list(c.descriptions)
    hv = a_grilla(sao(B, "Tp3_Armonizacion", nom, "HV"), c)
    hv = np.where(ndimage.distance_transform_edt(np.isfinite(hv)) * c.transform.a > franja_m, hv, np.nan)
    def bordes(x, radar):
        y = db(x) if radar else x.astype("f8"); y = np.where(np.isfinite(y), y, np.nanmedian(y))
        if radar: y = ndimage.uniform_filter(y, 3)
        g = np.hypot(ndimage.sobel(y, 1), ndimage.sobel(y, 0)); return (g - g.mean()) / (g.std() + 1e-12)
    filas = []
    for refn in ("L_NISAR_gamma0_HV_20260930", "OPT_S2_B08"):
        R = c.read(D3.index(refn) + 1).astype("f8"); ref = bordes(R, not refn.startswith("OPT_")); mov = bordes(hv, True)
        com = np.isfinite(R) & np.isfinite(hv); H, W = ref.shape
        for i in range(4):
            for j in range(4):
                f0, f1, c0, c1 = i * H // 4, (i + 1) * H // 4, j * W // 4, (j + 1) * W // 4
                if com[f0:f1, c0:c1].mean() < 0.8: continue
                rv, mv = ref[f0:f1, c0:c1], mov[f0:f1, c0:c1]
                d, _, _ = phase_cross_correlation(rv, mv, upsample_factor=10)
                ms = ndimage.shift(mv, d, order=1, mode="nearest")
                ca, cd = np.corrcoef(rv.ravel(), mv.ravel())[0, 1], np.corrcoef(rv.ravel(), ms.ravel())[0, 1]
                filas.append(dict(ref=refn, ventana="%d,%d" % (i, j), dy_px=round(d[0], 2), dx_px=round(d[1], 2),
                                  corr_antes=round(ca, 3), corr_despues=round(cd, 3), usada=cd >= ca))
    t = pd.DataFrame(filas)
    for refn, s in t.groupby("ref"):
        u = s[s.usada]
        print("  %s: %d ventanas, %d usadas; dx %.2f px (%+.0f m este), dy %.2f px (%+.0f m norte), dispersion %.2f / %.2f px"
              % (refn, len(s), len(u), u.dx_px.median(), 20 * u.dx_px.median(), u.dy_px.median(), -20 * u.dy_px.median(), u.dx_px.std(), u.dy_px.std()))
    guardar(B, "Tp3_Armonizacion", "A2_IBICUY_corregistro_SAOCOM_HV.csv", t)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    ap.add_argument("--solo", choices=["Tp2", "Tp8", "Tp9", "Tp10"], default=None, help="Tp2 incluye el Tp3")
    a = ap.parse_args()
    for n, f in [("Tp10", tp10), ("Tp9", tp9), ("Tp8", tp8), ("Tp2", tp2_tp3)]:
        if a.solo in (None, n):
            f(a.base)

if __name__ == "__main__":
    main()
