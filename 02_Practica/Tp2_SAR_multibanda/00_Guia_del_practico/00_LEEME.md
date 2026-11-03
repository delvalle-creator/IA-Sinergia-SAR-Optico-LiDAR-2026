# Tp2 — Guía paso a paso

Lunes, 14 a 18 h. Sitio: `A2_IBICUY` (alternativa: `DELTA_NISAR`).

Cada paso dice: **(a)** qué se hace y por qué, **(b)** dónde, **(c)** la orden o los
menús exactos, **(d)** qué muestra la pantalla, **(e)** cómo saber si salió bien y **(f)** los
errores típicos.

La regla de unidades del curso, que atraviesa todo el práctico: **el radar se guarda y
se opera en γ⁰ LINEAL (potencia). El dB es para ver y para umbralizar. Todo promedio,
remuestreo o diferencia se calcula en lineal.** Promediar en dB sesga hacia valores
bajos, porque el logaritmo del promedio no es el promedio de los logaritmos.

**Landsat 8 y 9.** Escenas de este práctico, la pasada más cercana a cada Sentinel-2 con el sitio cubierto y despejado: Ibicuy, `A2_IBICUY_L8_20260915`: Landsat 8 del 15/09/2026 para el Sentinel-2 del 16/09/2026.

Son Colección 2, Nivel 2 de USGS (reflectancia y temperatura de superficie, píxel de 30 m), bajadas del Planetary Computer. Están en `02_Subsets_SNAP_QGIS\SNAP_DIMAP` y `QGIS_GeoTIFF`, con las bandas `SR_B1` a `SR_B7` (reflectancia), `ST_B10` (temperatura, K), `ST_QA`, `QA_PIXEL` y las virtuales `NDVI` y `ST_B10_C` (°C).

Landsat 9 da imágenes desde el 31/10/2021; antes sólo hay Landsat 8. Los dos llevan instrumentos gemelos (OLI y TIRS) y se comparan entre sí sin ajuste. Con Sentinel-2 no: el píxel es de 30 m contra 10 y 20 m, y las bandas no coinciden del todo (el infrarrojo cercano de Landsat, 865 nm, equivale a la B8A, no a la B08).

Fuente: USGS / NASA, Landsat 8 y Landsat 9 OLI/TIRS, Colección 2 Nivel 2, distribuido por Microsoft Planetary Computer, https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2

**Fusión Landsat + Sentinel-2.** El Landsat también viene afinado a 10 m con el detalle espacial del Sentinel-2 de la fecha más cercana: se lo interpola a la grilla de 10 m y se le suma el detalle fino de la banda Sentinel-2 de 10 m que más se le parece, escalado por una regresión entre los dos sensores (filtro pasa-altos con modulación por regresión, HPF). Trae las bandas `SR_B1` a `SR_B7` en reflectancia, `mascara_detalle` (1 = se agregó detalle; 0 = nube, sombra o falta de dato en alguna de las dos) y el `NDVI` virtual; el método y la calidad de cada banda están en los metadatos.

El control es el ERGAS: la imagen afinada se lleva de nuevo a 30 m y se compara con el Landsat original; por debajo de 3 la fusión es buena. Sirve para mirar e interpretar, con tres cuidados: un cambio real entre las dos fechas aparece como detalle falso; las bandas 6 y 7 (infrarrojo de onda corta) toman el detalle de una banda de 10 m de otra región del espectro y son las menos confiables; y la temperatura no se afina.

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

**BIOMASS en banda P (ESA).** El primer radar satelital en banda P: 435 MHz, unos 69 cm de longitud de onda, cuatro polarizaciones. La onda larga atraviesa el follaje y responde a troncos y ramas gruesas: es la banda que más separa un monte de un pajonal. En `02_Subsets_SNAP_QGIS\SNAP_DIMAP` y `QGIS_GeoTIFF` vienen tres productos:

- `A2_IBICUY_BIOMASS_P_20261005`: nivel L1B DGM del 05/10/2026 (cinco días después del NISAR del 30/09), con `Gamma0_HH`, `Gamma0_HV`, `Gamma0_VH` y `Gamma0_VV` en lineal (la `Gamma0_HV` trae interferencia de radiofrecuencia sin corregir: como cruzada se usa la `Gamma0_VH`; ver paso 4), el ángulo de incidencia y las bandas virtuales en dB. γ⁰ = (amplitud de β⁰)² × tan(incidencia), sobre el elipsoide. El GeoTIFF **no está proyectado**: está en geometría de rango en el terreno y se ubica con 121 puntos de enlace (QGIS y SNAP lo ubican solos). `Tp2_01` lo reproyecta a la grilla común con esos puntos (paso 4).
- `A2_IBICUY_BIOMASS_P_FH_20251123_1205` (altura del bosque) y `..._GN_...` (retrodispersión con el suelo cancelado): nivel L2A, de una pila de pasadas del 23/11 al 05/12/2025, píxel de unos 90 m. El producto de altura sólo vale sobre bosque: sobre pajonal y agua da números sin sentido. Por eso se usa **sin agua**: `..._FH_20251123_1205_sin_agua.tif` deja sin dato los píxeles con más de la mitad de agua en MapBiomas 2025 (clases 26, 31 y 33) o con ocurrencia JRC de 50 % o más. Se usa en el Tp3.
- `DELTA_NISAR_BIOMASS_P_...`: cuatro fechas sobre el Delta medio; la del 29/09/2026 está a un día del NISAR del 30/09.

Fuente: ESA, BIOMASS banda P (435 MHz), L1B DGM y L2A FP_FH y FP_GN; ESA MAAP, https://catalog.maap.eo.esa.int

**MapBiomas Argentina.** Mapas anuales de cobertura y uso del suelo de 1985 a 2025 a 30 m, hechos con Landsat por la red MapBiomas, y productos derivados: pérdida de vegetación natural (1987–2025) y área quemada (1999–2025). En `QGIS_GeoTIFF`: `A2_IBICUY_MapBiomas_cobertura_1985_2025.tif` (una banda por año; el `.qml` con la leyenda oficial se carga solo en QGIS), `..._perdida_veg_1987_2025` y `..._fuego_...`. Es un producto de terceros, óptico, y sirve de **contexto**: qué cubiertas hay y cómo cambiaron, no la verdad del terreno. Cubre Entre Ríos: el sector de Ibicuy al sur del Paraná Guazú (provincia de Buenos Aires) queda sin dato, el 30 % del sitio.

