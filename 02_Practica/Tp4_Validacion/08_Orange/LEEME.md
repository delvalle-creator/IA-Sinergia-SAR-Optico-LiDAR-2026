# Tp4 - workflows de Orange (desarrollo)

Abrir con Orange 3.40 (`Archivo > Abrir`). Los datos estan en `datos\` con ruta relativa: la carpeta
`08_Orange` puede copiarse entera a otra computadora.

- `Tp4_A_puntos_y_matriz_de_error.ows` - los 70 puntos del ensayo, etiquetados al azar y unidos despues a la
  llave (`datos\Tp4_puntos_etiquetados_con_llave.csv`). Pivot Table arma la matriz de error en conteos y cuenta
  aciertos por fuente del mapa de control (digitalizado, JRC, MapBiomas recortado) y por confianza; Select Rows deja los
  desacuerdos (10 con el monte recortado con las copas de 2 m); Scatter Plot los ubica en el sitio.
- `Tp4_B_exactitud_y_area.ows` - la tabla de `Tp4_03` (`datos\Tp4_exactitud_y_area.csv`): exactitud del usuario
  y del productor por clase y el cociente area estimada / area del mapa.

- `Tp4_C_mapbiomas_2025_validado.ows` - paso 10: los 70 puntos de MapBiomas 2025 etiquetados al azar y unidos a la
  llave, con el CCI Biomass 2024 y la banda P de BIOMASS (VH y HH, dB) en el pixel de 20 m
  (`datos\Tp4_C_mapbiomas_puntos_con_llave.csv`): matriz de error en conteos, aciertos por confianza, P VH y CCI por
  clase de referencia y el mapa de puntos; y la tabla de `Tp4_03` (`datos\Tp4_C_mapbiomas_exactitud_y_area.csv`) en
  tres Bar Plot. La cruzada de P es la VH: la HV trae interferencia de radiofrecuencia sin corregir.
  Además, dos Group by con su Data Table calculan la proporción de aciertos (media de la columna `acierto`) por
  confianza y por clase del mapa (el usuario de cada estrato en conteos), y un Box Plot muestra la banda P VH por clase
  del mapa, para compararlo con el de clase de referencia. El punto de túneles no se excluye: cuenta como error.

Orange no calcula los intervalos de confianza ni la matriz en proporcion de area: eso lo hace `Tp4_03`. Las figuras del
Desarrollo con barras de error se hicieron con la salida de `Tp4_03` (columnas `_inf`, `_sup` y `usuario_Wilson`).
