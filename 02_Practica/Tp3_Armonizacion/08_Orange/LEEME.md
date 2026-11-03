# Tp3 - Workflows de Orange Data Mining

Se abren con File > Open en Orange 3.40; cada widget File lee su tabla de la subcarpeta `datos`
con ruta relativa, de modo que la carpeta `08_Orange` se puede copiar entera a otro disco o equipo.

| Workflow | Datos | Paso de la guia | Que muestra |
|---|---|---|---|
| `Tp3_A_huellas_LiDAR_en_el_cubo.ows` | `datos/Tp3_huellas_LiDAR_en_el_cubo.csv`: las 23.681 huellas validas (20.858 GEDI L2A y 2.823 ATL08), con la columna `plausible` de Tp3_03 con los valores del cubo de 20 m (radar en dB, incluida la banda P de BIOMASS en HH y VH, Sentinel-2, MDE) y la biomasa de CCI Biomass v7 (AGB 2020 y 2024, muestreada en QGIS) | 4 y 5 | Estadisticas; Select Rows que deja solo plausible = si (afuera la pasada GEDI del 29/11/2020 y la huella de mas de 50 m); Correlations (Spearman entre la altura y cada banda); Group By (medianas por clase de altura); cajas de L HV, C VH, P VH, NDVI y AGB por clase de altura; L HV por clase de AGB; altura frente a L HV; dias entre huella y radar; terreno elipsoidal menos MDE |
| `Tp3_B_corregistro_y_fechas.ows` | `datos/Tp3_corregistro_por_ventana.csv` (cada ventana de cada par medido con Tp3_02, Ibicuy y Bovril, NovaSAR sin corregir y corregida) y `datos/Tp3_diferencias_de_fecha.csv` | 1 y 3 | Tabla de ventanas (incluida la banda P frente a S2 y frente a NISAR L y el Landsat 8 frente a S2 a 30 m); Select Rows con las ventanas usadas (mediana +/- 3 MAD); dx frente a dy en metros, coloreado por la columna `grupo` (a lo sumo diez grupos, para que Orange de un color a cada uno); dy por par; tabla de diferencias de fecha |
| `Tp3_C_contexto_de_las_huellas.ows` | `datos/Tp3_huellas_LiDAR_en_el_cubo.csv` (con `clase_MapBiomas_2025`, `FH_m`, `FH_calidad` y `FH_menos_LiDAR_m` de Tp3_04; sin FH en las 649 huellas que caen en agua) y `datos/Tp3_contexto_pixeles_muestra.csv` (hasta 2.000 pixeles por clase de MapBiomas 2025 con CCI, FH sin agua y banda P) | 6 | Altura LiDAR y AGB del CCI por clase de MapBiomas; altura FH por clase de altura LiDAR; altura LiDAR frente a FH y frente a P VH; P VH y CCI por clase de MapBiomas en todo el sitio |

Cuidados:

- Las columnas `_dB` son dB de la media lineal de cada huella: la mediana de las cajas es valida; la media que
  muestra Orange es media de dB.
- `altura_dosel_m` es rh98 en GEDI y h_canopy en ATL08; `plausible` viene de Tp3_03: "no" para la pasada GEDI
  del 29/11/2020 (160 huellas con rh98 mediano de 91 m que los indicadores de calidad no descartaron) y para
  toda huella de mas de 50 m. Las clases de altura son "< 3 m", "3-5 m", ... (el rotulo es el mismo en tablas,
  figuras y texto).
- `elips_menos_MDE_m` compara una altura elipsoidal (WGS 84) con una sobre el geoide (EGM2008): la diferencia de
  16,9 m (GEDI) es casi toda ondulacion del geoide (N = 16,9 m en el sitio), no un error.
- CCI Biomass es un producto de unos 100 m: una huella GEDI de 25 m toma el valor del pixel de CCI que la contiene.
  102 huellas del borde este quedan fuera del recorte de CCI (AGB vacio).

- La cruzada de la banda P es la VH: la HV de BIOMASS trae interferencia de radiofrecuencia sin corregir.
- `clase_MapBiomas_2025` = "sin dato" son las huellas fuera de la cobertura de MapBiomas (islas bonaerenses).

Las tablas de `datos` las arma `03_Scripts/Tp3_05_tablas_para_Orange.py` a partir de las salidas de Tp3_01 a
Tp3_04 (incluido el muestreo del CCI en cada huella): ningun numero de Orange sale de una tabla preparada aparte.

Datos: NASA GEDI L2A V003 y NSIDC ATL08 v007 (huellas del Tp1); NISAR L2 GCOV (ASF DAAC), Sentinel-1 RTC y
Sentinel-2 L2A (Microsoft Planetary Computer), Copernicus DEM GLO-30; ESA CCI Biomass v7.0 (Santoro y Cartus,
2026, https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903); NovaSAR-1 escena 47974; ESA BIOMASS L1B y L2A FH (ESA MAAP); MapBiomas Argentina, Coleccion 3 y MapBiomas
Fuego, Coleccion 1 (https://argentina.mapbiomas.org). Elaboracion propia.
