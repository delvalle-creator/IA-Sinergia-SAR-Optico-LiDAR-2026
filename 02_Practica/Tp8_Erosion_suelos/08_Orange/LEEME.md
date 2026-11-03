# Tp8 - workflows de Orange (desarrollo)

Abrir con Orange 3.40 (`Archivo > Abrir`). Los datos estan en `datos\` con ruta relativa: la carpeta
`08_Orange` puede copiarse entera a otra computadora.

- `Tp8_A_textura_y_rasgos.ows` - muestra de unos 1.400 pixeles de 10 m de F_BOVRIL por clase de frecuencia de suelo
  desnudo (nunca, 1 a 2, 3 a 5 y 6 o mas meses), con la textura (CV) de NovaSAR S y de Sentinel-1 C de `Tp8_02`
  (corregida: 84 puntos de enlace y -80 20), el contraste GLCM de SNAP, la pendiente FABDEM, la susceptibilidad de
  `Tp8_03` y la clase de MapBiomas 2023 (`datos\Tp8_A_textura_y_rasgos.csv`). Box Plot del CV de S por clase, después de un Select Rows
  con `S_CV_HH <= 1` (saca 111 pixeles extremos de casas y alambrados que aplastaban las cajas), y Scatter Plot del CV
  frente al contraste GLCM, con un widget Color que ordena la paleta de las clases de claro (nunca) a oscuro (6 o mas).
- `Tp8_B_variantes_e_importancia.ows` - la tabla de `Tp4_04` con las dos variantes (`datos\Tp8_B_tabla_de_variantes.csv`)
  y la importancia de cada rasgo del Random Forest (`datos\Tp8_B_importancia_rasgos.csv`, con la columna `sensor`
  discreta: el Bar Plot colorea por sensor). La importancia dice cuanto uso el modelo cada rasgo, no cuanto mejora el mapa.
- `Tp8_C_puntos_y_embeddings.ows` - los 284 puntos etiquetados al azar en el paso 6, con la semejanza AlphaEarth al
  prototipo de erosion, la susceptibilidad, la pendiente y los meses de suelo desnudo (`datos\Tp8_C_puntos_etiquetados.csv`).

- `Tp8_D_aporte_del_radar.ows` - los 620 pixeles de los 40 poligonos de entrenamiento con sus cinco rasgos y la columna
  `id_poligono` (meta) (`datos\Tp8_D_pixeles_entrenamiento.tab`). Dos Select Columns (optico + pendiente; optico +
  pendiente + S + C), Random Forest de 300 arboles con semilla fija y Test and Score con "Cross validation by feature" =
  `id_poligono`: todos los pixeles de un poligono quedan juntos. AUC 0,697 sin radar y 0,734 con radar: con 40
  poligonos, la diferencia esta dentro de la variacion de las particiones.

Orange escribe los numeros con punto decimal y no se puede cambiar. Orange no calcula los intervalos de confianza: estan en las tablas. La muestra de A es estratificada por clase de
frecuencia (no proporcional al area): sirve para comparar distribuciones, no para estimar superficies.
