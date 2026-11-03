# Tp7 — Guía paso a paso

Jueves, 9 a 13 h. Sitio `E1_DIAMANTE_BARRANCA`. Grilla común EPSG:32721 (UTM 21 S),
10 m para la interferometría y 30 m para los volúmenes.

Antes de empezar, en el **Miniforge Prompt**:

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp7_Barrancas_deslizamientos\03_Scripts
```

Deje esa ventana abierta toda la mañana. Todas las órdenes de esta guía se
escriben ahí.

Distribución sugerida del tiempo:

| Horario | Paso |
|---|---|
| 9:00–9:20 | Paso 1. Pares Sentinel-1 (banda C) |
| 9:20–11:00 | Paso 2. Desenrollado de la banda X en SNAP |
| 11:00–11:30 | Paso 3. Coherencia, desplazamiento y fusión de decisión |
| 11:30–12:30 | Pasos 4 y 5. Cicatriz, depósito y volumen |
| 12:30–13:00 | Paso 6. Control del MDE con ICESat-2 y preguntas |

**Landsat 8 y 9.** Escenas de este práctico, la pasada más cercana a cada Sentinel-2 con el sitio cubierto y despejado: Diamante, `E1_DIAMANTE_BARRANCA_L8_20181025`: Landsat 8 del 25/10/2018 para el Sentinel-2 del 19/10/2018. El Sentinel-2 del 04/10/2018 no tiene Landsat: ninguna pasada a 16 días o menos cubría el sitio despejado (en 2018 no existía Landsat 9).

Son Colección 2, Nivel 2 de USGS (reflectancia y temperatura de superficie, píxel de 30 m), bajadas del Planetary Computer. Están en `02_Subsets_SNAP_QGIS\SNAP_DIMAP` y `QGIS_GeoTIFF`, con las bandas `SR_B1` a `SR_B7` (reflectancia), `ST_B10` (temperatura, K), `ST_QA`, `QA_PIXEL` y las virtuales `NDVI` y `ST_B10_C` (°C).

Landsat 9 da imágenes desde el 31/10/2021; antes sólo hay Landsat 8. Los dos llevan instrumentos gemelos (OLI y TIRS) y se comparan entre sí sin ajuste. Con Sentinel-2 no: el píxel es de 30 m contra 10 y 20 m, y las bandas no coinciden del todo (el infrarrojo cercano de Landsat, 865 nm, equivale a la B8A, no a la B08).

Fuente: USGS / NASA, Landsat 8 y Landsat 9 OLI/TIRS, Colección 2 Nivel 2, distribuido por Microsoft Planetary Computer, https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2

**Fusión Landsat + Sentinel-2.** El Landsat también viene afinado a 10 m con el detalle espacial del Sentinel-2 de la fecha más cercana: se lo interpola a la grilla de 10 m y se le suma el detalle fino de la banda Sentinel-2 de 10 m que más se le parece, escalado por una regresión entre los dos sensores (filtro pasa-altos con modulación por regresión, HPF). Trae las bandas `SR_B1` a `SR_B7` en reflectancia, `mascara_detalle` (1 = se agregó detalle; 0 = nube, sombra o falta de dato en alguna de las dos) y el `NDVI` virtual; el método y la calidad de cada banda están en los metadatos.

El control es el ERGAS: la imagen afinada se lleva de nuevo a 30 m y se compara con el Landsat original; por debajo de 3 la fusión es buena. Sirve para mirar e interpretar, con tres cuidados: un cambio real entre las dos fechas aparece como detalle falso; las bandas 6 y 7 (infrarrojo de onda corta) toman el detalle de una banda de 10 m de otra región del espectro y son las menos confiables; y la temperatura no se afina.

En este práctico: `E1_DIAMANTE_BARRANCA_L8_20181025_fusion_S2_20181019_10m`: 6 días entre las dos imágenes; ERGAS 1,70. El frente de la barranca es más angosto que el píxel de 30 m: lo que se ve más nítido viene del Sentinel-2.

**Pléiades y Pléiades Neo de CONAE.** Referencia visual de muy alta resolución del casco urbano (Pléiades, 0,5 m; Pléiades Neo, 0,3 m), 2022-2023, del proyecto Impactar de CONAE. Es un servicio de mapas y necesita internet: en `02_Subsets_SNAP_QGIS\Pleiades_CONAE_WMS` hay un `.xml` por localidad que se arrastra a QGIS (instrucciones en el `LEEME.md` de esa carpeta). Sirve para mirar y digitalizar, no para calcular: es RGB color real, sin infrarrojo ni reflectancia, y la fecha exacta no está publicada, sólo el año.

En este práctico: Diamante, Pléiades 2022 (`Diamante_2022_Pleiades_CONAE.xml`), y Gran Paraná, Pléiades 2022 (`GranParana_2022_Pleiades_CONAE.xml`).

Fuente: CONAE, proyecto Impactar; Pléiades y Pléiades Neo, Airbus Defence and Space. Servicio WMS: https://geotematico01.conae.gov.ar/geoserver/wms; catálogo: https://catalogos.conae.gov.ar/catalogo/catalogoGeoServiciosOGC.html

**CBERS-4A, cámara WPM (INPE).** Pancromática de 2 m y multiespectral de 8 m (azul, verde, rojo e infrarrojo cercano), producto L4 ortorrectificado, en números digitales. Cada escena viene en dos productos: `..._MS_8m` (las cuatro bandas originales) y `..._pansharpened_2m` (la pancromática y las cuatro bandas afinadas a 2 m por Brovey ponderado, el método por defecto de GDAL). Es un pansharpening clásico: pancromática y multiespectral del mismo satélite y del mismo instante; compárelo con la fusión Landsat + Sentinel-2, que combina dos sensores y dos fechas. El control es el mismo ERGAS (por debajo de 3, bueno). Los números digitales no son reflectancia y el Brovey altera la radiometría: sirve para mirar y digitalizar, no para calcular índices. Cubre una zona de 12 a 21 km, no el sitio entero, y la escena se eligió a ojo, sin nubes, porque el catálogo del INPE no informa la nubosidad.

En este práctico: Diamante, `E1_DIAMANTE_BARRANCA_CBERS4A_DIAMANTE_20260926_...`: 26/09/2026, la ciudad y la barranca; ERGAS 1,71.

Fuente: INPE / CAST, CBERS-4A WPM L4, licencia CC BY 4.0. Catálogo STAC del INPE, colección CB4A-WPM-L4-DN-1, https://data.inpe.br/stac/browser/collections/CB4A-WPM-L4-DN-1

**Embeddings anuales AlphaEarth Foundations (Google y Google DeepMind).** 64 números por píxel de 10 m que resumen un año entero de Sentinel-1, Sentinel-2, Landsat, GEDI, clima y otras fuentes, aprendidos por un modelo de inteligencia artificial. Las dimensiones (`A00` a `A63`) no tienen significado físico propio: sirven para clasificar con pocas muestras, buscar zonas parecidas y detectar cambios entre años. Vienen en enteros de 8 bits tal como los entrega Google (`..._AlphaEarth_embeddings_<año>_10m`); para pasarlos a valores reales, valor = signo(DN) × (DN / 127,5)², y −128 es sin dato. El `..._CP1_CP2_CP3_RGB_8bit.tif` muestra las tres primeras componentes principales para mirar en QGIS; sus colores no tienen significado fijo. Resumen un año, no una fecha; 2026 todavía no existe y se usa 2025, el último.

En este práctico: Diamante, 2018 y 2025.

Fuente: The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind (CC BY 4.0). Copia en Source Cooperative (Taylor Geospatial), https://source.coop/tge-labs/aef

---

## Paso 0. Comprobar que el entorno y los datos están

**Qué y por qué.** Los scripts leen las rutas de `00_COMUN\configuracion_comun.py`.
Si una carpeta de datos no existe, conviene saberlo ahora y no a las 11.

**Orden:**

```
python ..\..\00_COMUN\configuracion_comun.py
```

**Qué debe observar.** La carpeta de práctica, la de originales y la grilla de cada
sitio. La línea de `E1_DIAMANTE_BARRANCA` dice `kml_COSMO (-60.71, -32.135, -60.575, -32.015)`.

**Control.** Abra el Explorador de archivos y confirme que existen:

- `F:\HFdV COURSES\CEREGEO\2018\TelSAR\DIAMANTE\GRIETAS\barranca-periferia_Polygon.shp`
- la carpeta `...\InSAR HI\` del curso 2023 con el producto `*_Stack_ifg_dinsar_flt_TC.dim`;
- la carpeta de HyP3 `...\08_Originales_crudos\HYP3\E1_DIAMANTE_BARRANCA\`.

**Error típico.** El disco del curso montado con otra letra. Se corrige con las
variables de entorno, sin tocar el código:

```
set CURSO_SAR_COSMO=G:\HFdV COURSES\CEREGEO\2018\TelSAR\DIAMANTE
set CURSO_SAR_ORIGINALES=G:\ORIGINALES
```

(valen sólo para esa ventana del Miniforge Prompt).

---

## Paso 1. Pares interferométricos en banda C (Sentinel-1)

**Qué y por qué.** La interferometría mide la diferencia de fase entre dos tomas
de la misma órbita. Tres condiciones la hacen confiable:

- **separación temporal corta** (6 a 24 días; en 2018 volaban Sentinel-1A y 1B, pero sobre Diamante sólo hay adquisiciones cada 12 días, órbita 141, descendente): la vegetación y la humedad cambian
  menos, y se conserva la coherencia;
- **línea de base perpendicular chica** (< 150 m): menos fase topográfica residual
  si el MDE tiene errores;
- **misma órbita relativa y misma pasada**: la geometría de visión es la misma.

**Dónde.** Miniforge.

**Orden (por defecto busca entre el 15/09 y el 15/11/2018):**

```
python Tp7_01_pares_insar_C.py
```

Argumentos y valores por defecto: `--desde 2018-09-15`, `--hasta 2018-11-15`,
`--dias_max 24`, `--base_max 150`, `--hyp3 0` (no pide nada a HyP3).

**Qué debe observar.** Los criterios y el período de búsqueda (quedan escritos al principio de la bitácora), el número de escenas SLC sobre el sitio, las escenas por órbita
relativa y pasada (ascendente o descendente), y una tabla con los pares aptos
ordenados por días y línea de base. Se guarda en
`05_Resultados/04_Tablas/E1_pares_S1.csv` (columnas `orbita`, `pasada`,
`fecha_1`, `fecha_2`, `dias`, `base_perpendicular_m`, `apto`, `escena_1`, `escena_2`).

**Control.**

1. Abra el CSV. Elija el par apto que **cubra el 15–19/10/2018** o quede lo más
   cerca posible.
2. Anote su **pasada**. Compárela con la del par COSMO-SkyMed (está en los
   metadatos del producto, en SNAP: `Metadata > Abstracted_Metadata > PASS`). Si
   las pasadas difieren, el desplazamiento en la línea de visión de una banda
   puede tener el **signo opuesto** al de la otra para el mismo movimiento real
   (ver Paso 3). Prefiera un par Sentinel-1 de la misma pasada que el COSMO.

**El pedido a HyP3 (YA VIENE HECHO).** El docente corrió antes del curso:

```
python Tp7_01_pares_insar_C.py --hyp3 1
```

que pide el mejor par al procesador GAMMA de ASF (`looks="10x2"`, mapas de
desplazamiento, ángulo de incidencia y máscara de agua) y lo baja a
`00_COMUN\08_Originales_crudos\HYP3\E1_DIAMANTE_BARRANCA\<producto>\`. Los `.zip` (y su carpeta descomprimida) traen `*_corr.tif`
(coherencia), `*_unw_phase.tif`, `*_los_disp.tif` y `*_vert_disp.tif`. Pide la
cuenta de NASA Earthdata (desde `.netrc` o por teclado; nunca se escribe en un
archivo del curso) y consume créditos gratuitos. Tarda de 30 minutos a horas: por
eso no se hace en clase.

**Errores típicos.**

- `Escenas SLC sobre el sitio: 0`: sin red hacia ASF, o fechas mal escritas
  (formato `AAAA-MM-DD`).
- `no se pudo pedir la pila de lineas de base`: ASF no respondió la consulta de
  la pila. La columna `base_perpendicular_m` queda vacía y el par se marca apto
  sólo por los días. Declárelo.
- Si el par elegido por usted no coincide con el que pidió el docente a HyP3,
  use el de HyP3 y explique la diferencia.

---

## Paso 2. Desenrollar la fase de la banda X en SNAP (EN SNAP)

**Qué y por qué.** El interferograma da la fase **envuelta**, entre −π y +π. Un
ciclo completo en banda X equivale a λ/2 = 1,56 cm de desplazamiento en la línea
de visión. Para saber cuántos ciclos hay que sumar se **desenrolla** la fase; en
SNAP se hace con el programa externo SNAPHU.

El producto del curso 2023 (`*_Stack_ifg_dinsar_flt_TC.dim`) tiene la banda
`Unw_Phase_ifg_*` **toda en cero**: el desenrollado se exportó pero nunca se
importó. Un cero no es «sin deformación»: es una banda vacía. El script del paso
3 lo detecta y lo dice en la bitácora.

**Condición previa importante.** SNAPHU trabaja en **geometría de radar**. El
producto `..._TC` ya está ortorrectificado (TC = Terrain Correction) y **no
conviene desenrollarlo**: SNAPHU está pensado para geometría radar. Si no está el
producto sin `_TC`, puede desenrollarse el `_TC` como alternativa de menor calidad
(así se hizo en el Desarrollo del docente, con SNAPHU desde Python). Busque en la carpeta `InSAR HI` el producto previo, sin `_TC`
(`*_Stack_ifg_dinsar_flt.dim`: interferograma con la fase topográfica restada y
filtrado con Goldstein). Si no está, hay que rehacer la cadena stripmap desde las
dos Himage (ver `09_Grafos_SNAP/LEEME_grafos.md`, cadena B): lleva más de una hora.

### 2.1 Abrir y recortar

1. `File > Open Product...` → el `.dim` sin `_TC`.
2. En `Product Explorer`, despliegue `Bands`: debe ver `i_ifg_*`, `q_ifg_*`,
   `Phase_ifg_*` y `coh_*`.
3. Abra `Phase_ifg_*` (doble clic). Debe ver franjas de colores (el ciclo de fase)
   y ruido sobre el río.
4. Recorte a la barranca para que SNAPHU tarde minutos y no horas:
   `Raster > Subset...`, pestaña `Spatial Subset`, ajuste el rectángulo a la
   barranca y unos 2 km alrededor (incluya tierra firme estable, que será la
   referencia). En `Band Subset` deje todas. Guarde con `File > Save Product`
   en una carpeta **sin espacios ni tildes**, por ejemplo `D:\Tp7\X_subset.dim`.

### 2.2 Snaphu Export

`Radar > Interferometric > Unwrapping > Snaphu Export`

- `I/O Parameters`: fuente = el subset; `Target folder` = `D:\Tp7\snaphu`
  (sin espacios ni tildes).
- `Export`:
  - `Statistical-cost mode`: **DEFO** (deformación; TOPO se usa para MDE).
  - `Initial method`: **MCF**.
  - `Number of Tile Rows` y `Number of Tile Columns`: 1 y 1 para un subset chico
    (si el recorte supera unos 3 000 × 3 000 píxeles, use 2 × 2 o más).
  - `Number of Processors`: los núcleos de su máquina menos uno.
  - `Row Overlap`, `Column Overlap`: deje los valores por defecto (sólo importan
    si hay más de una tesela).
- `Run`.

**Qué debe observar.** En `D:\Tp7\snaphu\` una carpeta con el nombre del producto que
contiene `snaphu.conf`, `Phase_ifg_*.snaphu.img`, `coh_*.snaphu.img` y
`UnwPhase_ifg_*.snaphu.hdr` (el encabezado vacío que espera el resultado).

### 2.3 Correr snaphu fuera de SNAP

1. Abra `snaphu.conf` con el Bloc de notas. En las primeras líneas (comentadas
   con `#`) está la orden exacta, del tipo
   `snaphu -f snaphu.conf Phase_ifg_<...>.snaphu.img <ancho>`.
