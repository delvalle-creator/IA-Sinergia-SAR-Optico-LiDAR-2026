# -*- coding: utf-8 -*-
"""
Tp2_05_saocom_por_cubierta.py   [SE CORRE, PARA PROFUNDIZAR]   Tp2, paso 8 (bloque SAOCOM)
=========================================================================================
Lee el SAOCOM-1A cuadripolar del 24/09/2026 (HH, HV, VV en gamma0 sobre el
elipsoide, 20 m; 02_Subsets_SNAP_QGIS/SAOCOM_gamma0/QGIS_GeoTIFF) y calcula, por
clase de cubiertas_<SITIO>.gpkg, la media de cada polarizacion (en LINEAL,
informada en dB), la diferencia HH - VV y la diferencia HH - HV.

Para que sirve: con las cuatro polarizaciones en intensidad se puede PROPONER el
mecanismo de dispersion compatible con cada cubierta:
  - superficie lisa o rugosa: HH parecido a VV y cruzada muy baja;
  - volumen (copas, ramas): cruzada alta, HH - HV chico;
  - doble rebote (paredes, troncos sobre agua): HH bastante mayor que VV.
Pero la intensidad NO alcanza para confirmarlo: la confirmacion del doble rebote
es la diferencia de FASE HH - VV cercana a 180 grados, que exige el producto
complejo (SLC) y una descomposicion polarimetrica (Pauli), fuera del alcance de
este practico.

Banda de ruido: en este producto los 2 a 3 km del borde este de la franja son
ruido del extremo del haz (una banda casi negra que no es agua). Se excluyen
los poligonos cuyo centro queda al este de X_RUIDO (metros, UTM 21 S), el lugar
donde la mediana de HV por columna cae por debajo de -24 dB.

SALIDA
  Tp2_SAR_multibanda/05_Resultados/04_Tablas/<SITIO>_SAOCOM_cuadripolar_por_clase.csv

USO
    python Tp2_05_saocom_por_cubierta.py --sitio A2_IBICUY
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

from configuracion_comun import SITIOS, ruta_tp                       # noqa: E402
from funciones_comunes import media_lineal_db, Bitacora               # noqa: E402

# ------------------------------------------------------------------ parametros
PRODUCTO = "%s_SAOCOM_L_20260924_QP_gamma0_Gamma0_%s.tif"
X_RUIDO = 299400.0        # m (UTM 21 S): al este empieza la banda de ruido del borde del haz
ORDEN = ["agua_calma", "agua_rizada", "pajonal", "suelo_desnudo", "cultivo", "monte_o_bosque", "urbano", "estable"]


def main():
    import geopandas as gpd
    import rasterio
    from rasterio.mask import mask

    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", required=True, choices=list(SITIOS.keys()))
    ap.add_argument("--x_ruido", type=float, default=X_RUIDO,
                    help="coordenada este (m) desde la que empieza la banda de ruido")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp2", "05_Resultados", "06_Control_calidad"), "Tp2_05_%s" % a.sitio)

    carpeta = ruta_tp("Tp2", "02_Subsets_SNAP_QGIS", "SAOCOM_gamma0", "QGIS_GeoTIFF")
    rutas = {p: os.path.join(carpeta, PRODUCTO % (a.sitio, p)) for p in ("HH", "HV", "VV")}
    faltan = [r for r in rutas.values() if not os.path.exists(r)]
    if faltan:
        log("No encuentro el SAOCOM del sitio: %s" % "; ".join(faltan))
        log.cerrar()
        return
    vec = ruta_tp("Tp2", "04_Tablas_de_trabajo", "cubiertas_%s.gpkg" % a.sitio)
    pol = gpd.read_file(vec, layer="cubiertas")
    pol["n_pol"] = pol.groupby("clase").cumcount() + 1
    fuentes = {p: rasterio.open(r) for p, r in rutas.items()}
    pol = pol.to_crs(fuentes["HH"].crs)

    datos = {}
    for _, r in pol.iterrows():
        nombre = "%s %d" % (r.clase, r.n_pol)
        if r.geometry.centroid.x >= a.x_ruido:
            log("%-18s queda en la banda de ruido del borde este: no se usa." % nombre)
            continue
        vals = {}
        for p, s in fuentes.items():
            arr, _ = mask(s, [r.geometry], crop=True, filled=False)
            v = arr[0].compressed()
            vals[p] = v[np.isfinite(v) & (v > 0)].astype("float64")
        if vals["HH"].size == 0:
            log("%-18s sin dato de SAOCOM (fuera de la franja)." % nombre)
            continue
        datos.setdefault(r.clase, []).append(vals)

    filas = []
    for c in [x for x in ORDEN if x in datos] + sorted(x for x in datos if x not in ORDEN):
        m = {p: media_lineal_db(np.concatenate([v[p] for v in datos[c]])) for p in ("HH", "HV", "VV")}
        filas.append({"clase": c, "n_poligonos": len(datos[c]),
                      "n_pixeles_20m": int(sum(v["HH"].size for v in datos[c])),
                      "HH_dB": round(float(m["HH"]), 1), "HV_dB": round(float(m["HV"]), 1),
                      "VV_dB": round(float(m["VV"]), 1),
                      "HH_menos_VV_dB": round(float(m["HH"] - m["VV"]), 1),
                      "HH_menos_HV_dB": round(float(m["HH"] - m["HV"]), 1)})
    t = pd.DataFrame(filas)
    log.titulo("SAOCOM-1A cuadripolar, 24/09/2026: media por clase (dB, promediada en lineal)")
    log(t.to_string(index=False))
    out = ruta_tp("Tp2", "05_Resultados", "04_Tablas", "%s_SAOCOM_cuadripolar_por_clase.csv" % a.sitio)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    t.to_csv(out, index=False, encoding="utf-8-sig")
    log("")
    log("Tabla:", out)
    log("Recuerde: HH - VV alto es COMPATIBLE con doble rebote; confirmarlo exige la fase HH - VV (producto complejo).")
    log.cerrar("responder las preguntas del Tp2")


if __name__ == "__main__":
    main()
