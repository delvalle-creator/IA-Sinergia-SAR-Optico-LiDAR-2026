# -*- coding: utf-8 -*-
"""
Tp7_02_coherencia_y_deformacion.py   [SE CORRE]   Tp7, paso 3 de la guia
================================================================
Compara, sobre la barranca de Diamante, la COHERENCIA y el DESPLAZAMIENTO de
cada banda (sinergia) y despues los combina con una regla (fusion de decision):

  SINERGIA  la diapositiva 30 lo plantea con C y L ("la banda L conserva
            coherencia en la vegetacion donde la C la pierde"). Para octubre
            de 2018 las bandas disponibles son X (COSMO-SkyMed) y C
            (Sentinel-1): SAOCOM-1A se lanzo ese mismo mes y no hay par en L.
            Se mide la coherencia media de cada banda en la ladera y en la
            zona de referencia, y se compara banda contra banda.
  FUSION    "deformacion confirmada solo si las bandas coinciden": un pixel
            se decide solo si TODAS las bandas con dato (al menos dos) tienen
            coherencia suficiente; se confirma si todas superan su umbral.
            Un pixel visto por una sola banda queda SIN DECIDIR: no es
            "confirmado".

LA REGLA DE SIGNO DEPENDE DE LA GEOMETRIA (correccion del 27/10/2026)
  Cada banda mide en SU linea de vision (LOS). El mismo movimiento puede dar
  signos distintos en dos geometrias. Por eso el signo se trata asi (--signo):
    vector  cada banda debe detectar con el signo que tendria, en SU LOS, un
            movimiento hipotetico (--mov_azimut, --mov_inclinacion; por defecto
            hacia el ONO y un poco hacia abajo, como el de 2018). Se usa la
            pasada, el rumbo y la incidencia de cada banda.
    no      no se interpreta el signo: se informa solo la COINCIDENCIA DE
            DETECCION (todas las bandas superan su umbral, con cualquier signo).
    crudo   la regla anterior ("mismo signo crudo"): solo para comparar.
    auto    (por defecto) "vector" si las pasadas de todas las bandas estan
            declaradas y son iguales; si no, "no".
  Convencion de signo: positivo = acercamiento al satelite (Phase to
  Displacement de SNAP y los_disp de HyP3).

ENTRADAS (GeoTIFF; se pasan las que haya, al menos dos bandas para fusionar)
  --x_desp / --x_coh   COSMO-SkyMed, par 15-19/10/2018. La fase hay que desenrollarla en
                       SNAP con SNAPHU (guia, paso 2): el producto del curso 2023
                       (...\\InSAR HI\\*_Stack_ifg_dinsar_flt_TC.dim) tiene la banda
                       Unw_Phase_ifg_* TODA EN CERO. --x_desp es el GeoTIFF de
                       Phase to Displacement ortorrectificado; --x_coh, la coherencia
                       ortorrectificada aparte (Phase to Displacement no la conserva).
  --x_componentes      componentes conexas de SNAPHU (GeoTIFF): la componente 0, sin
                       confianza, se enmascara (no se usa la fase aunque tenga valor).
  --x_fase             alternativa a --x_desp: la fase DESENROLLADA y ortorrectificada,
                       en radianes; el programa la convierte con d = -lambda*fase/(4*pi).
  --c_desp / --c_coh   Sentinel-1 (HyP3: *_los_disp.tif y *_corr.tif, o SNAP)
  --l_desp / --l_coh   SAOCOM, si se consiguio un par
  Geometria de cada banda: --pasada_x, --rumbo_x, --inc_x (y _c, _l). Para un
  producto HyP3, la pasada y el rumbo se leen solos del .txt que acompana al
  los_disp, y la incidencia del *_inc_map.tif si esta al lado.

REMUESTREO (regla 2 del curso)
  Para pasar a un pixel mas grueso se PROMEDIA (X de 2 m a 10 m: "average").
  No se afina a un pixel mas chico que el nativo: la C de HyP3 (40 m) se lleva
  a 10 m por vecino mas cercano (cada 16 pixeles de 10 m repiten un valor) o,
  mejor, se corre todo a --pixel 40.

ZONAS
  ladera     : barranca-periferia_Polygon.shp (relevamiento del curso 2018)
  referencia : anillo de --anillo m alrededor de la ladera, SIN el agua (se
               quita lo que el JRC Global Surface Water marca como agua al
               menos el 50 % del tiempo; si no hay conexion, se avisa). Se
               supone estable. Con --zona_estable <gpkg> se usa en cambio un
               poligono digitalizado por el grupo. El desplazamiento de cada
               banda se refiere a la mediana de esta zona: InSAR mide diferencias.
  --control_independiente : la referencia es la mitad NORTE del anillo y la
               mitad SUR queda como zona de CONTROL, que no entra en la
               referencia: alli la deformacion confirmada deberia ser cero.
  --zonas <gpkg> : poligonos con un campo "zona" (escarpa, bloque, pie,
               ciudad...): se informa por zona la fraccion observable.

UMBRALES (regla 6: cada umbral con su histograma)
  --umbral_m 0.01 (10 mm en la LOS) o, con --umbral_k k > 0, k veces la NMAD
  del desplazamiento en la referencia DE CADA BANDA. --coh_min 0.3. El
  programa guarda el histograma con la linea de cada umbral en
  05_Resultados/05_Graficos/.

SALIDA
  Tp7_Barrancas_deslizamientos/05_Resultados/04_Tablas/E1_coherencia_y_desplazamiento.csv
  Tp7_Barrancas_deslizamientos/05_Resultados/04_Tablas/E1_fusion_por_zona.csv (con --zonas)
  Tp7_Barrancas_deslizamientos/05_Resultados/02_Rasters/E1_deformacion_confirmada.tif
  Tp7_Barrancas_deslizamientos/05_Resultados/05_Graficos/E1_histogramas_umbrales.png

USO
    python Tp7_02_coherencia_y_deformacion.py --x_desp X_los.tif --x_coh X_coh.tif --pasada_x descendente
           --rumbo_x 197.5 --inc_x 59.6 --c_desp C_los.tif --c_coh C_coh.tif
"""
import argparse
import glob
import math
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import COSMO_DIAMANTE, ruta_tp               # noqa: E402
from funciones_comunes import (grilla_sitio, leer_en_grilla, rasterizar,  # noqa: E402
                               guardar_tif, Bitacora)
