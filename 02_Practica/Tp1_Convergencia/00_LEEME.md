# Tp1 — Verificación de convergencia multisensor

**Pregunta:** ¿qué sensores observan el mismo sitio en fechas compatibles con el evento?

**Sitio de práctica:** B · Concordia – Salto Grande (`B_CONCORDIA`, río Uruguay).
Bbox WGS 84 (oeste, sur, este, norte): −58,25, −31,50, −57,85, −31,10.
Fecha de análisis: 04/11/2023, el día con el par óptico–radar más cercano
(Sentinel-1A y Sentinel-2B con cuatro horas y media de diferencia), la fecha que
`configuracion_comun.py` registra como verificada. No es el pico de la crecida: la
serie de banda C del Tp6 da 2.912 ha de agua el 04/11 y un máximo cartografiado de
3.869 ha el 28/11/2023.

**Horario:** lunes, 9 a 13 h. Es el primer práctico y el que decide todos los demás.

## Para qué sirve este práctico

Un catálogo responde «qué escenas **tocan** el rectángulo». El Tp1 responde otra
cosa: qué escenas **cubren** el sitio con dato real, en qué fecha (la de los
metadatos, en UTC), con qué banda y polarización, y si están lo bastante cerca del
evento como para combinarlas. La respuesta es la **matriz de convergencia** y su
**grado**: completa, parcial, un solo sensor cerca del evento o histórica
(presentación 01, diapositiva 18). Ese
grado dice, antes de procesar nada, si más adelante se podrá fusionar o sólo
interpretar en sinergia.

## Qué hay en cada carpeta

| Carpeta | Qué hay |
|---|---|
| `00_Guia_del_practico/` | **Empiece por acá:** `00_LEEME.md` (la guía paso a paso, con órdenes, menús y controles) y `objetivos.md` |
| `01_Prompt_IA/` | El prompt ingenuo y sus defectos, el análisis de la respuesta, el prompt corregido que produjo los scripts y el protocolo de verificación |
| `02_Subsets_SNAP_QGIS/` | Vacía a propósito: el Tp1 no produce rásters. Ver su `LEEME.md` |
| `03_Scripts/` | Los nueve scripts y `00_ORDEN_DE_EJECUCION.md` |
| `04_Tablas_de_trabajo/` | La planilla que el grupo completa a mano: `escenas_por_pedido.csv` (la crea `Tp1_06`) |
| `05_Resultados/` | Tablas, vectores, la figura de la línea de tiempo y las bitácoras. Ver su `LEEME.md` |
| `06_Bibliografia/` | `referencias.md` |
| `07_Preguntas_y_entrega/` | Las preguntas, la rúbrica y **lo que entrega el grupo** |
| `NOTAS_TECNICAS.md` | Las decisiones técnicas y su fundamento, y los hallazgos con datos reales |

Los polígonos de los sitios **no** se guardan aquí: `Tp1_01` los escribe en
`00_COMUN/01_AOI/`, porque los usan los once prácticos.

## Los nueve scripts

| Paso | Script | Marca | Qué hace |
|---|---|---|---|
| 1 | `Tp1_01_sitios_a_vector.py` | **SE CORRE** | Sitios del curso a GeoPackage y GeoJSON; grilla de 10 m de cada sitio |
| — | revisión de los sitios | **EN QGIS** | Se controla sobre la imagen que los sitios «aproximados» caigan donde deben |
| 2 | `Tp1_02_inventario_local.py` | **SE CORRE** | Inventario de lo que ya está en disco (NovaSAR-1, NISAR L y S, archivo 2023, COSMO-SkyMed 2018): huella frente a píxeles con dato |
| 3 | `Tp1_03_buscar_optico_y_C.py` | **SE CORRE** | Sentinel-2 L2A y Sentinel-1 RTC en el Planetary Computer, verificados dentro del sitio; pares óptico-radar |
| 4 | `Tp1_04_buscar_asf.py` | **SE CORRE** (la búsqueda) / **YA VIENE HECHO** (la descarga) | NISAR GCOV, Sentinel-1 SLC y GRD, ALOS PALSAR RTC en ASF |
| 5 | `Tp1_05_buscar_lidar.py` | **SE CORRE** (búsqueda y conteo) / **YA VIENE HECHO** (la descarga) | GEDI L2A v003 e ICESat-2 ATL08 v007: granulos, huellas en el sitio y motivo de cada descarte |
| 6 | `Tp1_06_escenas_por_pedido.py` | **SE CORRE** | BIOMASS en ESA MAAP y la planilla manual de SAOCOM, NISAR S, NovaSAR y COSMO-SkyMed |
| 6b | `Tp1_06b_banda_L_antes_despues.py` | **SE CORRE** (sobre un insumo **YA VIENE HECHO**: la máscara de agua del 04/11/2023 del Tp6) | Banda L (SAOCOM y ALOS-2) antes y durante la crecida, frente a la banda C, con una zona independiente (agua del óptico que la C no marcó) |
| 7 | `Tp1_07_matriz_convergencia.py` | **SE CORRE** | Matriz sensor × fecha, grado de convergencia y figura de la línea de tiempo |
| — | control cruzado | **AUXILIAR** | Otro grupo repite la búsqueda y compara los identificadores de escena |
| 9 | `Tp1_08_contexto_del_sitio.py` | **SE CORRE** + **EN QGIS** y Orange | Contexto del sitio: MapBiomas (cobertura 1985–2025, pérdida de vegetación, fuego), CCI Biomass y BIOMASS banda P (HH y VH) por clase de cobertura |

