# Tp10 — Orden de ejecución

Todo se corre desde el **Miniforge Prompt**, con el entorno `sar`, parado en esta carpeta:

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp10_Impacto_urbano\03_Scripts
```

La numeración es la de la guía (`00_Guia_del_practico\00_LEEME.md`); los pasos 0, 1, 3 y 4 de la guía no corren nada (el 4 se hace en QGIS después del 6).

Los tiempos son estimados para una notebook del aula con buena conexión; dependen sobre todo de la red (el Planetary Computer se lee en el momento).

| Paso de la guía | Script | Marca | Qué hace | Entrada | Salida | Tiempo |
|---|---|---|---|---|---|---|
| 2 | `Tp10_01_doble_rebote_sinergia.py` | **SE CORRE** | SINERGIA: mapa urbano por banda, tabla de coincidencias, detalle a 6, 10 y 20 m | S1 RTC (MPC), NovaSAR 47942 (local), NISAR GCOV `.h5` (local), cobertura de control del Tp4 (opcional) | `02_Subsets_SNAP_QGIS/<SITIO>_urbano_por_banda_20m.tif`; `04_Tablas/<SITIO>_coincidencias_urbano.csv`, `_detalle_6_10_20m.csv`; `05_Graficos/<SITIO>_hist_*.png` | 10–20 min (el detalle a 6 m es lo más lento) |
| 5 y 6 | `Tp10_02_fusion_pixel_urbano.py` | **SE CORRE** | Compuestos de temporada (Sentinel-1 media lineal, Sentinel-2 mediana); entrenamiento proporcional de MapBiomas; FUSIÓN DE RASGOS: un Random Forest por conjunto de sensores (óptico, C, C + L, C + L + óptico, con S) | Ráster del paso 2, S1 RTC y S2 L2A (MPC), MapBiomas | `02_Subsets_SNAP_QGIS/<SITIO>_compuestos_2026-09-16_20m.tif`; `05_Resultados/02_Rasters/<SITIO>_variante_optico.tif`, `_variante_C.tif`, `_variante_SAR_multibanda.tif`, `_variante_multisensor.tif`, `_variante_multisensor_con_S.tif`, `_clases_sin_S.tif`, `_clases_con_S.tif`; `04_Tablas/<SITIO>_importancia_por_version.csv`, `_superficie_por_variante.csv`, `_entrenamiento_mapbiomas.csv`; `04_Tablas_de_trabajo/entrenamiento_mapbiomas_<SITIO>.gpkg` | 20 min |
| 4 | Revisar el entrenamiento | **EN QGIS** | 30 puntos de urbano y 30 de vegetación leñosa sobre la imagen de alta resolución | `04_Tablas_de_trabajo/entrenamiento_mapbiomas_<SITIO>.gpkg` (lo escribe `Tp10_02`) | El campo `revisado` | 15 min |
| 7 | `Tp10_03_expansion_urbana.py` | **SE CORRE** | DETECCIÓN DE CAMBIOS por comparación posterior a la clasificación: Random Forest (fusión de rasgos Sentinel-1 + Sentinel-2) de cada año con compuestos y MapBiomas del año; cambio con probabilidad mínima y unidad mínima de mapeo | S1 RTC y S2 L2A de las dos ventanas (MPC), MapBiomas 2019 y 2025 | `02_Rasters/<SITIO>_expansion_2019_2026.tif`; `04_Tablas/<SITIO>_expansion_superficies.csv` y `_expansion_matriz_transiciones.csv`; figura | 40 min |
| 8 | `Tp10_04_pares_sbas.py` | **AUXILIAR / YA VIENE HECHO** | Red de pares de línea de base corta Sentinel-1 SLC; con `--hyp3` los pide a HyP3 | Catálogo de ASF | `04_Tablas/<SITIO>_red_sbas.csv`, `05_Graficos/<SITIO>_red_sbas.png`; con `--hyp3`, `00_COMUN\08_Originales_crudos\HYP3\<SITIO>\` (en clase se usa el recorte `02_Subsets_SNAP_QGIS\HyP3_<SITIO>\`) | Búsqueda: 1–2 min. Pedido HyP3: horas (no en clase) |
| 9 | Digitalizar referencia y control | **EN QGIS** | Polígonos estables y puntos de control | — | `04_Tablas_de_trabajo/referencia_estable_E.gpkg`, `control_estable_E.gpkg` | 15 min |
| 10 | `Tp10_05_velocidad_subsidencia.py` | **SE CORRE** | Velocidad vertical por apilado de tasas, referencia, control (error de la media) y saltos de desenrollado | HyP3 descomprimidos, referencia, control | `02_Rasters/<SITIO>_velocidad_vertical.tif`; `04_Tablas/<SITIO>_pares_usados.csv`; figura | 5–10 min |
| 11 | `Tp4_02`, `Tp4_03`, `Tp4_04` (en `Tp4_Validacion\03_Scripts`) | **SE CORRE** | Validación de las variantes | Variantes de los pasos 6 y 7 | Tablas de exactitud y área; `tabla_de_variantes_urbano.csv` | 1 h de etiquetado por variante (fuera de hora) |

Cada script deja su bitácora en `05_Resultados/06_Control_calidad/` y termina con la línea `SIGUIENTE PASO: ...`.

## Las órdenes, con los valores por defecto

### Paso 2

```
python Tp10_01_doble_rebote_sinergia.py --nisar_h5 ..\..\00_COMUN\08_Originales_crudos\NISAR\NISAR_L2_PR_GCOV_031_010_D_104_2005_DHDH_A_20260918T215921_20260918T215955_P05023_F_F_J_001.h5 --puntos_enlace todos --desplazamiento DX DY
```

Valores por defecto: `--sitio B_CONCORDIA --pixel 20 --fecha 2026-09-16 --novasar 47942 --puntos_enlace todos --desplazamiento 0 0 --u_c -3 --u_s -3 --u_l -3 --umm_m2 1200`. Corrida del docente (23/10/2026): `--puntos_enlace todos --desplazamiento -40 100 --u_c -6 --u_s -3 --u_l 0` (guía, pasos 1 y 2). Agregar `--otsu` para usar Otsu en lugar de los umbrales manuales.

Variante para Paraná (NovaSAR 47942 no lo cubre; necesita un NISAR que cubra Paraná):

```
python Tp10_01_doble_rebote_sinergia.py --sitio E_PARANA_DIAMANTE --nisar_h5 "D:\...\NISAR_L2_PR_GCOV_....h5"
```

### Pasos 5 y 6

```
python Tp10_02_fusion_pixel_urbano.py --sitio B_CONCORDIA --pixel 20
```

Valores por defecto: `--fecha 2026-09-16 --dias 20 --anio_mb 2025 --n_entrenamiento 20000 --excluir 2026-09-04` (el Sentinel-2 del 04/09/2026 es la imagen de referencia de la validación y no entra al compuesto). Una capa de entrenamiento propia, con los mismos códigos: `--entrenamiento ruta.gpkg`. `--equilibrar` repite el error de entrenar con el mismo número de píxeles por clase, para mostrarlo. El `--pixel` tiene que ser el mismo que en el paso 2. Lee la banda L y la S del ráster del paso 2: no recibe `--nisar_h5`.

### Paso 7

```
python Tp10_03_expansion_urbana.py --sitio B_CONCORDIA
```

Valores por defecto: `--pixel 20 --base 2019-11-01 --final 2026-10-01 --dias 30 --anio_mb_base 2019 --anio_mb_final 2025 --p_min 0.6 --umm 5 --excluir 2026-09-04 --aviso_clase4 0.2`. Las ventanas no pueden empezar antes de fines de octubre de 2019: la órbita 68 de Sentinel-1 RTC empieza el 14/10/2019 en el Planetary Computer. La órbita se elige en la fecha final y la base se busca en la misma.

### Paso 8 (sólo para ver cómo se arma la red)

```
python Tp10_04_pares_sbas.py --sitio E_PARANA_DIAMANTE --desde 2025-01-01 --hasta 2026-09-30
```

Valores por defecto: `--vecinos 2 --dias_max 48 --base_max 150 --orbita 0 --hyp3 0`. El pedido real (lo hizo el docente antes del curso; necesita la cuenta de NASA Earthdata en `.netrc`, o la pide por teclado):

```
python Tp10_04_pares_sbas.py --sitio E_PARANA_DIAMANTE --desde 2025-01-01 --hasta 2026-09-30 --hyp3 120
```

### Paso 10

```
python Tp10_05_velocidad_subsidencia.py --sitio E_PARANA_DIAMANTE ^
    --carpeta ..\02_Subsets_SNAP_QGIS\HyP3_E_PARANA_DIAMANTE\QGIS_GeoTIFF ^
     --referencia ..\04_Tablas_de_trabajo\referencia_estable_E.gpkg ^
     --control ..\04_Tablas_de_trabajo\control_estable_E.gpkg
