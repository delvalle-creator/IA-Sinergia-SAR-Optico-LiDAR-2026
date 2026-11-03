# Tp6 · Inundaciones: extensión, duración y profundidad

**Pregunta del práctico:** ¿qué área cubrió el agua, cuánto tiempo y a qué profundidad?

## Sitio y eventos

B · Concordia – Salto Grande, río Uruguay (`B_CONCORDIA`, bbox −58,25, −31,50, −57,85, −31,10). Dos crecidas: **noviembre de 2023** (el umbral se fija el 04/11/2023, la fecha con Sentinel-1A y Sentinel-2B del mismo día; no es el pico de la serie, que llega el 28/11/2023) y **mayo de 2024** (activación 880 de la Carta Internacional Espacio y Grandes Catástrofes).

## Horario

Miércoles de 14 a 18 h. La validación de las variantes (Tp4) se reparte entre grupos: cada grupo etiqueta una sola variante.

## Núcleo y bloques para profundizar

- **Núcleo (se evalúa):** pasos 1 a 6, la prueba de la banda L con SAOCOM y la segunda crecida.
- **Para profundizar (optativo):** ALOS-2, banda P, NovaSAR, el Sentinel-1 desde el producto sin procesar en SNAP, Orange y los embeddings.

## Los sensores, cada uno con su pregunta

| Sensor | Qué responde | Fechas |
|---|---|---|
| Sentinel-1 RTC (C, VV) | agua abierta con cualquier cielo: el agua calma refleja especularmente y se ve muy oscura | serie del 01/10/2023 al 30/06/2024, una sola órbita relativa |
| Sentinel-2 L2A (MNDWI) | agua abierta con cielo despejado | 04/11/2023 |
| Banda L, HH (SAOCOM) | agua **bajo** la vegetación: el doble rebote tronco–agua aumenta HH | SAOCOM-1B del 10/10 (seco) y del 11/11/2023 (crecida), en γ⁰; se prueba en el paso 2 y no aporta agua bajo vegetación detectable |
| NovaSAR-1 (S, HH, 6 m) | agua en el cauce antes de la crecida, como interpretación | 13/09/2023 (escena 47942, cubre el 39 % del sitio) |
| JRC Global Surface Water | agua permanente (ocurrencia ≥ 90 %): el río y el embalse no son inundación | 1984–2021 |
| Copernicus DEM GLO-30 | cota del terreno para la profundidad | 2011–2015 |
| ICESat-2 ATL08 | altura del terreno para controlar el MDE | las trazas que caen en el sitio |

**Banda L: se prueba y se descarta con fundamento.** CONAE entregó dos SAOCOM-1B de la misma órbita, uno seco (10/10/2023) y uno de la crecida (11/11/2023, una semana después de la fecha del práctico). Entre las dos fechas la HH subió 3,1 dB en todo el paisaje, así que la regla fija de 3 dB marca medio sitio; restando ese cambio general y mirando sólo el monte y las plantaciones queda un 1,4 % de candidatos lejos del río, sin coincidencia con el agua de C ni del óptico. El agua bajo vegetación no se puede separar con este par: la sinergia que entra a la fusión es C frente a óptico, y la variante «SAR multibanda» no existe.

## Carpetas

| Carpeta | Qué hay |
|---|---|
| `00_Guia_del_practico/` | **Empiece por acá.** `objetivos.md` y la guía paso a paso `00_LEEME.md` |
| `01_Prompt_IA/` | Prompt ingenuo, análisis, prompt corregido y verificación |
| `02_Subsets_SNAP_QGIS/` | La serie de agua de banda C por fecha: `B_agua_C_por_fecha_<pixel>m.tif` |
| `03_Scripts/` | Los cinco scripts y `00_ORDEN_DE_EJECUCION.md` |
| `04_Tablas_de_trabajo/` | Sin archivos propios: el etiquetado de las variantes se hace en el Tp4 |
| `05_Resultados/` | Extensión, duración, agua por sensor, variantes, profundidad, tablas, gráficos y bitácoras |
| `06_Bibliografia/` | Referencias del práctico |
| `07_Preguntas_y_entrega/` | Preguntas, rúbrica y entrega |
| `09_Grafos_SNAP/` | Cómo se procesó la banda L SAOCOM en SNAP |

## Los scripts

