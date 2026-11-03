# -*- coding: utf-8 -*-
"""
armar_subsets.py - Subsets de cada practico para SNAP y para QGIS.

Para cada producto del practico deja, en <Tp>\\02_Subsets_SNAP_QGIS:

  SNAP_DIMAP\\<nombre>.dim (+ .data)
      Formato BEAM-DIMAP de SNAP. Bandas LINEALES reales (potencia, gamma0 o
      sigma0 segun el producto) y bandas VIRTUALES en dB (y el cociente
      copolarizada/cruzada en dB). Los metadatos ORIGINALES del proveedor van
      dentro del .dim (Metadata > Original_Product_Metadata) y el recorte se
      documenta en Metadata > Procesamiento_del_recorte.
      Este programa escribe el .dim directamente. NovaSAR-1: el lector de SNAP
      es un complemento de la comunidad que gpt no carga; si en SNAP_DIMAP ya
      hay un .dim de NovaSAR hecho en SNAP Desktop (Import > SAR Sensors >
      NOVASAR, Raster > Subset, Save Product As), se conserva y solo se le
      agregan las bandas virtuales. Si no, se escribe uno propio con
      geocodificacion por puntos de enlace y sigma0 por la constante de
      calibracion del producto (sin Abstracted_Metadata).

  QGIS_GeoTIFF\\<nombre>.tif + <nombre>_metadatos.txt
      Mismas bandas, con las de dB como bandas reales (GeoTIFF no tiene bandas
      virtuales). Los metadatos van como etiquetas GDAL (QGIS: Propiedades >
      Informacion) y, completos y legibles, en el _metadatos.txt, porque QGIS
      no muestra los metadatos internos de SNAP.

  RGB_copol_cruzada_cociente\\<nombre>_RGB_dB.tif y _RGB_8bit.tif
      Solo productos de polarizacion dual: R = copolarizada (dB),
      G = cruzada (dB), B = cociente copolarizada/cruzada (dB). La version de
      8 bits usa rangos FIJOS (tabla RANGOS_RGB) para que dos fechas o dos
      sensores se comparen con la misma escala.

  Metadatos_originales\\<nombre>\\
      Copia sin tocar de los archivos de metadatos del proveedor (XML, JSON).

  LEEME_subsets.md
      Lista de lo que se armo, con su fuente (organismo, sensor, fecha, URL)
      y lo que falto.

Pixel y proyeccion NATIVOS de cada producto (no se remuestrea a la grilla del
practico: eso lo hacen los scripts del practico). Unica excepcion: en
Sentinel-2 las bandas de 20 m se llevan a 10 m por vecino mas proximo para que
el .dim tenga un solo tamano de banda; se declara en sus metadatos.

USO (Miniforge Prompt, entorno sar):
    cd /d D:\\CURSOS_CEREGEO_2026\\02_Practica\\00_COMUN
    python armar_subsets.py Tp9                 (muestra que hay y que falta)
    python armar_subsets.py Tp9 --confirmar     (arma los subsets)
    python armar_subsets.py Tp9 --confirmar --solo nisar_gcov s1_rtc
    python armar_subsets.py Tp9 --confirmar --rehacer   (pisa lo ya armado)

SNAP: se busca gpt.exe en C:\\Program Files\\esa-snap*\\bin (o la variable de
entorno SNAP_GPT) solo para el control final: SNAP abre cada .dim y lo recorta
por coordenadas.
"""
import argparse
import datetime as _dt
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from configuracion_comun import SITIOS, ORIGINALES, NOVASAR, ORIGINALES_2023, ruta_tp   # noqa: E402

PROGRAMA = "00_COMUN/armar_subsets.py"

# Rangos fijos de la version de 8 bits del RGB (dB). Iguales para todas las
# fechas y sensores del curso: si cada imagen se estira sola, el desfase entre
# sensores parece cambio.
RANGOS_RGB = {"co": (-25.0, 0.0), "cruz": (-32.0, -8.0), "cociente": (0.0, 15.0)}

