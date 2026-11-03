# 04_Tablas_de_trabajo — los polígonos de cubierta

Aquí va **un** archivo por sitio:

`cubiertas_<SITIO>.gpkg` (por ejemplo `cubiertas_A2_IBICUY.gpkg`)

- Lo **crea vacío** `Tp2_03_respuesta_por_cubierta.py` la primera vez que se corre:
  capa `cubiertas`, campos `clase` y `observacion`, EPSG:32721. Después el script se
  detiene.
- Lo **completa el grupo en QGIS** (guía, paso 6): polígonos con el campo `clase` en
  una de estas ocho, escritas exactamente así: `agua_calma`, `agua_rizada`,
  `pajonal`, `monte_o_bosque`, `cultivo`, `suelo_desnudo`, `urbano`, `estable`.
- Al menos 3 polígonos y 200 píxeles de 10 m por clase. El criterio con que se acepta un polígono no debe
  usar la banda que después se compara (por ejemplo, no elegir las aguas por la C VV). La clase `estable` es la que
  usa el control del paso 8 (`Tp2_04_control_zona_estable.py`).

En el desarrollo docente (22/10/2026) los 28 polígonos salieron de un sorteo: `puntos_sorteo_A2_IBICUY.gpkg`
tiene los puntos sorteados y `sorteo_poligonos_A2_IBICUY.csv` lo que pasó con cada uno (aceptado o descartado y por qué). Los grupos entregan el mismo
registro de su sorteo. Los polígonos
anteriores, ubicados a mano, quedaron como `cubiertas_A2_IBICUY.gpkg.bak_20261022s`.

No cambie el nombre de la capa ni del campo `clase`: los dos scripts los buscan por
esos nombres.

- `cubiertas_A2_IBICUY.qml`: el estilo de la capa (un color fijo por clase y el campo `clase` como Mapa de valores). QGIS lo carga solo al abrir el `.gpkg`.
