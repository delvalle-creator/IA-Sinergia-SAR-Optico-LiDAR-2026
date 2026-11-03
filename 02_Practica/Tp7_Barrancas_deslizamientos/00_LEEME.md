# Tp7 — Barrancas y deslizamientos: deformación y cicatriz

**Pregunta del práctico:** ¿hay deformación previa en la ladera, y con qué MDE se podría medir el volumen movilizado? (Los MDE disponibles son anteriores al evento: el volumen se calcula como ejercicio de método.)

**Sitio:** `E1_DIAMANTE_BARRANCA`, la barranca del río Paraná en Diamante
(WGS84: −60,71 / −32,135 / −60,575 / −32,015; ventana tomada del polígono `.kml`
de la escena COSMO-SkyMed Spotlight del 20/10/2018; la escena es un SLC, en geometría de radar, y sólo se usa su huella).

**Horario:** jueves, 9 a 13 h.

**Período de trabajo:** octubre de 2018. Es cuando se relevaron las grietas de la
barranca y cuando existe el par interferométrico en banda X (COSMO-SkyMed,
15/10 y 19/10/2018). Para comparar o fusionar bandas, todas tienen que mirar el
**mismo período**: por eso la búsqueda en banda C también empieza ahí.

## El recorrido, en orden

| Carpeta | Qué hay |
|---|---|
| `00_Guia_del_practico/` | **Empiece por acá.** Los objetivos y la guía paso a paso (Miniforge, SNAP y QGIS), con controles y errores típicos |
| `01_Prompt_IA/` | El prompt ingenuo y sus defectos, el análisis de lo que contestó la IA, el prompt corregido que produjo los scripts y el protocolo de verificación |
| `02_Subsets_SNAP_QGIS/` | Los productos que usted exporta de SNAP (desplazamiento y coherencia en banda X) y los MDE recortados. Ver su LEEME |
| `03_Scripts/` | Los scripts y el orden de ejecución |
| `04_Tablas_de_trabajo/` | Lo que digitaliza el grupo (cicatriz y depósito) y las zonas que escribe el paso 2 (ladera reparada, zona de referencia) |
| `05_Resultados/` | Tablas, ráster de deformación confirmada y bitácoras |
| `06_Bibliografia/` | Referencias del práctico, con DOI |
| `07_Preguntas_y_entrega/` | Las preguntas, la rúbrica y **lo que deja el grupo** |
| `09_Grafos_SNAP/` | Las cadenas de operadores InSAR de SNAP (TOPS para Sentinel-1, stripmap para COSMO-SkyMed), descriptas en su LEEME |
| `08_Orange/` | Dos flujos de Orange: Tp7_A (coherencia por banda, zona y cobertura) y Tp7_B (ICESat-2 menos MDE por zona y MDE), con sus CSV |
| `NOTAS_TECNICAS.md` | Decisiones técnicas, limitaciones y hallazgos con datos reales |

## Los scripts

| # | Script | Marca | Qué hace |
|---|---|---|---|
| 1 | `Tp7_01_pares_insar_C.py` | **SE CORRE** (búsqueda) / **YA VIENE HECHO** (pedido a HyP3) | Busca pares Sentinel-1 SLC sobre el sitio con `asf_search`, los lista con días y línea de base perpendicular; con `--hyp3 N` pide los N mejores a ASF HyP3 |
| 2 | `Tp7_02_coherencia_y_deformacion.py` | **SE CORRE** | Coherencia y desplazamiento de cada banda en la ladera y en la zona de referencia (sinergia) y deformación confirmada por todas las bandas (fusión de decisión) |
| 3 | `Tp7_03_cicatriz_y_volumen.py` | **SE CORRE** | Volumen perdido en la cicatriz y ganado en el depósito por diferencia de MDE (GLO-30 «antes», IGN «después»), descontando el sesgo medido en una zona estable, con el signo esperado y una escarpa de control |
| 4 | `Tp7_04_icesat2_20m_cicatriz.py` | **SE CORRE** | Cotas de ICESat-2 cada 20 m sobre la cicatriz frente al IGN, con el sesgo local y el rango de las laderas sin evento |
| 5 | `Tp7_05_velocidad_y_susceptibilidad.py` | **AMPLIACIÓN** | Velocidad vertical 2025–2026 del Tp10 por franja y susceptibilidad hipotética a fisuras, con umbral de 2σ |
| 6 | `Tp7_06_embeddings_cambio.py` | **AMPLIACIÓN** | Semejanza de los embeddings AlphaEarth 2018–2025 por zona |

Además, tres pasos que no tienen script propio:

| Paso | Marca | Qué es |
|---|---|---|
| Desenrollado de la fase de la banda X | **EN SNAP** | El producto InSAR del curso 2023 tiene la banda `Unw_Phase` **toda en cero**: el desenrollado con SNAPHU nunca se importó. Se rehace en clase (Snaphu Export → snaphu → Snaphu Import → Phase to Displacement) |
| Digitalización de cicatriz y depósito | **EN QGIS** | Sobre el CBERS-4A de 2 m del 26/09/2026 (fondo principal), con su NDVI y las cotas del IGN, y la Pléiades de CONAE (0,5 m, 2022) o el Sentinel-2 del 19/10/2018 como apoyo, con el protocolo de la guía. El Spotlight de COSMO-SkyMed es un SLC sin geocodificar: no sirve de fondo sin procesarlo en SNAP |
| Zonas de la ladera | **EN QGIS** | Escarpa, bloque, pie y ciudad (`E1_zonas_ladera.gpkg`), para `Tp7_02 --zonas` |
| Control del MDE con ICESat-2 | **EN QGIS** + **AUXILIAR** | Comparar el MDE con la altura de terreno de ATL08 en zona estable (la guía da los pasos); los puntos de 20 m sobre la cicatriz, con `Tp7_04` |

## Qué es sinergia y qué es fusión en este práctico

| Paso | Tipo | Nivel | Cómo se valida |
|---|---|---|---|
| Comparar la coherencia de X y C (y L si hubiera par) en la ladera y en la referencia | **SINERGIA** | — | Coherencia física: ¿la banda más larga conserva más coherencia en la vegetación de la ladera? |
| Desplazamiento de cada banda referido a la zona estable | **SINERGIA** | — | Ruido en la zona de referencia menor que el umbral |
| «Deformación confirmada sólo si las bandas coinciden» | **FUSIÓN** | **de decisión** (regla `interseccion` estricta de `fusion_decision`: se decide sólo donde todas las bandas tienen dato coherente; signo según la geometría de cada banda) | Cero en una zona de control independiente de la referencia |
| Cicatriz y depósito digitalizados sobre X y óptico, volumen con MDE | **SINERGIA** (interpretación) + cálculo | — | Píxeles que superan dos desvíos con el signo esperado, y que el patrón no se repita en la escarpa de control |

La presentación (diapositiva 30) habla de bandas C y L. Para octubre de 2018 **no
hay par en banda L**: SAOCOM-1A recién se lanzó ese mes. Las bandas disponibles
son X (COSMO-SkyMed) y C (Sentinel-1). El script acepta L (`--l_desp`, `--l_coh`)
para quien consiga un par SAOCOM de otro período, pero eso ya es otra pregunta.

## Qué se entrega

- `05_Resultados/04_Tablas/E1_coherencia_y_desplazamiento.csv` y su lectura.
- `05_Resultados/02_Rasters/E1_deformacion_confirmada.tif`, con la regla escrita.
- `05_Resultados/04_Tablas/E1_volumenes.csv`, con el sesgo y el ruido restados, el signo esperado y el control.
- La tabla de verificación completa (`01_Prompt_IA/04_Verificacion/verificacion_resultados.md`).
- El polígono `04_Tablas_de_trabajo/E1_cicatriz_y_deposito.gpkg`.
- Las bitácoras de `05_Resultados/06_Control_calidad/`.
- Las respuestas de `07_Preguntas_y_entrega/preguntas.md`.

## Lo que tiene que estar listo antes (YA VIENE HECHO)

| Insumo | Dónde está | Quién lo dejó |
|---|---|---|
| COSMO-SkyMed Himage y Spotlight de Diamante, octubre de 2018 (banda X) | `F:\HFdV COURSES\CEREGEO\2018\TelSAR\DIAMANTE` (copia en `E:\CURSO SAR CEREGEO 2023\PRACTICAL EXERCISES\InSAR\02 IMAGES\CSKS SCS\DIAMANTE`) | Archivo del docente |
| Producto InSAR del par 15/10–19/10/2018, procesado en SNAP en el curso 2023 | `E:\CURSO SAR CEREGEO 2023\PRACTICAL EXERCISES\...\InSAR HI\` (`*_Stack_ifg_dinsar_flt_TC.dim`) | Curso 2023. **`Unw_Phase` en cero** |
| Polígono de la ladera `barranca-periferia_Polygon.shp` | `F:\HFdV COURSES\CEREGEO\2018\TelSAR\DIAMANTE\GRIETAS\` | Relevamiento del curso 2018 |
| MDE recortados al sitio: Copernicus DEM GLO-30, FABDEM, IGN 5 m (vuelo de 2013) y el mosaico IGN del curso 2018 | `02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\E1_DIAMANTE_BARRANCA_*` | Docente (`armar_subsets.py Tp7`) |
| Productos HyP3 del par Sentinel-1 elegido (`*_corr.tif`, `*_los_disp.tif`, …) | `00_COMUN\08_Originales_crudos\HYP3\E1_DIAMANTE_BARRANCA\` (o la carpeta de la variable `CURSO_SAR_ORIGINALES`) | Docente, con `Tp7_01 --hyp3 1` (tarda de 30 min a horas) |
| ICESat-2 ATL08 del sitio | `Tp1_Convergencia\05_Resultados\03_Vectores\lidar_E1_DIAMANTE_BARRANCA.gpkg`, capa `atl08` | Docente, con `Tp1_05_buscar_lidar.py --sitio E1_DIAMANTE_BARRANCA --descargar` |
| SNAP con el ejecutable `snaphu` | En la computadora del aula | Docente |

Si alguno falta, la guía dice qué hacer en cada paso. Las decisiones técnicas y
los resultados con datos reales están en `NOTAS_TECNICAS.md`.
