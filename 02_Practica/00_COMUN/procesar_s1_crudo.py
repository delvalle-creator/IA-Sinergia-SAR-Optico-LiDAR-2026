# -*- coding: utf-8 -*-
"""
procesar_s1_crudo.py - Sentinel-1 GRDH sin procesar -> gamma0 con SNAP (gpt), por sitio.

Es el camino que se ensena en clase, hecho una vez por el docente como
referencia. Entrada: los .zip de 08_Originales_crudos\\S1_CRUDO (datos_crudos.py
s1_crudo). Cadena (grafo de SNAP, se guarda para abrirlo en Graph Builder):

  Read -> ThermalNoiseRemoval -> Remove-GRD-Border-Noise (en cada cuadro)
  (-> S-1 Slice Assembly si el sitio necesita dos cuadros: La Paz-Villaguay)
  -> Apply-Orbit-File (orbita precisa)
  -> Calibration a beta0 (lo que pide Terrain-Flattening)
  -> Subset al sitio (caja + 0,02 grados de margen)
  -> Terrain-Flattening (Copernicus DEM 30 m) -> gamma0 normalizado por el terreno
  -> Speckle-Filter (Refined Lee)
  -> Range-Doppler Terrain-Correction (Copernicus DEM 30 m, 10 m, UTM automatico)
  -> BEAM-DIMAP

Despues el programa agrega al .dim las bandas VIRTUALES en dB y el cociente
VV/VH en dB, escribe el GeoTIFF (lineal + dB, con _metadatos.txt) y el RGB
VV-VH-VV/VH, y COMPARA con el gamma0 RTC del Planetary Computer de la misma
fecha (que ya viene corregido): diferencia mediana en dB y correlacion.

Salida, en el practico de cada sitio:
  <Tp>\\02_Subsets_SNAP_QGIS\\S1_procesado_desde_crudo\\
      SNAP_DIMAP, QGIS_GeoTIFF, RGB_copol_cruzada_cociente, Grafos_SNAP, LEEME_S1_crudo.md

USO (Miniforge Prompt, entorno sar):
    python D:\\CURSOS_CEREGEO_2026\\02_Practica\\00_COMUN\\procesar_s1_crudo.py            (todos los sitios)
    python ...\\procesar_s1_crudo.py --sitios C_FEDERAL                                   (uno)
    python ...\\procesar_s1_crudo.py --rehacer                                            (pisa lo hecho)
SNAP baja solo la orbita y el Copernicus DEM la primera vez (hace falta internet).
"""
import argparse
import datetime as _dt
import glob
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import armar_subsets as A                                          # noqa: E402
from configuracion_comun import ORIGINALES, SITIOS, ruta_tp         # noqa: E402

PROGRAMA = "00_COMUN/procesar_s1_crudo.py"
# sitio -> (practico, escenas en orden de la pasada)
SITIOS_S1 = {
    "A1_DELTA_QUEMAS": ("Tp5", ["S1A_IW_GRDH_1SDV_20200908T091510_20200908T091535_034265_03FB78_6C2A"]),
    "A2_IBICUY": ("Tp2", ["S1C_IW_GRDH_1SDV_20260926T091407_20260926T091432_009616_013235_EE65"]),
    "B_CONCORDIA": ("Tp6", ["S1A_IW_GRDH_1SDV_20231104T091449_20231104T091514_051065_06285B_E987"]),
    "F_BOVRIL": ("Tp8", ["S1A_IW_GRDH_1SDV_20230917T091449_20230917T091514_050365_061067_C33B"]),
    "C_FEDERAL": ("Tp9", ["S1C_IW_GRDH_1SDV_20260914T091317_20260914T091342_009441_012C7A_AB47"]),
    "D_LAPAZ_VILLAGUAY": ("Tp9", ["S1C_IW_GRDH_1SDV_20260914T091317_20260914T091342_009441_012C7A_AB47",
                                  "S1C_IW_GRDH_1SDV_20260914T091342_20260914T091407_009441_012C7A_4769"]),
}
DEM = "Copernicus 30m Global DEM"


