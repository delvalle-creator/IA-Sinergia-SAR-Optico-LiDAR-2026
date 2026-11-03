# Tp5 — Preguntas y entrega

Cada respuesta cita el archivo del que sale cada cifra.

## Preguntas

1. **Qué ve cada sensor.** Dé la mediana de ΔVH (C) y de ΔHV (L) en un sector quemado de pajonal y en uno de albardón. Explique la diferencia con el tamaño de la onda (5,5 cm frente a unos 23 cm) y el mecanismo de dispersión. (`A1_DELTA_QUEMAS_indicadores_20m.tif`, `Tp5_01_indicadores.log`)
2. **Umbrales.** ¿Qué umbral quedó para cada indicador, con qué método, y qué porcentaje del sitio deja como quemado? ¿Algún histograma no era bimodal? ¿Qué hizo entonces? ¿Por qué el dNBR de 0,27 no se adopta tal cual en un humedal? (`histograma_*.png`, `Tp5_02_sinergia.log`)
3. **Sinergia.** Con las medianas por estrato de estructura (CCI Biomass 2020: pajonal < 15 Mg/ha, albardón ≥ 30 Mg/ha; Tabla 5 del Desarrollo u Orange `Tp5_A`), ¿se cumple que en el pajonal la C cae más que la L y que en el albardón la L acompaña? ¿La diferencia de medianas alcanza para clasificar píxel a píxel? Si no se cumple, proponga una explicación física o de fechas. (`A1_sinergia_coincidencias.csv`, `Tp5_A_muestra_pixeles.csv`)
4. **Fusión de decisión.** ¿Qué regla usó para V3 y cuántos radares votaron? Con dos radares, ¿por qué `mayoria` equivale a `interseccion`? ¿Qué regla elegiría para un mapa de alerta temprana y cuál para un informe de daños, y por qué? (`Tp5_03_fusion.log`, banda `votos` de `A1_variante_CL.tif`)
5. **Fusión de rasgo.** ¿Qué variables tuvieron más importancia en el Random Forest? ¿Por qué la exactitud fuera de bolsa no es la exactitud del mapa? ¿Qué dice la ablación por polígono de Orange (`Tp5_D_ablacion_por_poligono.ows`) sobre el aporte del radar? ¿Por qué la V3 es de decisión y la V4 de rasgo, si las fechas difieren en las dos? (`A1_importancia_variables.csv`)
6. **Validación e incertidumbre.** Complete la tabla de variantes: exactitud global, omisión y comisión de quemado, y área quemada estimada ± IC. ¿La multisensor mejora a la óptica y a la C sola, con un IC del 95 % de la diferencia que excluye el cero (bitácora de `Tp4_04`)? ¿Qué imagen usó como referencia y comparte dato con alguna variante? ¿Qué acuerdo tuvo la revisión de 30 puntos con otro grupo? (`tabla_de_variantes_quemado.csv`, `revision_30_puntos_segundo_interprete.csv`)
7. **Humo y nubes.** ¿Cuántas hectáreas quedaron sin dato en V1 por nubes o humo? ¿Las cubrió alguna variante de radar? ¿Qué dice eso sobre la pregunta del práctico, «aun bajo humo»?
8. **Evidencia estructural.** Con la misma estación antes y después (`--antes_desde`, `--despues_hasta`), ¿cuántas celdas GEDI tuvieron huellas antes y después? ¿Qué mediana de Δrh98 tienen las celdas «quemado» y las «no quemado»? ¿Qué fracción tiene rh98 previo < 3 m, el piso del instrumento? ¿Cuántas celdas leñosas caen en lo quemado? (`A1_delta_rh98_por_clase.csv`, `Tp5_04_gedi.log`)
9. **Limitaciones.** Nombre al menos tres y su efecto: las quemas anteriores a la fecha «antes» (empezaron en febrero de 2020; mire el mes de quema de MapBiomas Fuego en el sitio), el mosaico anual ALOS-2 (fecha de cada píxel), la lluvia y la bajante del Paraná (separe el efecto de cada una), el píxel de 20 m frente a 25 m, la referencia que comparte dato con el mapa, el entrenamiento digitalizado por el grupo, el desfase de ventanas entre sensores. Con el mes de quema de MapBiomas Fuego, ¿cuántas hectáreas caen dentro de la ventana de cada sensor? ¿Con qué cifra debe compararse el área estimada?
10. **Severidad.** ¿Qué exactitud de usuario y de productor tiene cada clase de severidad? ¿Por qué el área estimada de severidad alta (9.544 ± 2.860 ha) cuadruplica la del mapa? ¿Puede llamarse severidad ecológica? (`A1_severidad_multisensor_exactitud_y_area.csv`)
11. **Diseño.** Proponga cómo reduciría el efecto del aumento general de humedad (por ejemplo, ΔVH relativo a la mediana del no quemado del mismo estrato, pares Sentinel-1 más cercanos o en días secos, promedio de varias pasadas, coherencia interferométrica) y qué esperaría de la variante C con ese cambio.

## Producto a entregar

Perímetro con exactitud por variante y severidad con su propia exactitud (o con la leyenda «severidad no validada»): el mapa de severidad y el perímetro (variante elegida) con leyenda, fecha y fuentes; la tabla de variantes con IC; la tabla de coincidencias de la sinergia; la tabla de Δrh98; las respuestas.

## Rúbrica

| Criterio | Peso | Logrado | Parcial | No logrado |
|---|---|---|---|---|
| Indicadores en lineal y física de cada banda | 15 % | ΔVH y ΔHV calculados en lineal y explicados por mecanismo de dispersión | Calculados bien, explicación vaga | dB promediados o sin explicación |
| Umbrales documentados | 10 % | Histograma, método y justificación para cada uno | Otsu sin revisar el histograma | Umbral sin documentar |
| Sinergia leída por estrato de estructura | 20 % | Medianas por estrato (CCI) interpretadas; coherencia física evaluada y discrepancias explicadas | Tabla presentada sin interpretar | Sinergia confundida con fusión |
| Fusión justificada (decisión y rasgo) | 15 % | Nivel elegido por el tipo de salida (binaria con un umbral por radar, o graduada con los valores) y diferencias de fecha declaradas; regla escrita; entrenamiento independiente | Fusión correcta sin justificar el nivel | Fusión sin regla o con entrenamiento usado como validación |
| Validación de variantes con IC | 20 % | Tabla completa, área estimada ± IC, IC de la diferencia, referencia independiente o dependencia declarada, severidad validada | Tabla incompleta o conclusión exagerada | Exactitud fuera de bolsa informada como exactitud |
| Evidencia GEDI y limitaciones | 10 % | Δrh98 en la misma estación, leído con el piso del instrumento en cuenta; limitaciones con su efecto | Limitaciones listadas sin efecto | No declaradas |
| Comunicación | 10 % | Mapas con leyenda, fecha, fuentes e incertidumbre | Falta un elemento | Mapas sin fuente ni fecha |
