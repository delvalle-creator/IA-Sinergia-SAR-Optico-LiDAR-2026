# Tp6 · Guía paso a paso

Miércoles, 14 a 18 h. Sitio `B_CONCORDIA` (crecida de noviembre de 2023).

Se sigue en orden. Cada paso dice qué se hace y por qué, dónde, la orden o los menús exactos, qué sale en pantalla, cómo saber si salió bien y los errores típicos. Menús de QGIS en español, con el inglés entre paréntesis; menús de SNAP en inglés.

## Antes de empezar

Miniforge Prompt:

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp6_Inundaciones\03_Scripts
```

Compruebe los insumos que el práctico no genera:

```
dir ..\..\Tp4_Validacion\02_Subsets_SNAP_QGIS\B_CONCORDIA_cobertura_control_20m.tif
dir ..\..\Tp1_Convergencia\05_Resultados\03_Vectores\lidar_B_CONCORDIA.gpkg
```

Si falta el primero:

```
python ..\..\Tp4_Validacion\03_Scripts\Tp4_01_cobertura_de_control.py --sitio B_CONCORDIA --pixel 20
```

Si falta el segundo, el paso 6 no se puede hacer: avise al docente.

Deje lista la grilla del geoide (una sola vez por equipo, con red):

```
projsync --file us_nga_egm08_25
```

**Landsat 8 y 9.** Escenas de este práctico, la pasada más cercana a cada Sentinel-2 con el sitio cubierto y despejado: Concordia, `B_CONCORDIA_L8_20231025`: Landsat 8 del 25/10/2023 para el Sentinel-2 del 04/11/2023 (10 días antes de la fecha del umbral; el Landsat 9 del 02/11/2023 pasó con casi todo el sitio nublado).

Son Colección 2, Nivel 2 de USGS (reflectancia y temperatura de superficie, píxel de 30 m), bajadas del Planetary Computer. Están en `02_Subsets_SNAP_QGIS\SNAP_DIMAP` y `QGIS_GeoTIFF`, con las bandas `SR_B1` a `SR_B7` (reflectancia), `ST_B10` (temperatura, K), `ST_QA`, `QA_PIXEL` y las virtuales `NDVI` y `ST_B10_C` (°C).

Landsat 9 da imágenes desde el 31/10/2021; antes sólo hay Landsat 8. Los dos llevan instrumentos gemelos (OLI y TIRS) y se comparan entre sí sin ajuste. Con Sentinel-2 no: el píxel es de 30 m contra 10 y 20 m, y las bandas no coinciden del todo (el infrarrojo cercano de Landsat, 865 nm, equivale a la B8A, no a la B08).

Fuente: USGS / NASA, Landsat 8 y Landsat 9 OLI/TIRS, Colección 2 Nivel 2, distribuido por Microsoft Planetary Computer, https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2

**Fusión Landsat + Sentinel-2.** El Landsat también viene afinado a 10 m con el detalle espacial del Sentinel-2 de la fecha más cercana: se lo interpola a la grilla de 10 m y se le suma el detalle fino de la banda Sentinel-2 de 10 m que más se le parece, escalado por una regresión entre los dos sensores (filtro pasa-altos con modulación por regresión, HPF). Trae las bandas `SR_B1` a `SR_B7` en reflectancia, `mascara_detalle` (1 = se agregó detalle; 0 = nube, sombra o falta de dato en alguna de las dos) y el `NDVI` virtual; el método y la calidad de cada banda están en los metadatos.

El control es el ERGAS: la imagen afinada se lleva de nuevo a 30 m y se compara con el Landsat original; por debajo de 3 la fusión es buena. Sirve para mirar e interpretar, con tres cuidados: un cambio real entre las dos fechas aparece como detalle falso; las bandas 6 y 7 (infrarrojo de onda corta) toman el detalle de una banda de 10 m de otra región del espectro y son las menos confiables; y la temperatura no se afina.

En este práctico: `B_CONCORDIA_L8_20231025_fusion_S2_20231104_10m`: 10 días entre las dos imágenes, con la crecida subiendo en el medio. Es la fusión más débil del curso (ERGAS 1,85; correlación entre los sensores en el visible de 0,5 a 0,8, así que el programa agrega poco detalle): un buen ejemplo de por qué la fusión exige fechas cercanas.

**Pléiades y Pléiades Neo de CONAE.** Referencia visual de muy alta resolución del casco urbano (Pléiades, 0,5 m; Pléiades Neo, 0,3 m), 2022-2023, del proyecto Impactar de CONAE. Es un servicio de mapas y necesita internet: en `02_Subsets_SNAP_QGIS\Pleiades_CONAE_WMS` hay un `.xml` por localidad que se arrastra a QGIS (instrucciones en el `LEEME.md` de esa carpeta). Sirve para mirar y digitalizar, no para calcular: es RGB color real, sin infrarrojo ni reflectancia, y la fecha exacta no está publicada, sólo el año.

En este práctico: Concordia y General Roca, Pléiades Neo 2023 (`Concordia_2023_Pleiades_CONAE.xml`).

Fuente: CONAE, proyecto Impactar; Pléiades y Pléiades Neo, Airbus Defence and Space. Servicio WMS: https://geotematico01.conae.gov.ar/geoserver/wms; catálogo: https://catalogos.conae.gov.ar/catalogo/catalogoGeoServiciosOGC.html

**CBERS-4A, cámara WPM (INPE).** Pancromática de 2 m y multiespectral de 8 m (azul, verde, rojo e infrarrojo cercano), producto L4 ortorrectificado, en números digitales. Cada escena viene en dos productos: `..._MS_8m` (las cuatro bandas originales) y `..._pansharpened_2m` (la pancromática y las cuatro bandas afinadas a 2 m por Brovey ponderado, el método por defecto de GDAL). Es un pansharpening clásico: pancromática y multiespectral del mismo satélite y del mismo instante; compárelo con la fusión Landsat + Sentinel-2, que combina dos sensores y dos fechas. El control es el mismo ERGAS (por debajo de 3, bueno). Los números digitales no son reflectancia y el Brovey altera la radiometría: sirve para mirar y digitalizar, no para calcular índices. Cubre una zona de 12 a 21 km, no el sitio entero, y la escena se eligió a ojo, sin nubes, porque el catálogo del INPE no informa la nubosidad.

En este práctico: no hay escena: ninguna pasada a 120 días cubre Concordia despejada en 2023.

**Embeddings anuales AlphaEarth Foundations (Google y Google DeepMind).** 64 números por píxel de 10 m que resumen un año entero de Sentinel-1, Sentinel-2, Landsat, GEDI, clima y otras fuentes, aprendidos por un modelo de inteligencia artificial. Las dimensiones (`A00` a `A63`) no tienen significado físico propio: sirven para clasificar con pocas muestras, buscar zonas parecidas y detectar cambios entre años. Vienen en enteros de 8 bits tal como los entrega Google (`..._AlphaEarth_embeddings_<año>_10m`); para pasarlos a valores reales, valor = signo(DN) × (DN / 127,5)², y −128 es sin dato. El `..._CP1_CP2_CP3_RGB_8bit.tif` muestra las tres primeras componentes principales para mirar en QGIS; sus colores no tienen significado fijo. Resumen un año, no una fecha; 2026 todavía no existe y se usa 2025, el último.

En este práctico: Concordia, 2023.

Fuente: The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind (CC BY 4.0). Copia en Source Cooperative (Taylor Geospatial), https://source.coop/tge-labs/aef

---

## Paso 1 · Serie de agua abierta en banda C — SE CORRE

**Qué y por qué.**

- **Una sola órbita relativa** (la más frecuente en la ventana, o la que se fije con `--orbita`). Mezclar órbitas mezcla ángulos de incidencia y direcciones de mirada: el mismo lote se ve distinto sin que haya cambiado nada.
- **El umbral se calcula una vez**, con Otsu sobre VV en dB de la fecha con Sentinel-1 y Sentinel-2 del mismo día (04/11/2023; no es el pico de la serie), fuera del agua permanente, y **se aplica a todas las fechas**. Un umbral por fecha haría variar la definición de agua dentro de la serie.
- **El agua permanente se excluye** (JRC ≥ 90 %): el río y el embalse no son inundación.
- **El agua que ya estaba en una fecha seca se excluye.** Con el mismo umbral se mira la escena Sentinel-1 de la misma órbita más cercana al 22/01/2026 (río en nivel normal; `--referencia_seca`): las lagunas estacionales, los bañados y los arrozales con agua ese día no son inundación. Lo que queda es **agua de inundación**: agua abierta en la fecha, que no es permanente ni estaba en la referencia seca. Si no hay escena de referencia de esa órbita, la bitácora lo avisa y la capa se llama «agua temporal»: hay que declararlo.
- **Duración:** cada fecha con agua cuenta los días hasta la fecha siguiente de la serie; la última, la mitad de la revisita mediana. Con una pasada cada 12 días por órbita, la duración tiene esa resolución.

Lo que el umbral de VV **no** ve, y se declara: el agua bajo pajonal o monte (allí VV puede **subir** por doble rebote) y el embalse rizado por el viento (dispersión de Bragg), que se aclara: con −15 dB, el 04/11/2023 un tercio del agua permanente queda arriba del umbral, y otras fechas menos. Por eso se excluye por JRC y no por el umbral.

```
python Tp6_01_serie_agua_C.py --pixel 20 --desde 2023-10-01 --hasta 2024-06-30 --fecha_umbral 2023-11-04
```

Valores por defecto: `--pixel 20`, `--desde 2023-10-01`, `--hasta 2024-06-30`, `--fecha_umbral 2023-11-04` (antes `--pico`, que se sigue aceptando), `--umbral_vv` (vacío: Otsu), `--orbita` (vacío: la más frecuente), `--referencia_seca 2026-01-22` (una o varias fechas separadas por coma; `no` para no usarla), `--persistencia 2`.

**Limitación de la referencia seca.** La del 22/01/2026 es posterior al evento: puede borrar unas 400 ha de agua real el 04/11 (9 % de la unión). Lo correcto es una referencia previa, de varias fechas de la misma órbita, con el río en nivel normal verificado en el hidrómetro; la de 2026 queda como análisis de sensibilidad.

**Salida en pantalla.**
- `Escenas en la ventana: N; se usa la orbita relativa X (M escenas). Otras orbitas: [...]`.
- `Agua permanente (JRC >= 90 %): x % del sitio, excluida de la inundacion.`
- `Fecha del umbral AAAA-MM-DD: 2 cuadro(s) de la pasada, 100 % del sitio con dato.` (el umbral se calcula con los cuadros de la pasada unidos).
- `Umbral de agua abierta: umbral de OTSU -xx.xxx calculado sobre ... valores; deja ... %`.
- **Con los datos del curso (corrida del 22/10/2026), Otsu falla:** da −9,5 dB y deja casi la mitad del sitio como agua, porque el histograma de VV del 04/11/2023 es unimodal (el agua de inundación es poca y, ese día, el viento y la corriente la aclaran: mediana de −16 dB). Se fija a mano `--umbral_vv -15`, elegido con el agua permanente de JRC y la tierra de JRC = 0 (omite un tercio del agua permanente y marca el 1,4 % de la tierra). Declárelo. En VH el agua se separa mejor (−22 contra −15 dB), pero el práctico usa VV.
- `Referencia seca: Sentinel-1 del AAAA-MM-DD (orbita X): ... ha de agua no permanente que ya estaba;` (o el AVISO de que no hay escena de esa órbita).
- Una línea por fecha: `AAAA-MM-DD  agua temporal  ... ha  (... % del sitio con dato)` (con referencia seca, esas hectáreas ya no incluyen el agua que estaba el día seco).
- Si el sitio cae en dos cuadros consecutivos de la misma pasada, una línea más: `AAAA-MM-DD  segundo cuadro de la misma pasada: unido -> agua de inundacion ... ha  (... % del sitio con dato)`. En B_CONCORDIA casi todas las fechas llegan así: el primer cuadro cubre el 2 % del sitio y la línea que vale es la del segundo, con las hectáreas de los dos unidos. Cuatro fechas tienen un solo cuadro (2 a 20 % del sitio) y no son comparables. Los dos cuadros forman una sola capa y una sola fila de la tabla.
- Al final: `Extension maxima: ... ha; pixeles con mas de 30 dias de agua: ... ha`.

**Salidas.**
- `02_Subsets_SNAP_QGIS\B_agua_C_por_fecha_20m.tif` (una banda por fecha, `agua_AAAAMMDD`, 1 = agua de inundación; la descripción del archivo dice si se usó la referencia seca).
- `05_Resultados\02_Rasters\B_extension_y_duracion_C_20m.tif` (bandas `extension_maxima`, `duracion_dias` y `agua_en_referencia_seca`, que usa el paso 3; y `duracion_min_dias`, `duracion_max_dias` y `extension_persistente`: la duración real está entre la mínima, que trata lo no observado como seco, y la máxima, que lo trata como agua).
- `05_Resultados\04_Tablas\B_serie_agua_C.csv` (fecha, hora UTC, id, hectáreas, % con dato, días que representa). Una fila por fecha; cuando la fecha se armó con dos cuadros de la misma pasada, la columna `id` lleva los dos identificadores unidos por ` + `.
- `05_Resultados\05_Graficos\B_serie_agua_C.png` y `B_histograma_VV_pico.png`.

**Ver en QGIS.** `B_extension_y_duracion_C_20m.tif`, banda `duracion_dias`, `Pseudocolor monobanda` (Singleband pseudocolor) de 0 a 90 días, rampa de azules. Encima, la capa de agua permanente (clase 1 de la cobertura de control) en gris.

**Control.**
- Mire `B_histograma_VV_pico.png`: si hay dos modas (agua muy oscura y tierra), el umbral de Otsu cae en el valle. Con los datos del curso el histograma de VV es unimodal y Otsu da −9,5 dB: se fija −15 dB con el agua de JRC (Figura 10 del Desarrollo). Declárelo.
- La serie tiene dos máximos, 3.869 ha el 28/11/2023 y 3.589 ha el 14/05/2024; el 04/11 da 2.912 ha. Una fecha aislada con muchas hectáreas y vecinas bajas suele ser viento o escena incompleta: mire su `pixeles_validos_%` y, en QGIS, si el embalse está más claro esa fecha (más viento).
- En una fecha armada con dos cuadros de la misma pasada, `pixeles_validos_%` debe ser parecido al de las demás fechas: los dos cuadros juntos cubren el sitio.

**Errores típicos.**
- `No hay escena de la orbita X el 2023-11-04. Elegir --fecha_umbral entre: ...`: la órbita más frecuente no pasó ese día. Fije `--orbita` con la órbita de la escena del 04/11/2023 (la ve en la planilla del Tp1_03) o elija otra fecha entre las listadas.
- `El Planetary Computer no devolvio Sentinel-1 RTC para la ventana.`: sin red o sin escenas.

---

## Paso 2 · SINERGIA: qué ve cada sensor el día del evento — SE CORRE

**Qué y por qué.** Cada sensor dice dónde ve agua, con su propia física, y se comparan sin fusionar:

- **C, VV:** agua abierta con cualquier cielo (la del paso 1, misma fecha).
- **Óptico, MNDWI = (B03 − B11)/(B03 + B11):** el agua absorbe fuerte en el infrarrojo de onda corta (B11) y refleja algo en el verde (B03), así que el índice es positivo sobre agua. Umbral manual 0 por defecto, justificado con `B_histograma_MNDWI.png`: el 04/11/2023 el MNDWI es bimodal (tierra en −0,55, agua en +0,58) y el 0 cae en el valle, aun con el agua turbia del Uruguay. Donde hay nube, no vota.
- **L, HH (SAOCOM):** aumento de HH ≥ 3 dB respecto de una referencia seca = agua bajo la vegetación (el tronco y el agua forman un diedro que devuelve la señal). CONAE entregó dos SAOCOM-1B TNA cuadripolares de la misma órbita: 10/10/2023 (seco) y 11/11/2023 (crecida), ya en γ⁰ a 20 m en `02_Subsets_SNAP_QGIS\SAOCOM_gamma0\QGIS_GeoTIFF` (ver el LEEME de esa carpeta). Los del 31/10 y 08/11/2023 (TNB) cubren la mitad del sitio y no se usan aquí. **La banda L se corre aparte, como prueba** (ver abajo): no entra en las variantes validadas.
- **L, HH y HV (ALOS-2 PALSAR-2, mismo día que C; para profundizar, optativo):** ScanSAR del 16/11/2023, ya en γ⁰ lineal a 20 m en `02_Subsets_SNAP_QGIS\ALOS2_gamma0` (ver su LEEME). Sirve para comparar el agua abierta en banda L (HH bajo) con la de C del mismo día. Su nivel absoluto queda unos 4 dB por debajo del mosaico de JAXA: se usa dentro de la escena, sin comparar decibeles con otro sensor. No sirve para medir doble rebote: no hay escena seca del mismo ALOS-2, y compararlo con el SAOCOM seco sería un cambio entre sensores.

```
python Tp6_02_sinergia_agua.py --pixel 20 --fecha 2023-11-04
```

Valores por defecto: `--pixel 20`, `--fecha 2023-11-04`, `--u_mndwi 0.0`, `--l_evento` y `--l_referencia` (vacíos), `--u_doble_rebote 3.0` (dB).

**Prueba con banda L (SAOCOM).** Antes de correrla, copie `05_Resultados\04_Tablas\B_sinergia_agua.csv` y `05_Resultados\02_Rasters\B_agua_por_sensor_20m.tif` con otro nombre: la corrida los reescribe. Primero con la regla fija del curso:

```
python Tp6_02_sinergia_agua.py --pixel 20 --fecha 2023-11-04 ^
    --l_evento ..\02_Subsets_SNAP_QGIS\SAOCOM_gamma0\QGIS_GeoTIFF\B_CONCORDIA_SAOCOM_L_20231111_QP_gamma0_Gamma0_HH.tif ^
    --l_referencia ..\02_Subsets_SNAP_QGIS\SAOCOM_gamma0\QGIS_GeoTIFF\B_CONCORDIA_SAOCOM_L_20231010_QP_gamma0_Gamma0_HH.tif
