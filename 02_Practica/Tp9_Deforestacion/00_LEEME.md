# Tp9 — Deforestación y degradación del monte nativo

**Pregunta del práctico:** ¿dónde se perdió el monte entre 2021 y 2026 (con 2011 como referencia histórica), cómo se distingue un desmonte de un lote cosechado y es detectable la degradación bajo el dosel con estos datos?

**Sitio:** `C_FEDERAL`, Federal, monte nativo del Espinal
(WGS84: −59,02 / −30,99 / −58,62 / −30,59; ventana de la presentación 02). La
banda P de BIOMASS sí cubre Federal: el L1B DGM del 12/08/2026 y los productos
L2A de altura del bosque (FH) y de retrodispersión con el suelo cancelado (GN) del
28/07 al 09/08/2026 están recortados al sitio en `02_Subsets_SNAP_QGIS`.

**Horario:** viernes, 9 a 12 h.

**Grilla:** EPSG:32721, **20 m** (la de NISAR GCOV). ALOS-2 es de 25 m: se lleva a
20 m y se declara.

## Los datos y sus fechas

| Banda | Sensor | Fecha | Polarización |
|---|---|---|---|
| L | ALOS-1 PALSAR FBS (RTC de ASF, 12,5 m) | 13/03/2011 | **sólo HH** |
| L | ALOS-2 PALSAR-2 mosaico anual (JAXA, 25 m) | 2021 | HH y HV |
| L | NISAR GCOV (ASF) | 17/09/2026 | HH y HV |
| C | Sentinel-1 RTC (órbita 68, descendente) | 10/08/2021 y 14/09/2026 | VV y VH |
| S | NovaSAR-1, escena 50896 (cubre el 51 % del sitio) | 22/12/2023 | HH |
| P | BIOMASS L1B DGM (geometría de radar, ubicado por puntos de control) | 12/08/2026 | HH, HV, VH y VV |
| Óptico | Sentinel-2 NDVI | 06/08/2021 y 16/09/2026 (por defecto) | — |
| LiDAR | GEDI L2A V003, huellas válidas | 2019–2023 y 2024–2025 | rh98 |

## El recorrido, en orden

| Carpeta | Qué hay |
|---|---|
| `00_Guia_del_practico/` | **Empiece por acá.** Objetivos y guía paso a paso |
| `01_Prompt_IA/` | Prompt ingenuo y defectos, análisis, prompt corregido que produjo los scripts, verificación |
| `02_Subsets_SNAP_QGIS/` | La pila temporal multibanda y el ráster de Δrh98 por celda. Los escriben los pasos 1 y 2 |
| `03_Scripts/` | Los tres scripts y el orden de ejecución |
| `04_Tablas_de_trabajo/` | La capa de entrenamiento: trae 70 polígonos de partida hechos sobre la imagen CBERS-4A de 2 m (2021 y 2026), con sorteo al azar y revisión a ojo, que el grupo revisa, corrige y completa (la vacía está en `entrenamiento_C_vacio.gpkg`) |
| `05_Resultados/` | Mapa de pérdida y degradación, variantes, curvas de respuesta, tablas y bitácoras |
| `06_Bibliografia/` | Referencias con DOI |
| `07_Preguntas_y_entrega/` | Preguntas, rúbrica y **lo que deja el grupo** |
| `NOTAS_TECNICAS.md` | Decisiones técnicas, limitaciones y hallazgos con datos reales |

## Los tres scripts

| # | Script | Marca | Qué hace |
|---|---|---|---|
| 1 | `Tp9_01_pila_temporal.py` | **SE CORRE** | Arma la pila multitemporal y multibanda (L, C, S, NDVI) en la grilla de 20 m y calibra entre sí ALOS-1, ALOS-2 y NISAR en zonas estables |
| 2 | `Tp9_02_sinergia_estratos.py` | **SE CORRE** | Qué estrato ve cada banda: correlación y curva de respuesta frente a la altura GEDI rh98; parte B banda P (BIOMASS de Federal); parte C degradación con Δrh98 por celda de 200 m sin cambio óptico |
| 3 | `Tp9_03_fusion_perdida_degradacion.py` | **SE CORRE** | Random Forest de rasgos (ΔHV L, ΔHH L histórico, ΔVH C, ΔNDVI, nivel actual) → pérdida, degradación, monte estable, no bosque; variantes y control complementario con GEDI. Opciones para comparar: `--sin_equilibrar`, `--sin_historico`, `--mascara_monte_2021` |

## Qué es sinergia y qué es fusión en este práctico

