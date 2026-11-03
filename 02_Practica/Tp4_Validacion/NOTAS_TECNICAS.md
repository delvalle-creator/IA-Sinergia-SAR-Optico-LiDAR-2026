# Tp4 — Notas técnicas

> **Qué es este archivo.** Las decisiones técnicas del práctico y su fundamento, las limitaciones conocidas y lo que ya se comprobó con datos reales. No es el punto de entrada: para eso está `00_LEEME.md`.

## Por qué hay que generar el mapa de control

No hay un mapa de cobertura de Entre Ríos que sea a la vez reciente, con las clases que necesita el curso (pajonal, monte, plantación, agua permanente, ciudad) y **independiente** de los sensores que se evalúan. Un mapa de cobertura global derivado de Sentinel-1 y Sentinel-2 no sirve de control para mapas hechos con Sentinel-1 y Sentinel-2. Por eso se combina interpretación propia sobre imágenes submétricas con dos productos de otra fuente (Landsat): JRC y MapBiomas.

## La prioridad de fuentes

Digitalizado > JRC > MapBiomas. La interpretación del grupo manda porque es la única hecha con imágenes de muy alta resolución y conocimiento del lugar. JRC va segundo porque su definición de agua permanente es objetiva y documentada. MapBiomas va último porque es una clasificación automática de terceros: se acepta como monte sólo donde el grupo no dijo otra cosa, y sólo donde la imagen de 2 m muestra copas.

## Agua permanente: ocurrencia ≥ 90 %

JRC Global Surface Water da, para cada píxel de 30 m, el porcentaje de observaciones Landsat válidas entre 1984 y 2021 en que hubo agua. Con ≥ 90 % entra el cauce del río Uruguay, el embalse de Salto Grande y las lagunas permanentes, y quedan fuera los bañados que se llenan en las crecidas. Es lo que necesitan el Tp6 (el río no es inundación) y el Tp5 (las lagunas no son quema). Un umbral de 50 % metería en “permanente” una parte de lo que el Tp6 quiere medir.

JRC se lee por vecino más próximo (es un porcentaje entero con 255 como sin dato) y se lleva de 30 m a la grilla de 20 m sin promediar.

## MapBiomas: moda, no promedio

Los rásteres `Bosques_MapBiomas_2023_*.tif` son clases. Promediar clases no tiene sentido; se remuestrean por moda. Todo valor > 0 se toma como monte (clase 3). Los recortes siguen las huellas de las escenas NovaSAR del archivo: en B_CONCORDIA sólo puede aportar dentro de la escena 47942, que cubre el 39 % del sitio; sobre el Delta ninguna escena NovaSAR del archivo pasa, de modo que en A1_DELTA_QUEMAS MapBiomas no aporta.

## Monte de MapBiomas recortado con las copas de 2 m

El bosque de MapBiomas es de 30 m y, sobre Esri, cubría caseríos, pasto, bañados y bordes de frutales. Se hizo una máscara de copas sobre la imagen CBERS-4A WPM del 15/07/2026 fusionado a 2 m (`Tp10_Impacto_urbano\02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\B_CONCORDIA_CBERS4A_CONCORDIA_20260715_pansharpened_2m.tif`, 13 × 21 km del centro del sitio). En julio el NDVI no separa árboles de pasto seco; la regla usa brillo y textura: copa si el brillo medio en 10 m < 0,92 × la mediana local (ventana de 2,5 km, que absorbe la costura entre escenas y la bruma) y el desvío en 10 m > 0,045 × la mediana, o si el brillo medio < 0,80 × la mediana (copa cerrada). La copa cubre el 20 % de la imagen. La fracción de copa por píxel de 20 m está en `02_Subsets_SNAP_QGIS\B_CONCORDIA_copa_CBERS4A_fraccion_20m.tif` y la máscara de 2 m en `B_CONCORDIA_copa_CBERS4A_2m_20260715.tif`. `Tp4_01` deja como monte sólo el bosque de MapBiomas con copa ≥ 0,5 (`--copa_min`); fuera de la imagen o bajo nubes no hay monte. Quedan 37.652 de 237.389 píxeles (1.506 ha de 9.496). Límites: una sola imagen de invierno; la regla no separa plantaciones ni frutales que MapBiomas llame bosque (tienen copas). Control independiente con ICESat-2 ATL08 (5.524 segmentos de 100 m de 2024 a 2026 dentro de la imagen): los segmentos con árboles de 5 m o más son el 27 % donde la máscara marca menos del 2 % de copa y el 65 % donde marca más del 40 %; la altura mediana del dosel pasa de 5,4 a 10,1 m. La máscara ordena bien, pero no marca todas las copas.

