# Tp6 — Objetivos

## Objetivo general

Estimar la extensión, la duración y la profundidad del agua de las crecidas del río Uruguay en Concordia (noviembre de 2023 y mayo de 2024) con radar de banda C, óptico, un modelo de elevación y LiDAR, separando la sinergia de la fusión, y validar las variantes con el Tp4.

## Objetivos específicos

1. Construir una serie temporal de agua abierta con Sentinel-1 VV de una sola órbita, con un umbral fijado en la fecha con Sentinel-1 y Sentinel-2 del mismo día (04/11/2023) y aplicado a todas las fechas, y estimar la duración del agua tratando las fechas no observadas como desconocidas.
2. Excluir el agua permanente (JRC ≥ 90 %) y explicar por qué el embalse rizado por el viento se aclara en VV y entraría, según el viento de cada fecha, como falsa inundación.
3. Comparar sin fusionar el agua según C y según el óptico el día del evento, y explicar sus diferencias (**sinergia**); reconocer qué agrega la banda L y probar con SAOCOM si el par de fechas disponible la deja medir.
4. Combinar las decisiones de cada sensor con reglas escritas (R1 a R5) y producir las variantes para el Tp4 (**fusión de decisión**).
5. Estimar la profundidad por la cota del borde con un modelo de superficie y uno de terreno, y declarar por qué es una profundidad plausible y no medida.
6. Controlar el modelo de elevación con el terreno de ICESat-2, con la conversión de alturas elipsoidales al geoide EGM2008, y decir cuánto sesgo y cuánto error por píxel hereda la profundidad.

## Qué debe entregar

- `B_extension_y_duracion_C_20m.tif`, `B_serie_agua_C.csv` y su gráfico.
- `B_sinergia_agua.csv` y `B_agua_por_sensor_20m.tif`.
- Las variantes y la tabla de variantes del Tp4.
- `B_profundidad_multisensor_20m.tif` y `B_control_mde_icesat2.csv`.
- Las respuestas, cada cifra con el archivo del que sale.

## Criterio de evaluación

Se evalúa que el grupo **declare lo que cada sensor no ve** (agua bajo vegetación que la banda L de este par no separa, agua bajo nubes para el óptico, embalse rizado), que el umbral esté documentado con su histograma, que la fusión tenga sus reglas escritas, que la referencia de validación sea independiente o su sesgo esté declarado por variante, que la profundidad se presente con su incertidumbre y su control, y que la conclusión no diga más de lo que permiten los intervalos del Tp4.

## Núcleo y bloques para profundizar

- **Núcleo (se evalúa):** pasos 1 a 6, la prueba de la banda L con SAOCOM y la segunda crecida (mayo de 2024). Cada grupo etiqueta una sola variante (142 puntos); las otras dos se comparten entre grupos.
- **Para profundizar (optativo):** ALOS-2 del 16/11/2023, banda P de BIOMASS, NovaSAR, el Sentinel-1 desde el producto sin procesar en SNAP, los workflows de Orange y los embeddings AlphaEarth. Tienen preguntas optativas (A a D) y no entran en la rúbrica.
