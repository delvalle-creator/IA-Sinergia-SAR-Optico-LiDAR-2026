# Tp6 — Notas técnicas

> **Qué es este archivo.** Las decisiones técnicas del práctico y su fundamento, las limitaciones conocidas y lo comprobado con datos reales. El punto de entrada es `00_LEEME.md`.

## Unidades

Sentinel-1 RTC se lee en γ⁰ lineal y se pasa a dB **sólo** para aplicar el umbral de VV y para el histograma. El aumento de HH en banda L (SAOCOM 11/11 frente a 10/10/2023) se calcula como 10·log₁₀(evento/referencia) en lineal. El óptico va en reflectancia (0 a 1); la escena de 2023 es de línea de base ≥ 04.00 y la función común le descuenta el desplazamiento de +1000.

## Calibración

Sentinel-1 RTC del Planetary Computer ya es γ⁰ corregido por el terreno. No se procesa en SNAP. Valores ≤ 0 → sin dato.

## Georreferencia

Todo en la grilla de B_CONCORDIA a 20 m, EPSG:32721. El Copernicus DEM se lee con interpolación bilineal (variable continua). JRC, por vecino más próximo (porcentaje entero, 255 sin dato). Los segmentos ATL08 se ubican en el píxel de la grilla en que caen.

## Fechas

- Serie C: 01/10/2023 a 30/06/2024, una sola órbita relativa. En ese período sólo volaba Sentinel-1A (1B dejó de funcionar en diciembre de 2021): una pasada por órbita cada 12 días.
- Pico: 04/11/2023, Sentinel-1A y Sentinel-2B del mismo día.
- Referencia seca: 22/01/2026 (Sentinel-1C y Sentinel-2B, río en nivel normal; `EVENTOS["Tp6"]["referencia_seca"]`). `Tp6_01` toma la escena Sentinel-1 de la misma órbita más cercana (± 6 días) y, con el mismo umbral, excluye el agua no permanente que ya estaba ese día (lagunas estacionales, bañados, arrozales). Así «agua de inundación» quiere decir agua abierta que no es permanente (JRC) ni estaba con el río en nivel normal; la banda `agua_en_referencia_seca` la aplica `Tp6_03` a todas las variantes (regla R5). Limitación: la referencia es de otro año (2026); una laguna que en 2023 estaba seca y en 2026 con agua quedaría excluida de más.
- Dos cuadros consecutivos de la misma pasada (misma fecha) se unen en una sola capa `agua_AAAAMMDD` y una sola fila de la tabla; donde se superponen, manda el primero. La bitácora lo informa.
- Copernicus DEM: 2011–2015. ICESat-2: las trazas disponibles; el terreno de pastura y suelo desnudo no cambia de forma apreciable en esos años, salvo obras.

## Filtros

- Óptico: SCL 4, 5, 6, 7, 11; con nube, sin dato (no vota).
- Agua permanente: JRC ≥ 90 %, excluida en todos los sensores.
- ATL08: terreno válido (sin valor de relleno, que en el producto es 3,4·10³⁸; el código descarta todo valor ≥ 3·10³⁸) y `segment_watermask` = 0. Haz fuerte o débil según `orbit_info/sc_orient` (0: fuertes los izquierdos; 1: los derechos).

## Por qué cada umbral

- **VV, umbral manual de −15 dB en la fecha del umbral (04/11/2023):** Otsu se calcula fuera del agua permanente, para que el río no domine la moda oscura; pero así el agua de inundación queda en la cola, el histograma de VV del 04/11/2023 es unimodal y Otsu falla (−9,5 dB, casi la mitad del sitio). Se fija −15 dB con el agua permanente de JRC y la tierra de JRC = 0, y se declara. Se aplica igual a todas las fechas para que «agua» signifique lo mismo en toda la serie. Alternativa: Otsu por partición en ventanas con agua y tierra (Martinis et al., 2009).
- **MNDWI > 0:** el agua tiene MNDWI positivo; el valor 0 es el límite natural del índice. El 04/11/2023 el histograma del MNDWI es bimodal (tierra en −0,55, agua en +0,58) y el 0 cae en el valle. Manual por defecto; si el histograma muestra otro valle, se cambia con `--u_mndwi` y se declara.
- **Doble rebote ≥ 3 dB:** un aumento de 3 dB es duplicar la potencia retrodispersada; por debajo, el speckle y la humedad producen cambios de ese orden sin agua.
- **Sesgo del MDE de 1 m:** es el criterio que escribe `Tp6_05`. Una crecida de llanura tiene profundidades de decímetros a pocos metros: un sesgo de más de 1 m es del orden de la cifra que se quiere medir.

