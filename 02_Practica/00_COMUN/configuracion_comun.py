# -*- coding: utf-8 -*-
"""
configuracion_comun.py
======================
Configuracion UNICA y compartida por los once trabajos practicos.

Aqui, y solo aqui, se definen:
  - la proyeccion y el tamano de pixel de la grilla comun,
  - los sitios de la matriz de convergencia (A a F, con sus subsitios A1, A2 y E1,
    y el recorte DELTA_NISAR del sector medio del Delta),
  - las fechas y ventanas de cada evento,
  - donde estan los datos originales en el disco del curso,
  - el nombre de la carpeta de cada practico.

Ningun practico redefine estos valores: todos los importan de este archivo.
Asi, dos practicos que trabajan sobre el mismo sitio producen rasteres que se
apilan pixel a pixel sin remuestrear.

COMO SE USA DESDE UN SCRIPT DE UN PRACTICO
------------------------------------------
Cada script trae al principio cuatro lineas que suben por el arbol de carpetas
hasta encontrar 00_COMUN y lo agregan a la ruta de Python. Despues:

    from configuracion_comun import SITIOS, EPSG, ruta_tp, ORIGINALES

COMO SE COMPRUEBA
-----------------
    conda activate sar
    python configuracion_comun.py

imprime la grilla de cada sitio y avisa si alguna carpeta de datos no existe.
"""
import os

# --------------------------------------------------------------- CARTOGRAFIA
# Toda la provincia se trabaja en UNA sola proyeccion: WGS 84 / UTM zona 21 S.
# Es la de los productos NISAR GCOV del Delta y la de las teselas Sentinel-2
# 21H y 21J.
# Paraná y Diamante (60,6 grados O) quedan a 3,6 grados del meridiano central
# (57 grados O): el error de escala alli es de alrededor de 1 m por km, que no
# afecta a ningun resultado del curso. Se declara y se acepta.
EPSG = 32721
PIXEL = 10.0          # metros: la grilla de trabajo comun (la de Sentinel-1 y 2)

NODATA = -9999.0      # valor sin dato de todos los GeoTIFF que escribe el curso


# -------------------------------------------------------------------- SITIOS
# bbox en grados (lon_min, lat_min, lon_max, lat_max).
# "origen" dice de donde salio la ventana, para que nadie la tome por exacta
# cuando no lo es:
#   "presentacion_02"  -> ventana escrita en las notas de la presentacion 02
#                         (02_SAR_eje_multisensor.pptx), con la que se
#                         procesaron las figuras del curso;
#   "mosaico_NISAR"    -> sale de la geometria de los mosaicos NISAR del Delta;
#   "subset_curso_2023"-> recorte de las escenas SAOCOM del curso SAR CEREGEO
#                         2023 (E:\CURSO SAR CEREGEO 2023), leido de sus .dim;
#   "kml_COSMO"        -> poligono del .kml que acompana la escena COSMO-SkyMed;
#   "aproximada"       -> ubicacion aproximada de la diapositiva 19 de la
#                         presentacion 01. Se ajusta en el Tp1, paso 1, y se
#                         anota aqui el valor definitivo.
SITIOS = {
    "A1_DELTA_QUEMAS": {
        "nombre": "Delta del Parana, quemas de 2020 (islas frente a Victoria y Gualeguay)",
        "bbox": (-59.96, -33.36, -59.72, -33.07),
        "origen": "subset_curso_2023",
        "practicos": ["Tp5"],
    },
    "A2_IBICUY": {
        "nombre": "Delta, Ibicuy (humedales)",
        "bbox": (-59.30, -33.85, -59.10, -33.65),
        "origen": "aproximada",
        "practicos": ["Tp2", "Tp3"],
    },
    "B_CONCORDIA": {
        "nombre": "Concordia - Salto Grande, rio Uruguay",
        "bbox": (-58.25, -31.50, -57.85, -31.10),
        "origen": "presentacion_02",
        "practicos": ["Tp1", "Tp4", "Tp6", "Tp10"],
    },
    "C_FEDERAL": {
        "nombre": "Federal, monte nativo del Espinal",
        "bbox": (-59.02, -30.99, -58.62, -30.59),
        "origen": "presentacion_02",
        "practicos": ["Tp9"],
    },
    "D_LAPAZ_VILLAGUAY": {
        "nombre": "Franja La Paz - Villaguay (BIOMASS, banda P)",
        "bbox": (-59.80, -31.95, -58.80, -30.60),
        "origen": "aproximada",
        "practicos": ["Tp9"],
    },
    "E_PARANA_DIAMANTE": {
        "nombre": "Barrancas del rio Parana, Parana - Diamante",
        "bbox": (-60.70, -32.10, -60.45, -31.65),
        "origen": "aproximada",
        "practicos": ["Tp7", "Tp10"],
    },
    "E1_DIAMANTE_BARRANCA": {
        "nombre": "Barranca de Diamante (escena COSMO-SkyMed Spotlight del 20/10/2018)",
        "bbox": (-60.71, -32.135, -60.575, -32.015),
        "origen": "kml_COSMO",
        "practicos": ["Tp7"],
    },
    "F_BOVRIL": {
        "nombre": "Bovril y su entorno rural",
        "bbox": (-59.53, -31.42, -59.40, -31.29),
        "origen": "presentacion_02",
        "practicos": ["Tp8"],
    },
    "DELTA_NISAR": {
        "nombre": "Delta del Parana, sector medio (recorte NISAR 2026)",
        "bbox": (-60.16, -33.83, -58.72, -32.96),
        "origen": "mosaico_NISAR",
        "practicos": ["Tp2", "Tp3"],
    },
}


