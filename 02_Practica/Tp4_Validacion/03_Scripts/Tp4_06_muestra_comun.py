# -*- coding: utf-8 -*-
"""
Tp4_06_muestra_comun.py   [SE CORRE]   Tp4, paso 9 (alternativa) y paso 10 (otra equivalencia)
==========================================================================================
UNA SOLA MUESTRA PARA VARIOS MAPAS (Stehman, 2014)

Con Tp4_02 cada mapa se valida con SU muestra, estratificada por SUS clases: cuatro
variantes son cuatro muestras y cuatro etiquetados. Stehman (2014) mostro que se
puede usar una sola muestra estratificada para evaluar varios mapas, aunque los
estratos NO sean las clases de cada mapa. Las ventajas:
  - se etiqueta una sola vez (menos puntos en total);
  - las comparaciones entre mapas son PAREADAS (los mismos puntos), y la
    varianza de la diferencia se calcula directamente, sin suponer muestras
    independientes.

DOS USOS
  1) --disenar: arma la muestra comun para varias variantes de un practico.
     Estratos = combinaciones de las variantes. Para mapas de dos clases
     (1 = clase de interes, 2 = no) los estratos son:
         "todas"       todas las variantes dicen clase de interes
         "ninguna"     ninguna variante la dice
         "desacuerdo"  algunas si y otras no
     Ahi esta la informacion: en el estrato de desacuerdo se decide que variante
     acierta. Por eso ese estrato recibe mas puntos (--reparto).
     Salidas: <NOMBRE>_puntos_a_etiquetar.gpkg (sin clases), <NOMBRE>_llave_NO_ABRIR.csv
     (estrato y clase de CADA variante en cada punto) y <NOMBRE>_diseno_muestral.csv.

  2) --estimar: con los puntos ya etiquetados, estima para CADA mapa (columna de la
     llave) la exactitud global, la del usuario y la del productor de cada clase y el
     area de cada clase, con su IC del 95 %, y la DIFERENCIA de exactitud global y de
     omision/comision de la clase de interes entre cada par de mapas (pareada).
     Sirve tambien para evaluar un mapa que no se uso para estratificar: por ejemplo,
     MapBiomas 2025 con otra equivalencia de clases (Tp4_05 --equivalencias), sobre la
     misma muestra del paso 10. Para eso, --agregar_mapa suma a la llave la clase de
     ese otro mapa en cada punto.

LAS FORMULAS (Stehman, 2014; h = estrato, N_h pixeles, n_h puntos)
  total estimado de y:  Y = sum_h N_h * media_h(y)
  proporcion:           p = Y / N
  cociente (usuario, productor):  R = Y / X  (y = acierto de la clase, x = pertenece a la clase)
  V(R) = (1 / X^2) * sum_h N_h^2 * (s2_y,h + R^2 s2_x,h - 2 R s_xy,h) / n_h
  Sin correccion por poblacion finita (como Olofsson et al., 2014). Con estratos iguales a
  las clases del mapa, estas formulas dan lo mismo que Tp4_03 (se comprueba con --estimar).

USO
  python Tp4_06_muestra_comun.py --disenar --nombre A1_muestra_comun --tp Tp5 ^
      --mapa "Optico solo|..\\..\\Tp5_Incendios\\05_Resultados\\02_Rasters\\A1_variante_optico.tif" ^
      --mapa "SAR solo (C)|..\\..\\Tp5_Incendios\\05_Resultados\\02_Rasters\\A1_variante_C.tif" ^
      --mapa "SAR multibanda|..\\..\\Tp5_Incendios\\05_Resultados\\02_Rasters\\A1_variante_CL.tif" ^
      --mapa "Multisensor|..\\..\\Tp5_Incendios\\05_Resultados\\02_Rasters\\A1_variante_multisensor.tif" ^
      --n 200 --reparto "todas=50,ninguna=50,desacuerdo=100"
  (etiquetar en QGIS como en el paso 7: 1 = clase de interes, 2 = no)
  python Tp4_06_muestra_comun.py --estimar --nombre A1_muestra_comun --clase 1

  Paso 10, otra equivalencia sobre la misma muestra:
  python Tp4_05_mapbiomas_como_mapa.py --sitio B_CONCORDIA --equivalencias mi_equivalencia.csv --sufijo abiertos_herbaceo
  python Tp4_06_muestra_comun.py --agregar_mapa ..\\02_Subsets_SNAP_QGIS\\B_CONCORDIA_mapbiomas_2025_abiertos_herbaceo_clases_curso_20m.tif ^
      --nombre B_CONCORDIA_mapbiomas_2025_clases_curso_20m --columna abiertos_herbaceo
  python Tp4_06_muestra_comun.py --estimar --nombre B_CONCORDIA_mapbiomas_2025_clases_curso_20m --clase 3

REFERENCIA
  Stehman, S. V. (2014). Estimating area and map accuracy for stratified random sampling
  when the strata are different from the map classes. International Journal of Remote
  Sensing, 35, 4923-4939. https://doi.org/10.1080/01431161.2014.930207
"""
import argparse
import itertools
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import numpy as np                                                    # noqa: E402
import pandas as pd                                                   # noqa: E402

