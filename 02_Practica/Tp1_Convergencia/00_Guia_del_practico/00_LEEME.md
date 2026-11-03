# Tp1 — Guía paso a paso

Lunes, 9 a 13 h. Sitio: `B_CONCORDIA`. Fecha de análisis: 04/11/2023, el día con el
par óptico–radar más cercano (Sentinel-1 y Sentinel-2 con cuatro horas y media de
diferencia); no es el pico de la crecida.

Cada paso dice: **(a)** qué se hace y por qué, **(b)** dónde, **(c)** la orden o
los menús exactos, **(d)** lo que muestra la pantalla, **(e)** cómo saber si salió bien y
**(f)** los errores típicos.

Todas las órdenes se escriben en el **Miniforge Prompt** (menú Inicio de Windows >
Miniforge3 > Miniforge Prompt), no en la consola común de Windows.

**Landsat 8 y 9.** Escenas de este práctico, la pasada más cercana a cada Sentinel-2 con el sitio cubierto y despejado: Concordia, `B_CONCORDIA_L8_20231025`: Landsat 8 del 25/10/2023 para el Sentinel-2 del 04/11/2023 (10 días antes; el Landsat 9 del 02/11/2023 pasó con casi todo el sitio nublado).

Son Colección 2, Nivel 2 de USGS (reflectancia y temperatura de superficie, píxel de 30 m), bajadas del Planetary Computer. Están en `02_Subsets_SNAP_QGIS\SNAP_DIMAP` y `QGIS_GeoTIFF`, con las bandas `SR_B1` a `SR_B7` (reflectancia), `ST_B10` (temperatura, K), `ST_QA`, `QA_PIXEL` y las virtuales `NDVI` y `ST_B10_C` (°C).

Landsat 9 da imágenes desde el 31/10/2021; antes sólo hay Landsat 8. Los dos llevan instrumentos gemelos (OLI y TIRS) y se comparan entre sí sin ajuste. Con Sentinel-2 no: el píxel es de 30 m contra 10 y 20 m, y las bandas no coinciden del todo (el infrarrojo cercano de Landsat, 865 nm, equivale a la B8A, no a la B08).

Fuente: USGS / NASA, Landsat 8 y Landsat 9 OLI/TIRS, Colección 2 Nivel 2, distribuido por Microsoft Planetary Computer, https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2

**Fusión Landsat + Sentinel-2.** El Landsat también viene afinado a 10 m con el detalle espacial del Sentinel-2 de la fecha más cercana: se lo interpola a la grilla de 10 m y se le suma el detalle fino de la banda Sentinel-2 de 10 m que más se le parece, escalado por una regresión entre los dos sensores (filtro pasa-altos con modulación por regresión, HPF). Trae las bandas `SR_B1` a `SR_B7` en reflectancia, `mascara_detalle` (1 = se agregó detalle; 0 = nube, sombra o falta de dato en alguna de las dos) y el `NDVI` virtual; el método y la calidad de cada banda están en los metadatos.

El control es el ERGAS: la imagen afinada se lleva de nuevo a 30 m y se compara con el Landsat original; por debajo de 3 la fusión es buena. Sirve para mirar e interpretar, con tres cuidados: un cambio real entre las dos fechas aparece como detalle falso; las bandas 6 y 7 (infrarrojo de onda corta) toman el detalle de una banda de 10 m de otra región del espectro y son las menos confiables; y la temperatura no se afina.

En este práctico: `B_CONCORDIA_L8_20231025_fusion_S2_20231104_10m`: 10 días entre las dos imágenes, con la crecida subiendo en el medio. ERGAS 1,85 (protocolo de Wald: la fusión degradada a 30 m frente al Landsat; por debajo de 3 es buena), que mide la coherencia espectral, no la ganancia de detalle. La correlación entre los sensores a 30 m es de 0,60 a 0,77 en el visible, así que el programa agrega detalle sólo en parte: un buen ejemplo de por qué la fusión exige fechas cercanas.

**Pléiades y Pléiades Neo de CONAE.** Referencia visual de muy alta resolución del casco urbano (Pléiades, 0,5 m; Pléiades Neo, 0,3 m), 2022-2023, del proyecto Impactar de CONAE. Es un servicio de mapas y necesita internet: en `02_Subsets_SNAP_QGIS\Pleiades_CONAE_WMS` hay un `.xml` por localidad que se arrastra a QGIS (instrucciones en el `LEEME.md` de esa carpeta). Sirve para mirar y digitalizar, no para calcular: es RGB color real, sin infrarrojo ni reflectancia, y la fecha exacta no está publicada, sólo el año.

En este práctico: Concordia y General Roca, Pléiades Neo 2023 (`Concordia_2023_Pleiades_CONAE.xml`).

Fuente: CONAE, proyecto Impactar; Pléiades y Pléiades Neo, Airbus Defence and Space. Servicio WMS: https://geotematico01.conae.gov.ar/geoserver/wms; catálogo: https://catalogos.conae.gov.ar/catalogo/catalogoGeoServiciosOGC.html

**CBERS-4A, cámara WPM (INPE).** Pancromática de 2 m y multiespectral de 8 m (azul, verde, rojo e infrarrojo cercano), producto L4 ortorrectificado, en números digitales. Cada escena viene en dos productos: `..._MS_8m` (las cuatro bandas originales) y `..._pansharpened_2m` (la pancromática y las cuatro bandas afinadas a 2 m por Brovey ponderado, el método por defecto de GDAL). Es un pansharpening clásico: pancromática y multiespectral del mismo satélite y del mismo instante; compárelo con la fusión Landsat + Sentinel-2, que combina dos sensores y dos fechas. El control es el mismo ERGAS (por debajo de 3, bueno). Los números digitales no son reflectancia y el Brovey altera la radiometría: sirve para mirar y digitalizar, no para calcular índices. Cubre una zona de 12 a 21 km, no el sitio entero, y la escena se eligió a ojo, sin nubes, porque el catálogo del INPE no informa la nubosidad.

En este práctico: no hay escena: ninguna pasada a 120 días cubre Concordia despejada en 2023.