2. Abra una ventana de órdenes (`cmd`) y vaya a esa carpeta:
   `cd /d D:\Tp7\snaphu\<carpeta_del_producto>`.
3. Pegue la orden. Si `snaphu` no está en el `PATH`, escriba la ruta completa del
   ejecutable, por ejemplo `C:\snaphu\bin\snaphu.exe -f snaphu.conf ...`.

**Qué debe observar.** SNAPHU imprime el avance (`Building cost arrays`, `Solving`,
`Writing output`) y al final aparece `UnwPhase_ifg_*.snaphu.img`. En un recorte
chico tarda de uno a pocos minutos.

**Errores típicos.**

- `'snaphu' no se reconoce como un comando`: falta el ejecutable o el `PATH`.
- Termina en segundos sin escribir el `.img`: la carpeta tiene espacios o tildes
  (`IMÁGENES`, `HFdV COURSES`). Repita con `D:\Tp7\...`.
- Tarda horas: el recorte es demasiado grande. Vuelva a 2.1.

### 2.4 Snaphu Import

`Radar > Interferometric > Unwrapping > Snaphu Import`

- Pestaña `1-Read-Phase`: el producto **envuelto** (`D:\Tp7\X_subset.dim`).
- Pestaña `2-Read-Unwrapped-Phase`: `D:\Tp7\snaphu\<carpeta>\UnwPhase_ifg_*.snaphu.hdr`.
- Pestaña `3-SnaphuImport`: puede marcar `Do NOT save Wrapped interferogram in the target product`.
- Pestaña `4-Write`: `D:\Tp7\X_unw.dim`. `Run`.

