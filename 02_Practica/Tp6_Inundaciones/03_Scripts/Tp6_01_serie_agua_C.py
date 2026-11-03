# -*- coding: utf-8 -*-
"""
Tp6_01_serie_agua_C.py   [SE CORRE]   Tp6, paso 1 de la guia - Inundaciones
===================================================================
Pregunta del practico: que area cubrio el agua, cuanto tiempo y a que
profundidad. Sitio: B_CONCORDIA (rio Uruguay; crecidas de noviembre de 2023
y mayo de 2024).

Este paso arma la SERIE de agua abierta con Sentinel-1 (banda C, VV):

  1. Lista todas las escenas Sentinel-1 RTC del Planetary Computer sobre el
     sitio en la ventana (por defecto 01/10/2023 a 30/06/2024), de UNA sola
     orbita relativa (la mas frecuente): mezclar orbitas mezcla geometrias.
  2. Calcula el umbral de agua con Otsu sobre la FECHA DEL UMBRAL (04/11/2023,
     la del par Sentinel-1 y Sentinel-2 del mismo dia; NO es el pico de la serie:
     el 28/11/2023 y el 14/05/2024 tienen mas agua) y lo APLICA a todas las
     fechas. Un umbral por fecha haria variar la definicion de agua dentro de la
     serie. Si el histograma no tiene dos modas, Otsu falla: se fija el umbral a
     mano (--umbral_vv) mirando el histograma, y se declara.
  3. Quita el agua PERMANENTE (JRC Global Surface Water, ocurrencia >= 90 %):
     el rio y el embalse no son inundacion.
  3b. Quita el agua que YA estaba en una fecha SECA de referencia (por defecto
     la del 22/01/2026, rio en nivel normal; la escena Sentinel-1 de la MISMA
     orbita mas cercana, +/- 6 dias), con el mismo umbral: lagunas estacionales,
     banados y arrozales con agua en la fecha seca no son inundacion. Lo que
     queda es AGUA DE INUNDACION: agua abierta en la fecha, que no es permanente
     ni estaba en la referencia seca. Si no hay escena de referencia de esa
     orbita, se avisa y la capa se llama "agua temporal" (solo sin JRC).
     LIMITACION: la referencia de 2026 es POSTERIOR al evento. Lo correcto es
     una o varias fechas secas ANTERIORES, de la misma orbita, con el nivel del
     rio normal verificado en el hidrometro. Se pueden dar varias fechas
     separadas por coma (--referencia_seca 2023-AA-BB,2023-CC-DD): cuenta como
     agua ya presente la que aparece en CUALQUIERA de ellas. La de 2026 queda
     como analisis de sensibilidad.
  4. Duracion: cada fecha con agua cuenta los dias hasta la fecha siguiente
     de la serie (la ultima, la mitad de la revisita mediana). Las fechas con
     un solo cuadro cubren del 2 al 20 % del sitio: lo que no vieron es
     DESCONOCIDO, no seco. Por eso se guardan dos duraciones:
       duracion_min_dias  lo no observado cuenta como SIN agua (es la de antes);
       duracion_max_dias  lo no observado cuenta como CON agua.
     La duracion real de cada pixel esta entre las dos.
  5. Extension: extension_maxima (agua en al menos una fecha) y
     extension_persistente (agua en al menos --persistencia fechas, por defecto
     2): un pixel que cae una sola vez bajo el umbral suele ser ruido o viento.

Lo que el umbral de VV NO ve, y se declara
  - agua bajo vegetacion (pajonal, monte inundado): ahi VV puede SUBIR por
    doble rebote; es tarea de la banda L (Tp6_02);
  - el embalse de Salto Grande rizado por el viento (dispersion de Bragg) se
    aclara y, segun el viento de cada fecha, puede quedar arriba o abajo del
    umbral (el 04/11/2023, con -15 dB, dos tercios del agua permanente quedan
    abajo y un tercio arriba): por eso se excluye por JRC y no por el umbral.

SALIDA
  Tp6_Inundaciones/02_Subsets_SNAP_QGIS/B_agua_C_por_fecha_<pixel>m.tif   (una banda por fecha, 1/0)
  Tp6_Inundaciones/05_Resultados/02_Rasters/B_extension_y_duracion_C_<pixel>m.tif
  Tp6_Inundaciones/05_Resultados/04_Tablas/B_serie_agua_C.csv
  Tp6_Inundaciones/05_Resultados/05_Graficos/B_serie_agua_C.png

USO
    python Tp6_01_serie_agua_C.py --pixel 20 --desde 2023-10-01 --hasta 2024-06-30 --fecha_umbral 2023-11-04
    (--pico sigue aceptandose con el mismo significado, por compatibilidad)
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

from configuracion_comun import EVENTOS, ruta_tp                      # noqa: E402
from funciones_comunes import (grilla_sitio, buscar_stac, fecha_item, s1_rtc, s1_rtc_mas_cercana, agrupar_por_pasada,  # noqa: E402
                               jrc_ocurrencia, lin_a_db, guardar_tif, Bitacora, fuente_mpc)
from funciones_cambio import umbral_documentado                       # noqa: E402

# ------------------------------------------------------------------ PARAMETROS
SITIO = "B_CONCORDIA"
PERSISTENCIA = 2          # fechas con agua para la extension persistente


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pixel", type=float, default=20.0)
    ap.add_argument("--desde", default="2023-10-01")
    ap.add_argument("--hasta", default="2024-06-30")
    ap.add_argument("--fecha_umbral", "--pico", dest="pico", default="2023-11-04",
                    help="fecha en que se calcula el umbral (la del par Sentinel-1 y Sentinel-2); no es el pico")
    ap.add_argument("--umbral_vv", type=float, default=None, help="dB; si no se da, Otsu en la fecha del umbral")
    ap.add_argument("--persistencia", type=int, default=PERSISTENCIA,
                    help="fechas con agua para la extension persistente (por defecto 2)")
    ap.add_argument("--orbita", type=int, default=None)
    ap.add_argument("--referencia_seca", default=EVENTOS["Tp6"]["referencia_seca"],
                    help="fecha(s) seca(s) de referencia AAAA-MM-DD, separadas por coma; 'no' para no usarla")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp6", "05_Resultados", "06_Control_calidad"), "Tp6_01_serie")
    g = grilla_sitio(SITIO, pixel=a.pixel)
    its = buscar_stac("sentinel-1-rtc", SITIO, a.desde, a.hasta)
    if not its:
        sys.exit("El Planetary Computer no devolvio Sentinel-1 RTC para la ventana.")
    orbs = pd.Series([it.properties.get("sat:relative_orbit") for it in its])
    orb = a.orbita if a.orbita is not None else int(orbs.mode()[0])
    its = [it for it in its if it.properties.get("sat:relative_orbit") == orb]
    log("Escenas en la ventana: %d; se usa la orbita relativa %d (%d escenas). Otras orbitas: %s"
        % (len(orbs), orb, len(its), sorted(set(orbs) - {orb})))

    permanente, _ = jrc_ocurrencia(SITIO, g)
    perm = permanente >= 90
    log("Agua permanente (JRC >= 90 %%): %.1f %% del sitio, excluida de la inundacion." % (100 * np.nanmean(perm)))

    # umbral en la fecha del umbral (la del par Sentinel-1 y Sentinel-2)
    pico = [it for it in its if fecha_item(it)[0] == a.pico]
    if not pico:
        sys.exit("No hay escena de la orbita %d el %s. Elegir --fecha_umbral entre: %s"
                 % (orb, a.pico, ", ".join(fecha_item(i)[0] for i in its)))
    # todos los cuadros de la pasada del pico, unidos: con un solo cuadro el Otsu puede salir de un borde del sitio
    vv_pico = lin_a_db(s1_rtc(agrupar_por_pasada(pico)[0], "vv", g))
    log("Fecha del umbral %s: %d cuadro(s) de la pasada, %.0f %% del sitio con dato." % (a.pico, len(pico), 100 * np.isfinite(vv_pico).mean()))
    u, txt = umbral_documentado(vv_pico[~perm], "VV del %s (dB)" % a.pico,
                                ruta_tp("Tp6", "05_Resultados", "05_Graficos", "B_histograma_VV_pico.png"),
                                metodo="manual" if a.umbral_vv is not None else "otsu",
                                manual=a.umbral_vv, signo="<")
    log("Umbral de agua abierta: %s" % txt)

    # referencia seca: el agua que ya estaba con el rio en nivel normal no es inundacion
    seca = np.zeros((g["height"], g["width"]), bool)
    clase_nombre = "agua temporal"
    if a.referencia_seca.lower() != "no":
        for fr in [x.strip() for x in a.referencia_seca.split(",") if x.strip()]:
            it_ref = s1_rtc_mas_cercana(SITIO, fr, dias=6, orbita=orb, grilla=g)
            if it_ref is None:
                log("AVISO: no hay Sentinel-1 de la orbita %d a +/- 6 dias del %s: esa fecha no se usa." % (orb, fr))
                continue
            f_ref, _ = fecha_item(it_ref)
            vv_ref = lin_a_db(s1_rtc(it_ref, "vv", g))
            seca_f = np.isfinite(vv_ref) & (vv_ref < u) & ~perm
            seca |= seca_f
            log("Referencia seca: %.0f %% del sitio con dato." % (100 * np.isfinite(vv_ref).mean()))
            clase_nombre = "agua de inundacion"
            log("Referencia seca: Sentinel-1 del %s (orbita %d): %.1f ha de agua no permanente que ya estaba;"
                % (f_ref, orb, seca_f.sum() * a.pixel ** 2 / 1e4))
            if f_ref > a.pico:
                log("       OJO: esta referencia es POSTERIOR al evento: puede borrar agua real de la crecida.")
        if clase_nombre == "agua temporal":
            log("AVISO: ninguna fecha de referencia seca tiene escena: la capa queda como AGUA TEMPORAL")
            log("       (incluye lagunas estacionales y banados).")
        else:
            log("       Total: %.1f ha de agua ya presente; se excluye de la inundacion en todas las fechas."
                % (seca.sum() * a.pixel ** 2 / 1e4))

    col_ha = clase_nombre.replace(" ", "_") + "_ha"      # agua_de_inundacion_ha o agua_temporal_ha
    capas, filas, fechas = {}, [], []
    for it in its:
        f, h = fecha_item(it)
        vv = lin_a_db(s1_rtc(it, "vv", g))
        agua = np.where(np.isfinite(vv), ((vv < u) & ~perm & ~seca).astype("float32"), np.nan)
        clave = "agua_%s" % f.replace("-", "")
        if clave in capas:
            # dos cuadros consecutivos de la MISMA pasada: se unen en una sola fecha
            capas[clave] = np.where(np.isnan(capas[clave]), agua, capas[clave])
            agua = capas[clave]
            vv_ok = np.isfinite(agua)
            ha = np.nansum(agua) * a.pixel ** 2 / 1e4
            filas[-1].update({"id": filas[-1]["id"] + " + " + it.id, col_ha: round(ha, 1),
                              "pixeles_validos_%": round(100 * vv_ok.mean(), 1)})
            log("  %s  segundo cuadro de la misma pasada: unido -> %s %9.1f ha  (%.0f %% del sitio con dato)"
                % (f, clase_nombre, ha, filas[-1]["pixeles_validos_%"]))
            continue
        capas[clave] = agua
        fechas.append(f)
        ha = np.nansum(agua) * a.pixel ** 2 / 1e4
        filas.append({"fecha": f, "hora_utc": h, "id": it.id, col_ha: round(ha, 1),
                      "pixeles_validos_%": round(100 * np.isfinite(vv).mean(), 1)})
        log("  %s  %s %9.1f ha  (%.0f %% del sitio con dato)" % (f, clase_nombre, ha, filas[-1]["pixeles_validos_%"]))
    t = pd.DataFrame(filas).sort_values("fecha")
    fe = pd.to_datetime(t.fecha)
    dias = fe.diff().shift(-1).dt.days
    dias.iloc[-1] = float(np.nanmedian(fe.diff().dt.days)) / 2.0
    t["dias_que_representa"] = dias.values
    orden = ["agua_%s" % f.replace("-", "") for f in t.fecha]
    pila = np.stack([capas[k] for k in orden])
    w = t.dias_que_representa.values[:, None, None]
    # duracion minima: lo no observado (NaN) cuenta como SIN agua; maxima: como CON agua
    duracion = np.nansum(np.where(np.isfinite(pila), pila, 0.0) * w, axis=0).astype("float32")
    duracion_max = np.where(perm | seca, 0.0, np.sum(np.where(np.isfinite(pila), pila, 1.0) * w, axis=0)).astype("float32")
    n_fechas_agua = np.nansum(pila, axis=0)
    extension = (n_fechas_agua >= 1).astype("float32")
    persistente = (n_fechas_agua >= a.persistencia).astype("float32")
    fuente = fuente_mpc("ESA - Copernicus", "Sentinel-1 IW GRD RTC (gamma0 VV), orbita relativa %d, %d escenas"
                        % (orb, len(t)), "%s a %s" % (t.fecha.iloc[0], t.fecha.iloc[-1]),
                        detalle="Agua permanente: JRC Global Surface Water (Pekel et al., 2016).")
    guardar_tif(ruta_tp("Tp6", "02_Subsets_SNAP_QGIS", "B_agua_C_por_fecha_%dm.tif" % a.pixel),
                {k: capas[k] for k in orden}, g, fuente,
                "%s por fecha: VV < %.2f dB, sin agua permanente (JRC >= 90 %%)%s"
                % (clase_nombre.capitalize(), u, " ni agua de la referencia seca" if seca.any() else ""))
    guardar_tif(ruta_tp("Tp6", "05_Resultados", "02_Rasters", "B_extension_y_duracion_C_%dm.tif" % a.pixel),
                {"extension_maxima": extension, "duracion_dias": duracion,
                 "agua_en_referencia_seca": seca.astype("float32"),
                 "duracion_min_dias": duracion, "duracion_max_dias": duracion_max,
                 "extension_persistente": persistente}, g, fuente,
                "Extension maxima y persistente (>= %d fechas) y duracion minima y maxima (dias) del %s en banda C"
                % (a.persistencia, clase_nombre))
    out = ruta_tp("Tp6", "05_Resultados", "04_Tablas", "B_serie_agua_C.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    t.to_csv(out, index=False, encoding="utf-8-sig")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 3.6))
    import matplotlib.ticker as mt
    ax.plot(fe, t[col_ha], "o-", color="#1f3b73")
    ax.set_ylabel("%s (ha)" % clase_nombre.replace("inundacion", "inundación"))
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda x, p: ("{:,.0f}".format(x)).replace(",", ".")))
    ax.grid(alpha=0.3)
    ax.set_title("%s en banda C, %s" % (clase_nombre.capitalize().replace("inundacion", "inundación"), SITIO), fontsize=11)
    fig.text(0.01, 0.01, "Fuente: " + fuente[:220], fontsize=8)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(ruta_tp("Tp6", "05_Resultados", "05_Graficos", "B_serie_agua_C.png"), dpi=140)
    plt.close(fig)
    log("")
    ha_px = a.pixel ** 2 / 1e4
    log("Extension maxima: %.1f ha; pixeles con mas de 30 dias de agua: %.1f ha"
        % (extension.sum() * ha_px, (duracion > 30).sum() * ha_px))
    log("Extension persistente (agua en %d fechas o mas): %.1f ha" % (a.persistencia, persistente.sum() * ha_px))
    log("Duracion de mas de 30 dias: %.1f ha (minima, lo no observado = seco) a %.1f ha (maxima, lo no observado = agua)"
        % ((duracion > 30).sum() * ha_px, (duracion_max > 30).sum() * ha_px))
    log.cerrar("python Tp6_02_sinergia_agua.py --pixel %d" % a.pixel)


if __name__ == "__main__":
    main()
