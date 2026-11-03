# Tp2 — Notas técnicas

> **Qué es este archivo.** Las decisiones técnicas del práctico, su fundamento y los
> errores que ya costaron tiempo. Para el recorrido, `00_LEEME.md`; para los pasos,
> `00_Guia_del_practico/00_LEEME.md`; para los grafos, `09_Grafos_SNAP/LEEME_grafos.md`.

## Unidades

- **γ⁰ lineal para todo cálculo; dB sólo para ver y umbralizar.** Con speckle, la
  distribución de la intensidad es muy asimétrica: el promedio de los dB es menor que
  el dB del promedio, y la diferencia crece con la varianza. Promediar en dB sesga
  hacia abajo y sesga distinto a bandas con distinto speckle.
- **Cambios entre fechas** como cociente de potencias en lineal expresado en dB:
  10·log10(post/pre). Es lo mismo que restar dB **sólo** si cada lado se promedió antes
  en lineal.
- **NovaSAR-1 queda en σ⁰** (σ⁰ = DN² / CalibrationConstant, 1E+05 en las cinco
  escenas). El curso no tiene un modelo de ángulo local para normalizarlo a γ⁰ fuera de
  SNAP, y se dice en el nombre de la banda. En el Delta, casi plano, la diferencia
  entre σ⁰ y γ⁰ depende sobre todo del ángulo de incidencia a lo ancho de la franja, no
  del relieve: no es despreciable al comparar con NISAR.
- **El RGB es de 8 bits y no se mide sobre él.**

## Calibración y normalización

- **β⁰ antes del Terrain Flattening.** El operador lo exige: normaliza β⁰ por el área
  iluminada simulada con el modelo de elevación y devuelve γ⁰ (Small, 2011).
- **El ángulo de incidencia local es diagnóstico, no corrección.** Aplicarlo de nuevo
  después del Terrain Flattening corrige dos veces lo mismo.
- **NISAR GCOV ya viene en γ⁰** y georreferenciado: no pasa por SNAP. Se usa sólo la
  frecuencia A; la B (80 m en los GCOV de banda L del curso) no se usa.

## Georreferencia y grilla

- **EPSG:32721 y 10 m**, bordes de píxel en múltiplos de 10 m. En SNAP eso se logra
  con `alignToStandardGrid` y origen 5, 5 en el `Terrain-Correction`: SNAP alinea los
  centros de píxel al origen, y con 5, 5 los bordes caen en 0, 10, 20…
- **Agregación:** píxel de origen más fino que 10 m → promedio de potencia
  (`average` sobre lineal; en NovaSAR, media cuadrática `rms` de los DN antes de
  calibrar). Píxel igual o más grueso (NISAR de 20 m) → bilineal. Interpolar a un píxel
  más fino no agrega información: la pila de 10 m no tiene más detalle que su banda más
  gruesa, y el Tp3 trabaja por eso a 20 m.
- **NovaSAR se proyecta con sus cuatro puntos de esquina** (GCP) y puede estar corrido
  cientos de metros. La escena 47974 necesitó desplazarse 92 m al oeste y 484 m al sur
  para corregistrar con Sentinel-2 (medido con `Tp3_02` en el Tp3). El desplazamiento se mide
  con `Tp3_02` y se aplica en `Tp2_01` con `--desplazamiento DX DY` (metros; DX
  positivo = hacia el este, DY positivo = hacia el norte): para la 47974,
  `--desplazamiento -92 -484`. Sin ese argumento la pila toma NovaSAR sin corregir y la
  bitácora lo avisa.

## NISAR: la máscara

La máscara del GCOV vale 0 (muestra inválida o parcialmente enfocada), 255 (fuera de la
adquisición) o 1 a n (número de subfranja, válida). Sin aplicarla, en los bordes de la
pasada aparecen valores de alrededor de **−133 dB**, que arruinan cualquier promedio.
`nisar_gcov_en_grilla()` la aplica siempre y además descarta los valores ≤ 0.

## Speckle

- **Fuera del grafo, como paso aparte**, para ver su efecto solo: el mismo producto
  antes y después.
- **Se aplica sobre el producto ya proyectado** (la salida del grafo), en lineal. La
  alternativa es filtrar en geometría de radar, antes de la corrección del terreno;
  conviene cuando la escena tiene relieve fuerte. En el Delta la diferencia es menor.
- **Refined Lee o Lee Sigma**, y todo el grupo usa el mismo. Los parámetros de Lee
  Sigma se dejan por defecto y se anotan.
- El filtro conserva aproximadamente la media lineal y reduce el desvío. No reemplaza
  la agregación: una media sobre un polígono de 200 píxeles ya promedia el speckle.

