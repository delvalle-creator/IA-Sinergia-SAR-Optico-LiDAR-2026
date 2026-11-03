# Prompt inicial del Tp4 — el que se escribió primero

---

> Tengo un mapa de áreas quemadas del Delta hecho con Sentinel-1. Calculá la
> exactitud con una matriz de confusión y decime cuántas hectáreas se quemaron.

---

## Qué produjo

Un script que tomaba 500 puntos al azar en todo el sitio, les asignaba como
referencia el valor del dNBR de Sentinel-2 (quemado si dNBR > 0,27), armaba la
matriz de confusión y calculaba el kappa. El área quemada la sacaba contando
píxeles del mapa. Corría. Daba una exactitud global alta y una cifra de hectáreas sin intervalo.

## Los cinco defectos

**1. Muestreo aleatorio simple en todo el sitio.** El área quemada es una
fracción chica del Delta. Con 500 puntos al azar, a la clase quemado le tocan
unos pocos: la exactitud del usuario y la del productor de esa clase, que son
las que importan, quedan con intervalos enormes o directamente sin calcular. El
muestreo se estratifica por clase del mapa para asegurar puntos en la clase rara.

**2. La referencia salía de otro mapa automático.** Comparar Sentinel-1 con un
umbral de dNBR no es validar: es medir el acuerdo entre dos mapas, ninguno de
los cuales es la verdad. Si los dos se equivocan igual (lagunas oscuras en el
radar y en el óptico), el acuerdo sube y el error queda escondido. La
referencia se interpreta sobre imágenes que **no** son las evaluadas.

**3. El área salía de contar píxeles del mapa.** El área de un mapa con
omisión y comisión no es el área real. Con una muestra estratificada se estima
el área de cada clase con su intervalo de confianza (Olofsson et al., 2014). El
conteo de píxeles se informa al lado, como lo que “dice” el mapa.

**4. No había intervalos de confianza.** Una exactitud sin intervalo no
permite comparar variantes: no se sabe si 0,91 contra 0,88 es una diferencia o
es la muestra.

**5. Kappa como resumen.** Kappa no agrega información a la exactitud global
para estimar área y su comparación con un acuerdo “al azar” no responde
ninguna pregunta de la emergencia. Se informan exactitud global, del usuario y
del productor, con sus intervalos.

## La lección

El prompt pedía «la exactitud». La IA devolvió **un número**. Lo que hacía
falta era **un diseño**: cómo se eligen los puntos, de dónde sale la
referencia, quién la etiqueta sin ver el mapa y con qué estimador se pasa de la
muestra al área.