```

Valores por defecto: `--carpeta` vacía (= `ORIGINALES\HYP3\E_PARANA_DIAMANTE`), `--pixel 40 --coh_min 0.3 --frac_min 0.9 --frac_ref 0.9 --min_pares 5 --salto_mm 35 --frac_salto 0.2` (con `--descartar_saltos` los pares sospechosos no entran) (40 m: el píxel de HyP3 con 10 × 2 looks; `--frac_min` sobre los pares que cubren cada píxel). El `^` continúa la orden en la línea siguiente en Windows; también puede escribirse todo en una línea.

### Paso 11 (validación, desde `Tp4_Validacion\03_Scripts`)

```
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp10_Impacto_urbano\05_Resultados\02_Rasters\B_CONCORDIA_variante_multisensor.tif --banda 1 --minimo 50
python Tp4_03_exactitud_y_area.py --nombre B_CONCORDIA_variante_multisensor --nombres_clase "1=urbano,2=no_urbano"
(lo mismo para _variante_optico, _variante_C y _variante_SAR_multibanda)
python Tp4_04_tabla_de_variantes.py --tp Tp10 --clase urbano ^
    --variante "Optico solo|Sentinel-2|B_CONCORDIA_variante_optico" ^
    --variante "SAR solo (C)|Sentinel-1|B_CONCORDIA_variante_C" ^
    --variante "SAR multibanda|C + L|B_CONCORDIA_variante_SAR_multibanda" ^
    --variante "Multisensor|C + L + optico|B_CONCORDIA_variante_multisensor"
