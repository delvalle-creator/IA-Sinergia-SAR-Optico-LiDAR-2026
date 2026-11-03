# Qué contestó la IA, y qué había que mirarle

## La respuesta

Un script ordenado: búsqueda STAC de Sentinel-2, `NDVI < 0.3` como suelo
desnudo, lectura de NovaSAR con `rasterio`, `10*log10(DN)`, desvío en ventana de
7 × 7 con `scipy`, `RandomForestClassifier` y `classification_report`. Al final,
un GeoTIFF y una tabla de exactitud.

## Lo que había que detectar

**`10*log10(DN)` en lugar de `DN²/1E+05`.** Los DN de NovaSAR son amplitud; la
potencia es su cuadrado, y la calibración del producto divide por la constante
del `metadata.xml`. El logaritmo del DN, sin elevar al cuadrado, ni siquiera
está en la escala de potencia.

**La escena de Sentinel-2 era la del catálogo con menos nubes de la tesela**, no
la de menos nubes en el sitio. El catálogo informa la nubosidad de los
110 × 110 km de la tesela; el sitio puede estar cubierto aunque la tesela no.
Hay que contar con la SCL dentro del sitio.

**Reflectancias de 2023 sin descontar el +1000.** Desde la línea de base 04.00
(25/01/2022) los DN de L2A traen un desplazamiento de 1000. Sin descontarlo, el
NDVI de 2023 no es comparable con el de 2021.

**Sin desplazamiento de NovaSAR.** El script no lo mencionaba.

**`classification_report` sobre los mismos píxeles de entrenamiento.**

## Cómo se detectó

**Mirando el mapa sobre la imagen.** Los «focos de erosión» coincidían con lotes
enteros recién labrados, con bordes rectos. Las cárcavas reales, sinuosas y
estrechas, no aparecían. Y en la capa de NovaSAR, los alambrados quedaban 8
píxeles al este de los de Sentinel-2.

## La regla

**Si el foco de erosión tiene la forma de un lote, está midiendo la labranza.**
La erosión sigue el agua, no el alambrado.
