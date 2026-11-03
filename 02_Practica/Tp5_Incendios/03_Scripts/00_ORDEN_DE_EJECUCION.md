# Tp5 — Orden de ejecución

| Paso de la guía | Script | Marca | Qué hace | Entrada | Salida |
|---|---|---|---|---|---|
| previo | `Tp4_01_cobertura_de_control.py --sitio A1_DELTA_QUEMAS --pixel 20` | SE CORRE (si falta) | Cobertura de control del sitio | JRC, digitalización | `Tp4_Validacion\02_Subsets_SNAP_QGIS\A1_DELTA_QUEMAS_cobertura_control_20m.tif` |
| previo | `Tp1_05_buscar_lidar.py --sitio A1_DELTA_QUEMAS --descargar` | YA VIENE HECHO | Huellas GEDI filtradas | NASA Earthdata | `Tp1_Convergencia\05_Resultados\03_Vectores\lidar_A1_DELTA_QUEMAS.gpkg` |
| previo | `00_COMUN\procesar_saocom.py` (grafo de SNAP) | YA VIENE HECHO | γ⁰ de SAOCOM, GeoTIFF de una banda y RGB | recortes SLC SAOCOM-1A del 21/07, 07/09 y 25/10/2020 | `02_Subsets_SNAP_QGIS\SAOCOM_gamma0\QGIS_GeoTIFF\A1_DELTA_QUEMAS_SAOCOM_L_<fecha>_<QP\|DP>_gamma0_Gamma0_<POL>.tif` |
| 1 | `Tp5_01_indicadores.py` | SE CORRE | Indicadores por sensor | Planetary Computer (S1, S2, ALOS-2), SAOCOM | `02_Subsets_SNAP_QGIS\A1_DELTA_QUEMAS_indicadores_20m.tif`, `..._fuentes.csv` |
| 2 | `Tp5_02_sinergia.py` | SE CORRE | SINERGIA: mapa por sensor y tabla de acuerdo | indicadores, cobertura de control | `05_Resultados\02_Rasters\A1_quema_por_sensor_20m.tif`, `A1_sensores_que_coinciden_20m.tif`; `04_Tablas\A1_sinergia_coincidencias.csv`; histogramas |
| 3 y 4 | `Tp5_03_fusion.py` (1.ª vez) | SE CORRE | V1, V2, V3 y la capa de entrenamiento vacía | mapas por sensor | `A1_variante_optico.tif`, `A1_variante_C.tif`, `A1_variante_CL.tif`; `04_Tablas_de_trabajo\entrenamiento_A1.gpkg` |
| 3 | (QGIS) | EN QGIS | Digitalizar entrenamiento de severidad | indicadores, imágenes fechadas | `entrenamiento_A1.gpkg` con polígonos |
| 4 | `Tp5_03_fusion.py` (2.ª vez) | SE CORRE | V4: FUSIÓN DE RASGO (Random Forest) | indicadores, entrenamiento | `A1_severidad_multisensor.tif`, `A1_variante_multisensor.tif`; `04_Tablas\A1_importancia_variables.csv`; figura |
| 5 | `Tp4_02`, `Tp4_03`, `Tp4_04` | SE CORRE + EN QGIS | Validación de las cuatro variantes y de la severidad (A1_severidad_multisensor, 4 clases) | variantes y severidad | `Tp4_Validacion\05_Resultados\04_Tablas\A1_variante_*_exactitud_y_area.csv`; `Tp5_Incendios\05_Resultados\04_Tablas\tabla_de_variantes_quemado.csv` |
| 5 | `Tp5_05_dominio_comun.py` | SE CORRE | Las cuatro variantes en la superficie común (estimación de dominio e IC de la diferencia con el óptico) | variantes y muestras etiquetadas | `05_Resultados\04_Tablas\tabla_de_variantes_quemado_dominio_comun.csv` |
| 6 | `Tp5_04_gedi_cambio_de_altura.py` | SE CORRE | SINERGIA: Δrh98 por celda y por clase | huellas GEDI, variante multisensor | `05_Resultados\04_Tablas\A1_delta_rh98_por_celda.csv`, `A1_delta_rh98_por_clase.csv` |

Todas las bitácoras quedan en `Tp5_Incendios\05_Resultados\06_Control_calidad\`.

## Las órdenes exactas

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp5_Incendios\03_Scripts
```

**Paso 1.** Argumentos y valores por defecto: `--pixel 20`, `--c_pre 2020-07-16`, `--c_post 2020-09-26`, `--opt_pre` (vacío), `--opt_post 2020-10-13`, `--alos2_pre 2019`, `--alos2_post 2020`, `--saocom_pre_hv` y `--saocom_post_hv` (vacíos). Opcionales: `--c_pre_extra` y `--c_post_extra` (otras fechas de la misma órbita, promediadas en lineal), `--nbr_nir B08|B8A`, `--alos2_desde AAAA-MM-DD`.