```

La pantalla dice `Banda L: aumento mediano de HH en el sitio entre las dos fechas: +3.12 dB` y la regla marca más de la mitad del sitio: entre las dos fechas todo el paisaje se aclaró en banda L (humedad del suelo, crecimiento de cultivos y pasturas), no sólo el monte inundado. Después repita agregando `--l_relativo` (resta esa mediana antes del umbral) y `--l_solo_lenoso` (aplica la regla sólo en monte y plantaciones de MapBiomas 2023, clases 3, 4, 6 y 9). Queda alrededor del 1,4 % del sitio, en plantaciones de las lomas, sin casi ningún píxel en común con el agua de C o del óptico. Restar la mediana de todo el sitio (dominada por pastos y cultivos) deja en las leñosas un umbral efectivo de unos 6 dB: agregue `--l_base clase` para restar la mediana del monte y las plantaciones fuera del agua (+2,59 dB, umbral efectivo 5,6 dB); quedan 2,1 % de candidatos, también lejos del río. Abra en QGIS la diferencia de HH entre las dos fechas y el raster `L_HH_doble_rebote` sobre el agua de C: ¿los candidatos están pegados al río? ¿Qué pasa con la HH en el bañado inundado (baja: espejo, no diedro)? Conclusión esperada: con este par de fechas R2 no se aplica. Vuelva a poner sus archivos originales antes del paso 3.

**Salida en pantalla.**
- `Sentinel-2 ...: nubes en el sitio x %` por cada escena del día.
- `Optico: umbral MANUAL 0.000 (justificar con el histograma y la referencia); deja ... %`.
- `Sin banda L: el agua bajo vegetacion NO se evalua. Los SAOCOM de CONAE del 10/10 y el 11/11/2023...`. Es el mensaje esperado en la corrida sin banda L.
- La tabla `Acuerdo entre sensores el 2023-11-04 (sin fusionar)` con `%_clase_sensor_1`, `%_clase_sensor_2`, `%_ambos`, `%_solo_1`, `%_solo_2`, `acuerdo_%`.

**Salidas.** `05_Resultados\02_Rasters\B_agua_por_sensor_20m.tif` (bandas `C_Sentinel1_VV`, `Optico_MNDWI` y, si hubiera, `L_HH_doble_rebote`), `05_Resultados\04_Tablas\B_sinergia_agua.csv`, `05_Resultados\05_Graficos\B_histograma_MNDWI.png`.

**Interpretación (la sinergia).**
- `%_ambos` alto en agua abierta con cielo despejado: C y óptico coinciden donde deben.
- `%_solo_2` (sólo el óptico ve agua): agua somera o muy turbia con viento, o bordes donde el píxel mezcla.
- `%_solo_1` (sólo C ve agua): superficies lisas que no son agua (pistas, suelo muy liso) o sombra de radar; mírelas en QGIS.
- La tabla usa sólo píxeles donde **todos** los sensores tienen dato: los píxeles con nube quedan fuera. Anote qué fracción del sitio era.
- **Interpretación con NovaSAR (opcional, EN QGIS).** El σ⁰ HH de la escena 47942 (13/09/2023, banda S, 6 m) ya está en el práctico: `02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\B_CONCORDIA_NovaSAR1_S_20230913_Sigma0_HH.tif` (y `_Sigma0_HH_db.tif` para mirarlo en dB). Cárguelo al lado de su mapa: muestra el río en su cauce dos meses antes de la crecida. Cubre el 39 % del sitio. **Atención:** está en geometría de radar y QGIS lo ubica con los puntos de control que trae; no está en la grilla de B_CONCORDIA (medido contra Sentinel-2 el 20/10/2026: corrido unos 200 a 420 m en sentido norte–sur, y no de manera uniforme). Por eso no entra a la tabla ni a ningún script del Tp6: sirve para razonar (sinergia en el razonamiento), no para medir.

**Errores típicos.**
- `La serie C no tiene la fecha 2023-11-04. Fechas: ...`: el paso 1 usó otra órbita. Use una fecha de la lista o rehaga el paso 1 con `--orbita`.
- `No hay Sentinel-2 el ...: la sinergia queda sin optico (declararlo).` y luego `Solo hay un sensor: no hay sinergia que medir.`: con una fecha sin óptico (por ejemplo una de mayo de 2024) y sin L, no hay sinergia posible ese día.

---

## Paso 3 · FUSIÓN DE DECISIÓN y variantes — SE CORRE

**Qué y por qué.** Reglas escritas:

- R1: agua de inundación si C dice agua (agua abierta, cualquier cielo).
- R2: o si L dice doble rebote (agua bajo vegetación). Probada con SAOCOM en el paso 2: no se aplica.
- R3: o si el óptico dice agua **y** el píxel no tiene nube (con nube, el óptico no vota).
- R4: nunca donde JRC marca agua permanente (ya aplicado en los pasos 1 y 2).
- R5: nunca donde ya había agua en la fecha seca de referencia (banda `agua_en_referencia_seca` del paso 1).

Es una **unión**: maximiza la detección y también la comisión. El Tp4 dirá cuánto.

```
python Tp6_03_fusion_y_variantes.py --pixel 20
```

**Salida en pantalla.** `Optico solo ... ha de agua (x % del sitio sin dato por nubes)`, `C solo ... ha`, `Multisensor ... ha (union de C_Sentinel1_VV, Optico_MNDWI)` y la advertencia sobre la comisión. Sin L no aparece `C union L`.

**Salidas** (en `05_Resultados\02_Rasters\`, códigos 1 = agua de inundación, 2 = no): `B_variante_optico.tif`, `B_variante_C.tif`, `B_variante_CL.tif` (sólo si hay L) y `B_variante_multisensor.tif` (bandas `clase` y `sensores_que_votaron`).

**Control.** Las hectáreas de la multisensor son mayores o iguales que las de cada variante sola (es una unión). La banda `sensores_que_votaron` vale 1 donde había nube (votó sólo C) y 2 donde había cielo despejado.

**Antes de validar o de procesar otra fecha: copie y renombre.** Los archivos no llevan la fecha. Para conservar la crecida de noviembre:

```
cd ..\05_Resultados\02_Rasters
copy /Y B_variante_C.tif B_variante_C_20231104.tif
copy /Y B_variante_optico.tif B_variante_optico_20231104.tif
copy /Y B_variante_multisensor.tif B_variante_multisensor_20231104.tif
cd ..\..\03_Scripts
```

El Tp4 usa el nombre del archivo como `<NOMBRE>`, así que cada copia se valida por separado y sin pisarse.

---

## Paso 4 · Validar las variantes con el Tp4 — SE CORRE + EN QGIS

Desde la carpeta de scripts del Tp4:

```
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp4_Validacion\03_Scripts
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp6_Inundaciones\05_Resultados\02_Rasters\B_variante_C_20231104.tif --banda 1
```

Etiquete al azar en QGIS (guía del Tp4, paso 7) con `1` agua de inundación y `2` no, con **la misma definición que el mapa**: agua abierta el 04/11/2023, con ocurrencia JRC menor que 90 % y fuera de la banda `agua_en_referencia_seca`. Referencia disponible: el Sentinel-2 del mismo día (no hay imágenes de alta resolución fechadas cerca del 04/11/2023 en todo el sitio). Ese Sentinel-2 entra en la variante óptica y en la multisensor: la validación las favorece, y se declara por variante; sólo la C se valida sin ese sesgo. Una referencia independiente posible es la fotointerpretación del Landsat 8 del 25/10/2023 (sólo para lo estable) o la HH del ALOS-2 del 16/11/2023 para la C. Cada grupo etiqueta una sola variante. Para mayo de 2024, los productos de la Carta Internacional, activación 880.

**Muestra común (diseño recomendado).** Para comparar variantes con eficiencia conviene una sola muestra para las tres, con un estrato de borde: `Tp4_Validacion\04_Tablas_de_trabajo\B_muestra_comun_20231104_puntos_a_etiquetar.gpkg` (300 puntos: 50 en agua en las tres, 75 en desacuerdo, 75 en un anillo de 200 m y 100 en el resto).

```
python Tp4_03_exactitud_y_area.py --nombre B_variante_C_20231104 --nombres_clase "1=agua,2=no_agua"
```

Repita con `B_variante_optico_20231104` y `B_variante_multisensor_20231104`. Después:

```
python Tp4_04_tabla_de_variantes.py --tp Tp6 --clase agua ^
    --variante "Optico solo|Sentinel-2|B_variante_optico_20231104" ^
    --variante "SAR solo (C)|Sentinel-1|B_variante_C_20231104" ^
    --variante "Multisensor|C + optico|B_variante_multisensor_20231104"
