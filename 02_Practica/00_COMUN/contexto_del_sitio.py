# -*- coding: utf-8 -*-
"""
contexto_del_sitio.py   [lo llaman los TpN_..._contexto_del_sitio.py]   (agregado el 21/10/2026)

El contexto de biomasa y de uso del suelo de un sitio, con los productos que el curso trae en
02_Subsets_SNAP_QGIS\\QGIS_GeoTIFF de cada practico:

  - MapBiomas Argentina, Coleccion 3: cobertura anual 1985-2025, perdida y vegetacion secundaria
    1987-2025; MapBiomas Fuego, Coleccion 1: area quemada anual 1999-2025 y frecuencia.
  - ESA CCI Biomass v7: biomasa aerea (AGB, Mg/ha) y su desvio, 2010, 2015, 2020, 2021 y 2024.
  - BIOMASS (ESA), banda P: L1B DGM (gamma0 HH y VH; la HV trae interferencia de radiofrecuencia sin
    corregir en el producto de origen y no se usa) y L2A FH (altura del bosque, con su calidad).

Todo se lleva a la grilla de MapBiomas (EPSG:4326, unos 30 m): las clases no se remuestrean. El area de
cada pixel se calcula con la latitud. Las areas se dan sobre la parte del sitio que MapBiomas cubre
(Entre Rios); el resto queda fuera de las cuentas y se informa.

Salidas (05_Resultados/04_Tablas y 05_Graficos):
  <SITIO>_mapbiomas_area_por_clase_y_anio.csv      anio, clase, nombre, ha, % del area con dato
  <SITIO>_mapbiomas_perdida_por_anio.csv           anio, ha de perdida de vegetacion primaria y secundaria,
                                                   ha de recuperacion de vegetacion secundaria
  <SITIO>_mapbiomas_fuego_por_anio.csv             anio, ha quemadas, clase de cobertura mas quemada
  <SITIO>_contexto_por_clase.csv                   por clase de MapBiomas del ultimo anio: ha, CCI (mediana,
                                                   p25, p75, % > 0), FH y su calidad (medianas), P HH y P VH
                                                   (mediana en dB), veces quemado
  <SITIO>_contexto_pixeles_muestra.csv             hasta 2000 pixeles por clase, para Orange
  <SITIO>_mapbiomas_area_por_clase.png, _perdida_y_fuego_por_anio.png
"""
import glob
import os
import re

import numpy as np
import pandas as pd

from funciones_comunes import leer_en_grilla, grilla_de_tif, lin_a_db, Bitacora, mascara_agua

FUENTE_MB = ("Proyecto MapBiomas Argentina, Coleccion 3 de los mapas anuales de cobertura y uso del suelo y "
             "productos derivados; MapBiomas Fuego, Coleccion 1. https://argentina.mapbiomas.org (CC BY 4.0)")
FUENTE_CCI = ("Santoro, M. y Cartus, O. (2026). ESA Biomass Climate Change Initiative (Biomass_cci), v7.0, NERC EDS "
              "CEDA, https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903")
FUENTE_BIO = "ESA, BIOMASS banda P (435 MHz), L1B DGM y L2A FH, ESA MAAP, https://catalog.maap.eo.esa.int"


def _leyenda(qml):
    ley = {}
    if os.path.exists(qml):
        for v, l in re.findall(r'value="(\d+)"[^/]*?label="([^"]*)"', open(qml, encoding="utf-8").read()):
            ley[int(v)] = re.sub(r"^\d+\s+", "", l)
    return ley


def _uno(carpeta, patron):
    f = sorted(glob.glob(os.path.join(carpeta, patron)))
    return f[0] if f else None


def _area_pixel_ha(grilla):
    """Area (ha) de cada fila de una grilla en grados: depende de la latitud."""
    t = grilla["transform"]
    lat = t.f + (np.arange(grilla["height"]) + 0.5) * t.e
    r = 6371008.8
    dx = np.radians(abs(t.a)) * r * np.cos(np.radians(lat))
    dy = np.radians(abs(t.e)) * r
    return (dx * dy / 1e4)[:, None]


