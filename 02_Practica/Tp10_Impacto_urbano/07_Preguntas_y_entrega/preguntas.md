# Tp10 — Preguntas, producto y rúbrica

Cada respuesta cita el archivo del que sale cada cifra (por ejemplo, `05_Resultados/04_Tablas/B_CONCORDIA_coincidencias_urbano.csv`, fila «control: urbano», par C_VV – L_HH). Las respuestas son cortas: lo que se evalúa es el razonamiento físico y la trazabilidad, no la extensión.

## Preguntas

**1. Doble rebote por banda (sinergia).** En la tabla de coincidencias, ¿qué par de bandas coincide más en la clase urbana de control y cuál menos? Elija **tres lugares** del mapa `bandas_que_marcan_urbano` donde las bandas discrepan y explique cada uno con el mecanismo de dispersión (diedro, volumen, superficie especular), con la longitud de onda, con la polarización (VV en C, HH en S y L) y con la **orientación de las calles respecto de la dirección de vuelo** de cada satélite (donde haya calles, mida en QGIS el ángulo de la cuadrícula con «Medir línea» y su acimut; si el lugar no tiene calles —una plantación, un lote—, dígalo: allí la orientación de las calles no aplica).
*Archivos:* `B_CONCORDIA_coincidencias_urbano.csv`, `B_CONCORDIA_urbano_por_banda_20m.tif`.

**2. El umbral.** ¿Qué umbral usó en cada banda y por qué? Muestre el histograma con la línea. ¿Por qué no se usa Otsu por defecto para la clase urbana, y qué pasó si lo probó?
*Archivos:* `B_CONCORDIA_hist_C_VV.png`, `_hist_S_HH.png`, `_hist_L_HH.png`, bitácora `Tp10_01_B_CONCORDIA.log`.

**3. Detalle y escala.** Según la tabla de detalle, ¿qué se pierde al pasar de 6 a 20 m: superficie, número de manchas, forma? ¿Qué escala recomendaría para un plan de ordenamiento urbano y cuál para un seguimiento provincial? Considere el desplazamiento de NovaSAR que aplicó: ¿a cuántos píxeles de 6 m equivale su error residual?
*Archivos:* `B_CONCORDIA_detalle_6_10_20m.csv`, `B_CONCORDIA_corregistro_S_NovaSAR_sigma0_HH_vs_OPT_S2_B08.csv` del Tp3 y el residual que midió a mano en QGIS (guía, paso 2, «Control del residual de corregistro»).

**4. Entrenamiento y fusión de rasgos.** ¿Cuántos píxeles de entrenamiento tiene cada clase y qué porcentaje del sitio ocupa el urbano en MapBiomas? De los 60 puntos que revisó sobre la imagen, ¿cuántos estaban mal? Compare la superficie urbana de cada variante con la de MapBiomas 2025 y con la que da `--equilibrar`: ¿qué le pasa al clasificador cuando todas las clases tienen el mismo número de ejemplos? ¿Qué capa es la más importante en la variante multisensor?
*Archivos:* bitácora `Tp10_02_B_CONCORDIA.log`, `B_CONCORDIA_entrenamiento_mapbiomas.csv`, `B_CONCORDIA_superficie_por_variante.csv`, `B_CONCORDIA_importancia_por_version.csv`.

**5. ¿Píxel o rasgo? ¿Escena o compuesto?** El script llama «fusión de píxel» a un clasificador que recibe VV y VH en dB, pero también NDBI, NDVI, MNDWI y la textura de VV. Según la definición del curso (REGLAS_DEL_PROYECTO.md, regla 5, y GLOSARIO.md, «Fusión»), ¿qué nivel de fusión es en sentido estricto? ¿Por qué se usan compuestos de temporada y no una escena suelta, y por qué el Sentinel-2 del 04/09/2026 queda fuera del compuesto? Mire `n_escenas_S2`: ¿dónde el compuesto óptico es casi una escena suelta?
*Archivos:* `B_CONCORDIA_compuestos_2026-09-16_20m.tif`, bitácora `Tp10_02_B_CONCORDIA.log`.

**6. Expansión urbana (detección de cambios por comparación posterior a la clasificación).** ¿Por qué se clasifica cada año por separado con el mismo método, y no con el Random Forest del paso 6 aplicado a 2019? ¿Cuántas hectáreas nuevas encontró y qué porcentaje de crecimiento representa? ¿Qué superficie queda «sin decidir» (clase 5) y qué tamaño tiene la clase 4? Compare con la ganancia bruta de área urbana de MapBiomas entre 2019 y 2025 (píxeles no urbanos en 2019 y urbanos en 2025), no con el cambio neto. Describa tres manchas de la clase 2 sobre la imagen (loteo, galpón, obra o error). ¿Qué órbita relativa usaron las dos fechas de Sentinel-1 y por qué tiene que ser la misma?
*Archivos:* `B_CONCORDIA_expansion_superficies.csv`, `B_CONCORDIA_expansion_2019_2026.tif`, bitácora `Tp10_03_B_CONCORDIA.log`.

**7. Validación e incertidumbre.** Complete la fila del Tp10 de la tabla de variantes (óptico solo, C solo, SAR multibanda C + L, multisensor) con exactitud global, omisión y comisión de la clase urbana, y área estimada con su intervalo de confianza del 95 %. ¿Alguna variante mejora significativamente a otra? (La mejora está demostrada si el IC del 95 % de la DIFERENCIA no incluye el cero.) ¿Por qué la exactitud fuera de bolsa del Random Forest no sirve para contestar esto? ¿Por qué la versión con S se valida aparte, en la huella de NovaSAR?
*Archivos:* `tabla_de_variantes_urbano.csv`, `B_CONCORDIA_variante_*_exactitud_y_area.csv` del Tp4.

