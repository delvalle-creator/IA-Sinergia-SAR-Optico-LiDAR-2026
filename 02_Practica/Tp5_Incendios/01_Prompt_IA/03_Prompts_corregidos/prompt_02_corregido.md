# Prompt corregido — el que produjo los scripts del Tp5

---

> **Contexto.**
> Curso de posgrado «Sinergias multisensor y estrategias de fusión SAR-Óptico-LiDAR
> para evaluación de emergencias ambientales», Diamante (Entre Ríos), 2026.
> Python 3.11 en el entorno de Miniforge `sar` (conda-forge: numpy, scipy, pandas,
> matplotlib, gdal, rasterio, geopandas, pyogrio, pyproj, h5py, scikit-learn,
> scikit-image, pystac-client, planetary-computer). Windows; los scripts se corren
> desde el Miniforge Prompt en `02_Practica\Tp5_Incendios\03_Scripts`.
>
> **Configuración y funciones comunes.** Todo sale de `02_Practica\00_COMUN`:
> `configuracion_comun.py` (SITIOS, EVENTOS, EPSG, `ruta_tp()`),
> `funciones_comunes.py` (`grilla_sitio`, `buscar_stac`, `fecha_item`, `s1_rtc`,
> `alos2_mosaico`, `s2_reflectancia`, `s2_mascara_valida`, `leer_en_grilla`,
> `guardar_tif`, `leer_tif`, `grilla_de_tif`, `Bitacora`, `fuente_mpc`),
> `funciones_cambio.py` (`cociente_db`, `nbr`, `rdnbr`, `umbral_documentado`,
> `aplicar_umbral`, `tabla_de_coincidencias`, `fusion_decision`,
> `fusion_pixel_o_rasgo`, `leer_entrenamiento`, `figura_mapa`). Los scripts las
> importan; no las reescriben. Cada script sube por el árbol hasta `00_COMUN` y lo
> agrega a `sys.path`.
>
> **Sitio.** `A1_DELTA_QUEMAS`: islas del Delta del Paraná frente a Victoria y
> Gualeguay, bbox (−59,96, −33,36, −59,72, −33,07) en WGS84, recorte de las
> escenas SAOCOM del curso 2023. Quemas de 2020: desde febrero, con el pico en julio;
> el práctico mide lo quemado entre mediados de julio y octubre (declararlo).
>
> **Grilla.** EPSG:32721 (UTM 21S), bordes alineados a múltiplos del píxel. Píxel de
> **20 m** por defecto: el mosaico ALOS-2 es de 25 m, y bajar a 10 m inventaría
> detalle en banda L. Sin dato: −9999 en los GeoTIFF; NaN en memoria.
>
> **Sensores y fechas (reales).**
> - Sentinel-1 IW RTC del Microsoft Planetary Computer (`sentinel-1-rtc`), γ⁰
>   lineal VV y VH, ya corregido por el terreno. Pre 16/07/2020, post 26/09/2020
>   (las fechas de los SLC del archivo del curso, que van del 10/07 al 26/09/2020).
> - ALOS-2 PALSAR-2, mosaicos anuales de JAXA (`alos-palsar-mosaic`), HH y HV, 25 m;
>   2019 = antes, 2020 = después. γ⁰ = DN² · 10^(−8,3) (equivale a
>   10·log₁₀(DN²) − 83 dB), con el cuadrado calculado **antes** de remuestrear.
> - SAOCOM-1A StripMap QP del 21/07/2020 y del 25/10/2020 (CONAE, archivo del curso
>   SAR CEREGEO 2023), llevados a γ⁰ con `00_COMUN\procesar_saocom.py` (SNAP: Calibration a σ⁰,
>   Multilook, Refined Lee, Terrain-Correction; γ⁰ = σ⁰/cos θ sobre el elipsoide, SIN
>   Terrain-Flattening) y exportados a GeoTIFF, banda HV en lineal. Opcional.
> - Sentinel-2 L2A (`sentinel-2-l2a`): después 13/10/2020; antes, la fecha que el
>   grupo elige con `Tp1_03` (por defecto 15/07/2020). Reflectancia = (DN − desplazamiento)/10 000,
>   con el desplazamiento de +1000 sólo para la línea de base ≥ 04.00 (lo resuelve
>   `s2_reflectancia`).
> - GEDI L2A V003, huellas del sitio ya filtradas por `Tp1_05_buscar_lidar.py`
>   (`l2a_quality_flag_rel3` = 1, `degrade_flag` = 0, `sensitivity` ≥ 0,95,
>   `surface_flag` = 1), en `Tp1_Convergencia\05_Resultados\03_Vectores\lidar_A1_DELTA_QUEMAS.gpkg`,
>   capa `gedi_l2a`, columna booleana `valido`.
> - Cobertura de control del Tp4: `Tp4_Validacion\02_Subsets_SNAP_QGIS\A1_DELTA_QUEMAS_cobertura_control_<pixel>m.tif`,
>   banda 1, clases 1 agua_permanente, 2 humedal_pajonal, 3 monte_nativo,
>   4 plantacion_forestal, 5 cultivo_pastura, 6 suelo_desnudo, 7 urbano, 8 otra. En
>   A1_DELTA_QUEMAS sólo tiene la clase 1: para pajonal y albardón se usa el CCI Biomass 2020
>   (`A1_DELTA_QUEMAS_CCI_Biomass_v7_AGB`, banda AGB_2020; pajonal < 15 Mg/ha, albardón ≥ 30 Mg/ha).
>
> **La pregunta:** ¿dónde se quemó y con qué severidad, aun bajo humo? Y la de la
> sinergia: ¿la banda C y la banda L responden en el pajonal y en el albardón como
> predice la física de la dispersión? Si no, ¿por qué?
>
> **Requisitos no negociables (para los cuatro scripts).**
>
> 1. **Radar en γ⁰ LINEAL.** Toda lectura, remuestreo y promedio en lineal. El
>    cambio es `10·log₁₀(post/pre)` (`cociente_db`), con NaN donde algún lado es
>    ≤ 0 o falta. dB sólo para el indicador final, los histogramas y la vista.
> 2. **Remuestreo:** promedio (`average`) para radar en lineal y reflectancias;
>    vecino más próximo para clases y máscaras.
> 3. **Una sola órbita** de Sentinel-1 para pre y post; anotar la órbita relativa
>    en la cita de fuente.
> 4. **Nubes:** en Sentinel-2, sólo píxeles con SCL 4, 5, 6, 7 u 11; los demás quedan
>    NaN. La nubosidad se informa **dentro del sitio**, no la de la tesela. Si el
>    sitio cae en varias teselas del mismo día, se rellena con las otras.
> 5. **Agua permanente:** la clase 1 de la cobertura de control nunca es quema en
>    ningún mapa por sensor. Si no existe la cobertura, decirlo en la bitácora.
> 6. **Umbrales documentados:** Otsu por defecto o manual por argumento; en ambos
>    casos guardar el histograma con la línea del umbral y escribir en la bitácora
>    el valor, el método y el porcentaje de píxeles que deja en la clase. Signo:
>    quema si Δradar < umbral; si dNBR > umbral.
> 7. **dNBR 0,27** (Key y Benson) sólo como referencia: está definido para bosques
>    templados y en humedales se calibra. Escribirlo en el docstring.
> 8. **Cita de fuente** en los metadatos de cada GeoTIFF (`guardar_tif`):
>    organismo, sensor, producto, fecha, hora UTC, órbita y URL del Planetary
>    Computer (`fuente_mpc`), o CONAE y el archivo del curso para SAOCOM. Además,
>    una tabla CSV de fuentes por capa.
> 9. **Bitácora** (`Bitacora`) en `Tp5_Incendios\05_Resultados\06_Control_calidad\`:
>    todo lo que se imprime queda en un `.log` con fecha y versión de Python. Al
>    final, la orden exacta del siguiente paso.
> 10. **Declarar** en la bitácora: el píxel de 20 m frente a los 25 m de ALOS-2;
>     que el mosaico anual combina pasadas de varios meses (la fecha de cada
>     píxel está en su banda `date`); que la exactitud fuera de bolsa del Random
>     Forest es optimista; que rh98 por debajo de 2 a 3 m está en el ruido.
> 11. Rutas siempre con `ruta_tp()`. CSV en `utf-8-sig`. Sin credenciales.
>
> **`Tp5_01_indicadores.py` — un indicador por sensor, sin combinar.**
>
> - Argumentos: `--pixel` (20), `--c_pre` (2020-07-16), `--c_post` (2020-09-26),
>   `--opt_pre` (vacío), `--opt_post` (2020-10-13), `--alos2_pre` (2019),
>   `--alos2_post` (2020), `--saocom_pre_hv`, `--saocom_post_hv` (vacíos).
> - Capas: `dVH_C_dB`, `dVV_C_dB`; `dHV_L_ALOS2_dB`, `dHH_L_ALOS2_dB` (si hay
>   mosaicos de los dos años; si el sitio cae en varias teselas, se rellenan);
>   `dHV_SAOCOM_dB` (si se pasan los dos GeoTIFF; se leen con promedio);
>   `NBR_pre`, `NBR_post`, `dNBR`, `RdNBR` (si hay `--opt_pre`). RdNBR =
>   dNBR / √|NBR_pre| (Miller y Thode), NaN si √|NBR_pre| ≤ 0,001.
> - Si falta una fecha en el catálogo, decirlo y seguir con los demás sensores.
> - Imprimir la mediana de cada indicador y el % de píxeles con dNBR > 0,27.
> - Salidas: `Tp5_Incendios\02_Subsets_SNAP_QGIS\A1_DELTA_QUEMAS_indicadores_<pixel>m.tif`
>   (una banda con nombre por indicador) y `...\A1_DELTA_QUEMAS_indicadores_fuentes.csv`.
> - Siguiente paso: `python Tp5_02_sinergia.py --pixel <pixel>`.
>
> **`Tp5_02_sinergia.py` — SINERGIA: un mapa por sensor y la tabla de acuerdo.**
>
> - Argumentos: `--pixel` (20) y umbrales manuales opcionales `--u_dvh`, `--u_dhv`,
>   `--u_dhv_saocom`, `--u_dnbr`.
> - Sensores: `C_Sentinel1_dVH` (de `dVH_C_dB`, signo <), `L_ALOS2_dHV`
>   (`dHV_L_ALOS2_dB`, <), `L_SAOCOM_dHV` (`dHV_SAOCOM_dB`, <), `Optico_dNBR`
>   (`dNBR`, >). Sólo los que existan en el GeoTIFF de indicadores.
> - Cada sensor: umbral documentado, mapa binario 1/0/NaN, agua permanente → 0.
> - **No producir un mapa único.** Producir la tabla de coincidencias por par de
>   sensores (`tabla_de_coincidencias`): `%_clase` de cada uno, `%_ambos`, `%_solo_1`,
>   `%_solo_2`, `acuerdo_%`, en todo el sitio **y por clase de control** (con los
>   nombres de clase).
> - Hacen falta al menos dos sensores; si no, decirlo y terminar.
> - Salidas: `Tp5_Incendios\05_Resultados\02_Rasters\A1_quema_por_sensor_<pixel>m.tif`
>   (una banda por sensor), `...\A1_sensores_que_coinciden_<pixel>m.tif` (cuántos
>   sensores marcan quema), `Tp5_Incendios\05_Resultados\04_Tablas\A1_sinergia_coincidencias.csv`,
>   `Tp5_Incendios\05_Resultados\05_Graficos\histograma_<indicador>.png` y
>   `A1_sensores_que_coinciden.png` con la cita «Fuente» al pie.
> - No imprimir una «lectura sugerida» que dé por cierto el resultado físico. Si la
>   cobertura de control sólo tiene la clase 1, escribir que no hay clases de pajonal y
>   monte y que se separe por estrato del CCI (guía, paso 2).
>
> **`Tp5_03_fusion.py` — FUSIÓN y las cuatro variantes para el Tp4.**
>
> - Argumentos: `--pixel` (20), `--regla` (`mayoria` | `union` | `interseccion`,
>   por defecto `mayoria`).
> - Códigos de las variantes para el Tp4: **1 = quemado, 2 = no quemado**, NaN sin dato.
> - V1 `A1_variante_optico.tif`: mapa `Optico_dNBR` del paso 2. Un sensor.
> - V2 `A1_variante_C.tif`: mapa `C_Sentinel1_dVH`. Un sensor.
> - V3 `A1_variante_CL.tif`: **fusión de decisión** (`fusion_decision`) de todos los
>   mapas de radar (`C_*` y `L_*`) con la regla escrita; banda `clase` y banda
>   `votos` (cuántos sensores votaron). Donde un sensor no tiene dato, decide el resto.
>   Justificar en el docstring por qué decisión: C y L difieren en píxel y en fecha.
> - V4 `A1_variante_multisensor.tif` y `A1_severidad_multisensor.tif`: **fusión de
>   rasgo** con Random Forest (`fusion_pixel_o_rasgo`) sobre `dVH_C_dB`, `dVV_C_dB`,
>   `dHV_L_ALOS2_dB`, `dHV_SAOCOM_dB`, `dNBR`, `RdNBR` (las que existan). 300
>   árboles, `class_weight="balanced"`, `min_samples_leaf=2`, semilla 2026, hasta
>   20 000 píxeles de entrenamiento repartidos por igual entre clases, sólo
>   píxeles con dato en todas las capas. Clases de severidad: 1 quemado alta,
>   2 quemado baja, 3 no quemado, 4 agua. La variante binaria colapsa 1 y 2 en
>   quemado y 3 y 4 en no quemado. Banda `probabilidad` de la clase ganadora.
>   Justificar en el docstring por qué rasgo: la severidad es graduada.
> - Entrenamiento: `Tp5_Incendios\04_Tablas_de_trabajo\entrenamiento_A1.gpkg`, capa
>   `entrenamiento`, campo entero `codigo`. Si no existe, crearlo vacío con tipo de
>   geometría **Polygon** declarado (EPSG:32721, campos `codigo` y `clase`), para que
>   QGIS habilite el dibujo directamente, producir V1 a V3, decir que V4 queda pendiente y
>   terminar. Si está vacío, lo mismo.
> - Docstring: el entrenamiento se digitaliza **antes** de `Tp4_02` y lejos de donde
>   se validará; validar con datos de entrenamiento infla la exactitud.
> - Imprimir los píxeles de entrenamiento, la exactitud fuera de bolsa con la
>   palabra OPTIMISTA, la importancia de cada variable ordenada, y las hectáreas
>   de cada clase de severidad.
> - Salidas en `05_Resultados\02_Rasters\`, la tabla `05_Resultados\04_Tablas\A1_importancia_variables.csv`
>   y la figura `05_Resultados\05_Graficos\A1_severidad_multisensor.png` con leyenda y fuente.
> - Siguiente paso: `Tp4_02` y `Tp4_03` para cada variante; después `Tp4_04 --tp Tp5`.
>
> **`Tp5_04_gedi_cambio_de_altura.py` — SINERGIA: evidencia estructural independiente.**
>
> - Argumentos: `--antes_desde` (2019-10-01), `--antes_hasta` (2020-04-01),
>   `--despues_desde` (2020-10-01), `--despues_hasta` (2021-03-31): la misma estación
>   antes y después, con fin; `--celda` (100 m), `--min_huellas` (2). Escribir las
>   ventanas en la bitácora.
> - Si falta `lidar_A1_DELTA_QUEMAS.gpkg` o `A1_variante_multisensor.tif`, salir con
>   un mensaje que diga qué paso correr antes. Escribir en la bitácora, al empezar,
>   el aviso del hueco de GEDI (17/03/2023 a 26/04/2024) y que para 2020 hay datos.
> - Sólo huellas `valido`. Período: antes, durante (se descarta), después.
> - GEDI no repite la huella: agrupar en celdas de `--celda` m en la proyección de la
>   variante multisensor, y en cada celda con al menos `--min_huellas` válidas antes
>   y después, Δrh98 = mediana(después) − mediana(antes), en metros.
> - Muestrear la variante multisensor en el centro de cada celda y resumir Δrh98
>   por clase del mapa (conteo, media, mediana, desvío).
> - Informar el % de celdas con rh98 previo < 3 m: ahí el rh98 es el piso del
>   instrumento sobre terreno llano, no la altura del pajonal. Informar cuántas celdas
>   de 3 m o más caen en lo quemado.
> - Si no hay celdas con datos antes y después, decirlo y sugerir ampliar la celda o
>   las fechas, declarándolo.
> - Salidas: `05_Resultados\04_Tablas\A1_delta_rh98_por_celda.csv` y `A1_delta_rh98_por_clase.csv`.
> - Docstring: es evidencia **independiente** porque no entró en ningún modelo;
>   GEDI no adquirió entre el 17/03/2023 y el 26/04/2024, pero para 2020 hay datos.
>
> **Sinergia y fusión, explícitas.** Los pasos 2 y 4 (GEDI) son **sinergia**: cada
> sensor da su resultado y el analista los interpreta juntos; se validan por
> coherencia física. V3 es **fusión de decisión** y V4 **fusión de rasgo**; se
> validan con la exactitud del producto (Tp4). V1 y V2 no son fusión. Cada
> docstring dice qué es cada paso.
>
> **Formato de cada script.** Docstring en español al principio, con: pregunta del
> práctico, qué calcula, fuentes y fechas, salidas con ruta, uso con argumentos
> reales y la marca `[SE CORRE]`. Imprime qué leyó, qué calculó, cuánto quedó en
> cada clase, y el siguiente paso.
>
> **Lo que NO debe hacer:**
>
> - No promediar, remuestrear ni restar en dB.
> - No llevar el mosaico ALOS-2 a un píxel menor que el de la grilla de trabajo sin
>   declararlo, ni mezclar órbitas de Sentinel-1.
> - No usar el dNBR (ni ningún indicador) como referencia de validación.
> - No informar la exactitud fuera de bolsa como exactitud del mapa.
> - No fusionar en el paso 2: allí cada sensor queda con su mapa.
> - No meter GEDI en el modelo: se usa para interpretar.
> - No clasificar el agua permanente como quema.
> - No inventar fechas: si una escena no está, se dice y se sigue sin ella.
> - No escribir credenciales.

---

## La diferencia

El primero pedía **un mapa combinado y su exactitud**. Éste pide primero **la
respuesta de cada sensor por separado**, con su física y su umbral, después dos
fusiones distintas justificadas por la diferencia de fecha y de resolución, y
recién al final una exactitud con una referencia que no salió de los datos. Y deja
dicho que puede pasar que la banda L no agregue nada en el pajonal: eso también
es un resultado.
