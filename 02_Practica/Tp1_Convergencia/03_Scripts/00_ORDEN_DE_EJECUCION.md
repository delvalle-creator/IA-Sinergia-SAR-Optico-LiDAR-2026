# Tp1 — Orden de ejecución

Todos los scripts se corren desde esta carpeta, en el Miniforge Prompt:

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp1_Convergencia\03_Scripts
```

Antes del primer práctico, una sola vez por computadora, se revisa el entorno desde
`00_COMUN` (debe terminar con `Resultado: TODO EN ORDEN`; `--red` prueba además la
conexión a los catálogos):

```
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\00_COMUN
python comprobar_entorno.py
```

| Paso | Script | Marca | Qué hace | Entrada | Salida | Tiempo aprox. |
|---|---|---|---|---|---|---|
| 1 | `Tp1_01_sitios_a_vector.py` | **SE CORRE** | Sitios a vector y grilla de 10 m de cada uno | `00_COMUN/configuracion_comun.py` | `00_COMUN/01_AOI/sitios_curso.gpkg` y `<SITIO>.geojson` | 1 min |
| — | revisión de los sitios | **EN QGIS** | Ver que cada sitio cae donde debe | `sitios_curso.gpkg` + imagen de fondo | anotaciones del grupo | 15 min |
| 2 | `Tp1_02_inventario_local.py` | **SE CORRE** | Inventario de NovaSAR-1, NISAR L y S, archivo 2023 y COSMO 2018: huella frente a píxeles con dato | carpetas de datos del curso | `05_Resultados/04_Tablas/inventario_local.csv` | 10–20 min |
| 3 | `Tp1_03_buscar_optico_y_C.py` | **SE CORRE** | Sentinel-2 L2A y Sentinel-1 RTC verificados en el sitio; pares | Planetary Computer (red) | `planilla_MPC_<SITIO>.csv`, `pares_optico_C_<SITIO>.csv` | 5–20 min (según la red y la ventana) |
| 4 | `Tp1_04_buscar_asf.py` | **SE CORRE** / descarga **YA VIENE HECHO** | NISAR GCOV, S1 SLC y GRD, ALOS RTC en ASF | ASF (red) | `planilla_ASF_<SITIO>.csv` | 2–5 min |
| 5 | `Tp1_05_buscar_lidar.py` | **SE CORRE** / descarga **YA VIENE HECHO** | Granulos GEDI L2A v003 y ATL08 v007; conteo de huellas válidas | NASA Earthdata (red) y `.h5` ya bajados | `lidar_granulos_<SITIO>.csv`, `lidar_conteo_<SITIO>.csv`, `03_Vectores/lidar_<SITIO>.gpkg` | 2–5 min la búsqueda; 1–10 min el conteo |
| 6 | `Tp1_06_escenas_por_pedido.py` | **SE CORRE** + planilla a mano | BIOMASS en ESA MAAP y escenas por pedido | ESA MAAP (red) y `04_Tablas_de_trabajo/escenas_por_pedido.csv` | `planilla_por_pedido_<SITIO>.csv` | 2 min + 30 min de portales |
| 6b | `Tp1_06b_banda_L_antes_despues.py` | **SE CORRE** (insumo del Tp6 **YA VIENE HECHO**) | Banda L (SAOCOM y ALOS-2) antes y durante la crecida, frente a la banda C | `02_Subsets_SNAP_QGIS\SAOCOM_gamma0`, `ALOS2_gamma0` y los recortes del Tp6 (sin red) | `B_CONCORDIA_banda_L_escenas.csv`, `B_CONCORDIA_antes_despues_por_zona.csv`, tres figuras | 3 min |
| 7 | `Tp1_07_matriz_convergencia.py` | **SE CORRE** | Matriz sensor × fecha, grado de convergencia, línea de tiempo | las planillas de los pasos 2 a 6 | `matriz_convergencia_<SITIO>.csv`, `grado_convergencia_<SITIO>.csv`, `05_Graficos/linea_tiempo_<SITIO>.png` | 1 min |
| 8 | control cruzado | **AUXILIAR** | Otro grupo repite la búsqueda | planillas de los dos grupos | tabla de verificación | 15 min |
| 9 | `Tp1_08_contexto_del_sitio.py` | **SE CORRE** + **EN QGIS** y Orange | Contexto del sitio: MapBiomas (cobertura 1985–2025, pérdida, fuego), CCI Biomass y banda P (HH y VH; la HV trae RFI de origen) | `02_Subsets_SNAP_QGIS\QGIS_GeoTIFF` | `<SITIO>_mapbiomas_*.csv`, `<SITIO>_contexto_por_clase.csv`, `<SITIO>_contexto_pixeles_muestra.csv` y dos gráficos | 6 s (medido) + 20 min |

Cada script escribe, además, su bitácora en `05_Resultados/06_Control_calidad/`.

## Las órdenes, con sus argumentos

```
python Tp1_01_sitios_a_vector.py

python Tp1_02_inventario_local.py
    (opcional: --sitios B_CONCORDIA F_BOVRIL ; por defecto, todos los sitios)

python Tp1_03_buscar_optico_y_C.py --sitio B_CONCORDIA --desde 2023-10-01 --hasta 2023-11-30
    (opcionales: --nubes_max 80  --dias_par 3 ; esos son los valores por defecto)

