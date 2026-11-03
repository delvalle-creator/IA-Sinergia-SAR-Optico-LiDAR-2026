# Tp10 — Notas técnicas

> **Qué es este archivo.** Las decisiones técnicas del práctico, su fundamento y las limitaciones conocidas. No es el punto de entrada: para saber qué hay en cada carpeta, abra `00_LEEME.md`; para hacer el práctico, `00_Guia_del_practico/00_LEEME.md`.

**Pregunta:** ¿cómo crece la ciudad y dónde se hunde el terreno? Sitios `B_CONCORDIA` (urbano) y `E_PARANA_DIAMANTE` (subsidencia).

## Qué datos entran y en qué unidad

| Sensor | Banda | Producto | Fecha | Unidad | Origen |
|---|---|---|---|---|---|
| Sentinel-1 | C (5,5 cm) | IW GRD RTC, VV y VH | La más cercana al 16/09/2026 (± 6 días) | γ⁰ lineal | Microsoft Planetary Computer, `sentinel-1-rtc` |
| NovaSAR-1 | S (9,4 cm) | Stripmap GRD HH, 6 m, escena 47942 | 13/09/2023, 01:36 UTC | **σ⁰** lineal = DN² / 1E+05 | Archivo del curso (SSTL – CSIRO) |
| NISAR | L (24 cm) | L2 GCOV, frecuencia A, HHHH y HVHV | 18/09/2026, descendente | γ⁰ lineal | ASF DAAC (bajado con `Tp1_04`) |
| Sentinel-2 | Óptico | L2A, B04, B08, B11, SCL | La más limpia en el sitio en ± 10 días del 16/09/2026 | Reflectancia 0 a 1 | Planetary Computer, `sentinel-2-l2a` |
| Sentinel-1 | C | IW SLC → interferogramas HyP3 INSAR_GAMMA | búsqueda 01/01/2025 a 30/09/2026; pares usados del 01/06/2025 al 03/07/2026 | m (desplazamiento), 0–1 (coherencia) | ASF DAAC / HyP3 |

## Decisiones y su fundamento

**Radar en lineal; dB para umbralizar, clasificar y mostrar.** El promedio de los logaritmos no es el logaritmo del promedio: remuestrear o promediar en dB sesga hacia valores bajos (diapositiva 14). Todos los rásters se guardan en lineal; el clasificador recibe dB porque la escala logarítmica hace comparables las colas de los distintos sensores, y eso se dice.

**NovaSAR queda en σ⁰.** El curso no tiene un modelo de ángulo local para llevarlo a γ⁰ fuera de SNAP. Sentinel-1 RTC y NISAR GCOV vienen en γ⁰. En Concordia el relieve es suave y la diferencia es menor que en terreno montañoso (Small, 2011), pero no es cero: entre bandas, compare formas y contrastes, no valores absolutos. Mezclar σ⁰ y γ⁰ sin decirlo es uno de los errores de la diapositiva 14.

**NovaSAR remuestreado con media cuadrática de los DN.** rms(DN)² = media(DN²) = media de la potencia: el píxel de 20 m promedia potencia y recién después se calibra.

**Georreferencia de NovaSAR.** El `image_HH.tif` trae sólo las cuatro esquinas como puntos de enlace: la proyección es un ajuste de la franja entera y deja desplazamientos de cientos de metros (el código de `00_COMUN` registra desfases de hasta 1120 m medidos en la presentación 02 entre COSMO-SkyMed, NovaSAR y SAOCOM y Sentinel-2). Se mide con `Tp3_02` y, si el corrimiento es rígido, se corrige con `--desplazamiento DX DY` en metros (en la 47942 no lo es: ver «Hallazgos con datos reales»), en el sentido en que lo informa `Tp3_02` (este y norte positivos). A 6 m, un error de 80 m son 13 píxeles: sin corregir, la tabla de detalle no tiene sentido.

**Máscara de NISAR.** Dataset `mask`: 0 = inválido, 255 = fuera de la adquisición, 1..n = válido. Sin ella, los bordes de la pasada entran con valores del orden de −133 dB. Sólo frecuencia A; la B (80 m) no se usa.

