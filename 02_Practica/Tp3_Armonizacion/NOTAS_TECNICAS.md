# Tp3 — Notas técnicas

> **Qué es este archivo.** Las decisiones técnicas del práctico, su fundamento y los
> errores que ya costaron tiempo. Para el recorrido, `00_LEEME.md`; para los pasos,
> `00_Guia_del_practico/00_LEEME.md`.

## Los tres requisitos de la fusión, y dónde se comprueban

| Requisito | Dónde | Cómo |
|---|---|---|
| Misma grilla | `Tp3_01` | `grilla_sitio(sitio, pixel)`: EPSG:32721, bordes en múltiplos exactos del píxel. Todas las capas se escriben en un mismo GeoTIFF |
| Corregistro < 1 píxel | `Tp3_02` | Correlación de fase sobre mapas de bordes, por ventanas. Fusión de píxel: módulo < 0,5 px, dispersión < 0,5 px y rango < 1 px. Rasgo o decisión: < 1 px y rango < 2 px |
| Fechas compatibles | `Tp3_01` y `Tp3_03` | Diferencia en días por par de sensores y por huella-capa |

«Compatible» no tiene un umbral único: depende del fenómeno. La altura de un monte no
cambia en meses; la extensión del agua en el Delta cambia en días. Por eso el código
escribe los días y el grupo decide, y lo justifica.

## La grilla

- **La grilla toma el espaciado más grueso de los productos que se fusionan a nivel de
  píxel** (`--pixel`, 20 m por defecto): NISAR GCOV es de 20 m y B11 y B12 de Sentinel-2
  también. Llevarlos a 10 m inventaría detalle. Los productos más gruesos que entran
  igual al cubo (el MDE de 30 m; la banda P de BIOMASS, con 6 MHz de ancho de banda, unos
  25 m en rango oblicuo y unos 50 a 60 m en rango de terreno con la incidencia de 27 a
  29° de Ibicuy, aunque el L1B DGM venga muestreado a 25 × 22 m) quedan
  **sobremuestreados**: `Tp3_01` lo declara en las columnas `resolucion_nativa_m` y
  `remuestreo` de la tabla de capas, y no se interpretan detalles menores que su
  resolución. Los que no entran (CCI Biomass, FH, MapBiomas) se muestrean en su grilla.
- **Proyección EPSG:32721** para todo el curso; en el Delta y Diamante el error de
  escala de UTM 21 S ronda 1 m por km, sin efecto en los resultados.
- La pila del Tp2 está a 10 m; aquí se agrega a 20 m. Las bandas de NISAR que en el Tp2
  se llevaron de 20 a 10 m con bilineal vuelven a 20 m promediando: el resultado es
  cercano al original, pero no idéntico. Se declara.

## La agregación

| Dato | Método | Por qué |
|---|---|---|
| Radar (γ⁰ o σ⁰ lineal) | `average` | Promedio de potencia; en dB sesgaría hacia abajo |
| Reflectancia Sentinel-2 | `average` | La reflectancia de un píxel grande es la media de sus partes |
| SCL | `mode` | Una clase no se promedia: la clase 5 entre la 4 y la 6 no es nada |
| Copernicus DEM | bilineal | Variable continua, de 30 m a 20 m: queda sobremuestreado y se declara |

**Desplazamiento +1000 de Sentinel-2.** Desde la línea de base 04.00 (25/01/2022) los
DN de L2A traen +1000. `s2_reflectancia()` lo descuenta leyendo
`s2:processing_baseline` del ítem; si falta, decide por la fecha.

**Máscara.** Válidas las clases SCL 4, 5, 6, 7 y 11. Las demás (sin dato, saturado,
oscuro, sombra de nube, nubes media y alta, cirro) quedan sin dato en todas las bandas
ópticas. Si el sitio cae en dos teselas el mismo día, la primera manda y la segunda
rellena. La clase 7 (sin clasificar) puede ser borde de nube de baja probabilidad y la 11
(nieve) es imposible en el Delta: `Tp3_01` informa cuántos píxeles aporta cada una y
`--excluir_scl7` deja la 7 sin dato. En Ibicuy el 16/09/2026 la clase 7 aporta el 9,1 %
del sitio (vegetación oscura de los bajos, NDVI mediano 0,51, casi sin agua JRC) y la 11
ninguno; sin la clase 7 el corregistro con NISAR L pasa de 0,10 a 0,20 px: no cambia el
veredicto.

## El corregistro

- **Bordes, no valores.** El óptico mide color; el radar, estructura y rugosidad. Sus
  valores no se correlacionan pixel a pixel, pero las costas, caminos y límites de lotes
  coinciden. Mapa de bordes: módulo del gradiente de Sobel, normalizado a media 0 y
  desvío 1.
