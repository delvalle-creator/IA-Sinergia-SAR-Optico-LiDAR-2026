# Tp9 — Orden de ejecución

Todo se corre desde el **Miniforge Prompt**:

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp9_Deforestacion\03_Scripts
```

| Paso | Script o herramienta | Marca | Qué hace | Entrada | Salida | Cuándo |
|---|---|---|---|---|---|---|
| 0a | `Tp1_04_buscar_asf.py` (ALOS 2011 y NISAR) | **YA VIENE HECHO** | Baja ALOS-1 FBS RTC y NISAR GCOV | cuenta Earthdata | ALOS-1: `00_COMUN\08_Originales_crudos\ASF\C_FEDERAL\ALOS\`; NISAR: `00_COMUN\08_Originales_crudos\NISAR\` | ya viene hecho |
| 0b | `Tp1_05_buscar_lidar.py --sitio C_FEDERAL --descargar` | **YA VIENE HECHO** | GEDI L2A filtrado | cuenta Earthdata | `lidar_C_FEDERAL.gpkg` | ya viene hecho |
| 0c | `Tp4_01_cobertura_de_control.py --sitio C_FEDERAL --pixel 20` | **SE CORRE** si falta | Cobertura de control (zona estable) | polígonos del grupo, JRC, MapBiomas | `C_FEDERAL_cobertura_control_20m.tif` | en clase |
| 1 | `Tp9_01_pila_temporal.py` | **SE CORRE** | Pila L, C, S y NDVI a 20 m; calibración cruzada de banda L | 0a, 0c, Planetary Computer | `02_Subsets_SNAP_QGIS/C_pila_temporal_20m.tif`, `05_Resultados/04_Tablas/C_calibracion_cruzada.csv` | en clase |
| 2 | `Tp9_02_sinergia_estratos.py` | **SE CORRE** | Curvas de respuesta frente a rh98 (sinergia); degradación por Δrh98 | pila, 0b | `C_sensibilidad_a_la_altura.csv`, `C_curvas_de_respuesta.png`, `C_delta_rh98_por_celda.csv`, `02_Subsets_SNAP_QGIS/C_delta_rh98_20m.tif` | en clase |
| 3 | `Tp9_03_fusion_perdida_degradacion.py` (primera vez) + QGIS | **SE CORRE** / **EN QGIS** | Crea la capa de entrenamiento y las variantes de un sensor; el grupo digitaliza | pila | `04_Tablas_de_trabajo/entrenamiento_C.gpkg`, `C_variante_optico.tif`, `C_variante_L.tif` | en clase |
| 4 | `Tp9_03_fusion_perdida_degradacion.py` | **SE CORRE** | Random Forest de rasgos; control con GEDI | pila, entrenamiento, Δrh98 | `C_perdida_degradacion.tif`, `C_variante_multisensor.tif`, `C_control_gedi_por_clase.csv`, `C_perdida_degradacion.png` | en clase |
| 5 | `Tp4_02`, `Tp4_03`, `Tp4_04` | **SE CORRE** | Exactitud y área de las tres variantes | variantes | tablas del Tp4 | `Tp4_02` en clase; etiquetado, `Tp4_03` y `Tp4_04` fuera de horario |

## Las órdenes, con sus valores por defecto

**Paso 1.**

```
python Tp9_01_pila_temporal.py --pixel 20 --puntos_enlace todos --desplazamiento -60 10 ^
  --alos1_hh ..\..\00_COMUN\08_Originales_crudos\ASF\C_FEDERAL\ALOS\AP_27336_FBS_F6560_RT1\AP_27336_FBS_F6560_RT1_HH.tif ^
  --nisar_h5 ..\..\00_COMUN\08_Originales_crudos\NISAR\NISAR_L2_PR_GCOV_030_161_A_162_2005_DHDH_A_20260917T095508_20260917T095543_P05023_N_F_J_001.h5