from funciones_cambio import fusion_decision                          # noqa: E402

# ------------------------------------------------------------ PARAMETROS
SITIO = "E1_DIAMANTE_BARRANCA"
PIXEL = 10.0                 # m; 40 para trabajar al pixel nativo de HyP3
COH_MIN = 0.3                # coherencia minima para usar un pixel
UMBRAL_M = 0.01              # umbral fijo en la LOS (m)
ANILLO = 500.0               # m alrededor de la ladera
MOV_AZIMUT = 292.5           # grados desde el norte: ONO (Soffiantini y Brunetto, 2023)
MOV_INCLINACION = 5.0        # grados por debajo de la horizontal (1,4 m horizontal, 0,1 a 0,2 m vertical)
NOMBRES = {"x": "X_COSMO", "c": "C_Sentinel1", "l": "L_SAOCOM"}


def nmad(v):
    """Dispersion robusta: 1,4826 x mediana de |v - mediana|."""
    v = v[np.isfinite(v)]
    return float(1.4826 * np.median(np.abs(v - np.median(v)))) if v.size else np.nan


def geometria_hyp3(ruta_desp):
    """Pasada, rumbo e incidencia de un producto HyP3 (del .txt y del _inc_map.tif de al lado)."""
    base = ruta_desp.replace("_los_disp.tif", "")
    pasada = rumbo = inc = None
    if os.path.exists(base + ".txt"):
        for linea in open(base + ".txt", encoding="utf-8", errors="ignore"):
            k, _, v = linea.partition(":")
            if k.strip() == "Reference Pass Direction":
                pasada = "descendente" if "DESC" in v.upper() else "ascendente"
            elif k.strip() == "Heading":
                rumbo = float(v)
    return pasada, rumbo, (base + "_inc_map.tif") if os.path.exists(base + "_inc_map.tif") else None


