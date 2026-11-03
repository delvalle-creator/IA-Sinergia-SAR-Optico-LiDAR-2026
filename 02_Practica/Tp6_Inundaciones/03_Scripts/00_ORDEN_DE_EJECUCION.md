# Tp6 — Orden de ejecución

| Paso | Script | Marca | Qué hace | Entrada | Salida |
|---|---|---|---|---|---|
| previo | `Tp4_01_cobertura_de_control.py --sitio B_CONCORDIA --pixel 20` | SE CORRE (si falta) | Cobertura de control | JRC, digitalización | `Tp4_Validacion\02_Subsets_SNAP_QGIS\B_CONCORDIA_cobertura_control_20m.tif` |
| previo | `Tp1_05_buscar_lidar.py --sitio B_CONCORDIA --descargar` | YA VIENE HECHO | Segmentos ATL08 del sitio | NASA Earthdata | `Tp1_Convergencia\05_Resultados\03_Vectores\lidar_B_CONCORDIA.gpkg` (capa `atl08`) |
| previo | `projsync --file us_nga_egm08_25` | AUXILIAR | Grilla del geoide EGM2008 para PROJ | red | grilla en la carpeta de PROJ del entorno |
| 1 | `Tp6_01_serie_agua_C.py` | SE CORRE | Serie de agua C, extensión y duración | Planetary Computer (S1 RTC, JRC) | `02_Subsets_SNAP_QGIS\B_agua_C_por_fecha_20m.tif`; `05_Resultados\02_Rasters\B_extension_y_duracion_C_20m.tif`; `04_Tablas\B_serie_agua_C.csv`; gráficos |
| 2 | `Tp6_02_sinergia_agua.py` | SE CORRE | SINERGIA: agua por sensor y tabla de acuerdo | serie C, S2, JRC, (L) | `05_Resultados\02_Rasters\B_agua_por_sensor_20m.tif`; `04_Tablas\B_sinergia_agua.csv` |
| 3 | `Tp6_03_fusion_y_variantes.py` | SE CORRE | FUSIÓN DE DECISIÓN y variantes | agua por sensor | `05_Resultados\02_Rasters\B_variante_*.tif` |
| 4 | `Tp4_02`, `Tp4_03`, `Tp4_04` | SE CORRE + EN QGIS | Validación de las variantes | variantes (copiadas con la fecha) | `Tp4_Validacion\05_Resultados\04_Tablas\B_variante_*_exactitud_y_area.csv`; `05_Resultados\04_Tablas\tabla_de_variantes_agua.csv` |
| 5 | `Tp6_04_profundidad.py` | SE CORRE | Profundidad por cota del borde | una variante, Copernicus DEM | `05_Resultados\02_Rasters\B_profundidad_<variante>_20m.tif` |
| 6 | `Tp6_05_control_mde_icesat2.py` | SE CORRE | Control del MDE con ATL08 | ATL08, Copernicus DEM, cobertura de control | `05_Resultados\04_Tablas\B_control_mde_icesat2.csv` |

Bitácoras en `Tp6_Inundaciones\05_Resultados\06_Control_calidad\`. Ningún paso del Tp6 requiere SNAP: la banda L SAOCOM ya viene procesada en `02_Subsets_SNAP_QGIS\SAOCOM_gamma0` (cadena en `09_Grafos_SNAP\LEEME_grafos.md`).

## Las órdenes exactas

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp6_Inundaciones\03_Scripts
```

**Paso 1.** `--pixel 20`, `--desde 2023-10-01`, `--hasta 2024-06-30`, `--fecha_umbral 2023-11-04` (antes `--pico`), `--umbral_vv` (vacío = Otsu), `--orbita` (vacío = la más frecuente), `--referencia_seca` (una o varias fechas separadas por coma), `--persistencia 2`.

```
python Tp6_01_serie_agua_C.py --pixel 20 --desde 2023-10-01 --hasta 2024-06-30 --fecha_umbral 2023-11-04
```