Fuente: Proyecto MapBiomas Argentina, Colección 3 de los mapas anuales de cobertura y uso del suelo y Colección 1 de fuego, https://argentina.mapbiomas.org

**ESA CCI Biomass.** Biomasa aérea (AGB, en Mg/ha) y su desvío (AGB_SD), a unos 100 m, para 2010, 2015, 2020, 2021 y 2024, estimada con radar en banda C y L. `A2_IBICUY_CCI_Biomass_v7_AGB.tif` tiene diez bandas: AGB de cada año y su desvío. En el Delta asigna biomasa también al pajonal y no es independiente del radar: se usa como contexto, no como verdad.

Fuente: Santoro, M. y Cartus, O. (2026). ESA Biomass Climate Change Initiative (Biomass_cci), v7.0, NERC EDS CEDA, https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903

---

## Paso 0 — Entorno, carpeta y fecha de la escena

**(a)** Los scripts necesitan el entorno `sar`. Además hay que saber qué día hay
Sentinel-1 sobre el sitio, para procesar en SNAP **la misma fecha** que después se
compara con el Sentinel-1 RTC del Planetary Computer (paso 8).

**(b)** Miniforge Prompt.

**(c)**

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp2_SAR_multibanda\03_Scripts
python ..\..\Tp1_Convergencia\03_Scripts\Tp1_03_buscar_optico_y_C.py --sitio A2_IBICUY --desde 2026-09-01 --hasta 2026-10-15
```

**(d)** La lista de Sentinel-1 RTC sobre Ibicuy, con fecha, órbita relativa, pasada y
`candidata` o `descartada`.

**(e)** Elija una fecha `candidata` y anótela: es `<FECHA_C>` en el resto de la
guía. Elija, si puede, la de la escena GRD que el docente dejó para SNAP: el
**26/09/2026** (Sentinel-1C, órbita relativa 68, descendente; cubre Ibicuy entero y
es la misma pasada que el RTC del Planetary Computer de ese día, 4 días antes de los
NISAR L y S del 30/09/2026). En el resto de la guía el ejemplo usa esa fecha.

**(f)** Si el Planetary Computer no responde, use 2026-09-26 (la escena GRD que dejó el
docente) y declare que el RTC no se pudo consultar: el paso 8 se hará entre fechas de
NISAR.

---

## Paso 1 — Sentinel-1 GRD a γ⁰ con el grafo (EN SNAP)

**(a)** El GRD trae números digitales. Para llegar a γ⁰ comparable hay que: aplicar la
órbita precisa (la geolocalización depende de ella), quitar el ruido térmico (que
levanta artificialmente la polarización cruzada en las zonas oscuras, como el agua),
calibrar a **β⁰** (no a σ⁰: el Terrain Flattening necesita β⁰ de entrada), recortar el
sitio, **normalizar a γ⁰ con el modelo de elevación** (Terrain Flattening: divide por
el área realmente iluminada, no por la de un plano) y proyectar al mapa (Range Doppler
Terrain Correction) en EPSG:32721 a 10 m, con la grilla alineada a la del curso. En el
Delta el relieve es suave, pero la cadena es la misma que en una barranca: así se
compara igual con igual. La descripción nodo por nodo está en
`09_Grafos_SNAP/LEEME_grafos.md`.

**(b)** SNAP.

**(c)**

1. `File > Open Product...` y elija la escena GRD:
   `00_COMUN\08_Originales_crudos\S1_CRUDO\S1C_IW_GRDH_1SDV_20260926T091407_20260926T091432_009616_013235_EE65.zip`
   (SNAP abre el `.zip` directamente; no hace falta descomprimirlo).
2. `Tools > GraphBuilder`. En la ventana, botón **Load** (abajo) y elija
   `Tp2_SAR_multibanda\09_Grafos_SNAP\Tp2_S1_GRD_a_gamma0.xml`. Aparecen los ocho
   nodos: Read → Apply-Orbit-File → ThermalNoiseRemoval → Calibration → Subset →
   Terrain-Flattening → Terrain-Correction → Write.
3. Pestaña **Read**: elija la escena abierta.
4. Pestaña **Subset**: marque **Geographic Coordinates** y pegue el polígono del sitio
   con un margen de 0,02° (el margen evita bordes sin dato después del Terrain
   Flattening):

   ```
   POLYGON((-59.32 -33.87, -59.08 -33.87, -59.08 -33.63, -59.32 -33.63, -59.32 -33.87))
   ```

   Para `DELTA_NISAR`:
   `POLYGON((-60.18 -33.85, -58.70 -33.85, -58.70 -32.94, -60.18 -32.94, -60.18 -33.85))`.
5. Pestañas **Terrain-Flattening** y **Terrain-Correction**. El Graph Builder de SNAP no
   toma del `.xml` dos parámetros, y hay que fijarlos a mano cada vez (prueba del
   21/10/2026):
   - **Terrain-Flattening:** destilde **Mask out areas without elevation**. En el Delta
     los ríos y las lagunas están a cota ~0 m en el Copernicus DEM y SNAP los toma como
     mar: con la casilla tildada el agua sale en 0 (sin dato) y se pierde la clase agua.
   - **Terrain-Correction:** la proyección aparece como `WGS84(DD)`. Clic en ese botón >
     **Predefined CRS** > **Select...**, escriba `32721` en Filter y elija
     `EPSG:32721 - WGS 84 / UTM zone 21S`; OK, OK. Tilde además **Layover Shadow Mask**.
   Verifique que el DEM sea `Copernicus 30m Global DEM` y el píxel 10 m.
6. Pestaña **Write**: nombre `A2_IBICUY_S1_<FECHA_C>_gamma0` (por ejemplo
   `A2_IBICUY_S1_20260926_gamma0`), formato **BEAM-DIMAP**, carpeta
   `Tp2_SAR_multibanda\02_Subsets_SNAP_QGIS`.
7. Botón **Run**. Guarde además el grafo con sus parámetros (**File > Save Graph**) en
   `02_Subsets_SNAP_QGIS` con el mismo nombre: es la constancia de lo que se hizo.

**(d)** Al terminar, el producto aparece en **Product Explorer** con las bandas
`Gamma0_VH`, `Gamma0_VV`, `localIncidenceAngle` y la máscara de inversión por relieve
y sombra (`layover_shadow_mask`). Doble clic en `Gamma0_VV`: el agua se ve negra y la
imagen está orientada al norte.

**(e)** Controles:

- `Analysis > Information` sobre el producto: CRS `WGS 84 / UTM zone 21S`, tamaño de
  píxel 10 m.
- `Analysis > Statistics` sobre `Gamma0_VV`: los valores son **lineales**, positivos y
  la mayoría por debajo de 1. Si ve valores negativos de −5 a −25, el producto está en
  dB: algo cambió en Calibration.
- En la carpeta de salida hay un `.dim` y una carpeta `.data` con un `.img` + `.hdr`
  por banda.

**(f)** Errores típicos:

- `No valid orbit file found`: no hay red hacia el servidor de órbitas. El nodo está
  configurado para seguir (`continueOnFail`), pero la geolocalización queda con la
  órbita de la anotación. **Se declara.**
- Falla al bajar el DEM: el Terrain Flattening necesita el Copernicus DEM. Sin red,
  debe estar en la carpeta auxiliar de SNAP (el docente la deja lista).
- El Subset vacío (`0,0,0,0`) procesa la escena entera: tarda mucho y ocupa varios GB.
- Calibrar a σ⁰ «para ganar tiempo»: el Terrain Flattening se niega o da resultados
  sin sentido. Va β⁰.
- Pestañas en blanco al cargar el grafo: abra antes la escena en Product Explorer.

---

## Paso 2 — Filtro de speckle, como paso aparte (EN SNAP)

**(a)** El speckle no es ruido del instrumento: es la interferencia de las ondas
devueltas por muchos dispersores dentro del mismo píxel. Dos píxeles de la misma
cubierta difieren varios dB sólo por eso. El filtro lo atenúa a costa de algo de
detalle. Se hace **aparte del grafo** para ver su efecto solo: mismo producto, antes y
después.

**(b)** SNAP.

**(c)**

1. Seleccione el producto del paso 1 en Product Explorer.
2. `Radar > Speckle Filtering > Single Product Speckle Filter`.
3. Pestaña **I/O Parameters**: origen = el producto `..._gamma0`; destino con el
   sufijo `_Spk`, formato BEAM-DIMAP, carpeta `02_Subsets_SNAP_QGIS`.
4. Pestaña **Processing Parameters**: en **Source Bands** marque sólo `Gamma0_VH` y
   `Gamma0_VV` (no filtre `localIncidenceAngle` ni la máscara). En **Filter** elija
   **Refined Lee** (sin parámetros) o **Lee Sigma** (deje los valores por defecto y
   anótelos). Todo el grupo usa el mismo filtro.
5. **Run**.
6. Repita los pasos 2 a 5 sobre el mismo producto del paso 1 con **Gamma Map**,
   ventana de 7 × 7 (Filter Size X y Y = 7) y **Estimate Equivalent Number of Looks**
   tildado; destino con el sufijo `_GammaMap`. Agregue a los dos productos filtrados
   las bandas virtuales en dB del paso 3.

**(d)** Un producto nuevo `..._gamma0_Spk`. Abra `Gamma0_VV` de los dos productos y
use `Window > Tile Horizontally` para verlos lado a lado: el filtrado se ve más «liso»; los
bordes netos (costas, rutas) siguen netos con Refined Lee. Haga lo mismo con
`..._gamma0_GammaMap`: alisa más el interior de cada cubierta, pero un riacho de 20 a
30 m de ancho, del orden de la ventana de 7 × 7, pierde contraste.

**(e)** `Analysis > Statistics` sobre la misma zona homogénea (dibuje un rectángulo
con la herramienta de dibujo y marque **Use ROI mask**) en los dos productos: la
**media** lineal casi no cambia; la **desviación estándar** baja. Si la media cambia
mucho, el filtro se aplicó sobre dB. Compare también el número equivalente de vistas
(ENL = media² ÷ varianza) de los tres productos en el agua y en el monte, y la media en
lo construido: allí Refined Lee rebaja los reflectores puntuales y Gamma Map los
conserva (Lopes et al., 1993).

**(f)** Errores típicos:

- Filtrar sobre bandas en dB. El filtro promedia: en dB sesga hacia abajo.
- Filtrar dos veces (una aquí y otra en un grafo). Revise el árbol
  `Metadata > Processing_Graph` del producto.
- Esperar que el filtro «arregle» una escena con borde inválido. No lo hace.

---

## Paso 3 — Bandas virtuales en dB, guardado y exportación (EN SNAP)

**(a)** El producto se guarda en **BEAM-DIMAP (`.dim`)**: es el formato nativo de SNAP
y conserva **todos los metadatos originales** (órbita, calibración, historia de
procesamiento), de modo que puede seguir procesándose. Las bandas físicas quedan en
**lineal**; para mirar se agregan **bandas virtuales en dB**, que no ocupan disco
(guardan sólo la expresión `10*log10(...)`). Para Python se exporta además **una banda
lineal por archivo** en GeoTIFF, porque `Tp2_01` lee la primera banda de cada archivo.

**(b)** SNAP.

**(c)**

1. En el producto `_Spk`, seleccione `Gamma0_VV` y vaya a
   `Raster > Data Conversion > Linear to/from dB`. Aparece la banda virtual
   `Gamma0_VV_db`. Repita con `Gamma0_VH`.
2. `File > Save Product`. Confirme que se guarda como BEAM-DIMAP.
3. Exportación de **VV lineal**: seleccione el producto y vaya a
   `File > Export > GeoTIFF`. Botón **Subset...** > pestaña **Band Subset**: marque
   **sólo** `Gamma0_VV` (desmarque VH, las `_db`, `localIncidenceAngle` y la máscara);
   pestaña **Metadata Subset**: desmarque todo. Nombre
   `A2_IBICUY_S1_<FECHA_C>_Gamma0_VV_Spk.tif`, carpeta `02_Subsets_SNAP_QGIS`.
4. Repita para `Gamma0_VH` → `A2_IBICUY_S1_<FECHA_C>_Gamma0_VH_Spk.tif`.

**(d)** En Product Explorer, las bandas `_db` llevan una **V** en el ícono (virtuales).
En la carpeta, dos `.tif` de una banda cada uno.

**(e)** Abra cada `.tif` en QGIS (`Capa > Añadir capa > Añadir capa ráster...`) y vea
en Propiedades > **Información**: 1 banda, EPSG:32721, tamaño de píxel 10, valores
lineales.

**(f)** Errores típicos:

- Exportar el producto entero a un GeoTIFF de varias bandas: `Tp2_01` leería sólo la
  primera, que puede ser VH, el ángulo o una banda en dB.
- Exportar la banda virtual `_db` creyendo que es la lineal. Si exporta en dB, el
  nombre que le dé en el paso 4 debe terminar en `_db` (ver abajo).
- Guardar el `.dim` sólo como GeoTIFF: se pierden los metadatos.

---

## Productos que YA VIENEN HECHOS

- **El mismo Sentinel-1 del 26/09/2026, procesado por el docente** con
  `00_COMUN\procesar_s1_crudo.py` (misma cadena que el grafo del paso 1, más el
  ruido de borde y Refined Lee), en
  `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\` (`.dim`, GeoTIFF y RGB
  VV–VH–VV/VH). Sirve para **comparar** con el que usted hizo en los pasos 1 a 3: si
  difieren en más de unas décimas de dB en la mediana, revise la calibración y el
  Terrain Flattening. El `LEEME_S1_crudo.md` de esa carpeta da la diferencia con el
  RTC del Planetary Computer.
- **SAOCOM-1A en banda L (2020).** Llevar un SAOCOM L1A a γ⁰ es un proceso de una a
  varias horas por escena entera: el docente lo dejó hecho con
  `00_COMUN\procesar_saocom.py` para los tres SAOCOM del Delta, en
  `Tp5_Incendios\02_Subsets_SNAP_QGIS\SAOCOM_gamma0\`. Cubren el sector de las
  quemas de 2020 (`A1_DELTA_QUEMAS`), **no Ibicuy**: sirven para el ejemplo de la
  pila sobre `A1_DELTA_QUEMAS` (ver «Las órdenes» en `00_ORDEN_DE_EJECUCION.md`).
  El grafo general, `Tp2_SAOCOM_StripMap_a_gamma0.xml`, queda para ver cómo se hace.
- **SAOCOM-1A cuadripolar del 24/09/2026 sobre Ibicuy** (TOPSAR Narrow B,
  `EOL1ASARSAO1A15583751`, CONAE), llevado a γ⁰ sobre el elipsoide a 20 m con
  `00_COMUN\procesar_saocom_topsar.py`, en `02_Subsets_SNAP_QGIS\SAOCOM_gamma0\`. Cubre
  el 80,5 % de Ibicuy; los 2 a 3 km del borde este son ruido del extremo del haz. No
  entra en la pila (está a 20 m, corrido unos 30 m respecto de NISAR y con esa banda de
  ruido): se usa **para profundizar** en el paso 8 con `Tp2_05_saocom_por_cubierta.py`.
- **Sentinel-1 IW SLC.** El grafo `Tp2_S1_SLC_a_gamma0.xml` queda para ver cómo se
  hace (TOPS Split, Deburst, etc.); no hay un SLC procesado del sitio: para la banda C
  alcanza con el GRD.

---

## Paso 4 — La pila multibanda (SE CORRE)

**(a)** Se reúne en **una** pila, sobre la grilla común de 10 m del sitio, todo el
radar disponible, en lineal y con el nombre normalizado
`<banda>_<sensor>_<gamma0|sigma0>_<pol>[_AAAAMMDD]`:

- C: Sentinel-1 RTC del Planetary Computer (`C_S1_gamma0_VV`, `C_S1_gamma0_VH`), si
  se da `--fecha_c`.
- S y L: **todos** los NISAR GCOV del disco que cubran el sitio, HH y HV, frecuencia A,
  con la máscara del producto aplicada (`S_NISAR_gamma0_HH_20260930`, etc.).
- S: NovaSAR-1, sólo con `--novasar`, guardado como **σ⁰** y dicho en el nombre
  (`S_NovaSAR_sigma0_HH`): el curso no tiene un modelo de ángulo local para
  normalizarlo a γ⁰ fuera de SNAP. NovaSAR viene georreferenciado con sólo cuatro
  puntos de esquina: la corrección que mide `Tp3_02` se aplica con
  `--desplazamiento DX DY` (metros; DX positivo = hacia el este, DY positivo = hacia
  el norte).
- Lo procesado en SNAP, con
  `--extra "nombre_de_banda=ruta.tif|sensor|lambda_cm|AAAA-MM-DD|unidad|pasada|traza"`
  (una vez por banda). Sensor, longitud de onda en cm (con punto decimal: `5.6`,
  `23.5`), fecha de adquisición, unidad (`gamma0`, normalizado por el terreno;
  `gamma0E`, γ⁰ sobre el elipsoide; `sigma0`) y pasada (`A` o `D`) y traza leídas en los
  metadatos (en SNAP, `Metadata > Abstracted_Metadata`, campos `PASS` y `REL_ORBIT`)
  son opcionales para el programa, pero póngalos siempre: con ellos se completa
  `<SITIO>_pila_bandas.csv`, el Tp3 arma la tabla de fechas y el paso 8 sabe si un par
  es de la misma pasada.

Cada banda entra sólo si tiene dato en al menos el 20 % del sitio (`--min_validos`).
Los productos de píxel más fino que 10 m se agregan **promediando potencia**; los de
píxel igual o más grueso (NISAR de 20 m), con interpolación bilineal. Un GeoTIFF en
dB se pasa primero a lineal en su propia grilla y recién después se promedia.

**(b)** Miniforge Prompt.

**(c)** Con el Sentinel-1 de SNAP del paso 3 (rutas de ejemplo; ajuste la fecha):

```
python Tp2_01_pila_multibanda.py --sitio A2_IBICUY --fecha_c 2026-09-26 --extra "C_SNAP_gamma0_VV=D:\CURSOS_CEREGEO_2026\02_Practica\Tp2_SAR_multibanda\02_Subsets_SNAP_QGIS\A2_IBICUY_S1_20260926_Gamma0_VV_Spk.tif|Sentinel-1 SNAP|5.6|2026-09-26|gamma0|D|68" --extra "C_SNAP_gamma0_VH=D:\CURSOS_CEREGEO_2026\02_Practica\Tp2_SAR_multibanda\02_Subsets_SNAP_QGIS\A2_IBICUY_S1_20260926_Gamma0_VH_Spk.tif|Sentinel-1 SNAP|5.6|2026-09-26|gamma0|D|68"
```

Va en **una sola línea**. Si la parte en una línea larga, termine cada línea con `^`
(el carácter de continuación del símbolo del sistema de Windows).

**La banda P.** El GeoTIFF de BIOMASS trae varias bandas: con `#1` y `#3` al final de la
ruta se elige la HH y la VH. Se agregan dos `--extra` más a la misma orden:

