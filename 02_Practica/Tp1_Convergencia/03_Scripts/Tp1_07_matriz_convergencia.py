# -*- coding: utf-8 -*-
"""
Tp1_07_matriz_convergencia.py   [SE CORRE]   paso 7 (ultimo) del Tp1
====================================================================
Une las planillas de los pasos 2 a 6 de UN sitio y arma:

  1. la matriz sensor x fecha (que hay, de que banda y cuando);
  2. el GRADO de convergencia alrededor de una fecha de evento, con la regla
     de la presentacion 01 (diapositiva 18):
        completa   optico + SAR de 2 o mas bandas + LiDAR, fechas compatibles
                   -> fusion a nivel de pixel (optico y radar) o de rasgo; el LiDAR
                      muestrea por huellas: entra como referencia o en fusion de
                      rasgo, nunca a nivel de pixel
        parcial    optico + una banda SAR, o fechas separadas por semanas
                   -> sinergia o fusion a nivel de decision
        parcial (sin optico)  dos o mas bandas SAR sin optico en la ventana
                   -> sinergia SAR multibanda
        un solo sensor cerca del evento  optico solo o una sola banda SAR
                   -> mapa de ese sensor; los demas, solo para interpretar
        historica  nada dentro de la ventana (sensores de anos distintos)
                   -> solo interpretacion de cambios de largo plazo
  3. una figura de la linea de tiempo, con la cita de las fuentes al pie y un
     recuadro ampliado de +/- 30 dias alrededor del evento.

OBSERVACIONES INDEPENDIENTES (revision del 27/10/2026)
  S1_SLC, S1_GRD y Sentinel-1 RTC de la misma fecha son TRES productos de UNA
  sola toma. La matriz los conserva como columnas separadas (se ve de donde sale
  cada uno), pero la bitacora y grado_convergencia_<SITIO>.csv informan ademas las
  observaciones independientes: se cuenta una por plataforma, banda y fecha.

Solo entran las escenas VERIFICADAS: "candidata" en las planillas del
Planetary Computer, pixeles validos >= 50 % en el inventario local, huella
>= 50 % en ASF, "obtenida" o "en catalogo" en las escenas por pedido y, en
LiDAR, las fechas con al menos una huella valida en el sitio
(lidar_fechas_validas_<SITIO>.csv de Tp1_05). Una planilla que falta o que
quedo vacia (busqueda sin resultados) no detiene el programa: ese sensor no
entra y se dice en la bitacora.

SALIDA
  Tp1_Convergencia/05_Resultados/04_Tablas/matriz_convergencia_<SITIO>[_<etiqueta>].csv
  Tp1_Convergencia/05_Resultados/04_Tablas/grado_convergencia_<SITIO>[_<etiqueta>].csv
  Tp1_Convergencia/05_Resultados/05_Graficos/linea_tiempo_<SITIO>[_<etiqueta>].png

USO
    python Tp1_07_matriz_convergencia.py --sitio B_CONCORDIA --evento 2023-11-04 --ventana 12
    python Tp1_07_matriz_convergencia.py --sitio B_CONCORDIA --evento 2026-09-16 --ventana 12 --etiqueta 2026_Tp10
      (con --etiqueta las salidas llevan ese sufijo: matriz_convergencia_B_CONCORDIA_2026_Tp10.csv,
       y se leen primero las planillas de busqueda con el mismo sufijo, si existen:
       planilla_MPC_B_CONCORDIA_2026_Tp10.csv, planilla_ASF_..., planilla_por_pedido_...)
"""
import argparse
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import pandas as pd                                                   # noqa: E402

from configuracion_comun import SITIOS, ruta_tp                       # noqa: E402
from funciones_comunes import Bitacora                                # noqa: E402

T = lambda *p: ruta_tp("Tp1", "05_Resultados", "04_Tablas", *p)    # noqa: E731


