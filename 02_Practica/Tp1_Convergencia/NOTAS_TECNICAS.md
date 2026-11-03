# Tp1 — Notas técnicas

> **Qué es este archivo.** Las decisiones técnicas del práctico, su fundamento y
> los errores que ya costaron tiempo. No es el punto de entrada: para el recorrido,
> abra `00_LEEME.md`; para los pasos, `00_Guia_del_practico/00_LEEME.md`.

## Referencia espacial

- **Una sola proyección para todo el curso: EPSG:32721 (WGS 84 / UTM 21 S).** Es la
  de los NISAR GCOV del Delta y la de las teselas Sentinel-2 21H y
  21J. Paraná y Diamante (60,6° O) quedan a 3,6° del meridiano central (57° O); el
  error de escala allí es de alrededor de 1 m por km, que no afecta ningún resultado
  del curso. Se declara y se acepta.
- **Grilla de 10 m con bordes en múltiplos exactos del píxel** (`grilla_sitio()`).
  Dos rásteres del mismo sitio, aunque vengan de sensores distintos, tienen los bordes
  de píxel en el mismo lugar y se apilan sin remuestrear otra vez.
- **El bbox del sitio es la unidad de comparación de coberturas.** Toda fracción de
  cobertura se calcula sobre el área del rectángulo en grados. Es una aproximación:
  en coordenadas geográficas un rectángulo de 0,4° no tiene la misma superficie en
  todas las latitudes. Para comparar escenas sobre un mismo sitio no importa.

## Fechas

- **Siempre de los metadatos y en UTC.** La fecha del archivo en el disco es la de
  descarga o la de copia. La hora UTC importa: una NovaSAR de las 01:36 UTC fue tomada
  la noche anterior en hora argentina (UTC−3).
- GEDI y ATL08 cuentan `delta_time` en segundos desde el 01/01/2018. La diferencia con
  UTC por segundos intercalares es de segundos y no cambia ninguna fecha.

## Huella frente a dato

- **La huella es lo que toca; el dato es lo que cubre.** Por eso se informan dos cifras.
- **NovaSAR-1:** el `image_HH.tif` del GRD trae sólo las cuatro esquinas como puntos
  de enlace. La huella es su envolvente y la proyección es un ajuste afín de la franja:
  de ahí los desplazamientos de cientos de metros que se miden en el Tp3.
- **NISAR GCOV:** sólo la frecuencia A. La máscara del producto vale 0 (muestra
  inválida o parcialmente enfocada), 255 (fuera de la adquisición) o 1 a n (número de
  subfranja, válida). Sin aplicarla, el borde de la pasada entra con valores de
  alrededor de −133 dB, que hunden cualquier promedio e inflan cualquier conteo.
- **Conteo a 100 m.** Basta para decidir si una escena cubre un sitio y es mucho más
  rápido que contar a 10 m. No sirve para nada más.
- **Productos en geometría de radar** (Sentinel-1 SLC, SAOCOM L1A, COSMO SCS): no
  tienen coordenadas de mapa hasta procesarlos en SNAP. En el Tp1 sólo se informa su
  huella declarada (`manifest.safe` o `.kml`); en la matriz se marcan con la fuente
  `inventario local (huella)`.

## Umbrales y por qué

| Umbral | Valor | Dónde | Fundamento |
|---|---|---|---|
| Cobertura mínima del sitio (S2, S1, inventario, ASF) | 50 % | `Tp1_03`, `Tp1_07` | Con menos de la mitad del sitio no se puede describir el evento en el sitio; se usa como regla única para todos los sensores |
| Nubosidad máxima dentro del sitio (S2) | 20 % | `Tp1_03` | Por encima, la escena sirve como evidencia parcial, no como mapa del sitio |
| Nubosidad de catálogo para no verificar | 80 % (`--nubes_max`) | `Tp1_03` | Sólo ahorra tiempo; no selecciona |
| Escena «engañosa» | huella ≥ 50 % y dato < 10 % | `Tp1_02` | Lo que un catálogo daría como útil y no lo es |
| Par óptico-radar | ≤ 3 días (`--dias_par`) | `Tp1_03` | En una crecida, el agua cambia en días; más de 3 días es otra situación |
| Ventana del evento | ±12 días (`--ventana`) | `Tp1_07` | Coincide con el ciclo de 12 días de una constelación Sentinel-1 con un solo satélite; es una decisión del analista y se declara |
| Sensibilidad de GEDI | ≥ 0,95 | `funciones_lidar.py` | Umbral habitual; en vegetación densa puede subirse a 0,98 y se declara |

