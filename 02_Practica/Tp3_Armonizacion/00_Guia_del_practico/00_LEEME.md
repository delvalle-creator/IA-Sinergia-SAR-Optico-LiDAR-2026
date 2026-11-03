# Tp3 — Guía paso a paso

Martes, 9 a 12 h. Sitio: `A2_IBICUY`. Caso de control: `F_BOVRIL` (NovaSAR 47974).

Cada paso dice: **(a)** qué se hace y por qué, **(b)** dónde, **(c)** la orden o los
menús exactos, **(d)** lo que muestra la pantalla, **(e)** cómo saber si salió bien y **(f)** los
errores típicos.

Los tres requisitos que se comprueban en este práctico, y en qué paso:

| Requisito de la fusión | Paso |
|---|---|
| Misma grilla | 1 (se construye) y 2 (se mira) |
| Corregistro < 1 píxel | 3 |
| Fechas compatibles | 1 (entre sensores) y 4 (entre cada huella LiDAR y cada capa) |

**Landsat 8 y 9.** Escenas de este práctico, la pasada más cercana a cada Sentinel-2 con el sitio cubierto y despejado: Ibicuy, `A2_IBICUY_L8_20260915`: Landsat 8 del 15/09/2026 para el Sentinel-2 del 16/09/2026.

Son Colección 2, Nivel 2 de USGS (reflectancia y temperatura de superficie, píxel de 30 m), bajadas del Planetary Computer. **Ejercicio optativo del paso 3:** medir si el Landsat 8 y el Sentinel-2 de 1 día de diferencia están corregistrados (ver el paso 3). Están en `02_Subsets_SNAP_QGIS\SNAP_DIMAP` y `QGIS_GeoTIFF`, con las bandas `SR_B1` a `SR_B7` (reflectancia), `ST_B10` (temperatura, K), `ST_QA`, `QA_PIXEL` y las virtuales `NDVI` y `ST_B10_C` (°C).

Landsat 9 da imágenes desde el 31/10/2021; antes sólo hay Landsat 8. Los dos llevan instrumentos gemelos (OLI y TIRS) y se comparan entre sí sin ajuste. Con Sentinel-2 no: el píxel es de 30 m contra 10 y 20 m, y las bandas no coinciden del todo (el infrarrojo cercano de Landsat, 865 nm, equivale a la B8A, no a la B08).

Fuente: USGS / NASA, Landsat 8 y Landsat 9 OLI/TIRS, Colección 2 Nivel 2, distribuido por Microsoft Planetary Computer, https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2

**Fusión Landsat + Sentinel-2.** El Landsat también viene afinado a 10 m con el detalle espacial del Sentinel-2 de la fecha más cercana: se lo interpola a la grilla de 10 m y se le suma el detalle fino de la banda Sentinel-2 de 10 m que más se le parece, escalado por una regresión entre los dos sensores (filtro pasa-altos con modulación por regresión, HPF). Trae las bandas `SR_B1` a `SR_B7` en reflectancia, `mascara_detalle` (1 = se agregó detalle; 0 = nube, sombra o falta de dato en alguna de las dos) y el `NDVI` virtual; el método y la calidad de cada banda están en los metadatos.

Este producto afinado **no entra al cubo de 20 m**: es justamente el tipo de afinado que el Tp3 evita en una fusión de píxel (lleva un sensor de 30 m a 10 m con el detalle de otro). Se trae para mirar y para comparar con el pansharpening del CBERS-4A. El control es el ERGAS: la imagen afinada se lleva de nuevo a 30 m y se compara con el Landsat original; por debajo de 3 la fusión es buena. Sirve para mirar e interpretar, con tres cuidados: un cambio real entre las dos fechas aparece como detalle falso; las bandas 6 y 7 (infrarrojo de onda corta) toman el detalle de una banda de 10 m de otra región del espectro y son las menos confiables; y la temperatura no se afina.

En este práctico: `A2_IBICUY_L8_20260915_fusion_S2_20260916_10m`: 1 día entre las dos imágenes; ERGAS 1,28.

**Pléiades y Pléiades Neo de CONAE.** Referencia visual de muy alta resolución del casco urbano (Pléiades, 0,5 m; Pléiades Neo, 0,3 m), 2022-2023, del proyecto Impactar de CONAE. Es un servicio de mapas y necesita internet: en `02_Subsets_SNAP_QGIS\Pleiades_CONAE_WMS` hay un `.xml` por localidad que se arrastra a QGIS (instrucciones en el `LEEME.md` de esa carpeta). Sirve para mirar y digitalizar, no para calcular: es RGB color real, sin infrarrojo ni reflectancia, y la fecha exacta no está publicada, sólo el año.

En este práctico: Ibicuy, Pléiades 2023 (`Ibicuy_2023_Pleiades_CONAE.xml`).

Fuente: CONAE, proyecto Impactar; Pléiades y Pléiades Neo, Airbus Defence and Space. Servicio WMS: https://geotematico01.conae.gov.ar/geoserver/wms; catálogo: https://catalogos.conae.gov.ar/catalogo/catalogoGeoServiciosOGC.html

**CBERS-4A, cámara WPM (INPE).** Pancromática de 2 m y multiespectral de 8 m (azul, verde, rojo e infrarrojo cercano), producto L4 ortorrectificado, en números digitales. Cada escena viene en dos productos: `..._MS_8m` (las cuatro bandas originales) y `..._pansharpened_2m` (la pancromática y las cuatro bandas afinadas a 2 m por Brovey ponderado, el método por defecto de GDAL). Es un pansharpening clásico: pancromática y multiespectral del mismo satélite y del mismo instante; compárelo con la fusión Landsat + Sentinel-2, que combina dos sensores y dos fechas. El control es el mismo ERGAS (por debajo de 3, bueno). Los números digitales no son reflectancia y el Brovey altera la radiometría: sirve para mirar y digitalizar, no para calcular índices. Cubre una zona de 12 a 21 km, no el sitio entero, y la escena se eligió a ojo, sin nubes, porque el catálogo del INPE no informa la nubosidad.

