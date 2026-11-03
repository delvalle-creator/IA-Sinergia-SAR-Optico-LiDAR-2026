# Qué contestó la IA, y qué había que mirarle

## La respuesta

Un `rasterio.warp.reproject` por capa con `resampling=Resampling.bilinear` a una grilla
de 10 m, un `scipy.interpolate.griddata` para las huellas GEDI y un `np.stack`. Para el
corregistro, una línea: «las capas comparten CRS y transformación, por lo tanto están
alineadas». Todo correcto en su sintaxis, y el cubo no cumplía ninguno de los tres
requisitos de la fusión o no los había medido.

## Lo que había que detectar

**`Resampling.bilinear` para agregar.** Para pasar a un píxel más grueso se usa
`average` sobre el radar en lineal y sobre las reflectancias, y `mode` sobre la SCL
(una clase no se promedia). `bilinear` sólo para llevar un píxel igual o más grueso a
uno más fino, en variables continuas, y declarándolo.

**El píxel de 10 m fijo.** El píxel sale de un argumento (`--pixel`, 20 m por defecto)
y la bitácora declara la regla: el más grueso del análisis.

**La frase «comparten CRS, por lo tanto están alineadas».** Compartir la grilla es
condición necesaria, no suficiente. Una NovaSAR georreferenciada con cuatro puntos de
esquina comparte la grilla después de reproyectarla y puede estar corrida cientos de
metros. El corregistro **se mide**: correlación de fase sobre mapas de bordes, por
ventanas, con mediana y dispersión.

**Comparar valores en lugar de bordes.** Una correlación directa entre la reflectancia
del infrarrojo y γ⁰ no tiene por qué dar un máximo nítido: los dos sensores miden cosas
distintas. Los bordes (costas, caminos, límites de lotes) sí coinciden.

**`griddata` sobre las huellas.** Se reemplaza por la extracción inversa: para cada
huella válida, la media de los píxeles del cubo dentro de su radio (12,5 m para GEDI,
50 m para ATL08, más medio píxel), con el número de píxeles y los días de diferencia.

**Alturas sin referencia vertical.** La IA sumaba `elev_lowestmode` de GEDI y el
Copernicus DEM en la misma tabla. La primera es elipsoidal; el segundo, sobre el geoide
EGM2008. En Entre Ríos la diferencia ronda los 15 m, y no se ve a simple vista.

## Cómo se detectó

**Con NovaSAR en Bovril.** Superpuesta a Sentinel-2 en QGIS, los caminos y los bordes
de los lotes de la NovaSAR 47974 no caían sobre los del óptico. El cubo «alineado» no
lo estaba. En la presentación 02, esa escena necesitó desplazarse unos 80 m al oeste y
20 m al norte para corregistrar con Sentinel-2: varios píxeles, en un cubo que «compartía
la grilla».

## La regla

Misma grilla no es mismo lugar. Lo que no se midió no se puede afirmar.
