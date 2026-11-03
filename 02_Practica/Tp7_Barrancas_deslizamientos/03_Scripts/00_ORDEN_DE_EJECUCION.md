# Tp7 — Orden de ejecución

Todo se corre desde el **Miniforge Prompt**:

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp7_Barrancas_deslizamientos\03_Scripts
```

| Paso | Script o herramienta | Marca | Qué hace | Entrada | Salida |
|---|---|---|---|---|---|
| 1 | `Tp7_01_pares_insar_C.py` | **SE CORRE** | Lista pares Sentinel-1 SLC del período con días y línea de base | catálogo de ASF (red) | `05_Resultados/04_Tablas/E1_pares_S1.csv` |
| 1b | `Tp7_01_pares_insar_C.py --hyp3 1` | **YA VIENE HECHO** | Pide el mejor par a HyP3 y lo baja | cuenta Earthdata | `ORIGINALES\HYP3\E1_DIAMANTE_BARRANCA\*.zip` |
| 2 | SNAP: Snaphu Export, `snaphu`, Snaphu Import, Phase to Displacement, Terrain Correction | **EN SNAP** | Rehace el desenrollado de la banda X y exporta desplazamiento y coherencia | interferograma COSMO sin `_TC` | `02_Subsets_SNAP_QGIS/E1_X_los_disp.tif`, `E1_X_coh.tif` |
| 3 | `Tp7_02_coherencia_y_deformacion.py` | **SE CORRE** | Coherencia y desplazamiento por banda (sinergia); deformación confirmada (fusión de decisión, con la regla de signo según la geometría); histogramas de los umbrales; fusión por zona | GeoTIFF X y C, polígono de la ladera, zonas | `E1_coherencia_y_desplazamiento.csv`, `E1_deformacion_confirmada.tif`, `E1_histogramas_umbrales.png`, `E1_fusion_por_zona.csv`, `E1_ladera_reparada.gpkg`, `E1_zona_referencia.gpkg` |
| 4 | QGIS: digitalización | **EN QGIS** | Cicatriz y depósito, con el protocolo de la guía | CBERS-4A de 2 m (2026), NDVI, IGN 5 m, grieta; Pléiades o Sentinel-2 de apoyo | `04_Tablas_de_trabajo/E1_cicatriz_y_deposito.gpkg` |
| 5 | `Tp7_03_cicatriz_y_volumen.py` | **SE CORRE** | Volumen por diferencia de MDE (GLO-30 antes, IGN después) con sesgo restado, signo esperado y escarpa de control | dos MDE, polígonos, zona estable | `05_Resultados/04_Tablas/E1_volumenes.csv`, `E1_dz_despues_menos_antes.tif` |
| 6 | QGIS | **EN QGIS** | Control de cada MDE con ATL08 (cotas ya en EGM2008 y SRVN16) | `02_Subsets_SNAP_QGIS/LiDAR_E1_DIAMANTE_BARRANCA/E1_DIAMANTE_BARRANCA_LiDAR.gpkg` | diferencias en la tabla de atributos |
| 6b | `Tp7_04_icesat2_20m_cicatriz.py` | **SE CORRE** | Puntos de ICESat-2 cada 20 m sobre la cicatriz frente al IGN, con sesgo local | gránulos ATL08 v007 del sitio | `E1_atl08_20m_cicatriz.csv`, `E1_icesat2_20m_transectas.png` |
| A1 | `Tp7_05_velocidad_y_susceptibilidad.py` | **AMPLIACIÓN** | Velocidad 2025–2026 por franja y susceptibilidad hipotética (umbral 2σ) | velocidad vertical del Tp10 | `E1_velocidad_por_franja.csv`, `E1_susceptibilidad_fisuras_hipotetica.tif` |
| A2 | `Tp7_06_embeddings_cambio.py` | **AMPLIACIÓN** | Semejanza de embeddings 2018–2025 por zona | embeddings AlphaEarth 2018 y 2025 | `E1_embeddings_cambio.csv` |

Los mensajes de los scripts se escriben sin tildes ni eñes («pixeles»,
«deposito», «desvio») para que se lean bien en cualquier consola de Windows; los
documentos del práctico sí llevan tildes.

## Las órdenes, con sus valores por defecto

**Paso 1.**

```
python Tp7_01_pares_insar_C.py
python Tp7_01_pares_insar_C.py --desde 2018-09-15 --hasta 2018-11-15 --dias_max 24 --base_max 150 --hyp3 0
```

(las dos son equivalentes). Para la pregunta «¿sigue la deformación hoy?»:
`python Tp7_01_pares_insar_C.py --desde 2025-01-01 --hasta 2026-09-30`. Eso ya
no se fusiona con la banda X.

**Paso 3.**

```
python Tp7_02_coherencia_y_deformacion.py ^
  --x_desp ..\02_Subsets_SNAP_QGIS\E1_X_los_disp.tif --x_coh ..\02_Subsets_SNAP_QGIS\E1_X_coh.tif ^
  --pasada_x descendente --rumbo_x 197.5 --inc_x 59.6 ^
  --c_desp D:\CURSOS_CEREGEO_2026\...\HYP3\E1_DIAMANTE_BARRANCA\<producto>\<producto>_los_disp.tif ^
  --c_coh  D:\CURSOS_CEREGEO_2026\...\HYP3\E1_DIAMANTE_BARRANCA\<producto>\<producto>_corr.tif