**Umbrales manuales de −3 dB por defecto.** La ciudad es una fracción chica del sitio y su moda casi no se ve en el histograma: Otsu, que supone dos modas, cae en cualquier lado (con `--otsu`, el 27/10/2026: −11,6 dB en C, −8,3 en S y −10,1 en L, que marcan el 58, 54 y 57 % del sitio: separa el agua de la tierra, no la ciudad). El −3 dB es un punto de partida que el grupo confirma con el histograma y con los polígonos urbanos del control, y anota. Es el mismo valor para C, S y L por simplicidad, no porque la física lo exija: cada banda tiene su rango.

**Grilla de 20 m en los pasos 2 a 6.** Es la de NISAR GCOV y la de la B11 de Sentinel-2 (NDBI). Trabajar a 10 m inventaría detalle que la banda L y el SWIR no tienen. El detalle fino se estudia aparte, con NovaSAR a 6, 10 y 20 m.

**La tabla de coincidencias usa sólo píxeles con todas las bandas.** Si NovaSAR entra, la sinergia se mide en su huella (39 % del sitio). Es correcto —no se comparan bandas donde una no existe— y hay que decirlo.

**Dos versiones del clasificador.** El Random Forest sólo clasifica píxeles con todas las capas. Con NovaSAR al 39 %, una sola versión con banda S dejaría el 61 % del sitio sin mapa; una sola sin S no permitiría saber qué aporta S. Las dos versiones y su acuerdo son la medida honesta del aporte de la banda S. La variante multisensor que va al Tp4 sale de `sin_S` porque es la que cubre el sitio. La versión `con_S` se escribe además como `<SITIO>_variante_multisensor_con_S.tif` (sólo la huella de NovaSAR), para validarla aparte en el Tp4: su exactitud vale para esa huella.

**Fusión de rasgos.** El clasificador recibe valores de los radares en dB y además NDBI, NDVI, MNDWI y la textura de VV, que son variables derivadas. Según la regla 5 del proyecto y el glosario, es fusión de rasgos (el mismo nombre que en el Tp8 y el Tp9). La validación es la misma (Tp4). La importancia de Gini no reparte el aporte entre sensores: favorece variables continuas y correlacionadas; el aporte de cada sensor se mide con las variantes del Tp4.

**Exactitud fuera de bolsa: optimista.** Se calcula con píxeles vecinos de los mismos polígonos de entrenamiento. La exactitud que se informa es la del Tp4, con puntos estratificados etiquetados al azar (Olofsson et al., 2014).

**Expansión por comparación posterior a la clasificación.** El método tiene que ser el mismo en 2019 y en 2026. NovaSAR y NISAR no existen en 2019: el clasificador del paso 6 no se puede aplicar a la base. Cada año se clasifica con una fusión de rasgos Sentinel-1 + Sentinel-2 (Random Forest, compuestos y MapBiomas del año) y una regla compara los dos mapas: cambio sólo si la probabilidad es ≥ 0,6 en las dos fechas y la mancha tiene ≥ 5 píxeles. La regla no fusiona sensores, compara decisiones de dos fechas. Es asimétrica: la probabilidad mínima se exige sólo para el cambio, no para las clases 1 y 3; la matriz de transiciones (`_expansion_matriz_transiciones.csv`) lo deja a la vista. El aviso de clase 4 salta al 20 % de la clase 2 (`--aviso_clase4`), el mismo umbral de la verificación. 2019 es el primer año completo con Sentinel-2 L2A producido de forma sistemática fuera de Europa (desde fines de 2018) y con los dos satélites.

**Píxel de la expansión.** 20 m por defecto, el de la B11 que entra al NDBI: a 10 m su valor se repetiría en cuatro píxeles y el detalle sería aparente.

**Misma órbita en la expansión.** El doble rebote depende de la dirección de vuelo. `Tp10_03` resuelve primero la fecha final, toma la órbita relativa de esa Sentinel-1 y busca la base en la misma órbita (`s1_rtc_mas_cercana(..., orbita=...)`), en ± `--dias` (12) días: la revisita de una órbita con un satélite.

**Subsidencia por apilado de tasas.** Velocidad = Σ desplazamientos / Σ intervalos (equivale a promediar la tasa de cada par pesándola por su intervalo: un par de 48 días pesa cuatro veces más que uno de 12), con los pares de coherencia ≥ 0,3 en cada píxel. Un píxel tiene velocidad sólo si es coherente en al menos el 90 % de los pares que lo cubren (`--frac_min`): no todos los pares cubren todo el sitio (Diamante entra en 106 de 120), así que el porcentaje se cuenta sobre los pares que cubren cada píxel. La atmósfera, aleatoria en el tiempo, se promedia; la deformación constante se acumula. Da la velocidad media, no la serie temporal: no es una inversión SBAS (eso lo hace MintPy o LiCSBAS; Morishita et al., 2020). Píxel de 40 m: el de los productos HyP3 con 10 × 2 looks (con 20 × 4 looks sería de 80 m).

