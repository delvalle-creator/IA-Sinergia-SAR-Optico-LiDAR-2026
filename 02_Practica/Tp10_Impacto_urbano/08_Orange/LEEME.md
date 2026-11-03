# Tp10 — workflows de Orange (desarrollo)

Abrir con Orange 3.40 (`Archivo > Abrir`). Los datos están en `datos\` con ruta relativa: la carpeta `08_Orange` puede copiarse entera a otra computadora.

- `Tp10_A_sinergia_bandas_por_clase.ows` — 300 píxeles de 20 m por clase del entrenamiento de MapBiomas (píxeles estables 2023-2025: urbano, vegetación leñosa, herbáceas y cultivos, agua, suelo desnudo), con C VV y VH del compuesto de Sentinel-1, S HH de NovaSAR, L HH y HV de NISAR en dB, y NDBI, NDVI y MNDWI del compuesto de Sentinel-2 (`datos\Tp10_A_pixeles_entrenamiento.csv`). Box Plot de cada banda por clase y Scatter Plot C VV frente a L HH. La S HH sólo tiene dato en los píxeles que caen en la huella de NovaSAR.
  - **Rank** (nodo nuevo): ordena las capas por ganancia de información respecto de la clase. En la corrida del docente: NDVI 0,849, MNDWI 0,836, C VV 0,752, C VH 0,711, L HH 0,666, NDBI 0,605, L HV 0,555.
  - **Random Forest + Test and Score** (nodos nuevos): validación cruzada de 10 grupos sobre los mismos 1.500 píxeles de entrenamiento: exactitud 0,779. Es una exactitud **optimista** (los píxeles salen de los mismos lugares que el entrenamiento) y no reemplaza la del Tp4: sirve para ver por qué la exactitud fuera de bolsa no es la del mapa.
- `Tp10_B_variantes_e_importancia.ows` — la tabla de `Tp4_04` con las cuatro variantes (óptico, C, C + L, multisensor), más la fila de la multisensor con banda S de `Tp4_03` (sólo en la huella de NovaSAR) (`datos\Tp10_B_tabla_de_variantes.csv`), y la importancia de cada capa del Random Forest multisensor de `Tp10_02` (`datos\Tp10_B_importancia_por_version.csv`). Orange no dibuja los intervalos de confianza: la figura con IC del 95 % está en el desarrollo (Figura 18), y la mejora se afirma sólo si el IC de la diferencia no incluye el cero.
- `Tp10_C_velocidad_por_cobertura.ows` — muestra de píxeles de 40 m de E_PARANA_DIAMANTE con velocidad vertical (`Tp10_05`), hasta 1.500 por clase de MapBiomas 2025, con la dispersión entre pares, los pares válidos y la altura del MDE del IGN (`datos\Tp10_C_pixeles_velocidad.csv`; la columna de velocidad conserva el nombre `velocidad_mm_ano` para no romper el workflow, y es mm/año).
  - En el Box Plot conviene fijar el eje de −60 a 20 mm/año: los extremos comprimen las cajas.
  - **Distributions** (nodo nuevo): la velocidad o la altura del IGN por clase, como histograma.

Las muestras de A y C son por clase (no proporcionales al área): sirven para comparar distribuciones, no para estimar superficies.
