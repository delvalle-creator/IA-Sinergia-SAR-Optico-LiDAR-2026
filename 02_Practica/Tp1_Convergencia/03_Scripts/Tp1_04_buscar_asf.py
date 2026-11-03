# -*- coding: utf-8 -*-
"""
Tp1_04_buscar_asf.py   [SE CORRE]   paso 4 del Tp1
==================================================
Busca en el catalogo de ASF (Alaska Satellite Facility) los productos de
radar que el Planetary Computer no tiene:

  NISAR L2 GCOV       banda L, gamma0 a 20 m (o 10 m), HH+HV       -> Tp2, Tp9, Tp10
  Sentinel-1 IW SLC   banda C, con fase, para interferometria        -> Tp7, Tp10
  Sentinel-1 IW GRD   banda C, para la cadena completa en SNAP       -> Tp2
  ALOS PALSAR RTC     banda L historica (2006-2011), 12,5 m          -> Tp9

Para cada producto informa la fraccion del sitio que toca su HUELLA
declarada. Los productos de ASF no son COG: el conteo de pixeles con dato se
hace despues de bajarlos (en el Tp2) y se anota en la planilla. Por eso la
columna "pixeles_validos_%" queda vacia aqui, a proposito: una cifra que no
se midio no se escribe.

BUSCAR no pide cuenta. DESCARGAR pide la cuenta de NASA Earthdata (la misma
para ASF, GEDI e ICESat-2). La credencial NUNCA se escribe en este archivo:
se toma de la variable de entorno EARTHDATA_TOKEN, o del archivo .netrc del
usuario, o se pide por teclado.

SALIDA
  Tp1_Convergencia/05_Resultados/04_Tablas/planilla_ASF_<SITIO>.csv
  descargas (solo con --descargar) en ORIGINALES\\ASF\\<SITIO>\\

USO (Miniforge Prompt, entorno sar):
    python Tp1_04_buscar_asf.py --sitio B_CONCORDIA --desde 2026-09-01 --hasta 2026-09-30
    python Tp1_04_buscar_asf.py --sitio C_FEDERAL --desde 2011-01-01 --hasta 2011-12-31 --solo ALOS
    python Tp1_04_buscar_asf.py --sitio B_CONCORDIA --desde 2026-09-17 --hasta 2026-09-19 --solo NISAR --descargar 1
          (--descargar N baja, de cada sensor pedido, los N productos de mayor huella)
"""
import argparse
import getpass
import netrc
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import pandas as pd                                                   # noqa: E402
from shapely.geometry import box, shape                               # noqa: E402

from configuracion_comun import SITIOS, ORIGINALES, ruta_tp           # noqa: E402
from funciones_comunes import Bitacora                                # noqa: E402

BUSQUEDAS = {
    # nombre: (parametros de asf_search, banda, lambda en cm)
    "NISAR": (dict(dataset="NISAR", processingLevel="GCOV"), "L", 24.0),
    "S1_SLC": (dict(platform="SENTINEL-1", processingLevel="SLC", beamMode="IW"), "C", 5.6),
    "S1_GRD": (dict(platform="SENTINEL-1", processingLevel="GRD_HD", beamMode="IW"), "C", 5.6),
    "ALOS": (dict(platform="ALOS", processingLevel="RTC_HI_RES"), "L", 23.6),
}



def _bytes_asf(prop):
    """Tamano del archivo principal. En NISAR, 'bytes' es un diccionario
    {archivo: {'bytes': n, 'format': ...}}; en Sentinel-1 y ALOS es un numero."""
    b = prop.get("bytes", 0) or 0
    if isinstance(b, dict):
        nombre = os.path.basename(str(prop.get("url", "")))
        v = b.get(nombre) or max(b.values(), key=lambda x: float(x.get("bytes", 0)) if isinstance(x, dict) else 0, default=0)
        b = v.get("bytes", 0) if isinstance(v, dict) else v
    try:
        return int(float(b or 0))
    except (TypeError, ValueError):
        return 0

def sesion_asf(log):
    """Sesion autenticada de ASF sin escribir credenciales en el codigo."""
    import asf_search as asf
    try:                                              # CMR a veces tarda mas de 30 s
        asf.constants.INTERNAL.CMR_TIMEOUT = 120
    except AttributeError:
        pass

    s = asf.ASFSession()
    token = os.environ.get("EARTHDATA_TOKEN", "").strip()
    if token:
        log("Credencial: ficha EARTHDATA_TOKEN (variable de entorno).")
        return s.auth_with_token(token)
    casa = os.path.expanduser("~")
    for archivo in (os.path.join(casa, ".netrc"), os.path.join(casa, "_netrc")):   # en Windows suele ser _netrc
        if not os.path.exists(archivo):
            continue
        try:
            usuario, _, clave = netrc.netrc(archivo).authenticators("urs.earthdata.nasa.gov")
            log("Credencial: archivo %s del usuario." % os.path.basename(archivo))
            return s.auth_with_creds(usuario, clave)
        except (TypeError, netrc.NetrcParseError):
            continue
    log("No hay ficha ni .netrc: se pide la cuenta de NASA Earthdata por teclado.")
    usuario = input("Usuario de NASA Earthdata: ").strip()
    clave = getpass.getpass("Contrasena (no se muestra): ")
    return s.auth_with_creds(usuario, clave)


