# Tp5 · Incendios: perímetro y severidad

**Pregunta del práctico:** ¿dónde se quemó y con qué severidad, aun bajo humo?

## Sitio y evento

A1 · Delta del Paraná, islas frente a Victoria (`A1_DELTA_QUEMAS`, bbox −59,96, −33,36, −59,72, −33,07). Quemas de 2020 (desde febrero; el pico fue en julio): el práctico mide lo quemado entre mediados de julio y octubre, en pajonales y bosques de albardón de las islas, durante la bajante extraordinaria del Paraná.

## Horario

Miércoles de 9 a 13 h. El etiquetado de las variantes (Tp4) se reparte entre grupos y puede seguir el jueves.

## Los sensores, cada uno con su pregunta

| Sensor | Banda / tipo | Qué responde | Fechas |
|---|---|---|---|
| Sentinel-1 RTC (Planetary Computer) | C, VV y VH, γ⁰ | caída de VH: pérdida de volumen herbáceo (pajonal) | 16/07/2020 y 26/09/2020 por defecto |
| ALOS-2 PALSAR-2, mosaicos anuales JAXA | L, HH y HV, 25 m | caída de HV: pérdida de volumen leñoso (albardón) | 2019 (antes) y 2020 (después) |
| SAOCOM-1A StripMap QP (archivo del curso) | L, HV, γ⁰ | lo mismo que ALOS-2, con fecha precisa | 21/07/2020 y 25/10/2020 |
| Sentinel-2 L2A (Planetary Computer) | óptico | dNBR y RdNBR: severidad | antes: la que elija en el Tp1; después: 13/10/2020 |
| GEDI L2A V003 | LiDAR | Δrh98: cambio de altura, evidencia estructural independiente | antes del 01/07/2020 y después del 01/11/2020 |

## Carpetas

| Carpeta | Qué hay |
|---|---|
| `00_Guia_del_practico/` | **Empiece por acá.** `objetivos.md` y la guía paso a paso `00_LEEME.md` |
| `01_Prompt_IA/` | Prompt ingenuo, análisis, prompt corregido y verificación |
| `02_Subsets_SNAP_QGIS/` | Los indicadores por sensor en la grilla común: `A1_DELTA_QUEMAS_indicadores_<pixel>m.tif` y su tabla de fuentes |
| `03_Scripts/` | Los cuatro scripts y `00_ORDEN_DE_EJECUCION.md` |
| `04_Tablas_de_trabajo/` | El entrenamiento que digitaliza el grupo: `entrenamiento_A1.gpkg` |
| `05_Resultados/` | Mapas de quema por sensor, variantes, severidad, tablas, histogramas y bitácoras |
| `06_Bibliografia/` | Referencias del práctico |
| `07_Preguntas_y_entrega/` | Preguntas, rúbrica y entrega |
| `09_Grafos_SNAP/` | Cómo se procesó SAOCOM en SNAP (los grafos están en `02_Subsets_SNAP_QGIS\SAOCOM_gamma0\Grafos_SNAP`) |

## Los scripts

| Paso | Script | Marca | Qué hace | Sinergia o fusión |
|---|---|---|---|---|
| 1 | `Tp5_01_indicadores.py` | **SE CORRE** | ΔVH y ΔVV (C), ΔHV y ΔHH (L, ALOS-2), ΔHV (SAOCOM), NBR, dNBR, RdNBR | ninguna: un indicador por sensor |
| 2 | `Tp5_02_sinergia.py` | **SE CORRE** | Un mapa de quema por sensor, con su umbral; tabla de coincidencias general (y por clase de control si la hay; en A1, por estrato del CCI en QGIS u Orange) | **SINERGIA** |
| 3 | `Tp5_03_fusion.py` | **SE CORRE** + **EN QGIS** | V1 óptico, V2 C, V3 fusión de decisión C + L, V4 fusión de rasgos con Random Forest (severidad) | **FUSIÓN de decisión** (V3) y **de rasgo** (V4) |
| 5 | `Tp4_02`, `Tp4_03`, `Tp4_04` | **SE CORRE** + **EN QGIS** | Validación de las cuatro variantes, de la severidad y tabla de variantes | validación de la fusión |
| 5 | `Tp5_05_dominio_comun.py` | **SE CORRE** | Las cuatro variantes en la superficie común | validación |
| 6 | `Tp5_04_gedi_cambio_de_altura.py` | **SE CORRE** | Δrh98 de GEDI por celda de 100 m, cruzado con la variante multisensor | **SINERGIA** (evidencia independiente) |
| previo | `00_COMUN\procesar_saocom.py` (grafo de SNAP) | **YA VIENE HECHO** | SAOCOM a γ⁰ = σ⁰/cos θ sobre el elipsoide (sin Terrain-Flattening), GeoTIFF de una banda y RGB copolarizada–cruzada–cociente | — |