```
--extra "P_BIOMASS_gamma0_HH=D:\CURSOS_CEREGEO_2026\02_Practica\Tp2_SAR_multibanda\02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\A2_IBICUY_BIOMASS_P_20261005.tif#1|BIOMASS|69.0|2026-10-05|gamma0E|A|6" --extra "P_BIOMASS_gamma0_VH=D:\CURSOS_CEREGEO_2026\02_Practica\Tp2_SAR_multibanda\02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\A2_IBICUY_BIOMASS_P_20261005.tif#3|BIOMASS|69.0|2026-10-05|gamma0E|A|6"
```

El programa lo reproyecta con sus puntos de enlace y lo promedia en lineal: deben salir
`P_BIOMASS_gamma0_HH 99.8 % con dato media -13.08 dB` y `P_BIOMASS_gamma0_VH 99.8 % con dato
media -23.30 dB`. La pila queda con 14 bandas: C, L (tres fechas), S y P. La P es γ⁰ sobre el
elipsoide (sin normalización por terreno): se declara con `gamma0E` y la tabla de bandas lo
dice («gamma0 elipsoidal lineal»).

**Por qué VH y no HV.** En este producto el canal HV trae interferencia de radiofrecuencia
(RFI): emisiones de radares y comunicaciones terrestres que comparten los 435 MHz. El
procesador de ESA la detectó pero no la corrigió (en los metadatos, `rfiDetectionFlag = true`
y `rfiCorrectionFlag = false`). Se suma a la señal en líneas de acimut enteras y pesa más en
la cruzada, que es la señal más débil. En la retrodispersión de un radar monoestático la HV
y la VH miden lo mismo, así que la VH, que llega limpia, es la cruzada que se usa.

