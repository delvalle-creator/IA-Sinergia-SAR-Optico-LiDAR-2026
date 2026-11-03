# Qué contestó la IA, y qué había que mirarle

## La respuesta

Un script que abría los tres productos con `rasterio`, los reproyectaba con
`reproject(..., resampling=Resampling.bilinear)` después de pasarlos a dB, restaba
`HV_2026_dB − HV_2011_dB`, umbralaba en −3 dB y combinaba con
`NDVI_2025 − NDVI_2016 < −0,1`. Explicaba con soltura que «la banda L penetra el
dosel y responde a la biomasa leñosa».

## Lo que había que detectar

**El archivo de 2011 tenía una sola banda.** El nombre del producto lo dice
(`..._FBS_..._HH.tif`). La IA no lo leyó: asumió dos polarizaciones porque las
otras dos fechas las tenían.

**Paso a dB antes de remuestrear.** El remuestreo bilineal de dB promedia
logaritmos. Para agregar SAR se promedia potencia en lineal; el dB se calcula al
final y sólo para mirar o umbralizar.

**ALOS-2 mosaico en números digitales.** El mosaico de JAXA viene en DN. La
conversión publicada es γ⁰ [dB] = 10·log10(DN²) − 83. La IA lo trató como γ⁰.

**NISAR sin máscara.** En los bordes de la pasada, sin la máscara del producto
(0 = inválido, 255 = fuera de la adquisición), aparecen valores de −133 dB que
entraron como «pérdida total».

**Ninguna zona estable.** No había calibración cruzada ni medida del desfase.

## Cómo se detectó

**Mirando la diferencia en un lugar que no cambió.** En el casco urbano de
Federal y en un monte que el historial de imágenes muestra intacto desde 2011, la
«pérdida» daba varios dB. Una ciudad no se deforesta. Y en el borde del NISAR,
una franja recta de «desmonte total» seguía la traza de la órbita.

## La regla

**Antes de interpretar un cambio entre sensores, mídalo donde no hubo cambio.**
Si en la zona estable la diferencia no es cero, eso es calibración, no monte.
