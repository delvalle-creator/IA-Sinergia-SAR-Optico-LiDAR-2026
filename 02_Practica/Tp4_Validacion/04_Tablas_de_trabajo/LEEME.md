# 04_Tablas_de_trabajo

Aquí trabaja el grupo. Van a aparecer:

- `control_digitalizado_<SITIO>.gpkg`, capa `control` — la crea vacía `Tp4_01_cobertura_de_control.py` y la completa el grupo en QGIS (campo `codigo` de 1 a 8).
- `<NOMBRE>_puntos_a_etiquetar.gpkg`, capa `puntos` — lo escribe `Tp4_02_muestreo_estratificado.py`; el grupo completa `clase_ref`, `confianza`, `imagen_usada` y `observacion` en QGIS.
- `<NOMBRE>_llave_NO_ABRIR.csv` — lo escribe `Tp4_02`. **No se abre hasta terminar de etiquetar.** Lo lee `Tp4_03_exactitud_y_area.py`.

En el desarrollo docente (22/10/2026) los polígonos de `control_digitalizado_B_CONCORDIA.gpkg` salieron de un sorteo:
`puntos_sorteo_control_B_CONCORDIA.gpkg` y `sorteo_poligonos_control_B_CONCORDIA.csv` registran los puntos y lo que pasó con
cada uno; los anteriores, dibujados a mano, quedaron como `.bak_20261022s`.

`<NOMBRE>` es el nombre del mapa evaluado sin extensión (por ejemplo `A1_variante_multisensor`).

Si `<NOMBRE>_puntos_a_etiquetar.gpkg` ya tiene puntos etiquetados, `Tp4_02` no lo reescribe: avisa y termina. Sólo `--sobrescribir` lo reemplaza (y borra el etiquetado); copie antes el GeoPackage a otro nombre.