# ------------------------------------------------------------------- EVENTOS
# Cada practico especifico trabaja un evento con una ventana "antes" y otra
# "despues". Las fechas marcadas como verificadas son las de las escenas que
# ya se usaron en la presentacion 02; las demas son VENTANAS DE BUSQUEDA:
# el Tp1 de cada grupo decide la escena concreta y la anota en la planilla.
EVENTOS = {
    "Tp5": {
        "sitio": "A1_DELTA_QUEMAS",
        "que": "Quemas en las islas del Delta, 2020 (desde febrero; el practico mide de mediados de julio a octubre)",
        # Escenas reales del archivo del curso 2023 (ORIGINALES_2023):
        "s1_slc": ["2020-07-10", "2020-07-16", "2020-07-28", "2020-08-21",
                   "2020-09-02", "2020-09-26"],             # Sentinel-1 IW SLC, descendente
        "saocom_qp": ["2020-07-21", "2020-10-25"],         # SAOCOM-1A Stripmap QP (antes / despues)
        "saocom_dp": ["2020-09-07"],                       # SAOCOM-1A Stripmap DP VV+VH
        "alos2_mosaico": "2020",                           # mosaico anual JAXA 25 m
        "optico_despues": "2020-10-13",                    # S2B, Planetary Computer (presentacion 02)
        "antes": ("2020-06-15", "2020-07-31"),             # ventana de busqueda del optico previo
        "despues": ("2020-10-01", "2020-10-31"),
    },
    "Tp6": {
        "sitio": "B_CONCORDIA",
        "que": "Crecidas del rio Uruguay, noviembre de 2023 y mayo de 2024",
        "serie": ("2023-10-01", "2024-06-30"),
        "pico_1": "2023-11-04",                     # S1A y S2B del mismo dia (verificada)
        "referencia_seca": "2026-01-22",            # S1C y S2B, rio en nivel normal (verificada)
    },
    "Tp7": {
        "sitio": "E1_DIAMANTE_BARRANCA",
        "que": "Grietas y deformacion de la barranca de Diamante",
        # COSMO-SkyMed del archivo del curso 2023 (octubre de 2018):
        "cosmo_himage": ["2018-10-12", "2018-10-15", "2018-10-18", "2018-10-19",
                         "2018-10-28"],
        "cosmo_spotlight": "2018-10-20",
        "par_insar_x": ("2018-10-15", "2018-10-19"),       # ya procesado en el curso 2023
        "s1_grdh": "2018-10-12",
        "serie_c": ("2025-01-01", "2026-09-30"),           # pares Sentinel-1 SLC recientes (ASF)
    },
    "Tp8": {
        "sitio": "F_BOVRIL",
        "que": "Suelo expuesto y carcavas en el centro de Entre Rios",
        "serie": ("2023-01-01", "2023-12-31"),
        "novasar": "2023-09-14",                    # escena 47974 (verificada)
        "optico_par": "2023-09-10",                 # S2A (verificada)
    },
    "Tp9": {
        "sitio": "C_FEDERAL",
        "que": "Perdida y degradacion del monte nativo",
        "fechas_L": ["2011-03-13", "2021-08-08", "2026-09-17"],  # ALOS, ALOS-2, NISAR (verificadas)
        "fechas_C": ["2021-08-10", "2025-09-24"],                # S1 (verificadas)
        "fechas_optico": ["2016-03-30", "2021-08-06", "2025-09-24", "2026-09-16"],
        "biomass": "2026-08-12",                                  # L1B DGM sobre Federal (verificada)
        "biomass_franja_D": "2026-09-17",                         # franja D (verificada)
    },
    "Tp10": {
        "sitio": "B_CONCORDIA",
        "que": "Crecimiento urbano y subsidencia (Concordia y Parana)",
        "nisar": "2026-09-18",                      # descendente (verificada)
        "optico": "2026-09-16",                     # S2A (verificada)
        "novasar": "2023-09-13",                    # escena 47942 (verificada)
    },
}


