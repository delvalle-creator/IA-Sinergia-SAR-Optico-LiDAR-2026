# Prompt corregido — el que produjo los scripts del Tp9

---

> **Contexto.**
>
> Curso de posgrado «Sinergias multisensor y estrategias de fusión
> SAR-Óptico-LiDAR para evaluación de emergencias ambientales», Diamante (Entre
> Ríos), 2026. Práctico Tp9: deforestación y degradación del monte nativo.
>
> Sitio `C_FEDERAL`: Federal, monte nativo del Espinal. Caja WGS84 (lon_min,
> lat_min, lon_max, lat_max) = (−59.02, −30.99, −58.62, −30.59), de la presentación
> 02. La banda P (BIOMASS) también es de Federal. Caja, proyección, rutas, escenas y fechas **no se escriben
> en los scripts**: se importan de `00_COMUN/configuracion_comun.py` (`SITIOS`,
> `EPSG`, `ruta_tp`, `NOVASAR`, `EVENTOS["Tp9"]`). Lecturas por sensor, grilla,
> unidades, escritura y bitácora vienen de `00_COMUN/funciones_comunes.py`;
> cocientes, índices, entrenamiento, Random Forest y figura, de
> `00_COMUN/funciones_cambio.py`. Cada script encuentra `00_COMUN` subiendo por el
> árbol de carpetas.
>
> Grilla común: EPSG:32721 (UTM 21 S), **20 m** (la de NISAR GCOV), bordes
> múltiplos del píxel. Sin dato: −9999. ALOS-2 es de 25 m: se lleva a 20 m y se
> declara.
>
> Entorno: Miniforge, entorno `sar` (Python 3.11, numpy, scipy, pandas,
> rasterio, geopandas, h5py, pyproj, pystac-client, planetary-computer,
> scikit-learn, matplotlib; conda-forge). Windows, Miniforge Prompt.
>
> Datos (fechas verificadas en `EVENTOS["Tp9"]`):
>
> - **L.** ALOS-1 PALSAR FBS del 13/03/2011, RTC de ASF a 12,5 m, γ⁰ en
>   potencia, **sólo HH** (FBS es de una polarización; el HV de 2011 existe sólo
>   en FBD). ALOS-2 PALSAR-2 mosaico anual 2021 de JAXA (Planetary Computer,
>   `alos-palsar-mosaic`, DN; γ⁰ = DN² · 10^(−8,3)). NISAR L2 GCOV del 17/09/2026
>   (ASF, `.h5`), términos HHHH y HVHV, frecuencia A, con la máscara del producto.
> - **C.** Sentinel-1 RTC VV y VH del 10/08/2021 y del 14/09/2026 (Planetary
>   Computer, γ⁰ lineal).
> - **S.** NovaSAR-1 GRD HH, escena 50896 del 22/12/2023 (cubre el 51 % del
>   sitio), σ⁰ = DN²/CalibrationConstant.
> - **P.** BIOMASS L1B DGM del 12/08/2026 recortado a Federal (`C_FEDERAL_BIOMASS_P_20260812.tif`,
>   γ⁰ HH, HV, VH y VV lineal, en geometría de radar con puntos de control).
> - **Óptico.** Sentinel-2 L2A del 06/08/2021 y del 16/09/2026, NDVI sólo en
>   píxeles válidos de la SCL.
> - **LiDAR.** GEDI L2A V003, huellas válidas del sitio en
>   `Tp1_Convergencia/05_Resultados/03_Vectores/lidar_C_FEDERAL.gpkg` (capa
>   `gedi_l2a`, filtradas con `l2a_quality_flag_rel3`, `degrade_flag`,
>   `sensitivity ≥ 0,95` y `surface_flag`). Sin adquisiciones entre el 17/03/2023 y
>   el 26/04/2024.
> - **Control.** Cobertura de control del Tp4 a 20 m
>   (`Tp4_Validacion/02_Subsets_SNAP_QGIS/C_FEDERAL_cobertura_control_20m.tif`):
>   clase 3 monte nativo, clase 7 urbano.
>
> **La pregunta:** ¿dónde se perdió monte y dónde se degradó bajo el dosel? Los
> controles del práctico: «cultivos y pasturas no se detectan como pérdida» y
> «calibrar ALOS frente a ALOS-2 en zonas estables». No los dé por cumplidos.
>
> **Requisitos no negociables.**
>
> *Script 1, `Tp9_01_pila_temporal.py` (pila y calibración cruzada)*
>
> 1. `--pixel` 20 por defecto. Todas las capas en la misma grilla del sitio.
> 2. ALOS-2: mosaico del año `--anio_alos2` (2021), HH y HV; el cuadrado del DN
>    **antes** de remuestrear (promediar potencia); varias teselas se unen.
>    Nombre `L_ALOS2_<anio>_<pol>`.
> 3. ALOS-1: `--alos1_hh` (y `--alos1_hv` sólo si hubiera una FBD), leído con
>    remuestreo `average`. Nombres `L_ALOS1_2011_HH`, `L_ALOS1_2011_HV`. Escribir en
>    el docstring que FBS es sólo HH y que, sin HV, la comparación 2011 se hace en
>    HH y se declara.
> 4. NISAR: `--nisar_h5`, términos HHHH y HVHV de `LSAR`, **frecuencia A** (la B
>    de 80 m no se usa), sólo la ventana del sitio, con la **máscara del producto**
>    (0 inválido, 255 fuera, 1..n válido) y valores ≤ 0 a sin dato; promedio si el
>    píxel de origen es más fino que la grilla, bilineal si no. Si el gránulo no
>    cubre el sitio, avisar y seguir. Nombres `L_NISAR_2026_HH`, `_HV`.
> 5. Sentinel-1 RTC de cada fecha de `--fechas_c` (2021-08-10, 2026-09-14), VV y
>    VH; si no hay escena ese día, avisar. Nombres `C_S1_<anio>_<POL>`.
> 6. NovaSAR `--novasar` (50896) con `novasar_sigma0` (media cuadrática de los
>    DN, σ⁰ = DN²/k), con `--desplazamiento DX DY` (metros; DX positivo = este,
>    DY positivo = norte; 0 0 por defecto, y entonces avisar que se mida con
>    `Tp3_02`); nombre `S_NovaSAR_2023_sigma0_HH`; si falla, avisar y seguir.
> 7. NDVI de Sentinel-2 de cada fecha de `--fechas_opt` (2021-08-06, 2026-09-16),
>    sólo píxeles válidos de la SCL, reflectancia con el desplazamiento de la
>    línea de base 04.00 descontado; varias teselas del mismo día se unen. Nombre
>    `O_NDVI_<anio>`.
> 8. Una capa entra sólo si tiene dato en más del 5 % del sitio; imprimir el %
>    de cada una.
> 9. **Calibración cruzada (control de la diapositiva 32).** Zona estable = clases
>    3 (monte confirmado sin cambio por el grupo) y 7 (urbano) de la cobertura de
>    control, o sólo 7 con `--solo_urbano`. Referencia = ALOS-2 del año
>    `--anio_alos2`. Para cada otro producto de banda L de la misma polarización,
>    con al menos 100 píxeles estables: desfase = mediana(γ⁰_ref_dB − γ⁰_otro_dB);
>    corregir el otro multiplicando en lineal por 10^(desfase/10). Si no hay
>    cobertura de control, **no calibrar y declararlo**.
> 10. `05_Resultados/04_Tablas/C_calibracion_cruzada.csv` con `referencia`,
>     `producto`, `desfase_dB`, `pixeles_estables`, `aplicado` y `aviso`
>     («cambios < X dB no interpretables» si |desfase| > 1 dB).
> 11. Pila en `02_Subsets_SNAP_QGIS/C_pila_temporal_<pixel>m.tif`, radar lineal,
>     con todas las fuentes en los metadatos (JAXA, JAXA – ASF DAAC, NASA – ISRO
>     con el nombre del gránulo, ESA – Copernicus con fecha y hora, SSTL – CSIRO).
>
> *Script 2, `Tp9_02_sinergia_estratos.py` (SINERGIA)*
>
> 12. Huellas válidas de GEDI dentro de la pila (columna `valido`), en el CRS de
>     la pila. Si falta el GeoPackage, terminar diciendo qué correr.
> 13. Para cada capa: año desde el nombre; usar sólo huellas a menos de
>     `--dias_max` (730) del 1 de julio de ese año; radar en dB (sólo para
>     correlacionar), NDVI tal cual. Con menos de 20 huellas, «no se evalúa».
> 14. ρ de Spearman con rh98 y su valor p; curva de respuesta = mediana por clase
>     de rh98 con cortes 0, 2, 5, 8, 12, 16, 60 m; rango de la curva. Tabla
>     `05_Resultados/04_Tablas/C_sensibilidad_a_la_altura.csv` (`capa`,
>     `huellas`, `spearman_rho`, `p_valor`, `rango_de_la_curva`, `unidad`),
>     ordenada por ρ.
> 15. Figura `05_Resultados/05_Graficos/C_curvas_de_respuesta.png` con las curvas
>     de radar, ejes rotulados y la cita **Fuente** al pie.
> 16. Parte B, banda P: `--p_tif` (por defecto el BIOMASS de Federal; γ⁰ lineal, o
>     dB con `--p_en_db`), ubicado con sus puntos de control si no tiene
>     proyección; misma comparación con las huellas GEDI de Federal filtradas a
>     `--dias_max` de `--p_fecha`; filas `P_BIOMASS_<banda>` en la misma tabla y
>     en la figura; `--sin_p` la omite.
> 17. Parte C, degradación: período 1 hasta `--p1_hasta` (2022-12-31), período 2
>     desde `--p2_desde` (2024-04-26); mediana de rh98 por celda de `--celda`
>     (200 m) y período, con al menos 2 huellas en cada uno; Δrh98 = p2 − p1; ΔNDVI
>     = último NDVI − primero en el centro de la celda. Candidata si rh98_p1 ≥
>     `--monte_min` (5 m), Δrh98 ≤ `--u_rh98` (−3 m) y |ΔNDVI| < `--u_dndvi` (0,05).
>     Tabla `C_delta_rh98_por_celda.csv` y ráster
>     `02_Subsets_SNAP_QGIS/C_delta_rh98_<pixel>m.tif` (`delta_rh98_m`,
>     `candidato_degradacion`) en la grilla de la pila.
> 18. Declarar en la bitácora que caídas menores de 3 m están cerca del ruido y el
>     hueco de GEDI entre 17/03/2023 y 26/04/2024. Si no hay celdas con huellas
>     en los dos períodos, decir que se amplíe `--celda` y declararlo.
>
> *Script 3, `Tp9_03_fusion_perdida_degradacion.py` (FUSIÓN DE RASGOS)*
>
> 19. Rasgos desde la pila (los que falten, no entran): `dHV_L` = cociente NISAR
>     2026 / ALOS-2 2021 en HV y `HV_L_actual_dB`; si NISAR no trae HV, en HH,
>     con los nombres `dHH_L` y `HH_L_actual_dB` y un aviso;
>     `dHH_L_hist` = ALOS-2 2021 / ALOS-1 2011 en HH; `dVH_C` = VH último / VH
>     primero; `dNDVI` = NDVI último − primero y `NDVI_actual`. Cocientes en lineal
>     expresados en dB (`cociente_db`).
> 20. Δrh98 **no entra** por defecto: es el control independiente. Con
>     `--rh98_como_rasgo` entra y se avisa que el mapa queda sólo en las celdas con
>     huellas.
> 21. Variantes de un solo sensor, antes del entrenamiento: `C_variante_optico.tif`
>     (ΔNDVI < `--u_ndvi`, −0,10) y `C_variante_L.tif` (`dHV_L`, o `dHH_L`, <
>     `--u_hv`, −1,5 dB),
>     códigos 1 pérdida/degradación, 2 no.
> 22. Entrenamiento en `04_Tablas_de_trabajo/entrenamiento_C.gpkg`, capa
>     `entrenamiento`, campo `codigo`: 1 pérdida, 2 degradación, 3 monte estable,
>     4 no bosque estable (cultivo, pastura, ciudad). Si no existe, crearla vacía
>     en EPSG:32721, listar las clases y terminar.
> 23. Random Forest con `fusion_pixel_o_rasgo` (300 árboles, semilla 2026,
>     clases equilibradas). Salidas: `C_perdida_degradacion.tif` (`clase`,
>     `probabilidad`), `C_variante_multisensor.tif` (1 = clases 1 y 2, 2 = resto),
>     figura `05_Graficos/C_perdida_degradacion.png` con la fuente al pie.
> 24. Imprimir la exactitud fuera de bolsa rotulada **OPTIMISTA**, la importancia
>     de cada rasgo y las hectáreas por clase (conteo de píxeles).
> 25. **Control independiente con GEDI:** Δrh98 por clase del mapa (cantidad,
>     mediana, media) en `05_Resultados/04_Tablas/C_control_gedi_por_clase.csv`,
>     con la expectativa escrita (pérdida y degradación negativas, monte estable
>     cerca de 0) y la advertencia de que `count` son píxeles, no celdas.
> 26. Escribir en el docstring el control «cultivos y pasturas no se detectan
>     como pérdida» y cómo lo atienden `NDVI_actual` y la clase 4.
>
> *Comunes a los tres*
>
> 27. Radar en lineal; dB sólo para correlacionar, umbralizar y mirar. Ningún
>     promedio en dB.
> 28. GeoTIFF con `guardar_tif` (FUENTE, PROCESO, SCRIPT, FECHA_PROCESO, UNIDADES).
> 29. Bitácoras en `05_Resultados/06_Control_calidad/`: `Tp9_01_pila.log`,
>     `Tp9_02_sinergia.log`, `Tp9_03_fusion.log`.
> 30. Docstring con paso, marca, pregunta, cita de la diapositiva 32, entradas,
>     salidas y USO; terminar con el SIGUIENTE PASO.
>
> **Lo que NO debe hacer.**
>
> - No inventar un HV de 2011.
> - No restar productos de banda L sin medir su desfase en zona estable.
> - No remuestrear ni promediar en dB.
> - No usar NISAR sin su máscara ni la frecuencia B.
> - No comparar una capa con huellas GEDI de otra época sin filtrar por fecha.
> - No informar la exactitud fuera de bolsa ni el conteo de píxeles como
>   exactitud y área: eso es del Tp4.
> - No escribir credenciales ni rutas absolutas en los scripts.

---

## La diferencia

El primero pedía **restar el HV**. Éste pide **comprobar que cada polarización
existe, calibrar los sensores donde nada cambió, preguntar a GEDI qué estrato ve
cada banda** y dejar que un cultivo cosechado sea una clase, no un error.