def leer(ruta):
    """Planilla de un paso anterior; None si no existe o si quedo vacia (busqueda sin resultados)."""
    if not os.path.exists(ruta):
        return None
    try:
        d = pd.read_csv(ruta, encoding="utf-8-sig", dtype=str).fillna("")
    except pd.errors.EmptyDataError:
        return None
    return d if len(d.columns) else None


def num(s):
    return pd.to_numeric(s, errors="coerce")


def planilla(nombre, sitio, etiqueta, log):
    """La planilla de la busqueda de ESTE evento: con --etiqueta, primero <nombre>_<SITIO>_<etiqueta>.csv
    (la copia que se guardo al buscar ese periodo); si no existe, la generica <nombre>_<SITIO>.csv."""
    if etiqueta:
        r = T("%s_%s_%s.csv" % (nombre, sitio, etiqueta))
        if os.path.exists(r):
            log("  %s: se usa %s" % (nombre, os.path.basename(r)))
            return leer(r)
        log("  %s: no hay %s_%s_%s.csv; se usa la generica (puede ser de otro periodo)" % (nombre, nombre, sitio, etiqueta))
    return leer(T("%s_%s.csv" % (nombre, sitio)))


def reunir(sitio, log, etiqueta=""):
    partes = []
    d = leer(T("inventario_local.csv"))
    if d is not None:
        # Con pixeles contados manda el conteo; en los productos en geometria
        # de radar (SLC, L1A), todavia sin coordenadas, manda la huella, y se
        # marca en la columna "fuente" para no confundir una cosa con la otra.
        px = num(d["pixeles_validos_%"])
        hu = num(d["cobertura_huella_%"])
        ok_px = (d.sitio == sitio) & (px >= 50)
        ok_hu = (d.sitio == sitio) & px.isna() & (hu >= 50)
        d = pd.concat([d[ok_px].assign(fuente="inventario local (pixeles)"),
                       d[ok_hu].assign(fuente="inventario local (huella)")])
        partes.append(d[["sensor", "banda", "fecha", "fuente"]])
        d = None
    d = planilla("planilla_MPC", sitio, etiqueta, log)
    if d is not None:
        # Desde el 18/10/2026 la planilla trae, ademas de cada tesela, el mosaico de cada
        # dia ("Sentinel-2 mosaico del dia"). Si esta, manda el mosaico: un sitio grande
        # no lo cubre ninguna tesela sola, y contar teselas duplicaria las fechas.
        if (d.sensor == "Sentinel-2 mosaico del dia").any():
            d = d[d.sensor != "Sentinel-2"].replace({"sensor": {"Sentinel-2 mosaico del dia": "Sentinel-2"}})
        d = d[d.decision == "candidata"]
        partes.append(d.assign(fuente="Planetary Computer")[["sensor", "banda", "fecha", "fuente"]])
    d = planilla("planilla_ASF", sitio, etiqueta, log)
    if d is not None:
        d = d[num(d["cobertura_huella_%"]) >= 50]
        partes.append(d.assign(fuente="ASF (huella)")[["sensor", "banda", "fecha", "fuente"]])
    d = planilla("planilla_por_pedido", sitio, etiqueta, log)
    if d is not None:
        d = d[d.resultado.str.lower().isin(["obtenida", "en catalogo"])]
        # Si el grupo anoto la cobertura con dato (columna opcional pixeles_validos_%), rige la
        # misma regla que en el inventario local: 50 % o mas del sitio.
        if "pixeles_validos_%" in d.columns:
            px = num(d["pixeles_validos_%"])
            fuera = d[px < 50]
            for _, f in fuera.iterrows():
                log("  Por pedido: %s %s cubre %.1f %% del sitio (< 50 %%): no entra a la matriz."
                    % (f.sensor, f.fecha, float(num(pd.Series([f["pixeles_validos_%"]]))[0])))
            d = d[~(px < 50)]
        partes.append(d.assign(fuente="por pedido")[["sensor", "banda", "fecha", "fuente"]])
    # LiDAR: entran SOLO las fechas con al menos una huella valida en el sitio
    # (lidar_fechas_validas_<SITIO>.csv, que escribe Tp1_05 al contar los .h5).
    # Un granulo que cruza el sitio en la busqueda no alcanza: puede no tener
    # ninguna huella valida (nubes, agua, calidad).
    d = leer(T("lidar_fechas_validas_%s.csv" % sitio))
    if d is not None and len(d):
        d = d[num(d.huellas_validas) > 0]
        for prod, g in d.groupby("producto"):
            partes.append(pd.DataFrame({"sensor": prod, "banda": "LiDAR",
                                        "fecha": g.fecha, "fuente": "Earthdata (huellas validas contadas)"}))
            log("  %s: %d fechas con huellas validas en el sitio." % (prod, g.fecha.nunique()))
    elif leer(T("lidar_granulos_%s.csv" % sitio)) is not None:
        log("  LiDAR: hay granulos en la busqueda pero no estan contados (falta correr")
        log("         Tp1_05 con los .h5 descargados, o con --solo_contar). NO entra a la matriz.")
    if not partes:
        return pd.DataFrame(columns=["sensor", "banda", "fecha", "fuente"])
    t = pd.concat(partes, ignore_index=True)
    t = t[t.fecha.str.match(r"\d{4}-\d{2}-\d{2}")]
    return t.drop_duplicates(["sensor", "banda", "fecha"]).sort_values("fecha")


