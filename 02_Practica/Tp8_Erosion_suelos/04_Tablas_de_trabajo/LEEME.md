# 04_Tablas_de_trabajo — qué va a aparecer aquí

| Archivo | Quién lo escribe | Qué es |
|---|---|---|
| `entrenamiento_F.gpkg` | Lo crea vacío `Tp8_03_susceptibilidad.py`; lo **digitaliza el grupo** en QGIS | Capa `entrenamiento`, campos `codigo` (1 erosión activa o cárcava, 2 suelo estable) y `clase` (texto) |
| `estrato_erosion_F.gpkg` | **Ya viene hecho** | Capa `estrato_erosion` (suelo desnudo ≥ 3 meses, fuera del casco urbano, pendiente FABDEM ≥ 0,78°: 509 ha) y capa `puntos_sorteados` (144 puntos con semilla, en el orden del sorteo) para el paso 4 |
| `zonas_homogeneas.gpkg` | **Ya viene hecho** (el grupo puede agregar las suyas) | 12 ventanas de 100 × 100 m en lotes con cultivo o pastura parejos para el piso de speckle (`Tp8_02 --zonas_homogeneas`); no agua |
| `bordes_carcavas.gpkg` (opcional) | El grupo, en QGIS | Bordes de cárcava en dos fechas, para el paso opcional de avance |