# ------------------------------------------------------------------ parametros
SEMILLA = 2026          # la misma semilla que Tp4_02: el diseno se puede rehacer identico
Z = 1.96                # IC del 95 %


# ------------------------------------------------------------------ estimador
def _tot(N, n, est, v):
    """Total estimado de v y su varianza (sin correccion por poblacion finita)."""
    Y, V = 0.0, 0.0
    for h in N:
        sel = est == h
        vh = v[sel]
        if vh.size == 0:
            continue
        Y += N[h] * vh.mean()
        if vh.size > 1:
            V += N[h] ** 2 * vh.var(ddof=1) / vh.size
    return Y, V


def _cociente(N, est, y, x):
    """Cociente R = Y / X (Stehman, 2014) y su varianza."""
    Y, _ = _tot(N, None, est, y)
    X, _ = _tot(N, None, est, x)
    if X == 0:
        return np.nan, np.nan
    R = Y / X
    V = 0.0
    for h in N:
        sel = est == h
        if sel.sum() < 2:
            continue
        yh, xh = y[sel], x[sel]
        s2y, s2x = yh.var(ddof=1), xh.var(ddof=1)
        sxy = np.cov(yh, xh, ddof=1)[0, 1]
        V += N[h] ** 2 * (s2y + R ** 2 * s2x - 2 * R * sxy) / sel.sum()
    return R, V / X ** 2


def estimar_mapa(N, est, mapa, ref, clases, area_pixel_ha):
    """Exactitud global, usuario, productor y area por clase de un mapa evaluado con la muestra comun."""
    Ntot = float(sum(N.values()))
    acierto = (mapa == ref).astype(float)
    O, VO = _tot(N, None, est, acierto)
    filas = []
    for k in clases:
        U, VU = _cociente(N, est, ((mapa == k) & (ref == k)).astype(float), (mapa == k).astype(float))
        P, VP = _cociente(N, est, ((mapa == k) & (ref == k)).astype(float), (ref == k).astype(float))
        A, VA = _tot(N, None, est, (ref == k).astype(float))
        Am, _ = _tot(N, None, est, (mapa == k).astype(float))
        filas.append({"clase": k,
                      "usuario": U, "IC95_usuario": Z * np.sqrt(VU) if np.isfinite(VU) else np.nan,
                      "productor": P, "IC95_productor": Z * np.sqrt(VP) if np.isfinite(VP) else np.nan,
                      "area_estimada_ha": A * area_pixel_ha, "IC95_area_ha": Z * np.sqrt(VA) * area_pixel_ha,
                      "area_mapa_en_la_muestra_ha": Am * area_pixel_ha})
    return O / Ntot, Z * np.sqrt(VO) / Ntot, pd.DataFrame(filas)


def diferencia(N, est, y1, y2, x1=None, x2=None):
    """Diferencia PAREADA entre dos mapas sobre la misma muestra.
    Sin x: diferencia de proporciones (exactitud global). Con x: diferencia de cocientes,
    linealizada (z = (y - R x) / X de cada mapa), que es lo que corresponde a usuario o productor."""
    Ntot = float(sum(N.values()))
    if x1 is None:
        D, V = _tot(N, None, est, y1 - y2)
        return D / Ntot, Z * np.sqrt(V) / Ntot
    R1, _ = _cociente(N, est, y1, x1)
    R2, _ = _cociente(N, est, y2, x2)
    X1, _ = _tot(N, None, est, x1)
    X2, _ = _tot(N, None, est, x2)
    z = (y1 - R1 * x1) / X1 - (y2 - R2 * x2) / X2
    _, V = _tot(N, None, est, z)
    return R1 - R2, Z * np.sqrt(V)