- **El radar se pasa a dB y se suaviza 3 × 3 antes del gradiente**: en lineal, los
  bordes los dominan los reflectores brillantes; sin suavizar, el speckle produce
  bordes en todas partes. Este dB es sólo para medir bordes; no altera el cubo.
- **Correlación de fase con sobremuestreo 10**: el estimador avanza en pasos de una
  décima de píxel; ese paso no es la exactitud. La incertidumbre se lee en la
  dispersión entre ventanas.
- **Qué ventanas se usan**: las que tienen dx y dy dentro de la mediana ± 3 MAD
  (desviación absoluta mediana escalada, con un piso de 0,1 px). Es un criterio que no
  mira cuánto mejora el ajuste, y por eso no achica artificialmente la dispersión. La
  bitácora informa siempre las dos cifras: con todas las ventanas y con las usadas.
  `corr_antes` y `corr_despues` (correlación de los mapas de bordes antes y después de
  aplicar el desplazamiento) quedan como dato de calidad (`mejora_bordes`), no como
  filtro: con desplazamientos de décimas de píxel, el interpolado bilineal de la prueba
  cambia la correlación por sí solo (0,425 → 0,429 sin nada que corregir).
- **Dispersión y rango**: la dispersión es el desvío estándar muestral de dx y de dy
  entre las ventanas usadas. El rango es el máximo menos el mínimo de la mediana de dy
  por fila de ventanas y de dx por columna: un error de escala de 0,3 % (1,6 píxeles de
  un extremo al otro en 550 filas) da un desvío de unos 0,6 px y pasaría como «rígido»;
  el rango lo detecta. Sólo cuentan ventanas con ≥ 80 % de dato en común
  (`--min_comun 0.8`); si la capa móvil cubre poco el sitio se puede bajar, y se declara.
- **Dos niveles de veredicto** (Townshend et al., 1992; Dai y Khorram, 1998: para
  detectar cambios a nivel de píxel hacen falta 0,2 a 0,5 píxel): CUMPLE PARA FUSIÓN DE
  PÍXEL si el módulo de la mediana y la dispersión son < 0,5 px y el rango < 1 px;
  CUMPLE PARA RASGO O DECISIÓN si son < 1 px y el rango < 2 px.
- **Signo.** `phase_cross_correlation` devuelve el desplazamiento que hay que aplicar a
  la capa móvil para alinearla con la de referencia, en (filas, columnas). La bitácora
  lo escribe en palabras: «Hay que mover la capa móvil X m al ESTE y Y m al NORTE (la
  imagen está corrida al oeste y al sur)». Regla única del curso: dx = +17 m → mover la
  capa 17 m al este → la imagen estaba 17 m al oeste. El signo se contrasta con el caso
  de control de NovaSAR antes de aplicar una corrección.
- **El desplazamiento no se aplica solo.** Cuando el veredicto es un corrimiento
  rígido (o, como primera aproximación, cuando no es rígido), `Tp3_02` imprime la orden
  lista para NovaSAR, `--desplazamiento DX DY` en
  metros (DX = dx × píxel, positivo hacia el este; DY = −dy × píxel, positivo hacia el
  norte). Se pasa a `Tp2_01`, que la aplica a través de `novasar_sigma0()`; después se
  rearma el cubo y se vuelve a medir. En SNAP, `Radar > Coregistration`.
- **Un archivo por par.** La tabla y la bitácora llevan el par en el nombre:
  `<SITIO>_corregistro_<mov>_vs_<ref>.csv` y `Tp3_02_<SITIO>_<mov>_vs_<ref>.log`.
  Cada par queda guardado; repetir el mismo par reescribe sólo sus propios archivos. El
  CSV trae, además de cada ventana, el resumen del par: `modulo_px`, `dispersion_x_px`,
  `dispersion_y_px`, `rango_dx_columnas_px`, `rango_dy_filas_px`, `dx_m_este`,
  `dy_m_norte`, `ventanas_usadas`, las cifras con todas las ventanas y `veredicto`.

## El LiDAR en el cubo

- **No se rasteriza.** Se lleva el cubo a cada huella válida.
- **Soporte:** GEDI, círculo de 12,5 m de radio (huella de 25 m) más medio píxel. ATL08,
  rectángulo de 100 m a lo largo de la traza por 14 m de ancho, orientado con el acimut
  de la traza (calculado entre segmentos consecutivos del mismo haz), más medio píxel
  por lado. Entran los píxeles cuyo centro cae adentro. A 20 m, una huella GEDI toma 3 a
  6 píxeles (4 en el 84 %) y un segmento ATL08, 7 a 13 (10 de mediana): la media
  conserva mucho speckle. Se declara.
