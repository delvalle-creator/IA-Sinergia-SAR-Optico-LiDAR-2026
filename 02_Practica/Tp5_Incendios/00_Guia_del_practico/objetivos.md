# Tp5 — Objetivos

## Objetivo general

Delimitar las áreas quemadas en las islas del Delta en 2020 y estimar su severidad combinando radar de bandas C y L, óptico y LiDAR, distinguiendo lo que se resuelve por sinergia de lo que se resuelve por fusión, y validar cada variante con la exactitud y el área del Tp4.

## Objetivos específicos

1. Calcular, en la grilla común de 20 m, un indicador de cambio por sensor: ΔVH y ΔVV en dB como 10·log₁₀(post/pre) en lineal, ΔHV en banda L, NBR, dNBR y RdNBR.
2. Evaluar, con los datos del sitio, si la caída de VH en banda C y la de HV en banda L se comportan como predice la física de la dispersión en el pajonal y en el albardón, y explicar las discrepancias (humedad, fechas, estructura).
3. Obtener un mapa de quema por sensor con un umbral documentado (Otsu o manual, con su histograma) y comparar los mapas sin fusionarlos, en todo el sitio y por estrato de estructura (CCI Biomass 2020: pajonal < 15 Mg/ha; albardón ≥ 30 Mg/ha) (**sinergia**).
4. Construir y justificar una fusión de decisión C + L con una regla escrita y una fusión de rasgos con Random Forest para la severidad (**fusión**).
5. Validar las cuatro variantes y la severidad con el Tp4, con una referencia independiente de los datos del mapa (Landsat 8) o declarando la dependencia, y decidir, con el IC de la diferencia, si sumar bandas y sensores mejora la exactitud.
6. Usar el cambio de altura GEDI (Δrh98), en la misma estación antes y después, como evidencia estructural independiente, y reconocer dónde el rh98 es el piso del instrumento y no la altura de la vegetación.

## Qué debe entregar

- `A1_quema_por_sensor_20m.tif`, `A1_sinergia_coincidencias.csv` y los histogramas con los umbrales.
- Las cuatro variantes, el mapa de severidad con su figura y la tabla de importancia de variables.
- La tabla de variantes del Tp4 para la clase quemado.
- La tabla `A1_delta_rh98_por_clase.csv`.
- Las respuestas a las preguntas, cada cifra con el archivo del que sale.

## Criterio de evaluación

No se evalúa que la variante multisensor «gane». Se evalúa que el grupo **explique qué ve cada sensor**, que cada umbral esté justificado, que la sinergia y la fusión estén separadas y nombradas, y que la conclusión sobre la mejora no diga más de lo que los intervalos del Tp4 permiten.
