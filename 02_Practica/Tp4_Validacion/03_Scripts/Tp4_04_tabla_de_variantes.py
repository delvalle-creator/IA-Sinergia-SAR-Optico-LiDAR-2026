# -*- coding: utf-8 -*-
"""
Tp4_04_tabla_de_variantes.py   [SE CORRE]   Tp4, paso 9 de la guia (y cierre de Tp5 a Tp10)
===================================================================================
Arma la "tabla de resultados que entrega cada grupo" (presentacion 01,
diapositiva 23): una fila por variante y la misma clase de interes.

    Variante | Datos usados | Exactitud global | Omision | Comision | Area +/- IC

La pregunta de cada practico especifico es cuanto mejora la exactitud al sumar
bandas y sensores. Esta tabla la contesta con numeros y con su incertidumbre:
la diferencia entre dos variantes se estima directamente, con su propio
intervalo de confianza (muestras independientes: V(d) = V1 + V2); si ese
intervalo incluye el cero, la mejora NO esta demostrada con esa muestra.

La comparacion se hace en la CLASE DE INTERES (omision y comision, con sus IC
al 95 %), no solo con la exactitud global: cuando el quemado o el agua ocupan
el 1 al 10 % del sitio, la exactitud global la domina la clase "no" y puede
ser alta aunque la variante falle justo en lo que importa. La exactitud
global se informa igual, como contexto. El area estimada de cada variante
tambien se compara: si dos variantes dan areas con IC que no se superponen,
al menos una esta sesgada.

USO
    python Tp4_04_tabla_de_variantes.py --tp Tp5 --clase quemado ^
        --variante "Optico solo|Sentinel-2|A1_variante_optico" ^
        --variante "SAR solo (C)|Sentinel-1|A1_variante_C" ^
        --variante "SAR multibanda|C + L|A1_variante_CL" ^
        --variante "Multisensor|SAR (C + L) + optico|A1_variante_multisensor"
    Cada --variante es "nombre|datos usados|nombre usado en Tp4_02 y Tp4_03".

SALIDA
    <Tp>/05_Resultados/04_Tablas/tabla_de_variantes_<clase>.csv
"""
import argparse
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))

import pandas as pd                                                   # noqa: E402

