# -*- coding: utf-8 -*-
"""
Tp3_04_contexto_y_huellas.py   [SE CORRE]   Tp3, paso 6 de la guia
====================================================================
Las huellas LiDAR del paso 4 con tres productos de contexto que el practico trae en
02_Subsets_SNAP_QGIS\\QGIS_GeoTIFF y que NO estan en el cubo de 20 m (otra grilla, otra fecha):

  - MapBiomas Argentina 2025 (clase de cobertura, unos 30 m): en que cubierta cae cada huella;
  - ESA CCI Biomass v7, AGB 2024 (unos 100 m);
  - BIOMASS L2A FH, altura del bosque (unos 90 m), con su calidad: se compara con la altura del dosel de
    GEDI (rh98) y de ATL08 (h_canopy) en la misma huella. El agua se enmascara antes (MapBiomas y JRC):
    la FH sobre rios y lagunas no es altura de bosque.

Cada producto se lee en su propia grilla, en el pixel donde cae el centro de la huella (vecino mas proximo):
ninguno se remuestrea a 20 m (los productos mas gruesos que la grilla del cubo no se afinan). Ademas corre el
contexto del sitio (cobertura 1985-2025, perdida, fuego, CCI y banda P por clase), con
00_COMUN/contexto_del_sitio.py, el mismo del Tp1.

Solo se usan las huellas con plausible = 1 (columna que escribe Tp3_03: fuera la pasada GEDI del 29/11/2020
y toda huella con mas de 50 m). La tabla de salida conserva todas, con su columna plausible.

SALIDA
  Tp3_Armonizacion/04_Tablas_de_trabajo/<SITIO>_huellas_con_contexto.csv
  Tp3_Armonizacion/05_Resultados/04_Tablas/<SITIO>_huellas_por_clase_MapBiomas.csv
  Tp3_Armonizacion/05_Resultados/04_Tablas/<SITIO>_mapbiomas_*.csv y <SITIO>_contexto_*.csv (contexto del sitio)
  Tp3_Armonizacion/05_Resultados/05_Graficos/<SITIO>_altura_LiDAR_frente_a_FH.png

USO
    python Tp3_04_contexto_y_huellas.py --sitio A2_IBICUY --pixel 20
"""
import argparse
import glob
import os
import re
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import SITIOS, ruta_tp                       # noqa: E402
import contexto_del_sitio                                             # noqa: E402

FH_CALIDAD_MIN = 50.0


