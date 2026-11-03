# Tp8 — Orden de ejecución

Todo se corre desde el **Miniforge Prompt**:

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp8_Erosion_suelos\03_Scripts
```

| Paso | Script o herramienta | Marca | Qué hace | Entrada | Salida |
|---|---|---|---|---|---|
| 1 | `Tp8_01_frecuencia_suelo_desnudo.py` | **SE CORRE** | Meses con suelo desnudo en 2023 | Sentinel-2 L2A (Planetary Computer) | `02_Subsets_SNAP_QGIS/F_frecuencia_suelo_desnudo_2023_10m.tif`, `05_Resultados/04_Tablas/F_escenas_opticas_2023.csv` |
| 2 | `Tp8_02_textura_S_y_C.py` (sin corrección) + QGIS | **SE CORRE** / **EN QGIS** | Pone NovaSAR en la grilla para medir su desfase | NovaSAR 47974 | `F_textura_S_C_10m.tif` provisorio |
| 3 | `Tp8_02_textura_S_y_C.py --desplazamiento DX DY` | **SE CORRE** | Textura S y C (sinergia) y tabla por clase de frecuencia | NovaSAR, Sentinel-1 RTC, paso 1 | `02_Subsets_SNAP_QGIS/F_textura_S_C_10m.tif`, `05_Resultados/04_Tablas/F_textura_por_frecuencia.csv` |
| 3b | SNAP: GLCM | **EN SNAP** | Textura de Haralick para comparar con el CV | `F_textura_S_C_10m.tif` | figura del grupo |
| 4 | `Tp8_03_susceptibilidad.py` (primera vez) + QGIS | **SE CORRE** / **EN QGIS** | Crea la capa de entrenamiento vacía y la variante solo óptico; el grupo digitaliza sobre los puntos ya sorteados | `04_Tablas_de_trabajo/estrato_erosion_F.gpkg` | `04_Tablas_de_trabajo/entrenamiento_F.gpkg`, `F_variante_optico.tif` |
| 5 | `Tp8_03_susceptibilidad.py` | **SE CORRE** | Random Forest de rasgos → susceptibilidad y variante multisensor | pasos 1–3, FABDEM v1-2 (pendiente), entrenamiento | `05_Resultados/02_Rasters/F_susceptibilidad.tif`, `F_variante_multisensor.tif` |
| 5b | `08_Orange/Tp8_D_aporte_del_radar.ows` | **EN ORANGE** | Random Forest con y sin radar, validado por polígono | `datos/Tp8_D_pixeles_entrenamiento.tab` | AUC y exactitud de cada juego de rasgos |
| 6 | `Tp4_02`, `Tp4_03`, `Tp4_04` | **SE CORRE** | Exactitud y área de las dos variantes (si no alcanza, el etiquetado y `Tp4_03` se completan fuera del horario) | las variantes | tablas del Tp4 |

## Las órdenes, con sus valores por defecto

```
python Tp8_01_frecuencia_suelo_desnudo.py --anio 2023 --pixel 10 --nubes_max 60 --ndvi_max 0.25 --bsi_min 0
python Tp8_01_frecuencia_suelo_desnudo.py --local        (sin internet: copia de 00_COMUN/08_Originales_crudos)

python Tp8_02_textura_S_y_C.py --puntos_enlace todos
python Tp8_02_textura_S_y_C.py --pixel 10 --fecha_c 2023-09-14 --novasar 47974 --ventana 5 --puntos_enlace todos --desplazamiento -80 20 --zonas_homogeneas ..\04_Tablas_de_trabajo\zonas_homogeneas.gpkg

python Tp8_03_susceptibilidad.py --pixel 10 --umbral 0.5
python Tp8_03_susceptibilidad.py --rasgos meses_suelo_desnudo pendiente_grados --nombre_variante opt_pend
python Tp8_03_susceptibilidad.py --equilibrar no --nombre_variante sin_equilibrar
python Tp8_03_susceptibilidad.py --mascara_urbana --nombre_variante urbana
```

Valores por defecto de `Tp8_02`: `--pixel 10 --fecha_c 2023-09-14 --novasar 47974
--ventana 5 --puntos_enlace esquinas --desplazamiento 0 0 --anio 2023`. El ejemplo usa
`--puntos_enlace todos` (los 84 puntos de enlace del `metadata.xml`) y `-80 20`: la
banda S está 80 m al este y 20 m al sur, y se la mueve 80 m al oeste y 20 m al norte
(DX y DY son la corrección: DX positivo = mover al este, DY positivo = mover al
norte). Use el que midió su grupo, con los mismos puntos de enlace. `--fecha_c` es la
fecha buscada: el script toma el Sentinel-1 más cercano en ± 6 días (17/09/2023). `Tp8_03`: `--pixel 10 --umbral 0.5
--anio 2023 --equilibrar si`, todos los rasgos (el equilibrado infla la clase rara). Si el paso 1 se corrió con otro año, pase el mismo `--anio` a los
pasos 2 y 3.

Para el Tp4 (desde `...\Tp4_Validacion\03_Scripts`):

```
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp8_Erosion_suelos\05_Resultados\02_Rasters\F_variante_multisensor.tif --banda 1
python Tp4_03_exactitud_y_area.py --nombre F_variante_multisensor --nombres_clase "1=susceptible,2=no_susceptible"
python Tp4_04_tabla_de_variantes.py --tp Tp8 --clase susceptible ^
  --variante "Solo optico|Sentinel-2|F_variante_optico" ^
  --variante "Multisensor|Sentinel-2 + NovaSAR S + Sentinel-1 C + FABDEM|F_variante_multisensor"
```

(lo mismo con `F_variante_optico` en los dos primeros).

## Si falla

| Mensaje | Qué pasa | Qué hacer |
|---|---|---|
| `ModuleNotFoundError` | Entorno no activado | `conda activate sar` |
| HTTP 403 a mitad de la corrida | Venció la firma de las URL del Planetary Computer (≈ 1 h) | Volver a correr, o usar `--local` en el paso 1 |
| `No encuentro el GRD de la escena 47974` | Disco de NovaSAR con otra letra | `set CURSO_SAR_NOVASAR=<ruta>` |
| `El metadata.xml no trae CalibrationConstant` | Carpeta equivocada | Revisar que sea el GRD de 47974 |
| `Sin Sentinel-1 RTC +/- 6 dias` | No hay escena C cercana | Seguir con S; declararlo |
| `Falta la frecuencia de suelo desnudo` | No se corrió el paso 1 (o con otro `--anio`) | Correr el paso 1, o pasar a `Tp8_02` el mismo `--anio` |
| `FileNotFoundError ... F_textura_S_C_10m.tif` en el paso 5 | No se corrió el paso 3 | Correrlo |
| `Muy pocos pixeles de entrenamiento con dato en todas las capas` | Polígonos fuera de NovaSAR o sin dato C | Digitalizar dentro de la cobertura |
