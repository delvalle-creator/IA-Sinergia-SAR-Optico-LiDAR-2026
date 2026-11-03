# -*- coding: utf-8 -*-
"""
Tp2_03_respuesta_por_cubierta.py   [SE CORRE]   Tp2, paso 7 de la guia
==============================================================
"Comparar la misma cubierta en todas las bandas y explicar las diferencias"
(presentacion 01, diapositiva 25, paso 5).

ENTRADA QUE PREPARA EL GRUPO EN QGIS
  Tp2_SAR_multibanda/04_Tablas_de_trabajo/cubiertas_<SITIO>.gpkg
  capa "cubiertas", poligonos con el campo de texto "clase". Clases sugeridas:
      agua_calma, agua_rizada, pajonal, monte_o_bosque, cultivo, suelo_desnudo,
      urbano, estable
  Se digitalizan sobre el RGB de Tp2_02 y sobre Sentinel-2 o la imagen de
  muy alta resolucion de QGIS (complemento QuickMapServices o XYZ de ESRI).
  Al menos 3 poligonos por clase y 200 pixeles de 10 m por clase.
  Si el archivo no existe, el programa lo crea vacio con su campo y se
  detiene: la digitalizacion es del grupo, no del programa.

QUE CALCULA (por clase y por banda)
  - media en dB calculada promediando en LINEAL; p10 y p90 en dB; n pixeles.
  - la media de CADA POLIGONO (tambien en lineal) y, por clase, la menor y la
    mayor de esas medias y su desvio. Los pixeles de un mismo poligono no son
    observaciones independientes: lo que dice cuanto varia una cubierta en el
    paisaje es la diferencia ENTRE poligonos, no el desvio de los pixeles.
  - contraste entre clases (diferencia de medias en dB): es lo que hace que una
    banda "vea" algo y otra no.
  - separabilidad M = |mu1 - mu2| / (sigma1 + sigma2), con mu y sigma de los
    pixeles en dB. Si M > 1, las dos clases se separan pixel a pixel (sus
    distribuciones casi no se tocan); si M < 1, se separan las medias pero no
    cada pixel. Es el indice de separabilidad de Kaufman y Remer (1994), muy
    usado en teledeteccion para elegir bandas.
  - una figura de cajas por banda, en dos filas, con las clases en orden fisico
    (del agua a lo construido) y un color fijo por clase (el mismo que usan la
    capa de QGIS y los workflows de Orange del Tp2).

SALIDA
  Tp2_SAR_multibanda/05_Resultados/04_Tablas/<SITIO>_respuesta_por_cubierta.csv
  Tp2_SAR_multibanda/05_Resultados/04_Tablas/<SITIO>_media_por_poligono.csv
  Tp2_SAR_multibanda/05_Resultados/04_Tablas/<SITIO>_contraste_entre_clases.csv
  Tp2_SAR_multibanda/05_Resultados/05_Graficos/<SITIO>_cajas_por_banda.png

USO
    python Tp2_03_respuesta_por_cubierta.py --sitio A2_IBICUY
"""
import argparse
import itertools
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import SITIOS, EPSG, ruta_tp                 # noqa: E402
from funciones_comunes import (leer_tif, grilla_de_tif, lin_a_db,      # noqa: E402
                               media_lineal_db, Bitacora)

# ------------------------------------------------------------------ parametros
# Clases sugeridas, en ORDEN FISICO (de lo que menos devuelve a lo que mas devuelve).
CLASES_SUGERIDAS = ["agua_calma", "agua_rizada", "pajonal", "suelo_desnudo", "cultivo",
                    "monte_o_bosque", "urbano", "estable"]
