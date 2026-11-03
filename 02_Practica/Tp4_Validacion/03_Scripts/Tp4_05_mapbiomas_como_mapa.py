# -*- coding: utf-8 -*-
"""
Tp4_05_mapbiomas_como_mapa.py   [SE CORRE]   Tp4, paso 10 de la guia
=================================================================
Prepara un mapa REAL para validar con el mismo ciclo de los pasos 6 a 8:
la cobertura 2025 de MapBiomas Argentina (Coleccion 3) llevada a las clases
del curso y a la grilla de 20 m del mapa de control.

POR QUE
  El ensayo de los pasos 6 a 8 se hace sobre el mapa de control, que es la
  referencia del grupo. MapBiomas es un mapa de terceros que se usa en todo el
  curso como contexto (Tp1 a Tp3): antes de usarlo hay que saber cuanto vale.
  Se lo valida igual que cualquier mapa: muestreo estratificado por SUS
  clases (Tp4_02), etiquetado al azar y estimador de Olofsson (Tp4_03).

EQUIVALENCIA DE CLASES (MapBiomas -> curso)
   3 Bosques cerrados, 4 Bosques abiertos, 6 Bosques inundables -> 3 monte_nativo
   9 Silvicultura                                               -> 4 plantacion_forestal
  11 Herbaceas inundables                                       -> 2 humedal_pajonal
  12 Herbaceas, 15 Pastura, 19 Cultivos temporarios,
  36 Cultivos perennes (citricos, arandanos), 21 Mosaico        -> 5 herbaceo_cultivo_pastura
  25 Otras areas no vegetadas, 30 Mineria                       -> 6 suelo_desnudo
  24 Areas urbanas                                              -> 7 urbano
  33 Rios, lagunas, lagos                                       -> 1 agua_permanente
  La clase 8 (otra: tuneles de arandanos) no existe en MapBiomas: los tuneles
  quedan dentro de cultivos perennes. Es una decision del curso y se declara.
  OJO: la clase 5 del curso es "herbaceo": junta las herbaceas NATURALES (12, el
  pastizal) con la pastura y los cultivos. No es solo "cultivo".

OTRA EQUIVALENCIA (sin programar)
  La equivalencia de arriba es la del curso. Para ensayar otra (por ejemplo,
  Bosques abiertos -> herbaceo, o Herbaceas -> humedal), copie el archivo
  05_Resultados/04_Tablas/<SITIO>_mapbiomas_2025_equivalencias.csv, cambie la
  columna codigo_curso en una planilla y corra con
      --equivalencias <archivo.csv> --sufijo <nombre_corto>
  El mapa sale con otro nombre (no pisa el del curso). Como la muestra ya se
  sorteo con los estratos del mapa del curso, el mapa alternativo se evalua con
  la MISMA muestra y Tp4_06_muestra_comun.py (estimador de Stehman, 2014).

CONTEXTO (no entra a la validacion)
  Por clase del curso: la mediana de la biomasa del CCI 2024 y de la banda P de
  BIOMASS (HH y VH, en dB; la HV trae interferencia de radiofrecuencia sin
  corregir y no se usa).

SALIDA
  Tp4_Validacion/02_Subsets_SNAP_QGIS/<SITIO>_mapbiomas_2025_clases_curso_20m.tif   (uint8, 0 = sin dato)
  Tp4_Validacion/05_Resultados/04_Tablas/<SITIO>_mapbiomas_2025_equivalencias.csv
  Tp4_Validacion/05_Resultados/04_Tablas/<SITIO>_mapbiomas_2025_contexto_por_clase.csv

USO
    python Tp4_05_mapbiomas_como_mapa.py --sitio B_CONCORDIA --anio 2025
"""
import argparse
import glob
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import SITIOS, ruta_tp                       # noqa: E402
from funciones_comunes import leer_en_grilla, grilla_de_tif, lin_a_db, Bitacora  # noqa: E402

CURSO = {1: "agua_permanente", 2: "humedal_pajonal", 3: "monte_nativo", 4: "plantacion_forestal",
         5: "herbaceo_cultivo_pastura", 6: "suelo_desnudo", 7: "urbano", 8: "otra"}
