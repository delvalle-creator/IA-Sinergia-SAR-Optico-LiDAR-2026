# Qué contestó la IA, y qué había que mirarle

## La respuesta

Una búsqueda STAC correcta en su sintaxis: `collections=["sentinel-2-l2a"]`,
`bbox` del sitio, `datetime` de la ventana y `query={"eo:cloud_cover": {"lt": 20}}`.
Para el radar, una búsqueda en ASF por `intersectsWith` y una tabla con la columna
«cobertura» calculada como intersección de la huella con el rectángulo. Para GEDI,
un bucle de reintentos. Todo estándar, todo bien escrito, y la tabla final mezclaba
escenas verificadas con escenas que sólo rozaban el sitio.

## Lo que había que detectar

**El filtro `eo:cloud_cover < 20` estaba ANTES de mirar el sitio.** Un parámetro. El
script corre igual, pero descarta escenas buenas y conserva escenas malas. La
corrección es contar la nubosidad dentro del sitio con la SCL (clases 4, 5, 6, 7 y
11 válidas) e informar las dos cifras, una al lado de la otra. El filtro de catálogo
puede quedar, pero sólo como atajo para no leer escenas inútiles (`--nubes_max`, por
defecto 80), nunca como criterio de selección.

**La columna «cobertura» era la de la huella.** Se llamaba igual que la cobertura
real. Hay que separar `cobertura_huella_%` de `pixeles_validos_%` y, cuando no se
puede medir la segunda (productos de ASF todavía no bajados), dejarla vacía. Un
número que no se midió no se escribe.

**En NISAR no aplicaba la máscara del producto.** Sin la máscara (0 = inválido,
255 = fuera de la adquisición), el borde de la franja entra con valores del orden de
−133 dB, que no son agua ni sombra: son muestras inválidas. Con ellas, cualquier
conteo de «píxeles con dato» infla la cobertura y cualquier promedio se hunde.

**Las fechas no eran UTC de los metadatos.** En NovaSAR la fecha va del
`RawDataStartTime` del `metadata.xml`; en NISAR, del `zeroDopplerStartTime`; en STAC,
del `datetime` del ítem. La hora UTC importa: una escena de las 01:36 UTC es de la
noche anterior en hora argentina.

## Cómo se detectó

**Abriendo una escena «útil» en QGIS sobre el sitio.** La primera NovaSAR de la lista
cubría menos de la mitad de Concordia; la tabla decía «sirve». Y la nubosidad: una
escena descartada por 35 % de nubes de catálogo tenía el sitio despejado; la máscara
SCL recortada al sitio lo mostraba en segundos.

## La regla

Lo que dice el catálogo es una hipótesis. Se verifica dentro del sitio, con el dato.