En este práctico: Ibicuy, `A2_IBICUY_CBERS4A_IBICUY_20260910_...`: 10/09/2026, 6 días antes del Sentinel-2; ERGAS 1,11.

Fuente: INPE / CAST, CBERS-4A WPM L4, licencia CC BY 4.0. Catálogo STAC del INPE, colección CB4A-WPM-L4-DN-1, https://data.inpe.br/stac/browser/collections/CB4A-WPM-L4-DN-1

**Embeddings anuales AlphaEarth Foundations (Google y Google DeepMind).** 64 números por píxel de 10 m que resumen un año entero de Sentinel-1, Sentinel-2, Landsat, GEDI, clima y otras fuentes, aprendidos por un modelo de inteligencia artificial. Las dimensiones (`A00` a `A63`) no tienen significado físico propio: sirven para clasificar con pocas muestras, buscar zonas parecidas y detectar cambios entre años. Vienen en enteros de 8 bits tal como los entrega Google (`..._AlphaEarth_embeddings_<año>_10m`); para pasarlos a valores reales, valor = signo(DN) × (DN / 127,5)², y −128 es sin dato. El `..._CP1_CP2_CP3_RGB_8bit.tif` muestra las tres primeras componentes principales para mirar en QGIS; sus colores no tienen significado fijo. Resumen un año, no una fecha; 2026 todavía no existe y se usa 2025, el último.

En este práctico: Ibicuy, 2025 (en lugar de 2026).

Fuente: The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind (CC BY 4.0). Copia en Source Cooperative (Taylor Geospatial), https://source.coop/tge-labs/aef

**BIOMASS en banda P (ESA).** El primer radar satelital en banda P: 435 MHz, unos 69 cm de longitud de onda, cuatro polarizaciones. La onda larga atraviesa el follaje y responde a troncos y ramas gruesas. En `02_Subsets_SNAP_QGIS\QGIS_GeoTIFF` vienen `A2_IBICUY_BIOMASS_P_20261005` (nivel L1B DGM del 05/10/2026, γ⁰ HH, HV, VH y VV en lineal, sin proyectar; se ubica con sus puntos de enlace) y, del nivel L2A, la altura del bosque `..._FH_20251123_1205` y la retrodispersión con el suelo cancelado `..._GN_20251123_1205` (pila del 23/11 al 05/12/2025, píxel de unos 90 m). La pila del Tp2 ya trae la banda P en la grilla del sitio (`P_BIOMASS_gamma0_HH` y `P_BIOMASS_gamma0_VH`), y el cubo del paso 1 la hereda. Resolución: con 6 MHz de ancho de banda, unos 25 m en rango oblicuo y unos 50 a 60 m en rango de terreno (incidencia de 27 a 29° en Ibicuy); el L1B DGM viene muestreado más fino (25 × 22 m). En el cubo de 20 m queda sobremuestreada. Como cruzada se usa la **VH**: la HV de estos productos trae interferencia de radiofrecuencia (emisiones terrestres que comparten los 435 MHz) que ESA detectó y no corrigió (`rfiDetectionFlag = true`, `rfiCorrectionFlag = false` en los metadatos). En un radar monoestático, por reciprocidad, HV y VH tienen la misma retrodispersión; la VH llega limpia.

Fuente: ESA, BIOMASS banda P (435 MHz), L1B DGM y L2A FP_FH y FP_GN; ESA MAAP, https://catalog.maap.eo.esa.int

**MapBiomas Argentina.** Mapas anuales de cobertura y uso del suelo de 1985 a 2025 a 30 m, hechos con Landsat por la red MapBiomas, y productos derivados: pérdida y vegetación secundaria (1987–2025) y área quemada de MapBiomas Fuego (1999–2025). En `QGIS_GeoTIFF`: `A2_IBICUY_MapBiomas_cobertura_1985_2025.tif` (una banda por año; el `.qml` con la leyenda oficial se carga solo en QGIS, sobre la banda 41 = 2025), `..._perdida_veg_1987_2025` (con su `.qml`) y `..._fuego_anual_1999_2025`, `..._fuego_frecuencia_1999_2025`, `..._fuego_mes_...` y `..._fuego_ultimo_anio_2025`. Es un producto de terceros, óptico, y sirve de **contexto**: qué cubiertas hay y cómo cambiaron, no la verdad del terreno. Cubre Entre Ríos: las islas de la provincia de Buenos Aires, al sur del Paraná Guazú, quedan sin dato (el 26 % de `A2_IBICUY`).

Fuente: Proyecto MapBiomas Argentina, Colección 3 de los mapas anuales de cobertura y uso del suelo y Colección 1 de MapBiomas Fuego, https://argentina.mapbiomas.org

**ESA CCI Biomass.** Biomasa aérea (AGB, en Mg/ha) y su desvío (AGB_SD), a unos 100 m, para 2010, 2015, 2020, 2021 y 2024, estimada con radar en banda C y L. `A2_IBICUY_CCI_Biomass_v7_AGB.tif` tiene diez bandas: AGB de cada año y su desvío. Resume un año, no una fecha, y no es independiente del radar: se usa como contexto, no como verdad.

Fuente: Santoro, M. y Cartus, O. (2026). ESA Biomass Climate Change Initiative (Biomass_cci), v7.0, NERC EDS CEDA, https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903

---

## Paso 0 — Entorno y huellas LiDAR del sitio (AUXILIAR)

**(a)** `Tp3_03` lee las huellas válidas de `lidar_<SITIO>.gpkg`, que escribe el Tp1.
En el Tp1 se trabajó Concordia; para Ibicuy hay que contar las huellas de los granulos
que el docente dejó bajados. No hace falta red: sólo se leen los `.h5`.

**(b)** Miniforge Prompt.