## Píxel de 20 m

El Tp5 y el Tp6 corren a 20 m: en el Tp5 porque el mosaico ALOS-2 es de 25 m y no tiene sentido fabricar detalle de 10 m; en el Tp6 por el volumen de la serie temporal. El mapa de control debe tener **la misma grilla** que los mapas con los que se cruza; si se cambia el píxel de un práctico, se rehace el control con el mismo `--pixel`.

## El muestreo

- **Estratificado por clase del mapa evaluado**, no por clase del mapa de control: el estimador de Olofsson et al. (2014) usa como estratos las clases del mapa que se valida.
- **Centro del píxel.** La unidad de evaluación es el píxel de 20 m. Por eso en QGIS el punto se dibuja como un cuadrado de 20 m.
- **Semilla fija (2026).** El diseño se puede rehacer idéntico. Cambiar la semilla después de ver los resultados sería elegir la muestra que conviene: no se hace.
- **Orden mezclado.** Los `id` se asignan después de mezclar los puntos, para que quien etiqueta no deduzca el estrato por el número.
- **Mínimo por clase.** Con muy pocos puntos en una clase, su exactitud del usuario queda con un intervalo inútil. El script asigna un mínimo a las clases chicas y reparte el resto en proporción al área: un reparto intermedio entre el igual y el proporcional, como sugieren Olofsson et al. (2014). Informa la suma de n_i frente a n_total.
- **Tamaño.** Con U = 0,85 y S_O = 0,03 la ecuación 13 da unos 142 puntos. Con S_O = 0,05, unos 51. El script nunca baja del mínimo por clase multiplicado por el número de clases.

## El estimador

`Tp4_03` implementa las ecuaciones de Olofsson et al. (2014): matriz en proporción de área, exactitudes con sus varianzas, área por clase de referencia con su varianza, y la varianza de la exactitud del productor según la ecuación 7 del artículo. El IC es ±1,96 √V.

**Comprobado con el ejemplo publicado:** `--autoprueba` reproduce deforestación 21.158 ± 6.158 ha, usuario 0,88, productor 0,75 y global 0,95. Es la cifra que verifica las fórmulas, y se puede citar. Las cifras del ensayo en Concordia están más abajo.

## Archivos de trabajo

- **Capa para digitalizar.** `Tp4_01` crea `control_digitalizado_<SITIO>.gpkg` con la capa `control` declarada como polígonos (`Polygon`) en EPSG:32721, con los campos `codigo` (int32), `clase`, `fuente_interpretacion`, `fecha_imagen` e `interprete`. QGIS habilita la herramienta de dibujo directamente.
- **Protección del etiquetado.** Si `<NOMBRE>_puntos_a_etiquetar.gpkg` ya existe con al menos un `clase_ref` cargado, `Tp4_02` no lo reescribe y termina con un aviso. `--sobrescribir` fuerza un muestreo nuevo y borra el trabajo hecho: se usa sólo después de copiar el archivo etiquetado.
- **La clase en `Tp4_04`.** La tabla de `Tp4_03` lleva `codigo` (valor del mapa) y `clase` (nombre de `--nombres_clase`, o el código si no se dio). `--clase` acepta cualquiera de los dos.

## La comparación de variantes

