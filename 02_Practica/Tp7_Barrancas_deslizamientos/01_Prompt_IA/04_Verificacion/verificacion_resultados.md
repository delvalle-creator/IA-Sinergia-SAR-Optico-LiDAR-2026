# Verificación de los resultados del Tp7

Dos niveles: lo que entregó la IA (el código) y lo que dieron los datos.

## A. Controles sobre lo que entregó la IA

| # | Control | Criterio de aceptación |
|---|---|---|
| 1 | El período de búsqueda de banda C | Por defecto incluye el 15–19/10/2018 |
| 2 | La conversión de fase a desplazamiento | `d = −λ · fase / (4π)` con λ de la banda correcta (X 0,03123 m) |
| 3 | La detección de banda vacía | Con la `Unw_Phase` del curso 2023 el script escribe «banda vacía» y no informa desplazamiento |
| 4 | La referencia del desplazamiento | Se resta la mediana de la zona estable, sólo con píxeles coherentes; el agua del JRC queda fuera del anillo (o se usa `--zona_estable`) |
| 5 | La regla de fusión | `interseccion` estricta (`minimo_votos` = número de bandas): sin decidir donde falta una banda; con una banda, no hay fusión y se dice; el signo se juzga con la geometría de cada banda (movimiento hipotético proyectado en cada LOS) o no se interpreta |
| 6 | El volumen | Se resta el sesgo de la zona estable antes de sumar; se informa el ruido |
| 7 | Credenciales | Ninguna escrita en los scripts |

## B. Controles sobre los resultados

| # | Control | Criterio de aceptación | Dónde se lee |
|---|---|---|---|
| 1 | La fase desenrollada X es confiable | Distinta de cero (`Analysis > Statistics` en SNAP: mínimo ≠ máximo), componentes conexas revisadas, píxeles de la componente 0 enmascarados y parámetros de SNAPHU anotados | SNAP; componentes de SNAPHU |
| 2 | Georreferencia de la banda X | La barranca cae sobre la barranca de la imagen de muy alta resolución; desfase < 1 píxel (10 m) o medido y declarado | QGIS |
| 3 | Ruido en la zona de referencia, por banda | `desvio_referencia_m` < `umbral_m` (10 mm); si no, la banda no detecta | `E1_coherencia_y_desplazamiento.csv` |
| 4 | Coherencia en la ladera | Se informa por banda; con coherencia < 0,3 en casi toda la ladera, no hay medición | misma tabla, `%_ladera_coherente` |
| 5 | Deformación confirmada en una zona de control | 0 píxeles (o muy pocos, y explicados) en una zona independiente de la usada como referencia (`--control_independiente`) | `Tp7_02_deformacion.log` |
| 6 | Ladera decidida | Se informa la fracción de la ladera decidida (todas las bandas con dato coherente) y se explica dónde falta cada banda | `Tp7_02_deformacion.log`; `E1_deformacion_confirmada.tif`, banda 2 |
| 7 | Geometría X y C | Pasada, rumbo e incidencia de cada banda leídos en los metadatos; con la misma pasada se aplica la regla de signo proyectada; si no, la regla de signo no se interpreta | CSV, metadatos SNAP y bitácora |
| 8 | Sesgo entre MDE | Se informa y se resta; ruido de la zona estable declarado | `E1_volumenes.csv`, `sesgo_restado_m`, `ruido_zona_estable_m` |
| 9 | Detectabilidad del volumen | Detectable sólo si supera el límite de detección con el signo esperado Y el patrón no se repite fuera de la forma (control en la escarpa vecina) | `E1_volumenes.csv`, columnas de signo esperado y contrario, filas `control_*` |
| 10 | Control del MDE con ICESat-2 | Cota de ICESat-2 en el sistema vertical de cada MDE (EGM2008 para GLO-30 y FABDEM, SRVN16 para el IGN); sesgo, desvío y NMAD en tierra firme | tabla del grupo |

## Cifras que deben aparecer en la bitácora

- Número de escenas SLC y de pares aptos (`Tp7_01_pares.log`).
- Píxeles de agua quitados del anillo (o el aviso del JRC), píxeles de la
  ladera y de la referencia (`Tp7_02_deformacion.log`).
- Por banda: coherencia en ladera y referencia, % coherente, desplazamiento
  mediano y ruido, en mm.
- Píxeles confirmados en la ladera y en la referencia, y píxeles de la ladera
  decididos (todas las bandas con dato coherente).
- Sesgo y desvío entre MDE; área, dZ medio y volumen de cicatriz y depósito
  (`Tp7_03_volumen.log`).

