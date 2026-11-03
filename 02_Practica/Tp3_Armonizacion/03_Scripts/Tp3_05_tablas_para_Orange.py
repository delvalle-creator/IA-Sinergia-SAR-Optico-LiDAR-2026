# -*- coding: utf-8 -*-
"""
Tp3_05_tablas_para_Orange.py   [SE CORRE]   Tp3, despues de los pasos 4 y 6
====================================================================
Arma las tablas que leen los tres workflows de Orange del Tp3 (carpeta
08_Orange/datos) a partir de lo que escribieron los scripts del grupo. Asi
cada cifra que se ve en Orange sale de un programa del practico, no de una
tabla preparada aparte.

  datos/Tp3_huellas_LiDAR_en_el_cubo.csv
      una fila por huella (GEDI y ATL08) con las columnas que usan los
      workflows A y C: altura del dosel, clase de altura, plausible, radar en
      dB, NDVI, dias, terreno elipsoidal menos MDE, clase de MapBiomas, FH y
      CCI Biomass (AGB 2020 y 2024 y su desvio, leidos en el pixel de unos
      100 m que contiene la huella, sin remuestrear).
  datos/Tp3_corregistro_por_ventana.csv
      cada ventana de cada par medido con Tp3_02 (todas las tablas
      <SITIO>_corregistro_*.csv de 05_Resultados/04_Tablas) y el veredicto
      del par, con la columna "grupo" (diez categorias como maximo, para que
      Orange les de un color a todas).
  datos/Tp3_diferencias_de_fecha.csv
      las diferencias de fecha de Ibicuy y de Bovril (Tp3_01).
  datos/Tp3_contexto_pixeles_muestra.csv
      copia de la muestra de pixeles por clase de MapBiomas que escribe Tp3_04.

ENTRADAS (ya escritas por el grupo)
  04_Tablas_de_trabajo/<SITIO>_huellas_con_contexto.csv     (Tp3_03 y Tp3_04)
  02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/<SITIO>_CCI_Biomass_v7_AGB.tif
  05_Resultados/04_Tablas/*_corregistro_*.csv y *_diferencias_de_fecha.csv

USO
    python Tp3_05_tablas_para_Orange.py --sitio A2_IBICUY
"""
import argparse
import glob
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

from configuracion_comun import SITIOS, ruta_tp                       # noqa: E402
from funciones_comunes import Bitacora                                # noqa: E402

# ----------------------------------------------------------------- PARAMETROS
CLASES_ALTURA = [0, 3, 5, 10, 15, 20, 40, 1e9]
ROTULOS_ALTURA = ["< 3 m", "3-5 m", "5-10 m", "10-15 m", "15-20 m", "20-40 m", "40 m o mas"]   # mismo rotulo en tablas, figuras y texto
CLASES_AGB = [-0.5, 0.5, 20.5, 40.5, 60.5, 80.5, 1e9]
ROTULOS_AGB = ["0 Mg/ha", "1-20", "21-40", "41-60", "61-80", "mas de 80"]
NOMBRES_CORTOS = {"OPT_S2_B08": "S2 B08", "C_S1_gamma0_VV": "S1 RTC VV", "C_SNAP_gamma0_VV": "S1 SNAP VV",
                  "S_NovaSAR_sigma0_HH": "NovaSAR HH", "P_BIOMASS_gamma0_VH": "BIOMASS P VH",
                  "P_BIOMASS_gamma0_HH": "BIOMASS P HH", "OPT_L8_SR_B5": "Landsat 8 B5"}


def corto(n):
    if n in NOMBRES_CORTOS:
        return NOMBRES_CORTOS[n]
    p = n.split("_")
    if p[1] == "NISAR":
        return "NISAR %s %s" % (p[0], p[3])
    return n