# --------------------------------------------------------------------- RUTAS
def _localizar_practica():
    """Devuelve la carpeta 02_Practica subiendo desde este archivo."""
    d = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(d) == "00_COMUN":
        return os.path.dirname(d)
    p = d
    while p != os.path.dirname(p):
        if os.path.isdir(os.path.join(p, "00_COMUN")):
            return p
        p = os.path.dirname(p)
    return os.path.dirname(d)


PRACTICA = _localizar_practica()                 # ...\02_Practica
COMUN = os.path.join(PRACTICA, "00_COMUN")
AOI_DIR = os.path.join(COMUN, "01_AOI")
REFERENCIAS_DIR = os.path.join(COMUN, "02_Referencias_control")
TOPOGRAFIA_DIR = os.path.join(COMUN, "03_Topografia")

# Los ORIGINALES (lo que entrega el proveedor, sin tocar) viven en el disco del
# curso, en UN solo lugar. No se copian dentro de los practicos.
# Se pueden mover cambiando solo estas dos lineas, o con la variable de entorno
# CURSO_SAR_ORIGINALES.
ORIGINALES = os.environ.get(
    "CURSO_SAR_ORIGINALES",
    os.path.join(COMUN, "08_Originales_crudos"))

# Copias locales hechas con 00_COMUN/datos_crudos.py (copiar_locales). Si el
# disco original no esta conectado (una computadora del aula), los programas
# usan la copia de 08_Originales_crudos/LOCALES/<NOMBRE>, que conserva la misma
# estructura de carpetas que el original.
LOCALES = os.path.join(ORIGINALES, "LOCALES")


def _ruta_dato(variable, original, nombre_local):
    """Variable de entorno > disco original > copia local en datos crudos."""
    if os.environ.get(variable):
        return os.environ[variable]
    copia = os.path.join(LOCALES, nombre_local)
    if not os.path.isdir(original) and os.path.isdir(copia):
        return copia
    return original

# Los NISAR GCOV del Delta. Los llena datos_crudos.py nisar (ASF, cuenta NASA
# Earthdata) en 08_Originales_crudos\NISAR_DELTA\BANDA_L_NASA. La banda S (ISRO)
# se baja a mano del portal Bhoonidhi de ISRO a BANDA_S_ISRO: alli esta la del
# 30/09/2026 (traza 10, cuadro 105), de la misma pasada que la banda L de esa fecha. Si estan en otra carpeta, se indica con CURSO_SAR_NISAR_DELTA.
NISAR_DELTA = os.environ.get("CURSO_SAR_NISAR_DELTA") or os.path.join(ORIGINALES, "NISAR_DELTA")

# Las escenas NovaSAR-1 (banda S, 6 m, HH) del archivo del curso, cedidas por
# CSIRO. Cada escena viene en tres niveles: grd (proyectada al terreno), srd
# (rango oblicuo) y slc (complejo, con fase). Calibracion del producto:
# sigma0 = DN^2 / CalibrationConstant, con CalibrationConstant = 1E+05 en el
# metadata.xml de las cinco escenas.
NOVASAR = _ruta_dato("CURSO_SAR_NOVASAR",
                     r"E:\IMÁGENES NOVASAR-1 2023 2024\ENTRE RIOS-SANTA FE", "NOVASAR")
