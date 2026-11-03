# 05_Resultados

Los scripts del Tp6 escriben aquí:

- `02_Rasters/`
  - `B_extension_y_duracion_C_<pixel>m.tif` — `Tp6_01` (bandas `extension_maxima`, `duracion_dias`).
  - `B_agua_por_sensor_<pixel>m.tif` — `Tp6_02` (sinergia; una banda por sensor).
  - `B_variante_optico.tif`, `B_variante_C.tif`, `B_variante_CL.tif` (si hay L), `B_variante_multisensor.tif` — `Tp6_03` (fusión de decisión; 1 agua, 2 no). Cópielas con la fecha antes de procesar otro evento.
  - `B_profundidad_<variante>_<pixel>m.tif` — `Tp6_04` (`profundidad_m`, `cota_agua_m`).
- `04_Tablas/`
  - `B_serie_agua_C.csv` — `Tp6_01`.
  - `B_sinergia_agua.csv` — `Tp6_02`.
  - `B_control_mde_icesat2.csv` — `Tp6_05`.
  - `tabla_de_variantes_agua.csv` — `Tp4_04_tabla_de_variantes.py --tp Tp6`.
- `05_Graficos/` — `B_serie_agua_C.png`, `B_histograma_VV_pico.png`, `B_histograma_MNDWI.png`.
- `06_Control_calidad/` — las bitácoras `.log`.

Las tablas de exactitud y área de cada variante quedan en `Tp4_Validacion\05_Resultados\04_Tablas\`.
