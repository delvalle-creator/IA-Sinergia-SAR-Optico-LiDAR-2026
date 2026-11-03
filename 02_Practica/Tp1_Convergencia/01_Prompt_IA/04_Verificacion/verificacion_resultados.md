# Verificación del Tp1 — protocolo

Dos partes: primero se verifica **lo que la IA entregó** (los scripts), después se
verifican **los resultados** que los scripts produjeron sobre `B_CONCORDIA`. Cada
control tiene su criterio de aceptación. Un control que no se cumple no se oculta: se
anota, se explica y se declara en la entrega.

## A. Controles sobre los scripts

| N.º | Qué se controla | Cómo | Se acepta si… |
|---|---|---|---|
| A1 | No hay credenciales en el código | Buscar en los `.py` las palabras `password`, `clave`, `token` | Sólo aparecen como lectura de variables de entorno, `.netrc` o `getpass` |
| A2 | La nubosidad se cuenta en el sitio | Leer `s2_mascara_valida()` en `00_COMUN/funciones_comunes.py` | Usa la SCL leída en la grilla del sitio, no `eo:cloud_cover` |
| A3 | Huella y dato están separados | Abrir `inventario_local.csv` | Existen las dos columnas `cobertura_huella_%` y `pixeles_validos_%` |
| A4 | Lo que no se midió queda vacío | Abrir `planilla_ASF_B_CONCORDIA.csv` | `pixeles_validos_%` vacía en todas las filas |
| A5 | NISAR usa la máscara del producto | Leer `nisar_gcov_en_grilla()` | Pone sin dato los valores de máscara 0 y 255 |
| A6 | Fechas de metadatos | Leer `fecha_item()`, `metadato_novasar()`, `info_nisar()` | Ninguna fecha sale de `os.path.getmtime` ni de la fecha del archivo |
| A7 | GEDI v003 con su campo de calidad | Leer `leer_gedi_l2a()` | Usa `l2a_quality_flag_rel3` si existe, e informa cuál usó |

## B. Controles sobre los resultados

1. **Bitácoras completas.** En `05_Resultados/06_Control_calidad/` hay un `.log` por
   script corrido (`Tp1_01_sitios`, `Tp1_02_inventario_local`, `Tp1_03_B_CONCORDIA`,
   `Tp1_04_B_CONCORDIA`, `Tp1_05_B_CONCORDIA`, `Tp1_06_B_CONCORDIA`,
   `Tp1_07_B_CONCORDIA`). *Se acepta si* cada uno termina con `SIGUIENTE PASO:`.
2. **Sitio correcto.** En QGIS, `sitios_curso.gpkg` sobre la imagen. *Se acepta si*
   `B_CONCORDIA` contiene Concordia, la represa de Salto Grande y el cauce del Uruguay.
3. **Huella frente a dato, NovaSAR.** En `inventario_local.csv`, escena 47942 sobre
   `B_CONCORDIA`. *Se acepta si* `pixeles_validos_%` ronda el 39 % (valor medido con
   este script sobre los GRD) y es menor que `cobertura_huella_%`.
4. **Escena que no corresponde.** *Se acepta si* la escena 50896 no figura sobre
   `B_CONCORDIA` con píxeles válidos, aunque tenga la misma hora de pasada (01:36 UTC)
   que la 47942.
5. **Nubosidad.** En `planilla_MPC_B_CONCORDIA.csv`, compare `nubosidad_catalogo_%`
   con `nubosidad_sitio_%`. *Se acepta si* el grupo identifica al menos una escena
   donde las dos difieren en más de 20 puntos, o declara que no la hay en la ventana.
6. **Ausencias esperadas.** *Se acepta si* la planilla de ASF no tiene NISAR ni ALOS
   en octubre-noviembre de 2023 y la bitácora de LiDAR muestra el AVISO del receso de
   GEDI con cero granulos GEDI en la ventana del evento.
7. **LiDAR coherente.** En `lidar_conteo_B_CONCORDIA.csv` (si hubo granulos que
   contar). *Se acepta si* `validas ≤ huellas_en_sitio`, la columna `descartes` da
   los motivos con su cantidad y las huellas sobre agua figuran descartadas en
   `lidar_B_CONCORDIA.gpkg` (ATL08: motivo de la máscara de agua; GEDI: motivo
   `agua`, persistencia de agua de Landsat ≥ 50 %).
