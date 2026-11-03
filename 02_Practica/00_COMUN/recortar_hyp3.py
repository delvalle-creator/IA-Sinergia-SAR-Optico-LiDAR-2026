# -*- coding: utf-8 -*-
"""
recortar_hyp3.py - Recortes de los interferogramas HyP3 de un sitio para el practico.

Los 120 pares de Parana-Diamante pesan ~99 GB descomprimidos (cada par cubre
una franja de ~250 x 180 km). Este programa recorta cada par a la caja del
sitio, en su pixel (40 m) y proyeccion (UTM 20 S) NATIVOS, sin remuestrear, y
deja en <Tp>\\02_Subsets_SNAP_QGIS\\HyP3_<SITIO>:

  SNAP_DIMAP\\<SITIO>_HyP3_<fecha1>_<fecha2>.dim (+ .data)
      Bandas: amp (sigma0 potencia, LINEAL), corr, unw_phase (rad),
      los_disp y vert_disp (m), water_mask; banda VIRTUAL amp_db.
      Metadatos originales (archivo de parametros .txt, README y los .tif.xml)
      dentro del .dim, en Metadata > Original_Product_Metadata.

  QGIS_GeoTIFF\\<par>\\<par>_<capa>.tif
      Un GeoTIFF por capa con el MISMO nombre que el original de HyP3, sus
      etiquetas GDAL, su .tif.xml, el README y el .txt de parametros. Los
      programas del Tp10 leen esta carpeta tal cual:
          python Tp10_05_velocidad_subsidencia.py --sitio E_PARANA_DIAMANTE ^
              --carpeta ..\\02_Subsets_SNAP_QGIS\\HyP3_E_PARANA_DIAMANTE\\QGIS_GeoTIFF

  LEEME_HyP3.md con la lista de pares, la cita y el control de SNAP.

Se puede cortar y volver a correr: saltea los pares ya recortados (--rehacer
los pisa).

USO (Miniforge Prompt, entorno sar):
    python D:\\CURSOS_CEREGEO_2026\\02_Practica\\00_COMUN\\recortar_hyp3.py --sitio E_PARANA_DIAMANTE --tp Tp10
"""
import argparse
import datetime as _dt
import glob
import os
import re
import shutil
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import armar_subsets as A                                         # noqa: E402
from configuracion_comun import ORIGINALES, ruta_tp                # noqa: E402

CAPAS = [  # sufijo, unidad SNAP, descripcion
    ("amp", "intensity", "sigma0 en potencia LINEAL de la imagen de referencia (corregida geometricamente, no radiometricamente)"),
    ("corr", "", "coherencia interferometrica (0 a 1)"),
    ("unw_phase", "radian", "fase desenrollada (rad), relativa al punto de referencia de HyP3"),
    ("los_disp", "m", "desplazamiento en la linea de vision (m)"),
    ("vert_disp", "m", "desplazamiento vertical (m), positivo = ascenso, supone sin movimiento horizontal"),
    ("water_mask", "", "mascara de agua de HyP3 (1 = tierra, 0 = agua)"),
]
CITA = ("ASF DAAC HyP3 (2026), INSAR_GAMMA (GAMMA), Sentinel-1 IW SLC (ESA Copernicus), 10 x 2 looks, 40 m. "
        "https://hyp3-docs.asf.alaska.edu. Hogenson, K. et al. (2020). Hybrid Pluggable Processing Pipeline (HyP3). "
        "Zenodo. https://doi.org/10.5281/zenodo.4646138. Contiene datos Copernicus Sentinel modificados (2025-2026), "
        "procesados por ESA.")
PATRON = re.compile(r"(\d{8})T\d{6}_(\d{8})T\d{6}")


def txt_a_arbol(ruta):
    d = {}
    for linea in open(ruta, encoding="utf-8", errors="replace"):
        if ":" in linea:
            k, v = linea.split(":", 1)
            d[A._nombre_valido(k.strip())] = v.strip()
    return d


