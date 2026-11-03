# Tp1 — Preguntas, producto y rúbrica

Cada respuesta cita el archivo del que sale la cifra (por ejemplo,
`05_Resultados/04_Tablas/inventario_local.csv`, fila de la escena 47942). Respuestas
cortas: dos a cinco oraciones, con el dato y la razón física o metodológica.

## Preguntas

1. **Huella frente a dato.** En `inventario_local.csv`, elija dos combinaciones
   escena-sitio donde `cobertura_huella_%` y `pixeles_validos_%` difieran mucho.
   ¿Por qué difieren en cada caso (forma de la franja, borde inválido de NISAR,
   georreferencia por cuatro esquinas de NovaSAR)? ¿Cuántas combinaciones
   «engañosas» informó la bitácora de `Tp1_02`?

2. **Nubosidad.** En `planilla_MPC_B_CONCORDIA.csv`, ¿qué escena Sentinel-2 muestra la
   mayor diferencia entre `nubosidad_catalogo_%` y `nubosidad_sitio_%`? ¿Qué habría
   pasado si se la hubiera elegido o descartado con la cifra del catálogo?

3. **Geometría del radar.** ¿Cuántas órbitas relativas de Sentinel-1 cubren
   `B_CONCORDIA` en la ventana? Si hubiera que comparar dos fechas pixel a pixel,
   ¿cuáles elegiría y por qué no mezclaría órbitas distintas?

4. **La escena que queda afuera.** La NovaSAR 47942 (13/09/2023) cubre el 39 % de
   `B_CONCORDIA`. ¿Por qué `Tp1_07` no la incluye en la matriz? Proponga y defienda una
   regla de entrada a la matriz distinta del 50 % para escenas parciales, y diga qué
   cambiaría en el grado. ¿Y por qué la 50896, con la misma hora de pasada, no sirve
   para Concordia?

5. **Ausencias.** Enumere lo que **no** hay alrededor del 04/11/2023 (GEDI, banda P,
   banda X, banda S) con la fuente que lo demuestra (bitácora, planilla o fila
   `sin cobertura` / `sin acceso`). ¿La banda L falta o está? ¿En qué colecciones no
   aparece y en cuáles sí? ¿Cuál de esas ausencias limita más lo que se podrá hacer en
   el Tp6?

6. **LiDAR.** En `lidar_conteo_B_CONCORDIA.csv` (período completo), ¿cuántas huellas
   GEDI y segmentos ATL08 caen en el sitio y cuántos son válidos? ¿Cuál es el motivo
   de descarte más frecuente y qué tiene que ver con el paisaje de Concordia (río,
   embalse, ciudad)? ¿Alcanzan para usar el LiDAR como referencia o sólo como
   ilustración?

7. **Sinergia o fusión.** Con el grado de `grado_convergencia_B_CONCORDIA.csv`, ¿qué
   se podrá hacer en el Tp6: sinergia, fusión de decisión o fusión de píxel? Justifique
   con los tres requisitos de la fusión (misma grilla, corregistro menor que un píxel,
   fechas compatibles). ¿Cuál de los tres ya puede evaluarse en el Tp1 y cuáles
   recién en el Tp3?

8. **Ventana temporal.** Repita mentalmente el paso 7 con `--ventana 3` y con
   `--ventana 30`. ¿Cambiaría el grado? ¿Qué ventana defiende para una crecida del río
   Uruguay, y por qué no sería la misma para una quema de pastizal en el Delta?

9. **Validación de la búsqueda.** ¿Coincidieron sus escenas con las del otro grupo?
   Si no, ¿cuál fue la causa? ¿Qué dice eso sobre la reproducibilidad de una búsqueda
   que «sólo» depende de un catálogo?

10. **Limitaciones.** Los sitios «aproximada» no están ajustados y las búsquedas
    dependen de que los servicios respondan. Nombre dos limitaciones de su matriz que
    un lector del informe del trabajo final del curso debería conocer.