## LiDAR

- **GEDI L2A versión 003**: el campo de calidad es `l2a_quality_flag_rel3`; en la 002
  era `quality_flag`. Un nombre de campo equivocado no siempre da error: puede leer
  una banda vacía y aprobar todo. El código usa el que exista y lo informa.
- **Receso de GEDI**: sin adquisiciones entre el 17/03/2023 y el 26/04/2024. Una
  búsqueda en esa ventana devuelve cero granulos y no es un error.
- **ATL08 versión 007**: el valor de relleno es 3,4 × 10³⁸ (el código descarta todo lo
  que no sea menor que 3,0 × 10³⁸). La fuerza del haz depende de `sc_orient`: con 0,
  los izquierdos son los fuertes; con 1, los derechos; con 2 (transición), no se
  clasifica.
- **Alturas de terreno elipsoidales.** `elev_lowestmode` (GEDI) y `h_te_best_fit`
  (ATL08) están referidas al elipsoide WGS 84. El Copernicus DEM, al geoide EGM2008.
  Antes de comparar se convierte con `alturas_a_egm2008()` (PROJ, grilla
  `us_nga_egm08_25.tif`). El Tp1 no compara alturas; el aviso es para el Tp3 en
  adelante.

## Grado de convergencia

La regla de `Tp1_07` traduce la diapositiva 18 de la presentación 01. Se evalúa en
este orden, sólo con las escenas verificadas que caen dentro de `--ventana` días del
evento:

1. Óptico + 2 o más bandas SAR + LiDAR: «completa».
2. Óptico + al menos una banda SAR: «parcial».
3. Dos o más bandas SAR sin óptico: «parcial (sin óptico)».
4. Óptico solo, o una sola banda SAR: «un solo sensor cerca del evento». Ese sensor
   da el mapa; los demás datos sirven sólo para interpretar. No hay nada que fusionar.
5. Nada dentro de la ventana, pero sí escenas verificadas en otras fechas:
   «histórica». El código no mira si son de años distintos: «histórica» quiere decir
   que no hay convergencia alrededor del evento.
6. Ninguna escena verificada: «sin datos».

Las bandas SAR se cuentan por banda (X, C, S, L, P), no por sensor: Sentinel-1 y
otro sensor de banda C suman una sola banda.

## Limitaciones conocidas

- Las consultas al Planetary Computer, ASF, CMR (NASA Earthdata) y ESA MAAP **no se
  pudieron probar** desde el entorno de desarrollo, sin red hacia esos servicios. Los
  scripts están probados con datos sintéticos o locales y el docente los corre una vez
  antes del curso.
- Los sitios de origen «aproximada» (`A2_IBICUY`, `D_LAPAZ_VILLAGUAY`,
  `E_PARANA_DIAMANTE`) no están ajustados todavía.
- `inventario_local.csv` es una sola tabla para todos los sitios y se reescribe en
  cada corrida de `Tp1_02`.
- Las planillas llevan el nombre del sitio, no el de la ventana: una segunda búsqueda
  sobre el mismo sitio con otras fechas las sobrescribe.

## Hallazgos con datos reales del curso

- Contexto del sitio (`Tp1_08`, 21/10/2026): MapBiomas cubre el 69,7 % de `B_CONCORDIA` (la margen uruguaya
  queda sin dato). De 1985 a 2025 las herbáceas bajan de 53,1 a 32,0 % y crecen la silvicultura (14,7 a
  24,2 %) y los cultivos perennes (5,6 a 12,1 %). 2007 es un año ruidoso de la clasificación (los cultivos
  perennes saltan a 20.552 ha y es el año con más pérdida). Quemado al menos una vez entre 1999 y 2025: 16,3 %.
- BIOMASS banda P del 22/07/2026: la HV trae interferencia de radiofrecuencia sin corregir
  (`rfiCorrectionFlag = false`); la cruzada es la VH. P VH por clase de MapBiomas 2025: bosques −13,5 a
  −13,7 dB, silvicultura −16,9, herbáceas −22,4, agua −29,3 dB.
- La altura FH de BIOMASS (L2A, julio de 2026) se mide con el agua enmascarada (MapBiomas 2025 clases 26, 31
  y 33, o JRC ≥ 50 %: el 10,8 % de los píxeles con FH, que daban 24 m de mediana sobre el lago). Aun sin agua no
  sirve en Concordia: 3,5 m en la silvicultura, 5,0 m en bosques cerrados y 7,1 m en herbáceas (22/10/2026).
