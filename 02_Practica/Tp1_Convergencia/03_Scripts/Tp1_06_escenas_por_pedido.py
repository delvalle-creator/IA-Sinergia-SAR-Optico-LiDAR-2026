# -*- coding: utf-8 -*-
"""
Tp1_06_escenas_por_pedido.py   [SE CORRE]   paso 6 del Tp1
==========================================================
Las bandas que NO se bajan con un solo programa:

  Banda P   BIOMASS (ESA)           catalogo STAC de ESA MAAP: se BUSCA sin
                                    cuenta; bajar exige la ficha de 90 dias.
  Banda L   SAOCOM-1A/1B (CONAE)    catalogo con registro, pedido y cuota.
  Banda S   NISAR S (ISRO)          portal Bhoonidhi, con registro.
  Banda S   NovaSAR-1 (CSIRO)       portal de CSIRO, con registro y licencia.
  Banda X   COSMO-SkyMed (ASI)      pedido institucional (CONAE-ASI).

Este programa hace dos cosas:
  1. Busca BIOMASS en ESA MAAP sobre el sitio (niveles 1a, 1b, 1c y 2a) y
     lista lo que hay. Con --descargar y la ficha, baja los productos 1b.
  2. Lee la planilla que el grupo completa A MANO con lo que pidio o encontro
     en los otros portales (04_Tablas_de_trabajo/escenas_por_pedido.csv),
     controla que no falte ninguna columna obligatoria y la suma al
     inventario. Si la planilla no existe, la crea vacia con sus columnas y
     una fila de ejemplo (marcada EJEMPLO, que el programa ignora).

Una ausencia documentada es informacion; una ausencia silenciosa es un hueco.
Por eso la planilla tiene la columna "resultado" (obtenida / pedida / sin
cobertura / sin acceso) y no solo las escenas que se consiguieron.

CREDENCIALES (nunca en el codigo)
  BIOMASS_TOKEN          ficha offline de ESA MAAP (90 dias)
  BIOMASS_CLIENT_SECRET  secreto de cliente de ESA MAAP
Se definen en el Miniforge Prompt antes de correr:   set BIOMASS_TOKEN=...

USO
    python Tp1_06_escenas_por_pedido.py --sitio D_LAPAZ_VILLAGUAY
    python Tp1_06_escenas_por_pedido.py --sitio D_LAPAZ_VILLAGUAY --descargar
"""
import argparse
import getpass
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import pandas as pd                                                   # noqa: E402

from configuracion_comun import SITIOS, ORIGINALES, ruta_tp           # noqa: E402
from funciones_comunes import Bitacora                                # noqa: E402

MAAP_STAC = "https://catalog.maap.eo.esa.int/catalogue/"
MAAP_TOKEN = "https://iam.maap.eo.esa.int/realms/esa-maap/protocol/openid-connect/token"
COLECCIONES = ["BiomassLevel1a", "BiomassLevel1b", "BiomassLevel1c", "BiomassLevel2a"]

COLUMNAS = ["sensor", "banda", "lambda_cm", "portal", "producto", "escena", "fecha",
            "hora_utc", "pasada", "polarizaciones", "pixel_m", "sitio",
            "resultado", "fecha_pedido", "observaciones"]
EJEMPLO = {"sensor": "EJEMPLO SAOCOM-1A", "banda": "L", "lambda_cm": 23.5,
           "portal": "https://catalogos.conae.gov.ar", "producto": "L1D GTC QP",
           "escena": "(identificador del catalogo)", "fecha": "AAAA-MM-DD", "hora_utc": "HH:MM",
           "pasada": "ascendente/descendente", "polarizaciones": "HH+HV+VH+VV",
           "pixel_m": 10, "sitio": "B_CONCORDIA",
           "resultado": "obtenida / pedida / sin cobertura / sin acceso",
           "fecha_pedido": "AAAA-MM-DD", "observaciones": "texto libre"}


def ficha_maap(log):
    tok = os.environ.get("BIOMASS_TOKEN", "").strip()
    if not tok:
        log("  Sin BIOMASS_TOKEN: solo se BUSCA, no se descarga.")
        return None
    import requests

    sec = os.environ.get("BIOMASS_CLIENT_SECRET", "").strip() or getpass.getpass(
        "client_secret de ESA MAAP (no se muestra): ")
    r = requests.post(MAAP_TOKEN, data={"client_id": "offline-token", "client_secret": sec,
                                        "grant_type": "refresh_token", "refresh_token": tok},
                      timeout=60)
    if r.status_code != 200:
        log("  ESA MAAP rechazo la ficha (%d). Si dice invalid_grant, generar una ficha nueva "
            "en el portal de MAAP." % r.status_code)
        return None
    return r.json()["access_token"]