def nodo(id_, op, fuentes, params):
    src = "".join("<sourceProduct%s refid=\"%s\"/>" % ("" if i == 0 else ".%d" % i, f) for i, f in enumerate(fuentes))
    par = "".join("<%s>%s</%s>" % (k, escape(str(v)), k) for k, v in params.items())
    return ("  <node id=\"%s\">\n    <operator>%s</operator>\n    <sources>%s</sources>\n"
            "    <parameters class=\"com.bc.ceres.binding.dom.XppDomElement\">%s</parameters>\n  </node>\n"
            % (id_, op, src, par))


def grafo(zips, wkt, salida, aplanar=True):
    g = "<graph id=\"S1_GRD_a_gamma0\">\n  <version>1.0</version>\n"
    # ruido termico y de borde ANTES de unir cuadros: cada cuadro trae sus propios vectores de ruido
    lecturas = []
    for i, z in enumerate(zips):
        k = i + 1
        g += nodo("Read_%d" % k, "Read", [], {"file": z, "copyMetadata": "true"})
        g += nodo("Ruido_termico_%d" % k, "ThermalNoiseRemoval", ["Read_%d" % k], {"removeThermalNoise": "true"})
        g += nodo("Ruido_de_borde_%d" % k, "Remove-GRD-Border-Noise", ["Ruido_termico_%d" % k],
                  {"borderLimit": 500, "trimThreshold": 0.5})
        lecturas.append("Ruido_de_borde_%d" % k)
    prev = lecturas[0]
    if len(lecturas) > 1:
        g += nodo("Slice_Assembly", "SliceAssembly", lecturas, {"selectedPolarisations": "VH,VV"})
        prev = "Slice_Assembly"
    pasos = [
        ("Orbita", "Apply-Orbit-File", {"orbitType": "Sentinel Precise (Auto Download)", "polyDegree": 3,
                                        "continueOnFail": "true"}),
        ("Calibracion_beta0", "Calibration", {"outputBetaBand": "true", "outputSigmaBand": "false",
                                              "outputImageScaleInDb": "false"}) if aplanar else
        ("Calibracion_sigma0", "Calibration", {"outputBetaBand": "false", "outputSigmaBand": "true",
                                               "outputImageScaleInDb": "false"}),
        ("Recorte_al_sitio", "Subset", {"geoRegion": wkt, "copyMetadata": "true"}),
        ("Aplanado_del_terreno", "Terrain-Flattening", {"demName": DEM, "demResamplingMethod": "BILINEAR_INTERPOLATION",
                                                        "oversamplingMultiple": 1.5, "additionalOverlap": 0.1,
                                                        "nodataValueAtSea": "false", "outputSimulatedImage": "false"}),
        ("Filtro_speckle", "Speckle-Filter", {"filter": "Refined Lee"}),
        ("Correccion_geometrica", "Terrain-Correction", {"demName": DEM, "demResamplingMethod": "BILINEAR_INTERPOLATION",
                                                         "imgResamplingMethod": "BILINEAR_INTERPOLATION",
                                                         "pixelSpacingInMeter": 10.0, "mapProjection": "AUTO:42001",
                                                         "nodataValueAtSea": "false", "saveSelectedSourceBand": "true"}),
    ]
    if not aplanar:
        pasos = [x for x in pasos if x[1] != "Terrain-Flattening"]
        tc = dict(pasos[-1][2], saveDEM="true", saveIncidenceAngleFromEllipsoid="true",
                  saveLocalIncidenceAngle="true")
        pasos[-1] = (pasos[-1][0], pasos[-1][1], tc)
    for id_, op, par in pasos:
        g += nodo(id_, op, [prev], par)
        prev = id_
    g += nodo("Write", "Write", [prev], {"file": salida, "formatName": "BEAM-DIMAP"})
    return g + "</graph>\n"


