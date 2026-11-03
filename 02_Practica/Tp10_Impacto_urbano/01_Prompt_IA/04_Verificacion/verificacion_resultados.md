# Verificación de lo que entregó la IA y de los resultados del Tp10

Un programa que corre no es un programa que está bien. Esta lista se recorre **después** de correr cada paso, con la bitácora y los archivos de `05_Resultados` abiertos. Cada control tiene un criterio de aceptación: si no se cumple, se declara.

## A. Controles sobre el código (antes de creerle a los números)

| N.º | Qué se verifica | Cómo | Se acepta si |
|---|---|---|---|
| 1 | El radar se guarda en lineal | Abrir `B_CONCORDIA_urbano_por_banda_20m.tif` en QGIS, banda `C_VV`, Identificar en la ciudad | Valores positivos del orden de 0,01 a 10, no negativos (los negativos serían dB) |
| 2 | La máscara de NISAR está aplicada | Mirar la banda `L_HH` en el borde de la franja | No hay un borde de valores extremadamente bajos; fuera de la franja, sin dato |
| 3 | NovaSAR se declaró σ⁰ | Etiqueta FUENTE del ráster (`Propiedades > Metadatos` en QGIS) | Dice «sigma0 = DN^2/1e+05» |
| 4 | Cada umbral tiene su histograma | `05_Graficos/B_CONCORDIA_hist_*.png` | Un PNG por banda con la línea del umbral y el título del método |
| 5 | La tabla de coincidencias no fusiona | `B_CONCORDIA_coincidencias_urbano.csv` | Una fila por par de bandas; ningún mapa combinado sale de este paso |
| 6 | El clasificador no recibe ceros por falta de dato | Bitácora de `Tp10_02`: «cubre el X % del sitio» de `con_S` | El porcentaje de `con_S` no supera la cobertura de NovaSAR del paso 1 |
| 7 | La exactitud fuera de bolsa está rotulada como optimista | Bitácora de `Tp10_02` | Aparece la palabra OPTIMISTA |
| 8 | La expansión usa el mismo método en las dos fechas | Bitácora de `Tp10_03` | Una sola regla impresa, aplicada a la base y a la final |
| 9 | El cambio sólo se marca si es confiable en las dos fechas | Bitácora de `Tp10_03` y `B_CONCORDIA_expansion_matriz_transiciones.csv` | La regla p ≥ 0,6 en las dos fechas y mancha ≥ 5 píxeles está impresa; la matriz urbano 2019 × urbano 2026 × confiable existe y se cita |
| 10 | La subsidencia tiene referencia | Bitácora de `Tp10_05` | «Zona de referencia: N pixeles» con N ≥ 10 (sin el AVISO de menos de 10); no aparece el AVISO «sin --referencia; se usa la mediana de los N pixeles persistentes» |
| 11 | Ninguna credencial en los scripts | Buscar `password`, `token`, `usuario` en los `.py` | Sólo lecturas de `.netrc`, de variable de entorno o pedido por teclado |
| 12 | Cada figura lleva fuente | Los PNG de `05_Graficos` | Línea «Fuente: …» al pie con organismo, sensor y fecha |

## B. Controles sobre los resultados