# Nombres de las clases de MapBiomas con sus tildes, para los graficos (el .qml del curso los trae sin tildes).
TILDES_MB = {"Herbaceas": "Herbáceas", "Rios": "Ríos", "areas": "áreas", "Areas": "Áreas", "Vegetacion": "Vegetación",
             "herbacea": "herbácea", "Coleccion": "Colección", "Area": "Área", "perenne": "perenne",
             "Turberas": "Turberas", "oceano": "océano", "Oceano": "Océano", "Agricultura": "Agricultura"}


def con_tildes(texto):
    """Pone las tildes a los nombres de clase de MapBiomas (solo para mostrar)."""
    out = []
    for p in str(texto).split(" "):
        base = p.rstrip(",;.")
        out.append(TILDES_MB.get(base, base) + p[len(base):])
    return " ".join(out)


def formato_es(ax, decimales=0):
    """Ejes con coma decimal y punto de miles (regla del curso)."""
    from matplotlib.ticker import FuncFormatter

    def f(v, _pos):
        d = decimales if abs(v - round(v)) < 1e-9 else max(decimales, 1)
        s = ("{:,.%df}" % d).format(v)
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: "%d" % v if abs(v - round(v)) < 1e-9 else f(v, p)))
    ax.yaxis.set_major_formatter(FuncFormatter(f))


