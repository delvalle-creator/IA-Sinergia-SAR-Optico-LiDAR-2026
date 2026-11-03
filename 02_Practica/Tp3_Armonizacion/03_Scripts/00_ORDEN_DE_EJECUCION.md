# Tp3 — Orden de ejecución

Los scripts se corren desde esta carpeta, en el Miniforge Prompt:

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp3_Armonizacion\03_Scripts
```

| Paso | Script o herramienta | Marca | Qué hace | Entrada | Salida |
|---|---|---|---|---|---|
| 0 | `..\..\Tp1_Convergencia\03_Scripts\Tp1_05_buscar_lidar.py --solo_contar` | **AUXILIAR** (granulos **YA VIENEN HECHOS**) | Huellas GEDI y ATL08 del sitio con su validez | `<ORIGINALES>\LIDAR\<SITIO>\` | `Tp1_Convergencia\05_Resultados\03_Vectores\lidar_<SITIO>.gpkg` |
| 1 | `Tp3_01_cubo_comun.py` | **SE CORRE** | Cubo común: radar en lineal, óptico con SCL, MDE; diferencias de fecha | pila del Tp2, Sentinel-2 y GLO-30 (red) | `02_Subsets_SNAP_QGIS\<SITIO>_cubo_<pixel>m.tif`, `..._bandas.csv`, `05_Resultados\04_Tablas\<SITIO>_diferencias_de_fecha.csv` |
| 2 | revisión del cubo | **EN QGIS** | Grilla, bordes y máscara a la vista | el cubo | anotaciones |
| 3 | `Tp3_02_medir_corregistro.py` | **SE CORRE** (una vez por par) | Desplazamiento residual por correlación de fase sobre bordes | el cubo | `05_Resultados\04_Tablas\<SITIO>_corregistro_<mov>_vs_<ref>.csv` |
| 4 | `Tp3_03_lidar_en_el_cubo.py` | **SE CORRE** | Valores del cubo en cada huella válida y columna `plausible` | el cubo y `lidar_<SITIO>.gpkg` | `04_Tablas_de_trabajo\<SITIO>_huellas_con_cubo.csv`, `05_Resultados\03_Vectores\<SITIO>_huellas_con_cubo.gpkg` |
| 5 | gráfico rh98 frente a γ⁰ | **EN QGIS** | Lectura conjunta (sinergia) | `<SITIO>_huellas_con_cubo.gpkg` | figuras del grupo |
| 6 | `Tp3_04_contexto_y_huellas.py` | **SE CORRE** + QGIS y Orange | Contexto: MapBiomas, CCI Biomass, altura FH y banda P, del sitio y de cada huella | `QGIS_GeoTIFF\<SITIO>_MapBiomas_*`, `_CCI_*`, `_BIOMASS_P_*` y `<SITIO>_huellas_con_cubo.csv` | `05_Resultados\04_Tablas\<SITIO>_mapbiomas_*.csv`, `_contexto_*.csv`, `_huellas_por_clase_MapBiomas.csv`; `04_Tablas_de_trabajo\<SITIO>_huellas_con_contexto.csv`; tres gráficos |
| 6 | `Tp3_05_tablas_para_Orange.py` | **SE CORRE** | Tablas de los workflows de Orange desde las salidas de los pasos 1 a 6 | tablas de `05_Resultados\04_Tablas`, `04_Tablas_de_trabajo\<SITIO>_huellas_con_contexto.csv` y el CCI | `08_Orange\datos\Tp3_*.csv` |

## Las órdenes, con sus argumentos

```
python ..\..\Tp1_Convergencia\03_Scripts\Tp1_05_buscar_lidar.py --sitio A2_IBICUY --solo_contar

python Tp3_01_cubo_comun.py --sitio A2_IBICUY --fecha_optico 2026-09-16 --pixel 20 --mde
    (por defecto --pixel 20 ; sin --fecha_optico no hay óptico ; sin --mde no hay MDE)

python Tp3_02_medir_corregistro.py --sitio A2_IBICUY --pixel 20 --ref OPT_S2_B08 --mov L_NISAR_gamma0_HV_20260930
python Tp3_02_medir_corregistro.py --sitio A2_IBICUY --pixel 20 --ref L_NISAR_gamma0_HH_20260930 --mov S_NISAR_gamma0_HH_20260930
python Tp3_02_medir_corregistro.py --sitio A2_IBICUY --pixel 20 --ref OPT_S2_B08 --mov P_BIOMASS_gamma0_VH
python Tp3_02_medir_corregistro.py --sitio A2_IBICUY --pixel 20 --ref L_NISAR_gamma0_HV_20260930 --mov P_BIOMASS_gamma0_VH
    (por defecto --pixel 20 --ventanas 4 --min_comun 0.8)

python Tp3_03_lidar_en_el_cubo.py --sitio A2_IBICUY --pixel 20