**Qué debe observar.** Una banda nueva `Unw_Phase_ifg_*`. Ábrala: ya no hay franjas
que se repiten, sino una superficie continua. **Control:** botón derecho sobre la
banda → `Properties` no alcanza; use `Analysis > Information` y `Analysis >
Statistics` (botón `Refresh`): el mínimo y el máximo **no** deben ser ambos cero.

### 2.5 Fase a desplazamiento y ortorrectificación

`Phase to Displacement` deja en el producto de salida **una sola banda**,
`displacement`: la coherencia no pasa. Por eso el desplazamiento y la coherencia
se ortorrectifican **por separado**, con los mismos parámetros, y salen dos
GeoTIFF.

1. `Radar > Interferometric > Products > Phase to Displacement` sobre `X_unw.dim`.
   Guarde `D:\Tp7\X_disp.dim`. Sale la banda `displacement`, en metros en la
   línea de visión.
2. Ortorrectifique el desplazamiento:
   `Radar > Geometric > Terrain Correction > Range-Doppler Terrain Correction`
   - `I/O Parameters`: fuente = `X_disp.dim`; destino `D:\Tp7\X_disp_TC.dim`.
   - `Processing Parameters` > `Source Bands`: `displacement`.
   - `Digital Elevation Model`: `Copernicus 30m Global DEM` (auto-descarga) o el
     MDE del IGN como `External DEM`.
   - `Map Projection`: EPSG:32721 (`Custom CRS` > `Predefined CRS` > `EPSG:32721`).
   - `Pixel Spacing`: 10 m.
