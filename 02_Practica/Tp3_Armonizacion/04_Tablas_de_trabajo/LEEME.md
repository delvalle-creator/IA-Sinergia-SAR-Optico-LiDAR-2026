# 04_Tablas_de_trabajo — las huellas LiDAR con los valores del cubo

Aquí va la tabla que escribe `Tp3_03_lidar_en_el_cubo.py`:

`<SITIO>_huellas_con_cubo.csv` (por ejemplo `A2_IBICUY_huellas_con_cubo.csv`)

Una fila por huella GEDI válida o segmento ATL08 con canopia válida, con:

- `producto` (`gedi_l2a` o `atl08`), `fecha_lidar`, `x`, `y` (EPSG:32721);
- las variables LiDAR: `rh98`, `rh50` (GEDI), `h_canopy` (ATL08) y las alturas de
  terreno **elipsoidales** `elev_lowestmode_elips` o `h_te_best_fit_elips`;
- por cada capa del cubo: su media en la huella (radar en lineal, más `<capa>_dB`),
  `n_<capa>` (píxeles usados) y `dias_<capa>` (días entre la huella y la capa).

Es la tabla de trabajo de los prácticos con fusión de rasgo (Tp5, Tp9). No se edita a
mano: si algo está mal, se corrige la causa y se vuelve a correr `Tp3_03`.

Antes de comparar las alturas de terreno con `MDE_GLO30_m`, pasarlas a EGM2008 con
`alturas_a_egm2008()` de `00_COMUN/funciones_lidar.py`.
