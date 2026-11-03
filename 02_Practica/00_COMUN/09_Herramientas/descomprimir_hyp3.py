"""Descomprime los productos HyP3 de un sitio, cada .zip en su propia carpeta.

Saltea los que ya estan descomprimidos y completos (mismo numero de archivos
y mismos tamanos que dentro del .zip). Se puede cortar y volver a correr.
Los .zip no se borran.

Uso, en el Miniforge Prompt con el entorno sar:
    python D:\\CURSOS_CEREGEO_2026\\02_Practica\\00_COMUN\\09_Herramientas\\descomprimir_hyp3.py E_PARANA_DIAMANTE
"""
import glob
import os
import sys
import time
import zipfile

BASE = r"D:\CURSOS_CEREGEO_2026\02_Practica\00_COMUN\08_Originales_crudos\HYP3"


def completo(z, carpeta):
    for i in z.infolist():
        if i.is_dir():
            continue
        f = os.path.join(carpeta, i.filename)
        if not os.path.isfile(f) or os.path.getsize(f) != i.file_size:
            return False
    return True


def main():
    sitio = sys.argv[1] if len(sys.argv) > 1 else "E_PARANA_DIAMANTE"
    carpeta = os.path.join(BASE, sitio)
    zips = sorted(glob.glob(os.path.join(carpeta, "*.zip")))
    print("Carpeta: %s\n.zip encontrados: %d\n" % (carpeta, len(zips)))
    hechos = saltados = malos = 0
    t0 = time.time()
    for k, ruta in enumerate(zips, 1):
        nombre = os.path.basename(ruta)
        try:
            with zipfile.ZipFile(ruta) as z:
                if completo(z, carpeta):
                    saltados += 1
                    print("[%3d/%d] ya estaba   %s" % (k, len(zips), nombre))
                    continue
                z.extractall(carpeta)
                if not completo(z, carpeta):
                    raise IOError("quedo incompleto")
            hechos += 1
            print("[%3d/%d] descomprimido %s  (%.0f min)" % (k, len(zips), nombre, (time.time() - t0) / 60))
        except Exception as e:  # noqa: BLE001
            malos += 1
            print("[%3d/%d] ERROR %s: %s" % (k, len(zips), nombre, e))
    n_vert = len(glob.glob(os.path.join(carpeta, "*", "*_vert_disp.tif")))
    print("\nDescomprimidos ahora: %d | ya estaban: %d | con error: %d" % (hechos, saltados, malos))
    print("Pares listos (con *_vert_disp.tif): %d de %d" % (n_vert, len(zips)))
    if malos:
        print("Hay .zip con error: volver a correr; si persiste, avisar.")


if __name__ == "__main__":
    main()
