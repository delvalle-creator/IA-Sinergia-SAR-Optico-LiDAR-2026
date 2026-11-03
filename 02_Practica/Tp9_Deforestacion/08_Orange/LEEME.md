# Tp9 - workflows de Orange (desarrollo)

Abrir con Orange 3.40 (`Archivo > Abrir`). Los datos estan en `datos\` con ruta relativa: la carpeta
`08_Orange` puede copiarse entera a otra computadora.

- `Tp9_A_sinergia_huellas_GEDI.ows` - muestra estratificada de huellas GEDI L2A validas de C_FEDERAL a menos de 730 dias
  del 1/7/2021 (hasta 700 por clase de rh98; las clases de 12 a 16 m y de mas de 16 m tienen todas sus huellas, 75 y 48),
  con el gamma0 de ALOS-2 L (HH, HV) y de Sentinel-1 C (VV, VH) de 2021 en dB, el NDVI de 2021 y la clase de MapBiomas
  2021 (`datos\Tp9_A_huellas_GEDI_2021.csv`). Box Plot de cada banda por clase de altura y Scatter Plot rh98 frente al HV.
- `Tp9_B_variantes_e_importancia.ows` - la tabla de `Tp4_04` con las tres variantes (`datos\Tp9_B_tabla_de_variantes.csv`)
  y la importancia de cada rasgo del Random Forest de `Tp9_03` (`datos\Tp9_B_importancia_rasgos.csv`).
- `Tp9_C_puntos_y_rasgos.ows` - los 426 puntos etiquetados al azar de las tres variantes, con los rasgos de cambio de cada
  sensor en el punto, la clase del mapa multisensor y el cambio AlphaEarth 2021 a 2025 (`datos\Tp9_C_puntos_etiquetados.csv`).

Orange no calcula los intervalos de confianza: estan en las tablas. La muestra de A es estratificada por clase de altura
(no proporcional al area): sirve para comparar distribuciones, no para estimar superficies.

Cambios del 27/10/2026 (los widgets nuevos arrancan con sus valores por defecto; se configuran así):

- `Tp9_C_puntos_y_rasgos.ows`: **Select Rows** con la condición `confianza` es una de `alta`, `media` y, a la salida, un
  **Box Plot** del dHV por referencia (333 puntos, 10 positivos: mediana −2,59 dB contra +0,74 dB). **Select Columns**
  (target = `referencia`; features = `dHV_L_dB`, `dNDVI`, `HV_L_2026_dB`; el resto a metas) hacia **Test and Score**
  (Cross validation, 5 folds, estratificada) con **Tree** y **Logistic Regression**: AUC de 0,59 y 0,67. Con 14
  positivos el resultado es inestable y no es la exactitud del mapa.
- `Tp9_B_variantes_e_importancia.ows`: el Bar Plot de la comisión se reemplazó por un **Scatter Plot** (eje X =
  `comision_perdida`, eje Y = `IC_comision`, etiqueta = `variante`): una variante sólo es mejor si la diferencia
  supera los intervalos. El Bar Plot de importancia se colorea con la columna nueva `banda` (banda L, banda C, óptico)
  de `datos\Tp9_B_importancia_rasgos.csv`, que trae también `importancia (%)`.