# Un color por clase, el mismo en QGIS (cubiertas_<SITIO>.qml) y en Orange (cabecera del .tab).
# Es la paleta de las figuras del Desarrollo (mapas de polígonos y capturas de Orange).
COLOR_CLASE = {"agua_calma": "#1f3a93", "agua_rizada": "#4fa3e0", "pajonal": "#e6c229",
               "suelo_desnudo": "#f4a6c6", "cultivo": "#ff7f0e", "monte_o_bosque": "#1b8a3a",
               "urbano": "#d62728", "estable": "#7f7f7f"}
MIN_PIXELES = 200          # menos pixeles por clase: la media es inestable (se avisa)


def nombre_legible(banda):
    """'L_NISAR_gamma0_HV_20260930' -> 'L HV 30/09/2026 (NISAR)'."""
    p = banda.split("_")
    sensor = {"S1": "Sentinel-1 RTC", "SNAP": "Sentinel-1 SNAP", "NISAR": "NISAR",
              "BIOMASS": "BIOMASS", "NovaSAR": "NovaSAR", "SAOCOM": "SAOCOM"}.get(p[1], p[1])
    pol = p[3] if len(p) > 3 else ""
    fecha = ""
    if len(p) > 4 and p[4].isdigit() and len(p[4]) == 8:
        fecha = " %s/%s" % (p[4][6:8], p[4][4:6])
    return "%s %s%s\n(%s)" % (p[0], pol, fecha, sensor)


def formato_coma(ax):
    """Ejes con coma decimal (convencion del curso)."""
    from matplotlib.ticker import FuncFormatter
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: ("%g" % v).replace(".", ",").replace("-", "−")))


def plantilla(ruta, log):
    import geopandas as gpd

    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    gpd.GeoDataFrame({"clase": pd.Series(dtype="str"), "observacion": pd.Series(dtype="str")},
                     geometry=gpd.GeoSeries([], crs=EPSG), crs=EPSG).to_file(
        ruta, layer="cubiertas", driver="GPKG", engine="pyogrio", geometry_type="Polygon")
    log("Se creo la capa vacia: %s (capa 'cubiertas', campo 'clase', EPSG:%d)." % (ruta, EPSG))
    log("Abrala en QGIS, active la edicion y digitalice poligonos de estas clases:")
    log("   " + ", ".join(CLASES_SUGERIDAS))
    log("Despues vuelva a correr este programa.")


