# Lea esto primero

**Sinergias multisensor y estrategias de fusión SAR-Óptico-LiDAR para evaluación
de emergencias ambientales. Curso de posgrado, Diamante (Entre Ríos), 2026.**

Héctor Francisco del Valle · CeReGeo (FCyT, UADER)

**Desarrollo con inteligencia artificial.** Este curso fue desarrollado en su mayor parte con la inteligencia artificial Claude (Anthropic) y con aportes de ChatGPT (OpenAI) y Copilot (Microsoft), en sus versiones Premium. La idea, la supervisión y la revisión de todo el material son del docente responsable, Héctor Francisco del Valle.

---

## Qué es esta carpeta

`02_Practica` es **todo lo que se ejecuta** en el curso: los diez trabajos
prácticos, la carpeta común que comparten y la guía teórico-práctica. Cada
práctico es una carpeta con la misma estructura, de modo que lo que se aprende a
recorrer en el Tp1 sirve para todos los demás.

El curso es **todo práctica**: cinco días, de 9 a 13 y de 14 a 18 h (40 horas).
La teoría necesaria para cada paso está en la guía teórico-práctica y en la
presentación de introducción; en el aula se trabaja con los datos.

## Ningún Word llega al estudiante

El estudiante recibe **PDF y `.md`**, nada más. La guía teórico-práctica se
entrega en PDF (`00_Guia_teorica_practica`). Los informes se entregan en PDF.

## El cronograma

| Día | 9 a 13 h | 14 a 18 h |
|---|---|---|
| Lunes | **Tp1** Convergencia: qué datos existen para cada sitio y fecha | **Tp2** SAR multibanda: X, C, S, L y P frente a cada cubierta |
| Martes | **Tp3** Armonización (9 a 12) · **Tp4** Validación (12 a 13) | **Tp4** Validación: mapa de control y diseño de muestreo |
| Miércoles | **Tp5** Incendios en las islas del Delta (2020) | **Tp6** Inundaciones del río Uruguay en Concordia (2023) |
| Jueves | **Tp7** Barrancas y deslizamientos en Diamante | **Tp8** Erosión de suelos y cárcavas en Bovril |
| Viernes | **Tp9** Deforestación y degradación del monte (9 a 12) · **Tp10** Impacto urbano (12 a 13) | **Tp10** (14 a 16) · Consultas sobre el trabajo final del curso (16 a 18) |

Los prácticos son diez (Tp1 a Tp10). El trabajo final integrador del curso es un informe grupal sobre un sitio y una emergencia de los Tp5 a Tp10; se entrega por escrito después del curso y se aprueba con tres criterios: cada afirmación trazada hasta un resultado y su dominio; amenaza, exposición y vulnerabilidad separadas; y un proyecto reproducible con estados de evidencia claros (capítulo 14 de la guía teórico-práctica).

## La diferencia que recorre todo el curso: sinergia y fusión

- **Sinergia:** cada sensor produce **su** resultado (un mapa, una curva, una
  tabla) y el analista los interpreta juntos. Ocurre en el razonamiento. Se
  valida por coherencia física entre sensores. En los prácticos: tablas de
  coincidencia, curvas de respuesta por banda.
- **Fusión:** un algoritmo combina los datos en **un único producto**. Puede ser
  a nivel de **píxel** (los valores de cada sensor entran juntos a un
  clasificador), de **rasgo** (entran variables derivadas: ΔVH, ΔNDVI, Δrh98) o
  de **decisión** (cada sensor decide por su lado y una regla escrita combina).
  Exige misma grilla, corregistro menor que un píxel y fechas compatibles. Se
  valida con la exactitud del producto (Tp4).

Toda fusión bien diseñada busca sinergia; no toda sinergia requiere fusión. Cada
práctico marca qué paso es sinergia y qué paso es fusión, y de qué nivel.

## Antes del primer día: el entorno de Miniforge

Una sola vez por computadora, en el **Miniforge Prompt**:

```
cd /d <ruta>\02_Practica\00_COMUN
conda env create -f entorno_sar.yml
conda activate sar
python comprobar_entorno.py
```