- CCI Biomass 2024 por clase de MapBiomas 2025: bosques cerrados 83 Mg/ha, silvicultura 69, cultivos perennes
  45, herbáceas inundables 28 (hipótesis: mezcla del monte de ribera y el humedal en el píxel de 100 m; a contrastar con el PVIR v7.0 del producto), herbáceas 0.

- NovaSAR **47942** (13/09/2023) cubre el **39 %** de `B_CONCORDIA`; **47974**
  (14/09/2023) el **92 %** de `F_BOVRIL`; **50896** (22/12/2023) el **51 %** de
  `C_FEDERAL` y **no** cubre Concordia, aunque tenga la misma hora de pasada que la
  47942; **50918** el **4 %** de la franja D; **47525** es de San Javier (Santa Fe),
  fuera de los sitios. Medido con `Tp1_02` sobre los GRD.
- **Banda L durante la crecida de Concordia de noviembre de 2023:** NISAR y ALOS de
  ASF no tienen; sí hay SAOCOM (CONAE: 31/10 y 08/11, haz TNB, mitad oeste del sitio;
  11/11, haz TNA, todo el sitio; referencia seca del 10/10) y un ALOS-2 PALSAR-2
  ScanSAR del 16/11/2023 en ASF (HH y HV, 62,8 GB; bajado y llevado a γ⁰ a 20 m con
  `00_COMUN\procesar_alos2_scansar.py`, en `02_Subsets_SNAP_QGIS\ALOS2_gamma0`). Con ± 12 días el grado
  queda parcial con C + L; falta el LiDAR.
- GEDI no tiene adquisiciones entre el 17/03/2023 y el 26/04/2024.
- ALOS-1 PALSAR FBS 2011 es sólo HH; el HV de 2011 existe sólo en escenas FBD.
  Importa para el Tp9: una búsqueda que devuelve ALOS 2011 no garantiza la
  polarización cruzada.

## Banda L antes y durante la crecida (26/10/2026, `Tp1_06b_banda_L_antes_despues.py`)

- Escenas: SAOCOM de CONAE del 10/10/2023 (TNA, antes), 31/10 y 08/11/2023 (TNB, mitad oeste del sitio, 50,7 y 50,9 %),
  11/11/2023 (TNA, misma geometria que el 10/10) y 16/09/2026 (TNA), y ALOS-2 ScanSAR del 16/11/2023. Todas descendentes y
  mirando al oeste, como la orbita 68 del Sentinel-1. Incidencia: TNA 17,6 a 27,3 grados; TNB 27,2 a 35,5; ALOS-2 39 a 42.
- Pares de la misma geometria: L TNA 10/10 -> 11/11 (32 dias), L TNB 31/10 -> 08/11 (8 dias, sin 2,5 km del borde del haz),
  C Sentinel-1 23/10 -> 04/11 (12 dias).
- Resultado: en el agua de crecida de banda C del 04/11 (Tp6, 2.912 ha) la L (TNA) sube 0,6 dB frente a 3,2 dB en la tierra
  (-2,5 dB relativo) y la C baja 3,8 frente a 1,3 dB (-2,5 dB relativo). Para la C la comparacion es circular (la zona
  sale de su propia mascara). Prueba independiente (corrida del 27/10/2026): en el agua del optico del 04/11 que la C no
  marco (Tp6, MNDWI; 55.712 pixeles de 20 m), la L queda -2,7 dB (HH) y -2,6 dB (HV) respecto de la tierra, y la C solo
  -0,7 dB (VV). Las dos bandas, comparadas por separado, marcan la misma zona: es sinergia, no fusion de decision.
  El par TNB da +0,3 dB relativo: el 31/10 la crecida ya habia llegado (par durante-durante).
- Por clase (fuera de la mascara de C): en L bajan respecto del resto las herbaceas inundables (-2,6 dB), los bosques
  cerrados (-1,8) y los bordes de rios y lagunas (-3,4); en C ninguna clase se aparta mas de 0,3 dB. En banda L la
  vegetacion emergente inundada suele aumentar HH por doble rebote: la caida medida sugiere agua expuesta o pastos bajos
  cubiertos, no agua bajo un dosel (lo pone a prueba el Tp6).
