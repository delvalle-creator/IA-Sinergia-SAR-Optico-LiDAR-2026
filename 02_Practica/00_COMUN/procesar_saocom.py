# -*- coding: utf-8 -*-
"""
procesar_saocom.py - SAOCOM-1A StripMap SLC (recortes del curso) -> gamma0 con SNAP (gpt).

Los tres SAOCOM-1A del Delta (archivo del curso SAR CEREGEO 2023) estan recortados al sitio
A1_DELTA_QUEMAS en Tp5_Incendios\\02_Subsets_SNAP_QGIS\\SNAP_DIMAP como SLC (i, q en geometria
de radar, sin calibrar):
    A1_DELTA_QUEMAS_SAOCOM_L_20200721_QP.dim   (antes de las quemas, cuadripolar HH HV VH VV)
    A1_DELTA_QUEMAS_SAOCOM_L_20200907_DP.dim   (durante, doble polarizacion VV VH)
    A1_DELTA_QUEMAS_SAOCOM_L_20201025_QP.dim   (despues, cuadripolar)

Este programa los lleva a gamma0 con la misma cadena que se ensena en el Tp2 (grafo de SNAP,
se guarda para abrirlo en Graph Builder):

  Read -> Calibration (sigma0) -> Multilook (pixel cuadrado en el terreno) -> Speckle-Filter (Refined Lee)
       -> Range-Doppler Terrain-Correction (Copernicus DEM 30 m, 10 m, EPSG:32721, con el angulo de
          incidencia sobre el elipsoide) -> BEAM-DIMAP

Los SLC de CONAE ya vienen calibrados (|DN|^2 = sigma0; el Calibration de SNAP los deja iguales).
gamma0 = sigma0 / cos(angulo de incidencia sobre el elipsoide). No se usa el Terrain-Flattening de
SNAP 14: con SAOCOM da entre 5 y 10 dB menos (comparado con NISAR GCOV y con el mosaico ALOS-2).

Despues agrega al .dim las bandas VIRTUALES en dB y el cociente co/cruzada en dB, escribe:
  - el GeoTIFF de todas las bandas (lineal + dB) con su _metadatos.txt,
  - un GeoTIFF LINEAL de UNA banda por polarizacion (<nombre>_Gamma0_HV.tif, ...), que es lo
    que leen Tp5_01 (--saocom_pre_hv / --saocom_post_hv) y Tp2_01 (--extra),
  - el RGB copolarizada-cruzada-cociente: HH-HV-HH/HV en los cuadripolares, VV-VH-VV/VH en el
    doble polarizacion.

Salida: Tp5_Incendios\\02_Subsets_SNAP_QGIS\\SAOCOM_gamma0\\
          SNAP_DIMAP, QGIS_GeoTIFF, RGB_copol_cruzada_cociente, Grafos_SNAP, LEEME_SAOCOM_gamma0.md

USO (Miniforge Prompt, entorno sar):
    python D:\\CURSOS_CEREGEO_2026\\02_Practica\\00_COMUN\\procesar_saocom.py
    python ...\\procesar_saocom.py --rehacer
SNAP baja solo el Copernicus DEM la primera vez (hace falta internet). 5 a 20 min por escena.
"""
import argparse
import datetime as _dt
import glob
import os
import re
import subprocess
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import armar_subsets as A                                          # noqa: E402
from configuracion_comun import ruta_tp                             # noqa: E402
from procesar_s1_crudo import DEM, nodo                             # noqa: E402

PROGRAMA = "00_COMUN/procesar_saocom.py"
SITIO = "A1_DELTA_QUEMAS"
ESCENAS = {
    "SAOCOM_L_20200721_QP": ("2020-07-21", "antes de las quemas", ["HH", "HV", "VH", "VV"]),
    "SAOCOM_L_20200907_DP": ("2020-09-07", "durante la temporada de quemas", ["VV", "VH"]),
    "SAOCOM_L_20201025_QP": ("2020-10-25", "despues de las quemas", ["HH", "HV", "VH", "VV"]),
}


