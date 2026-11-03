# Tp9 - proyecto de QGIS del desarrollo

$${\color{red}\textbf{ATENCIÓN: ESTE PROYECTO DE QGIS SÓLO FUNCIONA CON LOS DATOS DEL DISCO EXTERNO DEL CURSO.}}$$

$${\color{red}\textbf{LAS CAPAS SE CARGAN DESDE LAS CARPETAS 02\_Subsets\_SNAP\_QGIS DE CADA PRÁCTICO, QUE NO ESTÁN EN GITHUB.}}$$

$${\color{red}\textbf{COPIE EL CURSO COMPLETO DESDE EL DISCO EXTERNO Y ABRA EL PROYECTO DESDE ESA COPIA.}}$$

**ATENCIÓN: ESTE PROYECTO DE QGIS SÓLO FUNCIONA CON LOS DATOS DEL DISCO EXTERNO DEL CURSO. LAS CAPAS SE CARGAN DESDE LAS CARPETAS `02_Subsets_SNAP_QGIS` DE CADA PRÁCTICO, QUE NO ESTÁN EN GITHUB. COPIE EL CURSO COMPLETO DESDE EL DISCO EXTERNO Y ABRA EL PROYECTO DESDE ESA COPIA.**


`Tp9_desarrollo.qgz` reune las capas del Tp9 (perdida y degradacion del monte en Federal, 2011-2026) agrupadas por
paso: la pila temporal con el RGB de cambio de banda L (R = NISAR HV 2026, G y B = ALOS-2 HV 2021, misma escala) y los
NDVI (paso 1); el delta rh98 por celda y las celdas candidatas a degradacion (paso 2); los 70 poligonos de entrenamiento
y la zona estable de la calibracion (paso 3); el mapa de perdida y degradacion, su probabilidad y las tres variantes
(paso 4); los puntos etiquetados al azar del Tp4 (paso 5). Contexto: MapBiomas 2011 y 2025, perdida de vegetacion y
fuego con la leyenda oficial, CCI Biomass 2021 y su desvio, la altura FH sin agua, la banda P en RGB HH, VH, HH/VH y
los embeddings AlphaEarth 2021 y 2025. Optico: Sentinel-2 del 06/08/2021 y del 16/09/2026, Landsat 8 del 07/08/2021 y
CBERS-4A de 2 m del 02/08/2021 y del 05/09/2026. Marcadores: el sitio, la ventana CBERS, los desmontes del oeste y la
ciudad de Federal. Temas de mapa por paso.