**Embeddings anuales AlphaEarth Foundations (Google y Google DeepMind).** 64 números por píxel de 10 m que resumen un año entero de Sentinel-1, Sentinel-2, Landsat, GEDI, clima y otras fuentes, aprendidos por un modelo de inteligencia artificial. Las dimensiones (`A00` a `A63`) no tienen significado físico propio: sirven para clasificar con pocas muestras, buscar zonas parecidas y detectar cambios entre años. Vienen en enteros de 8 bits tal como los entrega Google (`..._AlphaEarth_embeddings_<año>_10m`); para pasarlos a valores reales, valor = signo(DN) × (DN / 127,5)², y −128 es sin dato. El `..._CP1_CP2_CP3_RGB_8bit.tif` muestra las tres primeras componentes principales para mirar en QGIS; sus colores no tienen significado fijo. Resumen un año, no una fecha; 2026 todavía no existe y se usa 2025, el último.

En este práctico: Concordia, 2023.

Fuente: The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind (CC BY 4.0). Copia en Source Cooperative (Taylor Geospatial), https://source.coop/tge-labs/aef

**BIOMASS en banda P (ESA).** El primer radar satelital en banda P: 435 MHz, unos 69 cm de longitud de onda, cuatro polarizaciones. La onda larga atraviesa el follaje y responde a troncos y ramas gruesas. En `02_Subsets_SNAP_QGIS\SNAP_DIMAP` y `QGIS_GeoTIFF` vienen `B_CONCORDIA_BIOMASS_P_20260722` (nivel L1B DGM del 22/07/2026, con `Gamma0_HH`, `Gamma0_HV`, `Gamma0_VH` y `Gamma0_VV` en lineal, el ángulo de incidencia y las bandas virtuales en dB; no está proyectado y se ubica con sus puntos de enlace) y la altura del bosque `..._FH_20260707_0719` y la retrodispersión con el suelo cancelado `..._GN_20260707_0719` (nivel L2A, pila del 07 al 19/07/2026, píxel de unos 90 m). En el RGB de `RGB_copol_cruzada_cociente` la cruzada es la `VH`: la `HV` de estos productos trae interferencia de radiofrecuencia que ESA detectó y no corrigió (paso 9). Es de 2026: no entra a la matriz del evento de 2023 (paso 6 y paso 7).

Fuente: ESA, BIOMASS banda P (435 MHz), L1B DGM y L2A FP_FH y FP_GN; ESA MAAP, https://catalog.maap.eo.esa.int

**MapBiomas Argentina.** Mapas anuales de cobertura y uso del suelo de 1985 a 2025 a 30 m, hechos con Landsat por la red MapBiomas, y productos derivados: pérdida y vegetación secundaria (1987–2025) y área quemada de MapBiomas Fuego (1999–2025). En `QGIS_GeoTIFF`: `B_CONCORDIA_MapBiomas_cobertura_1985_2025.tif` (una banda por año; el `.qml` con la leyenda oficial se carga solo en QGIS), `..._perdida_veg_1987_2025` (con su `.qml`) y `..._fuego_anual_1999_2025`, `..._fuego_frecuencia_1999_2025`, `..._fuego_mes_...` y `..._fuego_ultimo_anio_2025`. Es un producto de terceros, óptico, y sirve de **contexto**: qué cubiertas hay y cómo cambiaron, no la verdad del terreno. Cubre Entre Ríos: la margen uruguaya del sitio queda sin dato, el 30 % de `B_CONCORDIA`.

Fuente: Proyecto MapBiomas Argentina, Colección 3 de los mapas anuales de cobertura y uso del suelo y Colección 1 de MapBiomas Fuego, https://argentina.mapbiomas.org

**ESA CCI Biomass.** Biomasa aérea (AGB, en Mg/ha) y su desvío (AGB_SD), a unos 100 m, para 2010, 2015, 2020, 2021 y 2024, estimada con radar en banda C y L. `B_CONCORDIA_CCI_Biomass_v7_AGB.tif` tiene diez bandas: AGB de cada año y su desvío. Resume un año, no una fecha, y no es independiente del radar: se usa como contexto, no como verdad.

Fuente: Santoro, M. y Cartus, O. (2026). ESA Biomass Climate Change Initiative (Biomass_cci), v7.0, NERC EDS CEDA, https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903

---

## Paso 0 — Abrir el entorno y ubicarse

**(a)** Los scripts usan el entorno `sar` (Python 3.11, GDAL, rasterio, geopandas,
h5py, pystac-client, asf_search, earthaccess). Fuera de ese entorno no encuentran las
bibliotecas.

**(b)** Miniforge Prompt.

