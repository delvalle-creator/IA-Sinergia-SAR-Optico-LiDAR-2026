# Tp3 — Preguntas, producto y rúbrica

Cada respuesta cita el archivo del que sale la cifra (por ejemplo,
`05_Resultados/04_Tablas/A2_IBICUY_corregistro_L_NISAR_gamma0_HV_20260930_vs_OPT_S2_B08.csv`, columna
`mediana_dx_px`). Respuestas cortas: el dato y la razón.

## Preguntas

1. **La resolución de la grilla.** ¿Por qué el cubo es de 20 m y no de 10 m? ¿Qué se
   «inventaría» al llevar NISAR o B11 a 10 m? ¿Qué se pierde, a cambio, en Sentinel-1 y
   en las bandas de 10 m de Sentinel-2? ¿Qué capas del cubo son más gruesas que 20 m y
   cómo se declaran (columna `remuestreo` de `<SITIO>_cubo_20m_bandas.csv`)?

2. **Agregar bien.** ¿Por qué el radar se agrega con promedio en lineal, la reflectancia
   con promedio y la SCL con la moda? ¿Qué pasaría si la SCL se promediara?

3. **Corregistro óptico frente a radar.** Informe la mediana, la dispersión y el rango
   de `OPT_S2_B08` frente a la banda L, y el veredicto (¿para fusión de píxel o sólo
   para rasgo o decisión?). Escriba el desplazamiento con la regla del recuadro de
   signo («hay que mover la capa X m al este; la imagen está corrida X m al oeste»).
   ¿Por qué se comparan mapas de bordes y no los valores?

4. **Rígido o no rígido.** En el caso de NovaSAR en Bovril, ¿qué dio la medición (dx,
   dy en metros, dispersión, veredicto)? ¿Es un corrimiento rígido o una deformación?
   ¿Qué tiene que ver con que el GRD de NovaSAR esté georreferenciado sólo por sus
   cuatro esquinas? Compare con la cifra de la presentación 02 (unos 80 m al oeste y
   20 m al norte de corrección): ¿en qué componente coincide y en cuál no? ¿Qué pasó al
   aplicar la mediana con `--desplazamiento` y volver a medir?

5. **Fechas.** Con `A2_IBICUY_diferencias_de_fecha.csv` y la mediana de `dias_<capa>`
   de la bitácora de `Tp3_03`: ¿cuántos días separan el óptico del radar, y las huellas
   LiDAR del cubo? En un humedal del Delta, ¿son compatibles esas diferencias? ¿Para
   qué variable sí y para cuál no (altura del monte frente a extensión del agua)?

6. **Los tres requisitos.** Complete la tabla de los tres requisitos de
   `01_Prompt_IA/04_Verificacion/verificacion_resultados.md`. Para cada par, ¿qué nivel
   de fusión permite: píxel, rasgo, decisión, o ninguno (sólo sinergia)?

7. **Huella frente a píxel.** ¿Cuántos píxeles de 20 m entran, en promedio, en una huella
   GEDI (`n_<capa>`)? ¿Qué consecuencia tiene sobre el speckle del radar en esa media, y
   sobre la representatividad de la huella?

8. **Sinergia.** En el gráfico rh98 frente a la cruzada de L (y de C), ¿qué se ve? ¿La
   banda L sigue la altura del dosel en un rango más amplio que la C? Si no se ve,
   ¿qué lo explica: pocas huellas, fechas lejanas, agua bajo el dosel, tamaño de huella?
   Use sólo las huellas con `plausible = 1` y el widget Correlations (Spearman) de
   `08_Orange/Tp3_A`.

9. **Alturas.** ¿Por qué no se puede restar `elev_lowestmode_elips` de `MDE_GLO30_m`
   directamente? ¿Qué función del curso hace la conversión y qué pasa si falta la
   grilla del geoide?

10. **Limitaciones.** Nombre dos limitaciones del cubo de Ibicuy que debería conocer
    quien lo use en el Tp6 o el Tp9 (por ejemplo: sitio de ubicación aproximada, fechas
    de NISAR distintas entre sí, el círculo de 50 m como aproximación del segmento
    ATL08, huellas de otra época).

11. **Contexto del sitio.** Con las bitácoras de `Tp3_04`: ¿qué cubre MapBiomas en 2025
    y qué parte del sitio quedó quemada al menos una vez desde 1999? ¿En qué clases de
    MapBiomas caen las huellas, y qué altura LiDAR, CCI y P VH tienen? ¿Por qué se enmascara el agua
    antes de comparar la altura FH de BIOMASS L2A con el LiDAR, y sirve en Ibicuy? ¿Por qué la cruzada de P es la VH y no la HV?

12. **Transferencia: dos pares nuevos.** Mida el corregistro de
    `S_NISAR_gamma0_HH_20260930` frente a `OPT_S2_B08` y de `P_BIOMASS_gamma0_HH` frente
    a `C_SNAP_gamma0_VV` (con `Tp3_02`, `--min_comun 0.8`; si la banda S no alcanza
    ventanas, declare cómo lo resolvió). Para cada par, complete la fila de la tabla de
    los tres requisitos (grilla, corregistro con mediana, dispersión, rango y veredicto,
    días entre fechas) y decida el nivel de fusión, justificándolo. El Desarrollo no
    resuelve estos dos pares.

## Producto a entregar

- El cubo, su tabla de capas y la tabla de diferencias de fecha.
- Las tablas de corregistro, una por par, con su bitácora.
- La tabla de huellas con los valores del cubo y su GeoPackage.
- La tabla de los tres requisitos completa.
- Las tablas y gráficos de contexto de `Tp3_04` y la tabla de huellas con contexto.
- Las respuestas a estas doce preguntas y la tabla de verificación completada
  (controles A1 a A7 y B1 a B12, con la cifra de cada control).

## Rúbrica

| Criterio | Peso | Logrado | Parcial | No logrado |
|---|---|---|---|---|
| Grilla y agregación (píxel justificado; lineal, media, moda; capas sobremuestreadas declaradas) | 15 % | Justificadas con la física de cada dato y el sobremuestreo declarado | Correctas sin justificar | Bilineal para agregar o radar en dB |
| Corregistro medido e interpretado (mediana, dispersión, rango, signo, dos niveles de veredicto), sobre todo en los pares nuevos de la pregunta 12 | 25 % | Pares nuevos medidos, signo escrito con la regla del recuadro y nivel de fusión justificado | Medido sin interpretar | No medido o «alineado por compartir grilla» |
| Fechas documentadas (por par y por huella) | 10 % | Completas y evaluadas según el fenómeno | Listadas sin evaluar | Omitidas |
| LiDAR en el cubo (soporte, n, plausibilidad, alturas elipsoidales) | 10 % | Correcto, con huellas no plausibles excluidas y limitaciones | Correcto sin limitaciones | Rasterizado, alturas mezcladas o huellas imposibles usadas |
| Sinergia y contexto (pasos 5 y 6, preguntas 8 y 11) | 15 % | Lectura física de la respuesta del radar y papel de cada producto de contexto (estrato, contexto o ninguno) | Cifras sin interpretación | Contexto tomado como verdad o ausente |
| Decisión sobre el nivel de fusión por par (tabla de requisitos, incluidos los pares nuevos) | 15 % | Coherente con las mediciones | Incompleta | Sin decisión o contradictoria |
| Trazabilidad (cada cifra con su archivo; tabla de verificación completa) | 10 % | Todas citadas | Algunas citadas | Ninguna citada |