def csv_orange(df, ruta, orden=None, tiempo=()):
    """CSV con el encabezado de tres filas de Orange (nombre, tipo, rol), para fijar el orden de las clases
    (por ejemplo, que "< 3 m" vaya primero y no al final) y el tipo de cada columna."""
    orden = orden or {}
    tipos = []
    for c in df.columns:
        if c in orden:
            tipos.append(" ".join(v.replace(" ", "\\ ") for v in orden[c]))
        elif c in tiempo:
            tipos.append("time")
        elif pd.api.types.is_numeric_dtype(df[c]):
            tipos.append("continuous")
        else:
            tipos.append("discrete")
    with open(ruta, "w", encoding="utf-8-sig", newline="") as f:
        f.write(",".join(df.columns) + "\n")
        f.write(",".join(tipos) + "\n")
        f.write(",".join("" for _ in df.columns) + "\n")
        df.to_csv(f, index=False, header=False)


def muestrear(ruta, banda, x, y):
    """Valor del pixel del raster (en su grilla propia) donde cae cada punto UTM 21 S."""
    import rasterio
    from pyproj import Transformer
    with rasterio.open(ruta) as s:
        xx, yy = Transformer.from_crs("EPSG:32721", s.crs, always_xy=True).transform(np.asarray(x), np.asarray(y))
        a = s.read(banda).astype("float32")
        if s.nodata is not None and not np.isnan(s.nodata):
            a[a == s.nodata] = np.nan
        f, c = rasterio.transform.rowcol(s.transform, xx, yy)
        f, c = np.asarray(f), np.asarray(c)
        ok = (f >= 0) & (f < s.height) & (c >= 0) & (c < s.width)
        v = np.full(len(f), np.nan, "float32")
        v[ok] = a[f[ok], c[ok]]
        return v, list(s.descriptions)


