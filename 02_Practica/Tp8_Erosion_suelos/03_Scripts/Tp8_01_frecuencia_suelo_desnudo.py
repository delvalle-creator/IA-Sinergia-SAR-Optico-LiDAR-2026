# -*- coding: utf-8 -*-
"""
Tp8_01_frecuencia_suelo_desnudo.py   [SE CORRE]   Tp8, paso 1 de la guia - Erosion de suelos
===================================================================================
Pregunta del practico: donde hay suelo expuesto de forma persistente y que parte
de el muestra erosion visible. Sitio: F_BOVRIL (centro de Entre Rios).

Paso 1, con el optico: frecuencia de suelo desnudo en la serie optica (meses
por ano). Guia teorico-practica general, seccion 11.2.

Para cada FECHA Sentinel-2 L2A del ano, solo en los pixeles sin nube (SCL):
    NDVI = (B08 - B04) / (B08 + B04)
    BSI  = ((B11 + B04) - (B08 + B02)) / ((B11 + B04) + (B08 + B02))   indice de suelo desnudo
y un pixel se considera SUELO DESNUDO si NDVI < --ndvi_max (0,25) y BSI > --bsi_min (0).
Despues, por MES: el mes cuenta como "desnudo" si la mayoria de las
observaciones validas de ese mes lo fueron. Resultado: meses por ano con suelo
desnudo, y cuantos meses tuvieron al menos una observacion valida.

UNA FECHA, UN VOTO (corregido el 27/10/2026). El catalogo trae muchas fechas dos
veces: dos versiones de procesamiento del mismo dia y la misma tesela (por
ejemplo ..._20230104T022310 y ..._20240809T095959). Antes de contar se deja una
sola por fecha y tesela: la de linea de base de procesamiento (s2:processing_baseline)
mas alta y, si empatan, la procesada mas tarde. Asi una fecha repetida no pesa
el doble en la mayoria del mes. La bitacora informa entradas del catalogo,
versiones descartadas y fechas distintas.

UMBRALES CON HISTOGRAMA (regla 6 del proyecto). Para la fecha --fecha_histograma
(por defecto 2023-11-07, con mucho suelo desnudo) se guardan los histogramas de
NDVI y de BSI con la linea de cada umbral en 05_Resultados/05_Graficos.

SIN INTERNET (--local). Con --local se leen las escenas ya bajadas a
00_COMUN/08_Originales_crudos/PLANETARY/F_BOVRIL/sentinel-2-l2a (una carpeta por
fecha, con B02, B04, B08, B11, SCL e item_STAC.json): el paso corre en minutos.
Esa copia trae solo las fechas con el sitio casi entero despejado; las pasadas con
nube parcial quedan afuera y la bitacora lo dice.

Lectura: 1 o 2 meses = labranza normal (no es erosion); 6 o mas meses =
suelo expuesto de forma persistente (incluye ciudad, caminos, rastrojo y terrazas:
hay que verificar cada mancha en la imagen de 2 m).

SALIDA
  Tp8_Erosion_suelos/02_Subsets_SNAP_QGIS/F_frecuencia_suelo_desnudo_<anio>_<pixel>m.tif
  Tp8_Erosion_suelos/05_Resultados/04_Tablas/F_escenas_opticas_<anio>.csv
  Tp8_Erosion_suelos/05_Resultados/05_Graficos/F_histograma_NDVI_<fecha>.png y F_histograma_BSI_<fecha>.png

USO
    python Tp8_01_frecuencia_suelo_desnudo.py --anio 2023 --pixel 10 --nubes_max 60
    python Tp8_01_frecuencia_suelo_desnudo.py --anio 2023 --local        (sin internet)
"""
import argparse
import glob
import json
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import ruta_tp, ORIGINALES                   # noqa: E402
from funciones_comunes import (grilla_sitio, buscar_stac, fecha_item, s2_reflectancia,  # noqa: E402
                               s2_mascara_valida, guardar_tif, Bitacora, fuente_mpc,
                               leer_en_grilla, CLASES_SCL_VALIDAS)
from funciones_cambio import indice_normalizado, umbral_documentado   # noqa: E402

# ----------------------------------------------------------------- PARAMETROS
SITIO = "F_BOVRIL"
UTIL_MINIMO = 0.20          # se descarta la fecha si menos del 20 % del sitio esta despejado
FECHA_HISTOGRAMA = "2023-11-07"


# ------------------------------------------------------------ lectura local
class EscenaLocal:
    """Una fecha Sentinel-2 bajada a disco (carpeta con B02.tif ... SCL.tif e item_STAC.json)."""

    def __init__(self, carpeta):
        self.carpeta = carpeta
        nombre = os.path.basename(carpeta)           # 20230103_S2A_MSIL2A_20230103T134701_R024_T21JTF_20240809T095959
        d = {}
        ruta_json = os.path.join(carpeta, "item_STAC.json")
        if os.path.exists(ruta_json):
            with open(ruta_json, encoding="utf-8") as f:
                d = json.load(f)
        self.id = d.get("id", nombre.split("_", 1)[-1])
        self.properties = d.get("properties", {})
        # la fecha de ADQUISICION sale de los metadatos; si falta el json, del nombre del producto
        self.fecha = self.properties.get("datetime", "")[:10] or "%s-%s-%s" % (nombre[:4], nombre[4:6], nombre[6:8])

    def banda(self, b):
        return os.path.join(self.carpeta, b + ".tif")