Los nombres de las bandas extra **deben terminar en `_VV`, `_VH`, `_HH` o `_HV`**
para que el paso 5 encuentre su gemela y arme el RGB. Si un GeoTIFF está en dB, el
nombre debe terminar en `_db` (por ejemplo `C_SNAP_gamma0_VV_db=...`): el script lo
pasa a lineal en su grilla original, **después** lo promedia a la grilla común, lo
avisa en la bitácora y le quita el sufijo. Aun así, exportar la banda lineal es lo
más directo.

Otras formas:

```
python Tp2_01_pila_multibanda.py --sitio A2_IBICUY --fecha_c 2026-09-26
python Tp2_01_pila_multibanda.py --sitio F_BOVRIL --novasar 47974 --fecha_c 2023-09-17
python Tp2_01_pila_multibanda.py --sitio F_BOVRIL --novasar 47974 --fecha_c 2023-09-17 --desplazamiento -92 -484
```

La tercera aplica a NovaSAR 47974 la corrección medida en el Tp3 con `Tp3_02`: 92 m al oeste
y 484 m al sur (la presentación 02 daba unos 80 m al oeste y 20 m al norte; la medición no lo
confirma, y además la deformación no es rígida); `Tp3_02`, que al final imprime la orden
`--desplazamiento DX DY` lista para pegar.