def grafo(dim_entrada, salida, pols, aplanar=False):
    g = "<graph id=\"SAOCOM_SLC_a_sigma0\">\n  <version>1.0</version>\n"
    g += nodo("Read", "Read", [], {"file": dim_entrada, "copyMetadata": "true"})
    pasos = [
        ("Calibracion", "Calibration", {"selectedPolarisations": ",".join(pols), "outputSigmaBand": "true",
                                        "outputBetaBand": "false", "outputImageInComplex": "false",
                                        "outputImageScaleInDb": "false"}),
        ("Multilook", "Multilook", {"nRgLooks": 2, "outputIntensity": "true", "grSquarePixel": "true"}),
        ("Filtro_speckle", "Speckle-Filter", {"filter": "Refined Lee"}),
        ("Correccion_geometrica", "Terrain-Correction", {"demName": DEM, "demResamplingMethod": "BILINEAR_INTERPOLATION",
                                                         "imgResamplingMethod": "BILINEAR_INTERPOLATION",
                                                         "pixelSpacingInMeter": 10.0, "mapProjection": "EPSG:32721",
                                                         "nodataValueAtSea": "false", "saveSelectedSourceBand": "true",
                                                         "saveIncidenceAngleFromEllipsoid": "true"}),
    ]
    prev = "Read"
    for id_, op, par in pasos:
        g += nodo(id_, op, [prev], par)
        prev = id_
    g += nodo("Write", "Write", [prev], {"file": salida, "formatName": "BEAM-DIMAP"})
    return g + "</graph>\n"


def correr(gpt, xml, dim, reg):
    r = subprocess.run([gpt, xml, "-c", "4G", "-q", "8"], capture_output=True, text=True, errors="replace")
    with open(reg, "w", encoding="utf-8") as f:
        f.write("CODIGO: %s\nSALIDA:\n%s\nERRORES:\n%s\n" % (r.returncode, r.stdout, r.stderr))
    return r.returncode == 0 and os.path.exists(dim), (r.stderr or r.stdout)[-600:]


def a_producto(dim, nombre, magnitud, pols, cita, fecha):
    """gamma0 = sigma0 / cos(angulo de incidencia sobre el elipsoide) (ver el encabezado)."""
    import rasterio
    datos = os.path.splitext(dim)[0] + ".data"
    pref = "Gamma0"
    p = A.Producto(nombre)
    with rasterio.open(os.path.join(datos, "incidenceAngleFromEllipsoid.img")) as r:
        th = r.read(1).astype("float32")
    cos = np.cos(np.radians(np.where((th > 0) & (th < 90), th, np.nan)))
    p.gamma_virtuales = []
    for pol in pols:
        img = sorted(glob.glob(os.path.join(datos, "Sigma0_*%s.img" % pol)))
        if not img:
            continue
        nsig = os.path.basename(img[0])[:-4]
        with rasterio.open(img[0]) as r:
            s0 = r.read(1).astype("float32")
            p.transform, p.crs_wkt = r.transform, A._wkt(r.crs)
        g = s0 / cos
        g[~np.isfinite(g) | (s0 <= 0)] = 0.0
        p.banda("Gamma0_%s" % pol, g.astype("float32"), "intensity",
                "gamma0 %s LINEAL sobre el elipsoide (sigma0 / cos del angulo de incidencia; Refined Lee + "
                "Terrain-Correction en SNAP, desde el SLC SAOCOM-1A)" % pol)
        p.gamma_virtuales.append(dict(nombre="Gamma0_%s" % pol, funcion=None, unidad="intensity",
            expr="(%s > 0 && incidenceAngleFromEllipsoid > 0) ? %s / cos(rad(incidenceAngleFromEllipsoid)) : NaN" % (nsig, nsig),
            desc="gamma0 %s lineal sobre el elipsoide = sigma0 / cos(angulo de incidencia) (banda virtual)" % pol,
            valida="%s > 0" % nsig))
    co, cruz = ("HH", "HV") if "HH" in pols else ("VV", "VH")
    A.agregar_db_y_cociente(p, "%s_%s" % (pref, co), "%s_%s" % (pref, cruz), co, cruz, "gamma0")
    for pol in pols:
        if pol not in (co, cruz):
            p.virtual("%s_%s_db" % (pref, pol), "%s_%s > 0 ? 10*log10(%s_%s) : NaN" % (pref, pol, pref, pol),
                      (lambda nb: (lambda pr: A.db(pr.datos(nb))))("%s_%s" % (pref, pol)), "dB",
                      "gamma0 %s en dB (banda virtual)" % pol, "%s_%s > 0" % (pref, pol))
    try:
        p.metadatos = A.xml_a_arbol(dim)
    except Exception:                                    # noqa: BLE001
        p.metadatos = {}
    p.inicio = p.fin = fecha
    p.tipo = "SAOCOM_1A_SM_SLC_sigma0_y_gamma0_elipsoide_SNAP"
    p.cita = cita
    p.recorte = A._doc_recorte(SITIO, "pixel 10 m, EPSG:32721 (SNAP Terrain-Correction)")
    return p


