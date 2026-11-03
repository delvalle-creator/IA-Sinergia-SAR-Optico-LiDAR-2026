# -*- coding: utf-8 -*-
"""
funciones_cambio.py
===================
Las herramientas que comparten los practicos especificos (Tp5 a Tp10):
deteccion de cambios, umbrales, SINERGIA y FUSION.

La distincion que ordena todo (presentacion 01, diapositivas 10 a 12)
---------------------------------------------------------------------
  SINERGIA  ocurre en el razonamiento del analista. Cada sensor produce SU
            mapa o SU indicador; el analista los compara y explica por que
            coinciden o difieren. No se genera un producto unico.
            -> funcion: tabla_de_coincidencias()
  FUSION    ocurre en el algoritmo y produce UN producto. Tres niveles:
            pixel    se apilan bandas en una grilla comun y se clasifica
            rasgo    se extraen variables de cada sensor y entran a un modelo
            decision cada sensor produce su mapa y se combinan las decisiones
            -> funciones: fusion_pixel_o_rasgo() (Random Forest) y
                          fusion_decision() (reglas escritas)
  "Toda fusion bien disenada busca sinergia; no toda sinergia requiere fusion."

Unidades: los cambios de radar se calculan como cociente de potencias en
LINEAL y se expresan en dB:  delta_dB = 10*log10(post/pre). Es lo mismo que
restar dB, pero solo si cada lado se promedio antes en lineal.
"""
import os

import numpy as np

from funciones_comunes import lin_a_db, umbral_otsu


# ============================================================ INDICADORES
def cociente_db(pre_lineal, post_lineal):
    """Cambio de retrodispersion: 10*log10(post/pre). Negativo = perdida de senal."""
    pre = np.asarray(pre_lineal, dtype="float64")
    post = np.asarray(post_lineal, dtype="float64")
    ok = np.isfinite(pre) & np.isfinite(post) & (pre > 0) & (post > 0)
    out = np.full(pre.shape, np.nan)
    out[ok] = 10.0 * np.log10(post[ok] / pre[ok])
    return out.astype("float32")


def indice_normalizado(a, b):
    """(a - b) / (a + b), con NaN donde el denominador es cero o falta dato."""
    a = np.asarray(a, dtype="float64")
    b = np.asarray(b, dtype="float64")
    den = a + b
    out = np.where(np.isfinite(den) & (np.abs(den) > 1e-9), (a - b) / den, np.nan)
    return out.astype("float32")


def nbr(b08, b12):
    """Normalized Burn Ratio: (NIR - SWIR2) / (NIR + SWIR2)."""
    return indice_normalizado(b08, b12)


def rdnbr(nbr_pre, nbr_post, nbr_min=0.05):
    """dNBR relativizado (Miller y Thode, 2007): dNBR / raiz(|NBR_pre|).
    Donde |NBR_pre| < nbr_min (agua, suelo desnudo, nube residual) el cociente explota: queda sin dato."""
    d = np.asarray(nbr_pre, "float64") - np.asarray(nbr_post, "float64")
    pre = np.abs(np.asarray(nbr_pre, "float64"))
    return np.where(pre >= nbr_min, d / np.sqrt(np.where(pre > 0, pre, 1)), np.nan).astype("float32")