def muestrear(ruta, banda, x, y, crs_xy):
    """Valor del pixel donde cae cada punto (vecino mas proximo), en la grilla propia del raster."""
    import rasterio
    from pyproj import Transformer
    with rasterio.open(ruta) as s:
        tr = Transformer.from_crs(crs_xy, s.crs, always_xy=True)
        xx, yy = tr.transform(np.asarray(x), np.asarray(y))
        a = s.read(banda).astype("float32")
        if s.nodata is not None and not np.isnan(s.nodata):
            a[a == s.nodata] = np.nan
        f, c = rasterio.transform.rowcol(s.transform, xx, yy)
        f, c = np.asarray(f), np.asarray(c)
        ok = (f >= 0) & (f < s.height) & (c >= 0) & (c < s.width)
        v = np.full(len(f), np.nan, "float32")
        v[ok] = a[f[ok], c[ok]]
        return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", default="A2_IBICUY", choices=list(SITIOS.keys()))
    ap.add_argument("--pixel", type=int, default=20)
    a = ap.parse_args()
    R = lambda *p: ruta_tp("Tp3", "05_Resultados", *p)              # noqa: E731
    for c in ("04_Tablas", "05_Graficos", "06_Control_calidad"):
        os.makedirs(R(c), exist_ok=True)
    qg = ruta_tp("Tp3", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF")

    # 1. contexto del sitio (el mismo calculo del Tp1, sobre este sitio)
    contexto_del_sitio.correr(a.sitio, qg, R("04_Tablas"), R("05_Graficos"), R("06_Control_calidad"),
                              "Tp3_04_%s_contexto" % a.sitio, graficos_es=True)

    # 2. las huellas del paso 4 con MapBiomas, CCI y FH
    from funciones_comunes import Bitacora
    log = Bitacora(R("06_Control_calidad"), "Tp3_04_%s" % a.sitio)
    tabla = ruta_tp("Tp3", "04_Tablas_de_trabajo", "%s_huellas_con_cubo.csv" % a.sitio)
    if not os.path.exists(tabla):
        log("No existe %s: correr antes Tp3_03_lidar_en_el_cubo.py." % tabla)
        log.cerrar()
        return
    t = pd.read_csv(tabla, encoding="utf-8-sig")
    if "plausible" not in t:
        log("La tabla %s no tiene la columna plausible: vuelva a correr Tp3_03_lidar_en_el_cubo.py." % tabla)
        log.cerrar()
        return
    t["altura_LiDAR_m"] = np.where(t["producto"] == "gedi_l2a", t.get("rh98"), t.get("h_canopy"))
    crs_xy = "EPSG:32721"
    f_cob = sorted(glob.glob(os.path.join(qg, "%s_MapBiomas_cobertura_*.tif" % a.sitio)))
    f_cci = sorted(glob.glob(os.path.join(qg, "%s_CCI_Biomass_*AGB.tif" % a.sitio)))
    f_fh = sorted(glob.glob(os.path.join(qg, "%s_BIOMASS_P_FH_*[0-9].tif" % a.sitio)))
    ley = {}
    if f_cob:
        import rasterio
        with rasterio.open(f_cob[0]) as s:
            ultimo = s.count
            anio = int(s.descriptions[-1].split("_")[-1])
        cl = muestrear(f_cob[0], ultimo, t.x, t.y, crs_xy)
        ley = contexto_del_sitio._leyenda(f_cob[0].replace(".tif", ".qml"))
        t["clase_MapBiomas_%d" % anio] = [("%d %s" % (int(v), ley.get(int(v), ""))).strip() if v > 0 else "sin dato"
                                          for v in np.nan_to_num(cl)]
        col_cl = "clase_MapBiomas_%d" % anio
    else:
        col_cl = None
        log("No hay MapBiomas para %s." % a.sitio)
    if f_cci:
        import rasterio
        with rasterio.open(f_cci[0]) as s:
            d = list(s.descriptions)
        if "AGB_2024" in d:
            t["CCI_AGB_2024"] = muestrear(f_cci[0], d.index("AGB_2024") + 1, t.x, t.y, crs_xy)
    if f_fh:
        t["FH_m"] = muestrear(f_fh[0], 1, t.x, t.y, crs_xy)
        t["FH_calidad"] = muestrear(f_fh[0], 2, t.x, t.y, crs_xy)
        log("Altura FH de BIOMASS: %s" % os.path.basename(f_fh[0]))
        # La FH sobre el agua no es altura de bosque: se enmascara en la grilla de la FH y se
        # descartan las huellas que caen en un pixel de agua.
        from funciones_comunes import mascara_agua, grilla_de_tif
        import rasterio
        gfh = grilla_de_tif(f_fh[0])
        agua, txt_agua = mascara_agua(qg, a.sitio, gfh)
        from pyproj import Transformer
        xx, yy = Transformer.from_crs(crs_xy, gfh["crs"], always_xy=True).transform(np.asarray(t.x), np.asarray(t.y))
        f, c = rasterio.transform.rowcol(gfh["transform"], xx, yy)
        f, c = np.asarray(f), np.asarray(c)
        ok = (f >= 0) & (f < gfh["height"]) & (c >= 0) & (c < gfh["width"])
        en_agua = np.zeros(len(t), bool)
        en_agua[ok] = agua[f[ok], c[ok]]
        t["FH_en_agua"] = en_agua.astype(int)
        t.loc[en_agua, ["FH_m", "FH_calidad"]] = np.nan
        log("Mascara de agua para la FH: %s; %d huellas en agua quedan sin FH." % (txt_agua, int(en_agua.sum())))
    out = ruta_tp("Tp3", "04_Tablas_de_trabajo", "%s_huellas_con_contexto.csv" % a.sitio)
    t.to_csv(out, index=False, encoding="utf-8-sig")
    log("Huellas: %d (GEDI %d, ATL08 %d); plausibles: %d" % (len(t), (t.producto == "gedi_l2a").sum(),
                                                             (t.producto == "atl08").sum(), int(t.plausible.sum())))
    tt = t                                  # tabla completa (se guarda)
    t = t[t.plausible == 1].copy()          # lo que sigue usa solo las huellas plausibles

    # 3. resumen por clase de MapBiomas
    if col_cl:
        cols_db = [c for c in t.columns if c.endswith("_dB") and ("HV" in c or "VH" in c)]
        filas = []
        for c, g in t.groupby(col_cl):  # huellas plausibles
            r = {"clase": c, "huellas": len(g), "altura_LiDAR_mediana_m": round(float(g.altura_LiDAR_m.median()), 1)}
            for k in ("CCI_AGB_2024", "FH_m"):
                if k in g:
                    r[k + "_mediana"] = round(float(g[k].median()), 1)
            for k in cols_db:
                r[k + "_mediana"] = round(float(g[k].median()), 1)
            filas.append(r)
        pc = pd.DataFrame(filas).sort_values("huellas", ascending=False)
        pc.to_csv(R("04_Tablas", "%s_huellas_por_clase_MapBiomas.csv" % a.sitio), index=False, encoding="utf-8-sig")
        log.titulo("Huellas por clase de MapBiomas %d (medianas)" % anio)
        for r in pc.itertuples(index=False):
            dd = r._asdict()
            log("  %-34s %6d huellas  altura LiDAR %5.1f m  CCI %5s  FH %5s" % (
                dd["clase"][:34], dd["huellas"], dd["altura_LiDAR_mediana_m"],
                dd.get("CCI_AGB_2024_mediana", "-"), dd.get("FH_m_mediana", "-")))

    # 4. altura LiDAR frente a FH
    if "FH_m" in t:
        log.titulo("Altura del dosel LiDAR frente a la altura FH de BIOMASS")
        for nom, sub in (("todas", t), ("calidad FH >= %d" % FH_CALIDAD_MIN, t[t.FH_calidad >= FH_CALIDAD_MIN])):
            s = sub[["altura_LiDAR_m", "FH_m"]].dropna()
            if len(s) > 10:
                rho = s.corr(method="spearman").iloc[0, 1]
                sesgo = (s.FH_m - s.altura_LiDAR_m).median()
                log("  %-18s n = %6d   Spearman %.2f   mediana FH - LiDAR %+.1f m" % (nom, len(s), rho, sesgo))
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        s = t[["altura_LiDAR_m", "FH_m"]].dropna()
        fig, ax = plt.subplots(figsize=(7, 6))
        hb = ax.hexbin(s.altura_LiDAR_m, s.FH_m, gridsize=50, bins="log", cmap="viridis", mincnt=1)
        m = max(30, np.nanpercentile(s.values, 99))
        ax.plot([0, m], [0, m], "w--", lw=1)
        ax.set_xlim(0, m); ax.set_ylim(0, m)
        ax.set_xlabel("Altura del dosel LiDAR (m): GEDI rh98 o ATL08 h_canopy")
        ax.set_ylabel("Altura del bosque FH de BIOMASS (m)")
        ax.set_title("%s: altura LiDAR frente a FH, sin agua (%s huellas)" % (a.sitio, ("{:,}".format(len(s))).replace(",", ".")))
        contexto_del_sitio.formato_es(ax, decimales=0)
        fig.colorbar(hb, ax=ax, label="huellas (escala logarítmica)")
        fig.tight_layout()
        fig.savefig(R("05_Graficos", "%s_altura_LiDAR_frente_a_FH.png" % a.sitio), dpi=150)
        plt.close(fig)
    log("")
    log("Tabla de huellas: " + out)
    log.cerrar("QGIS y Orange (08_Orange/Tp3_C_contexto_de_las_huellas.ows)")


if __name__ == "__main__":
    main()