## Umbrales y por qué

| Umbral | Valor | Dónde | Fundamento |
|---|---|---|---|
| Fracción mínima del sitio con dato para entrar a la pila | 20 % (`--min_validos`) | `Tp2_01` | Una banda que cubre menos de un quinto del sitio no permite comparar cubiertas en todo el sitio |
| Píxeles mínimos por clase | 200 (aviso) | `Tp2_03` | Con menos, la media de una cubierta queda dominada por el speckle |
| Estiramiento del RGB | 2–98 % por canal | `Tp2_02` | Descarta los extremos (esquinas brillantes, borde) sin recortar las cubiertas |
| Zona estable | \|dif. de medias\| < 1 dB | `Tp2_04` | Criterio de la presentación 01, diapositiva 25: más de 1 dB en una superficie que no cambió es calibración, normalización, órbita o corregistro. Es del orden de la exactitud radiométrica absoluta: 1,0 dB (3σ) para Sentinel-1 (ESA; Schmidt et al., 2018) y menos de 0,9 dB (copolarizada) y 1,2 dB (cruzada) para NISAR (Chapman, 2019). Entre fechas se usa lo estable; entre procesadores del mismo día, cubiertas homogéneas |
| Píxeles estables en común | ≥ 50 | `Tp2_04` | Por debajo, la diferencia de medias no es estable |

## Detalles del código que conviene conocer

- **GeoTIFF exportado desde SNAP:** `Tp2_01` lee **la primera banda** de cada archivo
  de `--extra`. Por eso se exporta una banda por archivo.
- **Forma de `--extra`:** `"nombre_de_banda=ruta.tif|sensor|lambda_cm|AAAA-MM-DD"`.
  Sensor, longitud de onda (cm) y fecha son opcionales para el programa, pero deben
  ponerse: con ellos se completa `<SITIO>_pila_bandas.csv` y el Tp3 arma la tabla de
  fechas. Sin ellos la banda queda con sensor `SNAP`, sin longitud de onda ni fecha, y
  la bitácora avisa `AVISO: sin fecha`.
- **GeoTIFF lineal:** se lleva a la grilla común promediando la potencia (`average`).
- **GeoTIFF en dB (nombre terminado en `_db`):** se pasa a lineal en su grilla
  original y recién después se promedia a la grilla común (`leer_db_como_lineal()`).
  El sufijo `_db` se quita del nombre de la banda, que en la pila queda en lineal.
- **Las bandas `--extra` no llevan fecha en el nombre**, de modo que el paso 8 no las
  empareja solo: se piden con `--a` y `--b`.
- **Emparejamiento automático del paso 8:** compara bandas cuyo nombre sólo difiere en
  la fecha final `_AAAAMMDD`. En la práctica, las fechas de NISAR.
- **Fecha de NISAR:** `Tp2_01` la toma del nombre del granulo (el campo de fecha y hora
  de inicio de la convención de nombres de NISAR). Si un granulo tiene otro patrón de
  nombre, la banda queda sin fecha: compárela con el `zeroDopplerStartTime` que lista
  `Tp1_02`.
- Las bitácoras y las tablas se reescriben en cada corrida del mismo script y sitio.

## Limitaciones conocidas

- La consulta al Planetary Computer (Sentinel-1 RTC) se probó en la computadora del aula el
  21/10/2026 y funciona. Si ese día no responde, la banda C se toma del procesamiento propio
  en SNAP.
- `A2_IBICUY` es una ubicación aproximada.
- COSMO-SkyMed (X) es de Diamante: sobre Ibicuy no entra.
- BIOMASS banda P **sí cubre Ibicuy**: L1B DGM del 05/10/2026 en `02_Subsets_SNAP_QGIS`. Está
  en geometría de rango en el terreno, con 121 puntos de enlace y sin proyección; γ⁰ se calculó
  sobre el elipsoide (sin corrección por pendiente, que en el Delta no hace falta). `Tp2_01` lo
  reproyecta con los puntos de enlace (`--extra "...tif#1"` y `"#3"`: HH y VH). El canal HV
  (`#2`) trae interferencia de radiofrecuencia que ESA detectó y no corrigió
  (`rfiCorrectionFlag = false`): en el recorte, 111 líneas de acimut hasta 3 dB por encima de
  sus vecinas, contra 25 líneas de menos de 2 dB en el VH. Por reciprocidad HV y VH miden lo
  mismo: la cruzada de P es la VH. El corregistro con el
  resto de la pila se midió en el Tp3 con `Tp3_02` (21/10/2026): frente a Sentinel-2 B08, hay que
  mover la P VH 12 m al oeste y 6 m al norte (0,67 píxel de 20 m, CUMPLE); frente a NISAR L HV,
  9 m al oeste y 4 m al norte (0,49 px). Una prueba rápida previa contra Sentinel-1 había dado
  30 a 50 m: era una sobreestimación (el RTC de Sentinel-1 tiene además su propio corrimiento).
