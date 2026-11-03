# 05_Resultados — lo que escriben los scripts del Tp2

Las subcarpetas se crean solas al correr los scripts. Nada se edita a mano.

| Subcarpeta | Archivo | Lo escribe |
|---|---|---|
| `02_Rasters/` | `<SITIO>_RGB_<etiqueta>.tif` (8 bits, 3 bandas: copol / cros / cociente en dB, estiramiento 2–98 %; 0 = sin dato) | `Tp2_02_rgb_copol_cruzada_cociente.py` |
| `04_Tablas/` | `<SITIO>_respuesta_por_cubierta.csv` (banda, clase, n_pixeles, media_dB, p10_dB, p90_dB) | `Tp2_03_respuesta_por_cubierta.py` |
| `04_Tablas/` | `<SITIO>_contraste_entre_clases.csv` (clase_1, clase_2, banda, contraste_dB) | `Tp2_03_respuesta_por_cubierta.py` |
| `04_Tablas/` | `<SITIO>_control_zona_estable.csv` (banda_a, banda_b, n_pixeles, diferencia_media_dB, desvio_pixel_a_pixel_dB, umbral_dB, veredicto) | `Tp2_04_control_zona_estable.py` |
| `05_Graficos/` | `<SITIO>_RGB_<etiqueta>.png` y `<SITIO>_gris_<banda>.png`, con la cita «Fuente:» al pie | `Tp2_02_rgb_copol_cruzada_cociente.py` |
| `05_Graficos/` | `<SITIO>_cajas_por_banda.png` | `Tp2_03_respuesta_por_cubierta.py` |
| `06_Control_calidad/` | `Tp2_01_<SITIO>.log` … `Tp2_04_<SITIO>.log` | cada script |

El RGB de 8 bits es **sólo para ver**: toda medición se hace sobre la pila en lineal
de `02_Subsets_SNAP_QGIS`.

Las tablas y bitácoras se reescriben en cada corrida del mismo script y sitio. Si corre
el control del paso 8 con dos pares distintos, copie la primera tabla con otro nombre
antes de la segunda corrida.
