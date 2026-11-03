# Tp3 — Armonización multisensor

**Pregunta:** ¿cómo llevar SAR, óptico y LiDAR a una grilla y una fecha comparables,
y cómo se demuestra que quedaron alineados?

**Sitio de práctica:** A2 · Delta, Ibicuy (`A2_IBICUY`), el mismo del Tp2, bbox WGS 84
(oeste, sur, este, norte) = −59,30, −33,85, −59,10, −33,65 (ubicación aproximada).
Caso de control con un desplazamiento conocido: `F_BOVRIL` (−59,53, −31,42, −59,40,
−31,29) con la NovaSAR-1 47974 del 14/09/2023 y la Sentinel-2 del 10/09/2023.

**Horario:** martes, 9 a 12 h.

## Para qué sirve este práctico

**Aquí se comprueban los tres requisitos de toda fusión** (presentación 01 del curso,
los tres requisitos de la fusión):

| Requisito | Cómo se comprueba | Script | Criterio |
|---|---|---|---|
| Misma grilla | Todas las capas en EPSG:32721, mismo origen y mismo píxel (el espaciado más grueso de los productos que se fusionan a nivel de píxel; las capas más gruesas que entran igual, como el MDE y la banda P, se declaran sobremuestreadas) | `Tp3_01_cubo_comun.py` | Por construcción; se verifica en QGIS y en la columna `remuestreo` de la tabla de capas |
| Corregistro menor que un píxel | Desplazamiento residual medido con correlación de fase sobre mapas de bordes | `Tp3_02_medir_corregistro.py` | Para fusión de píxel: módulo de la mediana < 0,5 píxel, dispersión < 0,5 píxel y rango < 1 píxel. Para rasgo o decisión: < 1 píxel y rango < 2 píxeles |
| Fechas compatibles | Diferencia en días entre cada par de sensores, y entre cada huella LiDAR y cada capa | `Tp3_01` y `Tp3_03` | Documentada y justificada según el fenómeno |

Si los tres se cumplen, el cubo puede entrar a una fusión de píxel o de rasgo en los
Tp5 a Tp10. Si alguno no se cumple, la fusión de ese par no se hace: se baja a fusión
de decisión o a sinergia, y se declara.

## Qué hay en cada carpeta

| Carpeta | Qué hay |
|---|---|
| `00_Guia_del_practico/` | **Empiece por acá:** `00_LEEME.md` (paso a paso) y `objetivos.md` |
| `01_Prompt_IA/` | Prompt ingenuo, análisis, prompt corregido y verificación |
| `02_Subsets_SNAP_QGIS/` | El cubo armonizado `<SITIO>_cubo_<pixel>m.tif` y su tabla de capas |
| `03_Scripts/` | Los cinco scripts y `00_ORDEN_DE_EJECUCION.md` |
| `08_Orange/` | Tres workflows de Orange (huellas en el cubo, corregistro y fechas, contexto de las huellas) |
| `04_Tablas_de_trabajo/` | `<SITIO>_huellas_con_cubo.csv`: cada huella LiDAR con los valores del cubo |
| `05_Resultados/` | Diferencias de fecha, corregistro, huellas en GeoPackage y bitácoras |
| `06_Bibliografia/` | `referencias.md` |
| `07_Preguntas_y_entrega/` | Preguntas, rúbrica y **lo que entrega el grupo** |
| `NOTAS_TECNICAS.md` | Decisiones técnicas y hallazgos con datos reales |

## Los scripts