def signo_esperado(rumbo, inc_grados, azimut_mov, incl_mov, lado="derecha"):
    """Signo (+1 acercamiento, -1 alejamiento) que tendria en la LOS el movimiento hipotetico."""
    mira = rumbo + (90.0 if lado == "derecha" else -90.0)      # azimut de la mirada (satelite -> suelo)
    hacia_sat = math.radians(mira + 180.0)
    th = math.radians(inc_grados)
    los = np.array([math.sin(th) * math.sin(hacia_sat), math.sin(th) * math.cos(hacia_sat), math.cos(th)])
    a, b = math.radians(azimut_mov), math.radians(incl_mov)
    mov = np.array([math.cos(b) * math.sin(a), math.cos(b) * math.cos(a), -math.sin(b)])
    p = float(los @ mov)
    return (1 if p > 0 else -1), p


def figura_umbrales(datos, ruta, coh_min, log):
    """Histogramas con la linea de cada umbral: desplazamiento en la referencia y coherencia en la ladera."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    plt.rcParams["font.family"] = "Liberation Serif"
    coma = FuncFormatter(lambda v, p: ("%g" % v).replace(".", ","))
    miles = FuncFormatter(lambda v, p: "{:,.0f}".format(v).replace(",", "."))
    n = len(datos)
    fig, axs = plt.subplots(2, n, figsize=(5.2 * n, 6.4), squeeze=False)
    for j, d in enumerate(datos):
        ax = axs[0, j]
        v = 1000 * d["ref"]
        ax.hist(np.clip(v, -30, 30), bins=120, color="#1f3b73")
        u, s = 1000 * d["umbral"], 1000 * d["nmad"]
        for x, c, ls in ((u, "#d9822b", "-"), (-u, "#d9822b", "-"), (2 * s, "#2a9d8f", "--"), (-2 * s, "#2a9d8f", "--")):
            ax.axvline(x, color=c, ls=ls, lw=2)
        ax.set_title("(%s) %s: desplazamiento en la referencia" % ("ab"[j] if n == 2 else chr(97 + j), d["banda"]), fontsize=11)
        ax.set_xlabel("desplazamiento LOS (mm)")
        ax.set_ylabel("píxeles")
        ax.xaxis.set_major_formatter(coma)
        ax.yaxis.set_major_formatter(miles)
        ax = axs[1, j]
        ax.hist(d["coh"], bins=100, range=(0, 1), color="#555555")
        ax.axvline(coh_min, color="#d9822b", lw=2)
        ax.set_title("(%s) %s: coherencia en la ladera" % (chr(97 + n + j), d["banda"]), fontsize=11)
        ax.set_xlabel("coherencia")
        ax.set_ylabel("píxeles")
        ax.xaxis.set_major_formatter(coma)
        ax.yaxis.set_major_formatter(miles)
    from matplotlib.lines import Line2D
    fig.legend(handles=[Line2D([], [], color="#d9822b", lw=2, label="umbral usado (±desplazamiento o coherencia mínima)"),
                        Line2D([], [], color="#2a9d8f", lw=2, ls="--", label="±2 NMAD del desplazamiento en la referencia")],
               loc="lower center", ncol=2, frameon=False, fontsize=11)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    fig.savefig(ruta, dpi=170)
    plt.close(fig)
    log("Histogramas de los umbrales: %s" % ruta)


def main():
    import geopandas as gpd

    ap = argparse.ArgumentParser(description="Tp7, paso 3: coherencia y desplazamiento por banda y fusion de decision.")
    ap.add_argument("--pixel", type=float, default=PIXEL)
    for b in ("x", "c", "l"):
        ap.add_argument("--%s_desp" % b, default="")
        ap.add_argument("--%s_fase" % b, default="", help="fase DESENROLLADA (rad), en lugar de --%s_desp" % b)
        ap.add_argument("--%s_coh" % b, default="")
        ap.add_argument("--%s_componentes" % b, default="",
                        help="raster de componentes conexas de SNAPHU: la componente 0 (sin confianza) se enmascara")
        ap.add_argument("--pasada_%s" % b, default="", help="ascendente / descendente (metadatos: PASS)")
        ap.add_argument("--rumbo_%s" % b, type=float, default=None, help="rumbo del satelite (grados desde el norte)")
        ap.add_argument("--inc_%s" % b, type=float, default=None, help="angulo de incidencia en el sitio (grados)")
    ap.add_argument("--lambda_x", type=float, default=0.03123, help="m (COSMO-SkyMed, 9,6 GHz)")
    ap.add_argument("--lambda_c", type=float, default=0.05547, help="m (Sentinel-1, 5,405 GHz)")
    ap.add_argument("--lambda_l", type=float, default=0.2350, help="m (SAOCOM, 1,275 GHz)")
    ap.add_argument("--remuestreo_x", default="average", help="average (2 m -> pixel mas grueso)")
    ap.add_argument("--remuestreo_c", default="", help="vacio: average si el pixel >= 40 m, nearest si es menor")
    ap.add_argument("--coh_min", type=float, default=COH_MIN)
    ap.add_argument("--umbral_m", type=float, default=UMBRAL_M)
    ap.add_argument("--umbral_k", type=float, default=0.0, help="> 0: umbral = k x NMAD de la referencia de cada banda")
    ap.add_argument("--signo", default="auto", choices=("auto", "vector", "no", "crudo"))
    ap.add_argument("--mov_azimut", type=float, default=MOV_AZIMUT)
    ap.add_argument("--mov_inclinacion", type=float, default=MOV_INCLINACION)
    ap.add_argument("--anillo", type=float, default=ANILLO)
    ap.add_argument("--ladera", default="")
    ap.add_argument("--zona_estable", default="", help="GeoPackage con la zona de referencia (reemplaza el anillo)")
    ap.add_argument("--control_independiente", action="store_true",
                    help="referencia = mitad norte del anillo; control = mitad sur")
    ap.add_argument("--zonas", default="", help="GeoPackage con poligonos y campo 'zona' (escarpa, bloque, pie, ciudad)")
    ap.add_argument("--sufijo", default="", help="agrega un sufijo a las salidas (para variantes)")
    a = ap.parse_args()
    suf = a.sufijo
    log = Bitacora(ruta_tp("Tp7", "05_Resultados", "06_Control_calidad"), "Tp7_02_deformacion" + suf)
    g = grilla_sitio(SITIO, pixel=a.pixel)
    ladera_shp = a.ladera or (glob.glob(os.path.join(COSMO_DIAMANTE, "GRIETAS", "barranca-periferia_Polygon.shp")) or [""])[0]
    if not ladera_shp or not os.path.exists(ladera_shp):
        sys.exit("No encuentro el poligono de la ladera (barranca-periferia_Polygon.shp). Pasarlo con --ladera.")
    lad = gpd.read_file(ladera_shp).to_crs(g["crs"])
    # El poligono relevado en 2018 tiene autointersecciones: se repara antes de
    # operar (make_valid no cambia la forma, solo la topologia).
    lad["geometry"] = lad.geometry.make_valid()
    lad_ok = ruta_tp("Tp7", "04_Tablas_de_trabajo", "E1_ladera_reparada.gpkg")
    os.makedirs(os.path.dirname(lad_ok), exist_ok=True)
    lad.to_file(lad_ok, driver="GPKG")
    m_lad = rasterizar(lad_ok, g) > 0
    union = lad.union_all() if hasattr(lad, "union_all") else lad.unary_union
    anillo = gpd.GeoSeries([union.buffer(a.anillo).difference(union)], crs=g["crs"])
    tmp = ruta_tp("Tp7", "04_Tablas_de_trabajo", "E1_zona_referencia.gpkg")
    gpd.GeoDataFrame(geometry=anillo, crs=g["crs"]).to_file(tmp, driver="GPKG")
    m_ctl = None
    if a.zona_estable:
        m_ref = (rasterizar(a.zona_estable, g) > 0) & ~m_lad
        log("Referencia: zona estable digitalizada %s (%d pixeles)." % (a.zona_estable, m_ref.sum()))
    else:
        m_ref = rasterizar(tmp, g) > 0
        try:
            from funciones_comunes import jrc_ocurrencia
            occ, _ = jrc_ocurrencia(SITIO, g)
            agua = np.nan_to_num(occ, nan=0) >= 50
            log("Del anillo se quitan %d pixeles de agua (JRC, ocurrencia >= 50 %%)." % (m_ref & agua).sum())
            m_ref &= ~agua
        except Exception as e:                       # noqa: BLE001
            log("AVISO: no se pudo leer el JRC (%s): el anillo puede incluir el rio. Usar --zona_estable." % str(e)[:80])
        log("Referencia: anillo de %.0f m alrededor de la ladera (%d pixeles)." % (a.anillo, m_ref.sum()))
    if a.control_independiente:
        # La referencia y el control no comparten pixeles: el control prueba la regla sin circularidad.
        filas_y = np.arange(g["height"])[:, None] * np.ones((1, g["width"]))
        cy = (g["bounds"][3] - union.centroid.y) / a.pixel
        m_ctl = m_ref & (filas_y > cy)
        m_ref = m_ref & (filas_y <= cy)
        log("Control independiente: referencia = mitad norte del anillo (%d pixeles); control = mitad sur (%d pixeles)."
            % (m_ref.sum(), m_ctl.sum()))
    log("Ladera: %s (%d pixeles de %.0f m)." % (os.path.basename(ladera_shp), m_lad.sum(), a.pixel))

    filas, decisiones, rels, datos_fig, geo = [], {}, {}, [], {}
    for b in ("x", "c", "l"):
        nombre = NOMBRES[b]
        rd, rf, rc = getattr(a, "%s_desp" % b), getattr(a, "%s_fase" % b), getattr(a, "%s_coh" % b)
        if not ((rd or rf) and rc):
            continue
        rem = a.remuestreo_x if b == "x" else (a.remuestreo_c or ("average" if a.pixel >= 40 else "nearest"))
        if b != "x" and rem == "bilinear":
            log("AVISO: %s con bilineal afina por debajo del pixel nativo (regla 2). Se usa igual, declarado." % nombre)
        if rd:
            dsp = leer_en_grilla(rd, g, rem)
        else:
            # desplazamiento en la linea de vision: d = -lambda * fase / (4 pi)
            # (la misma convencion que Phase to Displacement de SNAP: positivo = acercamiento)
            lam = getattr(a, "lambda_%s" % b)
            dsp = -lam * leer_en_grilla(rf, g, rem) / (4 * np.pi)
            log("%s: desplazamiento LOS calculado de la fase desenrollada con lambda = %.4f m" % (nombre, lam))
        coh = leer_en_grilla(rc, g, rem)
        coh = np.where(coh > 0, coh, np.nan)          # SNAP escribe 0 fuera de la escena
        rcomp = getattr(a, "%s_componentes" % b)
        if rcomp:
            # La componente 0 de SNAPHU no tiene confianza: alli el numero de ciclos sumado puede estar mal.
            # Se toma la componente mas frecuente dentro del pixel (moda) y se anula la fase donde es 0.
            comp = leer_en_grilla(rcomp, g, "mode")
            sin_conf = ~(np.nan_to_num(comp) > 0)
            log("%s: componentes de SNAPHU: %.1f %% de la ladera en la componente 0 (sin confianza); alli no se usa"
                " la fase." % (nombre, 100 * float(np.mean(sin_conf[m_lad]))))
            dsp = np.where(sin_conf, np.nan, dsp)
        log("%s: remuestreo a %.0f m por '%s'." % (nombre, a.pixel, rem))
        # geometria de vision
        pas, rum, inc = getattr(a, "pasada_%s" % b), getattr(a, "rumbo_%s" % b), getattr(a, "inc_%s" % b)
        if rd and rd.endswith("_los_disp.tif"):
            p2, r2, finc = geometria_hyp3(rd)
            pas = pas or p2 or ""
            rum = rum if rum is not None else r2
            if inc is None and finc:
                inc = float(np.degrees(np.nanmedian(leer_en_grilla(finc, g, "average")[m_lad])))
        geo[nombre] = (pas, rum, inc)
        log("%s: pasada %s, rumbo %s, incidencia en la ladera %s" % (
            nombre, pas or "NO DECLARADA", ("%.1f grados" % rum) if rum is not None else "no declarado",
            ("%.1f grados" % inc) if inc is not None else "no declarada"))
        # Banda vacia: el producto del curso 2023 tiene la Unw_Phase en cero salvo un punado de pixeles
        # (11 de 5,8 millones), asi que "todo cero" no alcanza: se mira la fraccion de pixeles con
        # coherencia y valor distinto de cero.
        con_coh = np.isfinite(dsp) & np.isfinite(coh)
        frac_no_cero = float(np.mean(dsp[con_coh] != 0)) if con_coh.any() else 0.0
        if frac_no_cero < 0.01:
            log("%s: el desplazamiento (o la fase desenrollada) vale CERO en casi todo el sitio (%.4f %% distinto"
                " de cero). Eso no es"
                " estabilidad: es una banda vacia (el desenrollado con SNAPHU no se importo). Se informa"
                " solo la coherencia de esta banda." % (nombre, 100 * frac_no_cero))
            dsp = np.full(dsp.shape, np.nan, dtype="float32")
        ok = np.isfinite(dsp) & np.isfinite(coh) & (coh >= a.coh_min)
        ref = np.nanmedian(dsp[ok & m_ref]) if (ok & m_ref).any() else np.nan
        rel = dsp - ref
        s_ref = nmad(rel[ok & m_ref])
        umbral = a.umbral_k * s_ref if a.umbral_k > 0 else a.umbral_m
        fila = {"banda": nombre,
                "pasada": pas, "incidencia_grados": round(inc, 1) if inc is not None else np.nan,
                "coherencia_media_ladera": round(float(np.nanmean(coh[m_lad])), 3),
                "coherencia_media_referencia": round(float(np.nanmean(coh[m_ref])), 3),
                # coherencia sola: una banda sin desplazamiento (fase sin desenrollar) igual informa su coherencia
                "%_ladera_coherente": round(float(100 * np.mean((np.nan_to_num(coh) >= a.coh_min)[m_lad])), 1),
                "desp_mediana_ladera_m": round(float(np.nanmedian(rel[ok & m_lad])), 4) if (ok & m_lad).any() else np.nan,
                "desp_p05_ladera_m": round(float(np.nanpercentile(rel[ok & m_lad], 5)), 4) if (ok & m_lad).any() else np.nan,
                "desvio_referencia_m": round(float(np.nanstd(rel[ok & m_ref])), 4) if (ok & m_ref).any() else np.nan,
                "nmad_referencia_m": round(s_ref, 4),
                "umbral_m": round(umbral, 4)}
        filas.append(fila)
        if np.isfinite(dsp).any():
            decisiones[nombre] = np.where(ok, (np.abs(rel) > umbral).astype("float32") * np.sign(rel), np.nan)
            rels[nombre] = rel
            datos_fig.append({"banda": nombre, "ref": rel[ok & m_ref], "nmad": s_ref, "umbral": umbral,
                              "coh": coh[m_lad & np.isfinite(coh)]})
        log("%-12s coherencia ladera %.2f / referencia %.2f; %4.1f %% de la ladera coherente; "
            "desplazamiento mediano %.1f mm; ruido en la referencia %.1f mm (desvio) / %.1f mm (NMAD); umbral %.1f mm"
            % (nombre, fila["coherencia_media_ladera"], fila["coherencia_media_referencia"],
               fila["%_ladera_coherente"], 1000 * fila["desp_mediana_ladera_m"],
               1000 * fila["desvio_referencia_m"], 1000 * s_ref, 1000 * umbral))
        if fila["desvio_referencia_m"] and fila["desvio_referencia_m"] > umbral:
            log("   ATENCION: el ruido en la zona estable (%.1f mm) supera el umbral (%.1f mm): la deteccion"
                " en esta banda no es confiable (atmosfera, desenrollado)." % (1000 * fila["desvio_referencia_m"], 1000 * umbral))
    t = pd.DataFrame(filas)
    out = ruta_tp("Tp7", "05_Resultados", "04_Tablas", "E1_coherencia_y_desplazamiento%s.csv" % suf)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    t.to_csv(out, index=False, encoding="utf-8-sig")
    if datos_fig:
        figura_umbrales(datos_fig, ruta_tp("Tp7", "05_Resultados", "05_Graficos", "E1_histogramas_umbrales%s.png" % suf),
                        a.coh_min, log)
    if len(decisiones) < 2:
        log("Menos de dos bandas con desplazamiento valido (%s): hay medicion, pero no fusion de"
            " decision. Declararlo." % (", ".join(decisiones) or "ninguna"))
        log.cerrar("python Tp7_03_cicatriz_y_volumen.py")
        return
    # ------------------------------------------------- regla de signo segun la geometria
    modo = a.signo
    pasadas = [geo[k][0] for k in decisiones]
    if modo == "auto":
        modo = "vector" if all(pasadas) and len(set(pasadas)) == 1 and all(geo[k][1] is not None and geo[k][2] is not None
                                                                           for k in decisiones) else "no"
        log("Regla de signo: '%s' (pasadas %s)." % (modo, ", ".join(p or "sin declarar" for p in pasadas)))
    esperado = {}
    if modo == "vector":
        for k in decisiones:
            pas, rum, inc = geo[k]
            if rum is None or inc is None:
                sys.exit("Para --signo vector hace falta el rumbo y la incidencia de %s (--rumbo_*, --inc_*)." % k)
            s, p = signo_esperado(rum, inc, a.mov_azimut, a.mov_inclinacion)
            esperado[k] = s
            log("%s: un movimiento de 1 m hacia %.1f grados y %.1f grados hacia abajo da %+.2f m en su LOS (%s)."
                % (k, a.mov_azimut, a.mov_inclinacion, p, "acercamiento" if s > 0 else "alejamiento"))
    n = len(decisiones)
    if modo == "no":
        det = {k: np.where(np.isfinite(v), (v != 0).astype("float32"), np.nan) for k, v in decisiones.items()}
        cp, votos = fusion_decision(det, "interseccion", minimo_votos=n)
        conf = np.where(np.isfinite(cp), cp, np.nan).astype("float32")
        regla = "coincidencia de deteccion (todas superan su umbral, signo no interpretado)"
    else:
        norm = {k: (v * esperado[k] if modo == "vector" else v) for k, v in decisiones.items()}
        pos = {k: np.where(np.isfinite(v), (v > 0).astype("float32"), np.nan) for k, v in norm.items()}
        neg = {k: np.where(np.isfinite(v), (v < 0).astype("float32"), np.nan) for k, v in norm.items()}
        cp, _ = fusion_decision(pos, "interseccion", minimo_votos=n)
        cn, votos = fusion_decision(neg, "interseccion", minimo_votos=n)
        conf = np.where(np.isfinite(cp), np.where(cp == 1, 1, np.where(cn == 1, -1, 0)), np.nan).astype("float32")
        regla = ("+1 = todas detectan con el signo del movimiento hipotetico en su LOS; -1 = todas con el signo contrario"
                 if modo == "vector" else "+1 / -1 = todas superan el umbral con el mismo signo crudo")
    guardar_tif(ruta_tp("Tp7", "05_Resultados", "02_Rasters", "E1_deformacion_confirmada%s.tif" % suf),
                {"deformacion_confirmada": conf, "bandas_que_votaron": votos.astype("float32")}, g,
                "Interferometria de %s (ver bitacora para cada producto)" % ", ".join(decisiones),
                "Fusion de decision (%s): %s; umbral %s; coherencia >= %.2f" % (
                    modo, regla, ", ".join("%s %.1f mm" % (r["banda"], 1000 * r["umbral_m"]) for r in filas), a.coh_min))
    log("Regla aplicada (%s): %s." % (modo, regla))
    log("Deformacion confirmada por las %d bandas: %d pixeles en la ladera (%d en la referencia)."
        % (n, np.nansum(np.abs(conf[m_lad])), np.nansum(np.abs(conf[m_ref]))))
    log("Pixeles de la ladera decididos (todas las bandas con dato coherente): %d de %d (%.1f %%)."
        % (np.isfinite(conf[m_lad]).sum(), m_lad.sum(), 100 * np.isfinite(conf[m_lad]).mean()))
    if a.pixel < 40 and any(k != "X_COSMO" for k in decisiones):
        log("   Nota: la C de HyP3 tiene pixeles de 40 m; a %.0f m cada %d pixeles comparten un valor: las"
            " observaciones independientes son unas %d." % (a.pixel, (40 / a.pixel) ** 2,
                                                           np.isfinite(conf[m_lad]).sum() / (40 / a.pixel) ** 2))
    if m_ctl is not None:
        log("Control independiente (mitad sur del anillo, fuera de la referencia): %d pixeles confirmados de %d decididos."
            % (np.nansum(np.abs(conf[m_ctl])), np.isfinite(conf[m_ctl]).sum()))
        for k, r in rels.items():
            okc = m_ctl & np.isfinite(r)
            log("   %s en el control: mediana %.1f mm, NMAD %.1f mm" % (k, 1000 * np.nanmedian(r[okc]), 1000 * nmad(r[okc])))
    else:
        log("Control: en la referencia deberia ser cero; para un control que no sea circular, correr con"
            " --control_independiente.")
    if a.zonas:
        z = gpd.read_file(a.zonas).to_crs(g["crs"])
        filas_z = []
        for nom in z["zona"].unique():
            tz = ruta_tp("Tp7", "04_Tablas_de_trabajo", "_tmp_zona.gpkg")
            z[z["zona"] == nom].to_file(tz, driver="GPKG")
            mz = rasterizar(tz, g) > 0
            fz = {"zona": nom, "pixeles": int(mz.sum())}
            for k, v in decisiones.items():
                fz["%%_coherente_%s" % k] = round(100 * float(np.isfinite(v[mz]).mean()), 1) if mz.any() else np.nan
            fz["%_observable_todas"] = round(100 * float(np.isfinite(conf[mz]).mean()), 1) if mz.any() else np.nan
            fz["confirmados"] = int(np.nansum(np.abs(conf[mz])))
            filas_z.append(fz)
            log("Zona %-8s %6d pixeles; observable por todas las bandas %5.1f %%; %s; confirmados %d"
                % (nom, fz["pixeles"], fz["%_observable_todas"],
                   ", ".join("%s %.1f %%" % (k, fz["%%_coherente_%s" % k]) for k in decisiones), fz["confirmados"]))
        pd.DataFrame(filas_z).to_csv(ruta_tp("Tp7", "05_Resultados", "04_Tablas", "E1_fusion_por_zona%s.csv" % suf),
                                     index=False, encoding="utf-8-sig")
    log.cerrar("python Tp7_03_cicatriz_y_volumen.py")


if __name__ == "__main__":
    main()
