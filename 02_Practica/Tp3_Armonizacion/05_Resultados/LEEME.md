# 05_Resultados — lo que escriben los scripts del Tp3

Las subcarpetas se crean solas al correr los scripts. Nada se edita a mano.

| Subcarpeta | Archivo | Lo escribe |
|---|---|---|
| `03_Vectores/` | `<SITIO>_huellas_con_cubo.gpkg` (capa `huellas`, EPSG:32721) | `Tp3_03_lidar_en_el_cubo.py` |
| `04_Tablas/` | `<SITIO>_diferencias_de_fecha.csv` (sensor_1, fecha_1, sensor_2, fecha_2, diferencia_dias) | `Tp3_01_cubo_comun.py` |
| `04_Tablas/` | `<SITIO>_corregistro_<mov>_vs_<ref>.csv`, una por par (ventana, dy_px, dx_px, error, mediana_dx_px, mediana_dy_px, pixel_m, ref, mov) | `Tp3_02_medir_corregistro.py` |
| `06_Control_calidad/` | `Tp3_01_<SITIO>.log`, `Tp3_02_<SITIO>_<mov>_vs_<ref>.log` (una por par), `Tp3_03_<SITIO>.log` | cada script |

Cada par medido con `Tp3_02` deja su propia tabla y su propia bitácora; repetir el
mismo par reescribe sólo esos dos archivos.