- Contraste tierra-agua permanente en HH: 5,6 a 7,3 dB en los TNA de 2023 (compatible con viento sobre el embalse con
  incidencia empinada; sin dato de viento), 11,5 en el TNB del 08/11 y 14,5 el 16/09/2026 (compatible con agua calma). ALOS-2: nivel absoluto unos 4 dB bajo; solo dentro de su escena.
- Salidas: `05_Resultados/04_Tablas/B_CONCORDIA_banda_L_escenas.csv`, `B_CONCORDIA_antes_despues_por_zona.csv`,
  tres figuras en `05_Resultados/05_Graficos/Figuras_del_desarrollo`, muestra de Orange y bitacora
  `06_Control_calidad/Tp1_06b_banda_L_antes_despues.log` (corrida en el equipo del docente el 26/10/2026).

## Cambios del 18/10/2026 en `Tp1_03_buscar_optico_y_C.py` (corrida del docente)

1. **Tomas Sentinel-2 duplicadas.** El Planetary Computer guarda a veces la
   misma toma y tesela dos veces: la original y el reprocesamiento de ESA
   (Colección 1, 2024). Se deja la versión más nueva y se informa cuántas se
   descartaron (Concordia 2023: 15 de 39; Bovril 2023: 95 de 237).
2. **Mosaico del día.** Antes se decidía tesela por tesela y se descartaba la
   que cubría menos del 50 % del sitio; en un sitio grande ninguna tesela lo
   cubre sola (La Paz – Villaguay cae en 9). Así se perdía el 16/09/2026, sin
   nubes, que es la fecha óptica verificada del Tp9. Ahora se unen las teselas
   de la misma fecha y órbita y se mide cobertura y nubes del mosaico dentro
   del sitio. Los pares se arman con el mosaico del día.

Respaldo de la versión anterior: `00_COMUN\Tp1_03_buscar_optico_y_C_respaldo_20261018.py`.

Resultados de la corrida (pares óptico-C a 3 días o menos):

| Sitio | Ventana | Mosaicos S2 candidatos | S1 RTC candidatas | Pares | Mejor par |
|---|---|---|---|---|---|
| B Concordia | 10-11/2023 | 8 de 9 | 5 | 4 | 04/11/2023, mismo día, 0,1 % de nubes |
| A1 Delta | 06-10/2020 | 21 de 36 | 20 | 23 | 08/09/2020, mismo día, 0,4 % |
| F Bovril | 2023 | 68 de 98 | 27 | 37 | varios del mismo día sin nubes |
| E1 Barranca | 10/2018 | 2 de 5 | 2 | **0** | ninguno: óptico 04 y 19/10, radar 12 y 24/10 (5 días) |
| C Federal | 09/2026 | 6 de 13 | 5 | 6 | 14/09/2026, mismo día, 0 % |
| D La Paz – Villaguay | 09/2026 | 4 de 13 | 5 | 4 | 02/09/2026, mismo día, 0 % |

El 17/09/2026 (BIOMASS y NISAR) estaba nublado: 39 % de nubes en la franja D
y 99 % en Federal. El óptico más cercano útil es el 16/09/2026.

## Corrida del 20/10/2026, después de la auditoría (vale ésta)

Hecha con `00_COMUN\09_Herramientas\correcciones_auditoria_datos.bat` (pasos 4 y 5). Cambio de fondo respecto
de la corrida del 18/10: el LiDAR entra a la matriz **sólo** en las fechas con al menos una huella válida
contada en los `.h5` del equipo (`lidar_fechas_validas_<SITIO>.csv`), y GEDI descarta además las huellas sobre
agua (`landsat_water_persistence` ≥ 50 %). Un gránulo que cruza el sitio ya no alcanza.

| Sitio | Evento | Óptico | SAR | LiDAR a ±12 días | Grado | LiDAR válido más cercano |
|---|---|---|---|---|---|---|
| B Concordia (inundación, `_2023_Tp6`) | 04/11/2023 | sí | C | **no** | parcial | ATL08 12/10/2023 (23 días antes; el ATL08 del 10/11/2023 no tiene huellas válidas en el sitio) |
| B Concordia (urbano, `_2026_Tp10`) | 16/09/2026 | sí | C + L | no | parcial | — |
| A1 Delta | 13/10/2020 | sí | C + L | sí | **completa** | ATL08 16/10/2020 (3 días, 19 huellas) |
| F Bovril | 14/09/2023 | sí | C + S | no | parcial | ATL08 19/08/2023 (26 días antes) |
| E1 Barranca | 15/10/2018 | sí | C + X | no | parcial | ATL08 03/11/2018 (19 días después) |
| C Federal | 17/09/2026 | sí | C + L + P | no | parcial | ATL08 13/12/2025 (278 días antes, con los `.h5` del equipo) |
| D La Paz – Villaguay | 17/09/2026 | sí | C + L + P | no | parcial | ATL08 15/07/2026 (64 días antes) |

