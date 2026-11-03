# Verificación de los resultados del Tp6

Cada control tiene su criterio de aceptación. Si uno no se cumple, se corrige o se declara.

## A. Controles sobre los scripts

1. **Órbita única.** Acepta si la bitácora de `Tp6_01` nombra una sola órbita relativa para toda la serie y lista las descartadas.
2. **Un umbral para toda la serie.** Acepta si el umbral de VV aparece una sola vez en la bitácora y la descripción del GeoTIFF de la serie dice `VV < <umbral> dB`.
3. **Agua permanente fuera.** En QGIS, acepta si ningún píxel de `extension_maxima` = 1 cae sobre la clase 1 de la cobertura de control o sobre el cauce del río y el embalse.
4. **Nube no vota.** Acepta si en `B_agua_por_sensor_20m.tif` la banda `Optico_MNDWI` es sin dato donde la SCL marca nube (compárela en QGIS con la escena del Copernicus Browser del 04/11/2023).
5. **Reglas de la fusión.** Acepta si las hectáreas de `B_variante_multisensor` son ≥ que las de cada variante de un solo sensor (es una unión).
6. **Geoide.** Acepta si `Tp6_05` corre sin el `RuntimeError` de PROJ; si aparece, no se acepta ninguna cifra de sesgo hasta resolverlo.

## B. Controles sobre los resultados

7. **Histograma en la fecha del umbral.** Acepta si `B_histograma_VV_pico.png` muestra dos modas y el umbral en el valle; si no (con los datos del curso es unimodal), si el umbral manual está justificado con el agua de JRC.
8. **Serie sin saltos espurios.** Acepta si cada fecha con un salto brusco de hectáreas tiene `pixeles_validos_%` cercano a las demás fechas; si no, se explica (escena incompleta, viento).
9. **Cuadros de la misma pasada unidos.** Acepta si `B_serie_agua_C.csv` tiene una fila por fecha y, en las fechas armadas con dos cuadros (bitácora: `segundo cuadro de la misma pasada: unido`), `pixeles_validos_%` es comparable con el de las demás fechas.
10. **Acuerdo C–óptico en agua abierta despejada.** Acepta si `%_ambos` es la mayor parte del agua que marca cualquiera de los dos en `B_sinergia_agua.csv`; si `%_solo_1` o `%_solo_2` son grandes, se explica con lo que se ve en QGIS.
11. **Profundidades negativas.** Acepta si son menos del 20 % de los píxeles inundados (bitácora de `Tp6_04`); si son más, se declara que la mancha o el MDE no son coherentes en esa zona.
12. **Sesgo del MDE en suelo y pastura.** Acepta si |sesgo| ≤ 1 m en las clases 5 y 6 de `B_control_mde_icesat2.csv` (el criterio que escribe el propio script). Si es mayor, la profundidad hereda ese error y se dice cuánto.
13. **Sesgo en monte.** Se espera positivo en las clases 3 y 4 (el MDE mide la copa). Acepta si el informe lo explica y no presenta profundidades bajo el monte como confiables.
14. **Validación.** Acepta si la tabla de variantes informa área estimada ± IC y si se aclara que la variante óptica se valida sólo en la parte despejada del sitio.
15. **Banda L probada.** Acepta si el informe muestra el aumento mediano de HH entre el 10/10 y el 11/11/2023 (+3,1 dB), explica por qué la regla fija marca medio sitio, informa el resultado de la regla relativa en leñosas (alrededor de 1,4 %, sin coincidencia con el agua de C ni del óptico) y concluye qué agua queda sin evaluar.
16. **Independencia de la referencia.** Acepta si la referencia de validación no es un dato que entró al mapa, o si el informe declara por variante a cuáles favorece (con el Sentinel-2 del mismo día: la óptica y la multisensor).
17. **Misma definición de agua.** Acepta si la regla de etiquetado usa la misma definición que el mapa: agua abierta en la fecha, JRC < 90 % y fuera de la banda `agua_en_referencia_seca` (R5).
18. **Referencia seca.** Acepta si el informe dice la fecha de la referencia seca y, si es posterior al evento, cuánta agua saca (R5) y que puede borrar agua real.

## Cifras que deben aparecer en las bitácoras

| Bitácora | Cifra |
|---|---|
| `Tp6_01_serie.log` | escenas totales y de la órbita usada; % de agua permanente; umbral de VV y método; ha por fecha; extensión máxima; ha con más de 30 días |
| `Tp6_02_sinergia.log` | nubosidad en el sitio; umbral MNDWI; mensaje sobre la banda L; tabla de acuerdo |
| `Tp6_03_fusion.log` | ha de cada variante; % sin dato por nubes de la óptica |
| `Tp4_03_B_variante_*.log` | exactitud global ± IC; usuario y productor de agua; área estimada ± IC |
| `Tp6_04_profundidad.log` | píxeles inundados; % negativos; mediana, p90 y máximo |
| `Tp6_05_control_mde.log` | segmentos válidos; sesgo, desvío, RMSE y mediana por grupo |

## Tabla para anotar los valores del grupo

| Control | Valor obtenido | ¿Acepta? | Observación |
|---|---|---|---|
| 1 Órbita usada / descartadas | | | |
| 2 Umbral VV (dB) y método | | | |
| 5 ha C / óptico / multisensor | | | |
| 9 Fechas con dos cuadros unidos (cuáles) | | | |
| 10 % ambos / % solo C / % solo óptico | | | |
| 11 Profundidades negativas (%) | | | |
| 12 Sesgo MDE clases 5 y 6 (m) | | | |
| 13 Sesgo MDE clases 3 y 4 (m) | | | |
| 14 Área de agua estimada ± IC (ha) | | | |
| 15 Agua bajo vegetación sin evaluar (declarada sí/no) | | | |
| 16 Referencia independiente o sesgo declarado (por variante) | | | |
| 17 Regla de etiquetado = definición del mapa (sí/no) | | | |
| 18 Fecha de la referencia seca y ha que saca R5 | | | |
