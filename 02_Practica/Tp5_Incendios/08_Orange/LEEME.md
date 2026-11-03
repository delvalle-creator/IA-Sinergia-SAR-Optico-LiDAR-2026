# Tp5 - workflows de Orange (desarrollo)

Abrir con Orange 3.40 (`Archivo > Abrir`). Los datos estan en `datos\` con ruta relativa: la carpeta
`08_Orange` puede copiarse entera a otra computadora.

- `Tp5_A_indicadores_por_grupo.ows` - muestra aleatoria de 20 000 pixeles de 20 m de A1_DELTA_QUEMAS (sin el agua
  permanente del mapa de control) con los indicadores del paso 1 (dVH, dVV, dHV de SAOCOM y de ALOS-2, dNBR), el mes
  de quema de MapBiomas Fuego 2020, la biomasa del CCI 2020 (para separar pajonal y albardon), la banda P de
  BIOMASS de 2026 (VH y HH) y la clase de severidad de la V4 (`datos\Tp5_A_muestra_pixeles.csv`). Box Plot de cada
  indicador por mes de quema y por estructura, y un Scatter Plot de dNBR frente a dVH.
- `Tp5_B_variantes.ows` - la tabla de `Tp4_04` con las cuatro variantes (`datos\Tp5_B_tabla_de_variantes.csv`):
  omision, comision, exactitud global y porcentaje quemado estimado en Bar Plot.
- `Tp5_C_gedi_cambio_de_altura.ows` - la salida de `Tp5_04` por celda de 100 m (`datos\Tp5_C_gedi_celdas.csv`)
  con la clase de la V4, el mes de quema de MapBiomas y la altura previa. Rehecho el 27/10/2026 con la misma estación antes
  y después (325 celdas).
- `Tp5_D_ablacion_por_poligono.ows` - aporte de cada grupo de sensores: los 875 píxeles de los 35 polígonos de entrenamiento
  (`datos\Tp5_D_entrenamiento_pixeles.csv`, con la clase como objetivo y el polígono como meta), tres Select Columns (solo
  óptico, solo radar, todos), un Random Forest (300 árboles, semilla 2026) y tres Test and Score con «Cross validation by
  feature» = poligono: el modelo nunca se evalúa con un polígono que vio al entrenar. Resultado (CA, 4 clases): solo óptico
  0,94; solo radar 0,67; todos 0,96. La Confusion Matrix muestra dónde falla el radar solo.

MapBiomas Fuego entra como referencia de terceros para describir como responde cada indicador; la validacion del
practico es la del paso 5 (etiquetado al azar). Orange no calcula los intervalos de confianza: estan en la tabla.
La cruzada de la banda P es la VH: la HV trae interferencia de radiofrecuencia sin corregir.