# ------------------------------------------------------------------ disenar
def disenar(a, log):
    import geopandas as gpd
    import rasterio
    from configuracion_comun import ruta_tp
    nombres, arrs = [], []
    T = crs = None
    for m in a.mapa:
        nom, ruta = [x.strip() for x in m.split("|")]
        with rasterio.open(ruta) as s:
            arr = s.read(1)
            nd = s.nodata
            T, crs = s.transform, s.crs
        arr = np.where(np.isfinite(arr), arr, 0)
        if nd is not None:
            arr = np.where(arr == nd, 0, arr)
        nombres.append(nom)
        arrs.append(arr.astype("int64"))
    valido = np.all([(x > 0) for x in arrs], axis=0)
    log("Dominio comun (pixeles con dato en TODAS las variantes): %d pixeles, %.1f ha"
        % (valido.sum(), valido.sum() * T.a * abs(T.e) / 1e4))
    si = np.sum([(x == a.clase_interes) for x in arrs], axis=0)
    estrato = np.full(si.shape, "", dtype=object)
    estrato[valido & (si == len(arrs))] = "todas"
    estrato[valido & (si == 0)] = "ninguna"
    estrato[valido & (si > 0) & (si < len(arrs))] = "desacuerdo"
    rep = {k: int(v) for k, v in (x.split("=") for x in a.reparto.split(","))}
    if sum(rep.values()) != a.n:
        log("AVISO: el reparto suma %d y --n es %d: manda el reparto." % (sum(rep.values()), a.n))
    rng = np.random.default_rng(a.semilla)
    filas, dis = [], []
    for h in ("todas", "ninguna", "desacuerdo"):
        f, c = np.nonzero(estrato == h)
        dis.append({"estrato": h, "pixeles": int(f.size), "superficie_ha": round(f.size * T.a * abs(T.e) / 1e4, 1),
                    "W_h": round(f.size / valido.sum(), 5), "n_h": min(rep.get(h, 0), f.size)})
        if f.size == 0:
            continue
        for k in rng.choice(f.size, size=min(rep.get(h, 0), f.size), replace=False):
            x, y = T * (c[k] + 0.5, f[k] + 0.5)
            fila = {"x": x, "y": y, "estrato": h}
            for nom, arr in zip(nombres, arrs):
                fila[nom] = int(arr[f[k], c[k]])
            filas.append(fila)
    dis = pd.DataFrame(dis)
    log(dis.to_string(index=False))
    log("Suma de n_h = %d" % dis.n_h.sum())
    pts = pd.DataFrame(filas).sample(frac=1.0, random_state=a.semilla).reset_index(drop=True)
    pts.insert(0, "id", np.arange(1, len(pts) + 1))
    carpeta = ruta_tp("Tp4", "04_Tablas_de_trabajo")
    os.makedirs(carpeta, exist_ok=True)
    gp = os.path.join(carpeta, "%s_puntos_a_etiquetar.gpkg" % a.nombre)
    if os.path.exists(gp) and not a.sobrescribir:
        sys.exit("YA EXISTE %s: no se reescribe (use --sobrescribir despues de copiarlo)." % gp)
    vacio = pd.Series([None] * len(pts), dtype="object")
    gpd.GeoDataFrame({"id": pts.id, "clase_ref": vacio, "confianza": vacio, "imagen_usada": vacio,
                      "observacion": vacio}, geometry=gpd.points_from_xy(pts.x, pts.y), crs=crs
                     ).to_file(gp, layer="puntos", driver="GPKG")
    pts.drop(columns=["x", "y"]).to_csv(os.path.join(carpeta, "%s_llave_NO_ABRIR.csv" % a.nombre),
                                        index=False, encoding="utf-8-sig")
    tab = ruta_tp("Tp4", "05_Resultados", "04_Tablas", "%s_diseno_muestral.csv" % a.nombre)
    os.makedirs(os.path.dirname(tab), exist_ok=True)
    dis.assign(pixel_ha=T.a * abs(T.e) / 1e4).to_csv(tab, index=False, encoding="utf-8-sig")
    log("Puntos a etiquetar (SIN las clases de las variantes): %s (%d puntos)" % (gp, len(pts)))
    log("Llave con el estrato y la clase de cada variante: %s_llave_NO_ABRIR.csv" % a.nombre)


