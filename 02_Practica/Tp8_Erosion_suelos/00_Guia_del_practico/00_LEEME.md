# Tp8 — Guía paso a paso

Jueves, 14 a 18 h. Sitio `F_BOVRIL`. Grilla común EPSG:32721 (UTM 21 S), 10 m.

Antes de empezar, en el **Miniforge Prompt**:

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp8_Erosion_suelos\03_Scripts
```

Distribución sugerida del tiempo:

| Horario | Paso |
|---|---|
| 14:00–14:40 | Paso 1. Frecuencia de suelo desnudo (mientras corre, lea el paso 2; sin internet, `--local`) |
| 14:40–15:10 | Paso 2. Desfase de NovaSAR |
| 15:10–15:50 | Paso 3. Textura en S y en C (sinergia) y GLCM en SNAP |
| 15:50–16:40 | Paso 4. Entrenamiento en QGIS sobre los puntos ya sorteados |
| 16:40–17:10 | Paso 5. Susceptibilidad (fusión de rasgos) y aporte del radar (Tp8_D en Orange) |
| 17:10–18:00 | Paso 6. Variantes para el Tp4 y preguntas |

**Landsat 8 y 9.** Escenas de este práctico, la pasada más cercana a cada Sentinel-2 con el sitio cubierto y despejado: Bovril, `F_BOVRIL_L8_20230914`: Landsat 8 del 14/09/2023 para el Sentinel-2 del 10/09/2023.

Son Colección 2, Nivel 2 de USGS (reflectancia y temperatura de superficie, píxel de 30 m), bajadas del Planetary Computer. Están en `02_Subsets_SNAP_QGIS\SNAP_DIMAP` y `QGIS_GeoTIFF`, con las bandas `SR_B1` a `SR_B7` (reflectancia), `ST_B10` (temperatura, K), `ST_QA`, `QA_PIXEL` y las virtuales `NDVI` y `ST_B10_C` (°C).

Landsat 9 da imágenes desde el 31/10/2021; antes sólo hay Landsat 8. Los dos llevan instrumentos gemelos (OLI y TIRS) y se comparan entre sí sin ajuste. Con Sentinel-2 no: el píxel es de 30 m contra 10 y 20 m, y las bandas no coinciden del todo (el infrarrojo cercano de Landsat, 865 nm, equivale a la B8A, no a la B08).

Fuente: USGS / NASA, Landsat 8 y Landsat 9 OLI/TIRS, Colección 2 Nivel 2, distribuido por Microsoft Planetary Computer, https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2

**Fusión Landsat + Sentinel-2.** El Landsat también viene afinado a 10 m con el detalle espacial del Sentinel-2 de la fecha más cercana: se lo interpola a la grilla de 10 m y se le suma el detalle fino de la banda Sentinel-2 de 10 m que más se le parece, escalado por una regresión entre los dos sensores (filtro pasa-altos con modulación por regresión, HPF). Trae las bandas `SR_B1` a `SR_B7` en reflectancia, `mascara_detalle` (1 = se agregó detalle; 0 = nube, sombra o falta de dato en alguna de las dos) y el `NDVI` virtual; el método y la calidad de cada banda están en los metadatos.

El control es el ERGAS: la imagen afinada se lleva de nuevo a 30 m y se compara con el Landsat original; por debajo de 3 la fusión es buena. Sirve para mirar e interpretar, con tres cuidados: un cambio real entre las dos fechas aparece como detalle falso; las bandas 6 y 7 (infrarrojo de onda corta) toman el detalle de una banda de 10 m de otra región del espectro y son las menos confiables; y la temperatura no se afina.

En este práctico: `F_BOVRIL_L8_20230914_fusion_S2_20230910_10m`: 4 días entre las dos imágenes; ERGAS 0,90.

**Pléiades y Pléiades Neo de CONAE.** Referencia visual de muy alta resolución del casco urbano (Pléiades, 0,5 m; Pléiades Neo, 0,3 m), 2022-2023, del proyecto Impactar de CONAE. Es un servicio de mapas y necesita internet: en `02_Subsets_SNAP_QGIS\Pleiades_CONAE_WMS` hay un `.xml` por localidad que se arrastra a QGIS (instrucciones en el `LEEME.md` de esa carpeta). Sirve para mirar y digitalizar, no para calcular: es RGB color real, sin infrarrojo ni reflectancia, y la fecha exacta no está publicada, sólo el año.

En este práctico: Bovril no tiene capa de CONAE.

**CBERS-4A, cámara WPM (INPE).** Pancromática de 2 m y multiespectral de 8 m (azul, verde, rojo e infrarrojo cercano), producto L4 ortorrectificado, en números digitales. Cada escena viene en dos productos: `..._MS_8m` (las cuatro bandas originales) y `..._pansharpened_2m` (la pancromática y las cuatro bandas afinadas a 2 m por Brovey ponderado, el método por defecto de GDAL). Es un pansharpening clásico: pancromática y multiespectral del mismo satélite y del mismo instante; compárelo con la fusión Landsat + Sentinel-2, que combina dos sensores y dos fechas. El control es el mismo ERGAS (por debajo de 3, bueno). Los números digitales no son reflectancia y el Brovey altera la radiometría: sirve para mirar y digitalizar, no para calcular índices. Cubre una zona de 12 a 21 km, no el sitio entero, y la escena se eligió a ojo, sin nubes, porque el catálogo del INPE no informa la nubosidad.

En este práctico: Bovril, `F_BOVRIL_CBERS4A_BOVRIL_20230615_...`: 15/06/2023, 87 días antes del Sentinel-2 (la del 16/08 tenía una nube al oeste del pueblo); ERGAS 1,48.

Fuente: INPE / CAST, CBERS-4A WPM L4, licencia CC BY 4.0. Catálogo STAC del INPE, colección CB4A-WPM-L4-DN-1, https://data.inpe.br/stac/browser/collections/CB4A-WPM-L4-DN-1

**Embeddings anuales AlphaEarth Foundations (Google y Google DeepMind).** 64 números por píxel de 10 m que resumen un año entero de Sentinel-1, Sentinel-2, Landsat, GEDI, clima y otras fuentes, aprendidos por un modelo de inteligencia artificial. Las dimensiones (`A00` a `A63`) no tienen significado físico propio: sirven para clasificar con pocas muestras, buscar zonas parecidas y detectar cambios entre años. Vienen en enteros de 8 bits tal como los entrega Google (`..._AlphaEarth_embeddings_<año>_10m`); para pasarlos a valores reales, valor = signo(DN) × (DN / 127,5)², y −128 es sin dato. El `..._CP1_CP2_CP3_RGB_8bit.tif` muestra las tres primeras componentes principales para mirar en QGIS; sus colores no tienen significado fijo. Resumen un año, no una fecha; 2026 todavía no existe y se usa 2025, el último.

En este práctico: Bovril, 2023.

Fuente: The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind (CC BY 4.0). Copia en Source Cooperative (Taylor Geospatial), https://source.coop/tge-labs/aef

---

## Paso 1. Frecuencia de suelo desnudo en la serie óptica

**Qué y por qué.** Un lote recién labrado está desnudo uno o dos meses; un suelo
degradado o una cárcava, todo el año. Lo que distingue la erosión de la labranza
es la **persistencia**. Para cada escena Sentinel-2 L2A de 2023, sólo en los
píxeles sin nube según la SCL:

- NDVI = (B08 − B04) / (B08 + B04): baja con poca vegetación verde;
- BSI = ((B11 + B04) − (B08 + B02)) / ((B11 + B04) + (B08 + B02)): sube con suelo
  expuesto (el SWIR y el rojo reflejan más que el NIR y el azul);
- suelo desnudo si NDVI < 0,25 **y** BSI > 0.

Un mes cuenta como desnudo si la mayoría de sus observaciones válidas lo fueron.
El catálogo trae dos versiones de procesamiento de muchas fechas: el script
conserva una por fecha y tesela (la de línea de base más alta) e informa cuántas
descartó, para que una fecha repetida no pese el doble en la mayoría del mes.
El resultado es «meses por año con suelo desnudo» y «meses con al menos una
observación». La reflectancia se corrige por el desplazamiento de +1000 de la
línea de base 04.00 (desde el 25/01/2022), que tienen todas las escenas de 2023.

**Dónde.** Miniforge.

**Orden** (los valores son los de por defecto):

```
python Tp8_01_frecuencia_suelo_desnudo.py --anio 2023 --pixel 10 --nubes_max 60
```

Argumentos: `--anio 2023`, `--pixel 10`, `--nubes_max 60` (nubosidad de catálogo
de la tesela, en %), `--ndvi_max 0.25`, `--bsi_min 0`, `--fecha_histograma 2023-11-07`
(fecha de los histogramas de NDVI y BSI con la línea de cada umbral, en
`05_Resultados/05_Graficos/`) y `--local` (sin internet: lee la copia de la serie de
`00_COMUN/08_Originales_crudos/PLANETARY/F_BOVRIL`, 68 fechas con el sitio casi entero
despejado; el resultado puede diferir un poco del de la serie completa).

**Qué debe observar.** El número de escenas con menos de 60 % de nubes de catálogo y,
por cada escena usada, la fecha, el % del sitio útil y el % de suelo desnudo. Las
escenas con menos del 20 % del sitio útil se descartan. Al final, la mediana de
meses con observación, el % del sitio sin ninguna observación válida en el año, y
el % de lo observado en cada clase: nunca desnudo, 1–2 meses (labranza), 3–5
meses, 6 o más meses (persistente). Los píxeles nunca observados no entran en
esos porcentajes.

Mire también los dos histogramas: ¿dónde cae cada umbral respecto de las modas?

Salidas:
`02_Subsets_SNAP_QGIS/F_frecuencia_suelo_desnudo_2023_10m.tif` (bandas
`meses_suelo_desnudo` y `meses_con_observacion`) y
`05_Resultados/04_Tablas/F_escenas_opticas_2023.csv`.

**Control (en QGIS).**

1. `Capa > Añadir capa > Añadir capa ráster...` → el GeoTIFF. `Propiedades >
   Simbología > Pseudocolor monobanda`, banda 1, mínimo 0 y máximo 12.
2. Banda 2: si hay zonas con pocos meses observados (menos de 8), la frecuencia
   ahí está subestimada. Anótelo.
3. Con el fondo de muy alta resolución, mire tres lotes de 1–2 meses: deben
   verse como lotes agrícolas comunes. Mire los de 6 o más: ¿son caminos de
   tierra, cárcavas, cascos, canteras, bañados secos? **Lo que no es erosión
   también puede estar desnudo todo el año** (caminos, áreas urbanas).

**Errores típicos.**

- Error HTTP 403 a mitad de la corrida: las URL firmadas del Planetary Computer
  duran alrededor de una hora. Vuelva a correr el script, o córralo con `--local`.
- Muy pocas escenas: suba `--nubes_max` a 80 y declárelo.
- Rastrojo seco: con siembra directa, el rastrojo de soja o maíz tiene NDVI bajo
  y puede dar BSI > 0. Si un lote aparece 6 o más meses «desnudo» y en la imagen
  se ve rastrojo, es una limitación del índice, no erosión.

---

## Paso 2. El desfase de NovaSAR (EN QGIS)

**Qué y por qué.** El `image_HH.tif` de la escena NovaSAR-1 47974 trae sólo los
**cuatro puntos de esquina** (GCP): el ajuste es afín sobre toda la franja y
deja corrimientos de cientos de metros que, además, cambian de norte a sur
(medido en el desarrollo: la banda S queda unos 90 m al este y de 560 m en el norte
a 330 m en el sur al norte; ver el Tp3). El `metadata.xml` del mismo producto trae
**84 puntos de enlace** (6 × 14) repartidos en la franja: con ellos el corrimiento
queda chico y rígido: la banda S queda **unos 80 m al este y 20 m al sur** del
óptico, y se corrige moviéndola 80 m al oeste y 20 m al norte. Con 10 m de píxel, eso son 8 píxeles: comparar
texturas por lote sin corregirlo mezcla un lote con el vecino.

**Primero, sin corregir.** Corra el paso 3 una vez sin desplazamiento (es el
valor por defecto), con los 84 puntos de enlace, para tener la banda S en la grilla:

```
python Tp8_02_textura_S_y_C.py --puntos_enlace todos
```

Si quiere ver el efecto de las cuatro esquinas, córralo también sin
`--puntos_enlace` (o con `--puntos_enlace esquinas`) y compare las dos salidas.

La bitácora avisa: «AVISO: NovaSAR sin correccion de georreferencia...».

**En QGIS.**

1. Abra `02_Subsets_SNAP_QGIS/F_textura_S_C_10m.tif`, banda `S_NovaSAR_sigma0_HH`.
   Para verla, cree una banda en dB con `Ráster > Calculadora ráster...`:
   `10 * log10("F_textura_S_C_10m@1")` (sólo para mirar).
2. Sume un Sentinel-2 del 10/09/2023 o el fondo de muy alta resolución.
3. Con la herramienta `Medir línea`, mida en tres o cuatro rasgos lineales
   (rutas, bordes de lote, alambrados) cuánto hay que mover la banda S para que
   coincida. Mida de la esquina en el óptico a la misma esquina en la NovaSAR: eso
   es el error (por ejemplo, dx = +80 m al este, dy = −20 m al sur). La corrección
   que se pasa al script es la opuesta.

**Cómo se pasa el desplazamiento al script.** `--desplazamiento DX DY` en metros:
es la CORRECCIÓN que se **aplica** al producto (DX positivo = mover al este, DY
positivo = mover al norte), no el error medido. Si la banda S está 80 m al este y
20 m al sur, se la mueve 80 m al oeste y 20 m al norte: `--desplazamiento -80 20`.
Va siempre junto con el `--puntos_enlace` con que se midió: un desplazamiento medido
con las cuatro esquinas no sirve para los 84 puntos de enlace, y al revés.

**Control.** Después del paso 3 con la corrección, repita la medición: la
mediana del residuo tiene que ser menor que un píxel (10 m); las ventanas con 1 a
2 píxeles de residuo se declaran y se enmascaran. Si cambia mucho de un lado a
otro del sitio, no es una traslación rígida: dígalo.

**Errores típicos.** Pasar el error en lugar de la corrección (`+80 -20`): la banda
S se aleja el doble. Medir con las cuatro esquinas y aplicar con `--puntos_enlace
todos`, o al revés. Medir sobre bordes de monte, que en radar y en óptico no
coinciden por la sombra y la altura de las copas.

---

## Paso 3. Textura en banda S y en banda C (SINERGIA)

**Qué y por qué.** La rugosidad del suelo (terrones, surcos, bordes de cárcava)
cambia la retrodispersión; la **textura** espacial (cuánto varía la señal entre
píxeles vecinos) la describe mejor que el valor medio. Se calcula para cada
banda **por separado**:

- **S**: NovaSAR-1 GRD HH 47974 (9,4 cm), σ⁰ = DN²/CalibrationConstant
  (1E+05, leída del `metadata.xml`). El paso de 6 m a 10 m se hace con la media
  cuadrática de los DN: `media(DN²)` es la media de la potencia.
- **C**: Sentinel-1 RTC VV y VH (5,5 cm), γ⁰ lineal, de la escena **más
  cercana** a `--fecha_c` dentro de ± 6 días: `--fecha_c` es la fecha buscada; en
  Bovril el script toma el Sentinel-1 del 17/09/2023, tres días después de la NovaSAR.

Textura = coeficiente de variación local en una ventana de 5 × 5 píxeles:
CV = desvío(potencia) / media(potencia), **en potencia lineal, no en dB**. El
speckle solo ya da un CV: en intensidad (potencia), 1 para una vista y 1/√L para L
vistas (en amplitud, 0,52 para una vista). ENL = 1/CV² en una zona homogénea dice
cuántas vistas promedia el producto. Por eso el CV se
compara contra el de una zona homogénea del **mismo producto**.

**Orden:**

```
python Tp8_02_textura_S_y_C.py --pixel 10 --fecha_c 2023-09-14 --ventana 5 --novasar 47974 --puntos_enlace todos --desplazamiento -80 20 --zonas_homogeneas ..\04_Tablas_de_trabajo\zonas_homogeneas.gpkg
```

Valores por defecto: `--pixel 10`, `--fecha_c 2023-09-14`, `--novasar 47974`,
`--ventana 5`, `--puntos_enlace esquinas`, `--desplazamiento 0 0`, `--anio 2023` (año de la frecuencia de
suelo desnudo del paso 1 que se lee para la tabla). **Use el desplazamiento que
midió.** Signo: DX y DY son la corrección (DX positivo = mover al este, DY
positivo = mover al norte); para mover la banda S 80 m al oeste y 20 m al norte:
`--desplazamiento -80 20`. `--zonas_homogeneas` (opcional) calcula el piso de
speckle en los polígonos del `.gpkg` con la misma ventana y lo agrega como última
fila de la tabla. La fecha de la escena NovaSAR (para la cita
de fuente y la diferencia de días S–C) se toma de la escena pedida con
`--novasar`.

**Qué debe observar.** El % del sitio con dato de NovaSAR y su CV mediano; la fecha
de Sentinel-1 usada, el CV mediano de VV y VH, y la diferencia de días entre S y
C (la lluvia entre fechas cambia la humedad y la retrodispersión). Después, la
tabla del CV mediano de cada banda por clase de frecuencia de suelo desnudo.

Salidas: `02_Subsets_SNAP_QGIS/F_textura_S_C_10m.tif` (bandas
`S_NovaSAR_sigma0_HH`, `S_CV_HH`, `C_S1_gamma0_VV`, `C_CV_VV`, `C_S1_gamma0_VH`,
`C_CV_VH`) y `05_Resultados/04_Tablas/F_textura_por_frecuencia.csv`.

**Control (en QGIS).**

1. Abra `04_Tablas_de_trabajo/zonas_homogeneas.gpkg` (12 ventanas de 100 × 100 m en
   lotes con cultivo o pastura parejos) o dibuje cuatro polígonos de 100 × 100 m en
   lotes lisos (cultivo parejo, pastura, labrado parejo), lejos de los bordes, y use
   `Procesos > Caja de herramientas > Estadísticas de zona` sobre `S_CV_HH`,
   `C_CV_VV` y `C_CV_VH` (es la misma ventana del script). Ese es el CV del speckle
   de cada producto. No use agua: en banda S y en la VH de C está cerca del ruido y
   su CV no es el del speckle. Si el piso queda por encima de la mediana de todo el
   sitio, sus zonas no son homogéneas (en C, la resolución es de 20 × 22 m).
2. Lea la tabla `F_textura_por_frecuencia.csv` **contra ese piso**: lo que
   importa es cuánto sube el CV respecto de la zona homogénea, no el valor
   absoluto de cada sensor.
3. Abra `S_CV_HH` sobre el fondo de alta resolución: ¿aparecen las cárcavas como
   líneas de CV alto, o sólo los bordes de lote, los alambrados y la ciudad?

**Errores típicos.**

- `No encuentro el GRD de la escena 47974`: el disco de NovaSAR con otra letra.
  `set CURSO_SAR_NOVASAR=F:\IMÁGENES NOVASAR-1 2023 2024\ENTRE RIOS-SANTA FE`.
- «Sin Sentinel-1 RTC +/- 6 días»: la comparación queda sin banda C; el paso 5
  sigue sólo con la banda S. Declárelo.
- «Falta la frecuencia de suelo desnudo»: corra el paso 1 antes, o pase el
  mismo `--anio` con que lo corrió.

### 3b. Textura de Haralick en SNAP (EN SNAP, sinergia de medidas)

Ver `09_Grafos_SNAP/LEEME_grafos.md`. En resumen: abra
`F_textura_S_C_10m.tif` en SNAP. **Atención con los nombres:** SNAP 11 lee los
nombres de banda que escribe Python (`S_NovaSAR_sigma0_HH`, `S_CV_HH`, …); otras versiones
pueden mostrarlas como `band_1`, `band_2`, … en el orden de la lista de salidas del paso 3
(`band_1` = `S_NovaSAR_sigma0_HH`, `band_2` = `S_CV_HH`, y así). Verifíquelo en
`Analysis > Information` antes de seguir. El grafo `09_Grafos_SNAP/Tp8_GLCM_S.xml` hace lo
mismo con `gpt` (dB, GLCM 5 × 5, 32 niveles, `Contrast` y `Homogeneity`). Cree la banda en dB de `S_NovaSAR_sigma0_HH`
(`Raster > Data Conversion > Linear to/from dB`), y corra `Raster > Image
Analysis > Texture Analysis > Grey Level Co-occurrence Matrix` con ventana 5 × 5.
Compare `Contrast` y `Homogeneity` con `S_CV_HH` en tres lotes: ¿ordenan los
lotes de la misma manera?

---

## Paso 4. Entrenamiento (EN QGIS)

**Qué y por qué.** El Random Forest aprende de ejemplos. Dos clases:

- `codigo = 1`: **erosión activa o cárcava** (cárcavas visibles, suelo
  decapitado, surcos de erosión);
- `codigo = 2`: **suelo estable** (lote cultivado, pastura, monte).

Las cárcavas se reconocen en la imagen de muy alta resolución y en el NovaSAR de
6 m (bordes brillantes y sombras lineales). **Incluya en la clase 2 lotes recién
labrados**: es lo que enseña al modelo que labranza no es erosión.

**El estrato y los puntos ya vienen hechos.** `04_Tablas_de_trabajo/estrato_erosion_F.gpkg`
trae la capa `estrato_erosion` (suelo desnudo 3 meses o más, fuera del casco urbano,
pendiente FABDEM de 0,78° o más: 509 ha) y la capa `puntos_sorteados` (144 puntos con
semilla, numerados en el orden del sorteo). Recórralos en orden. Mínimo: 10 polígonos
de erosión y 15 estables. Si el curso se reparte los puntos entre grupos, las capas
se unen al final.

**Crear la capa.** La primera corrida del paso 5 crea
`04_Tablas_de_trabajo/entrenamiento_F.gpkg` (capa `entrenamiento`, campos
`codigo` y `clase`) vacía y termina:

```
python Tp8_03_susceptibilidad.py
```

(Esa primera corrida ya escribe `F_variante_optico.tif`.)

**En QGIS.** Abra la capa, `Conmutar edición` → `Añadir polígono`. Complete
`codigo` (1 o 2), `clase` (texto libre: «carcava», «lote labrado»…) y
`dist_al_punto_m`. Cuadrados de 40 × 40 m: en la clase 2, centrados en el punto; en
la clase 1, sobre el reguero o la cárcava visible más cercana al punto si está a
menos de 100 m (si no hay ninguna, el punto se saltea). Los lotes con terrazas de
conservación se saltean (son una obra contra la erosión), y los lotes del estrato
labrados en pendiente sin surcos van a la clase 2. Esta muestra no es probabilística
(búsqueda dirigida asistida por sorteo): no sirve para validar. Guarde.

**Polígonos al azar.** Los polígonos se trazan al azar, no donde la clase se ve más fácil. `Vectorial > Herramientas de investigación > Puntos aleatorios en la extensión` (Random Points in Extent), con la extensión del sitio y 100 puntos. Recorra los puntos en el orden en que salieron (campo `id`) y trace un polígono alrededor de cada punto que caiga en una cubierta inequívoca, hasta completar el número pedido para cada clase; los puntos que caen en bordes o en cubiertas dudosas se saltean y se anotan. Elegir los lugares a ojo concentra los polígonos en los ejemplos más típicos y hace que el mapa parezca mejor de lo que es. Con 100 puntos uniformes las clases raras (las que ocupan pocas hectáreas: monte cerrado, suelo desnudo, severidad alta) casi nunca se completan. Para esas clases, haga un **sorteo estratificado**: convierta a polígono el estrato de la clase (`Ráster > Conversión > Poligonizar` sobre MapBiomas, o sobre el rango del índice que define la clase) y use `Vectorial > Herramientas de investigación > Puntos aleatorios dentro de polígonos`; recorra esos puntos también en el orden en que salieron, con la misma revisión en la imagen. Anote de qué sorteo salió cada polígono. En las cárcavas, así no se dibujan sólo las más vistosas.

**Errores típicos.** Polígonos sólo en un rincón del sitio (el modelo aprende
ese rincón); polígonos fuera del dominio multisensor (NovaSAR cubre el 92,9 % del sitio y,
con las ventanas de textura y la banda C, la variante multisensor evalúa el 89 %:
esos píxeles no entran).

---

## Paso 5. Susceptibilidad (FUSIÓN DE RASGOS)

**Qué y por qué.** Cada sensor aporta una **variable derivada** (un rasgo):

| Rasgo | Sensor | Qué describe |
|---|---|---|
| `meses_suelo_desnudo` | Sentinel-2 | Persistencia de la exposición |
| `S_CV_HH` | NovaSAR (S) | Rugosidad y bordes a 6 m |
| `C_CV_VV`, `C_CV_VH` | Sentinel-1 (C) | Rugosidad en la grilla de 10 m (el IW GRD tiene píxel de 10 m pero resolución de unos 20 × 22 m; si hubo escena) |
| `pendiente_grados` | FABDEM v1-2 (`02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\F_BOVRIL_FABDEM_v1-2.tif`: el GLO-30 sin monte ni edificios) | La ladera (a 30 m la pendiente de una cárcava NO se resuelve). No se usa el GLO-30 directo: es de superficie y el borde de un monte o de una cortina da una pendiente falsa que el modelo aprendería como cárcava |

Un Random Forest (300 árboles, semilla fija, muestreo equilibrado por clase) los
combina. **El equilibrado infla la probabilidad de la clase rara: el umbral 0,5
marca de más.** La pendiente se calcula a 30 m y se lleva a 10 m. La
probabilidad de la clase 1 es el **índice de susceptibilidad** (0 a 1); con
`--umbral` se hace el mapa binario para el Tp4.

**Orden:**

```
python Tp8_03_susceptibilidad.py --pixel 10 --umbral 0.5
```

Valores por defecto: `--pixel 10`, `--umbral 0.5`, `--anio 2023` (el año del
paso 1; si lo corrió con otro, páselo aquí también), `--equilibrar si`, todos los
rasgos. **Variantes** (con los mismos polígonos):

```
python Tp8_03_susceptibilidad.py --rasgos meses_suelo_desnudo pendiente_grados --nombre_variante opt_pend
python Tp8_03_susceptibilidad.py --equilibrar no --nombre_variante sin_equilibrar
python Tp8_03_susceptibilidad.py --mascara_urbana --nombre_variante urbana
```

La diferencia entre «óptico + pendiente» y la variante completa es el aporte del
radar; sin programar, se mide en Orange con `08_Orange/Tp8_D_aporte_del_radar.ows`
(Test and Score con «Cross validation by feature» = `id_poligono`). La bitácora
informa además la superficie con umbrales 0,5, 0,8 y 0,9.

**Qué debe observar.** Los rasgos usados, la exactitud fuera de bolsa (marcada
OPTIMISTA), la importancia de cada rasgo ordenada, y la superficie susceptible
(ha) frente a la del «solo óptico».

Salidas en `05_Resultados/02_Rasters/`: `F_susceptibilidad.tif`,
`F_variante_multisensor.tif` (1 susceptible, 2 no) y `F_variante_optico.tif`
(solo frecuencia ≥ 6 meses).

**Control.**

1. La exactitud fuera de bolsa se calcula con píxeles vecinos de los mismos
   polígonos: **siempre es optimista**. No la informe como exactitud.
2. Si la pendiente está entre los dos rasgos más importantes, mire si sus polígonos de
   cárcava están todos en las barrancas de arroyos: el modelo puede estar
   aprendiendo «ladera», no «erosión».
3. Compare en QGIS las dos variantes: ¿dónde las separa la textura SAR?
4. La importancia dice cuánto usó el modelo cada rasgo, no cuánto mejora el mapa:
   el aporte del radar sale de comparar variantes validadas por polígono.
5. Si el mapa tiene forma de lote, está midiendo la labranza (la regla de
   `01_Prompt_IA`).

**Errores típicos.** `Muy pocos pixeles de entrenamiento con dato en todas las
capas`: polígonos fuera de NovaSAR o sin banda C con dato. `AVISO: no esta ...FABDEM...; la pendiente sale del Copernicus DEM GLO-30, que es de SUPERFICIE`:
falta `F_BOVRIL_FABDEM_v1-2.tif` en `QGIS_GeoTIFF`; el GLO-30 de superficie marca bordes de monte
como pendiente (declárelo). Error de red: el paso lee Sentinel-1 del Planetary Computer.

---

## Paso 6. Variantes para el Tp4

Desde la carpeta de scripts del Tp4
(`cd /d ...\02_Practica\Tp4_Validacion\03_Scripts`):

```
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp8_Erosion_suelos\05_Resultados\02_Rasters\F_variante_multisensor.tif --banda 1
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp8_Erosion_suelos\05_Resultados\02_Rasters\F_variante_optico.tif --banda 1
```

Defina antes la clase de referencia: 1 = un reguero, una cárcava o suelo decapitado
dentro del píxel de 10 m o a menos de 15 m; 2 = cualquier otra cosa (caminos,
terrazas, lotes labrados sin regueros). Mezcle los puntos de las dos muestras en un
solo orden al azar y etiquételos sin ver ningún mapa. El mapa es de
susceptibilidad y la referencia es erosión visible en junio de 2023: la comparación
dice cuán bien el mapa localiza esa erosión, no si predice la futura.

Etiquete **al azar** en QGIS los puntos de
`Tp4_Validacion\04_Tablas_de_trabajo\<nombre>_puntos_a_etiquetar.gpkg`
(campo `clase_ref`: 1 susceptible, 2 no), y después:

```
python Tp4_03_exactitud_y_area.py --nombre F_variante_multisensor --nombres_clase "1=susceptible,2=no_susceptible"
python Tp4_03_exactitud_y_area.py --nombre F_variante_optico --nombres_clase "1=susceptible,2=no_susceptible"
python Tp4_04_tabla_de_variantes.py --tp Tp8 --clase susceptible ^
  --variante "Solo optico|Sentinel-2|F_variante_optico" ^
  --variante "Multisensor|Sentinel-2 + NovaSAR S + Sentinel-1 C + FABDEM|F_variante_multisensor"
