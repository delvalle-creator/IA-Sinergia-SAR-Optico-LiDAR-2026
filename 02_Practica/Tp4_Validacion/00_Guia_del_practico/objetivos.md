# Tp4 — Objetivos

## Objetivo general

Validar un mapa con una referencia independiente, estimar su exactitud y el área de cada clase con su intervalo de confianza, y comparar dos versiones de un mapa por la diferencia estimada con su intervalo. La decisión de si una variante multisensor mejora a una de un solo sensor se toma en cada práctico específico (Tp5 a Tp10) con estas herramientas.

## Objetivos específicos

1. Generar un mapa de cobertura de control con fuentes que no son las imágenes evaluadas (digitalización propia, JRC, MapBiomas) y declarar de dónde sale cada píxel.
2. Diseñar un muestreo aleatorio estratificado por clase del mapa y calcular el tamaño de muestra con la ecuación 13 de Olofsson et al. (2014).
3. Etiquetar la referencia **al azar** en QGIS, sin ver el mapa evaluado ni la llave, con un protocolo de respuesta escrito (definición operativa de cada clase), registrando la fuente, la fecha cuando la fuente la tiene (o «sin fecha») y la confianza de cada punto, y medir el acuerdo entre dos intérpretes.
4. Calcular la matriz de error en conteos y en proporción de área, la exactitud global, la del usuario y la del productor, con su IC del 95 %.
5. Estimar el área de cada clase con el estimador estratificado y compararla con el área que dice el mapa contando píxeles.
6. Calcular la diferencia entre dos estimaciones con su IC del 95 % (d = O₁ − O₂, V(d) = V₁ + V₂) y el tamaño de muestra necesario para detectar una diferencia dada; en el ensayo, el mapa de control con y sin el recorte de copas.

## Qué debe entregar

- El mapa de control y su tabla resumen por clase y fuente.
- El GeoPackage de puntos etiquetados, completo, y la llave.
- La tabla `<NOMBRE>_exactitud_y_area.csv` de cada mapa validado y la `tabla_de_variantes_<clase>.csv` de cada práctico específico.
- Las bitácoras de `05_Resultados/06_Control_calidad/`.
- Las respuestas a las preguntas, cada cifra con el archivo del que sale.

## Criterio de evaluación

No se evalúa que la exactitud sea alta. Se evalúa que **sea creíble**: muestra aleatoria y estratificada, etiquetado al azar, referencia independiente de lo evaluado, intervalos informados y una conclusión que no diga más de lo que la muestra permite. Una exactitud de 0,95 sin intervalo, o calculada con los polígonos de entrenamiento, vale menos que una de 0,80 bien hecha.

## Objetivos de aprendizaje

1. Mantener la población, la leyenda y la muestra sin exclusiones posteriores al resultado: el punto de una clase que el mapa no tiene entra como error.
2. Calcular la exactitud y el área ponderadas por estrato con su incertidumbre de muestreo, y distinguirlas de los conteos de puntos y de píxeles.
3. Comparar dos mapas o variantes por la diferencia estimada con su intervalo, no por el solapamiento de los intervalos de cada uno.
4. Escribir y aplicar un protocolo de respuesta, y medir con él el acuerdo entre intérpretes de la referencia.
5. Diseñar una muestra (estratos, n por estrato y justificación) para un mapa propio con varias variantes.
