# Tp1 - proyecto de QGIS del docente

$${\color{red}\textbf{ATENCIÓN: ESTE PROYECTO DE QGIS SÓLO FUNCIONA CON LOS DATOS DEL DISCO EXTERNO DEL CURSO.}}$$

$${\color{red}\textbf{LAS CAPAS SE CARGAN DESDE LAS CARPETAS 02\_Subsets\_SNAP\_QGIS DE CADA PRÁCTICO, QUE NO ESTÁN EN GITHUB.}}$$

$${\color{red}\textbf{COPIE EL CURSO COMPLETO DESDE EL DISCO EXTERNO Y ABRA EL PROYECTO DESDE ESA COPIA.}}$$

**ATENCIÓN: ESTE PROYECTO DE QGIS SÓLO FUNCIONA CON LOS DATOS DEL DISCO EXTERNO DEL CURSO. LAS CAPAS SE CARGAN DESDE LAS CARPETAS `02_Subsets_SNAP_QGIS` DE CADA PRÁCTICO, QUE NO ESTÁN EN GITHUB. COPIE EL CURSO COMPLETO DESDE EL DISCO EXTERNO Y ABRA EL PROYECTO DESDE ESA COPIA.**


Abrir `Tp1_desarrollo.qgz` (doble clic, o en QGIS Proyecto > Abrir). Se abre en B_CONCORDIA.

Capas, en grupos:
- Sitios del curso: los nueve sitios (de `configuracion_comun.py`, con superficie en km2), en EPSG:4326 y en
  EPSG:32721. Es lo mismo que escribe `Tp1_01_sitios_a_vector.py` en `00_COMUN\01_AOI\sitios_curso.gpkg`; aca
  esta en `Tp1_sitios_docente.gpkg` para no tocar la carpeta de los alumnos.
- LiDAR (paso 5): huellas GEDI L2A y segmentos ATL08 de `lidar_B_CONCORDIA.gpkg`, verde valida y rojo descartada.
  Son medio millon de puntos: se dibujan recien a escala 1:150 000 o mas cerca.
- Contexto del sitio (paso 9): MapBiomas Argentina, cobertura 1985, 2023 y 2025 con la leyenda oficial, perdida de
  vegetacion de 2007 (el anio con mas perdida) y MapBiomas Fuego (cantidad de anios con quema, 1999-2025). MapBiomas
  cubre solo Entre Rios: la margen uruguaya queda sin dato.
- Banda P y biomasa: BIOMASS banda P del 22/07/2026 (RGB HH, VH, HH/VH; la HV trae interferencia de
  radiofrecuencia sin corregir en el producto de origen), altura del bosque L2A (07 a 19/07/2026) y CCI Biomass v7
  (biomasa aerea 2020 y su desvio, Mg/ha; 0 transparente).
- Banda L antes y durante la crecida (paso 6): SAOCOM de CONAE del 10/10/2023 (antes, TNA), 31/10 y 08/11/2023
  (TNB, mitad oeste), 11/11/2023 (TNA, misma geometria que el 10/10) y 16/09/2026, y ALOS-2 del 16/11/2023, todos en
  RGB HH, HV, HH/HV con los rangos fijos del curso.
- Radar: Sentinel-1 del 04/11/2023 en RGB VV, VH, VV/VH y NovaSAR-1 47942 del 13/09/2023 (sigma0 HH en dB).
- Optico: Sentinel-2 del 04/11/2023 en color natural y en falso color (B11, B08, B04).
- Fondo: ESRI World Imagery (necesita internet; sin red, usar el tema "Sin internet").

Marcadores espaciales (Ver > Administrador de marcadores espaciales, o Ctrl+B): las vistas de las figuras del
documento Tp1_desarrollo_docente.

Temas de mapa (boton del ojo en el panel Capas): uno por figura, prende solo las capas de esa figura.

Las rutas son relativas: el proyecto funciona mientras siga en `02_Practica\00_Desarrollo_docente\Tp1_QGIS`.