**(c)**

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp1_Convergencia\03_Scripts
python ..\..\00_COMUN\configuracion_comun.py
```

El `/d` de `cd` hace falta cuando se cambia de unidad (de `C:` a `D:`).

**(d)** El último programa imprime la carpeta de práctica, la de originales, la de
NISAR del Delta, la proyección común (`EPSG:32721, pixel 10 m`) y la lista de sitios
con su origen (`presentacion_02`, `aproximada`, `mosaico_NISAR`, etc.).

**(e)** Al lado de cada carpeta de datos no debe aparecer `<-- NO EXISTE`. Si aparece
para NISAR o para los originales, los pasos 2 y 5 lo van a declarar y seguir, pero
conviene corregirlo antes.

Si es la primera vez que usa esta computadora, revise además el entorno completo
desde `00_COMUN`:

```
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\00_COMUN
python comprobar_entorno.py
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp1_Convergencia\03_Scripts
```

`comprobar_entorno.py` revisa la versión de Python y cada biblioteca, que GDAL lea
JPEG 2000 y HDF5, que PROJ tenga la grilla del geoide EGM2008, las carpetas de datos y
que exista la credencial de NASA Earthdata (sin leer su contenido). Con `--red` prueba
además la conexión al Planetary Computer, ASF y Earthdata. Debe terminar con
`Resultado: TODO EN ORDEN`; si no, cada problema aparece arriba con su línea `FALTA`,
`NO ESTA` o `SIN CONEXION`.

**(f)** Errores típicos:

- `conda` no se reconoce: abrió la consola común en lugar del Miniforge Prompt.
- `EnvironmentNameNotFound: sar`: el entorno no está instalado. Desde
  `02_Practica\00_COMUN`: `conda env create -f entorno_sar.yml`.
- Los datos están en otra unidad: se indica sin tocar el código, en la misma ventana,
  antes de correr cualquier script:

```
set CURSO_SAR_NISAR_DELTA=G:\NISAR_DELTA
set CURSO_SAR_NOVASAR=G:\IMÁGENES NOVASAR-1 2023 2024\ENTRE RIOS-SANTA FE
set CURSO_SAR_ORIGINALES=G:\ORIGINALES_CURSO_SAR
```

La variable dura mientras la ventana esté abierta.

---

## Paso 1 — Los sitios a vector (SE CORRE) y su revisión (EN QGIS)

**(a)** Toda búsqueda en un catálogo empieza por un polígono. Si cada grupo dibuja el
suyo, cada uno busca sobre un sitio distinto y nada se puede comparar. Este paso
escribe el polígono oficial a partir de `configuracion_comun.py`, el único lugar
donde se definen los sitios.

**(b)** Miniforge Prompt y después QGIS.

**(c)**

```
python Tp1_01_sitios_a_vector.py
```

**(d)** Una línea por sitio: columnas × filas de la grilla de 10 m, superficie en
km² y origen. Los sitios de origen `aproximada` (`A2_IBICUY`, `D_LAPAZ_VILLAGUAY`,
`E_PARANA_DIAMANTE`) llevan el aviso `<-- REVISAR en el Tp1, paso 1`. Al final:
`Escrito: ...\00_COMUN\01_AOI\sitios_curso.gpkg (capas sitios y sitios_utm21s)` y
un `.geojson` por sitio.

**Revisión en QGIS:**

1. `Capa > Añadir capa > Añadir capa vectorial...`, elija
   `02_Practica\00_COMUN\01_AOI\sitios_curso.gpkg` y marque las dos capas.
2. Fondo de imagen: en el panel **Navegador**, clic derecho en **XYZ Tiles >
   Nueva conexión...**, nombre `ESRI World Imagery`, URL
   `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`.
   Arrástrela al mapa debajo de los sitios.
3. Propiedades de la capa `sitios` > **Simbología** > relleno transparente, borde
   amarillo de 0,8 mm. Propiedades > **Etiquetas** > etiquetas simples con el campo `sitio`.
4. Verifique que `B_CONCORDIA` encierre Concordia, Salto Grande y el río Uruguay.
   Mire también los sitios `aproximada`: ¿caen sobre lo que dice su nombre?

**(e)** Con la herramienta **Identificar objetos** (botón con la «i» de la barra de
atributos) o con la tabla de atributos (botón derecho sobre la capa > `Abrir tabla de
atributos`), el campo `superficie_km2` de cada sitio debe coincidir con
lo que imprimió la bitácora `05_Resultados/06_Control_calidad/Tp1_01_sitios.log`.
La capa `sitios_utm21s` debe estar en EPSG:32721 (Propiedades > Información).

**(f)** Errores típicos:

- Editar el `.geojson` a mano para «corregir» un sitio. **No se hace.** Si un sitio
  está mal, se avisa al docente: se corrige en `configuracion_comun.py` y se vuelve
  a correr este script.
- Confundir la imagen de fondo con una fuente datada: el mosaico de ESRI no tiene
  fecha conocida. Sirve para ubicarse, no como referencia de un evento.

---

## Paso 2 — Inventario de lo que ya está en disco (SE CORRE)

**(a)** Antes de buscar afuera, se mira lo que el curso ya tiene: NovaSAR-1 (banda S,
6 m, HH, cedidas por CSIRO), NISAR GCOV banda L (NASA) y banda S (ISRO) del Delta,
los NISAR banda L bajados aparte para Concordia, Federal y Bovril
(`00_COMUN\08_Originales_crudos\NISAR`), el archivo del curso 2023 (Sentinel-1 SLC, SAOCOM-1A) y los COSMO-SkyMed de
Diamante. Para cada escena y cada sitio se informan **dos cifras, una al lado de la
otra**:

- `cobertura_huella_%`: cuánto del sitio toca el polígono que declara el producto
  (lo que diría un catálogo);
- `pixeles_validos_%`: cuántos píxeles del sitio traen dato real, contados uno por
  uno a 100 m.

La diferencia entre las dos es el centro del Tp1. La huella es lo que **toca** el
rectángulo; el dato es lo que lo **cubre**. En NovaSAR la huella es el cuadrilátero
de las cuatro esquinas que trae el GRD como puntos de enlace; en NISAR, el borde de
la franja trae muestras que la máscara del producto marca como inválidas
(0 = inválido, 255 = fuera de la adquisición, 1 a n = válido).

**(b)** Miniforge Prompt.

**(c)** Corra el inventario **completo**, sin `--sitios`, porque la tabla de salida
es una sola y se reescribe en cada corrida:

```
python Tp1_02_inventario_local.py
```

(La forma `python Tp1_02_inventario_local.py --sitios B_CONCORDIA F_BOVRIL` existe,
pero deja en la tabla sólo esos sitios para NovaSAR y NISAR.)

**(d)** Seis bloques: NovaSAR-1; NISAR banda L del Delta (`NISAR_DELTA\BANDA_L_NASA`);
NISAR banda S del Delta (`NISAR_DELTA\BANDA_S_ISRO`, si existe); NISAR banda L de
`08_Originales_crudos\NISAR` (Concordia, Federal, Bovril); el archivo de escenas del
curso 2023; y los COSMO-SkyMed de Diamante. En cada línea de NovaSAR y NISAR: escena, fecha, sitio, `huella ... %` y
`pixeles con dato ... %`. En el archivo 2023 y COSMO: sensor, fecha, modo y la
huella sobre cada sitio, **sin** conteo de píxeles (esos productos están en
geometría de radar y recién tienen coordenadas después de SNAP). Al final, el
resumen: cuántas combinaciones escena-sitio se inventariaron y cuántas «tocan el
sitio con la huella (≥ 50 %) pero casi no traen dato (< 10 %)».

**(e)** Controles:

- La escena NovaSAR 47942 (13/09/2023) debe dar alrededor del **39 %** de
  `B_CONCORDIA` con dato: es la cifra medida con este mismo script sobre los GRD.
- La 50896 (22/12/2023) **no** debe aparecer sobre Concordia aunque tenga la misma
  hora de pasada que la 47942: cubre Federal.
- Si aparece `AVISO: la fecha del metadato (...) no coincide con la de la
  configuracion`, manda el metadato. Anótelo.

**(f)** Errores típicos:

- `NO EXISTE la carpeta de NovaSAR en este equipo`: falta la unidad `E:` o la
  variable `CURSO_SAR_NOVASAR`. El script sigue y lo deja escrito; no es un error del
  programa.
- Tardanza: el recorrido del archivo 2023 (cientos de GB) lleva varios minutos
  aunque no lea imágenes. No lo interrumpa.
- Leer `cobertura_huella_%` como cobertura real. No lo es.

Salida: `05_Resultados/04_Tablas/inventario_local.csv` y la bitácora
`05_Resultados/06_Control_calidad/Tp1_02_inventario_local.log`.

---

## Paso 3 — Óptico y banda C en el Planetary Computer (SE CORRE)

**(a)** Se buscan Sentinel-2 L2A y Sentinel-1 RTC (γ⁰ ya corregido por el terreno)
en el catálogo STAC del Planetary Computer, que no pide cuenta, y se **verifica cada
escena dentro del sitio** antes de bajar nada. La nubosidad que declara el catálogo
(`eo:cloud_cover`) es la de la tesela entera de 110 × 110 km; la que importa es la
del sitio, que el script cuenta con la capa de clasificación de escena (SCL). La
verificación lee sólo la ventana del sitio, a 60 m (Sentinel-2) o a 100 m
(Sentinel-1): mide en segundos lo que costaría minutos bajar.

**(b)** Miniforge Prompt (necesita red).

**(c)**

```
python Tp1_03_buscar_optico_y_C.py --sitio B_CONCORDIA --desde 2023-10-01 --hasta 2023-11-30
```

Opciones, con su valor por defecto: `--nubes_max 80` (no verifica las escenas con
más nubosidad de catálogo, sólo para ahorrar tiempo) y `--dias_par 3` (diferencia
máxima de días para formar un par óptico-radar).

**(d)** Para cada Sentinel-2: fecha, identificador, `nubes catalogo`, `sitio`,
`util` y la decisión: `candidata`, `descartada: cubre X % del sitio` (menos del
50 %), `descartada: X % de nubes DENTRO del sitio` (más del 20 %) o
`no se verifica (supera --nubes_max)`. Para cada Sentinel-1: fecha y hora, órbita
relativa, pasada, polarizaciones, `util` y la decisión (`candidata` si cubre al menos
el 50 % del sitio). Después, un bloque **«mosaico del día»**: las teselas
Sentinel-2 de una misma fecha y órbita se unen y se decide sobre el sitio entero
(un sitio grande no lo cubre ninguna tesela sola). **Esa es la decisión que cuenta**:
los pares óptico-C y la matriz del paso 7 usan el mosaico del día, no cada tesela por
separado (en `planilla_MPC_<SITIO>.csv` son las filas `Sentinel-2 mosaico del dia`). Al
final, los pares óptico-C a 3 días o menos, ordenados por diferencia de días y nubes en
el sitio.

**(e)** Controles:

- Busque una escena con poca nube de catálogo y mucha en el sitio, o al revés. Si
  aparece, ya tiene el ejemplo para la pregunta 2.
- El 04/11/2023 debería aparecer como fecha de un par de 0 días: es la que
  `configuracion_comun.py` registra como verificada (Sentinel-1A y Sentinel-2B del
  mismo día). Si no aparece, revise si el Sentinel-2 de ese día quedó descartado y
  por qué.
- Mire la columna de órbita relativa: dos fechas de Sentinel-1 con órbitas distintas
  tienen geometrías de mirada distintas y no se comparan pixel a pixel sin decirlo.

**(f)** Errores típicos:

- Error de red o de certificado: el script no puede contactar el catálogo. Pruebe en
  el navegador `https://planetarycomputer.microsoft.com/api/stac/v1`. Si no abre, es
  la red del aula: se declara y se usa la planilla del grupo vecino o la del docente.
