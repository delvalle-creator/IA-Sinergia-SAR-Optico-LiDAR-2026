# Verificación de los resultados del Tp5

Cada control tiene su criterio de aceptación. Si uno no se cumple, se corrige o se declara antes de seguir.

## A. Controles sobre los scripts

1. **Unidades.** En `Tp5_01`, el cambio de radar se calcula con `cociente_db` sobre γ⁰ lineal. Acepta si en el código no hay ninguna resta de dB ni promedio en dB, y si los metadatos del GeoTIFF dicen «radar: 10 log10(post/pre) en dB».
2. **Órbita única.** Acepta si la cita de `dVH_C_dB` en `A1_DELTA_QUEMAS_indicadores_fuentes.csv` nombra la misma órbita relativa para pre y post.
3. **Agua enmascarada.** En `A1_sinergia_coincidencias.csv`, acepta si en la región `control: agua_permanente` el `%_clase` de todos los sensores es 0.
4. **Sinergia sin fusión.** Acepta si `A1_quema_por_sensor_20m.tif` tiene una banda por sensor y ningún mapa combinado.
5. **Códigos de las variantes.** Acepta si las cuatro variantes tienen en la banda `clase` sólo 1, 2 y sin dato.
6. **Entrenamiento separado de la validación.** Acepta si menos del 5 % de los puntos de `Tp4_02` de cada variante cae dentro de un polígono de `entrenamiento_A1.gpkg` (se comprueba en QGIS con `Vectorial > Herramientas de investigación > Seleccionar por localización`).

## B. Controles sobre los resultados

7. **Cambio general en lo no quemado.** La mediana de ΔVH en lo no quemado se informa y se explica (en 2020 fue de unos +3,7 dB: la fecha «después» del 26/09 es una pasada con todo el sitio mojado). Acepta si la cifra está y si la explicación separa la humedad de la fecha de la del fuego. Se mide en QGIS con la caja de herramientas de Procesos (`Procesos > Caja de herramientas`), `Análisis ráster > Estadísticas de zona` (Zonal Statistics), sobre polígonos de control o en Python sobre el GeoTIFF.
8. **Umbral justificado.** Acepta si cada histograma `histograma_<indicador>.png` muestra la línea del umbral en el valle entre dos modas, o si el umbral fue fijado a mano con una justificación escrita.
9. **Coherencia física de la sinergia, por estrato del CCI.** Con las medianas por estrato (pajonal < 15 Mg/ha, albardón ≥ 30 Mg/ha), acepta si se informa cuánto cae cada banda en lo quemado frente a lo no quemado en cada estrato y si se evalúa la predicción física (en pajonal la C cae más que la L; en albardón la L acompaña). Si no se cumple, no es un error del script: es un resultado que hay que explicar (fechas, humedad, mosaico anual).
10. **Exactitud fuera de bolsa no informada como exactitud.** Acepta si el informe sólo cita la exactitud del Tp4.
11. **Probabilidad del Random Forest.** Acepta si menos del 20 % de los píxeles clasificados tiene `probabilidad` < 0,5; si es más, el modelo duda y se dice dónde.
12. **Área estimada frente a área del mapa.** En `tabla_de_variantes_quemado.csv`, acepta si se informa el área estimada con su IC y se comenta si el área del mapa cae dentro.
13. **Comparación de variantes.** Acepta si toda frase del tipo «la multisensor es mejor» se apoya en que el IC del 95 % de la diferencia excluye el cero (bitácora de `Tp4_04` o `Tp5_05`). Que los IC de cada variante se superpongan no prueba que sean iguales.
14. **GEDI.** Acepta si la ventana «antes» y la «después» son de la misma estación y tienen fin, si se informa el número de celdas con datos antes y después y el % con rh98 previo < 3 m (piso del instrumento), y si la conclusión estructural se limita a las celdas leñosas.
15. **Acuerdo entre intérpretes.** Cada grupo revisa 30 puntos al azar del etiquetado de otro grupo en `04_Tablas_de_trabajo/revision_30_puntos_segundo_interprete.csv`, sin ver la etiqueta original. Acepta si el acuerdo es del 80 % o más; si es menor, se revisan juntos los desacuerdos y se declara. Con Landsat 8 como segundo intérprete, el etiquetado del Desarrollo coincidió en el 81 %.

## Cifras que deben aparecer en las bitácoras

| Bitácora | Cifra |
|---|---|
| `Tp5_01_indicadores.log` | tamaño de la grilla; mediana de ΔVH, ΔVV, ΔHV; nubosidad óptica en el sitio; % con dNBR > 0,27 |
| `Tp5_02_sinergia.log` | umbral, método y % en clase de cada sensor; tabla de acuerdo |
| `Tp5_03_fusion.log` | regla de V3 y sensores que votaron; píxeles de entrenamiento; exactitud fuera de bolsa (optimista); importancia; ha por clase de severidad |
| `Tp4_03_A1_variante_*.log` | exactitud global ± IC; usuario y productor de quemado; área estimada ± IC |
| `Tp4_04_variantes_quemado.log` | frase de superposición de IC por par |
| `Tp5_04_gedi.log` | huellas antes, durante y después; celdas; Δrh98 por clase; % con rh98 < 3 m |

## Tabla para anotar los valores del grupo

| Control | Valor obtenido | ¿Acepta? | Observación |
|---|---|---|---|
| 3 Agua enmascarada (%) | | | |
| 6 Puntos en entrenamiento (%) | | | |
| 7 Mediana ΔVH en lo no quemado (dB) y explicación | | | |
| 8 Umbral ΔVH / ΔHV / dNBR | | | |
| 9 Pajonal: caída de C y de L (dB) | | | |
| 9 Albardón: caída de C y de L (dB) | | | |
| 11 Píxeles con probabilidad < 0,5 (%) | | | |
| 12 Área quemada estimada ± IC (ha) | | | |
| 13 IC de la diferencia multisensor − óptico | | | |
| 15 Acuerdo con el otro grupo (%) | | | |
| 14 Celdas GEDI / % rh98 < 3 m | | | |