def correr(sitio, carpeta_qg, tablas, graficos, control, nombre_log, siguiente=None, por_clase=2000,
           graficos_es=False):
    """graficos_es=True: graficos con tildes, coma decimal y punto de miles, y la leyenda debajo del grafico
    (opcional; por defecto se conservan los graficos de siempre)."""
    import rasterio

    log = Bitacora(control, nombre_log)
    f_cob = _uno(carpeta_qg, "%s_MapBiomas_cobertura_*.tif" % sitio)
    if not f_cob:
        log("No encuentro %s_MapBiomas_cobertura_*.tif en %s" % (sitio, carpeta_qg))
        log.cerrar()
        return
    ley = _leyenda(f_cob.replace(".tif", ".qml"))
    g = grilla_de_tif(f_cob)
    area = _area_pixel_ha(g) * np.ones((1, g["width"]))
    with rasterio.open(f_cob) as s:
        anios = [int(d.split("_")[-1]) for d in s.descriptions]
        cob = s.read()
    con_dato = cob[-1] > 0
    ha_sitio, ha_dato = area.sum(), area[con_dato].sum()
    log("Sitio %s: grilla de MapBiomas %d x %d pixeles (EPSG:4326, %.1f m)" % (
        sitio, g["width"], g["height"], abs(g["transform"].e) * 111320))
    log("MapBiomas cubre %.0f ha de %.0f (%.1f %%); el resto queda fuera de las cuentas." % (
        ha_dato, ha_sitio, 100 * ha_dato / ha_sitio))

    # ---------------------------------------------------------------- cobertura por anio
    filas = []
    for k, a in enumerate(anios):
        c = cob[k]
        for cl in np.unique(c[c > 0]):
            ha = area[c == cl].sum()
            filas.append((a, int(cl), ley.get(int(cl), str(cl)), round(ha, 1), round(100 * ha / ha_dato, 2)))
    t_cob = pd.DataFrame(filas, columns=["anio", "clase", "nombre", "ha", "pct_area_con_dato"])
    t_cob.to_csv(os.path.join(tablas, "%s_mapbiomas_area_por_clase_y_anio.csv" % sitio), index=False, encoding="utf-8-sig")
    a0, a1 = anios[0], anios[-1]
    piv = t_cob.pivot_table(index=["clase", "nombre"], columns="anio", values="pct_area_con_dato", fill_value=0)
    log.titulo("Cobertura de MapBiomas: %% del area con dato, %d y %d" % (a0, a1))
    for (cl, nom), r in piv.sort_values(a1, ascending=False).iterrows():
        if max(r[a0], r[a1]) >= 0.5:
            log("  %2d %-42s %6.1f %%  %6.1f %%   (%+.1f puntos)" % (cl, nom, r[a0], r[a1], r[a1] - r[a0]))

    # ---------------------------------------------------------------- perdida y vegetacion secundaria
    t_per = None
    f_per = _uno(carpeta_qg, "%s_MapBiomas_perdida_veg_*.tif" % sitio)
    if f_per:
        with rasterio.open(f_per) as s:
            ap = [int(d.split("_")[-1]) for d in s.descriptions]
            per = s.read()
        t_per = pd.DataFrame({"anio": ap,
                              "ha_perdida_primaria": [round(area[per[k] == 4].sum(), 1) for k in range(len(ap))],
                              "ha_perdida_secundaria": [round(area[per[k] == 6].sum(), 1) for k in range(len(ap))],
                              "ha_recuperacion_secundaria": [round(area[per[k] == 5].sum(), 1) for k in range(len(ap))]})
        t_per.to_csv(os.path.join(tablas, "%s_mapbiomas_perdida_por_anio.csv" % sitio), index=False, encoding="utf-8-sig")
        tot = t_per.ha_perdida_primaria.sum() + t_per.ha_perdida_secundaria.sum()
        top = t_per.assign(t=t_per.ha_perdida_primaria + t_per.ha_perdida_secundaria).nlargest(3, "t")
        log.titulo("Perdida de vegetacion (MapBiomas), %d-%d" % (ap[0], ap[-1]))
        log("  Total: %.0f ha de vegetacion primaria y %.0f ha de secundaria; %.0f ha de recuperacion." % (
            t_per.ha_perdida_primaria.sum(), t_per.ha_perdida_secundaria.sum(), t_per.ha_recuperacion_secundaria.sum()))
        log("  Anios con mas perdida: " + ", ".join("%d (%.0f ha)" % (r.anio, r.t) for r in top.itertuples()))

    # ---------------------------------------------------------------- fuego
    t_fue, veces = None, None
    f_fue = _uno(carpeta_qg, "%s_MapBiomas_fuego_anual_*.tif" % sitio)
    if f_fue:
        with rasterio.open(f_fue) as s:
            af = [int(d.split("_")[-1]) for d in s.descriptions]
            fue = s.read()
        veces = fue.sum(axis=0)
        filas = []
        for k, a in enumerate(af):
            q = fue[k] == 1
            ha = area[q].sum()
            cl_mas = ""
            if q.any() and a in anios:
                c = cob[anios.index(a)][q]
                u, n = np.unique(c[c > 0], return_counts=True)
                if u.size:
                    cl_mas = ley.get(int(u[np.argmax(n)]), str(u[np.argmax(n)]))
            filas.append((a, round(ha, 1), cl_mas))
        t_fue = pd.DataFrame(filas, columns=["anio", "ha_quemadas", "clase_mas_quemada"])
        t_fue.to_csv(os.path.join(tablas, "%s_mapbiomas_fuego_por_anio.csv" % sitio), index=False, encoding="utf-8-sig")
        log.titulo("Area quemada (MapBiomas Fuego), %d-%d" % (af[0], af[-1]))
        log("  Total acumulado: %.0f ha; quemado al menos una vez: %.0f ha (%.1f %% del area con dato)." % (
            t_fue.ha_quemadas.sum(), area[veces > 0].sum(), 100 * area[veces > 0].sum() / ha_dato))
        for r in t_fue.nlargest(3, "ha_quemadas").itertuples():
            log("  %d: %.0f ha (sobre todo %s)" % (r.anio, r.ha_quemadas, r.clase_mas_quemada))

    # ---------------------------------------------------------------- biomasa: CCI, FH y banda P en la grilla de MapBiomas
    capas = {}
    f_cci = _uno(carpeta_qg, "%s_CCI_Biomass_*AGB.tif" % sitio)
    if f_cci:
        with rasterio.open(f_cci) as s:
            dcci = list(s.descriptions)
        for y in (2020, 2024):
            if "AGB_%d" % y in dcci:
                capas["CCI_AGB_%d" % y] = leer_en_grilla(f_cci, g, "nearest", banda=dcci.index("AGB_%d" % y) + 1)
    f_fh = _uno(carpeta_qg, "%s_BIOMASS_P_FH_*[0-9].tif" % sitio)
    if f_fh:
        capas["FH_m"] = leer_en_grilla(f_fh, g, "nearest", banda=1)
        capas["FH_calidad"] = leer_en_grilla(f_fh, g, "nearest", banda=2)
        # 22/10/2026: la FH sobre el agua no es altura de bosque; se enmascara antes de medir
        agua, txt_agua = mascara_agua(carpeta_qg, sitio, g)
        con_fh = np.isfinite(capas["FH_m"])
        log("Altura FH: se enmascara el %s (%.1f %% de los pixeles con FH)." % (
            txt_agua, 100 * (agua & con_fh).sum() / max(con_fh.sum(), 1)))
        capas["FH_m"][agua] = np.nan
        capas["FH_calidad"][agua] = np.nan
    f_p = [f for f in sorted(glob.glob(os.path.join(carpeta_qg, "%s_BIOMASS_P_2*.tif" % sitio)))
           if re.search(r"_BIOMASS_P_\d{8}(_S\d)?\.tif$", f)]
    if f_p:
        with rasterio.open(f_p[0]) as s:
            dp = list(s.descriptions)
        for pol in ("HH", "VH"):
            capas["P_%s_dB" % pol] = lin_a_db(leer_en_grilla(f_p[0], g, "average", banda=dp.index("Gamma0_" + pol) + 1))
        log("")
        log("Banda P: %s (HH y VH; la HV trae interferencia de radiofrecuencia sin corregir y no se usa)." %
            os.path.basename(f_p[0]))
    if veces is not None:
        capas["veces_quemado"] = veces.astype("float32")
    if f_per:
        capas["perdida_alguna_vez"] = (np.isin(per, (4, 6)).any(axis=0)).astype("float32")

    c1 = cob[-1]
    filas = []
    for cl in np.unique(c1[c1 > 0]):
        m = c1 == cl
        ha = area[m].sum()
        if 100 * ha / ha_dato < 0.2:
            continue
        r = {"clase": int(cl), "nombre": ley.get(int(cl), str(cl)), "ha_%d" % a1: round(ha, 1),
             "pct_area_con_dato": round(100 * ha / ha_dato, 2)}
        for n, a in capas.items():
            v = a[m]
            v = v[np.isfinite(v)]
            if n.startswith("CCI"):
                r[n + "_mediana"] = round(float(np.median(v)), 1) if v.size else np.nan
                r[n + "_p25"] = round(float(np.percentile(v, 25)), 1) if v.size else np.nan
                r[n + "_p75"] = round(float(np.percentile(v, 75)), 1) if v.size else np.nan
                r[n + "_pct_mayor_0"] = round(100 * float((v > 0.5).mean()), 1) if v.size else np.nan
            elif n == "veces_quemado":
                r["pct_quemado_alguna_vez"] = round(100 * float((v > 0).mean()), 1) if v.size else np.nan
            elif n == "perdida_alguna_vez":
                r["pct_perdida_alguna_vez"] = round(100 * float(v.mean()), 1) if v.size else np.nan
            else:
                r[n + "_mediana"] = round(float(np.median(v)), 1) if v.size else np.nan
                if n == "FH_m":
                    r["FH_pct_con_dato"] = round(100 * v.size / m.sum(), 1)
        filas.append(r)
    t_cl = pd.DataFrame(filas).sort_values("pct_area_con_dato", ascending=False)
    t_cl.to_csv(os.path.join(tablas, "%s_contexto_por_clase.csv" % sitio), index=False, encoding="utf-8-sig")
    log.titulo("Por clase de MapBiomas %d (medianas)" % a1)
    cols = [c for c in t_cl.columns if c.endswith("_mediana")]
    log("  %-38s %7s " % ("clase", "% area") + " ".join("%14s" % c.replace("_mediana", "") for c in cols))
    for r in t_cl.itertuples(index=False):
        d = r._asdict()
        log("  %-38s %7.1f " % (d["nombre"][:38], d["pct_area_con_dato"]) +
            " ".join("%14s" % ("%.1f" % d[c] if np.isfinite(d[c]) else "-") for c in cols))

    # ---------------------------------------------------------------- muestra para Orange
    rng = np.random.default_rng(20261021)
    partes = []
    for r in t_cl.itertuples(index=False):
        idx = np.flatnonzero(c1.ravel() == r.clase)
        idx = rng.choice(idx, min(por_clase, idx.size), replace=False)
        d = {"clase_MapBiomas_%d" % a1: "%d %s" % (r.clase, r.nombre)}
        for n, a in capas.items():
            d[n] = np.round(a.ravel()[idx], 2)
        partes.append(pd.DataFrame(d))
    mu = pd.concat(partes, ignore_index=True)
    mu.to_csv(os.path.join(tablas, "%s_contexto_pixeles_muestra.csv" % sitio), index=False, encoding="utf-8-sig")
    log("")
    log("Muestra para Orange: %d pixeles (hasta %d por clase)." % (len(mu), por_clase))

    # ---------------------------------------------------------------- graficos
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colores = {}
    with open(f_cob.replace(".tif", ".qml"), encoding="utf-8") as fq:
        for v, col in re.findall(r'value="(\d+)"[^/]*?color="(#[0-9a-fA-F]{6})"', fq.read()):
            colores[int(v)] = col
    principales = [cl for (cl, nom), r in piv.iterrows() if r.max() >= 1.0]
    if graficos_es:
        _graficos_es(sitio, t_cob, anios, principales, colores, ley, a0, a1, t_per, t_fue, graficos, plt)
    else:
        fig, ax = plt.subplots(figsize=(10, 5.6))
        for cl in principales:
            s = t_cob[t_cob.clase == cl].set_index("anio").ha.reindex(anios, fill_value=0) / 1000
            ax.plot(anios, s, lw=2, color=colores.get(cl, None), label="%d %s" % (cl, ley.get(cl, cl)))
        ax.set_xlabel("Año")
        ax.set_ylabel("Área (miles de ha)")
        ax.set_title("%s: área por clase de MapBiomas, %d-%d" % (sitio, a0, a1))
        ax.grid(alpha=.3)
        ax.legend(fontsize=8, ncol=2, loc="upper left", bbox_to_anchor=(1.01, 1))
        fig.text(0.01, 0.01, "Fuente: " + FUENTE_MB + ". Elaboración propia.", fontsize=7, wrap=True)
        fig.tight_layout(rect=(0, 0.05, 1, 1))
        fig.savefig(os.path.join(graficos, "%s_mapbiomas_area_por_clase.png" % sitio), dpi=150)
        plt.close(fig)
    if (t_per is not None or t_fue is not None) and not graficos_es:
        fig, axs = plt.subplots(2, 1, figsize=(10, 6.4), sharex=True)
        if t_per is not None:
            axs[0].bar(t_per.anio, t_per.ha_perdida_primaria, color="#d4271e", label="Pérdida de vegetación primaria")
            axs[0].bar(t_per.anio, t_per.ha_perdida_secundaria, bottom=t_per.ha_perdida_primaria, color="#f5a623",
                       label="Pérdida de vegetación secundaria")
            axs[0].set_ylabel("ha por año")
            axs[0].legend(fontsize=8)
            axs[0].set_title("%s: pérdida de vegetación y área quemada por año (MapBiomas)" % sitio)
        if t_fue is not None:
            axs[1].bar(t_fue.anio, t_fue.ha_quemadas, color="#8b1a1a", label="Área quemada")
            axs[1].set_ylabel("ha por año")
            axs[1].legend(fontsize=8)
        axs[1].set_xlabel("Año")
        for a in axs:
            a.grid(alpha=.3)
        fig.text(0.01, 0.01, "Fuente: " + FUENTE_MB + ". Elaboración propia.", fontsize=7, wrap=True)
        fig.tight_layout(rect=(0, 0.04, 1, 1))
        fig.savefig(os.path.join(graficos, "%s_mapbiomas_perdida_y_fuego_por_anio.png" % sitio), dpi=150)
        plt.close(fig)
    log("")
    log("Tablas en  : " + tablas)
    log("Graficos en: " + graficos)
    log.cerrar(siguiente)