`comprobar_entorno.py` revisa las bibliotecas, que GDAL lea JPEG 2000 y HDF5, el
geoide EGM2008 de PROJ, las carpetas de datos y la credencial de NASA Earthdata
(sin leerla). Si la grilla del geoide falta:

```
projsync --file us_nga_egm08_25.tif
```

Cada vez que se abre una sesión de trabajo:

```
conda activate sar
cd /d <ruta>\02_Practica\TpN_<nombre>\03_Scripts
```

Además hacen falta **SNAP** (ESA, versión 10 o posterior) y **QGIS** (3.34 LTR o
posterior). La cuenta gratuita de **NASA Earthdata** sirve para ASF, GEDI e
ICESat-2. Las credenciales nunca se escriben en un programa: se guardan en el
archivo `.netrc` del usuario o se escriben cuando el programa las pide.

## La estructura de cada práctico

```
TpN_<nombre>\
    00_LEEME.md                el recorrido del práctico: empiece por acá
    NOTAS_TECNICAS.md          las decisiones técnicas y su fundamento
    00_Guia_del_practico\      objetivos y la guía paso a paso
    01_Prompt_IA\              el prompt inicial, el análisis de la respuesta,
                               el prompt corregido (súper detallado) y la verificación
    02_Subsets_SNAP_QGIS\      recortes y pilas en la grilla común
    03_Scripts\                los programas y 00_ORDEN_DE_EJECUCION.md
    04_Tablas_de_trabajo\      lo que digitaliza el grupo (entrenamiento, control)
    05_Resultados\             rásters, tablas, gráficos y bitácoras
    06_Bibliografia\           las referencias del práctico
    07_Preguntas_y_entrega\    las preguntas, la rúbrica y la entrega del grupo
    08_Orange\                 los flujos de Orange (.ows) y sus datos
    09_Grafos_SNAP\            (cuando corresponde) los grafos o cadenas de SNAP
```

## Las marcas de cada paso

| Marca | Qué significa |
|---|---|
| **SE CORRE** | Lo corre el estudiante en clase. |
| **YA VIENE HECHO** | Descarga o proceso largo que hizo el docente antes del curso. El programa queda para ver cómo se hace y repetirlo en otro sitio. |
| **AUXILIAR** | No es un paso de la cadena: sirve para diagnosticar o inspeccionar. |
| **EN SNAP** | Se hace con la interfaz de SNAP (los menús se indican en la guía). |
| **EN QGIS** | Se hace en QGIS (digitalizar, etiquetar, mirar). |

## Los sitios

El mapa de los sitios es el de la presentación de introducción («Sitios de
convergencia en Entre Ríos»); está en `00_COMUN/01_AOI/mapa_sitios_convergencia.png`
y en el capítulo 1 de la guía.

| Sitio | Lugar | Prácticos |
|---|---|---|
| A1_DELTA_QUEMAS | Islas del Delta frente a Victoria y Rosario | Tp5 |
| A2_IBICUY | Delta inferior, Ibicuy (aproximado) | Tp2, Tp3 |
| B_CONCORDIA | Río Uruguay y ciudad de Concordia | Tp1, Tp6, Tp10 |
| C_FEDERAL | Monte nativo del Espinal, Federal | Tp9 |
| D_LAPAZ_VILLAGUAY | Franja La Paz – Villaguay (aproximada; BIOMASS) | Tp9 |
| E_PARANA_DIAMANTE | Paraná y Diamante (aproximado) | Tp10 |
| E1_DIAMANTE_BARRANCA | Barranca del río Paraná en Diamante | Tp7 |
| F_BOVRIL | Centro de Entre Ríos, Bovril | Tp8 |
| DELTA_NISAR | Recorte de los NISAR GCOV del Delta | Tp2, Tp3 |

Las coordenadas están en un solo lugar: `00_COMUN/configuracion_comun.py`. La
grilla común de todo el curso es **EPSG:32721 (UTM 21S)**, con píxel de 10 m por
defecto (20 m donde el práctico lo justifica).

## Los datos

