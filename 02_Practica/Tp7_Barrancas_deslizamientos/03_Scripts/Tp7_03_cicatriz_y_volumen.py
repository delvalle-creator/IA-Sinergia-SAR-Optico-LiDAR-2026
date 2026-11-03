# -*- coding: utf-8 -*-
"""
Tp7_03_cicatriz_y_volumen.py   [SE CORRE]   Tp7, paso 4 y 5 de la guia
==========================================================
"Delimitar cicatriz y deposito en el optico; volumen por diferencia de MDE"
(presentacion 01, diapositiva 30, paso 4).

El grupo digitaliza en QGIS, sobre el CBERS-4A de 2 m (26/09/2026), el Pleiades de CONAE
(0,5 m, 2022) o el Sentinel-2 del 19/10/2018, dos poligonos (el Spotlight de COSMO-SkyMed es
un SLC sin geocodificar y no sirve de fondo sin procesarlo en SNAP):

  04_Tablas_de_trabajo/E1_cicatriz_y_deposito.gpkg, capa "formas",
  campo "tipo" = "cicatriz" (de donde salio material) o "deposito" (adonde llego)

y el programa calcula con DOS modelos de elevacion de fechas distintas:

  dZ = MDE_despues - MDE_antes          (orden del curso: --antes GLO-30, --despues IGN 5 m)
  volumen perdido  = suma de dZ < 0 en la cicatriz  x area del pixel
  volumen ganado   = suma de dZ > 0 en el deposito  x area del pixel

DETECTABILIDAD (correccion del 27/10/2026)
  Un pixel es detectable si |dZ| supera 2 desvios del ruido de la zona estable Y
  tiene el SIGNO ESPERADO (negativo en la cicatriz, positivo en el deposito). Se
  informan aparte:
    - %_pixeles_sobre_2_desvios_signo_esperado y %_..._signo_contrario;
    - volumen_detectable_m3: solo los pixeles detectables con el signo esperado;
    - incertidumbre_m3 = 2 x ruido x area del pixel x raiz(n). SUPONE ERRORES
      INDEPENDIENTES entre pixeles: con error autocorrelacionado es mayor.
  Y se repite el calculo en una zona de CONTROL (--control; por defecto, la escarpa
  de E1_zonas_ladera.gpkg a mas de 200 m de las formas): si el mismo patron aparece
  en el control, el resultado de la forma no se distingue del error del MDE.

Los MDE del curso y sus limites (se escriben en la bitacora)
  02_Subsets_SNAP_QGIS\\QGIS_GeoTIFF\\E1_DIAMANTE_BARRANCA_CopernicusDEM30.tif: GLO-30,
     30 m, TanDEM-X 2011-2015, SUPERFICIE, sobre EGM2008 ("antes").
  02_Subsets_SNAP_QGIS\\QGIS_GeoTIFF\\E1_DIAMANTE_BARRANCA_IGN_MDE_5m.tif: IGN MDE-Ar
     aerofotogrametrico de 5 m, vuelo de 2013, SUPERFICIE, referencia vertical SRVN16 ("despues").
  NINGUNO ES POSTERIOR AL EVENTO DE 2018: con ellos el calculo es un ejercicio de
  metodo (sesgo, ruido, limite de deteccion), no el volumen movilizado en 2018.
  Pixel por defecto 30 m (el del GLO-30): los MDE se PROMEDIAN a esa grilla; el
  GLO-30 no se afina a 5 m (regla del curso).
  Entre esos dos MDE hay DIFERENCIA DE DATUM (decimetros), de RESOLUCION
  (5 contra 30 m) y de FECHA. Antes de atribuir un dZ a la barranca hay que
  restar el sesgo medido en una zona estable (--zona_estable o, si no se da,
  el anillo de referencia de Tp7_02). Un volumen sin ese control no se informa.

SALIDA  Tp7_Barrancas_deslizamientos/05_Resultados/04_Tablas/E1_volumenes.csv
        Tp7_Barrancas_deslizamientos/05_Resultados/02_Rasters/E1_dz_despues_menos_antes.tif
        Tp7_Barrancas_deslizamientos/05_Resultados/04_Tablas/E1_comparacion_interpretes.csv (con --comparar_con)
USO     python Tp7_03_cicatriz_y_volumen.py --antes <GLO-30.tif> --despues <IGN_5m.tif> --pixel 30
        (--comparar_con <gpkg del docente> compara los poligonos del grupo con los de otro interprete: area e IoU)
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

from configuracion_comun import EPSG, ruta_tp                         # noqa: E402
from funciones_comunes import grilla_sitio, leer_en_grilla, rasterizar, guardar_tif, Bitacora  # noqa: E402

# ------------------------------------------------------------ PARAMETROS
SITIO = "E1_DIAMANTE_BARRANCA"
PIXEL = 30.0           # m: el del GLO-30 (no se afina)
K_DESVIOS = 2.0        # un pixel es detectable si |dZ| > K x ruido de la zona estable
DIST_CONTROL = 200.0   # m: el control en la escarpa queda a mas de esta distancia de las formas
SIGNO_ESPERADO = {"cicatriz": -1, "deposito": +1}


def main():
    import geopandas as gpd

    ap = argparse.ArgumentParser(description="Tp7, pasos 4 y 5: volumen por diferencia de MDE con sesgo, ruido y control.")
    ap.add_argument("--antes", default="", help="MDE anterior (GeoTIFF). En el curso: el GLO-30 (2011-2015)")
    ap.add_argument("--despues", default="", help="MDE posterior (GeoTIFF). En el curso: el IGN 5 m (2013)")
    ap.add_argument("--pixel", type=float, default=PIXEL)
    ap.add_argument("--zona_estable", default="")
    ap.add_argument("--control", default="", help="GeoPackage de control (por defecto, la escarpa lejos de las formas)")
    ap.add_argument("--comparar_con", default="",
                    help="GeoPackage (capa formas) de otro interprete: compara areas e interseccion sobre union por tipo")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp7", "05_Resultados", "06_Control_calidad"), "Tp7_03_volumen")
    formas = ruta_tp("Tp7", "04_Tablas_de_trabajo", "E1_cicatriz_y_deposito.gpkg")
    if not os.path.exists(formas):
        os.makedirs(os.path.dirname(formas), exist_ok=True)
        gpd.GeoDataFrame({"tipo": pd.Series(dtype="str"), "fuente": pd.Series(dtype="str")},
                         geometry=gpd.GeoSeries([], crs=EPSG), crs=EPSG).to_file(formas, layer="formas", driver="GPKG", engine="pyogrio", geometry_type="Polygon")
        log("Se creo %s (capa 'formas', campo 'tipo': cicatriz / deposito). Digitalizar y volver a correr." % formas)
        log.cerrar()
        return
    if not (a.antes and a.despues):
        sys.exit("Faltan --antes y --despues (los dos MDE a comparar).")
    g = grilla_sitio(SITIO, pixel=a.pixel)
    # promedio: a 30 m el IGN de 5 m se agrega (no se afina el GLO-30)
    z0 = leer_en_grilla(a.antes, g, "average")
    z1 = leer_en_grilla(a.despues, g, "average")
    log("MDE antes  : %s" % a.antes)
    log("MDE despues: %s" % a.despues)
    log("dZ = despues - antes. Con --antes GLO-30 y --despues IGN, una perdida de material da dZ negativo.")
    log("AVISO: los MDE del curso (GLO-30 2011-2015, IGN 2013) son ANTERIORES al evento de 2018: el volumen")
    log("       que sigue es un ejercicio de metodo, no el volumen movilizado en 2018.")
    dz = z1 - z0
    estable = a.zona_estable or ruta_tp("Tp7", "04_Tablas_de_trabajo", "E1_zona_referencia.gpkg")
    if not os.path.exists(estable):
        sys.exit("Falta la zona estable (%s). Correr Tp7_02 o pasar --zona_estable." % estable)
    m_est = rasterizar(estable, g) > 0
    if not a.zona_estable:
        try:
            from funciones_comunes import jrc_ocurrencia
            occ, _ = jrc_ocurrencia(SITIO, g)
            m_est &= ~(np.nan_to_num(occ, nan=0) >= 50)
            log("Zona estable: anillo de Tp7_02 sin el agua del JRC (ocurrencia >= 50 %).")
        except Exception as e:                       # noqa: BLE001
            log("AVISO: sin JRC (%s): el anillo puede incluir el rio, cuya cota cambia entre MDE." % str(e)[:80])
    sesgo = float(np.nanmedian(dz[m_est]))
    ruido = float(np.nanstd(dz[m_est]))
    v_est = dz[m_est & np.isfinite(dz)]
    nmad = float(1.4826 * np.median(np.abs(v_est - np.median(v_est))))
    log("Sesgo entre MDE en la zona estable: %+.2f m (desvio %.2f m; NMAD %.2f m). Se resta." % (sesgo, ruido, nmad))
    dz = dz - sesgo
    guardar_tif(ruta_tp("Tp7", "05_Resultados", "02_Rasters", "E1_dz_despues_menos_antes.tif"), {"dz_m": dz}, g,
                "despues: %s; antes: %s" % (os.path.basename(a.despues), os.path.basename(a.antes)),
                "dZ = despues - antes, promediados a %.0f m, sesgo de la zona estable (%+.2f m) restado" % (a.pixel, sesgo))
    f = gpd.read_file(formas, layer="formas")
    area_px = a.pixel ** 2
    lim = K_DESVIOS * ruido
    # zona de control: la escarpa lejos de las formas
    ctl = a.control
    if not ctl:
        zonas = ruta_tp("Tp7", "04_Tablas_de_trabajo", "E1_zonas_ladera.gpkg")
        if os.path.exists(zonas):
            z = gpd.read_file(zonas).to_crs(g["crs"])
            esc = z[z["zona"] == "escarpa"]
            if not esc.empty:
                lejos = esc.union_all().difference(f.to_crs(g["crs"]).union_all().buffer(DIST_CONTROL))
                ctl = ruta_tp("Tp7", "04_Tablas_de_trabajo", "E1_control_escarpa.gpkg")
                gpd.GeoDataFrame({"zona": ["control_escarpa"]}, geometry=[lejos], crs=g["crs"]).to_file(ctl, driver="GPKG")
                log("Control: escarpa de E1_zonas_ladera.gpkg a mas de %.0f m de las formas (%s)." % (DIST_CONTROL, ctl))
    filas = []
    piezas = [(t, f[f.tipo == t]) for t in ("cicatriz", "deposito")]
    for tipo, sub in piezas + ([("control_cicatriz", None), ("control_deposito", None)] if ctl else []):
        if sub is not None and sub.empty:
            log("No hay poligonos de tipo '%s'." % tipo)
            continue
        if sub is None:
            m = rasterizar(ctl, g) > 0
            signo = SIGNO_ESPERADO[tipo.split("_")[1]]
        else:
            tmp = ruta_tp("Tp7", "04_Tablas_de_trabajo", "_tmp_%s.gpkg" % tipo)
            sub.to_file(tmp, driver="GPKG")
            m = rasterizar(tmp, g) > 0
            signo = SIGNO_ESPERADO[tipo]
        v = dz[m & np.isfinite(dz)]
        n = int(v.size)
        if n == 0:
            log("%s: sin pixeles con dato." % tipo)
            continue
        con_signo = v[np.sign(v) == signo]
        vol = float(con_signo.sum() * area_px)
        det_esp = (np.abs(v) > lim) & (np.sign(v) == signo)
        det_con = (np.abs(v) > lim) & (np.sign(v) == -signo)
        vol_det = float(v[det_esp].sum() * area_px)
        inc = float(lim * area_px * np.sqrt(n))
        filas.append({"forma": tipo, "pixeles": n, "area_m2": round(n * area_px, 1), "dz_medio_m": round(float(v.mean()), 2),
                      "volumen_m3": round(vol, 1), "volumen_detectable_m3": round(vol_det, 1),
                      "incertidumbre_m3": round(inc, 1),
                      "%_pixeles_sobre_2_desvios_signo_esperado": round(float(100 * det_esp.mean()), 1),
                      "%_pixeles_sobre_2_desvios_signo_contrario": round(float(100 * det_con.mean()), 1),
                      "sesgo_restado_m": round(sesgo, 2), "ruido_zona_estable_m": round(ruido, 2),
                      "nmad_zona_estable_m": round(nmad, 2)})
        r = filas[-1]
        log("%-17s %3d pixeles (%6.0f m2)  dz medio %+.2f m  volumen %+9.0f m3  detectable %+9.0f +/- %6.0f m3  "
            "sobre 2 desvios: %.0f %% con el signo esperado, %.0f %% con el contrario"
            % (tipo, n, r["area_m2"], r["dz_medio_m"], vol, vol_det, inc,
               r["%_pixeles_sobre_2_desvios_signo_esperado"], r["%_pixeles_sobre_2_desvios_signo_contrario"]))
    out = ruta_tp("Tp7", "05_Resultados", "04_Tablas", "E1_volumenes.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pd.DataFrame(filas).to_csv(out, index=False, encoding="utf-8-sig")
    log("Detectable solo si supera 2 desvios con el signo esperado Y el patron no se repite en el control.")
    log("La incertidumbre supone errores independientes entre pixeles: con error autocorrelacionado es mayor.")
    if a.comparar_con:
        comparar(f, a.comparar_con, log)
    log.cerrar("responder las preguntas del Tp7")


def comparar(f, otra, log):
    """Variabilidad entre interpretes: area de cada uno e interseccion sobre union (IoU) por tipo."""
    import geopandas as gpd
    o = gpd.read_file(otra, layer="formas").to_crs(f.crs)
    filas = []
    for tipo in ("cicatriz", "deposito"):
        a_, b_ = f[f.tipo == tipo], o[o.tipo == tipo]
        if a_.empty or b_.empty:
            log("Comparacion: falta el tipo '%s' en alguna de las dos capas." % tipo)
            continue
        A, B = a_.union_all(), b_.union_all()
        iou = A.intersection(B).area / A.union(B).area if A.union(B).area else float("nan")
        filas.append({"forma": tipo, "area_grupo_m2": round(A.area, 0), "area_otro_m2": round(B.area, 0),
                      "interseccion_m2": round(A.intersection(B).area, 0), "IoU": round(iou, 2)})
        log("Comparacion %-9s area %6.0f m2 frente a %6.0f m2; interseccion %6.0f m2; IoU %.2f"
            % (tipo, A.area, B.area, A.intersection(B).area, iou))
    pd.DataFrame(filas).to_csv(ruta_tp("Tp7", "05_Resultados", "04_Tablas", "E1_comparacion_interpretes.csv"), index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
