# -*- coding: utf-8 -*-
"""
Tp7_01_pares_insar_C.py   [SE CORRE]   Tp7, paso 1 de la guia - interferometria en banda C
==================================================================================
Pregunta del practico: hay deformacion previa en la ladera, y con que MDE se
podria medir el volumen movilizado. Sitio: E1_DIAMANTE_BARRANCA (barranca del rio Parana en Diamante).

La banda X ya esta en el archivo del curso (COSMO-SkyMed de octubre de 2018,
par interferometrico 15/10-19/10 procesado en SNAP; ver la guia, paso 2). Este
programa agrega la banda C con Sentinel-1, por dos caminos:

  A) BUSCAR pares SLC de una misma orbita sobre el sitio y LISTARLOS con su
     separacion temporal y su linea de base perpendicular (asf_search). Con
     ese listado se procesa el par en SNAP (TOPS: Split, Orbita, Back-
     Geocoding, ESD, Interferograma, Deburst, Topographic Phase Removal,
     Goldstein, SNAPHU, Phase to Displacement, Terrain Correction).
  B) PEDIR el par al servicio HyP3 de ASF (procesador GAMMA), que devuelve
     interferograma desenrollado, coherencia y desplazamiento en la linea de
     vision y vertical, en GeoTIFF, sin procesar nada localmente.
     Requiere cuenta de NASA Earthdata y consume creditos gratuitos de HyP3.

Criterios para elegir el par (se escriben en la bitacora)
  - separacion temporal corta (6 a 24 dias): mas coherencia. En 2018 volaban
    Sentinel-1A y 1B, pero sobre Diamante solo hay adquisiciones cada 12 dias
    (orbita 141, descendente);
  - linea de base perpendicular chica (< 150 m): menos fase topografica residual;
  - misma orbita relativa y misma pasada.
  Si en una misma fecha hay dos escenas contiguas de la misma pasada (dos cuadros
  a lo largo de la orbita), se queda la que mas cubre el sitio: asi no aparecen
  pares de 0 dias, que no son interferogramas.

SALIDA
  Tp7_Barrancas_deslizamientos/05_Resultados/04_Tablas/E1_pares_S1.csv
  (con --hyp3) descargas en ORIGINALES\\HYP3\\E1_DIAMANTE_BARRANCA\\

POR QUE OCTUBRE DE 2018 POR DEFECTO
  El par en banda X (COSMO-SkyMed) es del 15 y 19 de octubre de 2018, cuando se
  relevaron las grietas de la barranca. Para COMPARAR o FUSIONAR las dos bandas
  tienen que mirar el MISMO periodo: por eso la busqueda en C empieza alli.
  Para ver si la deformacion sigue hoy, se corre otra vez con fechas recientes
  (y eso ya no es fusion con la banda X: es otra pregunta).

USO
    python Tp7_01_pares_insar_C.py
    python Tp7_01_pares_insar_C.py --hyp3 1
    python Tp7_01_pares_insar_C.py --desde 2025-01-01 --hasta 2026-09-30
          (--hyp3 N pide los N mejores pares)
"""
import argparse
import os
import sys
import time

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import pandas as pd                                                   # noqa: E402
from shapely.geometry import box                                      # noqa: E402

from configuracion_comun import SITIOS, ORIGINALES, ruta_tp           # noqa: E402
from funciones_comunes import Bitacora                                # noqa: E402

SITIO = "E1_DIAMANTE_BARRANCA"