## Por qué fusión de decisión

C, óptico y L llegan con nubes, fechas y píxeles distintos. Apilar sus valores en un clasificador obligaría a decidir qué hacer con las nubes y con las fechas distintas dentro del modelo. Combinando decisiones, cada sensor decide con su física y la regla queda escrita. La unión maximiza la detección y también la comisión; el Tp4 lo mide.

## La profundidad

Idea de FwDET (Cohen et al., 2018, versión 1.0; Cohen et al., 2019, versión 2.0): superficie del agua horizontal localmente, a la cota del borde. La cota de borde se suaviza con el promedio de las cotas de borde dentro de una ventana de 7 × 7 píxeles (140 m a 20 m) y cada píxel inundado toma la del borde más cercano. Es una profundidad **plausible**: el Copernicus DEM es un modelo de superficie de banda X, mide la copa en el monte y el espejo de agua del día de su adquisición en el cauce.

## Limitaciones conocidas

0. **Referencia de validación no independiente.** El Sentinel-2 del 04/11/2023 es la referencia y entra en la variante óptica y en la multisensor (R3): las favorece. Sólo la C se valida sin ese sesgo.
1. **Banda L con un solo par útil** (SAOCOM 10/10 y 11/11/2023). La HH subió 3,1 dB en la mediana de todo el sitio entre las dos fechas; la regla fija marca el 52 % del sitio. Con `--l_relativo --l_solo_lenoso` queda el 1,4 %, sin coincidencia con el agua de C ni del óptico. El agua bajo vegetación no se separa del cambio general; la variante «SAR multibanda» no existe.
2. **Nubes:** la variante óptica sólo cubre la parte despejada; su área no es comparable con la de las variantes de radar.
3. **Revisita:** con una órbita y un satélite, 12 días entre fechas; la duración tiene esa resolución.
4. **Nombres sin fecha:** `B_agua_por_sensor_20m.tif` y `B_variante_*.tif` no llevan la fecha; procesar otra fecha los reescribe.
5. **MDE de superficie** (ver arriba) y profundidad sin validación directa.
6. **Desplazamiento de la cota:** la superficie horizontal local es una simplificación; en tramos largos del río el agua tiene pendiente.

## Hallazgos con datos reales del curso