def _graficos_es(sitio, t_cob, anios, principales, colores, ley, a0, a1, t_per, t_fue, graficos, plt):
    """Los dos graficos de contexto con tildes, coma decimal, punto de miles, colores oficiales de la
    leyenda de MapBiomas (los del .qml) y la leyenda debajo del grafico, sin superponerse a las lineas."""
    plt.rcParams["font.family"] = ["Times New Roman", "Liberation Serif", "DejaVu Serif"]
    fig, ax = plt.subplots(figsize=(8.5, 5.4))
    for cl in principales:
        s = t_cob[t_cob.clase == cl].set_index("anio").ha.reindex(anios, fill_value=0) / 1000
        ax.plot(anios, s, lw=2, color=colores.get(cl, None),
                label="%d %s" % (cl, con_tildes(ley.get(cl, cl))))
    ax.set_xlabel("Año")
    ax.set_ylabel("Área (miles de ha)")
    ax.set_title("%s: área por clase de MapBiomas, %d–%d" % (sitio, a0, a1))
    ax.grid(alpha=.3)
    formato_es(ax, decimales=0)
    ax.legend(fontsize=9, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.13), frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(graficos, "%s_mapbiomas_area_por_clase.png" % sitio), dpi=170, bbox_inches="tight")
    plt.close(fig)
    if t_per is None and t_fue is None:
        return
    fig, axs = plt.subplots(2, 1, figsize=(8.5, 6.2), sharex=True)
    if t_per is not None:
        axs[0].bar(t_per.anio, t_per.ha_perdida_primaria, color="#d4271e", label="Pérdida de vegetación primaria")
        axs[0].bar(t_per.anio, t_per.ha_perdida_secundaria, bottom=t_per.ha_perdida_primaria, color="#f5a623",
                   label="Pérdida de vegetación secundaria")
        axs[0].set_ylabel("ha por año")
        axs[0].set_title("%s: pérdida de vegetación (arriba) y área quemada (abajo) por año" % sitio)
        tope = float((t_per.ha_perdida_primaria + t_per.ha_perdida_secundaria).max())
        axs[0].set_ylim(0, tope * 1.45 if tope > 0 else 1)      # lugar para la leyenda sin tapar barras
        axs[0].legend(fontsize=9, loc="upper right", frameon=False, ncol=2)
    if t_fue is not None:
        axs[1].bar(t_fue.anio, t_fue.ha_quemadas, color="#8b1a1a", label="Área quemada (MapBiomas Fuego)")
        axs[1].set_ylabel("ha por año")
        axs[1].set_ylim(0, float(t_fue.ha_quemadas.max()) * 1.2 if t_fue.ha_quemadas.max() > 0 else 1)
        axs[1].legend(fontsize=9, loc="upper left", frameon=False)
    axs[1].set_xlabel("Año")
    for a in axs:
        a.grid(alpha=.3)
        formato_es(a, decimales=0)
    fig.tight_layout()
    fig.savefig(os.path.join(graficos, "%s_mapbiomas_perdida_y_fuego_por_anio.png" % sitio), dpi=170, bbox_inches="tight")
    plt.close(fig)