**8. Subsidencia y referencia.** Describa la zona de referencia que digitalizó y por qué la supone estable. ¿Qué dio el control en los puntos estables (media, desvío, error de la media, puntos con dato)? ¿Cumple el criterio valor absoluto de la media < 2 × error de la media? ¿Cuántos pares marcó el programa como sospechosos de salto de desenrollado? Si no lo cumple, ¿qué explicación propone: referencia inestable, tendencia orbital, atmósfera?
*Archivos:* bitácora `Tp10_05_E_PARANA_DIAMANTE.log`, `E_PARANA_DIAMANTE_velocidad_vertical.tif`.

**9. Lectura conjunta (sinergia).** ¿Dónde está la mayor velocidad negativa? ¿Coincide con zonas urbanas nuevas, rellenos, la planicie del río o la barranca? Si en la barranca el «desplazamiento vertical» de HyP3 supone que no hay movimiento horizontal, ¿qué puede estar midiendo en realidad allí?

**10. Limitaciones.** Enumere las limitaciones de este práctico que pondría en un informe para el municipio: al menos la cobertura de NovaSAR, la diferencia de fechas entre sensores, la dependencia del doble rebote con la orientación de las calles, el uso de σ⁰ en NovaSAR frente a γ⁰ en C y L, el píxel de 40 m de la subsidencia y que PS no se hizo. ¿Cuál de ellas cambia más la conclusión?

**11. Diseño de la muestra (crear).** Diseñe una muestra para estimar el área urbana con tres estratos: urbano del mapa, una franja de 1 km alrededor de las manchas urbanas y el resto. Calcule cuántos puntos pondría en cada estrato con la fórmula del Tp4 y justifique el reparto: ¿cuánto se achica el IC del área frente al diseño de dos estratos? Elija además sus propios umbrales de C, S y L con la tabla de los 50 polígonos y diga en qué difieren de los del docente.
*Archivos:* `B_CONCORDIA_variante_multisensor.tif`, `diseno_tres_estratos.csv`.

## Producto a entregar

- Mapa de expansión urbana 2019 → 2026 de Concordia, con leyenda de las cinco clases, fechas de las escenas de cada sensor, fuentes, escala, EPSG:32721 y exactitud con IC del 95 % (si se validó).
- Mapa de velocidad vertical de Paraná – Diamante, con la zona de referencia, los puntos de control y el resultado del control.
- Las respuestas, la tabla de verificación y la bitácora de IA (ver `00_LEEME_que_va_aqui.md`).

## Rúbrica

| Criterio | Peso | Logrado | Parcial | No logrado |
|---|---|---|---|---|
| Sinergia: interpretación física de las coincidencias y diferencias entre C, S y L | 10 % | Explica cada discrepancia con mecanismo, longitud de onda, polarización y orientación de las calles | Describe las diferencias sin explicar la física | Confunde la tabla de coincidencias con una fusión |
| Umbrales documentados | 5 % | Cada umbral con histograma y justificación | Umbrales sin justificar o con un solo histograma | Umbrales por defecto sin mirar |
| Detalle y escala (6, 10 y 20 m) | 5 % | Cuantifica lo que se pierde (superficie, manchas, forma) con la tabla de detalle, lo relaciona con el residual de corregistro y recomienda escala según el uso | Da las cifras sin interpretarlas o sin el residual | No usa la tabla de detalle |
| Entrenamiento y fusión de rasgos | 15 % | Entrenamiento en proporción al paisaje y revisado; compara las variantes con MapBiomas y discute cobertura y fechas | Compara variantes sin revisar el entrenamiento o sin MapBiomas | Entrenamiento con el mismo número por clase, o la exactitud fuera de bolsa como exactitud del mapa |
| Expansión por comparación posterior a la clasificación | 15 % | Justifica la clasificación por año, revisa las clases 4 y 5, la órbita y el contraste con MapBiomas | Mapa correcto sin revisar clases 4 y 5 u órbita | Usa el Random Forest del paso 6 en 2019 |
| Validación e incertidumbre | 15 % | Variantes validadas con el Tp4, IC del 95 %; «mejora» sólo si el IC del 95 % de la diferencia no incluye el cero | Validación parcial o sin IC | Sin validación independiente |
| Subsidencia con referencia y control | 15 % | Referencia justificada, control fuera de ella, criterio valor absoluto de la media < 2 × error de la media aplicado y declarado, pares con saltos revisados | Referencia sin justificar o control mal ubicado | Sin referencia o sin control |
| Diseño propio de la muestra y de los umbrales (pregunta 11) | 5 % | Tres estratos con n justificado y comparación del IC; umbrales propios argumentados con la tabla | Estratos sin justificar o umbrales copiados | No lo hace |
| Comunicación y limitaciones | 10 % | Mapas completos (leyenda, fecha, fuente, escala, EPSG, incertidumbre); limitaciones jerarquizadas | Mapas incompletos o limitaciones genéricas | Mapas sin fuente o sin fecha; limitaciones ocultas |
| Trazabilidad y bitácora de IA | 5 % | Cada cifra con su archivo; bitácora completa | Algunas cifras sin archivo | Cifras sin origen |
