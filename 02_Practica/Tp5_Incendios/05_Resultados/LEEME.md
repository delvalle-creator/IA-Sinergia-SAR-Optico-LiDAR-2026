# 05_Resultados

Los scripts del Tp5 escriben aquí:

- `02_Rasters/`
  - `A1_quema_por_sensor_<pixel>m.tif`, `A1_sensores_que_coinciden_<pixel>m.tif` — `Tp5_02` (sinergia).
  - `A1_variante_optico.tif`, `A1_variante_C.tif`, `A1_variante_CL.tif`, `A1_variante_multisensor.tif`, `A1_severidad_multisensor.tif` — `Tp5_03` (fusión). Códigos de las variantes: 1 quemado, 2 no quemado.
- `04_Tablas/`
  - `A1_sinergia_coincidencias.csv` — `Tp5_02`.
  - `A1_importancia_variables.csv` — `Tp5_03`.
  - `A1_delta_rh98_por_celda.csv`, `A1_delta_rh98_por_clase.csv` — `Tp5_04`.
  - `tabla_de_variantes_quemado.csv` — `Tp4_04_tabla_de_variantes.py --tp Tp5`.
- `05_Graficos/` — `histograma_<indicador>.png`, `A1_sensores_que_coinciden.png`, `A1_severidad_multisensor.png` (con la cita «Fuente» al pie).
- `06_Control_calidad/` — las bitácoras `.log` de cada script.

Las tablas de exactitud y área de cada variante quedan en `Tp4_Validacion\05_Resultados\04_Tablas\`.