**Referencia y control.** Cada interferograma tiene una constante arbitraria del desenrollado: se resta la mediana de la zona de referencia de cada par. Sin referencia se usa la mediana de los píxeles persistentes (coherentes en ≥ 90 % de los pares que los cubren, casi siempre zona construida): si toda esa zona se mueve, queda escondido. No se usa la mediana de todos los píxeles coherentes: en este sitio son sobre todo campos e islas, con sesgo de fase propio, y hacían aparecer a Paraná y Diamante «subiendo» 12 a 18 mm/año. La referencia se rasteriza con todos los píxeles que toca cada polígono (un edificio o un puente es más chico que 40 m); con menos de 10 píxeles, la bitácora avisa. El control son puntos estables fuera de la referencia: los que caen fuera de la grilla o dentro de la referencia se excluyen con aviso. Criterio (desde el 27/10/2026): la referencia se acepta si el valor absoluto de la media es menor que 2 × error de la media (desvío / raíz de n). El criterio anterior (la media más cerca de 0 que el desvío) era débil: el desvío no achica con más puntos. Además, cada par se revisa por saltos de desenrollado: se marca «sospechoso» si más del 20 % de sus píxeles coherentes queda a más de 35 mm (media longitud de onda en vertical) de la mediana del par; con `--descartar_saltos` no entra.

**Red de pares de línea de base corta.** Cada fecha se une con sus `--vecinos` (2) siguientes, con `--dias_max` (48) y `--base_max` (150 m). Un par sin base perpendicular conocida (después de pedir la pila de cada escena) se acepta por tiempo si las dos escenas son del mismo satélite o si ASF no devolvió ninguna base; si son de satélites distintos, se rechaza. La nota queda en la tabla y la bitácora los cuenta.

**Componente vertical.** HyP3 calcula el desplazamiento vertical a partir del de línea de visión suponiendo que no hay movimiento horizontal. En la barranca, donde sí lo hay, el valor «vertical» mezcla componentes.

## Limitaciones conocidas

1. **NovaSAR cubre el 39 % de Concordia.** La otra escena con la misma hora de pasada (50896, 22/12/2023) no cubre Concordia: cubre el 51 % de Federal. No hay otra banda S para este sitio.
2. **Tres años entre NovaSAR (2023) y C y L (2026).** Lo que aparece urbano sólo en C y L puede ser crecimiento real.
3. **El doble rebote depende de la orientación de las calles** respecto de la dirección de vuelo: una manzana girada 45° puede verse oscura en una banda y brillante en otra de distinta órbita.
4. **La red de pares se arma con un vecindario fijo** (`--vecinos`, 2 fechas siguientes): con revisita irregular puede quedar cortada; la bitácora lo avisa.
5. **`dispersion_entre_pares_mm_por_anio`** es la dispersión de las velocidades de cada par alrededor de la velocidad apilada, no el error estándar de la velocidad; los pares cortos pesan mucho. No es un intervalo de confianza.
6. **PS (dispersores persistentes) no se hace:** necesita StaMPS o SARPROZ y más de 20 SLC corregistrados.
7. **La ventana de 13 meses de la subsidencia** (01/06/2025 a 03/07/2026) no es un número entero de años: una señal estacional (humedad del suelo, arcillas) puede no cancelarse.
8. **Alturas de edificios con MDE o LiDAR** (diapositiva 33, «MDE y alturas LiDAR ○») no se implementaron en los scripts del Tp10.
9. **La ventana de Paraná – Diamante es aproximada** (`origen: aproximada` en `configuracion_comun.py`).

## Estado de prueba

Las consultas al Planetary Computer y a ASF no pudieron probarse desde el entorno de desarrollo (sin red hacia esos servicios). `Tp10_01`, `Tp10_02` y `Tp10_03` dependen del Planetary Computer; `Tp10_04`, de ASF y HyP3; `Tp10_05` lee productos HyP3 locales cuyo nombre debe seguir el patrón de HyP3 (`..._AAAAMMDDThhmmss_AAAAMMDDThhmmss_..._vert_disp.tif`). El docente corrió `Tp10_04` y `Tp10_05` con los datos reales el 20/10/2026 (resultado más abajo). Las cifras de `Tp10_01`, `Tp10_02` y `Tp10_03` no se informan aquí: se producen en clase.

