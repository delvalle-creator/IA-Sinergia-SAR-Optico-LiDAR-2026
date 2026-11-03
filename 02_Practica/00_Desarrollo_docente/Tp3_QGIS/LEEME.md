# Tp3 - proyecto de QGIS del desarrollo

$${\color{red}\textbf{ATENCIÓN: ESTE PROYECTO DE QGIS SÓLO FUNCIONA CON LOS DATOS DEL DISCO EXTERNO DEL CURSO.}}$$

$${\color{red}\textbf{LAS CAPAS SE CARGAN DESDE LAS CARPETAS 02\_Subsets\_SNAP\_QGIS DE CADA PRÁCTICO, QUE NO ESTÁN EN GITHUB.}}$$

$${\color{red}\textbf{COPIE EL CURSO COMPLETO DESDE EL DISCO EXTERNO Y ABRA EL PROYECTO DESDE ESA COPIA.}}$$

**ATENCIÓN: ESTE PROYECTO DE QGIS SÓLO FUNCIONA CON LOS DATOS DEL DISCO EXTERNO DEL CURSO. LAS CAPAS SE CARGAN DESDE LAS CARPETAS `02_Subsets_SNAP_QGIS` DE CADA PRÁCTICO, QUE NO ESTÁN EN GITHUB. COPIE EL CURSO COMPLETO DESDE EL DISCO EXTERNO Y ABRA EL PROYECTO DESDE ESA COPIA.**


Abrir `Tp3_desarrollo.qgz` (en QGIS, Proyecto > Abrir). Se abre en A2_IBICUY. No necesita internet.

Grupos:
- Huellas LiDAR en el cubo (paso 4): `A2_IBICUY_huellas_con_cubo.gpkg`, capa `huellas`, con GEDI por clase de rh98,
  la pasada GEDI del 29/11/2020 marcada con cruces (rh98 no plausible) y los segmentos ATL08.
- CCI Biomass v7 (ESA, Santoro y Cartus 2026): biomasa aerea AGB 2024 y 2020 y su desvio 2024, en Mg/ha, en su
  grilla nativa (EPSG:4326, ~100 m; QGIS la reproyecta solo para mostrarla). El muestreo de AGB en cada huella
  queda en `05_Resultados\03_Vectores\A2_IBICUY_huellas_con_CCI.gpkg` (columnas CCI_1 a CCI_10, en el orden de las
  bandas: AGB 2010, 2015, 2020, 2021, 2024 y sus desvios).
- Cubo de Ibicuy, 20 m (pasos 1 y 2): el mismo `A2_IBICUY_cubo_20m.tif` agregado cinco veces: Sentinel-2 en color
  natural; NISAR L HV y Sentinel-1 RTC VV en gris con opacidad 50 % para comparar bordes; una composicion
  NISAR L HH, L HV, S HH; y el Copernicus DEM.
- Banda P y contexto del sitio (pasos 3 y 6): BIOMASS P VH del cubo con opacidad 50 % (la HV del producto trae
  interferencia de radiofrecuencia sin corregir y no se usa), el RGB HH, VH, HH/VH de Tp2_02, MapBiomas 2025 con
  su leyenda oficial y la altura del bosque FH de BIOMASS L2A (0 a 30 m).
- Caso de control (paso 3): `F_BOVRIL_cubo_20m.tif` con Sentinel-2, la NovaSAR 47974 ya trasladada con
  `--desplazamiento -92 -484` y NISAR L HH, las dos con opacidad 50 %.

Marcadores (Ctrl+B): Ibicuy entero, detalle de bordes de 5 km, Bovril entero y detalle de Bovril. Temas de mapa
(boton del ojo del panel Capas): uno por figura del documento Desarrollo del Tp3.