def una_banda(p, banda, carpeta):
    """GeoTIFF LINEAL de una sola banda (lo que leen Tp5_01 y Tp2_01)."""
    import rasterio
    from rasterio.crs import CRS
    ruta = os.path.join(carpeta, "%s_%s.tif" % (p.nombre, banda))
    a = p.datos(banda).astype("float32")
    a = np.where(a > 0, a, np.nan).astype("float32")
    with rasterio.open(ruta, "w", driver="GTiff", width=p.ancho, height=p.alto, count=1, dtype="float32",
                       crs=CRS.from_wkt(p.crs_wkt), transform=p.transform, nodata=np.nan, compress="deflate",
                       predictor=3, tiled=True, blockxsize=512, blockysize=512) as d:
        d.write(a, 1)
        d.set_band_description(1, banda)
        d.update_tags(FUENTE=p.cita, UNIDAD="lineal (potencia); dB = 10*log10", PROGRAMA=PROGRAMA)
    return ruta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rehacer", action="store_true")
    a = ap.parse_args()
    gpt = A.gpt_snap()
    if not gpt:
        sys.exit("No se encontro gpt.exe de SNAP (C:\\Program Files\\esa-snap*\\bin). Definir SNAP_GPT.")
    print("SNAP gpt: %s" % gpt)
    origen = ruta_tp("Tp5", "02_Subsets_SNAP_QGIS", "SNAP_DIMAP")
    base = ruta_tp("Tp5", "02_Subsets_SNAP_QGIS", "SAOCOM_gamma0")
    c_dim, c_tif, c_rgb, c_g = [os.path.join(base, x) for x in
                                ("SNAP_DIMAP", "QGIS_GeoTIFF", "RGB_copol_cruzada_cociente", "Grafos_SNAP")]
    for c in (c_dim, c_tif, c_rgb, c_g):
        os.makedirs(c, exist_ok=True)
    filas = []
    for etiqueta, (fecha, cuando, pols) in ESCENAS.items():
        entrada = os.path.join(origen, "%s_%s.dim" % (SITIO, etiqueta))
        print("\n=== %s (%s) ===" % (etiqueta, fecha))
        if not os.path.exists(entrada):
            print("  FALTA %s: correr armar_subsets.py Tp5" % entrada)
            continue
        hecho = None
        for magnitud, aplanar in (("gamma0", False),):
            nombre = "%s_%s_%s" % (SITIO, etiqueta, magnitud)
            dim = os.path.join(c_dim, nombre + ".dim")
            xml = os.path.join(c_g, "Grafo_%s.xml" % nombre)
            with open(xml, "w", encoding="utf-8") as f:
                f.write(grafo(entrada, dim, pols, aplanar))
            if os.path.exists(dim) and not a.rehacer:
                print("  Ya estaba: %s" % dim)
                hecho = (nombre, dim, xml, magnitud)
                break
            print("  SNAP procesando a %s (calibracion, multilook, %sspeckle, correccion)..."
                  % (magnitud, "aplanado, " if aplanar else ""))
            t0 = time.time()
            ok, err = correr(gpt, xml, dim, os.path.join(c_dim, "_registro_gpt_%s.txt" % nombre))
            if ok:
                print("  SNAP termino en %.0f min" % ((time.time() - t0) / 60))
                hecho = (nombre, dim, xml, magnitud)
                break
            print("  SNAP no pudo hacer %s:\n  %s" % (magnitud, err.replace("\n", "\n  ")))
        if not hecho:
            continue
        nombre, dim, xml, magnitud = hecho
        cita = ("CONAE. SAOCOM-1A StripMap %s, SLC, %s (%s). Archivo del curso SAR CEREGEO 2023 "
                "(https://catalogos.conae.gov.ar). Procesado a %s sobre el elipsoide con ESA SNAP (Copernicus DEM GLO-30)."
                % ("doble polarizacion VV+VH" if len(pols) == 2 else "cuadripolar HH HV VH VV",
                   "%s/%s/%s" % (fecha[8:], fecha[5:7], fecha[:4]), cuando, magnitud))
        p = a_producto(dim, nombre, magnitud, pols, cita, fecha)
        if not p.bandas:
            print("  El .dim no tiene bandas %s_*: revisar %s" % (magnitud, dim))
            continue
        rec = dict(p.recorte)
        rec.update(programa=PROGRAMA, fecha=_dt.datetime.now().strftime("%d/%m/%Y %H:%M"), fuente=cita,
                   grafo=os.path.basename(xml), entrada=os.path.basename(entrada))
        A.agregar_virtuales_a_dim(dim, p.gamma_virtuales + p.virtuales, rec)
        t = A.escribir_geotiff(p, c_tif)
        sueltos = [una_banda(p, b["nombre"], c_tif) for b in p.bandas]
        rgb = A.escribir_rgb(p, c_rgb)
        ctrl = A.control_snap(gpt, [dim], os.path.join(base, "_control_snap_tmp"), SITIO).get(dim, "")
        validos = [round(100.0 * float((b["datos"] > 0).mean()), 1) for b in p.bandas]
        print("  .dim: %s\n  GeoTIFF: %s\n  Una banda: %s\n  RGB: %s\n  Control SNAP: %s"
              % (dim, t, ", ".join(os.path.basename(s) for s in sueltos), rgb, ctrl))
        filas.append((nombre, fecha, cuando, magnitud, pols, [os.path.basename(s) for s in sueltos], validos, ctrl, cita))
    if not filas:
        print("\nNo se proceso ninguna escena.")
        return
    leeme = os.path.join(base, "LEEME_SAOCOM_gamma0.md")
    with open(leeme, "w", encoding="utf-8") as f:
        f.write("# SAOCOM-1A del Delta procesado a gamma0 (SNAP)\n\n"
                "Hecho con `00_COMUN\\procesar_saocom.py` desde los recortes SLC de `..\\SNAP_DIMAP` "
                "(ESA SNAP, gpt). Cadena: calibracion a sigma0 (los SLC de CONAE ya vienen calibrados: |DN|^2 = "
                "sigma0), multilook a pixel cuadrado, filtro Refined Lee y Range-Doppler Terrain-Correction a 10 m en "
                "EPSG:32721 (Copernicus DEM 30 m), con el angulo de incidencia sobre el elipsoide. gamma0 = sigma0 / "
                "cos(angulo de incidencia): normalizacion sobre el elipsoide, no Terrain-Flattening (con SAOCOM, el "
                "Terrain-Flattening de SNAP 14 da entre 5 y 10 dB menos; comparado con el mosaico ALOS-2 2020 y con "
                "NISAR GCOV). En las islas del Delta, llanas, la diferencia con un gamma0 aplanado es chica. El grafo de cada producto esta en `Grafos_SNAP` "
                "(SNAP: Tools > Graph Builder > Load).\n\n"
                "| Carpeta | Que hay |\n|---|---|\n"
                "| `SNAP_DIMAP` | sigma0 LINEAL de cada polarizacion, angulo de incidencia, gamma0 (virtual) + bandas "
                "virtuales en dB y cociente co/cruzada en dB; metadatos de SNAP completos |\n"
                "| `QGIS_GeoTIFF` | `<nombre>.tif`: todas las bandas (lineal y dB). `<nombre>_Gamma0_<POL>.tif`: UNA "
                "banda lineal, para Python (Tp5_01 `--saocom_pre_hv` / `--saocom_post_hv`, Tp2_01 `--extra`) |\n"
                "| `RGB_copol_cruzada_cociente` | Cuadripolares: R = HH, G = HV, B = HH/HV. Doble polarizacion: "
                "R = VV, G = VH, B = VV/VH. En dB y en 8 bits con rangos fijos |\n"
                "| `Grafos_SNAP` | El grafo XML de cada producto |\n\n")
        for nombre, fecha, cuando, magnitud, pols, sueltos, validos, ctrl, cita in filas:
            f.write("## %s\n\n- Fecha: %s (%s). Polarizaciones: %s. Magnitud: **%s**%s.\n"
                    "- GeoTIFF de una banda: %s\n- Pixeles con dato en el sitio: %s %%\n- Control SNAP: %s\n"
                    "- Fuente: %s\n\n"
                    % (nombre, fecha, cuando, " ".join(pols), magnitud,
                       "" if magnitud == "gamma0" else " (SNAP no acepto el Terrain-Flattening; no es gamma0)",
                       ", ".join("`%s`" % s for s in sueltos), " / ".join(str(v) for v in validos), ctrl, cita))
    print("\nLEEME: %s\nFIN" % leeme)


if __name__ == "__main__":
    main()
