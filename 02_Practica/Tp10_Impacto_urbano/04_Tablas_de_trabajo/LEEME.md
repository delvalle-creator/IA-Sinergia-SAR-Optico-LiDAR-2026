# 04_Tablas_de_trabajo

Empieza vacía. Aquí queda lo que el grupo digitaliza en QGIS:

| Archivo | Quién lo crea | Contenido |
|---|---|---|
| `entrenamiento_B_CONCORDIA.gpkg` | `Tp10_02_fusion_pixel_urbano.py` la primera vez que corre (vacío, EPSG:32721); el grupo lo completa | Capa `entrenamiento`, campo entero `codigo`: 1 urbano denso, 2 urbano abierto y periurbano, 3 vegetación, 4 agua, 5 suelo desnudo; campo `clase` con el nombre |
| `referencia_estable_E.gpkg` | El grupo, con `Capa > Crear capa > Nueva capa GeoPackage…` | Polígonos estables para la subsidencia (manzanas antiguas sobre terreno firme; más grandes que el píxel de 40 m) |
| `control_estable_E.gpkg` | El grupo, igual | Puntos estables **fuera** de la referencia, para el control de `Tp10_05` |

Los polígonos de entrenamiento no se usan para validar: la validación del Tp4 usa puntos etiquetados al azar.

La guía (`00_Guia_del_practico/00_LEEME.md`, pasos 4 y 9) explica cómo digitalizar cada uno.