```

Si no alcanza el tiempo, el etiquetado y `Tp4_03` se completan fuera del horario (el trabajo final del curso es de planificación y no tiene tiempo para etiquetar); si no se llega, la entrega lo declara. Si el intervalo de confianza
de la diferencia entre las dos variantes incluye el cero, la mejora **no está
demostrada** con esa muestra. Con pocos aciertos en la clase 1, el intervalo normal
de la exactitud del usuario puede dar un límite negativo: informe el de Wilson. La
muestra se dimensiona con U = 0,85; si la clase es rara y U real es cercano a 0,1,
hacen falta al menos 100 puntos en la clase 1.

---

## Paso opcional. Avance de cárcavas (COMPLEMENTARIO, fuera del horario)

Se digitalizan los bordes de cárcava en alta resolución y se comparan entre dos
fechas. El archivo del curso tiene una sola fecha de 2 m (CBERS-4A del 15/06/2023):
la segunda sale del historial de Google Earth Pro. No hay script. En QGIS: `Capa > Crear capa > Nueva capa
GeoPackage` de líneas, digitalice el borde en dos fechas de la imagen de muy
alta resolución (el control de historial de Google Earth Pro sirve para ver
fechas), y mida el avance con `Medir línea`. Declare que el GLO-30 de 30 m no
resuelve la cárcava.

## Paso opcional. Del Sentinel-1 sin procesar a γ⁰ — EN SNAP

**Qué y por qué.** Todos los Sentinel-1 de este práctico vienen ya corregidos: son el γ⁰ RTC del Planetary Computer. Este paso muestra de dónde sale ese γ⁰. Se parte del producto GRDH de nivel 1 tal como lo entrega ESA, el `.zip` con la carpeta `.SAFE` adentro (mediciones, anotaciones, calibración, ruido y órbita predicha), y se recorre en SNAP la misma cadena que usó el docente. El resultado del docente viene hecho y sirve para controlar el suyo.

**Insumo.** `00_COMUN\08_Originales_crudos\S1_CRUDO\S1A_IW_GRDH_1SDV_20230917T091449_20230917T091514_050365_061067_C33B.zip` (Sentinel-1A IW GRDH, VV + VH, 17/09/2023). Se eligió esa pasada porque es tres días posterior a la NovaSAR-1 47974.

**Lo que viene hecho.** `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo` de este práctico: `SNAP_DIMAP` (γ⁰ VV y VH lineales, bandas virtuales en dB y cociente VV/VH en dB, metadatos completos), `QGIS_GeoTIFF` (con `_metadatos.txt`), `RGB_copol_cruzada_cociente` (R = VV, G = VH, B = VV/VH) y `Grafos_SNAP` (el grafo XML). El detalle está en `LEEME_S1_crudo.md` de esa carpeta.

**Dónde.** SNAP Desktop. La primera vez SNAP baja la órbita precisa y el Copernicus DEM, así que necesita internet. Hay dos formas de hacerlo.

**Forma rápida: el grafo del docente.**

1. `Tools > GraphBuilder`, botón `Load`, y elija `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\Grafos_SNAP\Grafo_F_BOVRIL_S1_20230917_gamma0_desde_crudo.xml`.
2. Recorra las pestañas: cada una es un paso de la cadena, con los parámetros que se usaron.
3. En la pestaña `Write`, cambie el nombre y la carpeta de salida a `05_Resultados\02_Rasters`, para no pisar el producto del docente. Botón `Run`.

**Forma completa: paso a paso con los menús.** Cada operador escribe un producto intermedio. En la ventana de cada uno, pestaña `I/O Parameters`, deje como entrada el producto anterior y guarde en `05_Resultados\02_Rasters`.

1. `File > Open Product…` sobre el `.zip` (no hace falta descomprimirlo).
2. `Radar > Radiometric > S-1 Thermal Noise Removal`: quita el ruido térmico del instrumento, que pesa en VH y en las superficies oscuras, como el agua.
3. `Radar > Sentinel-1 TOPS > S-1 Remove GRD Border Noise` (límite de borde 500, umbral 0,5): quita las franjas de valores falsos de los bordes de la escena.
4. `Radar > Apply Orbit File`, tipo `Sentinel Precise (Auto Download)`: reemplaza la órbita predicha por la precisa.
5. `Radar > Radiometric > Calibrate`: en `Processing Parameters` marque sólo `Output beta0 band`. El aplanado necesita β⁰, no σ⁰.
6. `Raster > Subset…`, pestaña `Geo Coordinates`: recorte al sitio. Recortar antes del aplanado ahorra mucho tiempo y memoria.
7. `Radar > Radiometric > Terrain Flattening`, DEM `Copernicus 30m Global DEM`, remuestreo bilineal: pasa de β⁰ a γ⁰, normalizado por el área iluminada. Es el paso más lento.
8. `Radar > Speckle Filtering > Single Product Speckle Filter`, filtro `Refined Lee`.
9. `Radar > Geometric > Terrain Correction > Range-Doppler Terrain Correction`: DEM `Copernicus 30m Global DEM`, píxel de 10 m, proyección UTM automática (`AUTO:42001`, que en este sitio es la zona 21 S, la de la grilla del curso), formato BEAM-DIMAP.
10. Bandas en dB: clic derecho sobre cada banda γ⁰ > `Linear to/from dB`. Crea bandas virtuales y deja intactas las lineales.
11. Cociente: `Raster > Band Maths…`, expresión `Gamma0_VV_db - Gamma0_VH_db` (en dB, la resta es el cociente VV/VH).
12. RGB: `Window > Open RGB Image Window`, con R = `Gamma0_VV_db`, G = `Gamma0_VH_db` y B = el cociente.

**Qué debe observar.**

- Un producto con `Gamma0_VV` y `Gamma0_VH` en lineal y sus bandas virtuales en dB.
- En `Metadata > Processing_Graph`, la lista de operadores en el orden en que se aplicaron. Ahí queda escrito todo lo que se le hizo al dato.
- En `Metadata > Abstracted_Metadata`, la misión, la fecha, la órbita y el ángulo de incidencia del original: el recorte no los pierde.
- Abierto junto al producto del docente (el `.dim` de `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\SNAP_DIMAP`), los dos se superponen en `World View` y se ven casi iguales.

**Comparación con el RTC del Planetary Computer.** El mismo día existe el γ⁰ RTC del Planetary Computer, en `02_Subsets_SNAP_QGIS\SNAP_DIMAP\F_BOVRIL_S1_C_20230917.dim` de este práctico. Diferencia mediana del γ⁰ de SNAP menos el RTC, en todo el sitio:

- VV: −1,40 dB (p5 a p95, −4,2 a +1,5 dB; correlación 0,78).
- VH: −1,80 dB (p5 a p95, −4,8 a +1,2 dB; correlación 0,83).

**Cómo se interpreta.**

- En VV, casi toda la diferencia es un desfase de normalización de `Terrain Flattening` de SNAP: su γ⁰ queda por debajo de σ⁰/cos θ aun en terreno plano. El desfase cambia con la escena y el ángulo de incidencia (−0,5 dB en Concordia, −1,0 dB en Federal). Su causa no está documentada.
- VH queda siempre más abajo que VV. Lo más probable es la remoción del ruido térmico, que pesa más cuanto más débil es la señal. No está verificado cómo trata el ruido el RTC del Planetary Computer.
- Consecuencia práctica: **nunca** calcule un cambio (Δ) entre una fecha procesada en SNAP y otra del RTC. Una diferencia de 1 a 3 dB entre cadenas de proceso es del mismo orden que la señal que se busca. Todas las fechas de una serie se procesan con la misma cadena.
- Las cárcavas de Bovril son más angostas que el píxel de 30 m del Copernicus DEM: el aplanado no las ve y no las corrige. Si usa este producto en la textura del paso 3, procese todas las fechas con la misma cadena.

**Errores típicos.**

- SNAP se queda en `Apply Orbit File` o en `Terrain Flattening` sin avanzar: está bajando la órbita o el DEM. Sin internet no puede; conéctese y repita.
- `Terrain Flattening` rechaza la entrada: la calibración no dejó la banda β⁰. Repita `Calibrate` con `Output beta0 band`.
- Falta de memoria o un proceso de horas: no recortó antes del aplanado. Haga el `Subset` antes.
- El producto no cubre el sitio: el recorte se definió por píxeles. Use la pestaña `Geo Coordinates`.
- QGIS no abre el `.zip`: es normal, el original es para SNAP. En QGIS use `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\QGIS_GeoTIFF`.

Fuente: ESA Copernicus, Sentinel-1A IW GRDH, 17/09/2023, S1A_IW_GRDH_1SDV_20230917T091449_20230917T091514_050365_061067_C33B. Distribuido por ASF DAAC, https://search.asf.alaska.edu. Procesado con ESA SNAP y Copernicus DEM GLO-30.

## Cierre

Responda `07_Preguntas_y_entrega/preguntas.md`. Controle las bitácoras de
`05_Resultados/06_Control_calidad/`: `Tp8_01_suelo_desnudo.log`,
`Tp8_02_textura.log`, `Tp8_03_susceptibilidad.log`.