# La clase 5 lleva aqui el nombre "herbaceo_cultivo_pastura" porque, desde MapBiomas, junta el pastizal
# natural (12 Herbaceas) con la pastura y los cultivos. El codigo (5) es el mismo del mapa de control.
EQUIV = {3: 3, 4: 3, 6: 3, 9: 4, 11: 2, 12: 5, 15: 5, 19: 5, 21: 5, 36: 5, 25: 6, 30: 6, 24: 7, 33: 1}
FUENTE = ("Proyecto MapBiomas Argentina, Coleccion 3 de los mapas anuales de cobertura y uso del suelo, "
          "https://argentina.mapbiomas.org (CC BY 4.0)")


def nombres_mapbiomas(qml):
    import re
    out = {}
    if qml and os.path.exists(qml):
        s = open(qml, encoding="utf-8").read()
        for m in re.finditer(r'<paletteEntry([^>]*)/>', s):
            at = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
            out[int(at["value"])] = re.sub(r"^\d+\s+", "", at.get("label", ""))
    return out


def carpetas_qgis():
    """Las carpetas QGIS_GeoTIFF de los practicos, la del Tp1 primero (sus subsets cubren Concordia)."""
    otras = sorted(glob.glob(os.path.join(ruta_tp("Tp1"), "..", "Tp*", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF")))
    tp1 = os.path.join(ruta_tp("Tp1"), "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF")
    return [tp1] + [c for c in otras if os.path.normpath(c) != os.path.normpath(tp1)]


def buscar(patron):
    """Busca un subset del sitio en la carpeta QGIS_GeoTIFF del Tp1 y, si no esta, en la de otro practico."""
    for c in carpetas_qgis():
        f = sorted(glob.glob(os.path.join(c, patron)))
        if f:
            return os.path.normpath(f[0])
    return None


def main():
    import rasterio
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", required=True, choices=list(SITIOS.keys()))
    ap.add_argument("--anio", type=int, default=2025)
    ap.add_argument("--equivalencias", default="",
                    help="CSV con columnas codigo_mapbiomas y codigo_curso (por defecto, la del curso)")
    ap.add_argument("--sufijo", default="", help="se agrega al nombre del mapa si se usa otra equivalencia")
    a = ap.parse_args()
    equiv = dict(EQUIV)
    if a.equivalencias:
        e = pd.read_csv(a.equivalencias, encoding="utf-8-sig")
        equiv = {int(k): int(v) for k, v in zip(e.codigo_mapbiomas, e.codigo_curso)}
        if not a.sufijo:
            sys.exit("Con --equivalencias hay que dar --sufijo (por ejemplo --sufijo abiertos_herbaceo), "
                     "para no pisar el mapa del curso.")
    suf = ("_" + a.sufijo) if a.sufijo else ""
    log = Bitacora(ruta_tp("Tp4", "05_Resultados", "06_Control_calidad"), "Tp4_05_%s%s" % (a.sitio, suf))
    if a.equivalencias:
        log("Equivalencia leida de %s (no es la del curso)." % a.equivalencias)

    control = ruta_tp("Tp4", "02_Subsets_SNAP_QGIS", "%s_cobertura_control_20m.tif" % a.sitio)
    if not os.path.exists(control):
        sys.exit("Falta %s: corra antes Tp4_01 (la grilla del mapa de MapBiomas es la del mapa de control)." % control)
    g = grilla_de_tif(control)
    f_mb = buscar("%s_MapBiomas_cobertura_1985_*.tif" % a.sitio)
    if not f_mb:
        sys.exit("No encuentro %s_MapBiomas_cobertura_1985_*.tif en ninguna carpeta QGIS_GeoTIFF." % a.sitio)
    banda = a.anio - 1985 + 1
    nom = nombres_mapbiomas(f_mb.replace(".tif", ".qml"))
    log("MapBiomas: %s, banda %d (= %d)" % (f_mb, banda, a.anio))
    log("Grilla: la del mapa de control (%s), %d x %d, pixel %.0f m" % (os.path.basename(control), g["width"],
                                                                        g["height"], g["transform"].a))
    mb = leer_en_grilla(f_mb, g, "nearest", banda=banda, nodata_origen=0, tipo="uint8").astype("int64")
    curso = np.zeros(mb.shape, dtype="uint8")
    for k, v in equiv.items():
        curso[mb == k] = v
    sin_equiv = sorted(set(np.unique(mb[mb > 0]).tolist()) - set(equiv))
    if sin_equiv:
        log("AVISO: clases de MapBiomas sin equivalencia (quedan sin dato): %s" % sin_equiv)
    px_ha = g["transform"].a * abs(g["transform"].e) / 1e4
    log("MapBiomas cubre el %.1f %% del sitio; el resto (fuera de la coleccion) queda sin dato." %
        (100 * (mb > 0).mean()))

    filas = []
    for k in sorted(np.unique(mb[mb > 0])):
        filas.append({"codigo_mapbiomas": int(k), "clase_mapbiomas": nom.get(int(k), ""),
                      "codigo_curso": equiv.get(int(k), 0), "clase_curso": CURSO.get(equiv.get(int(k), 0), "sin equivalencia"),
                      "superficie_ha": round(float((mb == k).sum() * px_ha), 1)})
    eq = pd.DataFrame(filas)
    log.titulo("Equivalencia de clases, %d" % a.anio)
    log(eq.to_string(index=False))

    out = ruta_tp("Tp4", "02_Subsets_SNAP_QGIS", "%s_mapbiomas_%d%s_clases_curso_20m.tif" % (a.sitio, a.anio, suf))
    perfil = {"driver": "GTiff", "width": g["width"], "height": g["height"], "count": 1, "dtype": "uint8",
              "crs": g["crs"], "transform": g["transform"], "nodata": 0, "compress": "deflate"}
    with rasterio.open(out, "w", **perfil) as dst:
        dst.write(curso, 1)
        dst.set_band_description(1, "clase_curso_desde_MapBiomas_%d" % a.anio)
        dst.update_tags(FUENTE=FUENTE, PROCESO="MapBiomas %d reclasificado a las clases del curso (Tp4_05), "
                        "vecino mas cercano a la grilla del mapa de control" % a.anio,
                        CLASES="; ".join("%d=%s" % kv for kv in CURSO.items()))

    # ------------------------------------------------ contexto: CCI 2024 y banda P por clase del curso
    ctx = {}
    f_cci = buscar("%s_CCI_Biomass_*AGB.tif" % a.sitio)
    if f_cci:
        with rasterio.open(f_cci) as s:
            d = list(s.descriptions)
        if "AGB_2024" in d:
            ctx["CCI_AGB_2024"] = leer_en_grilla(f_cci, g, "nearest", banda=d.index("AGB_2024") + 1)
    f_p = [f for c in carpetas_qgis() for f in sorted(glob.glob(os.path.join(c, "%s_BIOMASS_P_2*.tif" % a.sitio)))
           if os.path.basename(f).count("_") == a.sitio.count("_") + 3]
    if f_p:
        with rasterio.open(f_p[0]) as s:
            d = list(s.descriptions)
        for pol in ("HH", "VH"):
            ctx["P_%s_dB" % pol] = lin_a_db(leer_en_grilla(f_p[0], g, "average", banda=d.index("Gamma0_" + pol) + 1))
        log("")
        log("Banda P: %s (HH y VH; la HV trae interferencia de radiofrecuencia sin corregir y no se usa)." %
            os.path.basename(f_p[0]))
    filas = []
    for k, n in CURSO.items():
        sel = curso == k
        if not sel.any():
            continue
        f = {"codigo_curso": k, "clase_curso": n, "superficie_ha": round(float(sel.sum() * px_ha), 1),
             "pct_area_con_dato": round(100 * sel.sum() / (curso > 0).sum(), 2)}
        for c, arr in ctx.items():
            v = arr[sel]
            v = v[np.isfinite(v)]
            f[c + "_mediana"] = round(float(np.median(v)), 1) if v.size else np.nan
        filas.append(f)
    tc = pd.DataFrame(filas)
    log.titulo("Mapa a validar: clases del curso desde MapBiomas %d, con CCI 2024 y banda P (medianas)" % a.anio)
    log(tc.to_string(index=False))
    tab = ruta_tp("Tp4", "05_Resultados", "04_Tablas")
    os.makedirs(tab, exist_ok=True)
    eq.to_csv(os.path.join(tab, "%s_mapbiomas_%d%s_equivalencias.csv" % (a.sitio, a.anio, suf)), index=False, encoding="utf-8-sig")
    tc.to_csv(os.path.join(tab, "%s_mapbiomas_%d%s_contexto_por_clase.csv" % (a.sitio, a.anio, suf)), index=False,
              encoding="utf-8-sig")
    log("")
    log("Mapa a validar:", out)
    log.cerrar("python Tp4_02_muestreo_estratificado.py --mapa ..\\02_Subsets_SNAP_QGIS\\%s --SE 0.05 --minimo 10"
               % os.path.basename(out))


if __name__ == "__main__":
    main()