3. Ortorrectifique la coherencia con **los mismos parámetros**, desde el
   recorte que la contiene:
   - fuente = `X_subset.dim`; destino `D:\Tp7\X_coh_TC.dim`;
   - `Source Bands`: `coh_*` (una sola banda).
4. Exporte cada uno a GeoTIFF (`File > Export > GeoTIFF`, sin bandas virtuales):
   - `X_disp_TC.dim` → `02_Subsets_SNAP_QGIS\E1_X_los_disp.tif`;
   - `X_coh_TC.dim` → `02_Subsets_SNAP_QGIS\E1_X_coh.tif`.

**Qué debe observar.** En QGIS, los dos GeoTIFF se superponen exactamente (mismo
píxel de 10 m y misma extensión). Si difieren en extensión no es un problema:
`Tp7_02` lleva cada uno a la grilla del sitio.

**Atajo para la coherencia.** El producto del curso 2023
(`*_Stack_ifg_dinsar_flt_TC.dim`) ya trae `coh_*` ortorrectificada de la escena
completa; sirve igual como `--x_coh` (exportada a GeoTIFF sin bandas virtuales).

**Alternativa equivalente.** Si prefiere no convertir en SNAP, exporte la banda
`Unw_Phase_ifg_*` ortorrectificada y pásela al script con `--x_fase`: el script
calcula `d = −λ · fase / (4π)` con `--lambda_x 0.03123` m, la misma convención de
`Phase to Displacement`.

**Control.** Abra los dos GeoTIFF en QGIS sobre la imagen de muy alta
resolución: la barranca tiene que caer donde está. COSMO-SkyMed mostró en la
presentación 02 desfases de georreferencia respecto de Sentinel-2; si ve uno,
mídalo y anótelo.

---

## Paso 3. Coherencia, desplazamiento y fusión de decisión

**Qué y por qué.**

- **SINERGIA.** Cada banda da SU coherencia y SU desplazamiento. La coherencia
  mide cuánto se parecen las dos tomas: en vegetación cae más rápido cuanto más
  corta es la onda (X = 3,1 cm, C = 5,55 cm), pero la comparación entre bandas también depende de la resolución (2 m frente a 40 m), la polarización y el intervalo: compare dentro de una misma cobertura (MapBiomas). En octubre de 2018 la comparación es
  X frente a C: no hay par en banda L. El desplazamiento de InSAR es
  **relativo**: se refiere a la mediana de una zona que se supone estable.
- **La zona de referencia.** Por defecto, un anillo de 500 m alrededor de la
  ladera **sin el agua**: el script quita los píxeles que el JRC Global Surface
  Water marca como agua al menos el 50 % del tiempo (el Paraná no es estable ni
  coherente). La lectura del JRC necesita conexión; sin ella, la bitácora avisa
  que el anillo puede incluir el río. Con `--zona_estable <gpkg>` se usa, en
  lugar del anillo, un polígono de tierra firme digitalizado por el grupo.
