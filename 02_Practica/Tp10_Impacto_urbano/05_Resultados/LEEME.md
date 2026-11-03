# 05_Resultados

Trae ya los resultados de la corrida docente de la subsidencia (`Tp10_04` y `Tp10_05` sobre Paraná – Diamante: red SBAS, pares usados y velocidad vertical, con sus bitácoras), para comparar con los del grupo. El resto lo escriben los programas del Tp10:

| Subcarpeta | Qué aparece | Qué script lo escribe |
|---|---|---|
| `02_Rasters/` | `<SITIO>_variante_optico.tif`, `_variante_C.tif`, `_variante_multisensor.tif`, `_variante_multisensor_con_S.tif` (sólo la huella de NovaSAR) (1 urbano, 2 no urbano: formato del Tp4); `_clases_con_S.tif`, `_clases_sin_S.tif` (clase y probabilidad) | `Tp10_02` |
| | `<SITIO>_expansion_2019_2026.tif` (clase, urbano_base, urbano_final) | `Tp10_03` |
| | `E_PARANA_DIAMANTE_velocidad_vertical.tif` (velocidad_mm_ano, pares_validos, dispersion_entre_pares_mm_ano) | `Tp10_05` |
| `04_Tablas/` | `<SITIO>_coincidencias_urbano.csv`, `_detalle_6_10_20m.csv` | `Tp10_01` |
| | `<SITIO>_importancia_por_version.csv` | `Tp10_02` |
| | `<SITIO>_expansion_superficies.csv` | `Tp10_03` |
| | `<SITIO>_red_sbas.csv` | `Tp10_04` |
| | `<SITIO>_pares_usados.csv` | `Tp10_05` |
| | `tabla_de_variantes_urbano.csv` | `Tp4_04_tabla_de_variantes.py --tp Tp10` |
| `05_Graficos/` | `<SITIO>_hist_C_VV.png`, `_hist_S_HH.png`, `_hist_L_HH.png` | `Tp10_01` |
| | `<SITIO>_clases_con_S.png`, `_clases_sin_S.png` | `Tp10_02` |
| | `<SITIO>_expansion_2019_2026.png` | `Tp10_03` |
| | `<SITIO>_red_sbas.png` | `Tp10_04` |
| | `<SITIO>_velocidad_vertical.png` | `Tp10_05` |
| `06_Control_calidad/` | Una bitácora `.log` por corrida: lo mismo que se vio en pantalla | Todos |

Todos los rásters están en EPSG:32721, float32, sin dato = −9999, con la cita de fuente en los metadatos. Toda cifra de las respuestas sale de uno de estos archivos y se cita con su nombre.
