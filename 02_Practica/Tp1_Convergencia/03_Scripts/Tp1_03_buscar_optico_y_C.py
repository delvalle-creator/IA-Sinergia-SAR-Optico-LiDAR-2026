# -*- coding: utf-8 -*-
"""
Tp1_03_buscar_optico_y_C.py   [SE CORRE]   paso 3 del Tp1
=========================================================
Busca en el Planetary Computer (STAC, sin cuenta) las escenas Sentinel-2 L2A
(optico) y Sentinel-1 RTC (banda C, gamma0 ya corregido por el terreno) sobre
un sitio y una ventana de fechas, y VERIFICA cada una antes de bajar nada:

  Sentinel-2:  nubosidad_catalogo_%   la que declara el catalogo (tesela
                                      entera de 110 x 110 km)
               nubosidad_sitio_%      la contada con la SCL dentro del sitio
               pixeles_validos_%      fraccion del sitio con dato util
  Sentinel-1:  pixeles_validos_%      fraccion del sitio con gamma0 > 0
               orbita y pasada        para no mezclar geometrias (diap. 14)

La verificacion lee la ventana del sitio a 60 m (S2) o a 100 m (S1): mide en
segundos lo que costaria minutos bajar. Nada se descarga en este paso.

Al final propone PARES optico-radar con su diferencia de dias, porque la
convergencia es temporal antes que nada (presentacion 01, diapositiva 18).

SALIDA
  Tp1_Convergencia/05_Resultados/04_Tablas/planilla_MPC_<SITIO>.csv
  Tp1_Convergencia/05_Resultados/04_Tablas/pares_optico_C_<SITIO>.csv

USO (Miniforge Prompt, entorno sar):
    python Tp1_03_buscar_optico_y_C.py --sitio B_CONCORDIA --desde 2023-10-01 --hasta 2023-11-30
    python Tp1_03_buscar_optico_y_C.py --sitio A1_DELTA_QUEMAS --desde 2020-06-15 --hasta 2020-10-31
Opciones: --nubes_max 80 (descarta antes de verificar las de mas nubosidad de
catalogo, solo para ahorrar tiempo) y --dias_par 3 (diferencia maxima de un par).
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
from funciones_comunes import (grilla_sitio, buscar_stac, fecha_item,  # noqa: E402
                               s1_rtc, Bitacora, leer_en_grilla, CLASES_SCL_VALIDAS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", required=True, choices=list(SITIOS.keys()))
    ap.add_argument("--desde", required=True)
    ap.add_argument("--hasta", required=True)
    ap.add_argument("--nubes_max", type=float, default=80.0)
    ap.add_argument("--dias_par", type=int, default=3)
    a = ap.parse_args()

    log = Bitacora(ruta_tp("Tp1", "05_Resultados", "06_Control_calidad"),
                   "Tp1_03_%s" % a.sitio)
    log("Sitio %s  (%s)   ventana %s a %s" % (a.sitio, SITIOS[a.sitio]["nombre"], a.desde, a.hasta))
    g60 = grilla_sitio(a.sitio, pixel=60.0)
    g100 = grilla_sitio(a.sitio, pixel=100.0)
    filas = []

    # ------------------------------------------------------------ Sentinel-2
    log.titulo("Sentinel-2 L2A (coleccion sentinel-2-l2a)")
    try:
        items = buscar_stac("sentinel-2-l2a", a.sitio, a.desde, a.hasta)
    except Exception as e:                       # noqa: BLE001
        log("No se pudo consultar el Planetary Computer (sentinel-2-l2a): %s. Revise la conexion y vuelva a correr;"
            " esta coleccion queda sin filas." % str(e)[:120])
        items = []
    log("El catalogo devolvio %d escenas (teselas) que TOCAN el sitio." % len(items))
    # El Planetary Computer guarda a veces DOS versiones de la misma toma y tesela: la
    # original y un reprocesamiento posterior de ESA (Coleccion 1). El identificador termina
    # en la fecha de procesamiento (..._T21JUF_20241030T133525). Se deja la mas nueva.
    unicas = {}
    for it in items:
        base, proc = it.id.rsplit("_", 1) if it.id.count("_") >= 5 else (it.id, "")
        if base not in unicas or proc > unicas[base][0]:
            unicas[base] = (proc, it)
    if len(unicas) < len(items):
        log("  %d son la misma toma reprocesada: se deja la version mas nueva de cada una -> %d."
            % (len(items) - len(unicas), len(unicas)))
    items = [v[1] for v in sorted(unicas.values(), key=lambda v: v[1].id)]
    mosaicos = {}
    for it in items:
        f, h = fecha_item(it)
        nc = float(it.properties.get("eo:cloud_cover", np.nan))
        if nc > a.nubes_max:
            log("  %s %s  nubes catalogo %5.1f %%  -> no se verifica (supera --nubes_max)"
                % (f, it.id[:38], nc))
            filas.append({"sensor": "Sentinel-2", "banda": "optico", "fecha": f, "hora_utc": h,
                          "id": it.id, "tesela": it.properties.get("s2:mgrs_tile", ""),
                          "nubosidad_catalogo_%": nc, "nubosidad_sitio_%": np.nan,
                          "pixeles_validos_%": np.nan, "decision": "descartada: nubes de catalogo"})
            continue
        scl = leer_en_grilla(it.assets["SCL"].href, g60, "nearest", nodata_origen=0, tipo="uint8")
        con_dato = scl > 0
        valido = np.isin(scl, CLASES_SCL_VALIDAS)
        n_dato = int(con_dato.sum())
        cobertura = 100.0 * n_dato / scl.size
        nubes = 100.0 * (con_dato & ~valido).sum() / n_dato if n_dato else float("nan")
        util = 100.0 * valido.mean()
        # para el mosaico del dia: misma fecha y misma orbita relativa (R024, R067...)
        clave = (f, it.id.split("_")[3] if it.id.count("_") >= 3 else "")
        m = mosaicos.setdefault(clave, {"dato": np.zeros_like(con_dato), "valido": np.zeros_like(valido),
                                        "teselas": [], "hora": h})
        m["dato"] |= con_dato
        m["valido"] |= valido
        m["teselas"].append(it.properties.get("s2:mgrs_tile", ""))
        if cobertura < 50:
            dec = "descartada: cubre %.0f %% del sitio" % cobertura
        elif nubes > 20:
            dec = "descartada: %.0f %% de nubes DENTRO del sitio" % nubes
        else:
            dec = "candidata"
        log("  %s %s  nubes catalogo %5.1f %% | sitio %5.1f %% | util %5.1f %%  -> %s"
            % (f, it.id[:38], nc, nubes, util, dec))
        filas.append({"sensor": "Sentinel-2", "banda": "optico", "fecha": f, "hora_utc": h,
                      "id": it.id, "tesela": it.properties.get("s2:mgrs_tile", ""),
                      "nubosidad_catalogo_%": nc, "nubosidad_sitio_%": round(nubes, 1),
                      "pixeles_validos_%": round(util, 1), "decision": dec})

    # ------------------------------------------- Sentinel-2: mosaico de cada dia
    # Un sitio grande cae en varias teselas y ninguna lo cubre por si sola. Lo que
    # importa es el DIA: se unen las teselas de la misma fecha y orbita y se mide la
    # cobertura y las nubes del mosaico dentro del sitio. Los pares se arman con esto.
    log.titulo("Sentinel-2: mosaico de las teselas de cada dia (lo que se usa para los pares)")
    for (f, orb), m in sorted(mosaicos.items()):
        n_dato = int(m["dato"].sum())
        cob = 100.0 * n_dato / m["dato"].size
        nub = 100.0 * (m["dato"] & ~m["valido"]).sum() / n_dato if n_dato else float("nan")
        util = 100.0 * m["valido"].mean()
        if cob < 50:
            dec = "descartada: cubre %.0f %% del sitio" % cob
        elif nub > 20:
            dec = "descartada: %.0f %% de nubes DENTRO del sitio" % nub
        else:
            dec = "candidata"
        tes = sorted(set(m["teselas"]))
        log("  %s %s  %d tesela(s)  cubre %5.1f %% | nubes sitio %5.1f %% | util %5.1f %%  -> %s"
            % (f, orb, len(tes), cob, nub, util, dec))
        filas.append({"sensor": "Sentinel-2 mosaico del dia", "banda": "optico", "fecha": f,
                      "hora_utc": m["hora"], "id": "%s %s (%s)" % (f, orb, " ".join(tes)),
                      "tesela": " ".join(tes), "nubosidad_catalogo_%": np.nan,
                      "nubosidad_sitio_%": round(nub, 1), "pixeles_validos_%": round(util, 1),
                      "decision": dec})

    # ------------------------------------------------------------ Sentinel-1
    log.titulo("Sentinel-1 RTC (coleccion sentinel-1-rtc): gamma0 lineal, VV y VH")
    try:
        items = buscar_stac("sentinel-1-rtc", a.sitio, a.desde, a.hasta)
    except Exception as e:                       # noqa: BLE001
        log("No se pudo consultar el Planetary Computer (sentinel-1-rtc): %s. Revise la conexion y vuelva a correr;"
            " esta coleccion queda sin filas." % str(e)[:120])
        items = []
    log("El catalogo devolvio %d escenas que TOCAN el sitio." % len(items))
    for it in items:
        f, h = fecha_item(it)
        p = it.properties
        orb = p.get("sat:relative_orbit", "")
        pas = p.get("sat:orbit_state", "")
        pols = "+".join(p.get("sar:polarizations", []))
        try:
            vv = s1_rtc(it, "vv", g100)
            util = 100.0 * np.isfinite(vv).mean()
        except Exception as e:                       # noqa: BLE001
            util = np.nan
            log("     (no se pudo leer la ventana: %s)" % str(e)[:80])
        dec = "candidata" if util >= 50 else "descartada: cubre %.0f %% del sitio" % (util if util == util else 0)
        log("  %s %s  orbita %s %s  %s  util %5.1f %%  -> %s"
            % (f, h, orb, pas, pols, util, dec))
        filas.append({"sensor": "Sentinel-1 RTC", "banda": "C", "fecha": f, "hora_utc": h,
                      "id": it.id, "tesela": "", "orbita_relativa": orb, "pasada": pas,
                      "polarizaciones": pols, "nubosidad_catalogo_%": np.nan,
                      "nubosidad_sitio_%": np.nan, "pixeles_validos_%": round(util, 1),
                      "decision": dec})

    df = pd.DataFrame(filas)
    if len(df) and (df.sensor == "Sentinel-2").any():
        teselas = sorted(set(df.loc[df.sensor == "Sentinel-2", "tesela"]) - {""})
        if len(teselas) > 1:
            log("")
            log("  El sitio cae en %d teselas Sentinel-2 (%s): los pares se arman con el mosaico"
                % (len(teselas), ", ".join(teselas)))
            log("  de cada dia, no con cada tesela suelta. Para ver el sitio entero hay que unirlas.")
    tabla = ruta_tp("Tp1", "05_Resultados", "04_Tablas", "planilla_MPC_%s.csv" % a.sitio)
    os.makedirs(os.path.dirname(tabla), exist_ok=True)
    df.to_csv(tabla, index=False, encoding="utf-8-sig")

    # --------------------------------------------------- pares optico-radar
    log.titulo("Pares optico-C con diferencia <= %d dias" % a.dias_par)
    pares = []
    if len(df):
        s2 = df[(df.sensor == "Sentinel-2 mosaico del dia") & (df.decision == "candidata")]
        s1 = df[(df.sensor == "Sentinel-1 RTC") & (df.decision == "candidata")]
        for _, o in s2.iterrows():
            for _, r in s1.iterrows():
                dd = abs((pd.Timestamp(o.fecha) - pd.Timestamp(r.fecha)).days)
                if dd <= a.dias_par:
                    pares.append({"fecha_optico": o.fecha, "fecha_radar": r.fecha, "dias": dd,
                                  "nubes_sitio_%": o["nubosidad_sitio_%"],
                                  "orbita_radar": r.get("orbita_relativa", ""),
                                  "id_optico": o.id, "id_radar": r.id})
    dp = pd.DataFrame(pares).sort_values(["dias", "nubes_sitio_%"]) if pares else pd.DataFrame()
    for _, p in dp.head(15).iterrows():
        log("  optico %s  radar %s  (%d dias)  nubes en el sitio %.1f %%"
            % (p.fecha_optico, p.fecha_radar, p.dias, p["nubes_sitio_%"]))
    if not pares:
        log("  Ningun par cumple la condicion. Ampliar la ventana o --dias_par, y DECLARARLO.")
    salida_pares = ruta_tp("Tp1", "05_Resultados", "04_Tablas", "pares_optico_C_%s.csv" % a.sitio)
    dp.to_csv(salida_pares, index=False, encoding="utf-8-sig")
    log("")
    log("Planilla:", tabla)
    log("Pares   :", salida_pares)
    log.cerrar("python Tp1_04_buscar_asf.py --sitio %s --desde %s --hasta %s" % (a.sitio, a.desde, a.hasta))


if __name__ == "__main__":
    main()