`Tp4_04` decide con la omisión y la comisión de la clase de interés (la exactitud global queda como contexto): compara la mejor variante en cada medida con cada una de las otras por la diferencia, con su IC del 95 % (muestras independientes: V(d) = V1 + V2); si el intervalo de la diferencia incluye el cero, la mejora no está demostrada con esa muestra. Si los IC de las dos variantes se superponen pero la diferencia es significativa, la bitácora lo dice. Además avisa si las áreas estimadas de dos variantes son incompatibles.

Las cuatro variantes de un práctico se validan con muestras **distintas** (cada una se estratifica con sus clases). No son muestras pareadas. La alternativa recomendada es una sola muestra común (Stehman, 2014), implementada en `Tp4_06_muestra_comun.py`: estratos = combinaciones de las variantes (todas, ninguna, desacuerdo), estimación con la fórmula de estratos distintos de las clases y diferencias pareadas. Con los cuatro mapas del Tp5 son 200 puntos en lugar de unos 560. `Tp4_06` reproduce a `Tp4_03` cuando los estratos son las clases del mapa (MapBiomas: 0,568 ± 0,167).

## Limitaciones conocidas

1. **Las teselas de Esri y Google son recientes.** Para eventos de 2020, 2023 y 2024 hay que buscar imágenes fechadas (Google Earth Pro, imágenes históricas; Esri World Imagery Wayback; Carta Internacional, activación 880). Si no hay, se etiqueta con confianza baja o no se etiqueta.
2. **Referencia con Sentinel-2.** Si la única imagen de la fecha es Sentinel-2, la validación de la variante óptica queda sesgada a favor. Se declara.
3. **Carga de trabajo.** Cada variante necesita su muestra (unos 140 puntos con los valores por defecto). Cuatro variantes son unos 560 puntos por práctico (el Tp5 terminó con 711): se reparten entre grupos, se declara un S_O mayor o, mejor, se usa una muestra común con `Tp4_06`.
4. **Píxeles mezcla.** A 20 m, el borde entre quemado y no quemado o entre agua y tierra cae dentro de muchos píxeles. Se etiqueta la clase mayoritaria con confianza baja; la proporción de confianza baja se informa.

## Lo que se comprobó en la computadora del aula

- **JRC.** La lectura desde el Planetary Computer (colección `jrc-gsw`, activo `occurrence`) funciona: 422.856 píxeles de agua permanente en B_CONCORDIA y 87.462 en A1_DELTA_QUEMAS. Si la red del aula está lenta o inestable, `--sin_jrc` permite seguir.
- **Ciclo completo del ensayo.** Con 24 polígonos ubicados por sorteo y aceptados sólo en cubiertas homogéneas (100 puntos uniformes y sorteo estratificado por MapBiomas para humedal, monte y suelo desnudo; la clase otra quedó sin polígono) y el monte de MapBiomas recortado con las copas de 2 m, `Tp4_02 --SE 0.05 --minimo 10` dio 70 puntos y `Tp4_03` dio exactitud global 0,983 ± 0,021 (n = 70); monte 8 de 10 (los dos errores son plantaciones dentro del bosque de MapBiomas), área de plantación estimada 333 ± 397 ha (de 0 a 730 ha; productor 0,066), cultivo 17 ± 8 ha. El mismo ciclo con el monte sin recortar dio 0,856 ± 0,115: la diferencia (+0,127 ± 0,117) está demostrada. La llave es idéntica entre corridas con la misma semilla (`fc /b`) y la protección del etiquetado funciona.
- **Mensaje del tamaño de muestra.** `Tp4_02` ahora imprime por separado el n de la fórmula y el mínimo por clase, para que el alumno pueda comparar su cálculo a mano (antes imprimía sólo el n final).

## Limitaciones que dejó el ensayo

