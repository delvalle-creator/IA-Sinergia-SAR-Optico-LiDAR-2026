# Tp10 — Guía paso a paso

**Viernes, 12 a 13 h y 14 a 16 h.** Pregunta: ¿cómo crece la ciudad y dónde se hunde el terreno?

Reparto sugerido del tiempo:

| Horario | Pasos |
|---|---|
| 12:00 – 12:40 | Pasos 0 a 3: preparar, correr el paso 1 (sinergia) y leer histogramas y tabla |
| 12:40 – 13:00 | Pasos 5 y 6: lanzar `Tp10_02` antes del corte (compuestos y Random Forest; unos 20 minutos) |
| 14:00 – 14:45 | Paso 4: revisar el entrenamiento en QGIS; paso 6: comparar las variantes. Lanzar `Tp10_03` (unos 40 minutos) |
| 14:45 – 15:45 | Pasos 8 a 10 mientras corre el paso 7: red SBAS (ver), referencia y control (QGIS), velocidad vertical |
| 15:45 – 16:00 | Paso 7: leer la expansión urbana 2019 → 2026 (fusión de decisión) |
| Después | Paso 11: validación con el Tp4 y respuestas |

La validación completa con el Tp4 (unos 140 puntos por mapa, al azar, al menos 50 en el estrato urbano) **no entra en las tres horas**. En clase se deja el muestreo diseñado; el etiquetado se termina fuera del horario (después del Tp10 no queda horario de clase para etiquetar).

Convenciones de esta guía:

- `D:\...\02_Practica` es `D:\CURSOS_CEREGEO_2026\02_Practica` en la computadora del docente. Use la ruta de su equipo.
- Los menús de QGIS están en la interfaz en español (QGIS 3.x). Si su QGIS está en inglés, el menú equivalente va entre paréntesis la primera vez.
- Cada programa escribe una **bitácora** (`.log`) en `05_Resultados/06_Control_calidad/`. Lo que ve en pantalla queda guardado ahí: no copie a mano.

**Landsat 8 y 9.** Escenas de este práctico, la pasada más cercana a cada Sentinel-2 con el sitio cubierto y despejado: Concordia, `B_CONCORDIA_L8_20260915`: Landsat 8 del 15/09/2026 para el Sentinel-2 del 16/09/2026. La temperatura de superficie (`ST_B10_C`) permite mirar la isla de calor urbana junto con el mapa de superficie impermeable.

Son Colección 2, Nivel 2 de USGS (reflectancia y temperatura de superficie, píxel de 30 m), bajadas del Planetary Computer. Están en `02_Subsets_SNAP_QGIS\SNAP_DIMAP` y `QGIS_GeoTIFF`, con las bandas `SR_B1` a `SR_B7` (reflectancia), `ST_B10` (temperatura, K), `ST_QA`, `QA_PIXEL` y las virtuales `NDVI` y `ST_B10_C` (°C).

Landsat 9 da imágenes desde el 31/10/2021; antes sólo hay Landsat 8. Los dos llevan instrumentos gemelos (OLI y TIRS) y se comparan entre sí sin ajuste. Con Sentinel-2 no: el píxel es de 30 m contra 10 y 20 m, y las bandas no coinciden del todo (el infrarrojo cercano de Landsat, 865 nm, equivale a la B8A, no a la B08).

Fuente: USGS / NASA, Landsat 8 y Landsat 9 OLI/TIRS, Colección 2 Nivel 2, distribuido por Microsoft Planetary Computer, https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2

**Fusión Landsat + Sentinel-2.** El Landsat también viene afinado a 10 m con el detalle espacial del Sentinel-2 de la fecha más cercana: se lo interpola a la grilla de 10 m y se le suma el detalle fino de la banda Sentinel-2 de 10 m que más se le parece, escalado por una regresión entre los dos sensores (filtro pasa-altos con modulación por regresión, HPF). Trae las bandas `SR_B1` a `SR_B7` en reflectancia, `mascara_detalle` (1 = se agregó detalle; 0 = nube, sombra o falta de dato en alguna de las dos) y el `NDVI` virtual; el método y la calidad de cada banda están en los metadatos.

El control es el ERGAS: la imagen afinada se lleva de nuevo a 30 m y se compara con el Landsat original; por debajo de 3 la fusión es buena. Sirve para mirar e interpretar, con tres cuidados: un cambio real entre las dos fechas aparece como detalle falso; las bandas 6 y 7 (infrarrojo de onda corta) toman el detalle de una banda de 10 m de otra región del espectro y son las menos confiables; y la temperatura no se afina.

En este práctico: `B_CONCORDIA_L8_20260915_fusion_S2_20260916_10m`: 1 día entre las dos imágenes; ERGAS 1,45. En el visible la correlación entre los sensores es baja (0,5), posiblemente por el agua del río Uruguay y del embalse, que cambia mucho de un día a otro.

**Pléiades y Pléiades Neo de CONAE.** Referencia visual de muy alta resolución del casco urbano (Pléiades, 0,5 m; Pléiades Neo, 0,3 m), 2022-2023, del proyecto Impactar de CONAE. Es un servicio de mapas y necesita internet: en `02_Subsets_SNAP_QGIS\Pleiades_CONAE_WMS` hay un `.xml` por localidad que se arrastra a QGIS (instrucciones en el `LEEME.md` de esa carpeta). Sirve para mirar y digitalizar, no para calcular: es RGB color real, sin infrarrojo ni reflectancia, y la fecha exacta no está publicada, sólo el año.

En este práctico: Concordia y General Roca (localidad del departamento Concordia, Entre Ríos; no es la ciudad de Río Negro), Pléiades Neo 2023; Gran Paraná, Pléiades 2022; Diamante, Pléiades 2022.

Fuente: CONAE, proyecto Impactar; Pléiades y Pléiades Neo, Airbus Defence and Space. Servicio WMS: https://geotematico01.conae.gov.ar/geoserver/wms; catálogo: https://catalogos.conae.gov.ar/catalogo/catalogoGeoServiciosOGC.html

**CBERS-4A, cámara WPM (INPE).** Pancromática de 2 m y multiespectral de 8 m (azul, verde, rojo e infrarrojo cercano), producto L4 ortorrectificado, en números digitales. Cada escena viene en dos productos: `..._MS_8m` (las cuatro bandas originales) y `..._pansharpened_2m` (la pancromática y las cuatro bandas afinadas a 2 m por Brovey ponderado, el método por defecto de GDAL). Es un pansharpening clásico: pancromática y multiespectral del mismo satélite y del mismo instante; compárelo con la fusión Landsat + Sentinel-2, que combina dos sensores y dos fechas. El control es el mismo ERGAS (por debajo de 3, bueno). Los números digitales no son reflectancia y el Brovey altera la radiometría: sirve para mirar y digitalizar, no para calcular índices. Cubre una zona de 12 a 21 km, no el sitio entero, y la escena se eligió a ojo, sin nubes, porque el catálogo del INPE no informa la nubosidad.