| Paso | Script o herramienta | Marca | Qué hace |
|---|---|---|---|
| 0 | `Tp1_05_buscar_lidar.py --solo_contar` (del Tp1) | **AUXILIAR** | Huellas GEDI y ATL08 del sitio, a partir de los granulos ya bajados |
| 1 | `Tp3_01_cubo_comun.py` | **SE CORRE** | Radar (pila del Tp2), óptico (Sentinel-2 L2A con máscara SCL) y MDE en una grilla; diferencias de fecha |
| 2 | revisión del cubo | **EN QGIS** | Grilla, bordes y nubes, a la vista |
| 3 | `Tp3_02_medir_corregistro.py` | **SE CORRE** | Desplazamiento residual entre dos capas: óptico frente a radar, banda L frente a banda S |
| 4 | `Tp3_03_lidar_en_el_cubo.py` | **SE CORRE** | Valores del cubo en cada huella GEDI y segmento ATL08 válido, con la columna `plausible` |
| 5 | gráfico rh98 frente a γ⁰ | **EN QGIS** | Primera lectura conjunta LiDAR-radar-óptico (incluida la banda P de BIOMASS, VH) |
| 6 | `Tp3_04_contexto_y_huellas.py` | **SE CORRE** | Contexto del sitio y de cada huella: MapBiomas (cobertura, pérdida, fuego), CCI Biomass, altura FH de BIOMASS y banda P por clase |
| 6 | `Tp3_05_tablas_para_Orange.py` | **SE CORRE** | Arma las tablas de `08_Orange/datos` (huellas con plausibilidad y CCI, ventanas de corregistro, fechas) a partir de las salidas anteriores |

Las descargas de GEDI y ATL08 **YA VIENEN HECHAS**: el docente deja los granulos en
`<ORIGINALES>\LIDAR\<SITIO>\GEDI02_A\` y `...\ATL08\`.

## Sinergia y fusión en el Tp3

- **El Tp3 no fusiona.** Comprueba si se puede fusionar. Es el control de calidad que
  separa una fusión legítima de una que suma ruido o confunde fechas.
- **El cubo (paso 1)** es la base de una futura **fusión a nivel de píxel** (Tp6,
  Tp10): bandas de varios sensores apiladas en una grilla común.
- **La tabla de huellas (paso 4)** es la base de una futura **fusión a nivel de rasgo**
  (Tp5, Tp9): variables de cada sensor en el mismo punto, listas para un modelo.
- **El paso 5 es SINERGIA**: se mira cómo varían juntos la altura LiDAR, la cruzada
  del radar y el óptico en las mismas huellas, y se los interpreta. Ningún algoritmo
  produce todavía un mapa.

## Qué se entrega

1. El cubo `02_Subsets_SNAP_QGIS/<SITIO>_cubo_20m.tif` y su tabla de capas.
2. `05_Resultados/04_Tablas/<SITIO>_diferencias_de_fecha.csv`.
3. Las mediciones de corregistro (una tabla por par medido) con su veredicto.
4. `04_Tablas_de_trabajo/<SITIO>_huellas_con_cubo.csv` y su GeoPackage.
5. La tabla de los tres requisitos completa: qué pares cumplen y cuáles no, incluidos los
   dos pares nuevos de la pregunta 12.
6. Las tablas y gráficos de contexto de `Tp3_04` (MapBiomas, CCI, FH y banda P).
7. La tabla de verificación de `01_Prompt_IA/04_Verificacion/verificacion_resultados.md`.
8. Las respuestas de `07_Preguntas_y_entrega/preguntas.md`.

## Qué tiene que estar listo antes (YA VIENE HECHO)

- El Tp2 corrido sobre el mismo sitio: `Tp2_SAR_multibanda/02_Subsets_SNAP_QGIS/<SITIO>_pila_gamma0_lineal.tif`
  y `<SITIO>_pila_bandas.csv`. Sin la pila, el cubo se arma sin radar.
- Una fecha de Sentinel-2 L2A `candidata` sobre el sitio (la búsqueda del paso 0 del Tp2).
- Los granulos GEDI L2A v003 y ATL08 v007 del sitio, bajados por el docente.
- La grilla del geoide EGM2008 de PROJ (`us_nga_egm08_25.tif`) si se van a comparar
  alturas de terreno LiDAR con el MDE (ver `NOTAS_TECNICAS.md`).

La lectura de Sentinel-2 y del Copernicus DEM usa el Planetary Computer. Si el Planetary
Computer no responde en el aula, el cubo se arma sólo con radar y la falla se declara.
