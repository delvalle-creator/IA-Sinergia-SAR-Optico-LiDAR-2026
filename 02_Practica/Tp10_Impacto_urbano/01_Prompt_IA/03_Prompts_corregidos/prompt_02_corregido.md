# Prompt corregido — el que produjo los scripts del Tp10

> **Nota.** Este prompt describe la versión anterior de los scripts (fusión de decisión por intersección radar–óptico, `--u_ndbi`). Los scripts actuales de `03_Scripts` salen de `prompt_03_scripts_actuales.md`, que tiene su propia verificación. Se conserva para mostrar cómo cambia el código cuando cambia el pedido.


Este es el prompt que produjo la primera versión de los programas de `03_Scripts`. Es largo a propósito: cada requisito numerado corresponde a una línea de código que existe porque alguien la pidió. Léalo con los scripts abiertos al lado.

---

> ## Contexto
>
> Curso de posgrado sobre sinergia y fusión SAR – óptico – LiDAR para emergencias
> ambientales (Diamante, Entre Ríos, octubre–noviembre de 2026). Práctico Tp10:
> **impacto urbano y subsidencia**. Lo corren estudiantes de posgrado que no son
> programadores, en Windows, desde el **Miniforge Prompt** con el entorno
> `conda` llamado **`sar`** (Python 3.11, conda-forge: numpy, scipy, pandas,
> matplotlib, gdal, rasterio, geopandas, pyogrio, shapely, pyproj, h5py,
> scikit-learn, scikit-image, pystac-client, planetary-computer, asf_search,
> earthaccess, hyp3_sdk). No agregue dependencias fuera de esa lista.
>
> **La pregunta del práctico es: ¿cómo crece la ciudad y dónde se hunde el
> terreno?**
>
> **Sitios** (ventanas en grados WGS84: oeste, sur, este, norte; están definidas
> en `00_COMUN/configuracion_comun.py`, diccionario `SITIOS`; no las redefina):
>
> - `B_CONCORDIA` (−58,25, −31,50, −57,85, −31,10): crecimiento urbano. Sitio por defecto.
> - `E_PARANA_DIAMANTE` (−60,70, −32,10, −60,45, −31,65), ventana aproximada: subsidencia.
>   Sitio por defecto de la subsidencia.
>
> **Sensores y fechas** (las verificadas están en `EVENTOS["Tp10"]`):
>
> - **C**: Sentinel-1 IW GRD RTC (γ⁰ lineal, VV y VH) del Microsoft Planetary
>   Computer, colección `sentinel-1-rtc`, la escena más cercana al 16/09/2026
>   (± 6 días). Sentinel-1 IW SLC (ASF) para la serie InSAR, 01/01/2025 a 30/09/2026.
> - **S**: NovaSAR-1 Stripmap GRD HH, 6 m, escena **47942** del 13/09/2023,
>   archivo local cedido por CSIRO. σ⁰ = DN² / CalibrationConstant (1E+05 en el
>   `metadata.xml`). Georreferenciada sólo con 4 GCP de esquina: tiene
>   desplazamientos de cientos de metros. **Cubre el 39 % de B_CONCORDIA y no
>   cubre Paraná.**
> - **L**: NISAR L2 GCOV, banda L (`LSAR`), frecuencia A, HHHH y HVHV, del
>   18/09/2026, órbita descendente. Archivo `.h5` bajado de ASF con
>   `Tp1_04_buscar_asf.py`. **No está en la carpeta NISAR del Delta**: la ruta
>   se pasa por argumento.
> - **Óptico**: Sentinel-2 L2A (Planetary Computer, `sentinel-2-l2a`), bandas
>   B04, B08, B11 y SCL, la escena más limpia **dentro del sitio** en ± 10 días
>   del 16/09/2026. Para la base de la expansión, ± 20 días del 15/09/2019.
> - **InSAR**: interferogramas de ASF HyP3 (`INSAR_GAMMA`, 10 × 2 looks,
>   40 m de píxel) con mapas de desplazamiento vertical y en la línea de visión,
>   coherencia y máscara de agua.
>
> **Grilla**: EPSG:32721 (UTM 21 S), con los bordes ajustados a múltiplos del
> píxel (`grilla_sitio()` de `00_COMUN/funciones_comunes.py`). Píxel: 20 m en
> los pasos 1 y 2 (NISAR GCOV y bandas de 20 m de Sentinel-2), 20 m también
> en la expansión (la B11 del NDBI), 40 m en la subsidencia. Todos los GeoTIFF se escriben con
> `guardar_tif()`: float32, nodata −9999, una banda con nombre por capa, y en
> los metadatos FUENTE, PROCESO, SCRIPT, FECHA_PROCESO y UNIDADES.
>
> **Estructura de carpetas** (use `ruta_tp("Tp10", ...)`, no rutas fijas):
> `02_Subsets_SNAP_QGIS` (recortes en la grilla), `04_Tablas_de_trabajo`
> (lo que digitaliza el grupo), `05_Resultados/02_Rasters`, `04_Tablas`,
> `05_Graficos` y `06_Control_calidad` (bitácoras). Los originales se leen de
> `ORIGINALES` y `NOVASAR` de `configuracion_comun.py`; nunca se copian.
>
> Reutilice las funciones de `00_COMUN` (`funciones_comunes.py` y
> `funciones_cambio.py`): `s1_rtc_mas_cercana`, `s1_rtc`, `s2_escena_mas_limpia`,
> `s2_reflectancia`, `novasar_sigma0`, `nisar_gcov_en_grilla`, `leer_en_grilla`,
> `lin_a_db`, `guardar_tif`, `leer_tif`, `grilla_de_tif`, `rasterizar`,
> `Bitacora`, `fuente_mpc`, `umbral_documentado`, `aplicar_umbral`,
> `tabla_de_coincidencias`, `fusion_pixel_o_rasgo`, `fusion_decision`,
> `indice_normalizado`, `leer_entrenamiento`, `figura_mapa`. No copie su código
> dentro de los scripts.
>
> ## Qué es sinergia y qué es fusión en este pedido
>
> - **Paso 1 = SINERGIA.** Cada banda produce SU mapa urbano. No se combinan en
>   un producto: se comparan en una tabla y el analista interpreta. Se valida
>   por coherencia física.
> - **Paso 3 = FUSIÓN DE PÍXEL.** Un clasificador recibe las capas de todos los
>   sensores en la misma grilla y produce UN mapa. Se valida con la exactitud
>   del Tp4.
> - **Paso 3b (expansión) = FUSIÓN DE DECISIÓN**, regla de intersección escrita.
> - **Paso 4 (subsidencia)**: un solo sensor en el tiempo; no es fusión.
>
> Escriba en el encabezado de cada script cuál de las tres cosas hace.
>
> ## Requisitos no negociables
>
> ### Generales
>
> 1. **Radar en LINEAL.** γ⁰ (o σ⁰ en NovaSAR, y se dice) se lee, remuestrea,
>    promedia y guarda en lineal. El dB se calcula **sólo** para umbralizar,
>    para entrar al clasificador y para mostrar, con `lin_a_db()`, que deja NaN
>    (no −∞) donde el valor es cero o negativo.
> 2. **Remuestreo**: radar y reflectancia con `average` al agregar; clases y
>    máscaras con `nearest` o `mode`. NovaSAR con media cuadrática de los DN
>    (`rms`), que equivale a promediar potencia, y después se calibra.
> 3. **NovaSAR es σ⁰; Sentinel-1 RTC y NISAR GCOV son γ⁰.** El curso no tiene
>    un modelo de ángulo local para normalizar NovaSAR fuera de SNAP. Se
>    declara en la bitácora y en la fuente; no se esconde.
> 4. **Máscara de NISAR**: aplicar el dataset `mask` del GCOV (0 = inválido,
>    255 = fuera de la adquisición, 1..n = válido). Sin ella, el borde de la
>    franja entra con valores de alrededor de −133 dB. Usar sólo la frecuencia A.
> 5. **Nube contada dentro del sitio** con la SCL (clases válidas 4, 5, 6, 7 y
>    11), no el `eo:cloud_cover` de la tesela. Máximo 20 %. Informar la cifra.
>    Descontar el desplazamiento de +1000 de los DN de Sentinel-2 desde la
>    línea de base 04.00 (25/01/2022).
> 6. **Fecha y hora UTC de cada escena tomadas de los metadatos**, nunca del
>    nombre o de la fecha del archivo. Van a la bitácora y a la cita de fuente.
> 7. **Cita de fuente** en cada GeoTIFF (etiqueta FUENTE) y al pie de cada
>    figura: organismo, sensor, producto, fecha, hora y URL del servicio.
> 8. **Bitácora**: cada script imprime y guarda en
>    `05_Resultados/06_Control_calidad/<script>_<SITIO>.log` qué leyó, cuántos
>    datos entraron y salieron, cada umbral, cada aviso y, al cerrar, la orden
>    exacta del paso siguiente.
> 9. **Credenciales**: nunca en el código. Earthdata con `.netrc` o con la
>    variable de entorno `EARTHDATA_TOKEN`; HyP3 con `.netrc` o pidiéndola por
>    teclado.
> 10. Si un servicio en línea falla (Planetary Computer, ASF), el script **lo
>     dice y sigue** con lo que tiene, sin abortar ni inventar el dato.
>
> ### Paso 1 — `Tp10_01_doble_rebote_sinergia.py` (SINERGIA)
>
> 11. Argumentos: `--sitio` (B_CONCORDIA o E_PARANA_DIAMANTE), `--pixel 20`,
>     `--fecha 2026-09-16`, `--nisar_h5` (ruta; vacío = sin banda L, y lo
>     avisa con la orden de Tp1_04 para bajarlo), `--novasar 47942`,
>     `--desplazamiento DX DY` en metros (0 0 por defecto), umbrales
>     `--u_c`, `--u_s`, `--u_l` y `--otsu`.
> 12. **Umbrales MANUALES por defecto (−3 dB, clase urbana por ENCIMA)**,
>     porque la ciudad ocupa pocos píxeles del sitio y su moda casi no se ve:
>     Otsu supone dos modas. Cada umbral se documenta con su histograma
>     (`<SITIO>_hist_<banda>.png`, línea vertical en el umbral) y con el
>     porcentaje de píxeles que deja en la clase. El texto de la bitácora dice
>     «justificar con el histograma y la referencia».
> 13. Si NovaSAR no cubre el sitio (menos de 1 % con dato), avisar y seguir sin
>     banda S. Si no se pasó `--desplazamiento`, avisar: «a 6 m un error de
>     80 m son 13 píxeles».
> 14. **Tabla de coincidencias** con `tabla_de_coincidencias()`: por par de
>     bandas, porcentaje de la clase en cada una, en ambas, sólo en una, sólo
>     en la otra y acuerdo. Sólo donde todas las bandas tienen dato. Si existe
>     `Tp4_Validacion/02_Subsets_SNAP_QGIS/<SITIO>_cobertura_control_<pixel>m.tif`,
>     separar además por clase de control (código 7 = urbano). Imprimir las
>     filas «todo el sitio» y «control: urbano». Hace falta al menos dos
>     bandas; si no, decirlo y terminar.
> 15. **Detalle**: repetir el mapa de banda S a 6, 10 y 20 m con el mismo
>     umbral y contar superficie urbana (ha), número de manchas, área media y
>     perímetro/área (1/km).
> 16. Informar cuántos píxeles usa la tabla de coincidencias (sólo los que
>     tienen todas las bandas: con NovaSAR, su huella). Cerrar con la orden del
>     paso siguiente con los argumentos que existen en `Tp10_02`
>     (`--sitio`, `--pixel`). Al cerrar, explicar cómo leer la tabla: «% solo 1» alto en C frente a L
>     suele ser vegetación densa o techos metálicos; «% solo 2» alto en L,
>     edificación entre árboles.
> 17. Advertencias que van a la bitácora: el doble rebote depende de la
>     orientación de las calles respecto de la dirección de vuelo; NovaSAR es
>     de 2023 y C y L de 2026 (lo que aparece sólo en C y L puede ser
>     crecimiento real).
> 18. Salidas: `02_Subsets_SNAP_QGIS/<SITIO>_urbano_por_banda_<pixel>m.tif`
>     (bandas lineales, `mapa_<banda>` y `bandas_que_marcan_urbano`),
>     `04_Tablas/<SITIO>_coincidencias_urbano.csv`,
>     `04_Tablas/<SITIO>_detalle_6_10_20m.csv`, `05_Graficos/<SITIO>_hist_*.png`.
>
> ### Pasos 2 y 3 — `Tp10_02_fusion_pixel_urbano.py` (variantes y FUSIÓN DE PÍXEL)
>
> 19. Leer el ráster de `Tp10_01` (misma grilla, mismo `--pixel`); si no existe,
>     terminar diciendo qué correr antes. No volver a consultar los radares.
> 20. Capas del clasificador: `C_VV_dB`, `C_VH_dB`, `S_HH_dB`, `L_HV_dB`,
>     NDBI = (B11 − B08)/(B11 + B08), NDVI = (B08 − B04)/(B08 + B04) y
>     `C_CV_VV`, coeficiente de variación local de VV **en lineal**, ventana 5,
>     exigiendo más del 60 % de la ventana con dato.
> 21. **Dos variantes de un solo sensor**, en el formato del Tp4 (1 = urbano,
>     2 = no urbano, NaN = sin dato): `<SITIO>_variante_optico.tif`
>     (NDBI > `--u_ndbi`, 0 por defecto, y NDVI < 0,3) y
>     `<SITIO>_variante_C.tif` (el mapa de VV de `Tp10_01`).
> 22. **Entrenamiento**: `04_Tablas_de_trabajo/entrenamiento_<SITIO>.gpkg`,
>     capa `entrenamiento`, campo entero `codigo`: 1 urbano denso, 2 urbano
>     abierto y periurbano, 3 vegetación, 4 agua, 5 suelo desnudo. Si no
>     existe, **crearlo vacío en EPSG:32721** con los campos `codigo` y
>     `clase`, decir qué hay que digitalizar y terminar.
> 23. **Random Forest con `fusion_pixel_o_rasgo()`**: 300 árboles, semilla
>     2026, muestreo equilibrado por clase, `class_weight="balanced"`. Sólo
>     clasifica píxeles con todas las capas.
> 24. **Dos versiones, porque NovaSAR cubre el 39 % del sitio**: `con_S`
>     (todas las capas; sólo donde hay NovaSAR) y `sin_S` (sin la banda S;
>     todo el sitio). Para cada una: capas usadas, porcentaje del sitio que
>     cubre, exactitud fuera de bolsa **rotulada OPTIMISTA** e importancia de
>     cada capa. Si una versión no tiene 50 píxeles de entrenamiento válidos,
>     decirlo y seguir con la otra.
> 25. Informar en qué porcentaje coinciden las dos versiones (urbano / no
>     urbano) donde hay NovaSAR.
> 26. Variante multisensor para el Tp4: `<SITIO>_variante_multisensor.tif`
>     a partir de la versión `sin_S` (clases 1 y 2 = urbano), porque es la que
>     cubre el sitio; y `<SITIO>_variante_multisensor_con_S.tif` a partir de
>     `con_S` (sólo la huella de NovaSAR), para validar aparte la versión con
>     banda S.
> 27. Salidas: `02_Rasters/<SITIO>_clases_<version>.tif` (clase y
>     probabilidad), `04_Tablas/<SITIO>_importancia_por_version.csv`,
>     `05_Graficos/<SITIO>_clases_<version>.png` con leyenda y fuente.
>
> ### Paso 3b — `Tp10_03_expansion_urbana.py` (FUSIÓN DE DECISIÓN)
>
> 28. **El mismo método en las dos fechas.** El Random Forest de `Tp10_02` no
>     sirve: NovaSAR y NISAR no existen en 2019. Regla, con los dos sensores
>     que hay en ambas fechas: urbano = [VV > `--u_vv` dB] **Y** [NDBI >
>     `--u_ndbi` y NDVI < 0,3]. Intersección con `fusion_decision()`: donde
>     falta uno de los dos sensores, el píxel queda sin decidir (NaN), no lo
>     decide el otro.
> 29. Argumentos: `--base 2019-09-15`, `--final 2026-09-16`, `--pixel 20`
>     (el de la B11 del NDBI), `--u_vv -3`, `--u_ndbi 0`, `--dias 12`
>     (Sentinel-1), `--dias_opt 20` (Sentinel-2). **Misma órbita**: resolver
>     primero la fecha final y buscar la base en la misma órbita relativa de
>     Sentinel-1 (`s1_rtc_mas_cercana(..., orbita=...)`), informándola. Explicar en el encabezado por qué 2019 y no antes
>     (Sentinel-2 L2A continuo desde fines de 2018 en el Planetary Computer).
> 30. Para cada fecha, informar la fecha real de cada sensor, la nube en el
>     sitio, la superficie urbana y el porcentaje de acuerdo radar–óptico.
> 31. Clases: 1 urbano en ambas fechas, 2 nuevo urbano, 3 no urbano, 4 urbano
>     sólo en la base, **rotulada «revisar»**: casi siempre es error, obra o
>     cultivo, no des-urbanización. Avisar si la clase 4 supera el 20 % de la
>     clase 2.
> 32. Informar el crecimiento: hectáreas nuevas sobre hectáreas urbanas de la
>     base, en porcentaje y en años.
> 33. Salidas: `02_Rasters/<SITIO>_expansion_<base>_<final>.tif` (clase,
>     urbano_base, urbano_final), `04_Tablas/<SITIO>_expansion_superficies.csv`
>     y la figura con leyenda y fuente.
>
> ### Paso 4 — `Tp10_04_pares_sbas.py` (red SBAS; auxiliar, ya viene hecho)
>
> 34. Buscar con `asf_search` las Sentinel-1 IW SLC del sitio entre `--desde`
>     y `--hasta`; agrupar por órbita relativa y dirección; usar la que tenga
>     más escenas (o la de `--orbita`; si no existe, terminar listando las
>     órbitas disponibles); una escena por fecha.
> 35. Unir cada fecha con sus `--vecinos` siguientes (2 por defecto, red
>     redundante). Par apto si dura `--dias_max` (48) días o menos y su base
>     perpendicular es `--base_max` (150 m) o menos. Un par sin base conocida
>     (aun pidiendo la pila de cada escena) se acepta por tiempo sólo si las
>     dos escenas son del mismo satélite o si no se obtuvo ninguna base; si
>     son de satélites distintos, se rechaza. Anotarlo y contarlo.
> 36. Avisar si alguna fecha queda sin par apto: la red queda cortada y el
>     SBAS no puede unir los subconjuntos.
> 37. Salidas: `04_Tablas/<SITIO>_red_sbas.csv` y el gráfico tiempo – base
>     perpendicular con fuente.
> 38. Con `--hyp3 N`, pedir hasta N pares a HyP3 (`submit_insar_job`,
>     `looks="10x2"`, con mapas de desplazamiento, ángulo de incidencia y
>     máscara de agua), esperar y bajar a `00_COMUN\08_Originales_crudos\HYP3\<SITIO>\`.
>     Encabezado: el proceso lleva horas y varios GB; en clase ya viene hecho.
> 39. Decir en el encabezado que **PS** (dispersores persistentes) necesita
>     StaMPS o SARPROZ y más de 20 SLC corregistrados: se explica, no se hace.
>
> ### Paso 5 — `Tp10_05_velocidad_subsidencia.py` (velocidad vertical)
>
> 40. Leer de cada par `*_vert_disp.tif` (m, positivo = ascenso, supone sin
>     movimiento horizontal), `*_corr.tif` y, si está, `*_los_disp.tif` sólo
>     para verificar el signo. Fechas tomadas del nombre del archivo HyP3.
> 41. **Apilado**: velocidad = suma de desplazamientos / suma de intervalos,
>     en mm/año, por píxel, usando sólo los pares con coherencia ≥ `--coh_min`
>     (0,3) allí. Píxel con velocidad sólo si es coherente en ≥ `--frac_min`
>     (0,9) de los pares QUE LO CUBREN (no todos cubren todo el sitio) y en
>     ≥ `--min_pares` (5). Píxel de trabajo `--pixel 40`, el de los productos
>     HyP3 con 10 × 2 looks.
> 42. **Referencia**: a cada par se le resta la mediana de la zona de
>     referencia (`--referencia`, polígonos estables digitalizados por el
>     grupo). Sin referencia, la mediana de los píxeles persistentes (coherentes
>     en ≥ `--frac_ref`, 0,9, de los pares que los cubren), y se avisa que si
>     esa zona se mueve el mapa lo esconde. NO la mediana de todos los
>     píxeles coherentes: los campos tienen sesgo de fase propio. La
>     referencia se rasteriza con todos los píxeles tocados (polígonos más
>     chicos que el píxel cuentan); con menos de 10 píxeles, avisar. Par sin
>     ningún píxel coherente en la referencia: se descarta y se dice.
> 43. **Control**: con `--control` (puntos estables NO usados como
>     referencia; los que caen fuera de la grilla o dentro de la referencia se
>     excluyen con aviso), informar media, desvío, máximo absoluto y cuántos tienen
>     dato. Criterio impreso: si la media se aleja de 0 más que el desvío, la
>     referencia no es estable o hay tendencia orbital.
> 44. Informar la correlación LOS – vertical, el porcentaje del sitio con
>     velocidad y la mediana y los percentiles 5 y 95.
> 45. Salidas: `02_Rasters/<SITIO>_velocidad_vertical.tif` (velocidad_mm_ano,
>     pares_validos, dispersion_entre_pares_mm_ano: cuánto varían los pares,
>     no el error de la velocidad), `04_Tablas/<SITIO>_pares_usados.csv` y la
>     figura recortada a ± 20 mm/año con la fuente (Sentinel-1 IW SLC;
>     interferogramas HyP3 INSAR_GAMMA, ASF DAAC, con el número de pares).
>
> ## Formato de cada script
>
> - Encabezado (docstring) en español, sin tildes en el código: nombre, marca
>   (SE CORRE / AUXILIAR / YA VIENE HECHO), número de paso, la frase de la
>   diapositiva 33 que implementa, QUÉ SE HACE, POR QUÉ (física y decisiones),
>   SALIDA con rutas y USO con un ejemplo de orden de Windows.
> - Las cuatro líneas que suben por el árbol hasta `00_COMUN`, igual que en el
>   resto del curso.
> - `argparse` con todos los valores por defecto visibles.
> - Al terminar: `log.cerrar("<orden del paso siguiente>")`.
>
> ## Lo que NO debe hacer
>
> - No rellenar con ceros ni con medias las capas que faltan.
> - No aplicar el clasificador de `Tp10_02` a 2019.
> - No informar la exactitud fuera de bolsa como exactitud del mapa.
> - No promediar ni remuestrear en dB.
> - No mezclar σ⁰ y γ⁰ sin decirlo.
> - No usar Otsu por defecto en un sitio donde la clase es rara.
> - No calcular subsidencia con un solo interferograma ni sin referencia.
> - No bajar el píxel de la subsidencia a 10 m.
> - No escribir credenciales.
> - No inventar fechas, escenas, coberturas ni cifras: lo que no se pudo leer
>   o calcular, se informa como faltante.

---

## La diferencia

El primero pedía **fusionar todo**. Éste pide **saber qué se puede fusionar con qué, en qué fecha y en qué parte del sitio**, y deja escrito que la respuesta cambia entre pasos: sinergia donde las fechas difieren, fusión de píxel donde todas las capas existen, fusión de decisión para comparar años, y un solo sensor con referencia y control para la subsidencia.