En este práctico: Concordia, `B_CONCORDIA_CBERS4A_CONCORDIA_20260715_...` (15/07/2026, 63 días antes del Sentinel-2, con una nube chica en el noroeste; ERGAS 1,44), y Gran Paraná, `B_CONCORDIA_CBERS4A_GRAN_PARANA_20260926_...` (26/09/2026; ERGAS 3,30, apenas por encima de 3: conserva peor la radiometría). **Ojo con el nombre:** el prefijo `B_CONCORDIA_` de los productos de Gran Paraná (y de `B_CONCORDIA_E_PARANA_DIAMANTE_AlphaEarth_...`) es un resto de cómo se armaron; cubren el sitio `E_PARANA_DIAMANTE`, no Concordia. Se dejaron con ese nombre porque el `.dim` apunta a su carpeta `.data` por nombre y renombrarlos lo rompería.

Fuente: INPE / CAST, CBERS-4A WPM L4, licencia CC BY 4.0. Catálogo STAC del INPE, colección CB4A-WPM-L4-DN-1, https://data.inpe.br/stac/browser/collections/CB4A-WPM-L4-DN-1

**Embeddings anuales AlphaEarth Foundations (Google y Google DeepMind).** 64 números por píxel de 10 m que resumen un año entero de Sentinel-1, Sentinel-2, Landsat, GEDI, clima y otras fuentes, aprendidos por un modelo de inteligencia artificial. Las dimensiones (`A00` a `A63`) no tienen significado físico propio: sirven para clasificar con pocas muestras, buscar zonas parecidas y detectar cambios entre años. Vienen en enteros de 8 bits tal como los entrega Google (`..._AlphaEarth_embeddings_<año>_10m`); para pasarlos a valores reales, valor = signo(DN) × (DN / 127,5)², y −128 es sin dato. El `..._CP1_CP2_CP3_RGB_8bit.tif` muestra las tres primeras componentes principales para mirar en QGIS; sus colores no tienen significado fijo. Resumen un año, no una fecha; 2026 todavía no existe y se usa 2025, el último.

En este práctico: Concordia y Paraná-Diamante, 2025 (en lugar de 2026).

Fuente: The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind (CC BY 4.0). Copia en Source Cooperative (Taylor Geospatial), https://source.coop/tge-labs/aef

---

## Paso 0 — Preparar la consola (Miniforge)

**Qué y por qué.** Todos los programas usan el entorno `sar`, que tiene las bibliotecas del curso, y buscan solos la carpeta `00_COMUN` con la configuración común (sitios, grilla EPSG:32721, rutas).

**Dónde.** Menú Inicio de Windows → **Miniforge Prompt**.