def main():
    ap = argparse.ArgumentParser(description="Arma las tablas de Orange del Tp3 desde las salidas de los scripts.")
    ap.add_argument("--sitio", default="A2_IBICUY", choices=list(SITIOS.keys()))
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp3", "05_Resultados", "06_Control_calidad"), "Tp3_05_%s" % a.sitio)
    dest = ruta_tp("Tp3", "08_Orange", "datos")
    os.makedirs(dest, exist_ok=True)

    # 1. huellas -----------------------------------------------------------------------------
    tabla = ruta_tp("Tp3", "04_Tablas_de_trabajo", "%s_huellas_con_contexto.csv" % a.sitio)
    if not os.path.exists(tabla):
        log("No existe %s: correr antes Tp3_03 y Tp3_04." % tabla)
        log.cerrar()
        return
    t = pd.read_csv(tabla, encoding="utf-8-sig", low_memory=False)
    g = t.producto == "gedi_l2a"
    o = pd.DataFrame({
        "producto": np.where(g, "GEDI L2A", "ICESat-2 ATL08"),
        "fecha_lidar": t.fecha_lidar,
        "anio": ["año " + str(f)[:4] for f in t.fecha_lidar],
        "altura_dosel_m": np.where(g, t.rh98, t.h_canopy).round(2),
        "plausible": np.where(t.plausible == 1, "si", "no (" + t.motivo_no_plausible.fillna("") + ")"),
    })
    o["clase_altura"] = pd.cut(o.altura_dosel_m, CLASES_ALTURA, right=False, labels=ROTULOS_ALTURA).astype(str)
    for nuevo, col in (("L_HV_dB", "L_NISAR_gamma0_HV_20260930_dB"), ("L_HH_dB", "L_NISAR_gamma0_HH_20260930_dB"),
                       ("S_HV_dB", "S_NISAR_gamma0_HV_20260930_dB"), ("C_VH_dB", "C_S1_gamma0_VH_dB"),
                       ("C_VV_dB", "C_S1_gamma0_VV_dB"), ("P_HH_dB", "P_BIOMASS_gamma0_HH_dB"),
                       ("P_VH_dB", "P_BIOMASS_gamma0_VH_dB")):
        o[nuevo] = t[col].round(2) if col in t else np.nan
    o["B08"] = t.OPT_S2_B08.round(4)
    o["NDVI"] = ((t.OPT_S2_B08 - t.OPT_S2_B04) / (t.OPT_S2_B08 + t.OPT_S2_B04)).round(3)
    o["n_pixeles"] = t.n_L_NISAR_gamma0_HV_20260930
    o["dias_al_radar_L"] = t.dias_L_NISAR_gamma0_HV_20260930
    o["dias_al_optico"] = t.dias_OPT_S2_B08
    o["terreno_elips_m"] = np.where(g, t.elev_lowestmode_elips, t.h_te_best_fit_elips).round(2)
    o["MDE_EGM2008_m"] = t.MDE_GLO30_m.round(2)
    o["elips_menos_MDE_m"] = (o.terreno_elips_m - o.MDE_EGM2008_m).round(2)
    o["clase_MapBiomas_2025"] = t.get("clase_MapBiomas_2025")
    o["FH_m"] = t.get("FH_m")
    o["FH_calidad"] = t.get("FH_calidad")
    o["FH_menos_LiDAR_m"] = (o.FH_m - o.altura_dosel_m).round(2)
    o["x"], o["y"] = t.x.round(1), t.y.round(1)
    f_cci = sorted(glob.glob(ruta_tp("Tp3", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", "%s_CCI_Biomass_*AGB.tif" % a.sitio)))
    if f_cci:
        _, desc = muestrear(f_cci[0], 1, t.x[:1], t.y[:1])
        for nom in ("AGB_2020", "AGB_2024", "AGB_SD_2024"):
            if nom in desc:
                o[nom] = muestrear(f_cci[0], desc.index(nom) + 1, t.x, t.y)[0]
        o["clase_AGB_2024"] = pd.cut(o.AGB_2024, CLASES_AGB, labels=ROTULOS_AGB).astype(str).replace("nan", "")
        log("CCI Biomass: %s; %d huellas fuera del recorte (sin AGB)." % (os.path.basename(f_cci[0]),
                                                                      int(o.AGB_2024.isna().sum())))
    csv_orange(o, os.path.join(dest, "Tp3_huellas_LiDAR_en_el_cubo.csv"),
               orden={"clase_altura": ROTULOS_ALTURA, "clase_AGB_2024": ROTULOS_AGB}, tiempo=("fecha_lidar",))
    log("Huellas para Orange: %d (%d plausibles)  ->  datos/Tp3_huellas_LiDAR_en_el_cubo.csv"
        % (len(o), int((o.plausible == "si").sum())))

    # 2. corregistro -------------------------------------------------------------------------
    filas = []
    for f in sorted(glob.glob(ruta_tp("Tp3", "05_Resultados", "04_Tablas", "*_corregistro_*.csv"))):
        c = pd.read_csv(f, encoding="utf-8-sig")
        if "veredicto" not in c or "mov" not in c:
            continue                          # tablas viejas o de otra herramienta
        sitio = os.path.basename(f).split("_corregistro_")[0]
        nombre_sitio = {"A2_IBICUY": "Ibicuy", "F_BOVRIL": "Bovril"}.get(sitio, sitio)
        if "NovaSAR" not in c.mov.iloc[0]:
            estado = "no aplica"
        elif f.endswith("_corregida.csv") or not (f.endswith("_sin_corregir.csv") or
                                                  os.path.exists(f.replace(".csv", "_corregida.csv"))):
            estado = "NovaSAR corregida"
        else:
            estado = "NovaSAR sin corregir"
        par = "%s / %s" % (corto(c.mov.iloc[0]), corto(c.ref.iloc[0]))
        if "pixel_m" in c and float(c.pixel_m.iloc[0]) != 20:
            par += " (%d m)" % c.pixel_m.iloc[0]
        for r in c.itertuples(index=False):
            i, j = (int(v) for v in r.ventana.split(","))
            filas.append({"sitio": nombre_sitio, "par": par,
                          "par_y_estado": "%s: %s%s" % (nombre_sitio, par, "" if estado == "no aplica" else " (" + estado.split(" ", 1)[1] + ")"),
                          "estado": estado, "veredicto": r.veredicto, "ventana": r.ventana, "fila": i, "columna": j,
                          "dx_px": r.dx_px, "dy_px": r.dy_px, "dx_m_este": round(r.dx_px * r.pixel_m, 1),
                          "dy_m_norte": round(-r.dy_px * r.pixel_m, 1) + 0.0,
                          "corr_antes": r.corr_antes, "corr_despues": r.corr_despues,
                          "usada": "si" if bool(r.usada) else "no"})
    cv = pd.DataFrame(filas)
    if len(cv):
        # a lo sumo diez grupos de color: los pares de Ibicuy que cumplen para pixel van juntos
        def grupo(r):
            if r.sitio == "Ibicuy" and r.veredicto.startswith("CUMPLE para fusion de pixel"):
                return "Ibicuy: pares que cumplen para pixel"
            if r.sitio == "Ibicuy" and "S1 RTC" in r.par:
                return "Ibicuy: S1 RTC VV (con S2, NISAR L o SNAP)"
            if r.sitio == "Ibicuy" and "BIOMASS" in r.par:
                return "Ibicuy: BIOMASS P (con S2 o SNAP)"
            if r.sitio == "Bovril" and "NovaSAR" in r.par:
                return "Bovril: NovaSAR HH %s (S2, NISAR L o RTC)" % r.estado.split(" ", 1)[1]
            if r.sitio == "Bovril":
                return "Bovril: %s" % r.par
            return r.par_y_estado
        cv["grupo"] = cv.apply(grupo, axis=1)
        n_g = cv.grupo.nunique()
        cv.to_csv(os.path.join(dest, "Tp3_corregistro_por_ventana.csv"), index=False, encoding="utf-8-sig")
        log("Ventanas de corregistro: %d de %d pares, en %d grupos de color  ->  datos/Tp3_corregistro_por_ventana.csv"
            % (len(cv), cv.par_y_estado.nunique(), n_g))
        if n_g > 10:
            log("AVISO: mas de diez grupos; Orange pintara de gris (Other) los que sobren.")

    # 3. fechas ------------------------------------------------------------------------------
    partes = []
    for sitio, nombre in (("A2_IBICUY", "Ibicuy"), ("F_BOVRIL", "Bovril")):
        f = ruta_tp("Tp3", "05_Resultados", "04_Tablas", "%s_diferencias_de_fecha.csv" % sitio)
        if os.path.exists(f):
            d = pd.read_csv(f, encoding="utf-8-sig")
            d.insert(0, "par", ["%s %s / %s %s" % (r.sensor_1, str(r.fecha_1)[5:], r.sensor_2, str(r.fecha_2)[5:])
                                for r in d.itertuples()])
            d.insert(0, "sitio", nombre)
            partes.append(d)
    if len(partes) == 2:  # solo si estan los dos sitios: si falta Bovril se conserva la tabla anterior
        pd.concat(partes).to_csv(os.path.join(dest, "Tp3_diferencias_de_fecha.csv"), index=False, encoding="utf-8-sig")
        log("Diferencias de fecha: %d filas  ->  datos/Tp3_diferencias_de_fecha.csv" % sum(len(p) for p in partes))
    mu = ruta_tp("Tp3", "05_Resultados", "04_Tablas", "%s_contexto_pixeles_muestra.csv" % a.sitio)
    if os.path.exists(mu):
        pd.read_csv(mu, encoding="utf-8-sig").to_csv(os.path.join(dest, "Tp3_contexto_pixeles_muestra.csv"),
                                                     index=False, encoding="utf-8-sig")
        log("Pixeles por clase de MapBiomas  ->  datos/Tp3_contexto_pixeles_muestra.csv")
    log.cerrar("abrir 08_Orange/Tp3_A, Tp3_B y Tp3_C en Orange (File > Open)")


if __name__ == "__main__":
    main()
