# -*- coding: utf-8 -*-
"""
Tp10_04_pares_sbas.py   [AUXILIAR / YA VIENE HECHO]   Tp10, paso 8 de la guía - red de pares de línea de base corta
==============================================================================================
"Subsidencia: serie InSAR en banda C (PS o SBAS)" (presentación 01, diapositiva 33).

Se arma una RED DE PARES DE LÍNEA DE BASE CORTA (en el tiempo y en el espacio, todos de la MISMA
órbita). Con esa red, el paso 10 hace un APILADO DE TASAS (Tp10_05). Una inversión SBAS (Small
BAseline Subset), que resolvería el desplazamiento de cada fecha, no se hace en el curso. Aquí:

  - se buscan todas las escenas Sentinel-1 IW SLC sobre el sitio (asf_search);
  - se elige la órbita relativa con más escenas;
  - cada escena se une con sus --vecinos siguientes (1 = cadena, 2 = red
    redundante), siempre que la separacion sea <= --dias_max;
  - (opcional, --hyp3) se piden los pares a HyP3 de ASF (procesador GAMMA).

El procesamiento de 120 pares lleva horas en HyP3 y varios GB de descarga: por
eso en clase la red YA VIENE HECHA y descargada. Este programa queda para que
el grupo vea como se arma y lo repita en su propio sitio.

PS (Persistent Scatterers) necesita software especifico (StaMPS, SARPROZ) y
una pila de más de 20 SLC co-registrados: se explica, no se hace en el curso.

SALIDA
  Tp10_Impacto_urbano/05_Resultados/04_Tablas/<SITIO>_red_sbas.csv
  Tp10_Impacto_urbano/05_Resultados/05_Graficos/<SITIO>_red_sbas.png   (tiempo - base perpendicular)
  (con --hyp3) productos en ORIGINALES\\HYP3\\<SITIO>\\

USO
    python Tp10_04_pares_sbas.py --sitio E_PARANA_DIAMANTE --desde 2025-01-01 --hasta 2026-09-30
    python Tp10_04_pares_sbas.py ... --hyp3 120         (pide los 120 primeros pares aptos: los de la corrida docente)
"""
import argparse
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import pandas as pd                                                   # noqa: E402
from shapely.geometry import box                                      # noqa: E402

from configuracion_comun import SITIOS, ORIGINALES, ruta_tp           # noqa: E402
from funciones_comunes import Bitacora                                # noqa: E402