| N.º | Control | Archivo | Criterio de aceptación |
|---|---|---|---|
| 13 | Corregistro de NovaSAR | DX, DY de la bitácora de `Tp3_02` y el residual medido a mano en QGIS (paso 2, «Control del residual de corregistro») | Mediana de las distancias menor o igual que un píxel de la grilla (20 m); si es igual, se declara que el corrimiento es de un píxel |
| 14 | Umbral urbano por banda | `hist_*.png` y bitácora de `Tp10_01` | La línea cae en el comienzo de la cola brillante; el porcentaje de la clase es compatible con la fracción urbana del sitio |
| 15 | Sinergia en la clase urbana de control | Fila «control: urbano» de la tabla de coincidencias | `%_ambos` alto en todos los pares; si no, explicar por banda |
| 16 | Detalle 6 – 10 – 20 m | `B_CONCORDIA_detalle_6_10_20m.csv` | Con la unidad mínima de 1.200 m² (tres píxeles de 20 m) en las tres escalas, el perímetro/área crece al afinar el píxel; el número de manchas depende del filtro y se informa con él; si la superficie cambia mucho, se declara |
| 17 | Aporte de la banda S | `B_CONCORDIA_importancia_por_version.csv` y acuerdo entre versiones | Se informa la posición de `S_HH_dB` y el acuerdo, sea cual sea |
| 17b | Aporte de la banda S validado | `Tp4_Validacion/05_Resultados/04_Tablas/B_CONCORDIA_variante_multisensor_con_S_exactitud_y_area.csv` | Exactitud con IC, referida a la huella de NovaSAR |
| 18 | El agua no es urbana | `B_CONCORDIA_clases_sin_S.tif` sobre el embalse y el río | Clase 4 en el agua abierta |
| 19 | Clase 4 de la expansión | `B_CONCORDIA_expansion_superficies.csv` | Menor que el 20 % de la clase 2 (si no, el programa avisa: se revisan las manchas en la imagen y se declara) |
| 20 | Misma órbita en 2019 y 2026 | Bitácora de `Tp10_03` | La línea «Orbita relativa de Sentinel-1 en la fecha final: N» y las dos fechas de Sentinel-1 encontradas |
| 21 | Red SBAS conexa | Bitácora de `Tp10_04` | `subredes: 1` y sin el AVISO «la red esta cortada en K subredes» |
| 22 | Control en puntos estables | Bloque CONTROL de `Tp10_05` | Valor absoluto de la media < 2 × error de la media (error de la media = desvío / raíz de n); además, cuántos pares marcó el programa con salto de desenrollado |
| 23 | Puntos de control fuera de la referencia | Bitácora de `Tp10_05` | Sin los AVISOS de puntos dentro de la referencia o fuera de la grilla (si aparecen, esos puntos se excluyeron) |
| 24 | Exactitud independiente | `Tp4_Validacion/05_Resultados/04_Tablas/B_CONCORDIA_variante_*_exactitud_y_area.csv` | Calculada con puntos etiquetados al azar; con IC del 95 % |
| 25 | Mejora de la fusión | `Tp10_Impacto_urbano/05_Resultados/04_Tablas/tabla_de_variantes_urbano.csv` | Se afirma «mejora» sólo si el IC del 95 % de la DIFERENCIA no incluye el cero (lo informa `Tp4_04`); que los IC de cada variante se superpongan no prueba que no haya mejora |

## C. Cifras que deben quedar en la bitácora del grupo

- Fecha y hora UTC de cada escena: Sentinel-1 (paso 2 y las dos fechas del paso 7, con su órbita), Sentinel-2 (con la nube en el sitio), NovaSAR 47942 (13/09/2023), NISAR (18/09/2026).
- Desplazamiento aplicado a NovaSAR (DX, DY en metros) y residual medido.
- Porcentaje del sitio con dato de NovaSAR.
- Umbral de cada banda y porcentaje de píxeles en la clase urbana.
- Número de polígonos de entrenamiento por clase.
- Para `con_S` y `sin_S`: cobertura, exactitud fuera de bolsa (optimista) y las tres capas más importantes.
- Acuerdo entre versiones donde hay NovaSAR.
- Superficie por clase de la expansión y el crecimiento en porcentaje.
- Número de pares de la red, aptos y usados; píxeles de la referencia.
- Velocidad: mediana, percentiles 5 y 95; control: media, desvío, máximo y puntos con dato.
- Exactitud global, omisión y comisión con IC de cada variante validada.

## D. Tabla para el grupo

| Control | Valor obtenido | Archivo de donde sale | ¿Cumple? | Comentario |
|---|---|---|---|---|
| Residual de corregistro NovaSAR (px) | | | | |
| Umbral C VV (dB) / % en clase | | | | |
| Umbral S HH (dB) / % en clase | | | | |
| Umbral L HH (dB) / % en clase | | | | |
| Cobertura NovaSAR en el sitio (%) | | | | |
| `%_ambos` C–L en control urbano | | | | |
| Manchas a 6 / 10 / 20 m | | | | |
| Cobertura `con_S` / `sin_S` (%) | | | | |
| Capa más importante `con_S` / `sin_S` | | | | |
| Acuerdo entre versiones (%) | | | | |
| Nuevo urbano 2019 → 2026 (ha) | | | | |
| Matriz de transiciones (sí/no × confiable) | | | | |
| Clase 4 / clase 2 | | | | |
| Órbita relativa S1 (base y final) | | | | |
| Pares aptos / usados | | | | |
| Píxeles de referencia | | | | |
| Velocidad en control: media, desvío y error de la media (mm/año) | | | | |
| Pares con salto de desenrollado | | | | |
| Exactitud global multisensor ± IC | | | | |
| Exactitud global óptico solo ± IC | | | | |
| Exactitud global C solo ± IC | | | | |

## E. Tabla D resuelta por el docente (corridas del 23 al 27/10/2026)

Sirve de modelo. Un control que falla se declara: vale más que un mapa sin control.

