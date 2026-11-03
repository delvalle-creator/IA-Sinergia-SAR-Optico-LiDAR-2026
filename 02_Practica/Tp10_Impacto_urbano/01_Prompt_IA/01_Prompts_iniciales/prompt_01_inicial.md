# Prompt inicial del Tp10 — el que se escribió primero

---

> Tengo Sentinel-1, NovaSAR, NISAR y Sentinel-2 de Concordia. Hacé un mapa de
> crecimiento urbano fusionando todo con Random Forest y calculá la subsidencia
> con InSAR.

---

## Qué produjo

Un script que apilaba las cuatro fuentes, entrenaba un Random Forest con «urbano» y «no urbano», clasificaba 2019 y 2026 y restaba los mapas. Para la subsidencia, un interferograma de dos fechas pasado a milímetros. Corría. Daba dos mapas con colores convincentes.

## Los cinco defectos

**1. Aplicó a 2019 un clasificador que usa sensores de 2023 y 2026.** NovaSAR (2023) y NISAR (2026) no existen en 2019. El script rellenó esas capas con ceros en la fecha de base y clasificó igual. La «expansión» resultante mide sobre todo la aparición de dos sensores, no el crecimiento de la ciudad. Para comparar fechas hace falta el mismo método con los mismos sensores en las dos.

**2. Trató como simultáneas imágenes separadas por tres años.** NovaSAR es del 13/09/2023; Sentinel-1 y NISAR, de septiembre de 2026. Apiladas en un mismo píxel, un barrio construido en 2024 es «urbano» en C y L y «no urbano» en S. El clasificador aprende esa contradicción como si fuera una propiedad del barrio.

**3. Ignoró que NovaSAR cubre el 39 % del sitio.** Donde no hay banda S, el script puso 0 dB… o cero lineal, que en dB es −∞. El Random Forest aprendió que «sin dato» es una clase. El mapa tiene un borde recto donde termina la escena.

**4. Promedió el radar en dB y mezcló σ⁰ con γ⁰ sin decirlo.** Remuestreó NovaSAR de 6 a 10 m promediando decibeles, lo que sesga hacia valores bajos. Y NovaSAR es σ⁰, mientras Sentinel-1 RTC y NISAR GCOV son γ⁰: una diferencia artificial entre sensores que entra al clasificador como señal.

**5. Llamó «subsidencia» a un solo interferograma sin referencia.** Un par aislado mezcla deformación, atmósfera y la constante arbitraria del desenrollado. Sin una zona estable de referencia ni puntos de control, el mapa de milímetros no tiene cero: cualquier valor es posible.

## La lección

El prompt pedía «fusionar todo». El script obedeció: fusionó fechas, sensores ausentes y unidades distintas. **Fusionar exige misma grilla, fechas compatibles y los mismos sensores en las fechas que se comparan.** Cuando no se cumple, lo que corresponde es sinergia o fusión de decisión, y decirlo.