```

Por defecto: `--pixel 20 --fechas_c 2021-08-10 2026-09-14 --fechas_opt
2021-08-06 2026-09-16 --anio_alos2 2021 --novasar 50896 --semilla 20261027`; `--alos1_hh`,
`--alos1_hv` y `--nisar_h5` vacíos; `--solo_urbano` apagado; `--desplazamiento 0 0`;
`--puntos_enlace esquinas`. Con `--puntos_enlace todos` (84 puntos de enlace) el
corrimiento medido es `-60 10`.
Si el monte de la cobertura de control no está confirmado: agregue
`--solo_urbano`. Si midió el desfase de NovaSAR con `Tp3_02`, agregue la orden
que éste imprime, `--desplazamiento DX DY` (metros; DX positivo = este, DY
positivo = norte).

**Paso 2.**

```
python Tp9_02_sinergia_estratos.py --pixel 20
```

La parte B (banda P) usa sola el BIOMASS de Federal. Por defecto: `--dias_max 730
--p1_hasta 2022-12-31 --p2_desde 2024-04-26 --celda 200 --monte_min 5 --u_rh98 -3
--u_dndvi 0.05 --rh98_max 60 --min_huellas_clase 100 --bootstrap 500 --semilla 2026`;
`--ndvi_p1` y `--ndvi_p2` vacíos (primera y última capa NDVI de la pila); `--p_tif` = `02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\C_FEDERAL_BIOMASS_P_20260812.tif`,
`--p_fecha 2026-08-12`, `--p_en_db` y `--sin_p` apagados.

**Pasos 3 y 4.**

```
python Tp9_03_fusion_perdida_degradacion.py --pixel 20 --u_ndvi -0.10 --u_hv -1.5
python Tp9_03_fusion_perdida_degradacion.py --pixel 20 --rh98_como_rasgo
```

(la segunda, sólo para comparar: el mapa queda limitado a las celdas con huellas).

Corridas para comparar (no pisan el mapa principal):

```
python Tp9_03_fusion_perdida_degradacion.py --pixel 20 --sin_equilibrar --sufijo _sin_equilibrar
python Tp9_03_fusion_perdida_degradacion.py --pixel 20 --sin_historico --sufijo _sin_historico
python Tp9_03_fusion_perdida_degradacion.py --pixel 20 --mascara_monte_2021 --sufijo _mascara_monte
python Tp9_03_fusion_perdida_degradacion.py --pixel 20 --entrenamiento ..\04_Tablas_de_trabajo\entrenamiento_C_ampliado.gpkg --sufijo _ampliado
```

**Paso 5** (desde `...\Tp4_Validacion\03_Scripts`):

```
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp9_Deforestacion\05_Resultados\02_Rasters\C_variante_multisensor.tif --banda 1
python Tp4_03_exactitud_y_area.py --nombre C_variante_multisensor --nombres_clase "1=perdida_o_degradacion,2=no"
python Tp4_04_tabla_de_variantes.py --tp Tp9 --clase perdida_o_degradacion ^
  --variante "Solo optico|Sentinel-2|C_variante_optico" ^
  --variante "Solo banda L|ALOS-2 + NISAR|C_variante_L" ^
  --variante "Multisensor|L + C + optico|C_variante_multisensor"
```

## Si falla

| Mensaje | Qué pasa | Qué hacer |
|---|---|---|
| `No hay cobertura de control (Tp4_01 para C_FEDERAL): NO se calibra` | Falta el paso 0c | Correr `Tp4_01` a 20 m o declarar la falta de calibración |
| `NISAR: El granulo ... no cubre el sitio` | `.h5` de otra pasada | Usar el gránulo del 17/09/2026 sobre Federal |
| `NovaSAR: No encuentro el GRD de la escena 50896` | Disco con otra letra | `set CURSO_SAR_NOVASAR=<ruta>` |
| `Sin Sentinel-1 RTC el ...` / `Sin Sentinel-2 el ...` | No hay escena ese día | Otra fecha con `--fechas_c` / `--fechas_opt`, anotada |
| `Falta ...lidar_C_FEDERAL.gpkg` | No se corrió `Tp1_05` | Pedirlo al docente (descarga larga) |
| `No hay celdas con huellas en los dos periodos` | Pocas huellas | `--celda 400` y declararlo |
| `La pila no tiene pares de fechas para calcular cambios` | Faltan fechas en la pila | Revisar el paso 1 |
| `Muy pocos pixeles de entrenamiento con dato en todas las capas` | Polígonos donde falta algún rasgo | Digitalizar donde haya todos los datos |