def a_producto(dim, nombre, sitio, cita, inicio):
    import rasterio
    datos = os.path.splitext(dim)[0] + ".data"
    p = A.Producto(nombre)
    for pol in ("VV", "VH"):
        img = glob.glob(os.path.join(datos, "Gamma0_%s*.img" % pol))
        if not img:
            continue
        with rasterio.open(img[0]) as r:
            arr = r.read(1).astype("float32")
            p.transform, p.crs_wkt = r.transform, A._wkt(r.crs)
        arr[~np.isfinite(arr) | (arr <= 0)] = 0.0
        p.banda("Gamma0_" + pol, arr, "intensity", "gamma0 %s LINEAL (Terrain-Flattening + Refined Lee + "
                "Terrain-Correction en SNAP, desde el GRDH sin procesar)" % pol)
    A.agregar_db_y_cociente(p, "Gamma0_VV", "Gamma0_VH", "VV", "VH", "gamma0")
    try:
        p.metadatos = A.xml_a_arbol(dim)
    except Exception:                                    # noqa: BLE001
        p.metadatos = {}
    p.inicio = p.fin = inicio
    p.tipo = "S1_IW_GRDH_procesado_a_gamma0_en_SNAP"
    p.cita = cita
    p.recorte = A._doc_recorte(sitio, "pixel 10 m y UTM automatico de SNAP Terrain-Correction")
    return p


def comparar_con_rtc(p, sitio, fecha):
    import rasterio
    from rasterio.crs import CRS
    from rasterio.enums import Resampling
    from rasterio.warp import reproject
    carp = [c for c in sorted(glob.glob(os.path.join(ORIGINALES, "PLANETARY", sitio, "sentinel-1-rtc", fecha + "_*")))
            if os.path.exists(os.path.join(c, "vv.tif"))]
    if not carp:
        return "no hay RTC del Planetary Computer del %s para comparar" % fecha
    filas = []
    for pol in ("vv", "vh"):
        arr, tr, crs, nd = A.mosaico([os.path.join(c, pol + ".tif") for c in carp
                                      if os.path.exists(os.path.join(c, pol + ".tif"))], sitio)
        arr = arr.astype("float32")
        arr[(arr <= 0) | ~np.isfinite(arr)] = np.nan
        dst = np.full((p.alto, p.ancho), np.nan, "float32")
        # el RTC (10 m) se lleva a la grilla de SNAP por promedio en LINEAL
        reproject(arr, dst, src_transform=tr, src_crs=crs, dst_transform=p.transform,
                  dst_crs=CRS.from_wkt(p.crs_wkt), resampling=Resampling.average, src_nodata=np.nan, dst_nodata=np.nan)
        nuestro = p.datos("Gamma0_" + pol.upper()).astype("float32")
        ok = np.isfinite(dst) & (dst > 0) & (nuestro > 0)
        if ok.sum() < 1000:
            filas.append("%s: menos de 1000 pixeles en comun" % pol.upper())
            continue
        a, b = 10 * np.log10(nuestro[ok]), 10 * np.log10(dst[ok])
        filas.append("%s: diferencia mediana (SNAP - RTC) %+.2f dB, p5 a p95 %+.1f a %+.1f dB, correlacion %.2f, "
                     "%d pixeles" % (pol.upper(), np.median(a - b), np.percentile(a - b, 5),
                                     np.percentile(a - b, 95), np.corrcoef(a, b)[0, 1], ok.sum()))
    return "; ".join(filas)


CLASES = [(0, 1), (1, 3), (3, 10), (10, 90)]