**(d)** La grilla del sitio (columnas × filas, EPSG) y, por banda, una línea
`nombre   X % con dato   media Y dB   (sensor, fecha)`, o
`-> NO entra (menos de 20 %)`. Con NovaSAR, `Desplazamiento aplicado: ... m este, ... m
norte (medido con Tp3_02).` o, sin `--desplazamiento`, `AVISO: sin --desplazamiento`.
Para cada `--extra`, un título `Producto de SNAP: nombre (sensor, lambda cm, fecha)`.
Al final, la ruta de la pila y el número de bandas. Con `#3`, la línea `Banda 3 del GeoTIFF.`

**(e)** Controles:

- Las medias en dB salen promediadas en lineal (`media_lineal_db`). En agua calma deben
  ser las más bajas de cada banda.
- Las bandas S y L de NISAR sobre Ibicuy deben estar presentes si los granulos cubren
  el sitio. El corregistro entre L y S se mide en el Tp3; si sólo hay banda L
  (la S de ISRO puede no existir para el Delta), el paso sigue con L.
- Abra `<SITIO>_pila_bandas.csv`: columnas `banda, sensor, lambda_cm, fecha, pasada, traza,
  unidad, pixeles_validos_%, media_dB, fuente`. La `unidad` de NovaSAR dice `sigma0 lineal`
  y la de BIOMASS `gamma0 elipsoidal lineal`; ninguna banda debe decir «unidad sin declarar».
- Si la pila incluye `C_S1_gamma0_VV` (RTC del Planetary Computer) y `C_SNAP_gamma0_VV`
  (su procesamiento) del mismo día, sus medias deben ser parecidas. Se mide en el
  paso 8.

**(f)** Errores típicos:

- `El catalogo no tiene Sentinel-1 RTC ese dia`: otra fecha, o sin red. Se declara.
- `No encuentro el GRD de la escena ...`: la carpeta de NovaSAR no está o la escena no
  existe. NovaSAR no cubre Ibicuy: no use `--novasar` con `A2_IBICUY`.
- Banda `-> NO entra`: cubre menos del 20 % del sitio. No baje el umbral para «hacerla
  entrar» sin declararlo.
- `--extra` de BIOMASS sin `#1` o `#3` al final de la ruta: entra la banda 1 (HH) las dos veces.
- Usar `#2` (HV) como cruzada de P: entra con la interferencia del producto de origen. Se usa `#3` (VH).
- Comillas mal cerradas en `--extra`, o una ruta con espacios sin comillas. Toda la
  expresión `nombre=ruta|sensor|lambda|fecha` va entre las mismas comillas.
- `AVISO: sin fecha`: el `--extra` no lleva `|sensor|lambda_cm|AAAA-MM-DD` después de
  la ruta. La banda entra con sensor `SNAP`, sin longitud de onda ni fecha, y el Tp3
  no la ubica en la tabla de fechas. Corrija la orden y vuelva a correr.
- Longitud de onda con coma (`5,6`): el programa espera punto decimal (`5.6`).
- Signo de `--desplazamiento` invertido: la capa se aleja en lugar de acercarse. Se
  ve en QGIS contra el óptico y se confirma con `Tp3_02`.

---

## Paso 5 — RGB copolarizada / cruzada / cociente (SE CORRE)

**(a)** Para cada sensor de polarización dual de la pila se arma el RGB que el curso
usa **siempre** para el radar dual: **R = copolarizada (VV o HH) en dB, G = cruzada
(VH o HV) en dB, B = cociente copol/cros en dB** (= copol_dB − cros_dB). Cómo se interpreta
(presentación 02):