Los originales se reúnen en una sola carpeta de **datos crudos**,
`00_COMUN/08_Originales_crudos`, que llena el docente antes del curso con
`00_COMUN/datos_crudos.py` (ver el `LEEME.md` de esa carpeta). Allí van las
copias de las escenas propias que cubren cada sitio, el LiDAR de ICESat-2
(ATL08 y ATL13) y de GEDI (L2A y L4A), BIOMASS en banda P, los recortes del
ESA CCI Biomass (ya bajados: nueve sitios, cinco años) y, si hace falta trabajar sin red, los del Planetary Computer.
Si un disco original no está conectado, los programas usan la copia local.
Los NISAR GCOV del Delta se bajan de ASF a `NISAR_DELTA` con `datos_crudos.py nisar`.
Las rutas se definen en `configuracion_comun.py` y se pueden cambiar con
variables de entorno (`CURSO_SAR_NISAR_DELTA`, `CURSO_SAR_NOVASAR`,
`CURSO_SAR_2023`, `CURSO_SAR_COSMO`, `CURSO_SAR_ORIGINALES`).

| Fuente | Qué hay | Cómo se obtiene |
|---|---|---|
| Microsoft Planetary Computer | Sentinel-2 L2A, Sentinel-1 RTC, mosaicos ALOS-2, Copernicus DEM, JRC Global Surface Water | Sin cuenta, por STAC |
| ASF DAAC | NISAR GCOV, Sentinel-1 SLC, ALOS-1 PALSAR, interferogramas HyP3 | Cuenta NASA Earthdata |
| LP DAAC y NSIDC | GEDI L2A V003, ICESat-2 ATL08 v007 | Cuenta NASA Earthdata |
| ESA MAAP | BIOMASS (banda P), franja D | Cuenta ESA |
| CEDA (ESA CCI) | Biomasa aérea ESA CCI Biomass v7.0, 100 m, 2005–2024 | Sin cuenta |
| CSIRO (archivo del curso) | Cinco escenas NovaSAR-1 (banda S, 6 m) de 2023 | Disco del curso |
| Archivo del curso 2023 | Sentinel-1 SLC, SAOCOM-1A, ALOS-2, COSMO-SkyMed de Diamante, MDE del IGN | Disco del curso |
| ASF DAAC (NISAR) | NISAR GCOV banda L (NASA) del Delta, julio a octubre de 2026; banda S (ISRO) si existe | `datos_crudos.py nisar`, cuenta NASA Earthdata |

## Lo que conviene saber desde el principio

- El radar se trabaja en **γ⁰ lineal**; los dB sirven para mirar y para poner
  umbrales. Los promedios se hacen en lineal.
- Cada programa escribe una **bitácora** (`05_Resultados/06_Control_calidad`)
  con lo que hizo, cuántos datos entraron y salieron, y el paso siguiente.
- Cada ráster lleva en sus metadatos la **fuente** de cada dato y el proceso.
  Toda figura lleva la cita de la fuente al pie.
- Una cifra del informe que no se puede rastrear hasta un archivo de
  `05_Resultados` no es una cifra: es una opinión.

## Los documentos de 00_COMUN

| Archivo | Para qué |
|---|---|
| `entorno_sar.yml` | El entorno de Miniforge |
| `comprobar_entorno.py` | La verificación del entorno |
| `datos_crudos.py` | Reúne los datos crudos en `08_Originales_crudos` (lo corre el docente) |
| `08_Originales_crudos/` | Los datos crudos, con un `LEEME.md` por carpeta: el del CCI Biomass resume qué esperar en cada sitio; el de `LIDAR` reúne lo que dieron ICESat-2 y GEDI en cada sitio (disparos, válidos, fechas) y las decisiones al usarlos |
| `configuracion_comun.py` | Sitios, eventos, grilla y rutas: lo único que se toca para cambiar de área |
| `funciones_comunes.py`, `funciones_cambio.py`, `funciones_lidar.py` | Las funciones que usan todos los prácticos |
| `REGLAS_DEL_PROYECTO.md` | Las reglas que siguen todos los programas |
| `GLOSARIO.md` | Los términos del curso |
| `COMO_CAMBIAR_DE_AREA.md` | Cómo repetir un práctico en otro sitio |