**Hallazgo con los datos del curso** (banda X, par 15/10–19/10/2018): la
coherencia da ≈ 0,41 en la ladera y 0,40 en el anillo de referencia. Su grupo
debe obtener valores parecidos; si se alejan mucho, revise la georreferencia o la
banda que exportó.

## Tabla para el grupo

| Control | Banda X | Banda C | Banda L | Observación |
|---|---|---|---|---|
| Fecha del par | 15/10–19/10/2018 | | | |
| Pasada (asc./desc.) e incidencia | | | | |
| Coherencia media ladera | | | | |
| Coherencia media referencia | | | | |
| % ladera coherente | | | | |
| Desplazamiento mediano ladera (mm) | | | | |
| Ruido en referencia (mm, desvío y NMAD) | | | | |
| ¿Supera el umbral de 10 mm el ruido? | | | | |
| Píxeles confirmados en ladera | | | | |
| Píxeles de la ladera decididos / total | | | | |
| Píxeles confirmados en referencia | | | | |
| Píxeles confirmados en el control independiente | | | | |

| Volumen | Cicatriz | Depósito | Escarpa de control |
|---|---|---|---|
| MDE antes / después | | | |
| Sesgo restado (m) | | | |
| Ruido zona estable (m, desvío y NMAD) | | | |
| Área (m²) | | | |
| Volumen (m³) | | | |
| Volumen detectable ± incertidumbre (m³) | | | |
| % píxeles > 2 desvíos, signo esperado | | | |
| % píxeles > 2 desvíos, signo contrario | | | |
| ¿Detectable? | | | |

| Control del MDE con ICESat-2 | GLO-30 | IGN 5 m |
|---|---|---|
| Sistema vertical de la cota de ICESat-2 | EGM2008 | SRVN16 |
| Segmentos ATL08 válidos en tierra firme | | |
| Sesgo (mediana, m) | | |
| Desvío y NMAD (m) | | |

### Valores del Desarrollo del docente (para contrastar)

| Control | Banda X | Banda C (12/10–24/10/2018) | Banda L | Observación |
|---|---|---|---|---|
| Fecha del par | 15/10–19/10/2018 | 12/10–24/10/2018 | — | No hay par L en octubre de 2018 |
| Pasada e incidencia | Descendente, 59,6° | Descendente, 38,9° | — | Misma dirección, distinta incidencia |
| Coherencia media ladera | 0,41 | 0,59 | — | |
| Coherencia media referencia | 0,40 | 0,54 | — | |
| % ladera coherente | 80,2 | 78,4 | — | |
| Desplazamiento mediano ladera (mm) | −0,5 | −3,9 | — | |
| Ruido en referencia (mm, desvío / NMAD) | 1,5 / 1,4 | 3,5 / 2,9 | — | |
| ¿Supera el umbral de 10 mm el ruido? | No | No | — | |
| Píxeles confirmados en ladera | 0 | 0 | — | Fusión de las dos bandas |
| Píxeles de la ladera decididos / total | 15.104 / 36.599 (41,3 %) | | — | Unas 944 observaciones independientes de la C |
| Píxeles confirmados en referencia | 0 | 0 | — | |
| Píxeles confirmados en el control independiente | 0 de 5.513 decididos | | — | Mitad sur del anillo |

| Volumen | Cicatriz | Depósito | Escarpa de control |
|---|---|---|---|
| MDE antes / después | GLO-30 / IGN 5 m | GLO-30 / IGN 5 m | GLO-30 / IGN 5 m |
| Sesgo restado (m) | +0,83 | +0,83 | +0,83 |
| Ruido zona estable (m, desvío y NMAD) | 2,06 y 1,15 | 2,06 y 1,15 | 2,06 y 1,15 |
| Área (m²) | 4.500 (5 píxeles) | 5.400 (6 píxeles) | 268.200 |
| Volumen (m³) | −19.096 | 0 | −705.754 |
| Volumen detectable ± incertidumbre (m³) | −16.210 ± 8.308 | 0 ± 9.101 | −511.469 ± 64.140 |
| % píxeles > 2 desvíos, signo esperado | 40 | 0 | 27 |
| % píxeles > 2 desvíos, signo contrario | 0 | 100 | 15 |
| ¿Detectable? | No: el patrón se repite en el control | No | — |

| Control del MDE con ICESat-2 | GLO-30 | IGN 5 m |
|---|---|---|
| Sistema vertical de la cota de ICESat-2 | EGM2008 | SRVN16 |
| Segmentos ATL08 válidos en tierra firme (fuera de ladera, anillo y río) | 11.827 | 9.626 |
| Sesgo (mediana, m) | −0,03 | −0,96 |
| Desvío y NMAD (m) | 2,06 y 0,80 | 2,62 y 0,60 |