- Los SAOCOM de 2020 (γ⁰ en `Tp5_Incendios\02_Subsets_SNAP_QGIS\SAOCOM_gamma0`) cubren
  el sector de las quemas (`A1_DELTA_QUEMAS`), no Ibicuy; sus fechas distan seis años de
  NISAR: en la misma pila son interpretación histórica, no comparación simultánea.
- La escena GRD del paso 1 es la del 26/09/2026 (Sentinel-1C, órbita 68, descendente),
  en `00_COMUN\08_Originales_crudos\S1_CRUDO`; el docente la dejó además procesada en
  `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo` para comparar.

## Hallazgos con datos reales del curso

- NISAR L y S (si existe la banda S para el Delta): el corregistro entre ambas se mide en el Tp3; se espera menos de medio píxel porque los dos GCOV vienen en la misma grilla geocodificada.
- NISAR: en los bordes de la pasada aparecen valores de **−133 dB** si no se aplica la
  máscara del producto.
- NovaSAR **47974**: `Tp3_02` midió 92 m al oeste y 484 m al sur, con una deformación no
  rígida (la presentación 02 daba unos 80 m al oeste y 20 m al norte).
- NovaSAR 47974 cubre el **92 %** de `F_BOVRIL`; 47942, el **39 %** de `B_CONCORDIA`.
- Banda P en Ibicuy (polígonos sorteados, 22/10/2026): la cruzada VH del pajonal queda 13,4 dB por debajo de la del monte
  (en C son 2,2 a 2,6 dB y en L HV, 7,2 dB); con los polígonos ubicados a mano (21/10) eran 10,6, 3 y 5 dB. Sobre todo el sitio, con las clases de MapBiomas 2025, la diferencia
  de medianas entre bosque cerrado y herbáceas inundables es de 2,6 dB en C, 1,9 en S, 7,3 en L y
  12,6 en P (VH).
- MapBiomas Argentina cubre Entre Ríos: el 30 % de `A2_IBICUY` (al sur del Paraná Guazú) queda sin
  dato.
- `leer_en_grilla` (00_COMUN/funciones_comunes.py) ahora acepta rásteres sin proyección con
  puntos de enlace (BIOMASS L1B): antes los devolvía enteros sin dato, sin aviso.
- ALOS-1 PALSAR FBS 2011 es sólo HH: si se suma ALOS 2011 a una pila, no hay RGB dual
  para esa fecha.

## Cambios del 27/10/2026 (auditoría académica)

- `--extra` acepta la unidad (`gamma0`, `gamma0E`, `sigma0`) y la pasada y traza; la tabla
  de bandas del Tp2 declara la banda P como «gamma0 elipsoidal lineal» y lleva la pasada
  de los productos de SNAP (D 68) y de BIOMASS (A 006).
- `Tp2_03` escribe la media de cada polígono (`<SITIO>_media_por_poligono.csv`), el rango
  de medias por clase y la separabilidad M = |μ1 − μ2| / (σ1 + σ2) de cada par; la figura
  de cajas sale en dos filas, en orden físico de clases y con un color fijo por clase.
- `Tp2_04` informa la diferencia de cada polígono y un intervalo del 95 % por remuestreo de
  polígonos (2.000 repeticiones, semilla 20261022); con `--clase` acepta varias clases y con
  `--sufijo` la tabla y la bitácora de cada corrida no se pisan. El umbral de 1 dB se apoya en la
  exactitud radiométrica absoluta de Sentinel-1 (1 dB, 3σ; Schmidt et al., 2018).
- `Tp2_02` agrega `--rango_fijo` y pone en el PNG coordenadas, escala, norte y la cita sin
  rutas locales.
- `Tp2_05_saocom_por_cubierta.py` (nuevo, para profundizar): SAOCOM cuadripolar por clase,
  fuera de la banda de ruido del borde este (al este de 299.400 m).
- Paleta única de clases en QGIS (`cubiertas_A2_IBICUY.qml`), Orange (cabecera de los
  `.tab`) y figuras: agua calma #1f3a93, agua rizada #4fa3e0, pajonal #e6c229, suelo
  desnudo #f4a6c6, monte #1b8a3a, urbano #d62728, estable #7f7f7f (en los mapas sobre imagen,
  estable va en blanco para que se vea sobre lo oscuro); cultivo #ff7f0e.
