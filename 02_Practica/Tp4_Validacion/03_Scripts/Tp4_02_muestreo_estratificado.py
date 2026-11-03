# -*- coding: utf-8 -*-
"""
Tp4_02_muestreo_estratificado.py   [SE CORRE]   Tp4, paso 6 de la guia
==============================================================
Disena el muestreo aleatorio ESTRATIFICADO por clase del mapa que se va a
evaluar y deja los puntos listos para etiquetar AL AZAR en QGIS.

POR QUE ASI (Olofsson et al., 2014: buenas practicas de exactitud y area)
  - Estratificado por clase del mapa: asegura muestras en las clases raras
    (el area quemada o inundada suele ser el 1 a 10 % del sitio).
  - Aleatorio dentro de cada estrato: permite estimar area e incertidumbre
    con formulas conocidas; un muestreo "a ojo" no lo permite.
  - Al azar y sin ver el mapa: el archivo que se etiqueta NO trae la clase del mapa. Quien
    etiqueta mira solo la imagen de referencia. La clase del mapa queda en
    un archivo aparte (la "llave") que se une recien en Tp4_03.

TAMANO DE LA MUESTRA
  n = ( sum_i W_i * S_i / S_O )^2      (Olofsson et al., 2014, ec. 13)
  con W_i = proporcion de superficie de la clase i en el mapa, S_i = desvio
  esperado de la clase (raiz de U_i (1 - U_i), con U_i = exactitud del usuario
  que se espera) y S_O = error estandar buscado para la exactitud global.
  Despues se reparte: al menos --minimo puntos por clase y el resto en
  proporcion al area (un reparto intermedio entre el igual y el proporcional,
  como sugieren Olofsson et al., 2014).

  Valores por defecto del curso: U = 0,85, S_O = 0,03 y minimo 30 por clase.
  Para dos clases dan unos 140 puntos por mapa, que un grupo etiqueta en una
  hora repartiendose el trabajo. Con S_O = 0,01 (lo que se usaria en un
  trabajo de investigacion) son mas de 1.000 puntos: se dice en el informe
  que intervalo de confianza permite la muestra que se pudo etiquetar.

ENTRADA  el mapa de clases (GeoTIFF de enteros; 0 o sin dato = fuera)
SALIDA
  Tp4_Validacion/04_Tablas_de_trabajo/<NOMBRE>_puntos_a_etiquetar.gpkg  (capa "puntos": id, clase_ref vacia)
  Tp4_Validacion/04_Tablas_de_trabajo/<NOMBRE>_llave_NO_ABRIR.csv        (id, clase_mapa)
  Tp4_Validacion/05_Resultados/04_Tablas/<NOMBRE>_diseno_muestral.csv   (W_i, n_i por estrato)

USO
    python Tp4_02_muestreo_estratificado.py --mapa ..\\..\\Tp5_Incendios\\05_Resultados\\02_Rasters\\A1_variante_multisensor.tif --banda 1
    opciones: --UA 0.85 --SE 0.03 --minimo 30 --semilla 2026
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

from configuracion_comun import ruta_tp                               # noqa: E402
from funciones_comunes import Bitacora                                # noqa: E402


def main():
    import geopandas as gpd
    import rasterio

    ap = argparse.ArgumentParser()
    ap.add_argument("--mapa", required=True)
    ap.add_argument("--banda", type=int, default=1)
    ap.add_argument("--UA", type=float, default=0.85, help="exactitud del usuario esperada")
    ap.add_argument("--SE", type=float, default=0.03, help="error estandar buscado de la exactitud global")
    ap.add_argument("--minimo", type=int, default=30)
    ap.add_argument("--semilla", type=int, default=2026)
    ap.add_argument("--sobrescribir", action="store_true",
                    help="reescribir los puntos aunque ya tengan etiquetas (borra el trabajo hecho)")
    a = ap.parse_args()
    nombre = os.path.splitext(os.path.basename(a.mapa))[0]
    log = Bitacora(ruta_tp("Tp4", "05_Resultados", "06_Control_calidad"), "Tp4_02_%s" % nombre)

    with rasterio.open(a.mapa) as src:
        m = src.read(a.banda)
        T, crs = src.transform, src.crs
        nd = src.nodata
    m = np.where(np.isfinite(m), m, 0)
    if nd is not None:
        m = np.where(m == nd, 0, m)
    m = m.astype("int64")
    clases, cuenta = np.unique(m[m > 0], return_counts=True)
    if clases.size < 2:
        sys.exit("El mapa tiene %d clase(s): para validar hacen falta al menos dos." % clases.size)
    W = cuenta / cuenta.sum()
    Si = np.sqrt(a.UA * (1 - a.UA))
    n_formula = int(np.ceil(round((np.sum(W * Si) / a.SE) ** 2, 6)))
    n_total = max(n_formula, a.minimo * clases.size)
    # Reparto: el minimo para cada clase y el resto en proporcion al area.
    resto = n_total - a.minimo * clases.size
    n_i = a.minimo + np.round(W * resto).astype(int)
    n_i = np.minimum(n_i, cuenta)          # no mas puntos que pixeles

    log("Mapa: %s (banda %d), pixel %.0f m" % (a.mapa, a.banda, T.a))
    log("Formula: n = (sum W_i S_i / S_O)^2 con U = %.2f y S_O = %.3f  ->  n = %d" % (a.UA, a.SE, n_formula))
    if n_total > n_formula:
        log("Minimo: %d puntos x %d clases = %d > %d: manda el minimo, n = %d"
            % (a.minimo, clases.size, a.minimo * clases.size, n_formula, n_total))
    else:
        log("Minimo: %d puntos x %d clases = %d <= %d: manda la formula, n = %d"
            % (a.minimo, clases.size, a.minimo * clases.size, n_formula, n_total))
    diseno = pd.DataFrame({"clase_mapa": clases, "pixeles": cuenta, "W_i": W.round(5),
                           "superficie_ha": (cuenta * T.a * abs(T.e) / 1e4).round(1), "n_i": n_i})
    log(diseno.to_string(index=False))
    # El redondeo del reparto puede hacer que la suma de n_i no coincida con n_total: se informa.
    log("Suma de n_i = %d (n_total = %d)%s" % (int(n_i.sum()), n_total,
        "" if int(n_i.sum()) == n_total else ": la diferencia viene del redondeo del reparto"))

    rng = np.random.default_rng(a.semilla)
    filas = []
    for c, n in zip(clases, n_i):
        f, col = np.nonzero(m == c)
        elegidos = rng.choice(f.size, size=n, replace=False)
        for k in elegidos:
            x, y = T * (col[k] + 0.5, f[k] + 0.5)
            filas.append({"x": x, "y": y, "clase_mapa": int(c)})
    pts = pd.DataFrame(filas).sample(frac=1.0, random_state=a.semilla).reset_index(drop=True)
    pts.insert(0, "id", np.arange(1, len(pts) + 1))
    carpeta = ruta_tp("Tp4", "04_Tablas_de_trabajo")
    os.makedirs(carpeta, exist_ok=True)
    ciego = gpd.GeoDataFrame({"id": pts.id, "clase_ref": pd.Series([None] * len(pts), dtype="object"),
                              "confianza": pd.Series([None] * len(pts), dtype="object"),
                              "imagen_usada": pd.Series([None] * len(pts), dtype="object"),
                              "observacion": pd.Series([None] * len(pts), dtype="object")},
                             geometry=gpd.points_from_xy(pts.x, pts.y), crs=crs)
    gp = os.path.join(carpeta, "%s_puntos_a_etiquetar.gpkg" % nombre)
    if os.path.exists(gp) and not a.sobrescribir:
        try:
            previo = gpd.read_file(gp, layer="puntos")
            etiquetados = int(previo.clase_ref.notna().sum())
        except Exception:                            # noqa: BLE001
            etiquetados = -1
        if etiquetados != 0:
            log("YA EXISTE %s con %s puntos etiquetados: NO se reescribe." % (gp, etiquetados if etiquetados >= 0 else "?"))
            log("Si de verdad quiere un muestreo nuevo, copie antes ese archivo y corra con --sobrescribir.")
            log.cerrar()
            return
    ciego.to_file(gp, layer="puntos", driver="GPKG")
    llave = os.path.join(carpeta, "%s_llave_NO_ABRIR.csv" % nombre)
    pts[["id", "clase_mapa"]].to_csv(llave, index=False, encoding="utf-8-sig")
    tab = ruta_tp("Tp4", "05_Resultados", "04_Tablas", "%s_diseno_muestral.csv" % nombre)
    os.makedirs(os.path.dirname(tab), exist_ok=True)
    diseno.to_csv(tab, index=False, encoding="utf-8-sig")
    log("")
    log("Puntos a etiquetar (SIN la clase del mapa): %s  (%d puntos, orden aleatorio)" % (gp, len(pts)))
    log("Llave (no abrir hasta terminar de etiquetar): %s" % llave)
    log("En QGIS: abrir el GeoPackage, ocultar el mapa evaluado, mirar SOLO la imagen de referencia")
    log("y completar clase_ref (el mismo codigo de clases del mapa), confianza (alta/media/baja),")
    log("imagen_usada y observacion.")
    log.cerrar("python Tp4_03_exactitud_y_area.py --nombre %s" % nombre)


if __name__ == "__main__":
    main()
