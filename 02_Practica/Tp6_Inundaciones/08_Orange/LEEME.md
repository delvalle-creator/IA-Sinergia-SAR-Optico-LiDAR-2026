# Tp6 - workflows de Orange (desarrollo)

Abrir con Orange 3.40 (`Archivo > Abrir`). Los datos estan en `datos\` con ruta relativa: la carpeta
`08_Orange` puede copiarse entera a otra computadora.

- `Tp6_A_agua_por_sensor.ows` - muestra de 30 000 pixeles de 20 m de B_CONCORDIA del 04/11/2023: 10 000 de agua
  permanente (JRC >= 90 %), 10 000 de agua de inundacion segun el optico (MNDWI > 0) y 10 000 del resto del sitio
  (`datos\Tp6_A_muestra_pixeles.csv`), con VV, VH y VV/VH de Sentinel-1 en dB, el MNDWI, la ocurrencia JRC, lo que
  marco cada sensor, la duracion de la serie y la clase de MapBiomas 2023. Box Plot de VV y de VH por grupo y Scatter
  Plot de VV frente a VH: por que el umbral de VV se fijo a mano en -15 dB y por que VH separaria mejor el agua.
  Agrega Select Columns (grupo como clase), Rank y Tree (profundidad 2) con Tree Viewer: el alumno comprueba
  que VH es la banda que mas informacion da sobre el grupo y ve los cortes que elige el arbol.
- `Tp6_B_variantes_y_mde.ows` - la tabla de `Tp4_04` con las tres variantes (`datos\Tp6_B_tabla_de_variantes.csv`):
  omision y area estimada en Bar Plot, y una Data Table con cada valor y su IC del 95 % (Select Columns), porque las barras
  no muestran el intervalo; y el control del Copernicus DEM con ICESat-2 de `Tp6_05`
  (`datos\Tp6_B_control_mde_icesat2.csv`, todos los haces y solo los fuertes): sesgo por clase de control.
- `Tp6_C_serie_agua.ows` - la serie de `Tp6_01` (`datos\Tp6_C_serie_agua.csv`): hectareas de agua de inundacion
  por fecha, con las fechas de cobertura parcial marcadas aparte.

Orange no calcula los intervalos de confianza: estan en las tablas. La muestra de A es estratificada por grupo (no
proporcional al area): sirve para comparar distribuciones, no para estimar superficies.