from configuracion_comun import ruta_tp                               # noqa: E402
from funciones_comunes import Bitacora                                # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tp", required=True)
    ap.add_argument("--clase", required=True, help="nombre o codigo de la clase de interes")
    ap.add_argument("--variante", action="append", required=True)
    a = ap.parse_args()
    log = Bitacora(ruta_tp(a.tp, "05_Resultados", "06_Control_calidad"), "Tp4_04_variantes_%s" % a.clase)
    filas = []
    for v in a.variante:
        nombre, datos, clave = [x.strip() for x in v.split("|")]
        ruta = ruta_tp("Tp4", "05_Resultados", "04_Tablas", "%s_exactitud_y_area.csv" % clave)
        if not os.path.exists(ruta):
            log("Falta %s (correr Tp4_02 y Tp4_03 con --nombre %s)." % (ruta, clave))
            continue
        t = pd.read_csv(ruta, encoding="utf-8-sig")
        # la clase se busca por nombre (si Tp4_03 se corrio con --nombres_clase) o por codigo
        f = t[(t.clase.astype(str) == str(a.clase)) |
              (t.get("codigo", pd.Series(dtype=str)).astype(str) == str(a.clase))]
        if f.empty:
            log("La clase %s no esta en %s." % (a.clase, ruta))
            continue
        f = f.iloc[0]
        tot = float(t.area_mapa_ha.sum())          # superficie con dato en ESE mapa (todas las clases)
        filas.append({"variante": nombre, "datos_usados": datos,
                      "exactitud_global": "%.3f +/- %.3f" % (f.exactitud_global, f.IC95_global),
                      "omision": "%.3f +/- %.3f" % (f.omision, f.IC95_productor),
                      "comision": "%.3f +/- %.3f" % (f.comision, f.IC95_usuario),
                      "area_estimada_ha": "%.0f +/- %.0f" % (f.area_estimada_ha, f.IC95_area_ha),
                      "area_segun_mapa_ha": "%.0f" % f.area_mapa_ha,
                      "superficie_mapeada_ha": "%.0f" % tot,
                      "porcentaje_estimado": "%.1f +/- %.1f %%" % (100 * f.area_estimada_ha / tot, 100 * f.IC95_area_ha / tot),
                      "_tot": tot,
                      "_og": f.exactitud_global, "_ic": f.IC95_global,
                      "_om": f.omision, "_icom": f.IC95_productor,
                      "_co": f.comision, "_icco": f.IC95_usuario,
                      "_ar": f.area_estimada_ha, "_icar": f.IC95_area_ha})
    if not filas:
        log("No hay variantes para comparar.")
        log.cerrar()
        return
    t = pd.DataFrame(filas)
    ocultas = [c for c in t.columns if c.startswith("_")]
    log(t.drop(columns=ocultas).to_string(index=False))
    log("")
    # (columna, IC, mas_es_mejor, nombre, columna de la tabla)
    if len(t) == 1:
        # Con una sola variante no hay "mejor variante": se dice asi, para no confundir.
        log("Una sola variante: no hay comparacion. La tabla queda escrita para sumarle las otras variantes.")
    for col, ic, mas, que, salida in (("_om", "_icom", False, "OMISION de la clase %s" % a.clase, "omision_frente_a_la_mejor"),
                                      ("_co", "_icco", False, "COMISION de la clase %s" % a.clase, "comision_frente_a_la_mejor"),
                                      ("_og", "_ic", True, "exactitud global (contexto)", "exactitud_global_frente_a_la_mejor")):
        mejor = t.loc[t[col].idxmax() if mas else t[col].idxmin()]
        t[salida] = ""
        if len(t) == 1:
            log("%s: %s (%.3f +/- %.3f)" % (que, mejor.variante, mejor[col], mejor[ic]))
            t.at[t.index[0], salida] = "una sola variante: no hay comparacion"
            continue
        log("%s: mejor variante %s (%.3f +/- %.3f)" % (que, mejor.variante, mejor[col], mejor[ic]))
        for k, f in t.iterrows():
            if f.variante == mejor.variante:
                t.at[k, salida] = "es la mejor"
                continue
            # Un IC nulo o indefinido no es certeza, es falta de puntos
            # de referencia de la clase (0 o todos en una celda de la matriz): no se puede comparar.
            if any(pd.isna(v) for v in (f[col], f[ic], mejor[col], mejor[ic])) or f[ic] == 0 or mejor[ic] == 0:
                t.at[k, salida] = "no comparable con %s (IC nulo o indefinido)" % mejor.variante
                log("   frente a %s (%.3f +/- %.3f): NO SE PUEDE DECIDIR: un IC nulo o indefinido sale de muy pocos puntos"
                    " de referencia de la clase, no de una medicion exacta" % (f.variante, f[col], f[ic]))
                continue
            # Diferencia directa con su IC. Cada variante tiene su propia muestra
            # (independientes): V(d) = V1 + V2, con V = (IC / 1,96)^2. Si las dos variantes se
            # evaluaran con la MISMA muestra habria que sumar la covarianza: no es el caso del curso.
            dif = f[col] - mejor[col]
            ic_dif = 1.96 * ((f[ic] / 1.96) ** 2 + (mejor[ic] / 1.96) ** 2) ** 0.5
            solapan = abs(dif) <= (f[ic] + mejor[ic])
            signif = abs(dif) > ic_dif
            t.at[k, salida] = ("diferencia %+.3f +/- %.3f con %s: %s" % (dif, ic_dif, mejor.variante,
                               "significativa al 95 %" if signif else "no demostrada con esta muestra"))
            log("   frente a %s (%.3f +/- %.3f): diferencia %+.3f +/- %.3f -> %s%s" % (
                f.variante, f[col], f[ic], dif, ic_dif,
                "SIGNIFICATIVA al 95 %" if signif else "no demostrada con esta muestra",
                " (los IC se superponen, pero la diferencia es significativa)" if (signif and solapan) else ""))
    log("")
    log("Area estimada (ha, IC 95 %):")
    for _, f in t.iterrows():
        log("   %-28s %8.0f +/- %.0f" % (f.variante, f._ar, f._icar))
    # Cada variante cubre SOLO los pixeles con dato en todas sus capas.
    # Si las superficies mapeadas difieren, las hectareas no se comparan: se comparan los porcentajes.
    if (t._tot.max() - t._tot.min()) > 0.01 * t._tot.max():
        log("   OJO: las variantes no cubren la misma superficie (pixeles con dato en todas sus capas):")
        for _, f in t.iterrows():
            log("      %-28s %8.0f ha mapeadas; %s %5.1f +/- %.1f %%"
                % (f.variante, f._tot, a.clase, 100 * f._ar / f._tot, 100 * f._icar / f._tot))
        log("   Las hectareas no son comparables entre si; se comparan los porcentajes.")
    for x, y in [(t.iloc[i], t.iloc[k]) for i in range(len(t)) for k in range(i + 1, len(t))]:
        px, py = x._ar / x._tot, y._ar / y._tot
        if x._icar == 0 or y._icar == 0:
            log("   %s y %s: una de las areas tiene IC nulo (muy pocos puntos de referencia de la clase): no se comparan."
                % (x.variante, y.variante))
        elif abs(px - py) > (x._icar / x._tot + y._icar / y._tot):
            log("   AVISO: %s y %s dan proporciones de area incompatibles (los IC no se superponen): al menos una"
                " esta sesgada." % (x.variante, y.variante))
    log("")
    log("Lectura: una variante MEJORA a otra en la clase %s si la DIFERENCIA de omision o de comision, con su"
        % a.clase)
    log("propio IC del 95 %, no incluye el cero. Que los IC de cada variante no se superpongan es una regla visual")
    log("mas exigente (si no se superponen, la diferencia es significativa; si se superponen, puede serlo igual).")
    log("Las variantes se comparan en la misma superficie: si cubren superficies distintas, la comparacion vale")
    log("solo para la interseccion. Una exactitud global mas alta, sola, no demuestra nada sobre la clase.")
    out = ruta_tp(a.tp, "05_Resultados", "04_Tablas", "tabla_de_variantes_%s.csv" % a.clase)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    t.drop(columns=ocultas).to_csv(out, index=False, encoding="utf-8-sig")
    log("Tabla:", out)
    log.cerrar()


if __name__ == "__main__":
    main()