**Órdenes.**

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp10_Impacto_urbano\03_Scripts
python ..\..\00_COMUN\configuracion_comun.py
```

**Qué debe observar.** La lista de sitios con su ventana y, arriba, las carpetas de originales. `B_CONCORDIA` y `E_PARANA_DIAMANTE` tienen que figurar.

**Control.** Que no diga `NO EXISTE` en la carpeta de originales. Si los originales están en otro disco, defina la variable antes de correr nada:

```
set CURSO_SAR_ORIGINALES=E:\ORIGINALES_CURSO
set CURSO_SAR_NOVASAR=E:\IMÁGENES NOVASAR-1 2023 2024\ENTRE RIOS-SANTA FE
```

(Las rutas son ejemplos: escriba las de su equipo. `set` vale sólo para esa ventana de consola.)

**Errores típicos.**

- `conda: command not found` o `"conda" no se reconoce`: abrió el símbolo del sistema común y no el **Miniforge Prompt**.
- `ModuleNotFoundError`: no activó `sar`. El nombre del entorno aparece entre paréntesis al principio de la línea.
- `cd` no cambia de disco: falta `/d`.

---

## Paso 1 — Verificar los insumos que YA VIENEN HECHOS

**Qué y por qué.** Tres insumos tardan horas o piden cuenta: el docente los dejó listos. Verifíquelos antes de empezar para no descubrir a mitad del práctico que falta uno.

**Dónde.** Explorador de Windows o la consola.

**Órdenes.**

```
dir /b ..\..\00_COMUN\08_Originales_crudos\NISAR\*20260918*.h5
dir /s /b ..\02_Subsets_SNAP_QGIS\HyP3_E_PARANA_DIAMANTE\QGIS_GeoTIFF\*_vert_disp.tif
type ..\..\Tp3_Armonizacion\05_Resultados\04_Tablas\B_CONCORDIA_corregistro_S_NovaSAR_sigma0_HH_vs_OPT_S2_B08.csv
```

(Si no definió `CURSO_SAR_ORIGINALES`, los originales están en `..\..\00_COMUN\08_Originales_crudos`.)

**Qué debe observar.**

1. El archivo `NISAR_L2_PR_GCOV_031_010_D_104_2005_DHDH_A_20260918T215921_20260918T215955_P05023_F_F_J_001.h5`. **El NISAR del 18/09/2026 sobre Concordia no está en los mosaicos del Delta:** el docente lo bajó aparte. La ruta completa la va a pegar en el paso 2.
2. Una lista de archivos `..._vert_disp.tif` (uno por par de interferograma).
3. La tabla de corregistro de NovaSAR frente a Sentinel-2 (el nombre lleva el par: capa móvil `_vs_` capa de referencia), con las columnas `mediana_dx_px` y `mediana_dy_px`.

**Si falta el NISAR.** Se baja con el Tp1 (necesita la cuenta de NASA Earthdata en `.netrc` o en la variable `EARTHDATA_TOKEN`; la credencial nunca se escribe en un programa):

```
python ..\..\Tp1_Convergencia\03_Scripts\Tp1_04_buscar_asf.py --sitio B_CONCORDIA --desde 2026-09-17 --hasta 2026-09-19 --solo NISAR --descargar 1
```

Lo deja en `00_COMUN\08_Originales_crudos\ASF\B_CONCORDIA\NISAR\`: pase esa ruta en el paso 2.

**Si falta el corregistro de NovaSAR.** Se mide con el Tp2 y el Tp3 (unos 15 minutos; requiere internet):

```
python ..\..\Tp2_SAR_multibanda\03_Scripts\Tp2_01_pila_multibanda.py --sitio B_CONCORDIA --novasar 47942 --fecha_c 2026-09-16
python ..\..\Tp3_Armonizacion\03_Scripts\Tp3_01_cubo_comun.py --sitio B_CONCORDIA --fecha_optico 2026-09-16 --pixel 20
python ..\..\Tp3_Armonizacion\03_Scripts\Tp3_02_medir_corregistro.py --sitio B_CONCORDIA --pixel 20 --ref OPT_S2_B08 --mov S_NovaSAR_sigma0_HH
```

La bitácora de `Tp3_02` (`05_Resultados\06_Control_calidad\Tp3_02_B_CONCORDIA_S_NovaSAR_sigma0_HH_vs_OPT_S2_B08.log`) escribe una línea `Mediana: dx = ... px (... m este), dy = ... px (... m sur-norte, filas)`. **Los dos valores en metros** son los que va a pasar con `--desplazamiento DX DY` en el paso 2: DX positivo = este, DY positivo = norte. Si el corrimiento es rígido y mayor que un píxel, la bitácora termina con la orden lista para copiar: `Para NovaSAR pase a Tp2_01:  --desplazamiento DX DY`; si no es rígido, da la mediana como primera aproximación y avisa que una traslación sola no alcanza. Como referencia de orden de magnitud, otra escena NovaSAR del curso (47974, Bovril, medida en el Tp3 el 21/10/2026) necesita unos 92 m al oeste y 484 m al sur (`--desplazamiento -92 -484`) y no es rígida; la 47942 hay que medirla.

**Lo que dio la corrida del docente (20/10/2026) para la 47942.** Sólo 2 ventanas válidas (NovaSAR cubre el 39 % del sitio): `Mediana: dx = -0.45 px (-9 m este), dy = +15.40 px (-308 m sur-norte, filas)`, con una ventana que pide unos 200 m y otra unos 420 m en sentido norte–sur, y el veredicto `NO CUMPLE: el desplazamiento cambia entre ventanas (no es rigido)`. Por eso la bitácora **no** da la orden lista para copiar. Qué hacer en clase: (a) correr el paso 2 con `--desplazamiento -9 -308` (la mediana) y medir el residual a mano (ver «Control del residual de corregistro» más abajo), sabiendo que en partes del sitio quedará del orden de 100 m (5 píxeles de 20 m); o (b) no desplazar y usar la banda S **sólo para interpretar** (sinergia), no en la fusión `con_S`. Cualquiera de las dos se declara en el informe; la (b) es la más prudente.

**Corrida del docente del 23/10/2026: georreferencia con todos los puntos de enlace.** El `metadata.xml` de la 47942 trae 84 puntos de enlace, no sólo las cuatro esquinas. Con `--puntos_enlace todos` el programa ajusta la imagen con los 84 y el corrimiento que queda es chico y casi rígido: medido en 11 ventanas contra el VV de Sentinel-1 del 14/09/2026, unos 40 m al oeste (0 a 60 m según la ventana) y 100 m al norte (100 a 120 m). La orden del paso 2 queda con `--puntos_enlace todos --desplazamiento -40 100`. Con la misma medición, la pila del Tp9, ya corregida, deja un residual de 20 m o menos. Si su grupo mide otro valor, use el suyo y anótelo.

Como NovaSAR cubre sólo el 39 % de Concordia, puede que pocas ventanas tengan 80 % de dato en común. Si `Tp3_02` dice `Ninguna ventana tiene 80 % de dato en comun`, pruebe con `--ventanas 2` o `--min_comun 0.5`, como sugiere el propio mensaje.

**Si faltan los HyP3.** No se piden en clase: llevan horas. Trabaje con la carpeta que le indique el docente (`--carpeta` en el paso 10).

---

## Paso 2 — SINERGIA: doble rebote en C, S y L (`Tp10_01`, SE CORRE)

**Qué y por qué.** En la ciudad, la pared de un edificio y la calle forman un **diedro**: la onda rebota dos veces y vuelve directo a la antena. Por eso la ciudad es lo más brillante de una imagen de radar. Cada banda lo ve distinto: con la C (5,5 cm) la vegetación densa también da valores altos de VV y se confunde con lo urbano; la S (9,4 cm) de NovaSAR tiene 6 m de píxel y ve manzanas; la L (24 cm) atraviesa el follaje y ve edificación entre árboles. **Pero las tres bandas no difieren sólo en la longitud de onda:** la C está en VV y la S y la L en HH (en el diedro pared–calle el VV se atenúa por el efecto Brewster y el HH no, así que la ciudad brilla más en HH), y las pasadas son distintas (Sentinel-1 descendente hacia las 09:13 UTC, NISAR descendente hacia las 21:59 UTC, NovaSAR hacia la 01:36 UTC), con distinta dirección de mirada respecto de las calles. Al explicar una diferencia entre bandas, piense en las tres causas: longitud de onda, polarización y geometría. El programa hace **un mapa por banda**, con un umbral en dB, y compara los mapas **sin fusionarlos**.

**Dónde.** Miniforge Prompt.

**Orden** (pegue la ruta del NISAR del paso 1 y el desplazamiento medido en el Tp3):

```
python Tp10_01_doble_rebote_sinergia.py --nisar_h5 ..\..\00_COMUN\08_Originales_crudos\NISAR\NISAR_L2_PR_GCOV_031_010_D_104_2005_DHDH_A_20260918T215921_20260918T215955_P05023_F_F_J_001.h5 --puntos_enlace todos --desplazamiento DX DY
```

Valores por defecto que usa si no los cambia: `--sitio B_CONCORDIA`, `--pixel 20`, `--fecha 2026-09-16` (busca la Sentinel-1 RTC más cercana, ± 6 días), `--novasar 47942`, `--puntos_enlace esquinas` (con `todos` usa los 84 puntos del `metadata.xml`; ver el paso 1), umbrales `--u_c -3 --u_s -3 --u_l -3` (dB, clase urbana = por encima del umbral). Con `--otsu` reemplaza los manuales por Otsu.

**Qué debe observar en pantalla.**

- Bloque «Banda C – Sentinel-1»: la fecha y hora UTC de la escena y una línea `C_VV  umbral MANUAL -3.000 ...; deja X % de los pixeles en la clase de interes`.
- Bloque «Banda S – NovaSAR-1»: `S_HH ...` y `X % del sitio con dato` (debe rondar el 39 %). Si no pasó `--desplazamiento`, un AVISO: «a 6 m un error de 80 m son 13 pixeles».

**Control del residual de corregistro (EN QGIS, 10 min).** El programa aplica el desplazamiento pero no lo vuelve a medir; el residual se comprueba a mano:

1. Cargue la banda `S_HH` de `02_Subsets_SNAP_QGIS\B_CONCORDIA_urbano_por_banda_20m.tif` (ya desplazada) y la banda `OPT_S2_B08` del cubo del Tp3 (`Tp3_Armonizacion\02_Subsets_SNAP_QGIS\B_CONCORDIA_cubo_20m.tif`).
2. Elija **tres rasgos nítidos y separados** que se vean en las dos: la costanera, una cabecera de puente o del muelle, una esquina de la represa o un cruce de rutas.
3. Con `Ver > Herramientas de medición > Medir línea`, mida en cada uno la distancia entre el borde en S_HH y el mismo borde en B08. Anote las tres distancias y su dirección.
4. El **residual** es la mediana de las tres. Expréselo en metros y en píxeles de la grilla (20 m). Aceptable: menos de un píxel (20 m). Si las tres distancias van hacia el mismo lado y superan un píxel, el desplazamiento medido en el Tp3 no alcanzó: sume esa diferencia a DX, DY y vuelva a correr.

Anote DX, DY y el residual en el informe (pregunta 3).
- Bloque «Detalle»: tres líneas (6, 10 y 20 m) con hectáreas urbanas, número de manchas y perímetro/área.
- Bloque «Banda L – NISAR»: `L_HH ...`.
- Bloque «SINERGIA»: la línea `La tabla usa SOLO los pixeles con dato en todas las bandas (N): si entra NovaSAR, es su huella.` y la tabla de coincidencias para «todo el sitio» y, si existe la cobertura de control del Tp4, para «control: urbano».
- Al terminar: `SIGUIENTE PASO: python Tp10_02_fusion_pixel_urbano.py --sitio B_CONCORDIA --pixel 20`.

**Salidas.**

- `02_Subsets_SNAP_QGIS/B_CONCORDIA_urbano_por_banda_20m.tif`: bandas `C_VV`, `C_VH`, `S_HH`, `L_HH`, `L_HV` (γ⁰ o σ⁰ **lineal**), `mapa_C_VV`, `mapa_S_HH`, `mapa_L_HH` (1 urbano, 0 no) y `bandas_que_marcan_urbano` (0 a 3).
- `05_Resultados/04_Tablas/B_CONCORDIA_coincidencias_urbano.csv` y `B_CONCORDIA_detalle_6_10_20m.csv`.
- `05_Resultados/05_Graficos/B_CONCORDIA_hist_C_VV.png`, `_hist_S_HH.png`, `_hist_L_HH.png`.

**Control.**

1. **El histograma.** Abra cada `hist_*.png`. La línea naranja tiene que caer al **comienzo de la cola brillante**, no en el medio de la moda principal. La ciudad ocupa pocos píxeles del sitio: su moda casi no se ve, por eso Otsu no sirve por defecto. Si el porcentaje en la clase de interés es mayor que la fracción urbana razonable del sitio, el umbral está bajo: súbalo y vuelva a correr. Anote el umbral elegido y por qué. Lo que dio la corrida del docente (23/10/2026), con 10 polígonos de manzanas compactas del casco revisados en la imagen como referencia («urbano denso» en lo que sigue): en C, −3 dB marca sólo el 33 % de los píxeles de urbano denso y el 0,8 % del sitio (cae en el extremo de la cola); −6 dB marca el 71 % del urbano denso, 0 % de vegetación y de suelo, y el 3,7 % del sitio. En S, −3 dB marca el 84 % del urbano denso y 0 % de vegetación. En L, −3 dB marca también el 15 % de la vegetación (la L atraviesa el follaje y el tronco–suelo es otro diedro); 0 dB baja la vegetación al 4 % y deja el 92 % del urbano denso. MapBiomas da un 2,4 % del sitio como área urbana. El docente usó `--u_c -6 --u_s -3 --u_l 0`.
2. **La tabla.** La comparación sólo usa los píxeles donde **todas** las bandas tienen dato: si entró NovaSAR, la tabla se limita a su huella (el 39 % del sitio). La bitácora dice cuántos píxeles son. Dígalo cuando la cite.
3. **El detalle.** El programa iguala el número de vistas en las tres escalas antes del umbral (media en lineal de 3 × 3 a 6 m y de 2 × 2 a 10 m; a 20 m el remuestreo ya promedia unos 11 píxeles de 6 m), así la comparación mide el píxel y no un filtro distinto en cada escala, y descarta las manchas de menos de 400 m² en las tres escalas: sin eso, a 6 m el speckle fabrica manchas sueltas y el «detalle» medido es ruido. Con ese filtro, de 20 a 6 m el número de manchas y la relación perímetro/área deberían crecer porque aparecen manzanas y calles que a 20 m se funden. Si la superficie urbana cambia mucho entre escalas, el umbral no es independiente de la escala: anótelo.

**Errores típicos.**

- `Hace falta al menos dos bandas para la sinergia.`: falló la consulta al Planetary Computer (sin internet) y además falta el NISAR o NovaSAR. Lea los mensajes de cada bloque.
- `NovaSAR: No encuentro el GRD de la escena 47942`: la variable `CURSO_SAR_NOVASAR` no apunta a la carpeta de las escenas.
- `NISAR: El granulo ... no cubre el sitio`: bajó otro gránulo; vuelva al paso 1.
- `Sin Sentinel-1 RTC +/- 6 dias de 2026-09-16`: cambie `--fecha`.

---

## Paso 3 — Mirar el resultado del paso 2 (EN QGIS)

**Qué y por qué.** El número de la tabla no dice **dónde** coinciden y dónde no. En el mapa se ve si la diferencia es la vegetación de las quintas, los techos de los galpones o una manzana girada.

**Menús.**

1. `Proyecto > Propiedades > SRC`: escriba `32721` en el filtro y elija **WGS 84 / UTM zone 21S**. Aceptar.
2. Imagen de alta resolución de fondo: en el panel **Navegador**, clic derecho sobre **XYZ Tiles > Nueva conexión…**. Nombre `ESRI World Imagery`, URL `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`. Aceptar y arrastrar la conexión al mapa. Sirve **para mirar**, no como dato; si aparece en una figura, va con su cita de fuente.
3. `Capa > Añadir capa > Añadir capa ráster…` (`Layer > Add Layer > Add Raster Layer…`): `02_Subsets_SNAP_QGIS\B_CONCORDIA_urbano_por_banda_20m.tif`.
4. Clic derecho sobre la capa → `Propiedades > Simbología`. Tipo de renderizador **Gris monobanda**, banda `bandas_que_marcan_urbano`, mínimo 0 y máximo 3. O mejor **Pseudocolor monobanda** con modo **Intervalo igual** y 4 clases.
5. Para ver una banda de radar en dB: `Ráster > Calculadora ráster…`, expresión `10 * log10("B_CONCORDIA_urbano_por_banda_20m@1")`, salida temporal. Si entró Sentinel-1, la banda 1 es `C_VV`; si no, el orden cambia: verifique el nombre de cada banda en `Propiedades > Información`. Estírela de −25 a 5 dB. **Sólo para ver**: no use esa capa para calcular nada.
6. RGB dual-pol de la banda C, copolarizada / cruzada / cociente: con la calculadora haga VV dB, VH dB y el cociente VV/VH en dB (`VV_dB − VH_dB`), y combínelas con `Ráster > Miscelánea > Combinar…` (`Merge`, opción «Situar cada archivo de entrada en una banda separada»). Simbología **Color multibanda**: rojo = VV (dB), verde = VH (dB), azul = cociente VV/VH (dB).

**Qué debe observar.** El centro de Concordia con valor 3 (las tres bandas lo marcan). Barrios con arbolado: 1 o 2 (L sí, C no). El embalse de Salto Grande y el río Uruguay en 0 (el agua es especular y oscura), salvo con viento.

**Control.** Identifique (`Ver > Identificar objetos espaciales`, Ctrl+Mayús+I) tres sitios donde las bandas discrepan y explique cada uno con el mecanismo físico. Ésa es la sinergia: ocurre en su razonamiento, no en el programa.

**Error típico.** El ráster aparece negro: está en lineal con cola larga; use la calculadora en dB o fije mínimo y máximo a mano.

**Una segunda banda L, cuadripolar: SAOCOM (EN QGIS).** CONAE entregó un SAOCOM-1B del 16/09/2026 sobre Concordia (TOPSAR Narrow A, HH, HV, VH y VV), dos días antes del NISAR, ya en γ⁰ lineal a 20 m: `02_Subsets_SNAP_QGIS\SAOCOM_gamma0\QGIS_GeoTIFF\B_CONCORDIA_SAOCOM_L_20260916_QP_gamma0_Gamma0_HH.tif` (y `_HV`, `_VV`). El RGB copolarizada–cruzada–cociente ya armado está en `SAOCOM_gamma0\RGB_copol_cruzada_cociente`. Es la misma banda que NISAR con otra geometría: los dos en órbita descendente, pero SAOCOM mira hacia el oeste y NISAR hacia el este.

1. Con la calculadora ráster haga `10 * log10("..._Gamma0_HH@1") > 0`: el urbano de SAOCOM con el mismo umbral que la L de NISAR. Compárelo con la banda `mapa_L_HH` de `B_CONCORDIA_urbano_por_banda_20m.tif`. ¿Dónde marca uno y no el otro? Mire el sur de Salto.
2. Haga `10 * log10("..._Gamma0_HH@1") - 10 * log10("..._Gamma0_VV@1")` (HH − VV en dB) y estírelo de −6 a 6 dB. ¿Qué pasa en la ciudad, en el campo y en el monte? Relaciónelo con el efecto Brewster en el diedro: la HH se refleja casi entera en las dos caras, la VV pierde en cada rebote.
3. Anote: ¿cuánto del desacuerdo entre bandas de la tabla del paso 2 puede ser de geometría y no de longitud de onda?

Referencia del docente: con L HH > 0 dB, SAOCOM marca el 2,6 % del sitio y NISAR el 3,2 %; coinciden en el 1,7 % del sitio y en el 84 % de la ciudad de control. HH − VV mediano: 6 dB en el urbano denso, 4 dB en el abierto, 1,6 dB en la vegetación, 0,8 dB en el suelo desnudo.

También hay un SAOCOM del 22/09/2026 sobre Paraná – Diamante (`E_PARANA_DIAMANTE_SAOCOM_L_20260922_QP_gamma0`), para mirar la ciudad y las islas en banda L junto al mapa de velocidad del paso 10. Una sola fecha no mide deformación: sirve para reconocer las coberturas.

---

## Paso 4 — El entrenamiento: píxeles estables de MapBiomas, en proporción al paisaje (EN QGIS)

**Qué y por qué.** El Random Forest aprende de ejemplos, y aprende también **cuánto** hay de cada clase. Si se le dan 10 polígonos de ciudad y 10 de campo, «entiende» que la ciudad ocupa lo mismo que el campo y marca ciudad de más: en Concordia la ciudad es menos del 5 % del sitio. Por eso el entrenamiento tiene que estar **en proporción al paisaje**, con un mínimo para las clases chicas (Waldner et al., 2017, https://doi.org/10.1080/2150704X.2017.1362124).

El programa del paso 6 toma el entrenamiento de **MapBiomas Argentina** (Colección 3, leyenda oficial): sólo los píxeles **estables**, que tienen la misma clase en 2023, 2024 y 2025, y los sortea en proporción a la superficie de cada clase (20 000 píxeles, al menos 600 por clase). Las clases del Tp10:

| `codigo` | Clase | Clases de MapBiomas |
|---|---|---|
| 1 | urbano | 24 área urbanizada |
| 2 | vegetación leñosa | 3, 4, 5, 6 bosques; 9 silvicultura (eucalipto, pino); 35 y 36 cultivos perennes (citrus) |
| 3 | herbáceas y cultivos | 11, 12, 13, 15, 18 a 21, 39 a 41, 46 a 48, 62 y 63 |
| 4 | agua | 26, 31, 33 |
| 5 | suelo desnudo y otras no vegetadas | 22, 23, 25, 29, 30 |

Las plantaciones de eucalipto tienen su propia clase porque son las que más se confunden con la ciudad en el radar: el volumen de las copas también brilla.

MapBiomas Argentina no cubre el lado uruguayo (Salto): el entrenamiento sale sólo de la Argentina y el clasificador se aplica a todo el sitio.

**Menús (después de correr el paso 6).**

1. `Capa > Añadir capa > Añadir capa vectorial…`: `04_Tablas_de_trabajo\entrenamiento_mapbiomas_B_CONCORDIA.gpkg`, capa `entrenamiento` (un punto por píxel de entrenamiento, con `codigo` y `clase`).
2. Simbología **Categorizado** por `clase`.
3. Revise **30 puntos al azar** de la clase urbano y 30 de vegetación leñosa sobre la imagen de alta resolución: `Vectorial > Herramientas de investigación > Selección aleatoria` (30 objetos), y recórralos con la tabla de atributos (F6, «Mover el mapa a la fila seleccionada»). Anote en el campo `revisado` «bien» o «mal». MapBiomas es un mapa de 30 m y tiene errores: el porcentaje de «mal» es el ruido del entrenamiento y se informa.

**Si el grupo prefiere digitalizar.** Puede usar su propia capa con los mismos códigos: `--entrenamiento ruta.gpkg` (capa `entrenamiento`, campo `codigo`). Entonces la **cantidad de polígonos de cada clase tiene que seguir la proporción del paisaje** (por ejemplo, 5 de urbano por cada 60 de vegetación y herbáceas), sorteados al azar, cada uno de 3 × 3 píxeles o más y homogéneo. Nunca 10 por clase.

**No reutilice el entrenamiento para validar.** La validación del Tp4 usa puntos etiquetados al azar sobre la imagen.

---

## Paso 5 — Los compuestos de temporada (`Tp10_02`, primera parte)

**Qué y por qué.** Una escena suelta mete en el mapa lo que pasó **ese día**: la humedad del suelo después de una lluvia, el riego, una cosecha, las nubes y el moteado del radar. Para mapear la ciudad, que no cambia de un día al otro, se usan **compuestos**:

- **Sentinel-1 RTC**: la **media en lineal** de hasta 5 pasadas de la **misma órbita relativa** (las más cercanas a la fecha; la órbita es la que más cubre el sitio según el catálogo) en ± `--dias` de `--fecha` (por defecto ± 20 días del 2026-09-16). Promediar en lineal reduce el moteado sin sesgar el valor.
- **Sentinel-2 L2A**: la **mediana**, píxel por píxel, de hasta 5 escenas (las de menos nube), usando sólo los píxeles que la SCL marca sin nube, sombra ni cirros. Una nube que tapa Salto en una fecha no tapa las otras.
- **La imagen de referencia no entra.** El Sentinel-2 del 04/09/2026 es la imagen sobre la que se etiquetan los puntos de validación del Tp4 (paso 11): se excluye del compuesto (`--excluir 2026-09-04`, el valor por defecto). Si la referencia entrara en el mapa, la validación mediría en parte el acuerdo de la imagen consigo misma.

Del compuesto óptico salen el NDBI = (B11 − B08) / (B11 + B08), que sube en la superficie construida; el NDVI = (B08 − B04) / (B08 + B04), que separa la vegetación; y el MNDWI = (B03 − B11) / (B03 + B11), que separa el agua. Del compuesto de radar sale la textura de VV (coeficiente de variación en 5 × 5 píxeles, 100 m): lo «rugoso» de la ciudad.

**Salida.** `02_Subsets_SNAP_QGIS\B_CONCORDIA_compuestos_2026-09-16_20m.tif`: `C_VV_dB`, `C_VH_dB`, `C_CV_VV`, `NDBI`, `NDVI`, `MNDWI`, `B04`, `B03`, `B02` (color natural) y dos bandas de control: `n_pasadas_S1` y `n_escenas_S2` (cuántas observaciones entraron en cada píxel).

**Control.** En la bitácora: la órbita, las fechas de las pasadas de Sentinel-1 y de las escenas de Sentinel-2 con su nube en el sitio, y el porcentaje del sitio sin ninguna observación óptica. En QGIS, `n_escenas_S2` en gris: donde vale 1 o 2, el compuesto óptico es casi una escena suelta.

---

## Paso 6 — FUSIÓN DE PÍXEL: un Random Forest por conjunto de sensores (`Tp10_02`, segunda parte, SE CORRE)

**Qué y por qué.** Para saber cuánto aporta cada sensor hay que cambiar **sólo los datos**: el mismo clasificador (Random Forest de 300 árboles, semilla 2026) y el mismo entrenamiento, con cinco conjuntos de capas:

| Variante | Capas |
|---|---|
| `optico` | B02, B03, B04, B08, B11, B12, NDBI, NDVI, MNDWI (compuesto Sentinel-2) |
| `C` | C_VV_dB, C_VH_dB, C_CV_VV (compuesto Sentinel-1) |
| `SAR_multibanda` | C + L_HH_dB, L_HV_dB (NISAR) |
| `multisensor` | C + L + óptico |
| `multisensor_con_S` | C + L + S_HH_dB (NovaSAR) + óptico; sólo en la huella de NovaSAR |

**Orden.**

```
python Tp10_02_fusion_pixel_urbano.py --sitio B_CONCORDIA --pixel 20
```

El `--pixel` debe ser **el mismo** que en el paso 2: el programa lee la banda L y la S de `B_CONCORDIA_urbano_por_banda_20m.tif`. Lee Sentinel-1 y Sentinel-2 del Planetary Computer: necesita internet y tarda unos 20 minutos (cinco pasadas de radar y cinco escenas ópticas). La bitácora informa cada lectura con su tiempo.

**Qué debe observar.** Los compuestos (paso 5), la tabla del entrenamiento, y para cada variante las capas, `cubre el X % del sitio`, las hectáreas urbanas y la exactitud **fuera de bolsa (OPTIMISTA)**. Al final, la superficie de cada clase por variante.

**Salidas.**

- `05_Resultados/02_Rasters/B_CONCORDIA_variante_optico.tif`, `_variante_C.tif`, `_variante_SAR_multibanda.tif`, `_variante_multisensor.tif` y `_variante_multisensor_con_S.tif`: 1 = urbano, 2 = no urbano (el formato del Tp4).
- `05_Resultados/02_Rasters/B_CONCORDIA_clases_sin_S.tif` y `_clases_con_S.tif`: las cinco clases de la multisensor, con la banda `probabilidad`.
- `05_Resultados/04_Tablas/B_CONCORDIA_importancia_por_version.csv`, `_superficie_por_variante.csv` y `_entrenamiento_mapbiomas.csv`.

**Control.**

1. **La exactitud fuera de bolsa no es la exactitud del mapa.** Se calcula con los mismos píxeles de entrenamiento. La que se informa es la del Tp4.
2. **La superficie urbana.** Compare las hectáreas urbanas de cada variante con el área urbana de MapBiomas 2025. Una variante que marca el doble está confundiendo algo: búsquelo en QGIS.
3. **El error que se corrigió.** Con `--equilibrar` el programa repite el entrenamiento con el mismo número de píxeles por clase. Compare la superficie urbana: es lo que pasa cuando el clasificador cree que todas las clases ocupan lo mismo.

**Errores típicos.**

- `Sin Sentinel-1 RTC en la ventana` o `Sin Sentinel-2 en la ventana`: amplíe `--dias`.
- El compuesto óptico tiene huecos: ninguna escena sin nube en esa parte; amplíe `--dias`.

---

## Paso 7 — FUSIÓN DE DECISIÓN: expansión urbana 2019 → 2026 (`Tp10_03`, SE CORRE)

**Qué y por qué.** Para comparar dos fechas hace falta **el mismo método en las dos**. NovaSAR y NISAR no existían en 2019; Sentinel-1 y Sentinel-2 sí. El programa **clasifica cada año por separado** con el mismo método del paso 6 (compuestos de Sentinel-1 y Sentinel-2, Random Forest, entrenamiento de MapBiomas **de ese año**) y después compara los dos mapas. Es una **comparación posterior a la clasificación**: cada fecha decide por su lado y la regla compara; es fusión de decisión.

Un píxel cambia sólo si el cambio es **confiable**: la clase ganadora tiene probabilidad ≥ `--p_min` (0,6) en las dos fechas y el cambio forma una mancha de al menos `--umm` píxeles conectados (5 píxeles = 0,2 ha). Lo demás queda **sin decidir**, a la vista.

**Las fechas.** Las dos ventanas caen en primavera: ± 30 días del 2019-11-01 y del 2026-10-01. La órbita 68 de Sentinel-1 RTC sobre Concordia empieza el 14/10/2019 en el Planetary Computer: el programa elige la órbita de la fecha final y busca la base **en la misma órbita**, porque el doble rebote depende de la dirección de mirada. ¿Por qué 2019? La colección Sentinel-2 L2A es homogénea desde 2019.

**Orden.**

```
python Tp10_03_expansion_urbana.py --sitio B_CONCORDIA
```

Por defecto: `--base 2019-11-01`, `--final 2026-10-01`, `--dias 30`, MapBiomas 2019 y 2025, `--p_min 0.6`, `--umm 5`.

**Qué debe observar.** Para cada fecha: la órbita, las pasadas de Sentinel-1, las escenas de Sentinel-2, el entrenamiento y las hectáreas urbanas. Después, la tabla de las cinco clases y la línea `Crecimiento: X ha nuevas sobre Y ha urbanas en la base = Z % en N anos`.

**Salidas.**

- `05_Resultados/02_Rasters/B_CONCORDIA_expansion_2019_2026.tif`: bandas `clase` (1 urbano en ambas, 2 nuevo urbano, 3 no urbano, 4 urbano sólo en la base, 5 sin decidir), `urbano_base`, `urbano_final`, `probabilidad_base` y `probabilidad_final`.
- `05_Resultados/04_Tablas/B_CONCORDIA_expansion_superficies.csv` y `05_Graficos/B_CONCORDIA_expansion_2019_2026.png`.

**Control.**

1. **La clase 4** («des-urbanización») casi nunca es real. Si supera la mitad de la clase 2, el programa avisa: revise esas manchas en la imagen antes de informar.
2. **Comparar con MapBiomas.** El área urbana de MapBiomas del lado argentino cambia poco entre 2019 y 2025. Si la expansión del programa es mucho mayor, búsquela en la imagen: ¿loteos nuevos o error?
3. **Visual.** Con la imagen de fondo, busque tres manchas de la clase 2 y diga qué son (loteo, galpón, obra, error).

**Errores típicos.**

- `2019-11-01: falta Sentinel-1`: no hay pasadas de la misma órbita que la final en la ventana. La órbita 68 empieza el 14/10/2019: no use una base anterior a fines de octubre de 2019.

---

## Paso 8 — La red SBAS (`Tp10_04`, AUXILIAR / YA VIENE HECHO)

**Qué y por qué.** Un interferograma mide la diferencia de fase entre dos fechas: el desplazamiento del terreno en la línea de visión, más atmósfera, más ruido. Un SBAS (Small BAseline Subset) usa **muchos** pares de línea de base corta en el tiempo y en el espacio, de la **misma órbita**, para separar la deformación (que se acumula) de la atmósfera (que cambia al azar). El programa busca las Sentinel-1 IW SLC del sitio en ASF, elige la órbita relativa con más escenas, une cada fecha con sus 2 siguientes (`--vecinos 2`), descarta los pares de más de 48 días (`--dias_max`) o de más de 150 m de base perpendicular (`--base_max`) y, con `--hyp3 N`, pide los pares al procesador HyP3 de ASF (GAMMA, 10 × 2 looks, 40 m de píxel).

Pedir y bajar los 120 pares de la corrida docente (`--hyp3 120`: los 120 primeros pares aptos de la red, del 01/06/2025 al 03/07/2026) lleva horas y unos 99 GB: **ya viene hecho**, recortado al sitio. Si quiere ver cómo se arma la red (sin pedir nada; no hace falta cuenta para buscar):

```
python Tp10_04_pares_sbas.py --sitio E_PARANA_DIAMANTE --desde 2025-01-01 --hasta 2026-09-30
```

**Qué mirar.** `05_Resultados/04_Tablas/E_PARANA_DIAMANTE_red_sbas.csv` (pares, días, base perpendicular, apto) y `05_Resultados/05_Graficos/E_PARANA_DIAMANTE_red_sbas.png` (tiempo frente a base perpendicular: cada línea es un par).

**Control.** La bitácora da `Fechas en la red: N de M; subredes: K` y, si alguna fecha quedó suelta, `fechas sin par apto (quedan fuera del SBAS): ...`. Si dice `AVISO: la red esta cortada en K subredes y el SBAS no puede unirlas`, el SBAS no puede unir los subconjuntos. Se arregla con `--dias_max` o `--vecinos` mayores.

**Base perpendicular.** Cuando a un par le falta la base perpendicular, el programa primero la pide a la pila de cada una de sus dos escenas. Si sigue sin base: se acepta por separación temporal cuando las dos escenas son **del mismo satélite** (el tubo orbital de Sentinel-1 es estrecho, del orden de 150 m; pasa con Sentinel-1D, que todavía no tiene bases en el catálogo de ASF) o cuando ASF no devolvió **ninguna** base; se rechaza cuando son de satélites distintos. Esos pares quedan con la nota `sin base en ASF; mismo satelite` en la tabla y la bitácora dice cuántos son. Si se pide una órbita con `--orbita` que no tiene escenas, el programa termina con `La orbita N no tiene escenas sobre el sitio. Orbitas disponibles: ...`.

**PS (dispersores persistentes).** Se explica en clase y no se hace: necesita StaMPS o SARPROZ y más de 20 SLC corregistrados.

---

## Paso 9 — Zona de referencia estable y puntos de control (EN QGIS)

**Qué y por qué.** Cada interferograma tiene una constante arbitraria: el desenrollado de la fase empieza en cualquier punto. Antes de sumar, a cada par se le resta la mediana de una **zona de referencia** que se supone quieta. Si no se da, el programa usa la mediana de los **píxeles persistentes** (coherentes en al menos el 90 % de los pares que los cubren, casi siempre zona construida), y si toda esa zona se mueve, eso **esconde** el movimiento. Después, en **puntos estables que no se usaron como referencia**, la velocidad tiene que dar cerca de 0: ése es el control.

**Menús — la zona de referencia.**

1. `Capa > Crear capa > Nueva capa GeoPackage…` (`Layer > Create Layer > New GeoPackage Layer…`).
2. Base de datos: `...\Tp10_Impacto_urbano\04_Tablas_de_trabajo\referencia_estable_E.gpkg`. Nombre de la tabla: `referencia`. Tipo de geometría: **Polígono**. SRC: **EPSG:32721**. No hace falta agregar campos. Aceptar.
3. `Capa > Conmutar edición`, `Editar > Añadir polígono`, guardar.

**Qué digitalizar.** Estructuras antiguas, grandes y rígidas sobre terreno firme: el casco histórico de Paraná sobre la barranca alta, grandes edificios públicos antiguos, cabeceras de puentes. **Nunca** sobre la ladera de la barranca, rellenos recientes ni la planicie del río.

**El tamaño importa.** El píxel es de 40 m. El programa rasteriza la referencia marcando **todos los píxeles que el polígono toca**, así que un edificio o un puente más chico que el píxel también cuenta. Aun así, conviene sumar **varias zonas estables separadas entre sí**: si la referencia tiene menos de 10 píxeles, la bitácora avisa que el ruido de esos pocos píxeles pasa entero a todo el mapa. Un par se descarta sólo si no tiene ningún píxel coherente en la referencia.

**Menús — los puntos de control.**

1. `Capa > Crear capa > Nueva capa GeoPackage…`: `04_Tablas_de_trabajo\control_estable_E.gpkg`, tabla `control`, geometría **Punto**, EPSG:32721.
2. `Editar > Añadir punto` (Ctrl+.). Entre 10 y 20 puntos sobre estructuras estables **fuera** de los polígonos de referencia y alejados de ellos (otros barrios antiguos, plazas consolidadas).

**Errores típicos.**

- Puntos de control dentro de la referencia: allí la velocidad es 0 por construcción y no prueban nada. El programa los excluye y avisa cuántos eran: digitalícelos fuera.
- Puntos fuera de la ventana del sitio: el programa los excluye y avisa. Que todos caigan dentro, o el control queda con menos puntos.

---

## Paso 10 — Velocidad vertical por apilado (`Tp10_05`, SE CORRE)

**Qué y por qué.** De cada par HyP3 se usan `*_vert_disp.tif` (desplazamiento vertical en metros, positivo = ascenso, **suponiendo que no hay movimiento horizontal**), `*_corr.tif` (coherencia 0 a 1) y `*_los_disp.tif` (sólo para verificar el signo). En cada píxel se descartan los pares con coherencia menor que 0,3 y se calcula:

> velocidad = suma de desplazamientos / suma de intervalos (mm/año)

La deformación constante se acumula; el ruido atmosférico, aleatorio en el tiempo, se promedia. Es un SBAS simplificado: da la velocidad media, no la serie fecha por fecha (eso lo haría MintPy).

**Orden.**

```
python Tp10_05_velocidad_subsidencia.py --sitio E_PARANA_DIAMANTE --carpeta ..\02_Subsets_SNAP_QGIS\HyP3_E_PARANA_DIAMANTE\QGIS_GeoTIFF --referencia ..\04_Tablas_de_trabajo\referencia_estable_E.gpkg --control ..\04_Tablas_de_trabajo\control_estable_E.gpkg
```

`--carpeta` apunta a los 120 pares HyP3 recortados al sitio (`02_Subsets_SNAP_QGIS\HyP3_E_PARANA_DIAMANTE\QGIS_GeoTIFF`; 3,4 GB con los `.dim`, contra 99 GB de los originales completos, que quedan en el archivo del docente). Sin `--carpeta`, el programa los busca en `ORIGINALES\HYP3\E_PARANA_DIAMANTE`. Otros valores por defecto: `--coh_min 0.3`, `--frac_min 0.9` (un píxel tiene velocidad sólo si es coherente en al menos el 90 % de los pares que lo cubren; no todos los pares cubren todo el sitio), `--frac_ref 0.9` (píxeles persistentes para la referencia automática) y `--min_pares 5`. **No baje `--frac_min`**: con 0,7 los campos e islas que siguen coherentes dan «hundimientos» de más de 20 mm/año que son sesgo de fase de los pares cortos, no deformación. **No baje `--pixel` a 10 m**: los interferogramas son de 40 m y bajar el píxel inventa detalle.

**Qué debe observar.**

- `Carpeta: ...; pares con *_vert_disp.tif: N`.
- `Zona de referencia: N pixeles de 40 m`. Con menos de 10, un AVISO: sume zonas estables (paso 9).
- Una línea por par: fechas, días y porcentaje de píxeles coherentes.
- `Correlacion LOS frente a vertical: ...`: confirma la convención de signos.
- `Pares que cubren cada pixel: minimo ..., maximo ... de N`.
- `Pixeles coherentes en >= 90 % de los pares que los cubren (persistentes): X % del sitio`.
- `Pixeles con velocidad (coherentes en >= 90 % de los pares que los cubren y en >= 5): X % del sitio`.
- `Velocidad vertical: mediana ... mm/ano; percentiles 5 y 95: ... y ... mm/ano`.
- Si corresponde, los AVISOS de puntos de control fuera de la grilla o dentro de la referencia (se excluyen).
- Bloque **CONTROL**: media, desvío y máximo absoluto de la velocidad en los puntos estables, y cuántos tienen dato.

**Salidas.**

- `05_Resultados/02_Rasters/E_PARANA_DIAMANTE_velocidad_vertical.tif`: `velocidad_mm_ano`, `pares_validos`, `dispersion_entre_pares_mm_ano`.
- `05_Resultados/04_Tablas/E_PARANA_DIAMANTE_pares_usados.csv`.
- `05_Resultados/05_Graficos/E_PARANA_DIAMANTE_velocidad_vertical.png` (escala recortada a ± 20 mm/año, rojo-azul).

**Control.**

1. **Puntos estables.** La media tiene que estar cerca de 0. Criterio del programa: si la media se aleja de 0 **más que el desvío**, la referencia no es estable o hay una tendencia orbital. Declárelo; no lo esconda.
2. **Pares válidos.** En QGIS, la banda `pares_validos`: el agua, los bañados y los cultivos pierden coherencia y quedan sin velocidad. Es correcto.
3. **La ladera.** En la barranca hay movimiento horizontal. La componente «vertical» de HyP3 lo ignora: allí el valor no es subsidencia pura. Dígalo.
4. **La dispersión.** `dispersion_entre_pares_mm_ano` dice cuánto varían las velocidades de cada par alrededor de la velocidad apilada (atmósfera, desenrollado), no el error de la velocidad. Los pares cortos pesan mucho en esa dispersión. Úselo para comparar zonas, no como intervalo de confianza.

**Errores típicos.**

- `No hay productos HyP3 descomprimidos en ...`: los `.zip` de HyP3 no se descomprimieron, o la carpeta es otra (`--carpeta`).
- `sin pixeles coherentes en la referencia; par descartado` en muchos pares: la referencia está en zona de baja coherencia o es chica.
- `sin fechas en el nombre`: un archivo renombrado a mano; el programa necesita el nombre original de HyP3 (`..._AAAAMMDDThhmmss_AAAAMMDDThhmmss_...`).

---

## Paso 11 — Validar con el Tp4 (SE CORRE, fuera de hora)

**Qué y por qué.** La exactitud fuera de bolsa es optimista. La exactitud que se informa sale de puntos estratificados por clase del mapa y etiquetados **al azar** (Olofsson et al., 2014). Se valida cada variante con el mismo procedimiento y se comparan en la tabla de variantes. Como el urbano es menos del 5 % del sitio, se piden **al menos 50 puntos por estrato** (`--minimo 50`): con 30, el intervalo de confianza de la exactitud del usuario del urbano es de ± 0,15 o más y ninguna comparación se puede decidir.

**Órdenes** (desde `Tp4_Validacion\03_Scripts`; una por variante):

```
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp4_Validacion\03_Scripts
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp10_Impacto_urbano\05_Resultados\02_Rasters\B_CONCORDIA_variante_multisensor.tif --banda 1 --minimo 50
```

Repita con `B_CONCORDIA_variante_optico`, `_variante_C`, `_variante_SAR_multibanda` y `_variante_multisensor_con_S`. Si ya existe un muestreo anterior, el programa no lo pisa: cópielo antes y agregue `--sobrescribir`.

Etiquete en QGIS la capa `puntos` de cada `Tp4_Validacion\04_Tablas_de_trabajo\B_CONCORDIA_variante_..._puntos_a_etiquetar.gpkg`: campo `clase_ref` = 1 (urbano) o 2 (no urbano), mirando **sólo** la imagen de alta resolución. No abra la llave. Regla: urbano si el píxel de 20 m está ocupado en su mayor parte por techos o pavimento.

```
python Tp4_03_exactitud_y_area.py --nombre B_CONCORDIA_variante_multisensor --nombres_clase "1=urbano,2=no_urbano"
```

(una vez por variante) y la tabla:

```
python Tp4_04_tabla_de_variantes.py --tp Tp10 --clase urbano ^
    --variante "Optico solo|Sentinel-2|B_CONCORDIA_variante_optico" ^
    --variante "SAR solo (C)|Sentinel-1|B_CONCORDIA_variante_C" ^
    --variante "SAR multibanda|C + L|B_CONCORDIA_variante_SAR_multibanda" ^
    --variante "Multisensor|C + L + optico|B_CONCORDIA_variante_multisensor"
```

**La versión con banda S** sólo existe en la huella de NovaSAR: su exactitud se refiere a esa huella, y la comparación justa con la versión sin S es en esa misma huella.

**Control.** Si el intervalo de confianza de la diferencia entre dos variantes incluye el cero, el programa lo dice: **la mejora no está demostrada con esa muestra**. Se informa así.

---

## Lo que tiene que quedar anotado (bitácora del grupo)

- Fecha y hora UTC de cada escena usada (Sentinel-1, Sentinel-2, NovaSAR, NISAR) y la órbita de cada Sentinel-1.
- Los umbrales elegidos y por qué (histograma).
- El desplazamiento aplicado a NovaSAR y de dónde salió.
- El entrenamiento: cuántos píxeles por clase y cuántos de los 60 revisados estaban mal.
- La diferencia de fechas: NovaSAR 2023 frente a C y L 2026.
- La zona de referencia y los puntos de control de la subsidencia.
- Cada cifra que use en las respuestas, con el archivo de `05_Resultados` del que sale.