- **Plausibilidad (columna `plausible`):** una huella GEDI no es plausible si su rh98
  supera 50 m o si la mediana de rh98 de su pasada supera 40 m (en Ibicuy, la pasada del
  29/11/2020: 160 huellas con 91 m de mediana, más una huella de 76 m). Para ATL08, el
  mismo límite de 50 m sobre h_canopy (ninguna lo supera). `motivo_no_plausible` dice
  por qué. Quedan 20.697 huellas GEDI plausibles. `Tp3_04`, `Tp3_05`, Orange y los Tp5 a
  Tp10 usan sólo `plausible = 1`.
- **Radar en lineal** en la media, con su dB aparte. **Óptico**: media de reflectancias.
- **Fechas:** `dias_<capa>` por huella. Las huellas GEDI son de 2019–2023 y 2024–2025;
  el radar NISAR, de 2026.
- **Alturas elipsoidales.** `elev_lowestmode` (GEDI) y `h_te_best_fit` (ATL08) son
  alturas sobre el elipsoide WGS 84; el Copernicus DEM, sobre el geoide EGM2008. En
  Entre Ríos el ondulamiento del geoide ronda los 15 m. `alturas_a_egm2008()`
  (`00_COMUN/funciones_lidar.py`) convierte con PROJ y la grilla
  `us_nga_egm08_25.tif`; si la grilla falta, **falla con un mensaje** en lugar de
  devolver alturas sin convertir. `Tp3_03` no convierte: copia las alturas con el
  sufijo `_elips`.

## Detalles del código que conviene conocer

- La tabla `<SITIO>_diferencias_de_fecha.csv` tiene una entrada por cada combinación
  (sensor, fecha): dos fechas de NISAR son dos entradas distintas, y se compara cada
  una con todas las demás. Una banda de SNAP que entró a la pila del Tp2 sin fecha
  queda con la diferencia vacía: la fecha se pone en el `--extra` del Tp2.
- `Tp3_02` y `Tp3_03` buscan el cubo por el nombre `<SITIO>_cubo_<pixel>m.tif`: el
  `--pixel` debe ser el mismo del paso 1.

## Limitaciones conocidas

- Sentinel-2 y el Copernicus DEM se leen del Planetary Computer. Si el Planetary
  Computer no responde en el aula, el cubo se arma sólo con radar y la falla se declara.
- `A2_IBICUY` es una ubicación aproximada.
- Si la pila del Tp2 se armó sin `--desplazamiento`, la NovaSAR entra sin corregir y
  el cubo de Bovril hereda su desplazamiento (la bitácora de `Tp2_01` lo avisa).
- El rectángulo de 100 × 14 m para ATL08 supone una traza recta dentro del segmento y
  un ancho de huella nominal.

## Hallazgos con datos reales del curso

- NISAR L y S sobre Ibicuy: 0,22 px (8 ventanas; la banda S cubre el 58 % del sitio).
  CUMPLE para fusión de píxel.
- **Sentinel-1 RTC del Planetary Computer**: corrimiento rígido de 0,75 a 1,0 px (15 a
  20 m): hay que moverlo hacia el este (la imagen está corrida al oeste), en Ibicuy y en
  Bovril, frente a Sentinel-2, NISAR L y el mismo Sentinel-1 procesado en SNAP. El
  producto de SNAP no lo tiene (0,28 px frente a Sentinel-2). En Ibicuy CUMPLE sólo para
  rasgo o decisión (0,82 px con 15 ventanas; 0,87 px con las 16); en Bovril, NO CUMPLE,
  rígido (1,02 px).
- NovaSAR **47974** (frente a Sentinel-2 y a NISAR L): hay que moverla unos **90 m al
  oeste y 480 m al sur** (la imagen está corrida al este y al norte), y **no es
  rígido**: dy va de +28 px (norte) a +18 px (sur), un rango de 10,5 px, un error de
  escala a lo largo de la órbita. Con `--desplazamiento -92 -484` la mediana baja a
  0,25 px pero la dispersión sigue en 4 px y el rango en 10,6 px: no entra a fusión de
  píxel con sus cuatro esquinas. Con los 84 puntos de enlace del metadata.xml el desfase
  es rígido (80 m al oeste y 20 m al norte) y una traslación lo corrige (Tp8). La
  presentación 02 daba unos **80 m al oeste y 20 m al norte** de corrección, la cifra de
  los 84 puntos de enlace: coincide en x, no en y.