- `(no se pudo leer la ventana: ...)` en un Sentinel-1: falló la lectura de esa
  escena; queda con `util` vacío y se descarta. Vuelva a correr: las URL firmadas
  duran alrededor de una hora.
- `Ningun par cumple la condicion`: no es un error. Amplíe la ventana o
  `--dias_par`, **y declárelo**.

Salida: `planilla_MPC_B_CONCORDIA.csv` y `pares_optico_C_B_CONCORDIA.csv` en
`05_Resultados/04_Tablas/`.

---

## Paso 4 — Radar en ASF (SE CORRE la búsqueda; la descarga YA VIENE HECHA)

**(a)** ASF tiene lo que el Planetary Computer no: NISAR L2 GCOV (banda L),
Sentinel-1 IW SLC (con fase, para interferometría) e IW GRD (para la cadena completa
en SNAP del Tp2) y ALOS PALSAR RTC (banda L histórica, 2006–2011). Los productos de
ASF no son COG: no se pueden contar píxeles sin bajarlos. Por eso aquí la columna
`pixeles_validos_%` queda **vacía a propósito**: una cifra que no se midió no se escribe.

**(b)** Miniforge Prompt (necesita red). Buscar no pide cuenta.

**(c)**

```
python Tp1_04_buscar_asf.py --sitio B_CONCORDIA --desde 2023-10-01 --hasta 2023-11-30
```

Para limitar a algunos productos: `--solo NISAR S1_SLC S1_GRD ALOS` (cualquiera de
esos cuatro nombres). Para bajar los N productos de mayor huella de cada sensor
pedido: `--descargar N` (por defecto 0, no baja nada). **En clase no se descarga.**

Si alguna vez descarga, la cuenta de NASA Earthdata se toma, en este orden, de la
variable `EARTHDATA_TOKEN`, del archivo `.netrc` del usuario o del teclado (la
contraseña no se muestra). Nunca se escribe en el script.

**(d)** Un bloque por producto: `N productos tocan el sitio` y una línea por
producto con fecha, hora, pasada, track, polarizaciones, `huella %` y nombre.

**(e)** Controles:

- **NISAR debe devolver cero productos** para octubre y noviembre de 2023: la misión
  no estaba en órbita. Eso dice que NISAR no tiene banda L para la crecida, no que
  falte toda la banda L: SAOCOM (CONAE) y ALOS-2 PALSAR-2 (JAXA) se buscan en el
  paso 6, y para B_CONCORDIA hay SAOCOM del 31/10, el 08/11 y el 11/11/2023 y un
  ALOS-2 del 16/11/2023.
- **ALOS RTC debe devolver cero** para 2023: la serie termina en 2011.
- Compare las fechas de Sentinel-1 GRD de ASF con las del paso 3: deben coincidir
  las pasadas (el RTC del Planetary Computer se hace a partir de esos GRD).

**(f)** Errores típicos:

- `La busqueda fallo: ...`: el servicio no respondió. El script lo escribe y sigue
  con el siguiente producto. Se declara.
- Tomar `huella %` de ASF como cobertura real: en ASF, en este paso, sólo hay huella.