def main():
    import asf_search as asf
    try:                                              # CMR a veces tarda mas de 30 s
        asf.constants.INTERNAL.CMR_TIMEOUT = 120
    except AttributeError:
        pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", required=True, choices=list(SITIOS.keys()))
    ap.add_argument("--desde", required=True)
    ap.add_argument("--hasta", required=True)
    ap.add_argument("--solo", nargs="*", default=list(BUSQUEDAS.keys()),
                    choices=list(BUSQUEDAS.keys()))
    ap.add_argument("--descargar", type=int, default=0)
    a = ap.parse_args()

    log = Bitacora(ruta_tp("Tp1", "05_Resultados", "06_Control_calidad"), "Tp1_04_%s" % a.sitio)
    caja = box(*SITIOS[a.sitio]["bbox"])
    filas, por_bajar = [], []
    for nombre in a.solo:
        params, banda, lam = BUSQUEDAS[nombre]
        log.titulo("%s  (%s)" % (nombre, params))
        try:
            res = asf.search(intersectsWith=caja.wkt, start=a.desde, end=a.hasta + "T23:59:59Z",   # el ultimo dia entero
                             maxResults=500, **params)
        except Exception as e:                       # noqa: BLE001
            log("  La busqueda fallo: %s" % str(e)[:150])
            log("  Se deja constancia y se sigue con el siguiente producto.")
            continue
        log("  %d productos tocan el sitio." % len(res))
        lista = []
        for r in res:
            p = r.properties
            hu = shape(r.geometry)
            cob = 100.0 * hu.intersection(caja).area / caja.area
            t = str(p.get("startTime", ""))
            fila = {"sensor": nombre, "banda": banda, "lambda_cm": lam,
                    "producto": p.get("processingLevel", ""), "fecha": t[:10],
                    "hora_utc": t[11:16], "pasada": str(p.get("flightDirection", "")).lower(),
                    "orbita_track": p.get("pathNumber", ""), "frame": p.get("frameNumber", ""),
                    "polarizaciones": p.get("polarization", ""),
                    "cobertura_huella_%": round(cob, 1), "pixeles_validos_%": "",
                    "nombre": p.get("fileID", p.get("sceneName", "")),
                    "tamano_MB": round(_bytes_asf(p) / 1e6, 1),
                    "url": p.get("url", "")}
            filas.append(fila)
            lista.append((cob, r, fila))
            log("  %s %s %-10s track %-4s %-10s huella %5.1f %%  %s"
                % (fila["fecha"], fila["hora_utc"], fila["pasada"], fila["orbita_track"],
                   fila["polarizaciones"], cob, fila["nombre"][:60]))
        lista.sort(key=lambda x: -x[0])
        por_bajar += [(nombre, r) for _, r, _ in lista[:a.descargar]]

    # Con encabezado aunque no haya filas: asi Tp1_07 la lee sin error
    # (una busqueda vacia o fallida es un resultado que se declara, no un error).
    df = pd.DataFrame(filas, columns=["sensor", "banda", "lambda_cm", "producto", "fecha", "hora_utc", "pasada",
                                      "orbita_track", "frame", "polarizaciones", "cobertura_huella_%",
                                      "pixeles_validos_%", "nombre", "tamano_MB", "url"])
    if not len(df):
        log("  Ningun producto en ASF para esta ventana: la planilla queda con el encabezado solo.")
    tabla = ruta_tp("Tp1", "05_Resultados", "04_Tablas", "planilla_ASF_%s.csv" % a.sitio)
    os.makedirs(os.path.dirname(tabla), exist_ok=True)
    df.to_csv(tabla, index=False, encoding="utf-8-sig")
    log("")
    log("Planilla:", tabla)

    if por_bajar:
        log.titulo("Descarga de %d producto(s)" % len(por_bajar))
        ses = sesion_asf(log)
        for nombre, r in por_bajar:
            destino = os.path.join(ORIGINALES, "ASF", a.sitio, nombre)
            os.makedirs(destino, exist_ok=True)
            log("  bajando %s -> %s" % (r.properties.get("fileID", ""), destino))
            r.download(path=destino, session=ses)
        log("Descargas terminadas. Verificar los tamanos contra la columna tamano_MB.")
    log.cerrar("python Tp1_05_buscar_lidar.py --sitio %s" % a.sitio)


if __name__ == "__main__":
    main()
