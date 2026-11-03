# Qué contestó la IA, y qué había que mirarle

## La respuesta

Un script prolijo: `numpy.random.choice` sobre todos los píxeles válidos,
`sklearn.metrics.confusion_matrix`, `cohen_kappa_score` y un `print` con el
área quemada = píxeles × 0,04 ha. Todo funciona. La exactitud global daba alta.

## Lo que había que detectar

**La exactitud global alta era de la clase grande.** En un sitio donde casi
todo es “no quemado”, un mapa que no marque nada tiene una exactitud global
altísima. Había que mirar la exactitud del usuario y del productor de la clase
**quemado**, y su número de puntos. Tenía muy pocos.

**La referencia era el dNBR.** La columna “verdad” se calculaba con el mismo
tipo de umbral automático que se quería evaluar. Si se evaluaba la variante
óptica, el acuerdo era casi perfecto por construcción.

**El área era la del mapa.** Ni estimador, ni intervalo. Y la matriz se
armaba en conteos de puntos, no en proporción de área: con muestreo
estratificado eso es un error, porque cada punto representa superficies
distintas según su estrato.

**No había llave ni etiquetado.** La referencia no la miraba nadie: no había
interpretación, por lo tanto no había sesgo de confirmación que evitar… ni
validación.

## Cómo se detectó

**Con una prueba conocida.** Se le pasó al estimador el ejemplo publicado por
Olofsson et al. (2014). Con la matriz publicada, calcular en conteos da una
exactitud global de 0,917 (587 aciertos en 640 puntos) y una exactitud del
productor para deforestación de 0,957 (66 de 69); el área, contando píxeles,
queda en 18 000 ha. Ninguna de las tres cifras es la del artículo. El estimador correcto
(hoy `Tp4_03 --autoprueba`) da 21 158 ± 6 158 ha, usuario 0,88, productor 0,75
y global 0,95, que son las cifras publicadas.

**Y con un mapa vacío.** Un mapa sin ningún píxel quemado obtenía con el
script ingenuo una exactitud global alta. Un procedimiento de validación que
aprueba un mapa vacío no está validando.

## La regla

Antes de creer una exactitud, pregunte tres cosas: **cómo se eligieron los
puntos, de dónde salió la referencia y si quien etiquetó veía el mapa**. Y
antes de usar un estimador, hágale reproducir un ejemplo publicado.