| Color | Mecanismo | Cubiertas típicas en el Delta |
|---|---|---|
| verde o amarillo | volumen (cruzada alta) | monte, pajonal, juncal denso |
| magenta o blanco | doble rebote | poblado, troncos sobre agua (bosque inundado) |
| azul o violeta | cociente alto, cruzada baja | suelo desnudo, agua rizada por el viento |
| negro | reflexión especular | agua calma |

Los colores son orientativos y dependen del estiramiento de cada RGB. En banda L el pajonal
sale violeta o magenta por cociente alto (cruzada baja), no por doble rebote; el doble rebote
sólo se confirma con datos cuadripolares (la fase HH − VV).

Con BIOMASS (banda P), el programa promedia antes las intensidades en una ventana de 5 × 5 píxeles, en lineal: con una sola mirada, el moteado de la banda P tapa los detalles; el detalle efectivo del RGB de P es de unos 50 m.

El estiramiento es 2–98 % por canal, calculado sobre el sitio. **Es sólo para ver**:
el GeoTIFF RGB es de 8 bits y no sirve para medir. Las bandas de una sola polarización
(NovaSAR HH) se exportan en gris.

**(b)** Miniforge Prompt y QGIS.

**(c)**

```
python Tp2_02_rgb_copol_cruzada_cociente.py --sitio A2_IBICUY
```

En QGIS: `Capa > Añadir capa > Añadir capa ráster...` y elija
`05_Resultados\02_Rasters\A2_IBICUY_RGB_<etiqueta>.tif`. QGIS lo abre como
**Color multibanda** (R = 1, G = 2, B = 3). En Propiedades > **Simbología**, deje
**Mín/Máx**: «Sin ajuste» o «Mín/Máx» de la capa: el estiramiento ya viene aplicado.

**(d)** Por cada par, una línea: `etiqueta  R=VV [a, b] dB  G=VH [c, d] dB  B=VV/VH [e, f] dB`
(los límites del estiramiento 2–98 %). Los PNG en `05_Resultados/05_Graficos/` con el
título `RGB = VV - VH - VV/VH (dB)` y la línea **Fuente:** al pie. Las etiquetas son,
por ejemplo, `C_S1`, `C_SNAP`, `L_NISAR_20260930`, `S_NISAR_20260930` y `P_BIOMASS`.

**(e)** Controles:

- El río y las lagunas en negro en todas las bandas (salvo con viento).
- El monte, verde o amarillo en el RGB de L y en el de C (volumen en las dos). Cada
  RGB se estira por separado (2–98 % de cada canal y sensor): **el brillo no se compara
  entre composiciones**. Si quiere comparar la cruzada de L con la de C sobre el monte,
  hágalo con los valores en dB de la tabla del paso 7, o con los RGB de rango fijo
  (`python Tp2_02_rgb_copol_cruzada_cociente.py --sitio A2_IBICUY --rango_fijo`: los mismos
  límites para todos los sensores, sufijo `_rango_fijo`): se espera la cruzada de L más
  alta, porque la banda L penetra hasta ramas y troncos.
- Compare `C_S1` con `C_SNAP` del mismo día: deben verse casi iguales; `C_SNAP` con
  menos granulado si se filtró.

**(f)** Errores típicos:

- Un sensor dual que sale en gris: las dos bandas no se encontraron como gemelas
  (nombre sin `_VV`/`_VH` al final del bloque de polarización).
- Medir algo sobre el RGB de 8 bits. Se mide sobre la pila.
- Cambiar el estiramiento en QGIS para que «se parezcan» dos bandas: se pierde la
  comparación.

---

## Paso 6 — Digitalizar las cubiertas (EN QGIS)

**(a)** Para comparar la misma cubierta en todas las bandas hay que delimitarla. Lo
hace el grupo, no el programa, mirando el RGB y una imagen óptica.

**(b)** Miniforge Prompt (una vez) y QGIS.

**(c)**

1. Corra una vez el paso 7: como el archivo de cubiertas no existe, el script lo crea
   **vacío** y se detiene:

   ```
   python Tp2_03_respuesta_por_cubierta.py --sitio A2_IBICUY
   ```

   Crea `04_Tablas_de_trabajo\cubiertas_A2_IBICUY.gpkg`, capa `cubiertas`, campos
   `clase` y `observacion`, EPSG:32721.
2. En QGIS, arrastre el `.gpkg` al mapa. Cargue debajo los RGB del paso 5 y una imagen
   de fondo (XYZ Tiles > ESRI World Imagery, como en el Tp1). Para el óptico datado,
   use un Sentinel-2 cercano a la fecha (lo trae el Tp3) o el Copernicus Browser.
3. Para evitar errores de tipeo: Propiedades de `cubiertas` > **Formulario de
   atributos** > campo `clase` > **Tipo de control: Mapa de valores**, y cargue las
   ocho clases: `agua_calma`, `agua_rizada`, `pajonal`, `monte_o_bosque`, `cultivo`,
   `suelo_desnudo`, `urbano`, `estable`.
4. **Conmutar edición** (ícono del lápiz) > **Añadir polígono** (Ctrl+.). Clic para
   cada vértice, clic derecho para cerrar, elija la clase.
5. Al menos **3 polígonos por clase** y **200 píxeles de 10 m por clase**
   (2 hectáreas en total por clase). La clase `estable` es la del paso 8: superficies
   que no cambian entre fechas (casco urbano, ruta asfaltada, playón). Polígonos
   dentro de la cubierta, lejos de sus bordes.
6. **Polígonos al azar.** Ningún criterio para aceptar un punto puede usar la banda que
   después se compara: si el agua calma se acepta por «C VV menor que −19 dB», el contraste
   de C VV entre las aguas deja de ser un resultado. Use criterios independientes (MapBiomas,
   NDVI, ancho del curso de agua en el óptico).
    Los polígonos se trazan al azar, no donde la clase se ve más fácil. `Vectorial > Herramientas de investigación > Puntos aleatorios en la extensión` (Random Points in Extent), con la extensión del sitio y 100 puntos. Recorra los puntos en el orden en que salieron (campo `id`) y trace un polígono alrededor de cada punto que caiga en una cubierta inequívoca, hasta completar el número pedido para cada clase; los puntos que caen en bordes o en cubiertas dudosas se saltean y se anotan. Elegir los lugares a ojo concentra los polígonos en los ejemplos más típicos y hace que el mapa parezca mejor de lo que es. Con 100 puntos uniformes las clases raras (las que ocupan pocas hectáreas: monte cerrado, suelo desnudo, severidad alta) casi nunca se completan. Para esas clases, haga un **sorteo estratificado**: convierta a polígono el estrato de la clase (`Ráster > Conversión > Poligonizar` sobre MapBiomas, o sobre el rango del índice que define la clase) y use `Vectorial > Herramientas de investigación > Puntos aleatorios dentro de polígonos`; recorra esos puntos también en el orden en que salieron, con la misma revisión en la imagen. Anote de qué sorteo salió cada polígono.