# ------------------------------------------------------------------ agregar un mapa a la llave
def agregar_mapa(a, log):
    import geopandas as gpd
    import rasterio
    from configuracion_comun import ruta_tp
    carpeta = ruta_tp("Tp4", "04_Tablas_de_trabajo")
    pts = gpd.read_file(os.path.join(carpeta, "%s_puntos_a_etiquetar.gpkg" % a.nombre), layer="puntos")
    llave_r = os.path.join(carpeta, "%s_llave_NO_ABRIR.csv" % a.nombre)
    llave = pd.read_csv(llave_r, encoding="utf-8-sig")
    with rasterio.open(a.agregar_mapa) as s:
        v = [int(x[0]) for x in s.sample(zip(pts.geometry.x, pts.geometry.y))]
    llave = llave.merge(pd.DataFrame({"id": pts.id, a.columna: v}), on="id", how="left") \
        if a.columna not in llave.columns else llave.assign(**{a.columna: llave.id.map(dict(zip(pts.id, v)))})
    # copia: la llave original del paso 10 no se toca
    salida = os.path.join(carpeta, "%s_llave_varios_mapas_NO_ABRIR.csv" % a.nombre)
    if os.path.exists(salida):
        prev = pd.read_csv(salida, encoding="utf-8-sig")
        prev[a.columna] = prev.id.map(dict(zip(pts.id, v)))
        llave = prev
    llave.to_csv(salida, index=False, encoding="utf-8-sig")
    log("Agregada la columna %s (clase del mapa %s en cada punto) a %s" % (a.columna, a.agregar_mapa, salida))


