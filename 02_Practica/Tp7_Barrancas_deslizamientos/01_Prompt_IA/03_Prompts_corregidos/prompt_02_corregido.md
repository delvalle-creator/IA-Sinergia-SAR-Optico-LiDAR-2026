# Prompt corregido — el que produjo los scripts del Tp7

---

> **Contexto.**
>
> Curso de posgrado «Sinergias multisensor y estrategias de fusión
> SAR-Óptico-LiDAR para evaluación de emergencias ambientales», Diamante (Entre
> Ríos), 2026. Práctico Tp7: barrancas y deslizamientos.
>
> Sitio `E1_DIAMANTE_BARRANCA`: barranca del río Paraná en Diamante. Caja WGS84
> (lon_min, lat_min, lon_max, lat_max) = (−60.71, −32.135, −60.575, −32.015),
> tomada del `.kml` de la escena COSMO-SkyMed Spotlight del 20/10/2018. La caja,
> la proyección y las rutas **no se escriben en los scripts**: se importan de
> `00_COMUN/configuracion_comun.py` (`SITIOS`, `EPSG`, `ORIGINALES`,
> `COSMO_DIAMANTE`, `ruta_tp`). Las funciones de lectura, grilla, escritura y
> bitácora se importan de `00_COMUN/funciones_comunes.py`, y la fusión de decisión
> de `00_COMUN/funciones_cambio.py` (`fusion_decision`). Cada script encuentra
> `00_COMUN` subiendo por el árbol de carpetas desde su propia ubicación.
>
> Grilla común: EPSG:32721 (WGS 84 / UTM 21 S), bordes múltiplos exactos del
> píxel (`grilla_sitio`). Píxel de 10 m para la interferometría y de 30 m para
> los volúmenes. Valor sin dato de los GeoTIFF: −9999.
>
> Entorno: Miniforge, entorno `sar` (`00_COMUN/entorno_sar.yml`: Python 3.11,
> numpy, pandas, rasterio, geopandas, shapely, pyproj, asf_search, hyp3_sdk,
> todo de conda-forge). Windows; se corre desde el Miniforge Prompt.
>
> Datos:
>
> - **Banda X.** COSMO-SkyMed Himage (3 m) del 12, 15, 18, 19 y 28/10/2018 y
>   Spotlight (1 m) del 20/10/2018, en `COSMO_DIAMANTE`
>   (`F:\HFdV COURSES\CEREGEO\2018\TelSAR\DIAMANTE`). Par interferométrico
>   15/10–19/10/2018 procesado en SNAP en el curso 2023
>   (`...\InSAR HI\*_Stack_ifg_dinsar_flt_TC.dim`), **con la banda `Unw_Phase`
>   toda en cero porque el desenrollado SNAPHU nunca se importó**: el estudiante
>   rehace el desenrollado en SNAP y exporta desplazamiento (o fase desenrollada)
>   y coherencia a GeoTIFF.
> - **Banda C.** Sentinel-1 IW SLC del catálogo de ASF (búsqueda sin cuenta),
>   procesado en SNAP (cadena TOPS) o pedido al servicio HyP3 de ASF (GAMMA), que
>   devuelve `*_corr.tif`, `*_unw_phase.tif`, `*_los_disp.tif`, `*_vert_disp.tif`.
> - **Banda L.** SAOCOM, sólo si se consigue un par; para octubre de 2018 no hay.
> - **Ladera.** `COSMO_DIAMANTE\GRIETAS\barranca-periferia_Polygon.shp`
>   (relevamiento del curso 2018; tiene autointersecciones).
> - **MDE.** Recortados al sitio en `02_Subsets_SNAP_QGIS\QGIS_GeoTIFF`: IGN 5 m
>   (vuelo de 2013, superficie, SRVN16), Copernicus DEM GLO-30 (TanDEM-X 2011–2015,
>   superficie, EGM2008) y FABDEM (terreno, EGM2008). Ninguno es posterior al evento.
> - **ICESat-2 ATL08** del sitio, ya filtrado por `Tp1_05` (control del MDE).
>
> **La pregunta:** ¿hay deformación previa en la ladera y qué volumen se
> movilizó? No la dé por respondida. Puede que la respuesta sea «no se detecta
> por encima del ruido», y eso hay que poder decirlo con números.
>
> **Requisitos no negociables.**
>
> *Script 1, `Tp7_01_pares_insar_C.py` (búsqueda y pedido de pares en banda C)*
>
> 1. Buscar con `asf_search.search(platform="SENTINEL-1", processingLevel="SLC",
>    beamMode="IW", intersectsWith=<caja del sitio en WKT>, start, end,
>    maxResults=1000)`.
> 2. Período por defecto `--desde 2018-09-15 --hasta 2018-11-15`, **porque el par
>    X es del 15–19/10/2018** y para comparar o fusionar bandas todas tienen que
>    mirar el mismo período. Explicar en el docstring que correrlo con fechas
>    recientes (`EVENTOS["Tp7"]["serie_c"]` = 2025-01-01 a 2026-09-30) responde
>    otra pregunta y ya no es fusión con la banda X.
> 3. Agrupar por (órbita relativa `pathNumber`, pasada `flightDirection`), ordenar
>    por fecha y formar **pares consecutivos** dentro de cada grupo.
> 4. Línea de base perpendicular de cada escena respecto de la primera de la
>    órbita, pidiendo la pila a ASF (`stack()`, propiedad
>    `perpendicularBaseline`); la del par es |b2 − b1|. Si la pila no responde,
>    seguir sin línea de base y decirlo en la bitácora.
> 5. Marcar el par como apto si `dias <= --dias_max` (24) y línea de base
>    `<= --base_max` (150 m) o desconocida. Escribir en la bitácora el porqué de
>    cada criterio (coherencia, fase topográfica residual, misma geometría).
> 6. Guardar `Tp7_Barrancas_deslizamientos/05_Resultados/04_Tablas/E1_pares_S1.csv`
>    (UTF-8 con BOM) con `orbita, pasada, fecha_1, fecha_2, dias,
>    base_perpendicular_m, apto, escena_1, escena_2`, e imprimir los diez mejores
>    pares aptos ordenados por días y línea de base.
> 7. Con `--hyp3 N` (por defecto 0), pedir los N mejores a HyP3 con
>    `submit_insar_job(..., looks="10x2", include_displacement_maps=True,
>    include_inc_map=True, apply_water_mask=True)`, nombre
>    `Tp7_E1_<fecha_1>_<fecha_2>`, esperar con `watch` y bajar a
>    `ORIGINALES\HYP3\E1_DIAMANTE_BARRANCA\`. La cuenta de NASA Earthdata
>    **nunca** se escribe: `.netrc` o pedido por teclado.
>
> *Paso en SNAP (no es script: se documenta)*
>
> 8. Describir el desenrollado de la banda X: el producto `_TC` no se puede
>    desenrollar (SNAPHU trabaja en geometría de radar); usar el interferograma
>    filtrado sin `_TC`, recortarlo, `Snaphu Export` (DEFO, MCF), correr `snaphu`
>    con la orden de la cabecera de `snaphu.conf`, `Snaphu Import`, `Phase to
>    Displacement` (que deja sólo `displacement`), y dos `Range-Doppler Terrain
>    Correction` a 10 m con los mismos parámetros: una del desplazamiento y otra
>    de `coh_*` desde el recorte. Exportar cada una a GeoTIFF. Carpetas sin
>    espacios ni tildes.
>
> *Script 2, `Tp7_02_coherencia_y_deformacion.py` (sinergia y fusión de decisión)*
>
> 9. Entradas por banda (x, c, l): `--<b>_desp` (desplazamiento LOS en metros) o
>    `--<b>_fase` (fase desenrollada en radianes) y `--<b>_coh`. Una banda entra
>    sólo si tiene desplazamiento o fase **y** coherencia.
> 10. Con fase: `d = −λ · fase / (4π)`, la convención de `Phase to Displacement`
>     de SNAP. λ por defecto: X 0,03123 m (9,6 GHz), C 0,05547 m (5,405 GHz),
>     L 0,2350 m (1,275 GHz), modificables con `--lambda_x/c/l`.
> 11. Todo se lee en la grilla del sitio a `--pixel` (10 m) sin afinar por debajo
>     del píxel nativo: la X de 2 m por promedio (`average`), la C de 40 m por
>     vecino más cercano declarado (o promedio si la grilla es de 40 m o más);
>     nunca bilineal hacia un píxel más chico (`leer_en_grilla`). En la X, la fase
>     de la componente 0 de SNAPHU (sin confianza) se anula. La coherencia ≤ 0 pasa a sin dato (SNAP
>     escribe 0 fuera de la escena).
> 12. **Banda vacía:** si el valor absoluto máximo del desplazamiento es cero en
>     todo el sitio, escribir en la bitácora que eso no es estabilidad sino una
>     banda vacía (desenrollado no importado), anular el desplazamiento de esa
>     banda e informar sólo su coherencia.
> 13. Ladera: el shapefile del relevamiento, o el que se pase con `--ladera`.
>     Si no existe, terminar con un mensaje claro. Reparar la topología con
>     `make_valid` (no cambia la forma) y guardar
>     `04_Tablas_de_trabajo/E1_ladera_reparada.gpkg`.
> 14. Zona de referencia: anillo de `--anillo` m (500) alrededor de la ladera,
>     guardado en `04_Tablas_de_trabajo/E1_zona_referencia.gpkg`, **sin el agua**:
>     quitar los píxeles con ocurrencia ≥ 50 % en el JRC Global Surface Water
>     (`jrc_ocurrencia`); si no hay conexión, avisar que el anillo puede incluir
>     el río. Opción `--zona_estable <gpkg>` que reemplaza el anillo por un
>     polígono digitalizado. Informar los píxeles de cada zona. El
>     desplazamiento de cada banda se refiere a la **mediana de la referencia**
>     en los píxeles con coherencia ≥ `--coh_min` (0,3): InSAR mide diferencias.
> 15. Por banda, en una fila de
>     `05_Resultados/04_Tablas/E1_coherencia_y_desplazamiento.csv`:
>     `coherencia_media_ladera`, `coherencia_media_referencia`,
>     `%_ladera_coherente`, `desp_mediana_ladera_m`, `desp_p05_ladera_m`,
>     `desvio_referencia_m`, `nmad_referencia_m`, la pasada y la incidencia.
>     Imprimir lo mismo en mm, y dibujar los histogramas del desplazamiento y de
>     la coherencia con la línea de cada umbral.
> 16. Si el desvío en la referencia supera `--umbral_m` (0,01 m), advertir que la
>     detección en esa banda no es confiable (atmósfera, desenrollado).
> 17. **SINERGIA:** la tabla anterior. Cada banda produce su resultado; no se
>     combinan valores. Se interpreta con la física: la onda más larga conserva
>     más coherencia en vegetación. El docstring aclara que la diapositiva 30
>     plantea la sinergia con C y L, y que en octubre de 2018 es X frente a C
>     (SAOCOM-1A se lanzó ese mes: no hay par en L).
> 18. **FUSIÓN DE DECISIÓN:** por banda, decisión = signo del desplazamiento
>     relativo donde |d| > umbral y coherencia suficiente (0 si no supera,
>     sin dato si no es coherente). Una banda vacía no entra. Separar positivos y
>     negativos y combinar con `fusion_decision(..., "interseccion",
>     minimo_votos=n)`, n = número de bandas con desplazamiento válido
>     (intersección **estricta**): un píxel se decide sólo si todas las bandas
>     tienen dato coherente; +1 si todas superan el umbral con el signo que
>     tendría en su línea de visión un movimiento hipotético (azimut e
>     inclinación por parámetro), proyectado con la pasada, el rumbo y la
>     incidencia de cada banda; −1 si todas lo superan con el signo contrario; 0
>     si no; sin decidir si falta alguna. Si las pasadas difieren o no se
>     declaran, no interpretar el signo: informar sólo la coincidencia de
>     detección. Requiere al menos dos
>     bandas; con una sola, escribir «hay medición, pero no fusión de decisión».
> 19. Guardar `05_Resultados/02_Rasters/E1_deformacion_confirmada.tif` con dos
>     bandas, `deformacion_confirmada` y `bandas_que_votaron`, con la fuente y la
>     regla en los metadatos (`guardar_tif`: FUENTE, PROCESO, SCRIPT,
>     FECHA_PROCESO).
> 20. Control escrito en la bitácora: contar los píxeles confirmados en la ladera
>     y en la referencia, cuántos píxeles de la ladera quedaron decididos (en
>     número y en porcentaje, aclarando cuántas observaciones independientes da
>     la C de 40 m) y, con una opción, en una zona de control independiente de la
>     usada como referencia.
> 21. Declarar en el docstring que comparar LOS de satélites distintos sin
>     proyectar a la vertical es aproximado.
>
> *Script 3, `Tp7_03_cicatriz_y_volumen.py` (volumen)*
>
> 22. Polígonos en `04_Tablas_de_trabajo/E1_cicatriz_y_deposito.gpkg`, capa
>     `formas`, campos `tipo` (`cicatriz` o `deposito`) y `fuente`. Si no
>     existe, crearlo vacío en EPSG:32721 con tipo de geometría polígono
>     declarado (para que QGIS habilite el dibujo), avisar y terminar; esa primera
>     corrida no pide los MDE.
> 23. `--antes` y `--despues` necesarios desde la segunda corrida (si faltan,
>     terminar con un mensaje); `--pixel` 30 m por defecto (ningún MDE se
>     afina por debajo del más grueso); lectura por promedio en la grilla del sitio. `dZ = después − antes`.
> 24. **Sesgo y ruido en zona estable:** mediana y desvío de dZ en
>     `--zona_estable` o, si no se da, en `E1_zona_referencia.gpkg` del paso 2
>     sin el agua del JRC (ocurrencia ≥ 50 %; sin conexión, avisar); si no existe
>     ninguna, terminar con un mensaje. Restar el sesgo antes de
>     cualquier volumen. Un volumen sin ese control no se informa.
> 25. Volumen perdido = suma de dZ < 0 en la cicatriz × área del píxel; volumen
>     ganado = suma de dZ > 0 en el depósito × área del píxel. Informar área,
>     dZ medio, volumen, volumen detectable (sólo píxeles sobre 2 desvíos con el
>     signo esperado), incertidumbre (2σ × área del píxel × √n, declarando que
>     supone errores independientes), el porcentaje sobre 2 desvíos con el signo
>     esperado y con el contrario, sesgo restado, ruido y NMAD, en
>     `05_Resultados/04_Tablas/E1_volumenes.csv`, más las mismas cifras en una
>     escarpa de control lejos de las formas.
> 26. Escribir en el docstring los límites de los MDE: datum (decímetros),
>     resolución (5 frente a 30 m) y fecha; el sistema vertical del IGN (SRVN16)
>     se verifica en sus metadatos.
> 27. Cerrar con: «detectable sólo si supera el límite de detección con el signo
>     esperado Y el patrón no se repite fuera de la forma (control en la escarpa
>     vecina)».
>
> *Comunes a los tres*
>
> 28. Radar: la coherencia es adimensional (0 a 1); el desplazamiento, en metros
>     en la línea de visión. Ningún promedio de retrodispersión en dB.
> 29. Bitácora con `Bitacora` en `05_Resultados/06_Control_calidad/`
>     (`Tp7_01_pares.log`, `Tp7_02_deformacion.log`, `Tp7_03_volumen.log`): lo
>     que se imprime es lo que se guarda, con la versión de Python.
> 30. Cada script empieza con un docstring que dice: paso, marca (SE CORRE),
>     pregunta, entradas, salidas con su ruta, y USO con la orden exacta. Termina
>     imprimiendo el SIGUIENTE PASO.
> 31. Comentarios y mensajes en español, sin tildes en el código (consola de
>     Windows).
>
> **Lo que NO debe hacer.**
>
> - No interpretar como estable una banda cuyo desplazamiento vale cero en todo.
> - No promediar desplazamientos de bandas o geometrías distintas.
> - No fusionar un par C de otro período con el par X.
> - No restar MDE sin medir y restar el sesgo de una zona estable.
> - No escribir credenciales, ni rutas absolutas fuera de `configuracion_comun.py`.
> - No usar la exactitud de un modelo como validación: aquí no hay modelo, hay
>   reglas, y el control es la zona estable.

---

## La diferencia

El primero pedía **un mapa de deformación y un volumen**. Éste pide **saber si
cada banda tiene dato, del mismo período, referido a una zona estable**, y deja
escrito cuándo la respuesta honesta es «no detectable».
