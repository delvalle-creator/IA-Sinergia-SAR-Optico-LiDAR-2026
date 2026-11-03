# -*- coding: utf-8 -*-
"""
Conversor NISAR GCOV por linea de comandos (para usar fuera de QGIS,
sobre todo para preparar los productos que se abren en SNAP).

Ejemplos:
    python nisar_gcov_cli.py --info  ARCHIVO.h5
    python nisar_gcov_cli.py ARCHIVO.h5 -o C:\\salida --db
    python nisar_gcov_cli.py ARCHIVO.h5 -o C:\\salida --db --dimap
    python nisar_gcov_cli.py ARCHIVO.h5 -o C:\\salida --bandas HHHH HVHV
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nisar_gcov_core as core  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="NISAR GCOV -> GeoTIFF / BEAM-DIMAP")
    ap.add_argument("archivo", help="producto GCOV (.h5)")
    ap.add_argument("-o", "--salida", default=None, help="carpeta de salida")
    ap.add_argument("--bandas", nargs="*", default=None,
                    help="capas a exportar (por defecto: todas las polarizaciones)")
    ap.add_argument("--grilla", default=None,
                    help="nombre de la grilla, p. ej. frequencyA (por defecto la primera)")
    ap.add_argument("--db", action="store_true",
                    help="convertir gamma0 lineal a decibeles")
    ap.add_argument("--dimap", action="store_true",
                    help="escribir BEAM-DIMAP (.dim) en lugar de GeoTIFF")
    ap.add_argument("--submuestreo", type=int, default=1, metavar="N",
                    help="reducir N veces promediando bloques NxN (multilooking); 1 = resolucion completa")
    ap.add_argument("--decimar", action="store_true",
                    help="al submuestrear, tomar una celda de cada N en vez de promediar")
    ap.add_argument("--recorte", nargs=4, type=float, default=None,
                    metavar=("MINLON", "MINLAT", "MAXLON", "MAXLAT"),
                    help="recorte en longitud/latitud (WGS84)")
    ap.add_argument("--recorte-xy", nargs=4, type=float, default=None,
                    metavar=("MINX", "MINY", "MAXX", "MAXY"),
                    help="recorte en coordenadas del producto")
    ap.add_argument("--c3", action="store_true",
                    help="escribir la matriz C3 para SNAP (solo productos cuadripolares)")
    ap.add_argument("--info", action="store_true",
                    help="solo mostrar la estructura del archivo")
    a = ap.parse_args()

    if a.info:
        print(core.describe(a.archivo))
        return 0

    grids = core.open_grids(a.archivo)
    grid = grids[0]
    if a.grilla:
        for g in grids:
            if a.grilla.lower() in g.path.lower():
                grid = g
                break

    if a.recorte:
        core.recortar_lonlat(grid, *a.recorte)
    if getattr(a, "recorte_xy", None):
        grid.recortar(*a.recorte_xy)

    names = a.bandas or [b.name for b in grid.bands if b.is_pol and not b.is_complex]
    if not names:
        print("No hay polarizaciones en %s; use --bandas" % grid.path)
        return 2

    outdir = a.salida or os.path.join(
        os.path.dirname(os.path.abspath(a.archivo)),
        os.path.splitext(os.path.basename(a.archivo))[0] + "_gcov")

    print("Grilla   : %s  (%d x %d, EPSG:%s)" % (grid.path, grid.nx, grid.ny, grid.epsg))
    if grid.recortada:
        gt = grid.geotransform
        print("Recorte  : %d x %d celdas desde X %.0f Y %.0f"
              % (grid.ncols, grid.nrows, gt[0], gt[3]))
    print("Capas    : %s" % ", ".join(names))
    print("Salida   : %s" % outdir)
    print("Escala   : %s" % ("dB" if a.db else "gamma0 lineal"))
    if a.submuestreo > 1:
        nxo, nyo, _ = core.out_geometry(grid, a.submuestreo)
        print("Submuestreo: 1/%d (%s)  ->  %d x %d"
              % (a.submuestreo, "decimado" if a.decimar else "promediado", nxo, nyo))

    metodo = "decimar" if a.decimar else "promedio"
    state = {"last": -1}

    def prog(frac, msg):
        p = int(frac * 100)
        if p != state["last"]:
            state["last"] = p
            sys.stdout.write("\r  %3d%%  %-50s" % (p, msg[:50]))
            sys.stdout.flush()
        return True

    if a.c3:
        dim = core.export_c3(a.archivo, grid, outdir, progress=prog, step=a.submuestreo)
        print("\nMatriz C3 para SNAP: %s" % dim)
    elif a.dimap:
        dim = core.export_dimap(a.archivo, grid, names, outdir, to_db=a.db, progress=prog,
                                 step=a.submuestreo, metodo=metodo)
        print("\nProducto SNAP: %s" % dim)
    else:
        out = core.export_bands(a.archivo, grid, names, outdir, to_db=a.db, progress=prog,
                                step=a.submuestreo, metodo=metodo)
        print("\n" + "\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
