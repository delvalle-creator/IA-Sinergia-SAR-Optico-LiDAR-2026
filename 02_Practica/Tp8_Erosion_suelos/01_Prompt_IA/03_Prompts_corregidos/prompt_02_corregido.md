# Prompt corregido — el que produjo los scripts del Tp8

---

> **Contexto.**
>
> Curso de posgrado «Sinergias multisensor y estrategias de fusión
> SAR-Óptico-LiDAR para evaluación de emergencias ambientales», Diamante (Entre
> Ríos), 2026. Práctico Tp8: erosión de suelos y cárcavas.
>
> Sitio `F_BOVRIL`: Bovril y su entorno rural, centro de Entre Ríos. Caja WGS84
> (lon_min, lat_min, lon_max, lat_max) = (−59.53, −31.42, −59.40, −31.29), . La caja, la proyección, las rutas y las escenas NovaSAR **no se
> escriben en los scripts**: se importan de `00_COMUN/configuracion_comun.py`
> (`SITIOS`, `EPSG`, `ruta_tp`, `NOVASAR`). Las lecturas, la grilla, la
> calibración de NovaSAR, la escritura y la bitácora vienen de
> `00_COMUN/funciones_comunes.py`; el índice normalizado, el entrenamiento y el
> Random Forest, de `00_COMUN/funciones_cambio.py`. Cada script encuentra
> `00_COMUN` subiendo por el árbol de carpetas.
>
> Grilla común: EPSG:32721 (UTM 21 S), píxel de 10 m, bordes múltiplos del píxel
> (`grilla_sitio`). Sin dato: −9999.
>
> Entorno: Miniforge, entorno `sar` (Python 3.11, numpy, scipy, pandas,
> rasterio, geopandas, pystac-client, planetary-computer, scikit-learn; todo de
> conda-forge). Windows, Miniforge Prompt.
>
> Datos:
>
> - **Óptico.** Sentinel-2 L2A de 2023, Microsoft Planetary Computer (sin cuenta),
>   bandas B02, B04, B08, B11 y SCL. Par óptico verificado: 10/09/2023.
> - **Banda S.** NovaSAR-1 Stripmap GRD HH, 6 m, escena 47974 del 14/09/2023
>   (cubre el 92 % del sitio), cedida por CSIRO, en
>   `E:\IMÁGENES NOVASAR-1 2023 2024\ENTRE RIOS-SANTA FE`.
>   σ⁰ = DN²/CalibrationConstant, con la constante (1E+05) leída del
>   `metadata.xml`. El `image_HH.tif` trae sólo los cuatro puntos de esquina
>   como GCP. Con ellos el corrimiento es de cientos de metros y no rígido; con los
>   84 puntos de enlace del `metadata.xml`, la banda S queda 80 m al este y 20 m al
>   sur de Sentinel-2 y se corrige moviéndola 80 m al oeste y 20 m al norte.
> - **Banda C.** Sentinel-1 RTC VV y VH (γ⁰ lineal) del Planetary Computer, del
>   14/09/2023 o de ± 6 días.
> - **Relieve.** Copernicus DEM GLO-30 del Planetary Computer.
>
> **La pregunta:** ¿dónde hay suelo expuesto a la erosión y dónde avanzan las
> cárcavas? El control del práctico es «los lotes recién labrados no se
> clasifican como erosión». No lo dé por cumplido: mídalo.
>
> **Requisitos no negociables.**
>
> *Script 1, `Tp8_01_frecuencia_suelo_desnudo.py`*
>
> 1. Buscar todas las Sentinel-2 L2A del año `--anio` (2023) sobre el sitio con
>    nubosidad de catálogo menor que `--nubes_max` (60 %).
> 2. Para cada escena, máscara de píxeles útiles **dentro del sitio** con la SCL
>    (clases 4, 5, 6, 7 y 11 válidas) e informar el % útil. Descartar la escena si
>    menos del 20 % del sitio es útil, y anotarla igual en la tabla.
> 3. Reflectancia = (DN − desplazamiento) / 10000, con desplazamiento = 1000 si
>    la línea de base de procesamiento es ≥ 04.00 (leída de los metadatos, o
>    desde el 25/01/2022 si falta). Promedio al agregar: `average`.
> 4. NDVI = (B08 − B04)/(B08 + B04); BSI = ((B11 + B04) − (B08 + B02)) /
>    ((B11 + B04) + (B08 + B02)). Suelo desnudo si NDVI < `--ndvi_max` (0,25)
>    **y** BSI > 0, sólo en píxeles útiles.
> 5. Acumular por mes: un mes es «desnudo» si **más de la mitad** de sus
>    observaciones válidas lo fueron. Resultado: `meses_suelo_desnudo` (0–12) y
>    `meses_con_observacion` (0–12); sin dato donde no hubo observación.
> 6. Guardar `02_Subsets_SNAP_QGIS/F_frecuencia_suelo_desnudo_<anio>_<pixel>m.tif`
>    con las dos bandas, la fuente (ESA – Copernicus, Sentinel-2 MSI L2A, número
>    de escenas usadas, Planetary Computer con su URL) y el proceso con el umbral.
> 7. Guardar `05_Resultados/04_Tablas/F_escenas_opticas_<anio>.csv` (`fecha`,
>    `id`, `util_%`, `usada`, `desnudo_%_del_util`).
> 8. Imprimir la mediana de meses observados y el % del sitio en cuatro clases:
>    nunca, 1–2 meses (labranza), 3–5 meses, 6 o más (persistente). Escribir en
>    el docstring la lectura: 1–2 meses es labranza normal, no erosión.
>
> *Script 2, `Tp8_02_textura_S_y_C.py` (SINERGIA)*
>
> 9. NovaSAR: σ⁰ lineal en la grilla con `novasar_sigma0`, que proyecta por GCP
>    y remuestrea con la **media cuadrática** de los DN (rms² = media de la
>    potencia) antes de calibrar. Escena por defecto `--novasar 47974`.
> 10. `--desplazamiento DX DY` en metros (por defecto 0 0): la CORRECCIÓN que
>     se aplica al producto, DX positivo = mover al este, DY positivo = mover al
>     norte. Si es 0 0, escribir en la bitácora el aviso, cómo medirlo (`Tp3_02` o
>     Medir línea en QGIS) y el signo: si la banda S está 80 m al este y 20 m al sur,
>     la corrección es `--desplazamiento -80 20`.
> 11. Sentinel-1 RTC VV y VH de la escena **más cercana** a `--fecha_c`
>     (2023-09-14) dentro de ± 6 días (`s1_rtc_mas_cercana`). La fecha de NovaSAR
>     se toma de `NOVASAR_ESCENAS` para la escena de `--novasar` (nunca fija en el
>     código). Valores ≤ 0 a sin dato. Si no hay escena o no hay red,
>     seguir con la banda S sola y decirlo.
> 12. Textura = coeficiente de variación local en una ventana de `--ventana`
>     (5) píxeles: desvío/media **en potencia lineal**, contando sólo píxeles con
>     dato, y exigiendo más del 60 % de la ventana con dato.
> 13. Escribir en el docstring por qué se compara contra una zona homogénea del
>     mismo producto (el speckle solo ya da un CV) y que SNAP tiene la textura de
>     Haralick para comparar.
> 14. Guardar `02_Subsets_SNAP_QGIS/F_textura_S_C_<pixel>m.tif` con
>     `S_NovaSAR_sigma0_HH`, `S_CV_HH`, `C_S1_gamma0_VV`, `C_CV_VV`,
>     `C_S1_gamma0_VH`, `C_CV_VH`, y la fuente de cada sensor en los metadatos
>     (SSTL – CSIRO con escena, fecha, constante y URL; ESA – Copernicus con fecha
>     y hora de Sentinel-1).
> 15. Informar la diferencia de días entre S y C y advertir que la lluvia entre
>     fechas cambia la retrodispersión.
> 16. **SINERGIA:** con la frecuencia del paso 1 del año `--anio` (2023), leída
>     por vecino más próximo,
>     tabla del CV mediano de cada banda por clase (nunca, 1–2, 3–5, ≥ 6 meses), en
>     `05_Resultados/04_Tablas/F_textura_por_frecuencia.csv`. Cada banda produce
>     su indicador; no se combinan.
>
> *Script 3, `Tp8_03_susceptibilidad.py` (FUSIÓN DE RASGOS)*
>
> 17. Rasgos en la grilla de 10 m: `meses_suelo_desnudo` (paso 1, año `--anio`,
>     2023 por defecto), todas las
>     capas de textura `*_CV_*` del paso 2, y `pendiente_grados` calculada del
>     Copernicus DEM GLO-30 (gradiente centrado). Declarar que a 30 m la pendiente
>     de una cárcava no se resuelve.
> 18. Variante **solo óptico**: 1 si `meses_suelo_desnudo` ≥ 6, 2 si no;
>     `05_Resultados/02_Rasters/F_variante_optico.tif`. Se escribe antes de mirar
>     el entrenamiento.
> 19. Entrenamiento: `04_Tablas_de_trabajo/entrenamiento_F.gpkg`, capa
>     `entrenamiento`, campo `codigo` (1 erosión activa o cárcava, 2 suelo
>     estable) y `clase`. Si no existe, crearla vacía en EPSG:32721, avisar y
>     terminar.
> 20. Random Forest con `fusion_pixel_o_rasgo`: 300 árboles, semilla 2026,
>     `class_weight="balanced"`, `min_samples_leaf=2`, muestreo equilibrado por
>     clase hasta 20 000 píxeles, sólo píxeles con dato en todos los rasgos.
> 21. Susceptibilidad = probabilidad de la clase 1 (no la de la clase ganadora),
>     en `F_susceptibilidad.tif`. Variante **multisensor**: 1 si la
>     susceptibilidad ≥ `--umbral` (0,5), 2 si no, en `F_variante_multisensor.tif`.
> 22. Imprimir la exactitud fuera de bolsa **rotulada OPTIMISTA** y la
>     importancia de cada rasgo, ordenada. La exactitud que se informa es la del
>     Tp4.
> 23. Imprimir la superficie susceptible (ha) de la multisensor y la de solo
>     óptico, y cerrar indicando Tp4_02 y Tp4_03 para las dos variantes.
>
> *Comunes a los tres*
>
> 24. SAR en lineal (σ⁰ en NovaSAR, porque el producto no permite otra cosa, y se
>     dice; γ⁰ en Sentinel-1); dB sólo para mirar.
> 25. Todos los GeoTIFF con `guardar_tif`: FUENTE, PROCESO, SCRIPT,
>     FECHA_PROCESO y UNIDADES en los metadatos.
> 26. Bitácora (`Bitacora`) en `05_Resultados/06_Control_calidad/`:
>     `Tp8_01_suelo_desnudo.log`, `Tp8_02_textura.log`,
>     `Tp8_03_susceptibilidad.log`.
> 27. Docstring con paso, marca, pregunta, referencia a la sección de la guía general (11.2 a 11.7), salidas y
>     USO; cada script termina con el SIGUIENTE PASO.
>
> **Lo que NO debe hacer.**
>
> - No usar una sola fecha óptica para decidir erosión.
> - No usar la nubosidad de la tesela como nubosidad del sitio.
> - No calcular textura en dB ni agregar SAR con vecino más próximo.
> - No comparar NovaSAR con Sentinel-2 sin corregir y medir el desfase.
> - No informar la exactitud fuera de bolsa como exactitud del mapa.
> - No escribir rutas absolutas ni credenciales en los scripts.

---

## La diferencia

El primero pedía **un mapa de erosión**. Éste pide **separar la erosión de la
labranza con la persistencia en el tiempo**, poner cada sensor en la misma grilla
y en sus unidades, y dejar la exactitud a una muestra independiente.
