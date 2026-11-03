# Qué contestó la IA, y qué había que mirarle

## La respuesta

Un grafo correcto en su forma: `Read → Apply-Orbit-File → Calibration → Speckle-Filter
→ Terrain-Correction → LinearToFromdB → Write (GeoTIFF)`. Y un script de Python con
`rasterio.warp.reproject(..., resampling=bilinear)` sobre las bandas en dB, un
`np.stack` y un `np.mean` por clase. Todo estándar, todo documentado, y la pila
resultante no servía para comparar bandas.

## Lo que había que detectar

**`outputSigmaBand=true` y sin `Terrain-Flattening`.** Un parámetro. El grafo corre y
el producto se ve bien. Pero queda en σ⁰ mientras NISAR viene en γ⁰. Lo correcto:
`outputBetaBand=true` y después `Terrain-Flattening` con el Copernicus DEM, como en
`09_Grafos_SNAP/Tp2_S1_GRD_a_gamma0.xml`.

**`LinearToFromdB` dentro del grafo, antes de escribir.** El producto se guardaba en
dB como banda física. Lo correcto es guardar lineal y agregar el dB como **banda
virtual** (`Raster > Data Conversion > Linear to/from dB`), que no reemplaza al dato.

**Escritura en GeoTIFF.** El GeoTIFF pierde los metadatos de SNAP (órbita, calibración,
historia). El producto se guarda en BEAM-DIMAP; el GeoTIFF de una banda se exporta
aparte, sólo para Python.

**`resampling=bilinear` sobre dB.** Para agregar a un píxel más grueso se promedia
potencia (`average` sobre lineal). En NovaSAR, la media cuadrática de los DN (`rms`)
antes de calibrar: rms(DN)² = media(DN²) = media de la potencia.

**Ninguna máscara para NISAR.** El dataset `mask` del GCOV (0 inválido, 255 fuera, 1 a
n válido) no se leía.

**La alineación de la grilla.** El `Terrain-Correction` sin `alignToStandardGrid`
deja los píxeles corridos medio píxel respecto de la grilla del curso. Con
`standardGridOriginX = standardGridOriginY = 5` los bordes caen en múltiplos de 10 m,
igual que la grilla de los demás sensores.

## Cómo se detectó

**Con la zona estable.** El mismo Sentinel-1, procesado por la IA y descargado ya
corregido del Planetary Computer (RTC, γ⁰), no coincidía en el casco urbano. Y el
promedio del pajonal en NISAR bajaba varios dB cuando el polígono tocaba el borde de la
pasada: al abrir el producto en QGIS, el borde era una franja negra de muestras
inválidas.

## La regla

Antes de comparar dos bandas, igualar lo que no es la cubierta: unidad, normalización,
grilla y máscara. Lo que queda, recién ahí, es la cubierta.