NOVASAR_ESCENAS = {
    # escena: (fecha, hora UTC, sitio que cubre y fraccion del sitio con dato)
    # Coberturas MEDIDAS con Tp1_02_inventario_local.py sobre los GRD (16/10/2026):
    #   47942 -> B_CONCORDIA 39 %   (no cubre Concordia completa)
    #   47974 -> F_BOVRIL 92 %      (y 11 % de la franja D)
    #   50896 -> C_FEDERAL 51 %     (NO cubre Concordia, aunque tiene la misma hora de pasada que 47942)
    #   50918 -> franja D 4 %       (no sirve para ningun sitio del curso)
    #   47525 -> San Javier (Santa Fe), fuera de los sitios
    "47525": ("2023-08-30", "01:51", "San Javier (Santa Fe), fuera de los sitios"),
    "47942": ("2023-09-13", "01:36", "B_CONCORDIA (39 %)"),
    "47974": ("2023-09-14", "01:42", "F_BOVRIL (92 %)"),
    "50896": ("2023-12-22", "01:36", "C_FEDERAL (51 %)"),
    "50918": ("2023-12-23", "01:42", "D_LAPAZ_VILLAGUAY (4 %)"),
}
# Archivo de practicas del curso SAR CEREGEO 2023: escenas reales de Entre
# Rios y del Delta (Sentinel-1 SLC 2020, SAOCOM-1A Stripmap 2020, mosaicos
# ALOS-2 2020, COSMO-SkyMed de Diamante 2018, MDE del IGN de 5 m, grietas
# relevadas). Son 556 GB: se leen de donde estan; datos_crudos.py copia SOLO
# las escenas que cubren los sitios del curso.
ORIGINALES_2023 = _ruta_dato(
    "CURSO_SAR_2023", r"E:\CURSO SAR CEREGEO 2023\PRACTICAL EXERCISES", "CURSO_2023")

# COSMO-SkyMed (banda X) de Diamante, octubre-noviembre de 2018, del curso
# TelSAR 2018: HIMAGE (3 m) y Spotlight (1 m), con el MDE del IGN, las grietas
# relevadas en la barranca y una Sentinel-1 GRDH del 12/10/2018.
# (Hay copia en ORIGINALES_2023\InSAR\02 IMAGES\CSKS SCS\DIAMANTE.)
COSMO_DIAMANTE = _ruta_dato(
    "CURSO_SAR_COSMO", r"F:\HFdV COURSES\CEREGEO\2018\TelSAR\DIAMANTE", "COSMO_DIAMANTE")

# Bosques de MapBiomas Argentina 2023 recortados a cada escena NovaSAR (en la
# misma carpeta raiz). Es un producto de TERCEROS, hecho con Landsat: sirve
# para comparar y para estratificar, NUNCA como verdad de campo (Tp4).
MAPBIOMAS_BOSQUES = (os.path.join(LOCALES, "MAPBIOMAS") if NOVASAR.startswith(LOCALES)
                     else os.path.dirname(NOVASAR))

PRACTICOS = {
    "Tp1": "Tp1_Convergencia",
    "Tp2": "Tp2_SAR_multibanda",
    "Tp3": "Tp3_Armonizacion",
    "Tp4": "Tp4_Validacion",
    "Tp5": "Tp5_Incendios",
    "Tp6": "Tp6_Inundaciones",
    "Tp7": "Tp7_Barrancas_deslizamientos",
    "Tp8": "Tp8_Erosion_suelos",
    "Tp9": "Tp9_Deforestacion",
    "Tp10": "Tp10_Impacto_urbano",
    "Tp11": "Tp11_Integrador",
}


def ruta_tp(codigo, *sub):
    """Ruta dentro de un practico. Ej.: ruta_tp('Tp5', '05_Resultados', '02_Rasters')"""
    return os.path.join(PRACTICA, PRACTICOS[codigo], *sub)


# ------------------------------------------------------ CONVENCIONES DE VALOR
UNIDADES = {
    "SAR": "gamma0 LINEAL (potencia). dB = 10*log10(lineal) y SOLO para ver: "
           "todo promedio, remuestreo o diferencia se calcula en lineal.",
    "OPTICO": "reflectancia de superficie, 0 a 1 (Sentinel-2 L2A armonizado)",
    "LIDAR": "metros (rh98 de GEDI, h_canopy y h_te_best_fit de ATL08)",
}


if __name__ == "__main__":
    print(__doc__.split("COMO SE USA")[0])
    print("Carpeta de practica :", PRACTICA)
    print("Originales          :", ORIGINALES,
          "" if os.path.isdir(ORIGINALES) else "   <-- NO EXISTE todavia")
    print("NISAR del Delta     :", NISAR_DELTA,
          "" if os.path.isdir(NISAR_DELTA) else "   <-- NO EXISTE en este equipo")
    print("NovaSAR-1           :", NOVASAR,
          "" if os.path.isdir(NOVASAR) else "   <-- NO EXISTE en este equipo")
    print("MapBiomas (bosques) :", MAPBIOMAS_BOSQUES,
          "" if os.path.isdir(MAPBIOMAS_BOSQUES) else "   <-- NO EXISTE en este equipo")
    print()
    print("Proyeccion comun: EPSG:%d, pixel %.0f m" % (EPSG, PIXEL))
    for k, s in SITIOS.items():
        print("  %-18s %-10s %s" % (k, s["origen"], s["bbox"]))
