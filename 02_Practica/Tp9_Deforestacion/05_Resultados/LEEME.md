# 05_Resultados — qué va a aparecer aquí

Los scripts crean las subcarpetas al correr.

| Subcarpeta / archivo | Quién lo escribe | Qué es |
|---|---|---|
| `04_Tablas/C_calibracion_cruzada.csv` | `Tp9_01` | Desfase de cada producto de banda L respecto de ALOS-2 en zona estable |
| `04_Tablas/C_sensibilidad_a_la_altura.csv` | `Tp9_02` | Por capa: huellas, ρ de Spearman con rh98, p, rango de la curva (sinergia) |
| `05_Graficos/C_curvas_de_respuesta.png` | `Tp9_02` | Mediana de cada banda de radar por clase de altura GEDI |
| `04_Tablas/C_delta_rh98_por_celda.csv` | `Tp9_02` | Celdas de 200 m: rh98 por período, Δrh98, ΔNDVI, candidata a degradación |
| `02_Rasters/C_variante_optico.tif` | `Tp9_03` | 1 si ΔNDVI < −0,10; 2 si no |
| `02_Rasters/C_variante_L.tif` | `Tp9_03` | 1 si `dHV_L` < −1,5 dB (`dHH_L` si NISAR no trae HV); 2 si no |
| `02_Rasters/C_perdida_degradacion.tif` | `Tp9_03` | `clase` (1 pérdida, 2 degradación, 3 monte estable, 4 no bosque) y `probabilidad` (fusión de rasgos) |
| `02_Rasters/C_variante_multisensor.tif` | `Tp9_03` | 1 = pérdida o degradación; 2 = resto |
| `04_Tablas/C_control_gedi_por_clase.csv` | `Tp9_03` | Δrh98 por clase del mapa (control independiente) |
| `05_Graficos/C_perdida_degradacion.png` | `Tp9_03` | Figura del mapa con la fuente al pie |
| `06_Control_calidad/Tp9_01_pila.log`, `Tp9_02_sinergia.log`, `Tp9_03_fusion.log` | los tres scripts | Bitácoras |

No edite estos archivos a mano: si algo cambia, vuelva a correr el script.
