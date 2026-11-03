# Tp5 · Guía paso a paso

Miércoles, 9 a 13 h. Sitio `A1_DELTA_QUEMAS` (islas del Delta frente a Victoria, incendios de 2020).

Se sigue en orden. Cada paso dice qué se hace y por qué, dónde, la orden o los menús exactos, qué debe observar, cómo saber si salió bien y los errores típicos. Los menús de QGIS están como aparecen en español, con el nombre en inglés entre paréntesis; los de SNAP, en inglés, que es el idioma de su interfaz.

## Antes de empezar

Miniforge Prompt:

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp5_Incendios\03_Scripts
```

Compruebe que existen los insumos que el práctico no genera:

```
dir ..\..\Tp4_Validacion\02_Subsets_SNAP_QGIS\A1_DELTA_QUEMAS_cobertura_control_20m.tif
dir ..\..\Tp1_Convergencia\05_Resultados\03_Vectores\lidar_A1_DELTA_QUEMAS.gpkg
```

**Atención con la cobertura de control de este sitio.** En el Tp4 no se digitalizó nada sobre A1_DELTA_QUEMAS: su cobertura de control sólo tiene la clase 1, agua permanente de JRC (3.499 ha, el 4,6 % del sitio). Sirve para enmascarar el agua en el paso 2, pero la tabla de coincidencias no traerá filas de `humedal_pajonal` ni de `monte_nativo`. Para separar pajonal y albardón use el CCI Biomass 2020 (`A1_DELTA_QUEMAS_CCI_Biomass_v7_AGB`, banda `AGB_2020`): menos de 15 Mg/ha es pajonal; 30 Mg/ha o más, albardón con estructura leñosa (ver el paso 2). Si el grupo tiene tiempo, puede digitalizar polígonos de pajonal y de monte en el Tp4 (paso 3 de su guía) y volver a correr `Tp4_01`.

Si falta el primero, córralo ahora:

```
python ..\..\Tp4_Validacion\03_Scripts\Tp4_01_cobertura_de_control.py --sitio A1_DELTA_QUEMAS --pixel 20
```

Si falta el segundo, el paso 5 no se puede hacer; avise al docente (es una descarga larga que viene hecha).

**Landsat 8 y 9.** Escenas de este práctico, la pasada más cercana a cada Sentinel-2 con el sitio cubierto y despejado: Delta, `A1_DELTA_QUEMAS_L8_20200719` y `A1_DELTA_QUEMAS_L8_20201007`: Landsat 8 del 19/07/2020 y del 07/10/2020, para los Sentinel-2 del 15/07/2020 y del 13/10/2020 (en 2020 no existía Landsat 9).

Son Colección 2, Nivel 2 de USGS (reflectancia y temperatura de superficie, píxel de 30 m), bajadas del Planetary Computer. Están en `02_Subsets_SNAP_QGIS\SNAP_DIMAP` y `QGIS_GeoTIFF`, con las bandas `SR_B1` a `SR_B7` (reflectancia), `ST_B10` (temperatura, K), `ST_QA`, `QA_PIXEL` y las virtuales `NDVI` y `ST_B10_C` (°C).

Landsat 9 da imágenes desde el 31/10/2021; antes sólo hay Landsat 8. Los dos llevan instrumentos gemelos (OLI y TIRS) y se comparan entre sí sin ajuste. Con Sentinel-2 no: el píxel es de 30 m contra 10 y 20 m, y las bandas no coinciden del todo (el infrarrojo cercano de Landsat, 865 nm, equivale a la B8A, no a la B08).

Fuente: USGS / NASA, Landsat 8 y Landsat 9 OLI/TIRS, Colección 2 Nivel 2, distribuido por Microsoft Planetary Computer, https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2

**Fusión Landsat + Sentinel-2.** El Landsat también viene afinado a 10 m con el detalle espacial del Sentinel-2 de la fecha más cercana: se lo interpola a la grilla de 10 m y se le suma el detalle fino de la banda Sentinel-2 de 10 m que más se le parece, escalado por una regresión entre los dos sensores (filtro pasa-altos con modulación por regresión, HPF). Trae las bandas `SR_B1` a `SR_B7` en reflectancia, `mascara_detalle` (1 = se agregó detalle; 0 = nube, sombra o falta de dato en alguna de las dos) y el `NDVI` virtual; el método y la calidad de cada banda están en los metadatos.

El control es el ERGAS: la imagen afinada se lleva de nuevo a 30 m y se compara con el Landsat original; por debajo de 3 la fusión es buena. Sirve para mirar e interpretar, con tres cuidados: un cambio real entre las dos fechas aparece como detalle falso; las bandas 6 y 7 (infrarrojo de onda corta) toman el detalle de una banda de 10 m de otra región del espectro y son las menos confiables; y la temperatura no se afina.

En este práctico: `A1_DELTA_QUEMAS_L8_20200719_fusion_S2_20200715_10m` (4 días; ERGAS 0,48) y `A1_DELTA_QUEMAS_L8_20201007_fusion_S2_20201013_10m` (6 días; ERGAS 0,78). En temporada de quemas, un sector que se quemó entre las dos fechas aparece como detalle falso: compare con la `mascara_detalle` y con el Sentinel-2 antes de interpretar un borde.

**Pléiades y Pléiades Neo de CONAE.** Referencia visual de muy alta resolución del casco urbano (Pléiades, 0,5 m; Pléiades Neo, 0,3 m), 2022-2023, del proyecto Impactar de CONAE. Es un servicio de mapas y necesita internet: en `02_Subsets_SNAP_QGIS\Pleiades_CONAE_WMS` hay un `.xml` por localidad que se arrastra a QGIS (instrucciones en el `LEEME.md` de esa carpeta). Sirve para mirar y digitalizar, no para calcular: es RGB color real, sin infrarrojo ni reflectancia, y la fecha exacta no está publicada, sólo el año.

En este práctico: no hay capa de CONAE: las quemas son en islas, lejos de las localidades con capa.

**CBERS-4A, cámara WPM (INPE).** Pancromática de 2 m y multiespectral de 8 m (azul, verde, rojo e infrarrojo cercano), producto L4 ortorrectificado, en números digitales. Cada escena viene en dos productos: `..._MS_8m` (las cuatro bandas originales) y `..._pansharpened_2m` (la pancromática y las cuatro bandas afinadas a 2 m por Brovey ponderado, el método por defecto de GDAL). Es un pansharpening clásico: pancromática y multiespectral del mismo satélite y del mismo instante; compárelo con la fusión Landsat + Sentinel-2, que combina dos sensores y dos fechas. El control es el mismo ERGAS (por debajo de 3, bueno). Los números digitales no son reflectancia y el Brovey altera la radiometría: sirve para mirar y digitalizar, no para calcular índices. Cubre una zona de 12 a 21 km, no el sitio entero, y la escena se eligió a ojo, sin nubes, porque el catálogo del INPE no informa la nubosidad.

En este práctico: Delta, `A1_DELTA_QUEMAS_CBERS4A_DELTA_A1_20200525_...`: 25/05/2020, 51 días antes del Sentinel-2 del 15/07/2020 y antes de las quemas (ventana central de 12 × 12 km). Después de las quemas no hay ninguna pasada que cubra la zona; ERGAS 1,21.

Fuente: INPE / CAST, CBERS-4A WPM L4, licencia CC BY 4.0. Catálogo STAC del INPE, colección CB4A-WPM-L4-DN-1, https://data.inpe.br/stac/browser/collections/CB4A-WPM-L4-DN-1

**Embeddings anuales AlphaEarth Foundations (Google y Google DeepMind).** 64 números por píxel de 10 m que resumen un año entero de Sentinel-1, Sentinel-2, Landsat, GEDI, clima y otras fuentes, aprendidos por un modelo de inteligencia artificial. Las dimensiones (`A00` a `A63`) no tienen significado físico propio: sirven para clasificar con pocas muestras, buscar zonas parecidas y detectar cambios entre años. Vienen en enteros de 8 bits tal como los entrega Google (`..._AlphaEarth_embeddings_<año>_10m`); para pasarlos a valores reales, valor = signo(DN) × (DN / 127,5)², y −128 es sin dato. El `..._CP1_CP2_CP3_RGB_8bit.tif` muestra las tres primeras componentes principales para mirar en QGIS; sus colores no tienen significado fijo. Resumen un año, no una fecha; 2026 todavía no existe y se usa 2025, el último.

En este práctico: Delta, 2020. El año mezcla el antes y el después de las quemas.

Fuente: The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind (CC BY 4.0). Copia en Source Cooperative (Taylor Geospatial), https://source.coop/tge-labs/aef

---

## Paso 0 · (YA VIENE HECHO) SAOCOM en SNAP — EN SNAP

**Qué y por qué.** Los SAOCOM-1A del archivo del curso son productos SLC (complejos, en geometría de radar, sin calibrar): sus recortes al sitio están en `02_Subsets_SNAP_QGIS\SNAP_DIMAP\A1_DELTA_QUEMAS_SAOCOM_L_<fecha>_<QP|DP>.dim`. Para compararlos con el resto hay que llevarlos a γ⁰ en la grilla EPSG:32721. Los SLC de CONAE ya vienen calibrados (el píxel al cuadrado es σ⁰), y el γ⁰ se calcula como σ⁰/cos θ, con θ el ángulo de incidencia sobre el elipsoide; en las islas, llanas, equivale al γ⁰ aplanado. El Terrain-Flattening de SNAP 14 no se usa con SAOCOM: da entre 5 y 10 dB menos que el mosaico ALOS-2 y que NISAR. El docente lo dejó hecho con `00_COMUN\procesar_saocom.py` (ESA SNAP). Se describe para que sepa de dónde sale.

**Cadena de operadores** (el grafo de cada escena está en `02_Subsets_SNAP_QGIS\SAOCOM_gamma0\Grafos_SNAP`; se abre en SNAP con `Tools > GraphBuilder > Load`): `Read` → `Calibration` (σ⁰) → `Multilook` (píxel cuadrado en el terreno) → `Speckle-Filter` (Refined Lee) → `Terrain-Correction` (10 m, EPSG:32721, con el ángulo de incidencia sobre el elipsoide) → `Write` (BEAM-DIMAP). El γ⁰ = σ⁰/cos θ lo agrega el programa como banda virtual del `.dim` y como GeoTIFF.

**Dónde están** (`02_Subsets_SNAP_QGIS\SAOCOM_gamma0\`):

| Escena | Polarizaciones | `.dim` (SNAP) | GeoTIFF de una banda para Python | RGB copolarizada–cruzada–cociente |
|---|---|---|---|---|
| 21/07/2020, antes | HH, HV, VH, VV | `SNAP_DIMAP\A1_DELTA_QUEMAS_SAOCOM_L_20200721_QP_gamma0.dim` | `QGIS_GeoTIFF\A1_DELTA_QUEMAS_SAOCOM_L_20200721_QP_gamma0_Gamma0_HV.tif` (y `_HH`, `_VH`, `_VV`) | HH–HV–HH/HV |
| 07/09/2020, durante | VV, VH | `SNAP_DIMAP\A1_DELTA_QUEMAS_SAOCOM_L_20200907_DP_gamma0.dim` | `QGIS_GeoTIFF\A1_DELTA_QUEMAS_SAOCOM_L_20200907_DP_gamma0_Gamma0_VH.tif` (y `_VV`) | VV–VH–VV/VH |
| 25/10/2020, después | HH, HV, VH, VV | `SNAP_DIMAP\A1_DELTA_QUEMAS_SAOCOM_L_20201025_QP_gamma0.dim` | `QGIS_GeoTIFF\A1_DELTA_QUEMAS_SAOCOM_L_20201025_QP_gamma0_Gamma0_HV.tif` (y `_HH`, `_VH`, `_VV`) | HH–HV–HH/HV |

Los `.dim` traen el σ⁰ **lineal**, los ángulos de incidencia, el γ⁰ (virtual) y las bandas virtuales en dB; los GeoTIFF de una banda son lineales y son lo que lee `Tp5_01`. Los RGB están en `RGB_copol_cruzada_cociente`, en dB y en 8 bits con rangos fijos (los mismos para las tres fechas). La banda P de BIOMASS es la excepción: su `_RGB_8bit.tif` lleva promedio 5 × 5 (en lineal) y estiramiento 2–98 % por escena, porque con los rangos fijos quedaba en pocos tonos; sus colores no se comparan entre escenas (para eso, el `_RGB_dB.tif`). La ficha con la fuente y el porcentaje con dato de cada escena es `SAOCOM_gamma0\LEEME_SAOCOM_gamma0.md`.

**Resultado esperado** (en SNAP, `File > Open Product…`, el `.dim` del 21/07/2020): bandas `Gamma0_HH`, `Gamma0_HV`, `Gamma0_VH` y `Gamma0_VV` y sus virtuales `_db`. Abra el RGB del 21/07 y el del 25/10 lado a lado en QGIS: lo quemado pierde verde (HV).

---

## Paso 1 · Indicadores por sensor — SE CORRE

**Qué y por qué.** Antes de comparar o combinar, cada sensor produce **su** indicador de cambio, en la misma grilla:

- **Radar: Δ = 10·log₁₀(post/pre)**, con post y pre en γ⁰ **lineal**. Es lo mismo que restar dB sólo si cada lado se promedió antes en lineal; por eso el script divide potencias y recién después pasa a dB. Negativo = pérdida de señal.
- **ΔVH en banda C (5,5 cm):** la onda corta interactúa con hojas y tallos finos. El pajonal quemado pierde ese volumen y la polarización cruzada cae.
- **ΔHV en banda L (≈ 23 cm):** la onda larga atraviesa el follaje y responde a ramas y troncos. Cae donde se perdió volumen leñoso (bosque de albardón); en un pajonal quemado se espera que cambie menos que la C. Compruébelo con sus números: si no se cumple, explíquelo.
- **NBR = (B08 − B12)/(B08 + B12):** el fuego baja el infrarrojo cercano (menos hoja verde) y sube el infrarrojo de onda corta (suelo y carbón). dNBR = NBR_pre − NBR_post; RdNBR = dNBR / √|NBR_pre| corrige el efecto de que una cubierta rala tiene poco NBR que perder. Donde |NBR_pre| < 0,05 el cociente se dispara y el píxel queda sin dato; en este pajonal son muchos (el 12 % del sitio) y eso achica la V4 (la bitácora lo informa).

**Dónde.** Miniforge Prompt. Ponga la fecha óptica previa que eligió en el Tp1 (aquí, la del ejemplo del script):

```
python Tp5_01_indicadores.py --pixel 20 --c_pre 2020-07-16 --c_post 2020-09-26 ^
    --opt_pre 2020-07-15 --opt_post 2020-10-13 --alos2_pre 2019 --alos2_post 2020 ^
    --saocom_pre_hv ..\02_Subsets_SNAP_QGIS\SAOCOM_gamma0\QGIS_GeoTIFF\A1_DELTA_QUEMAS_SAOCOM_L_20200721_QP_gamma0_Gamma0_HV.tif ^
    --saocom_post_hv ..\02_Subsets_SNAP_QGIS\SAOCOM_gamma0\QGIS_GeoTIFF\A1_DELTA_QUEMAS_SAOCOM_L_20201025_QP_gamma0_Gamma0_HV.tif
