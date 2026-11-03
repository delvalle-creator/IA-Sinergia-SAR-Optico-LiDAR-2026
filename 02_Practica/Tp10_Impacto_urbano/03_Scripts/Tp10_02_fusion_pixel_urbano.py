# -*- coding: utf-8 -*-
"""
Tp10_02_fusion_pixel_urbano.py   [SE CORRE]   Tp10, pasos 4 a 6 de la guía - FUSIÓN DE RASGOS
====================================================================================
Diapositiva 33, paso 2: "Superficie impermeable con índices ópticos (NDBI) y textura."
Diapositiva 33, paso 3: "Fusión de píxel: VV, VH, HH (S), HV (L) y NDBI -> clasificador."
(presentación 01, diapositiva 33). Como el clasificador recibe además índices (NDBI, NDVI, MNDWI)
y una textura, que son variables derivadas, el curso lo llama FUSIÓN DE RASGOS (regla 5 de
REGLAS_DEL_PROYECTO.md y GLOSARIO.md).

QUÉ HACE
  1. COMPUESTOS de temporada. Sentinel-1: media en LINEAL de hasta 5 pasadas de la misma órbita
     en +/- --dias de --fecha. Sentinel-2: mediana de hasta 5 escenas (las de menos nube), píxel
     a píxel, usando sólo lo que la SCL marca sin nube.
  2. ENTRENAMIENTO EN PROPORCIÓN AL PAISAJE: píxeles ESTABLES de MapBiomas (la misma clase en los
     tres últimos años), sorteados en proporción a la superficie de cada clase, con un mínimo por
     clase (Waldner et al., 2017, https://doi.org/10.1080/2150704X.2017.1362124). Contrapartida:
     la clase chica (urbano) recibe probabilidades más bajas y sus bordes quedan con menos de 0,6,
     lo que baja la comisión pero sube la omisión.
  3. UNA VARIANTE POR CONJUNTO DE SENSORES, con el MISMO clasificador y el MISMO entrenamiento:
     óptico solo, banda C sola, SAR multibanda (C + L), multisensor (C + L + óptico) y
     multisensor con S. Así la comparación del Tp4 mide el aporte de los DATOS.
  La importancia de cada capa (Gini) favorece a las variables continuas y correlacionadas: no
  reparte el aporte entre sensores. El aporte de cada sensor se mide con las variantes del Tp4.
  (El historial de versiones está en NOTAS_TECNICAS.md.)

CAPAS (nivel de RASGO: bandas, índices y textura)
  C_VV_dB, C_VH_dB      compuesto Sentinel-1 RTC (gamma0), media lineal pasada a dB
  C_CV_VV               textura: coeficiente de variación local del VV compuesto (ventana 5)
  L_HH_dB, L_HV_dB      NISAR 2026 (de Tp10_01)
  S_HH_dB               NovaSAR-1 2023 (de Tp10_01; solo donde hay escena)
  B02, B03, B04, B08, B11  compuesto Sentinel-2 L2A (mediana de hasta 5 escenas)
  NDBI = (B11-B08)/(B11+B08), NDVI = (B08-B04)/(B08+B04), MNDWI = (B03-B11)/(B03+B11)

CLASES (de la leyenda oficial de MapBiomas Argentina, Coleccion 3)
  1 urbano (24)   2 vegetación leñosa (bosques, silvicultura, cultivos perennes)
  3 herbáceas y cultivos   4 agua   5 suelo desnudo y otras no vegetadas
  Los puntos de entrenamiento quedan en 04_Tablas_de_trabajo/entrenamiento_mapbiomas_<SITIO>.gpkg
  para revisarlos en QGIS (paso 4). Un grupo puede usar su propia capa con los mismos códigos:
  --entrenamiento <ruta.gpkg> (capa "entrenamiento", campo "codigo"); en ese caso conviene que
  la cantidad de polígonos de cada clase siga la proporción del paisaje.

VARIANTES PARA EL Tp4 (1 = urbano, 2 = no urbano)
  <SITIO>_variante_optico.tif, _variante_C.tif, _variante_SAR_multibanda.tif,
  _variante_multisensor.tif (todo el sitio) y _variante_multisensor_con_S.tif (huella de NovaSAR)

USO
    python Tp10_02_fusion_pixel_urbano.py --sitio B_CONCORDIA --pixel 20
    (--equilibrar repite el error de la versión anterior, para mostrarlo en clase)
    El Sentinel-2 del 2026-09-04 NO entra al compuesto (--excluir): es la imagen de referencia con la
    que se etiquetan los puntos de validación del Tp4, y la referencia tiene que ser independiente.
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

from configuracion_comun import ruta_tp                               # noqa: E402
from funciones_comunes import (leer_tif, grilla_de_tif, lin_a_db, guardar_tif, Bitacora, fuente_mpc,  # noqa: E402
                               s1_rtc_compuesto, s2_compuesto, entrenamiento_mapbiomas, CLASES_URBANO_MB)
from funciones_cambio import indice_normalizado, leer_entrenamiento, fusion_pixel_o_rasgo, figura_mapa  # noqa: E402

CLASES = {k: v[0] for k, v in CLASES_URBANO_MB.items()}


def cv_local(x, ventana=5):
    from scipy import ndimage

    ok = np.isfinite(x)
    v = np.where(ok, x, 0.0).astype("float64")
    n = ndimage.uniform_filter(ok.astype("float64"), ventana)
    m = ndimage.uniform_filter(v, ventana) / np.where(n > 0, n, np.nan)
    m2 = ndimage.uniform_filter(v * v, ventana) / np.where(n > 0, n, np.nan)
    return np.where(ok & (n > 0.6), np.sqrt(np.maximum(m2 - m * m, 0)) / m, np.nan).astype("float32")


def main():
    import geopandas as gpd

    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", default="B_CONCORDIA", choices=["B_CONCORDIA", "E_PARANA_DIAMANTE"])
    ap.add_argument("--pixel", type=int, default=20)
    ap.add_argument("--fecha", default="2026-09-16")
    ap.add_argument("--dias", type=int, default=20, help="ventana de los compuestos: +/- días de --fecha")
    ap.add_argument("--anio_mb", type=int, default=2025, help="año de MapBiomas para el entrenamiento (el último)")
    ap.add_argument("--n_entrenamiento", type=int, default=20000)
    ap.add_argument("--entrenamiento", default=None, help="capa propia (gpkg) con los códigos 1 a 5")
    ap.add_argument("--equilibrar", action="store_true", help="clases equilibradas (el error de la versión anterior)")
    ap.add_argument("--rehacer_compuestos", action="store_true", help="volver a calcular los compuestos aunque ya existan")
    ap.add_argument("--excluir", nargs="*", default=["2026-09-04"],
                    help="fechas de Sentinel-2 que no entran al compuesto (la imagen de referencia del Tp4)")
    a = ap.parse_args()
    S = a.sitio
    log = Bitacora(ruta_tp("Tp10", "05_Resultados", "06_Control_calidad"), "Tp10_02_%s" % S)
    ruta1 = ruta_tp("Tp10", "02_Subsets_SNAP_QGIS", "%s_urbano_por_banda_%dm.tif" % (S, a.pixel))
    if not os.path.exists(ruta1):
        sys.exit("Falta %s: correr antes Tp10_01_doble_rebote_sinergia.py" % ruta1)
    p1, _, t1 = leer_tif(ruta1)
    g = grilla_de_tif(ruta1)
    f0 = np.datetime64(a.fecha)
    desde, hasta = str(f0 - a.dias), str(f0 + a.dias)
    capas, fuentes = {}, [t1.get("FUENTE", "")]

    comp = ruta_tp("Tp10", "02_Subsets_SNAP_QGIS", "%s_compuestos_%s_%dm.tif" % (S, a.fecha, a.pixel))
    NOMBRES = ("C_VV_dB", "C_VH_dB", "C_CV_VV", "NDBI", "NDVI", "MNDWI", "B04", "B03", "B02", "B08", "B11")
    previo = leer_tif(comp) if os.path.exists(comp) and not a.rehacer_compuestos else None
    if previo is not None and all(k in previo[0] for k in NOMBRES):
        log.titulo("Compuestos de temporada: se reutilizan los ya calculados")
        log("  %s (para volver a calcularlos: --rehacer_compuestos)" % comp)
        for k in NOMBRES:
            capas[k] = previo[0][k]
        fuentes.append(previo[2].get("FUENTE", ""))
        for k, n in (("L_HH", "L_HH_dB"), ("L_HV", "L_HV_dB"), ("S_HH", "S_HH_dB")):
            if k in p1:
                capas[n] = lin_a_db(p1[k])
        fuente = " | ".join(x for x in fuentes if x)
    else:
        log.titulo("Compuesto de radar: Sentinel-1 RTC del %s al %s" % (desde, hasta))
        s1, n1, fechas1, orb = s1_rtc_compuesto(S, desde, hasta, g)
        if s1 is None:
            sys.exit("Sin Sentinel-1 RTC en la ventana.")
        capas["C_VV_dB"], capas["C_VH_dB"] = lin_a_db(s1["vv"]), lin_a_db(s1["vh"])
        capas["C_CV_VV"] = cv_local(s1["vv"])
        log("  órbita relativa %s; %d pasadas: %s; pasadas por píxel: mediana %d"
            % (orb, len(fechas1), ", ".join(fechas1), int(np.nanmedian(n1))))
        f_s1 = fuente_mpc("ESA - Copernicus", "Sentinel-1 IW GRD RTC, media lineal de %d pasadas de la órbita %s"
                          % (len(fechas1), orb), "%s a %s" % (fechas1[0], fechas1[-1]))
        for k, n in (("L_HH", "L_HH_dB"), ("L_HV", "L_HV_dB"), ("S_HH", "S_HH_dB")):
            if k in p1:
                capas[n] = lin_a_db(p1[k])

        log.titulo("Compuesto óptico: Sentinel-2 L2A del %s al %s (mediana, solo píxeles sin nube)" % (desde, hasta))
        s2, n2, usadas = s2_compuesto(S, desde, hasta, g, excluir=a.excluir)
        if s2 is None:
            sys.exit("Sin Sentinel-2 en la ventana.")
        for b, x in s2.items():
            capas[b] = x
        capas["NDBI"] = indice_normalizado(s2["B11"], s2["B08"]).astype("float32")
        capas["NDVI"] = indice_normalizado(s2["B08"], s2["B04"]).astype("float32")
        capas["MNDWI"] = indice_normalizado(s2["B03"], s2["B11"]).astype("float32")
        log("  %d escenas: %s" % (len(usadas), "; ".join("%s (nube %.1f %%)" % u for u in usadas)))
        log("  observaciones sin nube por píxel: mediana %d; sin ninguna: %.1f %% del sitio"
            % (int(np.nanmedian(n2)), 100 * np.mean(n2 == 0)))
        f_s2 = fuente_mpc("ESA - Copernicus", "Sentinel-2 MSI L2A, mediana de %d escenas (%s)" % (len(usadas), ", ".join(u[0] for u in usadas)),
                          "%s a %s" % (usadas[0][0], usadas[-1][0]))
        fuente_comp = f_s1 + " | " + f_s2
        guardar_tif(comp, {k: capas[k] for k in NOMBRES} | {"n_pasadas_S1": n1, "n_escenas_S2": n2}, g, fuente_comp,
                    "Compuestos de temporada +/- %d días de %s: Sentinel-1 media lineal, Sentinel-2 mediana" % (a.dias, a.fecha))
        log("  compuestos guardados en %s" % comp)
        fuentes.append(fuente_comp)
        fuente = " | ".join(x for x in fuentes if x)

    log.titulo("Entrenamiento (paso 4)")
    if a.entrenamiento:
        y = leer_entrenamiento(a.entrenamiento, g)
        log("  capa propia: %s" % a.entrenamiento)
    else:
        rmb = ruta_tp("Tp10", "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", "%s_MapBiomas_cobertura_1985_2025.tif" % S)
        y, filas = entrenamiento_mapbiomas(rmb, a.anio_mb, g, n_total=a.n_entrenamiento)
        te = pd.DataFrame(filas)
        log("  MapBiomas %d, píxeles estables 2023-2025, sorteo proporcional (mínimo 600 por clase):" % a.anio_mb)
        log(te.to_string(index=False))
        te.to_csv(ruta_tp("Tp10", "05_Resultados", "04_Tablas", "%s_entrenamiento_mapbiomas.csv" % S), index=False, encoding="utf-8-sig")
        fil, col = np.nonzero(y)
        T = g["transform"]
        xs, ys = T.c + (col + 0.5) * T.a, T.f + (fil + 0.5) * T.e
        cod = y[fil, col]
        pts = gpd.GeoDataFrame({"codigo": cod.astype("int32"), "clase": [CLASES[int(c)] for c in cod],
                                "revisado": [""] * len(cod)},
                               geometry=gpd.points_from_xy(xs, ys), crs=g["crs"])
        ruta_pts = ruta_tp("Tp10", "04_Tablas_de_trabajo", "entrenamiento_mapbiomas_%s.gpkg" % S)
        pts.to_file(ruta_pts, layer="entrenamiento", driver="GPKG", engine="pyogrio")
        log("  puntos para revisar en QGIS: %s" % ruta_pts)
        fuente += " | Proyecto MapBiomas Argentina, Coleccion 3, licencia CC BY 4.0, https://argentina.mapbiomas.org"

    log.titulo("FUSIÓN DE RASGOS - Random Forest, %s (pasos 5 y 6)" % ("CLASES EQUILIBRADAS" if a.equilibrar else "entrenamiento proporcional"))
    opt = ["B02", "B03", "B04", "B08", "B11", "NDBI", "NDVI", "MNDWI"]
    C = ["C_VV_dB", "C_VH_dB", "C_CV_VV"]
    L = [k for k in ("L_HH_dB", "L_HV_dB") if k in capas]
    variantes = {"optico": opt, "C": C, "SAR_multibanda": C + L, "multisensor": C + L + opt}
    if "S_HH_dB" in capas:
        variantes["multisensor_con_S"] = C + L + ["S_HH_dB"] + opt
    R = lambda n: ruta_tp("Tp10", "05_Resultados", "02_Rasters", "%s_%s" % (S, n))  # noqa: E731
    filas, sup = [], []
    for nom, lista in variantes.items():
        mapa, prob, info = fusion_pixel_o_rasgo({k: capas[k] for k in lista}, y, equilibrar=a.equilibrar)
        ok = np.isfinite(mapa)
        ha = g["pixel"] ** 2 / 1e4
        log("  %-18s capas: %s" % (nom, ", ".join(lista)))
        log("     cubre el %.1f %% del sitio; urbano %.0f ha; exactitud fuera de bolsa (OPTIMISTA) %.3f"
            % (100 * ok.mean(), np.sum(mapa == 1) * ha, info["exactitud_fuera_de_bolsa_OPTIMISTA"]))
        for k, v in sorted(info["importancia"].items(), key=lambda kv: -kv[1]):
            filas.append({"variante": nom, "capa": k, "importancia": v})
        sup.append({"variante": nom, "cubre_%": round(100 * ok.mean(), 1),
                    **{CLASES[c]: round(float(np.sum(mapa == c) * ha), 1) for c in CLASES}})
        guardar_tif(R("variante_%s.tif" % nom), {"clase": np.where(ok, np.where(mapa == 1, 1, 2), np.nan).astype("float32")},
                    g, fuente, "Random Forest %s (%s): 1 urbano, 2 no urbano" % (nom, ", ".join(lista)))
        if nom in ("multisensor", "multisensor_con_S"):
            sal = "clases_sin_S.tif" if nom == "multisensor" else "clases_con_S.tif"
            guardar_tif(R(sal), {"clase": mapa, "probabilidad": prob}, g, fuente,
                        "Random Forest %s. " % nom + "; ".join("%d %s" % kv for kv in CLASES.items()))
            figura_mapa(mapa, ruta_tp("Tp10", "05_Resultados", "05_Graficos", "%s_%s" % (S, sal.replace(".tif", ".png"))),
                        "%s - fusión de rasgos (%s)" % (S, nom), fuente[:300], etiquetas=CLASES, cmap="tab10")
    pd.DataFrame(filas).to_csv(ruta_tp("Tp10", "05_Resultados", "04_Tablas", "%s_importancia_por_version.csv" % S),
                               index=False, encoding="utf-8-sig")
    ts = pd.DataFrame(sup)
    log("Superficie por clase (ha):")
    log(ts.to_string(index=False))
    ts.to_csv(ruta_tp("Tp10", "05_Resultados", "04_Tablas", "%s_superficie_por_variante.csv" % S), index=False, encoding="utf-8-sig")
    log.cerrar("python Tp10_03_expansion_urbana.py --sitio %s" % S)


if __name__ == "__main__":
    main()