```

Salida: `Tp6_Inundaciones\05_Resultados\04_Tablas\tabla_de_variantes_agua.csv`. `Tp4_04` compara cada variante con la mejor; la diferencia entre otras dos (por ejemplo, multisensor frente a C) se calcula a mano: diferencia ± raíz(IC₁² + IC₂²). La fila «SAR multibanda» no existe porque la banda L no aportó agua bajo vegetación detectable (paso 2): se escribe así en el informe.

**Ojo con la variante óptica.** Sus píxeles con nube quedan sin dato y **no entran** al muestreo: su exactitud se refiere sólo a la parte despejada del sitio. Su área estimada no es comparable con la de las variantes de radar. Dígalo.

---

## Paso 5 · Profundidad por la cota del borde — SE CORRE

**Qué y por qué.** Es la idea de FwDET (Cohen et al., 2018, versión 1.0; Cohen et al., 2019, versión 2.0): la superficie del agua es **horizontal localmente**, a la cota del borde de la mancha. Para cada píxel inundado:

1. se buscan los píxeles de borde (inundados con algún vecino seco) y su cota en el MDE (Copernicus DEM por defecto; FABDEM con `--mde fabdem`);
2. se suaviza la cota de borde con el promedio de las cotas de borde dentro de una ventana móvil de `--suavizado` × `--suavizado` píxeles, para que un borde mal ubicado no fabrique un pozo;
3. cada píxel inundado toma la cota del borde más cercano;
4. profundidad = cota del borde − cota del MDE; los negativos se llevan a 0 y se cuentan.

Vuelva a la carpeta del Tp6:

```
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp6_Inundaciones\03_Scripts
python Tp6_04_profundidad.py --pixel 20 --variante multisensor --suavizado 7
python Tp6_04_profundidad.py --pixel 20 --variante multisensor_20231104 --suavizado 7 --mde fabdem
```

Valores por defecto: `--pixel 20`, `--variante multisensor`, `--suavizado 7`. `--variante` es lo que sigue a `B_variante_` en el nombre del archivo: con las copias del paso 3, use `--variante multisensor_20231104`.

**Salida en pantalla.**
- `Pixeles inundados: N; con profundidad negativa (llevados a 0): M (x %)`.
- `Profundidad: mediana ... m, p90 ... m, maximo ... m` (con los negativos llevados a 0), y las mismas cifras con los valores originales, con los positivos solos y el número de píxeles de más de 5 m.
- Las dos advertencias: el Copernicus DEM es de superficie (copa y espejo de agua de 2011–2015) y la profundidad es plausible, no medida.

**Salida.** `05_Resultados\02_Rasters\B_profundidad_<variante>_20m.tif` (bandas `profundidad_m`, `cota_agua_m` y `profundidad_sin_recortar_m`; con FABDEM el nombre lleva `_fabdem`).

**Control.**
- Un porcentaje alto de profundidades negativas (más de 10 a 20 %) indica que la mancha incluye zonas más altas que su borde: comisión en la mancha o MDE que mide copa.
- En QGIS, pseudocolor de 0 a 5 m. Las mayores profundidades deben estar cerca del cauce, no en el medio de un monte.

**Errores típicos.**
- `FileNotFoundError` con `B_variante_multisensor.tif`: el nombre de `--variante` no coincide con un archivo existente.
- Falla al leer el Copernicus DEM: sin red al Planetary Computer.

---

## Paso 6 · Control del MDE con ICESat-2 — SE CORRE

**Qué y por qué.** La profundidad depende del MDE. ICESat-2 ATL08 da la altura del **terreno** (`h_te_best_fit`) en segmentos de 100 m. Pero es una altura **elipsoidal** (WGS 84), y el Copernicus DEM está sobre el geoide EGM2008. En Entre Ríos la diferencia ronda los 15 m: sin convertir, la comparación no sirve. El script convierte con PROJ y se detiene si falta la grilla del geoide (prefiere fallar a comparar mal).

```
python Tp6_05_control_mde_icesat2.py --pixel 20
python Tp6_05_control_mde_icesat2.py --pixel 20 --solo_fuertes
python Tp6_05_control_mde_icesat2.py --pixel 20 --clases ambas --excluir_evento
```

Valores por defecto: `--pixel 20`, `--solo_fuertes` desactivado, `--clases control` (`mapbiomas` o `ambas` estratifican también por MapBiomas 2023), `--mde copdem` (`fabdem` controla FABDEM), `--excluir_evento` desactivado (deja afuera los segmentos de octubre de 2023 a junio de 2024). El MDE se promedia en los cinco píxeles que cubre el segmento de 100 m. Los haces fuertes se identifican con `sc_orient` (ATL08 v007): tienen más fotones y menos ruido.

Filtros (aplicados en el Tp1 y aquí): terreno válido (`h_te_best_fit` distinto del valor de relleno 3,4·10³⁸) y fuera de agua (`segment_watermask` = 0).

**Salida en pantalla.** `Segmentos ATL08 con terreno valido: N` y una tabla con `grupo` (`todos` y `clase k` de la cobertura de control), `n`, `sesgo_m` (MDE − ICESat-2), `desvio_m`, `RMSE_m`, `mediana_m`. Al final: `Si el sesgo en suelo desnudo, pastura o herbaceas supera 1 m, la profundidad de Tp6_04 hereda ese sesgo y, en cada pixel, un error del orden del RMSE de la clase.`

**Salida.** `05_Resultados\04_Tablas\B_control_mde_icesat2.csv`.

**Interpretación.**
- Clase 5 (cultivo_pastura) y 6 (suelo_desnudo): allí el MDE debería medir suelo. Con la cobertura de control hay sólo 8 segmentos de pastura; con MapBiomas, miles en herbáceas y herbáceas inundables: use esa tabla. La profundidad hereda el sesgo y, en cada píxel, un error del orden del RMSE.
- Clases 3 y 4 (monte, plantación): sesgo positivo esperable, porque el MDE es de superficie y mide la copa. No es un error del control: es la razón por la que la profundidad bajo el monte no es confiable.
- Sólo se informan los grupos con al menos 5 segmentos.

**Errores típicos.**
- `RuntimeError: PROJ no aplico el geoide EGM2008 (falta la grilla us_nga_egm08_25.tif)...`: corra `projsync --file us_nga_egm08_25` con red y repita.
- `Falta ...lidar_B_CONCORDIA.gpkg (Tp1_05 con --descargar).`
- Tabla con un solo grupo `todos`: no está la cobertura de control a 20 m.

---

## La segunda crecida (mayo de 2024)

La serie del paso 1 ya la incluye. Para la sinergia y las variantes de mayo, elija una fecha de la serie (columna `fecha` de `B_serie_agua_C.csv`) y repita el paso 2 con `--fecha <esa fecha>` y luego los pasos 3 a 5, después de haber copiado y renombrado las variantes de noviembre. Si ese día no hay Sentinel-2, el paso 2 avisa que no hay sinergia posible (un solo sensor) y termina sin escribir `B_agua_por_sensor_20m.tif`: en ese caso la única variante es la de C, que está en `02_Subsets_SNAP_QGIS\B_agua_C_por_fecha_20m.tif` (banda `agua_AAAAMMDD`) y puede compararse con los productos de la activación 880 de la Carta Internacional.

**Cuidado:** si en ese caso corre igual el paso 3, `Tp6_03` lee el `B_agua_por_sensor_20m.tif` que quedó de noviembre y vuelve a producir las variantes de noviembre con nombre genérico. Mire siempre la bitácora del paso 2 antes de correr el 3.

---

## Para profundizar (optativo) · Del Sentinel-1 sin procesar a γ⁰ — EN SNAP

**Qué y por qué.** Todos los Sentinel-1 de este práctico vienen ya corregidos: son el γ⁰ RTC del Planetary Computer. Este paso muestra de dónde sale ese γ⁰. Se parte del producto GRDH de nivel 1 tal como lo entrega ESA, el `.zip` con la carpeta `.SAFE` adentro (mediciones, anotaciones, calibración, ruido y órbita predicha), y se recorre en SNAP la misma cadena que usó el docente. El resultado del docente viene hecho y sirve para controlar el suyo.

**Insumo.** `00_COMUN\08_Originales_crudos\S1_CRUDO\S1A_IW_GRDH_1SDV_20231104T091449_20231104T091514_051065_06285B_E987.zip` (Sentinel-1A IW GRDH, VV + VH, 04/11/2023). Se eligió esa pasada porque es la del pico de la crecida y tiene Sentinel-2 del mismo día.

**Lo que viene hecho.** `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo` de este práctico: `SNAP_DIMAP` (γ⁰ VV y VH lineales, bandas virtuales en dB y cociente VV/VH en dB, metadatos completos), `QGIS_GeoTIFF` (con `_metadatos.txt`), `RGB_copol_cruzada_cociente` (R = VV, G = VH, B = VV/VH) y `Grafos_SNAP` (el grafo XML). El detalle está en `LEEME_S1_crudo.md` de esa carpeta.

**Dónde.** SNAP Desktop. La primera vez SNAP baja la órbita precisa y el Copernicus DEM, así que necesita internet. Hay dos formas de hacerlo.

**Forma rápida: el grafo del docente.**

1. `Tools > GraphBuilder`, botón `Load`, y elija `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\Grafos_SNAP\Grafo_B_CONCORDIA_S1_20231104_gamma0_desde_crudo.xml`.
2. Recorra las pestañas: cada una es un paso de la cadena, con los parámetros que se usaron.
3. En la pestaña `Write`, cambie el nombre y la carpeta de salida a `05_Resultados\02_Rasters`, para no pisar el producto del docente. Botón `Run`.

**Forma completa: paso a paso con los menús.** Cada operador escribe un producto intermedio. En la ventana de cada uno, pestaña `I/O Parameters`, deje como entrada el producto anterior y guarde en `05_Resultados\02_Rasters`.

1. `File > Open Product…` sobre el `.zip` (no hace falta descomprimirlo).
2. `Radar > Radiometric > S-1 Thermal Noise Removal`: quita el ruido térmico del instrumento, que pesa en VH y en las superficies oscuras, como el agua.
3. `Radar > Sentinel-1 TOPS > S-1 Remove GRD Border Noise` (límite de borde 500, umbral 0,5): quita las franjas de valores falsos de los bordes de la escena.
4. `Radar > Apply Orbit File`, tipo `Sentinel Precise (Auto Download)`: reemplaza la órbita predicha por la precisa.
5. `Radar > Radiometric > Calibrate`: en `Processing Parameters` marque sólo `Output beta0 band`. El aplanado necesita β⁰, no σ⁰.
6. `Raster > Subset…`, pestaña `Geo Coordinates`: recorte al sitio. Recortar antes del aplanado ahorra mucho tiempo y memoria.
7. `Radar > Radiometric > Terrain Flattening`, DEM `Copernicus 30m Global DEM`, remuestreo bilineal: pasa de β⁰ a γ⁰, normalizado por el área iluminada. Es el paso más lento.
8. `Radar > Speckle Filtering > Single Product Speckle Filter`, filtro `Refined Lee`.
9. `Radar > Geometric > Terrain Correction > Range-Doppler Terrain Correction`: DEM `Copernicus 30m Global DEM`, píxel de 10 m, proyección UTM automática (`AUTO:42001`, que en este sitio es la zona 21 S, la de la grilla del curso), formato BEAM-DIMAP.
10. Bandas en dB: clic derecho sobre cada banda γ⁰ > `Linear to/from dB`. Crea bandas virtuales y deja intactas las lineales.
11. Cociente: `Raster > Band Maths…`, expresión `Gamma0_VV_db - Gamma0_VH_db` (en dB, la resta es el cociente VV/VH).
12. RGB: `Window > Open RGB Image Window`, con R = `Gamma0_VV_db`, G = `Gamma0_VH_db` y B = el cociente.

**Salida en pantalla.**

- Un producto con `Gamma0_VV` y `Gamma0_VH` en lineal y sus bandas virtuales en dB.
- En `Metadata > Processing_Graph`, la lista de operadores en el orden en que se aplicaron. Ahí queda escrito todo lo que se le hizo al dato.
- En `Metadata > Abstracted_Metadata`, la misión, la fecha, la órbita y el ángulo de incidencia del original: el recorte no los pierde.
- Abierto junto al producto del docente (el `.dim` de `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\SNAP_DIMAP`), los dos se superponen en `World View` y se ven casi iguales.

**Comparación con el RTC del Planetary Computer.** El mismo día existe el γ⁰ RTC del Planetary Computer, en `02_Subsets_SNAP_QGIS\SNAP_DIMAP\B_CONCORDIA_S1_C_20231104.dim` de este práctico. Diferencia mediana del γ⁰ de SNAP menos el RTC, en todo el sitio:

- VV: −0,66 dB (p5 a p95, −3,1 a +2,2 dB; correlación 0,88).
- VH: −1,42 dB (p5 a p95, −6,3 a +1,4 dB; correlación 0,86).

(Corrida del Desarrollo, con el γ⁰ de SNAP llevado a la grilla del RTC por promedio; una corrida anterior, sin ese remuestreo, daba −0,71 y −1,45 dB.) Con −15 dB en VV, el γ⁰ de SNAP marca 17.457 ha de agua (incluido el río) y el RTC 15.191 ha.

**Interpretación.**

- En VV, casi toda la diferencia es un desfase de normalización de `Terrain Flattening` de SNAP: su γ⁰ queda por debajo de σ⁰/cos θ aun en terreno plano. El desfase cambia con la escena y el ángulo de incidencia (−0,5 dB en Concordia, −1,0 dB en Federal). Su causa no está documentada.
- VH queda siempre más abajo que VV. Lo más probable es la remoción del ruido térmico, que pesa más cuanto más débil es la señal. No está verificado cómo trata el ruido el RTC del Planetary Computer.
- Consecuencia práctica: **nunca** calcule un cambio (Δ) entre una fecha procesada en SNAP y otra del RTC. Una diferencia de 1 a 3 dB entre cadenas de proceso es del mismo orden que la señal que se busca. Todas las fechas de una serie se procesan con la misma cadena.
- El agua abierta tiene retrodispersión muy baja, cerca del piso de ruido, justo donde la remoción del ruido térmico más pesa. Un umbral de agua ajustado sobre el RTC no se puede aplicar tal cual al γ⁰ de SNAP: hay que reajustarlo.

**¿Hace falta el aplanado en un relieve plano?** Concordia es el sitio del curso con pendientes de verdad: barrancas del Uruguay y valles de arroyos (FABDEM: 15 % del sitio con más de 3°). Se procesó también σ⁰ sin aplanar (`procesar_s1_crudo.py --sin_aplanar`) y se separó, píxel a píxel, lo que corresponde al ángulo de incidencia, al desfase de SNAP (−0,49 dB) y al relieve. Lo que agrega el relieve, por clase de pendiente del Copernicus DEM (que, por ser de superficie, marca más pendientes que el FABDEM):

- 0 a 1° (30 % del sitio): mediana 0,00 dB; p5 a p95, −0,14 a +0,17 dB.
- 1 a 3° (44 %): +0,01 dB; −0,36 a +0,35 dB.
- 3 a 10° (22 %): −0,03 dB; −0,93 a +0,82 dB.
- Más de 10° (4 %): +0,08 dB; −2,24 a +2,37 dB.

El relieve no cambia la mediana en ninguna clase, porque las laderas que miran al satélite y las que le dan la espalda se compensan. Pero sí cambia cada píxel, hasta ±2,3 dB en las pendientes de más de 10°: ahí el aplanado sí corrige. Tabla y figura: `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\B_CONCORDIA_S1_20231104_gamma0_desde_crudo_aplanado_vs_sin_aplanar.csv` y `.png`.

**Errores típicos.**

- SNAP se queda en `Apply Orbit File` o en `Terrain Flattening` sin avanzar: está bajando la órbita o el DEM. Sin internet no puede; conéctese y repita.
- `Terrain Flattening` rechaza la entrada: la calibración no dejó la banda β⁰. Repita `Calibrate` con `Output beta0 band`.
- Falta de memoria o un proceso de horas: no recortó antes del aplanado. Haga el `Subset` antes.
- El producto no cubre el sitio: el recorte se definió por píxeles. Use la pestaña `Geo Coordinates`.
- QGIS no abre el `.zip`: es normal, el original es para SNAP. En QGIS use `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\QGIS_GeoTIFF`.

Fuente: ESA Copernicus, Sentinel-1A IW GRDH, 04/11/2023, S1A_IW_GRDH_1SDV_20231104T091449_20231104T091514_051065_06285B_E987. Distribuido por ASF DAAC, https://search.asf.alaska.edu. Procesado con ESA SNAP y Copernicus DEM GLO-30.