- **BIOMASS banda P (VH) del 05/10/2026**: frente a Sentinel-2 B08, hay que moverla 12 m
  al oeste y 6 m al norte (0,67 px; dispersión 0,14 y 0,16 px con 14 de 16 ventanas;
  0,28 y 0,20 px con todas): CUMPLE para rasgo o decisión. Frente a NISAR L HV, 8 m al
  oeste y 4 m al norte (0,45 px con 15 ventanas; 0,49 px con las 16): CUMPLE para fusión
  de píxel. Se ubicó con los puntos de enlace del L1B, sin modelo de terreno. La cruzada
  es la VH: la HV trae interferencia de radiofrecuencia detectada y no corregida por ESA.
- **Landsat 8 SR_B5 (15/09/2026) frente a Sentinel-2 B08 a 30 m** (ejercicio optativo,
  cubo `A2_IBICUY_cubo_30m.tif`): hay que mover el Landsat 15 m al este y 12 m al sur
  (0,64 px de 30 m; dispersión 0,07 y 0,05 px; rango 0,05 px): corrimiento rígido;
  CUMPLE para rasgo o decisión.
- **Banda P y altura LiDAR**: P VH sube de −28 dB (rh98 < 3 m) a −17 dB (5–10 m) y se
  aplana por encima; Spearman con rh98, 0,50 (igual que L HV); con h_canopy de ATL08,
  0,36 (L HV, 0,16), con el rectángulo orientado de 100 × 14 m.
- **Contexto (Tp3_04)**: MapBiomas cubre el 73,6 % del sitio (las islas bonaerenses
  quedan fuera); herbáceas inundables 84 % en 2025; pérdida de vegetación casi nula
  (123 ha en 1987–2025); quemado al menos una vez, el 48,2 % (años 2008, 2020–2022).
- **Altura FH de BIOMASS L2A** (23/11 a 05/12/2025), con el agua enmascarada (MapBiomas 2025
  clases 26, 31 y 33, o JRC ≥ 50 %; 12,8 % de los píxeles y 649 huellas): no sigue a la altura
  LiDAR (Spearman −0,12 en 22.899 huellas plausibles; −0,03 en las 2.386 con calidad ≥ 50)
  y da 9 a 12 m sobre pajonal y herbáceas. Sin la máscara los ríos salían con 10,8 m. No se
  usa en este sitio.
- **Geoide**: la ondulación de EGM2008 en el sitio es de 16,9 m (16,86 a 16,99 m). La
  diferencia terreno elipsoidal menos MDE es de 16,9 m en GEDI y 16,2 m en ATL08: el
  residuo, después de restar N, es de −0,1 m (GEDI) y −0,7 m (ATL08).
- **MDE sobre el agua**: el Copernicus DEM vale 0 m en el 99,8 % de los píxeles con
  ocurrencia JRC de 90 % o más (el Paraná frente a Ibicuy): el agua quedó aplanada a 0.
- GEDI no tiene adquisiciones entre el 17/03/2023 y el 26/04/2024; el campo de calidad
  de L2A V003 es `l2a_quality_flag_rel3`.
- ATL08 v007: valor de relleno 3,4 × 10³⁸; haz fuerte según `sc_orient`; alturas
  elipsoidales que se pasan a EGM2008 con PROJ.

## Historia de cambios del código (para el docente)

- 21/10/2026: `Tp3_02` agregó `corr_antes` y `corr_despues`; la columna `error` de
  scikit-image se eliminó porque con la normalización de fase vale ~1 siempre. Cuando el
  veredicto es «no rígido», la bitácora muestra el desplazamiento por fila y por columna
  de ventanas.
- 21/10/2026: se agregó `Tp3_04_contexto_y_huellas.py`.
- 22/10/2026: `Tp3_04` enmascara el agua antes de comparar la altura FH con el LiDAR.
- 27/10/2026 (auditoría académica): `Tp3_02` pasa a dos niveles de veredicto, ventanas
  por mediana ± 3 MAD, rango por fila y columna, signo en palabras y resumen completo en
  el CSV; `Tp3_03` agrega `plausible` y el rectángulo orientado de ATL08; `Tp3_01`
  declara la resolución nativa y el sobremuestreo de cada capa, y la clase 7 de la SCL;
  se agrega `Tp3_05_tablas_para_Orange.py`.
- El docstring anterior de `Tp3_02` citaba desfases de 129 a 1.120 m medidos en la
  presentación 02 en COSMO-SkyMed, NovaSAR-1 y SAOCOM; esas cifras corresponden a
  productos sin corrección geométrica fina y no a los productos de este práctico (el
  SAOCOM del Tp3, corregido en SNAP, está a unos 30 m de NISAR L). Se quitaron del código.
