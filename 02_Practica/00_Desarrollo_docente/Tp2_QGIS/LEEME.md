# Tp2 - proyecto de QGIS del desarrollo

$${\color{red}\textbf{ATENCIÓN: ESTE PROYECTO DE QGIS SÓLO FUNCIONA CON LOS DATOS DEL DISCO EXTERNO DEL CURSO.}}$$

$${\color{red}\textbf{LAS CAPAS SE CARGAN DESDE LAS CARPETAS 02\_Subsets\_SNAP\_QGIS DE CADA PRÁCTICO, QUE NO ESTÁN EN GITHUB.}}$$

$${\color{red}\textbf{COPIE EL CURSO COMPLETO DESDE EL DISCO EXTERNO Y ABRA EL PROYECTO DESDE ESA COPIA.}}$$

**ATENCIÓN: ESTE PROYECTO DE QGIS SÓLO FUNCIONA CON LOS DATOS DEL DISCO EXTERNO DEL CURSO. LAS CAPAS SE CARGAN DESDE LAS CARPETAS `02_Subsets_SNAP_QGIS` DE CADA PRÁCTICO, QUE NO ESTÁN EN GITHUB. COPIE EL CURSO COMPLETO DESDE EL DISCO EXTERNO Y ABRA EL PROYECTO DESDE ESA COPIA.**


Abrir `Tp2_desarrollo.qgz` (en QGIS, Proyecto > Abrir). Se abre en A2_IBICUY.

Grupos:
- Cubiertas (paso 6): `cubiertas_A2_IBICUY.gpkg` de `Tp2_SAR_multibanda\04_Tablas_de_trabajo`, con el campo
  `clase` como Mapa de valores (las ocho clases de la guia) y un color de borde por clase.
- RGB copolarizada - cruzada - cociente (paso 5): las composiciones de `Tp2_02` (la de banda P, en su grupo) (8 bits, estiramiento 2-98 %).
- Banda P (pasos 4 y 5): el BIOMASS L1B del 05/10/2026 tal cual, en VH dB (QGIS lo ubica con sus puntos de
  enlace), y el RGB HH, VH, HH/VH de `Tp2_02` en la grilla de 10 m. El HV no se usa: trae interferencia de
  radiofrecuencia sin corregir en el producto de origen.
- Contexto del sitio (paso 9): MapBiomas Argentina, cobertura 2025 con su leyenda oficial, y CCI Biomass AGB 2024.
- Sentinel-1 procesado en SNAP (pasos 1 a 3): gamma0 VV lineal sin filtrar y con Refined Lee.
- Optico de referencia: Landsat 8 del 15/09/2026, CBERS-4A de 2 m del 10/09/2026 y Pleiades 2023 de CONAE
  (servicio WMS: necesita internet).
- Fondo: ESRI World Imagery (necesita internet).

Marcadores (Ctrl+B): el sitio entero y el casco de Ibicuy. Temas de mapa (boton del ojo del panel Capas): uno por
figura del documento Desarrollo del Tp2.