El detalle de cada orden, con sus argumentos, está en `03_Scripts/00_ORDEN_DE_EJECUCION.md`.

## Sinergia y fusión en el Tp1

**En el Tp1 no hay fusión.** Ningún algoritmo combina datos en un producto.

Hay una **primera lectura de señales** (banda L y C antes y durante la crecida, paso
6b), que anticipa la sinergia del Tp6: cada banda se compara por separado contra su
propio cambio general. Lo central del Tp1 es **decidir qué será posible** después:

| Grado (paso 7) | Qué se combina | Qué habilita en los Tp5 a Tp10 |
|---|---|---|
| Completa | Óptico + SAR de 2 o más bandas + LiDAR, fechas compatibles | **Fusión** a nivel de píxel (óptico y radar) o de rasgo; el LiDAR entra como referencia o en fusión de rasgo, nunca a nivel de píxel |
| Parcial | Óptico + una banda SAR, o fechas separadas por semanas | **Sinergia**, o **fusión** a nivel de decisión |
| Parcial (sin óptico) | Dos o más bandas SAR, sin óptico en la ventana | **Sinergia** SAR multibanda; buscar el óptico antes de fusionar |
| Un solo sensor cerca del evento | Óptico solo, o una sola banda SAR, dentro de la ventana | El mapa de ese sensor; los demás datos sólo para interpretar (sin fusión) |
| Histórica | Nada dentro de la ventana (sensores de otras fechas o de años distintos) | Sólo interpretación de cambios de largo plazo |

La razón es física y metodológica: fusionar a nivel de píxel exige misma grilla,
corregistro menor que un píxel y fechas compatibles (eso se comprueba en el Tp3).
Si el Tp1 muestra que las fechas no son compatibles, la fusión de píxel queda
descartada desde el principio, por más que el algoritmo «corra».

## Qué se entrega

1. La planilla de escenas completa: `05_Resultados/04_Tablas/` (inventario local,
   Planetary Computer, ASF, LiDAR y por pedido), con fecha y hora UTC, órbita o
   pasada, modo, polarización, huella declarada y cobertura efectiva.
2. La matriz de convergencia y el grado: `matriz_convergencia_B_CONCORDIA.csv` y
   `grado_convergencia_B_CONCORDIA.csv`.
3. La figura `05_Graficos/linea_tiempo_B_CONCORDIA.png`, con la cita de fuentes al pie.
4. Las respuestas de `07_Preguntas_y_entrega/preguntas.md`, cada cifra con el archivo
   del que sale.
5. El control cruzado con otro grupo (protocolo en `01_Prompt_IA/04_Verificacion/`).
6. La bitácora de IA: el prompt, la respuesta, la corrección humana y la verificación.

## Qué tiene que estar listo antes (YA VIENE HECHO)

- El entorno `sar` de Miniforge instalado desde `00_COMUN/entorno_sar.yml` y revisado
  con `python comprobar_entorno.py`, corrido desde `00_COMUN` (debe terminar con
  `Resultado: TODO EN ORDEN`).
- Las escenas NovaSAR-1 (carpeta `E:\IMÁGENES NOVASAR-1 2023 2024\ENTRE RIOS-SANTA FE`)
  y los NISAR GCOV del Delta (`00_COMUN\08_Originales_crudos\NISAR_DELTA`, que baja el docente con
  `datos_crudos.py nisar`). Las escenas NovaSAR se leen de donde están o de su
  copia en `08_Originales_crudos\LOCALES`.
- El archivo del curso 2023 (`E:\CURSO SAR CEREGEO 2023\PRACTICAL EXERCISES`) y los
  COSMO-SkyMed de Diamante (`F:\HFdV COURSES\CEREGEO\2018\TelSAR\DIAMANTE`).
- Los granulos GEDI y ATL08 que se usen en el conteo, ya bajados en
  `<ORIGINALES>\LIDAR\<SITIO>\GEDI02_A\` y `...\ATL08\`. Bajar un granulo GEDI lleva
  entre 0,2 y 3 GB: en clase **no** se descarga.
- Una cuenta de NASA Earthdata del grupo (sólo para descargar; buscar no la pide).
  La credencial **nunca** se escribe en un script: va en el archivo `.netrc` del
  usuario o en la variable de entorno `EARTHDATA_TOKEN`.

Si alguna de esas carpetas está en otra unidad, se indica con las variables de
entorno `CURSO_SAR_NOVASAR`, `CURSO_SAR_NISAR_DELTA`, `CURSO_SAR_2023`,
`CURSO_SAR_COSMO` y `CURSO_SAR_ORIGINALES` (ver la guía, paso 0).

## Una advertencia honesta

Si en clase un servicio no responde, el script lo deja escrito en la bitácora y
sigue; los resultados de referencia están en el Desarrollo. **Una ausencia
documentada es información; una ausencia silenciosa es un hueco.**

## Núcleo y ampliación

El núcleo que se hace el lunes y se evalúa son los pasos 0 a 8 (con el 6b, que lee la
máscara de agua del Tp6 ya hecha) y la bitácora de IA; el paso 9 (contexto del sitio)
se hace si alcanza el tiempo. Los productos de alta resolución y la fusión HPF, los
complementos de QGIS (GEDIMetrics y GEDI-Pipeline) y los embeddings AlphaEarth son
**ampliación del docente (no se evalúa)**: el alumno lee el resultado en el Desarrollo.