def main():
    import asf_search as asf
    try:                                              # CMR a veces tarda más de 30 s
        asf.constants.INTERNAL.CMR_TIMEOUT = 120
    except AttributeError:
        pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", default="E_PARANA_DIAMANTE", choices=["E_PARANA_DIAMANTE", "B_CONCORDIA"])
    ap.add_argument("--desde", default="2025-01-01")
    ap.add_argument("--hasta", default="2026-09-30")
    ap.add_argument("--vecinos", type=int, default=2)
    ap.add_argument("--dias_max", type=int, default=48)
    ap.add_argument("--base_max", type=float, default=150.0)
    ap.add_argument("--orbita", type=int, default=0, help="forzar una órbita relativa")
    ap.add_argument("--hyp3", type=int, default=0, help="pedir a HyP3 los N primeros pares aptos")
    ap.add_argument("--marcar_pedidos", type=int, default=120,
                    help="en la figura, cuántos pares aptos se marcan como pedidos (los de la corrida docente: 120)")
    a = ap.parse_args()
    S = a.sitio
    log = Bitacora(ruta_tp("Tp10", "05_Resultados", "06_Control_calidad"), "Tp10_04_red_%s" % S)
    # el catálogo CMR de NASA a veces tarda más de 30 s: se amplia la espera y se reintenta
    try:
        asf.constants.INTERNAL.CMR_TIMEOUT = 180
    except AttributeError:
        pass
    import time
    for intento in range(1, 4):
        try:
            res = asf.search(platform="SENTINEL-1", processingLevel="SLC", beamMode="IW",
                             intersectsWith=box(*SITIOS[S]["bbox"]).wkt, start=a.desde, end=a.hasta + "T23:59:59Z",
                             maxResults=2000)
            break
        except asf.ASFSearchError as e:
            log("Busqueda en ASF, intento %d de 3: %s" % (intento, str(e)[:90]))
            if intento == 3:
                log("ASF/CMR no responde. Probar más tarde.")
                log.cerrar()
                return
            time.sleep(60)
    log("Escenas SLC sobre %s entre %s y %s: %d" % (S, a.desde, a.hasta, len(res)))
    if not res:
        log.cerrar()
        return
    por = {}
    for r in res:
        por.setdefault((r.properties["pathNumber"], r.properties["flightDirection"]), []).append(r)
    for (o, p), l in sorted(por.items(), key=lambda kv: -len(kv[1])):
        log("  órbita %s %-10s %d escenas" % (o, p.lower(), len(l)))
    if a.orbita:
        claves = [k for k in por if k[0] == a.orbita]
        if not claves:
            sys.exit("La órbita %d no tiene escenas sobre el sitio. Órbitas disponibles: %s"
                     % (a.orbita, ", ".join(str(k[0]) for k in por)))
        clave = claves[0]
    else:
        clave = max(por, key=lambda k: len(por[k]))
    lista = sorted(por[clave], key=lambda r: r.properties["startTime"])
    # una escena por fecha (a veces el sitio cae entre dos cuadros consecutivos)
    unicas = {}
    for r in lista:
        unicas.setdefault(r.properties["startTime"][:10], r)
    lista = list(unicas.values())
    log("Se usa la órbita %s (%s): %d fechas" % (clave[0], clave[1].lower(), len(lista)))
    try:
        bperp = {x.properties["sceneName"]: x.properties.get("perpendicularBaseline") for x in lista[0].stack()}
    except Exception as e:                           # noqa: BLE001
        log("No se pudo pedir la pila de líneas de base (%s)" % str(e)[:80])
        bperp = {}
    if not bperp:
        log("AVISO: sin líneas de base, los pares se eligen solo por separacion temporal (Sentinel-1 tiene")
        log("tubo orbital estrecho, casi siempre < 150 m, pero no se verifico).")
    pilas = {}

    def base_relativa(r1, r2):
        n1 = r1.properties["sceneName"]
        if n1 not in pilas:
            try:
                pilas[n1] = {x.properties["sceneName"]: x.properties.get("perpendicularBaseline") for x in r1.stack()}
            except Exception:                        # noqa: BLE001
                pilas[n1] = {}
        v = pilas[n1].get(r2.properties["sceneName"])
        return abs(v) if v is not None else None

    # pares: cada escena con sus --vecinos siguientes en el tiempo y, además, con sus --vecinos
    # siguientes del MISMO satelite (S1A, S1C, S1D), para que la red no se corte cuando un
    # satelite deja de adquirir o cuando las escenas de distinto satelite caen en otro cuadro
    sat = lambda r: r.properties["sceneName"][:3]                     # noqa: E731
    candidatos = []
    for i, r1 in enumerate(lista):
        sig = lista[i + 1:i + 1 + a.vecinos]
        mismo = [r for r in lista[i + 1:] if sat(r) == sat(r1)][:a.vecinos]
        for r2 in sig + [r for r in mismo if r not in sig]:
            candidatos.append((r1, r2))
    candidatos.sort(key=lambda p: (p[0].properties["startTime"], p[1].properties["startTime"]))
    filas = []
    for r1, r2 in candidatos:
        t1, t2 = pd.Timestamp(r1.properties["startTime"]), pd.Timestamp(r2.properties["startTime"])
        b1, b2 = bperp.get(r1.properties["sceneName"]), bperp.get(r2.properties["sceneName"])
        bp = abs(b2 - b1) if None not in (b1, b2) else None
        if bp is None and bperp:
            # la escena no esta en la pila de la primera fecha (otro satelite o cuadro):
            # se pide la pila de r1 y, si no, la de r2 (bases referidas a esa escena)
            bp = base_relativa(r1, r2)
            if bp is None:
                bp = base_relativa(r2, r1)
        dias_ok = (t2 - t1).days <= a.dias_max
        if bp is not None:
            ok, nota = dias_ok and bp <= a.base_max, ""
        elif not bperp or sat(r1) == sat(r2):
            # ASF no da base (p. ej. Sentinel-1D, aun sin líneas de base en el catálogo): para el
            # mismo satelite se acepta por el tubo orbital estrecho de Sentinel-1 (< 150 m)
            ok, nota = dias_ok, "sin base en ASF; mismo satelite"
        else:
            ok, nota = False, "sin base en ASF; satelites distintos"
        filas.append({"fecha_1": str(t1.date()), "fecha_2": str(t2.date()), "dias": (t2 - t1).days,
                      "base_perpendicular_m": round(bp, 1) if bp is not None else "",
                      "b1": b1, "b2": b2, "apto": "si" if ok else "no", "nota": nota,
                      "escena_1": r1.properties["sceneName"], "escena_2": r2.properties["sceneName"]})
    t = pd.DataFrame(filas)
    aptos = t[t.apto == "si"]
    log("Pares de la red: %d; aptos (<= %d días, <= %.0f m): %d" % (len(t), a.dias_max, a.base_max, len(aptos)))
    log("  de ellos sin base en ASF (mismo satelite, aceptados por tiempo): %d"
        % (aptos.nota == "sin base en ASF; mismo satelite").sum())
    # conectividad: el apilado necesita una sola red que una todas las fechas
    padre = {}

    def raiz(x):
        padre.setdefault(x, x)
        while padre[x] != x:
            x = padre[x]
        return x
    for _, p in aptos.iterrows():
        padre[raiz(p.fecha_1)] = raiz(p.fecha_2)
    todas = [x.properties["startTime"][:10] for x in lista]
    sueltas = [f for f in todas if f not in set(aptos.fecha_1) | set(aptos.fecha_2)]
    grupos = {}
    for f in todas:
        if f not in sueltas:
            grupos.setdefault(raiz(f), []).append(f)
    log("Fechas en la red: %d de %d; subredes: %d" % (len(todas) - len(sueltas), len(todas), len(grupos)))
    for g in sorted(grupos.values()):
        log("  subred %s a %s (%d fechas)" % (min(g), max(g), len(g)))
    if sueltas:
        log("  fechas sin par apto (quedan fuera de la red): %s" % ", ".join(sueltas))
    if len(grupos) > 1:
        log("AVISO: la red esta cortada en %d subredes y el apilado no puede unirlas. Subir --dias_max o --vecinos."
            % len(grupos))
    out = ruta_tp("Tp10", "05_Resultados", "04_Tablas", "%s_red_sbas.csv" % S)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    t.drop(columns=["b1", "b2"]).to_csv(out, index=False, encoding="utf-8-sig")
    if bperp:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(9, 4.6))
        # TODOS los pares de la red: los no aptos en gris punteado, los aptos que se pidieron a HyP3
        # (los --hyp3 primeros) en azul y los aptos que no se pidieron en naranja.
        n_pedidos = a.hyp3 if a.hyp3 else a.marcar_pedidos
        pedidos = set(map(tuple, aptos[["fecha_1", "fecha_2"]].head(n_pedidos).values)) if n_pedidos else set()
        for _, p in t.iterrows():
            if p.b1 is None or p.b2 is None:
                continue
            if p.apto != "si":
                estilo = dict(color="#b0b0b0", lw=0.8, ls="--")
            elif (p.fecha_1, p.fecha_2) in pedidos or not pedidos:
                estilo = dict(color="#1f3b73", lw=0.9)
            else:
                estilo = dict(color="#e08214", lw=1.4)
            ax.plot(pd.to_datetime([p.fecha_1, p.fecha_2]), [p.b1, p.b2], "-", **estilo)
        ax.plot(pd.to_datetime([x.properties["startTime"][:10] for x in lista]),
                [bperp.get(x.properties["sceneName"]) for x in lista], "o", color="#d9822b", ms=4)
        ax.set_ylabel("base perpendicular (m)")
        ax.set_xlabel("azul: pares usados; naranja: aptos no pedidos; gris: no aptos")
        ax.set_title("%s - red de pares de línea de base corta, órbita %s" % (S, clave[0]))
        ax.grid(alpha=0.3)
        fig.text(0.01, 0.01, "Fuente: ESA - Copernicus, Sentinel-1 IW SLC; catálogo ASF DAAC, https://search.asf.alaska.edu. Elaboración propia.", fontsize=8)
        fig.tight_layout(rect=(0, 0.05, 1, 1))
        png = ruta_tp("Tp10", "05_Resultados", "05_Graficos", "%s_red_sbas.png" % S)
        os.makedirs(os.path.dirname(png), exist_ok=True)
        fig.savefig(png, dpi=140)
        plt.close(fig)
    if a.hyp3 and len(aptos):
        import hyp3_sdk as sdk
        import hyp3_sdk.exceptions  # noqa: F401  (para sdk.exceptions.ServerError)

        log.titulo("Pedido de %d par(es) a HyP3 (INSAR_GAMMA, 10x2 looks, 40 m)" % min(a.hyp3, len(aptos)))
        try:
            hyp3 = sdk.HyP3()                   # usa el archivo .netrc de Earthdata si existe
        except Exception:                       # noqa: BLE001
            hyp3 = sdk.HyP3(prompt="password")  # si no, pregunta usuario y clave (nunca se escriben en el programa)
        nombre = "Tp10_%s" % S[:12]
        import time

        def con_reintentos(funcion, que, intentos=5, espera=60):
            # El servidor de ASF a veces responde "504 Gateway Timeout" (error del servidor, no nuestro):
            # se espera y se reintenta. Si sigue fallando se devuelve None y el programa continua.
            for i in range(1, intentos + 1):
                try:
                    return funcion()
                except (sdk.exceptions.ServerError, sdk.exceptions.HyP3Error, OSError) as e:
                    log("  ASF no respondio (%s), intento %d de %d: %s" % (que, i, intentos, type(e).__name__))
                    if i < intentos:
                        time.sleep(espera * i)
            return None

        def granulos(j):
            g = j.job_parameters.get("granules")
            if not g:
                g = [j.job_parameters.get("reference"), j.job_parameters.get("secondary")]
                g = [x[0] if isinstance(x, list) else x for x in g]
            return tuple(g)

        encontrados = con_reintentos(lambda: hyp3.find_jobs(name=nombre), "lista de pedidos previos")
        if encontrados is None:
            log("ASF no responde. Se corta aca sin pedir nada: volver a correr más tarde (no duplica pedidos).")
            log.cerrar("volver a correr este mismo comando más tarde")
            return
        previos = [j for j in encontrados if not j.failed()]
        ya = {granulos(j) for j in previos}
        lote = sdk.Batch(previos)
        nuevos, fallidos = 0, 0
        for _, p in aptos.head(a.hyp3).iterrows():
            if (p.escena_1, p.escena_2) in ya:
                continue
            r = con_reintentos(lambda: hyp3.submit_insar_job(p.escena_1, p.escena_2, name=nombre, looks="10x2",
                                                             include_displacement_maps=True, include_inc_map=True,
                                                             apply_water_mask=True),
                               "par %s / %s" % (p.escena_1[17:25], p.escena_2[17:25]))
            if r is None:
                fallidos += 1
                continue
            nuevos += 1
            lote += r
        log("Pares ya pedidos antes: %d; pares nuevos pedidos ahora: %d; no aceptados por ASF: %d"
            % (len(ya), nuevos, fallidos))
        if fallidos:
            log("Para pedir los que faltan, volver a correr el mismo comando más tarde (no duplica pedidos).")
        lote = hyp3.watch(lote)
        destino = os.path.join(ORIGINALES, "HYP3", S)
        os.makedirs(destino, exist_ok=True)
        hechos = set(os.listdir(destino))
        for j in lote:
            if j.succeeded() and not any(f.startswith(j.files[0]["filename"][:-4]) for f in hechos):
                j.download_files(destino)
        log("Trabajos terminados: %d de %d" % (sum(j.succeeded() for j in lote), len(lote)))
        log("Descargado en %s. Descomprimir cada .zip en su carpeta." % destino)
    log.cerrar("python Tp10_05_velocidad_subsidencia.py --sitio %s" % S)


if __name__ == "__main__":
    main()