def recortar_capa(src_ruta, dst_ruta, sitio):
    import rasterio
    from rasterio.windows import from_bounds, Window
    with rasterio.open(src_ruta) as s:
        caja = A.caja_nativa(sitio, s.crs)
        w = from_bounds(*caja, transform=s.transform).round_offsets().round_lengths()
        w = w.intersection(Window(0, 0, s.width, s.height))
        arr = s.read(1, window=w)
        perfil = s.profile.copy()
        perfil.update(driver="GTiff", width=arr.shape[1], height=arr.shape[0],
                      transform=s.window_transform(w), compress="deflate",
                      predictor=3 if arr.dtype.kind == "f" else 2, tiled=True, blockxsize=256, blockysize=256,
                      BIGTIFF="IF_SAFER")
        tags = s.tags()
        desc = s.descriptions[0] if s.descriptions else None
        if dst_ruta:
            os.makedirs(os.path.dirname(dst_ruta), exist_ok=True)
            with rasterio.open(dst_ruta, "w", **perfil) as o:
                o.write(arr, 1)
                tags.update(RECORTE="%s, caja %s; pixel y proyeccion nativos; %s" % (
                    sitio, ", ".join("%.1f" % c for c in caja), A.PROGRAMA.replace("armar_subsets", "recortar_hyp3")))
                o.update_tags(**tags)
                if desc:
                    o.set_band_description(1, desc)
        return arr, s.window_transform(w), s.crs, s.nodata