11. **El contexto del sitio.** Con `B_CONCORDIA_mapbiomas_area_por_clase_y_anio.csv` y
    `B_CONCORDIA_contexto_por_clase.csv` (paso 9): ¿qué clases de MapBiomas crecieron y
    cuáles se achicaron entre 1985 y 2025? ¿Qué clase tiene más biomasa según el CCI y
    cómo se ve en la banda P (VH)? ¿Por qué hay que enmascarar el agua antes de
    mirar la altura FH de BIOMASS, y por qué, aun sin agua, no se usa en Concordia? ¿Por qué ninguno de estos productos entra a la matriz de convergencia?

12. **Complementos de QGIS.** Con la salida de GEDIMetrics y de GEDI-Pipeline del
    paso 5 (g): ¿coinciden las huellas y las válidas con las de Tp1_05? ¿Cuántas
    válidas hay con los filtros por defecto del complemento y cuántas con los del
    curso? Las huellas de más de 50 m del 16/07/2019, ¿son árboles? Justifique con la
    clase de WorldCover, la biomasa del L4A y la forma de onda. ¿Para qué sirve cada
    complemento en los prácticos y qué no puede reemplazar del script?

13. **Banda L antes y durante.** Lea en el Desarrollo la tabla de los pares
    antes–durante (`B_CONCORDIA_antes_despues_por_zona.csv`, de `Tp1_06b`): ¿cuánto
    cambia la tierra sin agua y cuánto el agua de crecida de banda C en el par SAOCOM
    TNA y en el par Sentinel-1? ¿Por qué cada banda se compara contra su propio cambio
    general y no se resta una de la otra? ¿Por qué la comparación de la banda C dentro
    de su propia máscara es circular, y qué zona sirve de prueba independiente?

## Producto a entregar

- Planillas de `05_Resultados/04_Tablas/` y `04_Tablas_de_trabajo/escenas_por_pedido.csv`.
- Matriz, grado y línea de tiempo de `B_CONCORDIA` para el 04/11/2023.
- Las tablas y los dos gráficos del contexto del sitio (paso 9).
- Respuestas a estas trece preguntas, con la cita del archivo de cada cifra.
- La bitácora de IA: prompt, respuesta, corrección humana y verificación.
- Tabla de verificación y acta del control cruzado.

## Rúbrica

| Criterio | Peso | Logrado | Parcial | No logrado |
|---|---|---|---|---|
| Verificación dentro del sitio (huella frente a dato, nubosidad del sitio) | 20 % | Usa las dos cifras y explica cada diferencia | Usa las dos cifras sin explicar | Usa la huella o la nubosidad de catálogo |
| Fechas, órbitas y polarizaciones | 10 % | Fechas UTC de metadatos, órbita y pasada para cada escena | Faltan datos en algunas escenas | Fechas de archivo o sin órbita |
| Banda L antes y durante (pregunta 13) | 10 % | Cada banda contra su propio cambio general y circularidad de la C declarada | Lee las cifras sin explicar la comparación | Resta una banda de la otra o toma la C dentro de su máscara como prueba |
| Ausencias declaradas | 10 % | Cada ausencia con su fuente y su consecuencia | Ausencias listadas sin fuente | Ausencias omitidas o «rellenadas» |
| LiDAR: conteo y motivos | 10 % | Huellas válidas y motivos interpretados | Conteo sin interpretación | Granulos contados como huellas |
| Grado de convergencia y uso (sinergia o fusión) | 15 % | Grado coherente y justificado con los tres requisitos | Grado correcto sin justificar | Grado incoherente con las ausencias |
| Control cruzado y reproducibilidad | 10 % | Coincidencia o diferencias explicadas | Diferencias sin causa | Sin control |
| Contexto del sitio y control de productos de terceros (MapBiomas, CCI, banda P, GEDIMetrics), preguntas 11 y 12 | 10 % | Lee cada producto con su incertidumbre y su control | Da las cifras sin el control | Toma un producto de terceros como verdad |
| Trazabilidad (cada cifra con su archivo) y bitácora de IA | 5 % | Todas citadas y la bitácora completa | Algunas citadas o bitácora incompleta | Ninguna citada |
