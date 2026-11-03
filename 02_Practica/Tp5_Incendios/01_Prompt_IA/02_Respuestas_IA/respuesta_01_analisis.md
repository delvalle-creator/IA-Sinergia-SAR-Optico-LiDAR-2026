# Qué contestó la IA, y qué había que mirarle

## La respuesta

Un flujo completo y prolijo: `rasterio.warp.reproject` con `Resampling.bilinear`
para todo, `np.stack` de quince bandas, `train_test_split` y
`RandomForestClassifier`. Un mapa binario, una matriz de confusión y un
reporte de clasificación.

## Lo que había que detectar

**Las bandas de radar venían en dB desde el principio.** El producto RTC se
convertía a dB al leerlo, y después se remuestreaba y se restaba. Un parámetro
de conversión fuera de lugar; el script corre igual.

**`Resampling.bilinear` para el mosaico ALOS-2.** Al pasar de 25 m a 10 m, cada
píxel de banda L se replica suavizado en seis píxeles: el modelo ve detalle
inexistente y lo aprovecha para ajustar el entrenamiento.

**La referencia y el entrenamiento eran lo mismo.** `train_test_split` sobre
puntos derivados del dNBR: el 30 % de prueba son vecinos del 70 % de
entrenamiento, y todos dicen lo que el dNBR dice.

**No había mapa por sensor.** Ni histogramas, ni umbrales, ni tabla de
acuerdo. Imposible saber qué aportó cada banda.

## Cómo se detectó

**Mirando la importancia de las variables.** El dNBR se llevaba casi toda la
importancia. Lógico: la clase se había definido con el dNBR. El modelo había
aprendido a reproducir el umbral, no a detectar quema.

**Y mirando las lagunas.** En el mapa, varias lagunas permanentes de las islas
aparecían como quemadas. Ninguna laguna se quema.

## La regla

Si la referencia sale de una de las variables del modelo, el modelo aprende
esa variable. **Primero cada sensor por separado (sinergia), después la fusión,
y la exactitud siempre con una referencia que no esté en el modelo.**