# Productos distintos de una misma toma: se cuentan como UNA observacion independiente.
PLATAFORMA = {"S1_SLC": "Sentinel-1", "S1_GRD": "Sentinel-1", "Sentinel-1 RTC": "Sentinel-1"}


def observaciones(t):
    """Observaciones independientes: una por plataforma, banda y fecha."""
    if not len(t):
        return t.assign(plataforma=[])
    t = t.assign(plataforma=t.sensor.map(lambda s: PLATAFORMA.get(s, s)))
    return t.drop_duplicates(["plataforma", "banda", "fecha"])


def grado(t, evento, ventana):
    if not evento:
        return None
    ev = pd.Timestamp(evento)
    t = t.assign(dias=(pd.to_datetime(t.fecha) - ev).dt.days.abs())
    cerca = t[t.dias <= ventana]
    hay_opt = (cerca.banda.str.lower() == "optico").any()
    bandas_sar = sorted(set(cerca.banda) & {"X", "C", "S", "L", "P"})
    hay_lidar = (cerca.banda == "LiDAR").any()
    if hay_opt and len(bandas_sar) >= 2 and hay_lidar:
        g = "completa"
    elif hay_opt and len(bandas_sar) >= 1:
        g = "parcial"
    elif len(bandas_sar) >= 2:
        g = "parcial (sin optico)"
    elif len(cerca):
        g = "un solo sensor cerca del evento"
    elif len(t):
        g = "historica"
    else:
        g = "sin datos"
    # El "uso" es una orientacion general: la fusion se decide par por par, segun la variable y la
    # finalidad, con cuatro condiciones (fecha, soporte, geometria y calidad).
    uso = {"completa": "orientativo: fusion a nivel de pixel (optico y radar) o de rasgo, si cada par cumple fecha, soporte, geometria y calidad; el LiDAR entra como referencia o en fusion de rasgo, nunca a nivel de pixel",
           "parcial": "orientativo: sinergia o fusion a nivel de decision; un par que cumpla fecha, soporte, geometria y calidad puede fusionarse a nivel de pixel",
           "parcial (sin optico)": "sinergia SAR multibanda; buscar el optico (Tp1_03) antes de fusionar",
           "un solo sensor cerca del evento": "mapa de ese sensor; los demas datos, solo para interpretar (sin fusion)",
           "historica": "nada dentro de la ventana: solo interpretacion de cambios de largo plazo",
           "sin datos": "no hay base para el practico: declarar y cambiar de sitio o fecha"}[g]
    return {"evento": evento, "ventana_dias": ventana, "optico": hay_opt,
            "bandas_SAR": "+".join(bandas_sar), "LiDAR": hay_lidar,
            "registros_en_ventana": len(cerca),
            "observaciones_independientes_en_ventana": len(observaciones(cerca)),
            "grado": g, "uso_en_el_curso": uso}, cerca