def comparar_aplanado(dim_g, dim_s, sitio, nombre, carpeta, cita):
    """gamma0 aplanado vs sigma0 sin aplanar, por clase de pendiente.

    D = gamma0_aplanado(dB) - sigma0(dB). En terreno PLANO, gamma0 = sigma0 / cos(tita) y
    D_plano = -10 log10(cos tita_elipsoide): es solo la normalizacion por el angulo de incidencia.
    R = D - D_plano es lo que agrega el RELIEVE. Pendiente: del Copernicus DEM que guarda SNAP."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject

    def leer(dim, patron):
        f = glob.glob(os.path.join(os.path.splitext(dim)[0] + ".data", patron))
        if not f:
            return None, None, None
        with rasterio.open(f[0]) as r:
            return r.read(1).astype("float32"), r.transform, r.crs
    g, tg, cg = leer(dim_g, "Gamma0_VV*.img")
    filas = []
    s0, ts, cs = leer(dim_s, "Sigma0_VV*.img")
    ele, _, _ = leer(dim_s, "elevation*.img")
    inc, _, _ = leer(dim_s, "incidenceAngleFromEllipsoid*.img")
    if g is None or s0 is None or ele is None or inc is None:
        return "faltan bandas para comparar", []
    def a_grilla(a):
        out = np.full(g.shape, np.nan, "float32")
        reproject(a, out, src_transform=ts, src_crs=cs, dst_transform=tg, dst_crs=cg,
                  resampling=Resampling.nearest, src_nodata=0, dst_nodata=np.nan)
        return out
    s0, ele, inc = a_grilla(s0), a_grilla(ele), a_grilla(inc)
    dy, dx = np.gradient(ele, abs(tg.e), tg.a)
    pend = np.degrees(np.arctan(np.hypot(dx, dy)))
    ok = (g > 0) & (s0 > 0) & np.isfinite(pend) & np.isfinite(inc)
    D = 10 * np.log10(g[ok]) - 10 * np.log10(s0[ok])
    Dp = -10 * np.log10(np.cos(np.radians(inc[ok])))
    R, P = D - Dp, pend[ok]
    # En la clase plana (0 a 1 grado) R deberia ser 0. Si no lo es, es una diferencia de NORMALIZACION de
    # SNAP Terrain-Flattening (igual en todo el sitio), no del relieve: se informa aparte y se descuenta.
    plano = P < 1
    base_snap = float(np.median(R[plano])) if plano.sum() > 100 else 0.0
    R = R - base_snap
    lineas = ["Desfase de normalizacion de SNAP Terrain-Flattening (clase 0 a 1 grado, donde el relieve no "
              "aporta): %+.2f dB respecto de sigma0/cos(tita)" % base_snap]
    for lo, hi in CLASES:
        m = (P >= lo) & (P < hi)
        if m.sum() < 100:
            continue
        fila = dict(pendiente="%d a %d grados" % (lo, hi), pct_del_sitio=round(100 * m.mean(), 1),
                    diferencia_total_dB=round(float(np.median(D[m])), 2),
                    parte_angulo_incidencia_dB=round(float(np.median(Dp[m])), 2),
                    desfase_normalizacion_SNAP_dB=round(base_snap, 2),
                    parte_relieve_mediana_dB=round(float(np.median(R[m])), 2),
                    parte_relieve_p5_dB=round(float(np.percentile(R[m], 5)), 2),
                    parte_relieve_p95_dB=round(float(np.percentile(R[m], 95)), 2))
        filas.append(fila)
        lineas.append("pendiente %s (%.1f %% del sitio): diferencia %.2f dB = angulo %.2f %+.2f desfase SNAP "
                      "+ relieve %.2f (p5 a p95 del relieve %+.2f a %+.2f)" % (fila["pendiente"], fila["pct_del_sitio"],
                      fila["diferencia_total_dB"], fila["parte_angulo_incidencia_dB"], base_snap,
                      fila["parte_relieve_mediana_dB"], fila["parte_relieve_p5_dB"], fila["parte_relieve_p95_dB"]))
    import pandas as pd
    csv = os.path.join(carpeta, "%s_aplanado_vs_sin_aplanar.csv" % nombre)
    pd.DataFrame(filas).to_csv(csv, index=False, encoding="utf-8-sig")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7.5, 4.6))
        x = np.arange(len(filas))
        ax.bar(x - 0.3, [f["parte_angulo_incidencia_dB"] for f in filas], 0.3, label="angulo de incidencia")
        ax.bar(x, [base_snap for f in filas], 0.3, label="desfase de normalizacion de SNAP")
        ax.bar(x + 0.3, [f["parte_relieve_mediana_dB"] for f in filas], 0.3, label="relieve (mediana)")
        ax.errorbar(x + 0.3, [f["parte_relieve_mediana_dB"] for f in filas],
                    yerr=[[f["parte_relieve_mediana_dB"] - f["parte_relieve_p5_dB"] for f in filas],
                          [f["parte_relieve_p95_dB"] - f["parte_relieve_mediana_dB"] for f in filas]],
                    fmt="none", ecolor="k", capsize=4, label="relieve p5 a p95")
        ax.set_xticks(x)
        ax.set_xticklabels(["%s\n(%.0f %% del sitio)" % (f["pendiente"], f["pct_del_sitio"]) for f in filas])
        ax.set_ylabel("gamma0 aplanado - sigma0 (dB)")
        ax.axhline(0, color="0.5", lw=0.8)
        ax.legend(fontsize=8)
        ax.set_title("%s: que agrega el aplanado del terreno" % sitio, fontsize=10)
        fig.text(0.01, 0.01, "Fuente: " + cita, fontsize=6, wrap=True)
        fig.tight_layout(rect=(0, 0.08, 1, 1))
        fig.savefig(os.path.join(carpeta, "%s_aplanado_vs_sin_aplanar.png" % nombre), dpi=150)
        plt.close(fig)
    except Exception as e:                               # noqa: BLE001
        lineas.append("(sin figura: %s)" % e)
    return "\n".join(lineas), filas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitios", nargs="*", default=list(SITIOS_S1))
    ap.add_argument("--rehacer", action="store_true")
    ap.add_argument("--sin_aplanar", action="store_true",
                    help="ademas procesa sigma0 SIN Terrain-Flattening y compara por clase de pendiente")
    a = ap.parse_args()
    gpt = A.gpt_snap()
    if not gpt:
        sys.exit("No se encontro gpt.exe de SNAP (C:\\Program Files\\esa-snap*\\bin). Definir SNAP_GPT.")
    print("SNAP gpt: %s" % gpt)
    crudo = os.path.join(ORIGINALES, "S1_CRUDO")
    for sitio in a.sitios:
        tp, escenas = SITIOS_S1[sitio]
        zips = []
        for n in escenas:
            z = os.path.join(crudo, n + ".zip")
            if not os.path.exists(z) and n.endswith("_____"):
                # identificador final desconocido: el .zip que bajo datos_crudos.py para esa pasada
                cand = sorted(glob.glob(os.path.join(crudo, n[:-5] + "_????.zip")))
                if not cand:
                    cand = sorted(glob.glob(os.path.join(crudo, n[:3] + "_IW_GRDH_1SDV_" + n[17:25] + "T*_"
                                                         + "_".join(n.split("_")[-3:-1]) + "_????.zip")))
                if cand:
                    z = cand[0]
                    print("  Escena: %s" % os.path.basename(z))
            zips.append(z)
        falta = [z for z in zips if not os.path.exists(z)]
        print("\n=== %s (%s) ===" % (sitio, tp))
        if falta:
            print("  FALTA %s: correr datos_crudos.py s1_crudo" % ", ".join(os.path.basename(z) for z in falta))
            continue
        fecha = escenas[0][17:25]
        nombre = "%s_S1_%s_gamma0_desde_crudo" % (sitio, fecha)
        base = ruta_tp(tp, "02_Subsets_SNAP_QGIS", "S1_procesado_desde_crudo")
        c_dim, c_tif, c_rgb, c_g = [os.path.join(base, x) for x in
                                    ("SNAP_DIMAP", "QGIS_GeoTIFF", "RGB_copol_cruzada_cociente", "Grafos_SNAP")]
        for c in (c_dim, c_tif, c_rgb, c_g):
            os.makedirs(c, exist_ok=True)
        dim = os.path.join(c_dim, nombre + ".dim")
        o, s_, e, n = SITIOS[sitio]["bbox"]
        m = 0.02
        wkt = "POLYGON((%f %f, %f %f, %f %f, %f %f, %f %f))" % (o - m, n + m, e + m, n + m, e + m, s_ - m,
                                                            o - m, s_ - m, o - m, n + m)
        xml = os.path.join(c_g, "Grafo_%s.xml" % nombre)
        with open(xml, "w", encoding="utf-8") as f:
            f.write(grafo(zips, wkt, dim))
        print("  Grafo: %s" % xml)
        if a.rehacer or not os.path.exists(dim):
            t0 = time.time()
            print("  SNAP procesando (orbita, ruido, beta0, recorte, aplanado, speckle, correccion)... puede tardar 10-30 min")
            r = subprocess.run([gpt, xml, "-c", "4G", "-q", "8"], capture_output=True, text=True, errors="replace")
            reg = os.path.join(c_dim, "_registro_gpt_%s.txt" % nombre)
            with open(reg, "w", encoding="utf-8") as f:
                f.write("CODIGO: %s\nSALIDA:\n%s\nERRORES:\n%s\n" % (r.returncode, r.stdout, r.stderr))
            if r.returncode != 0 or not os.path.exists(dim):
                print("  ERROR de SNAP; detalle en %s" % reg)
                print("  " + (r.stderr or r.stdout)[-600:].replace("\n", "\n  "))
                continue
            print("  SNAP termino en %.0f min" % ((time.time() - t0) / 60))
        else:
            print("  Ya estaba: %s" % dim)
        plat = escenas[0][:3].replace("S1", "Sentinel-1")
        cita = ("ESA Copernicus. %s IW GRDH (nivel 1, sin procesar), %s-%s-%s, %s. Distribuido por ASF DAAC "
                "(https://search.asf.alaska.edu). Procesado a gamma0 con ESA SNAP (Copernicus DEM GLO-30)."
                % (plat, fecha[:4], fecha[4:6], fecha[6:], " + ".join(os.path.basename(z)[:-4] for z in zips)))
        p = a_producto(dim, nombre, sitio, cita, "%s-%s-%s" % (fecha[:4], fecha[4:6], fecha[6:]))
        rec = dict(p.recorte)
        rec.update(programa=PROGRAMA, fecha=_dt.datetime.now().strftime("%d/%m/%Y %H:%M"), fuente=cita,
                   grafo=os.path.basename(xml))
        A.agregar_virtuales_a_dim(dim, p.virtuales, rec)
        t = A.escribir_geotiff(p, c_tif)
        rgb = A.escribir_rgb(p, c_rgb)
        comp = comparar_con_rtc(p, sitio, fecha)
        ctrl = A.control_snap(gpt, [dim], os.path.join(base, "_control_snap_tmp"), sitio).get(dim, "")
        print("  .dim: %s\n  GeoTIFF: %s\n  RGB: %s" % (dim, t, rgb))
        print("  Comparacion con el RTC del Planetary Computer: %s" % comp)
        print("  Control SNAP: %s" % ctrl)
        comp_ap = ""
        if a.sin_aplanar:
            nom_s = nombre.replace("_gamma0_", "_sigma0_sin_aplanar_")
            dim_s = os.path.join(c_dim, nom_s + ".dim")
            xml_s = os.path.join(c_g, "Grafo_%s.xml" % nom_s)
            with open(xml_s, "w", encoding="utf-8") as f:
                f.write(grafo(zips, wkt, dim_s, aplanar=False))
            if a.rehacer or not os.path.exists(dim_s):
                print("  SNAP procesando sigma0 SIN aplanar (para comparar)...")
                r = subprocess.run([gpt, xml_s, "-c", "4G", "-q", "8"], capture_output=True, text=True, errors="replace")
                with open(os.path.join(c_dim, "_registro_gpt_%s.txt" % nom_s), "w", encoding="utf-8") as f:
                    f.write("CODIGO: %s\nSALIDA:\n%s\nERRORES:\n%s\n" % (r.returncode, r.stdout, r.stderr))
                if r.returncode != 0 or not os.path.exists(dim_s):
                    print("  ERROR de SNAP en sigma0: " + (r.stderr or r.stdout)[-400:])
                    continue
            ps = A.Producto(nom_s)
            ps.virtuales = [dict(nombre="Sigma0_VV_db", expr="Sigma0_VV > 0 ? 10*log10(Sigma0_VV) : NaN",
                                 funcion=None, unidad="dB", desc="sigma0 VV en dB (banda virtual)", valida="Sigma0_VV > 0"),
                            dict(nombre="Sigma0_VH_db", expr="Sigma0_VH > 0 ? 10*log10(Sigma0_VH) : NaN",
                                 funcion=None, unidad="dB", desc="sigma0 VH en dB (banda virtual)", valida="Sigma0_VH > 0")]
            A.agregar_virtuales_a_dim(dim_s, ps.virtuales, dict(rec, nota="sigma0 SIN Terrain-Flattening, para comparar"))
            comp_ap, _ = comparar_aplanado(dim, dim_s, sitio, nombre, base, cita)
            print("  Aplanado vs sin aplanar (VV), por pendiente:\n    " + comp_ap.replace("\n", "\n    "))
        leeme = os.path.join(base, "LEEME_S1_crudo.md")
        if os.path.exists(leeme):                       # se reemplaza la seccion de este producto si ya estaba
            import re as _re
            txt = open(leeme, encoding="utf-8").read()
            txt = _re.sub(r"## %s \(.*?(?=\n## |\Z)" % _re.escape(nombre), "", txt, flags=_re.S)
            open(leeme, "w", encoding="utf-8").write(txt.rstrip("\n") + "\n\n")
        nuevo = not os.path.exists(leeme)
        with open(leeme, "a", encoding="utf-8") as f:
            if nuevo:
                f.write("# Sentinel-1 procesado desde el GRDH sin procesar\n\n"
                        "Hecho con `00_COMUN\\procesar_s1_crudo.py` (ESA SNAP, gpt). Cadena: orbita precisa, "
                        "ruido termico, ruido de borde, calibracion a beta0, recorte al sitio, Terrain-Flattening "
                        "(gamma0), filtro Refined Lee y Range-Doppler Terrain-Correction a 10 m (Copernicus DEM 30 m). "
                        "El grafo de cada producto esta en `Grafos_SNAP` y se abre en SNAP con Tools > Graph Builder > Load.\n\n"
                        "| Carpeta | Que hay |\n|---|---|\n"
                        "| `SNAP_DIMAP` | gamma0 VV y VH LINEALES + bandas virtuales en dB y cociente VV/VH en dB; "
                        "metadatos de SNAP completos (Abstracted_Metadata, Original_Product_Metadata, Processing_Graph) |\n"
                        "| `QGIS_GeoTIFF` | Las mismas bandas, las de dB como bandas reales, y `_metadatos.txt` |\n"
                        "| `RGB_copol_cruzada_cociente` | R = VV, G = VH, B = VV/VH, en dB y en 8 bits con rangos fijos |\n"
                        "| `Grafos_SNAP` | El grafo XML de cada producto |\n\n")
            f.write("## %s (%s)\n\n- Fuente: %s\n- Comparacion con el RTC del Planetary Computer de la misma fecha: %s\n"
                    "- Control SNAP: %s\n- Armado: %s\n\n" % (nombre, sitio, cita, comp, ctrl,
                                                             _dt.datetime.now().strftime("%d/%m/%Y %H:%M")))
            if comp_ap:
                f.write("### Aplanado del terreno: gamma0 aplanado menos sigma0 sin aplanar (VV), por pendiente\n\n"
                        "En teoria, en terreno plano la diferencia es solo la normalizacion por el angulo de "
                        "incidencia (-10 log10 cos tita). Lo que sobra en la clase plana (0 a 1 grado) es un desfase "
                        "de normalizacion de SNAP, igual en todo el sitio; descontado ese desfase, lo que queda en cada "
                        "clase es el efecto del relieve. Tabla y figura: "
                        "`%s_aplanado_vs_sin_aplanar.csv/.png`.\n\n```\n%s\n```\n\n" % (nombre, comp_ap))
    print("\nFIN")


if __name__ == "__main__":
    main()