# ------------------------------------------------------------------ estimar
def estimar(a, log):
    import geopandas as gpd
    from configuracion_comun import ruta_tp
    carpeta = ruta_tp("Tp4", "04_Tablas_de_trabajo")
    pts = gpd.read_file(os.path.join(carpeta, "%s_puntos_a_etiquetar.gpkg" % a.nombre), layer="puntos")
    varios = os.path.join(carpeta, "%s_llave_varios_mapas_NO_ABRIR.csv" % a.nombre)
    llave = pd.read_csv(varios if os.path.exists(varios) else
                        os.path.join(carpeta, "%s_llave_NO_ABRIR.csv" % a.nombre), encoding="utf-8-sig")
    dis = pd.read_csv(ruta_tp("Tp4", "05_Resultados", "04_Tablas", "%s_diseno_muestral.csv" % a.nombre),
                      encoding="utf-8-sig")
    t = pts.drop(columns="geometry").merge(llave, on="id")
    t = t[t.clase_ref.notna() & (t.clase_ref.astype(str).str.strip() != "")].copy()
    t["clase_ref"] = t.clase_ref.astype(float).astype(int)
    # estrato: columna "estrato" (diseno comun) o "clase_mapa" (diseno de Tp4_02)
    col_est = "estrato" if "estrato" in t.columns else "clase_mapa"
    clave_dis = "estrato" if "estrato" in dis.columns else "clase_mapa"
    def _clave(v):
        # "1", 1 y 1.0 son el mismo estrato
        try:
            return str(int(float(v)))
        except (TypeError, ValueError):
            return str(v)
    N = {_clave(e): float(p) for e, p in zip(dis[clave_dis], dis.pixeles)}
    est = np.array([_clave(v) for v in t[col_est]])
    px_ha = float(dis.pixel_ha.iloc[0]) if "pixel_ha" in dis.columns else float(dis.superficie_ha.sum() / dis.pixeles.sum())
    # columnas de la llave que son mapas (clase de cada mapa en cada punto)
    mapas = [c for c in t.columns if c not in ("id", "clase_ref", "confianza", "imagen_usada", "observacion",
                                               "estrato", "fid")]
    t[mapas] = t[mapas].fillna(0).astype(int)
    clases = sorted(set(t.clase_ref.tolist()) | set(int(v) for c in mapas for v in t[c].unique()))
    clases = [k for k in clases if k > 0]
    ref = t.clase_ref.values
    res, glob = [], []
    for m in mapas:
        O, ICO, tab = estimar_mapa(N, est, t[m].values.astype(int), ref, clases, px_ha)
        glob.append({"mapa": m, "exactitud_global": round(O, 4), "IC95_global": round(ICO, 4)})
        res.append(tab.assign(mapa=m))
        log.titulo("Mapa: %s  (n = %d puntos de la muestra comun)" % (m, len(t)))
        log("Exactitud global: %.3f +/- %.3f" % (O, ICO))
        log(tab.round(3).to_string(index=False))
    res = pd.concat(res)
    log.titulo("Diferencias PAREADAS entre mapas (misma muestra)")
    dif = []
    k = a.clase
    for m1, m2 in itertools.combinations(mapas, 2):
        y1 = (t[m1].values == ref).astype(float)
        y2 = (t[m2].values == ref).astype(float)
        d, ic = diferencia(N, est, y1, y2)
        fila = {"mapa_1": m1, "mapa_2": m2, "dif_global": round(d, 4), "IC95_dif_global": round(ic, 4),
                "global": "demostrada" if abs(d) > ic else "no demostrada"}
        if k:
            yk1 = ((t[m1].values == k) & (ref == k)).astype(float)
            yk2 = ((t[m2].values == k) & (ref == k)).astype(float)
            dP, icP = diferencia(N, est, yk1, yk2, (ref == k).astype(float), (ref == k).astype(float))
            dU, icU = diferencia(N, est, yk1, yk2, (t[m1].values == k).astype(float), (t[m2].values == k).astype(float))
            fila.update({"dif_productor_%d" % k: round(dP, 4), "IC95_dif_productor": round(icP, 4),
                         "dif_usuario_%d" % k: round(dU, 4), "IC95_dif_usuario": round(icU, 4)})
        dif.append(fila)
        log("%s - %s: global %+.3f +/- %.3f (%s)%s" % (
            m1, m2, d, ic, fila["global"],
            ("; productor de %d %+.3f +/- %.3f; usuario de %d %+.3f +/- %.3f" % (k, dP, icP, k, dU, icU)) if k else ""))
    dif = pd.DataFrame(dif)
    tabla = ruta_tp("Tp4", "05_Resultados", "04_Tablas", "%s_muestra_comun_exactitud.csv" % a.nombre)
    res.merge(pd.DataFrame(glob), on="mapa").to_csv(tabla, index=False, encoding="utf-8-sig")
    dif.to_csv(tabla.replace("_exactitud.csv", "_diferencias.csv"), index=False, encoding="utf-8-sig")
    log("")
    log("Lectura: con la MISMA muestra, la diferencia entre dos mapas se estima pareada; si su IC del 95 %")
    log("incluye el cero, la diferencia no esta demostrada con esta muestra.")
    log("Tablas: %s y _diferencias.csv" % tabla)


def main():
    from configuracion_comun import ruta_tp
    from funciones_comunes import Bitacora
    ap = argparse.ArgumentParser(description="Una sola muestra estratificada para varios mapas (Stehman, 2014)")
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--disenar", action="store_true")
    ap.add_argument("--estimar", action="store_true")
    ap.add_argument("--agregar_mapa", default="")
    ap.add_argument("--columna", default="otro_mapa")
    ap.add_argument("--mapa", action="append", default=[], help='"nombre|ruta.tif" (una por variante)')
    ap.add_argument("--clase_interes", type=int, default=1)
    ap.add_argument("--clase", type=int, default=0, help="clase para las diferencias de usuario y productor")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--reparto", default="todas=50,ninguna=50,desacuerdo=100")
    ap.add_argument("--semilla", type=int, default=SEMILLA)
    ap.add_argument("--sobrescribir", action="store_true")
    ap.add_argument("--tp", default="Tp4")
    a = ap.parse_args()
    log = Bitacora(ruta_tp("Tp4", "05_Resultados", "06_Control_calidad"), "Tp4_06_%s" % a.nombre)
    if a.disenar:
        disenar(a, log)
        log.cerrar("etiquetar los puntos en QGIS (paso 7) y correr --estimar")
    elif a.agregar_mapa:
        agregar_mapa(a, log)
        log.cerrar("python Tp4_06_muestra_comun.py --estimar --nombre %s" % a.nombre)
    elif a.estimar:
        estimar(a, log)
        log.cerrar()
    else:
        sys.exit("Elija --disenar, --agregar_mapa o --estimar.")


if __name__ == "__main__":
    main()