Recuento con el filtro de agua: La Paz – Villaguay 3 460 703 huellas GEDI, 893 781 válidas (antes 897 376:
32 562 caen sobre agua). La tabla genérica `matriz_convergencia_B_CONCORDIA.csv` es la del evento 2023; para
cada emergencia de Concordia use la del sufijo (`Tp1_07` con `--etiqueta` lee las planillas de búsqueda con el
mismo sufijo).

## Corrida del docente del 18/10/2026: pasos 4, 5 y 7 (reemplazada por la de arriba)

Hecha con `00_COMUN\09_Herramientas\Tp1_corrida_docente.bat` (ventana y fecha de
evento de cada práctico, ventana de ±12 días). Sin errores en ningún sitio.
`Tp1_07` usa ahora el mosaico del día de Sentinel-2 (no cada tesela) y el rótulo
del evento quedó dentro del gráfico.

| Sitio | Evento | Óptico | SAR | LiDAR a ±12 días | Grado | LiDAR más cercano |
|---|---|---|---|---|---|---|
| B Concordia | 04/11/2023 | sí | C | sí | parcial | ATL08 10/11/2023 (6 días) |
| A1 Delta | 13/10/2020 | sí | C + L | sí | **completa** | ATL08 16/10/2020 (3 días) |
| F Bovril | 14/09/2023 | sí | C + S | no | parcial | ATL08 19/08/2023 (26 días antes) |
| E1 Barranca | 15/10/2018 | sí | C + X | no | parcial | ATL08 03/05/2019 (200 días después) |
| C Federal | 17/09/2026 | sí | C + L + P | no | parcial | ATL08 11/07/2026 (68 días antes) |
| D La Paz – Villaguay | 17/09/2026 | sí | C + L + P | no | parcial | ATL08 15/07/2026 (64 días antes) |

En Federal y La Paz – Villaguay la convergencia es parcial sólo por el LiDAR:
GEDI termina en 2025 y el último ATL08 es de julio de 2026. Para el monte, cuya
altura no cambia en dos meses, se puede justificar ampliar la ventana del LiDAR
(y declararlo); para un evento rápido, no.

Recuento LiDAR del paso 5: coincide exactamente con `LIDAR\recuento_lidar.csv`
(por ejemplo, La Paz – Villaguay: 3 460 703 huellas GEDI, 897 376 válidas).
El GeoPackage de huellas de La Paz – Villaguay pesa 1,2 GB.

## Revisión del 27/10/2026 (auditoría académica)

- `Tp1_06b_banda_L_antes_despues.py`: comprueba que existan las máscaras del Tp6 (insumo YA VIENE HECHO) y, si faltan,
  lo dice y termina; toma 0 como sin dato en γ⁰ cuando el GeoTIFF no lo declara (`--nodata_gamma`); semilla en
  `--semilla`; agrega la zona «agua del óptico 04/11 sin la de C». Corrido con los datos del curso: reproduce las cifras
  anteriores (Tabla de pares) y agrega la zona independiente.
- `Tp1_07_matriz_convergencia.py`: informa las observaciones independientes (una por plataforma, banda y fecha): en
  B_CONCORDIA, 243 registros = 233 observaciones; a ± 12 días, 16 registros = 10 observaciones. La línea de tiempo trae
  una ampliación de ± 30 días y fechas dd/mm/aaaa. La matriz no cambia (227 filas, mismo contenido).
- El filtro de agua de GEDI es la persistencia de agua de Landsat del propio L2A (`landsat_water_persistence` ≥ 50 %),
  no JRC Global Surface Water. JRC se usa sólo para el agua permanente del paso 6b y la máscara de la altura FH.
- Pasada GEDI del 16/07/2019: en las 755 válidas con rh98 > 50 m, el L2A eligió el algoritmo 1 sólo en el 16 % (48 % el
  10), contra el 82 % en las de 15 a 40 m; el suelo elegido queda 11,5 m por debajo del DEM del producto (mediana).
  Además de nubes finas, es posible una mala elección del suelo (columna `selected_algorithm` de GEDIMetrics).