## Qué es sinergia y qué es fusión en este práctico

- **SINERGIA (paso 2).** Cada sensor decide «quemado / no quemado» con su propio umbral. No se produce un mapa único. El analista compara: ¿dónde coinciden C, L y óptico?, ¿cómo responde cada banda en el pajonal y en el albardón? Se evalúa la **coherencia física** con las medianas por estrato de estructura (CCI Biomass 2020): la física predice que la C cae más en el pajonal y la L acompaña en el albardón. Con los datos de 2020 eso se cumple en el albardón y no en el pajonal, y la discrepancia se explica (fecha «después» mojada, suelo húmedo bajo la paja quemada, mosaico anual de ALOS-2).
- **SINERGIA (paso 6).** El cambio de altura de GEDI no entra en ningún modelo: se usa para interpretar si el mapa y la estructura cuentan la misma historia.
- **FUSIÓN DE DECISIÓN (V3).** Los mapas binarios de C y L se combinan con una regla escrita (`mayoria`, `union` o `interseccion`). Tolera que C (20 m, fecha precisa) y el mosaico ALOS-2 (25 m, anual) no coincidan en píxel ni en fecha.
- **FUSIÓN DE RASGO (V4).** ΔVH, ΔVV, ΔHV, dNBR y RdNBR entran a un Random Forest que asigna severidad. Requiere misma grilla (la hay: todo está en la grilla de 20 m) y fechas compatibles (se declara la del mosaico ALOS-2).
- Las fusiones se validan con la exactitud del producto (Tp4).

## Qué se entrega

Perímetro con la exactitud de cada variante (la tabla de variantes del Tp4 valida quemado / no quemado) y el mapa de severidad V4 con su figura y su propia validación de cuatro clases, o con la leyenda «severidad no validada» si no se hizo esa muestra; la tabla de coincidencias de la sinergia, la tabla de Δrh98 y las respuestas a las preguntas.

## Qué tiene que estar listo antes

- **Tp4_01** corrido para `A1_DELTA_QUEMAS` a 20 m (`Tp4_Validacion\02_Subsets_SNAP_QGIS\A1_DELTA_QUEMAS_cobertura_control_20m.tif`). Sin él, la sinergia no se separa por cubierta y las lagunas no se enmascaran.
- **YA VIENE HECHO:** las huellas GEDI del sitio, descargadas con `Tp1_05_buscar_lidar.py --sitio A1_DELTA_QUEMAS --descargar` (los gránulos pesan entre 0,2 y 3 GB cada uno). Quedan en `Tp1_Convergencia\05_Resultados\03_Vectores\lidar_A1_DELTA_QUEMAS.gpkg`, capa `gedi_l2a`.
- **YA VIENE HECHO:** los γ⁰ de SAOCOM del 21/07, del 07/09 y del 25/10/2020, procesados en SNAP con `00_COMUN\procesar_saocom.py`, en `02_Subsets_SNAP_QGIS\SAOCOM_gamma0` (`.dim`, GeoTIFF de una banda y RGB copolarizada–cruzada–cociente).
- **La fecha óptica previa**, elegida con `Tp1_03_buscar_optico_y_C.py --sitio A1_DELTA_QUEMAS --desde 2020-06-15 --hasta 2020-10-31`.
- Conexión a internet: Sentinel-1, Sentinel-2 y ALOS-2 se leen del Planetary Computer en el momento.

## Lo que se dice desde el principio

- Las lecturas del Planetary Computer **no pudieron probarse** desde el entorno de desarrollo (sin red hacia ese servicio). El código está probado con datos sintéticos. Hay que correr `Tp5_01` una vez antes del curso.
- El mosaico anual ALOS-2 de 2020 combina pasadas de varios meses: en parte del sitio puede ser **anterior** a las quemas. La fecha de cada píxel está en la banda `date` del mosaico, que el script no lee. Se declara al interpretar.
- La variante «multisensor» del Tp5 es SAR (C + L) + óptico. **El LiDAR no entra en el modelo**: GEDI se usa como evidencia independiente en el paso 6.
