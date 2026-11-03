# Tp4 - proyecto de QGIS del desarrollo

$${\color{red}\textbf{ATENCIÓN: ESTE PROYECTO DE QGIS SÓLO FUNCIONA CON LOS DATOS DEL DISCO EXTERNO DEL CURSO.}}$$

$${\color{red}\textbf{LAS CAPAS SE CARGAN DESDE LAS CARPETAS 02\_Subsets\_SNAP\_QGIS DE CADA PRÁCTICO, QUE NO ESTÁN EN GITHUB.}}$$

$${\color{red}\textbf{COPIE EL CURSO COMPLETO DESDE EL DISCO EXTERNO Y ABRA EL PROYECTO DESDE ESA COPIA.}}$$

**ATENCIÓN: ESTE PROYECTO DE QGIS SÓLO FUNCIONA CON LOS DATOS DEL DISCO EXTERNO DEL CURSO. LAS CAPAS SE CARGAN DESDE LAS CARPETAS `02_Subsets_SNAP_QGIS` DE CADA PRÁCTICO, QUE NO ESTÁN EN GITHUB. COPIE EL CURSO COMPLETO DESDE EL DISCO EXTERNO Y ABRA EL PROYECTO DESDE ESA COPIA.**


Abrir `Tp4_desarrollo.qgz` (en QGIS, Proyecto > Abrir). Se abre en B_CONCORDIA. Las teselas Esri y Google
necesitan internet; el resto de las capas esta en el disco.

Grupos:
- Etiquetado al azar (paso 7): `B_CONCORDIA_cobertura_control_20m_puntos_a_etiquetar.gpkg`, capa `puntos`, como
  cuadrados amarillos de 20 m con el `id` como etiqueta. El formulario tiene `clase_ref` y `confianza` como mapas de
  valores y el `id` no editable (guia, 7.3). Los 70 puntos ya estan etiquetados en el desarrollo.
- Poligonos digitalizados (paso 3): `control_digitalizado_B_CONCORDIA.gpkg`, capa `control`, 24 poligonos sorteados con el
  borde del color de su clase; `codigo` es un mapa de valores (guia, 3.4).
- Mapa de control 20 m: la banda 1 (clase) y la banda 2 (fuente: digitalizado, JRC, MapBiomas recortado) del mismo
  GeoTIFF, la version anterior (monte de MapBiomas 30 m sin recortar, `.bak_20261022m`), la mascara de copas de 2 m
  hecha sobre el CBERS-4A del 15/07/2026 y el mapa de A1_DELTA_QUEMAS (solo agua de JRC).
- MapBiomas 2025 como mapa a validar (paso 10): la cobertura 2025 de MapBiomas Argentina con su leyenda oficial
  (subset del Tp1), el mismo mapa llevado a las clases del curso por `Tp4_05`, sus 70 puntos etiquetados al azar,
  el CCI Biomass AGB 2024 y el RGB de la banda P (HH, VH, HH/VH).
- Referencia: Esri World Imagery, Google Satellite, CBERS-4A fusionado de 2 m del 15/07/2026 (del Tp10) y Pleiades
  Neo de CONAE 2023 (solo la ciudad).

Para etiquetar de verdad, el grupo del paso 7 debe ver SOLO los puntos y la referencia: use el tema de mapa
«Paso 7 - etiquetado al azar» (boton del ojo del panel Capas), que apaga el mapa de control.
Marcadores (Ctrl+B): sitio entero, aserradero y cantera, loteo, ciudad y un monte de MapBiomas recortado con las copas de 2 m.