python Tp1_04_buscar_asf.py --sitio B_CONCORDIA --desde 2023-10-01 --hasta 2023-11-30
    (opcionales: --solo NISAR S1_SLC S1_GRD ALOS  --descargar 0)

python Tp1_05_buscar_lidar.py --sitio B_CONCORDIA --desde 2023-10-01 --hasta 2023-11-30
python Tp1_05_buscar_lidar.py --sitio B_CONCORDIA
    (por defecto --desde 2019-04-01 --hasta 2026-09-30 --sensibilidad 0.95)
python Tp1_05_buscar_lidar.py --sitio B_CONCORDIA --solo_contar
    (sólo cuenta los .h5 ya bajados en <ORIGINALES>\LIDAR\B_CONCORDIA\)

python Tp1_06_escenas_por_pedido.py --sitio B_CONCORDIA --desde 2025-11-01
    (por defecto --desde 2025-12-01 --hasta 2026-12-31 ; BIOMASS publica sobre Concordia desde el
     23/11/2025, por eso --desde 2025-11-01 ; --descargar sólo con ficha de ESA MAAP)

python Tp1_06b_banda_L_antes_despues.py
    (opcionales: --semilla 2023 --muestra 20000 --nodata_gamma 0 ; usa la máscara de agua del Tp6,
     insumo YA VIENE HECHO: si falta, el script lo avisa y termina)

python Tp1_07_matriz_convergencia.py --sitio B_CONCORDIA --evento 2023-11-04 --ventana 12

python Tp1_08_contexto_del_sitio.py --sitio B_CONCORDIA
```

`--sitio` acepta cualquiera de las claves de `SITIOS`: `A1_DELTA_QUEMAS`,
`A2_IBICUY`, `B_CONCORDIA`, `C_FEDERAL`, `D_LAPAZ_VILLAGUAY`, `E_PARANA_DIAMANTE`,
`E1_DIAMANTE_BARRANCA`, `F_BOVRIL`, `DELTA_NISAR`. Se escribe exactamente así, con
mayúsculas y guiones bajos.

## Variables de entorno (sólo si hacen falta)

Se escriben en la misma ventana, antes de correr:

```
set CURSO_SAR_NOVASAR=E:\IMÁGENES NOVASAR-1 2023 2024\ENTRE RIOS-SANTA FE
set CURSO_SAR_NISAR_DELTA=<carpeta con BANDA_L_NASA y BANDA_S_ISRO>
set CURSO_SAR_2023=E:\CURSO SAR CEREGEO 2023\PRACTICAL EXERCISES
set CURSO_SAR_COSMO=F:\HFdV COURSES\CEREGEO\2018\TelSAR\DIAMANTE
set CURSO_SAR_ORIGINALES=<carpeta donde están ASF, LIDAR y BIOMASS ya bajados>
```

Los valores de arriba son los que el código usa por defecto, salvo
`CURSO_SAR_ORIGINALES`, cuyo defecto es `02_Practica\00_COMUN\08_Originales_crudos`.

Credenciales: **nunca** en un archivo del curso. NASA Earthdata, en el `.netrc` del
usuario (`C:\Users\<usuario>\.netrc`) o con `set EARTHDATA_TOKEN=...`; ESA MAAP, con
`set BIOMASS_TOKEN=...` y `set BIOMASS_CLIENT_SECRET=...`.

## Qué hacer si falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `ModuleNotFoundError` | No se activó el entorno, o le falta una biblioteca | `conda activate sar`; si sigue, `python comprobar_entorno.py` desde `00_COMUN` dice cuál falta |
| `No module named configuracion_comun` | Se corrió desde otra carpeta fuera del árbol del curso | Volver a `03_Scripts` del Tp1 |
| `NO EXISTE ... en este equipo` | Falta una unidad o una variable de entorno | Definir la variable y volver a correr; si no hay forma, se declara |
| Error de red, certificado o tiempo de espera | La red del aula no llega al servicio | Probar la URL en el navegador; si no abre, declararlo y usar la planilla del docente |
| `La busqueda fallo` en ASF | Servicio caído o parámetro rechazado | El script sigue; anotar el mensaje de la bitácora |
| `No hay granulos descargados` | Los `.h5` no están en `<ORIGINALES>\LIDAR\<SITIO>\` | Pedir al docente la carpeta o declarar el conteo como no hecho |
| `ERROR: a la planilla le faltan las columnas` | Se tocó el encabezado de `escenas_por_pedido.csv` | Borrar la planilla, correr de nuevo `Tp1_06` para recrearla, y volver a cargar |
| `PermissionError` al escribir un CSV | El CSV está abierto en Excel | Cerrarlo y volver a correr |
| Matriz vacía en el paso 7 | Los pasos anteriores se corrieron con otro `--sitio` | Correrlos con el mismo sitio |
| `Falta la máscara de agua del Tp6` (paso 6b) | No está `Tp6_Inundaciones\05_Resultados\02_Rasters\B_agua_por_sensor_20231104_20m.tif` | Es un insumo YA VIENE HECHO: avisar al docente |

Si en el aula un servicio (Planetary Computer, ASF, CMR o ESA MAAP) no responde, el
script lo deja escrito en la bitácora y sigue; la falla se declara y se trabaja con
los resultados de referencia del Desarrollo.
