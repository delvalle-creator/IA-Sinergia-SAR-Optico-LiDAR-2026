# Prompt corregido — el que produjo los scripts del Tp3

Este es el pedido que generó los tres scripts de `03_Scripts`. Cada requisito
corresponde a una línea del código. Léalo con el script abierto al lado.

---

> **Contexto.** Curso de posgrado «Sinergias multisensor y estrategias de fusión
> SAR-Óptico-LiDAR para evaluación de emergencias ambientales», Diamante, Entre Ríos,
> 2026. Práctico Tp3: armonización multisensor. Windows, Miniforge, entorno `sar`
> (Python 3.11, conda-forge: numpy, scipy, pandas, gdal, rasterio, geopandas, pyogrio,
> pyproj, h5py, scikit-image, pystac-client, planetary-computer).
>
> **Sitio de práctica:** `A2_IBICUY` (Delta, humedales), bbox WGS 84 (oeste, sur,
> este, norte) = (−59,30, −33,85, −59,10, −33,65), aproximada. Caso de control:
> `F_BOVRIL` (−59,53, −31,42, −59,40, −31,29), NovaSAR-1 47974 del 14/09/2023 y
> Sentinel-2 del 10/09/2023. Sitios y rutas en `00_COMUN/configuracion_comun.py`.
>
> **Grilla y referencia.** EPSG:32721 (WGS 84 / UTM 21 S). Píxel = **el más grueso del
> análisis**, por argumento; 20 m por defecto porque entra NISAR GCOV de 20 m. Bordes en
> múltiplos exactos del píxel (`grilla_sitio(sitio, pixel=...)`). Sin dato: −9999.
>
> **Datos y fechas.**
> - Radar: la pila del Tp2,
>   `Tp2_SAR_multibanda/02_Subsets_SNAP_QGIS/<SITIO>_pila_gamma0_lineal.tif`, en γ⁰ (o
>   σ⁰ declarado) **lineal**, con su tabla `<SITIO>_pila_bandas.csv` (sensor, fecha,
>   unidad, fuente). NISAR L y S del 30/09/2026 (Ibicuy); Sentinel-1 C; NovaSAR S
>   en Bovril.
> - Óptico: Sentinel-2 L2A del Planetary Computer (`sentinel-2-l2a`), bandas B02, B03,
>   B04, B08, B11, B12 y la SCL, en la fecha `--fecha_optico`.
> - Elevación: Copernicus DEM GLO-30 (`cop-dem-glo-30`), alturas sobre el geoide
>   EGM2008.
> - LiDAR: las huellas del Tp1,
>   `Tp1_Convergencia/05_Resultados/03_Vectores/lidar_<SITIO>.gpkg`, capas `gedi_l2a`
>   (GEDI L2A v003, columna `valido`) y `atl08` (ATL08 v007, columna `canopia_valida`),
>   con `fecha`, rh50, rh98 (GEDI), h_canopy (ATL08) y alturas de terreno elipsoidales.
>
> **La pregunta:** ¿cómo llevar SAR, óptico y LiDAR a una grilla y una fecha
> comparables? Y la que importa: **¿se cumplen los tres requisitos de la fusión
> (misma grilla, corregistro dentro de la tolerancia del nivel de fusión, fechas compatibles)?** No los des por cumplidos:
> **medilos**.
>
> **Requisitos no negociables.**
>
> *Paso 1 — `Tp3_01_cubo_comun.py`*
>
> 1. Argumentos: `--sitio` (obligatorio), `--pixel` (20 por defecto), `--fecha_optico`
>    (AAAA-MM-DD), `--mde` (bandera).
> 2. Declarar en la bitácora la grilla (CRS, píxel, columnas × filas) y la regla
>    aplicada: «pixel = el espaciado mas grueso de lo que se fusiona a nivel de pixel;
>    radar agregado en LINEAL», y por capa su resolución nativa y si queda agregada, igual
>    o sobremuestreada (el MDE de 30 m y la banda P de unos 50–60 m lo están).
> 3. Radar: cada banda de la pila del Tp2 llevada a la grilla con **`average`** (promedio
>    de potencia, en lineal; nunca en dB), conservando su nombre, sensor, fecha, unidad y
>    fuente desde la tabla del Tp2. Si no hay pila, decirlo y seguir sin radar.
> 4. Óptico: todos los ítems Sentinel-2 L2A de esa fecha sobre el sitio. La **SCL por
>    `mode`** (una clase no se promedia), 0 = sin dato. Reflectancias por **`average`**,
>    con el **desplazamiento de +1000** descontado cuando la línea de base de
>    procesamiento es ≥ 04.00 (leída de `s2:processing_baseline`; si falta, decidida por
>    la fecha: desde el 25/01/2022) y divididas por 10 000. Si el sitio cae en dos
>    teselas el mismo día, la primera manda y la segunda rellena lo que falta (misma
>    pasada, misma geometría).
> 5. Máscara: válidas las clases SCL **4, 5, 6, 7 y 11**. Todo píxel no válido queda
>    sin dato en **todas** las bandas ópticas.
> 6. **No «afinar» B11 y B12** a 10 m: con la grilla de 20 m se agregan como las demás.
> 7. MDE (con `--mde`): teselas GLO-30 llevadas a la grilla con bilineal, unidad «m
>    sobre EGM2008».
> 8. Salidas: `Tp3_Armonizacion/02_Subsets_SNAP_QGIS/<SITIO>_cubo_<pixel>m.tif`
>    (GeoTIFF float32, una banda por capa con su nombre: `C_S1_gamma0_VV`,
>    `L_NISAR_gamma0_HV_AAAAMMDD`, `OPT_S2_B08`, `MDE_GLO30_m`…; etiquetas `FUENTE`,
>    `PROCESO`, `SCRIPT`, `FECHA_PROCESO`, `UNIDADES`), `<SITIO>_cubo_<pixel>m_bandas.csv`
>    (`capa, sensor, fecha, unidad, fuente, pixeles_validos_%`) y
>    `05_Resultados/04_Tablas/<SITIO>_diferencias_de_fecha.csv` (`sensor_1, fecha_1,
>    sensor_2, fecha_2, diferencia_dias`, una fila por cada par de entradas
>    (sensor, fecha): dos fechas de NISAR son dos entradas distintas).
>
> *Paso 2 — `Tp3_02_medir_corregistro.py`*
>
> 9. Argumentos: `--sitio`, `--pixel` (20), `--ref` (capa que no se mueve), `--mov`
>    (capa cuyo desplazamiento se mide), `--ventanas` (4), `--min_comun` (0,8: fracción
>    mínima de dato en común por ventana). Si una capa no existe, salir con un mensaje
>    que liste las capas del cubo.
> 10. **Comparar bordes, no valores.** Radar (toda capa que no empiece por `OPT_` ni
>     `MDE_`): pasar a dB y suavizar con un filtro uniforme de 3 × 3 para atenuar el
>     speckle. Rellenar los sin dato con la mediana. Gradiente de **Sobel** (módulo) y
>     normalización a media 0 y desvío 1.
> 11. **Correlación de fase** (`skimage.registration.phase_cross_correlation`,
>     `upsample_factor=10`: una décima de píxel) en **ventanas** de una grilla
>     `--ventanas` × `--ventanas`. Sólo ventanas con al menos `--min_comun` (**80 %**) de
>     dato en común; si ninguna llega, decirlo y sugerir `--ventanas 2` o
>     `--min_comun 0.5`.
>     Por ventana: `dy_px`, `dx_px`, `corr_antes`, `corr_despues` (correlación de los
>     bordes antes y después de aplicar el desplazamiento), `usada` (False si el
>     desplazamiento empeora la correlación: esa ventana no entra a la mediana). No usar
>     el `error` de scikit-image: con la normalización de fase vale ~1 siempre.
>     El desplazamiento es el que hay que
>     **aplicar** a la capa móvil para alinearla con la de referencia.
> 12. Mediana de dx y dy, en píxeles y en metros (x hacia el este; y como −dy × píxel,
>     hacia el norte), la misma corrección en palabras («hay que mover la capa móvil X m
>     al este; la imagen está corrida X m al oeste»), la dispersión (desvío estándar)
>     entre ventanas y el rango de dy por fila y de dx por columna de ventanas.
> 13. Veredicto en dos niveles: **CUMPLE para fusión de píxel** si el módulo de la
>     mediana y la dispersión son < 0,5 píxel; **CUMPLE para fusión de rasgo o de
>     decisión** si son < 1 píxel. Si la dispersión o el rango ≥ 1: **NO CUMPLE, no es rígido**: revisar
>     la georreferencia (puntos de enlace, relieve) antes de trasladar nada. Si no: **NO
>     CUMPLE, corrimiento rígido** de X píxeles (Y m): corregirlo en el producto móvil
>     (en SNAP, Coregistration) y volver a medir. Para NovaSAR, imprimir la orden lista
>     para `Tp2_01`: `--desplazamiento DX DY` en metros (DX = dx × píxel, positivo al
>     este; DY = −dy × píxel, positivo al norte).
> 14. Salida, con el par en el nombre para que un par no pise a otro:
>     `05_Resultados/04_Tablas/<SITIO>_corregistro_<mov>_vs_<ref>.csv` con la tabla de
>     ventanas más el resumen (mediana, módulo, dispersión, rango, metros, ventanas
>     usadas, veredicto), `pixel_m`, `ref`, `mov`, y la
>     bitácora `Tp3_02_<SITIO>_<mov>_vs_<ref>.log`.
>
> *Paso 3 — `Tp3_03_lidar_en_el_cubo.py`*
>
> 15. Argumentos: `--sitio`, `--pixel` (20). Si no existe `lidar_<SITIO>.gpkg`, salir
>     diciendo que hay que correr antes `Tp1_05_buscar_lidar.py`.
> 16. **El LiDAR no se rasteriza: se lleva el cubo a la huella.** Sólo huellas válidas
>     (`valido` en GEDI, `canopia_valida` en ATL08), reproyectadas al CRS del cubo.
> 17. Soporte de extracción: círculo de **12,5 m** para GEDI (huella de 25 m) y
>     rectángulo de **100 × 14 m** orientado según la traza para ATL08, **más medio
>     píxel**. Entran los píxeles cuyo **centro** cae dentro y dentro del cubo. Marcar la
>     plausibilidad: no plausible si rh98 > 50 m o si la pasada entera tiene rh98 mediano
>     > 40 m (columnas `plausible` y `motivo_no_plausible`).
> 18. Por huella y capa: media (radar en **lineal**, y su dB en `<capa>_dB`; óptico,
>     media de reflectancias), `n_<capa>` (píxeles usados) y `dias_<capa>` (diferencia
>     entre la fecha de la huella y la de la capa; vacía si la capa no tiene fecha
>     única, como el MDE).
> 19. Copiar de la huella `rh98`, `rh50`, `h_canopy`, `elev_lowestmode_elips`,
>     `h_te_best_fit_elips`, con el sufijo `_elips` que recuerda que **son alturas
>     elipsoidales** y no se comparan con el MDE sin pasarlas a EGM2008.
> 20. Salidas: `Tp3_Armonizacion/04_Tablas_de_trabajo/<SITIO>_huellas_con_cubo.csv` y
>     `05_Resultados/03_Vectores/<SITIO>_huellas_con_cubo.gpkg` (capa `huellas`, en el
>     CRS del cubo). Bitácora con el número de huellas por producto, el radio y la
>     mediana de días LiDAR-capa por capa.
>
> *Generales*
>
> 21. Todo se importa de `00_COMUN`; nada se redefine. Bitácora por script en
>     `05_Resultados/06_Control_calidad/Tp3_0N_<SITIO>.log`, que imprima y guarde lo mismo
>     y cierre con `SIGUIENTE PASO:`. CSV en `utf-8-sig`.
> 22. Las fuentes de cada capa (organismo, sensor, producto, fecha, URL) viajan dentro del
>     GeoTIFF y en la tabla de capas.
>
> **Sinergia y fusión en este pedido.** El Tp3 **no fusiona**: comprueba si se puede.
> El cubo es la base de una fusión de píxel; la tabla de huellas, de una fusión de rasgo.
> La lectura conjunta de altura LiDAR, cruzada de radar y óptico en las huellas es
> sinergia. Que el código no diga «fusionado» en ningún lado.
>
> **Formato de cada script.** Docstring con nombre, marca `[SE CORRE]`, número de paso,
> qué hace y por qué (con la presentación del curso que lo pide), salidas con ruta y ejemplos de uso.
> Cada script imprime cuántas capas o huellas entraron, cuántos píxeles con dato, qué
> decidió y por qué, dónde guardó y el siguiente paso.
>
> **Lo que NO debe hacer.**
> - No uses bilineal para agregar a un píxel más grueso, ni promedies radar en dB.
> - No remuestrees la SCL con nada que no sea la moda.
> - No lleves a 10 m lo que mide 20 m.
> - No afirmes que dos capas están corregistradas porque comparten la grilla.
> - No correlaciones valores de óptico contra radar: usá bordes.
> - No apliques ningún desplazamiento sin medirlo, ni des por buena una traslación si la
>   dispersión entre ventanas es grande.
> - No interpoles las huellas LiDAR a una superficie.
> - No compares alturas elipsoidales con el MDE sin convertirlas.
> - No ocultes la diferencia de fechas: escribila por par y por huella.

---

## La diferencia

El primero pedía **un cubo para el clasificador**. Éste pide **la prueba** de que el
cubo se puede usar: la grilla justificada, el corregistro medido con su incertidumbre,
las fechas escritas, y el LiDAR respetado como muestra.
