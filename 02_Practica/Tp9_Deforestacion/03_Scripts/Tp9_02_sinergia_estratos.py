# -*- coding: utf-8 -*-
"""
Tp9_02_sinergia_estratos.py   [SE CORRE]   Tp9, paso 2 de la guia - SINERGIA
====================================================================
Que estrato ve cada banda: copa (C), ramas y troncos (L), troncos y suelo
(P) (guia teorico-practica, seccion 12.4, paso 2).

Se responde con el LiDAR como referencia de estructura: en cada huella GEDI
valida del sitio se toma el valor de cada capa de la pila (Tp9_01) y se mide
cuanto sigue cada banda a la altura del dosel (rh98):

  - correlacion de rangos de Spearman entre la banda (dB) y rh98, con su
    intervalo de confianza del 95 % por remuestreo de CELDAS de 200 m (500
    repeticiones, semilla fija). No se informa el p-valor: con decenas de miles
    de huellas vecinas, que no son independientes, siempre da 0 y no dice nada;
  - curva de respuesta: mediana de la banda por clase de altura (0-2, 2-5,
    5-8, 8-12, 12-16, > 16 m), con el numero de huellas de cada clase. El
    "rango de la curva" usa solo las clases con al menos --min_huellas_clase
    huellas (100 por defecto). Donde la curva se aplana, la banda SATURA.
  - huellas con rh98 mayor que --rh98_max (60 m por defecto; 20 m es lo
    plausible en el monte del Espinal, de 3 a 8 m) se dejan afuera y se cuentan.

Nada se fusiona: cada banda se evalua por separado y el resultado es una
explicacion fisica (que ve cada una), que justifica despues que rasgos
entran al modelo de Tp9_03.

ADVERTENCIA DE FECHA: las huellas GEDI son de 2019-2023 y 2024-2025; la pila
mezcla 2011, 2021, 2023 y 2026. Se usan solo las capas cuya fecha este a
menos de --dias_max de la huella (por defecto 2 anos) y se informa cuantas
huellas quedaron en cada comparacion.

PARTE B   BANDA P. BIOMASS cubre Federal: el L1B DGM del 12/08/2026 (franja S2,
traza 006, cuadro 284, pasada ascendente) recortado al sitio en
02_Subsets_SNAP_QGIS\\QGIS_GeoTIFF\\C_FEDERAL_BIOMASS_P_20260812.tif (gamma0 HH,
HV, VH, VV LINEAL). Ese GeoTIFF esta en geometria de radar con 121 puntos de
control: el programa lo ubica con ellos (WarpedVRT de GDAL) en la proyeccion
de las huellas. Se hace la misma comparacion con las huellas GEDI validas de
Federal, con el mismo filtro de fecha (--dias_max respecto del 12/08/2026).
Con --p_tif se puede pasar otro GeoTIFF; con --sin_p se omite. Para la franja D
(La Paz - Villaguay), con sus propias huellas GEDI:
  --p_tif ..\\02_Subsets_SNAP_QGIS\\QGIS_GeoTIFF\\D_LAPAZ_VILLAGUAY_BIOMASS_P_20260917_S1_UTM21S.tif
  --p_fecha 2026-09-17 --p_sitio D_LAPAZ_VILLAGUAY
(la banda P del 17/09/2026 ya reproyectada a EPSG:32721, 25 m; cubre la mitad este de la franja).

PARTE C   DEGRADACION CON GEDI (guia, seccion 12.4: caida de altura GEDI
sin cambio de cobertura optica). Como GEDI no repite huellas, se compara la
mediana de rh98 por CELDA (200 m) entre un periodo 1 (hasta 2022) y un
periodo 2 (desde la reactivacion de GEDI, 26/04/2024). Una celda es candidata
a degradacion si antes era monte (rh98 >= 5 m), bajo 3 m o mas y el NDVI no
cambio (|dNDVI| < 0,05, mediana de la celda). Es evidencia independiente del mapa de Tp9_03.
Por defecto el dNDVI es el ultimo NDVI de la pila menos el primero (2026 - 2021),
que NO son las fechas de las huellas (el periodo 2 termina el 28/06/2025): se
declara. Con --ndvi_p1 y --ndvi_p2 se eligen otras capas de la pila o GeoTIFF
de NDVI externos (por ejemplo el Sentinel-2 del 24/09/2025).

ENTRADA  la pila de Tp9_01 y lidar_C_FEDERAL.gpkg (Tp1_05)
SALIDA   Tp9_Deforestacion/05_Resultados/04_Tablas/C_sensibilidad_a_la_altura.csv
         Tp9_Deforestacion/05_Resultados/05_Graficos/C_curvas_de_respuesta.png
         Tp9_Deforestacion/05_Resultados/04_Tablas/C_delta_rh98_por_celda.csv
         Tp9_Deforestacion/02_Subsets_SNAP_QGIS/C_delta_rh98_<pixel>m.tif
USO      python Tp9_02_sinergia_estratos.py --pixel 20
         python Tp9_02_sinergia_estratos.py --pixel 20 --rh98_max 20
         python Tp9_02_sinergia_estratos.py --pixel 20 --ndvi_p2 ..\\02_Subsets_SNAP_QGIS\\QGIS_GeoTIFF\\C_FEDERAL_S2_20250924_NDVI.tif
"""
import argparse
import os
import re
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import ruta_tp                               # noqa: E402
from funciones_comunes import leer_tif, lin_a_db, Bitacora            # noqa: E402