```

`2020-07-15` es el Sentinel-2 previo del curso (S2B, el mismo de la fusión Landsat y del CBERS de este práctico). Sin las dos líneas de SAOCOM el script corre igual, sin la banda L de fecha precisa (queda sólo el mosaico anual ALOS-2).

Valores por defecto: `--pixel 20`, `--c_pre 2020-07-16`, `--c_post 2020-09-26`, `--opt_pre` vacío (sin él no hay dNBR), `--opt_post 2020-10-13`, `--alos2_pre 2019`, `--alos2_post 2020`, SAOCOM vacío.

**Resultado esperado.**
- `Sitio A1_DELTA_QUEMAS, pixel 20 m (... x ...)`.
- `AVISO: el mosaico ALOS-2 es de 25 m y la grilla de 20 m...`. Es correcto: el indicador de banda L tiene menos detalle que el píxel, y se declara.
- Por bloque: `dVH mediana ... dB, dVV mediana ... dB`, `dHV mediana ... dB`, y para el óptico la nubosidad dentro del sitio de cada escena y `dNBR mediana ...; pixeles con dNBR > 0,27: ... %`.
- `Indicadores: ...\A1_DELTA_QUEMAS_indicadores_20m.tif (N capas: ...)`.

**Salidas.** `02_Subsets_SNAP_QGIS\A1_DELTA_QUEMAS_indicadores_20m.tif` (una banda por indicador, con nombre) y `02_Subsets_SNAP_QGIS\A1_DELTA_QUEMAS_indicadores_fuentes.csv` (la cita de cada capa: organismo, sensor, fecha, hora, URL).

**Ver en QGIS.** `Capa > Añadir capa > Añadir capa ráster…`. `Propiedades > Simbología > Pseudocolor monobanda` (Singleband pseudocolor), banda `dVH_C_dB`, mínimo −6, máximo 6, rampa divergente (rojo para negativo). Haga lo mismo con `dHV_L_ALOS2_dB` y con `dNBR` (0 a 0,8). Si quiere ver la escena radar misma, use el RGB copolarizada–cruzada–cociente (VV–VH–VV/VH) del Tp2 (`Tp2_02_rgb_copol_cruzada_cociente.py`), si se armó la pila del sitio.

**Control.**
- En las lagunas y el cauce, ΔVH es ruidoso (agua calma, señal muy baja en las dos fechas): no lo interprete.
- En lo no quemado, ΔVH no tiene por qué ser 0: en 2020 subió unos +3,7 dB, porque la fecha «después» (26/09) es una de las pasadas con todo el sitio mojado (lluvia de fines de agosto y rebrote). Antes de umbralizar, mida la mediana en lo no quemado y explíquela.
- Las medianas del sitio dicen poco: el área quemada es una parte del sitio. Lo que importa es la cola de la distribución (paso 2).

**Errores típicos.**
- `Sentinel-1 RTC: no hay escena el ... sobre el sitio.`: esa fecha no está en el catálogo RTC del Planetary Computer. Busque las fechas disponibles con `Tp1_03` y use una de ellas, de la misma órbita para pre y post.
- `Sin --opt_pre: no se calcula dNBR`: falta la fecha óptica previa.
- La nubosidad de la escena óptica en el sitio es alta: los píxeles con nube quedan sin dato (la SCL los excluye). Elija otra fecha cercana.
- Cuelgues de red: las URL del Planetary Computer se firman por una hora; vuelva a correr.

---

## Paso 2 · SINERGIA: un mapa por sensor y la tabla de coincidencias — SE CORRE

**Qué y por qué.** Cada sensor decide con su umbral. No se fusiona nada. Después se mide dónde coinciden y dónde no, en todo el sitio y por estrato de estructura. Es la pregunta de la diapositiva 28: comparar la caída de VH (C), la de HV (L) y el dNBR, y explicar por qué difieren el pajonal y el bosque de albardón.

```
python Tp5_02_sinergia.py --pixel 20
```

Umbrales: Otsu por defecto. Para fijarlos a mano (y declararlo): `--u_dvh 1 --u_dhv -2 --u_dhv_saocom 1 --u_dnbr 0.15`. El signo es fijo: quema si Δradar **<** umbral, o si dNBR **>** umbral.

**Por qué estos valores de partida.** Entre el 16/07 y el 26/09/2020 la retrodispersión subió en todo el sitio, también donde no hubo fuego: ΔVH vale unos +3,7 dB de mediana en lo no quemado y ΔHV de SAOCOM, +4 dB. A fines de agosto llovió después de semanas de sequía y la vegetación rebrotó: más humedad, más señal. El fuego no aparece como una caída absoluta (Δ < 0) sino como **unos 2,5 a 3 dB menos de aumento** que el entorno. Por eso los histogramas de radar tienen una sola moda, Otsu corta por la mitad (umbrales positivos que dejan medio sitio «quemado») y un umbral de −3 dB no detecta casi nada. Como punto de partida se propone 1 dB para la banda C y para SAOCOM (unos 2,7 dB por debajo de la mediana de lo no quemado). Para ALOS-2 se deja −2 dB, sabiendo que el mosaico anual mezcla fechas y casi no separa la quema. Para el dNBR, 0,15: en este humedal el NBR de julio ya es negativo y lo quemado tiene un dNBR de 0,26 de mediana, así que 0,27 deja afuera la mitad. Son puntos de partida: el grupo los revisa con sus histogramas y los declara.

**Resultado esperado.**
- `Cobertura de control: ...` (si existe).
- Una línea por sensor: `umbral de OTSU -x.xxx calculado sobre N valores; deja y % de los pixeles en la clase de interes (< -x.xxx)`.
- La tabla `Acuerdo entre sensores (sin fusionar)`: por región (`todo el sitio` y `control: <clase>`) y por par de sensores, `%_clase_sensor_1`, `%_clase_sensor_2`, `%_ambos`, `%_solo_1`, `%_solo_2`, `acuerdo_%`.
- Al final, si la cobertura de control sólo tiene agua, la indicación de separar por estrato del CCI.

**Ojo con la tabla de acuerdo:** sólo usa los píxeles con dato en **todos** los sensores, también en el óptico. Los píxeles con nube o humo el día del Sentinel-2 (sin dato en el dNBR) quedan afuera de la tabla, justo donde el radar tiene su ventaja («aun bajo humo»). Para ver qué detecta el radar bajo el humo, mire el mapa por sensor (`A1_quema_por_sensor_20m.tif`) en esos píxeles, y dígalo al interpretar.

**Salidas.** `05_Resultados\02_Rasters\A1_quema_por_sensor_20m.tif` (una banda por sensor, 1 = quemado), `05_Resultados\02_Rasters\A1_sensores_que_coinciden_20m.tif`, `05_Resultados\04_Tablas\A1_sinergia_coincidencias.csv`, los histogramas `05_Resultados\05_Graficos\histograma_<indicador>.png` y la figura `A1_sensores_que_coinciden.png`.

**Cómo se interpreta (la sinergia).**
- Abra cada histograma. Otsu supone **dos modas**. Si el histograma de ΔVH tiene una sola joroba con una cola, el umbral de Otsu cae en cualquier lado: fíjelo a mano mirando la cola y la referencia, y escríbalo.
- **El dNBR de 0,27** es el límite de severidad moderada-baja de Key y Benson, definido para bosques templados de América del Norte. En un humedal no se adopta: se calibra. Úselo sólo como punto de partida.
- Haga la comparación por estrato de estructura del CCI Biomass 2020 (pajonal < 15 Mg/ha, albardón ≥ 30 Mg/ha) en QGIS, con la Calculadora ráster, o en Orange (08_Orange\Tp5_A_indicadores_por_grupo.ows). La física predice que en el pajonal la C cae más que la L y que en el albardón la L acompaña: eso se evalúa con los números, no se supone. Con los datos del curso, en el albardón quemado ΔVH, ΔHV de SAOCOM y ΔHV de ALOS-2 quedan 3,4 a 4,1 dB por debajo del albardón no quemado; en el pajonal, la C apenas 0,7 dB y la L de SAOCOM 1,7 dB. La cobertura de control del Tp4 sólo tiene agua en A1 (ver «Antes de empezar»): no trae filas de pajonal ni de monte.
- `control: agua_permanente` debe dar 0 % de quema en todos los sensores: el script enmascara la clase 1 (el agua calma es oscura en el radar y se confunde con ceniza en el óptico).

**Control.** En clases que no pueden quemarse o casi no se quemaron (urbano, agua), el porcentaje marcado como quema por cada sensor debe ser bajo. Si la C marca mucha quema en `cultivo_pastura` o en zonas sin fuego, sospeche cambios de humedad o del nivel del agua entre julio y septiembre (2020 fue un año de bajante extraordinaria del Paraná).

**Errores típicos.**
- `No hay cobertura de control para A1_DELTA_QUEMAS (Tp4_01)...`: el script sigue, pero sin separar por clase ni enmascarar lagunas. Corra `Tp4_01` (ver «Antes de empezar»).
- `Hace falta al menos dos sensores para la sinergia.`: el paso 1 dejó menos de dos indicadores.
- `Muy pocos valores validos para Otsu`: el indicador está casi vacío (por ejemplo un óptico todo nublado).

---

## Paso 3 · Digitalizar el entrenamiento de la severidad — EN QGIS

**Qué y por qué.** El Random Forest de V4 necesita ejemplos de cada clase de severidad. Los dibuja el grupo. El script crea la capa vacía la primera vez que corre el paso 4, y en esa corrida produce V1 a V3 y se detiene antes de V4.

Primero corra (deja V1, V2, V3 y la capa vacía):

```
python Tp5_03_fusion.py --pixel 20 --regla mayoria
```

Debe ver `Se creo la capa de entrenamiento vacia: ...\04_Tablas_de_trabajo\entrenamiento_A1.gpkg` y `V4 queda pendiente hasta que se digitalice el entrenamiento.`

**En QGIS.**

1. Proyecto con SRC `EPSG:32721`. Cargue `A1_DELTA_QUEMAS_indicadores_20m.tif` dos veces: una con `dNBR` y otra con `dVH_C_dB` (pseudocolor, paso 1). Cargue `A1_sensores_que_coinciden_20m.tif`.
2. Para ver el terreno de 2020: el Sentinel-2 del 15/07 y del 13/10 y el Landsat 8 del 19/07 y del 07/10 (B7-B5-B4) del práctico. Como referencia visual de Sentinel-2 en falso color, el Copernicus Browser (https://browser.dataspace.copernicus.eu) muestra la escena del 13/10/2020.
3. `Capa > Añadir capa > Añadir capa vectorial…`: `04_Tablas_de_trabajo\entrenamiento_A1.gpkg`, capa `entrenamiento` (polígonos, `EPSG:32721`, campos `codigo` entero y `clase` texto).
4. `Propiedades… > Formulario de atributos`, campo `codigo`, `Mapa de valores`: `1` quemado alta, `2` quemado baja, `3` no quemado, `4` agua.
5. `Conmutar edición`, `Añadir polígono` (se habilita apenas se activa la edición), dibuje, complete `codigo` y `clase`. `Guardar edición de la capa`.

**Criterios.**
- **Polígonos al azar.** Los polígonos se trazan al azar, no donde la clase se ve más fácil. `Vectorial > Herramientas de investigación > Puntos aleatorios en la extensión` (Random Points in Extent), con la extensión del sitio y 100 puntos. Recorra los puntos en el orden en que salieron (campo `id`) y trace un polígono alrededor de cada punto que caiga en una cubierta inequívoca, hasta completar el número pedido para cada clase; los puntos que caen en bordes o en cubiertas dudosas se saltean y se anotan. Elegir los lugares a ojo concentra los polígonos en los ejemplos más típicos y hace que el mapa parezca mejor de lo que es. Con 100 puntos uniformes las clases raras (las que ocupan pocas hectáreas: monte cerrado, suelo desnudo, severidad alta) casi nunca se completan. Para esas clases, haga un **sorteo estratificado**: convierta a polígono el estrato de la clase (`Ráster > Conversión > Poligonizar` sobre MapBiomas, o sobre el rango del índice que define la clase) y use `Vectorial > Herramientas de investigación > Puntos aleatorios dentro de polígonos`; recorra esos puntos también en el orden en que salieron, con la misma revisión en la imagen. Anote de qué sorteo salió cada polígono.
- **Severidad alta (1):** oliva o verde el 15/07 y rojo pleno el 13/10 (B12-B8A-B4), dNBR ≥ 0,40.
- **Severidad baja (2):** pardo a rojo o rosado el 13/10, dNBR 0,12 a 0,40.
- **No quemado (3):** pajonal, monte y cultivos verdes, en varias partes del sitio.
- **Agua (4):** lagunas y cauces. Sin esta clase, el modelo confunde agua oscura con ceniza.
- Polígonos de 100 × 100 m (5 × 5 píxeles de 20 m), repartidos, lejos de los bordes entre clases; al menos 5 a 10 por clase.
- **Lejos de donde se validará.** No concentre el entrenamiento en una sola isla: los puntos del Tp4 todavía no existen (por eso este paso va antes de `Tp4_02`). Después de sortear las muestras del Tp4, compruebe que ningún punto cae dentro de un polígono de entrenamiento: Vectorial > Herramientas de investigación > Seleccionar por localización (puntos que intersecan los polígonos: debe dar 0), o Vectorial > Herramientas de análisis > Distancia al centro más cercano para ver a qué distancia quedan. Si muchos caen dentro o muy cerca, la exactitud se infla.

---

## Paso 4 · FUSIÓN: las cuatro variantes y la severidad — SE CORRE

```
python Tp5_03_fusion.py --pixel 20 --regla mayoria
```

`--regla` admite `mayoria` (por defecto), `union` o `interseccion`.

**Qué hace cada variante.**
- **V1 Óptico solo:** el mapa de dNBR del paso 2. Un sensor; no es fusión.
- **V2 SAR solo (C):** el mapa de ΔVH del paso 2. Un sensor; no es fusión.
- **V3 SAR multibanda: FUSIÓN DE DECISIÓN.** Combina los mapas binarios de **todos** los radares del paso 2 (C, L ALOS-2 y, si está, L SAOCOM) con la regla elegida. Con dos radares, `mayoria` exige que los dos digan quemado (es igual a `interseccion`); con tres, dos de tres. Donde un sensor no tiene dato, deciden los demás. Es decisión, y no píxel, porque C y el mosaico ALOS-2 difieren en píxel y en fecha.
- **V4 Multisensor: FUSIÓN DE RASGO.** Random Forest con las capas `dVH_C_dB`, `dVV_C_dB`, `dHV_L_ALOS2_dB`, `dHV_SAOCOM_dB`, `dNBR`, `RdNBR` que existan. 300 árboles, clases equilibradas, hasta 20.000 píxeles de entrenamiento repartidos por igual entre clases, semilla 2026. Es de rasgo porque entran **variables derivadas** de cada sensor, no las bandas originales. Se pide severidad, que es graduada: el modelo necesita ver los valores, no sólo el sí o no de cada sensor.

**Resultado esperado.**
- `V1 optico solo -> A1_variante_optico.tif`, `V2 SAR solo (C) -> A1_variante_C.tif`, `V3 SAR multibanda -> A1_variante_CL.tif (fusion de decision, regla mayoria, ...)`.
- `Pixeles de entrenamiento: N` y `Exactitud fuera de bolsa: 0.xxx <- OPTIMISTA (pixeles vecinos de los mismos poligonos).`
- La importancia de cada variable, de mayor a menor.
- Las hectáreas de cada clase de severidad.

**Salidas.** En `05_Resultados\02_Rasters\`: `A1_variante_optico.tif`, `A1_variante_C.tif`, `A1_variante_CL.tif` (bandas `clase` y `votos`), `A1_severidad_multisensor.tif` (bandas `severidad` y `probabilidad`) y `A1_variante_multisensor.tif` (1 quemado = alta + baja; 2 no quemado, incluye agua). La tabla `05_Resultados\04_Tablas\A1_importancia_variables.csv` y la figura `05_Resultados\05_Graficos\A1_severidad_multisensor.png`, con la cita «Fuente» al pie.

**Cómo se interpreta.**
- **La exactitud fuera de bolsa no se informa como exactitud.** Se calcula con píxeles vecinos de los mismos polígonos de entrenamiento: siempre es optimista. La exactitud que vale es la del Tp4.
- La importancia dice qué variables usó el modelo, no cuáles son «verdaderas». Variables correlacionadas (dNBR y RdNBR; ΔVH y ΔVV) se reparten la importancia.
- En V4, un píxel sin dato en **cualquiera** de las capas (por ejemplo, nube en el óptico) queda sin clasificar.

**Control.** Abra `A1_severidad_multisensor.tif` en QGIS (`Paletizado/valores únicos`, banda `severidad`) junto con los polígonos de entrenamiento: dentro de ellos la clase debe coincidir casi siempre. Fuera, mire la banda `probabilidad`: valores bajos (menos de 0,5) marcan píxeles donde el modelo duda.

**Errores típicos.**
- `La capa de entrenamiento esta vacia. V4 queda pendiente.`: no se guardaron los polígonos.
- `ValueError: Muy pocos pixeles de entrenamiento con dato en todas las capas (N).`: los polígonos caen donde alguna capa no tiene dato (nubes). Muévalos o dibuje más.
- `FileNotFoundError` con `A1_quema_por_sensor_20m.tif`: no corrió el paso 2 con el mismo `--pixel`.

---

## Paso 5 · Validar las variantes con el Tp4 — SE CORRE + EN QGIS

Cada variante se valida con su propia muestra. Repártanse las variantes entre grupos. Desde la carpeta de scripts del Tp4:

```
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp4_Validacion\03_Scripts
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp5_Incendios\05_Resultados\02_Rasters\A1_variante_multisensor.tif --banda 1
```

Etiquete al azar en QGIS con códigos 1 quemado y 2 no quemado, como explica la guía del Tp4 (paso 7). La referencia sale de Landsat 8 (19/07 y 07/10/2020, B7-B5-B4), independiente del Sentinel-2 que usan la V1 y la V4; si se usa Sentinel-2, la validación de V1 y V4 queda sesgada a favor y se declara. Cada grupo revisa además 30 puntos al azar de otro grupo (04_Tablas_de_trabajo\revision_30_puntos_segundo_interprete.csv) y anota el acuerdo.

```
python Tp4_03_exactitud_y_area.py --nombre A1_variante_multisensor --nombres_clase "1=quemado,2=no_quemado"
```

Repita con `A1_variante_optico`, `A1_variante_C` y `A1_variante_CL`. Después:

```
python Tp4_04_tabla_de_variantes.py --tp Tp5 --clase quemado ^
    --variante "Optico solo|Sentinel-2|A1_variante_optico" ^
    --variante "SAR solo (C)|Sentinel-1|A1_variante_C" ^
    --variante "SAR multibanda|C + L|A1_variante_CL" ^
    --variante "Multisensor|SAR (C + L) + optico|A1_variante_multisensor"
