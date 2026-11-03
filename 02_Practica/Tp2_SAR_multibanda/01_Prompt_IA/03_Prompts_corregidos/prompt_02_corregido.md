# Prompt corregido — el que produjo los grafos y los scripts del Tp2

Este es el pedido que generó los tres grafos de `09_Grafos_SNAP` y los cuatro scripts
de `03_Scripts`. Cada requisito corresponde a un parámetro de un nodo o a una línea del
código. Léalo con el grafo abierto en el Graph Builder y el script al lado.

---

> **Contexto.** Curso de posgrado «Sinergias multisensor y estrategias de fusión
> SAR-Óptico-LiDAR para evaluación de emergencias ambientales», Diamante, Entre Ríos,
> 2026. Práctico Tp2: preprocesamiento SAR multibanda. Windows, Miniforge, entorno
> `sar` (Python 3.11, conda-forge: numpy, pandas, matplotlib, gdal con lector HDF5,
> rasterio, geopandas, pyogrio, shapely, pyproj, h5py, scikit-image, pystac-client,
> planetary-computer). SNAP 9 o posterior para los grafos.
>
> **Sitio de práctica:** `A2_IBICUY` (Delta, humedales de Ibicuy), bbox WGS 84
> (oeste, sur, este, norte) = (−59,30, −33,85, −59,10, −33,65), ubicación aproximada.
> Alternativas: `DELTA_NISAR` (−60,16, −33,83, −58,72, −32,96), `F_BOVRIL`
> (−59,53, −31,42, −59,40, −31,29) con NovaSAR, `A1_DELTA_QUEMAS` (−59,96, −33,36,
> −59,72, −33,07) con SAOCOM 2020. Todos en `SITIOS` de
> `00_COMUN/configuracion_comun.py`.
>
> **Grilla y referencia.** EPSG:32721 (WGS 84 / UTM 21 S), píxel de 10 m, bordes en
> múltiplos exactos del píxel (`grilla_sitio()`). Sin dato: −9999.
>
> **Sensores y fechas.**
> - C: Sentinel-1 IW GRD (SNAP) y Sentinel-1 RTC del Planetary Computer
>   (`sentinel-1-rtc`, γ⁰ lineal, VV y VH), la misma fecha; Sentinel-1 IW SLC de 2020
>   del archivo del curso 2023 (SNAP).
> - S: NISAR GCOV banda S (ISRO), 30/09/2026 sobre Ibicuy (17 y 18/09/2026 en otros sitios), en
>   `00_COMUN\08_Originales_crudos\NISAR_DELTA\BANDA_S_ISRO` (si existe); NovaSAR-1 GRD HH, 6 m (escenas 47942 del
>   13/09/2023, 47974 del 14/09/2023, etc.), σ⁰ = DN² / CalibrationConstant (1E+05).
> - L: NISAR GCOV banda L (NASA), 30/09/2026 sobre Ibicuy (17 y 18/09/2026 en otros sitios), en
>   `00_COMUN\08_Originales_crudos\NISAR_DELTA\BANDA_L_NASA`; SAOCOM-1A L1A Stripmap QP/DP 2020 y 2021
>   (SNAP).
> - P: BIOMASS L1b (ESA MAAP), franja D, 17/09/2026, si cubre el sitio.
> - X: COSMO-SkyMed (Diamante, 2018), si cubre el sitio.
> - Modelo de elevación: Copernicus DEM GLO-30.
>
> **La pregunta:** ¿cómo llevar escenas en bandas C, S, L y P a γ⁰ comparable, y qué
> ve cada banda sobre la misma cubierta? Respondela con **contrastes entre cubiertas**,
> no con valores absolutos.
>
> **Requisitos no negociables.**
>
> *Unidades (para todo)*
>
> 1. El radar se guarda y se opera en **γ⁰ LINEAL** (potencia). El dB = 10·log10(lineal)
>    es sólo para ver y para umbralizar. **Todo promedio, remuestreo o diferencia se
>    calcula en lineal**; las medias se informan en dB **después** de promediar en
>    lineal (`media_lineal_db()`). Ceros y negativos pasan a sin dato, nunca a −∞
>    (`lin_a_db()`).
> 2. Si un producto no admite γ⁰ (NovaSAR fuera de SNAP), queda en σ⁰ y **lo dice en el
>    nombre de la banda** (`S_NovaSAR_sigma0_HH`) y en la columna `unidad`.
>
> *Grafos de SNAP (`09_Grafos_SNAP`)*
>
> 3. Sentinel-1 GRD (`Tp2_S1_GRD_a_gamma0.xml`): `Read → Apply-Orbit-File` (Sentinel
>    Precise, descarga automática, polinomio de grado 3, que siga si falla) →
>    `ThermalNoiseRemoval` (quitar el ruido, no reintroducirlo) → `Calibration` a
>    **β⁰** (`outputBetaBand=true`, sin σ⁰ ni γ⁰, polarizaciones VV y VH, sin dB, sin
>    complejo) → `Subset` (región geográfica del sitio con margen, copiando metadatos)
>    → `Terrain-Flattening` (Copernicus 30m Global DEM, bilineal, superposición
>    adicional 0,1, sobremuestreo 1,0) → `Terrain-Correction` → `Write`.
> 4. Sentinel-1 SLC (`Tp2_S1_SLC_a_gamma0.xml`): igual, con `ThermalNoiseRemoval`
>    recortando negativos, `Calibration` a β⁰ **antes** de `TOPSAR-Deburst`, `Subset`
>    después del deburst y `Multilook` (2 vistas en rango, 1 en acimut, píxel
>    cuadrado en el terreno, salida en intensidad) antes del `Terrain-Flattening`.
> 5. SAOCOM-1 L1A (`Tp2_SAOCOM_StripMap_a_gamma0.xml`): `Read → Calibration` a β⁰
>    **sin fijar polarizaciones** (que procese las que traiga: cuatro en QP, dos en DP)
>    → `Subset` → `Multilook` (2 × 2, píxel cuadrado, intensidad) →
>    `Terrain-Flattening` → `Terrain-Correction` → `Write`. Advertí que dos productos
>    de distinta pasada (ascendente y descendente) se procesan con el mismo grafo pero
>    **no se apilan ni se promedian**: la geometría de mirada es opuesta.
> 6. `Terrain-Correction`, en los tres: Copernicus 30m Global DEM, remuestreo bilineal
>    de la imagen y del DEM, **10 m**, **EPSG:32721**, `alignToStandardGrid=true` con
>    **origen 5, 5** (SNAP alinea los centros de píxel al origen: con 5, 5 los centros
>    caen en 5, 15, 25… y los bordes en 0, 10, 20…, igual que la grilla del curso),
>    sin normalización radiométrica adicional (ya la hizo el Terrain Flattening),
>    guardando la banda de origen y el **ángulo de incidencia local** (diagnóstico, no
>    corrección) y, en los tres grafos, la **máscara de inversión por relieve y sombra**.
> 7. `Write` en **BEAM-DIMAP**, que conserva todos los metadatos originales. Nunca
>    GeoTIFF como producto de SNAP.
> 8. **Sin filtro de speckle en los grafos.** El filtro se aplica después, en la
>    interfaz, como paso aparte (`Radar > Speckle Filtering > Single Product Speckle
>    Filter`, Refined Lee o Lee Sigma), para ver su efecto solo.
> 9. Comentarios dentro del XML que expliquen cada decisión (por qué β⁰, por qué el
>    origen 5, 5, por qué BEAM-DIMAP).
>
> *Paso 1 — `Tp2_01_pila_multibanda.py`*
>
> 10. Argumentos: `--sitio` (obligatorio), `--fecha_c` (AAAA-MM-DD del Sentinel-1 RTC),
>     `--novasar` (número de escena),
>     `--extra "banda=ruta.tif|sensor|lambda_cm|AAAA-MM-DD"` (repetible; sensor,
>     longitud de onda y fecha opcionales, con aviso en la bitácora si falta la
>     fecha), `--desplazamiento DX DY` (metros, sólo NovaSAR; DX positivo = este,
>     DY positivo = norte; 0 0 por defecto) y `--min_validos` (20 % por defecto).
> 11. C: el primer ítem `sentinel-1-rtc` de ese día sobre el sitio; VV y VH con
>     `s1_rtc()`, valores ≤ 0 o no finitos a sin dato, agregados con `average`.
>     Nombres `C_S1_gamma0_VV`, `C_S1_gamma0_VH`.
> 12. NISAR: todos los `.h5` de `BANDA_L_NASA` (grupo `LSAR`) y `BANDA_S_ISRO` (grupo
>     `SSAR`), salvo los que tengan `COMPAT` en el nombre. Términos `HHHH` y `HVHV`,
>     **sólo frecuencia A**. Leé del `.h5` **sólo la ventana del sitio** (más un margen
>     de 3 píxeles), aplicá la **máscara del producto** (0 y 255 a sin dato) y
>     proyectá a la grilla: `average` si el píxel de origen es más fino que 10 m,
>     bilineal si es igual o más grueso. Si el granulo no cubre el sitio, se saltea.
>     Nombres `L_NISAR_gamma0_HH_AAAAMMDD`, `S_NISAR_gamma0_HV_AAAAMMDD`, etc.
> 13. NovaSAR: `novasar_sigma0()`: proyección por los puntos de enlace del
>     `image_HH.tif`, remuestreo **rms** de los DN (para promediar potencia) y después
>     σ⁰ = DN² / k, con k leído de `<CalibrationConstant>` del `metadata.xml`. Sin
>     constante, error explícito: no se calibra «a ojo». Aplicá el desplazamiento de
>     `--desplazamiento` (el que mide `Tp3_02`) y escribilo en la bitácora; sin él,
>     avisá que NovaSAR entra sin corregir.
> 14. Extras de SNAP: leer la primera banda del GeoTIFF y llevarla a la grilla
>     promediando en lineal. Si el nombre termina en `_db`, pasarlo a lineal **en su
>     grilla original** y recién después promediarlo a la grilla común, avisarlo y
>     quitar el sufijo. Sensor, longitud de onda y fecha de `--extra` van a la tabla
>     de bandas.
> 15. Una banda entra sólo si tiene dato en al menos `--min_validos` % del sitio; si no,
>     la bitácora dice `-> NO entra` y por qué.
> 16. Salida: `02_Subsets_SNAP_QGIS/<SITIO>_pila_gamma0_lineal.tif` (GeoTIFF float32,
>     una banda por capa con su **nombre como descripción de banda**, sin dato −9999,
>     compresión deflate con predictor 3, en teselas de 256 × 256, BigTIFF si hace
>     falta) con las etiquetas `FUENTE` (la cita de cada dato: organismo, sensor,
>     producto, fecha y URL del proveedor), `PROCESO`, `SCRIPT`, `FECHA_PROCESO` y
>     `UNIDADES`; y `<SITIO>_pila_bandas.csv` con `banda, sensor, lambda_cm, fecha,
>     unidad, pixeles_validos_%, media_dB, fuente`.
>
> *Paso 2 — `Tp2_02_rgb_copol_cruzada_cociente.py`*
>
> 17. Para cada par copol/cros de la pila (VV con VH, HH con HV, buscando la gemela por
>     el nombre): **R = copol en dB, G = cros en dB, B = cociente copol/cros en dB**
>     (copol_dB − cros_dB). Siempre en ese orden.
> 18. Estiramiento 2–98 % por canal sobre el sitio; valores 1 a 255; **0 reservado
>     para sin dato**. Imprimir los límites en dB de cada canal.
> 19. Salidas: `05_Resultados/02_Rasters/<SITIO>_RGB_<etiqueta>.tif` (8 bits, 3 bandas,
>     interpretación de color rojo-verde-azul) y `05_Resultados/05_Graficos/<SITIO>_RGB_<etiqueta>.png`
>     con título `RGB = VV - VH - VV/VH (dB)` y la línea **«Fuente: …»** al pie. Las
>     bandas de una sola polarización, en gris (`<SITIO>_gris_<banda>.png`).
> 20. Escribir en el docstring cómo se interpreta el RGB (verde o amarillo: volumen; magenta o
>     blanco: doble rebote; azul o violeta: cociente alto; negro: especular) y que el
>     RGB **no se usa para medir**.
>
> *Paso 3 — `Tp2_03_respuesta_por_cubierta.py`*
>
> 21. Entrada: `04_Tablas_de_trabajo/cubiertas_<SITIO>.gpkg`, capa `cubiertas`, campo
>     de texto `clase`. Si no existe, **crearla vacía** con tipo de geometría
>     **Polygon** declarado (campos `clase` y
>     `observacion`, EPSG:32721), listar las clases sugeridas (`agua_calma,
>     agua_rizada, pajonal, monte_o_bosque, cultivo, suelo_desnudo, urbano, estable`) y
>     **detenerse**: la digitalización es del grupo, no del programa.
> 22. Rasterizar los polígonos en la grilla de la pila. Por clase y banda:
>     `n_pixeles`, `media_dB` (promediada en lineal), `p10_dB`, `p90_dB`. Avisar si una
>     clase tiene menos de **200 píxeles** en una banda.
> 23. Contraste: para cada par de clases y cada banda, diferencia de medias en dB.
> 24. Figura de cajas, un panel por banda, sin valores extremos, con la línea de fuente
>     al pie.
> 25. Salidas: `05_Resultados/04_Tablas/<SITIO>_respuesta_por_cubierta.csv`,
>     `<SITIO>_contraste_entre_clases.csv`, `05_Graficos/<SITIO>_cajas_por_banda.png`.
>
> *Paso 4 — `Tp2_04_control_zona_estable.py`*
>
> 26. Polígonos de la clase `--clase` (por defecto `estable`) de
>     `cubiertas_<SITIO>.gpkg`. Pares: los que se pidan con `--a` y `--b`, o todos los
>     de la pila cuyo nombre sólo difiere en la fecha final `_AAAAMMDD` (mismo sensor,
>     misma polarización, distinta fecha).
> 27. Sólo píxeles con dato en las dos bandas; mínimo **50 píxeles**, si no, no se
>     evalúa y se dice.
> 28. Diferencia de **medias calculadas en lineal** y expresadas en dB, y desvío
>     estándar de la diferencia pixel a pixel en dB. Veredicto: **CUMPLE si |dif| <
>     1 dB**; si no, `NO CUMPLE: revisar calibracion, normalizacion u orbita`.
> 29. Salida: `05_Resultados/04_Tablas/<SITIO>_control_zona_estable.csv`.
>
> *Generales*
>
> 30. Todo se importa de `00_COMUN` (configuración y funciones); nada se redefine.
> 31. Bitácora por script en `05_Resultados/06_Control_calidad/Tp2_0N_<SITIO>.log`, que
>     imprima y guarde lo mismo y cierre con `SIGUIENTE PASO:`.
> 32. CSV en `utf-8-sig`.
>
> **Sinergia y fusión en este pedido.** El Tp2 no fusiona. La pila es la condición
> previa de una fusión de píxel; el RGB combina polarizaciones de un solo sensor y sólo
> sirve para ver; la respuesta por cubierta es **sinergia**: cada banda da su resultado
> y el analista los interpreta juntos, validando por coherencia física.
>
> **Formato de cada script.** Docstring con nombre, marca `[SE CORRE]`, número de
> paso, qué hace y por qué, entradas, salidas con ruta y ejemplos de uso. Cada script
> imprime qué leyó, cuántos píxeles con dato tiene cada banda, qué quedó afuera y por
> qué, dónde guardó y el siguiente paso.
>
> **Lo que NO debe hacer.**
> - No promedies, remuestrees ni filtres en dB.
> - No uses bilineal para agregar un píxel fino a uno grueso.
> - No mezcles σ⁰ y γ⁰ sin declararlo en el nombre.
> - No uses NISAR sin su máscara ni la frecuencia B.
> - No guardes el producto de SNAP en GeoTIFF ni conviertas a dB dentro del grafo.
> - No filtres el speckle dentro del grafo.
> - No midas sobre el RGB de 8 bits.
> - No inventes la clase de un polígono: si la capa está vacía, se detiene.
> - No copies los NISAR (varios GB cada uno) dentro del práctico: se leen de `00_COMUN\08_Originales_crudos\NISAR_DELTA`.

---

## La diferencia

El primero pedía **pasar todo a dB y apilar**. Éste pide **igualar todo lo que no es
la cubierta** (unidad, normalización, grilla, máscara) y recién entonces comparar, con
contrastes y con un control que demuestre que la calibración no inventa diferencias.
