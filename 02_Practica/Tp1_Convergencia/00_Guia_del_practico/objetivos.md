# Tp1 — Objetivos

## Objetivo general

Buscar, verificar y documentar, sobre un sitio y alrededor de un evento, los datos
SAR (bandas X, C, S, L y P), ópticos y LiDAR que existen, y decidir con criterio
explícito el **grado de convergencia** que permiten: completa, parcial, un solo
sensor cerca del evento o histórica.

## Objetivos específicos

1. Definir el polígono oficial del sitio y la ventana temporal del evento, y
   comprobar en QGIS que el sitio cae donde debe.
2. Consultar los catálogos que el curso usa (Planetary Computer, ASF, NASA
   Earthdata, ESA MAAP) y los portales por pedido (CONAE, Bhoonidhi, CSIRO, ASI), y
   entender qué devuelve cada uno.
3. **Verificar la cobertura real** de cada escena contando píxeles con dato dentro
   del sitio, en lugar de confiar en la huella que declara el catálogo.
4. Registrar de cada escena la fecha y la hora **UTC tomadas de los metadatos**, la
   órbita o pasada, el modo y la polarización.
5. Contar las huellas GEDI y los segmentos ATL08 válidos dentro del sitio, con el
   motivo de cada descarte.
6. Armar la matriz sensor × fecha, asignar el grado de convergencia y explicar qué
   habilita: fusión de píxel o de rasgo, sinergia o fusión de decisión, o sólo
   interpretación.
7. Declarar las ausencias (una banda que falta en una colección, GEDI en receso, servicio que no respondió)
   **antes** de procesar, no después.
8. Comparar la respuesta de la banda L y de la banda C entre una fecha anterior y una durante el evento,
   con pares de la misma geometría, cada banda contra su propio cambio general.

## Qué se entrega

- Las planillas de `05_Resultados/04_Tablas/` y la planilla manual
  `04_Tablas_de_trabajo/escenas_por_pedido.csv`, completas.
- La matriz y el grado de convergencia de `B_CONCORDIA` alrededor del 04/11/2023.
- La figura de la línea de tiempo, con su cita de fuentes.
- Las respuestas a `07_Preguntas_y_entrega/preguntas.md`.
- El acta del control cruzado con otro grupo.
- La bitácora de IA: el prompt, la respuesta, la corrección humana y la verificación.

## Criterio de evaluación

No se evalúa la cantidad de escenas encontradas, sino **la calidad de la
verificación**. Detectar qué escena NO sirve, y explicar por qué (nubes dentro del
sitio, cobertura parcial, borde inválido, pasada distinta, fecha lejana), vale tanto
como encontrar la que sirve. Una matriz con menos escenas pero todas verificadas vale
más que una larga copiada del catálogo.