def un_par(carpeta, sitio, c_dim, c_tif, rehacer):
    base = os.path.basename(carpeta)
    m = PATRON.search(base)
    nombre = "%s_HyP3_%s_%s" % (sitio, m.group(1), m.group(2))
    dim = os.path.join(c_dim, nombre + ".dim")
    d_tif = os.path.join(c_tif, base)
    if not rehacer and os.path.exists(dim) and os.path.exists(os.path.join(d_tif, base + "_vert_disp.tif")):
        return nombre, "ya estaba", dim
    p = A.Producto(nombre)
    for suf, unidad, desc in CAPAS:
        src = os.path.join(carpeta, "%s_%s.tif" % (base, suf))
        if not os.path.exists(src):
            continue
        arr, tr, crs, nd = recortar_capa(src, os.path.join(d_tif, os.path.basename(src)), sitio)
        arr = arr.astype("float32")
        p.banda(suf, arr, unidad, desc, nodata=0.0)
        if os.path.exists(src + ".xml"):
            shutil.copy2(src + ".xml", os.path.join(d_tif, os.path.basename(src) + ".xml"))
            p.archivos_meta.append(src + ".xml")
    p.transform, p.crs_wkt = tr, A._wkt(crs)
    p.virtual("amp_db", "amp > 0 ? 10*log10(amp) : NaN", lambda pr: A.db(pr.datos("amp")), "dB",
              "sigma0 de la imagen de referencia en dB (banda virtual: 10*log10 de amp)", "amp > 0")
    txt = os.path.join(carpeta, base + ".txt")
    readme = os.path.join(carpeta, base + ".README.md.txt")
    meta = {}
    if os.path.exists(txt):
        meta["Parametros_HyP3"] = txt_a_arbol(txt)
        shutil.copy2(txt, os.path.join(d_tif, os.path.basename(txt)))
        p.archivos_meta.append(txt)
    if os.path.exists(readme):
        meta["README"] = open(readme, encoding="utf-8", errors="replace").read()
        shutil.copy2(readme, os.path.join(d_tif, os.path.basename(readme)))
        p.archivos_meta.append(readme)
    for x in sorted(glob.glob(os.path.join(carpeta, "*.tif.xml"))):
        try:
            meta[A._nombre_valido(os.path.basename(x).replace(base + "_", ""))] = A.xml_a_arbol(x)
        except Exception:                                 # noqa: BLE001
            pass
    p.metadatos = meta
    t1, t2 = m.group(1), m.group(2)
    p.inicio = "%s-%s-%sT00:00:00" % (t1[:4], t1[4:6], t1[6:])
    p.fin = "%s-%s-%sT00:00:00" % (t2[:4], t2[4:6], t2[6:])
    p.tipo = "HyP3_INSAR_GAMMA"
    p.cita = CITA + " Par %s / %s." % (t1, t2)
    p.recorte = A._doc_recorte(sitio)
    p.recorte["carpeta_original"] = carpeta
    A.escribir_dim(p, c_dim)
    return nombre, "armado", dim


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", default="E_PARANA_DIAMANTE")
    ap.add_argument("--tp", default="Tp10")
    ap.add_argument("--rehacer", action="store_true")
    ap.add_argument("--controles", type=int, default=3, help="cuantos .dim abre SNAP para el control")
    a = ap.parse_args()
    origen = os.path.join(ORIGINALES, "HYP3", a.sitio)
    pares = sorted(d for d in glob.glob(os.path.join(origen, "*")) if os.path.isdir(d) and PATRON.search(d))
    salida = ruta_tp(a.tp, "02_Subsets_SNAP_QGIS", "HyP3_" + a.sitio)
    c_dim, c_tif = os.path.join(salida, "SNAP_DIMAP"), os.path.join(salida, "QGIS_GeoTIFF")
    print("Origen: %s (%d pares descomprimidos)\nSalida: %s\n" % (origen, len(pares), salida))
    if not pares:
        sys.exit("No hay pares descomprimidos: correr antes 09_Herramientas\\descomprimir_hyp3.py")
    informe, dims = [], []
    for k, c in enumerate(pares, 1):
        try:
            nombre, estado, dim = un_par(c, a.sitio, c_dim, c_tif, a.rehacer)
            informe.append((nombre, estado))
            if estado == "armado":
                dims.append(dim)
            print("[%3d/%d] %-10s %s" % (k, len(pares), estado, nombre))
        except Exception as e:                            # noqa: BLE001
            informe.append((os.path.basename(c), "ERROR: %s" % e))
            print("[%3d/%d] ERROR %s: %s" % (k, len(pares), os.path.basename(c), e))
    controles = {}
    gpt = A.gpt_snap()
    todos = sorted(glob.glob(os.path.join(c_dim, "*.dim")))
    muestra = [todos[i] for i in sorted(set(np.linspace(0, len(todos) - 1, min(a.controles, len(todos))).astype(int)))] if todos else []
    if gpt and muestra:
        print("\nControl: SNAP abre %d .dim (primero, del medio y ultimo)..." % len(muestra))
        controles = A.control_snap(gpt, muestra, os.path.join(salida, "_control_snap_tmp"), a.sitio)
        for d, r in controles.items():
            print("  %-50s %s" % (os.path.basename(d), r))
    elif not gpt:
        print("\nAVISO: no se encontro gpt.exe de SNAP; no se hizo el control.")
    tam = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(salida) for f in fs) / 2 ** 30
    with open(os.path.join(salida, "LEEME_HyP3.md"), "w", encoding="utf-8") as f:
        f.write("# Interferogramas HyP3 de `%s` recortados al sitio\n\n" % a.sitio)
        f.write("Armado con `00_COMUN\\recortar_hyp3.py --sitio %s --tp %s` el %s. %d pares, %.1f GB.\n\n"
                % (a.sitio, a.tp, _dt.datetime.now().strftime("%d/%m/%Y %H:%M"), len(todos), tam))
        f.write("Fuente: %s\n\n" % CITA)
        f.write("Píxel (40 m) y proyección (la de HyP3, UTM) **nativos**: sólo se recortó a la caja del sitio, "
                "sin remuestrear. HyP3 usa 0 como «sin dato».\n\n")
        f.write("| Carpeta | Qué hay |\n|---|---|\n")
        f.write("| `SNAP_DIMAP` | Un `.dim` por par: amp (sigma0 lineal), corr, unw_phase, los_disp, vert_disp, "
                "water_mask y la banda **virtual** amp_db. Metadatos originales en Metadata > "
                "Original_Product_Metadata (parámetros, README y los .tif.xml) |\n")
        f.write("| `QGIS_GeoTIFF\\<par>` | Un GeoTIFF por capa con el nombre original de HyP3, sus etiquetas, "
                "su `.tif.xml`, el README y el `.txt` de parámetros. Es la carpeta que lee `Tp10_05` con "
                "`--carpeta` |\n\n")
        f.write("Para la subsidencia:\n\n```\npython Tp10_05_velocidad_subsidencia.py --sitio %s ^\n"
                "    --carpeta ..\\02_Subsets_SNAP_QGIS\\HyP3_%s\\QGIS_GeoTIFF\n```\n\n" % (a.sitio, a.sitio))
        f.write("## Pares\n\n| Par | Estado |\n|---|---|\n")
        for n, e in informe:
            f.write("| `%s` | %s |\n" % (n, e))
        if controles:
            f.write("\n## Control con SNAP (muestra)\n\n")
            for d, r in controles.items():
                f.write("- `%s`: %s\n" % (os.path.basename(d), " ".join(r.split())))
    print("\nListo: %d pares, %.1f GB. LEEME: %s" % (len(todos), tam, os.path.join(salida, "LEEME_HyP3.md")))
    errores = [n for n, e in informe if e.startswith("ERROR")]
    if errores:
        print("Con error: %d (volver a correr; si persiste, avisar)" % len(errores))


if __name__ == "__main__":
    main()
