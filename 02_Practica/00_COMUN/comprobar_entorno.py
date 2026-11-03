# -*- coding: utf-8 -*-
"""
comprobar_entorno.py   [SE CORRE]   antes del Tp1, una sola vez por computadora
=============================================================================
Verifica que el entorno de Miniforge "sar" tiene todo lo que usan los once
practicos, y que las carpetas de datos del curso estan donde la
configuracion las espera. No descarga nada ni pide contrasenas.

QUE REVISA
  1. La version de Python (3.11) y cada biblioteca, con su version.
  2. Que GDAL lea JPEG 2000 (Sentinel-2 en SAFE) y HDF5 (NISAR, GEDI, ATL08).
  3. Que PROJ tenga la grilla del geoide EGM2008 (alturas de ICESat-2).
  4. Las carpetas de datos (configuracion_comun.py): NISAR del Delta, NovaSAR,
     archivo del curso 2023, COSMO-SkyMed de Diamante.
  5. Que exista la credencial de NASA Earthdata (.netrc o variable de
     entorno), SIN leer su contenido.
  6. Con --red: que respondan el Planetary Computer, ASF y Earthdata.

USO (Miniforge Prompt)
    conda activate sar
    cd <ruta>\\02_Practica\\00_COMUN
    python comprobar_entorno.py
    python comprobar_entorno.py --red
"""
import argparse
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BIBLIOTECAS = ["numpy", "scipy", "pandas", "matplotlib", "osgeo.gdal", "rasterio", "geopandas",
               "pyogrio", "shapely", "pyproj", "h5py", "sklearn", "skimage", "pystac_client",
               "planetary_computer", "asf_search", "earthaccess", "hyp3_sdk", "requests", "openpyxl"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--red", action="store_true", help="probar tambien la conexion a los catalogos")
    a = ap.parse_args()
    fallas = 0

    print("1. Python y bibliotecas")
    v = sys.version_info
    print("   Python %d.%d.%d %s" % (v.major, v.minor, v.micro, "(ok)" if (v.major, v.minor) == (3, 11) else
                                    "(se espera 3.11: recrear el entorno con entorno_sar.yml)"))
    for b in BIBLIOTECAS:
        try:
            m = importlib.import_module(b)
            ver = getattr(m, "__version__", None) or (m.VersionInfo("RELEASE_NAME") if b == "osgeo.gdal" else "?")
            print("   %-20s %s" % (b, ver))
        except Exception as e:                       # noqa: BLE001
            print("   %-20s FALTA (%s)" % (b, str(e)[:60]))
            fallas += 1

    print("\n2. Formatos de GDAL")
    try:
        from osgeo import gdal
        for drv, para in (("JP2OpenJPEG", "Sentinel-2 en formato SAFE (.jp2)"), ("HDF5", "NISAR, GEDI y ATL08 (.h5)"),
                          ("GPKG", "GeoPackage"), ("ENVI", "productos .img de SNAP")):
            ok = gdal.GetDriverByName(drv) is not None
            fallas += 0 if ok else 1
            print("   %-12s %s  %s" % (drv, "ok   " if ok else "FALTA", para))
    except Exception as e:                           # noqa: BLE001
        print("   no se pudo cargar GDAL: %s" % e)
        fallas += 1

    print("\n3. Geoide EGM2008 en PROJ (para pasar alturas de ICESat-2 a cotas)")
    try:
        from funciones_lidar import alturas_a_egm2008
        import numpy as np
        h = alturas_a_egm2008(np.array([-60.6]), np.array([-32.07]), np.array([30.0]))
        print("   ok: 30 m elipsoidales en Diamante = %.2f m sobre el geoide" % float(np.ravel(h)[0]))
    except Exception as e:                           # noqa: BLE001
        print("   NO disponible (%s)" % str(e)[:100])
        print("   Solucion: con conexion, correr  projsync --file us_nga_egm08_25.tif  en el Miniforge Prompt.")
        fallas += 1

    print("\n4. Carpetas de datos del curso")
    import configuracion_comun as cc
    for nombre in ("NISAR_DELTA", "NOVASAR", "ORIGINALES_2023", "COSMO_DIAMANTE", "MAPBIOMAS_BOSQUES", "ORIGINALES"):
        ruta = getattr(cc, nombre, None)
        if ruta is None:
            continue
        existe = os.path.isdir(ruta)
        print("   %-18s %s  %s" % (nombre, "ok   " if existe else "NO ESTA", ruta))
    print("   (Si una carpeta no esta, el practico que la usa lo avisa. Las rutas se cambian en")
    print("    configuracion_comun.py o con las variables de entorno CURSO_SAR_*.)")

    print("\n5. Credencial de NASA Earthdata (no se lee su contenido)")
    casa = os.path.expanduser("~")
    netrc = [p for p in (os.path.join(casa, ".netrc"), os.path.join(casa, "_netrc")) if os.path.exists(p)]
    token = bool(os.environ.get("EARTHDATA_TOKEN"))
    if netrc or token:
        print("   ok: %s" % (netrc[0] if netrc else "variable de entorno EARTHDATA_TOKEN"))
    else:
        print("   no hay .netrc ni EARTHDATA_TOKEN: Tp1_04 y Tp1_05 pediran usuario y contrasena al correr.")

    if a.red:
        print("\n6. Conexion a los catalogos")
        import requests
        for nombre, url in (("Planetary Computer", "https://planetarycomputer.microsoft.com/api/stac/v1"),
                            ("ASF", "https://api.daac.asf.alaska.edu/services/search/param?output=count&platform=SENTINEL-1&maxResults=1"),
                            ("NASA CMR", "https://cmr.earthdata.nasa.gov/search/collections.json?short_name=GEDI02_A")):
            try:
                r = requests.get(url, timeout=20)
                print("   %-20s %s (HTTP %d)" % (nombre, "ok" if r.ok else "RESPONDE CON ERROR", r.status_code))
            except Exception as e:                   # noqa: BLE001
                print("   %-20s SIN CONEXION (%s)" % (nombre, str(e)[:60]))
                fallas += 1

    print("\nResultado: %s" % ("TODO EN ORDEN" if fallas == 0 else "%d problema(s): ver arriba" % fallas))


if __name__ == "__main__":
    main()