- SAOCOM 10/10 frente a 11/11/2023 (TNA, misma órbita): aumento mediano de HH de +3,12 dB en el sitio; por clase de MapBiomas 2023, monte 2,3, plantaciones 2,7, herbáceas 3,8, cultivos 4,1 y herbáceas inundables 0,2 dB. En el bañado inundado la HH baja (espejo). Los SAOCOM del 31/10 y 08/11/2023 (TNB) cubren el 51 % del sitio.
- La escena NovaSAR 47942 (13/09/2023) cubre el 39 % de B_CONCORDIA; la 50896 (22/12/2023) **no** cubre Concordia, aunque tenga la misma hora de pasada que la 47942.
- GEDI no tiene adquisiciones entre el 17/03/2023 y el 26/04/2024: no hay altura de dosel GEDI para la crecida de noviembre. El control del MDE se hace con ICESat-2.
- ATL08 v007: valor de relleno 3,4·10³⁸; haz fuerte según `sc_orient`; alturas elipsoidales que se pasan a EGM2008 con PROJ.
- **Corrida del 22/10/2026 (desarrollo del docente).** Tp6_01 calculaba Otsu con el primer cuadro de la pasada del pico (2 % del sitio); ahora une los cuadros (`agrupar_por_pasada`) y la referencia seca exige cobertura del sitio. Aun con el sitio completo, el histograma de VV del 04/11/2023 es unimodal y Otsu da −9,49 dB (48,6 % del sitio): el umbral se fija a mano en −15 dB. El agua de ese día está clara (mediana de VV −16 dB en el agua permanente y −15,7 dB en la de inundación, contra −9,2 dB en tierra) por el viento sobre el embalse y la corriente del río. En VH se separa mejor (−22,2 y −20,2 contra −14,8 dB).
- Resultados con −15 dB: 20 fechas de la órbita 68 (cuatro con un solo cuadro, 2 a 20 % del sitio); 2.912 ha el 04/11/2023, máximos de 3.869 ha (28/11/2023) y 3.589 ha (14/05/2024); 4.380 ha con más de 30 días de agua (duración mínima; con la máxima, que trata las fechas parciales como agua, 124.164 ha); extensión persistente (dos fechas o más), 6.197 ha; referencia seca, 6.450 ha. Sinergia: acuerdo 98,2 %, 1,2 % ambos, 0,5 % sólo C, 1,3 % sólo óptico. Variantes: óptico 3.887 ha, C 2.912, multisensor 4.719. Validación (426 puntos, referencia Sentinel-2 del mismo día): omisión de agua 0,48 a 0,74, IC superpuestos; con la misma definición de agua que el mapa (JRC < 90 % y fuera de la referencia seca), 0,31 a 0,73, sin diferencias demostradas. Profundidad: 39,9 % de valores negativos con el Copernicus DEM y 38,6 % con FABDEM; mediana de los positivos 0,54 y 0,23 m. MDE frente a ATL08 (polígonos sorteados del Tp4 y monte de copa cerrada, 22/10/2026): cultivo_pastura 0,84 m (8 segmentos), monte 3,99 m, plantación 16,95 m; con los polígonos ubicados a mano eran 0,6 m (25 segmentos), 3,3 m y 6,3 m.
- Control del MDE estratificado por MapBiomas 2023 (27/10/2026, MDE promediado sobre el segmento): herbáceas inundables, Copernicus DEM sesgo 1,91 m y RMSE 3,32 m (3.931 segmentos); FABDEM 1,73 y 2,86 m. La profundidad de los bañados hereda ese sesgo y un error por píxel del orden del RMSE.

## Corridas del 28/10/2026

- **Referencia seca de 2023.** `Tp6_01 --umbral_vv -15 --referencia_seca 2023-05-20,2023-06-13,2023-07-07` (00_COMUN/09_Herramientas/TP6_REF_SECA_2023.bat). Tres pasadas de Sentinel-1A, órbita 68, sorteadas (semilla 20261028) entre el 20/05 y el 07/07/2023, antes de la crecida ordinaria de fines de julio (puerto de Concordia cerca de 5 m; LT15 Concordia, 25/07/2023). El 13/06 no tiene escena a ± 6 días. Las otras dos excluyen 2.673 ha (la de 2026, 6.450 ha). El 04/11/2023: 2.973 ha (2.912 con la de 2026); extensión máxima 18.185 ha; persistente 6.763 ha. Salidas con sufijo `_ref_seca_2023`; el producto del curso sigue siendo el de 2026.
- **Muestra común de 300 puntos etiquetada.** Dos intérpretes (A: Sentinel-2 del 04/11/2023, B11-B8-B4; B: Landsat 8 del 25/10/2023, B6-B5-B4); acuerdo 91,7 %, kappa 0,82 en 277 puntos. SAOCOM 31/10 y 08/11 descartado como referencia: el agua con viento sale clara. Omisión: óptico 0,339 ± 0,093, C 0,579 ± 0,066, unión 0,299 ± 0,093; diferencias pareadas unión − C −0,28 ± 0,06, óptico − C −0,24 ± 0,07, unión − óptico −0,04 ± 0,03. Tablas: `B_muestra_comun_20231104_omision_pareada.csv` y `B_muestra_comun_20231104_etiquetas_dos_interpretes.csv`.