| Paso | Tipo | Nivel | Cómo se valida |
|---|---|---|---|
| Calibración cruzada ALOS-1 / ALOS-2 / NISAR en zona estable | **Armonización** (ni sinergia ni fusión: condición previa) | — | Desfase corregido; el cambio mínimo interpretable es el residuo después de corregir, medido en cuadrados no usados para calibrar, por separado en monte y ciudad |
| Curvas de respuesta de cada banda frente a rh98 (C, L, S, NDVI y P, todas sobre las huellas de Federal) | **SINERGIA** | — | Coherencia física: la banda que sigue subiendo con la altura ve la estructura leñosa |
| Degradación: caída de rh98 por celda sin cambio de NDVI | **SINERGIA** (LiDAR + óptico interpretados juntos) | — | Se contrasta con el mapa del paso 4, contando celdas |
| SAOCOM 2021–2026 (gemelos, mediana del sitio restada) frente al mapa | **SINERGIA** (control independiente: no entró al modelo) | — | % de cada clase con caída de HV > 3 dB |
| ΔHV L + ΔHH L + ΔVH C + ΔNDVI + NDVI y HV actuales → 4 clases | **FUSIÓN** | **de rasgo** | Exactitud con muestra independiente (Tp4) y Δrh98 por clase del mapa |
| «Solo óptico» (ΔNDVI < −0,10) y «solo L» (ΔHV L < −1,5 dB, o ΔHH L si NISAR no trae HV) | Variantes de un solo sensor | — | Tabla de variantes del Tp4 |

## Qué se entrega

- `05_Resultados/04_Tablas/C_calibracion_cruzada.csv` y su lectura.
- `05_Resultados/04_Tablas/C_sensibilidad_a_la_altura.csv` y
  `05_Resultados/05_Graficos/C_curvas_de_respuesta.png`, interpretados.
- `05_Resultados/04_Tablas/C_delta_rh98_por_celda.csv` (candidatas a degradación).
- `05_Resultados/02_Rasters/C_perdida_degradacion.tif` y su figura.
- Las tres variantes para el Tp4 y `C_control_gedi_por_clase.csv`.
- Las respuestas a las preguntas.

## Lo que tiene que estar listo antes (YA VIENE HECHO)

| Insumo | Dónde está | Cómo se obtuvo |
|---|---|---|
| ALOS-1 PALSAR FBS RTC del 13/03/2011 (HH) | `00_COMUN\08_Originales_crudos\ASF\C_FEDERAL\ALOS\AP_27336_FBS_F6560_RT1\AP_27336_FBS_F6560_RT1_HH.tif` | `Tp1_04_buscar_asf.py --sitio C_FEDERAL --desde 2011-01-01 --hasta 2011-12-31 --solo ALOS --descargar 1` |
| NISAR GCOV del 17/09/2026 (traza 161, cuadro 162, ascendente) | `00_COMUN\08_Originales_crudos\NISAR\NISAR_L2_PR_GCOV_030_161_A_162_2005_DHDH_A_20260917T095508_20260917T095543_P05023_N_F_J_001.h5` | `Tp1_04_buscar_asf.py --solo NISAR --descargar 1` |
| Huellas GEDI L2A del sitio, filtradas | `Tp1_Convergencia\05_Resultados\03_Vectores\lidar_C_FEDERAL.gpkg`, capa `gedi_l2a` | `Tp1_05_buscar_lidar.py --sitio C_FEDERAL --descargar` |
| Cobertura de control a 20 m | `Tp4_Validacion\02_Subsets_SNAP_QGIS\C_FEDERAL_cobertura_control_20m.tif` | `Tp4_01_cobertura_de_control.py --sitio C_FEDERAL --pixel 20` con el monte **confirmado sin cambio** digitalizado (clase 3) |
| NovaSAR-1 escena 50896 | `E:\IMÁGENES NOVASAR-1 2023 2024\ENTRE RIOS-SANTA FE` | Archivo del curso (CSIRO) |
| BIOMASS de Federal (banda P) | `02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\C_FEDERAL_BIOMASS_P_20260812.tif` (γ⁰ HH, HV, VH y VV lineal; el `.dim` y el RGB HH-HV-HH/HV al lado) | `armar_subsets.py Tp9` (ESA MAAP) — **YA VIENE HECHO** |

Si la cobertura de control no tiene el monte confirmado, la calibración cruzada
se hace sólo con la clase urbana (`--solo_urbano`) y se declara. Lo que no se
pudo probar con datos reales está en `NOTAS_TECNICAS.md`.