5. **El mapa de control no cubre el sitio.** En B_CONCORDIA el 89,3 % queda sin clase (84,6 % con el monte sin recortar). El área estimada y la exactitud se refieren sólo a la parte clasificada (18.505 ha con el monte recortado), no al sitio entero. Para los mapas de los Tp5 a Tp10, que cubren todo el sitio, esto no ocurre.
6. **Clases de referencia que el mapa no tiene.** `Tp4_03` no excluye esos puntos: los cuenta como error del mapa (columna de referencia sin estrato) y lo avisa. Con muchos, el mapa omite una clase entera: se declara.
7. **Sitios puros.** Los polígonos de control se aceptan sólo en cubiertas homogéneas: la exactitud del ensayo es optimista por diseño.
8. **Un solo intérprete.** Las etiquetas del Desarrollo las puso un único intérprete; `Tp4_07_acuerdo_entre_interpretes.py` deja preparados los puntos para el segundo y mide el acuerdo.

## MapBiomas 2025 como mapa a validar (paso 10)

- `Tp4_05` reclasifica la cobertura 2025 de MapBiomas Argentina (Colección 3, banda 41 del subset del Tp1) a las
  clases del curso, por vecino más cercano a la grilla del mapa de control. Cubre el 68,3 % de B_CONCORDIA. La clase 5 junta las
  herbáceas naturales con pastura y cultivos (`herbaceo_cultivo_pastura`); `--equivalencias` lee otra equivalencia de un CSV.
- 70 puntos (`--SE 0.05 --minimo 10`), etiquetados al azar sobre Esri y Google (vistas de 300 m y 1.200 m): exactitud
  global 0,568 ± 0,167 (n = 70; el punto de túneles no se excluye: cuenta como error del estrato de suelo desnudo).
  Agua y plantación sirven (usuario 1,00 y 0,80); monte (0,20) y humedal (0,10) no. El suelo desnudo de MapBiomas junta
  galpones, loteos, frutales jóvenes y cosechas: usuario 0,20 y área sobrestimada (1.127 ha frente a 225 ± 295).
  Con otras equivalencias, evaluadas con la misma muestra (`Tp4_06`), la exactitud va de 0,585 a 0,609.
- Con confianza alta coinciden 22 de 27 puntos; con baja, 1 de 16: los desacuerdos se concentran en cubiertas mixtas
  (espinal abierto, bordes de lagunas, plantaciones cosechadas entre las fechas de Esri y Google).
- Contexto (medianas por clase del mapa): CCI 2024 de 69 Mg/ha en plantación y 36 en monte; banda P VH de −14 a −17 dB
  en urbano, monte y plantación, −18 a −21 dB en humedal, suelo y cultivo, −29 dB en agua.
- Limitación: las etiquetas del desarrollo las puso un único intérprete sobre vistas exportadas y las revisa el docente;
  en el aula las pone un grupo en QGIS y se mide el acuerdo entre intérpretes (`Tp4_07`) en al menos diez puntos.

**IC nulos o indefinidos en Tp4_04.** Cuando una variante no tiene puntos de referencia de la clase de interés en un estrato (o los tiene todos en una celda de la matriz), la omisión o la comisión sale con IC 0 o indefinido. Eso no es una medición exacta: es falta de puntos. `Tp4_04` ya no declara «significativa» una diferencia contra un IC nulo: escribe «NO SE PUEDE DECIDIR» y no compara esas áreas. En el Tp9 pasó con la variante solo banda L (ningún punto de pérdida en 142) y con la omisión del solo óptico (0 de 107 en el estrato «no»).

## Corrida del 28/10/2026: acuerdo entre intérpretes

- Segundo intérprete con CBERS-4A 2 m del 15/07/2026 y Sentinel-2 del 16/09/2026 (falso color 8-4-3), en orden de id. Control: 32 de 58 (0,55; kappa 0,47); MapBiomas: 21 de 37 (0,57; kappa 0,44); 12 y 33 puntos bajo nubes. No acepta el control 11: los desacuerdos están entre pajonal, monte, plantación y loteo, que necesitan imágenes submétricas como las del primer intérprete (Esri y Google).