```

Valores por defecto: `--pixel 10 --coh_min 0.3 --umbral_m 0.01 --anillo 500
--lambda_x 0.03123 --lambda_c 0.05547 --lambda_l 0.2350 --signo auto
--mov_azimut 292.5 --mov_inclinacion 5 --remuestreo_x average`; `--ladera` vacío
(busca `COSMO_DIAMANTE\GRIETAS\barranca-periferia_Polygon.shp`); `--zona_estable`
vacío (anillo sin el agua del JRC). Con fase en lugar de desplazamiento:
`--x_fase <Unw_Phase.tif>`. Con una zona estable digitalizada:
`--zona_estable ..\04_Tablas_de_trabajo\E1_zona_estable_tierra.gpkg`. Con las
zonas de la ladera: `--zonas ..\04_Tablas_de_trabajo\E1_zonas_ladera.gpkg`. Con un
control que no sea circular: `--control_independiente`. A 40 m: `--pixel 40`.

**Paso 4 (antes de digitalizar).** La primera corrida sólo crea el GeoPackage
vacío de cicatriz y depósito (capa `formas`, polígonos); no necesita los MDE:

```
python Tp7_03_cicatriz_y_volumen.py
```

**Paso 5.**

```
python Tp7_03_cicatriz_y_volumen.py
python Tp7_03_cicatriz_y_volumen.py --antes ..\02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\E1_DIAMANTE_BARRANCA_CopernicusDEM30.tif --despues ..\02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\E1_DIAMANTE_BARRANCA_IGN_MDE_5m.tif --pixel 30
python Tp7_03_cicatriz_y_volumen.py --antes ..\02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\E1_DIAMANTE_BARRANCA_CopernicusDEM30.tif --despues ..\02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\E1_DIAMANTE_BARRANCA_IGN_MDE_5m.tif --pixel 30 --zona_estable ..\04_Tablas_de_trabajo\E1_zona_estable_tierra.gpkg
```

El orden es siempre el mismo: `--antes` el GLO-30 (2011–2015) y `--despues` el
IGN (2013). `dZ = después − antes`: una pérdida de material da dZ negativo. Para
comparar su polígono con el del docente: `--comparar_con <gpkg del docente>`.

**Paso 6b.**

```
python Tp7_04_icesat2_20m_cicatriz.py
```

**Ampliación (optativa).**

```
python Tp7_05_velocidad_y_susceptibilidad.py
python Tp7_06_embeddings_cambio.py
```

## Si falla

| Mensaje | Qué pasa | Qué hacer |
|---|---|---|
| `ModuleNotFoundError: asf_search` / `hyp3_sdk` | No está activado el entorno | `conda activate sar` |
| `Escenas SLC sobre el sitio: 0` | Sin red o fechas mal escritas | Revisar `AAAA-MM-DD` y la conexión |
| `No encuentro el poligono de la ladera` | Disco con otra letra | `set CURSO_SAR_COSMO=...` o `--ladera` |
| «banda vacía (el desenrollado con SNAPHU no se importo)» | La `Unw_Phase` es la del curso 2023 | Rehacer el paso 2 |
| `RasterioIOError` al abrir un `.img` de SNAP | Falta el `.hdr` al lado | Exportar a GeoTIFF desde SNAP |
| `Falta la zona estable` | No se corrió el paso 3 | Correrlo o pasar `--zona_estable` |
| `Faltan --antes y --despues` | Segunda corrida de `Tp7_03` sin los MDE | Pasar los dos MDE |
| `AVISO: no se pudo leer el JRC` | Sin conexión al Planetary Computer | El anillo incluye el río: usar `--zona_estable` |
| `No hay poligonos de tipo 'cicatriz'` | `tipo` mal escrito | `cicatriz` / `deposito`, minúsculas, sin tilde |