Con los datos del curso Otsu no encuentra el valle (histograma unimodal) y da −9,5 dB: se repite con `--umbral_vv -15` (ver la guía, paso 1).

**Paso 2.** `--pixel 20`, `--fecha 2023-11-04`, `--u_mndwi 0.0`, `--l_evento` y `--l_referencia` (vacíos), `--u_doble_rebote 3.0`.

```
python Tp6_02_sinergia_agua.py --pixel 20 --fecha 2023-11-04
```

**Paso 3.** `--pixel 20`.

```
python Tp6_03_fusion_y_variantes.py --pixel 20
```

Después, copie las variantes con la fecha (desde `05_Resultados\02_Rasters`):

```
copy /Y B_variante_C.tif B_variante_C_20231104.tif
copy /Y B_variante_optico.tif B_variante_optico_20231104.tif
copy /Y B_variante_multisensor.tif B_variante_multisensor_20231104.tif
```

**Paso 4.** Desde `Tp4_Validacion\03_Scripts`:

```
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp6_Inundaciones\05_Resultados\02_Rasters\B_variante_C_20231104.tif --banda 1
python Tp4_03_exactitud_y_area.py --nombre B_variante_C_20231104 --nombres_clase "1=agua,2=no_agua"
python Tp4_04_tabla_de_variantes.py --tp Tp6 --clase agua ^
    --variante "Optico solo|Sentinel-2|B_variante_optico_20231104" ^
    --variante "SAR solo (C)|Sentinel-1|B_variante_C_20231104" ^
    --variante "Multisensor|C + optico|B_variante_multisensor_20231104"
```

**Paso 5.** `--pixel 20`, `--variante multisensor`, `--suavizado 7`, `--mde copdem` (o `fabdem`).

```
python Tp6_04_profundidad.py --pixel 20 --variante multisensor_20231104 --suavizado 7
python Tp6_04_profundidad.py --pixel 20 --variante multisensor_20231104 --suavizado 7 --mde fabdem
```

**Paso 6.** `--pixel 20`, `--solo_fuertes` (opcional), `--clases control|mapbiomas|ambas`, `--mde copdem|fabdem`, `--excluir_evento` (opcional).

```
python Tp6_05_control_mde_icesat2.py --pixel 20
python Tp6_05_control_mde_icesat2.py --pixel 20 --solo_fuertes
python Tp6_05_control_mde_icesat2.py --pixel 20 --clases ambas --excluir_evento
```

## Qué hacer si falla

| Mensaje | Causa | Qué hacer |
|---|---|---|
| `El Planetary Computer no devolvio Sentinel-1 RTC para la ventana.` | sin red o sin escenas | revisar la red; ampliar la ventana |
| `No hay escena de la orbita X el 2023-11-04. Elegir --fecha_umbral entre: ...` | la órbita más frecuente no pasó el día del pico | `--orbita` con la del 04/11/2023, o otra fecha |
| `La serie C no tiene la fecha ...` | `--fecha` fuera de la serie | usar una fecha listada |
| `No hay Sentinel-2 el ...` y `Solo hay un sensor...` | día sin óptico y sin L | elegir otra fecha o declarar que no hay sinergia ese día |
| `FileNotFoundError` con `B_agua_por_sensor_20m.tif` | no se corrió el paso 2 | correrlo |
| `FileNotFoundError` con `B_variante_<x>.tif` en `Tp6_04` | `--variante` no coincide con el nombre | revisar el nombre del archivo |
| `RuntimeError: PROJ no aplico el geoide EGM2008 ...` | falta `us_nga_egm08_25.tif` | `projsync --file us_nga_egm08_25` con red |
| `Falta ...lidar_B_CONCORDIA.gpkg (Tp1_05 con --descargar).` | no está la descarga ATL08 | pedirla al docente |
