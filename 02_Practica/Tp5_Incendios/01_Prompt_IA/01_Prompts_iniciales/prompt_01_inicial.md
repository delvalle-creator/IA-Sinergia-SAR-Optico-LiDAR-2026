# Prompt inicial del Tp5 — el que se escribió primero

---

> Hacé un mapa de áreas quemadas del Delta en 2020 combinando Sentinel-1,
> Sentinel-2 y ALOS-2 con un Random Forest, y dame la exactitud.

---

## Qué produjo

Un script que bajaba Sentinel-1 en dB, apilaba VV y VH en dB de dos fechas con
las bandas de Sentinel-2 y el mosaico ALOS-2 remuestreado a 10 m, entrenaba un
Random Forest con puntos tomados de un mapa de dNBR > 0,27 y daba como
exactitud la de una partición 70/30 de esos mismos puntos. Corría. El mapa se
veía razonable y la exactitud era alta.

## Los cinco defectos

**1. Promedió y restó en dB.** El remuestreo del radar se hizo sobre dB y el
cambio se calculó restando dB de escenas remuestreadas. El promedio de los
logaritmos no es el logaritmo del promedio: el remuestreo en dB sesga hacia
valores bajos. El cambio se calcula como 10·log₁₀(post/pre) con cada lado en
γ⁰ lineal.

**2. Llevó el mosaico ALOS-2 de 25 m a 10 m.** El remuestreo bilineal fabricó
un detalle que la banda L nunca vio. Y no dijo que el mosaico anual mezcla
pasadas de varios meses: en parte del sitio la imagen «posterior» puede ser
anterior a las quemas.

**3. No separó sinergia de fusión.** Metió todo en un modelo. Nunca preguntó
qué ve cada sensor: no hay forma de saber, con ese resultado, si la banda L
aportó algo o si el modelo usó sólo el dNBR. La pregunta del práctico (por qué
difieren el pajonal en C y el albardón en L) quedó sin respuesta.

**4. La referencia era el dNBR y la exactitud era de entrenamiento.** Los
puntos «verdaderos» salieron de un umbral de dNBR (que además es de bosques
templados de Norteamérica, no de humedales) y la exactitud se calculó con
puntos del mismo conjunto. Es exactitud inflada por construcción.

**5. Las lagunas salían quemadas.** El agua calma es oscura en el radar y en
el SWIR, igual que la ceniza. Sin una máscara de agua permanente, las lagunas
de las islas entraban como quema.

## La lección

El prompt pedía «combinar con un Random Forest». La IA lo hizo. Lo que faltaba
era preguntar **qué responde cada sensor**, mirarlo por separado antes de
combinar, y validar con una referencia que no salga de los datos combinados.
