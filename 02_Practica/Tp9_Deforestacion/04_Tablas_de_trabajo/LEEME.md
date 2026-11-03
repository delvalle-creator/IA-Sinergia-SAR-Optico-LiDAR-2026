# 04_Tablas_de_trabajo — qué va a aparecer aquí

| Archivo | Quién lo escribe | Qué es |
|---|---|---|
| `entrenamiento_C.gpkg` | Viene con 70 polígonos de partida (desde el 27/10/2026 los dos tramos del camino nuevo están en degradación: aperturas lineales = degradación) (copia de `entrenamiento_C_prueba_CBERS.gpkg`, 22/10/2026); lo **revisa, corrige y completa el grupo** en QGIS | Capa `entrenamiento`, campos `codigo` (1 pérdida, 2 degradación, 3 monte estable, 4 no bosque estable), `clase` (texto), `criterio` (qué se vio) y `origen` (de qué sorteo salió) |
| `entrenamiento_C_prueba_CBERS.gpkg` | `00_COMUN\09_Herramientas\poligonos_prueba_cbers_Tp9.py` | Los polígonos de partida sin tocar: 38 de monte estable, 26 de no bosque, 3 de degradación y 3 de pérdida, sobre la imagen CBERS-4A de 2 m de 2021 y 2026, con sorteo al azar y revisión a ojo. Son un borrador, no verdad de campo |
| `entrenamiento_C_prueba_WorldCover.gpkg` | `00_COMUN\09_Herramientas\poligonos_prueba_worldcover_Tp9.py` (21/10/2026) | Versión anterior, **no se usa**: 136 polígonos sacados de ESA WorldCover 2021 (10 m) y del cambio de NDVI de la pila. Se reemplazó porque una capa global de 10 m no sirve de máscara sobre la imagen de alta resolución. Queda para comparar |
| `entrenamiento_C.gpkg.bak_20261022m` | — | Respaldo de la capa con los 136 polígonos de WorldCover |
| `entrenamiento_C_ampliado.gpkg` | desarrollo (27/10/2026) | Los polígonos de partida con la regla de clases aplicada (el camino nuevo pasa a degradación) más 7 desmontes sorteados en la pérdida de MapBiomas 2022–2025 dentro del monte de 2021, 2 picadas nuevas sorteadas entre parches de pérdida parcial de copa CBERS y los lotes cosechados A y B en la clase 4. Es la «segunda corrida» del desarrollo, para comparar con la del grupo |
| `entrenamiento_C_vacio.gpkg` | `Tp9_03_fusion_perdida_degradacion.py` | La capa vacía, para empezar de cero: copiarla sobre `entrenamiento_C.gpkg` |

La zona estable de la calibración cruzada no está aquí: sale de la cobertura de
control del Tp4 (`Tp4_Validacion\04_Tablas_de_trabajo\control_digitalizado_C_FEDERAL.gpkg`
y `Tp4_Validacion\02_Subsets_SNAP_QGIS\C_FEDERAL_cobertura_control_20m.tif`).