Salida: `05_Resultados/04_Tablas/planilla_ASF_B_CONCORDIA.csv`.

---

## Paso 5 — LiDAR: GEDI e ICESat-2 (SE CORRE la búsqueda y el conteo; la descarga YA VIENE HECHA)

**(a)** El LiDAR satelital **no forma una imagen**: muestrea por huellas (GEDI,
25 m) o por segmentos (ATL08, 100 m a lo largo de la traza). Un granulo trae toda la
órbita y casi nada cae en el sitio. Lo que decide si el LiDAR puede entrar como
referencia es el **número de huellas válidas** en el sitio, no el número de granulos.

Filtros que aplica `00_COMUN/funciones_lidar.py`:

- GEDI L2A v003: bandera de calidad = 1 (en la versión 003 el campo se llama
  `l2a_quality_flag_rel3`, no `quality_flag`), `degrade_flag = 0`,
  `sensitivity ≥ 0,95` y `surface_flag = 1`.
- ATL08 v007: canopia válida si `h_canopy` no es el valor de relleno (3,4 × 10³⁸),
  `urban_flag = 0` y `segment_watermask = 0`; terreno válido si `h_te_best_fit` no
  es relleno y no es agua. Se informa además si el haz es fuerte (según
  `orbit_info/sc_orient`) y si la adquisición es nocturna.

**(b)** Miniforge Prompt (la búsqueda necesita red; el conteo no).

**(c)** Primero, la búsqueda alrededor del evento:

```
python Tp1_05_buscar_lidar.py --sitio B_CONCORDIA --desde 2023-10-01 --hasta 2023-11-30
```

Después, la búsqueda en el período completo de las dos misiones (es el valor por
defecto: `--desde 2019-04-01 --hasta 2026-09-30`):

```
python Tp1_05_buscar_lidar.py --sitio B_CONCORDIA
```