def escenas_locales(anio):
    base = os.path.join(ORIGINALES, "PLANETARY", SITIO, "sentinel-2-l2a")
    carpetas = sorted(c for c in glob.glob(os.path.join(base, "%d*" % anio)) if os.path.isdir(c))
    return [EscenaLocal(c) for c in carpetas if os.path.exists(os.path.join(c, "SCL.tif"))], base


def reflectancia_local(esc, b, g):
    dn = leer_en_grilla(esc.banda(b), g, "average", nodata_origen=0)
    # linea de base 04.00 o posterior (todas las de 2023): se descuenta el +1000 de los DN
    lb = float(esc.properties.get("s2:processing_baseline", "4.0") or 4.0)
    return (dn - (1000.0 if lb >= 4.0 else 0.0)) / 10000.0


def valida_local(esc, g):
    scl = leer_en_grilla(esc.banda("SCL"), g, "nearest", nodata_origen=0)
    scl = np.nan_to_num(scl, nan=0).astype("uint8")
    return np.isin(scl, CLASES_SCL_VALIDAS)


# --------------------------------------------------- una version por fecha
def _clave_version(props, ident):
    """Linea de base de procesamiento y fecha de proceso (la ultima parte del id)."""
    try:
        lb = float(props.get("s2:processing_baseline"))
    except (TypeError, ValueError):
        lb = 0.0
    return lb, ident.split("_")[-1]


def una_version_por_fecha(items, fecha_de, props_de, id_de, tesela_de):
    """Deja una sola entrada por (fecha, tesela): la de linea de base mas alta y la procesada mas tarde."""
    elegidas = {}
    for it in items:
        k = (fecha_de(it), tesela_de(it))
        if k not in elegidas or _clave_version(props_de(it), id_de(it)) > _clave_version(props_de(elegidas[k]), id_de(elegidas[k])):
            elegidas[k] = it
    quedan = set(id(v) for v in elegidas.values())
    return [it for it in items if id(it) in quedan], [it for it in items if id(it) not in quedan]