def bajar_item(item, carpeta, acceso, log):
    import requests

    os.makedirs(carpeta, exist_ok=True)
    for nombre, asset in item.assets.items():
        destino = os.path.join(carpeta, "%s__%s" % (item.id, nombre))
        if os.path.exists(destino) and os.path.getsize(destino) > 0:
            log("     ya estaba:", os.path.basename(destino))
            continue
        with requests.get(asset.href, headers={"Authorization": "Bearer %s" % acceso},
                          stream=True, timeout=900) as r:
            if r.status_code != 200:
                log("     ERROR %d en %s" % (r.status_code, nombre))
                continue
            with open(destino, "wb") as f:
                for trozo in r.iter_content(1 << 20):
                    f.write(trozo)
        log("     OK", os.path.basename(destino))


def main():
    from pystac_client import Client

    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", required=True, choices=list(SITIOS.keys()))
    ap.add_argument("--desde", default="2025-12-01")
    ap.add_argument("--hasta", default="2026-12-31")
    ap.add_argument("--descargar", action="store_true")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp1", "05_Resultados", "06_Control_calidad"), "Tp1_06_%s" % a.sitio)

    # ------------------------------------------------------------- BIOMASS
    log.titulo("BIOMASS (banda P) en ESA MAAP, %s a %s" % (a.desde, a.hasta))
    filas = []
    try:
        cat = Client.open(MAAP_STAC)
        acceso = ficha_maap(log) if a.descargar else None
        for col in COLECCIONES:
            items = list(cat.search(collections=[col], bbox=list(SITIOS[a.sitio]["bbox"]),
                                    datetime="%sT00:00:00Z/%sT23:59:59Z" % (a.desde, a.hasta),
                                    max_items=300).items())
            log("  %s: %d productos" % (col, len(items)))
            for it in items:
                f = it.datetime.strftime("%Y-%m-%d") if it.datetime else ""
                filas.append({"sensor": "BIOMASS", "banda": "P", "lambda_cm": 69.0,
                              "portal": MAAP_STAC, "producto": col, "escena": it.id,
                              "fecha": f, "hora_utc": it.datetime.strftime("%H:%M") if it.datetime else "",
                              "pasada": "", "polarizaciones": "HH+HV+VH+VV", "pixel_m": "",
                              "sitio": a.sitio, "resultado": "en catalogo",
                              "fecha_pedido": "", "observaciones": ""})
                log("     %s  %s" % (f, it.id))
                if acceso and col == "BiomassLevel1b":
                    bajar_item(it, os.path.join(ORIGINALES, "BIOMASS", a.sitio, col), acceso, log)
    except Exception as e:                           # noqa: BLE001
        log("  La consulta a ESA MAAP fallo: %s" % str(e)[:150])
        log("  Se deja constancia en la planilla y se sigue.")
        filas.append({"sensor": "BIOMASS", "banda": "P", "lambda_cm": 69.0, "portal": MAAP_STAC,
                      "producto": "", "escena": "", "fecha": "", "hora_utc": "", "pasada": "",
                      "polarizaciones": "", "pixel_m": "", "sitio": a.sitio,
                      "resultado": "consulta fallida", "fecha_pedido": "",
                      "observaciones": str(e)[:150]})

    # ---------------------------------------------- planilla manual del grupo
    log.titulo("Planilla de escenas por pedido (SAOCOM, NISAR S, NovaSAR, COSMO)")
    plan = ruta_tp("Tp1", "04_Tablas_de_trabajo", "escenas_por_pedido.csv")
    os.makedirs(os.path.dirname(plan), exist_ok=True)
    if not os.path.exists(plan):
        pd.DataFrame([EJEMPLO], columns=COLUMNAS).to_csv(plan, index=False, encoding="utf-8-sig")
        log("  No existia: se creo %s con sus columnas y una fila EJEMPLO." % plan)
        log("  Complete una fila por escena PEDIDA o CONSULTADA (aunque no se haya obtenido)")
        log("  y vuelva a correr este programa.")
    manual = pd.read_csv(plan, encoding="utf-8-sig", dtype=str).fillna("")
    faltan = [c for c in COLUMNAS if c not in manual.columns]
    if faltan:
        log("  ERROR: a la planilla le faltan las columnas %s. No se la usa." % faltan)
        manual = pd.DataFrame(columns=COLUMNAS)
    manual = manual[~manual["sensor"].str.startswith("EJEMPLO")]
    incompletas = manual[(manual["fecha"] == "") | (manual["resultado"] == "")]
    log("  %d filas cargadas por el grupo; %d incompletas (sin fecha o sin resultado)."
        % (len(manual), len(incompletas)))
    for _, f in incompletas.iterrows():
        log("     INCOMPLETA: %s %s" % (f["sensor"], f["escena"]))

    total = pd.concat([pd.DataFrame(filas, columns=COLUMNAS), manual], ignore_index=True)
    salida = ruta_tp("Tp1", "05_Resultados", "04_Tablas", "planilla_por_pedido_%s.csv" % a.sitio)
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    total.to_csv(salida, index=False, encoding="utf-8-sig")
    log("")
    log("Planilla:", salida)
    log.cerrar("python Tp1_07_matriz_convergencia.py --sitio %s" % a.sitio)


if __name__ == "__main__":
    main()
