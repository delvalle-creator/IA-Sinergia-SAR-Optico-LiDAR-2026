# -*- coding: utf-8 -*-
"""
Tp4_07_acuerdo_entre_interpretes.py   [SE CORRE]   Tp4, paso 7 (control de la referencia)
=====================================================================================
El acuerdo entre intérpretes es el control de la REFERENCIA, no del mapa: dice si
dos personas, mirando las mismas imágenes con el mismo protocolo, ponen la misma
clase. No es la exactitud del mapa y no entra en el estimador de Tp4_03.

DOS PASOS
  1) --preparar: copia los puntos etiquetados a un GeoPackage NUEVO, sin etiquetas y
     con los id mezclados otra vez (otra semilla), para que el segundo intérprete no
     pueda saber qué etiqueta puso el primero ni de qué estrato viene cada punto.
     Por defecto toma los 10 primeros id (como pide la guía) o todos con --todos.
       salida: 04_Tablas_de_trabajo/<NOMBRE>_segundo_interprete.gpkg
               04_Tablas_de_trabajo/<NOMBRE>_segundo_interprete_llave_NO_ABRIR.csv  (id nuevo -> id original)
  2) --medir: con el segundo GeoPackage ya etiquetado, une por la llave y calcula:
       - acuerdo simple (proporción de puntos con la misma clase) y su intervalo de Wilson;
       - kappa de Cohen (acuerdo corregido por el azar) con su error estándar aproximado;
       - la tabla de coincidencias entre intérpretes y la lista de desacuerdos.
     Criterio de la verificación (control 11): acuerdo en al menos 8 de 10.

USO
    python Tp4_07_acuerdo_entre_interpretes.py --preparar --nombre B_CONCORDIA_cobertura_control_20m
    (el segundo intérprete etiqueta <NOMBRE>_segundo_interprete.gpkg en QGIS, como en el paso 7)
    python Tp4_07_acuerdo_entre_interpretes.py --medir --nombre B_CONCORDIA_cobertura_control_20m
"""
import argparse
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

SEMILLA_SEGUNDO = 7         # distinta de la de Tp4_02 (2026): el orden nuevo no se deduce del primero
N_POR_DEFECTO = 10          # la guía pide diez puntos etiquetados por dos personas


def wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def kappa_cohen(a, b):
    """Kappa de Cohen y su error estándar aproximado (Fleiss, Cohen y Everitt, 1969, simplificado)."""
    cl = sorted(set(a) | set(b))
    n = len(a)
    m = pd.crosstab(pd.Categorical(a, cl), pd.Categorical(b, cl), dropna=False).values / n
    po = np.trace(m)
    pe = float(np.sum(m.sum(1) * m.sum(0)))
    if pe >= 1:
        return np.nan, np.nan
    k = (po - pe) / (1 - pe)
    se = np.sqrt(po * (1 - po) / (n * (1 - pe) ** 2))
    return k, se


def main():
    import geopandas as gpd
    from configuracion_comun import ruta_tp
    from funciones_comunes import Bitacora
    ap = argparse.ArgumentParser(description="Acuerdo entre dos intérpretes de la referencia")
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--preparar", action="store_true")
    ap.add_argument("--medir", action="store_true")
    ap.add_argument("--todos", action="store_true", help="re-etiquetar todos los puntos, no sólo los 10 primeros")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp4", "05_Resultados", "06_Control_calidad"), "Tp4_07_%s" % a.nombre)
    carpeta = ruta_tp("Tp4", "04_Tablas_de_trabajo")
    prim = os.path.join(carpeta, "%s_puntos_a_etiquetar.gpkg" % a.nombre)
    seg = os.path.join(carpeta, "%s_segundo_interprete.gpkg" % a.nombre)
    llave2 = os.path.join(carpeta, "%s_segundo_interprete_llave_NO_ABRIR.csv" % a.nombre)
    p1 = gpd.read_file(prim, layer="puntos")
    if a.preparar:
        if os.path.exists(seg):
            sys.exit("YA EXISTE %s: no se reescribe (puede tener etiquetas del segundo intérprete)." % seg)
        sel = p1 if a.todos else p1[p1.id <= N_POR_DEFECTO]
        sel = sel.sample(frac=1.0, random_state=SEMILLA_SEGUNDO).reset_index(drop=True)
        nuevo = np.arange(1, len(sel) + 1)
        vacio = pd.Series([None] * len(sel), dtype="object")
        gpd.GeoDataFrame({"id": nuevo, "clase_ref": vacio, "confianza": vacio, "imagen_usada": vacio,
                          "observacion": vacio}, geometry=sel.geometry.values, crs=p1.crs
                         ).to_file(seg, layer="puntos", driver="GPKG")
        pd.DataFrame({"id_nuevo": nuevo, "id_original": sel.id.values}).to_csv(llave2, index=False, encoding="utf-8-sig")
        log("Puntos para el segundo intérprete (sin etiquetas, orden nuevo): %s (%d puntos)" % (seg, len(sel)))
        log("No abra %s hasta terminar." % llave2)
        log.cerrar("etiquetar en QGIS y correr --medir")
        return
    if not a.medir:
        sys.exit("Elija --preparar o --medir.")
    p2 = gpd.read_file(seg, layer="puntos")
    ll = pd.read_csv(llave2, encoding="utf-8-sig")
    t = p2.drop(columns="geometry").merge(ll, left_on="id", right_on="id_nuevo") \
          .merge(p1.drop(columns="geometry"), left_on="id_original", right_on="id", suffixes=("_2", "_1"))
    t = t[t.clase_ref_1.notna() & t.clase_ref_2.notna()]
    a1 = t.clase_ref_1.astype(float).astype(int).values
    a2 = t.clase_ref_2.astype(float).astype(int).values
    n = len(t)
    k = int((a1 == a2).sum())
    lo, hi = wilson(k, n)
    kap, se = kappa_cohen(a1, a2)
    log.titulo("Acuerdo entre intérpretes (control de la referencia, no exactitud del mapa)")
    log("Puntos con las dos etiquetas: %d" % n)
    log("Acuerdo simple: %d de %d = %.2f (Wilson 95 %%: %.2f a %.2f)" % (k, n, k / n, lo, hi))
    log("Kappa de Cohen: %.2f +/- %.2f (IC 95 %% aproximado)" % (kap, 1.96 * se))
    log("Control 11 de la verificación: %s" % ("ACEPTA (8 o más de 10)" if k >= 0.8 * n else
                                                "NO ACEPTA: revisar el protocolo de respuesta y volver a etiquetar"))
    log.titulo("Coincidencias (filas = primer intérprete, columnas = segundo)")
    log(pd.crosstab(a1, a2).to_string())
    d = t[a1 != a2]
    if len(d):
        log.titulo("Desacuerdos")
        log(d[["id_original", "clase_ref_1", "clase_ref_2", "confianza_1", "confianza_2", "observacion_1",
               "observacion_2"]].to_string(index=False))
    out = ruta_tp("Tp4", "05_Resultados", "04_Tablas", "%s_acuerdo_entre_interpretes.csv" % a.nombre)
    pd.DataFrame([{"n": n, "acuerdos": k, "acuerdo_simple": round(k / n, 3), "wilson_inf": round(lo, 3),
                   "wilson_sup": round(hi, 3), "kappa": round(kap, 3), "IC95_kappa": round(1.96 * se, 3)}]
                 ).to_csv(out, index=False, encoding="utf-8-sig")
    log("Tabla:", out)
    log.cerrar()


if __name__ == "__main__":
    main()