SITIO = "C_FEDERAL"
CLASES_H = [0, 2, 5, 8, 12, 16, 60]


def main():
    import geopandas as gpd
    from scipy.stats import spearmanr

    ap = argparse.ArgumentParser()
    ap.add_argument("--pixel", type=int, default=20)
    ap.add_argument("--dias_max", type=int, default=730)
    ap.add_argument("--p_tif", default=ruta_tp("Tp9", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF",
                                               "C_FEDERAL_BIOMASS_P_20260812.tif"),
                    help="GeoTIFF de BIOMASS (gamma0 lineal; por defecto el L1B DGM de Federal del 12/08/2026)")
    ap.add_argument("--p_fecha", default="2026-08-12", help="fecha de la escena BIOMASS (filtro --dias_max)")
    ap.add_argument("--p_en_db", action="store_true", help="si el GeoTIFF de BIOMASS ya esta en dB")
    ap.add_argument("--sin_p", action="store_true", help="omitir la parte B (banda P)")
    ap.add_argument("--p_sitio", default=SITIO,
                    help="sitio de las huellas GEDI de la parte B (por defecto Federal; D_LAPAZ_VILLAGUAY para la franja D)")
    ap.add_argument("--p1_hasta", default="2022-12-31")
    ap.add_argument("--p2_desde", default="2024-04-26")
    ap.add_argument("--celda", type=float, default=200.0)
    ap.add_argument("--monte_min", type=float, default=5.0)
    ap.add_argument("--u_rh98", type=float, default=-3.0)
    ap.add_argument("--u_dndvi", type=float, default=0.05)
    ap.add_argument("--rh98_max", type=float, default=60.0,
                    help="huellas con rh98 mayor que esto quedan afuera (20 m es lo plausible en el Espinal)")
    ap.add_argument("--min_huellas_clase", type=int, default=100,
                    help="clases de altura con menos huellas no entran al rango de la curva")
    ap.add_argument("--bootstrap", type=int, default=500, help="repeticiones del IC de rho (0 = no calcularlo)")
    ap.add_argument("--semilla", type=int, default=2026)
    ap.add_argument("--ndvi_p1", default="", help="NDVI anterior de la parte C: nombre de capa de la pila o GeoTIFF")
    ap.add_argument("--ndvi_p2", default="", help="NDVI posterior de la parte C: nombre de capa de la pila o GeoTIFF")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp9", "05_Resultados", "06_Control_calidad"), "Tp9_02_sinergia")
    pila_r = ruta_tp("Tp9", "02_Subsets_SNAP_QGIS", "C_pila_temporal_%dm.tif" % a.pixel)
    capas, perfil, tags = leer_tif(pila_r)
    T = perfil["transform"]
    gp = ruta_tp("Tp1", "05_Resultados", "03_Vectores", "lidar_%s.gpkg" % SITIO)
    if not os.path.exists(gp):
        sys.exit("Falta %s: correr Tp1_05_buscar_lidar.py --sitio C_FEDERAL --descargar" % gp)
    h = gpd.read_file(gp, layer="gedi_l2a").to_crs(perfil["crs"])
    h = h[h.valido.astype(bool)]
    fuera = int((h.rh98 > a.rh98_max).sum())
    h = h[~(h.rh98 > a.rh98_max)]
    log("Huellas con rh98 > %.0f m (implausibles): %d, quedan afuera." % (a.rh98_max, fuera))
    col = ((h.geometry.x - T.c) / T.a).astype(int).values
    fil = ((h.geometry.y - T.f) / T.e).astype(int).values
    dentro = (col >= 0) & (col < perfil["width"]) & (fil >= 0) & (fil < perfil["height"])
    h, col, fil = h[dentro], col[dentro], fil[dentro]
    log("Huellas GEDI validas dentro de la pila: %d (%s a %s)" % (len(h), h.fecha.min(), h.fecha.max()))
    filas, curvas, conteos = [], {}, {}
    rng = np.random.default_rng(a.semilla)

    def rho_ic(y, x, celdas):
        """IC 95 % de rho remuestreando celdas de 200 m enteras (las huellas vecinas no son independientes)."""
        if a.bootstrap <= 0:
            return np.nan, np.nan
        u, inv = np.unique(celdas, return_inverse=True)
        grupos = [np.flatnonzero(inv == k) for k in range(u.size)]
        vals = []
        for _ in range(a.bootstrap):
            idx = np.concatenate([grupos[k] for k in rng.integers(0, u.size, u.size)])
            vals.append(spearmanr(y[idx], x[idx])[0])
        return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))

    def rango_valido(curva, n):
        ok_ = n >= a.min_huellas_clase
        return float(curva[ok_].max() - curva[ok_].min()) if ok_.sum() >= 2 else np.nan
    for n, arr in capas.items():
        m = re.search(r"_(\d{4})_", n + "_")
        anio = int(m.group(1)) if m else None
        v = arr[fil, col]
        es_radar = not n.startswith("O_")
        y = lin_a_db(v) if es_radar else v
        cerca = np.ones(len(h), bool)
        if anio:
            dias = np.abs((pd.to_datetime(h.fecha) - pd.Timestamp("%d-07-01" % anio)).dt.days.values)
            cerca = dias <= a.dias_max
        ok = np.isfinite(y) & cerca & np.isfinite(h.rh98.values)
        if ok.sum() < 20:
            log("  %-26s solo %d huellas cercanas en fecha: no se evalua" % (n, ok.sum()))
            continue
        rho, _ = spearmanr(y[ok], h.rh98.values[ok])
        cls = pd.cut(h.rh98.values[ok], CLASES_H)
        gr = pd.Series(y[ok]).groupby(cls, observed=False)
        curva, nn = gr.median(), gr.count()
        curvas[n], conteos[n] = curva, nn
        rango = rango_valido(curva, nn)
        celdas = (np.floor(h.geometry.x.values[ok] / 200).astype(int) * 100000
                  + np.floor(h.geometry.y.values[ok] / 200).astype(int))
        lo, hi = rho_ic(y[ok], h.rh98.values[ok], celdas)
        filas.append({"capa": n, "huellas": int(ok.sum()), "celdas_200m": int(np.unique(celdas).size),
                      "spearman_rho": round(float(rho), 3), "rho_IC95_inf": round(lo, 3), "rho_IC95_sup": round(hi, 3),
                      "rango_de_la_curva": round(rango, 2), "unidad": "dB" if es_radar else "NDVI",
                      "huellas_por_clase": " ".join("%s:%d" % (str(k), v) for k, v in nn.items())})
        log("  %-26s n=%5d  rho=%+.2f [%+.2f, %+.2f]  rango de la curva %.2f %s"
            % (n, ok.sum(), rho, lo, hi, rango, "dB" if es_radar else "(NDVI)"))
    t = pd.DataFrame(filas).sort_values("spearman_rho", ascending=False)
    out = ruta_tp("Tp9", "05_Resultados", "04_Tablas", "C_sensibilidad_a_la_altura.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    t.to_csv(out, index=False, encoding="utf-8-sig")

    log("")
    log("Lectura: la banda que mas sube con la altura y no se aplana es la que 've' la estructura")
    log("lenosa. Si C se aplana a pocos metros y L sigue subiendo, eso es lo que predice la fisica:")
    log("la onda de 5,5 cm interactua con hojas y ramitas de la copa; la de ~24 cm, con ramas y troncos; la P (69 cm), con troncos y suelo.")

    # ------------------------------------------------ parte B: banda P (Federal)
    if not a.sin_p and os.path.exists(a.p_tif):
        import rasterio
        from rasterio.vrt import WarpedVRT
        log.titulo("Banda P (BIOMASS, %s) frente a GEDI en %s" % (a.p_fecha, a.p_sitio))
        hp = h
        if a.p_sitio != SITIO:                    # huellas GEDI del otro sitio (franja D)
            gp2 = ruta_tp("Tp1", "05_Resultados", "03_Vectores", "lidar_%s.gpkg" % a.p_sitio)
            if not os.path.exists(gp2):
                sys.exit("Falta %s: correr Tp1_05_buscar_lidar.py --sitio %s --descargar" % (gp2, a.p_sitio))
            hp = gpd.read_file(gp2, layer="gedi_l2a").to_crs(perfil["crs"])
            hp = hp[hp.valido.astype(bool) & ~(hp.rh98 > a.rh98_max)]
            log("Huellas GEDI validas de %s: %d (%s a %s)" % (a.p_sitio, len(hp), hp.fecha.min(), hp.fecha.max()))
        dias = np.abs((pd.to_datetime(hp.fecha) - pd.Timestamp(a.p_fecha)).dt.days.values)
        cerca = dias <= a.dias_max
        log("Huellas GEDI validas a menos de %d dias de la escena BIOMASS: %d de %d"
            % (a.dias_max, cerca.sum(), len(hp)))
        with rasterio.open(a.p_tif) as src:
            # en geometria de radar se ubica con sus puntos de control; en otra proyeccion, se lleva a la de la pila
            vista = WarpedVRT(src, crs=perfil["crs"]) if (src.crs is None or src.crs != perfil["crs"]) else src
            if src.crs is None:
                log("  %s viene en geometria de radar: se ubica con sus %d puntos de control."
                    % (os.path.basename(a.p_tif), len(src.gcps[0])))
            else:
                log("  %s viene proyectado (%s)." % (os.path.basename(a.p_tif), src.crs.to_string()))
            xy = list(zip(hp.geometry.x, hp.geometry.y))
            muestras = np.array([x for x in vista.sample(xy)], "float64")
            for b in range(1, src.count + 1):
                nombre = (src.descriptions[b - 1] or "P_banda%d" % b)
                if nombre.endswith("_db") or "incidence" in nombre or "cociente" in nombre:
                    continue                      # se evaluan solo las bandas lineales de retrodispersion
                v = muestras[:, b - 1].copy()
                if src.nodata is not None:
                    v[v == src.nodata] = np.nan
                y = lin_a_db(np.where(v > 0, v, np.nan)) if not a.p_en_db else v
                ok = np.isfinite(y) & np.isfinite(hp.rh98.values) & cerca
                if ok.sum() < 20:
                    log("  %-20s solo %d huellas con dato y cerca en fecha: no se evalua" % (nombre, ok.sum()))
                    continue
                rho, _ = spearmanr(y[ok], hp.rh98.values[ok])
                gr = pd.Series(y[ok]).groupby(pd.cut(hp.rh98.values[ok], CLASES_H), observed=False)
                curva, nn = gr.median(), gr.count()
                curvas["P_BIOMASS_" + nombre], conteos["P_BIOMASS_" + nombre] = curva, nn
                rango = rango_valido(curva, nn)
                celdas = (np.floor(hp.geometry.x.values[ok] / 200).astype(int) * 100000
                          + np.floor(hp.geometry.y.values[ok] / 200).astype(int))
                lo, hi = rho_ic(y[ok], hp.rh98.values[ok], celdas)
                filas.append({"capa": "P_BIOMASS_" + nombre, "huellas": int(ok.sum()),
                              "celdas_200m": int(np.unique(celdas).size), "spearman_rho": round(float(rho), 3),
                              "rho_IC95_inf": round(lo, 3), "rho_IC95_sup": round(hi, 3),
                              "rango_de_la_curva": round(rango, 2), "unidad": "dB",
                              "huellas_por_clase": " ".join("%s:%d" % (str(k), v) for k, v in nn.items())})
                log("  %-20s n=%5d  rho=%+.2f [%+.2f, %+.2f]  rango de la curva %.2f dB"
                    % (nombre, ok.sum(), rho, lo, hi, rango))
            if vista is not src:
                vista.close()
        pd.DataFrame(filas).sort_values("spearman_rho", ascending=False).to_csv(out, index=False, encoding="utf-8-sig")
        if a.p_sitio == SITIO:
            log("La banda P (69 cm) se compara con C y L sobre las MISMAS huellas de Federal: si su curva sigue")
            log("subiendo donde la C ya se aplano, ve un estrato mas profundo (troncos y suelo).")
        else:
            log("La banda P se evalua en %s y C y L en Federal: se compara la FORMA de las curvas, no el valor." % a.p_sitio)
    elif not a.sin_p:
        log("No esta %s: la parte B (banda P) no se hace. Correr armar_subsets.py Tp9 o pasar --p_tif." % a.p_tif)

    # ------------------------------------------------ figura (despues de la parte B, para incluir la banda P)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    radar = {k: v for k, v in curvas.items() if not k.startswith("O_") and not k.startswith("P_")}
    banda_p = {k: v for k, v in curvas.items() if k.startswith("P_") and not k.endswith("_HV")}
    # color fijo por banda y trazo por polarizacion (lleno = cruzada, punteado = copolarizada)
    COLOR = {"C": "#1f5fbf", "S": "#d4a017", "L": "#2a8c3a", "P": "#c0392b"}

    def estilo(k):
        banda = "P" if k.startswith("P_") else k[0]
        pol = k[-2:]
        cruzada = pol in ("HV", "VH")
        anio = re.search(r"_(\d{4})", k)
        lw = 2.2 if (anio and anio.group(1) == "2021") or banda in ("P", "S") else 1.3
        return COLOR.get(banda, "k"), ("-" if cruzada else ":"), lw

    def etiqueta(k):
        if k.startswith("P_"):
            return "P BIOMASS 2026 " + k[-2:]
        partes = k.split("_")
        nombres = {"ALOS2": "ALOS-2", "NISAR": "NISAR", "S1": "Sentinel-1", "NovaSAR": "NovaSAR"}
        return "%s %s %s %s" % (partes[0], nombres.get(partes[1], partes[1]), partes[2], partes[-1].replace("sigma0", ""))

    def coma(x, _pos=None):
        return ("%.0f" % x).replace("-", "\u2212")
    from matplotlib.ticker import FuncFormatter
    if radar:
        if banda_p:
            fig, (ax, axp) = plt.subplots(1, 2, figsize=(12, 5.2), gridspec_kw={"width_ratios": [1.4, 1]})
        else:
            fig, ax = plt.subplots(figsize=(8, 5.2))
            axp = None
        clases = list(list(radar.values())[0].index)
        etiquetas = ["%s\u2013%s" % (int(c.left), int(c.right)) if c.right < 60 else "> %d" % int(c.left) for c in clases]
        for k, v in radar.items():
            c, ls, lw = estilo(k)
            nn = conteos[k].values
            vv = np.where(nn >= a.min_huellas_clase, v.values, np.nan)
            ax.plot(range(len(v)), vv, ls, color=c, lw=lw, marker="o", ms=4, label=etiqueta(k))
            ax.plot(range(len(v)), np.where(nn < a.min_huellas_clase, v.values, np.nan), "o", color=c, mfc="white", ms=4)
        for a_, tit, dic in ((ax, "(a) C, L y S en Federal", radar), (axp, "(b) P (BIOMASS 12/08/2026), mismas huellas", banda_p)):
            if a_ is None:
                continue
            n0 = conteos[list(dic)[0]].values
            a_.set_xticks(range(len(etiquetas)))
            a_.set_xticklabels(["%s m\nn = %s" % (e, ("{:,}".format(int(n))).replace(",", ".")) for e, n in zip(etiquetas, n0)],
                               fontsize=8)
            a_.set_xlabel("altura del dosel GEDI rh98 (clase)")
            a_.set_ylabel("mediana de la retrodispersi\u00f3n (dB)")
            a_.yaxis.set_major_formatter(FuncFormatter(coma))
            a_.grid(alpha=0.3)
            a_.set_title(tit, fontsize=10)
        if axp is not None:
            for k, v in banda_p.items():
                c, ls, lw = estilo(k)
                nn = conteos[k].values
                axp.plot(range(len(v)), np.where(nn >= a.min_huellas_clase, v.values, np.nan), ls, color=c, lw=lw,
                         marker="s", ms=4, label=etiqueta(k))
                axp.plot(range(len(v)), np.where(nn < a.min_huellas_clase, v.values, np.nan), "s", color=c, mfc="white", ms=4)
            axp.legend(fontsize=8, loc="lower right")
        ax.legend(fontsize=7.5, ncol=2, loc="lower right")
        fig.tight_layout()
        png = ruta_tp("Tp9", "05_Resultados", "05_Graficos", "C_curvas_de_respuesta.png")
        os.makedirs(os.path.dirname(png), exist_ok=True)
        fig.savefig(png, dpi=140)
        plt.close(fig)
        log("Marcadores huecos: clases con menos de %d huellas (no entran al rango de la curva)." % a.min_huellas_clase)
        log("Figura:", png)

    # ------------------------------------------ parte C: degradacion con GEDI
    log.titulo("Degradacion: caida de altura GEDI sin cambio de cobertura optica (guia, 12.4)")
    h["periodo"] = np.where(h.fecha <= a.p1_hasta, "p1", np.where(h.fecha >= a.p2_desde, "p2", "medio"))
    log("Huellas por periodo: p1 (<= %s) %d, p2 (>= %s) %d"
        % (a.p1_hasta, (h.periodo == "p1").sum(), a.p2_desde, (h.periodo == "p2").sum()))
    hh = h[h.periodo != "medio"].copy()
    hh["cx"] = np.floor((hh.geometry.x - T.c) / a.celda).astype(int)
    hh["cy"] = np.floor((T.f - hh.geometry.y) / a.celda).astype(int)
    agg = hh.groupby(["cx", "cy", "periodo"]).rh98.agg(["median", "count"]).unstack("periodo")
    agg.columns = ["%s_%s" % c for c in agg.columns]
    if not {"median_p1", "median_p2"} <= set(agg.columns):
        log("No hay celdas con huellas en los dos periodos: ampliar --celda y declararlo.")
        log.cerrar("python Tp9_03_fusion_perdida_degradacion.py --pixel %d" % a.pixel)
        return
    agg = agg.dropna(subset=["median_p1", "median_p2"])
    agg = agg[(agg.count_p1 >= 2) & (agg.count_p2 >= 2)].reset_index()
    agg["delta_rh98_m"] = agg.median_p2 - agg.median_p1
    nd = sorted([k for k in capas if k.startswith("O_NDVI_")])
    paso = int(round(a.celda / T.a))

    def ndvi(cual, defecto):
        """NDVI de la parte C: capa de la pila, GeoTIFF externo llevado a la grilla, o la capa por defecto."""
        if not cual:
            return capas.get(defecto), defecto
        if cual in capas:
            return capas[cual], cual
        from funciones_comunes import leer_en_grilla, grilla_de_tif
        return leer_en_grilla(cual, grilla_de_tif(pila_r), "average"), os.path.basename(cual)
    if len(nd) >= 2 or (a.ndvi_p1 and a.ndvi_p2):
        n1, e1 = ndvi(a.ndvi_p1, nd[0] if nd else "")
        n2, e2 = ndvi(a.ndvi_p2, nd[-1] if nd else "")
        nd = [e1, e2]
        log("dNDVI de la parte C: %s menos %s. Las huellas del periodo 2 terminan el %s: si el NDVI es de otra"
            % (e2, e1, str(h.fecha.max())[:10]))
        log("fecha, la condicion |dNDVI| < %.2f se evalua en otra ventana temporal (se declara)." % a.u_dndvi)
        # dNDVI de la CELDA: mediana de todos sus pixeles con dato (no el pixel del centro, que puede
        # caer en un camino, un claro o una nube y no representar a las huellas de la celda)
        dnd = n2 - n1
        med = []
        for cy, cx in zip(agg.cy.values, agg.cx.values):
            v = dnd[max(cy * paso, 0):min((cy + 1) * paso, perfil["height"]),
                    max(cx * paso, 0):min((cx + 1) * paso, perfil["width"])]
            ok = np.isfinite(v)
            # se exige dato en al menos la mitad de la celda; si no, la celda queda sin dNDVI
            med.append(float(np.median(v[ok])) if ok.sum() and ok.sum() >= 0.5 * v.size else np.nan)
        agg["dNDVI"] = med
        log("dNDVI por celda: mediana de los pixeles de %d m con dato de cada celda (%s menos %s)."
            % (int(T.a), nd[1], nd[0]))
    else:
        agg["dNDVI"] = np.nan
    agg["candidato_degradacion"] = ((agg.median_p1 >= a.monte_min) & (agg.delta_rh98_m <= a.u_rh98)
                                    & (agg.dNDVI.abs() < a.u_dndvi)).astype(int)
    log("Celdas de %.0f m con >= 2 huellas en cada periodo: %d" % (a.celda, len(agg)))
    log("Candidatas a degradacion (rh98 previo >= %.0f m, caida <= %.1f m, |dNDVI| < %.2f): %d"
        % (a.monte_min, a.u_rh98, a.u_dndvi, agg.candidato_degradacion.sum()))
    log("rh98 menor de 3 m esta cerca del ruido del instrumento; GEDI no adquirio entre 17/03/2023 y 26/04/2024.")
    agg.to_csv(ruta_tp("Tp9", "05_Resultados", "04_Tablas", "C_delta_rh98_por_celda.csv"), index=False, encoding="utf-8-sig")
    # raster en la grilla de la pila: cada pixel recibe el valor de su celda
    filas_c = np.arange(perfil["height"]) // paso
    cols_c = np.arange(perfil["width"]) // paso
    ny, nx = filas_c.max() + 1, cols_c.max() + 1
    dr = np.full((ny, nx), np.nan, "float32")
    cd = np.full((ny, nx), np.nan, "float32")
    ok = (agg.cy < ny) & (agg.cx < nx) & (agg.cy >= 0) & (agg.cx >= 0)
    dr[agg.cy[ok], agg.cx[ok]] = agg.delta_rh98_m[ok]
    cd[agg.cy[ok], agg.cx[ok]] = agg.candidato_degradacion[ok]
    from funciones_comunes import guardar_tif, grilla_de_tif
    guardar_tif(ruta_tp("Tp9", "02_Subsets_SNAP_QGIS", "C_delta_rh98_%dm.tif" % a.pixel),
                {"delta_rh98_m": dr[np.ix_(filas_c, cols_c)], "candidato_degradacion": cd[np.ix_(filas_c, cols_c)]},
                grilla_de_tif(pila_r), "NASA - GEDI L2A V003 (LP DAAC, Earthdata), huellas validas del sitio",
                "Cambio de rh98 por celda de %.0f m (p2 - p1)" % a.celda)
    log.cerrar("python Tp9_03_fusion_perdida_degradacion.py --pixel %d" % a.pixel)


if __name__ == "__main__":
    main()