7. **Guardar edición** y desactivar la edición.

   En el Desarrollo: 4 polígonos de 110 × 110 m por clase (121 píxeles cada uno), semilla
   20261022. El sorteo se puede repetir sin programar con `Ráster > Calculadora ráster`
   (por ejemplo, MapBiomas 2025 = 11 y NDVI ≥ 0,3 para el pajonal) y trazando el polígono
   donde el cuadrado queda entero en 1.

**(d)** La capa con sus polígonos de colores. El estilo `cubiertas_A2_IBICUY.qml` (al lado del
`.gpkg`) trae un color fijo por clase, el mismo de Orange y de las figuras del Desarrollo.

**(e)** `Vectorial > Herramientas de análisis > Estadísticas básicas para campos` no
hace falta: el paso 7 avisa si una clase tiene menos de 200 píxeles.

**(f)** Errores típicos:

- Polígonos que se superponen entre clases: el píxel queda en la última clase
  dibujada. Evítelo.
- Escribir `Agua calma` en lugar de `agua_calma`: son dos clases distintas para el
  programa.
- Dibujar sobre una imagen de fondo de otra fecha y otra estación: el pajonal de una
  imagen de verano puede ser agua en primavera. Mire el RGB del radar de la fecha.
- Olvidar guardar la edición: el script lee la capa vacía.

---

## Paso 7 — Respuesta por cubierta en cada banda (SE CORRE) — SINERGIA

**(a)** Por clase y por banda: **media en dB calculada promediando en lineal**, p10 y
p90 en dB y número de píxeles; el **contraste** entre cada par de clases (diferencia
de medias en dB), que es lo que hace que una banda «vea» algo y otra no; y una figura
de cajas por banda. Éste es el paso de **sinergia**: cada banda da su respuesta y el
grupo las interpreta juntas.

**(b)** Miniforge Prompt.

**(c)**

```
python Tp2_03_respuesta_por_cubierta.py --sitio A2_IBICUY
```

**(d)** La tabla pivote «Media por clase (dB, promediada en lineal)» con una fila por
clase y una columna por banda, y avisos `AVISO: <clase> en <banda> tiene solo N
pixeles: la media es inestable`. La figura `05_Graficos/A2_IBICUY_cajas_por_banda.png`
(una caja por clase en cada banda, en dos filas, con las clases en orden físico; caja
p25–p75; bigotes hasta 1,5 veces el rango intercuartil; sin los valores extremos). También
`<SITIO>_media_por_poligono.csv`, con la media de cada polígono, y, en el archivo de
contrastes, la separabilidad M = |μ1 − μ2| / (σ1 + σ2): si M > 1 las clases se separan
píxel a píxel.

**(e)** Controles de coherencia física (no son umbrales, son expectativas a explicar):

- Agua calma: la media más baja en todas las bandas, sobre todo en la cruzada.
- Monte: cruzada (HV, VH) más alta que en pajonal o cultivo, y con más diferencia en L
  que en C.
- Urbano: copolarizada alta en todas las bandas (doble rebote).
- El contraste entre monte y pajonal en la cruzada crece con la longitud de onda: en este
  desarrollo (polígonos sorteados), unos 2,2 a 2,6 dB en C, 7,2 dB en L y 13,4 dB en P. La onda larga atraviesa las hojas y
  el pajonal casi no tiene troncos que la devuelvan.
- Si una expectativa no se cumple, **no se fuerza**: se explica (viento, fecha,
  inundación del monte, polígono mal ubicado).

**(f)** Errores típicos:

- Comparar valores absolutos entre sensores distintos (S1 frente a NISAR): ángulos de
  incidencia y calibraciones distintas. Compare **contrastes** y formas.
- Interpretar NovaSAR (σ⁰) junto a NISAR S (γ⁰) como si fueran lo mismo.
- Calcular la media por polígono en QGIS con `Estadísticas de zona` sobre la banda virtual
  en dB o sobre el RGB de 8 bits: se promedian logaritmos o niveles de gris. La media se
  calcula sobre la pila lineal, con `Tp2_03`.
- Leer el ANOVA del pie del Box Plot de Orange como prueba entre clases: trata cada píxel
  como independiente; la unidad de muestreo es el polígono.

---

## Paso 8 — Control en zona estable (SE CORRE)

**(a)** Una zona estable no cambió entre fechas. Si allí dos productos del **mismo
sensor y la misma polarización** difieren más de **1 dB** (del orden de la exactitud
radiométrica absoluta especificada para Sentinel-1, 1 dB a 3σ), el problema no es el
paisaje: es la calibración, la normalización (σ⁰ frente a γ⁰), la órbita o el
corregistro. Hay dos controles distintos: **entre fechas** del mismo sensor y pasada se
usa la clase `estable`; **entre dos procesadores del mismo día** (RTC frente a SNAP) se
usan cubiertas homogéneas distribuidas (`--clase monte_o_bosque`, `--clase pajonal`),
porque en lo construido el filtro de speckle baja 0,4 a 0,8 dB la media de los
reflectores puntuales y un corrimiento de 15 m agranda el desvío. Como la unidad de
muestreo es el polígono, el programa informa también la diferencia de cada polígono y
un intervalo del 95 % por remuestreo de polígonos. Se informa también la dispersión pixel a pixel de la diferencia: con
speckle sin filtrar es grande aunque las medias coincidan.

**(b)** Miniforge Prompt.

**(c)** Sin argumentos de bandas, el script compara todos los pares de la pila que
sólo difieren en la fecha final (`_AAAAMMDD`), es decir, las fechas de NISAR, **y sólo si son de la misma
pasada y traza** (las columnas `pasada` y `traza` de `<SITIO>_pila_bandas.csv`). Un par de pasadas opuestas
(ascendente frente a descendente) se saltea y se informa: la diferencia mediría la geometría de visión, no la
calibración:

```
python Tp2_04_control_zona_estable.py --sitio A2_IBICUY
```

Para comparar el procesamiento propio de SNAP con el RTC del Planetary Computer del
mismo día:

```
python Tp2_04_control_zona_estable.py --sitio A2_IBICUY --a C_S1_gamma0_VV --b C_SNAP_gamma0_VV
```

Otras clases de control: `--clase` acepta una o varias (por defecto `estable`), y `--sufijo` se agrega al
nombre de la tabla y de la bitácora para que una corrida no pise a la anterior. Para el par del mismo
día sobre cubiertas homogéneas:

```
python Tp2_04_control_zona_estable.py --sitio A2_IBICUY --a C_S1_gamma0_VV --b C_SNAP_gamma0_VV ^
       --clase monte_o_bosque pajonal agua_calma --sufijo C_S1_vs_SNAP_VV_homogeneas
```

**Para profundizar (no se evalúa):** el SAOCOM-1A cuadripolar del 24/09/2026 por cubierta,
con HH − VV y HH − HV, fuera de la banda de ruido del borde este:

```
python Tp2_05_saocom_por_cubierta.py --sitio A2_IBICUY
```

La confirmación del doble rebote es la fase HH–VV cercana a 180°, que sólo da el SLC complejo:
`Tp2_06_saocom_pauli_y_fase.py` (lo corre el docente) calcula la descomposición de Pauli y esa
fase por polígono. Resultado (24/09/2026, Tabla 9 del Desarrollo): el polígono estable da 8°, no
180°, así que su HH − VV de 3,3 dB no es doble rebote; un polígono de pajonal da −152° (doble
rebote entre tallos y agua). La intensidad propone el mecanismo; la fase lo decide.

**(d)** Una línea por par: `banda_a - banda_b  n=...  dif. media +x.xx dB  desvio y.yy dB -> CUMPLE`
o `-> NO CUMPLE: revisar calibracion, normalizacion u orbita`, y debajo
`por poligono: ... dB   IC 95 % (remuestreo de N poligonos): ... a ... dB`.

**(e)** Criterio de aceptación: **|diferencia de medias| < 1 dB**. El desvío pixel a
pixel no tiene umbral: se compara entre pares (filtrado frente a sin filtrar).

**(f)** Errores típicos:

- `No hay poligonos de clase 'estable'`: falta digitalizarlos.
- `solo N pixeles estables en comun; no se evalua`: hacen falta al menos 50 píxeles
  con dato en las dos bandas.
- `No hay en la pila dos fechas del mismo sensor, polarizacion y pasada. Pida el par con --a y --b.`: no hay par comparable; use `--a` y `--b` sabiendo qué compara.
- `... vs ...: pasadas distintas (...)`: el par se salteó a propósito (geometría distinta).
- Un nombre de banda mal escrito en `--a` o `--b` corta el programa con `KeyError`:
  copie el nombre exacto de `<SITIO>_pila_bandas.csv`.
- Un NO CUMPLE entre dos fechas NISAR en una zona «estable» rural: puede ser
  humedad del suelo, no calibración. Por eso la zona estable se elige urbana o
  asfaltada.

---

## Paso 9 — Contexto del sitio: MapBiomas y CCI Biomass (EN QGIS y ORANGE)

**(a)** Los polígonos del paso 6 son pocos y chicos. MapBiomas cubre el sitio entero con
clases de cobertura: sirve para ver si lo que mostró el paso 7 vale para todo el sitio y no
sólo para los polígonos. El CCI Biomass agrega la biomasa estimada, para ver qué banda la
sigue. Las clases no son las mismas: pajonal ≈ 11 Herbáceas inundables; monte_o_bosque ≈
3 Bosques cerrados y 4 Bosques abiertos; suelo_desnudo ≈ 25 Otras áreas no vegetadas;
urbano y estable ≈ 24 Áreas urbanas; las dos aguas ≈ 33 Ríos, lagunas, lagos y océano.

**(b)** QGIS y Orange.

**(c)** En QGIS, `Capa > Añadir capa > Añadir capa ráster...` y elija
`02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\A2_IBICUY_MapBiomas_cobertura_1985_2025.tif`: el estilo
`.qml` de al lado se carga solo. En `Propiedades > Simbología` elija la banda `cobertura_2025`.
Agregue también `A2_IBICUY_CCI_Biomass_v7_AGB.tif`, banda `AGB_2024`, como
`Pseudocolor monobanda` de 0 a 100 Mg/ha. Prenda y apague el RGB de P y el de L encima.
En Orange abra `08_Orange\Tp2_E_bandas_por_clase_MapBiomas.ows`: 3.000 píxeles por clase
de MapBiomas 2025 con la cruzada de cada banda en dB y la AGB del CCI.

**(d)** MapBiomas 2025 en el sitio: 59 % herbáceas inundables, 6 % ríos y lagunas, 3 %
herbáceas, menos de 1 % de bosque, urbano y otras áreas no vegetadas, y 30 % sin dato (fuera
de Entre Ríos). En Orange, una caja por clase para cada banda.

**(e)** Controles: la diferencia de medianas de la cruzada entre bosque cerrado y herbáceas
inundables crece de C a P (unos 2,6 dB en C, 7,3 dB en L y 12,6 dB en P). El CCI da unos
60 Mg/ha en bosque y unos 20 en herbáceas inundables. Las causas posibles (mezcla de
cubiertas en 100 m, árboles dispersos, humedal fuera del dominio de calibración, doble
rebote del pajonal anegado) no se separan con estos datos. Los polígonos se resumen con la
media en lineal y MapBiomas con la mediana: las cifras no son idénticas, pero el orden C < L
< P se repite.

**(f)** Errores típicos:

- Tomar MapBiomas como verdad: es una clasificación de Landsat de 30 m, con sus errores.
- Comparar la AGB del CCI con el radar del curso como si fueran independientes: el CCI se
  estimó con radar C y L.
- Elegir la banda `cobertura_1985` (la primera) en lugar de `cobertura_2025`.

---

## Al terminar

En `05_Resultados/06_Control_calidad/` debe haber `Tp2_01_<SITIO>.log` a
`Tp2_04_<SITIO>.log`, cada uno con `SIGUIENTE PASO:`. Las bitácoras se reescriben en
cada corrida, y también `05_Resultados/04_Tablas/<SITIO>_control_zona_estable.csv`:
si corre el paso 8 varias veces con pares o clases distintas, use `--sufijo` en cada
corrida (por ejemplo `NISAR`, `C_S1_vs_SNAP_VV` o `C_S1_vs_SNAP_VV_homogeneas`): la tabla y la
bitácora salen con ese sufijo y no se pisan. Conteste `07_Preguntas_y_entrega/preguntas.md`.