def figura(t, sitio, evento, ruta, dias_recuadro=30):
    """Linea de tiempo de las escenas verificadas y, debajo, un recuadro ampliado de +/- dias_recuadro
    alrededor del evento, donde cada producto de una misma toma se dibuja con su propio simbolo."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    orden = ["optico", "X", "C", "S", "L", "P", "LiDAR"]
    rotulos = ["Óptico", "SAR X", "SAR C", "SAR S", "SAR L", "SAR P", "LiDAR"]
    t = t.assign(fila=t.banda.map({b: i for i, b in enumerate(orden)}))
    t = t[t.fila.notna()]
    ev = pd.Timestamp(evento) if evento else None
    ev_txt = ev.strftime("%d/%m/%Y") if ev is not None else ""
    if ev is None:
        fig, ax = plt.subplots(figsize=(11, 4.2))
        axs = [ax]
    else:
        fig, axs = plt.subplots(2, 1, figsize=(12, 6.6), gridspec_kw={"height_ratios": [1, 1.15]})
    ax = axs[0]
    for _, f in t.iterrows():
        ax.plot(pd.Timestamp(f.fecha), f.fila, "o", ms=6, color="#1f3b73")
    if ev is not None:
        ax.axvline(ev, color="#d9822b", lw=2)
        ax.axvspan(ev - pd.Timedelta(days=dias_recuadro), ev + pd.Timedelta(days=dias_recuadro),
                   color="#d9822b", alpha=0.12, lw=0)
        ax.text(ev, len(orden) - 0.45, "evento %s " % ev_txt, color="#d9822b",
                fontsize=10, ha="right", va="center")
    ax.set_yticks(range(len(orden)))
    ax.set_yticklabels(rotulos, fontsize=10)
    ax.set_ylim(-0.6, len(orden) - 0.2)
    ax.grid(axis="x", alpha=0.3)
    ax.set_title("(a) Escenas verificadas sobre %s" % sitio, fontsize=12, loc="left")
    if ev is not None:
        # (b) recuadro ampliado: cada producto con su simbolo, desplazado un poco en vertical
        az = axs[1]
        cerca = t[(pd.to_datetime(t.fecha) - ev).abs() <= pd.Timedelta(days=dias_recuadro)]
        estilos = {}
        marcas = ["o", "s", "^", "D", "v", "P", "X", "h", "<", ">"]
        colores = ["#1f3b73", "#2a9d8f", "#e76f51", "#6a4c93", "#8a5a00", "#3a86ff", "#d62828", "#555555",
                   "#118ab2", "#ef476f"]
        for i, s in enumerate(sorted(cerca.sensor.unique())):
            estilos[s] = (marcas[i % len(marcas)], colores[i % len(colores)])
        for fila, g in cerca.groupby("fila"):
            sens = sorted(g.sensor.unique())
            for j, s in enumerate(sens):
                dy = (j - (len(sens) - 1) / 2) * 0.16
                gg = g[g.sensor == s]
                az.plot(pd.to_datetime(gg.fecha), [fila + dy] * len(gg), estilos[s][0], ms=7,
                        color=estilos[s][1], mec="white", mew=0.6, ls="none", label=s, zorder=3)
        az.axvline(ev, color="#d9822b", lw=2, alpha=0.6, zorder=1)
        az.text(ev, len(orden) - 0.45, " evento %s" % ev_txt, color="#d9822b", fontsize=10, ha="left", va="center")
        az.set_xlim(ev - pd.Timedelta(days=dias_recuadro + 1), ev + pd.Timedelta(days=dias_recuadro + 1))
        az.xaxis.set_major_locator(mdates.DayLocator(bymonthday=[1, 8, 15, 22]))
        az.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        az.set_yticks(range(len(orden)))
        az.set_yticklabels(rotulos, fontsize=10)
        az.set_ylim(-0.6, len(orden) - 0.2)
        az.grid(axis="x", alpha=0.3)
        az.set_title("(b) Ampliación de ± %d días alrededor del evento (fechas dd/mm)" % dias_recuadro,
                     fontsize=12, loc="left")
        h, l = az.get_legend_handles_labels()
        uniq = dict(zip(l, h))
        az.legend(uniq.values(), uniq.keys(), loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=9,
                  frameon=False, title="Producto", title_fontsize=10)
    fig.text(0.01, 0.01, "Fuente: planillas del Tp1 (Planetary Computer, ASF, NASA Earthdata, ESA MAAP, "
             "catálogo SAOCOM de CONAE, archivo del curso). Elaboración propia.", fontsize=9,
             family=["Arial", "Liberation Sans", "DejaVu Sans"])
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", required=True, choices=list(SITIOS.keys()))
    ap.add_argument("--evento", default="")
    ap.add_argument("--ventana", type=int, default=12, help="dias a cada lado del evento")
    ap.add_argument("--etiqueta", default="",
                    help="se agrega al nombre de las salidas (p. ej. 2023_Tp6): un mismo sitio con dos eventos "
                         "no se pisa")
    a = ap.parse_args()
    suf = a.sitio + ("_" + a.etiqueta if a.etiqueta else "")
    log = Bitacora(ruta_tp("Tp1", "05_Resultados", "06_Control_calidad"), "Tp1_07_%s" % suf)

    t = reunir(a.sitio, log, a.etiqueta)
    log("Escenas verificadas reunidas: %d registros (filas producto x fecha)" % len(t))
    log("  observaciones independientes (una por plataforma, banda y fecha): %d" % len(observaciones(t)))
    m = pd.crosstab(t.fecha, t.sensor + " (" + t.banda + ")") if len(t) else pd.DataFrame()
    m.to_csv(T("matriz_convergencia_%s.csv" % suf), encoding="utf-8-sig")
    for b, g in t.groupby("banda"):
        log("  %-7s %3d fechas   primera %s   ultima %s" % (b, g.fecha.nunique(), g.fecha.min(), g.fecha.max()))

    r = grado(t, a.evento, a.ventana)
    if r:
        info, cerca = r
        pd.DataFrame([info]).to_csv(T("grado_convergencia_%s.csv" % suf), index=False, encoding="utf-8-sig")
        log.titulo("Convergencia alrededor del %s (+/- %d dias)" % (a.evento, a.ventana))
        for _, f in cerca.sort_values("dias").iterrows():
            log("  %-16s %-6s %s  (%d dias)" % (f.sensor, f.banda, f.fecha, f.dias))
        log("  %d registros en la ventana = %d observaciones independientes (S1_SLC, S1_GRD y Sentinel-1 RTC "
            "de una fecha son la misma toma)" % (info["registros_en_ventana"],
                                                 info["observaciones_independientes_en_ventana"]))
        log("")
        log("GRADO: %s  ->  %s" % (info["grado"].upper(), info["uso_en_el_curso"]))
    png = ruta_tp("Tp1", "05_Resultados", "05_Graficos", "linea_tiempo_%s.png" % suf)
    if len(t):
        figura(t, a.sitio, a.evento, png)
        log("Figura:", png)
    log.cerrar("responder las preguntas del Tp1 (07_Preguntas_y_entrega) y pasar al Tp2")


if __name__ == "__main__":
    main()