def figura_cajas(ruta_png, datos_db, clases, bandas, fuente_txt):
    """Cajas por clase en cada banda, en dos filas, con eje y rotulado en cada fila."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ncol = int(np.ceil(len(bandas) / 2.0))
    fig, axs = plt.subplots(2, ncol, figsize=(2.6 * ncol, 9.0), sharey=True, squeeze=False)
    for k, b in enumerate(bandas):
        ax = axs[k // ncol][k % ncol]
        serie = [datos_db[b].get(c, np.array([])) for c in clases]
        hay = [i for i, s in enumerate(serie) if s.size]
        bp = ax.boxplot([serie[i] for i in hay], positions=[i + 1 for i in hay], showfliers=False,
                        widths=0.65, patch_artist=True, medianprops={"color": "black"})
        for caja, i in zip(bp["boxes"], hay):
            caja.set_facecolor(COLOR_CLASE.get(clases[i], "#cccccc"))
            caja.set_alpha(0.85)
        ax.set_xticks(range(1, len(clases) + 1))
        ax.set_xticklabels([c.replace("_", " ") for c in clases], rotation=60, ha="right", fontsize=9)
        ax.set_title(nombre_legible(b), fontsize=9)
        ax.grid(axis="y", alpha=0.3)
        formato_coma(ax)
        if k % ncol == 0:
            ax.set_ylabel("γ⁰ (dB)", fontsize=10)
    for k in range(len(bandas), 2 * ncol):
        axs[k // ncol][k % ncol].set_visible(False)
    fig.suptitle("Caja: p25\u2013p75; l\u00ednea: mediana; bigotes: 1,5 veces el rango intercuartil; sin extremos",
                 fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    os.makedirs(os.path.dirname(ruta_png), exist_ok=True)
    fig.savefig(ruta_png, dpi=200)
    plt.close(fig)
    # La cita de la fuente va en el texto del informe, no dentro de la figura.
    return fuente_txt


def main():
    import geopandas as gpd
    from rasterio import features

    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", required=True, choices=list(SITIOS.keys()))
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp2", "05_Resultados", "06_Control_calidad"), "Tp2_03_%s" % a.sitio)

    vec = ruta_tp("Tp2", "04_Tablas_de_trabajo", "cubiertas_%s.gpkg" % a.sitio)
    if not os.path.exists(vec):
        plantilla(vec, log)
        log.cerrar()
        return
    pila = ruta_tp("Tp2", "02_Subsets_SNAP_QGIS", "%s_pila_gamma0_lineal.tif" % a.sitio)
    if not os.path.exists(pila):
        log("Falta la pila %s: correr antes Tp2_01 (paso 4)." % pila)
        log.cerrar()
        return
    capas, _, _ = leer_tif(pila)
    g = grilla_de_tif(pila)
    pol = gpd.read_file(vec, layer="cubiertas").to_crs(g["crs"])
    pol = pol[pol["clase"].notna() & (pol["clase"].astype(str).str.strip() != "")].reset_index(drop=True)
    if pol.empty:
        log("La capa existe pero no tiene poligonos con 'clase'. Digitalice y vuelva a correr.")
        log.cerrar()
        return
    # orden fisico: primero las clases sugeridas en su orden, despues las que el grupo invento
    presentes = list(pol["clase"].unique())
    clases = [c for c in CLASES_SUGERIDAS if c in presentes] + sorted(c for c in presentes if c not in CLASES_SUGERIDAS)
    # cada poligono con un numero propio (1, 2, ...) dentro de su clase
    pol["n_pol"] = pol.groupby("clase").cumcount() + 1
    pol["id"] = np.arange(1, len(pol) + 1)
    ids = features.rasterize(((geom, int(i)) for geom, i in zip(pol.geometry, pol["id"])),
                             out_shape=(g["height"], g["width"]), transform=g["transform"],
                             fill=0, dtype="int32")
    clase_de_id = dict(zip(pol["id"], pol["clase"]))
    filas, filas_pol, datos_db = [], [], {}
    for banda, arr in capas.items():
        datos_db[banda] = {}
        for c in clases:
            mc = np.isin(ids, [i for i, cc in clase_de_id.items() if cc == c]) & np.isfinite(arr)
            v = arr[mc]
            if v.size == 0:
                continue
            db = lin_a_db(v)
            datos_db[banda][c] = db[np.isfinite(db)]
            # media de cada poligono, en lineal
            medias = []
            for _, p in pol[pol["clase"] == c].iterrows():
                vp = arr[(ids == p["id"]) & np.isfinite(arr)]
                if vp.size:
                    mp = media_lineal_db(vp)
                    medias.append(mp)
                    filas_pol.append({"banda": banda, "clase": c, "poligono": "%s %d" % (c, p["n_pol"]),
                                      "n_pixeles": int(vp.size), "media_dB": round(mp, 2)})
            filas.append({"banda": banda, "clase": c, "n_pixeles": int(v.size), "n_poligonos": len(medias),
                          "media_dB": round(media_lineal_db(v), 2),
                          "p10_dB": round(float(np.nanpercentile(db, 10)), 2),
                          "p90_dB": round(float(np.nanpercentile(db, 90)), 2),
                          "media_dB_de_los_pixeles": round(float(np.nanmean(db)), 2),
                          "desvio_dB_de_los_pixeles": round(float(np.nanstd(db)), 2),
                          "min_media_poligono_dB": round(min(medias), 2) if medias else np.nan,
                          "max_media_poligono_dB": round(max(medias), 2) if medias else np.nan,
                          "desvio_entre_poligonos_dB": round(float(np.std(medias, ddof=1)), 2) if len(medias) > 1 else np.nan})
    t = pd.DataFrame(filas)
    out = ruta_tp("Tp2", "05_Resultados", "04_Tablas", "%s_respuesta_por_cubierta.csv" % a.sitio)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    t.to_csv(out, index=False, encoding="utf-8-sig")
    out_pol = out.replace("respuesta_por_cubierta", "media_por_poligono")
    pd.DataFrame(filas_pol).to_csv(out_pol, index=False, encoding="utf-8-sig")
    for _, f in t[t.n_pixeles < MIN_PIXELES].iterrows():
        log("AVISO: %s en %s tiene solo %d pixeles: la media es inestable." % (f.clase, f.banda, f.n_pixeles))

    piv = t.pivot(index="clase", columns="banda", values="media_dB").reindex(index=clases, columns=list(capas))
    log.titulo("Media por clase (dB, promediada en lineal)")
    log(piv.round(1).to_string())
    log.titulo("Rango de las medias por poligono (dB): menor / mayor")
    rng = t.assign(rango=t.min_media_poligono_dB.round(1).astype(str) + " / " + t.max_media_poligono_dB.round(1).astype(str))
    log(rng.pivot(index="clase", columns="banda", values="rango").reindex(index=clases, columns=list(capas)).to_string())

    mu = t.pivot(index="clase", columns="banda", values="media_dB_de_los_pixeles")
    sd = t.pivot(index="clase", columns="banda", values="desvio_dB_de_los_pixeles")
    lo = t.pivot(index="clase", columns="banda", values="min_media_poligono_dB")
    hi = t.pivot(index="clase", columns="banda", values="max_media_poligono_dB")
    contr = []
    # Los pares van en orden alfabetico (clase_1 - clase_2), como en las versiones anteriores del
    # practico: asi el signo de cada contraste no cambia si el grupo agrega una clase.
    for c1, c2 in itertools.combinations(sorted(clases), 2):
        for b in capas:
            if pd.isna(piv.loc[c1, b]) or pd.isna(piv.loc[c2, b]):
                # una de las dos clases no tiene dato en esa banda (p. ej. la S no cubre el monte)
                contr.append({"clase_1": c1, "clase_2": c2, "banda": b, "contraste_dB": np.nan,
                              "separabilidad_M": np.nan, "separa_pixel_a_pixel": "sin dato",
                              "rangos_de_poligonos_se_tocan": "sin dato"})
                continue
            m = abs(mu.loc[c1, b] - mu.loc[c2, b]) / (sd.loc[c1, b] + sd.loc[c2, b])
            # los rangos de medias por poligono se tocan?
            solapan = not (hi.loc[c1, b] < lo.loc[c2, b] or hi.loc[c2, b] < lo.loc[c1, b])
            contr.append({"clase_1": c1, "clase_2": c2, "banda": b,
                          "contraste_dB": round(piv.loc[c1, b] - piv.loc[c2, b], 2),
                          "separabilidad_M": round(float(m), 2),
                          "separa_pixel_a_pixel": "si" if m > 1 else "no",
                          "rangos_de_poligonos_se_tocan": "si" if solapan else "no"})
    pd.DataFrame(contr).to_csv(out.replace("respuesta_por_cubierta", "contraste_entre_clases"),
                               index=False, encoding="utf-8-sig")

    png = ruta_tp("Tp2", "05_Resultados", "05_Graficos", "%s_cajas_por_banda.png" % a.sitio)
    figura_cajas(png, datos_db, clases, list(capas),
                 "pila %s (ver %s_pila_bandas.csv)" % (os.path.basename(pila), a.sitio))
    log("")
    log("Tabla  :", out)
    log("Tabla  :", out_pol)
    log("Figura :", png, "(la cita de la fuente va en el informe, debajo de la figura)")
    log.cerrar("python Tp2_04_control_zona_estable.py --sitio %s" % a.sitio)


if __name__ == "__main__":
    main()