| Control | Valor obtenido | Archivo de donde sale | ¿Cumple? | Comentario |
|---|---|---|---|---|
| Residual de corregistro NovaSAR (px) | 20 m de mediana y 40 m en el percentil 90 (1 y 2 píxeles de 20 m) | 113 ventanas de 2 km, medición del docente | No (en el límite) | Es un píxel de 20 m, no menos: la banda S se fusiona a 20 m sabiendo que corre un píxel; a 6 m son 3 a 7 píxeles |
| Umbral C VV (dB) / % en clase | −6 dB / 3,7 % | `Tp10_01_B_CONCORDIA.log` | Sí | Marca el 71 % del urbano denso y 0 % de vegetación en los 50 polígonos |
| Umbral S HH (dB) / % en clase | −3 dB / 4,7 % de la franja | ídem | Sí | |
| Umbral L HH (dB) / % en clase | 0 dB / 3,2 % | ídem | Sí | Con −3 dB marcaba el 15 % de la vegetación |
| Cobertura NovaSAR en el sitio (%) | 39,5 % (39,3 % con dato óptico también) | ídem y `Tp10_02_B_CONCORDIA.log` | Sí | |
| `%_ambos` C–L en control urbano | 82,4 % | `B_CONCORDIA_coincidencias_urbano.csv` | Sí | |
| Manchas a 6 / 10 / 20 m | 5.598 / 6.346 / 9.798 (400 m²); 1.760 / 1.761 / 2.060 (1.200 m²) | `B_CONCORDIA_detalle_6_10_20m.csv` | No | Con el filtro de 400 m² (un píxel de 20 m) a 20 m no se descarta nada y a 6 m sí: hay más manchas a 20 m. Con 1.200 m² en las tres escalas la diferencia casi desaparece; el perímetro/área sí crece al afinar (26,8 a 42,6 1/km) |
| Cobertura `con_S` / `sin_S` (%) | 39,3 / 99,7 | `Tp10_02_B_CONCORDIA.log` | Sí | |
| Capa más importante `con_S` / `sin_S` | MNDWI (0,131) / B03 (0,120) | `B_CONCORDIA_importancia_por_version.csv` | Sí | Importancia de Gini: no reparte el aporte entre sensores |
| Acuerdo entre versiones (%) | comisión 0,083 sin S y 0,115 con S con la misma muestra | `tabla_de_variantes_urbano_huella_S.csv` | Sí | La banda S no mejora el mapa con esta muestra |
| Nuevo urbano 2019 → 2026 (ha) | 38,6 | `B_CONCORDIA_expansion_superficies.csv` | Sí (sin validar) | Exploratorio: el cambio no tiene muestra propia |
| Matriz de transiciones | ganancias 132,4 ha confiables y 1.249,9 no confiables; pérdidas 47,5 y 1.130,0 | `B_CONCORDIA_expansion_matriz_transiciones.csv` | Sí | La clase 5 se reparte casi por mitades entre ganancias y pérdidas inciertas: es ruido del borde |
| Clase 4 / clase 2 | 11,0 / 38,6 ha = 28,5 % | `B_CONCORDIA_expansion_superficies.csv` | No | Supera el 20 %. Las manchas de clase 4 caen en otras clases de MapBiomas (8,7 ha) y en Salto (2,3 ha): borde de la ciudad y lotes, no «des-urbanización» |
| Órbita relativa S1 (base y final) | 68 y 68 | `Tp10_03_B_CONCORDIA.log` | Sí | |
| Pares aptos / usados | 134 / 120 | `Tp10_04_red_E_PARANA_DIAMANTE.log` | Sí | Los 14 aptos posteriores al 03/07/2026 no entraron |
| Píxeles de referencia | 54 | `Tp10_05_E_PARANA_DIAMANTE.log` | Sí | |
| Velocidad en control: media, desvío y error de la media (mm/año) | −1,5; 4,9; 1,3 | ídem | Sí | 1,5 < 2 × 1,3 = 2,5 |
| Pares con salto de desenrollado | 1 de 120 (22/04 a 09/06/2026, 48 días) | ídem y `E_PARANA_DIAMANTE_pares_usados.csv` | No (se declara) | Sin ese par la mediana del sitio pasa de −4,9 a −1,5 mm/año y el control deja de cumplir (media +3,0, error 0,8): la referencia y el resultado dependen de un solo par |
| Exactitud global multisensor ± IC | 0,983 ± 0,021 | `tabla_de_variantes_urbano.csv` | Sí | La domina el no urbano |
| Exactitud global óptico solo ± IC | 0,979 ± 0,021 | ídem | Sí | |
| Exactitud global C solo ± IC | 0,974 ± 0,021 | ídem | Sí | |