def main():
    ap = argparse.ArgumentParser(description="Meses del ano con suelo desnudo en la serie Sentinel-2.")
    ap.add_argument("--anio", type=int, default=2023)
    ap.add_argument("--pixel", type=float, default=10.0)
    ap.add_argument("--nubes_max", type=float, default=60.0, help="nubosidad de catalogo de la tesela (solo preselecciona)")
    ap.add_argument("--ndvi_max", type=float, default=0.25, help="suelo desnudo si NDVI < este valor")
    ap.add_argument("--bsi_min", type=float, default=0.0, help="suelo desnudo si BSI > este valor")
    ap.add_argument("--local", action="store_true", help="leer las escenas ya bajadas a 08_Originales_crudos (sin internet)")
    ap.add_argument("--fecha_histograma", default=FECHA_HISTOGRAMA, help="fecha para los histogramas de NDVI y BSI")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp8", "05_Resultados", "06_Control_calidad"), "Tp8_01_suelo_desnudo")
    g = grilla_sitio(SITIO, pixel=a.pixel)

    if a.local:
        todas, base = escenas_locales(a.anio)
        log("Modo LOCAL (sin internet): %d fechas Sentinel-2 %d en %s" % (len(todas), a.anio, base))
        log("La copia local trae solo las fechas con el sitio casi entero despejado: las pasadas con nube")
        log("parcial no estan, y el resultado puede diferir un poco del de la corrida con el Planetary Computer.")
        fecha_de, props_de, id_de = (lambda e: e.fecha), (lambda e: e.properties), (lambda e: e.id)
    else:
        todas = buscar_stac("sentinel-2-l2a", SITIO, "%d-01-01" % a.anio, "%d-12-31" % a.anio,
                            query={"eo:cloud_cover": {"lt": a.nubes_max}})
        log("Escenas Sentinel-2 %d con menos de %.0f %% de nubes de catalogo: %d" % (a.anio, a.nubes_max, len(todas)))
        fecha_de, props_de, id_de = (lambda it: fecha_item(it)[0]), (lambda it: it.properties), (lambda it: it.id)
    tesela_de = lambda it: props_de(it).get("s2:mgrs_tile", id_de(it).split("_")[5] if len(id_de(it).split("_")) > 5 else "")  # noqa: E731
    items, repetidas = una_version_por_fecha(todas, fecha_de, props_de, id_de, tesela_de)
    log("Versiones de procesamiento repetidas que se descartan: %d (queda una por fecha y tesela)" % len(repetidas))
    log("Fechas distintas: %d" % len(set(fecha_de(it) for it in items)))

    meses_desn = np.zeros((12, g["height"], g["width"]), dtype="float32")
    meses_obs = np.zeros_like(meses_desn)
    filas = [{"fecha": fecha_de(it), "id": id_de(it), "util_%": np.nan, "usada": "no (version repetida)"} for it in repetidas]
    for it in items:
        f = fecha_de(it)
        if a.local:
            v = valida_local(it, g)
        else:
            v, cob, nub = s2_mascara_valida(it, g)
        if v.mean() < UTIL_MINIMO:
            filas.append({"fecha": f, "id": id_de(it), "util_%": round(100 * v.mean(), 1), "usada": "no"})
            continue
        if a.local:
            b2, b4, b8, b11 = (reflectancia_local(it, b, g) for b in ("B02", "B04", "B08", "B11"))
        else:
            b2, b4, b8, b11 = (s2_reflectancia(it, b, g) for b in ("B02", "B04", "B08", "B11"))
        ndvi = indice_normalizado(b8, b4)
        bsi = indice_normalizado(b11 + b4, b8 + b2)
        desn = (ndvi < a.ndvi_max) & (bsi > a.bsi_min) & v
        if f == a.fecha_histograma:
            for x, nom, u, signo in ((ndvi, "NDVI", a.ndvi_max, "<"), (bsi, "BSI", a.bsi_min, ">")):
                _, txt = umbral_documentado(x[v], "%s %s" % (nom, f),
                                            ruta_tp("Tp8", "05_Resultados", "05_Graficos", "F_histograma_%s_%s.png" % (nom, f)),
                                            metodo="manual", manual=u, signo=signo)
                log("Histograma %s del %s: %s" % (nom, f, txt))
        m = int(f[5:7]) - 1
        meses_desn[m] += desn
        meses_obs[m] += v
        filas.append({"fecha": f, "id": id_de(it), "util_%": round(100 * v.mean(), 1), "usada": "si",
                      "desnudo_%_del_util": round(100 * desn.sum() / max(v.sum(), 1), 1)})
        log("  %s  util %5.1f %%  suelo desnudo %5.1f %% de lo util" % (f, 100 * v.mean(), filas[-1]["desnudo_%_del_util"]))
    con_obs = meses_obs > 0
    mes_desnudo = np.where(con_obs, (meses_desn / np.where(con_obs, meses_obs, 1)) > 0.5, False)
    freq = mes_desnudo.sum(axis=0).astype("float32")
    n_meses = con_obs.sum(axis=0).astype("float32")
    freq = np.where(n_meses > 0, freq, np.nan)
    usadas = sum(fl["usada"] == "si" for fl in filas)
    fuente = ("ESA - Copernicus. Sentinel-2 MSI L2A, %d fechas de %d (copia local de 08_Originales_crudos)." % (usadas, a.anio)
              if a.local else fuente_mpc("ESA - Copernicus", "Sentinel-2 MSI L2A, %d fechas" % usadas, str(a.anio)))
    guardar_tif(ruta_tp("Tp8", "02_Subsets_SNAP_QGIS", "F_frecuencia_suelo_desnudo_%d_%dm.tif" % (a.anio, a.pixel)),
                {"meses_suelo_desnudo": freq, "meses_con_observacion": n_meses}, g, fuente,
                "Meses del ano con suelo desnudo (NDVI < %.2f y BSI > %.2f, mayoria de observaciones del mes; "
                "una version por fecha)" % (a.ndvi_max, a.bsi_min))
    t = pd.DataFrame(filas).sort_values(["fecha", "usada"])
    out = ruta_tp("Tp8", "05_Resultados", "04_Tablas", "F_escenas_opticas_%d.csv" % a.anio)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    t.to_csv(out, index=False, encoding="utf-8-sig")
    log("")
    log("Fechas usadas: %d; descartadas por menos del %.0f %% del sitio util: %d"
        % (usadas, 100 * UTIL_MINIMO, sum(fl["usada"] == "no" for fl in filas)))
    log("Meses con observacion valida: mediana %.0f de 12" % np.nanmedian(n_meses))
    observado = np.isfinite(freq)
    log("Pixeles sin ninguna observacion valida en el ano: %.1f %% del sitio (quedan fuera de los porcentajes)"
        % (100 * (1 - observado.mean())))
    for lo, hi, txt in ((0, 0, "nunca desnudo"), (1, 2, "1-2 meses (labranza)"), (3, 5, "3-5 meses"), (6, 12, "6 o mas meses (persistente)")):
        dentro = observado & (np.nan_to_num(freq, nan=-1) >= lo) & (np.nan_to_num(freq, nan=-1) <= hi)
        log("  %-28s %5.1f %% de lo observado (%.1f ha)" % (txt, 100 * dentro.sum() / max(observado.sum(), 1),
                                                         dentro.sum() * a.pixel ** 2 / 1e4))
    log.cerrar("python Tp8_02_textura_S_y_C.py --puntos_enlace todos   (paso 2: medir el desfase de NovaSAR)")


if __name__ == "__main__":
    main()
