# Tp7 — Objetivos

## Objetivo general

Determinar si hubo deformación previa en la barranca de Diamante en octubre de
2018 y evaluar con qué modelos de elevación se podría estimar el volumen
movilizado (los disponibles son anteriores al evento), combinando interferometría en dos bandas
(X y C), óptico y modelos de elevación, y **declarando qué parte del resultado
es detectable y qué parte es ruido**.

## Objetivos específicos

1. Desenrollar la fase del par COSMO-SkyMed 15/10–19/10/2018 con SNAPHU (en SNAP
   o desde Python), evaluar su confiabilidad con las componentes conexas y
   convertir la fase desenrollada a desplazamiento en la línea de visión.
2. Seleccionar un par Sentinel-1 del mismo período con criterios explícitos
   (separación temporal, línea de base perpendicular, misma órbita y pasada) y
   obtener su coherencia y desplazamiento.
3. Comparar la coherencia y el desplazamiento de cada banda en la ladera y en una
   zona de referencia estable (**sinergia**), y explicar la diferencia con la física
   de cada longitud de onda, separando su efecto del de la resolución, la
   cobertura y el intervalo.
4. Aplicar una **fusión de decisión** escrita («deformación confirmada sólo si
   todas las bandas coherentes superan el umbral con el signo que tendría en su
   línea de visión el movimiento esperado»), declarando la pasada y la incidencia
   de cada banda leídas en los metadatos, y comprobarla en una zona de control
   independiente de la usada como referencia (por ejemplo, la mitad norte del
   anillo como referencia y la sur como control).
5. Digitalizar la cicatriz y el depósito con un protocolo escrito y calcular el
   volumen por diferencia de MDE (GLO-30 «antes» e IGN 5 m «después», a 30 m: una
   pérdida da dZ negativo), restando el sesgo medido en zona estable y
   comparando con una escarpa de control, y
   declarar que, con dos MDE anteriores al evento, el resultado es un ejercicio de
   método y no el volumen de 2018.
6. Controlar el MDE con alturas de terreno de ICESat-2 (ATL08) y declarar el
   límite de detección del volumen.

## Qué debe entregar

- La tabla de coherencia y desplazamiento por banda, con su interpretación.
- El ráster de deformación confirmada, con la regla de fusión escrita y el
  número de bandas que votó en cada píxel.
- La tabla de volúmenes con el sesgo restado, el ruido de la zona estable, el
  porcentaje de píxeles que supera dos desvíos con el signo esperado y con el
  contrario, y la escarpa de control.
- El GeoPackage de cicatriz y depósito, con la fuente de cada polígono.
- Las bitácoras de los scripts y la de SNAP (operadores y parámetros usados).
- La tabla de verificación completa (`01_Prompt_IA/04_Verificacion/verificacion_resultados.md`).
- Las respuestas a las preguntas, con la cita del archivo del que sale cada cifra.

## Criterio de evaluación

No se evalúa que aparezca deformación, sino **que se pueda defender lo que se
informa**. Un «no se detecta deformación por encima del ruido» bien medido vale
tanto como un mapa de deformación. Un volumen sin el control de la zona estable
no se acepta.
