# 04_Tablas_de_trabajo

Aquí aparece `entrenamiento_A1.gpkg`, capa `entrenamiento`. Lo crea vacío `Tp5_03_fusion.py` la primera vez que corre, y lo completa el grupo en QGIS con polígonos y el campo entero `codigo`: 1 quemado severidad alta, 2 quemado severidad baja, 3 no quemado, 4 agua.

En el desarrollo docente (22/10/2026) los 35 polígonos salieron de un sorteo (100 puntos uniformes y sorteo estratificado por dNBR para completar las clases): `puntos_sorteo_entrenamiento_A1.gpkg` y `sorteo_poligonos_entrenamiento_A1.csv`. Los anteriores, ubicados a mano, quedaron como `entrenamiento_A1.gpkg.bak_20261022s`.

Lo lee `Tp5_03_fusion.py` para entrenar el Random Forest de la variante multisensor. No se usa nunca para validar.
