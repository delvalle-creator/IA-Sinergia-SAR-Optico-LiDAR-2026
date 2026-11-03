# Qué contestó la IA, y qué había que mirarle

## La respuesta

Un script corto: `vv_db < -15`, `ndwi > 0`, `np.logical_or`, `sum() * 0.01` ha
por píxel de 10 m. Profundidad = `cota_rio - mde`, con `cota_rio` igual al
mínimo del MDE sobre el cauce.

## Lo que había que detectar

**El umbral era una constante del código.** No salía de los datos ni de un
histograma. Un número escrito a mano en el código, sin comentario, es una
decisión que nadie tomó a conciencia.

**`ndwi > 0` con cualquier píxel.** No había máscara de nubes (SCL). Las nubes
y sus sombras no se excluían: el óptico votaba también donde no veía el suelo.

**No había JRC ni ninguna máscara de agua permanente.** El río entraba entero.

**`cota_rio` era un solo número.** Para todo el sitio. El agua tiene pendiente a
lo largo del río, y la mancha de una crecida no tiene un único nivel.

**El MDE no se controlaba.** No había ninguna comparación con alturas de terreno
independientes; ni conversión entre alturas elipsoidales y sobre el geoide.

## Cómo se detectó

**Mirando el mapa sobre el embalse.** La mitad de la «inundación» era el lago de
Salto Grande. Y una parte del embalse, rizada por el viento, aparecía como
tierra seca: el agua con olas es brillante en VV.

**Y mirando la profundidad bajo el monte.** Los valores más altos estaban en las
islas con monte en galería, no en los bajos. Eso no es agua profunda: es la copa
de los árboles en un modelo de superficie.

## La regla

Antes de medir la crecida, saque **el agua que siempre está**. Antes de sumar
sensores, escriba **la regla** y diga qué hace cada uno con las nubes. Y antes de
creerle una profundidad al MDE, **compárelo con el terreno** de otro sensor, en
la misma referencia vertical.