```

La versión con banda S se valida aparte, sobre su propio mapa (sólo la huella de NovaSAR):

```
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp10_Impacto_urbano\05_Resultados\02_Rasters\B_CONCORDIA_variante_multisensor_con_S.tif --banda 1 --minimo 50
python Tp4_03_exactitud_y_area.py --nombre B_CONCORDIA_variante_multisensor_con_S --nombres_clase "1=urbano,2=no_urbano"
```

Para comparar las cinco variantes en la misma superficie (la huella de NovaSAR), desde `Tp10_Impacto_urbano\03_Scripts`:

```
python Tp10_06_dominio_huella_S.py
```

Deja `tabla_de_variantes_urbano_huella_S.csv`: (A) cada variante con sus puntos dentro de la huella y (B) las cinco evaluadas con los 142 puntos de la variante con S (estimador de Stehman). Separa el efecto de la banda S del cambio de superficie.

El mapa de expansión también puede validarse con `Tp4_02 --mapa ...\B_CONCORDIA_expansion_2019_2026.tif --banda 1` (cinco estratos); la clase de interés es la 2, «nuevo urbano».

## Qué hacer si falla

| Mensaje | Causa | Qué hacer |
|---|---|---|
| `ModuleNotFoundError` | No está activo el entorno `sar` | `conda activate sar` |
| `No se pudo consultar el Planetary Computer` | Sin internet o servicio caído | Verificar la conexión y volver a correr. Las URL firmadas duran alrededor de una hora: si dejó la consola abierta mucho tiempo, vuelva a correr |
| `No encuentro el GRD de la escena 47942` | La carpeta NovaSAR está en otro disco | `set CURSO_SAR_NOVASAR=<ruta de las escenas>` |
| `El granulo ... no cubre el sitio` | NISAR de otra pasada | Bajar el del 18/09/2026 con `Tp1_04_buscar_asf.py` |
| `Hace falta al menos dos bandas para la sinergia.` | Faltan dos de las tres bandas | Revisar los mensajes de cada bloque |
| `Falta ..._urbano_por_banda_20m.tif` | No corrió `Tp10_01` (paso 2), o con otro `--pixel` | Correr `Tp10_01` con el mismo píxel |
| `Muy pocos pixeles de entrenamiento con dato en todas las capas` | Menos de 50 píxeles válidos (con una capa propia) | Más polígonos; dentro de la huella de NovaSAR para la versión con S |
| Error al rasterizar el entrenamiento (`int()` de un valor nulo) | Polígono sin `codigo` en una capa propia | Completar el campo en la tabla de atributos |
| `Sin Sentinel-2 en la ventana` o `Sin Sentinel-1 RTC en la ventana` | Ninguna escena útil en ± `--dias` | Ampliar `--dias` o cambiar `--fecha` |
| `falta Sentinel-1` en `Tp10_03` | Para la base: no hay pasadas de la misma órbita que la final en la ventana | Mover `--base` después del 14/10/2019 o ampliar `--dias` |
| `La orbita N no tiene escenas sobre el sitio. Orbitas disponibles: ...` en `Tp10_04` | La órbita pedida con `--orbita` no existe en la búsqueda | Elegir una de las órbitas que lista el mensaje |
| `No hay productos HyP3 descomprimidos` | `.zip` sin descomprimir o carpeta distinta | Descomprimir; usar `--carpeta` |
| `AVISO: menos de 10 pixeles de referencia` | Zona de referencia chica | Sumar varias zonas estables separadas |
| `AVISO: ... puntos de control caen DENTRO de la zona de referencia` | Puntos de control sobre la referencia | Se excluyen; digitalizarlos fuera |
