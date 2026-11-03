# Tp7 - workflows de Orange

Abrir con Orange 3.40 (`Archivo > Abrir`). Los datos estan en `datos\` con ruta relativa: la carpeta
`08_Orange` puede copiarse entera a otra computadora.

- `Tp7_A_coherencia_por_banda_y_zona.ows` - pixeles de 10 m de E1_DIAMANTE_BARRANCA, hasta 800 por clase de
  MapBiomas 2018 (semilla 2026), con la coherencia de la banda X (COSMO-SkyMed, 15-19/10/2018, promediada de 2 a
  10 m) y de la banda C (Sentinel-1 HyP3, 12-24/10/2018 y 18-30/09/2018, 40 m) y la zona de la ladera
  (`04_Tablas_de_trabajo\E1_zonas_ladera.gpkg`: escarpa, bloque, pie y ciudad), el anillo de referencia o el resto
  del sitio (`datos\Tp7_A_coherencia_por_banda_y_zona.csv`). Distributions de la coherencia X por cobertura, Box
  Plot de la coherencia C por cobertura y de la X por zona, y Scatter Plot X frente a C.
- `Tp7_B_icesat2_menos_mde.ows` - los 12.521 segmentos ATL08 de 100 m con terreno valido (2018-2026), en tabla
  larga: ICESat-2 menos IGN 5 m (SRVN16), GLO-30 y FABDEM (EGM2008), con la zona (ladera, anillo, resto), la
  fuerza del haz y la pendiente (`datos\Tp7_B_icesat2_menos_mde.csv`). Box Plot por MDE y por zona y Scatter Plot
  de la pendiente frente a la diferencia.

Para que sirven: la pregunta 3 (que parte de la diferencia de coherencia entre X y C se debe a la longitud de onda
y que parte a la resolucion, la polarizacion y el intervalo: compare las dos bandas en la MISMA cobertura) y la
pregunta 8 (sesgo y dispersion de cada MDE en tierra firme y en la barranca).

Orange no calcula los umbrales ni la fusion: estan en `Tp7_02` y en sus tablas. La muestra de A es por clase (no
proporcional al area): sirve para comparar distribuciones, no para estimar superficies.