| Paso | Script | Marca | Qué hace | Sinergia o fusión |
|---|---|---|---|---|
| 1 | `Tp6_01_serie_agua_C.py` | **SE CORRE** | Serie de agua abierta en C: umbral de VV en la fecha del par Sentinel-1 y Sentinel-2 (04/11/2023) aplicado a todas las fechas; extensión máxima y persistente, duración mínima y máxima | un sensor |
| 2 | `Tp6_02_sinergia_agua.py` | **SE CORRE** | Agua según C y según el óptico (y según L, si la hubiera) el día del evento; tabla de acuerdo | **SINERGIA** |
| 3 | `Tp6_03_fusion_y_variantes.py` | **SE CORRE** | Variantes óptico, C, C ∪ L (si hay L) y multisensor por reglas escritas | **FUSIÓN DE DECISIÓN** |
| 4 | `Tp4_02`, `Tp4_03`, `Tp4_04` | **SE CORRE** + **EN QGIS** | Validación de las variantes | validación de la fusión |
| 5 | `Tp6_04_profundidad.py` | **SE CORRE** | Profundidad por cota del borde (idea de FwDET), con el Copernicus DEM o con FABDEM (`--mde`) | producto derivado de la decisión y el MDE |
| 6 | `Tp6_05_control_mde_icesat2.py` | **SE CORRE** | Sesgo, desvío y RMSE del MDE frente al terreno de ICESat-2, por clase de control y por clase de MapBiomas 2023 (`--clases ambas`) | control del insumo |

## Qué es sinergia y qué es fusión en este práctico

- **SINERGIA (paso 2).** C y óptico dicen, cada uno con su física, dónde ven agua el 04/11/2023. No se combina: se mide el acuerdo. Donde el óptico tiene nube, no vota. Se valida por coherencia física: en agua abierta con cielo despejado, C y óptico deberían coincidir; donde no coinciden hay que explicar por qué (viento, vegetación, nubes, turbidez).
- **FUSIÓN DE DECISIÓN (paso 3).** Agua de inundación si C dice agua (R1), o si L dice doble rebote (R2, probada con SAOCOM y no aplicada), o si el óptico dice agua sin nube (R3); nunca en agua permanente (R4) ni donde ya había agua en la fecha seca de referencia (R5). Es decisión, y no píxel, porque los sensores llegan con nubes, fechas y píxeles distintos. Se valida con la exactitud del producto (Tp4).

## Qué se entrega

Mapas de extensión, duración y profundidad, con leyenda, fecha, fuentes e incertidumbre; la tabla de variantes del Tp4; la tabla de sinergia; el control del MDE; las respuestas.

## Qué tiene que estar listo antes

- **Tp4_01** corrido para `B_CONCORDIA` a 20 m (`Tp4_Validacion\02_Subsets_SNAP_QGIS\B_CONCORDIA_cobertura_control_20m.tif`). Lo usa el paso 6 para separar el control del MDE por cubierta.
- **YA VIENE HECHO:** los segmentos ATL08 del sitio, con `Tp1_05_buscar_lidar.py --sitio B_CONCORDIA --descargar`, en `Tp1_Convergencia\05_Resultados\03_Vectores\lidar_B_CONCORDIA.gpkg`, capa `atl08`.
- La grilla del geoide EGM2008 de PROJ (`us_nga_egm08_25.tif`). Con red, PROJ la baja sola; si no, `projsync --file us_nga_egm08_25` en el Miniforge Prompt.
- Conexión a internet: Sentinel-1, Sentinel-2, JRC y el Copernicus DEM se leen del Planetary Computer.

## Lo que se dice desde el principio

- Los pasos 1, 2 y 5 (con el Copernicus DEM) leen del Planetary Computer: necesitan internet.
- La validación usa como referencia el Sentinel-2 del mismo día, que entra en la variante óptica y en la multisensor: las favorece, y se declara. Sólo la variante C se valida sin ese sesgo.
- La referencia seca por defecto (22/01/2026) es posterior al evento: puede borrar agua real. Lo correcto es una o varias fechas secas anteriores de la misma órbita (`--referencia_seca` acepta varias, separadas por coma).
- La profundidad es **plausible, no medida**: sin un hidrómetro o una marca de crecida no se valida. Y el Copernicus DEM es un modelo de **superficie**: en el monte mide la copa.
- Los nombres de las variantes (`B_variante_*.tif`) no llevan la fecha: correr el paso 3 para la crecida de mayo de 2024 **reescribe** las de noviembre de 2023. Copie y renombre antes (la guía dice cómo).