- **FUSIÓN DE DECISIÓN (estricta).** Cada banda decide, píxel por píxel, si hay
  desplazamiento mayor que el umbral (1 cm) con coherencia suficiente (≥ 0,3), y
  con qué signo. Un píxel se decide sólo si **todas** las bandas con
  desplazamiento válido tienen dato coherente allí; si a una le falta, el píxel
  queda sin decidir (sin dato). Se marca +1 o −1 sólo si todas superan el
  umbral con el signo que tendría en su línea de visión el movimiento esperado;
  si no, 0. Una banda vacía (fase desenrollada en cero) no entra a la fusión.
- **LA REGLA DE SIGNO SÓLO VALE CON LA MISMA GEOMETRÍA.** Cada banda mide en su
  línea de visión: el mismo movimiento puede dar signos distintos en dos
  geometrías. Lea la pasada (`Abstracted_Metadata > PASS`), el rumbo y la
  incidencia del COSMO en SNAP y páselos con `--pasada_x --rumbo_x --inc_x`; los
  de HyP3 se leen solos. Con las dos pasadas iguales, el script proyecta en cada
  LOS un movimiento hipotético hacia el ONO (`--mov_azimut 292.5
  --mov_inclinacion 5`) y exige ese signo; si las pasadas difieren o no se
  declaran, informa la coincidencia de detección sin signo. Con los datos del
  curso las dos son descendentes (COSMO incidencia 59,6°, Sentinel-1 38,9°).

**Dónde.** Miniforge.

**Orden** (ejemplo con banda X de SNAP y banda C de HyP3; ajuste los nombres):

```
python Tp7_02_coherencia_y_deformacion.py ^
  --x_desp ..\02_Subsets_SNAP_QGIS\E1_X_los_disp.tif --x_coh ..\02_Subsets_SNAP_QGIS\E1_X_coh.tif ^
  --c_desp ..\..\00_COMUN\08_Originales_crudos\HYP3\E1_DIAMANTE_BARRANCA\S1BB_20181012T092149_20181024T092149_VVP012_INT40_G_weF_AF13\S1BB_20181012T092149_20181024T092149_VVP012_INT40_G_weF_AF13_los_disp.tif ^
  --c_coh  ..\..\00_COMUN\08_Originales_crudos\HYP3\E1_DIAMANTE_BARRANCA\S1BB_20181012T092149_20181024T092149_VVP012_INT40_G_weF_AF13\S1BB_20181012T092149_20181024T092149_VVP012_INT40_G_weF_AF13_corr.tif
```

En la carpeta de HyP3 hay dos productos: `..._AF13` (12/10–24/10/2018, **el que se usa**:
contiene el par X del 15–19/10) y `..._D357` (18/09–30/09/2018, anterior; sirve para ver
si la ladera ya se movía en septiembre).