```
python Tp5_01_indicadores.py --pixel 20 --c_pre 2020-07-16 --c_post 2020-09-26 ^
    --opt_pre 2020-07-15 --opt_post 2020-10-13 --alos2_pre 2019 --alos2_post 2020 ^
    --saocom_pre_hv ..\02_Subsets_SNAP_QGIS\SAOCOM_gamma0\QGIS_GeoTIFF\A1_DELTA_QUEMAS_SAOCOM_L_20200721_QP_gamma0_Gamma0_HV.tif ^
    --saocom_post_hv ..\02_Subsets_SNAP_QGIS\SAOCOM_gamma0\QGIS_GeoTIFF\A1_DELTA_QUEMAS_SAOCOM_L_20201025_QP_gamma0_Gamma0_HV.tif
```

(La carpeta de los GeoTIFF de SAOCOM es un ejemplo: use la que indique el docente. Sin SAOCOM, omita las dos últimas líneas.)

**Paso 2.** Argumentos: `--pixel 20`, umbrales manuales opcionales `--u_dvh`, `--u_dhv`, `--u_dhv_saocom`, `--u_dnbr`.

```
python Tp5_02_sinergia.py --pixel 20
python Tp5_02_sinergia.py --pixel 20 --u_dvh 1 --u_dhv -2 --u_dhv_saocom 1 --u_dnbr 0.15
```

**Pasos 3 y 4.** Argumentos: `--pixel 20`, `--regla mayoria` (o `union`, `interseccion`), `--sin_rdnbr` (variante de control de la V4). Se corre dos veces: antes y después de digitalizar.

```
python Tp5_03_fusion.py --pixel 20 --regla mayoria
```

**Paso 5.** Desde `Tp4_Validacion\03_Scripts` (ver su `00_ORDEN_DE_EJECUCION.md`):

```
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp5_Incendios\05_Resultados\02_Rasters\A1_variante_optico.tif --banda 1
python Tp4_03_exactitud_y_area.py --nombre A1_variante_optico --nombres_clase "1=quemado,2=no_quemado"
```

(lo mismo para `A1_variante_C`, `A1_variante_CL`, `A1_variante_multisensor`)

La severidad, con su propia muestra de cuatro clases:

```
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp5_Incendios\05_Resultados\02_Rasters\A1_severidad_multisensor.tif --banda 1
python Tp4_03_exactitud_y_area.py --nombre A1_severidad_multisensor --nombres_clase "1=severidad_alta,2=severidad_baja,3=no_quemado,4=agua"
```

```
python Tp4_04_tabla_de_variantes.py --tp Tp5 --clase quemado ^
    --variante "Optico solo|Sentinel-2|A1_variante_optico" ^
    --variante "SAR solo (C)|Sentinel-1|A1_variante_C" ^
    --variante "SAR multibanda|C + L|A1_variante_CL" ^
    --variante "Multisensor|SAR (C + L) + optico|A1_variante_multisensor"
```

Después, de vuelta en `Tp5_Incendios\03_Scripts`, la comparación en la superficie común:

```
python Tp5_05_dominio_comun.py
```

**Paso 6.** Argumentos: `--antes_desde 2019-10-01`, `--antes_hasta 2020-04-01`, `--despues_desde 2020-10-01`, `--despues_hasta 2021-03-31`, `--celda 100`, `--min_huellas 2`.

```
python Tp5_04_gedi_cambio_de_altura.py --antes_desde 2019-10-01 --antes_hasta 2020-04-01 --despues_desde 2020-10-01 --despues_hasta 2021-03-31 --celda 100
```

## Qué hacer si falla

| Mensaje | Causa | Qué hacer |
|---|---|---|
| `Sentinel-1 RTC: no hay escena el ...` | la fecha no está en el catálogo RTC | elegir otra fecha con `Tp1_03`, misma órbita |
| `Sentinel-2: no hay escena el ...` | no hay pasada ese día | usar la fecha de la planilla del Tp1 |
| `ALOS-2: el Planetary Computer no devolvio mosaico ...` | año sin mosaico o sin red | probar con red; declarar si falta |
| `No se calculo ningun indicador.` | fallaron todas las lecturas | revisar la red y las fechas |
| `FileNotFoundError` en `Tp5_02` o `Tp5_03` | no se corrió el paso anterior con el mismo `--pixel` | correrlo |
| `Hace falta al menos dos sensores para la sinergia.` | un solo indicador | revisar el paso 1 |
| `V4 queda pendiente hasta que se digitalice el entrenamiento.` | primera corrida | digitalizar y volver a correr |
| `ValueError: Muy pocos pixeles de entrenamiento...` | polígonos sobre nubes o sin dato | moverlos o agregar más |
| `Falta ...A1_variante_multisensor.tif: correr antes Tp5_03_fusion.py con la capa de entrenamiento digitalizada.` (en `Tp5_04`) | V4 no existe todavía | digitalizar el entrenamiento y completar el paso 3 |
| `Falta ...lidar_A1_DELTA_QUEMAS.gpkg` | no está la descarga GEDI | pedirla al docente |
