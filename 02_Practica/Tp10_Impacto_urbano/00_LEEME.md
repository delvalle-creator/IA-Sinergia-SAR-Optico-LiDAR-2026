# Tp10 — Impacto urbano y subsidencia

**Pregunta del práctico:** ¿cómo crece la ciudad y dónde se hunde el terreno?

**Sitios:**

- **B · Concordia – Salto Grande** (`B_CONCORDIA`, ventana −58,25 / −31,50 / −57,85 / −31,10): crecimiento urbano. Es el sitio de máxima convergencia del curso: bandas C, S y L más óptico.
- **E · Paraná – Diamante** (`E_PARANA_DIAMANTE`, −60,70 / −32,10 / −60,45 / −31,65, ventana aproximada): subsidencia con InSAR en banda C.

**Horario:** viernes, 12 a 13 h y 14 a 16 h (tres horas). De 16 a 18 h siguen las consultas sobre el trabajo final del curso.

**Producto:** mapa de expansión urbana 2019 → 2026 y mapa de velocidad vertical del terreno, cada uno con su control.

Grilla común: EPSG:32721 (UTM 21 S). El Tp10 trabaja a **20 m** en los pasos 2 a 6 (la grilla de NISAR GCOV y de las bandas de 20 m de Sentinel-2), a **20 m** también en la expansión (el píxel de la B11) y a **40 m** en la subsidencia (el píxel de los interferogramas HyP3).

---

## El recorrido, en orden

| Carpeta | Qué hay |
|---|---|
| `00_Guia_del_practico/` | **Empiece por acá.** Los objetivos y la guía paso a paso (órdenes de Miniforge, menús de QGIS, controles, errores típicos) |
| `01_Prompt_IA/` | El prompt ingenuo con sus defectos, el análisis de la respuesta, el prompt corregido de la primera versión (prompt_02), el que corresponde a los scripts actuales (prompt_03) y el protocolo de verificación |
| `02_Subsets_SNAP_QGIS/` | Los recortes del sitio que deja el docente (Sentinel-1 y 2, NovaSAR, NISAR, Landsat, CBERS-4A, AlphaEarth, los HyP3 de Paraná – Diamante, Pléiades de CONAE…; ver su LEEME) y el ráster de mapas urbanos por banda que escribe el paso 2 (`Tp10_01`) |
| `03_Scripts/` | Los seis programas y el orden de ejecución |
| `04_Tablas_de_trabajo/` | Lo que digitaliza el grupo en QGIS: polígonos de entrenamiento, zona de referencia estable y puntos de control |
| `05_Resultados/` | Rásters, tablas, gráficos y bitácoras que escriben los programas |
| `06_Bibliografia/` | Las referencias del práctico, cada una con para qué sirve |
| `07_Preguntas_y_entrega/` | Las preguntas, la rúbrica y **lo que deja el grupo** |
| `NOTAS_TECNICAS.md` | Las decisiones técnicas y su fundamento, y las limitaciones conocidas |

Este práctico **no usa SNAP**: no tiene carpeta de grafos. Todo se hace con Python (Miniforge, entorno `sar`) y QGIS.

---

## Los seis scripts

La numeración de pasos es la de la guía (`00_Guia_del_practico/00_LEEME.md`, pasos 0 a 11).

| Paso de la guía | Script | Marca | Qué hace | Tipo de combinación |
|---|---|---|---|---|
| 2 | `Tp10_01_doble_rebote_sinergia.py` | **SE CORRE** | Mapa urbano por banda (C, S, L) con umbral documentado; tabla de coincidencias; detalle del mapa en banda S a 6, 10 y 20 m | **SINERGIA** |
| 5 y 6 | `Tp10_02_fusion_pixel_urbano.py` | **SE CORRE** | Compuestos de temporada, entrenamiento de MapBiomas en proporción al paisaje y un Random Forest por conjunto de sensores: óptico (B02, B03, B04, B08, B11, NDBI, NDVI, MNDWI), C (VV, VH, textura de VV), C + L (más L HH y L HV), multisensor (C + L + óptico) y multisensor con S (más S HH, sólo en la huella de NovaSAR) | **FUSIÓN DE RASGOS** (bandas, índices y textura) |
| 7 | `Tp10_03_expansion_urbana.py` | **SE CORRE** | Un Random Forest Sentinel-1 + Sentinel-2 por año (2019 y 2026) y comparación de los dos mapas; cambio sólo si es confiable en las dos fechas; matriz de transiciones | **DETECCIÓN DE CAMBIOS por comparación posterior a la clasificación** (cada año es una fusión de rasgos; la regla compara decisiones de dos fechas, no de dos sensores) |
| 8 | `Tp10_04_pares_sbas.py` | **AUXILIAR / YA VIENE HECHO** | Arma la red de pares de línea de base corta de Sentinel-1 y, con `--hyp3`, los pide a HyP3 | — |
| 10 | `Tp10_05_velocidad_subsidencia.py` | **SE CORRE** | Velocidad vertical por apilado de tasas, con zona de referencia, puntos de control (criterio con el error de la media) y control de saltos de desenrollado | Un solo sensor (C); la sinergia está en la interpretación |
| 11 | `Tp10_06_dominio_huella_S.py` | **SE CORRE** | Compara las cinco variantes en la misma superficie (la huella de NovaSAR) | — |
| 4 y 9 | Revisar el entrenamiento, digitalizar referencia y control | **EN QGIS** | Ver la guía, pasos 4 y 9 | — |

