# Verificación de los resultados del Tp8

## A. Controles sobre lo que entregó la IA

| # | Control | Criterio de aceptación |
|---|---|---|
| 1 | Calibración de NovaSAR | σ⁰ = DN²/CalibrationConstant con la constante leída del `metadata.xml` (1E+05) |
| 2 | Agregación de 6 a 10 m | Media de la potencia (rms de DN), no vecino más próximo |
| 3 | Unidades de la textura | CV calculado en potencia lineal |
| 4 | Desplazamiento de Sentinel-2 L2A | Se descuenta 1000 en escenas con línea de base ≥ 04.00 |
| 5 | Nubosidad | Se cuenta dentro del sitio con la SCL; la del catálogo sólo preselecciona |
| 6 | Exactitud | La fuera de bolsa se rotula OPTIMISTA y no se informa como exactitud |
| 7 | Susceptibilidad | Es la probabilidad de la clase 1, no la de la clase ganadora |

## B. Controles sobre los resultados

| # | Control | Criterio de aceptación | Dónde se lee |
|---|---|---|---|
| 1 | Observación de la serie | Mediana de meses con observación ≥ 8 de 12; si es menor, la frecuencia está subestimada y se declara | `Tp8_01_suelo_desnudo.log`, banda 2 del ráster |
| 2 | Labranza no es erosión | Tres lotes recién labrados verificados en la imagen caen en «1–2 meses» | QGIS + `F_frecuencia_suelo_desnudo_2023_10m.tif` |
| 3 | Desfase de NovaSAR | Mediana del residuo < 1 píxel (10 m) después de aplicar `--desplazamiento`; ventanas con 1 a 2 píxeles declaradas | Medición en QGIS |
| 4 | Cobertura de NovaSAR | Cercana al 92,9 % del sitio (la variante multisensor evalúa el 89 %) | `Tp8_02_textura.log` («% del sitio con dato») |
| 5 | Diferencia de fecha S–C | Se informa en días; si hubo lluvia entre fechas, se declara | `Tp8_02_textura.log` |
| 6 | Piso de speckle | CV de zonas homogéneas (también a 20 × 22 m) medido para S y para C, con ENL = 1/CV² | `--zonas_homogeneas` o Estadísticas de zona en QGIS |
| 7 | Textura por clase | Se informa si el CV sube, baja o no cambia respecto del piso, en cada banda | `F_textura_por_frecuencia.csv` |
| 8 | Importancia de rasgos | Se informa; si domina la pendiente, se revisa el entrenamiento | `Tp8_03_susceptibilidad.log` |
| 9 | Exactitud con muestra independiente | Global, usuario y productor con IC 95 % para las dos variantes | Tp4_03, Tp4_04 |
| 10 | Mejora multisensor | Se afirma sólo si el intervalo de la diferencia entre variantes no incluye el cero (Tp4_04) | `tabla_de_variantes_susceptible.csv` |

## Cifras que deben aparecer en la bitácora

- Escenas Sentinel-2 encontradas y usadas; % útil de cada una.
- % del sitio en cada clase de frecuencia.
- % del sitio con NovaSAR, CV mediano de S, fecha de Sentinel-1 y CV de VV y VH,
  diferencia de días.
- La tabla de CV por clase.
- Exactitud fuera de bolsa (OPTIMISTA), importancia de cada rasgo, hectáreas
  susceptibles (multisensor) y con ≥ 6 meses (solo óptico).

**Hallazgos del curso que se deben reproducir:** NovaSAR 47974 cubre el 92,9 % de
`F_BOVRIL`; con los 84 puntos de enlace la banda S está 80 m al este y 20 m al sur,
y se corrige con `--desplazamiento -80 20`.

## Tabla para el grupo

| Control | Valor | Observación |
|---|---|---|
| Escenas Sentinel-2 usadas en 2023 | | |
| Mediana de meses con observación | | |
| % del sitio con 1–2 meses desnudo | | |
| % del sitio con ≥ 6 meses desnudo | | |
| Desplazamiento NovaSAR aplicado (dx, dy) en m | | |
| Residuo después de corregir (m) | | |
| % del sitio con NovaSAR | | |
| Fecha Sentinel-1 y diferencia con NovaSAR (días) | | |
| CV de zona homogénea: S_HH / C_VV / C_VH | | |
| CV mediano en «≥ 6 meses»: S_HH / C_VV / C_VH | | |
| Rasgo más importante | | |
| Exactitud fuera de bolsa (OPTIMISTA) | | |
| Ha susceptibles: multisensor / solo óptico | | |
| Exactitud global (Tp4): multisensor / solo óptico | | |