**(c)**

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp3_Armonizacion\03_Scripts
python ..\..\Tp1_Convergencia\03_Scripts\Tp1_05_buscar_lidar.py --sitio A2_IBICUY --solo_contar
```

**(d)** `GEDI L2A: N huellas en el sitio, M validas (...%)`, los descartes por motivo,
y el resumen de ATL08 (segmentos, con canopia válida, con terreno válido).

**(e)** Existe `Tp1_Convergencia\05_Resultados\03_Vectores\lidar_A2_IBICUY.gpkg` con
las capas `gedi_l2a` y `atl08`.

**(f)** Errores típicos:

- `No hay granulos descargados`: los `.h5` no están en `<ORIGINALES>\LIDAR\A2_IBICUY\`.
  Defina `set CURSO_SAR_ORIGINALES=<carpeta>` si están en otro lado; si no existen, el
  paso 4 no se puede hacer y se declara.
- En un humedal muchas huellas se descartan por agua o por baja sensibilidad: es
  esperable, no un error.

---

## Paso 1 — El cubo común (SE CORRE)

**(a)** Se llevan a **una** grilla el radar (la pila del Tp2), el óptico (Sentinel-2
L2A) y, si se pide, el modelo de elevación (Copernicus DEM GLO-30). Las decisiones que
el programa toma y declara en la bitácora:

1. **La grilla toma el espaciado más grueso de los productos que se fusionan a nivel de
   píxel** (`--pixel`, 20 m por defecto: NISAR y B11-B12). Trabajar a 10 m inventa un
   detalle que esos sensores no midieron. Los más gruesos que entran igual (el MDE de
   30 m y la banda P de unos 50 a 60 m) quedan **sobremuestreados**: la bitácora y las
   columnas `resolucion_nativa_m` y `remuestreo` de `<SITIO>_cubo_20m_bandas.csv` lo
   declaran, y no se interpretan en detalles menores que su resolución. Los que no entran
   (CCI, FH, MapBiomas) se muestrean en su grilla (paso 6).
2. **El radar se agrega en lineal** (promedio de potencia), nunca en dB.
3. **La reflectancia se promedia; la SCL se agrega por mayoría** (moda). Los píxeles
   con nube, sombra, cirro, saturados o sin dato según la SCL quedan sin dato en
   **todas** las bandas ópticas. Válidas: clases 4 (vegetación), 5 (suelo desnudo),
   6 (agua), 7 (sin clasificar) y 11 (nieve). La bitácora informa cuánto aporta cada
   una: la 7 puede ser borde de nube y la 11 es imposible en el Delta; con
   `--excluir_scl7` la 7 queda sin dato. El 16/09/2026 la clase 7 es el 9,1 % del sitio
   (vegetación oscura de los bajos) y la 11 no aparece.
4. **Las bandas de 20 m de Sentinel-2 (B11, B12) no se «afinan»** a 10 m.
5. **Desplazamiento de +1000 de Sentinel-2:** desde la línea de base 04.00 (25/01/2022)
   los números digitales L2A traen un desplazamiento de +1000. El código lo descuenta
   leyendo la línea de base de los metadatos de cada escena; sin eso, una escena de
   2020 y otra de 2023 no son comparables.

Bandas ópticas del cubo: B02, B03, B04, B08, B11, B12, como reflectancia de 0 a 1.
Bandas de radar: las de la pila del Tp2, incluida la banda P de BIOMASS
(`P_BIOMASS_gamma0_HH` y `P_BIOMASS_gamma0_VH` del 05/10/2026; la HV no entra, ver arriba).

**(b)** Miniforge Prompt (necesita red para Sentinel-2 y el MDE).

**(c)** Use la fecha de una Sentinel-2 `candidata` sobre Ibicuy (paso 0 del Tp2), lo
más cerca posible de la fecha del radar. Ejemplo:

```
python Tp3_01_cubo_comun.py --sitio A2_IBICUY --fecha_optico 2026-09-16 --pixel 20 --mde
```

Sin `--mde`, el cubo no lleva modelo de elevación. Sin `--fecha_optico`, no lleva óptico.

Caso de control (requiere haber corrido en el Tp2
`python Tp2_01_pila_multibanda.py --sitio F_BOVRIL --novasar 47974 --fecha_c 2023-09-17`;
el Sentinel-1 RTC de Bovril tiene pasadas el 05, el 17 y el 29/09/2023, no el 14/09, que
es la fecha de la NovaSAR):

```
python Tp3_01_cubo_comun.py --sitio F_BOVRIL --fecha_optico 2023-09-10 --pixel 20
```

**(d)** `Grilla comun: EPSG:32721, pixel 20 m, columnas x filas`; la regla aplicada;
una línea por capa de radar con su fecha y % con dato (en Ibicuy, catorce: Sentinel-1 RTC
y SNAP, NISAR L de tres fechas, NISAR S y BIOMASS P HH y VH, esta última con 99,8 %); `optico Sentinel-2 <fecha>: N
teselas, X % de pixeles utiles (SCL)`; el MDE si se pidió; y la tabla «Diferencia de
fecha entre sensores».

**(e)** Controles:

- En `<SITIO>_cubo_20m_bandas.csv` cada capa tiene `sensor`, `fecha`, `unidad`
  (`gamma0 lineal`, `sigma0 lineal`, `reflectancia 0-1`, `m sobre EGM2008`) y
  `fuente`.
- Las capas ópticas tienen el mismo `pixeles_validos_%` entre sí (la máscara SCL es
  común a todas).
- La diferencia de días entre el óptico y el radar figura en
  `<SITIO>_diferencias_de_fecha.csv`.

**(f)** Errores típicos:

- `No existe la pila del Tp2`: el cubo se arma sin radar. Corra el Tp2 con el mismo
  `--sitio`.
- `No hay Sentinel-2 L2A el <fecha> sobre el sitio`: no hay pasada ese día; busque la
  fecha con `Tp1_03`.
- Un óptico con pocos píxeles útiles: había nubes en el sitio. Cambie de fecha y
  declárelo; no use una escena nublada «porque es la del mismo día».
- Una banda de SNAP sin fecha en la tabla de diferencias: en el Tp2 se pasó con
  `--extra` sin `|sensor|lambda_cm|AAAA-MM-DD`. Vuelva a armar la pila del Tp2 con la
  fecha y después el cubo.

---

## Paso 2 — Mirar el cubo (EN QGIS)

**(a)** Antes de medir, se mira: que todas las capas estén en la misma grilla, que el
óptico y el radar muestren las mismas costas y caminos, y dónde quedó la máscara de
nubes.

**(b)** QGIS.

**(c)**

1. `Capa > Añadir capa > Añadir capa ráster...` y elija
   `Tp3_Armonizacion\02_Subsets_SNAP_QGIS\A2_IBICUY_cubo_20m.tif`. Agréguelo **dos
   veces**.
2. Primera copia, óptico en color natural: Propiedades > **Simbología** > **Color
   multibanda**; Rojo = `OPT_S2_B04`, Verde = `OPT_S2_B03`, Azul = `OPT_S2_B02`;
   **Configuración de valores Mín/Máx** > «Corte del conteo acumulado» 2–98 %.
3. Segunda copia, una banda de radar en gris: **Gris monobanda**, banda
   `L_NISAR_gamma0_HV_<fecha>` (o la que tenga), Mín/Máx 2–98 %.
4. Ponga el radar arriba y, en Propiedades > **Transparencia**, baje la **Opacidad**
   al 50 %; o active y desactive la capa para comparar.
5. Propiedades > **Información**: CRS, tamaño de píxel, número de bandas y sus nombres.

**(d)** Los cursos de agua, las lagunas y los caminos en el mismo lugar en las dos
capas; los huecos de la máscara SCL (nubes) en negro o transparentes en el óptico.

**(e)** Mida con **Medir línea** (menú Ver > Medir > Medir línea; en QGIS 3.44 el atajo Ctrl+Mayús+M puede abrir los marcadores espaciales) la distancia entre una costa en el
óptico y la misma costa en el radar. Si a simple vista hay más de un píxel (20 m), el
paso 3 lo va a confirmar.

**(f)** Errores típicos:

- Ver el radar «negro»: está en lineal; ajuste Mín/Máx a 2–98 %.
- Confundir una diferencia de fecha con un error de corregistro: si el agua subió entre
  la toma óptica y la de radar, la costa se movió de verdad.

---

## Paso 3 — Medir el corregistro (SE CORRE)

**(a)** Óptico y radar no se parecen pixel a pixel (uno mide color; el otro,
estructura), pero **los bordes coinciden**: costas, rutas, límites de lotes. Por eso
se comparan mapas de bordes (gradiente de Sobel), no valores. Antes, el radar se pasa a
dB y se suaviza con una ventana de 3 × 3 para atenuar el speckle; cada mapa de bordes
se normaliza (media 0, desvío 1). La **correlación de fase** entre los dos mapas da el
desplazamiento (dx, dy) con un paso de una décima de píxel; la incertidumbre se lee en
la dispersión entre ventanas. Se mide en **ventanas** (4 × 4 por defecto) y se informa
la **mediana**, la **dispersión** (desvío estándar de dx y de dy entre las ventanas
usadas) y el **rango** (máximo menos mínimo de la mediana de dy por fila de ventanas y
de dx por columna): un desplazamiento que cambia de una ventana a otra no es un
corrimiento rígido sino una deformación (relieve, puntos de enlace escasos) y no se
corrige con una traslación. Una ventana entra si su dx y su dy caen dentro de la mediana
± 3 MAD: es un criterio que no depende de cuánto mejora el ajuste.
Sólo se usan ventanas con al menos 80 % de dato en común en las dos capas
(`--min_comun 0.8`).

**(b)** Miniforge Prompt.

**(c)** Los nombres de capa se copian de `<SITIO>_cubo_20m_bandas.csv`.

Óptico frente a banda L:

```
python Tp3_02_medir_corregistro.py --sitio A2_IBICUY --pixel 20 --ref OPT_S2_B08 --mov L_NISAR_gamma0_HV_20260930
```

Banda L frente a banda S (el mismo satélite, dos radares):

```
python Tp3_02_medir_corregistro.py --sitio A2_IBICUY --pixel 20 --ref L_NISAR_gamma0_HH_20260930 --mov S_NISAR_gamma0_HH_20260930
```

Banda P frente al óptico y frente a la banda L (la banda P de BIOMASS se ubicó con los
puntos de enlace del producto L1B, no con un modelo de terreno: hay que medirla):

```
python Tp3_02_medir_corregistro.py --sitio A2_IBICUY --pixel 20 --ref OPT_S2_B08 --mov P_BIOMASS_gamma0_VH
python Tp3_02_medir_corregistro.py --sitio A2_IBICUY --pixel 20 --ref L_NISAR_gamma0_HV_20260930 --mov P_BIOMASS_gamma0_VH
```

Caso de control, NovaSAR frente a Sentinel-2 en Bovril:

```
python Tp3_02_medir_corregistro.py --sitio F_BOVRIL --pixel 20 --ref OPT_S2_B08 --mov S_NovaSAR_sigma0_HH
```

Opciones: `--ventanas 4` (por defecto; 4 × 4 = 16 ventanas; en sitios chicos, 3) y
`--min_comun 0.8` (fracción mínima de dato en común por ventana; bájela, por ejemplo a
0.5, si la capa móvil cubre poco el sitio, y declárelo).

Cada par deja su propia tabla y su propia bitácora, con el par en el nombre
(`<móvil>_vs_<referencia>`), de modo que los pares no se pisan:

- `05_Resultados\04_Tablas\<SITIO>_corregistro_<mov>_vs_<ref>.csv`, por ejemplo
  `A2_IBICUY_corregistro_L_NISAR_gamma0_HV_20260930_vs_OPT_S2_B08.csv`;
- `05_Resultados\06_Control_calidad\Tp3_02_<SITIO>_<mov>_vs_<ref>.log`.

**(d)** La tabla de ventanas (`ventana`, `dy_px`, `dx_px`, `corr_antes`,
`corr_despues`, `usada`, `mejora_bordes`): `usada` dice si la ventana entra (mediana ± 3
MAD); `corr_antes` y `corr_despues` son la correlación entre los dos mapas de bordes antes
y después de aplicar el desplazamiento medido en esa ventana, un dato de calidad. Después,
la mediana `dx = ... px (... m al este), dy = ... px en filas (... m al norte)`, la frase
con el sentido del movimiento («Hay que mover la capa móvil X m al ESTE y Y m al NORTE (la
imagen está corrida al oeste y al sur)»), el módulo, la dispersión, el rango por fila y
por columna, las mismas cifras con todas las ventanas, y el veredicto:

- `CUMPLE para fusion de pixel`: módulo de la mediana < 0,5 píxel, dispersión < 0,5 píxel
  en x y en y, y rango < 1 píxel;
- `CUMPLE para rasgo o decision`: módulo < 1 píxel, dispersión < 1 píxel y rango < 2
  píxeles (para una fusión de píxel hay que corregir antes el desfase y medir el residuo);
- `NO CUMPLE, no rigido`: la dispersión o el rango llegan a 1 o 2 píxeles; la bitácora
  da la mediana de dy por fila y de dx por columna. Si cambia de manera ordenada, hay un
  error de escala o de rotación que una traslación no corrige; la bitácora da igual la
  mediana como primera aproximación, o
- `NO CUMPLE, rigido`: el módulo pasa de 1 píxel con dispersión y rango chicos. Si la capa
  es NovaSAR, la bitácora da la orden lista para el Tp2: `--desplazamiento DX DY` (en
  metros).

El CSV de cada par guarda las ventanas y el resumen: `modulo_px`, `dispersion_x_px`,
`dispersion_y_px`, `rango_dx_columnas_px`, `rango_dy_filas_px`, `dx_m_este`,
`dy_m_norte`, `ventanas_usadas`, las cifras con todas las ventanas y `veredicto`.

**(e)** Criterio de aceptación: los dos niveles de arriba. El umbral de un píxel es
laxo para una fusión de píxel: para detectar cambios entre dos imágenes hacen falta 0,2 a
0,5 píxel (Townshend et al., 1992; Dai y Khorram, 1998). Referencias con datos reales del
curso:

- NISAR L y S sobre Ibicuy: los dos GCOV vienen geocodificados en la misma grilla:
  0,22 px con 8 ventanas (la banda S cubre el 58 % del sitio), dispersión 0,07 y 0,05 px:
  CUMPLE para fusión de píxel.
- Sentinel-1 RTC del Planetary Computer (`C_S1_...`): en Ibicuy y en Bovril, frente a
  Sentinel-2, a NISAR y al mismo Sentinel-1 procesado en SNAP en el Tp2, un corrimiento
  rígido de 0,75 a 1,0 píxel: hay que moverlo 15 a 20 m al **este** (la imagen está
  corrida al oeste). En Ibicuy, 0,82 px frente a Sentinel-2: CUMPLE sólo para rasgo o
  decisión; en Bovril, 1,02 px: NO CUMPLE, rígido. El Sentinel-1 procesado en SNAP
  (`C_SNAP_...`) no tiene ese corrimiento (0,28 px, CUMPLE para fusión de píxel): el
  desfase es del producto RTC, no del satélite.
- BIOMASS P VH sobre Ibicuy: frente a Sentinel-2 B08, hay que moverla 12 m al oeste y 6 m
  al norte (0,67 px; dispersión 0,14 y 0,16 px con 14 de 16 ventanas): CUMPLE para rasgo o
  decisión. Frente a NISAR L HV, 8 m al oeste y 4 m al norte (0,45 px): CUMPLE para fusión
  de píxel. Las correlaciones de bordes con el óptico son bajas (0,1 a 0,4: la banda P ve
  troncos y agua, poco del color), y con la banda L, altas (0,4 a 0,7).
- NovaSAR 47974 en Bovril (frente a Sentinel-2 y frente a NISAR L): hay que moverla unos
  **90 m al oeste y unos 480 m al sur** (dx ≈ −4,6 px, dy ≈ +24 px), y el veredicto es
  **NO CUMPLE, no rígido**: dy va de +28 px en la fila norte de ventanas a +18 px en la
  fila sur (rango de 10,5 px; dispersión 3,9 px). La componente este-oeste coincide con
  la presentación 02 (unos 80 m al oeste); la norte-sur no (allí, 20 m al norte), porque
  allí se usaron los 84 puntos de enlace del producto y aquí las cuatro esquinas. Si da
  CUMPLE, algo está mal en la medición.

**Signo: una regla y un ejemplo.**

| Lo que da `Tp3_02` | Lo que se hace | Dónde estaba la imagen |
|---|---|---|
| dx = +17 m (al este) | mover la capa 17 m al este | 17 m al oeste |
| dy = +6 m al norte | mover la capa 6 m al norte | 6 m al sur |

Antes de leer la respuesta, aplíquelo a la banda P frente a Sentinel-2 (dx = −0,60 px,
dy = −0,30 px en filas, píxel de 20 m): hay que moverla 12 m al oeste y 6 m al norte; la
imagen está corrida 12 m al este y 6 m al sur. En filas, un dy positivo baja (va al sur):
por eso la bitácora informa los metros al norte como −dy × píxel.

**Ejercicio optativo: Landsat 8 frente a Sentinel-2.** El Landsat 8 del 15/09/2026 está a
1 día del Sentinel-2. Se arma un cubo de 30 m con las dos bandas del infrarrojo cercano
(Landsat SR_B5 y Sentinel-2 B08, promedio de reflectancia) y se mide con
`--pixel 30 --ref OPT_S2_B08 --mov OPT_L8_SR_B5`. Resultado de referencia: hay que mover
el Landsat 15 m al este y 12 m al sur (0,64 px de 30 m, dispersión 0,07 y 0,05 px, rango
0,05 px): un corrimiento rígido; CUMPLE para rasgo o decisión.

**(f)** Errores típicos:

- `La capa X no esta en ...`: el nombre no es exacto. El mensaje lista las capas.
- `Ninguna ventana tiene 80 % de dato en comun`: las dos capas casi no se superponen
  (nubes, borde de franja). Pruebe con `--ventanas 2`, con `--min_comun 0.5` o con
  otra banda óptica.
- Usar como referencia una banda óptica con mucha máscara de nubes.
- Interpretar un NO CUMPLE entre óptico y radar en el río como error: si el agua cambió
  entre fechas, los bordes no son los mismos. Repita con una banda menos sensible al
  agua o en otra zona.
- **El desplazamiento medido no se aplica solo.** Para NovaSAR, copie la orden
  `--desplazamiento DX DY` que imprime la bitácora (con NovaSAR 47974 en Bovril:
  `--desplazamiento -92 -484`) y vuelva a armar la pila del Tp2 con ella (DX positivo =
  hacia el este, DY positivo = hacia el norte), después el cubo (paso 1) y después mida
  de nuevo:

  ```
  cd ..\..\Tp2_SAR_multibanda\03_Scripts
  python Tp2_01_pila_multibanda.py --sitio F_BOVRIL --novasar 47974 --fecha_c 2023-09-17 --desplazamiento DX DY
  cd ..\..\Tp3_Armonizacion\03_Scripts
  ```

  En SNAP se corregistra con `Radar > Coregistration`. Después de corregir, se vuelve
  a medir. Si el corrimiento era rígido, el par debe dar CUMPLE. Con NovaSAR 47974 la
  mediana baja a menos de un píxel (0,25 px) pero la dispersión sigue en 4 px (dy de +4 px
  al norte a −7 px al sur): la traslación corrigió el centro y no la escala. Ese par
  **no entra a una fusión de píxel**; para corregirlo hacen falta puntos de enlace y una
  transformación polinómica de orden 1 o mayor (en QGIS, `Ráster > Georreferenciador`,
  con puntos tomados sobre Sentinel-2 o NISAR). El mismo producto trae 84 puntos de
  enlace en su metadata.xml; con ellos el desfase es rígido (80 m al oeste y 20 m al
  norte) y una traslación lo corrige (Tp8, `--puntos_enlace todos --desplazamiento -80
  20`). Con las cuatro esquinas, la NovaSAR se usa sólo en fusión de decisión o en
  sinergia.

---

## Paso 4 — LiDAR en el cubo (SE CORRE)

**(a)** El LiDAR **no se rasteriza**: se lleva cada capa del cubo a cada huella
válida. Para GEDI, la media de los píxeles cuyo centro cae a menos de 12,5 m (radio de
la huella de 25 m) **más medio píxel** del centro de la huella; para ATL08, un rectángulo
de 100 m a lo largo de la traza por 14 m de ancho, orientado con el acimut de la traza,
más medio píxel por lado. Además marca la **plausibilidad** de cada huella (columna
`plausible`): no es plausible una huella GEDI con rh98 de más de 50 m o de una pasada
cuya mediana de rh98 supera 40 m (en Ibicuy, la pasada del 29/11/2020: 160 huellas con
91 m de mediana), ni un segmento ATL08 con más de 50 m. Los pasos siguientes usan sólo
`plausible = 1`. El radar se promedia en **lineal** y se agrega su
equivalente en dB en otra columna; el óptico, como media de reflectancias. Se guarda
cuántos píxeles entraron en cada media y la **diferencia de días** entre la huella y
cada capa: una huella de 2019 junto a un radar de 2026 no describe el mismo paisaje.

**(b)** Miniforge Prompt.

**(c)**

```
python Tp3_03_lidar_en_el_cubo.py --sitio A2_IBICUY --pixel 20
```

`--pixel` debe ser el mismo del cubo del paso 1 (busca `<SITIO>_cubo_<pixel>m.tif`).

**(d)** Por producto: las huellas válidas y la forma de extracción (círculo de 12,5 m
para GEDI, rectángulo de 100 × 14 m para ATL08); el total de huellas con valores del
cubo; la tabla «Plausibilidad» (en Ibicuy, 20.697 GEDI plausibles y 161 no plausibles:
160 de la pasada del 29/11/2020 y 1 con rh98 de más de 50 m; los 2.823 ATL08,
plausibles); los píxeles por huella (GEDI: 3 a 6, 4 en el 84 %; ATL08: 7 a 13, 10 de
mediana); y la mediana de la diferencia de días LiDAR-capa de las huellas plausibles.

**(e)** Controles:

- En `04_Tablas_de_trabajo\A2_IBICUY_huellas_con_cubo.csv`: columnas `producto`,
  `fecha_lidar`, `x`, `y`, `rh98`, `rh50` (GEDI), `h_canopy` (ATL08),
  `elev_lowestmode_elips` o `h_te_best_fit_elips`, `plausible` y `motivo_no_plausible`,
  y por cada capa el valor, `n_<capa>` y `dias_<capa>`; para el radar, además `<capa>_dB`.
- `n_<capa>` de GEDI a 20 m: pocos píxeles por huella (la huella es más chica que
  dos píxeles). Es esperable y se declara.
- Abra `05_Resultados\03_Vectores\A2_IBICUY_huellas_con_cubo.gpkg` (capa `huellas`)
  sobre el cubo: los puntos caen sobre la tierra firme y la vegetación, no en el río
  (las huellas sobre agua las descartó el Tp1_05: GEDI por la persistencia de agua de
  Landsat ≥ 50 %, ATL08 por su máscara de agua).

**(f)** Errores típicos:

- `No existe ... lidar_A2_IBICUY.gpkg`: falta el paso 0.
- Comparar `elev_lowestmode_elips` con `MDE_GLO30_m` directamente: la primera es
  **altura elipsoidal** (WGS 84) y la segunda está sobre el **geoide EGM2008**. En Entre
  Ríos la ondulación del geoide es de 16,9 m (EGM2008 en el sitio). Se convierte con
  `alturas_a_egm2008()` de `00_COMUN/funciones_lidar.py` antes de comparar.
- Usar huellas con `plausible = 0` (alturas de 91 m que los indicadores de calidad del
  producto no detectaron).
- Usar huellas con `dias_` de varios años como si fueran simultáneas.

---

## Paso 5 — Primera lectura conjunta (EN QGIS) — SINERGIA

**(a)** Con la tabla de huellas se mira cómo varían juntas la altura del dosel (rh98 o
`h_canopy`), la cruzada del radar y el óptico. No se ajusta ningún modelo: se
interpreta. Es **sinergia**: cada sensor aporta su variable y el analista las lee
juntas.

**(b)** QGIS (complemento DataPlotly) o una planilla de cálculo.

**(c)** `Complementos > Administrar e instalar complementos...`, busque **DataPlotly**
e instálelo. En su panel: tipo **Scatter Plot**, capa `huellas`, X = `rh98`,
Y = `L_NISAR_gamma0_HV_<fecha>_dB`; repita con la banda C (`..._VH_dB`), con la banda P
(`P_BIOMASS_gamma0_VH_dB`) y con `OPT_S2_B08`. Filtre `plausible = 1` (en DataPlotly,
el filtro de la capa) y, si quiere ver el efecto de la fecha, las huellas con
`dias_<capa>` grande. En Orange, el workflow `Tp3_A` trae el filtro de plausibles, las
cajas por clase de altura, el widget **Correlations** (Spearman entre la altura y cada
banda) y **Group By** (medianas por clase de altura).

**(d)** Nubes de puntos: una por banda.

**(e)** Lo esperable físicamente, a verificar y no a forzar: la cruzada de L sube con
la altura del dosel en un rango más amplio que la de C; el NDVI casi no cambia porque
mide el verdor del dosel y no su altura. La cruzada de P (VH) es la que más sube entre
el pajonal y el monte (en Ibicuy, de −28 dB en < 3 m a −17 dB en 5–10 m), con la misma correlación que L HV con rh98 (Spearman 0,50). Si
no se ve, se explica (pocas huellas, fechas lejanas, agua bajo el dosel, huella más
chica que el píxel).

**(f)** Graficar la columna lineal en lugar de la `_dB`: la nube se aplasta contra cero.

---

## Paso 5 bis — CCI Biomass en las huellas (EN QGIS)

**(a)** El CCI Biomass v7 (unos 100 m, EPSG:4326) es más grueso que el cubo y está en otro
sistema de coordenadas: **no se lleva a 20 m**. Se muestrea su valor en cada huella (la
huella de 25 m cae dentro de un píxel de 100 m) y, para compararlo con el radar, se
agrega el radar a la grilla del CCI.

**(b)** QGIS.

**(c)**

1. Cargue `02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\A2_IBICUY_CCI_Biomass_v7_AGB.tif` (banda 5,
   AGB 2024) y `05_Resultados\03_Vectores\A2_IBICUY_huellas_con_cubo.gpkg` encima.
2. `Procesos > Caja de herramientas` (Ctrl+Alt+T), busque «muestre» y abra
   `Análisis ráster > Muestra de valores ráster`.
3. Capa de entrada: `huellas`; Capa ráster: el CCI (se muestrean todas las bandas);
   Prefijo: `CCI_`; Muestreado: guardar en
   `05_Resultados\03_Vectores\A2_IBICUY_huellas_con_CCI.gpkg`. Ejecutar.
4. La capa nueva tiene las columnas `CCI_1` a `CCI_10`, en el orden de las bandas: AGB 2010,
   2015, 2020, 2021, 2024 y sus desvíos. `CCI_5` es AGB 2024.
5. Para comparar con el radar en la grilla del CCI: `Ráster > Alinear rásteres` con
   capa de referencia el CCI, método de remuestreo «Promedio», sobre la banda
   `L_NISAR_gamma0_HV_20260930` del cubo (en lineal); después se pasa a dB.

**(d)** La herramienta reproyecta cada punto al sistema del ráster y lee el píxel que lo
contiene, sin interpolar: 23.681 huellas, 102 fuera del recorte del CCI (AGB vacío).

**(e)** Mediana de AGB 2024 de 19 a 20 Mg/ha en las huellas de menos de 3 m y de 46 a
50 Mg/ha entre 5 y 20 m; Spearman entre rh98 y AGB, 0,25. `Tp3_05` hace el mismo muestreo
para las tablas de Orange.

**(f)** Errores típicos: remuestrear el CCI a 20 m (inventa detalle); compararlo con el
radar como si fuera independiente (el CCI se estimó con radar C y L).

---

## Paso 6 — Contexto de las huellas: MapBiomas, CCI Biomass, altura FH y banda P (SE CORRE + EN QGIS y ORANGE)

**(a)** Las huellas del paso 4 caen sobre un paisaje con historia. Este paso ubica el
sitio y cada huella en esa historia con tres productos que no entran al cubo porque
resumen años o tienen otra grilla: MapBiomas (cobertura 1985–2025, pérdida de
vegetación y área quemada), el CCI Biomass y la altura del bosque FH de BIOMASS L2A.
Además, la banda P (HH y VH) se resume por clase de MapBiomas. Sólo entran las huellas
con `plausible = 1`. El programa trabaja en la
grilla de MapBiomas (EPSG:4326, unos 30 m) y lleva a cada huella la clase de MapBiomas
2025, el AGB 2024 del CCI y la altura FH del píxel que la contiene, **sin agua**: los píxeles
de FH con más de la mitad de agua de MapBiomas 2025 (clases 26, 31 y 33) o con ocurrencia
JRC de 50 % o más quedan sin dato, y las huellas que caen en ellos también (columna
`FH_en_agua`). Sobre el agua la FH no es altura de bosque: sin la máscara, los ríos salen con 10 a 30 m
y la comparación con el LiDAR mide el agua, no el bosque; una causa posible es el doble
rebote agua–tallo.

**(b)** Miniforge Prompt, QGIS y Orange.

**(c)**

```
python Tp3_04_contexto_y_huellas.py --sitio A2_IBICUY --pixel 20
```

En QGIS, `Capa > Añadir capa > Añadir capa ráster...` y elija
`02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\A2_IBICUY_MapBiomas_cobertura_1985_2025.tif`: el
estilo `.qml` de al lado se carga solo, con la leyenda oficial, sobre la banda 41 (2025).
Agregue encima `05_Resultados\03_Vectores\A2_IBICUY_huellas_con_cubo.gpkg`. Lo mismo con
`A2_IBICUY_BIOMASS_P_FH_20251123_1205_sin_agua.tif` (banda 1) en `Pseudocolor monobanda` de 0 a 30 m. En
Orange abra `08_Orange\Tp3_C_contexto_de_las_huellas.ows`.

**(d)** La bitácora `Tp3_04_A2_IBICUY_contexto.log` informa:

- `MapBiomas cubre 30254 ha de 41108 (73.6 %)`, es decir 30.254 ha de 41.108 (73,6 %):
  las islas bonaerenses quedan fuera.
- La cobertura de 1985 y de 2025: herbáceas inundables de 81,4 a 84,0 %, ríos 9 %,
  herbáceas 4 %; bosques cerrados de 1,5 a 0,6 %.
- La pérdida de vegetación 1987–2025: 123 ha de primaria, casi nada.
- El área quemada 1999–2025: 37.442 ha acumuladas; quemado al menos una vez, el 48,2 %
  del área con dato; los años con más fuego, 2008 (10.407 ha), 2022 y 2021.
- `Altura FH: se enmascara el agua de MapBiomas 2025 (clases 26, 31 y 33) o JRC ocurrencia >= 50 % (12.8 % de los pixeles con FH)`.
- Una tabla por clase de 2025 con las medianas del CCI, la altura FH (sin agua) y su
  calidad, y P HH y P VH en dB.

La bitácora `Tp3_04_A2_IBICUY.log` informa las huellas por clase de MapBiomas (n, altura
LiDAR, CCI y FH medianos) y la comparación de la altura LiDAR con la FH: Spearman y
mediana de FH − LiDAR, para todas las huellas fuera del agua y para las de calidad FH ≥ 50;
antes, `649 huellas en agua quedan sin FH`.

Salidas: en `05_Resultados\04_Tablas`, `A2_IBICUY_mapbiomas_area_por_clase_y_anio.csv`,
`..._mapbiomas_perdida_por_anio.csv`, `..._mapbiomas_fuego_por_anio.csv`,
`..._contexto_por_clase.csv`, `..._contexto_pixeles_muestra.csv` y
`..._huellas_por_clase_MapBiomas.csv`; en `05_Graficos`, `..._mapbiomas_area_por_clase.png`,
`..._mapbiomas_perdida_y_fuego_por_anio.png` y `..._altura_LiDAR_frente_a_FH.png`; en
`04_Tablas_de_trabajo`, `A2_IBICUY_huellas_con_contexto.csv` (la tabla del paso 4 más
`altura_LiDAR_m`, `clase_MapBiomas_2025`, `CCI_AGB_2024`, `FH_m`, `FH_calidad` y `FH_en_agua`).

**(e)** Controles (las huellas por clase: herbáceas inundables 15.603, ríos 221; el resto
como en el Desarrollo):

- Bosques cerrados: CCI de 63 Mg/ha y P VH de −15,2 dB (medianas); herbáceas
  inundables: CCI de 23 Mg/ha y P VH de −27,7 dB; ríos: CCI 0 y P VH de −32,8 dB.
- Las huellas en bosques cerrados y abiertos tienen 5,3 y 5,7 m de altura LiDAR
  mediana; las de herbáceas, 2,5 a 2,7 m.
- La altura FH de BIOMASS, con el agua enmascarada, no pasa el control: no sigue a la
  altura LiDAR (Spearman −0,12 en 22.899 huellas plausibles; con calidad ≥ 50, −0,03 en
  2.386), da 9 a 12 m
  sobre el pajonal y las herbáceas y 5,5 m en los bosques. En este sitio no se usa.

**(f)** Errores típicos:

- Tomar MapBiomas como verdad: es una clasificación de Landsat de 30 m; el monte
  ribereño angosto (una o dos filas de sauces) cae en herbáceas inundables.
- Leer «sin dato» como una clase: son las 6.159 huellas de las islas bonaerenses.
- Usar la HV de BIOMASS como cruzada.
- Comparar el CCI con el radar del curso como si fueran independientes: el CCI se
  estimó con radar C y L.

---

## Al terminar

Corra `Tp3_05_tablas_para_Orange.py --sitio A2_IBICUY` para que los workflows de Orange
lean sus propias salidas. Complete la tabla de los tres requisitos de
`01_Prompt_IA/04_Verificacion/verificacion_resultados.md` (con los pares nuevos de la
pregunta 12) y su tabla de verificación. En
`05_Resultados/06_Control_calidad/` debe haber `Tp3_01_<SITIO>.log`,
`Tp3_02_<SITIO>_<mov>_vs_<ref>.log` (una por par), `Tp3_03_<SITIO>.log`,
`Tp3_04_<SITIO>_contexto.log`, `Tp3_04_<SITIO>.log` y `Tp3_05_<SITIO>.log`. Conteste
`07_Preguntas_y_entrega/preguntas.md`.