8. **Planilla manual completa.** *Se acepta si* la bitácora de `Tp1_06` dice
   `0 incompletas` y hay al menos una fila con `resultado` distinto de `obtenida`.
9. **Grado justificado.** *Se acepta si* el grado de `grado_convergencia_B_CONCORDIA.csv`
   es coherente con las ausencias del punto 6 (no puede ser «completa») y el grupo
   escribe en una frase qué habilita.
10. **Figura con fuente.** *Se acepta si* `linea_tiempo_B_CONCORDIA.png` muestra el
    evento y lleva la línea «Fuente: …» al pie.
11. **Control cruzado.** Otro grupo repite los pasos 3 y 4 con la misma ventana.
    *Se acepta si* los identificadores de las escenas `candidata` coinciden, o si
    cada diferencia tiene una causa escrita (otra ventana, otro `--nubes_max`, una
    lectura que falló).

## Cifras que deben aparecer en las bitácoras

- `Tp1_02`: `huella ... %` y `pixeles con dato ... %` por escena y sitio; el número
  de combinaciones «engañosas» (huella ≥ 50 %, dato < 10 %).
- `Tp1_03`: escenas devueltas por el catálogo, y por escena nubosidad de catálogo, del
  sitio y fracción útil; el número de pares a ≤ 3 días.
- `Tp1_04`: productos que tocan el sitio, por sensor.
- `Tp1_05`: granulos por producto; huellas en el sitio, válidas y descartes por motivo.
- `Tp1_06`: productos BIOMASS por colección; filas cargadas e incompletas.
- `Tp1_07`: escenas verificadas reunidas; fechas por banda; escenas a ±12 días;
  `GRADO:`.

## Tabla para el grupo

Complete con sus valores. Cada cifra con el archivo de donde sale.

| Control | Valor obtenido | Archivo | ¿Cumple? | Observación |
|---|---|---|---|---|
| 3. NovaSAR 47942: huella / dato (%) | | | | |
| 4. NovaSAR 50896 sobre Concordia | | | | |
| 5. Escena con mayor diferencia de nubosidad (catálogo / sitio) | | | | |
| 5. Sentinel-2 candidatas / devueltas | | | | |
| 5. Sentinel-1 RTC candidatas / devueltas | | | | |
| 6. NISAR y ALOS en la ventana | | | | |
| 6. Granulos GEDI en la ventana | | | | |
| 7. Huellas GEDI en el sitio / válidas (período completo) | | | | |
| 7. Segmentos ATL08 en el sitio / con canopia válida | | | | |
| 8. Filas de la planilla manual / incompletas | | | | |
| 9. Grado de convergencia | | | | |
| 11. Escenas coincidentes con el otro grupo | | | | |
| A6. Fechas de metadatos | | | | |

## Ejemplos resueltos (Desarrollo del Tp1)

- **A6, fechas de metadatos.** `fecha_item()` (00_COMUN/funciones_comunes.py) toma
  `item.datetime` del ítem STAC; `metadato_novasar()` lee `RawDataStartTime` del
  `metadata.xml`; `info_nisar()` lee `zeroDopplerStartTime` del HDF5. Ningún script del
  Tp1 usa `os.path.getmtime`. Fila: «A6 | fecha_item, metadato_novasar, info_nisar |
  Sí | ninguna fecha sale del archivo».
- **11, una discrepancia esperable.** Si el grupo vecino corre el paso 3 con
  `--nubes_max 20`, las teselas del 09/11 (21JUF 17,5 %, 21JVF 22,1 %), del 24/11
  (21JUF 21,8 %) y del 25/10 (21,2 y 20,3 %) no se verifican. Fila: «11 | 22/24 id
  Sentinel-2; mosaicos 6/8 | planilla_MPC de los dos grupos | No | el grupo vecino usó
  --nubes_max 20». Una URL firmada vencida se ve como «(no se pudo leer la ventana:
  …)» con la fracción útil vacía en una sola de las dos planillas.
