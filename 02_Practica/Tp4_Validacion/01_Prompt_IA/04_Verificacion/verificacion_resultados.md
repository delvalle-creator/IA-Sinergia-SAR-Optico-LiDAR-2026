# Verificación de los resultados del Tp4

Este protocolo se aplica dos veces: sobre lo que la IA entregó (los scripts) y
sobre los resultados de cada corrida. Cada control tiene su criterio de
aceptación. Si uno no se cumple, no se avanza.

## A. Controles sobre los scripts

1. **El estimador reproduce el ejemplo publicado.**
   `python Tp4_03_exactitud_y_area.py --autoprueba`.
   Acepta si imprime `AUTOPRUEBA: CORRECTA` (deforestación 21.158 ± 6.158 ha,
   usuario 0,88, productor 0,75, global 0,95). Con datos reales, ya lo hace.
2. **El archivo a etiquetar no trae la clase del mapa.** Abra el GeoPackage
   `<NOMBRE>_puntos_a_etiquetar.gpkg` en QGIS y mire sus campos. Acepta si sólo
   están `id`, `clase_ref`, `confianza`, `imagen_usada`, `observacion` (y la
   geometría).
3. **El orden de los `id` no delata el estrato.** Acepta si los `id` 1 a 10
   caen dispersos por el sitio, no agrupados en una clase.
4. **El diseño es reproducible.** Corra `Tp4_02` dos veces sobre el mismo mapa,
   antes de etiquetar (con puntos ya etiquetados el script no reescribe y avisa):
   con la misma `--semilla`, la llave debe ser idéntica.
5. **El reparto respeta el mínimo.** En `<NOMBRE>_diseno_muestral.csv`, acepta si
   cada `n_i` ≥ `--minimo` (o igual al número de píxeles de la clase, si la clase
   tiene menos píxeles que el mínimo).
6. **La prioridad de fuentes del mapa de control se cumple.** En la tabla
   `<SITIO>_cobertura_control_resumen.csv`, acepta si para cada clase
   `de_digitalizacion + de_JRC + de_MapBiomas = pixeles`, y si en QGIS un
   polígono digitalizado sobre un píxel que JRC marca como agua conserva la
   clase digitalizada.

## B. Controles sobre los resultados

7. **Agua permanente en su lugar.** El agua de JRC (clase 1, fuente 2) cae
   sobre el río Uruguay y el embalse de Salto Grande. Acepta si no aparecen
   bañados de crecida marcados como agua permanente.
8. **El área total se conserva.** En `<NOMBRE>_exactitud_y_area.csv`, acepta si
   la suma de `area_estimada_ha` iguala la suma de `area_mapa_ha` (diferencia
   menor que 1 ha, por redondeo).
9. **Puntos sin etiquetar declarados.** Acepta si la bitácora de `Tp4_03` dice
   cuántos puntos quedaron sin `clase_ref`, y si son menos del 10 % de la
   muestra. Si son más, el intervalo informado es más ancho que el diseñado y
   se dice.
10. **Clases de referencia ajenas al mapa.** No se excluyen: cuentan como error del
    mapa. Acepta si son cero o pocas; si son más del 5 %, el mapa omite una clase
    entera y se comenta.
11. **Acuerdo entre intérpretes.** En los diez puntos etiquetados por dos
    personas (`Tp4_07_acuerdo_entre_interpretes.py --preparar` y `--medir`), acepta
    si coinciden en al menos 8. Si no, la referencia es ambigua: se discute la
    regla del protocolo de respuesta y se vuelve a etiquetar.
12. **Independencia de la referencia.** Acepta si `imagen_usada` de cada punto
    nombra una fuente que no es la evaluada (Esri, Google, Google Earth Pro con
    fecha, Wayback, Carta Internacional). Si se usó Sentinel-2 para validar la
    variante óptica, se declara.
13. **Conclusión acorde a los intervalos.** En `tabla_de_variantes_<clase>.csv` y
    en el informe, acepta si toda afirmación del tipo «la variante X es mejor»
    se apoya en el IC del 95 % de la DIFERENCIA, que no incluye el cero (no en
    que los IC de cada variante no se superpongan).

## Cifras que deben aparecer en las bitácoras

| Bitácora | Cifra |
|---|---|
| `Tp4_01_<SITIO>.log` | píxeles digitalizados, de JRC y de MapBiomas; % del sitio sin clase |
| `Tp4_02_<NOMBRE>.log` | U, S_O, n de la fórmula; tabla de diseño con `n_i`; número de puntos |
| `Tp4_03_<NOMBRE>.log` | puntos sin etiquetar; matriz en conteos y en proporción de área; exactitud global ± IC y n |
| `Tp4_04_variantes_<clase>.log` | una fila por variante y la diferencia con su IC frente a la mejor |
| `Tp4_07_<NOMBRE>.log` | acuerdo simple con Wilson y kappa de Cohen |

## Tabla para anotar los valores del grupo

| Control | Mapa evaluado | Valor obtenido | ¿Acepta? | Observación |
|---|---|---|---|---|
| 1 Autoprueba | ejemplo publicado | | | |
| 5 Mínimo por clase | | | | |
| 6 Prioridad de fuentes | | | | |
| 7 Agua permanente | | | | |
| 8 Área total | | | | |
| 9 Sin etiquetar (%) | | | | |
| 10 Clases ajenas (%) | | | | |
| 11 Acuerdo entre intérpretes (de 10) | | | | |
| 12 Independencia | | | | |
| 13 Conclusión | | | | |

## Tabla completada en el Desarrollo del Tp4 (ensayo y MapBiomas 2025)

| Control | Mapa evaluado | Valor obtenido | ¿Acepta? | Observación |
|---|---|---|---|---|
| 1 Autoprueba | ejemplo publicado | 21.158 ± 6.158 ha; usuario 0,88; productor 0,75; global 0,95 | Sí | El conteo ingenuo da 0,917 y 18.000 ha |
| 5 Mínimo por clase | control y MapBiomas | 10 puntos por estrato (n = 70) | Sí | Suma de n_i = 70 |
| 6 Prioridad de fuentes | control | agua: 330 + 422.526 = 422.856 píxeles | Sí | |
| 7 Agua permanente | control | río y embalse; bañados afuera | Sí | |
| 8 Área total | control y MapBiomas | 18.504,6 ha y 117.656,5 ha | Sí | |
| 9 Sin etiquetar (%) | control y MapBiomas | 0 % | Sí | |
| 10 Clases ajenas (%) | MapBiomas | 1 de 70 (túneles) | Sí | No se excluye |
| 11 Acuerdo entre intérpretes | control y MapBiomas | control 32 de 58 (0,55; kappa 0,47); MapBiomas 21 de 37 (0,57; kappa 0,44) | No | Tp4_07; el segundo intérprete usó CBERS-4A de 2 m y Sentinel-2, no Esri ni Google |
| 12 Independencia | control | Esri, Google, Pléiades | Sí (parcial) | Comparte fuente con la digitalización |
| 13 Conclusión | con y sin recorte | d = +0,127 ± 0,117 | Sí | Por la diferencia |