python Tp3_04_contexto_y_huellas.py --sitio A2_IBICUY --pixel 20

python Tp3_05_tablas_para_Orange.py --sitio A2_IBICUY
```

Ejercicio optativo (Landsat 8 frente a Sentinel-2, cubo de 30 m) y pregunta 12 (pares
nuevos):

```
python Tp3_02_medir_corregistro.py --sitio A2_IBICUY --pixel 30 --ref OPT_S2_B08 --mov OPT_L8_SR_B5
python Tp3_02_medir_corregistro.py --sitio A2_IBICUY --pixel 20 --ref OPT_S2_B08 --mov S_NISAR_gamma0_HH_20260930
python Tp3_02_medir_corregistro.py --sitio A2_IBICUY --pixel 20 --ref C_SNAP_gamma0_VV --mov P_BIOMASS_gamma0_HH
```

La banda P entra al cubo desde la pila del Tp2 (`P_BIOMASS_gamma0_HH` y `P_BIOMASS_gamma0_VH`). La
cruzada es la VH: la HV de BIOMASS trae interferencia de radiofrecuencia sin corregir.

Caso de control en Bovril (NovaSAR con desplazamiento conocido):

```
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp2_SAR_multibanda\03_Scripts
python Tp2_01_pila_multibanda.py --sitio F_BOVRIL --novasar 47974 --fecha_c 2023-09-17
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp3_Armonizacion\03_Scripts
python Tp3_01_cubo_comun.py --sitio F_BOVRIL --fecha_optico 2023-09-10 --pixel 20
python Tp3_02_medir_corregistro.py --sitio F_BOVRIL --pixel 20 --ref OPT_S2_B08 --mov S_NovaSAR_sigma0_HH
```

Si el veredicto es un corrimiento rígido, la bitácora termina con la orden
`Para NovaSAR pase a Tp2_01:  --desplazamiento DX DY` (si no es rígido, la bitácora da la
mediana como primera aproximación). Se rearma la pila con ella, después el
cubo, y se vuelve a medir (un corrimiento rígido debe dar CUMPLE; NovaSAR 47974, que no es
rígido, baja la mediana a 0,25 px y sigue con 4 px de dispersión y 10,6 px de rango: no
entra a fusión de píxel):

```
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp2_SAR_multibanda\03_Scripts
python Tp2_01_pila_multibanda.py --sitio F_BOVRIL --novasar 47974 --fecha_c 2023-09-17 --desplazamiento DX DY
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp3_Armonizacion\03_Scripts
python Tp3_01_cubo_comun.py --sitio F_BOVRIL --fecha_optico 2023-09-10 --pixel 20
python Tp3_02_medir_corregistro.py --sitio F_BOVRIL --pixel 20 --ref OPT_S2_B08 --mov S_NovaSAR_sigma0_HH
```

Las fechas `2026-09-16` y `20260930` son ejemplos: los nombres de capa reales están en
`02_Subsets_SNAP_QGIS\<SITIO>_cubo_20m_bandas.csv`.

Cada corrida de `Tp3_02` escribe su tabla y su bitácora con el par en el nombre:
`<SITIO>_corregistro_<mov>_vs_<ref>.csv` y `Tp3_02_<SITIO>_<mov>_vs_<ref>.log`. Los
pares no se pisan entre sí.

## Qué hacer si falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `No existe la pila del Tp2` | No se corrió `Tp2_01` con ese sitio | Correrlo; si no, el cubo queda sin radar y se declara |
| `No hay Sentinel-2 L2A el <fecha>` | Sin pasada ese día o sin red | Elegir otra fecha con `Tp1_03` |
| `No such file ... _cubo_20m.tif` en los pasos 3 y 4 | `--pixel` distinto del usado en el paso 1 | Usar el mismo `--pixel` |
| `La capa X no esta en ...` | Nombre de capa inexacto | Copiar el nombre de la lista que imprime el mensaje |
| `Ninguna ventana tiene 80 % de dato en comun` | Nubes o capas que casi no se superponen | `--ventanas 2`, `--min_comun 0.5` (declarándolo), otra banda óptica u otra fecha |
| `No existe ... lidar_<SITIO>.gpkg` | Falta el paso 0 | Correr `Tp1_05 --solo_contar` con el mismo sitio |
| `Ninguna huella valida cae dentro del cubo` | El sitio no tiene huellas válidas o los granulos son de otro sitio | Declararlo; el LiDAR no entra como referencia |
| `RuntimeError: PROJ no aplico el geoide EGM2008` (si convierte alturas) | Falta `us_nga_egm08_25.tif` | Con red: `projsync --file us_nga_egm08_25` |
| `PermissionError` | El TIF o el CSV abiertos en QGIS o Excel | Quitar la capa o cerrar la planilla |
