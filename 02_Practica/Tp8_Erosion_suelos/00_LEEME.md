# Tp8 — Erosión de suelos y cárcavas

**Pregunta del práctico:** ¿dónde hay suelo expuesto de forma persistente y qué
parte de él muestra erosión visible? (El avance de las cárcavas necesita una
segunda fecha de 2 m y queda como extensión fuera del horario.)

**Sitio:** `F_BOVRIL`, Bovril y su entorno rural, centro de Entre Ríos
(WGS84: −59,53 / −31,42 / −59,40 / −31,29; ventana de la presentación 02).

**Horario:** jueves, 14 a 18 h.

**Fechas:** serie Sentinel-2 de 2023 completa; NovaSAR-1 (banda S, 6 m, HH)
escena 47974 del 14/09/2023, que cubre el 92,9 % del sitio (la variante multisensor, el 89 %); Sentinel-2 del
10/09/2023 como par óptico; Sentinel-1 RTC de la fecha más cercana al 14/09/2023.

## El recorrido, en orden

| Carpeta | Qué hay |
|---|---|
| `00_Guia_del_practico/` | **Empiece por acá.** Los objetivos y la guía paso a paso (Miniforge, SNAP y QGIS) |
| `01_Prompt_IA/` | El prompt ingenuo y sus defectos, el análisis de la respuesta, el prompt corregido que produjo los scripts y la verificación |
| `02_Subsets_SNAP_QGIS/` | Los rásters intermedios en la grilla de 10 m: frecuencia de suelo desnudo y texturas S y C. Los escriben los pasos 1 y 2 |
| `03_Scripts/` | Los tres scripts y el orden de ejecución |
| `04_Tablas_de_trabajo/` | La capa de entrenamiento que digitaliza el grupo |
| `05_Resultados/` | Susceptibilidad, variantes para el Tp4, tablas y bitácoras |
| `06_Bibliografia/` | Referencias con DOI |
| `07_Preguntas_y_entrega/` | Preguntas, rúbrica y **lo que deja el grupo** |
| `09_Grafos_SNAP/` | La textura de Haralick (GLCM) en SNAP, descripta en su LEEME |
| `NOTAS_TECNICAS.md` | Decisiones técnicas, limitaciones y hallazgos con datos reales |

## Los tres scripts

| # | Script | Marca | Qué hace |
|---|---|---|---|
| 1 | `Tp8_01_frecuencia_suelo_desnudo.py` | **SE CORRE** | Meses del año con suelo desnudo (NDVI < 0,25 y BSI > 0) en la serie Sentinel-2 de 2023 |
| 2 | `Tp8_02_textura_S_y_C.py` | **SE CORRE** | Textura (coeficiente de variación local) en banda S (NovaSAR) y en banda C (Sentinel-1), por separado, y su comparación por clase de frecuencia |
| 3 | `Tp8_03_susceptibilidad.py` | **SE CORRE** | Random Forest con los rasgos (suelo desnudo, texturas, pendiente) → índice de susceptibilidad y variantes para el Tp4 |

Pasos sin script propio:

| Paso | Marca | Qué es |
|---|---|---|
| Medir el desfase de NovaSAR | **EN QGIS** (o `Tp3_02`) | Con los 84 puntos de enlace, la escena 47974 está corrida 80 m al este y 20 m al sur; se corrige moviéndola 80 m al oeste y 20 m al norte (`--desplazamiento -80 20`) |
| Textura de Haralick | **EN SNAP** | `Raster > Image Analysis > Texture Analysis > Grey Level Co-occurrence Matrix`, para comparar con el CV del script |
| Entrenamiento | **EN QGIS** | Polígonos de erosión activa o cárcava (1) y suelo estable (2), trazados sobre los puntos ya sorteados de `04_Tablas_de_trabajo/estrato_erosion_F.gpkg` |
| Aporte del radar | **EN ORANGE** | Workflow `08_Orange/Tp8_D_aporte_del_radar.ows`: Random Forest con y sin radar, validado por polígono |
| Avance de cárcavas | **EN QGIS** (COMPLEMENTARIO, fuera del horario) | Digitalizar la cabecera de cada cárcava en dos fechas de 2 m (el archivo trae una sola, CBERS-4A del 15/06/2023; la segunda sale de Google Earth Pro) |

## Qué es sinergia y qué es fusión en este práctico

| Paso | Tipo | Nivel | Cómo se valida |
|---|---|---|---|
| Textura en S (NovaSAR, píxel de 6 m llevado a 10 m) frente a textura en C (Sentinel-1 IW: espaciado de 10 m, resolución de unos 20 × 22 m), por clase de frecuencia de suelo desnudo | **SINERGIA** | — | Coherencia física: ¿la banda S, más larga (9,4 cm frente a 5,5 cm) y de resolución más fina, marca más los bordes de cárcava? |
| GLCM de SNAP frente al CV del script | **SINERGIA** (dos medidas de lo mismo) | — | ¿Ordenan las clases de la misma manera? |
| Suelo desnudo + textura S + textura C + pendiente → susceptibilidad | **FUSIÓN** | **de rasgo** (variables derivadas de cada sensor en un Random Forest) | Exactitud de la variante con muestra independiente (Tp4) y comparación con la variante «óptico + pendiente» del mismo Random Forest (`--rasgos`), validada por polígono |
| «Solo óptico: ≥ 6 meses desnudo» | Variante de un solo sensor | — | Se compara con la multisensor en la tabla de variantes del Tp4 |

## Qué se entrega

- `05_Resultados/02_Rasters/F_susceptibilidad.tif` y su lectura.
- Las dos variantes binarias para el Tp4 (`F_variante_optico.tif`,
  `F_variante_multisensor.tif`) y, si hay tiempo, su exactitud.
- `05_Resultados/04_Tablas/F_textura_por_frecuencia.csv` interpretada.
- La importancia de cada rasgo (bitácora del paso 3).
- La capa de entrenamiento y las respuestas a las preguntas.

## Lo que tiene que estar listo antes (YA VIENE HECHO)

| Insumo | Dónde está |
|---|---|
| NovaSAR-1 escena 47974 (GRD, HH, 6 m), cedida por CSIRO | `E:\IMÁGENES NOVASAR-1 2023 2024\ENTRE RIOS-SANTA FE\NovaSAR_01_47974_grd_*_HH\` (variable `CURSO_SAR_NOVASAR`) |
| Red hacia el Planetary Computer (Sentinel-2, Sentinel-1 RTC, Copernicus DEM) | Sin cuenta |
| El desfase de NovaSAR medido por el docente en la clase teórica (presentación 02) | Corrección ≈ 80 m al oeste y 20 m al norte (`--desplazamiento -80 20`) |
| Serie Sentinel-2 local para correr el paso 1 sin internet (`--local`) | `00_COMUN/08_Originales_crudos/PLANETARY/F_BOVRIL/sentinel-2-l2a` (68 fechas) |
| Estrato y puntos sorteados del paso 4 | `04_Tablas_de_trabajo/estrato_erosion_F.gpkg` |
| Zonas homogéneas para el piso de speckle | `04_Tablas_de_trabajo/zonas_homogeneas.gpkg` |

Los pasos 1, 2 y 3 leen el Planetary Computer. Sin internet, el paso 1 corre con
`--local` y en los pasos 2 y 3 se usan los productos de `02_Subsets_SNAP_QGIS`.
Ver `NOTAS_TECNICAS.md`.
