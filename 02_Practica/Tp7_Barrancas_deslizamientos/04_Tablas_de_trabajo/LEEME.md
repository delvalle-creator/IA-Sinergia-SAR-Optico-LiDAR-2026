# 04_Tablas_de_trabajo — qué va a aparecer aquí

| Archivo | Quién lo escribe | Qué es |
|---|---|---|
| `E1_ladera_reparada.gpkg` | `Tp7_02_coherencia_y_deformacion.py` | El polígono de la ladera de 2018 con la topología reparada (`make_valid`) |
| `E1_zona_referencia.gpkg` | `Tp7_02_coherencia_y_deformacion.py` | El anillo de 500 m alrededor de la ladera (vector completo; el agua del JRC se quita al usarlo en `Tp7_02` y `Tp7_03`) |
| `E1_cicatriz_y_deposito.gpkg` | Lo crea vacío `Tp7_03`; lo **digitaliza el grupo** en QGIS | Capa `formas`, campos `tipo` (`cicatriz` / `deposito`) y `fuente` |
| `_tmp_cicatriz.gpkg`, `_tmp_deposito.gpkg` | `Tp7_03_cicatriz_y_volumen.py` | Archivos intermedios para rasterizar cada tipo. Se pueden borrar |
| `E1_zona_estable_tierra.gpkg` | El grupo, en QGIS (opcional) | Zona estable sólo en tierra firme, para `--zona_estable` de `Tp7_02` y `Tp7_03` |
| `E1_zonas_ladera.gpkg` | El grupo, en QGIS (viene uno del docente) | La ladera dividida en escarpa (pendiente del IGN > 30 %), bloque (150 m detrás de la escarpa), pie y ciudad; campo `zona`. Para `Tp7_02 --zonas` |
| `E1_control_escarpa.gpkg` | `Tp7_03_cicatriz_y_volumen.py` | La escarpa a más de 200 m de la cicatriz y el depósito: el control de que el patrón no se repite fuera de las formas |
