# Glosario del curso

**Banda (radar).** Intervalo de longitudes de onda. En el curso: X (≈ 3,1 cm,
COSMO-SkyMed), C (5,5 cm, Sentinel-1), S (9,4 cm, NovaSAR-1 y NISAR-S), L (≈ 24
cm, ALOS, SAOCOM y NISAR-L) y P (≈ 70 cm, BIOMASS). Cuanto más larga la onda,
más penetra en el dosel y en el suelo seco.

**Bitácora.** Archivo `.log` que escribe cada programa en
`05_Resultados/06_Control_calidad`: qué hizo, con qué datos, cuántos entraron y
salieron, y el paso siguiente.

**Coherencia interferométrica.** Medida (0 a 1) de cuánto se parece la fase de
dos adquisiciones del mismo lugar. Baja con la vegetación que se mueve, el agua,
el cambio de la superficie y el tiempo entre tomas.

**Convergencia (grado de).** Cuántos sensores tienen dato útil cerca de la
fecha del evento: completa, parcial, un solo sensor o histórica (Tp1).

**Corregistro.** Que el mismo punto del terreno caiga en el mismo píxel en todos
los sensores. Se mide en el Tp3; debe ser menor que un píxel para fusionar.

**Doble rebote.** Retorno fuerte del radar cuando la onda pega en una superficie
horizontal y luego en una vertical (calle y pared, agua y tronco). Marca
ciudades y bosques inundados.

**Exactitud de usuario / de productor.** De usuario: de lo que el mapa dice que es
la clase, qué fracción lo es (1 − comisión). De productor: de lo que en la
realidad es la clase, qué fracción el mapa encontró (1 − omisión).

**Fusión.** Combinación de datos de varios sensores en un único producto por
medio de un algoritmo. Niveles: **píxel** (los valores originales entran juntos),
**rasgo** (entran variables derivadas, como ΔVH o ΔNDVI) y **decisión** (cada
sensor decide y una regla escrita combina: unión, intersección, mayoría). Un
Random Forest que recibe bandas, índices y texturas es fusión de **rasgo**, no de
píxel. Comparar dos mapas del mismo método en fechas distintas (como la
expansión urbana del Tp10) no es fusión de decisión sino detección de cambios
posterior a la clasificación: se comparan fechas, no se fusionan sensores.

**γ⁰ (gamma cero).** Coeficiente de retrodispersión normalizado por el área
iluminada en el plano perpendicular a la mirada. Con corrección radiométrica del
terreno (terrain flattening) quita buena parte del efecto del relieve.

**GCOV.** Producto de NISAR con la matriz de covarianza polarimétrica ya
geocodificada (HHHH, HVHV, …), en γ⁰ lineal.

**InSAR.** Interferometría radar: la diferencia de fase entre dos tomas da el
desplazamiento del terreno en la línea de visión, d = −λ·φ / (4π).

**LOS (line of sight).** Línea de visión del satélite. InSAR mide el desplazamiento
en esa dirección, no el vertical.

**Muestreo estratificado.** Diseño de muestra en el que cada clase del mapa es un
estrato con su propio número de puntos. Con el estimador de Olofsson et al.
(2014) da exactitudes y superficies con intervalo de confianza.

**NDBI, NDVI, MNDWI, NBR.** Índices normalizados de Sentinel-2: construido
(B11, B08), vegetación (B08, B04), agua (B03, B11) y área quemada (B08, B12).

**rh98.** Altura relativa a la que se acumula el 98 % de la energía del pulso de
GEDI: aproxima la altura del dosel.

**RTC.** Radiometric Terrain Correction: producto radar en γ⁰ con la corrección
del relieve aplicada.

**σ⁰ (sigma cero).** Coeficiente de retrodispersión normalizado por el área en
el plano del terreno. No corrige el relieve.

**SBAS.** Small BAseline Subset: serie InSAR con muchos pares de línea de base
corta para estimar la velocidad de deformación.

**Sinergia.** Interpretación conjunta de los resultados de varios sensores, cada
uno por separado. Ocurre en el razonamiento; puede existir sin fusionar datos.

**Speckle (moteado).** Variación aleatoria de la intensidad del radar por la
suma coherente de muchos dispersores en un píxel. No es ruido del instrumento:
se reduce promediando.

**Umbral documentado.** Valor de corte acompañado de su histograma y de la
justificación de por qué se eligió.

**Variante.** Cada versión de un mapa hecha con distintos datos (sólo óptico,
sólo banda C, multisensor…). El Tp4 las valida a todas igual para saber qué
aportó cada sensor.