# ============================================================ UMBRALES
def umbral_documentado(valores, nombre, ruta_png, metodo="otsu", manual=None, signo="<",
                       etiqueta_y="pixeles", recortar_extremos=True, nota_extremos=False, coma_decimal=False):
    """Calcula (Otsu) o toma (manual) un umbral y guarda el histograma con la linea.

    signo: "<" si la clase de interes esta por DEBAJO del umbral (agua en VV,
    caida de VH en un incendio); ">" si esta por encima (dNBR).
    Devuelve (umbral, texto_para_la_bitacora).
    Opciones agregadas el 27/10/2026 (los valores por defecto dejan la figura como antes):
      etiqueta_y         rotulo del eje vertical ("píxeles", con tilde, en los practicos nuevos).
      recortar_extremos  True: los valores fuera del 0,5-99,5 % se llevan al borde y forman una barra
                         alta en cada extremo; False: se dejan fuera del grafico.
      nota_extremos      True: escribe debajo del grafico que esas barras acumulan los valores fuera de rango.
      coma_decimal       True: numeros del eje con coma decimal y punto de miles.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    v = np.asarray(valores, "float64")
    v = v[np.isfinite(v)]
    if metodo == "manual":
        u, n = float(manual), v.size
        txt = "umbral MANUAL %.3f (justificar con el histograma y la referencia)" % u
    else:
        u, n = umbral_otsu(v)
        txt = "umbral de OTSU %.3f calculado sobre %d valores" % (u, n)
    frac = float(np.mean(v < u) if signo == "<" else np.mean(v > u))
    txt += "; deja %.1f %% de los pixeles en la clase de interes (%s %.3f)" % (100 * frac, signo, u)
    lo, hi = np.percentile(v, [0.5, 99.5])
    fig, ax = plt.subplots(figsize=(7, 3.6))
    vh = np.clip(v, lo, hi) if recortar_extremos else v[(v >= lo) & (v <= hi)]
    ax.hist(vh, bins=200, color="#1f3b73")
    ax.axvline(u, color="#d9822b", lw=2)
    ax.set_title("%s: %s" % (nombre, txt.split(";")[0]), fontsize=10)
    ax.set_xlabel(nombre)
    ax.set_ylabel(etiqueta_y)
    if coma_decimal:
        ax.set_title("%s\numbral %s %s %s (línea naranja)" % (
            nombre, "manual" if metodo == "manual" else "de Otsu", signo,
            ("%.2f" % u).replace(".", ",")), fontsize=10)
        from matplotlib.ticker import FuncFormatter
        _f = lambda x, p: ("{:,.%df}" % (0 if abs(x) >= 100 else 2 if abs(x) < 1 else 1)).format(x).replace(
            ",", "X").replace(".", ",").replace("X", ".")
        ax.xaxis.set_major_formatter(FuncFormatter(_f))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: "{:,.0f}".format(x).replace(",", ".")))
    if nota_extremos:
        fig.text(0.01, 0.01, ("Las barras de los extremos acumulan el 1 % de los valores que cae fuera del rango mostrado."
                              if recortar_extremos else "Se muestra el 99 % central de los valores."), fontsize=8)
    fig.tight_layout(rect=(0, 0.05 if nota_extremos else 0, 1, 1))
    os.makedirs(os.path.dirname(ruta_png), exist_ok=True)
    fig.savefig(ruta_png, dpi=130)
    plt.close(fig)
    return u, txt


def aplicar_umbral(arr, u, signo="<"):
    """Mapa binario: 1 = clase de interes, 0 = resto, NaN = sin dato."""
    a = np.asarray(arr, "float64")
    m = (a < u) if signo == "<" else (a > u)
    return np.where(np.isfinite(a), m.astype("float32"), np.nan).astype("float32")


# ============================================================ SINERGIA
def tabla_de_coincidencias(mapas, clases_control=None, nombres_control=None):
    """SINERGIA: compara mapas binarios de distintos sensores SIN fusionarlos.

    mapas: {nombre_sensor: arreglo 0/1/NaN}
    Devuelve (DataFrame con el acuerdo por par de sensores, arreglo con cuantos
    sensores marcan la clase en cada pixel). Si se pasa la cobertura de
    control, la tabla separa el acuerdo por clase de control: es lo que permite
    explicar, por ejemplo, por que la banda C ve la quema del pajonal y la
    banda L la del bosque de albardon.
    """
    import itertools
    import pandas as pd

    nombres = list(mapas)
    pila = np.stack([np.asarray(mapas[n], "float32") for n in nombres])
    todos = np.all(np.isfinite(pila), axis=0)
    suma = np.where(todos, np.nansum(pila, axis=0), np.nan).astype("float32")
    filas = []
    regiones = {"todo el sitio": todos}
    if clases_control is not None:
        for c in np.unique(clases_control[todos & (clases_control > 0)]):
            etiqueta = (nombres_control or {}).get(int(c), str(int(c)))
            regiones["control: %s" % etiqueta] = todos & (clases_control == c)
    for reg, msk in regiones.items():
        if msk.sum() == 0:
            continue
        for x, y in itertools.combinations(range(len(nombres)), 2):
            a, b = pila[x][msk], pila[y][msk]
            filas.append({"region": reg, "sensor_1": nombres[x], "sensor_2": nombres[y],
                          "pixeles": int(msk.sum()),
                          "%_clase_sensor_1": round(float(100 * a.mean()), 1),
                          "%_clase_sensor_2": round(float(100 * b.mean()), 1),
                          "%_ambos": round(float(100 * np.mean((a == 1) & (b == 1))), 1),
                          "%_solo_1": round(float(100 * np.mean((a == 1) & (b == 0))), 1),
                          "%_solo_2": round(float(100 * np.mean((a == 0) & (b == 1))), 1),
                          "acuerdo_%": round(float(100 * np.mean(a == b)), 1)})
    return pd.DataFrame(filas), suma


# ============================================================ FUSION
def fusion_decision(mapas, regla="mayoria", k=None, minimo_votos=1):
    """FUSION A NIVEL DE DECISION: combina mapas binarios con una regla escrita.

    regla: "union"        1 si al menos un sensor dice 1   (maxima deteccion)
           "interseccion" 1 si todos dicen 1                (maxima confianza)
           "mayoria"      1 si mas de la mitad dice 1
           "k_de_n"       1 si al menos k sensores dicen 1
    Donde un sensor no tiene dato, decide el resto (y se cuenta cuantos votaron).
    minimo_votos: pixeles con menos sensores con dato quedan SIN DECIDIR (NaN).
    Para una interseccion estricta ("todos los sensores de acuerdo") use
    minimo_votos = numero de sensores: si no, un solo sensor decide solo.
    """
    pila = np.stack([np.asarray(m, "float32") for m in mapas.values()])
    votos = np.sum(np.isfinite(pila), axis=0)
    si = np.nansum(pila, axis=0)
    if regla == "union":
        out = si >= 1
    elif regla == "interseccion":
        out = (si == votos) & (votos > 0)
    elif regla == "mayoria":
        out = si > votos / 2.0
    elif regla == "k_de_n":
        out = si >= (k or 2)
    else:
        raise ValueError("regla desconocida: %s" % regla)
    return np.where(votos >= max(minimo_votos, 1), out.astype("float32"), np.nan).astype("float32"), votos


def leer_entrenamiento(ruta_gpkg, grilla, capa="entrenamiento", campo="codigo"):
    """Poligonos de entrenamiento (codigo entero > 0) rasterizados en la grilla."""
    from funciones_comunes import rasterizar

    return rasterizar(ruta_gpkg, grilla, campo=campo, capa=capa)


def fusion_pixel_o_rasgo(capas, entrenamiento, semilla=2026, n_arboles=300, max_muestras=20000, equilibrar=True):
    """FUSION A NIVEL DE PIXEL o DE RASGO con Random Forest.

    Nivel de PIXEL: capas = bandas originales apiladas (gamma0 en dB, reflectancias).
    Nivel de RASGO: capas = variables derivadas de cada sensor (delta VH, delta HV, dNBR...).
    El algoritmo es el mismo; lo que cambia, y se declara, es QUE se le da.

    Devuelve (mapa de clases, probabilidad de la clase ganadora, dict con
    exactitud fuera de bolsa e importancia de cada capa).
    equilibrar=True (por defecto, como hasta el 23/10/2026): el mismo numero de pixeles por clase y
    class_weight="balanced". Equivale a suponer que todas las clases ocupan lo mismo: sobrestima las
    clases chicas. equilibrar=False (24/10/2026): se usan los pixeles tal como vienen (el
    entrenamiento ya debe estar en proporcion al paisaje, por ejemplo entrenamiento_mapbiomas()),
    sin pesos; si son mas que max_muestras se sortean al azar sin cambiar la proporcion.
    ATENCION: la exactitud fuera de bolsa se calcula con pixeles vecinos de los
    mismos poligonos de entrenamiento y SIEMPRE es optimista. La exactitud que
    se informa es la del Tp4, con referencia independiente (diapositiva 14,
    ultimo error de la tabla).
    """
    from sklearn.ensemble import RandomForestClassifier

    nombres = list(capas)
    X = np.stack([np.asarray(capas[n], "float32") for n in nombres], axis=-1)
    validos = np.all(np.isfinite(X), axis=-1)
    y = np.asarray(entrenamiento)
    sel = validos & (y > 0)
    if sel.sum() < 50:
        raise ValueError("Muy pocos pixeles de entrenamiento con dato en todas las capas (%d)." % sel.sum())
    rng = np.random.default_rng(semilla)
    idx = np.flatnonzero(sel)
    if equilibrar:
        # muestreo equilibrado por clase para que una clase grande no se coma al resto
        elegido = []
        for c in np.unique(y[sel]):
            ic = idx[y.ravel()[idx] == c]
            elegido.append(rng.choice(ic, size=min(ic.size, max_muestras // len(np.unique(y[sel]))), replace=False))
        elegido = np.concatenate(elegido)
    else:
        elegido = idx if idx.size <= max_muestras else rng.choice(idx, size=max_muestras, replace=False)
    Xe = X.reshape(-1, len(nombres))[elegido]
    ye = y.ravel()[elegido]
    rf = RandomForestClassifier(n_estimators=n_arboles, oob_score=True, n_jobs=-1,
                                random_state=semilla, class_weight="balanced" if equilibrar else None,
                                min_samples_leaf=2)
    rf.fit(Xe, ye)
    mapa = np.full(validos.shape, np.nan, dtype="float32")
    prob = np.full(validos.shape, np.nan, dtype="float32")
    Xv = X[validos]
    for i in range(0, Xv.shape[0], 500000):
        p = rf.predict_proba(Xv[i:i + 500000])
        bloque = np.flatnonzero(validos.ravel())[i:i + 500000]
        mapa.ravel()[bloque] = rf.classes_[p.argmax(1)]
        prob.ravel()[bloque] = p.max(1)
    info = {"exactitud_fuera_de_bolsa_OPTIMISTA": round(float(rf.oob_score_), 3),
            "pixeles_entrenamiento": int(ye.size),
            "importancia": {n: round(float(v), 3) for n, v in zip(nombres, rf.feature_importances_)}}
    return mapa, prob, info


def figura_mapa(arr, ruta, titulo, fuente, etiquetas=None, cmap="viridis"):
    """Figura de un mapa (clases o continuo) con la cita 'Fuente' al pie."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    alto, ancho = arr.shape
    h = 7.5 * alto / ancho
    fig = plt.figure(figsize=(7.5, h + 1.2))
    ancho_ax = 1.0 if etiquetas else 0.86          # deja lugar a la barra de colores y sus numeros
    ax = fig.add_axes([0, 1.0 / (h + 1.2), ancho_ax, h / (h + 1.2)])
    im = ax.imshow(arr, cmap=cmap, interpolation="nearest")
    ax.set_axis_off()
    ax.set_title(titulo, fontsize=11)
    if etiquetas:
        cm = plt.get_cmap(cmap)
        vmin, vmax = np.nanmin(arr), np.nanmax(arr)
        hs = [Patch(color=cm((k - vmin) / max(vmax - vmin, 1)), label=v) for k, v in etiquetas.items()]
        ax.legend(handles=hs, loc="lower right", fontsize=8, framealpha=0.9)
    else:
        cax = fig.add_axes([0.88, 1.0 / (h + 1.2) + 0.25 * h / (h + 1.2), 0.025, 0.5 * h / (h + 1.2)])
        fig.colorbar(im, cax=cax)
    fig.text(0.01, 0.01, "Fuente: " + fuente, fontsize=8, wrap=True)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    fig.savefig(ruta, dpi=140)
    plt.close(fig)
