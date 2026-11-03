# 04_Tablas_de_trabajo — la planilla que llena el grupo

Aquí va **una sola** tabla de trabajo:

`escenas_por_pedido.csv`

- La crea `Tp1_06_escenas_por_pedido.py` la primera vez que se corre, con sus 15
  columnas (`sensor, banda, lambda_cm, portal, producto, escena, fecha, hora_utc,
  pasada, polarizaciones, pixel_m, sitio, resultado, fecha_pedido, observaciones`) y
  una fila `EJEMPLO` que el programa ignora.
- La completa **el grupo, a mano**, con una fila por escena pedida o consultada en
  los portales que no se manejan por programa: SAOCOM (CONAE), NISAR banda S
  (Bhoonidhi, ISRO), NovaSAR-1 (CSIRO), COSMO-SkyMed (CONAE–ASI).
- `resultado` es una de cuatro: `obtenida`, `pedida`, `sin cobertura`, `sin acceso`.
  Las ausencias también se anotan.
- Se guarda en CSV, separado por comas, UTF-8. No se cambia el encabezado.

Después de completarla se vuelve a correr `Tp1_06`, que la controla y la suma a
`05_Resultados/04_Tablas/planilla_por_pedido_<SITIO>.csv`.
