# -*- coding: utf-8 -*-
"""
Tp3_02_medir_corregistro.py   [SE CORRE]   Tp3, paso 3 de la guia (control)
===================================================================
Mide el desplazamiento residual entre dos capas del cubo. Es el control del
Tp3 (presentacion 01 del curso, los tres requisitos de la fusion):

    "desplazamiento entre sensores menor que un pixel"

COMO MIDE
  Optico y radar no se parecen pixel a pixel (uno mide color; el otro,
  estructura), pero los BORDES coinciden: costas, rutas, limites de lotes.
  Por eso se comparan mapas de bordes (gradiente de Sobel) y no los valores.
  La correlacion de fase entre los dos mapas de bordes da el desplazamiento
  (dx, dy) con un PASO de una decima de pixel (upsample_factor=10). Ese paso
  no es la exactitud: la incertidumbre de la medicion se lee en la
  dispersion entre ventanas.

  El desplazamiento se mide en ventanas (por defecto 4 x 4) y se informa:
    - la MEDIANA de dx y de dy (robusta);
    - la DISPERSION: desvio estandar muestral de dx y de dy entre las
      ventanas usadas;
    - el RANGO: maximo menos minimo de la mediana de dy por fila de
      ventanas y de dx por columna. Un error de escala o de rotacion hace
      crecer el desplazamiento de un borde al otro de la imagen: el rango
      lo detecta aunque el desvio estandar sea chico.

QUE VENTANAS SE USAN (criterio independiente del resultado)
  Una ventana entra si tiene al menos --min_comun de dato en comun y si su
  dx y su dy caen dentro de la mediana +/- 3 MAD (desviacion absoluta
  mediana escalada, 1,4826 x MAD; con un piso de 0,1 px). Asi se descartan
  las mediciones aberrantes (agua que cambio, ventana sin bordes) sin elegir
  las ventanas por cuanto mejoran el ajuste. La bitacora informa siempre las
  dos cifras: con todas las ventanas y con las usadas. La correlacion de
  bordes antes y despues de aplicar el desplazamiento (corr_antes,
  corr_despues) se informa como dato de calidad, no como filtro.

VEREDICTO (dos niveles)
  CUMPLE PARA FUSION DE PIXEL:  modulo de la mediana < 0,5 px, dispersion
                                < 0,5 px en x y en y, y rango < 1 px.
  CUMPLE PARA RASGO O DECISION: modulo < 1 px, dispersion < 1 px y rango
                                < 2 px.
  NO CUMPLE: lo demas. Se dice si es un corrimiento rigido (dispersion y
  rango chicos, modulo grande) o una deformacion (dispersion o rango
  grandes).

SIGNO
  dx y dy son lo que HAY QUE APLICAR a la capa movil para alinearla con la
  de referencia. La bitacora lo escribe en palabras: "hay que mover la capa
  movil X m al este y Y m al norte (la imagen esta corrida al oeste y al
  sur)". dx positivo = mover al este; dy positivo (filas) = mover al SUR.

SALIDA
  Tp3_Armonizacion/05_Resultados/04_Tablas/<SITIO>_corregistro_<mov>_vs_<ref>.csv
  (una fila por ventana, con el resumen del par repetido en cada fila:
  mediana, modulo, dispersion, rango, metros, ventanas usadas y veredicto)

USO
    python Tp3_02_medir_corregistro.py --sitio A2_IBICUY --pixel 20 --ref OPT_S2_B08 --mov L_NISAR_gamma0_HV_20260930
    python Tp3_02_medir_corregistro.py --sitio A2_IBICUY --pixel 20 --ref L_NISAR_gamma0_HH_20260930 --mov S_NISAR_gamma0_HH_20260930
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
from funciones_comunes import leer_tif, lin_a_db, Bitacora            # noqa: E402

# ----------------------------------------------------------------- PARAMETROS
UMBRAL_PIXEL = 0.5         # px: modulo y dispersion maximos para fusion de pixel
UMBRAL_RASGO = 1.0         # px: modulo y dispersion maximos para fusion de rasgo o de decision
RANGO_PIXEL = 1.0          # px: rango maximo (por fila o columna de ventanas) para fusion de pixel
RANGO_RASGO = 2.0          # px: rango maximo para rasgo o decision
K_MAD = 3.0                # una ventana se usa si dx y dy estan dentro de mediana +/- K_MAD x MAD
MAD_MINIMO = 0.1           # px: piso de la MAD (si todas las ventanas dan casi lo mismo)
SOBREMUESTREO = 10         # paso de la correlacion de fase: 1/10 de pixel


def bordes(x, es_radar):
    """Mapa de bordes normalizado (media 0, desvio 1). El radar se pasa a dB y se suaviza 3 x 3."""
    from scipy import ndimage

    y = lin_a_db(x) if es_radar else x.astype("float64")
    relleno = np.nanmedian(y)
    y = np.where(np.isfinite(y), y, relleno)
    if es_radar:
        y = ndimage.uniform_filter(y, 3)            # atenua el speckle antes del gradiente
    gx = ndimage.sobel(y, 1)
    gy = ndimage.sobel(y, 0)
    m = np.hypot(gx, gy)
    return (m - m.mean()) / (m.std() + 1e-12)


def resumen(u, pix):
    """Mediana, dispersion y rango de un conjunto de ventanas (DataFrame con dx_px, dy_px, _fi, _co)."""
    dx, dy = float(u.dx_px.median()), float(u.dy_px.median())
    sx = float(u.dx_px.std()) if len(u) > 1 else 0.0
    sy = float(u.dy_px.std()) if len(u) > 1 else 0.0
    fil = u.groupby("_fi").dy_px.median()
    col = u.groupby("_co").dx_px.median()
    rango_dy = float(fil.max() - fil.min()) if len(fil) > 1 else 0.0
    rango_dx = float(col.max() - col.min()) if len(col) > 1 else 0.0
    return {"dx": dx, "dy": dy, "sx": sx, "sy": sy, "mod": float(np.hypot(dx, dy)),
            "rango_dy": rango_dy, "rango_dx": rango_dx, "fil": fil, "col": col}


def veredicto(r):
    disp, rango = max(r["sx"], r["sy"]), max(r["rango_dx"], r["rango_dy"])
    if r["mod"] < UMBRAL_PIXEL and disp < UMBRAL_PIXEL and rango < RANGO_PIXEL:
        return "CUMPLE para fusion de pixel"
    if r["mod"] < UMBRAL_RASGO and disp < UMBRAL_RASGO and rango < RANGO_RASGO:
        return "CUMPLE para rasgo o decision"
    if disp >= UMBRAL_RASGO or rango >= RANGO_RASGO:
        return "NO CUMPLE, no rigido"
    return "NO CUMPLE, rigido"


def en_palabras(dx_m, dy_norte_m):
    """Frase con el sentido del movimiento y la posicion de la imagen (se omite la componente menor de 1 m)."""
    mov, img = [], []
    if abs(dx_m) >= 1:
        mov.append("%.0f m al %s" % (abs(dx_m), "ESTE" if dx_m > 0 else "OESTE"))
        img.append("al oeste" if dx_m > 0 else "al este")
    if abs(dy_norte_m) >= 1:
        mov.append("%.0f m al %s" % (abs(dy_norte_m), "NORTE" if dy_norte_m > 0 else "SUR"))
        img.append("al sur" if dy_norte_m > 0 else "al norte")
    if not mov:
        return "No hay que mover la capa movil: el desplazamiento es menor de 1 m."
    return "Hay que mover la capa movil %s (la imagen esta corrida %s)." % (" y ".join(mov), " y ".join(img))


def main():
    from skimage.registration import phase_cross_correlation
    from scipy import ndimage

    ap = argparse.ArgumentParser(description="Mide el corregistro entre dos capas del cubo del Tp3.")
    ap.add_argument("--sitio", required=True, choices=list(SITIOS.keys()))
    ap.add_argument("--pixel", type=int, default=20)
    ap.add_argument("--ref", required=True, help="capa de referencia (la que no se mueve)")
    ap.add_argument("--mov", required=True, help="capa cuyo desplazamiento se mide")
    ap.add_argument("--ventanas", type=int, default=4)
    ap.add_argument("--min_comun", type=float, default=0.8,
                    help="fraccion minima de dato en comun por ventana (bajarla si el movil cubre poco, y declararlo)")
    ap.add_argument("--sufijo", default="", help="texto opcional al final del nombre de la tabla y la bitacora")
    a = ap.parse_args()
    par = "%s_vs_%s%s" % (a.mov, a.ref, a.sufijo)
    log = Bitacora(ruta_tp("Tp3", "05_Resultados", "06_Control_calidad"), "Tp3_02_%s_%s" % (a.sitio, par))
    cubo = ruta_tp("Tp3", "02_Subsets_SNAP_QGIS", "%s_cubo_%dm.tif" % (a.sitio, a.pixel))
    if not os.path.exists(cubo):
        log("No encuentro el cubo %s." % cubo)
        log("Use el mismo --pixel que en el paso 1 (Tp3_01_cubo_comun.py).")
        log.cerrar()
        return
    capas, perfil, _ = leer_tif(cubo)
    pix = perfil["transform"].a
    for c in (a.ref, a.mov):
        if c not in capas:
            log("La capa %s no esta en el cubo. Copie el nombre exacto de esta lista:" % c)
            log("   " + ", ".join(capas))
            log.cerrar()
            return
    es_r = lambda n: not n.startswith(("OPT_", "MDE_"))     # noqa: E731
    ref = bordes(capas[a.ref], es_r(a.ref))
    mov = bordes(capas[a.mov], es_r(a.mov))
    comun = np.isfinite(capas[a.ref]) & np.isfinite(capas[a.mov])

    alto, ancho = ref.shape
    n = a.ventanas
    filas = []
    for i in range(n):
        for j in range(n):
            f0, f1 = i * alto // n, (i + 1) * alto // n
            c0, c1 = j * ancho // n, (j + 1) * ancho // n
            if comun[f0:f1, c0:c1].mean() < a.min_comun:
                continue                              # ventana con poco dato en comun
            r_v, m_v = ref[f0:f1, c0:c1], mov[f0:f1, c0:c1]
            desp, _, _ = phase_cross_correlation(r_v, m_v, upsample_factor=SOBREMUESTREO)
            # desp = (dy, dx) que hay que APLICAR a "mov" para alinearla con "ref" (filas, columnas).
            m_s = ndimage.shift(m_v, desp, order=1, mode="nearest")
            c_antes = float(np.corrcoef(r_v.ravel(), m_v.ravel())[0, 1])
            c_desp = float(np.corrcoef(r_v.ravel(), m_s.ravel())[0, 1])
            filas.append({"ventana": "%d,%d" % (i, j), "dy_px": round(float(desp[0]), 2),
                          "dx_px": round(float(desp[1]), 2), "corr_antes": round(c_antes, 3),
                          "corr_despues": round(c_desp, 3), "_fi": i, "_co": j})
    if not filas:
        log("Ninguna ventana tiene %.0f %% de dato en comun: no se puede medir." % (100 * a.min_comun))
        log("Si el producto movil cubre poco el sitio, probar --ventanas 2 o --min_comun 0.5 (y declararlo).")
        log.cerrar()
        return
    t = pd.DataFrame(filas)

    # Ventanas usadas: dentro de mediana +/- K_MAD x MAD en dx y en dy (criterio que no mira el resultado).
    def dentro(v):
        med = v.median()
        mad = max(1.4826 * (v - med).abs().median(), MAD_MINIMO)
        return (v - med).abs() <= K_MAD * mad
    t["usada"] = dentro(t.dx_px) & dentro(t.dy_px)
    t["mejora_bordes"] = t.corr_despues >= t.corr_antes
    if (~t.usada).any():
        log("Ventanas fuera de mediana +/- %.0f MAD (no entran): %s" % (K_MAD, ", ".join(t.ventana[~t.usada])))
    if (~t.mejora_bordes).any():
        log("Ventanas cuyo desplazamiento no mejora la correlacion de bordes (dato de calidad): "
            + ", ".join(t.ventana[~t.mejora_bordes]))
    if t.usada.sum() < 2:
        log("Quedan menos de 2 ventanas confiables: no se puede decidir. Pruebe otra banda o --ventanas 3.")
        log.cerrar()
        return
    u = t[t.usada]
    r = resumen(u, pix)
    r_todas = resumen(t, pix)
    ver = veredicto(r)
    dx_m, dy_norte_m = r["dx"] * pix + 0.0, -r["dy"] * pix + 0.0

    log("Referencia: %s   Movil: %s   pixel %.0f m   %d ventanas validas, %d usadas"
        % (a.ref, a.mov, pix, len(t), int(t.usada.sum())))
    log(t.drop(columns=["_fi", "_co"]).to_string(index=False))
    log("")
    log("Mediana: dx = %+.2f px (%+.0f m al este), dy = %+.2f px en filas (%+.0f m al norte)"
        % (r["dx"], dx_m, r["dy"], dy_norte_m))
    log(en_palabras(dx_m, dy_norte_m))
    log("Modulo de la mediana: %.2f px (%.0f m)" % (r["mod"], r["mod"] * pix))
    log("Dispersion entre ventanas usadas (desvio estandar): %.2f px en x, %.2f px en y" % (r["sx"], r["sy"]))
    log("Rango de dy entre filas de ventanas (norte a sur): %.2f px  [%s]"
        % (r["rango_dy"], ", ".join("%+.1f" % v for v in r["fil"])))
    log("Rango de dx entre columnas de ventanas (oeste a este): %.2f px  [%s]"
        % (r["rango_dx"], ", ".join("%+.1f" % v for v in r["col"])))
    log("Con TODAS las ventanas validas: modulo %.2f px, dispersion %.2f / %.2f px, rango %.2f / %.2f px"
        % (r_todas["mod"], r_todas["sx"], r_todas["sy"], r_todas["rango_dx"], r_todas["rango_dy"]))
    log("")
    log("VEREDICTO: %s." % ver)
    log("  (pixel: modulo y dispersion < %.1f px y rango < %.0f px; rasgo o decision: < %.0f px y rango < %.0f px)"
        % (UMBRAL_PIXEL, RANGO_PIXEL, UMBRAL_RASGO, RANGO_RASGO))
    if ver == "NO CUMPLE, no rigido":
        log("El desplazamiento cambia entre ventanas: no es un corrimiento rigido. Revise la georreferencia")
        log("del producto (puntos de enlace, relieve) antes de trasladar nada. Si la mediana por fila o por")
        log("columna crece o decrece de manera ordenada, hay un error de escala o de rotacion: una traslacion")
        log("sola no lo corrige. Como primera aproximacion (no la solucion) se puede aplicar la mediana y")
        log("volver a medir:  --desplazamiento %.0f %.0f" % (dx_m, dy_norte_m))
    elif ver == "NO CUMPLE, rigido":
        log("Corrimiento rigido de %.1f px (%.0f m): corregirlo en el producto movil y volver a medir." % (r["mod"], r["mod"] * pix))
        if "NovaSAR" in a.mov:
            log("Para NovaSAR pase a Tp2_01:  --desplazamiento %.0f %.0f" % (dx_m, dy_norte_m))
        else:
            log("Esta capa no se corrige desde los scripts: en SNAP, Radar > Coregistration con la")
            log("referencia como maestra; o se declara el desfase y el par no entra a fusion de pixel.")
    elif ver == "CUMPLE para rasgo o decision":
        log("El par sirve para fusion de rasgo o de decision. Para fusion de pixel, corregir antes el desfase")
        log("(%.0f m) y medir el residuo sobre puntos independientes." % (r["mod"] * pix))

    salida = t.drop(columns=["_fi", "_co"]).assign(
        mediana_dx_px=round(r["dx"], 2), mediana_dy_px=round(r["dy"], 2), modulo_px=round(r["mod"], 2),
        dispersion_x_px=round(r["sx"], 2), dispersion_y_px=round(r["sy"], 2),
        rango_dx_columnas_px=round(r["rango_dx"], 2), rango_dy_filas_px=round(r["rango_dy"], 2),
        dx_m_este=round(dx_m, 1), dy_m_norte=round(dy_norte_m, 1),
        ventanas_validas=len(t), ventanas_usadas=int(t.usada.sum()),
        modulo_todas_px=round(r_todas["mod"], 2), dispersion_x_todas_px=round(r_todas["sx"], 2),
        dispersion_y_todas_px=round(r_todas["sy"], 2),
        veredicto=ver, pixel_m=pix, ref=a.ref, mov=a.mov)
    salida.to_csv(ruta_tp("Tp3", "05_Resultados", "04_Tablas", "%s_corregistro_%s.csv" % (a.sitio, par)),
                  index=False, encoding="utf-8-sig")
    log.cerrar("python Tp3_03_lidar_en_el_cubo.py --sitio %s --pixel %d" % (a.sitio, a.pixel))


if __name__ == "__main__":
    main()