```

Salida: `Tp5_Incendios\05_Resultados\04_Tablas\tabla_de_variantes_quemado.csv`.

**Comparación en la superficie común.** Las cuatro variantes no cubren lo mismo (la V4 sólo donde hay las seis capas). Desde la carpeta del Tp5:

```
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp5_Incendios\03_Scripts
python Tp5_05_dominio_comun.py
```

Evalúa las cuatro variantes en los píxeles con dato en las cuatro, con los puntos de cada muestra que caen ahí, y estima la diferencia de cada una con el óptico con su IC del 95 %. Con los datos del curso, en esa superficie el óptico da 0,906 ± 0,057 y la V4 0,835 ± 0,061; la diferencia (−0,071 ± 0,084) no es significativa. Es una estimación de dominio: las áreas valen para esa superficie y no se extrapolan al sitio.

En «datos usados» de la variante multisensor escriba lo que realmente entró: SAR (C + L) + óptico. GEDI no entró en el modelo.

**La severidad tiene que validarse aparte.** La tabla de variantes mide el **perímetro** (quemado / no quemado): `A1_variante_multisensor` junta las dos clases de severidad en «quemado». El mapa de severidad V4 (`A1_severidad_multisensor.tif`, banda `severidad`: 1 severidad alta, 2 severidad baja, 3 no quemado, 4 agua) necesita su propia muestra estratificada por esas cuatro clases:

```
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp5_Incendios\05_Resultados\02_Rasters\A1_severidad_multisensor.tif --banda 1
python Tp4_03_exactitud_y_area.py --nombre A1_severidad_multisensor --nombres_clase "1=severidad_alta,2=severidad_baja,3=no_quemado,4=agua"
```

Etiquetar severidad al azar es más difícil que etiquetar quemado: la referencia es el Sentinel-2 posterior (y el dNBR, que entró al modelo: declárelo). Si no hay tiempo para esta muestra, el mapa de severidad se entrega con la leyenda **«severidad no validada»** y sólo el perímetro lleva exactitud.

---

## Paso 6 · SINERGIA: cambio de altura GEDI — SE CORRE

**Qué y por qué.** GEDI mide la altura del dosel (rh98: altura bajo la cual está el 98 % de la energía devuelta). Si el mapa dice «quemado» en un albardón, la estructura debería haber bajado. Es evidencia **independiente**: no entró en ningún modelo. GEDI no repite la huella, así que no se resta huella contra huella: se arman celdas de 100 m y, en cada celda con huellas válidas antes **y** después, se compara la mediana de rh98.

Vuelva a la carpeta del Tp5:

```
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp5_Incendios\03_Scripts
python Tp5_04_gedi_cambio_de_altura.py --antes_desde 2019-10-01 --antes_hasta 2020-04-01 --despues_desde 2020-10-01 --despues_hasta 2021-03-31 --celda 100
```

Valores por defecto: --antes_desde 2019-10-01, --antes_hasta 2020-04-01, --despues_desde 2020-10-01, --despues_hasta 2021-03-31 (la misma estación antes y después), --celda 100, --min_huellas 2.

Las huellas ya vienen filtradas desde el Tp1 (`l2a_quality_flag_rel3` = 1, `degrade_flag` = 0, `sensitivity` ≥ 0,95, `surface_flag` = 1); el script usa sólo las que tienen `valido` verdadero.

**Resultado esperado.**
- Primero, el aviso del hueco de GEDI y las dos ventanas: `GEDI no adquirió entre el 17/03/2023 y el 26/04/2024; ...` y `Ventana 'antes': ...`, `Ventana 'después': ...`.
- `Huellas GEDI válidas: N (antes a, durante b, después c, fuera de las ventanas d)`. Sólo se usan las de «antes» y «después».
- `Celdas de 100 m con 2 huellas o más antes y después: M`.
- Una tabla por clase del mapa (`quemado (mapa)`, `no quemado (mapa)`) con `count`, `mean`, `50%`, `std` de Δrh98.
- `X % de las celdas tiene rh98 previo < 3 m: ahí GEDI no mide la altura del pajonal, sino el piso del instrumento...` y cuántas celdas de 3 m o más caen en lo quemado.

**Salidas.** `05_Resultados\04_Tablas\A1_delta_rh98_por_celda.csv` y `A1_delta_rh98_por_clase.csv`.

**Cómo se interpreta.**
- En las celdas con rh98 previo menor de 3 m GEDI no mide la altura del pajonal: ese valor es el piso del instrumento sobre terreno llano, y el Δrh98 allí no tiene significado estructural. La evidencia útil está en las celdas de albardón, pero en A1 hay muy pocas celdas de albardón con huellas antes y después (2 en lo quemado con los datos del curso): el resultado suele ser no concluyente.
- Si la mediana de Δrh98 en celdas «quemado» es claramente negativa y en «no quemado» cercana a cero, la estructura confirma al mapa. Si no, hay algo que revisar (en el mapa o en la cantidad de celdas).
- Pocas celdas: es lo esperable con un LiDAR que muestrea. Se declara cuántas hubo.

**Errores típicos.**
- `Falta ...lidar_A1_DELTA_QUEMAS.gpkg: correr Tp1_05_buscar_lidar.py --sitio A1_DELTA_QUEMAS con --descargar.`
- `Falta ...\A1_variante_multisensor.tif: correr antes Tp5_03_fusion.py con la capa de entrenamiento digitalizada.`: el paso 4 no llegó a V4 (falta digitalizar el entrenamiento o no se guardó la edición). Este paso necesita la variante multisensor.
- `No hay celdas con huellas antes y despues. Ampliar --celda o las fechas, y declararlo.`: pruebe `--celda 200` y dígalo en el informe (celdas más grandes mezclan quemado y no quemado).

---

## Paso opcional · Del Sentinel-1 sin procesar a γ⁰ — EN SNAP

**Qué y por qué.** Todos los Sentinel-1 de este práctico vienen ya corregidos: son el γ⁰ RTC del Planetary Computer. Este paso muestra de dónde sale ese γ⁰. Se parte del producto GRDH de nivel 1 tal como lo entrega ESA, el `.zip` con la carpeta `.SAFE` adentro (mediciones, anotaciones, calibración, ruido y órbita predicha), y se recorre en SNAP la misma cadena que usó el docente. El resultado del docente viene hecho y sirve para controlar el suyo.

**Insumo.** `00_COMUN\08_Originales_crudos\S1_CRUDO\S1A_IW_GRDH_1SDV_20200908T091510_20200908T091535_034265_03FB78_6C2A.zip` (Sentinel-1A IW GRDH, VV + VH, 08/09/2020). Se eligió esa pasada porque es la de las quemas y tiene Sentinel-2 del mismo día.

**Lo que viene hecho.** `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo` de este práctico: `SNAP_DIMAP` (γ⁰ VV y VH lineales, bandas virtuales en dB y cociente VV/VH en dB, metadatos completos), `QGIS_GeoTIFF` (con `_metadatos.txt`), `RGB_copol_cruzada_cociente` (R = VV, G = VH, B = VV/VH) y `Grafos_SNAP` (el grafo XML). El detalle está en `LEEME_S1_crudo.md` de esa carpeta.

**Dónde.** SNAP Desktop. La primera vez SNAP baja la órbita precisa y el Copernicus DEM, así que necesita internet. Hay dos formas de hacerlo.

**Forma rápida: el grafo del docente.**

1. `Tools > GraphBuilder`, botón `Load`, y elija `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\Grafos_SNAP\Grafo_A1_DELTA_QUEMAS_S1_20200908_gamma0_desde_crudo.xml`.
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

**Resultado esperado.**

- Un producto con `Gamma0_VV` y `Gamma0_VH` en lineal y sus bandas virtuales en dB.
- En `Metadata > Processing_Graph`, la lista de operadores en el orden en que se aplicaron. Ahí queda escrito todo lo que se le hizo al dato.
- En `Metadata > Abstracted_Metadata`, la misión, la fecha, la órbita y el ángulo de incidencia del original: el recorte no los pierde.
- Abierto junto al producto del docente (el `.dim` de `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\SNAP_DIMAP`), los dos se superponen en `World View` y se ven casi iguales.

**Comparación con el RTC del Planetary Computer.** El mismo día existe el γ⁰ RTC del Planetary Computer, en `00_COMUN\08_Originales_crudos\PLANETARY\A1_DELTA_QUEMAS\sentinel-1-rtc\` (carpeta que empieza con `20200908`). Diferencia mediana del γ⁰ de SNAP menos el RTC, en todo el sitio:

- VV: −1,50 dB (p5 a p95, −3,9 a +1,0 dB; correlación 0,82).
- VH: −3,34 dB (p5 a p95, −7,5 a −0,4 dB; correlación 0,78).

**Cómo se interpreta.**

- En VV, casi toda la diferencia es un desfase de normalización de `Terrain Flattening` de SNAP: su γ⁰ queda por debajo de σ⁰/cos θ aun en terreno plano. El desfase cambia con la escena y el ángulo de incidencia (−0,5 dB en Concordia, −1,0 dB en Federal). Su causa no está documentada.
- VH queda siempre más abajo que VV. Lo más probable es la remoción del ruido térmico, que pesa más cuanto más débil es la señal. No está verificado cómo trata el ruido el RTC del Planetary Computer.
- Consecuencia práctica: **nunca** calcule un cambio (Δ) entre una fecha procesada en SNAP y otra del RTC. Una diferencia de 1 a 3 dB entre cadenas de proceso es del mismo orden que la señal que se busca. Todas las fechas de una serie se procesan con la misma cadena.
- En el Delta la diferencia en VH (−3,3 dB) es la mayor del curso: agua y bañados, con retrodispersión cerca del piso de ruido. Es del mismo orden que la caída de VH por el fuego del paso 1: un ΔVH entre un γ⁰ de SNAP y un RTC no mediría el incendio, sino la diferencia de proceso.

**Errores típicos.**

- SNAP se queda en `Apply Orbit File` o en `Terrain Flattening` sin avanzar: está bajando la órbita o el DEM. Sin internet no puede; conéctese y repita.
- `Terrain Flattening` rechaza la entrada: la calibración no dejó la banda β⁰. Repita `Calibrate` con `Output beta0 band`.
- Falta de memoria o un proceso de horas: no recortó antes del aplanado. Haga el `Subset` antes.
- El producto no cubre el sitio: el recorte se definió por píxeles. Use la pestaña `Geo Coordinates`.
- QGIS no abre el `.zip`: es normal, el original es para SNAP. En QGIS use `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\QGIS_GeoTIFF`.

Fuente: ESA Copernicus, Sentinel-1A IW GRDH, 08/09/2020, S1A_IW_GRDH_1SDV_20200908T091510_20200908T091535_034265_03FB78_6C2A. Distribuido por ASF DAAC, https://search.asf.alaska.edu. Procesado con ESA SNAP y Copernicus DEM GLO-30.
