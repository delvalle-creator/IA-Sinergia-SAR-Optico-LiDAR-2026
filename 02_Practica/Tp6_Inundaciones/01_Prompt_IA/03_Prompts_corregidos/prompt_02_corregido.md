# Prompt corregido — el que produjo los scripts del Tp6

---

> **Contexto.**
> Curso de posgrado «Sinergias multisensor y estrategias de fusión SAR-Óptico-LiDAR
> para evaluación de emergencias ambientales», Diamante (Entre Ríos), 2026.
> Python 3.11 en el entorno de Miniforge `sar` (conda-forge: numpy, scipy, pandas,
> matplotlib, gdal, rasterio, geopandas, pyogrio, pyproj, scikit-image,
> pystac-client, planetary-computer). Windows; los scripts se corren desde el
> Miniforge Prompt en `02_Practica\Tp6_Inundaciones\03_Scripts`.
>
> **Configuración y funciones comunes** en `02_Practica\00_COMUN`:
> `configuracion_comun.py` (SITIOS, EVENTOS, EPSG, `ruta_tp()`);
> `funciones_comunes.py` (`grilla_sitio`, `grilla_de_tif`, `buscar_stac`,
> `fecha_item`, `s1_rtc`, `s2_reflectancia`, `s2_mascara_valida`, `jrc_ocurrencia`,
> `copdem`, `leer_en_grilla`, `lin_a_db`, `leer_tif`, `guardar_tif`, `Bitacora`,
> `fuente_mpc`); `funciones_cambio.py` (`umbral_documentado`, `aplicar_umbral`,
> `indice_normalizado`, `cociente_db`, `tabla_de_coincidencias`, `fusion_decision`);
> `funciones_lidar.py` (`alturas_a_egm2008`). Se importan; no se reescriben.
>
> **Sitio.** `B_CONCORDIA`: Concordia – Salto Grande, río Uruguay, bbox
> (−58,25, −31,50, −57,85, −31,10) en WGS84 (ventana de la presentación 02).
>
> **Grilla.** EPSG:32721 (UTM 21S), bordes múltiplos del píxel, **20 m** por defecto
> (la serie es larga y el volumen importa). Sin dato: −9999 en disco, NaN en memoria.
>
> **Eventos y fechas.** Crecidas del río Uruguay de noviembre de 2023 y mayo de
> 2024. Serie: 01/10/2023 a 30/06/2024. Pico: 04/11/2023, con Sentinel-1A y
> Sentinel-2B del mismo día (verificado). Referencia de la crecida de mayo de 2024:
> Carta Internacional, activación 880.
>
> **Datos.**
> - Sentinel-1 IW RTC (`sentinel-1-rtc`, Planetary Computer, sin cuenta): γ⁰ VV
>   lineal, ya corregido por el terreno.
> - Sentinel-2 L2A (`sentinel-2-l2a`): B03 y B11, con la máscara SCL.
> - JRC Global Surface Water (`jrc-gsw`, activo `occurrence`, 0–100 %).
> - Copernicus DEM GLO-30 (`cop-dem-glo-30`), alturas sobre el geoide EGM2008.
> - ICESat-2 ATL08 v007, segmentos del sitio ya leídos por `Tp1_05_buscar_lidar.py`
>   en `Tp1_Convergencia\05_Resultados\03_Vectores\lidar_B_CONCORDIA.gpkg`, capa
>   `atl08`, con `h_te_best_fit_elips`, `terreno_valido` (relleno 3,4·10³⁸ y
>   `segment_watermask` ya filtrados) y `fuerza_haz` (según `sc_orient`).
> - Cobertura de control del Tp4:
>   `Tp4_Validacion\02_Subsets_SNAP_QGIS\B_CONCORDIA_cobertura_control_<pixel>m.tif`.
> - **Banda L:** hay dos SAOCOM-1B TNA de la misma órbita (10/10/2023, seco, y
>   11/11/2023, crecida) en `02_Subsets_SNAP_QGIS\SAOCOM_gamma0` y un ALOS-2 ScanSAR
>   del 16/11/2023 en `02_Subsets_SNAP_QGIS\ALOS2_gamma0` (sin escena seca del mismo
>   sensor). El código debe aceptar la L como entrada opcional (HH de evento y de
>   referencia seca, en lineal) y no aplicar la regla R2 sin probarla: medir antes el
>   cambio general entre las dos fechas.
> - NovaSAR-1 HH del 13/09/2023 (escena 47942): previa a la crecida, cubre el 39 %
>   del sitio. Sirve para interpretar; no entra a la comparación del evento.
>
> **La pregunta:** ¿qué área cubrió el agua, cuánto tiempo y a qué profundidad?
>
> **Requisitos no negociables (para los cinco scripts).**
>
> 1. **Radar en γ⁰ lineal**; dB (`lin_a_db`) sólo para el umbral y los histogramas.
>    El aumento de HH en banda L es `10·log₁₀(evento/referencia)` con `cociente_db`.
> 2. **Una sola órbita relativa** de Sentinel-1 en toda la serie: la más frecuente
>    en la ventana, o la que se fije con `--orbita`. Informar las otras órbitas que
>    se descartaron.
> 3. **Umbral de agua en VV:** Otsu sobre VV en dB del día del pico, **fuera del
>    agua permanente**, o manual con `--umbral_vv`; con su histograma guardado. Se
>    calcula **una vez** y se aplica a todas las fechas. Agua si VV < umbral.
> 4. **Agua permanente:** JRC con ocurrencia ≥ 90 %. Se excluye de la inundación en
>    todos los mapas, de todos los sensores (regla R4).
> 5. **Nubes:** el óptico sólo con SCL 4, 5, 6, 7 u 11; con nube, NaN (no vota).
>    Nubosidad informada dentro del sitio. Si el sitio cae en varias teselas del
>    mismo día, se rellenan.
> 6. **MNDWI = (B03 − B11)/(B03 + B11)**, agua si > `--u_mndwi` (0 por defecto),
>    con su histograma.
> 7. **Doble rebote en L:** aumento de HH ≥ `--u_doble_rebote` (3 dB por defecto)
>    respecto de la referencia seca = agua bajo vegetación.
> 8. **Duración:** cada fecha con agua cuenta los días hasta la fecha siguiente de
>    la serie; la última, la mitad de la revisita mediana. Extensión máxima = agua
>    en alguna fecha.
> 9. **Profundidad (FwDET, Cohen et al., 2018 y 2019):** borde = píxeles inundados con algún
>    vecino seco (vecindad 3 × 3); cota del borde en el Copernicus DEM; suavizado
>    de la cota de borde con un promedio móvil en una ventana de `--suavizado` píxeles (7) que considera
>    sólo píxeles de borde; cada píxel inundado toma la cota del borde más cercano
>    (transformada de distancia); profundidad = cota − MDE; negativos a 0 y
>    contados.
> 10. **Control del MDE:** ATL08 `h_te_best_fit` elipsoidal → EGM2008 con PROJ
>     (`EPSG:4979` → `EPSG:4326+3855`). Si PROJ no tiene la grilla
>     `us_nga_egm08_25.tif`, **detenerse con un mensaje que diga cómo bajarla**
>     (`projsync --file us_nga_egm08_25`), nunca comparar sin convertir (en Entre
>     Ríos el error sería de unos 15 m). Comparar en el píxel de la grilla donde
>     cae cada segmento: sesgo (MDE − ICESat-2), desvío, RMSE y mediana, para todos y
>     por clase de control (grupos con al menos 5 segmentos). Opción `--solo_fuertes`.
> 11. **Cita de fuente** en los metadatos de cada GeoTIFF: organismo, sensor,
>     órbita relativa, número de escenas, fechas, URL del Planetary Computer, y JRC
>     (Pekel et al., 2016) para el agua permanente; Copernicus DEM para la profundidad.
>     El gráfico de la serie lleva la cita «Fuente» al pie.
> 12. **Bitácora** en `Tp6_Inundaciones\05_Resultados\06_Control_calidad\` con todo
>     lo impreso y el siguiente paso.
> 13. Rutas con `ruta_tp()`. CSV en `utf-8-sig`. Sin credenciales.
>
> **`Tp6_01_serie_agua_C.py`.** Argumentos `--pixel` (20), `--desde` (2023-10-01),
> `--hasta` (2024-06-30), `--pico` (2023-11-04), `--umbral_vv`, `--orbita`. Si no hay
> escena de la órbita en la fecha del pico, terminar listando las fechas posibles.
> Por fecha: hectáreas de agua temporal y % del sitio con dato. Dos cuadros consecutivos de
> la misma pasada (misma fecha) se unen en una sola capa y una sola fila (los `id` unidos
> con ` + `), y la bitácora lo dice. Salidas:
> `02_Subsets_SNAP_QGIS\B_agua_C_por_fecha_<pixel>m.tif` (una banda `agua_AAAAMMDD`
> por fecha), `05_Resultados\02_Rasters\B_extension_y_duracion_C_<pixel>m.tif`
> (`extension_maxima`, `duracion_dias`), `05_Resultados\04_Tablas\B_serie_agua_C.csv`,
> `05_Resultados\05_Graficos\B_serie_agua_C.png` y `B_histograma_VV_pico.png`.
> Imprimir la extensión máxima y las hectáreas con más de 30 días de agua. Docstring:
> lo que VV no ve (agua bajo vegetación; embalse rizado por el viento, excluido por JRC).
>
> **`Tp6_02_sinergia_agua.py` — SINERGIA.** Argumentos `--pixel` (20), `--fecha`
> (2023-11-04), `--u_mndwi` (0.0), `--l_evento`, `--l_referencia`,
> `--u_doble_rebote` (3.0). Lee la capa de agua C de esa fecha (si no está, terminar
> listando las fechas); calcula MNDWI y, si se dan los dos GeoTIFF, el doble rebote en
> L. Si no hay óptico o no se da la L, decirlo («sin banda L: el agua bajo vegetación
> no se evalúa»). Con menos de dos sensores, terminar. Tabla de
> coincidencias **sin fusionar**. Salidas: `05_Resultados\02_Rasters\B_agua_por_sensor_<pixel>m.tif`
> (`C_Sentinel1_VV`, `Optico_MNDWI`, `L_HH_doble_rebote`), `05_Resultados\04_Tablas\B_sinergia_agua.csv`,
> `05_Resultados\05_Graficos\B_histograma_MNDWI.png`. Docstring: qué se aprende de la
> tabla (C y óptico coinciden en agua abierta despejada; L agrega agua bajo vegetación;
> la nube no vota), y que NovaSAR (13/09/2023, previa a la crecida) no se lee en el
> programa: no puede votar sobre el agua del 04/11/2023; se mira en QGIS y se declara.
>
> **`Tp6_03_fusion_y_variantes.py` — FUSIÓN DE DECISIÓN.** Argumento `--pixel` (20).
> Reglas escritas en el docstring: R1 C dice agua; R2 o L dice doble rebote (si hay);
> R3 o el óptico dice agua sin nube; R4 nunca en agua permanente. Variantes con
> códigos 1 = agua de inundación, 2 = no: `B_variante_optico.tif`, `B_variante_C.tif`,
> `B_variante_CL.tif` (C ∪ L, si hay L) y `B_variante_multisensor.tif` (unión de todos,
> con la banda `sensores_que_votaron`). Imprimir las hectáreas de cada una y el % sin
> dato por nubes de la óptica. Advertir que la unión maximiza la detección y la comisión.
> Justificar en el docstring por qué decisión y no píxel.
>
> **`Tp6_04_profundidad.py`.** Argumentos `--pixel` (20), `--variante` (multisensor),
> `--suavizado` (7). Lee `B_variante_<variante>.tif`. Imprime píxeles inundados,
> cuántos dieron profundidad negativa, y la mediana, el percentil 90 y el máximo.
> Advertencias escritas: el Copernicus DEM es un modelo de superficie de radar banda X
> de 2011–2015 (en el monte mide la copa; en el agua, el espejo de ese día); la
> profundidad es plausible, no medida. Salida:
> `05_Resultados\02_Rasters\B_profundidad_<variante>_<pixel>m.tif` (`profundidad_m`, `cota_agua_m`).
>
> **`Tp6_05_control_mde_icesat2.py`.** Argumentos `--pixel` (20), `--solo_fuertes`.
> Salida `05_Resultados\04_Tablas\B_control_mde_icesat2.csv`. Cierra con: «si el sesgo
> en suelo desnudo o pastura supera 1 m, la profundidad del paso 4 hereda ese error».
>
> **Sinergia y fusión, explícitas.** El paso 2 es **sinergia**: cada sensor con su
> resultado; se valida por coherencia física. El paso 3 es **fusión de decisión**; se
> valida con la exactitud del producto (Tp4). El paso 1 es un solo sensor. Los pasos 4 y
> 5 son un producto derivado y su control. Cada docstring lo dice.
>
> **Formato de cada script.** Docstring en español: pregunta, qué hace y por qué,
> salidas con ruta, uso con argumentos reales, marca `[SE CORRE]`. Imprime qué leyó,
> qué decidió, cuánto quedó en cada clase y el siguiente paso.
>
> **Lo que NO debe hacer:**
>
> - No contar el río ni el embalse como inundación.
> - No usar un umbral distinto por fecha, ni un umbral fijo sin histograma.
> - No mezclar órbitas en la serie.
> - No dejar votar al óptico donde hay nube.
> - No presentar el mapa de VV como «toda el agua»: declarar el agua bajo vegetación.
> - No aplicar la regla R2 de banda L sin probarla con el par de fechas disponible.
> - No usar una cota única de agua para todo el sitio.
> - No comparar ICESat-2 con el MDE sin pasar al mismo dato vertical.
> - No presentar la profundidad como medida.
> - No escribir credenciales.

---

## La diferencia

El primero pedía **una superficie y una profundidad**. Éste pide primero **sacar el
agua que siempre está**, fijar una definición de agua que no cambie en la serie, decir
qué agua no ve cada sensor (y que la banda L disponible no permite separar el agua bajo vegetación), escribir las
reglas de la fusión, y controlar el modelo de elevación en la misma referencia vertical
antes de dar una profundidad, que además se declara plausible y no medida.
