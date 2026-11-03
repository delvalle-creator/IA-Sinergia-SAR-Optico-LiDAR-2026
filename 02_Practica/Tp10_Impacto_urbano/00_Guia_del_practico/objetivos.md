# Tp10 — Objetivos

## Objetivo general

Mapear el crecimiento urbano de Concordia entre 2019 y 2026 y la velocidad vertical del terreno en Paraná – Diamante, combinando radar en bandas C, S y L con óptico, **distinguiendo en cada paso qué es sinergia y qué es fusión**, y declarar, para cada mapa, qué controles independientes tiene y cuáles le faltan.

## Objetivos específicos

1. Explicar el doble rebote urbano en cada banda (C, S, L) y por qué depende de la orientación de las calles respecto de la dirección de vuelo.
2. Producir un mapa urbano por banda con un umbral documentado en su histograma, y compararlos **sin fusionarlos** (sinergia).
3. Medir cuánto detalle urbano se pierde al pasar de 6 a 10 y a 20 m.
4. Armar un entrenamiento **en proporción al paisaje** con los píxeles estables de MapBiomas, revisarlo sobre la imagen y explicar por qué un entrenamiento con el mismo número de ejemplos por clase marca ciudad de más.
5. Construir con compuestos de temporada una fusión de rasgos (Random Forest con bandas, índices y textura) en cinco variantes que cambian sólo los sensores (óptico, C, C + L, multisensor y multisensor con S), y explicar con la cobertura de NovaSAR por qué la versión con S es aparte.
6. Calcular la expansión urbana 2019 → 2026 clasificando **cada año por separado con el mismo método** y comparando después (detección de cambios por comparación posterior a la clasificación), con la clase «sin decidir» a la vista.
7. Estimar la velocidad vertical del terreno por apilado de interferogramas, con una zona de referencia estable declarada y puntos de control que no se usaron como referencia.
8. Validar las variantes del mapa urbano con el Tp4 (al menos 50 puntos por estrato), afirmar una mejora sólo si el IC del 95 % de la diferencia no incluye el cero, y comunicar cada mapa con su fecha, su fuente y su incertidumbre.
9. Diseñar una muestra con un estrato de borde urbano (franja de 1 km) y mostrar cuánto se achica el intervalo de confianza del área.

## Qué debe entregar

(Las tablas y los mapas van dentro del PDF de respuestas; los dos mapas finales, en PDF aparte. Ver `07_Preguntas_y_entrega/00_LEEME_que_va_aqui.md`.)

- La tabla de coincidencias entre bandas, con la interpretación física de cada diferencia.
- La tabla de detalle a 6, 10 y 20 m, comentada.
- La tabla del entrenamiento (píxeles por clase) y el resultado de la revisión de 60 puntos sobre la imagen (cuántos «mal» en cada clase, con ejemplos).
- La superficie urbana de cada variante comparada con MapBiomas, la tabla de importancias y los mapas de clases `sin_S` y `con_S`.
- El mapa de expansión urbana 2019 → 2026 con sus cinco clases y su tabla de superficies.
- El mapa de velocidad vertical, la zona de referencia y el resultado del control en puntos estables.
- La fila del Tp10 en la tabla de variantes del Tp4 (exactitud con intervalo de confianza).
- La tabla D de verificación completa, con «¿Cumple?» y un comentario en cada control que falla.
- La bitácora de IA: prompt, respuesta, corrección humana y verificación.

## Criterio de evaluación

No se evalúa que el mapa «se vea bien», sino **que cada decisión esté declarada y controlada**: el umbral con su histograma, la proporción del entrenamiento, las fechas de los compuestos, el nivel de fusión con su justificación, la zona de referencia de la subsidencia y la exactitud medida con una referencia independiente. Un control que falla y se declara vale más que un mapa sin control.
