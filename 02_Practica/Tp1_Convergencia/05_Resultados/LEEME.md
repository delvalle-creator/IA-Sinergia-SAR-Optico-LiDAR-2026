# 05_Resultados — lo que escriben los scripts del Tp1

Las subcarpetas se crean solas al correr los scripts. Nada de esto se edita a mano:
si una cifra está mal, se corrige la causa y se vuelve a correr.

| Subcarpeta | Archivo | Lo escribe |
|---|---|---|
| `03_Vectores/` | `lidar_<SITIO>.gpkg` (capas `gedi_l2a` y `atl08`, todas las huellas con `valido` y `motivo`) | `Tp1_05_buscar_lidar.py` |
| `04_Tablas/` | `inventario_local.csv` | `Tp1_02_inventario_local.py` |
| `04_Tablas/` | `planilla_MPC_<SITIO>.csv`, `pares_optico_C_<SITIO>.csv` | `Tp1_03_buscar_optico_y_C.py` |
| `04_Tablas/` | `planilla_ASF_<SITIO>.csv` | `Tp1_04_buscar_asf.py` |
| `04_Tablas/` | `lidar_granulos_<SITIO>.csv`, `lidar_conteo_<SITIO>.csv` | `Tp1_05_buscar_lidar.py` |
| `04_Tablas/` | `planilla_por_pedido_<SITIO>.csv` | `Tp1_06_escenas_por_pedido.py` |
| `04_Tablas/` | `matriz_convergencia_<SITIO>.csv`, `grado_convergencia_<SITIO>.csv` | `Tp1_07_matriz_convergencia.py` |
| `05_Graficos/` | `linea_tiempo_<SITIO>.png` (con la cita de fuentes al pie) | `Tp1_07_matriz_convergencia.py` |
| `06_Control_calidad/` | una bitácora `.log` por script y sitio (`Tp1_01_sitios.log`, `Tp1_02_inventario_local.log`, `Tp1_03_<SITIO>.log` … `Tp1_07_<SITIO>.log`) | cada script |

Los CSV están en UTF-8 con BOM: Excel y LibreOffice los abren con las tildes bien.
Cierre el CSV antes de volver a correr el script que lo escribe, o Windows no deja
sobrescribirlo.
