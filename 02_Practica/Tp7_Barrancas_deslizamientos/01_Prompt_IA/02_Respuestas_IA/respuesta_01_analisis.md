# Qué contestó la IA, y qué había que mirarle

## La respuesta

Un script prolijo: leía `Unw_Phase_ifg_*` del `.data` de SNAP, aplicaba
`d = λ · fase / (4π)`, bajaba con `asf_search` el primer par Sentinel-1 que
encontraba, pedía el interferograma a HyP3, promediaba los dos desplazamientos y
escribía un GeoTIFF. Para el volumen, `dZ = IGN − GLO-30` y la suma de los
negativos. Todo con buenos nombres de variables y comentarios.

## Lo que había que detectar

**El histograma de la banda X era un solo valor.** El script no miraba el
contenido de lo que leía. Una banda con mínimo = máximo = 0 se procesó como
cualquier otra. El script del curso (`Tp7_02`) comprueba que el máximo absoluto
no sea cero y, si lo es, lo dice en la bitácora y usa sólo la coherencia.

**El signo de la conversión.** `Phase to Displacement` de SNAP usa
`d = −λ · fase / (4π)`. Con el signo cambiado, un hundimiento aparece como
levantamiento. Hay que usar la misma convención en todos los productos, o
comprobar la de cada uno.

**La fecha del par C.** El primer par que devolvió la búsqueda era de 2024. El
script no comparaba fechas con las del par X.

**El promedio de LOS.** La IA promedió desplazamientos de dos satélites como si
midieran lo mismo. No hay promedio posible: hay, a lo sumo, una regla de
decisión («las dos bandas coinciden») que además exige la misma geometría.

**La resta de MDE sin referencia.** No había zona estable, ni sesgo, ni ruido,
ni umbral de detección.

## Cómo se detectó

**Mirando los datos, no el código.** En SNAP, `Analysis > Statistics` sobre la
banda `Unw_Phase` daba cero en todo. En QGIS, el «mapa de deformación» era
exactamente el desplazamiento de la banda C dividido por dos. Y la tabla de
volúmenes daba la misma cifra para la cicatriz que para un lote vecino.

## La regla

**Antes de interpretar una banda, mire su histograma.** Si un resultado sale
igual en la barranca y en el campo de al lado, no está midiendo la barranca.
