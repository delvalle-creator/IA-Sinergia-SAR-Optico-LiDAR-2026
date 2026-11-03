# -*- coding: utf-8 -*-
"""
Tp4_03_exactitud_y_area.py   [SE CORRE]   Tp4, paso 1 (autoprueba) y 8 de la guia
========================================================
Une los puntos etiquetados al azar (clase_ref) con la llave (clase_mapa) y
calcula, con el estimador ESTRATIFICADO de Olofsson et al. (2014):

  - la matriz de error en conteos y en PROPORCION DE AREA (p_ij);
  - la exactitud global, la del usuario (1 - comision) y la del productor
    (1 - omision), cada una con su intervalo de confianza del 95 %;
  - el AREA de cada clase estimada con la referencia, con su intervalo de
    confianza, al lado del area que "dice" el mapa contando pixeles.

Las formulas (i = clase del mapa = estrato, j = clase de referencia)
  W_i = A_i / A                          proporcion de area del estrato
  p_ij = W_i * n_ij / n_i.               proporcion de area de la celda
  O = sum_i p_ii                         exactitud global
  U_i = p_ii / p_i.                      exactitud del usuario
  P_j = p_jj / p_.j                      exactitud del productor
  A_j = A * p_.j                         area estimada de la clase j
  V(O)   = sum_i W_i^2 U_i (1-U_i) / (n_i.-1)
  V(U_i) = U_i (1-U_i) / (n_i.-1)
  V(p_.j)= sum_i W_i^2 (n_ij/n_i.)(1-n_ij/n_i.) / (n_i.-1)
  V(P_j) segun la ecuacion 7 de Olofsson et al. (2014)
  IC 95 % = estimado +/- 1,96 * raiz(V)

  Puntos cuya clase de referencia no existe en el mapa: NO se excluyen.
  Son omision del mapa y entran como columnas de referencia sin estrato.
  Cuando un estrato acierta todos (o ninguno), el IC de la aproximacion normal da +/- 0;
  y con pocos aciertos (n*p < 5) la aproximacion normal puede dar limites negativos o
  mayores que 1. Por eso la tabla trae, ademas del "+/-":
    - IC95_area_inf / IC95_area_sup: limites del area truncados en [0, area total];
    - usuario_inf / usuario_sup y productor_inf / productor_sup: limites truncados en [0, 1];
    - usuario_Wilson_inf / usuario_Wilson_sup: intervalo de Wilson del usuario de cada estrato
      (diagnostico binomial; se imprime SIEMPRE, para todos los estratos);
    - productor_estimable: "no" cuando la clase no tiene ningun punto de referencia acertado
      (0 de 0, o 0 aciertos): ahi el "0,000 +/- 0,000" no es precision, es falta de datos.

AUTOPRUEBA
  python Tp4_03_exactitud_y_area.py --autoprueba
  reproduce el ejemplo numerico publicado por Olofsson et al. (2014)
  (deforestacion: area 21.158 ha +/- 6.158 ha; usuario 0,88; productor 0,75;
  global 0,95). Si no da esas cifras, el programa esta mal: no se usa.

USO
    python Tp4_03_exactitud_y_area.py --nombre A1_variante_multisensor
    (lee <nombre>_puntos_a_etiquetar.gpkg, <nombre>_llave_NO_ABRIR.csv y
     <nombre>_diseno_muestral.csv que dejo Tp4_02)
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

Z = 1.96


def wilson(k, n, z=Z):
    """Intervalo de Wilson del 95 % para una proporcion k/n (diagnostico binomial por estrato)."""
    if n == 0:
        return (np.nan, np.nan)
    ph = k / n
    den = 1 + z ** 2 / n
    c = (ph + z ** 2 / (2 * n)) / den
    h = z * np.sqrt(ph * (1 - ph) / n + z ** 2 / (4 * n ** 2)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def estimar(n, pixeles, area_pixel_ha, nombres, nombres_ref=None):
    """n: matriz de conteos (filas = clase del mapa = estrato, columnas = referencia).
    Las columnas pueden ser mas que las filas: las primeras K son las clases del mapa (en el mismo
    orden que las filas) y las siguientes, clases de referencia que el mapa no tiene. Esos puntos
    NO se excluyen: son errores del mapa (omision de una clase entera) y entran en el estimador."""
    n = np.asarray(n, dtype="float64")
    pixeles = np.asarray(pixeles, dtype="float64")
    K, M = n.shape
    nombres_ref = list(nombres) + list(nombres_ref or [])[len(nombres):] if nombres_ref else list(nombres)
    ni = n.sum(axis=1)
    if np.any(ni < 2):
        raise ValueError("Cada estrato necesita al menos 2 puntos etiquetados.")
    W = pixeles / pixeles.sum()
    A = pixeles.sum() * area_pixel_ha
    p = (W[:, None] * n / ni[:, None])                     # K x M
    pi_, p_j = p.sum(axis=1), p.sum(axis=0)
    diag = np.array([p[i, i] for i in range(K)])
    O = diag.sum()
    U = diag / pi_
    pjj = np.concatenate([diag, np.zeros(M - K)])
    P = np.where(p_j > 0, pjj / np.where(p_j > 0, p_j, 1), np.nan)
    V_O = np.sum(W ** 2 * U * (1 - U) / (ni - 1))
    V_U = U * (1 - U) / (ni - 1)
    V_pj = np.array([np.sum(W ** 2 * (n[:, j] / ni) * (1 - n[:, j] / ni) / (ni - 1)) for j in range(M)])
    # productor (Olofsson et al. 2014, ec. 7), en conteos de pixeles N_i.
    Ni = pixeles
    Nj = np.array([np.sum(Ni * n[:, j] / ni) for j in range(M)])
    V_P = np.full(M, np.nan)
    for j in range(M):
        if Nj[j] == 0:
            continue
        if j < K:
            t1 = Ni[j] ** 2 * (1 - P[j]) ** 2 * U[j] * (1 - U[j]) / (ni[j] - 1)
        else:
            t1 = 0.0                                       # el mapa no tiene estrato de esa clase
        otros = [i for i in range(K) if i != j]
        t2 = P[j] ** 2 * sum(Ni[i] ** 2 * (n[i, j] / ni[i]) * (1 - n[i, j] / ni[i]) / (ni[i] - 1) for i in otros)
        V_P[j] = (t1 + t2) / Nj[j] ** 2
    Uc = np.concatenate([U, np.full(M - K, np.nan)])
    VUc = np.concatenate([V_U, np.full(M - K, np.nan)])
    wl = [wilson(n[i, i], ni[i]) for i in range(K)] + [(np.nan, np.nan)] * (M - K)
    pix_c = np.concatenate([pixeles, np.zeros(M - K)])
    nic = np.concatenate([ni, np.zeros(M - K)])
    clase = pd.DataFrame({
        "clase": nombres_ref, "n_puntos_estrato": nic.astype(int),
        "area_mapa_ha": (pix_c * area_pixel_ha).round(1),
        "area_estimada_ha": (A * p_j).round(1),
        "IC95_area_ha": (Z * A * np.sqrt(V_pj)).round(1),
        "exactitud_usuario": np.round(Uc, 3), "IC95_usuario": np.round(Z * np.sqrt(VUc), 3),
        "usuario_Wilson_inf": np.round([w[0] for w in wl], 3), "usuario_Wilson_sup": np.round([w[1] for w in wl], 3),
        "comision": np.round(1 - Uc, 3),
        "exactitud_productor": np.round(P, 3), "IC95_productor": np.round(Z * np.sqrt(V_P), 3),
        "omision": np.round(1 - P, 3)})
    # Limites truncados (la aproximacion normal no sabe que un area no puede ser negativa
    # ni una proporcion mayor que 1). El "+/-" se conserva para comparar con el articulo.
    clase["IC95_area_inf"] = np.clip(clase.area_estimada_ha - clase.IC95_area_ha, 0, A).round(1)
    clase["IC95_area_sup"] = np.clip(clase.area_estimada_ha + clase.IC95_area_ha, 0, A).round(1)
    clase["usuario_inf"] = np.clip(clase.exactitud_usuario - clase.IC95_usuario, 0, 1).round(3)
    clase["usuario_sup"] = np.clip(clase.exactitud_usuario + clase.IC95_usuario, 0, 1).round(3)
    clase["productor_inf"] = np.clip(clase.exactitud_productor - clase.IC95_productor, 0, 1).round(3)
    clase["productor_sup"] = np.clip(clase.exactitud_productor + clase.IC95_productor, 0, 1).round(3)
    acert = np.concatenate([diag, np.zeros(M - K)]) > 0
    clase["productor_estimable"] = np.where(acert, "si", "no")
    # n*p < 5 o n*(1-p) < 5 en el estrato: la aproximacion normal del usuario es pobre
    k_ok = np.concatenate([[n[i, i] for i in range(K)], np.full(M - K, np.nan)])
    clase["aviso_normal"] = np.where((nic > 0) & ((k_ok < 5) | (nic - k_ok < 5)),
                                     "aproximacion normal inadecuada (n*p < 5): leer Wilson", "")
    glob = {"exactitud_global": round(O, 4), "IC95_global": round(Z * np.sqrt(V_O), 4),
            "area_total_ha": round(A, 1), "n_total": int(n.sum())}
    return clase, glob, pd.DataFrame(p, index=nombres, columns=nombres_ref)


def autoprueba():
    """Ejemplo numerico de Olofsson et al. (2014), Remote Sensing of Environment 148: 42-57."""
    nombres = ["deforestacion", "ganancia", "bosque_estable", "no_bosque_estable"]
    n = [[66, 0, 5, 4], [0, 55, 8, 12], [1, 0, 153, 11], [2, 1, 9, 313]]
    pix = [200000, 150000, 3200000, 6450000]          # pixeles de 30 m (0,09 ha)
    c, g, _ = estimar(n, pix, 0.09, nombres)
    print(c.to_string(index=False))
    print(g)
    d = c.iloc[0]
    ok = (abs(d.area_estimada_ha - 21158) < 30 and abs(d.IC95_area_ha - 6158) < 30
          and abs(d.exactitud_usuario - 0.88) < 0.005 and abs(d.exactitud_productor - 0.75) < 0.005
          and abs(g["exactitud_global"] - 0.95) < 0.005)
    print("AUTOPRUEBA:", "CORRECTA (coincide con el ejemplo publicado)" if ok else "FALLA: NO USAR")
    return ok


def main():
    import geopandas as gpd
    from configuracion_comun import ruta_tp
    from funciones_comunes import Bitacora

    ap = argparse.ArgumentParser()
    ap.add_argument("--nombre", default="")
    ap.add_argument("--autoprueba", action="store_true")
    ap.add_argument("--nombres_clase", default="", help='p. ej. "1=quemado,2=no_quemado"')
    a = ap.parse_args()
    if a.autoprueba:
        sys.exit(0 if autoprueba() else 1)
    if not a.nombre:
        sys.exit("Falta --nombre (el mismo que uso Tp4_02).")
    log = Bitacora(ruta_tp("Tp4", "05_Resultados", "06_Control_calidad"), "Tp4_03_%s" % a.nombre)
    carpeta = ruta_tp("Tp4", "04_Tablas_de_trabajo")
    pts = gpd.read_file(os.path.join(carpeta, "%s_puntos_a_etiquetar.gpkg" % a.nombre), layer="puntos")
    llave = pd.read_csv(os.path.join(carpeta, "%s_llave_NO_ABRIR.csv" % a.nombre), encoding="utf-8-sig")
    dis = pd.read_csv(ruta_tp("Tp4", "05_Resultados", "04_Tablas", "%s_diseno_muestral.csv" % a.nombre),
                      encoding="utf-8-sig")
    t = pts.merge(llave, on="id")
    sin = t["clase_ref"].isna() | (t["clase_ref"].astype(str).str.strip() == "")
    if sin.any():
        log("AVISO: %d de %d puntos sin etiquetar. Se calculan con los etiquetados, y se declara." % (sin.sum(), len(t)))
    t = t[~sin].copy()
    t["clase_ref"] = t["clase_ref"].astype(float).astype(int)
    clases = sorted(int(x) for x in dis.clase_mapa)
    fuera = ~t.clase_ref.isin(clases)
    extra = sorted(int(x) for x in t.loc[fuera, "clase_ref"].unique())
    if extra:
        log("AVISO: %d puntos tienen una clase de referencia que el mapa no tiene (%s)."
            % (fuera.sum(), extra))
        log("       NO se excluyen: son errores del mapa (omite una clase entera). Entran en la matriz como")
        log("       columnas de referencia sin estrato: bajan la exactitud de su estrato y suman area a esa clase.")
    nombres = {}
    if a.nombres_clase:
        nombres = {int(k): v for k, v in (x.split("=") for x in a.nombres_clase.split(","))}
    etiquetas = [nombres.get(c, str(c)) for c in clases]
    cols = clases + extra
    etiquetas_ref = [nombres.get(c, str(c)) for c in cols]
    n = np.zeros((len(clases), len(cols)))
    for _, r in t.iterrows():
        n[clases.index(int(r.clase_mapa)), cols.index(int(r.clase_ref))] += 1
    pix = [int(dis.loc[dis.clase_mapa == c, "pixeles"].sum()) for c in clases]
    sup_ha = dis.superficie_ha.sum() / dis.pixeles.sum()
    c, g, p = estimar(n, pix, sup_ha, etiquetas, etiquetas_ref)
    c.insert(0, "codigo", cols)
    log.titulo("Matriz de error en CONTEOS (filas = mapa, columnas = referencia)")
    log(pd.DataFrame(n.astype(int), index=etiquetas, columns=etiquetas_ref).to_string())
    log.titulo("Matriz de error en PROPORCION DE AREA (p_ij)")
    log(p.round(4).to_string())
    log.titulo("Exactitud y area por clase (IC del 95 %)")
    log(c.to_string(index=False))
    log("")
    log("Exactitud global: %.3f +/- %.3f   (n = %d puntos)" % (g["exactitud_global"], g["IC95_global"], g["n_total"]))
    log.titulo("Limites del IC del 95 % truncados e intervalo de Wilson del usuario (todas las clases)")
    est = c[c.n_puntos_estrato > 0]
    for _, f in c.iterrows():
        if f.n_puntos_estrato > 0:
            k = int(round(f.exactitud_usuario * f.n_puntos_estrato))
            log("%-22s usuario %d de %d = %.3f   normal truncado %.3f a %.3f   Wilson %.2f a %.2f   area %.1f a %.1f ha%s"
                % (f.clase, k, f.n_puntos_estrato, f.exactitud_usuario, f.usuario_inf, f.usuario_sup,
                   f.usuario_Wilson_inf, f.usuario_Wilson_sup, f.IC95_area_inf, f.IC95_area_sup,
                   ("   <- " + f.aviso_normal) if f.aviso_normal else ""))
        else:
            log("%-22s sin estrato en el mapa: area %.1f a %.1f ha; productor %s"
                % (f.clase, f.IC95_area_inf, f.IC95_area_sup,
                   "no estimable (ningun acierto posible)" if f.productor_estimable == "no" else "%.3f" % f.exactitud_productor))
    for _, f in c[c.productor_estimable == "no"].iterrows():
        log("OJO: el productor de %s es 0,000 (no estimable): ningun punto de esa clase fue acertado;"
            " el +/- 0 no es precision." % f.clase)
    neg = c[(c.area_estimada_ha - c.IC95_area_ha < 0) | (c.exactitud_usuario - c.IC95_usuario < 0)]
    for _, f in neg.iterrows():
        log("OJO: en %s la aproximacion normal da un limite inferior negativo: se trunca en 0 (columnas _inf)."
            % f.clase)
    deg = est[est.IC95_usuario == 0]
    if len(deg):
        nmin, nmax = int(est.n_puntos_estrato.min()), int(est.n_puntos_estrato.max())
        nn = ("%d" % nmin) if nmin == nmax else ("%d a %d" % (nmin, nmax))
        log("OJO: %d estrato(s) aciertan todos sus puntos (%s): el IC de +/- 0 no es certeza; vale el de Wilson."
            % (len(deg), ", ".join(deg.clase.astype(str))))
        log("     Con %s puntos por estrato no se estiman bien las colas: cero errores observados no es error nulo." % nn)
    out = ruta_tp("Tp4", "05_Resultados", "04_Tablas", "%s_exactitud_y_area.csv" % a.nombre)
    c.assign(**g).to_csv(out, index=False, encoding="utf-8-sig")
    log("Tabla:", out)
    log.cerrar("python Tp4_04_tabla_de_variantes.py")


if __name__ == "__main__":
    main()