## Hallazgos con datos reales del curso que afectan al Tp10

- NovaSAR 47942 (13/09/2023) cubre el 39 % de `B_CONCORDIA`; 50896 (22/12/2023), aunque tiene la misma hora de pasada, no cubre Concordia.
- NovaSAR 47974 (Bovril) necesitó desplazarse unos 80 m al oeste y 20 m al norte para corregistrar con Sentinel-2.
- NovaSAR 47942 (Concordia), medida el 20/10/2026 con `Tp3_02` a 20 m contra Sentinel-2 B08 del 16/09/2026: 2 ventanas válidas, mediana −9 m este y −308 m norte, pero las ventanas no coinciden (≈ 200 y ≈ 420 m): **corrimiento no rígido** (`NO CUMPLE`). Un desplazamiento único no lo corrige; la guía (paso 1) da las dos salidas posibles.
- NISAR: en los bordes de la pasada aparecen valores de −133 dB si no se aplica la máscara del producto.
- No hay banda L durante la crecida de Concordia de noviembre de 2023: la banda L del Tp10 es NISAR 2026, no un dato contemporáneo de NovaSAR.

**Resultado de la corrida docente (20/10/2026, 120 pares HyP3 del 01/06/2025 al 03/07/2026, órbita 141 descendente).** Con referencia automática: Paraná +4 mm/año de mediana, Diamante −3,5, San Benito −0,6, Oro Verde +2,8. El corrimiento de Paraná desaparece cuando el grupo digitaliza su referencia sobre edificios antiguos. Quedan manchas rurales aisladas de 0,3 a 0,8 km² con −25 a −43 mm/año, lejos de la barranca: no son creíbles como subsidencia lineal. Dos explicaciones, que el apilado de pares cortos no separa: (1) sesgo de fase por humedad del suelo y vegetación (De Zan et al. 2014; Ansari et al. 2021; ver `06_Bibliografia/referencias.md`); (2) movimiento real de contracción y expansión de Vertisoles (gilgai), que es estacional: en una ventana de 13 meses deja una «tendencia» si el suelo terminó más seco que al empezar. Las dos dependen del suelo. Prueba posible: superponer las manchas con la carta de suelos del INTA y con la serie de precipitación; para separarlas hace falta la serie de tiempo fecha por fecha (MintPy), no el apilado. Sirve para la pregunta de limitaciones.

**Corrida del docente del 23/10/2026 (desarrollo del Tp10).**

- NovaSAR 47942 con `--puntos_enlace todos` (84 puntos de enlace del `metadata.xml`): queda un corrimiento casi rígido de unos 40 m al oeste y 100 m al norte, medido por correlación contra el VV de Sentinel-1 en 11 ventanas. Con `--desplazamiento -40 100`, el residual en 113 ventanas de 2 km tiene una mediana de 20 m y un percentil 90 de 40 m, casi todo este–oeste.
- Umbrales del paso 2 elegidos con los polígonos de entrenamiento: C VV −6 dB (71 % del urbano denso, 0 % de vegetación), S HH −3 dB (84 % y 0 %), L HH 0 dB (92 % y 4 %). Con −3 dB, la C marcaba sólo un tercio de la ciudad y la L, el 15 % de la vegetación.
- Paso 7: la órbita 68 de Sentinel-1 RTC empieza el 14/10/2019 en el Planetary Computer; con `--base 2019-09-15` falta Sentinel-1. Con `--base 2019-10-14 --u_vv -6`: 593,6 ha de nuevo urbano y 1.308,4 ha de clase 4. La expansión píxel a píxel entre dos fechas sueltas no se distingue del ruido; MapBiomas da 44 ha nuevas entre 2019 y 2025 del lado argentino.
- Paso 11, 568 puntos etiquetados al azar: comisión de urbano 0,636 ± 0,167 (óptico), 0,455 ± 0,173 (C), 0,526 ± 0,161 (multisensor) y 0,585 ± 0,153 (multisensor con S, en la huella de NovaSAR). Ninguna mejora demostrada.
- Paso 10 con referencia en el casco (6 cuadrados de 120 m) y 15 puntos de control: media −1,5 ± 4,8 mm/año en el control; cumple el criterio.