Si el docente dejó granulos bajados en `<ORIGINALES>\LIDAR\B_CONCORDIA\`, el conteo
sólo, sin red:

```
python Tp1_05_buscar_lidar.py --sitio B_CONCORDIA --solo_contar
```

Otras opciones: `--sensibilidad 0.95` (umbral de GEDI; en vegetación densa puede
subirse a 0.98, y se declara) y `--descargar` (baja a
`<ORIGINALES>\LIDAR\<SITIO>\<producto>\`; **en clase no se usa**).

**(d)** Para cada producto (`GEDI02_A` versión `003`, `ATL08` versión `007`): cuántos
granulos cruzan el sitio y la lista con fecha y tamaño. En la ventana del evento
aparece:
`AVISO: la ventana incluye el receso de GEDI (17/03/2023 a 26/04/2024)`. En el
conteo: `GEDI L2A: N huellas en el sitio, M validas (...%)` y una línea por motivo de
descarte (`calidad`, `degradado`, `sensibilidad<0.95`, `superficie`); para ATL08,
segmentos en el sitio, con canopia válida y con terreno válido.

**(e)** Controles:

- **GEDI debe devolver cero granulos** entre el 17/03/2023 y el 26/04/2024. No es
  un error de la búsqueda: la misión estuvo guardada en la Estación Espacial.
- La suma de las huellas descartadas por cada motivo puede superar el total de
  descartadas: una huella puede tener más de un motivo.
- Abra en QGIS `05_Resultados/03_Vectores/lidar_B_CONCORDIA.gpkg` (capas `gedi_l2a` y
  `atl08`). Propiedades > **Simbología** > **Categorizado**, columna `valido` (GEDI) o
  `canopia_valida` (ATL08), botón **Clasificar**. Las huellas sobre el río deben
  estar descartadas: en ATL08 por la máscara de agua del producto
  (`segment_watermask`, motivo en `motivo_canopia`); en GEDI, que no trae una máscara
  propia, por la persistencia de agua de Landsat que viene en el L2A (columna
  `agua_persistencia` ≥ 50 %, motivo `agua` en la columna `motivo`). La tabla
  `lidar_conteo_B_CONCORDIA.csv` da cuántas se descartaron por cada motivo, y
  `lidar_fechas_validas_B_CONCORDIA.csv` las fechas con al menos una huella válida:
  son las únicas que entran a la matriz del paso 7.
- Control de plausibilidad: las huellas válidas con `rh98` mayor que 50 m (GEDI) o
  `h_canopy` mayor que 50 m (ATL08) quedan con `plausible = falso` y
  `control_plausibilidad = rh98 > 50 m: revisar` (o `h_canopy > 50 m: revisar`). No se
  borran ni cambian `valido`: se revisan en el mapa (Categorizado por `plausible`) y
  se decide huella por huella. En Concordia son 1.018 huellas GEDI y 115 segmentos
  ATL08.

**(f)** Errores típicos:

- `No hay granulos descargados`: el conteo no tiene qué leer. Se declara.
- Interpretar «0 granulos» en 2023 como falla de la red: lea el AVISO.
- `No se pudo autenticar en NASA Earthdata` (sólo con `--descargar`): revise el
  `.netrc` o la variable `EARTHDATA_TOKEN`. No pegue la contraseña en ningún archivo
  del curso.

**(g)** Evaluación de dos complementos de QGIS: GEDIMetrics y GEDI-Pipeline (EN QGIS;
necesitan red y la cuenta de NASA Earthdata del equipo). Los dos bajan el granulo
completo antes de recortar: si la red es lenta, se trabaja con la salida que deja el
docente.

- **GEDIMetrics** (Complementos > GEDIMetrics). Use una capa que tenga **sólo** el
  polígono de B_CONCORDIA: la opción «Selected features only» sólo achica el
  rectángulo de búsqueda y el recorte se hace con todos los polígonos de la capa.
  Pestaña General: L2A y L4A, versión 003, fechas 2019.07.16 a 2019.07.17 (la pasada
  con alturas de más de 50 m). Pestaña Filters: anote los valores por defecto
  (sensibilidad 0,90) y relájelos (calidad 0, sin sensibilidad, degradadas incluidas,
  superficie All) para que exporte todas las huellas. Pestaña Variables: agregue
  `solar_elevation`, `num_detectedmodes` y `worldcover_class`. Pestaña Output: unión
  externa (outer join) y GeoPackage.
- Compare la capa que deja GEDIMetrics con la capa `gedi_l2a` de
  `lidar_B_CONCORDIA.gpkg`: ¿están las mismas huellas (`shot_number`)? Aplique los
  filtros por defecto del complemento y después los del curso, y cuente las válidas
  y las que tienen `rh98` mayor que 50 m. Mire en qué clase de WorldCover caen esas
  huellas y qué biomasa (`agbd`) les da el L4A.
- **GEDI-Pipeline** (Complementos > GEDIPipeline > Download GEDI Data). Producto
  `GEDI01_B`, versión `002`, las mismas fechas y la misma capa; en Optional, los haces
  de potencia `BEAM0101,BEAM0110,BEAM1000,BEAM1011`. Deja las formas de onda crudas
  (`rxwaveform`) de cada huella. Compare la forma de onda de una huella válida con
  `rh98` mayor que 50 m con la de una de 20 a 30 m.

Salida: `lidar_granulos_B_CONCORDIA.csv`, `lidar_conteo_B_CONCORDIA.csv` (en
`04_Tablas`) y `lidar_B_CONCORDIA.gpkg` (en `03_Vectores`).

---

## Paso 6 — Lo que se consigue por pedido (SE CORRE + planilla a mano)

**(a)** Hay bandas que no se bajan con un programa: banda P de BIOMASS (ESA MAAP:
se busca sin cuenta, se baja con una ficha de 90 días), banda L de SAOCOM (CONAE,
con registro, pedido y cuota), banda S de NISAR (Bhoonidhi, ISRO) y de NovaSAR-1
(CSIRO), banda X de COSMO-SkyMed (pedido institucional CONAE–ASI). El script busca
BIOMASS en el catálogo STAC de ESA MAAP (niveles 1a, 1b, 1c y 2a) y suma la planilla
que el grupo llena a mano con lo que pidió o consultó en los otros portales.
La consulta de ALOS-2 PALSAR-2 (ASF y G-Portal de JAXA) la deja hecha el docente con
`00_COMUN\09_Herramientas\des_tp1_alos2.py`, en
`05_Resultados/04_Tablas/alos2_consulta_B_CONCORDIA.csv`: el grupo pasa a la planilla
la escena que cubra el sitio, con `resultado = en catalogo` si no se bajó.

**(b)** Miniforge Prompt, los portales en el navegador y una planilla de cálculo.

**(c)** Primera corrida (crea la planilla si no existe):

```
python Tp1_06_escenas_por_pedido.py --sitio B_CONCORDIA
```

Ventana por defecto de BIOMASS: `--desde 2025-12-01 --hasta 2026-12-31`. BIOMASS
publica sobre Concordia desde el 23/11/2025: para no perder esos productos, corra con
`--desde 2025-11-01`.

Después abra `Tp1_Convergencia\04_Tablas_de_trabajo\escenas_por_pedido.csv` (con
LibreOffice Calc o Excel, separador coma, codificación UTF-8) y complete **una fila
por escena pedida o consultada, aunque no se haya obtenido**. Columnas obligatorias:
`sensor, banda, lambda_cm, portal, producto, escena, fecha, hora_utc, pasada,
polarizaciones, pixel_m, sitio, resultado, fecha_pedido, observaciones`. En
`resultado` va una de estas: `obtenida`, `en catalogo`, `pedida`, `sin cobertura`,
`sin acceso`. Columna optativa `pixeles_validos_%`: el porcentaje del sitio con dato
de la escena (medido en QGIS o con `Tp1_02`); si es menor que 50, `Tp1_07` deja la fila
fuera de la matriz y lo informa, igual que en el inventario local. Deje la fila `EJEMPLO`: el programa la ignora. Guarde en CSV y corra de
nuevo la misma orden.

**(d)** El bloque de BIOMASS con el número de productos por colección
(`BiomassLevel1a`, `1b`, `1c`, `2a`) y la lista (con `--descargar` y sin ficha
aparece además `Sin BIOMASS_TOKEN: solo se BUSCA, no se descarga.`). Después:
`N filas cargadas por el grupo; M incompletas (sin fecha o sin resultado)` y una
línea `INCOMPLETA:` por cada fila sin fecha o sin resultado.

**(e)** Controles: cero filas incompletas. Si la consulta a ESA MAAP falla, el script
agrega una fila con `resultado = consulta fallida` y el error: déjela, es información.

**(f)** Errores típicos:

- Guardar la planilla como `.xlsx` o con punto y coma: el programa no la lee. Debe
  ser CSV con coma.
- Borrar o renombrar una columna: `ERROR: a la planilla le faltan las columnas ...`
  y la planilla no se usa.
- Anotar sólo lo que se consiguió. La columna `resultado` existe para las ausencias.
- Escribir la ficha de ESA MAAP en la planilla o en el script. Va en
  `set BIOMASS_TOKEN=...` y `set BIOMASS_CLIENT_SECRET=...`, en la ventana.

Salida: `05_Resultados/04_Tablas/planilla_por_pedido_B_CONCORDIA.csv`.

**(g) La banda L antes y durante la crecida (SE CORRE).** Los SAOCOM que entregó CONAE y el ALOS-2 se usan, no sólo se anotan. Están en `02_Subsets_SNAP_QGIS\SAOCOM_gamma0` y `ALOS2_gamma0` (`.dim` para SNAP, GeoTIFF para QGIS y RGB HH–HV–HH/HV). El par antes–después de la banda L es el SAOCOM TNA del 10/10/2023 (antes) y el del 11/11/2023 (durante): mismo haz y misma órbita. Los TNB del 31/10 y el 08/11 cubren la mitad oeste y son los dos de la crecida.

```
python Tp1_06b_banda_L_antes_despues.py
```

Lo que hace: describe las seis escenas de banda L (haz, incidencia, píxeles con dato, γ⁰ en tierra y en agua permanente) y mide el cambio después menos antes en tres pares de la misma geometría (L TNA 10/10→11/11, L TNB 31/10→08/11 y C Sentinel-1 23/10→04/11), en la tierra, en el agua de crecida de banda C del 04/11 (Tp6) y por clase de MapBiomas 2023.

La máscara de agua de crecida del 04/11/2023 (banda C y óptico) es un insumo **YA VIENE HECHO** del Tp6: el alumno la construirá el miércoles. Si falta, el script lo dice y termina.

Controles: los TNA y el ALOS-2 cubren el 100 % del sitio y los TNB, cerca del 51 %. En la zona inundada, la banda L (par TNA) y la banda C quedan las dos unos 2,5 dB por debajo del cambio general de su par. Para la banda C esa comparación es circular (la zona sale de su propia máscara); la prueba independiente es el agua del óptico que la C no marcó: ahí la L queda 2,7 dB abajo y la C sólo 0,7 dB. Las dos bandas, comparadas por separado, marcan la misma zona: es sinergia, no fusión de decisión.

Errores típicos: comparar un TNA con un TNB como antes y después; leer como agua la franja azul del borde de los TNB (ruido del extremo del haz); comparar en dB el ALOS-2 con el SAOCOM (su nivel absoluto queda unos 4 dB bajo).

Salida: `B_CONCORDIA_banda_L_escenas.csv` y `B_CONCORDIA_antes_despues_por_zona.csv` (en `04_Tablas`), tres figuras en `05_Graficos\Figuras_del_desarrollo` y una muestra para Orange en `08_Orange\datos\B_CONCORDIA_antes_despues_muestra.csv`.

---

## Paso 7 — Matriz y grado de convergencia (SE CORRE)

**(a)** Se reúnen las planillas de los pasos 2 a 6 del sitio, **sólo con escenas
verificadas**: `candidata` en el Planetary Computer; píxeles válidos ≥ 50 % en el
inventario local (o huella ≥ 50 % en los productos todavía en geometría de radar);
huella ≥ 50 % en ASF; `obtenida` o `en catalogo` en las escenas por pedido (y
`pixeles_validos_%` ≥ 50 si la columna está llena); y los
granulos LiDAR sólo si el conteo dio al menos una huella válida. Con eso se arma la
matriz sensor × fecha y se asigna el grado de convergencia alrededor del evento.

**(b)** Miniforge Prompt.

**(c)**

```
python Tp1_07_matriz_convergencia.py --sitio B_CONCORDIA --evento 2023-11-04 --ventana 12
```

`--ventana` son los días a cada lado del evento (por defecto 12). Sin `--evento`, el
script arma la matriz y la figura pero no asigna grado.

**(d)** `Escenas verificadas reunidas: N`; una línea por banda con número de fechas,
primera y última; las escenas a ±12 días del evento con su distancia en días; y la
línea final `GRADO: ... -> ...`.

Reglas del grado (las del código):

| Dentro de la ventana hay… | Grado | Uso en el curso (orientativo) |
|---|---|---|
| óptico + 2 o más bandas SAR + LiDAR | completa | fusión a nivel de píxel o de rasgo |
| óptico + al menos 1 banda SAR | parcial | sinergia o fusión a nivel de decisión |
| 2 o más bandas SAR sin óptico | parcial (sin óptico) | sinergia SAR multibanda; buscar el óptico antes de fusionar |
| óptico solo, o una sola banda SAR | un solo sensor cerca del evento | mapa de ese sensor; los demás datos, sólo para interpretar (sin fusión) |
| nada (todas las escenas verificadas caen fuera de la ventana) | histórica | sólo interpretación de cambios de largo plazo |
| ninguna escena verificada | sin datos | declarar y cambiar de sitio o fecha |

**(e)** Controles:

- Con ± 12 días el grado **no puede** salir «completa» para el 04/11/2023: hay óptico,
  banda C y banda L (SAOCOM y ALOS-2), pero GEDI estaba en receso y el ATL08 válido
  más cercano es del 12/10/2023, a 23 días. Si sale, algo entró sin estar
  verificado: revise la columna `fuente` de la matriz.
- El grado dice qué familias de sensores convergen; la columna de uso es orientativa.
  La fusión se decide par por par con fecha, soporte, geometría y calidad.
- La NovaSAR 47942 (39 % del sitio con dato) **no entra** a la matriz de Concordia:
  la regla pide 50 %. Es correcto, y es materia de la pregunta 4.
- Abra `05_Graficos/linea_tiempo_B_CONCORDIA.png`: una fila por banda (Óptico, SAR X,
  C, S, L, P, LiDAR), la línea naranja del evento y, al pie, la cita de fuentes.

**(f)** Errores típicos:

- Matriz vacía: no se corrieron los pasos 3 a 6 con **el mismo** `--sitio`. Los
  nombres de las planillas llevan el sitio.
- Cambiar `--ventana` hasta que el grado «mejore» sin declararlo. La ventana es una
  decisión del analista y se justifica por la duración del fenómeno (una crecida
  dura semanas; un incendio de pastizal, días).

Salida: `matriz_convergencia_B_CONCORDIA.csv`, `grado_convergencia_B_CONCORDIA.csv`
(en `04_Tablas`) y `linea_tiempo_B_CONCORDIA.png` (en `05_Graficos`).

---

## Paso 8 — Control cruzado (AUXILIAR)

**(a)** El control del Tp1 (diapositiva 24): otro grupo repite la búsqueda y obtiene
las mismas escenas. Si no las obtiene, uno de los dos filtró distinto, y hay que
encontrar cuál.

**(b)** Entre grupos, con las planillas de `05_Resultados/04_Tablas/`.

**(c)** Intercambie con el grupo vecino `planilla_MPC_B_CONCORDIA.csv`,
`planilla_ASF_B_CONCORDIA.csv` y `matriz_convergencia_B_CONCORDIA.csv`. Compare la
columna `id` (Planetary Computer) y `nombre` (ASF), no las fechas.

**(d)** Coincidencia total, o diferencias que se pueden explicar (otra ventana, otro
`--nubes_max`, una escena cuya lectura falló en un equipo y no en el otro).

**(e)** Se anota en la tabla de `01_Prompt_IA/04_Verificacion/verificacion_resultados.md`.

**(f)** Comparar sólo fechas: el mismo día puede haber dos teselas Sentinel-2 o dos
cortes de Sentinel-1.

---

## Paso 9 — Contexto del sitio: MapBiomas, CCI Biomass y banda P (SE CORRE + EN QGIS y ORANGE)

**(a)** La matriz del paso 7 dice qué sensores convergen en la fecha del evento. Este
paso ubica el evento en la historia del sitio con tres productos que ya están en
`02_Subsets_SNAP_QGIS\QGIS_GeoTIFF` y que no entran a la matriz porque resumen años o
son de 2026: MapBiomas (cobertura 1985–2025, pérdida de vegetación 1987–2025 y área
quemada 1999–2025), el CCI Biomass (biomasa aérea 2010–2024) y BIOMASS en banda P
(γ⁰ HH y VH del 22/07/2026 y altura del bosque L2A de julio de 2026). Como cruzada de
P se usa la **VH**: la HV del producto trae interferencia de radiofrecuencia (RFI),
emisiones de radares y comunicaciones terrestres que comparten los 435 MHz, que ESA
detectó pero no corrigió (en los metadatos, `rfiDetectionFlag = true` y
`rfiCorrectionFlag = false`). En la retrodispersión de un radar monoestático la HV y
la VH miden lo mismo (reciprocidad); la VH se usa porque no muestra el bandeamiento, y eso no prueba que esté libre de RFI.

**(b)** Miniforge Prompt, QGIS y Orange.

**(c)**

```
python Tp1_08_contexto_del_sitio.py --sitio B_CONCORDIA
```

En QGIS, `Capa > Añadir capa > Añadir capa ráster...` y elija
`02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\B_CONCORDIA_MapBiomas_cobertura_1985_2025.tif`: el
estilo `.qml` de al lado se carga solo, con la leyenda oficial, sobre la banda 41
(2025). En `Propiedades > Simbología` cambie la banda a la 1 (1985) y a la 39 (2023,
el año del evento) y compare. Lo mismo con `..._MapBiomas_perdida_veg_1987_2025.tif`
(banda 21 = 2007) y con `..._fuego_frecuencia_1999_2025.tif` (`Pseudocolor monobanda`
de 1 a 6). El RGB de la banda P está en
`RGB_copol_cruzada_cociente\B_CONCORDIA_BIOMASS_P_20260722_RGB_8bit.tif` (R = HH,
G = VH, B = HH/VH). En Orange abra `08_Orange\Tp1_F_contexto_del_sitio.ows`.

**(d)** Tarda unos 6 s. La bitácora informa:

- `MapBiomas cubre 117817 ha de 168978 (69.7 %)`: la margen uruguaya queda fuera.
- La cobertura de 1985 y de 2025 por clase: herbáceas de 53,1 a 32,0 %, silvicultura
  de 14,7 a 24,2 %, cultivos perennes (cítricos) de 5,6 a 12,1 %.
- La pérdida de vegetación 1987–2025 (38.604 ha de primaria y 31.724 ha de
  secundaria; años con más pérdida: 2007, 2008 y 2005).
- El área quemada 1999–2025: 24.765 ha acumuladas; quemado al menos una vez, el
  16,3 % del área con dato.
- `Altura FH: se enmascara el agua de MapBiomas 2025 (clases 26, 31 y 33) o JRC ocurrencia >= 50 % (10.8 % de los pixeles con FH)`.
- Una tabla por clase de 2025 con las medianas del CCI 2020 y 2024, la altura FH (sin
  agua) y su calidad, y P HH y P VH en dB.

La altura FH se mide **sin agua**: antes de resumirla, el programa deja sin dato los píxeles de 90 m con más de la mitad de agua en MapBiomas 2025 (clases 26, 31 y 33) o con ocurrencia de agua JRC de 50 % o más (función `mascara_agua` de `00_COMUN/funciones_comunes.py`). Sobre el agua el algoritmo de altura trabaja fuera de su dominio forestal y da 24 m; la causa no se resuelve aquí: sin la máscara, el lago de Salto Grande sale con 24 m y cualquier conclusión sobre la FH queda dominada por el agua. En `QGIS_GeoTIFF` está ya enmascarada: `..._FH_<fechas>_sin_agua.tif` (banda 1 altura, banda 2 calidad, banda 3 máscara).

Salidas: `05_Resultados/04_Tablas/B_CONCORDIA_mapbiomas_area_por_clase_y_anio.csv`,
`..._mapbiomas_perdida_por_anio.csv`, `..._mapbiomas_fuego_por_anio.csv`,
`..._contexto_por_clase.csv`, `..._contexto_pixeles_muestra.csv` y, en `05_Graficos`,
`..._mapbiomas_area_por_clase.png` y `..._mapbiomas_perdida_y_fuego_por_anio.png`.

**(e)** Controles:

- Silvicultura y bosques: CCI alto (69 a 87 Mg/ha de mediana) y P VH alta (−13,5 a
  −17 dB); herbáceas, cultivos temporarios y agua: CCI 0 y P VH baja (−22 a −29 dB).
- La altura FH de BIOMASS, con el agua enmascarada, no pasa el control: da 3,5 m de
  mediana en la silvicultura (eucaliptos de más de 20 m), 5,0 m en los bosques cerrados
  y 7,1 m en las herbáceas. En la tabla, la clase de ríos y lagos sale sin FH (raya).
  En este sitio no se usa.
- La pérdida de 2025 sale casi nula: MapBiomas confirma la pérdida con los años
  siguientes, y el último año siempre queda bajo.

**(f)** Errores típicos:

- Tomar MapBiomas como verdad: es una clasificación de Landsat de 30 m. Un año con un
  salto de clases (en 2007 los cultivos perennes pasan a 20.552 ha y en 2015 vuelven a
  13.521) es ruido de la clasificación, no un cambio del paisaje.
- Usar la HV de BIOMASS como cruzada.
- Comparar el CCI con el radar del curso como si fueran independientes: el CCI se
  estimó con radar C y L.

---

## Paso opcional — Repetir para la fecha del curso

Si sobra tiempo, repita los pasos 3 a 7 con la ventana de 2026, donde sí hay NISAR
banda L sobre Concordia (`configuracion_comun.py` registra un NISAR descendente del
18/09/2026 y un Sentinel-2A del 16/09/2026, verificados):

```
python Tp1_03_buscar_optico_y_C.py --sitio B_CONCORDIA --desde 2026-09-01 --hasta 2026-09-30
python Tp1_04_buscar_asf.py --sitio B_CONCORDIA --desde 2026-09-01 --hasta 2026-09-30
python Tp1_05_buscar_lidar.py --sitio B_CONCORDIA --desde 2026-09-01 --hasta 2026-09-30
python Tp1_07_matriz_convergencia.py --sitio B_CONCORDIA --evento 2026-09-18 --ventana 12
```

Las planillas llevan el nombre del sitio, no el de la ventana: **antes** de esta
segunda corrida copie las de 2023 a una subcarpeta (por ejemplo
`05_Resultados\04_Tablas\evento_2023\`), o se van a sobrescribir.

---

## Al terminar

Revise que en `05_Resultados/06_Control_calidad/` haya una bitácora `.log` por cada
script corrido. Cada una termina con `SIGUIENTE PASO:` y la ruta donde se guardó.
Conteste `07_Preguntas_y_entrega/preguntas.md` citando el archivo de cada cifra.