def main():
    import asf_search as asf
    try:                                              # CMR a veces tarda mas de 30 s
        asf.constants.INTERNAL.CMR_TIMEOUT = 120
    except AttributeError:
        pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", default="2018-09-15")
    ap.add_argument("--hasta", default="2018-11-15")
    ap.add_argument("--dias_max", type=int, default=24)
    ap.add_argument("--base_max", type=float, default=150.0)
    ap.add_argument("--hyp3", type=int, default=0)
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp7", "05_Resultados", "06_Control_calidad"), "Tp7_01_pares")
    caja = box(*SITIOS[SITIO]["bbox"])
    res = None
    for intento in range(1, 4):
        try:
            res = asf.search(platform="SENTINEL-1", processingLevel="SLC", beamMode="IW",
                             intersectsWith=caja.wkt, start=a.desde, end=a.hasta + "T23:59:59Z", maxResults=1000)
            break
        except Exception as e:                       # noqa: BLE001
            log("El catalogo de ASF/CMR no respondio (%s), intento %d de 3" % (str(e)[:90], intento))
            if intento < 3:
                time.sleep(30 * intento)
    if res is None:
        log("ASF no respondio. Vuelva a correr mas tarde; no se escribio E1_pares_S1.csv.")
        log.cerrar()
        sys.exit(1)
    log("Criterios: misma orbita relativa y pasada; separacion <= %d dias; linea de base perpendicular <= %.0f m;"
        % (a.dias_max, a.base_max))
    log("           una escena por fecha (la que mas cubre el sitio); pares de fechas consecutivas.")
    log("Busqueda: %s a %s" % (a.desde, a.hasta))
    log("Escenas SLC sobre el sitio: %d" % len(res))
    if not res:
        log.cerrar()
        return
    from shapely.geometry import shape
    por_orbita = {}
    for r in res:
        por_orbita.setdefault((r.properties["pathNumber"], r.properties["flightDirection"]), []).append(r)
    # una escena por fecha y orbita: la que mas cubre el sitio (evita pares de 0 dias entre cuadros contiguos)
    for clave, lista in list(por_orbita.items()):
        por_fecha = {}
        for r in lista:
            f = str(pd.Timestamp(r.properties["startTime"]).date())
            try:
                cub = shape(r.geometry).intersection(caja).area / caja.area
            except Exception:                        # noqa: BLE001
                cub = 0.0
            if f not in por_fecha or cub > por_fecha[f][0]:
                por_fecha[f] = (cub, r)
        if len(por_fecha) < len(lista):
            log("Orbita relativa %s (%s): %d escenas en %d fechas; se queda una por fecha"
                % (clave[0], clave[1].lower(), len(lista), len(por_fecha)))
        por_orbita[clave] = [v[1] for v in por_fecha.values()]
    filas = []
    for (orb, pas), lista in sorted(por_orbita.items(), key=lambda kv: -len(kv[1])):
        lista.sort(key=lambda r: r.properties["startTime"])
        log("Orbita relativa %s (%s): %d escenas" % (orb, pas.lower(), len(lista)))
        # linea de base respecto de la primera escena de la orbita (pila de ASF)
        try:
            pila = lista[0].stack()
            bperp = {p.properties["sceneName"]: p.properties.get("perpendicularBaseline") for p in pila}
        except Exception as e:                       # noqa: BLE001
            log("   no se pudo pedir la pila de lineas de base (%s)" % str(e)[:80])
            bperp = {}
        for i in range(len(lista) - 1):
            r1, r2 = lista[i], lista[i + 1]
            t1, t2 = pd.Timestamp(r1.properties["startTime"]), pd.Timestamp(r2.properties["startTime"])
            dias = (t2 - t1).days
            b1, b2 = bperp.get(r1.properties["sceneName"]), bperp.get(r2.properties["sceneName"])
            bp = abs(b2 - b1) if (b1 is not None and b2 is not None) else None
            ok = dias <= a.dias_max and (bp is None or bp <= a.base_max)
            if dias < 1:
                continue
            filas.append({"orbita": orb, "pasada": pas.lower(), "fecha_1": str(t1.date()), "fecha_2": str(t2.date()),
                          "dias": dias, "base_perpendicular_m": round(bp, 1) if bp is not None else float("nan"),
                          "apto": "si" if ok else "no", "escena_1": r1.properties["sceneName"],
                          "escena_2": r2.properties["sceneName"]})
    columnas = ["orbita", "pasada", "fecha_1", "fecha_2", "dias", "base_perpendicular_m", "apto", "escena_1",
                "escena_2"]
    t = pd.DataFrame(filas, columns=columnas)
    out = ruta_tp("Tp7", "05_Resultados", "04_Tablas", "E1_pares_S1.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    t.to_csv(out, index=False, encoding="utf-8-sig")
    aptos = t[t.apto == "si"].sort_values(["dias", "base_perpendicular_m"], na_position="last")
    sin_base = int(t.base_perpendicular_m.isna().sum())
    if sin_base:
        log("AVISO: %d par(es) sin linea de base (ASF no devolvio la pila): se juzgan solo por los dias." % sin_base)
    log("Pares consecutivos: %d; aptos (<= %d dias y <= %.0f m): %d" % (len(t), a.dias_max, a.base_max, len(aptos)))
    if len(aptos):
        log(aptos.head(10)[["orbita", "pasada", "fecha_1", "fecha_2", "dias", "base_perpendicular_m"]]
            .to_string(index=False))
    else:
        log("Ningun par cumple los criterios: amplie --desde/--hasta o --dias_max.")

    if a.hyp3 and len(aptos):
        import hyp3_sdk as sdk

        log.titulo("Pedido de %d par(es) a HyP3 (INSAR_GAMMA, 10x2 looks)" % a.hyp3)
        hyp3 = sdk.HyP3(prompt="password")      # usa .netrc si existe; si no, pregunta
        lote = sdk.Batch()
        for _, p in aptos.head(a.hyp3).iterrows():
            lote += hyp3.submit_insar_job(p.escena_1, p.escena_2, name="Tp7_E1_%s_%s" % (p.fecha_1, p.fecha_2),
                                          looks="10x2", include_displacement_maps=True,
                                          include_inc_map=True, apply_water_mask=True)
            log("   pedido: %s - %s" % (p.fecha_1, p.fecha_2))
        log("Esperando a HyP3 (puede tardar de 30 minutos a algunas horas)...")
        lote = hyp3.watch(lote)
        destino = os.path.join(ORIGINALES, "HYP3", SITIO)
        os.makedirs(destino, exist_ok=True)
        lote.download_files(destino)
        log("Descargado en %s (descomprimir los .zip: traen *_corr.tif, *_unw_phase.tif, *_los_disp.tif, *_vert_disp.tif)" % destino)
    log.cerrar("python Tp7_02_coherencia_y_deformacion.py")


if __name__ == "__main__":
    main()