El orden exacto, con los argumentos, está en `03_Scripts/00_ORDEN_DE_EJECUCION.md`.

---

## Qué es sinergia y qué es fusión en este práctico

Se sigue la regla 5 de `00_COMUN/REGLAS_DEL_PROYECTO.md` y el `GLOSARIO.md`.

**SINERGIA (paso 2, `Tp10_01`).** Cada banda produce **su** mapa urbano por doble rebote: el diedro pared + calle devuelve la señal a la antena. El programa no los combina: arma una tabla de coincidencias y el grupo explica por qué coinciden o difieren (longitud de onda, polarización —C en VV, S y L en HH— y geometría de cada pasada). Se valida por **coherencia física**.

**FUSIÓN DE RASGOS (paso 6, `Tp10_02`).** Un Random Forest recibe, en la misma grilla de 20 m, bandas de radar en dB, reflectancias, los índices NDBI, NDVI y MNDWI y la textura de VV, y produce **un** mapa de clases. Como entran variables derivadas, es fusión de rasgos (no de píxel). Se valida con la **exactitud del producto** en el Tp4.

**DETECCIÓN DE CAMBIOS (paso 7, `Tp10_03`).** Para comparar 2019 con 2026 hace falta el mismo método en las dos fechas. NovaSAR y NISAR no existían en 2019; Sentinel-1 y Sentinel-2 sí. Cada año se clasifica con una fusión de rasgos Sentinel-1 + Sentinel-2 y una regla escrita compara los dos mapas: un píxel cambia sólo si la clase ganadora tiene probabilidad de 0,6 o más en las dos fechas y forma una mancha de al menos 5 píxeles. Lo demás queda «sin decidir».

**Subsidencia (pasos 8 a 10).** Es un solo sensor (banda C) en muchas fechas: no hay fusión. Se calcula un **apilado de tasas** (no una inversión SBAS). La sinergia aparece al leer el mapa de velocidad junto al de clases: ¿se hunde lo nuevo, lo rellenado, lo construido sobre bajos?

---

## Lo que hay que tener listo antes (YA VIENE HECHO)

| Insumo | De dónde sale | Dónde queda |
|---|---|---|
| NISAR GCOV banda L del 18/09/2026 sobre Concordia (HH y HV; traza 10, cuadro 104, descendente) | **No está en los mosaicos del Delta.** Lo bajó el docente (`datos_crudos.py nisar`, cuenta de NASA Earthdata) | `00_COMUN\08_Originales_crudos\NISAR\NISAR_L2_PR_GCOV_031_010_D_104_2005_DHDH_A_20260918T215921_20260918T215955_P05023_F_F_J_001.h5` |
| NovaSAR-1 escena 47942 (13/09/2023, HH, 6 m) | Archivo del curso (CSIRO) | `E:\IMÁGENES NOVASAR-1 2023 2024\ENTRE RIOS-SANTA FE` |
| Desplazamiento de la georreferencia de NovaSAR 47942 | `Tp3_02_medir_corregistro.py` (Tp3) | `Tp3_Armonizacion\05_Resultados\04_Tablas\B_CONCORDIA_corregistro_S_NovaSAR_sigma0_HH_vs_OPT_S2_B08.csv` |
| Cobertura de control de Concordia a 20 m (opcional, mejora la tabla del paso 2) | `Tp4_01_cobertura_de_control.py --sitio B_CONCORDIA --pixel 20` (Tp4) | `Tp4_Validacion\02_Subsets_SNAP_QGIS\B_CONCORDIA_cobertura_control_20m.tif` |
| Interferogramas HyP3 de Paraná – Diamante: 120 pares del 01/06/2025 al 03/07/2026, recortados al sitio | `Tp10_04_pares_sbas.py --hyp3 120` (horas de proceso en ASF) y `00_COMUN\recortar_hyp3.py` | `02_Subsets_SNAP_QGIS\HyP3_E_PARANA_DIAMANTE\` (los originales completos, 99 GB, en `00_COMUN\08_Originales_crudos\HYP3\E_PARANA_DIAMANTE\`) |

Sentinel-1 RTC y Sentinel-2 L2A se leen en el momento desde el Microsoft Planetary Computer (sin cuenta): hace falta conexión a internet.

---

## Tres cosas que tiene que saber desde el principio

1. **NovaSAR cubre sólo el 39 % de Concordia.** Por eso el Random Forest se corre en dos versiones: `con_S` (sólo donde hay NovaSAR) y `sin_S` (todo el sitio). Compararlas es la manera honesta de medir cuánto aporta la banda S.
2. **NovaSAR es de 2023; C y L son de 2026.** Tres años de diferencia. Lo que aparece urbano sólo en C y en L puede ser crecimiento real, no error.
3. **PS (dispersores persistentes) se explica, no se hace.** Necesita software específico (StaMPS, SARPROZ) y una pila de más de 20 SLC corregistrados. El curso hace un apilado de tasas de una red de pares de línea de base corta; no es una inversión SBAS.

---

## Qué se entrega

En `07_Preguntas_y_entrega/`: las respuestas a `preguntas.md`, cada cifra con el archivo de `05_Resultados` del que sale; el mapa de expansión y el de velocidad, con leyenda, fecha, fuente e incertidumbre; la fila del Tp10 de la tabla de variantes del Tp4; la bitácora de IA. El detalle está en `07_Preguntas_y_entrega/00_LEEME_que_va_aqui.md`.