Argumentos y valores por defecto: `--pixel 10`, `--coh_min 0.3`,
`--umbral_m 0.01`, `--anillo 500`, `--lambda_x 0.03123`, `--lambda_c 0.05547`,
`--lambda_l 0.2350`, `--ladera` (vacío: busca el shapefile en
`COSMO_DIAMANTE\GRIETAS\`), `--zona_estable` (vacío: anillo sin agua). Por banda: `--x_desp`/`--x_fase`/`--x_coh`,
`--c_desp`/`--c_fase`/`--c_coh`, `--l_desp`/`--l_fase`/`--l_coh`.

**Qué debe observar.**

1. La zona de referencia: `Del anillo se quitan N pixeles de agua (JRC, ocurrencia >= 50 %).`
   y `Referencia: anillo de 500 m alrededor de la ladera (N pixeles).` (o, con
   `--zona_estable`, `Referencia: zona estable digitalizada ...`). Sin conexión
   aparece `AVISO: no se pudo leer el JRC (...): el anillo puede incluir el rio.
   Usar --zona_estable.` Después, el polígono de la ladera y sus píxeles.
2. Una línea por banda: coherencia media en la ladera y en la referencia, % de
   la ladera coherente, desplazamiento mediano (mm) y ruido en la referencia (mm).
3. Si el desplazamiento de una banda es cero en todo el sitio, el aviso
   «Eso no es estabilidad: es una banda vacía». Si lo ve con la banda X, el paso
   2 no se completó.
4. Si el ruido en la referencia supera el umbral, el aviso «la detección en esta
   banda no es confiable».
5. `Deformacion confirmada por las 2 bandas: N pixeles en la ladera (M en la referencia).`
6. `Pixeles de la ladera decididos (todas las bandas con dato coherente): N de M.`
   Es la parte de la ladera donde la fusión pudo decidir; el resto quedó sin
   decidir porque al menos una banda no era coherente allí.

Salidas: `05_Resultados/04_Tablas/E1_coherencia_y_desplazamiento.csv`,
`05_Resultados/02_Rasters/E1_deformacion_confirmada.tif` (bandas
`deformacion_confirmada` y `bandas_que_votaron`), y en `04_Tablas_de_trabajo/`
la ladera reparada (`E1_ladera_reparada.gpkg`) y la zona de referencia
(`E1_zona_referencia.gpkg`).

**Control (en QGIS).**

1. Abra `E1_deformacion_confirmada.tif`. Banda 1 con `Simbología > Valores
   únicos` o `Pseudocolor monobanda` de −1 a 1. Como el desplazamiento se refiere
   a la mediana de la referencia, que allí dé 0 es casi circular: corra también
   con `--control_independiente` (referencia en la mitad norte del anillo,
   control en la mitad sur) y mire la línea `Control independiente` de la
   bitácora. **En el control debe dar 0.** Si no, hay atmósfera o una referencia
   mal elegida.
2. Abra `05_Resultados/05_Graficos/E1_histogramas_umbrales.png`: el
   desplazamiento en la referencia de cada banda con la línea de ±10 mm y de
   ±2 NMAD, y la coherencia con la línea de 0,3 (regla 6 del proyecto).
2. Abra la banda 2 (`bandas_que_votaron`): cuántas bandas tenían dato coherente
   en cada píxel. La banda 1 sólo tiene valor donde votaron todas; donde votó
   una sola, queda sin dato. Sirve para ver **dónde** la ladera quedó sin decidir
   y qué banda falta allí (compárela con la coherencia de cada banda).
3. `E1_zona_referencia.gpkg` guarda el anillo completo (el vector); el agua del
   JRC se quita al rasterizarlo. Si la bitácora dio el `AVISO` del JRC, el anillo
   incluye el río: repita con `--zona_estable` y un polígono de tierra firme.
   La «coherencia en la referencia» se promedia sobre esa zona sin filtrar por
   coherencia.
4. Hallazgo con los datos del curso: la coherencia en banda X da **≈ 0,41 en la
   ladera y 0,40 en el anillo de referencia**. No hay contraste: las dos zonas son
   mayormente ciudad. Para comparar las bandas en el monte, use el flujo de
   Orange `08_Orange/Tp7_A` (coherencia por cobertura de MapBiomas).
5. **Zonas de la ladera (EN QGIS).** La ladera relevada es mayormente ciudad y
   diluye la señal. Divídala en escarpa (pendiente del IGN > 30 %), bloque
   (franja de 150 m detrás de la escarpa), pie y ciudad, en
   `04_Tablas_de_trabajo\E1_zonas_ladera.gpkg` (polígonos con el campo `zona`;
   viene uno del docente), y corra `Tp7_02` con `--zonas`: la bitácora da la
   fracción observable y los confirmados de cada zona (`E1_fusion_por_zona.csv`).

**Errores típicos.**

- `No encuentro el poligono de la ladera`: pase la ruta con `--ladera`.
- Una banda no aparece en la tabla: falta su `_coh` o su `_desp`/`_fase`
  (hacen falta los dos).
- Signos opuestos entre X y C sobre la ladera: puede ser la geometría (pasadas
  distintas), no un error. La regla de signo de la fusión supone la misma
  geometría de visión; si no lo es, dígalo y no la interprete.
- `Menos de dos bandas con desplazamiento valido (...): hay medicion, pero no
  fusion de decision. Declararlo.` Correcto: con una banda (por ejemplo, si la X
  quedó vacía) no hay fusión. Declárelo.

---

## Paso 4. Digitalizar cicatriz y depósito (EN QGIS)

**Qué y por qué.** El volumen se calcula dentro de dos polígonos: la
**cicatriz** (de donde salió material, el MDE baja) y el **depósito** (adonde
llegó, el MDE sube). Se digitalizan sobre el CBERS-4A de 2 m del 26/09/2026
(fondo principal, con su NDVI) y el MDE del IGN de 5 m, con la grieta relevada en
2018; la Pléiades de CONAE (0,5 m, 2022) o un mosaico XYZ y el Sentinel-2 del
19/10/2018 sirven de apoyo. El Spotlight de COSMO-SkyMed (20/10/2018) es un SLC
en geometría de radar: ver el punto 2 de abajo.
Es interpretación del analista: **sinergia**, no fusión.

**Primero, cree la capa.** El script la crea vacía (tipo de geometría polígono)
la primera vez que corre, sin necesidad de los MDE:

```
python Tp7_03_cicatriz_y_volumen.py
```

Debe ver:
«Se creo ...\04_Tablas_de_trabajo\E1_cicatriz_y_deposito.gpkg (capa 'formas',
campo 'tipo': cicatriz / deposito). Digitalizar y volver a correr.»

**En QGIS.**

1. `Capa > Añadir capa > Añadir capa vectorial...` → `E1_cicatriz_y_deposito.gpkg`, capa `formas`.
2. Fondo principal: el CBERS-4A del 26/09/2026 (`QGIS_GeoTIFF\E1_DIAMANTE_BARRANCA_CBERS4A_DIAMANTE_20260926_*_pansharpened_2m`),
   su NDVI (`Calculadora ráster`: (B4 − B3) / (B4 + B3), suavizado a 3 m), el MDE
   del IGN de 5 m y la grieta. **Protocolo del docente:** depósito = claro con
   NDVI < 0,30 al pie de la escarpa frente a la grieta, buscado entre las cotas 14
   y 42 m (el claro visible queda entre 25 y 33 m) y al este del camino costero;
   cicatriz = escarpa entre 5 m detrás de la grieta y el borde superior del claro.
   Apoyo: arrastre a QGIS `02_Subsets_SNAP_QGIS\Pleiades_CONAE_WMS\Diamante_2022_Pleiades_CONAE.xml`
   (Pléiades de CONAE, 0,5 m, 2022; necesita internet) o, en el `Navegador`, `XYZ Tiles` →
   `Nueva conexión...` (ESRI World Imagery o Google Satellite). Sume el Sentinel-2 del
   19/10/2018 (`QGIS_GeoTIFF\E1_DIAMANTE_BARRANCA_S2_20181019.tif`). El Spotlight de
   COSMO-SkyMed del 20/10/2018 está recortado como SLC, en geometría de radar: para
   usarlo de fondo habría que calibrarlo y geocodificarlo en SNAP (`Radar >
   Radiometric > Calibrate` y `Radar > Geometric > Terrain Correction`), lo que no
   entra en el tiempo del práctico; si lo hace, verifique su georreferencia (ver el
   error típico de abajo).
3. `Conmutar edición` (lápiz) → `Añadir polígono`. Al cerrar cada polígono
   complete `tipo` = `cicatriz` o `deposito` (sin tilde, en minúscula, tal cual)
   y `fuente` = la imagen sobre la que lo trazó y su fecha.
4. Guarde la edición.

**Control.** `tipo` escrito exactamente como `cicatriz` o `deposito`; si no, el
script avisa «No hay poligonos de tipo ...». El depósito, aguas abajo de la
cicatriz, al pie de la barranca o en el río.

**Variabilidad entre intérpretes.** Compare su polígono con el del docente:
`python Tp7_03_cicatriz_y_volumen.py ... --comparar_con <gpkg del docente>` da el
área de cada uno y la intersección sobre unión (`E1_comparacion_interpretes.csv`).

**Error típico.** Digitalizar sobre el Spotlight sin verificar su georreferencia:
si está corrido, el polígono queda corrido respecto del MDE.

---

## Paso 5. Volumen por diferencia de MDE

**Qué y por qué.** `dZ = MDE_después − MDE_antes`. El volumen perdido es la suma
de los dZ negativos en la cicatriz por el área del píxel; el ganado, la de los dZ
positivos en el depósito. Entre dos MDE de origen distinto hay diferencia de
datum (decímetros), de resolución y de fecha: por eso se mide y se resta el
**sesgo** en una zona estable, y se informa el **ruido** (desvío y NMAD) de esa
zona. Un píxel cuyo |dZ| no supera dos desvíos del ruido no es detectable; y un
resultado sólo es detectable si además tiene el **signo esperado** (bajada en la
cicatriz, subida en el depósito) y el patrón **no se repite** fuera de la forma:
el script lo compara con una escarpa de control a más de 200 m de las formas.

**Los MDE, y lo que este paso puede y no puede medir.** Están recortados al sitio en
`02_Subsets_SNAP_QGIS\QGIS_GeoTIFF`:

| Archivo | Qué es | Fecha | Referencia vertical | Superficie o terreno |
|---|---|---|---|---|
| `E1_DIAMANTE_BARRANCA_CopernicusDEM30.tif` | Copernicus DEM GLO-30, 30 m | TanDEM-X 2011–2015 | EGM2008 | **superficie** (con dosel y edificios) |
| `E1_DIAMANTE_BARRANCA_FABDEM_v1-2.tif` | GLO-30 sin bosque ni edificios, 30 m | 2011–2015 | EGM2008 | terreno |
| `E1_DIAMANTE_BARRANCA_IGN_MDE_5m.tif` | IGN MDE-Ar aerofotogramétrico, 5 m (hojas 3360-02-2) | vuelo de **2013** (metadato `0009 - 2013 - Rio Parana - Sector 3.5.pdf`) | SRVN16 (sistema nacional; verificar) | **superficie** |
| `E1_DIAMANTE_BARRANCA_IGN_MDE_mosaico2018.tif` | el mismo MDE del IGN, mosaico armado en el curso de 2018 (metros enteros; 0 sobre el río) | el del IGN, no 2018 | ídem | superficie |

**Ninguno es posterior a octubre de 2018.** El GLO-30 (2011–2015) y el IGN (2013) son
los dos anteriores al evento, y el «mosaico2018» es el mismo IGN armado en 2018, no un
relevamiento de ese año. Con estos MDE **no se mide el volumen movilizado en 2018**:
la diferencia entre ellos mezcla la diferencia de producto (datum, resolución,
método) con cualquier cambio de la barranca entre 2011–2015 y 2013. Este paso se hace
como **ejercicio de método**: cómo se mide el sesgo en zona estable, cómo se calcula el
ruido y cuándo un volumen sería detectable. El resultado se informa así. Si se
consigue un MDE posterior al evento (un vuelo del IGN posterior a 2018 o un LiDAR
aerotransportado), ése es el «después».

**Qué par comparar.** GLO-30 (antes, 2011–2015) contra IGN 5 m («después», 2013): los
dos son modelos de **superficie** e incluyen el dosel de la ladera, así que la altura
de los árboles se cancela en buena parte. El FABDEM es de terreno: compararlo con el IGN
(superficie) daría un «dZ» igual a la altura del monte de la ladera, que no es un
movimiento. **Orden único:** `--antes` el GLO-30 y `--despues` el IGN; con
`dZ = después − antes`, una pérdida de material da dZ negativo. **Píxel de 30 m** (`--pixel 30`): el del GLO-30. Llevar el GLO-30 a 5 m
inventaría detalle que no tiene (regla del curso: no se afina a un píxel más chico que
el nativo); el IGN se promedia a 30 m.

**Zona estable.** Por defecto el script usa el anillo `E1_zona_referencia.gpkg`
del paso 3 y le quita el agua del JRC (ocurrencia ≥ 50 %): la cota del río cambia
entre MDE y no es estable. Sin conexión no puede quitarla y lo avisa. También
puede dibujar una zona estable sólo en tierra firme, lejos de la barranca
(`Capa > Crear capa > Nueva capa GeoPackage`, polígono, EPSG:32721,
`04_Tablas_de_trabajo\E1_zona_estable_tierra.gpkg`) y pasarla con
`--zona_estable`; sirve igual para el paso 3 y para éste.

**Orden:**

```
python Tp7_03_cicatriz_y_volumen.py ^
  --antes ..\02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\E1_DIAMANTE_BARRANCA_CopernicusDEM30.tif ^
  --despues ..\02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\E1_DIAMANTE_BARRANCA_IGN_MDE_5m.tif ^
  --pixel 30 --zona_estable ..\04_Tablas_de_trabajo\E1_zona_estable_tierra.gpkg
```

Argumentos: `--antes` y `--despues` (necesarios una vez que existe el GeoPackage
de formas; si faltan, el script termina con `Faltan --antes y --despues (los dos
MDE a comparar).`), `--pixel 30` (por defecto: el del GLO-30; los MDE se promedian a esa grilla), `--zona_estable` (vacío: usa
`E1_zona_referencia.gpkg` sin el agua del JRC).

**Qué debe observar.** Sin `--zona_estable`, `Zona estable: anillo del paso 2 sin el
agua del JRC (ocurrencia >= 50 %).` (o el `AVISO` si no hubo conexión). Después, «Sesgo entre MDE en la zona estable: ±x,xx m (desvío y,yy m).
Se resta.» y una línea por forma y por control: área, dZ medio, volumen, volumen
detectable con su incertidumbre (2σ × área del píxel × √n, suponiendo errores
independientes) y el porcentaje de píxeles que supera dos desvíos con el signo
esperado y con el contrario. Sale `05_Resultados/04_Tablas/E1_volumenes.csv`.

**Control.** Si los píxeles no superan dos desvíos con el signo esperado, o si
el mismo patrón aparece en la escarpa de control, el volumen **no es detectable
con estos MDE** y así se informa. Con un MDE de 30 m frente a una
barranca de pocas decenas de metros de ancho, es lo esperable. Y aunque fuera
detectable, **no es el volumen del evento de 2018** (los dos MDE son anteriores):
escríbalo así en la entrega.

**Errores típicos.** `Falta la zona estable`: corra el paso 3 o pase
`--zona_estable`. Rutas con espacios sin comillas.

---

## Paso 6. Control del MDE con ICESat-2 (EN QGIS + AUXILIAR)

**Qué y por qué.** ATL08 da la altura de terreno (`h_te_best_fit`) en segmentos de
100 m, medida por un láser: es una referencia independiente de los dos MDE. Viene
en **altura elipsoidal**; el GLO-30 está sobre EGM2008 y el IGN sobre su propio
sistema vertical (SRVN16, a verificar). En Entre Ríos la ondulación del geoide
ronda los 15 m: comparar sin convertir es un error grosero.

**Las alturas ya convertidas.** La tabla LiDAR del sitio ya trae cada segmento
ATL08 con la cota del terreno en los dos sistemas verticales y el valor de los MDE
globales en el punto:
`02_Subsets_SNAP_QGIS\LiDAR_E1_DIAMANTE_BARRANCA\E1_DIAMANTE_BARRANCA_ATL08.csv`
(y el GeoPackage `E1_DIAMANTE_BARRANCA_LiDAR.gpkg` al lado). Columnas que importan:
`terreno_valido`, `fuerza_haz`, `h_terreno_egm2008` (sobre EGM2008, para el GLO-30 y el
FABDEM), `h_terreno_srvn16` (sobre SRVN16, para el IGN), `copdem_m`, `fabdem_m`,
`dif_lidar_copdem` y `dif_lidar_fabdem`. No hace falta convertir nada.

**En QGIS.**

1. Abra `E1_DIAMANTE_BARRANCA_LiDAR.gpkg` (capa de ATL08) y filtre
   `"terreno_valido" = 1` (botón derecho > `Filtrar…`).
2. Para el GLO-30 y el FABDEM, la diferencia ya está: columnas `dif_lidar_copdem` y
   `dif_lidar_fabdem` (LiDAR − MDE, en m).
3. Para el IGN: `Procesos > Caja de herramientas` → `Muestrear valores ráster`
   (capa de puntos filtrada, ráster `E1_DIAMANTE_BARRANCA_IGN_MDE_5m.tif`) y, con la
   `Calculadora de campos`, `dif_ign = "h_terreno_srvn16" − <valor_IGN>`. **El IGN se
   compara con `h_terreno_srvn16`, no con la de EGM2008**: mezclar sistemas verticales
   mete un sesgo falso del orden de decímetros.
4. Mire el sesgo (media o mediana) y el desvío de cada diferencia **sólo en segmentos
   fuera de la barranca y del río**, separando los haces fuertes (`fuerza_haz = 'fuerte'`).

**Control.** Si hay pocos segmentos válidos en el sitio (es chico), dígalo: el
control es ilustrativo, no estadístico. Un sesgo **negativo** (ICESat-2 menos
MDE) en monte y ciudad es esperable: el MDE de superficie mide copas y techos.

**Puntos cada 20 m sobre la cicatriz.** `python Tp7_04_icesat2_20m_cicatriz.py`
compara la cota del terreno de ATL08 cada 20 m (`h_te_best_fit_20m`) con el IGN,
restando el sesgo local, y la contrasta con el rango de las laderas sin evento:
un punto fuera de ese rango es un indicio puntual, no un patrón.

---

## Cierre

Responda `07_Preguntas_y_entrega/preguntas.md` citando el archivo de cada cifra.
Antes de irse, controle que estén las bitácoras en
`05_Resultados/06_Control_calidad/` (`Tp7_01_pares.log`, `Tp7_02_deformacion.log`,
`Tp7_03_volumen.log`, `Tp7_04_icesat2_20m.log`) y anote en un texto los parámetros
de SNAPHU que usó.

## Ampliación (optativa, fuera de la evaluación)

- **Contexto del sitio.** MapBiomas 2018 con la leyenda oficial, CCI Biomass 2024
  y la banda P de BIOMASS en RGB HH, VH, HH/VH (la cruzada es VH; la HV trae
  interferencia).
- **Velocidad 2025–2026.** `python Tp7_05_velocidad_y_susceptibilidad.py` usa la
  velocidad vertical del Tp10 (que la desarrolla) y arma una susceptibilidad
  hipotética a fisuras con umbral de 2σ.
- **Embeddings AlphaEarth.** `python Tp7_06_embeddings_cambio.py` mide la
  semejanza 2018–2025 por zona, con el umbral en el percentil 10 de la ladera.
