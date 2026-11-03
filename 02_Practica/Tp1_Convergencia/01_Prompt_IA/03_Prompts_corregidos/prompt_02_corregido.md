# Prompt corregido — el que produjo los scripts del Tp1

Este es el pedido que generó los siete scripts originales de `03_Scripts` (Tp1_06b y
Tp1_08 se agregaron después con pedidos propios). Es largo a
propósito: cada requisito corresponde a una línea del código, y cada línea del código
existe porque alguien la pidió. Léalo con el script abierto al lado.

---

> **Contexto.** Curso de posgrado «Sinergias multisensor y estrategias de fusión
> SAR-Óptico-LiDAR para evaluación de emergencias ambientales», Diamante, Entre
> Ríos, 2026. Práctico Tp1: verificación de convergencia multisensor. Se trabaja en
> Windows, con Miniforge y el entorno `sar` (Python 3.11, conda-forge: numpy, scipy,
> pandas, matplotlib, gdal con los lectores JPEG-2000 y HDF5, rasterio, geopandas,
> pyogrio, shapely, pyproj, h5py, scikit-image, pystac-client, planetary-computer,
> asf_search, earthaccess, requests). No se mezcla con pip.
>
> **Sitio de práctica:** `B_CONCORDIA` (Concordia – Salto Grande, río Uruguay),
> bbox WGS 84 (oeste, sur, este, norte) = (−58,25, −31,50, −57,85, −31,10). Evento:
> 04/11/2023, durante la crecida (no es el pico: es el día con Sentinel-1A y Sentinel-2B del mismo día,
> verificados). Los demás sitios del curso, con su bbox y su origen, están en
> `00_COMUN/configuracion_comun.py` (diccionario `SITIOS`): `A1_DELTA_QUEMAS`,
> `A2_IBICUY`, `B_CONCORDIA`, `C_FEDERAL`, `D_LAPAZ_VILLAGUAY`, `E_PARANA_DIAMANTE`,
> `E1_DIAMANTE_BARRANCA`, `F_BOVRIL`, `DELTA_NISAR`. Los de origen «aproximada» se
> marcan para revisar.
>
> **Grilla y referencia.** Proyección común EPSG:32721 (WGS 84 / UTM 21 S), píxel de
> 10 m, bordes ajustados a múltiplos exactos del píxel (función `grilla_sitio()` de
> `00_COMUN/funciones_comunes.py`). Valor sin dato de todo GeoTIFF: −9999.
>
> **Sensores y dónde están.**
> - Sentinel-2 L2A y Sentinel-1 RTC: Planetary Computer (STAC, sin cuenta).
> - NISAR L2 GCOV, Sentinel-1 IW SLC e IW GRD, ALOS PALSAR RTC: ASF (buscar sin
>   cuenta; descargar con cuenta de NASA Earthdata).
> - GEDI L2A versión 003 (`GEDI02_A`) e ICESat-2 ATL08 versión 007: NASA Earthdata
>   con `earthaccess`.
> - BIOMASS (banda P): catálogo STAC de ESA MAAP, colecciones `BiomassLevel1a`,
>   `BiomassLevel1b`, `BiomassLevel1c`, `BiomassLevel2a`.
> - En disco, y se leen de donde están (no se copian): NovaSAR-1 (banda S, 6 m, HH;
>   cinco escenas 47525, 47942, 47974, 50896, 50918), NISAR GCOV L (NASA) y S (ISRO)
>   del Delta, septiembre de 2026 (17, 18 y 30/09), el archivo del curso SAR CEREGEO 2023
>   (Sentinel-1 SLC 2020, SAOCOM-1A L1A 2020 y 2021) y los COSMO-SkyMed de Diamante
>   2018. Rutas por defecto en `configuracion_comun.py`, cambiables por variables de
>   entorno (`CURSO_SAR_NOVASAR`, `CURSO_SAR_NISAR_DELTA`, `CURSO_SAR_2023`,
>   `CURSO_SAR_COSMO`, `CURSO_SAR_ORIGINALES`).
>
> **La pregunta:** ¿qué sensores observan el mismo sitio en fechas compatibles con
> el evento? No la des por respondida con lo que dice un catálogo: **verificala
> dentro del sitio**.
>
> **Requisitos no negociables.**
>
> *Generales, para los siete scripts*
>
> 1. Nada se redefine en los scripts: sitios, proyección, píxel, rutas y nombres de
>    carpeta se importan de `00_COMUN/configuracion_comun.py`; las funciones comunes,
>    de `00_COMUN/funciones_comunes.py` y `00_COMUN/funciones_lidar.py`. Cada script
>    busca `00_COMUN` subiendo por el árbol de carpetas y lo agrega a la ruta de Python.
> 2. Cada script abre una **bitácora** (`Bitacora`) que imprime en pantalla y guarda
>    lo mismo en `Tp1_Convergencia/05_Resultados/06_Control_calidad/<nombre>.log`,
>    con encabezado (nombre, fecha, versión de Python y ejecutable). Al cerrar,
>    escribe `SIGUIENTE PASO:` con la orden exacta del paso siguiente y la ruta de la
>    bitácora.
> 3. Las tablas se escriben en CSV con codificación `utf-8-sig` (para que Excel
>    muestre bien las tildes), en `05_Resultados/04_Tablas/`; los vectores, en
>    `05_Resultados/03_Vectores/`; las figuras, en `05_Resultados/05_Graficos/`.
> 4. **Fechas y horas siempre de los metadatos y en UTC**, nunca de la fecha del
>    archivo en el disco: `datetime` del ítem STAC (o `start_datetime`),
>    `RawDataStartTime` del `metadata.xml` de NovaSAR, `zeroDopplerStartTime` de
>    NISAR, `startTime` del `.xemt` de SAOCOM, `startTime` de ASF, `delta_time` de
>    GEDI y ATL08 (segundos desde el 01/01/2018).
> 5. **Dos cifras de cobertura, nunca una sola**: `cobertura_huella_%` (intersección
>    del polígono declarado con el bbox del sitio, sobre el área del bbox) y
>    `pixeles_validos_%` (fracción de píxeles del sitio con dato real). Si la segunda
>    no se puede medir, la celda queda vacía: **una cifra que no se midió no se escribe**.
> 6. Si una carpeta de datos no existe o un servicio no responde, el script **no se
>    detiene**: escribe en la bitácora qué faltó, deja constancia en la tabla cuando
>    corresponda y sigue con lo siguiente.
> 7. **Ninguna credencial en el código.** Earthdata: variable `EARTHDATA_TOKEN`,
>    archivo `.netrc` del usuario (`urs.earthdata.nasa.gov`) o, en último caso, el
>    teclado con la contraseña oculta (`getpass`). ESA MAAP: variables
>    `BIOMASS_TOKEN` (ficha offline de 90 días) y `BIOMASS_CLIENT_SECRET`.
>
> *Paso 1 — `Tp1_01_sitios_a_vector.py`*
>
> 8. Escribí todos los sitios de `SITIOS` en `00_COMUN/01_AOI/sitios_curso.gpkg`,
>    capa `sitios` (EPSG:4326) y capa `sitios_utm21s` (EPSG:32721), con los campos
>    `sitio, nombre, origen, practicos, columnas, filas, superficie_km2`, y un
>    `<SITIO>.geojson` por sitio para subir a los buscadores web.
> 9. Imprimí la grilla de 10 m de cada sitio (columnas × filas y km²) y marcá con
>    `<-- REVISAR en el Tp1, paso 1` los de origen `aproximada`. Un sitio mal ubicado
>    se corrige en `configuracion_comun.py`, nunca editando el `.geojson`.
>
> *Paso 2 — `Tp1_02_inventario_local.py`*
>
> 10. NovaSAR-1: por cada escena de `NOVASAR_ESCENAS`, la huella es la envolvente
>     convexa de los puntos de enlace (GCP) del `image_HH.tif`; los píxeles válidos se
>     cuentan con `novasar_sigma0()` sobre una grilla del sitio de **100 m**
>     (`PIXEL_CONTEO`), sólo si la huella toca el sitio. Calibración del producto:
>     σ⁰ = DN² / CalibrationConstant, con la constante leída del `metadata.xml`
>     (1E+05 en las cinco escenas). El remuestreo es la media cuadrática de los DN
>     (`rms`), para promediar potencia. Si la fecha del metadato no coincide con la de
>     la configuración, avisá y que mande el metadato.
> 11. NISAR: leé de `NISAR_DELTA\BANDA_L_NASA` y `...\BANDA_S_ISRO` todos los `.h5`
>     que **no** tengan `COMPAT` en el nombre (son copias de compatibilidad para SNAP,
>     no otra escena). De `identification` tomá `boundingPolygon` (huella),
>     `zeroDopplerStartTime`, `orbitPassDirection`, `trackNumber`, `frameNumber`,
>     `productVersion`; de `GCOV/grids/frequencyA` la lista de términos de covarianza
>     y el paso de píxel. Contá píxeles válidos con `nisar_gcov_en_grilla()` sobre el
>     término `HHHH`, **sólo frecuencia A** (la B, de 80 m, no se usa), aplicando la
>     máscara del producto (0 = inválido, 255 = fuera de la adquisición, 1 a n =
>     válido) y descartando valores ≤ 0 o no finitos. Si el granulo no cubre, 0 %.
> 12. Archivo 2023 y COSMO 2018: recorré las carpetas sin entrar en `.data` ni en
>     `.SAFE`; reconocé por expresión regular los Sentinel-1 (`S1A/B_IW_SLC|GRDH_1SDV|1SSV_AAAAMMDDTHHMM`)
>     y los COSMO-SkyMed (`CSKS…_SCS|GEC|DGM_B_HI|S2|PP_…_AAAAMMDDHHMM`), y los
>     SAOCOM-1A por su `.xemt` (`SAR_EOSSP__CORE_L1A`: `startTime`, `acquiredPols`,
>     `OrbitDirection`, `acqMode`). La huella sale del `manifest.safe` (Sentinel-1) o
>     del `.kml` que acompaña al producto (SAOCOM lo guarda en `Images/`; COSMO usa
>     coordenadas sin espacios). No cuentes píxeles: están en geometría de radar.
>     No repitas la misma escena encontrada en dos carpetas.
> 13. Columnas de `inventario_local.csv`: `sensor, banda, lambda_cm, producto, escena,
>     fecha, hora_utc, pasada, modo, polarizaciones, pixel_m, sitio,
>     cobertura_huella_%, pixeles_validos_%, ruta`. Longitudes de onda: C 5,5 cm;
>     X 3,1; S 9,4; L 24,0 (NISAR) y 23,5 (SAOCOM).
> 14. Resumen final: cuántas combinaciones escena-sitio, y la lista de las
>     **engañosas**: huella ≥ 50 % y dato < 10 %.
>
> *Paso 3 — `Tp1_03_buscar_optico_y_C.py`*
>
> 15. Argumentos: `--sitio` (obligatorio, uno de `SITIOS`), `--desde` y `--hasta`
>     (obligatorios, AAAA-MM-DD), `--nubes_max` (80 por defecto) y `--dias_par`
>     (3 por defecto).
> 16. Sentinel-2 L2A (`sentinel-2-l2a`): si la nubosidad de catálogo supera
>     `--nubes_max`, no se verifica y se anota `descartada: nubes de catalogo`. Las
>     demás se verifican leyendo la SCL **sólo en la ventana del sitio a 60 m**
>     (vecino más próximo): cobertura del sitio, nubosidad dentro del sitio (píxeles
>     con dato que no son clase 4, 5, 6, 7 u 11) y fracción útil. Decisión:
>     `descartada` si cubre menos del 50 % del sitio, `descartada` si tiene más de
>     20 % de nubes dentro del sitio, `candidata` en otro caso. Guardá también la
>     tesela MGRS.
> 17. Sentinel-1 RTC (`sentinel-1-rtc`): γ⁰ lineal VV leído a 100 m; útil = fracción
>     del sitio con γ⁰ > 0; `candidata` si ≥ 50 %. Guardá órbita relativa
>     (`sat:relative_orbit`), pasada (`sat:orbit_state`) y polarizaciones: dos
>     órbitas distintas son dos geometrías y no se mezclan sin decirlo.
> 18. **Nada se descarga en este paso**: sólo se lee la ventana del sitio (los
>     productos son COG). Las URL firmadas duran alrededor de una hora.
> 19. Pares óptico-C: toda combinación de candidatas con diferencia ≤ `--dias_par`,
>     ordenada por días y por nubes en el sitio; si no hay ninguno, decilo y pedí
>     ampliar la ventana **declarándolo**.
> 20. Salidas: `planilla_MPC_<SITIO>.csv` (con `nubosidad_catalogo_%`,
>     `nubosidad_sitio_%`, `pixeles_validos_%` y `decision`) y
>     `pares_optico_C_<SITIO>.csv`.
>
> *Paso 4 — `Tp1_04_buscar_asf.py`*
>
> 21. Búsquedas con `asf_search`, intersección con el bbox del sitio, hasta 500
>     resultados: `NISAR` (dataset NISAR, nivel GCOV, banda L), `S1_SLC` (Sentinel-1,
>     SLC, IW), `S1_GRD` (Sentinel-1, GRD_HD, IW) y `ALOS` (ALOS, RTC_HI_RES, banda L
>     23,6 cm). Argumento `--solo` para elegir cuáles.
> 22. Por producto: fecha y hora, pasada, track (`pathNumber`), frame, polarización,
>     huella sobre el sitio, nombre, tamaño en MB y URL. `pixeles_validos_%` vacío.
> 23. `--descargar N` (0 por defecto) baja los N productos de mayor huella de cada
>     sensor pedido a `ORIGINALES\ASF\<SITIO>\<sensor>\`, con la sesión autenticada
>     del requisito 7. Pedí verificar los tamaños contra la columna `tamano_MB`.
> 24. Si una búsqueda falla, anotalo y seguí con el producto siguiente.
>
> *Paso 5 — `Tp1_05_buscar_lidar.py`*
>
> 25. Argumentos: `--sitio`, `--desde` (2019-04-01 por defecto), `--hasta`
>     (2026-09-30 por defecto), `--descargar`, `--solo_contar`, `--sensibilidad`
>     (0,95 por defecto).
> 26. Búsqueda con `earthaccess.search_data` de `GEDI02_A` versión `003` y `ATL08`
>     versión `007` sobre el bbox y la ventana; listá granulo, fecha y tamaño.
> 27. **Receso de GEDI**: si la ventana se superpone con el 17/03/2023 – 26/04/2024,
>     avisá que en ese lapso no hay huellas y que **no es un error**.
> 28. Descarga sólo con `--descargar`, a `ORIGINALES\LIDAR\<SITIO>\<producto>\`, con
>     `earthaccess.login(persist=True)` y hasta tres reintentos ante una interrupción.
> 29. Conteo sobre los `.h5` que haya en esa carpeta, con `funciones_lidar.py`:
>     - GEDI L2A: todas las huellas del bbox de todos los haces, con `valido` y
>       `motivo`. Filtros, en orden: bandera de calidad = 1 (campo
>       `l2a_quality_flag_rel3` en la v003, `quality_flag` en la v002; usá el que
>       exista e informá cuál), `degrade_flag = 0`, `sensitivity ≥ --sensibilidad`,
>       `surface_flag = 1`. Clasificá el haz en «potencia» (BEAM0101, BEAM0110,
>       BEAM1000, BEAM1011) o «cobertura». Guardá rh50, rh98, rh100 y
>       `elev_lowestmode` **declarada como elipsoidal**.
>     - ATL08: segmentos de 100 m de los seis haces, con `canopia_valida`
>       (`h_canopy` distinto del relleno 3,4 × 10³⁸, `urban_flag = 0`,
>       `segment_watermask = 0`) y `terreno_valido` (`h_te_best_fit` distinto del
>       relleno y no agua), y los motivos. Fuerza del haz según
>       `orbit_info/sc_orient` (0: izquierdos fuertes; 1: derechos fuertes;
>       2: transición, indeterminado). Bandera nocturna.
> 30. Salidas: `lidar_granulos_<SITIO>.csv`, `lidar_conteo_<SITIO>.csv` (producto,
>     granulos, huellas en el sitio, válidas, fechas con válidas, descartes por
>     motivo) y `lidar_<SITIO>.gpkg` con las capas `gedi_l2a` y `atl08` y **todas**
>     las huellas, válidas y descartadas, para verlas en QGIS.
>
> *Paso 6 — `Tp1_06_escenas_por_pedido.py`*
>
> 31. BIOMASS: buscá en `https://catalog.maap.eo.esa.int/catalogue/` las cuatro
>     colecciones sobre el bbox, ventana `--desde 2025-12-01 --hasta 2026-12-31` por
>     defecto, hasta 300 ítems. Sólo con `--descargar` y una ficha válida, bajá los
>     productos 1b a `ORIGINALES\BIOMASS\<SITIO>\BiomassLevel1b\`, sin volver a bajar
>     lo que ya está. Si la consulta falla, agregá una fila `consulta fallida` con el
>     error.
> 32. Planilla manual `Tp1_Convergencia/04_Tablas_de_trabajo/escenas_por_pedido.csv`
>     con las columnas `sensor, banda, lambda_cm, portal, producto, escena, fecha,
>     hora_utc, pasada, polarizaciones, pixel_m, sitio, resultado, fecha_pedido,
>     observaciones`. Si no existe, creala con una fila `EJEMPLO` (que se ignora) y
>     pedí completarla. `resultado` ∈ {obtenida, pedida, sin cobertura, sin acceso}:
>     **una ausencia documentada es información**. Controlá que no falte ninguna
>     columna y listá las filas sin fecha o sin resultado.
> 33. Salida: `planilla_por_pedido_<SITIO>.csv`.
>
> *Paso 7 — `Tp1_07_matriz_convergencia.py`*
>
> 34. Reuní **sólo escenas verificadas**: inventario local con píxeles válidos ≥ 50 %
>     (o, si no hay conteo, huella ≥ 50 %, y marcalo en la columna `fuente`),
>     Planetary Computer `candidata`, ASF con huella ≥ 50 %, por pedido `obtenida` o
>     `en catalogo`, y LiDAR sólo si el conteo dio al menos una huella válida.
> 35. Matriz sensor × fecha (`pd.crosstab`) y, con `--evento` y `--ventana` (12 días
>     por defecto), el grado con la regla de la presentación 01, diapositiva 18:
>     completa (óptico + ≥ 2 bandas SAR + LiDAR), parcial (óptico + ≥ 1 banda SAR),
>     parcial sin óptico (≥ 2 bandas SAR), un solo sensor cerca del evento (óptico
>     solo, o una sola banda SAR, dentro de la ventana), histórica (nada dentro de la
>     ventana, pero sí escenas en otras fechas) o sin datos; cada uno con su uso en el
>     curso (fusión de píxel o rasgo; sinergia o fusión de decisión; sinergia SAR
>     multibanda; mapa de ese sensor y los demás sólo para interpretar;
>     interpretación de largo plazo; declarar y cambiar).
> 36. Figura de la línea de tiempo, una fila por banda en el orden Óptico, SAR X, C,
>     S, L, P, LiDAR, con el evento en una línea vertical, letra legible (11–12 pt) y
>     **la cita de fuentes al pie** («Fuente: planillas del Tp1 (Planetary Computer,
>     ASF, NASA Earthdata, ESA MAAP, archivo del curso). Elaboración propia.»).
> 37. Salidas: `matriz_convergencia_<SITIO>.csv`, `grado_convergencia_<SITIO>.csv`,
>     `linea_tiempo_<SITIO>.png`.
>
> **Sinergia y fusión en este pedido.** El Tp1 no fusiona ni interpreta señales:
> decide qué será posible. El grado de convergencia es el que dice si después se
> podrá hacer fusión de píxel o de rasgo (completa), sinergia o fusión de decisión
> (parcial), el mapa de un solo sensor (un solo sensor cerca del evento) o sólo
> interpretación (histórica). Que el código lo escriba así, con esas
> palabras.
>
> **Formato de cada script.** Docstring al principio con: nombre, marca
> `[SE CORRE]`, número de paso, qué hace y por qué, salidas con su ruta y ejemplos de
> uso en el Miniforge Prompt. Cada script imprime qué leyó, cuántos elementos entraron
> y cuántos se descartaron (con el motivo), dónde guardó y cuál es el siguiente paso.
>
> **Lo que NO debe hacer.**
> - No uses `eo:cloud_cover` como criterio de selección.
> - No llames «cobertura» a la huella.
> - No completes una fila con lo que «debería» haber: si no hay, se declara.
> - No reintentes una búsqueda vacía de GEDI dentro del receso.
> - No uses la fecha del archivo ni la hora local.
> - No descargues nada en los pasos de verificación ni bajes escenas enteras para
>   contar píxeles cuando el producto permite leer la ventana.
> - No escribas usuario, contraseña ni ficha en ningún archivo.
> - No copies los datos originales dentro de las carpetas del práctico.

---

## La diferencia

El primero pedía **una lista de imágenes que sirven**. Éste pide **demostrar, dentro
del sitio y con el dato, cuáles sirven y cuáles no**, y deja escrito qué hacer cuando
la respuesta es «no hay».