# ---------------------------------------------------------------------------
# Que productos lleva cada practico
# ---------------------------------------------------------------------------
TRABAJOS = {
    "Tp9": {
        "sitio": "C_FEDERAL",
        "otros_sitios": ["D_LAPAZ_VILLAGUAY"],
        "productos": [
            ("nisar_gcov", {"patron": os.path.join("NISAR", "NISAR_L2_PR_GCOV_*_20260917T*.h5"),
                            "banda": "LSAR", "etiqueta": "NISAR_L_20260917"}),
            ("novasar_grd", {"escena": "50896", "etiqueta": "NovaSAR1_S_20231222",
                             "ventana": "filas 38720 a 59538, todas las columnas"}),
            ("alos1_rtc", {"carpeta": os.path.join("ASF", "C_FEDERAL", "ALOS"), "fecha": "20110313",
                           "etiqueta": "ALOS1_L_20110313"}),
            ("alos2_mosaico", {"anio": "2021", "etiqueta": "ALOS2_L_mosaico2021"}),
            ("s1_rtc", {"fecha": "20210810", "etiqueta": "S1_C_20210810"}),
            ("s1_rtc", {"fecha": "20250924", "etiqueta": "S1_C_20250924"}),
            ("s1_rtc", {"fecha": "20260914", "etiqueta": "S1_C_20260914"}),
            ("s2_l2a", {"fecha": "20210806", "etiqueta": "S2_20210806"}),
            ("s2_l2a", {"fecha": "20250924", "etiqueta": "S2_20250924"}),
            ("s2_l2a", {"fecha": "20260916", "etiqueta": "S2_20260916"}),
            ("copdem", {"etiqueta": "CopernicusDEM30"}),
            ("biomass_dgm", {"producto": "BIO_S2_DGM__1S_20260812T100031_20260812T100052_T_G01_M04_C07_T006_F284_02_DW2XBG",
                             "etiqueta": "BIOMASS_P_20260812"}),
            ("biomass_l2a", {"tipo": "FH", "etiqueta": "BIOMASS_P_FH_20260728_0809",
                             "productos": ["BIO_FP_FH__L2A_20260728T100021_20260809T100050_T_G01_M04_C___T006_F284_02_DY549T",
                                           "BIO_FP_FH__L2A_20260728T100040_20260809T100109_T_G01_M04_C___T006_F285_02_DY2GQU"]}),
            ("biomass_l2a", {"tipo": "GN", "etiqueta": "BIOMASS_P_GN_20260728_0809",
                             "productos": ["BIO_FP_GN__L2A_20260728T100021_20260809T100050_T_G01_M04_C___T006_F284_02_DY54BZ",
                                           "BIO_FP_GN__L2A_20260728T100040_20260809T100109_T_G01_M04_C___T006_F285_02_DY2GSX"]}),
            # la pila del 18/08 al 30/08/2026 completa el sitio (la anterior cubre el 89 %; juntas, el 100 %)
            ("biomass_l2a", {"tipo": "FH", "etiqueta": "BIOMASS_P_FH_20260818_0830",
                             "productos": ["BIO_FP_FH__L2A_20260818T100035_20260830T100104_T_G01_M04_C___T006_F284_02_DXKUMF",
                                           "BIO_FP_FH__L2A_20260818T100054_20260830T100127_T_G01_M04_C___T006_F285_02_DXKUMP"]}),
            ("biomass_l2a", {"tipo": "GN", "etiqueta": "BIOMASS_P_GN_20260818_0830",
                             "productos": ["BIO_FP_GN__L2A_20260818T100035_20260830T100104_T_G01_M04_C___T006_F284_02_DXKUOE",
                                           "BIO_FP_GN__L2A_20260818T100054_20260830T100127_T_G01_M04_C___T006_F285_02_DXKUP3"]}),
            # Agregado el 21/10/2026 (subsets completos del Tp5 al Tp10): todo dato crudo que cubre el sitio
            # Franja D (La Paz - Villaguay): hasta ahora solo tenia LiDAR. Sentinel-1, Sentinel-2, NISAR L,
            # BIOMASS (cinco franjas que juntas cubren el 97 % del sitio, que mide ~95 x 150 km; la del 17/09/2026
            # es la de la parte B de la guia) y L2A en dos pilas (17/09 al 29/09/2026, 66 % del sitio; 18/08 al 30/08, 48 %; juntas, 79 %)
            ("s1_rtc", {"sitio_prod": "D_LAPAZ_VILLAGUAY", "fecha": "20260914", "etiqueta": "S1_C_20260914"}),
            ("s2_l2a", {"sitio_prod": "D_LAPAZ_VILLAGUAY", "fecha": "20260916", "etiqueta": "S2_20260916"}),
            ("copdem", {"sitio_prod": "D_LAPAZ_VILLAGUAY", "etiqueta": "CopernicusDEM30"}),
            ("nisar_gcov", {"sitio_prod": "D_LAPAZ_VILLAGUAY", "patron": os.path.join("NISAR", "NISAR_L2_PR_GCOV_031_010_D_104_*_20260918T*.h5"),
                            "banda": "LSAR", "etiqueta": "NISAR_L_20260918"}),
            ("nisar_gcov", {"sitio_prod": "D_LAPAZ_VILLAGUAY", "patron": os.path.join("NISAR", "NISAR_L2_PR_GCOV_030_161_A_162_*_20260917T*.h5"),
                            "banda": "LSAR", "etiqueta": "NISAR_L_20260917"}),
            ("biomass_dgm", {"sitio_prod": "D_LAPAZ_VILLAGUAY", "etiqueta": "BIOMASS_P_20260917_S1",
                             "producto": "BIO_S1_DGM__1S_20260917T100450_20260917T100510_T_G01_M05_C02_T006_F284_02_DXX0LC"}),
            # la misma franja del 17/09/2026 reproyectada a la grilla del curso (EPSG:32721, 25 m) para la parte B
            # del Tp9 con las huellas GEDI de la franja D (Tp9_02 --p_sitio D_LAPAZ_VILLAGUAY)
            ("biomass_dgm", {"sitio_prod": "D_LAPAZ_VILLAGUAY", "etiqueta": "BIOMASS_P_20260917_S1_UTM21S",
                             "mapa": "EPSG:32721", "pixel": 25,
                             "producto": "BIO_S1_DGM__1S_20260917T100450_20260917T100510_T_G01_M05_C02_T006_F284_02_DXX0LC"}),
            ("biomass_dgm", {"sitio_prod": "D_LAPAZ_VILLAGUAY", "etiqueta": "BIOMASS_P_20260323_S2",
                             "producto": "BIO_S2_DGM__1S_20260323T215136_20260323T215157_T_G01_M02_C07_T043_F182_01_DORPNW"}),
            ("biomass_dgm", {"sitio_prod": "D_LAPAZ_VILLAGUAY", "etiqueta": "BIOMASS_P_20260902_S3",
                             "producto": "BIO_S3_DGM__1S_20260902T100046_20260902T100106_T_G01_M04_C07_T006_F284_02_DX5FS1"}),
            ("biomass_dgm", {"sitio_prod": "D_LAPAZ_VILLAGUAY", "etiqueta": "BIOMASS_P_20261002_S1",
                             "producto": "BIO_S1_DGM__1S_20261002T100442_20261002T100502_T_G01_M05_C07_T006_F283_02_DYOSV8"}),
            ("biomass_dgm", {"sitio_prod": "D_LAPAZ_VILLAGUAY", "etiqueta": "BIOMASS_P_20260302_S1",
                             "producto": "BIO_S1_DGM__1S_20260302T215122_20260302T215142_T_G01_M02_C07_T043_F182_01_DNOS23"}),
            ("biomass_l2a", {"sitio_prod": "D_LAPAZ_VILLAGUAY", "tipo": "FH", "etiqueta": "BIOMASS_P_FH_20260818_0830",
                             "productos": ["BIO_FP_FH__L2A_20260818T100035_20260830T100104_T_G01_M04_C___T006_F284_02_DXKUMF",
                                           "BIO_FP_FH__L2A_20260818T100016_20260830T100045_T_G01_M04_C___T006_F283_02_DXKU56",
                                           "BIO_FP_FH__L2A_20260818T100054_20260830T100127_T_G01_M04_C___T006_F285_02_DXKUMP"]}),
            ("biomass_l2a", {"sitio_prod": "D_LAPAZ_VILLAGUAY", "tipo": "GN", "etiqueta": "BIOMASS_P_GN_20260818_0830",
                             "productos": ["BIO_FP_GN__L2A_20260818T100035_20260830T100104_T_G01_M04_C___T006_F284_02_DXKUOE",
                                           "BIO_FP_GN__L2A_20260818T100016_20260830T100045_T_G01_M04_C___T006_F283_02_DXKU7S",
                                           "BIO_FP_GN__L2A_20260818T100054_20260830T100127_T_G01_M04_C___T006_F285_02_DXKUP3"]}),
            ("biomass_l2a", {"sitio_prod": "D_LAPAZ_VILLAGUAY", "tipo": "FH", "etiqueta": "BIOMASS_P_FH_20260917_0929",
                             "productos": ["BIO_FP_FH__L2A_20260917T100450_20260929T100519_T_G01_M05_C___T006_F284_02_DZ8GU6",
                                           "BIO_FP_FH__L2A_20260917T100431_20260929T100500_T_G01_M05_C___T006_F283_02_DZ8GTN"]}),
            ("biomass_l2a", {"sitio_prod": "D_LAPAZ_VILLAGUAY", "tipo": "GN", "etiqueta": "BIOMASS_P_GN_20260917_0929",
                             "productos": ["BIO_FP_GN__L2A_20260917T100450_20260929T100519_T_G01_M05_C___T006_F284_02_DZ8GW0",
                                           "BIO_FP_GN__L2A_20260917T100431_20260929T100500_T_G01_M05_C___T006_F283_02_DZ8GVH"]}),
        ],
    },
    "Tp1": {
        "sitio": "B_CONCORDIA",
        "productos": [
            ("s1_rtc", {"fecha": "20231104", "etiqueta": "S1_C_20231104"}),
            ("s2_l2a", {"fecha": "20231104", "etiqueta": "S2_20231104"}),
            ("novasar_grd", {"escena": "47942", "etiqueta": "NovaSAR1_S_20230913",
                             "ventana": "filas 62141 a 83002, columnas 0 a 5909"}),
            ("copdem", {"etiqueta": "CopernicusDEM30"}),
            ("jrc_gsw", {"etiqueta": "JRC_GSW_ocurrencia"}),
            # BIOMASS banda P (ESA), agregado el 21/10/2026. Se eligio la franja (S1, S2 o S3) cuya huella cubre
            # el 100 % del sitio (las otras franjas de la misma traza lo cubren en parte o no lo cubren)
            ("biomass_dgm", {"producto": "BIO_S1_DGM__1S_20260722T100017_20260722T100038_T_G01_M04_C07_T006_F284_02_DUZ5DS",
                             "etiqueta": "BIOMASS_P_20260722"}),
            # L2A: la pila del 07/07 al 19/07/2026 cubre todo el sitio (la del 28/07 al 09/08, solo el 17 %)
            ("biomass_l2a", {"tipo": "FH", "etiqueta": "BIOMASS_P_FH_20260707_0719",
                             "productos": ["BIO_FP_FH__L2A_20260707T100008_20260719T100036_T_G01_M04_C___T006_F284_02_DVEP9V"]}),
            ("biomass_l2a", {"tipo": "GN", "etiqueta": "BIOMASS_P_GN_20260707_0719",
                             "productos": ["BIO_FP_GN__L2A_20260707T100008_20260719T100036_T_G01_M04_C___T006_F284_02_DVEPD6"]}),
        ],
    },
    "Tp2": {
        "sitio": "A2_IBICUY",
        "otros_sitios": ["DELTA_NISAR"],
        "productos": [
            ("nisar_gcov", {"patron": os.path.join("NISAR_DELTA", "BANDA_L_NASA", "NISAR_L2_PR_GCOV_*_20260930T*.h5"),
                            "banda": "LSAR", "etiqueta": "NISAR_L_20260930"}),
            ("nisar_gcov", {"patron": os.path.join("NISAR_DELTA", "BANDA_S_ISRO", "NISAR_S2_PR_GCOV_*_20260930T*.h5"),
                            "banda": "SSAR", "etiqueta": "NISAR_S_20260930"}),
            ("nisar_gcov", {"patron": os.path.join("NISAR_DELTA", "BANDA_L_NASA", "NISAR_L2_PR_GCOV_*_2005_*_20260917T*.h5"),
                            "banda": "LSAR", "etiqueta": "NISAR_L_20260917"}),
            ("s1_rtc", {"fecha": "20260926", "etiqueta": "S1_C_20260926"}),
            ("s1_rtc", {"fecha": "20261002", "etiqueta": "S1_C_20261002"}),
            ("s2_l2a", {"fecha": "20260916", "etiqueta": "S2_20260916"}),
            # BIOMASS banda P (ESA), agregado el 21/10/2026. Se eligio la franja (S1, S2 o S3) cuya huella cubre
            # el 100 % del sitio (las otras franjas de la misma traza lo cubren en parte o no lo cubren)
            ("biomass_dgm", {"producto": "BIO_S2_DGM__1S_20261005T100425_20261005T100445_T_G01_M05_C01_T006_F282_02_DYUDWU",
                             "etiqueta": "BIOMASS_P_20261005"}),
            ("biomass_l2a", {"tipo": "FH", "etiqueta": "BIOMASS_P_FH_20251123_1205",
                             "productos": ["BIO_FP_FH__L2A_20251123T214705_20251205T214733_T_G01_M01_C___T043_F184_02_DYT1NC"]}),
            ("biomass_l2a", {"tipo": "GN", "etiqueta": "BIOMASS_P_GN_20251123_1205",
                             "productos": ["BIO_FP_GN__L2A_20251123T214705_20251205T214733_T_G01_M01_C___T043_F184_02_DYT1P9"]}),
            # Delta medio (DELTA_NISAR, el recorte NISAR 2026), agregado el 21/10/2026. El sitio mide ~135 x 97 km
            # y una franja BIOMASS cubre como mucho el 51 %: estas cuatro franjas lo cubren juntas (100 %).
            # La del 29/09/2026 es la mas cercana a NISAR (30/09/2026).
            # NISAR del 30/09/2026 sobre todo el Delta medio: L cubre todo el sitio; S, el 16 % (el resto queda sin dato)
            ("nisar_gcov", {"sitio_prod": "DELTA_NISAR", "patron": os.path.join("NISAR_DELTA", "BANDA_L_NASA", "NISAR_L2_PR_GCOV_*_20260930T*.h5"),
                            "banda": "LSAR", "etiqueta": "NISAR_L_20260930"}),
            ("nisar_gcov", {"sitio_prod": "DELTA_NISAR", "patron": os.path.join("NISAR_DELTA", "BANDA_S_ISRO", "NISAR_S2_PR_GCOV_*_20260930T*.h5"),
                            "banda": "SSAR", "etiqueta": "NISAR_S_20260930"}),
            ("biomass_dgm", {"sitio_prod": "DELTA_NISAR", "etiqueta": "BIOMASS_P_20260929_S1",
                             "producto": "BIO_S1_DGM__1S_20260929T100421_20260929T100441_T_G01_M05_C06_T006_F282_02_DYJ83M"}),
            ("biomass_dgm", {"sitio_prod": "DELTA_NISAR", "etiqueta": "BIOMASS_P_20261014_S2",
                             "producto": "BIO_S2_DGM__1S_20261014T100431_20261014T100452_T_G01_M05_C04_T006_F282_02_DZB1IV"}),
            ("biomass_dgm", {"sitio_prod": "DELTA_NISAR", "etiqueta": "BIOMASS_P_20260323_S2",
                             "producto": "BIO_S2_DGM__1S_20260323T215214_20260323T215235_T_G01_M02_C07_T043_F184_01_DORPKG"}),
            ("biomass_dgm", {"sitio_prod": "DELTA_NISAR", "etiqueta": "BIOMASS_P_20260413_S3",
                             "producto": "BIO_S3_DGM__1S_20260413T215228_20260413T215249_T_G01_M02_C07_T043_F184_01_DPULEB"}),
            ("biomass_l2a", {"sitio_prod": "DELTA_NISAR", "tipo": "FH", "etiqueta": "BIOMASS_P_FH_20251123_1205",
                             "productos": ["BIO_FP_FH__L2A_20251123T214646_20251205T214714_T_G01_M01_C___T043_F183_02_DYT5IA",
                                           "BIO_FP_FH__L2A_20251123T214705_20251205T214733_T_G01_M01_C___T043_F184_02_DYT1NC"]}),
            ("biomass_l2a", {"sitio_prod": "DELTA_NISAR", "tipo": "GN", "etiqueta": "BIOMASS_P_GN_20251123_1205",
                             "productos": ["BIO_FP_GN__L2A_20251123T214646_20251205T214714_T_G01_M01_C___T043_F183_02_DYT5K9",
                                           "BIO_FP_GN__L2A_20251123T214705_20251205T214733_T_G01_M01_C___T043_F184_02_DYT1P9"]}),
        ],
    },
    "Tp3": {
        "sitio": "A2_IBICUY",
        "productos": [
            ("s2_l2a", {"fecha": "20260916", "etiqueta": "S2_20260916"}),
            ("copdem", {"etiqueta": "CopernicusDEM30"}),
            ("jrc_gsw", {"etiqueta": "JRC_GSW_ocurrencia"}),
            # BIOMASS banda P (ESA), agregado el 21/10/2026. Se eligio la franja (S1, S2 o S3) cuya huella cubre
            # el 100 % del sitio (las otras franjas de la misma traza lo cubren en parte o no lo cubren)
            ("biomass_dgm", {"producto": "BIO_S2_DGM__1S_20261005T100425_20261005T100445_T_G01_M05_C01_T006_F282_02_DYUDWU",
                             "etiqueta": "BIOMASS_P_20261005"}),
            ("biomass_l2a", {"tipo": "FH", "etiqueta": "BIOMASS_P_FH_20251123_1205",
                             "productos": ["BIO_FP_FH__L2A_20251123T214705_20251205T214733_T_G01_M01_C___T043_F184_02_DYT1NC"]}),
            ("biomass_l2a", {"tipo": "GN", "etiqueta": "BIOMASS_P_GN_20251123_1205",
                             "productos": ["BIO_FP_GN__L2A_20251123T214705_20251205T214733_T_G01_M01_C___T043_F184_02_DYT1P9"]}),
        ],
    },
    "Tp5": {
        "sitio": "A1_DELTA_QUEMAS",
        "productos": [
            ("s1_rtc", {"fecha": "20200716", "etiqueta": "S1_C_20200716"}),
            ("s1_rtc", {"fecha": "20200926", "etiqueta": "S1_C_20200926"}),
            ("alos2_mosaico", {"anio": "2019", "etiqueta": "ALOS2_L_mosaico2019"}),
            ("alos2_mosaico", {"anio": "2020", "etiqueta": "ALOS2_L_mosaico2020"}),
            ("snap_nativo", {"raiz": ORIGINALES_2023,
                             "patron": os.path.join("TP 10 BURNED AREAS SAOCOM 1 STRIPMAP", "SAOCOM-1",
                                                    "subset_SAO1A_SQP_S5_SLC_AD_FULL_210720.dim"),
                             "etiqueta": "SAOCOM_L_20200721_QP", "tipo": "SAOCOM_1A_SM_QP_SLC", "fecha": "2020-07-21",
                             "cita": "CONAE. SAOCOM-1A StripMap S5 cuadripolar (QP), SLC, 21/07/2020 (antes de las quemas). "
                                     "Recorte del curso SAR CEREGEO 2023 (CONAE: https://catalogos.conae.gov.ar)"}),
            ("snap_nativo", {"raiz": ORIGINALES_2023,
                             "patron": os.path.join("TP 10 BURNED AREAS SAOCOM 1 STRIPMAP", "SAOCOM-1",
                                                    "subset_SAO1A_SQP_S5_SLC_AD_FULL_251020.dim"),
                             "etiqueta": "SAOCOM_L_20201025_QP", "tipo": "SAOCOM_1A_SM_QP_SLC", "fecha": "2020-10-25",
                             "cita": "CONAE. SAOCOM-1A StripMap S5 cuadripolar (QP), SLC, 25/10/2020 (despues de las quemas). "
                                     "Recorte del curso SAR CEREGEO 2023 (CONAE: https://catalogos.conae.gov.ar)"}),
            ("snap_nativo", {"raiz": ORIGINALES_2023,
                             "patron": os.path.join("TP 10 BURNED AREAS SAOCOM 1 STRIPMAP", "SAOCOM-1",
                                                    "subset_SAO1A_SDP_S2_SLC_AD_VV_VH_070920.dim"),
                             "etiqueta": "SAOCOM_L_20200907_DP", "tipo": "SAOCOM_1A_SM_DP_SLC", "fecha": "2020-09-07",
                             "cita": "CONAE. SAOCOM-1A StripMap S2 doble polarizacion VV+VH, SLC, 07/09/2020. Recorte del "
                                     "curso SAR CEREGEO 2023 (CONAE: https://catalogos.conae.gov.ar)"}),
            ("s2_l2a", {"fecha": "20200715", "etiqueta": "S2_20200715"}),
            ("s2_l2a", {"fecha": "20201013", "etiqueta": "S2_20201013"}),
            ("copdem", {"etiqueta": "CopernicusDEM30"}),
            ("jrc_gsw", {"etiqueta": "JRC_GSW_ocurrencia"}),
            # BIOMASS banda P (ESA), agregado el 21/10/2026. Se eligio la franja (S1, S2 o S3) cuya huella cubre
            # el 100 % del sitio (las otras franjas de la misma traza lo cubren en parte o no lo cubren)
            # Agregado el 21/10/2026 (subsets completos del Tp5 al Tp10): todo dato crudo que cubre el sitio
            # NISAR L del 30/09/2026 (cubre todo el sitio; posterior al evento). La banda S de esa pasada no tiene dato en el sitio
            ("nisar_gcov", {"patron": os.path.join("NISAR_DELTA", "BANDA_L_NASA", "NISAR_L2_PR_GCOV_*_20260930T*.h5"),
                            "banda": "LSAR", "etiqueta": "NISAR_L_20260930"}),
            ("biomass_dgm", {"producto": "BIO_S2_DGM__1S_20260323T215214_20260323T215235_T_G01_M02_C07_T043_F184_01_DORPKG",
                             "etiqueta": "BIOMASS_P_20260323"}),
        ],
    },
    "Tp6": {
        "sitio": "B_CONCORDIA",
        "productos": [
            ("s1_rtc", {"fecha": "20231023", "etiqueta": "S1_C_20231023"}),
            ("s1_rtc", {"fecha": "20231104", "etiqueta": "S1_C_20231104"}),
            ("s1_rtc", {"fecha": "20231116", "etiqueta": "S1_C_20231116"}),
            ("s2_l2a", {"fecha": "20231104", "etiqueta": "S2_20231104"}),
            ("novasar_grd", {"escena": "47942", "etiqueta": "NovaSAR1_S_20230913",
                             "ventana": "filas 62141 a 83002, columnas 0 a 5909"}),
            ("copdem", {"etiqueta": "CopernicusDEM30"}),
            ("jrc_gsw", {"etiqueta": "JRC_GSW_ocurrencia"}),
            # BIOMASS banda P (ESA), agregado el 21/10/2026. Se eligio la franja (S1, S2 o S3) cuya huella cubre
            # el 100 % del sitio (las otras franjas de la misma traza lo cubren en parte o no lo cubren)
            ("biomass_dgm", {"producto": "BIO_S1_DGM__1S_20260722T100017_20260722T100038_T_G01_M04_C07_T006_F284_02_DUZ5DS",
                             "etiqueta": "BIOMASS_P_20260722"}),
            # L2A: la pila del 07/07 al 19/07/2026 cubre todo el sitio (la del 28/07 al 09/08, solo el 17 %)
            ("biomass_l2a", {"tipo": "FH", "etiqueta": "BIOMASS_P_FH_20260707_0719",
                             "productos": ["BIO_FP_FH__L2A_20260707T100008_20260719T100036_T_G01_M04_C___T006_F284_02_DVEP9V"]}),
            ("biomass_l2a", {"tipo": "GN", "etiqueta": "BIOMASS_P_GN_20260707_0719",
                             "productos": ["BIO_FP_GN__L2A_20260707T100008_20260719T100036_T_G01_M04_C___T006_F284_02_DVEPD6"]}),
        ],
    },
    "Tp7": {
        "sitio": "E1_DIAMANTE_BARRANCA",
        "productos": [
            ("snap_nativo", {"patron": os.path.join("LOCALES", "**", "CSKS1_SCS_B_S2_13_HH_RD_SF_20181020210754_*.h5"),
                             "etiqueta": "CSK_X_20181020_Spotlight", "tipo": "CSK_SCS_B_Spotlight", "fecha": "2018-10-20",
                             "cita": "ASI. COSMO-SkyMed (CSKS1) Spotlight-2, SCS_B (SLC), HH, 20/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("snap_nativo", {"patron": os.path.join("LOCALES", "**", "CSKS4_SCS_B_HI_24_HH_RD_SF_20181015204956_*.h5"),
                             "etiqueta": "CSK_X_20181015_HI24", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-15",
                             "cita": "ASI. COSMO-SkyMed (CSKS4) Himage HI_24, SCS_B (SLC), HH, 15/10/2018 (primera del par "
                                     "InSAR). Archivo del curso TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("snap_nativo", {"patron": os.path.join("LOCALES", "**", "CSKS1_SCS_B_HI_24_HH_RD_SF_20181019204958_*.h5"),
                             "etiqueta": "CSK_X_20181019_HI24", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-19",
                             "cita": "ASI. COSMO-SkyMed (CSKS1) Himage HI_24, SCS_B (SLC), HH, 19/10/2018 (segunda del par "
                                     "InSAR). Archivo del curso TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            # Agregado el 21/10/2026 (subsets completos del Tp5 al Tp10): todo dato crudo que cubre el sitio
            # COSMO-SkyMed X: las otras seis escenas del archivo (cuatro cubren todo el sitio; las HI_04, ~28 %)
            ("snap_nativo", {"cobertura_minima": 10, "patron": os.path.join("LOCALES", "**", "CSKS2_SCS_B_HI_09_HH_RD_SF_20181012210752_*.h5"),
                             "etiqueta": "CSK_X_20181012_HI09", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-12",
                             "cita": "ASI. COSMO-SkyMed (CSKS2) Himage HI_09, SCS_B (SLC), HH, 12/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("snap_nativo", {"cobertura_minima": 10, "patron": os.path.join("LOCALES", "**", "CSKS3_SCS_B_HI_15_HH_RD_SF_20181018210151_*.h5"),
                             "etiqueta": "CSK_X_20181018_HI15", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-18",
                             "cita": "ASI. COSMO-SkyMed (CSKS3) Himage HI_15, SCS_B (SLC), HH, 18/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("snap_nativo", {"cobertura_minima": 10, "patron": os.path.join("LOCALES", "**", "CSKS3_SCS_B_HI_0A_HH_RD_SF_20181019211949_*.h5"),
                             "etiqueta": "CSK_X_20181019_HI0A", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-19",
                             "cita": "ASI. COSMO-SkyMed (CSKS3) Himage HI_0A, SCS_B (SLC), HH, 19/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("snap_nativo", {"cobertura_minima": 10, "patron": os.path.join("LOCALES", "**", "CSKS2_SCS_B_HI_09_VV_RD_SF_20181028210753_*.h5"),
                             "etiqueta": "CSK_X_20181028_HI09_VV", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-28",
                             "cita": "ASI. COSMO-SkyMed (CSKS2) Himage HI_09, SCS_B (SLC), VV, 28/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("snap_nativo", {"cobertura_minima": 10, "patron": os.path.join("LOCALES", "**", "CSKS4_SCS_B_HI_04_HH_RD_SF_20181011211351_*.h5"),
                             "etiqueta": "CSK_X_20181011_HI04", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-11",
                             "cita": "ASI. COSMO-SkyMed (CSKS4) Himage HI_04, SCS_B (SLC), HH, 11/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("snap_nativo", {"cobertura_minima": 10, "patron": os.path.join("LOCALES", "**", "CSKS1_SCS_B_HI_04_HH_RD_SF_20181015211352_*.h5"),
                             "etiqueta": "CSK_X_20181015_HI04", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-15",
                             "cita": "ASI. COSMO-SkyMed (CSKS1) Himage HI_04, SCS_B (SLC), HH, 15/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("s1_rtc", {"fecha": "20181012", "etiqueta": "S1_C_20181012"}),
            ("s1_rtc", {"fecha": "20181024", "etiqueta": "S1_C_20181024"}),
            ("ign_mde", {"raiz": ORIGINALES_2023, "etiqueta": "IGN_MDE_5m",
                         "carpeta": os.path.join("InSAR", "02 IMAGES", "CSKS SCS", "DIAMANTE", "DEM IGN")}),
            ("serie", {"etiqueta": "IGN_MDE_mosaico2018", "tipo": "IGN_MDE_AR_5M_MOSAICO_2018",
                       "capas": [("elevacion_IGN_mosaico2018",
                                  os.path.join(ORIGINALES_2023, "InSAR", "02 IMAGES", "CSKS SCS", "DIAMANTE",
                                               "DEM IGN", "diamante_IGN.tif"))],
                       "unidad": "m", "nodata": -32767,
                       "desc": "{nb}: MDE-Ar 5 m del IGN, mosaico del curso 2018 (metros enteros; 0 = sin dato sobre el rio)",
                       "cita": "Instituto Geografico Nacional (IGN), Argentina. MDE-Ar aerofotogrametrico 5 m, mosaico "
                               "diamante_IGN.tif armado en el curso TelSAR 2018. "
                               "https://www.ign.gob.ar/NuestrasActividades/Geodesia/ModeloDigitalElevaciones/Introduccion",
                       "nota": "Cubre la ciudad y la barranca de Diamante. El sitio entero cae en las hojas 3360-02-2-a, "
                               "-b, -c y -d del IGN; lo que queda sin dato al oeste de -60,65 es el rio Parana y las "
                               "islas, donde el relevamiento fotogrametrico no da altura (la hoja 3360-02-1 queda al "
                               "oeste de -60,75, fuera del sitio; verificado el 23/10/2026). "
                               "Valores en metros enteros (int16) y 0 sobre el rio: usar IGN_MDE_5m (teselas "
                               "originales, decimales) donde ambos tienen dato."}),
            ("s2_l2a", {"fecha": "20181019", "etiqueta": "S2_20181019"}),
            ("s2_l2a", {"fecha": "20181004", "etiqueta": "S2_20181004"}),
            ("copdem", {"etiqueta": "CopernicusDEM30"}),
            # BIOMASS banda P (ESA), agregado el 21/10/2026. Se eligio la franja (S1, S2 o S3) cuya huella cubre
            # el 100 % del sitio (las otras franjas de la misma traza lo cubren en parte o no lo cubren)
            ("biomass_dgm", {"producto": "BIO_S2_DGM__1S_20260603T215634_20260603T215654_T_G01_M03_C07_T043_F183_02_DSHG0C",
                             "etiqueta": "BIOMASS_P_20260603"}),
            ("biomass_l2a", {"tipo": "FH", "etiqueta": "BIOMASS_P_FH_20260519_0531",
                             "productos": ["BIO_FP_FH__L2A_20260519T215625_20260531T215653_T_G01_M03_C___T043_F183_02_DTF2U5"]}),
            ("biomass_l2a", {"tipo": "GN", "etiqueta": "BIOMASS_P_GN_20260519_0531",
                             "productos": ["BIO_FP_GN__L2A_20260519T215625_20260531T215653_T_G01_M03_C___T043_F183_02_DTF31G"]}),
        ],
    },
    "Tp8": {
        "sitio": "F_BOVRIL",
        "productos": [
            ("novasar_grd", {"escena": "47974", "etiqueta": "NovaSAR1_S_20230914",
                             "ventana": "filas 76468 a 83247, columnas 0 a 5235"}),
            ("s1_rtc", {"fecha": "20230917", "etiqueta": "S1_C_20230917"}),
            ("s1_rtc", {"fecha": "20230905", "etiqueta": "S1_C_20230905"}),
            ("s2_l2a", {"fecha": "20230910", "etiqueta": "S2_20230910"}),
            ("copdem", {"etiqueta": "CopernicusDEM30"}),
            # BIOMASS banda P (ESA), agregado el 21/10/2026. Se eligio la franja (S1, S2 o S3) cuya huella cubre
            # el 100 % del sitio (las otras franjas de la misma traza lo cubren en parte o no lo cubren)
            ("biomass_dgm", {"producto": "BIO_S1_DGM__1S_20260917T100450_20260917T100510_T_G01_M05_C02_T006_F284_02_DXX0LC",
                             "etiqueta": "BIOMASS_P_20260917"}),
            # Agregado el 21/10/2026 (subsets completos del Tp5 al Tp10): todo dato crudo que cubre el sitio
            # NISAR L: 18/09 (descendente) y 17/09 (ascendente), cada una cubre todo el sitio. La banda S del 30/09 no llega
            ("nisar_gcov", {"patron": os.path.join("NISAR", "NISAR_L2_PR_GCOV_031_010_D_104_*_20260918T*.h5"),
                            "banda": "LSAR", "etiqueta": "NISAR_L_20260918"}),
            ("nisar_gcov", {"patron": os.path.join("NISAR", "NISAR_L2_PR_GCOV_030_161_A_162_*_20260917T*.h5"),
                            "banda": "LSAR", "etiqueta": "NISAR_L_20260917"}),
            ("biomass_l2a", {"tipo": "FH", "etiqueta": "BIOMASS_P_FH_20260917_0929",
                             "productos": ["BIO_FP_FH__L2A_20260917T100450_20260929T100519_T_G01_M05_C___T006_F284_02_DZ8GU6"]}),
            ("biomass_l2a", {"tipo": "GN", "etiqueta": "BIOMASS_P_GN_20260917_0929",
                             "productos": ["BIO_FP_GN__L2A_20260917T100450_20260929T100519_T_G01_M05_C___T006_F284_02_DZ8GW0"]}),
        ],
    },
    "Tp10": {
        "sitio": "B_CONCORDIA",
        "otros_sitios": ["E_PARANA_DIAMANTE"],
        "productos": [
            ("nisar_gcov", {"patron": os.path.join("NISAR", "NISAR_L2_PR_GCOV_*_20260918T*.h5"),
                            "banda": "LSAR", "etiqueta": "NISAR_L_20260918"}),
            ("novasar_grd", {"escena": "47942", "etiqueta": "NovaSAR1_S_20230913",
                             "ventana": "filas 62141 a 83002, columnas 0 a 5909"}),
            ("s1_rtc", {"fecha": "20260914", "etiqueta": "S1_C_20260914"}),
            ("s1_rtc", {"fecha": "20260915", "etiqueta": "S1_C_20260915"}),
            ("s2_l2a", {"fecha": "20260916", "etiqueta": "S2_20260916"}),
            ("copdem", {"etiqueta": "CopernicusDEM30"}),
            # BIOMASS banda P (ESA), agregado el 21/10/2026. Se eligio la franja (S1, S2 o S3) cuya huella cubre
            # el 100 % del sitio (las otras franjas de la misma traza lo cubren en parte o no lo cubren)
            ("biomass_dgm", {"producto": "BIO_S1_DGM__1S_20260722T100017_20260722T100038_T_G01_M04_C07_T006_F284_02_DUZ5DS",
                             "etiqueta": "BIOMASS_P_20260722"}),
            # L2A: la pila del 07/07 al 19/07/2026 cubre todo el sitio (la del 28/07 al 09/08, solo el 17 %)
            ("biomass_l2a", {"tipo": "FH", "etiqueta": "BIOMASS_P_FH_20260707_0719",
                             "productos": ["BIO_FP_FH__L2A_20260707T100008_20260719T100036_T_G01_M04_C___T006_F284_02_DVEP9V"]}),
            ("biomass_l2a", {"tipo": "GN", "etiqueta": "BIOMASS_P_GN_20260707_0719",
                             "productos": ["BIO_FP_GN__L2A_20260707T100008_20260719T100036_T_G01_M04_C___T006_F284_02_DVEPD6"]}),
            # Sitio E (Parana - Diamante), agregado el 21/10/2026: banda P y banda X del sitio E en el Tp10
            # (subsidencia). Los nombres llevan el sitio E. BIOMASS L1B: ninguna franja cubre sola todo el sitio;
            # los cuadros 182 (norte, 55 %) y 183 (sur, 63 %) de la misma pasada del 03/06/2026 lo cubren juntos.
            ("biomass_dgm", {"sitio_prod": "E_PARANA_DIAMANTE", "etiqueta": "BIOMASS_P_20260603_F182",
                             "producto": "BIO_S2_DGM__1S_20260603T215615_20260603T215635_T_G01_M03_C07_T043_F182_02_DSHG5R"}),
            ("biomass_dgm", {"sitio_prod": "E_PARANA_DIAMANTE", "etiqueta": "BIOMASS_P_20260603_F183",
                             "producto": "BIO_S2_DGM__1S_20260603T215634_20260603T215654_T_G01_M03_C07_T043_F183_02_DSHG0C"}),
            ("biomass_l2a", {"sitio_prod": "E_PARANA_DIAMANTE", "tipo": "FH", "etiqueta": "BIOMASS_P_FH_20260519_0531",
                             "productos": ["BIO_FP_FH__L2A_20260519T215606_20260531T215634_T_G01_M03_C___T043_F182_02_DTF6T8",
                                           "BIO_FP_FH__L2A_20260519T215625_20260531T215653_T_G01_M03_C___T043_F183_02_DTF2U5"]}),
            ("biomass_l2a", {"sitio_prod": "E_PARANA_DIAMANTE", "tipo": "GN", "etiqueta": "BIOMASS_P_GN_20260519_0531",
                             "productos": ["BIO_FP_GN__L2A_20260519T215606_20260531T215634_T_G01_M03_C___T043_F182_02_DTF6VD",
                                           "BIO_FP_GN__L2A_20260519T215625_20260531T215653_T_G01_M03_C___T043_F183_02_DTF31G"]}),
            # MDE-Ar 5 m del IGN del sitio E, agregado el 22/10/2026: 63 hojas enviadas por el IGN (relevamiento
            # "0009 - 2013 - Rio Parana - Sector 3.5"), descomprimidas en 08_Originales_crudos\IGN_MDE_5m
            ("ign_mde", {"sitio_prod": "E_PARANA_DIAMANTE", "raiz": ORIGINALES, "carpeta": "IGN_MDE_5m",
                         "etiqueta": "IGN_MDE_5m", "fecha": "2013",
                         "origen": "Relevamiento 0009 - 2013 - Rio Parana - Sector 3.5, hojas enviadas por el IGN "
                                   "al docente el 22/10/2026"}),
            # NISAR L del 17/09/2026 (ascendente): cubre el 57 % del sitio E (la parte norte, Parana)
            ("nisar_gcov", {"sitio_prod": "E_PARANA_DIAMANTE", "patron": os.path.join("NISAR", "NISAR_L2_PR_GCOV_030_161_A_162_*_20260917T*.h5"),
                            "banda": "LSAR", "etiqueta": "NISAR_L_20260917"}),
            # COSMO-SkyMed X (SLC, octubre de 2018): las escenas estan centradas en Diamante y cubren solo la parte
            # oeste del sitio E; se recorta cada escena que cubre al menos el 10 % del sitio
            # (la cobertura se calcula con el .kml de la escena; las que cubren menos se informan y se saltean)
            ("snap_nativo", {"sitio_prod": "E_PARANA_DIAMANTE", "cobertura_minima": 10,
                             "patron": os.path.join("LOCALES", "**", "CSKS4_SCS_B_HI_04_HH_RD_SF_20181011211351_*.h5"),
                             "etiqueta": "CSK_X_20181011_HI04", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-11",
                             "cita": "ASI. COSMO-SkyMed (CSKS4) Himage HI_04, SCS_B (SLC), HH, 11/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("snap_nativo", {"sitio_prod": "E_PARANA_DIAMANTE", "cobertura_minima": 10,
                             "patron": os.path.join("LOCALES", "**", "CSKS2_SCS_B_HI_09_HH_RD_SF_20181012210752_*.h5"),
                             "etiqueta": "CSK_X_20181012_HI09", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-12",
                             "cita": "ASI. COSMO-SkyMed (CSKS2) Himage HI_09, SCS_B (SLC), HH, 12/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("snap_nativo", {"sitio_prod": "E_PARANA_DIAMANTE", "cobertura_minima": 10,
                             "patron": os.path.join("LOCALES", "**", "CSKS1_SCS_B_HI_04_HH_RD_SF_20181015211352_*.h5"),
                             "etiqueta": "CSK_X_20181015_HI04", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-15",
                             "cita": "ASI. COSMO-SkyMed (CSKS1) Himage HI_04, SCS_B (SLC), HH, 15/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("snap_nativo", {"sitio_prod": "E_PARANA_DIAMANTE", "cobertura_minima": 10,
                             "patron": os.path.join("LOCALES", "**", "CSKS4_SCS_B_HI_24_HH_RD_SF_20181015204956_*.h5"),
                             "etiqueta": "CSK_X_20181015_HI24", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-15",
                             "cita": "ASI. COSMO-SkyMed (CSKS4) Himage HI_24, SCS_B (SLC), HH, 15/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("snap_nativo", {"sitio_prod": "E_PARANA_DIAMANTE", "cobertura_minima": 10,
                             "patron": os.path.join("LOCALES", "**", "CSKS3_SCS_B_HI_15_HH_RD_SF_20181018210151_*.h5"),
                             "etiqueta": "CSK_X_20181018_HI15", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-18",
                             "cita": "ASI. COSMO-SkyMed (CSKS3) Himage HI_15, SCS_B (SLC), HH, 18/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("snap_nativo", {"sitio_prod": "E_PARANA_DIAMANTE", "cobertura_minima": 10,
                             "patron": os.path.join("LOCALES", "**", "CSKS1_SCS_B_HI_24_HH_RD_SF_20181019204958_*.h5"),
                             "etiqueta": "CSK_X_20181019_HI24", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-19",
                             "cita": "ASI. COSMO-SkyMed (CSKS1) Himage HI_24, SCS_B (SLC), HH, 19/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("snap_nativo", {"sitio_prod": "E_PARANA_DIAMANTE", "cobertura_minima": 10,
                             "patron": os.path.join("LOCALES", "**", "CSKS3_SCS_B_HI_0A_HH_RD_SF_20181019211949_*.h5"),
                             "etiqueta": "CSK_X_20181019_HI0A", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-19",
                             "cita": "ASI. COSMO-SkyMed (CSKS3) Himage HI_0A, SCS_B (SLC), HH, 19/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("snap_nativo", {"sitio_prod": "E_PARANA_DIAMANTE", "cobertura_minima": 10,
                             "patron": os.path.join("LOCALES", "**", "CSKS1_SCS_B_S2_13_HH_RD_SF_20181020210754_*.h5"),
                             "etiqueta": "CSK_X_20181020_Spotlight", "tipo": "CSK_SCS_B_Spotlight", "fecha": "2018-10-20",
                             "cita": "ASI. COSMO-SkyMed (CSKS1) Spotlight-2 S2_13, SCS_B (SLC), HH, 20/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
            ("snap_nativo", {"sitio_prod": "E_PARANA_DIAMANTE", "cobertura_minima": 10,
                             "patron": os.path.join("LOCALES", "**", "CSKS2_SCS_B_HI_09_VV_RD_SF_20181028210753_*.h5"),
                             "etiqueta": "CSK_X_20181028_HI09_VV", "tipo": "CSK_SCS_B_Himage", "fecha": "2018-10-28",
                             "cita": "ASI. COSMO-SkyMed (CSKS2) Himage HI_09, SCS_B (SLC), VV, 28/10/2018. Archivo del curso "
                                     "TelSAR 2018 (ASI: https://www.asi.it/en/earth-science/cosmo-skymed/)"}),
        ],
    },
}


class Falta(Exception):
    """El insumo no esta en datos crudos (se informa y se sigue)."""


# Landsat 8 y 9: a cada fecha Sentinel-2 de cada practico se le agrega la pasada Landsat
# mas cercana con el sitio despejado, la que eligio datos_crudos.py landsat
# (PLANETARY\landsat_elegidas.csv). El nombre lleva el satelite y la fecha real.
LANDSAT_CSV = os.path.join(ORIGINALES, "PLANETARY", "landsat_elegidas.csv")


def _landsat_elegida(sitio, fecha_s2):
    import csv
    if not os.path.exists(LANDSAT_CSV):
        return None
    with open(LANDSAT_CSV, encoding="utf-8-sig") as fc:
        for r in csv.DictReader(fc):
            if r["sitio"] == sitio and r["fecha_s2"] == fecha_s2:
                return r
    return None


# CBERS-4A WPM: por cada zona y fecha objetivo del practico, la escena elegida en CBERS4A\cbers_elegidas.csv,
# en dos productos: multiespectral a 8 m y pansharpened a 2 m (zonas_cbers.py).
CBERS_CSV = os.path.join(ORIGINALES, "CBERS4A", "cbers_elegidas.csv")


def _cbers_elegida(zona, f_obj):
    import csv
    if not os.path.exists(CBERS_CSV):
        return None
    with open(CBERS_CSV, encoding="utf-8-sig") as fc:
        for r in csv.DictReader(fc):
            if r["zona"] == zona and r["fecha_objetivo"] == f_obj and r.get("id"):
                return r
    return None


try:
    from zonas_cbers import ZONAS as _ZONAS_CBERS
except ImportError:
    _ZONAS_CBERS = {}
ZONAS_CBERS_SITIO = {z: v["sitio"] for z, v in _ZONAS_CBERS.items()}
for _z, _zc in _ZONAS_CBERS.items():
    for _fo, _tps in _zc["fechas"].items():
        _r = _cbers_elegida(_z, _fo)
        _f = _r["id"].split("_")[3] if _r else "cerca_de_%s" % _fo
        for _tp in _tps:
            if _tp in TRABAJOS:
                TRABAJOS[_tp]["productos"] += [
                    ("cbers_ms", {"zona": _z, "fecha_obj": _fo, "etiqueta": "CBERS4A_%s_%s_MS_8m" % (_z, _f)}),
                    ("cbers_ps", {"zona": _z, "fecha_obj": _fo,
                                  "etiqueta": "CBERS4A_%s_%s_pansharpened_2m" % (_z, _f)})]

# AlphaEarth Foundations: embeddings anuales de 10 m (datos_crudos.py embeddings), en los anios de las
# fechas de cada practico (2026 todavia no existe: se usa 2025).
EMB_PRACTICOS = {
    "Tp1": [("B_CONCORDIA", 2023)], "Tp2": [("A2_IBICUY", 2025)], "Tp3": [("A2_IBICUY", 2025)],
    "Tp5": [("A1_DELTA_QUEMAS", 2020)], "Tp6": [("B_CONCORDIA", 2023)],
    "Tp7": [("E1_DIAMANTE_BARRANCA", 2018), ("E1_DIAMANTE_BARRANCA", 2025)], "Tp8": [("F_BOVRIL", 2023)],
    "Tp9": [("C_FEDERAL", 2021), ("C_FEDERAL", 2025)],
    "Tp10": [("B_CONCORDIA", 2025), ("E_PARANA_DIAMANTE", 2025)],
}
for _tp, _lista in EMB_PRACTICOS.items():
    if _tp in TRABAJOS:
        for _st, _y in _lista:
            _et = "AlphaEarth_embeddings_%d_10m" % _y
            if _st != TRABAJOS[_tp]["sitio"]:
                _et = "%s_%s" % (_st, _et)
            TRABAJOS[_tp]["productos"].append(("embeddings", {"sitio_emb": _st, "anio": _y, "etiqueta": _et}))

for _tp, _t in TRABAJOS.items():
    for _tipo, _cfg in list(_t["productos"]):
        if _tipo == "s2_l2a":
            _sp = _cfg.get("sitio_prod", _t["sitio"])          # Landsat del mismo sitio que el Sentinel-2
            _extra = {"sitio_prod": _sp} if "sitio_prod" in _cfg else {}
            _r = _landsat_elegida(_sp, _cfg["fecha"])
            if "sitio_prod" in _cfg and not (_r and _r["fecha_landsat"]):
                continue                                      # sin Landsat elegido para ese otro sitio
            _et = ("L%s_%s" % (_r["plataforma"][-1], _r["fecha_landsat"])) if (_r and _r["fecha_landsat"]) else \
                "Landsat_cerca_S2_%s" % _cfg["fecha"]
            _t["productos"].append(("landsat_l2", dict({"fecha_s2": _cfg["fecha"], "etiqueta": _et}, **_extra)))
            if _r and _r["fecha_landsat"]:
                _t["productos"].append(("fusion_landsat_s2", dict({"fecha_s2": _cfg["fecha"],
                                                                   "etiqueta": "%s_fusion_S2_%s_10m" % (_et, _cfg["fecha"])},
                                                                  **_extra)))


# ---------------------------------------------------------------------------
# Modelo de producto
# ---------------------------------------------------------------------------
class Producto:
    def __init__(self, nombre):
        self.nombre = nombre
        self.crs_wkt = ""
        self.transform = None          # rasterio Affine
        self.gcps = None               # [(fila, columna, lon, lat, alt)] si no hay transform
        self.tie = None                # grillas de puntos de enlace lat/lon para SNAP (GRD sin proyectar)
        self.ancho = self.alto = 0
        self.bandas = []               # dict(nombre, datos, unidad, desc, nodata, escala, desplaz)
        self.virtuales = []            # dict(nombre, expr, funcion, unidad, desc, valida)
        self.rgb = None                # (banda_co, banda_cruz, etiqueta_co, etiqueta_cruz)
        self.metadatos = {}            # arbol original {nombre: valor | dict | list}
        self.recorte = {}              # documentacion del recorte
        self.inicio = self.fin = ""    # fechas ISO
        self.tipo = ""
        self.cita = ""                 # "Fuente: ..." para LEEME y figuras
        self.archivos_meta = []        # archivos originales a copiar
        self.dim_hecho_por_snap = ""   # ruta del .dim si lo escribio gpt

    def banda(self, nombre, datos, unidad, desc, nodata=0.0, escala=1.0, desplaz=0.0):
        self.bandas.append(dict(nombre=nombre, datos=datos, unidad=unidad, desc=desc,
                                nodata=nodata, escala=escala, desplaz=desplaz))
        self.alto, self.ancho = datos.shape

    def virtual(self, nombre, expr, funcion, unidad, desc, valida=""):
        self.virtuales.append(dict(nombre=nombre, expr=expr, funcion=funcion,
                                   unidad=unidad, desc=desc, valida=valida))

    def datos(self, nombre):
        for b in self.bandas:
            if b["nombre"] == nombre:
                return b["datos"]
        raise KeyError(nombre)


def db(x):
    x = np.asarray(x, dtype="float32")
    out = np.full(x.shape, np.nan, dtype="float32")
    ok = np.isfinite(x) & (x > 0)
    out[ok] = 10.0 * np.log10(x[ok])
    return out


def agregar_db_y_cociente(p, co, cruz, pol_co, pol_cruz, magnitud):
    """Bandas virtuales en dB de las dos polarizaciones y el cociente co/cruz."""
    for b, pol in ((co, pol_co), (cruz, pol_cruz)):
        if b is None:
            continue
        p.virtual(b + "_db", "%s > 0 ? 10*log10(%s) : NaN" % (b, b),
                  (lambda nb: (lambda pr: db(pr.datos(nb))))(b), "dB",
                  "%s %s en dB (banda virtual: 10*log10 de la banda lineal)" % (magnitud, pol), "%s > 0" % b)
    if co is not None and cruz is not None:
        p.virtual("%s_%s_cociente_db" % (pol_co, pol_cruz),
                  "(%s > 0 && %s > 0) ? 10*log10(%s/%s) : NaN" % (co, cruz, co, cruz),
                  lambda pr: db(_cociente(pr.datos(co), pr.datos(cruz))), "dB",
                  "Cociente %s/%s en dB = %s_db - %s_db" % (pol_co, pol_cruz, co, cruz),
                  "%s > 0 && %s > 0" % (co, cruz))
        p.rgb = (co + "_db", cruz + "_db", "%s_%s_cociente_db" % (pol_co, pol_cruz), pol_co, pol_cruz)


def _cociente(a, b):
    a = a.astype("float32")
    b = b.astype("float32")
    out = np.full(a.shape, np.nan, dtype="float32")
    ok = (a > 0) & (b > 0)
    out[ok] = a[ok] / b[ok]
    return out


# ---------------------------------------------------------------------------
# Metadatos: lectura de XML, JSON y HDF5 a un arbol comun
# ---------------------------------------------------------------------------
def _nombre_valido(s):
    s = re.sub(r"\{[^}]*\}", "", str(s))          # espacios de nombres XML
    s = re.sub(r"[^A-Za-z0-9_.\-]+", "_", s).strip("_")
    return s or "item"


def xml_a_arbol(ruta):
    raiz = ET.parse(ruta).getroot()

    def nodo(e):
        hijos = list(e)
        attrs = {("@" + _nombre_valido(k)): v for k, v in e.attrib.items()}
        if not hijos:
            texto = (e.text or "").strip()
            if attrs:
                d = dict(attrs)
                d["valor"] = texto
                return d
            return texto
        d = dict(attrs)
        for h in hijos:
            k = _nombre_valido(h.tag)
            v = nodo(h)
            if k in d:
                if not isinstance(d[k], list) or not getattr(d[k], "_repetido", False):
                    lst = _Lista([d[k]])
                    d[k] = lst
                d[k].append(v)
            else:
                d[k] = v
        return d

    return {_nombre_valido(raiz.tag): nodo(raiz)}


class _Lista(list):
    _repetido = True


def json_a_arbol(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def h5_a_arbol(ruta, grupos, max_elementos=200):
    """Atributos y datasets chicos (<= max_elementos) de los grupos pedidos."""
    import h5py

    def val(x):
        if isinstance(x, bytes):
            return x.decode("utf-8", "replace")
        if isinstance(x, np.ndarray):
            if x.dtype.kind in "SO":
                return ", ".join(v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)
                                 for v in x.ravel())
            if x.size == 1:
                return val(x.ravel()[0])
            return ", ".join(str(v) for v in x.ravel())
        if isinstance(x, np.generic):
            return x.item()
        return x

    def recorrer(g):
        d = {}
        for k, v in g.attrs.items():
            d["@" + _nombre_valido(k)] = val(v)
        for k, obj in g.items():
            if isinstance(obj, h5py.Group):
                d[_nombre_valido(k)] = recorrer(obj)
            elif obj.shape is not None and int(np.prod(obj.shape or (1,))) <= max_elementos:
                try:
                    v = val(obj[()])
                except Exception as e:                    # noqa: BLE001
                    v = "(no se pudo leer: %s)" % e
                if obj.attrs:
                    dd = {"valor": v}
                    for ka, va in obj.attrs.items():
                        dd["@" + _nombre_valido(ka)] = val(va)
                    d[_nombre_valido(k)] = dd
                else:
                    d[_nombre_valido(k)] = v
            else:
                d[_nombre_valido(k)] = "(dataset de %s %s: no se copia)" % (
                    "x".join(str(n) for n in obj.shape), obj.dtype)
        return d

    with h5py.File(ruta, "r") as h:
        arbol = {"atributos_raiz": {("@" + _nombre_valido(k)): val(v) for k, v in h.attrs.items()}}
        for gr in grupos:
            if gr in h:
                arbol[_nombre_valido(gr.strip("/").replace("/", "__"))] = recorrer(h[gr])
    return arbol


def aplanar(arbol, prefijo=""):
    """[(ruta, valor)] para etiquetas GDAL y el _metadatos.txt."""
    out = []
    if isinstance(arbol, dict):
        for k, v in arbol.items():
            out += aplanar(v, "%s/%s" % (prefijo, k) if prefijo else str(k))
    elif isinstance(arbol, list):
        for i, v in enumerate(arbol, 1):
            out += aplanar(v, "%s[%d]" % (prefijo, i))
    else:
        out.append((prefijo, "" if arbol is None else str(arbol)))
    return out


# ---------------------------------------------------------------------------
# Escritura BEAM-DIMAP
# ---------------------------------------------------------------------------
_TIPOS = {"int8": ("int8", 1), "uint8": ("uint8", 1), "int16": ("int16", 2), "uint16": ("uint16", 12),
          "int32": ("int32", 3), "float32": ("float32", 4), "float64": ("float64", 5)}


def _md_xml(nombre, arbol, sangria):
    s = " " * sangria
    lineas = ['%s<MDElem name="%s">' % (s, escape(_nombre_valido(nombre)))]
    usados = {}

    def unico(n):
        n = _nombre_valido(n)
        if n in usados:
            usados[n] += 1
            return "%s_%d" % (n, usados[n])
        usados[n] = 1
        return n

    if isinstance(arbol, dict):
        items = list(arbol.items())
    else:
        items = [("%s_%d" % (_nombre_valido(nombre), i), v) for i, v in enumerate(arbol, 1)]
    for k, v in items:
        k = k[1:] if str(k).startswith("@") else k
        if isinstance(v, dict):
            lineas += _md_xml(unico(k), v, sangria + 4).splitlines()
        elif isinstance(v, list):
            if all(not isinstance(x, (dict, list)) for x in v) and not getattr(v, "_repetido", False):
                lineas.append('%s    <MDATTR name="%s" type="ascii" mode="rw">%s</MDATTR>'
                              % (s, escape(unico(k)), escape(", ".join(str(x) for x in v))))
            else:
                for i, x in enumerate(v, 1):
                    nm = unico("%s_%d" % (k, i))
                    if isinstance(x, (dict, list)):
                        lineas += _md_xml(nm, x, sangria + 4).splitlines()
                    else:
                        lineas.append('%s    <MDATTR name="%s" type="ascii" mode="rw">%s</MDATTR>'
                                      % (s, escape(nm), escape(str(x))))
        else:
            lineas.append('%s    <MDATTR name="%s" type="ascii" mode="rw">%s</MDATTR>'
                          % (s, escape(unico(k)), escape("" if v is None else str(v))))
    lineas.append("%s</MDElem>" % s)
    return "\n".join(lineas)


def _fecha_dimap(iso):
    if not iso:
        return ""
    try:
        t = _dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return ""
    meses = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    return "%02d-%s-%04d %02d:%02d:%02d.%06d" % (t.day, meses[t.month - 1], t.year,
                                                  t.hour, t.minute, t.second, t.microsecond)


def escribir_dim(p, carpeta):
    os.makedirs(carpeta, exist_ok=True)
    dim = os.path.join(carpeta, p.nombre + ".dim")
    datos = os.path.join(carpeta, p.nombre + ".data")
    if os.path.isdir(datos):
        shutil.rmtree(datos)
    os.makedirs(datos)
    t = p.transform
    if t is not None:
        # Java AffineTransform: m00, m10, m01, m11, m02, m12 (esquina del pixel)
        geo = ("    <Coordinate_Reference_System>\n        <WKT>\n%s\n        </WKT>\n"
               "    </Coordinate_Reference_System>\n    <Geoposition>\n"
               "        <IMAGE_TO_MODEL_TRANSFORM>%r,%r,%r,%r,%r,%r</IMAGE_TO_MODEL_TRANSFORM>\n"
               "    </Geoposition>" % (escape(p.crs_wkt), t.a, t.d, t.b, t.e, t.c, t.f))
        tpg_info, tpg_files = "", ""
    else:
        # GRD sin proyectar: geocodificacion por puntos de enlace (TiePointGeoCoding de SNAP)
        # mismo bloque que escribe SNAP para la geocodificacion por puntos de enlace (TiePointGeoCoding)
        geo = ("    <Coordinate_Reference_System>\n        <Horizontal_CS>\n"
               "            <HORIZONTAL_CS_TYPE>GEOGRAPHIC</HORIZONTAL_CS_TYPE>\n            <Geographic_CS>\n"
               "                <Horizontal_Datum>\n                    <HORIZONTAL_DATUM_NAME>WGS-84</HORIZONTAL_DATUM_NAME>\n"
               "                    <Ellipsoid>\n                        <ELLIPSOID_NAME>WGS-84</ELLIPSOID_NAME>\n"
               "                        <Ellipsoid_Parameters>\n"
               "                            <ELLIPSOID_MAJ_AXIS unit=\"M\">6378137.0</ELLIPSOID_MAJ_AXIS>\n"
               "                            <ELLIPSOID_MIN_AXIS unit=\"M\">6356752.3</ELLIPSOID_MIN_AXIS>\n"
               "                        </Ellipsoid_Parameters>\n                    </Ellipsoid>\n"
               "                </Horizontal_Datum>\n            </Geographic_CS>\n        </Horizontal_CS>\n"
               "    </Coordinate_Reference_System>\n    <Geoposition>\n        <Geoposition_Points>\n"
               "            <TIE_POINT_GRID_NAME_LAT>latitude</TIE_POINT_GRID_NAME_LAT>\n"
               "            <TIE_POINT_GRID_NAME_LON>longitude</TIE_POINT_GRID_NAME_LON>\n"
               "        </Geoposition_Points>\n    </Geoposition>")
        os.makedirs(os.path.join(datos, "tie_point_grids"))
        infos, files = [], []
        for k, nb in enumerate(("latitude", "longitude")):
            g = p.tie[nb].astype(">f4")
            base = os.path.join(datos, "tie_point_grids", nb)
            g.tofile(base + ".img")
            with open(base + ".hdr", "w", encoding="ascii", newline="\n") as f:
                f.write("ENVI\ndescription = {Sentinel Application Platform (SNAP) Image - %s}\n" % nb)
                f.write("samples = %d\nlines = %d\nbands = 1\nheader offset = 0\n" % (g.shape[1], g.shape[0]))
                f.write("file type = ENVI Standard\ndata type = 4\ninterleave = bsq\nbyte order = 1\n")
                f.write("band names = { %s }\n" % nb)
            infos.append("        <Tie_Point_Grid_Info>\n"
                         "            <TIE_POINT_GRID_INDEX>%d</TIE_POINT_GRID_INDEX>\n"
                         "            <TIE_POINT_DESCRIPTION>%s</TIE_POINT_DESCRIPTION>\n"
                         "            <PHYSICAL_UNIT>deg</PHYSICAL_UNIT>\n"
                         "            <TIE_POINT_GRID_NAME>%s</TIE_POINT_GRID_NAME>\n"
                         "            <DATA_TYPE>float32</DATA_TYPE>\n"
                         "            <NCOLS>%d</NCOLS>\n            <NROWS>%d</NROWS>\n"
                         "            <OFFSET_X>0.5</OFFSET_X>\n            <OFFSET_Y>0.5</OFFSET_Y>\n"
                         "            <STEP_X>%r</STEP_X>\n            <STEP_Y>%r</STEP_Y>\n"
                         "            <CYCLIC discontinuity=\"0\">false</CYCLIC>\n        </Tie_Point_Grid_Info>"
                         % (k, "Latitud" if k == 0 else "Longitud", nb, g.shape[1], g.shape[0],
                            float(p.tie["paso_x"]), float(p.tie["paso_y"])))
            files.append("        <Tie_Point_Grid_File>\n"
                         '            <TIE_POINT_GRID_FILE_PATH href="%s.data/tie_point_grids/%s.hdr" />\n'
                         "            <TIE_POINT_GRID_INDEX>%d</TIE_POINT_GRID_INDEX>\n"
                         "        </Tie_Point_Grid_File>" % (escape(p.nombre), nb, k))
        tpg_info = ("    <Tie_Point_Grids>\n        <NUM_TIE_POINT_GRIDS>2</NUM_TIE_POINT_GRIDS>\n%s\n"
                    "    </Tie_Point_Grids>" % "\n".join(infos))
        tpg_files = "\n".join(files)
    data_files, band_info = [], []
    for i, b in enumerate(p.bandas):
        arr = b["datos"]
        tipo = str(arr.dtype)
        if tipo not in _TIPOS:
            arr = arr.astype("float32")
            tipo = "float32"
        dtype_dim, envi = _TIPOS[tipo]
        base = os.path.join(datos, b["nombre"])
        arr.astype(np.dtype(tipo).newbyteorder(">")).tofile(base + ".img")
        with open(base + ".hdr", "w", encoding="ascii", newline="\n") as f:
            f.write("ENVI\n")
            f.write("description = {Sentinel Application Platform (SNAP) Image - %s}\n" % b["nombre"])
            f.write("samples = %d\nlines = %d\nbands = 1\nheader offset = 0\n" % (p.ancho, p.alto))
            f.write("file type = ENVI Standard\ndata type = %d\ninterleave = bsq\nbyte order = 1\n" % envi)
            f.write("band names = { %s }\n" % b["nombre"])
            f.write("data gain values = {%r}\ndata offset values = {%r}\n" % (b["escala"], b["desplaz"]))
        data_files.append(
            "        <Data_File>\n"
            '            <DATA_FILE_PATH href="%s.data/%s.hdr" />\n'
            "            <BAND_INDEX>%d</BAND_INDEX>\n"
            "        </Data_File>" % (escape(p.nombre), escape(b["nombre"]), i))
        nd = b["nodata"]
        band_info.append(_band_info(i, b["nombre"], b["desc"], p, dtype_dim, b["unidad"],
                                    b["escala"], b["desplaz"], nd))
    n_reales = len(p.bandas)
    for j, v in enumerate(p.virtuales):
        band_info.append(_band_info(n_reales + j, v["nombre"], v["desc"], p, "float32", v["unidad"],
                                    1.0, 0.0, float("nan"), expr=v["expr"], valida=v["valida"]))
    hoy = _dt.datetime.now().strftime("%d/%m/%Y %H:%M")
    proc = dict(p.recorte)
    proc.setdefault("programa", PROGRAMA)
    proc.setdefault("fecha_del_recorte", hoy)
    proc["fuente"] = p.cita
    md = [_md_xml("Procesamiento_del_recorte", proc, 8),
          _md_xml("Original_Product_Metadata", p.metadatos, 8)]
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Dimap_Document name="{nombre}.dim">
    <Metadata_Id>
        <METADATA_FORMAT version="2.12.1">DIMAP</METADATA_FORMAT>
        <METADATA_PROFILE>BEAM-DATAMODEL-V1</METADATA_PROFILE>
    </Metadata_Id>
    <Dataset_Id>
        <DATASET_SERIES>BEAM-PRODUCT</DATASET_SERIES>
        <DATASET_NAME>{nombre}</DATASET_NAME>
    </Dataset_Id>
    <Dataset_Use>
        <DATASET_COMMENTS>{comentario}</DATASET_COMMENTS>
    </Dataset_Use>
    <Production>
        <DATASET_PRODUCER_NAME>{programa}</DATASET_PRODUCER_NAME>
        <PRODUCT_TYPE>{tipo}</PRODUCT_TYPE>
        <PRODUCT_SCENE_RASTER_START_TIME>{t0}</PRODUCT_SCENE_RASTER_START_TIME>
        <PRODUCT_SCENE_RASTER_STOP_TIME>{t1}</PRODUCT_SCENE_RASTER_STOP_TIME>
    </Production>
{geo}
    <Raster_Dimensions>
        <NCOLS>{ancho}</NCOLS>
        <NROWS>{alto}</NROWS>
        <NBANDS>{nb}</NBANDS>
    </Raster_Dimensions>
    <Data_Access>
        <DATA_FILE_FORMAT>ENVI</DATA_FILE_FORMAT>
        <DATA_FILE_FORMAT_DESC>ENVI File Format</DATA_FILE_FORMAT_DESC>
        <DATA_FILE_ORGANISATION>BAND_SEPARATE</DATA_FILE_ORGANISATION>
{data_files}
{tpg_files}
    </Data_Access>
{tpg_info}
    <Image_Interpretation>
{band_info}
    </Image_Interpretation>
    <Dataset_Sources>
        <MDElem name="metadata">
{md}
        </MDElem>
    </Dataset_Sources>
</Dimap_Document>
""".format(nombre=escape(p.nombre), comentario=escape(p.cita), programa=PROGRAMA, tipo=escape(p.tipo),
           t0=_fecha_dimap(p.inicio), t1=_fecha_dimap(p.fin or p.inicio), geo=geo,
           tpg_files=tpg_files, tpg_info=tpg_info, ancho=p.ancho, alto=p.alto, nb=len(band_info),
           data_files="\n".join(data_files), band_info="\n".join(band_info), md="\n".join(md))
    with open(dim, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)
    ET.parse(dim)          # control: XML bien formado
    return dim


def _band_info(i, nombre, desc, p, dtype_dim, unidad, escala, desplaz, nodata, expr="", valida=""):
    nd_usado = "true" if nodata is not None else "false"
    nd = "NaN" if nodata is None or (isinstance(nodata, float) and np.isnan(nodata)) else repr(float(nodata))
    s = ("        <Spectral_Band_Info>\n"
         "            <BAND_INDEX>%d</BAND_INDEX>\n"
         "            <BAND_DESCRIPTION>%s</BAND_DESCRIPTION>\n"
         "            <BAND_NAME>%s</BAND_NAME>\n"
         "            <BAND_RASTER_WIDTH>%d</BAND_RASTER_WIDTH>\n"
         "            <BAND_RASTER_HEIGHT>%d</BAND_RASTER_HEIGHT>\n"
         "            <DATA_TYPE>%s</DATA_TYPE>\n"
         "            <PHYSICAL_UNIT>%s</PHYSICAL_UNIT>\n"
         "            <SOLAR_FLUX>0.0</SOLAR_FLUX>\n"
         "            <BAND_WAVELEN>0.0</BAND_WAVELEN>\n"
         "            <BANDWIDTH>0.0</BANDWIDTH>\n"
         "            <SCALING_FACTOR>%r</SCALING_FACTOR>\n"
         "            <SCALING_OFFSET>%r</SCALING_OFFSET>\n"
         "            <LOG10_SCALED>false</LOG10_SCALED>\n"
         "            <NO_DATA_VALUE_USED>%s</NO_DATA_VALUE_USED>\n"
         "            <NO_DATA_VALUE>%s</NO_DATA_VALUE>\n"
         % (i, escape(desc), escape(nombre), p.ancho, p.alto, dtype_dim, escape(unidad),
            float(escala), float(desplaz), nd_usado, nd))
    if valida:
        s += "            <VALID_MASK_TERM>%s</VALID_MASK_TERM>\n" % escape(valida)
    if expr:
        s += ("            <VIRTUAL_BAND>true</VIRTUAL_BAND>\n"
              "            <EXPRESSION>%s</EXPRESSION>\n" % escape(expr))
    s += "        </Spectral_Band_Info>"
    return s


def _dim_de_snap(dim):
    """True si el .dim lo escribio un lector de SNAP (tiene Abstracted_Metadata)."""
    if not os.path.exists(dim):
        return False
    with open(dim, encoding="utf-8", errors="replace") as f:
        return 'name="Abstracted_Metadata"' in f.read()


def agregar_virtuales_a_dim(dim, virtuales, md_extra=None):
    """Agrega bandas virtuales (y metadatos del recorte) a un .dim escrito por SNAP."""
    arbol = ET.parse(dim)
    raiz = arbol.getroot()
    ii = raiz.find("Image_Interpretation")
    infos = ii.findall("Spectral_Band_Info")
    existentes = {e.findtext("BAND_NAME") for e in infos}
    ancho = infos[0].findtext("BAND_RASTER_WIDTH")
    alto = infos[0].findtext("BAND_RASTER_HEIGHT")
    n = len(infos)
    for v in virtuales:
        if v["nombre"] in existentes:
            continue
        e = ET.SubElement(ii, "Spectral_Band_Info")
        for etq, val in (("BAND_INDEX", str(n)), ("BAND_DESCRIPTION", v["desc"]),
                         ("BAND_NAME", v["nombre"]), ("BAND_RASTER_WIDTH", ancho),
                         ("BAND_RASTER_HEIGHT", alto), ("DATA_TYPE", "float32"),
                         ("PHYSICAL_UNIT", v["unidad"]), ("SOLAR_FLUX", "0.0"), ("BAND_WAVELEN", "0.0"),
                         ("BANDWIDTH", "0.0"), ("SCALING_FACTOR", "1.0"), ("SCALING_OFFSET", "0.0"),
                         ("LOG10_SCALED", "false"), ("NO_DATA_VALUE_USED", "true"),
                         ("NO_DATA_VALUE", "NaN"), ("VALID_MASK_TERM", v["valida"]),
                         ("VIRTUAL_BAND", "true"), ("EXPRESSION", v["expr"])):
            if val:
                ET.SubElement(e, etq).text = val
        n += 1
    rd = raiz.find("Raster_Dimensions/NBANDS")
    if rd is not None:
        rd.text = str(n)
    if md_extra:
        meta = raiz.find("Dataset_Sources/MDElem")
        if meta is not None:
            for viejo in meta.findall("MDElem[@name='Procesamiento_del_recorte']"):
                meta.remove(viejo)
            meta.append(ET.fromstring(_md_xml("Procesamiento_del_recorte", md_extra, 0)))
    arbol.write(dim, encoding="UTF-8", xml_declaration=True)


# ---------------------------------------------------------------------------
# Escritura GeoTIFF, RGB y ficha de metadatos
# ---------------------------------------------------------------------------
def escribir_geotiff(p, carpeta, datos_dim=None):
    import rasterio
    from rasterio.control import GroundControlPoint
    from rasterio.crs import CRS

    os.makedirs(carpeta, exist_ok=True)
    tif = os.path.join(carpeta, p.nombre + ".tif")
    capas = [(b["nombre"], b["datos"], b["desc"], b["escala"], b["desplaz"], b["unidad"]) for b in p.bandas]
    virt = [(v["nombre"], v["funcion"](p), v["desc"], 1.0, 0.0, v["unidad"]) for v in p.virtuales]
    tipos = {str(c[1].dtype) for c in capas}
    # Bandas enteras (Sentinel-2): se dejan en uint16 con su escala y desplazamiento
    # (pesan la mitad que en float32) y los indices (NDVI) van en un GeoTIFF aparte.
    entero = tipos <= {"uint16", "uint8", "int16"} or tipos == {"int8"}
    if entero:
        dtype = ("int8" if tipos == {"int8"} else "uint8" if tipos == {"uint8"} else
                 "int16" if "int16" in tipos else "uint16")
        for v in virt:
            _geotiff_simple(p, os.path.join(carpeta, "%s_%s.tif" % (p.nombre, v[0])), v)
    else:
        dtype = "float32"
        capas += virt
    nd0 = p.bandas[0]["nodata"]
    nodata = (None if nd0 is None or (isinstance(nd0, float) and np.isnan(nd0)) else nd0) if entero else np.nan
    perfil = dict(driver="GTiff", width=p.ancho, height=p.alto, count=len(capas), dtype=dtype,
                  compress="deflate", predictor=2 if entero else 3, tiled=True, blockxsize=512, blockysize=512, BIGTIFF="IF_SAFER",
                  nodata=nodata)
    if p.transform is not None:
        perfil.update(crs=CRS.from_wkt(p.crs_wkt), transform=p.transform)
    with rasterio.open(tif, "w", **perfil) as dst:
        for k, (nb, arr, desc, esc, des, uni) in enumerate(capas, 1):
            a = arr.astype(dtype)
            if not entero:
                a = arr.astype("float32")
                if esc != 1.0 or des != 0.0:          # p. ej. reflectancia de Sentinel-2
                    a = a * np.float32(esc) + np.float32(des)
                a[~np.isfinite(a)] = np.nan
                bnd = [b for b in p.bandas if b["nombre"] == nb]
                if bnd and bnd[0]["nodata"] is not None and not np.isnan(bnd[0]["nodata"]) \
                        and bnd[0]["nombre"] != "mask":
                    a[arr == bnd[0]["nodata"]] = np.nan
            dst.write(a, k)
            dst.set_band_description(k, nb)
            if esc != 1.0 or des != 0.0:
                desc += (" [en este GeoTIFF ya convertido: valor = DN x %g + %g]" % (esc, des) if not entero else
                         " [GeoTIFF en DN con escala %g y desplazamiento %g: QGIS los aplica]" % (esc, des))
            dst.update_tags(k, DESCRIPCION=desc, UNIDAD=uni)
        if entero:
            dst.scales = tuple(c[3] for c in capas)
            dst.offsets = tuple(c[4] for c in capas)
        if p.gcps:
            gc = [GroundControlPoint(row=f, col=c, x=lon, y=lat, z=z) for f, c, lon, lat, z in p.gcps]
            dst.gcps = (gc, CRS.from_epsg(4326))
        etiquetas = {"FUENTE": p.cita, "PROGRAMA": PROGRAMA, "TIPO_PRODUCTO": p.tipo,
                     "FECHA_INICIO": p.inicio, "FECHA_FIN": p.fin or p.inicio,
                     "METADATOS_COMPLETOS": p.nombre + "_metadatos.txt (en esta carpeta)"}
        for k, v in p.recorte.items():
            etiquetas["RECORTE_" + _nombre_valido(k).upper()] = str(v)
        for k, v in aplanar(p.metadatos)[:400]:
            clave = _nombre_valido(k.replace("/", "__"))[:120]
            etiquetas["ORIG__" + clave] = v[:800]
        dst.update_tags(**etiquetas)
    escribir_ficha(p, os.path.join(carpeta, p.nombre + "_metadatos.txt"), capas + (virt if entero else []))
    if getattr(p, "leyenda", None):
        escribir_qml(os.path.join(carpeta, p.nombre + ".qml"), p.leyenda, len(capas))
    return tif


def escribir_qml(ruta, leyenda, banda):
    """Estilo de QGIS (valores unicos con los colores oficiales); QGIS lo carga solo
    porque tiene el mismo nombre que el GeoTIFF. Muestra la ultima banda (el ultimo anio)."""
    entradas = "\n".join('        <paletteEntry value="%s" label="%s" color="%s" alpha="255"/>'
                         % (k, escape("%s %s" % (k, v[0])), v[1]) for k, v in sorted(leyenda.items()))
    with open(ruta, "w", encoding="utf-8") as f:
        f.write('<!DOCTYPE qgis PUBLIC \'http://mrcc.com/qgis.dtd\' \'SYSTEM\'>\n'
                '<qgis version="3.44" styleCategories="Symbology">\n  <pipe>\n'
                '    <rasterrenderer type="paletted" band="%d" opacity="1" alphaBand="-1" nodataColor="">\n'
                '      <colorPalette>\n%s\n      </colorPalette>\n'
                '    </rasterrenderer>\n  </pipe>\n</qgis>\n' % (banda, entradas))


def _geotiff_simple(p, ruta, capa):
    import rasterio
    from rasterio.crs import CRS

    from rasterio.control import GroundControlPoint

    nb, arr, desc, _, _, uni = capa
    geo = dict(crs=CRS.from_wkt(p.crs_wkt), transform=p.transform) if p.transform is not None else {}
    with rasterio.open(ruta, "w", driver="GTiff", width=p.ancho, height=p.alto, count=1, dtype="float32",
                       nodata=np.nan, compress="deflate", predictor=3, tiled=True, blockxsize=512,
                       blockysize=512, **geo) as d:
        d.write(arr.astype("float32"), 1)
        if p.gcps:
            d.gcps = ([GroundControlPoint(row=f, col=c, x=lon, y=lat, z=z) for f, c, lon, lat, z in p.gcps],
                      CRS.from_epsg(4326))
        d.set_band_description(1, nb)
        d.update_tags(1, DESCRIPCION=desc, UNIDAD=uni)
        d.update_tags(FUENTE=p.cita, PROGRAMA=PROGRAMA, FECHA_INICIO=p.inicio,
                      METADATOS_COMPLETOS=p.nombre + "_metadatos.txt (en esta carpeta)")


def escribir_ficha(p, ruta, capas):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("%s\n%s\n\n" % (p.nombre, "=" * len(p.nombre)))
        f.write("Fuente: %s\n" % p.cita)
        f.write("Tipo de producto: %s\n" % p.tipo)
        f.write("Adquisicion: %s%s\n\n" % (p.inicio, (" a " + p.fin) if p.fin and p.fin != p.inicio else ""))
        f.write("RECORTE\n")
        for k, v in p.recorte.items():
            f.write("  %s: %s\n" % (k, v))
        f.write("  programa: %s\n\n" % PROGRAMA)
        f.write("BANDAS DEL GEOTIFF\n")
        for k, c in enumerate(capas, 1):
            f.write("  %2d  %-28s %-12s %s\n" % (k, c[0], c[5], c[2]))
        f.write("\nMETADATOS ORIGINALES DEL PROVEEDOR (completos)\n")
        for k, v in aplanar(p.metadatos):
            f.write("  %s = %s\n" % (k, v))


def escribir_rgb(p, carpeta):
    import rasterio
    from rasterio.crs import CRS

    if not p.rgb:
        return None
    co_db, cruz_db, coc_db, pol_co, pol_cruz = p.rgb
    funcs = {v["nombre"]: v["funcion"] for v in p.virtuales}
    capas = [funcs[co_db](p), funcs[cruz_db](p), funcs[coc_db](p)]
    os.makedirs(carpeta, exist_ok=True)
    base = os.path.join(carpeta, p.nombre)
    perfil = dict(driver="GTiff", width=p.ancho, height=p.alto, count=3, compress="deflate", tiled=True,
                  blockxsize=512, blockysize=512, BIGTIFF="IF_SAFER")
    if p.transform is not None:
        perfil.update(crs=CRS.from_wkt(p.crs_wkt), transform=p.transform)
    nombres = ["R_%s_db" % pol_co, "G_%s_db" % pol_cruz, "B_%s_%s_cociente_db" % (pol_co, pol_cruz)]
    gcps = None
    if p.transform is None and p.gcps:
        from rasterio.control import GroundControlPoint
        gcps = ([GroundControlPoint(row=f, col=c, x=lon, y=lat, z=z) for f, c, lon, lat, z in p.gcps],
                CRS.from_epsg(4326))
    with rasterio.open(base + "_RGB_dB.tif", "w", dtype="float32", nodata=np.nan, **perfil) as d:
        for k, (a, n) in enumerate(zip(capas, nombres), 1):
            d.write(a.astype("float32"), k)
            d.set_band_description(k, n)
        if gcps:
            d.gcps = gcps
        d.update_tags(FUENTE=p.cita, COMPOSICION="R=%s G=%s B=%s/%s, todo en dB" % (pol_co, pol_cruz, pol_co, pol_cruz))
    if "BIOMASS_P" in p.nombre:
        # Banda P (decision del 22/10/2026): promedio 5 x 5 en lineal y estiramiento 2-98 % por escena.
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "09_Herramientas"))
        import rgb_bandaP_realce
        rgb_bandaP_realce.rehacer(base + "_RGB_dB.tif")
        return base + "_RGB_dB.tif"
    rangos = [RANGOS_RGB["co"], RANGOS_RGB["cruz"], RANGOS_RGB["cociente"]]
    with rasterio.open(base + "_RGB_8bit.tif", "w", dtype="uint8", nodata=0, photometric="RGB", **perfil) as d:
        for k, (a, (lo, hi)) in enumerate(zip(capas, rangos), 1):
            b = np.clip((a - lo) / (hi - lo), 0, 1) * 254 + 1
            b = np.where(np.isfinite(a), b, 0).astype("uint8")
            d.write(b, k)
            d.set_band_description(k, nombres[k - 1])
        if gcps:
            d.gcps = gcps
        d.update_tags(FUENTE=p.cita,
                      RANGOS_FIJOS_DB="R %s a %s; G %s a %s; B %s a %s" % (rangos[0] + rangos[1] + rangos[2]),
                      NOTA="Rangos fijos para comparar fechas y sensores con la misma escala")
    return base + "_RGB_dB.tif"


def copiar_meta(p, carpeta):
    if not p.archivos_meta:
        return
    dest = os.path.join(carpeta, p.nombre)
    os.makedirs(dest, exist_ok=True)
    for a in p.archivos_meta:
        if os.path.isfile(a):
            shutil.copy2(a, os.path.join(dest, os.path.basename(os.path.dirname(a)) + "__" + os.path.basename(a)
                                         if sum(os.path.basename(x) == os.path.basename(a) for x in p.archivos_meta) > 1
                                         else os.path.basename(a)))


# ---------------------------------------------------------------------------
# Recortes
# ---------------------------------------------------------------------------
def caja_nativa(sitio, crs):
    from rasterio.warp import transform_bounds
    return transform_bounds("EPSG:4326", crs, *SITIOS[sitio]["bbox"], densify_pts=21)


def recortar(ruta, sitio, banda=1):
    import rasterio
    from rasterio.windows import from_bounds, Window

    with rasterio.open(ruta) as src:
        caja = caja_nativa(sitio, src.crs)
        w = from_bounds(*caja, transform=src.transform).round_offsets().round_lengths()
        w = w.intersection(Window(0, 0, src.width, src.height))
        return src.read(banda, window=w), src.window_transform(w), src.crs, src.nodata


def mosaico(rutas, sitio, resolucion=None, remuestreo="nearest", nodata_forzado=None):
    """Une recortes de la misma fecha (teselas) en la grilla nativa comun."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.transform import from_origin
    from rasterio.warp import reproject

    # Si las teselas vienen en dos husos UTM (p. ej. 20HQJ y 21HTD), manda el huso del sitio
    # y las demas se reproyectan por vecino mas proximo (se declara en la nota del producto).
    o, s_, e, n = SITIOS[sitio]["bbox"]
    huso = int(((o + e) / 2 + 180) // 6) + 1
    epsg_sitio = (32700 if (s_ + n) / 2 < 0 else 32600) + huso

    def _prioridad(r):
        with rasterio.open(r) as x:
            return 0 if (x.crs and x.crs.to_epsg() == epsg_sitio) else 1
    rutas = sorted(rutas, key=_prioridad)
    with rasterio.open(rutas[0]) as s0:
        crs = s0.crs
        res = resolucion or s0.res[0]
        dtype = s0.dtypes[0]
        nodata = s0.nodata if nodata_forzado is None else nodata_forzado
    caja = caja_nativa(sitio, crs)
    x0 = np.floor(caja[0] / res) * res
    y1 = np.ceil(caja[3] / res) * res
    ancho = int(np.ceil((caja[2] - x0) / res))
    alto = int(np.ceil((y1 - caja[1]) / res))
    tr = from_origin(x0, y1, res, res)
    rell = nodata if nodata is not None else 0
    out = np.full((alto, ancho), rell, dtype=dtype)
    for r in rutas:
        with rasterio.open(r) as s:
            tmp = np.full((alto, ancho), rell, dtype=dtype)
            reproject(s.read(1), tmp, src_transform=s.transform, src_crs=s.crs, dst_transform=tr,
                      dst_crs=crs, resampling=getattr(Resampling, remuestreo),
                      src_nodata=rell, dst_nodata=rell)
            vacio = (out == rell) | (np.isnan(out) if out.dtype.kind == "f" else False)
            out = np.where(vacio & (tmp != rell), tmp, out)
    return out, tr, crs, nodata


def _wkt(crs):
    from pyproj import CRS as PCRS
    return PCRS.from_user_input(crs.to_wkt() if hasattr(crs, "to_wkt") else crs).to_wkt("WKT1_GDAL", pretty=True)


def _doc_recorte(sitio, extra=""):
    b = SITIOS[sitio]["bbox"]
    d = {"sitio": sitio, "nombre_del_sitio": SITIOS[sitio].get("nombre", ""),
         "caja_WGS84_oeste_sur_este_norte": "%.4f, %.4f, %.4f, %.4f" % b,
         "pixel_y_proyeccion": "nativos del producto (sin remuestrear)"}
    if extra:
        d["nota"] = extra
    return d


# ---------------------------------------------------------------------------
# Lectores por tipo de producto
# ---------------------------------------------------------------------------
def leer_nisar_gcov(sitio, cfg, nombre):
    import h5py
    from rasterio.transform import from_origin

    rutas = sorted(glob.glob(os.path.join(ORIGINALES, cfg["patron"])))
    if not rutas:
        raise Falta("No hay NISAR GCOV con el patron %s" % cfg["patron"])
    banda = cfg.get("banda", "LSAR")
    base = "/science/%s/GCOV/grids/frequencyA/" % banda
    elegido = None
    for ruta in rutas:
        with h5py.File(ruta, "r") as h:
            x = h[base + "xCoordinates"][:]
            y = h[base + "yCoordinates"][:]
            proy = h[base + "projection"]
            epsg = int(np.array(proy[()]).ravel()[0])
            if epsg < 1000 and "epsg_code" in proy.attrs:
                epsg = int(np.array(proy.attrs["epsg_code"]).ravel()[0])
            cx0, cy0, cx1, cy1 = caja_nativa(sitio, "EPSG:%d" % epsg)
            if cx1 < x.min() or cx0 > x.max() or cy1 < y.min() or cy0 > y.max():
                continue
            dx, dy = float(x[1] - x[0]), float(y[1] - y[0])
            c0 = max(int(np.searchsorted(x, cx0)), 0)
            c1 = min(int(np.searchsorted(x, cx1)), x.size)
            f0 = max(int(np.searchsorted(-y, -cy1)), 0) if dy < 0 else max(int(np.searchsorted(y, cy0)), 0)
            f1 = min(int(np.searchsorted(-y, -cy0)), y.size) if dy < 0 else min(int(np.searchsorted(y, cy1)), y.size)
            terminos = [t for t in ("HHHH", "HVHV", "VVVV", "VHVH") if (base + t) in h]
            capas = {t: h[base + t][f0:f1, c0:c1].astype("float32") for t in terminos}
            mascara = h[base + "mask"][f0:f1, c0:c1] if (base + "mask") in h else None
            extra = {}
            for nm in ("numberOfLooks", "rtcGammaToSigmaFactor"):
                if (base + nm) in h and h[base + nm].ndim == 2:
                    extra[nm] = h[base + nm][f0:f1, c0:c1].astype("float32")
            t0 = h["/science/%s/identification/zeroDopplerStartTime" % banda][()] \
                if "/science/%s/identification/zeroDopplerStartTime" % banda in h else b""
            t1 = h["/science/%s/identification/zeroDopplerEndTime" % banda][()] \
                if "/science/%s/identification/zeroDopplerEndTime" % banda in h else b""
            elegido = (ruta, epsg, x, y, dx, dy, c0, f0, capas, mascara, extra, t0, t1)
            break
    if elegido is None:
        raise Falta("Ningun NISAR GCOV %s cubre %s" % (cfg["patron"], sitio))
    ruta, epsg, x, y, dx, dy, c0, f0, capas, mascara, extra, t0, t1 = elegido
    if mascara is not None:
        invalido = (mascara == 0) | (mascara == 255)
    else:
        invalido = np.zeros(next(iter(capas.values())).shape, bool)
    p = Producto(nombre)
    p.crs_wkt = _wkt("EPSG:%d" % epsg)
    p.transform = from_origin(float(x[c0]) - dx / 2.0, float(y[f0]) - dy / 2.0, abs(dx), abs(dy))
    nombres = {"HHHH": ("Gamma0_HH", "HH"), "HVHV": ("Gamma0_HV", "HV"),
               "VVVV": ("Gamma0_VV", "VV"), "VHVH": ("Gamma0_VH", "VH")}
    for t, a in capas.items():
        a[invalido | ~np.isfinite(a) | (a <= 0)] = 0.0
        nb, pol = nombres[t]
        p.banda(nb, a, "intensity", "gamma0 %s LINEAL (termino %s de la matriz de covarianza GCOV, "
                "frecuencia A, con la mascara del producto aplicada)" % (pol, t))
    if mascara is not None:
        p.banda("mask", mascara.astype("uint8"), "", "Mascara del producto: 1..n subfranja valida; "
                "0 parcialmente enfocada o invalida; 255 fuera de la adquisicion", nodata=None)
    for nm, a in extra.items():
        a[~np.isfinite(a)] = 0.0
        p.banda(nm, a, "", {"numberOfLooks": "Numero de looks de cada pixel",
                            "rtcGammaToSigmaFactor": "Factor gamma0 -> sigma0 (sigma0 = gamma0 x factor)"}[nm])
    if "Gamma0_HV" in [b["nombre"] for b in p.bandas]:
        agregar_db_y_cociente(p, "Gamma0_HH", "Gamma0_HV", "HH", "HV", "gamma0")
    else:
        agregar_db_y_cociente(p, "Gamma0_VV" if "VVVV" in capas else "Gamma0_HH",
                              "Gamma0_VH" if "VHVH" in capas else None,
                              "VV" if "VVVV" in capas else "HH", "VH", "gamma0")
    dec = lambda v: v.decode() if isinstance(v, bytes) else str(v)     # noqa: E731
    p.inicio, p.fin = dec(t0)[:26], dec(t1)[:26]
    p.tipo = "NISAR_L2_GCOV_%s" % banda
    org = "NASA-ISRO" if banda == "LSAR" else "ISRO-NASA"
    p.cita = ("%s. NISAR L2 GCOV, banda %s (frecuencia A), %s. Archivo %s. %s"
              % (org, "L" if banda == "LSAR" else "S", p.inicio[:10], os.path.basename(ruta),
                 "ASF DAAC: https://search.asf.alaska.edu" if banda == "LSAR"
                 else "ISRO Bhoonidhi: https://bhoonidhi.nrsc.gov.in"))
    p.metadatos = h5_a_arbol(ruta, ["/science/%s/identification" % banda,
                                    "/science/%s/GCOV/metadata" % banda,
                                    "/science/%s/GCOV/grids/frequencyA" % banda])
    p.recorte = _doc_recorte(sitio, "Solo frecuencia A (la B, de 80 m, no se usa). Muestras con mascara 0 "
                             "o 255 puestas en 0 (sin dato). EPSG:%d, pixel %g m." % (epsg, abs(dx)))
    p.recorte["archivo_original"] = ruta
    return p


def leer_s1_rtc(sitio, cfg, nombre):
    carp = sorted(glob.glob(os.path.join(ORIGINALES, "PLANETARY", sitio, "sentinel-1-rtc", cfg["fecha"] + "_*")))
    carp = [c for c in carp if os.path.exists(os.path.join(c, ".completo"))]
    if not carp:
        raise Falta("No hay Sentinel-1 RTC del %s en PLANETARY\\%s" % (cfg["fecha"], sitio))
    pols = [x for x in ("vv", "vh", "hh", "hv") if os.path.exists(os.path.join(carp[0], x + ".tif"))]
    p = Producto(nombre)
    for pol in pols:
        arr, tr, crs, nd = mosaico([os.path.join(c, pol + ".tif") for c in carp
                                    if os.path.exists(os.path.join(c, pol + ".tif"))], sitio)
        arr = arr.astype("float32")
        arr[(arr == (nd if nd is not None else -32768)) | ~np.isfinite(arr) | (arr <= 0)] = 0.0
        p.banda("Gamma0_" + pol.upper(), arr, "intensity",
                "gamma0 %s LINEAL, corregido por terreno (RTC de Planetary Computer)" % pol.upper())
    p.transform, p.crs_wkt = tr, _wkt(crs)
    nb = [b["nombre"] for b in p.bandas]
    if "Gamma0_VH" in nb:
        agregar_db_y_cociente(p, "Gamma0_VV", "Gamma0_VH", "VV", "VH", "gamma0")
    elif "Gamma0_HV" in nb:
        agregar_db_y_cociente(p, "Gamma0_HH", "Gamma0_HV", "HH", "HV", "gamma0")
    stacs = [os.path.join(c, "item_STAC.json") for c in carp]
    p.metadatos = {("item_%d" % i if len(stacs) > 1 else "item_STAC"): json_a_arbol(s)
                   for i, s in enumerate(stacs, 1)}
    pr = p.metadatos[next(iter(p.metadatos))]["properties"]
    p.inicio, p.fin = pr.get("start_datetime", pr.get("datetime", "")), pr.get("end_datetime", "")
    p.tipo = "S1_IW_GRDH_RTC"
    p.cita = ("ESA Copernicus / Microsoft Planetary Computer. Sentinel-1 %s IW GRDH RTC (gamma0), %s, orbita "
              "relativa %s, %s. https://planetarycomputer.microsoft.com/dataset/sentinel-1-rtc"
              % (pr.get("platform", "").upper().replace("SENTINEL-", ""), p.inicio[:10],
                 pr.get("sat:relative_orbit", ""), pr.get("sat:orbit_state", "")))
    p.archivos_meta = stacs
    p.recorte = _doc_recorte(sitio)
    p.recorte["carpetas_originales"] = "; ".join(carp)
    return p


def leer_alos2_mosaico(sitio, cfg, nombre):
    carp = sorted(glob.glob(os.path.join(ORIGINALES, "PLANETARY", sitio, "alos-palsar-mosaic", cfg["anio"] + "*")))
    carp = [c for c in carp if os.path.exists(os.path.join(c, ".completo"))]
    if not carp:
        raise Falta("No hay mosaico ALOS-2 %s en PLANETARY\\%s\\alos-palsar-mosaic" % (cfg["anio"], sitio))
    p = Producto(nombre)
    for pol in ("HH", "HV"):
        rs = [os.path.join(c, pol + ".tif") for c in carp if os.path.exists(os.path.join(c, pol + ".tif"))]
        if not rs:
            continue
        dn, tr, crs, nd = mosaico(rs, sitio)
        p.banda(pol + "_DN", dn.astype("uint16"), "dl", "Numero digital original del mosaico JAXA (%s)" % pol)
        g = dn.astype("float64") ** 2 * 10 ** (-8.3)
        g = g.astype("float32")
        g[dn == 0] = 0.0
        p.banda("Gamma0_" + pol, g, "intensity",
                "gamma0 %s LINEAL = DN^2 x 10^(-8,3) (conversion publicada por JAXA: 10log10(DN^2) - 83 dB)" % pol)
    p.transform, p.crs_wkt = tr, _wkt(crs)
    agregar_db_y_cociente(p, "Gamma0_HH", "Gamma0_HV", "HH", "HV", "gamma0")
    stacs = [os.path.join(c, "item_STAC.json") for c in carp]
    p.metadatos = {"item_%d" % i: json_a_arbol(s) for i, s in enumerate(stacs, 1)}
    p.inicio = "%s-01-01T00:00:00" % cfg["anio"]
    p.fin = "%s-12-31T23:59:59" % cfg["anio"]
    p.tipo = "ALOS2_PALSAR2_MOSAICO_ANUAL"
    p.cita = ("JAXA / Microsoft Planetary Computer. ALOS-2 PALSAR-2 mosaico anual global 25 m, %s (HH, HV). "
              "https://planetarycomputer.microsoft.com/dataset/alos-palsar-mosaic" % cfg["anio"])
    p.archivos_meta = stacs
    p.recorte = _doc_recorte(sitio, "Mosaico anual: cada pixel puede venir de una fecha distinta del anio "
                             "(ver la capa de fechas del producto en el catalogo).")
    return p


def leer_s2_l2a(sitio, cfg, nombre):
    import rasterio

    carp = sorted(glob.glob(os.path.join(ORIGINALES, "PLANETARY", sitio, "sentinel-2-l2a", cfg["fecha"] + "_*")))
    carp = [c for c in carp if os.path.exists(os.path.join(c, ".completo"))]
    if not carp:
        raise Falta("No hay Sentinel-2 L2A del %s en PLANETARY\\%s" % (cfg["fecha"], sitio))
    # desplazamiento y cuantificacion del producto (L2A, linea de base >= 04.00: -1000 y 10000)
    q, desp = 10000.0, {}
    pm = os.path.join(carp[0], "product-metadata.xml")
    if os.path.exists(pm):
        tx = open(pm, encoding="utf-8", errors="replace").read()
        m = re.search(r"<BOA_QUANTIFICATION_VALUE[^>]*>([\d.]+)<", tx)
        if m:
            q = float(m.group(1))
        for bid, v in re.findall(r'<BOA_ADD_OFFSET band_id="(\d+)">(-?[\d.]+)<', tx):
            desp[int(bid)] = float(v)
    ids = {"B01": 0, "B02": 1, "B03": 2, "B04": 3, "B05": 4, "B06": 5, "B07": 6, "B08": 7, "B8A": 8,
           "B09": 9, "B10": 10, "B11": 11, "B12": 12}
    longitudes = {"B02": 490, "B03": 560, "B04": 665, "B05": 705, "B06": 740, "B07": 783, "B08": 842,
                  "B8A": 865, "B11": 1610, "B12": 2190}
    p = Producto(nombre)
    tr = crs = None
    for b in ("B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12", "SCL"):
        rs = [os.path.join(c, b + ".tif") for c in carp if os.path.exists(os.path.join(c, b + ".tif"))]
        if not rs:
            continue
        with rasterio.open(rs[0]) as s:
            res_nat = s.res[0]
        arr, tr, crs, _ = mosaico(rs, sitio, resolucion=10.0, remuestreo="nearest")
        if b == "SCL":
            p.banda("SCL", arr.astype("uint8"), "", "Clasificacion de escena de ESA (20 m llevado a 10 m por "
                    "vecino mas proximo)", nodata=0)
        else:
            nota = "" if res_nat == 10 else " (%g m llevado a 10 m por vecino mas proximo)" % res_nat
            p.banda(b, arr.astype("uint16"), "reflectance",
                    "Reflectancia de superficie %s, %d nm%s. Reflectancia = (DN + %g) / %g"
                    % (b, longitudes[b], nota, desp.get(ids[b], 0.0), q),
                    nodata=0, escala=1.0 / q, desplaz=desp.get(ids[b], 0.0) / q)
    p.transform, p.crs_wkt = tr, _wkt(crs)
    nb = [b["nombre"] for b in p.bandas]
    if "B04" in nb and "B08" in nb:
        def ndvi(pr):
            r = pr.datos("B04").astype("float32")
            n = pr.datos("B08").astype("float32")
            br = [b for b in pr.bandas if b["nombre"] == "B04"][0]
            bn = [b for b in pr.bandas if b["nombre"] == "B08"][0]
            rr = r * br["escala"] + br["desplaz"]
            nn = n * bn["escala"] + bn["desplaz"]
            out = np.full(r.shape, np.nan, "float32")
            ok = (r > 0) & (n > 0) & ((nn + rr) != 0)
            out[ok] = (nn[ok] - rr[ok]) / (nn[ok] + rr[ok])
            return out
        p.virtual("NDVI", "(B08 + B04) != 0 ? (B08 - B04) / (B08 + B04) : NaN", ndvi, "",
                  "NDVI = (B08 - B04) / (B08 + B04) con reflectancias (banda virtual)", "B04 > 0 && B08 > 0")
    md = {}
    for c in carp:
        tesela = re.search(r"_T(\d{2}[A-Z]{3})_", os.path.basename(c))
        t = tesela.group(1) if tesela else os.path.basename(c)
        dd = {}
        for x in ("product-metadata", "granule-metadata", "inspire-metadata"):
            r = os.path.join(c, x + ".xml")
            if os.path.exists(r):
                dd[x.replace("-", "_")] = xml_a_arbol(r)
                p.archivos_meta.append(r)
        r = os.path.join(c, "datastrip-metadata.xml")
        if os.path.exists(r):
            p.archivos_meta.append(r)
            dd["datastrip_metadata"] = "copiado sin tocar en Metadatos_originales (pesa mucho para el .dim)"
        r = os.path.join(c, "item_STAC.json")
        if os.path.exists(r):
            dd["item_STAC"] = json_a_arbol(r)
            p.archivos_meta.append(r)
        md["tesela_" + t] = dd
    p.metadatos = md
    stac = next((v["item_STAC"] for v in md.values() if "item_STAC" in v), {})
    pr = stac.get("properties", {})
    p.inicio = pr.get("datetime", cfg["fecha"])
    p.tipo = "S2_MSI_L2A"
    p.cita = ("ESA Copernicus / Microsoft Planetary Computer. Sentinel-2%s MSI L2A, %s, teselas %s. "
              "https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a"
              % (pr.get("platform", "").upper().replace("SENTINEL-2", ""), p.inicio[:10],
                 ", ".join(k.replace("tesela_", "") for k in md)))
    p.recorte = _doc_recorte(sitio, "Mosaico de las teselas del mismo dia. Bandas de 20 m llevadas a 10 m "
                             "por vecino mas proximo. Si hay teselas de otro huso UTM, se reproyectan al huso "
                             "del sitio por vecino mas proximo.")
    return p


def leer_landsat_l2(sitio, cfg, nombre):
    r = _landsat_elegida(sitio, cfg["fecha_s2"])
    if r is None:
        raise Falta("No hay Landsat elegido para el Sentinel-2 del %s: correr datos_crudos.py landsat --confirmar"
                    % cfg["fecha_s2"])
    if not r["fecha_landsat"]:
        raise Falta("No se usa Landsat para esta fecha: %s" % r["ids"])
    carp = [os.path.join(ORIGINALES, "PLANETARY", sitio, "landsat-c2-l2", "%s_%s" % (r["fecha_landsat"], i))
            for i in r["ids"].split()]
    carp = [c for c in carp if os.path.exists(os.path.join(c, ".completo"))]
    if not carp:
        raise Falta("Landsat %s del %s elegido pero no bajado (datos_crudos.py landsat --confirmar)"
                    % (r["plataforma"], r["fecha_landsat"]))
    # factores de escala del MTL de USGS (Coleccion 2 Nivel 2); si falta, los publicados por USGS
    mult_sr, add_sr, mult_st, add_st = 2.75e-05, -0.2, 0.00341802, 149.0
    mtl = (glob.glob(os.path.join(carp[0], "*_MTL.json")) or [None])[0]
    mtx = (glob.glob(os.path.join(carp[0], "*_MTL.xml")) or [None])[0]
    if not mtl and mtx:
        tx = open(mtx, encoding="utf-8", errors="replace").read()
        for clave, var in (("REFLECTANCE_MULT_BAND_4", "mult_sr"), ("REFLECTANCE_ADD_BAND_4", "add_sr"),
                           ("TEMPERATURE_MULT_BAND_ST_B10", "mult_st"), ("TEMPERATURE_ADD_BAND_ST_B10", "add_st")):
            m = re.search(r"<%s>\s*(-?[\d.Ee+-]+)\s*<" % clave, tx)
            if m:
                if var == "mult_sr":
                    mult_sr = float(m.group(1))
                elif var == "add_sr":
                    add_sr = float(m.group(1))
                elif var == "mult_st":
                    mult_st = float(m.group(1))
                else:
                    add_st = float(m.group(1))
    if mtl:
        try:
            js = json.load(open(mtl, encoding="utf-8"))
            res = js["LANDSAT_METADATA_FILE"]
            ref = res.get("LEVEL2_SURFACE_REFLECTANCE_PARAMETERS", {})
            tem = res.get("LEVEL2_SURFACE_TEMPERATURE_PARAMETERS", {})
            mult_sr = float(ref.get("REFLECTANCE_MULT_BAND_4", mult_sr))
            add_sr = float(ref.get("REFLECTANCE_ADD_BAND_4", add_sr))
            mult_st = float(tem.get("TEMPERATURE_MULT_BAND_ST_B10", mult_st))
            add_st = float(tem.get("TEMPERATURE_ADD_BAND_ST_B10", add_st))
        except Exception:                                    # noqa: BLE001
            pass
    bandas = [("SR_B1", "reflectance", "Reflectancia de superficie, banda 1 costera/aerosoles (443 nm)", mult_sr, add_sr, 0),
              ("SR_B2", "reflectance", "Reflectancia de superficie, banda 2 azul (482 nm)", mult_sr, add_sr, 0),
              ("SR_B3", "reflectance", "Reflectancia de superficie, banda 3 verde (561 nm)", mult_sr, add_sr, 0),
              ("SR_B4", "reflectance", "Reflectancia de superficie, banda 4 roja (655 nm)", mult_sr, add_sr, 0),
              ("SR_B5", "reflectance", "Reflectancia de superficie, banda 5 infrarrojo cercano (865 nm)", mult_sr, add_sr, 0),
              ("SR_B6", "reflectance", "Reflectancia de superficie, banda 6 SWIR 1 (1609 nm)", mult_sr, add_sr, 0),
              ("SR_B7", "reflectance", "Reflectancia de superficie, banda 7 SWIR 2 (2201 nm)", mult_sr, add_sr, 0),
              ("ST_B10", "K", "Temperatura de superficie, banda 10 TIRS (10,9 um; adquirida a 100 m y "
               "entregada por USGS a 30 m)", mult_st, add_st, 0),
              ("ST_QA", "K", "Incertidumbre de la temperatura de superficie", 0.01, 0.0, -9999),
              ("QA_PIXEL", "", "Calidad del pixel (bits: 0 relleno, 1 nube dilatada, 2 cirro, 3 nube, "
               "4 sombra de nube, 5 nieve, 6 despejado, 7 agua)", 1.0, 0.0, 1)]
    p = Producto(nombre)
    tr = crs = None
    for b, uni, desc, esc, des, nd in bandas:
        rs = [x for c in carp for x in glob.glob(os.path.join(c, "*_%s.TIF" % b))]
        if not rs:
            continue
        # relleno de USGS: 0 en SR y ST, -9999 en ST_QA, 1 (bit 0) en QA_PIXEL. Se fuerza, porque el
        # recorte no siempre trae el valor de relleno declarado y el cuadro WRS vecino taparia al bueno.
        arr, tr, crs, _ = mosaico(rs, sitio, resolucion=30.0, remuestreo="nearest", nodata_forzado=nd)
        if b == "ST_QA":            # a uint16 como las demas (el GeoTIFF lleva un solo tipo): relleno -9999 -> 0
            arr = np.where(arr == -9999, 0, arr).astype("uint16")
            nd = 0
        txt = "%s. Valor = DN x %g + %g" % (desc, esc, des) if (esc != 1.0 or des != 0.0) else desc
        p.banda(b, arr, uni, txt, nodata=nd, escala=esc, desplaz=des)
    if not p.bandas:
        raise Falta("La carpeta Landsat no tiene bandas: %s" % carp[0])
    p.transform, p.crs_wkt = tr, _wkt(crs)
    nb = [b["nombre"] for b in p.bandas]

    def _fis(pr, n):
        x = pr.datos(n).astype("float32")
        bb = [b for b in pr.bandas if b["nombre"] == n][0]
        return x * bb["escala"] + bb["desplaz"], x > 0
    if "SR_B4" in nb and "SR_B5" in nb:
        def ndvi(pr):
            rr, ok1 = _fis(pr, "SR_B4")
            nn, ok2 = _fis(pr, "SR_B5")
            out = np.full(rr.shape, np.nan, "float32")
            ok = ok1 & ok2 & ((nn + rr) != 0)
            out[ok] = (nn[ok] - rr[ok]) / (nn[ok] + rr[ok])
            return out
        p.virtual("NDVI", "(SR_B5 + SR_B4) != 0 ? (SR_B5 - SR_B4) / (SR_B5 + SR_B4) : NaN", ndvi, "",
                  "NDVI = (SR_B5 - SR_B4) / (SR_B5 + SR_B4) con reflectancias (banda virtual)",
                  "SR_B4.raw > 0 && SR_B5.raw > 0")
    if "ST_B10" in nb:
        def st_c(pr):
            t, ok = _fis(pr, "ST_B10")
            return np.where(ok, t - 273.15, np.nan).astype("float32")
        p.virtual("ST_B10_C", "ST_B10 - 273.15", st_c, "Celsius",
                  "Temperatura de superficie en grados Celsius (banda virtual)", "ST_B10.raw > 0")
    md = {}
    for c in carp:
        dd = {}
        x = (glob.glob(os.path.join(c, "*_MTL.xml")) or [None])[0]
        if x:
            dd["MTL"] = xml_a_arbol(x)
        x = os.path.join(c, "item_STAC.json")
        if os.path.exists(x):
            dd["item_STAC"] = json_a_arbol(x)
        for patron in ("*_MTL.xml", "*_MTL.txt", "*_MTL.json", "*_ANG.txt", "item_STAC.json"):
            p.archivos_meta += glob.glob(os.path.join(c, patron))
        md[os.path.basename(c)[9:]] = dd
    p.metadatos = md
    sat = r["plataforma"].replace("landsat-", "Landsat ")
    stac = next((v["item_STAC"] for v in md.values() if "item_STAC" in v), {})
    p.inicio = stac.get("properties", {}).get("datetime", r["fecha_landsat"])
    p.tipo = "LANDSAT_OLI_TIRS_C2_L2"
    p.cita = ("USGS / NASA. %s OLI/TIRS, Coleccion 2 Nivel 2 (reflectancia y temperatura de superficie), %s, "
              "%s. Microsoft Planetary Computer, https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2"
              % (sat, p.inicio[:10], ", ".join(r["ids"].split())))
    p.recorte = _doc_recorte(sitio, "Pasada %s mas cercana al Sentinel-2 del %s (%s dias; sitio %s %% con dato y "
                             "%s %% despejado segun QA_PIXEL). Pixel de 30 m nativo; si el sitio cae en dos "
                             "cuadros WRS de la misma pasada, se unen." % (sat, cfg["fecha_s2"], r["dias"],
                                                                           r["cobertura_pct"], r["despejado_pct"]))
    return p


def _caja_media(a, k=3):
    """Media movil k x k que ignora NaN (sin scipy)."""
    v = np.where(np.isfinite(a), a, 0.0).astype("float64")
    n = np.isfinite(a).astype("float64")
    p = k // 2

    def suma(x):
        x = np.pad(x, p, mode="edge")
        c = x.cumsum(0).cumsum(1)
        c = np.pad(c, ((1, 0), (1, 0)))
        return c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]
    sv, sn = suma(v), suma(n)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(sn > 0, sv / sn, np.nan).astype("float32")


def leer_fusion_landsat_s2(sitio, cfg, nombre):
    """Landsat 30 m afinado a 10 m con el detalle espacial del Sentinel-2 de la misma fecha.

    Filtro pasa-altos con modulacion por regresion (HPF, Gangkofner et al. 2008, adaptado a dos sensores):
        L_fus = L_30->10 + beta * (S_10 - media3x3(S_10))
    L_30->10: Landsat llevado a la grilla de 10 m del Sentinel-2 por interpolacion bilineal (conserva su
    radiometria); S_10: la banda Sentinel-2 de 10 m (B02, B03, B04 o B08) que mejor se correlaciona con esa
    banda Landsat a 30 m; beta: pendiente de la regresion de L sobre S a 30 m (lleva el detalle a la escala
    radiometrica de Landsat). Donde alguna de las dos tiene nube, sombra o falta dato, no se agrega detalle.
    Control (protocolo de Wald, consistencia): el fusionado promediado otra vez a 30 m debe reproducir el
    Landsat original.
    """
    from rasterio.crs import CRS
    from rasterio.enums import Resampling
    from rasterio.warp import reproject

    pl = leer_landsat_l2(sitio, cfg, nombre + "_L")
    ps = leer_s2_l2a(sitio, {"fecha": cfg["fecha_s2"]}, nombre + "_S")
    r = _landsat_elegida(sitio, cfg["fecha_s2"])
    crs_s, tr_s = CRS.from_wkt(ps.crs_wkt), ps.transform
    crs_l, tr_l = CRS.from_wkt(pl.crs_wkt), pl.transform
    alto, ancho = ps.alto, ps.ancho

    def fis(p, n):
        b = [x for x in p.bandas if x["nombre"] == n][0]
        d = b["datos"].astype("float32")
        out = d * np.float32(b["escala"]) + np.float32(b["desplaz"])
        out[d == (b["nodata"] if b["nodata"] is not None else -1)] = np.nan
        return out

    def a_10m(arr, metodo):
        out = np.full((alto, ancho), np.nan, "float32")
        reproject(arr, out, src_transform=tr_l, src_crs=crs_l, dst_transform=tr_s, dst_crs=crs_s,
                  resampling=metodo, src_nodata=np.nan, dst_nodata=np.nan)
        return out

    # mascaras: Landsat despejado (QA_PIXEL bits 6 o 7, sin relleno) y Sentinel-2 valido (SCL 4, 5, 6, 7)
    q = pl.datos("QA_PIXEL").astype("uint16")
    ok_l = (((q >> 6) & 1) | ((q >> 7) & 1)).astype(bool) & ((q & 1) == 0)
    ok_l10 = a_10m(ok_l.astype("float32"), Resampling.nearest) > 0.5
    scl = ps.datos("SCL")
    ok_s = np.isin(scl, (4, 5, 6, 7))
    ok = ok_l10 & ok_s
    if ok.mean() < 0.05:
        raise Falta("Landsat y Sentinel-2 casi no tienen pixeles despejados en comun (%.1f %%)" % (ok.mean() * 100))
    s10 = {b: fis(ps, b) for b in ("B02", "B03", "B04", "B08")}
    s_bajo = {b: _caja_media(np.where(ok, v, np.nan)) for b, v in s10.items()}
    rng = np.random.default_rng(0)
    idx = np.flatnonzero(ok.ravel())
    idx = idx[rng.choice(len(idx), size=min(len(idx), 400000), replace=False)]
    p = Producto(nombre)
    calidad = {}
    bandas_l = [b["nombre"] for b in pl.bandas if b["nombre"].startswith("SR_B")]
    for bl in bandas_l:
        l10 = a_10m(fis(pl, bl), Resampling.bilinear)
        mejor = None
        for bs in s10:
            x, y = s_bajo[bs].ravel()[idx], l10.ravel()[idx]
            m = np.isfinite(x) & np.isfinite(y)
            if m.sum() < 1000:
                continue
            rr = float(np.corrcoef(x[m], y[m])[0, 1])
            if mejor is None or abs(rr) > abs(mejor[1]):
                beta = float(np.polyfit(x[m], y[m], 1)[0])
                mejor = (bs, rr, beta)
        if mejor is None:
            raise Falta("Sin pixeles comunes para la regresion de %s" % bl)
        bs, rr, beta = mejor
        detalle = np.where(ok, s10[bs] - s_bajo[bs], 0.0)
        detalle[~np.isfinite(detalle)] = 0.0
        fus = (l10 + np.float32(beta) * detalle).astype("float32")
        # control de consistencia (Wald): fusionado -> 30 m (promedio) contra el Landsat original
        vuelta = np.full(pl.datos(bl).shape, np.nan, "float32")
        reproject(fus, vuelta, src_transform=tr_s, src_crs=crs_s, dst_transform=tr_l, dst_crs=crs_l,
                  resampling=Resampling.average, src_nodata=np.nan, dst_nodata=np.nan)
        orig = fis(pl, bl)
        m = ok_l & np.isfinite(vuelta) & np.isfinite(orig)
        dif = vuelta[m] - orig[m]
        calidad[bl] = dict(detalle_de=bs, r_30m=round(rr, 3), beta=round(beta, 3),
                           consistencia_sesgo=round(float(dif.mean()), 4),
                           consistencia_rmse=round(float(np.sqrt((dif ** 2).mean())), 4),
                           consistencia_r=round(float(np.corrcoef(vuelta[m], orig[m])[0, 1]), 4),
                           media_original=round(float(orig[m].mean()), 4))
        desc = [x for x in pl.bandas if x["nombre"] == bl][0]["desc"].split(". Valor")[0]
        p.banda(bl, fus, "reflectance",
                "%s, afinada a 10 m con el detalle de la %s del Sentinel-2 (r = %.2f a 30 m, beta = %.2f). "
                "Reflectancia (ya convertida)" % (desc, bs, rr, beta), nodata=float("nan"))
    p.transform, p.crs_wkt = tr_s, ps.crs_wkt
    p.banda("mascara_detalle", ok.astype("uint8"), "", "1 = se agrego detalle de Sentinel-2 (los dos "
            "despejados); 0 = solo Landsat interpolado (nube, sombra o sin dato en alguno)", nodata=255)

    def ndvi(pr):
        rr_, nn = pr.datos("SR_B4"), pr.datos("SR_B5")
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where((nn + rr_) != 0, (nn - rr_) / (nn + rr_), np.nan).astype("float32")
    p.virtual("NDVI", "(SR_B5 + SR_B4) != 0 ? (SR_B5 - SR_B4) / (SR_B5 + SR_B4) : NaN", ndvi, "",
              "NDVI del Landsat afinado (banda virtual)")
    # ERGAS a 30 m (consistencia): 100 * (h/l) * sqrt(mean((RMSE_k / media_k)^2)), h/l = 10/30
    ergas = 100.0 / 3.0 * float(np.sqrt(np.mean([(c["consistencia_rmse"] / c["media_original"]) ** 2
                                                  for c in calidad.values() if c["media_original"]])))
    dias = int(r["dias"])
    sat = r["plataforma"].replace("landsat-", "Landsat ")
    p.metadatos = {"Metodo": {
        "nombre": "Filtro pasa-altos con modulacion por regresion (HPF), Landsat afinado con Sentinel-2",
        "formula": "L_fus = L_30m_interpolado_a_10m + beta * (S2_10m - media_3x3(S2_10m))",
        "referencia": "Gangkofner, U. G., Pradhan, P. S. y Holcomb, D. W. (2008). Optimizing the high-pass "
                      "filter addition technique for image fusion. Photogrammetric Engineering & Remote "
                      "Sensing 74(9), 1107-1118.",
        "control": "Protocolo de Wald (consistencia): el fusionado promediado a 30 m comparado con el Landsat original",
        "ERGAS_consistencia": round(ergas, 3),
        "pixeles_con_detalle_pct": round(float(ok.mean() * 100), 1),
        "diferencia_de_fechas_dias": dias,
        "advertencia": "Las dos imagenes no son simultaneas (%d dias): un cambio real entre fechas (agua, "
                       "cosecha, quema) aparece como detalle falso. La temperatura (ST_B10, adquirida a 100 m) "
                       "no se afina." % abs(dias)},
        "Calidad_por_banda": {k: {kk: str(vv) for kk, vv in v.items()} for k, v in calidad.items()},
        "Landsat": pl.metadatos, "Sentinel2": ps.metadatos}
    p.archivos_meta = pl.archivos_meta + ps.archivos_meta
    p.inicio = pl.inicio
    p.tipo = "FUSION_LANDSAT_SENTINEL2_HPF_10M"
    p.cita = ("Fusion propia (HPF) de %s y Sentinel-2. Fuentes: %s | %s" % (sat, pl.cita, ps.cita))
    p.recorte = _doc_recorte(sitio, "Grilla de 10 m del Sentinel-2 del %s; %s del %s (%+d dias) interpolado "
                             "bilinealmente y afinado con el detalle de 10 m. ERGAS de consistencia a 30 m: %.2f "
                             "(menor que 3 es bueno). %.0f %% de los pixeles con detalle."
                             % (cfg["fecha_s2"], sat, r["fecha_landsat"], dias, ergas, ok.mean() * 100))
    p.recorte["pixel_y_proyeccion"] = "10 m, grilla y proyeccion del Sentinel-2 (remuestreado: es una fusion)"
    print("    fusion: ERGAS %.2f; detalle en %.0f %%; %s" % (ergas, ok.mean() * 100, "; ".join(
        "%s<-%s r=%.2f b=%.2f rmse=%.4f" % (k, v["detalle_de"], v["r_30m"], v["beta"], v["consistencia_rmse"])
        for k, v in calidad.items())))
    return p


def _cbers_carpeta(cfg):
    r = _cbers_elegida(cfg["zona"], cfg["fecha_obj"])
    if r is None:
        raise Falta("Sin escena CBERS-4A elegida para %s %s (CBERS4A\\cbers_elegidas.csv)" % (cfg["zona"], cfg["fecha_obj"]))
    c = glob.glob(os.path.join(ORIGINALES, "CBERS4A", cfg["zona"], "*_%s" % r["id"]))
    c = [x for x in c if os.path.exists(os.path.join(x, ".completo"))]
    if not c:
        raise Falta("CBERS-4A %s elegido pero no bajado (datos_crudos.py cbers --confirmar)" % r["id"])
    return c[0], r


def _cbers_meta(p, carp, r, cfg):
    from zonas_cbers import ZONAS, CITA
    md = {}
    for x in sorted(glob.glob(os.path.join(carp, "*.xml"))):
        try:
            md[os.path.basename(x).replace(".xml", "")] = xml_a_arbol(x)
        except Exception:                                # noqa: BLE001
            md[os.path.basename(x)] = "copiado sin tocar en Metadatos_originales"
        p.archivos_meta.append(x)
    j = os.path.join(carp, "item_STAC.json")
    if os.path.exists(j):
        md["item_STAC"] = json_a_arbol(j)
        p.archivos_meta.append(j)
    p.metadatos = md
    f = r["id"].split("_")[3]
    p.inicio = "%s-%s-%sT00:00:00" % (f[:4], f[4:6], f[6:])
    dias = (_dt.datetime.strptime(f, "%Y%m%d") - _dt.datetime.strptime(cfg["fecha_obj"], "%Y%m%d")).days
    p.cita = "%s Escena %s." % (CITA, r["id"])
    p.recorte = _doc_recorte(cfg["zona"] if cfg["zona"] in SITIOS else ZONAS[cfg["zona"]]["sitio"],
                             "Zona %s: %s. Escena del %s, %+d dias de la fecha objetivo %s (elegida a ojo, sin nubes "
                             "en la zona: el catalogo del INPE no informa nubes)."
                             % (cfg["zona"], ZONAS[cfg["zona"]]["nota"], f, dias, cfg["fecha_obj"]))
    o, s_, e, n = ZONAS[cfg["zona"]]["caja"]
    p.recorte["caja_WGS84_oeste_sur_este_norte"] = "%.4f, %.4f, %.4f, %.4f" % (o, s_, e, n)
    return f


def leer_cbers_ms(sitio, cfg, nombre):
    import rasterio
    from zonas_cbers import BANDAS_WPM
    carp, r = _cbers_carpeta(cfg)
    p = Producto(nombre)
    for b in ("BAND1", "BAND2", "BAND3", "BAND4"):
        ruta = glob.glob(os.path.join(carp, "*_%s.tif" % b))
        if not ruta:
            raise Falta("Falta la %s en %s" % (b, carp))
        with rasterio.open(ruta[0]) as s:
            arr = s.read(1)
            p.transform, p.crs_wkt = s.transform, _wkt(s.crs)
        nb, desc = BANDAS_WPM[b]
        p.banda(nb, arr, "DN", "CBERS-4A WPM %s. Numero digital (sin calibrar ni corregir por la atmosfera)" % desc,
                nodata=0)
    _cbers_meta(p, carp, r, cfg)
    p.tipo = "CBERS4A_WPM_L4_MULTIESPECTRAL_8M"
    return p


def leer_cbers_ps(sitio, cfg, nombre):
    """Pansharpening Brovey ponderado (el de GDAL): PS_i = MS_i(2 m) * PAN / (sum w_i MS_i(2 m) + c),
    con los pesos w_i y c ajustados por minimos cuadrados entre la pancromatica llevada a 8 m y las cuatro
    multiespectrales. Control de consistencia (Wald): PS_i promediado a 8 m contra MS_i."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject
    from zonas_cbers import BANDAS_WPM
    carp, r = _cbers_carpeta(cfg)
    rp = glob.glob(os.path.join(carp, "*_BAND0.tif"))
    if not rp:
        raise Falta("Falta la pancromatica (BAND0) en %s" % carp)
    with rasterio.open(rp[0]) as s:
        pan = s.read(1)
        tr_p, crs = s.transform, s.crs
    alto, ancho = pan.shape
    ms, tr_m = {}, None
    for b in ("BAND1", "BAND2", "BAND3", "BAND4"):
        with rasterio.open(glob.glob(os.path.join(carp, "*_%s.tif" % b))[0]) as s:
            ms[b] = s.read(1)
            tr_m = s.transform
    # pancromatica a 8 m (promedio 4 x 4) alineada con la multiespectral
    h8, w8 = min(alto // 4, ms["BAND1"].shape[0]), min(ancho // 4, ms["BAND1"].shape[1])
    p8 = pan[:h8 * 4, :w8 * 4].reshape(h8, 4, w8, 4).astype("float32")
    v8 = (p8 > 0).all(axis=(1, 3))
    p8 = p8.mean(axis=(1, 3))
    m8 = np.stack([ms[b][:h8, :w8].astype("float32") for b in ms])
    ok = v8 & (m8 > 0).all(0)
    idx = np.flatnonzero(ok.ravel())
    idx = idx[np.random.default_rng(0).choice(len(idx), size=min(len(idx), 300000), replace=False)]
    A = np.column_stack([m8[k].ravel()[idx] for k in range(4)] + [np.ones(len(idx))])
    coef, *_ = np.linalg.lstsq(A, p8.ravel()[idx], rcond=None)
    pred = A @ coef
    r2 = 1 - np.sum((p8.ravel()[idx] - pred) ** 2) / np.sum((p8.ravel()[idx] - p8.ravel()[idx].mean()) ** 2)

    def a_2m(arr):
        out = np.zeros((alto, ancho), "float32")
        reproject(arr.astype("float32"), out, src_transform=tr_m, src_crs=crs, dst_transform=tr_p, dst_crs=crs,
                  resampling=Resampling.bilinear, src_nodata=0, dst_nodata=0)
        return out
    psyn = np.full((alto, ancho), np.float32(coef[4]), "float32")
    for k, b in enumerate(ms):
        psyn += np.float32(coef[k]) * a_2m(ms[b])
    validos = (pan > 0) & (psyn > 0)
    razon = np.zeros((alto, ancho), "float32")
    razon[validos] = pan[validos].astype("float32") / psyn[validos]
    del psyn
    p = Producto(nombre)
    p.banda("PAN", pan, "DN", "CBERS-4A WPM %s. Numero digital" % BANDAS_WPM["BAND0"][1], nodata=0)
    calidad = {}
    for k, b in enumerate(ms):
        up = a_2m(ms[b])
        ps = np.clip(np.rint(up * razon), 0, 65535).astype("uint16")
        ps[~validos] = 0
        del up
        nb, desc = BANDAS_WPM[b]
        a8 = ps[:h8 * 4, :w8 * 4].reshape(h8, 4, w8, 4).astype("float32").mean(axis=(1, 3))
        m = ok & (a8 > 0)
        d = a8[m] - m8[k][m]
        calidad[nb] = dict(peso=round(float(coef[k]), 4), sesgo=round(float(d.mean()), 2),
                           rmse=round(float(np.sqrt((d ** 2).mean())), 2), media=round(float(m8[k][m].mean()), 2),
                           r=round(float(np.corrcoef(a8[m], m8[k][m])[0, 1]), 4))
        p.banda("PS_" + nb, ps, "DN", "CBERS-4A WPM %s, afinada a 2 m con la pancromatica (Brovey ponderado). "
                "Numero digital" % desc.replace(", 8 m", ""), nodata=0)
    ergas = 25.0 * float(np.sqrt(np.mean([(c["rmse"] / c["media"]) ** 2 for c in calidad.values()])))
    p.transform, p.crs_wkt = tr_p, _wkt(crs)
    f = _cbers_meta(p, carp, r, cfg)
    p.metadatos = {"Metodo": {
        "nombre": "Pansharpening Brovey ponderado (el metodo por defecto de GDAL)",
        "formula": "PS_i = MS_i(bilineal a 2 m) * PAN / (w1 MS1 + w2 MS2 + w3 MS3 + w4 MS4 + c)",
        "pesos": "w1 %.4f, w2 %.4f, w3 %.4f, w4 %.4f, c %.1f; ajuste por minimos cuadrados de la pancromatica "
                 "promediada a 8 m (R2 = %.3f)" % (tuple(coef) + (r2,)),
        "control": "Protocolo de Wald (consistencia): PS_i promediado 4 x 4 a 8 m contra MS_i",
        "ERGAS_consistencia": round(ergas, 3),
        "advertencia": "Numeros digitales sin calibrar: sirve para mirar, digitalizar y comparar formas; los "
                       "valores no son reflectancia y el Brovey altera la radiometria. No calcular indices con "
                       "las bandas afinadas."},
        "Calidad_por_banda": {k: {kk: str(vv) for kk, vv in v.items()} for k, v in calidad.items()},
        "Original": p.metadatos}
    p.tipo = "CBERS4A_WPM_PANSHARPENED_2M"
    p.recorte["pixel_y_proyeccion"] = "2 m, grilla nativa de la pancromatica (las multiespectrales, remuestreadas)"
    p.cita = "Pansharpening propio (Brovey ponderado) de " + p.cita
    print("    pansharpening: ERGAS %.2f; R2 de los pesos %.3f; %s" % (ergas, r2, "; ".join(
        "%s r=%.3f" % (k, v["r"]) for k, v in calidad.items())))
    return p


def leer_embeddings(sitio, cfg, nombre):
    """64 dimensiones int8 tal como las entrega Google (DN), con la descuantizacion documentada, y un RGB de
    las tres primeras componentes principales (8 bits) para mirar en QGIS."""
    import rasterio
    st = cfg.get("sitio_emb", sitio)
    ruta = os.path.join(ORIGINALES, "EMBEDDINGS", st, "AEF_%s_%d.tif" % (st, cfg["anio"]))
    if not os.path.exists(ruta):
        raise Falta("No esta %s (datos_crudos.py embeddings --confirmar)" % os.path.basename(ruta))
    p = Producto(nombre)
    with rasterio.open(ruta) as s:
        arr = s.read()
        p.transform, p.crs_wkt = s.transform, _wkt(s.crs)
        tags = s.tags()
    for k in range(arr.shape[0]):
        p.banda("A%02d" % k, arr[k], "", "Dimension %d del embedding anual AlphaEarth Foundations (DN int8). "
                "Valor = signo(DN) * (DN / 127,5)^2; -128 = sin dato" % k, nodata=-128)
    ok = arr[0] != -128
    # componentes principales sobre los valores descuantizados (muestra de hasta 200 000 pixeles)
    idx = np.flatnonzero(ok.ravel())
    if len(idx) > 1000:
        sel = idx[np.random.default_rng(0).choice(len(idx), size=min(len(idx), 200000), replace=False)]
        X = arr.reshape(arr.shape[0], -1)[:, sel].astype("float32").T
        X = np.sign(X) * (X / 127.5) ** 2
        mu = X.mean(0)
        _, sv, vt = np.linalg.svd(X - mu, full_matrices=False)
        comp = vt[:3]
        var = (sv[:3] ** 2) / (sv ** 2).sum()
        rgb = np.zeros((3,) + arr.shape[1:], "uint8")
        h = arr.shape[1]
        proy = []
        for f0 in range(0, h, 512):
            bl = arr[:, f0:f0 + 512].reshape(arr.shape[0], -1).astype("float32").T
            bl = np.sign(bl) * (bl / 127.5) ** 2
            proy.append(((bl - mu) @ comp.T).T.reshape(3, -1, arr.shape[2]))
        proy = np.concatenate(proy, axis=1)
        for k in range(3):
            v = proy[k][ok]
            lo, hi = np.percentile(v, (2, 98))
            rgb[k] = np.clip((proy[k] - lo) / max(hi - lo, 1e-6) * 254 + 1, 1, 255).astype("uint8")
            rgb[k][~ok] = 0
        p.extras = [("CP1_CP2_CP3_RGB_8bit", rgb,
                     "RGB de las tres primeras componentes principales de los 64 valores descuantizados "
                     "(varianza explicada %.0f, %.0f y %.0f %%), estirado 2-98 %%. Solo para mirar: los colores no "
                     "tienen significado fijo y cambian de un anio o sitio a otro." % tuple(var * 100))]
    p.metadatos = {"Producto": {"nombre": "AlphaEarth Foundations Satellite Embedding, anual",
                                "anio": str(cfg["anio"]), "descuantizar": "valor = signo(DN) * (DN / 127,5)^2",
                                "sin_dato": "-128",
                                "que_es": "Resumen anual de Sentinel-1, Sentinel-2, Landsat, GEDI, clima y otras "
                                          "fuentes, aprendido por un modelo de Google DeepMind: 64 numeros por "
                                          "pixel de 10 m. Las dimensiones no tienen significado fisico propio; "
                                          "sirven para clasificar, buscar parecidos y detectar cambios entre anios "
                                          "(producto punto entre embeddings de dos anios)."},
                   "Etiquetas_del_archivo": tags}
    p.archivos_meta = []
    p.inicio = "%d-01-01T00:00:00" % cfg["anio"]
    p.tipo = "ALPHAEARTH_EMBEDDING_ANUAL_10M"
    p.cita = ("Google y Google DeepMind, AlphaEarth Foundations Satellite Embedding, %d, CC BY 4.0; copia en "
              "Source Cooperative (Taylor Geospatial), https://source.coop/tge-labs/aef" % cfg["anio"])
    p.recorte = _doc_recorte(st, "Embedding anual %d (resume el anio completo, no una fecha). Pixel de 10 m y "
                             "UTM nativos." % cfg["anio"])
    return p


def leer_copdem(sitio, cfg, nombre):
    carp = sorted(glob.glob(os.path.join(ORIGINALES, "PLANETARY", sitio, "cop-dem-glo-30", "*")))
    rs = [os.path.join(c, "data.tif") for c in carp if os.path.exists(os.path.join(c, "data.tif"))]
    if not rs:
        raise Falta("No hay Copernicus DEM en PLANETARY\\%s" % sitio)
    arr, tr, crs, nd = mosaico(rs, sitio)
    p = Producto(nombre)
    p.banda("elevacion", arr.astype("float32"), "m",
            "Altura sobre el geoide EGM2008 (Copernicus DEM GLO-30, DSM: incluye dosel y edificios)",
            nodata=nd if nd is not None else -32767.0)
    p.transform, p.crs_wkt = tr, _wkt(crs)
    stacs = [os.path.join(c, "item_STAC.json") for c in carp if os.path.exists(os.path.join(c, "item_STAC.json"))]
    p.metadatos = {"item_%d" % i: json_a_arbol(s) for i, s in enumerate(stacs, 1)}
    p.inicio = "2021-04-22T00:00:00"
    p.tipo = "COPERNICUS_DEM_GLO30"
    p.cita = ("ESA / Airbus, Copernicus DEM GLO-30 (Microsoft Planetary Computer). "
              "https://planetarycomputer.microsoft.com/dataset/cop-dem-glo-30")
    p.archivos_meta = stacs
    p.recorte = _doc_recorte(sitio)
    return p


def leer_alos1_rtc(sitio, cfg, nombre):
    """ALOS-1 PALSAR RTC de alta resolucion de ASF (zip con GeoTIFF y metadatos)."""
    import zipfile

    carp = os.path.join(ORIGINALES, cfg["carpeta"])
    zips = sorted(glob.glob(os.path.join(carp, "*.zip")))
    for z in zips:
        dest = os.path.splitext(z)[0]
        if not os.path.isdir(dest):
            with zipfile.ZipFile(z) as zf:
                zf.extractall(carp)
    tifs = [t for t in glob.glob(os.path.join(carp, "**", "*.tif"), recursive=True)
            if re.search(r"[._](HH|HV|VV|VH)\.tif$", t, re.I)]
    if not tifs:
        raise Falta("No hay ALOS-1 PALSAR RTC en %s (falta bajarlo con Tp1_04_buscar_asf.py)" % carp)
    p = Producto(nombre)
    tr = crs = None
    pols = {}
    for t in sorted(tifs):
        pol = re.search(r"[._](HH|HV|VV|VH)\.tif$", t, re.I).group(1).upper()
        arr, tr, crs, nd = recortar(t, sitio)
        arr = arr.astype("float32")
        arr[~np.isfinite(arr) | (arr <= 0)] = 0.0
        p.banda("Gamma0_" + pol, arr, "intensity",
                "gamma0 %s LINEAL (potencia), RTC de ASF a 12,5 m" % pol)
        pols[pol] = t
    carpeta_prod = os.path.dirname(next(iter(pols.values())))
    for suf, nb, uni, desc in (("inc_map", "angulo_incidencia_local", "rad", "Angulo de incidencia local"),
                               ("ls_map", "mascara_sombra_inversion", "", "Mascara de sombra e inversion"),
                               ("dem", "dem_usado", "m", "MDE usado en la correccion por terreno")):
        cand = glob.glob(os.path.join(carpeta_prod, "*%s*.tif" % suf))
        if cand:
            a, _, _, _ = recortar(cand[0], sitio)
            if a.shape == p.bandas[0]["datos"].shape:
                p.banda(nb, a.astype("float32"), uni, desc, nodata=None)
    p.transform, p.crs_wkt = tr, _wkt(crs)
    co = "Gamma0_HH" if "HH" in pols else "Gamma0_VV"
    cr = "Gamma0_HV" if "HV" in pols else ("Gamma0_VH" if "VH" in pols else None)
    agregar_db_y_cociente(p, co, cr, co[-2:], cr[-2:] if cr else "", "gamma0")
    md = {}
    for x in sorted(glob.glob(os.path.join(carpeta_prod, "*.xml"))):
        try:
            md[_nombre_valido(os.path.basename(x))] = xml_a_arbol(x)
        except ET.ParseError:
            pass
        p.archivos_meta.append(x)
    for x in sorted(glob.glob(os.path.join(carpeta_prod, "*.txt")) + glob.glob(os.path.join(carpeta_prod, "*.md"))):
        md[_nombre_valido(os.path.basename(x))] = open(x, encoding="utf-8", errors="replace").read()[:20000]
        p.archivos_meta.append(x)
    p.metadatos = md
    nombre_prod = os.path.basename(carpeta_prod)
    p.inicio = cfg.get("fecha", "")
    if len(p.inicio) == 8:
        p.inicio = "%s-%s-%sT00:00:00" % (p.inicio[:4], p.inicio[4:6], p.inicio[6:])
    p.tipo = "ALOS_PALSAR_RTC_HI_RES"
    p.cita = ("JAXA / ASF DAAC. ALOS PALSAR %s RTC 12,5 m, %s. https://search.asf.alaska.edu"
              % (nombre_prod, p.inicio[:10]))
    p.recorte = _doc_recorte(sitio)
    p.recorte["carpeta_original"] = carpeta_prod
    return p


# NovaSAR-1: lo recorta SNAP (gpt Subset) para conservar su Abstracted_Metadata.
def gpt_snap():
    if os.environ.get("SNAP_GPT") and os.path.exists(os.environ["SNAP_GPT"]):
        return os.environ["SNAP_GPT"]
    cand = []
    for raiz in (r"C:\Program Files", os.path.expandvars(r"%LOCALAPPDATA%\Programs"), os.path.expanduser("~")):
        cand += glob.glob(os.path.join(raiz, "esa-snap*", "bin", "gpt.exe"))
        cand += glob.glob(os.path.join(raiz, "snap*", "bin", "gpt.exe"))
    cand = sorted(cand, key=lambda r: [int(n) for n in re.findall(r"\d+", r)] or [0])
    return cand[-1] if cand else ""


def _tiepoints_novasar(meta_xml):
    raiz = ET.parse(meta_xml).getroot()
    tp = []
    for e in raiz.iter("TiePoint"):
        tp.append((float(e.findtext("Line")), float(e.findtext("Pixel")), float(e.findtext("Longitude")),
                   float(e.findtext("Latitude")), float(e.findtext("Height") or 0)))
    return np.array(tp)


def _sigma0(amp, k):
    a = amp.astype("float32")
    out = np.full(a.shape, np.nan, "float32")
    ok = a > 0
    out[ok] = a[ok] ** 2 / np.float32(k)
    return out


def _ajuste_pol2(lon, lat, val):
    A = np.column_stack([np.ones_like(lon), lon, lat, lon * lat, lon ** 2, lat ** 2])
    coef, *_ = np.linalg.lstsq(A, val, rcond=None)
    return lambda lo, la: np.column_stack([np.ones_like(lo), lo, la, lo * la, lo ** 2, la ** 2]) @ coef


def leer_novasar_grd(sitio, cfg, nombre):
    import rasterio
    from rasterio.windows import Window

    metas = glob.glob(os.path.join(NOVASAR, "NovaSAR_01_%s_grd*" % cfg["escena"], "*", "metadata.xml"))
    if not metas:
        raise Falta("No esta la escena NovaSAR-1 %s (GRD) en %s" % (cfg["escena"], NOVASAR))
    meta = metas[0]
    carpeta = os.path.dirname(meta)
    img = glob.glob(os.path.join(carpeta, "image_HH.tif")) or glob.glob(os.path.join(carpeta, "image_*.tif"))
    pol = re.search(r"image_(\w\w)\.tif", os.path.basename(img[0])).group(1)
    tp = _tiepoints_novasar(meta)
    f_lin = _ajuste_pol2(tp[:, 2], tp[:, 3], tp[:, 0])
    f_pix = _ajuste_pol2(tp[:, 2], tp[:, 3], tp[:, 1])
    o, s, e, n = SITIOS[sitio]["bbox"]
    lo, la = np.meshgrid(np.linspace(o, e, 25), np.linspace(s, n, 25))
    lin = f_lin(lo.ravel(), la.ravel())
    pix = f_pix(lo.ravel(), la.ravel())
    with rasterio.open(img[0]) as src:
        r0, r1 = int(max(np.floor(lin.min()), 0)), int(min(np.ceil(lin.max()), src.height))
        c0, c1 = int(max(np.floor(pix.min()), 0)), int(min(np.ceil(pix.max()), src.width))
        if r1 <= r0 or c1 <= c0:
            raise Falta("La escena NovaSAR %s no cubre %s" % (cfg["escena"], sitio))
        amp = src.read(1, window=Window(c0, r0, c1 - c0, r1 - r0))
    p = Producto(nombre)
    p.banda("Amplitude_" + pol, amp, "amplitude", "Amplitud (DN) del GRD NovaSAR-1, sin calibrar", nodata=0)
    p.metadatos = xml_a_arbol(meta)
    txt = open(meta, encoding="utf-8", errors="replace").read()
    mc = re.search(r"<CalibrationConstant[^>]*>\s*([0-9.Ee+\-]+)\s*<", txt)
    kcal = float(mc.group(1)) if mc else 1e5
    a_nom = "Amplitude_" + pol
    p.virtual("Sigma0_" + pol, "{0} > 0 ? {0}*{0}/{1!r} : NaN".format(a_nom, kcal),
              lambda pr: _sigma0(pr.datos(a_nom), kcal), "intensity",
              "sigma0 %s LINEAL = DN^2 / CalibrationConstant (%g, del metadata.xml del producto)" % (pol, kcal),
              "%s > 0" % a_nom)
    p.virtual("Sigma0_%s_db" % pol, "{0} > 0 ? 10*log10({0}*{0}/{1!r}) : NaN".format(a_nom, kcal),
              lambda pr: db(_sigma0(pr.datos(a_nom), kcal)), "dB",
              "sigma0 %s en dB (banda virtual)" % pol, "%s > 0" % a_nom)
    p.gcps = [(fl - r0, px - c0, lon, lat, z) for fl, px, lon, lat, z in tp]
    # grillas de enlace lat/lon para SNAP: ajuste de 2.o grado a los tie points del producto
    f_lat = _ajuste_pol2(tp[:, 0], tp[:, 1], tp[:, 3])
    f_lon = _ajuste_pol2(tp[:, 0], tp[:, 1], tp[:, 2])
    resid = max(np.abs(f_lat(tp[:, 0], tp[:, 1]) - tp[:, 3]).max(), np.abs(f_lon(tp[:, 0], tp[:, 1]) - tp[:, 2]).max())
    alto, ancho = amp.shape
    nx, ny = 21, 21
    paso_x, paso_y = (ancho - 1) / (nx - 1), (alto - 1) / (ny - 1)
    cc, ff = np.meshgrid(np.arange(nx) * paso_x + 0.5, np.arange(ny) * paso_y + 0.5)
    # SNAP ubica la grilla en coordenadas de esquina (centro del pixel 0 = 0,5); los tie points
    # del producto van por indice de pixel: se resta 0,5 para evaluar el ajuste.
    fi, ci = (ff - 0.5 + r0).ravel(), (cc - 0.5 + c0).ravel()
    p.tie = {"latitude": f_lat(fi, ci).reshape(ny, nx),
             "longitude": f_lon(fi, ci).reshape(ny, nx),
             "paso_x": paso_x, "paso_y": paso_y}
    src_attr = p.metadatos.get("metadata", {}).get("Source_Attributes", {})
    p.inicio = str(src_attr.get("RawDataStartTime", "")).replace(" ", "T")
    p.tipo = "NovaSAR_GRD"
    p.cita = ("SSTL / CSIRO. NovaSAR-1 banda S, %s, escena %s, %s, GRD. Archivo del curso (CSIRO NovaSAR "
              "Data Hub: https://research.csiro.au/cceo/novasar/)" % (pol, cfg["escena"], p.inicio[:10]))
    p.archivos_meta = [meta]
    p.recorte = _doc_recorte(sitio, "Geometria de rango en el terreno (GRD): NO esta proyectado al mapa. "
                             "SNAP 14 no trae lector de NovaSAR-1: este .dim lo escribe el programa, con "
                             "geocodificacion por puntos de enlace (grillas latitude/longitude de 21 x 21 "
                             "ajustadas a los tie points del metadata.xml) y sigma0 por la constante de "
                             "calibracion del producto. Sin Abstracted_Metadata: en SNAP se proyecta con "
                             "Raster > Geometric > Reprojection, no con Terrain-Correction. El GeoTIFF lleva "
                             "los tie points como puntos de control y QGIS lo ubica con ellos.")
    p.recorte["error_maximo_del_ajuste_de_las_grillas_grados"] = "%.6f" % resid
    p.recorte["ventana_en_el_original_filas"] = "%d a %d" % (r0, r1)
    p.recorte["ventana_en_el_original_columnas"] = "%d a %d" % (c0, c1)
    p.recorte["archivo_original"] = meta
    p._novasar = (meta, pol)
    return p


def leer_jrc_gsw(sitio, cfg, nombre):
    carp = sorted(glob.glob(os.path.join(ORIGINALES, "PLANETARY", sitio, "jrc-gsw", "*")))
    rs = [os.path.join(c, "occurrence.tif") for c in carp if os.path.exists(os.path.join(c, "occurrence.tif"))]
    if not rs:
        raise Falta("No hay JRC Global Surface Water en PLANETARY\\%s" % sitio)
    arr, tr, crs, nd = mosaico(rs, sitio)
    p = Producto(nombre)
    p.banda("ocurrencia_agua", arr.astype("uint8"), "%",
            "Frecuencia con que hubo agua en 1984-2021 (0 a 100 %); >= 90 % es agua permanente",
            nodata=nd if nd is not None else 255)
    p.transform, p.crs_wkt = tr, _wkt(crs)
    stacs = [os.path.join(c, "item_STAC.json") for c in carp if os.path.exists(os.path.join(c, "item_STAC.json"))]
    p.metadatos = {"item_%d" % i: json_a_arbol(x) for i, x in enumerate(stacs, 1)}
    p.inicio, p.fin = "1984-03-16T00:00:00", "2021-12-31T23:59:59"
    p.tipo = "JRC_GSW_OCURRENCIA"
    p.cita = ("EC JRC / Google. Global Surface Water, ocurrencia 1984-2021 (Pekel et al. 2016), Microsoft "
              "Planetary Computer. https://planetarycomputer.microsoft.com/dataset/jrc-gsw")
    p.archivos_meta = stacs
    p.recorte = _doc_recorte(sitio)
    return p


LEYENDA_MAPBIOMAS_C3 = {
    3: ("Bosques cerrados", "#1f8d49"), 4: ("Bosques abiertos", "#7dc975"), 6: ("Bosques inundables", "#007785"),
    9: ("Silvicultura", "#7a6c00"), 10: ("Vegetacion natural herbacea y arbustiva", "#d6bc74"),
    11: ("Herbaceas inundables", "#519799"), 12: ("Herbaceas", "#d6bc74"), 14: ("Agropecuario", "#ffefc3"),
    15: ("Pastura", "#edde8e"), 18: ("Agricultura", "#E974ED"), 19: ("Cultivos temporarios", "#C27BA0"),
    21: ("Mosaico de usos", "#ffefc3"), 22: ("Area sin vegetacion", "#d4271e"), 24: ("Areas urbanas", "#d4271e"),
    25: ("Otras areas no vegetadas", "#db4d4f"), 26: ("Cuerpo de agua", "#2532e4"),
    27: ("No observado", "#ffffff"), 33: ("Rios, lagunas, lagos y oceano", "#2532e4"),
    34: ("Glaciares y nieve perenne", "#93dfe6"), 36: ("Cultivos perennes", "#d082de"),
    63: ("Mosaicos de arbustos y herbaceas", "#C7E0AB"), 66: ("Arbustales cerrados", "#a89358"),
    73: ("Turberas", "#6fc179"), 77: ("Arbustales abiertos", "#86b074"),
}
LEYENDA_MAPBIOMAS_PERDIDA = {
    1: ("Antropico", "#ffefc3"), 2: ("Vegetacion primaria", "#1f8d49"), 3: ("Vegetacion secundaria", "#7dc975"),
    4: ("Perdida de vegetacion primaria en el anio", "#d4271e"),
    5: ("Recuperacion de vegetacion secundaria en el anio", "#00ff00"),
    6: ("Perdida de vegetacion secundaria en el anio", "#ff9900"),
    7: ("Valor 7: no figura en la leyenda del LEEME de la descarga (en los sitios coincide con agua); verificar",
        "#2532e4"),
}
CITA_MAPBIOMAS = ("Proyecto MapBiomas Argentina. Coleccion 3 de los Mapas Anuales de Cobertura y Uso del Suelo y "
                  "productos derivados; Coleccion 1 de MapBiomas Fuego. Accedido el 18/10/2026, recorte a Entre Rios "
                  "(limite IGN IN1=30). Licencia CC BY 4.0. https://argentina.mapbiomas.org")
CITA_CCI = ("Santoro, M. y Cartus, O. (2026). ESA Biomass Climate Change Initiative (Biomass_cci): Global datasets "
            "of forest above-ground biomass for the years 2005-2012 and 2015-2024, v7.0. NERC EDS CEDA. "
            "https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903")


def leer_serie(sitio, cfg, nombre):
    """Serie de mapas (un archivo por anio o por variable) apilada en un solo producto, en la
    grilla nativa del primero. Para MapBiomas y CCI Biomass."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject

    capas = []
    for nb, rel in cfg["capas"]:
        r = os.path.join(ORIGINALES, rel.format(sitio=sitio))
        if os.path.exists(r):
            capas.append((nb, r))
    if not capas:
        raise Falta("No esta ninguna capa de %s" % cfg["capas"][0][1].format(sitio=sitio))
    p = Producto(nombre)
    if cfg.get("grilla_de"):
        # MapBiomas Fuego viene en EPSG:3857 (Pseudo-Mercator, esfera): SNAP lo ubica mal
        # (lo trata como Mercator sobre el elipsoide). Se lleva a la grilla EPSG:4326 de la
        # cobertura de MapBiomas (misma resolucion nominal de 30 m) por vecino mas proximo.
        arr0, tr0, crs0, nd0 = recortar(os.path.join(ORIGINALES, cfg["grilla_de"]), sitio)
    else:
        arr0, tr0, crs0, nd0 = recortar(capas[0][1], sitio)
    for nb, r in capas:
        with rasterio.open(r) as s:
            if s.crs == crs0 and s.res == (abs(tr0.a), abs(tr0.e)):
                a, tr, _, nd = recortar(r, sitio)
                if a.shape != arr0.shape or tr != tr0:
                    raise Falta("Grilla distinta en %s" % r)
            else:
                a = np.zeros(arr0.shape, dtype=s.dtypes[0])
                reproject(s.read(1), a, src_transform=s.transform, src_crs=s.crs, dst_transform=tr0,
                          dst_crs=crs0, resampling=Resampling.nearest)
                nd = s.nodata
        p.banda(nb, a, cfg.get("unidad", ""), cfg["desc"].format(nb=nb),
                nodata=cfg.get("nodata", nd))
    p.transform, p.crs_wkt = tr0, _wkt(crs0)
    p.leyenda = cfg.get("leyenda")
    md = {"capas_originales": {nb: r for nb, r in capas}}
    if p.leyenda:
        md["leyenda"] = {str(k): "%s (%s)" % v for k, v in sorted(p.leyenda.items())}
    for x in cfg.get("archivos_meta", []):
        x = os.path.join(ORIGINALES, x)
        if os.path.exists(x):
            p.archivos_meta.append(x)
            md[_nombre_valido(os.path.basename(x))] = open(x, encoding="utf-8", errors="replace").read()[:30000]
    with rasterio.open(capas[0][1]) as s:
        md["etiquetas_del_primer_archivo"] = s.tags()
    p.metadatos = md
    p.inicio, p.fin = cfg.get("inicio", ""), cfg.get("fin", "")
    p.tipo = cfg["tipo"]
    p.cita = cfg["cita"]
    p.recorte = _doc_recorte(sitio, cfg.get("nota", ""))
    return p


def contexto(sitio):
    """CCI Biomass y MapBiomas: la historia del sitio, para todos los practicos."""
    mb = "MAPBIOMAS_ENTRE_RIOS"
    leeme_mb = [os.path.join(mb, "LEEME.txt"), os.path.join(mb, "02_Estadisticas", "Entre_Rios_Historico_1985_2025.csv")]
    anios_cci = ["2010", "2015", "2020", "2021", "2024"]
    grilla_4326 = os.path.join(mb, "01_Cobertura", "Entre_Rios_integration-argentina_classification_2025.tif")
    nota_3857 = ("El original esta en EPSG:3857 (Pseudo-Mercator, 30 m); se llevo a la grilla EPSG:4326 de la "
                 "cobertura de MapBiomas (~30 m) por vecino mas proximo, porque SNAP ubica mal el EPSG:3857.")
    fab = os.environ.get("CURSO_SAR_FABDEM", os.path.join(os.path.expanduser("~"), ".snap", "auxdata", "dem",
                                                            "FABDEM", "FABDEM_v1-2_Entre_Rios.tif"))
    return [
        ("serie", {"etiqueta": "FABDEM_v1-2", "tipo": "FABDEM_V1_2",
                   "cita": "Hawker, L. et al. (2022). A 30 m global map of elevation with forests and buildings "
                           "removed. Environ. Res. Lett. 17, 024016. https://doi.org/10.1088/1748-9326/ac4d4f. "
                           "FABDEM v1-2, Universidad de Bristol (CC BY-NC-SA 4.0): "
                           "https://data.bris.ac.uk/data/dataset/s5hqmjcdj8yo2ibzi9b4ew3sn",
                   "capas": [("elevacion_fabdem", fab)], "unidad": "m",
                   "desc": "{nb}: altura del terreno sobre el geoide EGM2008, sin bosque ni edificios (FABDEM v1-2)",
                   "inicio": "2011-01-01T00:00:00", "fin": "2015-12-31T23:59:59",
                   "archivos_meta": [os.path.join(os.path.dirname(fab), "FABDEM_V1-2_fuente_y_licencia.txt"),
                                     os.path.join(os.path.dirname(fab), "FABDEM_v1-2_Entre_Rios.json")],
                   "nota": "Copernicus DEM GLO-30 con el dosel y los edificios quitados (aprendizaje automatico). "
                           "Para compararlo con LiDAR, las cotas GEDI e ICESat-2 se pasan a EGM2008 "
                           "(00_COMUN/alturas_lidar_egm2008.py)."}),
        ("serie", {"etiqueta": "CCI_Biomass_v7_AGB", "tipo": "ESA_CCI_BIOMASS_v7", "cita": CITA_CCI,
                   "capas": [("AGB_%s" % a, os.path.join("CCI_BIOMASS", "v7.0", "{sitio}", "{sitio}_CCI_AGB_%s_v7.0.tif" % a))
                             for a in anios_cci] +
                            [("AGB_SD_%s" % a, os.path.join("CCI_BIOMASS", "v7.0", "{sitio}", "{sitio}_CCI_AGB_SD_%s_v7.0.tif" % a))
                             for a in anios_cci],
                   "unidad": "Mg/ha", "desc": "{nb}: biomasa aerea (AGB) o su desvio estandar (AGB_SD), Mg/ha",
                   "nodata": None, "inicio": "2010-01-01T00:00:00", "fin": "2024-12-31T23:59:59",
                   "archivos_meta": [os.path.join("CCI_BIOMASS", "LEEME_CCI_BIOMASS_sitios.md")],
                   "nota": "CCI asigna biomasa a pajonales y campos agricolas; en Federal la subestima; la caida "
                           "2010 -> 2015 es un cambio de sensor, no del terreno (ver LEEME_CCI_BIOMASS_sitios.md)."}),
        ("serie", {"etiqueta": "MapBiomas_cobertura_1985_2025", "tipo": "MAPBIOMAS_AR_C3_COBERTURA",
                   "cita": CITA_MAPBIOMAS, "leyenda": LEYENDA_MAPBIOMAS_C3,
                   "capas": [("cobertura_%d" % a, os.path.join(mb, "01_Cobertura",
                              "Entre_Rios_integration-argentina_classification_%d.tif" % a)) for a in range(1985, 2026)],
                   "desc": "{nb}: clase de cobertura y uso del suelo (codigo de la Coleccion 3, ver leyenda)",
                   "inicio": "1985-01-01T00:00:00", "fin": "2025-12-31T23:59:59", "archivos_meta": leeme_mb,
                   "nota": "Producto de terceros hecho con Landsat: sirve para contextualizar y estratificar, "
                           "nunca como verdad de campo (Tp4)."}),
        ("serie", {"etiqueta": "MapBiomas_perdida_veg_1987_2025", "tipo": "MAPBIOMAS_AR_C3_PERDIDA_VEG_SEC",
                   "cita": CITA_MAPBIOMAS, "leyenda": LEYENDA_MAPBIOMAS_PERDIDA,
                   "capas": [("perdida_veg_%d" % a, os.path.join(mb, "03_Perdida_y_vegetacion_secundaria",
                              "Entre_Rios_deforestation_secondary_vegetation-argentina_classification_%d.tif" % a))
                             for a in range(1987, 2026)],
                   "desc": "{nb}: perdida y vegetacion secundaria (codigos 1 a 7, ver leyenda)",
                   "inicio": "1987-01-01T00:00:00", "fin": "2025-12-31T23:59:59", "archivos_meta": leeme_mb}),
        ("serie", {"etiqueta": "MapBiomas_fuego_anual_1999_2025", "tipo": "MAPBIOMAS_AR_FUEGO_C1_ANUAL",
                   "cita": CITA_MAPBIOMAS,
                   "capas": [("quemado_%d" % a, os.path.join(mb, "04_Fuego", "area_anual",
                              "Entre_Rios_annual_burned-argentina_burned_area_%d.tif" % a)) for a in range(1999, 2026)],
                   "desc": "{nb}: 1 = quemado en el anio, 0 = no quemado o fuera de Entre Rios",
                   "grilla_de": grilla_4326, "nota": nota_3857,
                   "inicio": "1999-01-01T00:00:00", "fin": "2025-12-31T23:59:59", "archivos_meta": leeme_mb}),
        ("serie", {"etiqueta": "MapBiomas_fuego_mes_1999_2025", "tipo": "MAPBIOMAS_AR_FUEGO_C1_MES",
                   "cita": CITA_MAPBIOMAS,
                   "capas": [("mes_quema_%d" % a, os.path.join(mb, "04_Fuego", "mes_quema",
                              "Entre_Rios_monthly_burned-argentina_burned_monthly_%d.tif" % a)) for a in range(1999, 2026)],
                   "desc": "{nb}: mes de la quema (1 a 12); 0 = sin quema",
                   "grilla_de": grilla_4326, "nota": nota_3857,
                   "inicio": "1999-01-01T00:00:00", "fin": "2025-12-31T23:59:59", "archivos_meta": leeme_mb}),
        ("serie", {"etiqueta": "MapBiomas_fuego_frecuencia_1999_2025", "tipo": "MAPBIOMAS_AR_FUEGO_C1_FRECUENCIA",
                   "cita": CITA_MAPBIOMAS,
                   "capas": [("frecuencia_1999_2025", os.path.join(mb, "04_Fuego", "frecuencia",
                              "Entre_Rios_frequency_burned-argentina_fire_frequency_1999_2025.tif"))],
                   "desc": "{nb}: cantidad de anios con quema entre 1999 y 2025",
                   "grilla_de": grilla_4326, "nota": nota_3857,
                   "inicio": "1999-01-01T00:00:00", "fin": "2025-12-31T23:59:59", "archivos_meta": leeme_mb}),
        ("serie", {"etiqueta": "MapBiomas_fuego_ultimo_anio_2025", "tipo": "MAPBIOMAS_AR_FUEGO_C1_ULTIMO",
                   "cita": CITA_MAPBIOMAS,
                   "capas": [("ultimo_anio_quema", os.path.join(mb, "04_Fuego", "ultimo_anio",
                              "Entre_Rios_year_last_fire-argentina_year_last_fire_2025.tif"))],
                   "desc": "{nb}: ultimo anio con quema hasta 2025; 0 = sin quema",
                   "inicio": "1999-01-01T00:00:00", "fin": "2025-12-31T23:59:59", "archivos_meta": leeme_mb}),
    ]


def leer_ign_mde(sitio, cfg, nombre):
    """MDE-Ar 5 m del IGN (teselas .img por hoja 1:50 000): mosaico de las teselas que tocan el sitio."""
    import rasterio
    from rasterio.coords import disjoint_bounds

    carpeta = os.path.join(cfg.get("raiz", ORIGINALES), cfg["carpeta"])
    o, s_, e, n = SITIOS[sitio]["bbox"]
    teselas = []
    for r in sorted(glob.glob(os.path.join(carpeta, "*.img"))):
        with rasterio.open(r) as x:
            if not disjoint_bounds(x.bounds, (o, s_, e, n)):
                teselas.append(r)
    if not teselas:
        raise Falta("No hay teselas del MDE-Ar 5 m del IGN sobre %s en %s" % (sitio, carpeta))
    arr, tr, crs, nd = mosaico(teselas, sitio)
    arr = arr.astype("float32")
    arr[(arr < -1e30) | ~np.isfinite(arr)] = np.nan
    p = Producto(nombre)
    p.banda("elevacion_IGN_5m", arr, "m", "Elevacion del MDE-Ar aerofotogrametrico de 5 m del IGN (superficie: "
            "incluye vegetacion y construcciones)", nodata=float("nan"))
    p.transform, p.crs_wkt = tr, _wkt(crs)
    p.metadatos = {"teselas_IGN": ", ".join(os.path.basename(t) for t in teselas), "carpeta_original": carpeta}
    for x in glob.glob(os.path.join(carpeta, "*.pdf")):
        p.archivos_meta.append(x)
    p.inicio = cfg.get("fecha", "")
    p.tipo = "IGN_MDE_AR_5M"
    p.cita = ("Instituto Geografico Nacional (IGN), Argentina. Modelo Digital de Elevaciones MDE-Ar, aerofotogrametrico "
              "5 m, hojas %s. %s. "
              "https://www.ign.gob.ar/NuestrasActividades/Geodesia/ModeloDigitalElevaciones/Introduccion"
              % (", ".join(os.path.splitext(os.path.basename(t))[0] for t in teselas),
                 cfg.get("origen", "Archivo del curso SAR CEREGEO 2023")))
    p.recorte = _doc_recorte(sitio, "Mosaico de las teselas originales (.img) que tocan el sitio, en su grilla nativa "
                             "(EPSG:4326, ~5 m). Referencia vertical: la del producto del IGN (ver su documentacion).")
    return p


def _cobertura_poligono(vertices, sitio, n=120):
    """Porcentaje del rectangulo del sitio dentro del poligono (lon, lat) y centro de la parte cubierta.
    Se cuenta en una grilla de n x n puntos (sin dependencias)."""
    o, s_, e, nn = SITIOS[sitio]["bbox"] if isinstance(sitio, str) else sitio
    vx = np.array([v[0] for v in vertices], "float64")
    vy = np.array([v[1] for v in vertices], "float64")
    X, Y = np.meshgrid(np.linspace(o, e, n), np.linspace(s_, nn, n))
    dentro = np.zeros(X.shape, bool)
    j = len(vx) - 1
    for i in range(len(vx)):                       # rayo horizontal (par/impar)
        cruza = ((vy[i] > Y) != (vy[j] > Y)) & (X < (vx[j] - vx[i]) * (Y - vy[i]) / (vy[j] - vy[i] + 1e-300) + vx[i])
        dentro ^= cruza
        j = i
    if not dentro.any():
        return 0.0, None
    return 100.0 * dentro.mean(), (float(X[dentro].mean()), float(Y[dentro].mean()))


def _huella_kml(carpeta):
    """Poligono (lon, lat) de la huella del producto, del .kml que viene con la escena (COSMO-SkyMed)."""
    for k in glob.glob(os.path.join(carpeta, "*.kml")):
        t = open(k, encoding="utf-8", errors="replace").read()
        for c in re.findall(r"<coordinates>(.*?)</coordinates>", t, re.S):
            v = [float(x) for x in re.split(r"[,\s]+", c.strip()) if x]
            pts = list(zip(v[0::3], v[1::3]))
            if len(pts) >= 4:
                return pts
    return None


def leer_snap_nativo(sitio, cfg, nombre):
    """Producto crudo que SNAP lee de fabrica (COSMO-SkyMed, SAOCOM, Sentinel-1 SLC/GRD...).
    El recorte lo hace gpt Subset con copyMetadata=true, en la geometria original del
    producto (sin proyectar): asi conserva el Abstracted_Metadata para procesarlo en clase."""
    cand = sorted(glob.glob(os.path.join(cfg.get("raiz", ORIGINALES), cfg["patron"]), recursive=True))
    if not cand:
        raise Falta("No esta el producto %s" % cfg["patron"])
    p = Producto(nombre)
    p._snap_fuente = cand[0]
    p.tipo = cfg.get("tipo", "SNAP")
    p.cita = cfg["cita"]
    p.inicio = cfg.get("fecha", "")
    p.recorte = _doc_recorte(sitio, "Recorte hecho por SNAP (gpt Subset, copyMetadata=true) en la geometria "
                             "original del producto, sin proyectar: se calibra, se filtra y se geocodifica en "
                             "SNAP en clase. Por eso no hay GeoTIFF de este producto.")
    p.recorte["archivo_original"] = cand[0]
    carpeta = os.path.dirname(cand[0])
    huella = _huella_kml(carpeta)
    if huella and "cobertura_minima" in cfg:
        pc, centro = _cobertura_poligono(huella, sitio)
        if pc < cfg["cobertura_minima"]:
            raise Falta("la escena cubre el %.0f %% del sitio %s (minimo pedido: %d %%)" % (pc, sitio, cfg["cobertura_minima"]))
        p.recorte["cobertura_del_sitio"] = "%.0f %% del sitio %s (huella del .kml de la escena)" % (pc, sitio)
        p.caja_control = (centro[0] - .01, centro[1] - .01, centro[0] + .01, centro[1] + .01)
    p.archivos_meta = [x for x in glob.glob(os.path.join(carpeta, "*.xml")) + glob.glob(os.path.join(carpeta, "*.txt"))
                       + glob.glob(os.path.join(carpeta, "*.kml"))]
    return p


def dim_con_gpt(p, carpeta, gpt, sitio):
    o, s_, e, n = SITIOS[sitio]["bbox"]
    wkt = "POLYGON((%f %f, %f %f, %f %f, %f %f, %f %f))" % (o, n, e, n, e, s_, o, s_, o, n)
    os.makedirs(carpeta, exist_ok=True)
    dim = os.path.join(carpeta, p.nombre + ".dim")
    orden = [gpt, "Subset", "-Ssource=%s" % p._snap_fuente, "-PgeoRegion=%s" % wkt, "-PcopyMetadata=true",
             "-t", dim, "-f", "BEAM-DIMAP"]
    print("    SNAP: gpt Subset de %s" % os.path.basename(p._snap_fuente))
    r = subprocess.run(orden, capture_output=True, text=True, errors="replace")
    if r.returncode != 0 or not os.path.exists(dim):
        reg = os.path.join(carpeta, "_registro_gpt_%s.txt" % p.nombre)
        with open(reg, "w", encoding="utf-8") as f:
            f.write("ORDEN: %s\nCODIGO: %s\nSALIDA:\n%s\nERRORES:\n%s\n" % (orden, r.returncode, r.stdout, r.stderr))
        raise RuntimeError("gpt Subset fallo; detalle en %s" % reg)
    nombres = [x.findtext("BAND_NAME") for x in ET.parse(dim).getroot().iter("Spectral_Band_Info")]
    virt = []
    for nb in nombres:
        if (nb.startswith("Intensity_") or nb.startswith("Sigma0_") or nb.startswith("Gamma0_")) \
                and not nb.endswith("_db") and (nb + "_db") not in nombres:
            virt.append(dict(nombre=nb + "_db", expr="%s > 0 ? 10*log10(%s) : NaN" % (nb, nb), unidad="dB",
                             desc="%s en dB (banda virtual)" % nb, valida="%s > 0" % nb))
    rec = dict(p.recorte)
    rec.update(programa=PROGRAMA, fecha=_dt.datetime.now().strftime("%d/%m/%Y %H:%M"), fuente=p.cita)
    agregar_virtuales_a_dim(dim, virt, rec)
    return dim


# ---------------------------------------------------------------------------
# BIOMASS (ESA), banda P
# ---------------------------------------------------------------------------
BIOMASS = os.path.join(ORIGINALES, "BIOMASS")
CITA_BIOMASS = "ESA. BIOMASS, radar de apertura sintetica en banda P (435 MHz). ESA MAAP: https://catalog.maap.eo.esa.int"


def _carpeta_biomass(coleccion, producto):
    c = os.path.join(BIOMASS, coleccion, producto)
    if not os.path.exists(os.path.join(c, ".completo")):
        raise Falta("No esta (o no termino de bajar) el producto BIOMASS %s" % producto)
    return c


def leer_biomass_dgm(sitio, cfg, nombre):
    """BIOMASS L1B DGM: detectado y llevado a rango en el terreno, SIN proyectar al mapa.
    El producto trae la amplitud de beta0 (|S|) de HH, HV, VH y VV; aqui se pasa a gamma0
    lineal con el angulo de incidencia de la tabla del producto (gamma0 = beta0 x tan(theta)),
    para compararlo con Sentinel-1 RTC y NISAR GCOV, que vienen en gamma0."""
    import h5py
    import rasterio
    from rasterio.windows import Window
    from scipy.interpolate import RegularGridInterpolator

    carp = _carpeta_biomass("BiomassLevel1b", cfg["producto"])
    tif = glob.glob(os.path.join(carp, "measurement", "*_i_abs.tif*"))[0]
    annot = glob.glob(os.path.join(carp, "annotation", "*_annot.xml"))[0]
    lut = glob.glob(os.path.join(carp, "annotation", "*_lut.nc"))[0]
    principal = [x for x in glob.glob(os.path.join(carp, "*.xml"))][0]
    kml = glob.glob(os.path.join(carp, "preview", "*_map.kml"))
    txt = open(annot, encoding="utf-8").read()

    def val(etq):
        return re.search(r"<%s[^>]*>([^<]+)<" % etq, txt).group(1).strip()
    dt = float(val("azimuthTimeInterval"))
    gs = float(val("rangePixelSpacing"))
    coef = [float(v) for v in val("groundToSlantCoefficients").split()]
    nl, ns = int(val("numberOfLines")), int(val("numberOfSamples"))
    cantidad = val("pixelQuantity")
    if cantidad != "Beta-Nought" or val("pixelRepresentation") != "Abs":
        raise RuntimeError("BIOMASS DGM con %s / %s: este lector espera amplitud de beta0" % (cantidad, val("pixelRepresentation")))
    with h5py.File(lut, "r") as nc:                 # el .nc del producto es NetCDF-4 (HDF5)
        ta = nc["relativeAzimuthTimeRGC"][:].astype("float64")
        tr = nc["slantRangeTimeRGC"][:].astype("float64")

        def grilla(v):
            g = nc[v][:].astype("float64")
            fv = nc[v].attrs.get("_FillValue")
            if fv is not None:
                g[g == float(np.ravel(fv)[0])] = np.nan
            return RegularGridInterpolator((ta, tr), g, bounds_error=False, fill_value=np.nan)
        i_lat, i_lon, i_inc = grilla("geometry/latitude"), grilla("geometry/longitude"), grilla("geometry/incidenceAngle")

    def tiempos(f, c):
        # fila -> tiempo de acimut relativo; columna -> distancia en el terreno -> tiempo de rango (polinomio del producto)
        g = np.asarray(c, dtype="float64") * gs
        return np.column_stack([(np.asarray(f, dtype="float64") * dt).ravel(),
                                sum(k * g.ravel() ** i for i, k in enumerate(coef))])
    ff, cc = np.meshgrid(np.arange(0, nl, 10), np.arange(0, ns, 10), indexing="ij")
    t = tiempos(ff, cc)
    la, lo = i_lat(t).reshape(ff.shape), i_lon(t).reshape(ff.shape)
    o, s_, e, n = SITIOS[sitio]["bbox"]
    dentro = (lo >= o) & (lo <= e) & (la >= s_) & (la <= n)
    if not dentro.any():
        raise Falta("El producto BIOMASS %s no cubre %s" % (cfg["producto"], sitio))
    r0, r1 = max(int(ff[dentro].min()) - 10, 0), min(int(ff[dentro].max()) + 11, nl)
    c0, c1 = max(int(cc[dentro].min()) - 10, 0), min(int(cc[dentro].max()) + 11, ns)
    with rasterio.open(tif) as src:
        amp = src.read(window=Window(c0, r0, c1 - c0, r1 - r0)).astype("float32")
        pols = src.tags().get("PolarisationsSequence", "HH HV VH VV").split()
        nd = src.nodata if src.nodata is not None else -9999.0
    alto, ancho = amp.shape[1:]
    # Orientacion de mapa (norte arriba, oeste a la izquierda): en pasada ascendente la primera
    # fila es la del sur y, con la mira de BIOMASS, la primera columna es la del este. Se da vuelta
    # el recorte (solo se reordenan filas y columnas, sin remuestrear); f_orig y c_orig llevan
    # del pixel del recorte al pixel del producto original.
    t = tiempos([r0, r1 - 1, r0], [c0, c0, c1 - 1])
    la3, lo3 = i_lat(t), i_lon(t)
    inv_f, inv_c = bool(la3[1] > la3[0]), bool(lo3[2] < lo3[0])

    def f_orig(f):
        return (r1 - 1 - np.asarray(f, dtype="float64")) if inv_f else (r0 + np.asarray(f, dtype="float64"))

    def c_orig(c):
        return (c1 - 1 - np.asarray(c, dtype="float64")) if inv_c else (c0 + np.asarray(c, dtype="float64"))
    if inv_f:
        amp = amp[:, ::-1, :]
    if inv_c:
        amp = amp[:, :, ::-1]
    amp = np.ascontiguousarray(amp)
    F, C = np.mgrid[0:alto, 0:ancho]
    inc = i_inc(tiempos(f_orig(F), c_orig(C))).reshape(alto, ancho).astype("float32")
    del F, C
    tan = np.tan(np.radians(inc))
    p = Producto(nombre)
    for k, pol in enumerate(pols):
        a = amp[k]
        ok = np.isfinite(a) & (a != nd) & (a > 0) & np.isfinite(tan)
        g = np.zeros(a.shape, "float32")
        g[ok] = a[ok] ** 2 * tan[ok]
        p.banda("Gamma0_" + pol, g, "intensity",
                "gamma0 %s LINEAL = (amplitud de beta0 del producto)^2 x tan(angulo de incidencia); 0 = sin dato" % pol)
    del amp
    inc[~np.isfinite(inc)] = np.nan
    p.banda("incidenceAngle", inc, "deg", "Angulo de incidencia sobre el elipsoide (tabla LUT del producto, "
            "interpolada a cada pixel). sigma0 = gamma0 x cos(angulo)", nodata=float("nan"))
    agregar_db_y_cociente(p, "Gamma0_HH", "Gamma0_HV", "HH", "HV", "gamma0")
    for b, pol in (("Gamma0_VH", "VH"), ("Gamma0_VV", "VV")):
        if b in [x["nombre"] for x in p.bandas]:
            p.virtual(b + "_db", "%s > 0 ? 10*log10(%s) : NaN" % (b, b),
                      (lambda nb: (lambda pr: db(pr.datos(nb))))(b), "dB",
                      "gamma0 %s en dB (banda virtual: 10*log10 de la banda lineal)" % pol, "%s > 0" % b)
    if "Gamma0_VH" in [x["nombre"] for x in p.bandas]:
        # El canal HV de BIOMASS trae interferencia de radiofrecuencia que ESA detecta y no corrige
        # (rfiCorrectionFlag = false): el RGB usa la VH, que por reciprocidad mide lo mismo y llega limpia.
        p.virtual("HH_VH_cociente_db", "(Gamma0_HH > 0 && Gamma0_VH > 0) ? 10*log10(Gamma0_HH/Gamma0_VH) : NaN",
                  lambda pr: db(_cociente(pr.datos("Gamma0_HH"), pr.datos("Gamma0_VH"))), "dB",
                  "Cociente HH/VH en dB = Gamma0_HH_db - Gamma0_VH_db (el HV trae RFI de origen)",
                  "Gamma0_HH > 0 && Gamma0_VH > 0")
        p.rgb = ("Gamma0_HH_db", "Gamma0_VH_db", "HH_VH_cociente_db", "HH", "VH")
    # geocodificacion: grillas de enlace 21 x 21 (SNAP) y 11 x 11 puntos de control (GeoTIFF), de la LUT del producto
    nx = ny = 21
    paso_x, paso_y = (ancho - 1) / (nx - 1), (alto - 1) / (ny - 1)
    gc, gf = np.meshgrid(np.arange(nx) * paso_x, np.arange(ny) * paso_y)
    t = tiempos(f_orig(gf), c_orig(gc))
    p.tie = {"latitude": i_lat(t).reshape(ny, nx), "longitude": i_lon(t).reshape(ny, nx),
             "paso_x": paso_x, "paso_y": paso_y}
    if not (np.isfinite(p.tie["latitude"]).all() and np.isfinite(p.tie["longitude"]).all()):
        raise RuntimeError("La LUT del producto no cubre todo el recorte (grillas de enlace con huecos)")
    # control de SNAP en el centro del recorte (no en el del sitio: la franja puede cubrir solo una parte)
    lo_c, la_c = float(p.tie["longitude"][ny // 2, nx // 2]), float(p.tie["latitude"][ny // 2, nx // 2])
    p.caja_control = (lo_c - .01, la_c - .01, lo_c + .01, la_c + .01)
    p.cobertura = _cobertura_poligono(list(zip(p.tie["longitude"][0, :].tolist() + p.tie["longitude"][:, -1].tolist()
                                               + p.tie["longitude"][-1, ::-1].tolist() + p.tie["longitude"][::-1, 0].tolist(),
                                               p.tie["latitude"][0, :].tolist() + p.tie["latitude"][:, -1].tolist()
                                               + p.tie["latitude"][-1, ::-1].tolist() + p.tie["latitude"][::-1, 0].tolist())),
                                      sitio)
    gc, gf = np.meshgrid(np.linspace(0, ancho - 1, 11), np.linspace(0, alto - 1, 11))
    t = tiempos(f_orig(gf), c_orig(gc))
    p.gcps = [(float(f), float(c), float(x), float(y), 0.0)
              for f, c, x, y in zip(gf.ravel(), gc.ravel(), i_lon(t), i_lat(t))]
    p.inicio, p.fin = val("firstLineAzimuthTime"), val("lastLineAzimuthTime")
    m = re.search(r"BIO_(S\d)_DGM__1S_.*_(M\d\d)_(C\d\d)_(T\d{3})_(F\d{3})_", cfg["producto"])
    franja, fase, ciclo, traza, cuadro = m.groups() if m else ("?",) * 5
    p.tipo = "BIOMASS_L1B_DGM"
    p.cita = ("ESA. BIOMASS banda P (435 MHz), L1B DGM (detectado, rango en el terreno), HH HV VH VV, %s, "
              "franja %s, traza %s, cuadro %s, fase %s ciclo %s, pasada %s. Producto %s. ESA MAAP: "
              "https://catalog.maap.eo.esa.int" % (p.inicio[:10], franja, traza[1:], cuadro[1:], fase[1:], ciclo[1:],
                                                   val("orbitPass").lower(), cfg["producto"]))
    p.metadatos = {"producto": xml_a_arbol(principal), "anotacion": xml_a_arbol(annot)}
    p.archivos_meta = [principal, annot] + kml
    p.recorte = _doc_recorte(sitio, "Geometria de rango en el terreno (DGM): NO esta proyectado al mapa. El producto "
                             "trae la amplitud de beta0; gamma0 = amplitud^2 x tan(incidencia), con la incidencia de la "
                             "tabla LUT del producto (elipsoide: sin correccion por pendiente, Federal es plano). "
                             "Geocodificacion por puntos de enlace (grillas latitude/longitude de 21 x 21 tomadas de la "
                             "LUT del producto); en SNAP se proyecta con Raster > Geometric > Reprojection. El GeoTIFF "
                             "lleva 121 puntos de control y QGIS lo ubica con ellos.")
    p.recorte["ventana_en_el_original_filas"] = "%d a %d" % (r0, r1)
    p.recorte["ventana_en_el_original_columnas"] = "%d a %d" % (c0, c1)
    p.recorte["pixel_original"] = "%g m en rango (terreno) x %s m en acimut" % (gs, val("azimuthPixelSpacing"))
    p.recorte["orientacion"] = ("recorte dado vuelta para verlo como un mapa (norte arriba, oeste a la izquierda): "
                                "%s%s" % ("filas invertidas" if inv_f else "filas como el original",
                                          ", columnas invertidas" if inv_c else ", columnas como el original"))
    p.recorte["archivo_original"] = tif
    p.recorte["cobertura_del_sitio"] = "%.0f %% del sitio %s" % (p.cobertura[0], sitio) + (
        "" if p.cobertura[0] >= 99 else " (la franja cubre una parte; el resto del sitio esta en el otro recorte "
                                        "BIOMASS L1B del practico)")
    if cfg.get("mapa"):
        # version reproyectada: latitud y longitud de CADA pixel desde la LUT del producto (no un ajuste a
        # puntos de control) y remuestreo bilineal a la grilla del curso
        geo = np.empty((2, alto, ancho), "float64")
        for f0 in range(0, alto, 400):
            ff_, cc_ = np.mgrid[f0:min(f0 + 400, alto), 0:ancho]
            t = tiempos(f_orig(ff_), c_orig(cc_))
            geo[0, f0:f0 + ff_.shape[0]] = i_lon(t).reshape(ff_.shape)
            geo[1, f0:f0 + ff_.shape[0]] = i_lat(t).reshape(ff_.shape)
        _dgm_a_mapa(p, geo, cfg["mapa"], float(cfg.get("pixel", 25)))
    return p


def _dgm_a_mapa(p, geo, crs_destino, pixel):
    """Lleva un recorte BIOMASS L1B DGM (geometria de radar) a una grilla proyectada, con la ubicacion de cada
    pixel (arreglo de geolocalizacion de GDAL). Las bandas lineales se remuestrean en lineal (bilineal)."""
    from rasterio.crs import CRS
    from rasterio.enums import Resampling
    from rasterio.transform import Affine
    from rasterio.warp import reproject, transform as _transformar

    dst = CRS.from_string(crs_destino)
    ok = np.isfinite(geo[0]) & np.isfinite(geo[1])
    xs, ys = _transformar("EPSG:4326", dst, geo[0][ok][::50].tolist(), geo[1][ok][::50].tolist())
    o, e = np.floor(min(xs) / pixel) * pixel, np.ceil(max(xs) / pixel) * pixel
    s_, n = np.floor(min(ys) / pixel) * pixel, np.ceil(max(ys) / pixel) * pixel
    tr = Affine(pixel, 0, o, 0, -pixel, n)
    ancho, alto = int(round((e - o) / pixel)), int(round((n - s_) / pixel))
    for b in p.bandas:
        nd = b["nodata"]
        sal = np.full((alto, ancho), nd, "float32")
        reproject(b["datos"].astype("float32"), sal, src_crs=CRS.from_epsg(4326), src_geoloc_array=geo,
                  src_nodata=nd, dst_transform=tr, dst_crs=dst, dst_nodata=nd, resampling=Resampling.bilinear)
        b["datos"] = sal
    p.ancho, p.alto = ancho, alto
    p.transform, p.crs_wkt = tr, dst.to_wkt()
    p.tie = p.gcps = None
    p.tipo = "BIOMASS_L1B_DGM_reproyectado"
    p.recorte["pixel_y_proyeccion"] = "%s, pixel de %g m (remuestreo bilineal de gamma0 lineal)" % (crs_destino, pixel)
    p.recorte["nota"] = ("Recorte BIOMASS L1B DGM llevado al mapa: la latitud y la longitud de cada pixel salen de la "
                         "tabla LUT del producto (grillas latitude/longitude) y GDAL remuestrea con ese arreglo de "
                         "geolocalizacion, sin ajustar un polinomio a puntos de control. gamma0 = amplitud de beta0^2 x "
                         "tan(incidencia), con la incidencia del elipsoide (sin correccion por pendiente). Es el mismo "
                         "dato que el recorte en geometria de radar del mismo nombre sin _UTM21S.")


def _mosaico_alineado(capas, sitio):
    """Une teselas geocodificadas en la grilla del primer archivo, alineada a sus pixeles
    (sin corrimiento de medio pixel). capas = [(ruta, banda)]. Devuelve float32 con NaN."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.transform import Affine
    from rasterio.warp import reproject

    with rasterio.open(capas[0][0]) as s0:
        t0, crs = s0.transform, s0.crs
        rx, ry = s0.res
    o, s_, e, n = caja_nativa(sitio, crs)
    col0, col1 = int(np.floor((o - t0.c) / rx)), int(np.ceil((e - t0.c) / rx))
    fil0, fil1 = int(np.floor((t0.f - n) / ry)), int(np.ceil((t0.f - s_) / ry))
    tr = Affine(rx, 0, t0.c + col0 * rx, 0, -ry, t0.f - fil0 * ry)
    out = np.full((fil1 - fil0, col1 - col0), np.nan, "float32")
    for r, b in capas:
        with rasterio.open(r) as s:
            tmp = np.full(out.shape, np.nan, "float32")
            reproject(s.read(b).astype("float32"), tmp, src_transform=s.transform, src_crs=s.crs,
                      dst_transform=tr, dst_crs=crs, resampling=Resampling.nearest,
                      src_nodata=s.nodata if s.nodata is not None else -9999.0, dst_nodata=np.nan)
            out = np.where(np.isnan(out), tmp, out)
    return out, tr, crs


def leer_biomass_l2a(sitio, cfg, nombre):
    """BIOMASS L2A geocodificado (EPSG:4326, ~90 m): FH (altura del bosque) o GN
    (retrodispersion con el suelo cancelado). Si el sitio cae en dos cuadros, se unen."""
    import rasterio

    carps = []
    for x in cfg["productos"]:
        try:
            carps.append(_carpeta_biomass("BiomassLevel2a", x))
        except Falta:
            pass
    if not carps:
        raise Falta("No esta ningun producto BIOMASS L2A de %s" % cfg["etiqueta"])
    p = Producto(nombre)
    if cfg["tipo"] == "FH":
        fh = [glob.glob(os.path.join(c, "measurement", "*_i_fh.tif*"))[0] for c in carps]
        q = [x for c in carps for x in glob.glob(os.path.join(c, "measurement", "*_i_quality.tif*"))]
        a, tr, crs = _mosaico_alineado([(r, 1) for r in fh], sitio)
        p.banda("altura_bosque_FH", a, "m", "Altura del bosque (FH, L2A BIOMASS) en metros; NaN = sin dato",
                nodata=float("nan"))
        if len(q) == len(fh):
            a, _, _ = _mosaico_alineado([(r, 1) for r in q], sitio)
            p.banda("calidad_FH", a, "", "Calidad de la altura del bosque (0 a 100, del producto)", nodata=float("nan"))
        p.tipo = "BIOMASS_L2A_FP_FH"
        que = "L2A FP_FH (altura del bosque)"
    else:
        gn = [glob.glob(os.path.join(c, "measurement", "*_i_gn.tif*"))[0] for c in carps]
        with rasterio.open(gn[0]) as s:
            pols = [s.tags(i).get("POLARIMETRIC_INTERP", "B%d" % i) for i in range(1, s.count + 1)]
        for i, pol in enumerate(pols, 1):
            a, tr, crs = _mosaico_alineado([(r, i) for r in gn], sitio)
            a[~np.isfinite(a) | (a <= 0)] = 0.0
            p.banda("GN_" + pol, a, "intensity", "Retrodispersion %s LINEAL con el suelo cancelado (GN, L2A BIOMASS): "
                    "queda la senal del dosel; 0 = sin dato" % pol)
        agregar_db_y_cociente(p, "GN_HH", "GN_VH" if "VH" in pols else None, "HH", "VH", "retrodispersion GN")
        if "VV" in pols:
            p.virtual("GN_VV_db", "GN_VV > 0 ? 10*log10(GN_VV) : NaN", lambda pr: db(pr.datos("GN_VV")), "dB",
                      "Retrodispersion GN VV en dB (banda virtual)", "GN_VV > 0")
        p.tipo = "BIOMASS_L2A_FP_GN"
        que = "L2A FP_GN (retrodispersion con el suelo cancelado)"
    p.transform, p.crs_wkt = tr, _wkt(crs)
    md = {}
    for c in carps:
        for x in glob.glob(os.path.join(c, "*.xml")) + glob.glob(os.path.join(c, "annotation", "*_annot.xml")):
            md[_nombre_valido(os.path.basename(x))] = xml_a_arbol(x)
            p.archivos_meta.append(x)
        for x in glob.glob(os.path.join(c, "*.json")):
            md[_nombre_valido(os.path.basename(x))] = json_a_arbol(x)
            p.archivos_meta.append(x)
    p.metadatos = md
    m = re.search(r"_L2A_(\d{8})T\d+_(\d{8})T\d+_.*_(T\d{3})_", cfg["productos"][0])
    if m:
        p.inicio = "%s-%s-%sT00:00:00" % (m.group(1)[:4], m.group(1)[4:6], m.group(1)[6:])
        p.fin = "%s-%s-%sT23:59:59" % (m.group(2)[:4], m.group(2)[4:6], m.group(2)[6:])
    p.cita = ("ESA. BIOMASS banda P (435 MHz), %s, pila del %s al %s, traza %s, cuadros %s. ESA MAAP: "
              "https://catalog.maap.eo.esa.int" % (que, p.inicio[:10], p.fin[:10], m.group(3)[1:] if m else "?",
                                                   ", ".join(re.search(r"_(F\d{3})_", os.path.basename(c)).group(1)[1:]
                                                             for c in carps)))
    p.recorte = _doc_recorte(sitio, "Producto geocodificado por ESA (EPSG:4326, pixel nativo). %s Valores sin dato "
                             "(-9999) pasados a NaN o 0." % ("Dos cuadros unidos en la grilla del primero (vecino mas "
                                                              "proximo)." if len(carps) > 1 else ""))
    return p

LECTORES = {"nisar_gcov": leer_nisar_gcov, "novasar_grd": leer_novasar_grd, "s1_rtc": leer_s1_rtc,
            "alos2_mosaico": leer_alos2_mosaico, "s2_l2a": leer_s2_l2a, "copdem": leer_copdem,
            "landsat_l2": leer_landsat_l2, "fusion_landsat_s2": leer_fusion_landsat_s2,
            "cbers_ms": leer_cbers_ms, "cbers_ps": leer_cbers_ps, "embeddings": leer_embeddings,
            "alos1_rtc": leer_alos1_rtc, "jrc_gsw": leer_jrc_gsw, "snap_nativo": leer_snap_nativo, "ign_mde": leer_ign_mde,
            "serie": leer_serie, "biomass_dgm": leer_biomass_dgm, "biomass_l2a": leer_biomass_l2a}


# ---------------------------------------------------------------------------
# Control: SNAP abre cada .dim
# ---------------------------------------------------------------------------
def control_snap(gpt, dims, tmp, sitio):
    res = {}
    os.makedirs(tmp, exist_ok=True)
    for d in dims:
        salida = os.path.join(tmp, "control_" + os.path.basename(d))
        r = subprocess.run([gpt, "Subset", "-Ssource=%s" % d, "-Pregion=0,0,64,64", "-PcopyMetadata=true",
                            "-t", salida, "-f", "BEAM-DIMAP"], capture_output=True, text=True, errors="replace")
        ok = r.returncode == 0 and os.path.exists(salida)
        if not ok:
            res[d] = "SNAP NO lo abre: %s" % (r.stderr or r.stdout)[-400:]
            continue
        # la geocodificacion: recorte por coordenadas de un cuadrado de 0,02 grados en el centro del sitio
        o, s_, e, n = SITIOS[sitio]["bbox"] if isinstance(sitio, str) else sitio
        cx, cy = (o + e) / 2, (s_ + n) / 2
        wkt = "POLYGON((%f %f, %f %f, %f %f, %f %f, %f %f))" % (cx - .01, cy + .01, cx + .01, cy + .01,
                                                            cx + .01, cy - .01, cx - .01, cy - .01, cx - .01, cy + .01)
        salida2 = os.path.join(tmp, "geo_" + os.path.basename(d))
        r = subprocess.run([gpt, "Subset", "-Ssource=%s" % d, "-PgeoRegion=%s" % wkt, "-t", salida2,
                            "-f", "BEAM-DIMAP"], capture_output=True, text=True, errors="replace")
        geo_ok = r.returncode == 0 and os.path.exists(salida2)
        if not geo_ok:
            reg = os.path.join(os.path.dirname(d), "_registro_control_%s.txt" % os.path.splitext(os.path.basename(d))[0])
            with open(reg, "w", encoding="utf-8") as f:
                f.write("SALIDA:\n%s\nERRORES:\n%s\n" % (r.stdout, r.stderr))
        res[d] = "SNAP lo abre bien y lo ubica en el mapa" if geo_ok else \
            "SNAP lo abre, pero NO lo pudo recortar por coordenadas (detalle en _registro_control_*.txt): %s" \
            % (r.stderr or r.stdout)[:300]
    shutil.rmtree(tmp, ignore_errors=True)
    return res


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Subsets de un practico para SNAP (.dim) y QGIS (GeoTIFF)")
    ap.add_argument("tp", choices=sorted(TRABAJOS))
    ap.add_argument("--confirmar", action="store_true", help="Arma los subsets (sin esto solo informa)")
    ap.add_argument("--solo", nargs="*", default=[], help="Solo estos tipos o etiquetas")
    ap.add_argument("--rehacer", action="store_true", help="Pisa los subsets ya armados")
    ap.add_argument("--salida", default="", help="Carpeta de salida (por defecto <Tp>\\02_Subsets_SNAP_QGIS)")
    ap.add_argument("--controlar", action="store_true",
                    help="Solo el control: SNAP abre y recorta por coordenadas cada .dim de SNAP_DIMAP")
    a = ap.parse_args()

    trabajo = TRABAJOS[a.tp]
    sitio = trabajo["sitio"]
    salida = a.salida or ruta_tp(a.tp, "02_Subsets_SNAP_QGIS")
    c_dim = os.path.join(salida, "SNAP_DIMAP")
    c_tif = os.path.join(salida, "QGIS_GeoTIFF")
    c_rgb = os.path.join(salida, "RGB_copol_cruzada_cociente")
    c_meta = os.path.join(salida, "Metadatos_originales")
    gpt = gpt_snap()
    print("Practico %s, sitio %s" % (a.tp, sitio))
    print("Salida  : %s" % salida)
    print("SNAP gpt: %s" % (gpt or "NO ENCONTRADO (NovaSAR quedara solo en GeoTIFF)"))
    print()
    if a.controlar:
        dims = sorted(glob.glob(os.path.join(c_dim, "*.dim")))
        print("Control de %d .dim con SNAP..." % len(dims))
        controles = control_snap(gpt, dims, os.path.join(salida, "_control_snap_tmp"), sitio)
        for d, r in controles.items():
            print("  %-60s %s" % (os.path.basename(d), r))
        escribir_leeme(a.tp, sitio, salida, [], controles, reemplazar_control=True)
        return
    informe, dims_propios, sitio_ctrl = [], [], {}
    # contexto (FABDEM, CCI Biomass, MapBiomas) del sitio del practico y de los otros sitios que trabaja
    otros = [(t, dict(c, sitio_prod=s2)) for s2 in trabajo.get("otros_sitios", []) for t, c in contexto(s2)]
    for tipo, cfg in trabajo["productos"] + contexto(sitio) + otros:
        etiqueta = cfg["etiqueta"]
        # sitio_prod: producto de otro sitio del mismo practico (p. ej. Parana - Diamante en el Tp10,
        # Delta medio en el Tp2 y el Tp3); el nombre lleva el sitio del producto
        s_p = cfg.get("sitio_prod", sitio)
        nombre = "%s_%s" % (s_p, etiqueta)
        if a.solo and tipo not in a.solo and etiqueta not in a.solo:
            continue
        hecho = os.path.exists(os.path.join(c_tif, nombre + ".tif")) or \
            (tipo == "snap_nativo" and os.path.exists(os.path.join(c_dim, nombre + ".dim")))
        if hecho and not a.rehacer:
            print("  %-34s ya armado (use --rehacer para pisarlo)" % nombre)
            informe.append((nombre, "ya armado", ""))
            continue
        try:
            p = LECTORES[tipo](s_p, cfg, nombre)
        except Falta as e:
            print("  %-34s FALTA: %s" % (nombre, e))
            informe.append((nombre, "FALTA", str(e)))
            continue
        except Exception as e:                       # noqa: BLE001  se informa y se sigue
            print("  %-34s ERROR al leer: %s" % (nombre, e))
            informe.append((nombre, "ERROR", str(e)[:300]))
            continue
        if tipo == "snap_nativo":
            print("  %-34s producto crudo para SNAP: %s" % (nombre, os.path.basename(p._snap_fuente)))
        else:
            print("  %-34s %d x %d px, bandas: %s%s" % (
                nombre, p.ancho, p.alto, ", ".join(b["nombre"] for b in p.bandas),
                (" + virtuales: " + ", ".join(v["nombre"] for v in p.virtuales)) if p.virtuales else ""))
        if not a.confirmar:
            informe.append((nombre, "disponible", p.cita))
            continue
        if tipo == "snap_nativo":
            try:
                if not gpt:
                    raise RuntimeError("falta SNAP (gpt)")
                d = dim_con_gpt(p, c_dim, gpt, s_p)
                print("    .dim (SNAP, geometria original; sin GeoTIFF): %s" % d)
                dims_propios.append(d)
                if getattr(p, "caja_control", None):
                    sitio_ctrl[d] = p.caja_control
                elif s_p != sitio:
                    sitio_ctrl[d] = s_p
                copiar_meta(p, c_meta)
                informe.append((nombre, "armado (solo .dim)", p.cita))
            except Exception as e:                   # noqa: BLE001
                print("    ERROR: %s" % e)
                informe.append((nombre, "ERROR", str(e)[:300]))
            continue
        try:
            reg = os.path.join(c_dim, "_registro_gpt_%s.txt" % nombre)
            if os.path.exists(reg):
                os.remove(reg)
            d = os.path.join(c_dim, nombre + ".dim")
            if tipo == "novasar_grd" and _dim_de_snap(d):
                # Recorte hecho en SNAP Desktop con el lector NovaSAR (complemento de la
                # comunidad, que gpt no carga): se conserva y solo se le agregan las bandas
                # virtuales y la documentacion del recorte.
                rec = dict(p.recorte)
                rec["nota"] = ("Recorte hecho en SNAP Desktop (Import > SAR Sensors > NOVASAR, complemento "
                               "NovaSAR Product Reader 1.2.4; Raster > Subset, %s). Conserva "
                               "Abstracted_Metadata y Original_Product_Metadata." % cfg.get("ventana", ""))
                rec.update(programa=PROGRAMA + " (solo agrego bandas virtuales)",
                           fecha=_dt.datetime.now().strftime("%d/%m/%Y %H:%M"), fuente=p.cita)
                agregar_virtuales_a_dim(d, [v for v in p.virtuales], rec)
                print("    .dim (hecho en SNAP Desktop, se le agregaron bandas virtuales): %s" % d)
            else:
                d = escribir_dim(p, c_dim)
                print("    .dim: %s" % d)
            dims_propios.append(d)
            # productos de otro sitio dentro del practico (zona CBERS, embeddings de otro sitio)
            if cfg.get("zona") in _ZONAS_CBERS:              # zona CBERS: se controla dentro de la zona
                sitio_ctrl[d] = tuple(_ZONAS_CBERS[cfg["zona"]]["caja"])
            elif cfg.get("sitio_emb") and cfg["sitio_emb"] != sitio:
                sitio_ctrl[d] = cfg["sitio_emb"]
            elif getattr(p, "caja_control", None):           # producto que cubre parte del sitio
                sitio_ctrl[d] = p.caja_control
            elif p.transform is not None and p.crs_wkt and (s_p != sitio or tipo == "nisar_gcov"):
                # control en el centro del producto (puede cubrir solo una parte del sitio)
                from rasterio.crs import CRS as _CRS
                from rasterio.warp import transform as _tr
                cx, cy = p.transform * (p.ancho / 2.0, p.alto / 2.0)
                lo_, la_ = _tr(_CRS.from_wkt(p.crs_wkt), "EPSG:4326", [cx], [cy])
                sitio_ctrl[d] = (lo_[0] - .01, la_[0] - .01, lo_[0] + .01, la_[0] + .01)
            elif s_p != sitio:
                sitio_ctrl[d] = s_p
            t = escribir_geotiff(p, c_tif)
            print("    GeoTIFF: %s (+ _metadatos.txt)" % t)
            for suf, arr3, desc in getattr(p, "extras", []):
                import rasterio
                from rasterio.crs import CRS
                rx = os.path.join(c_tif, "%s_%s.tif" % (p.nombre, suf))
                with rasterio.open(rx, "w", driver="GTiff", width=p.ancho, height=p.alto, count=arr3.shape[0],
                                   dtype=str(arr3.dtype), nodata=0, crs=CRS.from_wkt(p.crs_wkt),
                                   transform=p.transform, compress="deflate", tiled=True,
                                   photometric="RGB" if arr3.shape[0] == 3 else "MINISBLACK") as d:
                    d.write(arr3)
                    d.update_tags(DESCRIPCION=desc, FUENTE=p.cita)
                print("    %s: %s" % (suf, rx))
            r = escribir_rgb(p, c_rgb)
            if r:
                print("    RGB: %s (+ _RGB_8bit.tif)" % r)
            copiar_meta(p, c_meta)
            informe.append((nombre, "armado", p.cita))
        except Exception as e:                       # noqa: BLE001
            print("    ERROR: %s" % e)
            informe.append((nombre, "ERROR", str(e)[:300]))
        del p
    controles = {}
    if a.confirmar and gpt and dims_propios:
        print("\nControl: SNAP abre cada .dim escrito por este programa...")
        controles = control_snap(gpt, [d for d in dims_propios if d not in sitio_ctrl],
                                 os.path.join(salida, "_control_snap_tmp"), sitio)
        for d, st in sitio_ctrl.items():
            controles.update(control_snap(gpt, [d], os.path.join(salida, "_control_snap_tmp"), st))
        for d, r in controles.items():
            print("  %-60s %s" % (os.path.basename(d), r))
    if a.confirmar:
        escribir_leeme(a.tp, sitio, salida, informe, controles)
        print("\nLEEME: %s" % os.path.join(salida, "LEEME_subsets.md"))
    else:
        print("\nNo se escribio nada. Vuelva a correr con --confirmar.")


NOTAS_LEEME = {
    "Tp10": ("**Nombres:** los productos `B_CONCORDIA_CBERS4A_GRAN_PARANA_...` y "
             "`B_CONCORDIA_E_PARANA_DIAMANTE_AlphaEarth_...` cubren el sitio `E_PARANA_DIAMANTE` (Gran Parana); el prefijo "
             "`B_CONCORDIA_` es un resto del armado. No se renombran porque cada `.dim` apunta a su carpeta `.data` por nombre. "
             "Los productos agregados despues ya llevan el sitio en el nombre: `E_PARANA_DIAMANTE_BIOMASS_P_...` (banda P; "
             "los cuadros 182 y 183 del 03/06/2026 cubren juntos todo el sitio) y `E_PARANA_DIAMANTE_CSK_X_...` "
             "(COSMO-SkyMed X de octubre de 2018: las escenas estan centradas en Diamante y cubren solo el oeste del sitio) "
             "y `E_PARANA_DIAMANTE_NISAR_L_20260917` (57 % del sitio, la parte norte)."),
    "Tp9": ("**Franja D:** los productos `D_LAPAZ_VILLAGUAY_...` cubren la franja La Paz - Villaguay (~95 x 150 km). "
            "Ninguna franja BIOMASS la cubre sola: las cinco franjas L1B (17/09, 02/09 y 02/10/2026, traza 006; 23/03 y "
            "02/03/2026, traza 043) la cubren juntas en un 97 %; la del 17/09/2026 es la de la parte B de la guia. NISAR L "
            "cubre toda la franja en cada pasada (18/09 descendente y 17/09 ascendente). L2A en dos pilas: 17/09 al "
            "29/09/2026 (66 % de la franja) y 18/08 al 30/08 (48 %)."),
    "Tp2": ("**Delta medio:** los productos `DELTA_NISAR_...` (NISAR L y S del 30/09/2026; la S cubre el 16 % del sitio) y `DELTA_NISAR_BIOMASS_P_...` cubren el sitio `DELTA_NISAR` (sector medio del "
            "Delta, el recorte NISAR 2026, unos 135 x 97 km). Ninguna franja BIOMASS lo cubre sola: las cuatro franjas "
            "L1B (29/09 y 14/10/2026, traza 006; 23/03 y 13/04/2026, traza 043) lo cubren juntas. El L2A (traza 043, 23/11 "
            "al 05/12/2025, dos cuadros) cubre el 44 % del sitio: ninguna pila L2A lo cubre mas."),
}


def escribir_leeme(tp, sitio, salida, informe, controles, reemplazar_control=False):
    ruta = os.path.join(salida, "LEEME_subsets.md")
    previos, ctrl = {}, {}
    if os.path.exists(ruta):
        for linea in open(ruta, encoding="utf-8"):
            m = re.match(r"\| `([^`]+)` \| ([^|]+) \| (.*) \|$", linea.strip())
            if m and m.group(2).strip() != "ERROR":
                previos[m.group(1)] = (m.group(2).strip(), m.group(3).strip())
            m = re.match(r"- `([^`]+\.dim)`: (.*)$", linea.strip())
            if m and not reemplazar_control:
                ctrl[m.group(1)] = m.group(2)
    # los productos que ya no estan en disco (reemplazados) salen de la lista
    def _existe(nb):
        nb = nb[:-4] if nb.endswith(".dim") else nb
        return (os.path.exists(os.path.join(salida, "QGIS_GeoTIFF", nb + ".tif"))
                or os.path.exists(os.path.join(salida, "SNAP_DIMAP", nb + ".dim")))
    previos = {k: v for k, v in previos.items() if _existe(k)}
    ctrl = {k: v for k, v in ctrl.items() if _existe(k)}
    for d, r in controles.items():
        ctrl[os.path.basename(d)] = " ".join(r.split())
    for nombre, estado, texto in informe:
        if estado == "ya armado" and nombre in previos:
            continue
        previos[nombre] = (estado, " ".join(texto.replace("|", "/").split()))
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("# %s — subsets para SNAP y QGIS (sitio `%s`)\n\n" % (tp, sitio))
        f.write("Armado con `00_COMUN\\armar_subsets.py %s --confirmar` el %s.\n\n"
                % (tp, _dt.datetime.now().strftime("%d/%m/%Y %H:%M")))
        f.write("| Carpeta | Qué hay |\n|---|---|\n")
        f.write("| `SNAP_DIMAP` | Un `.dim` por producto: bandas **lineales** reales y bandas **virtuales en dB** "
                "(y el cociente co/cruzada en dB). Metadatos originales dentro del `.dim` "
                "(Metadata > Original_Product_Metadata) y el recorte en Metadata > Procesamiento_del_recorte |\n")
        f.write("| `QGIS_GeoTIFF` | Las mismas bandas, con las de dB como bandas reales, y `<nombre>_metadatos.txt` "
                "con todos los metadatos legibles (QGIS no muestra los de SNAP) |\n")
        f.write("| `RGB_copol_cruzada_cociente` | Sólo polarización dual: R = copolarizada, G = cruzada, "
                "B = cociente co/cruzada, en dB (`_RGB_dB.tif`) y en 8 bits con rangos fijos (`_RGB_8bit.tif`: "
                "R %g a %g dB, G %g a %g dB, B %g a %g dB; la banda P de BIOMASS, en cambio, con promedio 5 x 5 y "
                "estiramiento 2-98 %% por escena: sus colores no se comparan entre escenas) |\n" % (RANGOS_RGB["co"] + RANGOS_RGB["cruz"] + RANGOS_RGB["cociente"]))
        f.write("| `Metadatos_originales` | Copia sin tocar de los XML y JSON del proveedor |\n")
        f.write("| `LiDAR_<SITIO>` | Tablas LiDAR (las arma `00_COMUN\\exportar_lidar.py`) |\n\n")
        f.write("Píxel y proyección **nativos** de cada producto. El NovaSAR-1 GRD no está proyectado "
                "al mapa (geometría de rango en el terreno). Su `.dim` se recortó en SNAP Desktop con el lector "
                "NovaSAR (complemento NovaSAR Product Reader, que gpt no carga) y conserva el "
                "Abstracted_Metadata y el Original_Product_Metadata, para calibrar, filtrar y corregir por "
                "terreno en clase; el programa sólo le agregó las bandas virtuales. Si ese `.dim` no está, el "
                "programa escribe uno propio (sigma0 por la constante de calibración y ubicación por puntos de "
                "enlace, sin Abstracted_Metadata). El GeoTIFF se ubica en QGIS por sus puntos de control.\n\n")
        if tp in NOTAS_LEEME:
            f.write(NOTAS_LEEME[tp] + "\n\n")
        f.write("## Productos\n\n| Producto | Estado | Fuente o motivo |\n|---|---|---|\n")
        for nombre, (estado, texto) in previos.items():
            f.write("| `%s` | %s | %s |\n" % (nombre, estado, texto))
        if ctrl:
            f.write("\n## Control con SNAP (gpt abre cada .dim)\n\n")
            for d, r in ctrl.items():
                f.write("- `%s`: %s\n" % (d, r))


if __name__ == "__main__":
    main()