## Corrida del 24/10/2026: compuestos de temporada y entrenamiento proporcional (Tp10_02 y Tp10_03)

- Tp10_02 y Tp10_03 se reescribieron (respaldo .bak_20261024comp). Compuestos: Sentinel-1 RTC, media lineal de 5 pasadas de la orbita 68; Sentinel-2 L2A, mediana de hasta 5 escenas sin nube (SCL). El Sentinel-2 del 04/09/2026 se excluye (--excluir): es la referencia del Tp4.
- Entrenamiento: 20.444 pixeles estables de MapBiomas (2023-2025), en proporcion al paisaje (minimo 600 por clase), funcion entrenamiento_mapbiomas() de 00_COMUN/funciones_comunes.py. fusion_pixel_o_rasgo() tiene ahora equilibrar=True/False (por defecto True, como antes, para los demas practicos).
- Con 10 poligonos por clase y clases equilibradas el mapa marcaba 13.425 ha urbanas y la comision era 0,53. Con el entrenamiento proporcional: 5.615 ha, comision 0,196 +/- 0,110 (multisensor), 0,255 (C + L), 0,314 (optico), 0,471 (C). Multisensor mejor que C con IC no superpuestos.
- Validacion: Tp4_02 con --minimo 50; 710 puntos etiquetados al azar (semilla 1024); los puntos anteriores quedaron en Tp4_Validacion/04_Tablas_de_trabajo/respaldo_Tp10_20261023.
- Expansion (comparacion posterior a la clasificacion, p >= 0,6 y mancha >= 5 pixeles): 38,6 ha nuevas sobre 4.371,7 ha (0,9 %), 11,0 ha clase 4, 2.510,2 ha sin decidir. MapBiomas: 44 ha nuevas 2019-2025 del lado argentino.
- Tiempos en la computadora del docente: Tp10_02 17 min; Tp10_03 34 min.

## Historial de los scripts (trasladado desde las docstrings el 27/10/2026)

- `Tp10_02_fusion_pixel_urbano.py`, versión del 24/10/2026: compuestos de temporada en lugar de escenas sueltas; entrenamiento de MapBiomas en proporción al paisaje en lugar del mismo número de píxeles por clase con `class_weight="balanced"` (que sobrestimaba la ciudad: comisión de 0,53 en Concordia); una variante por conjunto de sensores con el mismo clasificador y el mismo entrenamiento.
- `Tp10_03_expansion_urbana.py`, versión del 24/10/2026: la versión anterior comparaba una escena de cada año con umbrales fijos (VV > u dB y NDBI > u) y la «ciudad que desaparece» salía más grande que la expansión; ahora compara dos clasificaciones con compuestos y exige cambio confiable.
- 27/10/2026 (auditoría): `Tp10_01` usa por defecto los 84 puntos de enlace (`--puntos_enlace todos`) y una unidad mínima de 1.200 m² para el detalle (`--umm_m2`); `Tp10_03` guarda la matriz de transiciones y avisa al 20 %; `Tp10_04` dibuja la red completa; `Tp10_05` informa el error de la media, aplica el criterio de 2 errores, controla saltos de desenrollado y escribe sus bandas como `velocidad_mm_por_anio` y `dispersion_entre_pares_mm_por_anio`. Comentarios y mensajes con tildes (UTF-8).

## Corrida del 28/10/2026: referencia revisada por dos intérpretes

- 243 puntos (193 de confianza media o baja y 50 de alta) revisados sin ver la etiqueta de la IA. A: CBERS-4A 2 m del 15/07/2026 (Sentinel-2 10 m del 16/09/2026 fuera de la escena); B: Sentinel-2 del 16/09/2026, color natural y falso color 8-4-3. Acuerdo 91,2 %, kappa 0,82 en 194 puntos; 34 no interpretables por nubes (sin etiqueta). Consenso: mayor confianza; empate, A.
- Tp4_03 (5 variantes), Tp4_04 y Tp10_06 corridos de nuevo (00_COMUN/09_Herramientas/ETIQUETADO_28_10.bat). Multisensor: comisión 0,143 ± 0,099, usuario 0,857 ± 0,099, productor 0,555 ± 0,342, área 8.676 ± 5.351 ha.
- Franja de 1 km etiquetada por los mismos intérpretes (acuerdo 88 %, kappa 0,27): con tres estratos, área urbana 6.023 ± 938 ha (`area_urbana_tres_estratos_multisensor.csv`).
