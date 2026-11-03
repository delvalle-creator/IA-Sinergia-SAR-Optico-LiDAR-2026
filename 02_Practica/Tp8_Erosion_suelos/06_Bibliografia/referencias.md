# Tp8 — Referencias

Artículos 2020–2026 con DOI verificado y referencias de método que el código usa.
Cada una, con una línea de para qué sirve en este práctico.

## Artículos

- Heiden, U., d'Angelo, P., Schwind, P., Karlshöfer, P., Müller, R., Zepp, S.,
  Wiesmeier, M. y Reinartz, P. (2022). Soil Reflectance Composites—Improved
  Thresholding and Performance Evaluation. *Remote Sensing*, 14(18), 4526.
  https://doi.org/10.3390/rs14184526
  — Para qué: compuestos de suelo desnudo a partir de series temporales y la
  elección de umbrales de índices para separar suelo expuesto de vegetación
  (paso 1).

- Yang, A., Wang, C., Yang, Q., Pang, G., Long, Y., Wang, L., Yang, L. y
  Cruse, R. M. (2022). Choosing the Right Horizontal Resolution for Gully Erosion
  Susceptibility Mapping Using Machine Learning Algorithms: A Case in Highly
  Complex Terrain. *Remote Sensing*, 14(11), 2580.
  https://doi.org/10.3390/rs14112580
  — Para qué: susceptibilidad a cárcavas con Random Forest y el efecto de la
  resolución (de 0,5 a 30 m): sostiene por qué la pendiente de un MDE de 30 m no
  resuelve la cárcava (paso 5). Trabaja en relieve muy complejo; en las lomas de
  Bovril la pendiente pesa menos y la resolución, más.

- Zhang, R., Yang, Y., Li, Z., Li, P. y Wang, H. (2026). Optical and SAR image
  fusion: a review of theories, methods, and applications. *Remote Sensing*,
  18(1), 73. https://doi.org/10.3390/rs18010073
  — Para qué: niveles de fusión óptico–SAR y sus requisitos de corregistro; el
  marco de la fusión de rasgos del paso 5.

- Li, Y. y Xiao, X. (2025). Deep learning-based fusion of optical, radar, and
  LiDAR data for advancing land monitoring. *Sensors*, 25(16), 4991.
  https://doi.org/10.3390/s25164991
  — Para qué: limitaciones de cada sensor al combinarlos; útil para la discusión
  de qué aporta la textura SAR frente al óptico.

- Louzada, R. O., Reis, L. K., Diniz, J. M. F. de S., Roque, F. de O., Gama, F. F.
  y Bergier, I. (2023). Combining optical and microwave remote sensing for
  assessing gullies in human-disturbed vegetated landscapes. *Catena*, 228,
  107127. https://doi.org/10.1016/j.catena.2023.107127
  — Para qué: cárcavas con Sentinel-1, Sentinel-2 y ALOS-PALSAR combinados en un
  Random Forest; los índices y la textura ópticos superaron al SAR, como en el
  paso 5 de este práctico.

- Sánchez-Crespo, F. A., Marques da Silva, J. R., Gómez-Villarino, M. T., Gallego,
  E., Fuentes, J. M., García, A. I. y Ayuga, F. (2021). Differential Interferometry
  over Sentinel-1 TopSAR Images as a Tool for Water and Tillage Soil Erosion
  Analysis. *Agronomy*, 11(10), 2075. https://doi.org/10.3390/agronomy11102075
  — Para qué: otra vía del SAR para la erosión (cambios de superficie por
  interferometría en banda C, no textura de una fecha); muestra qué haría falta
  para pasar de susceptibilidad a erosión medida.

## Referencias de método (anteriores a 2020, usadas por el código)

- Haralick, R. M., Shanmugam, K. y Dinstein, I. (1973). Textural features for
  image classification. *IEEE Transactions on Systems, Man, and Cybernetics*,
  SMC-3(6), 610–621. https://doi.org/10.1109/TSMC.1973.4309314
  — Referencia de método: la matriz de co-ocurrencia (GLCM) del paso 3b.

- Rikimaru, A., Roy, P. S. y Miyatake, S. (2002). Tropical forest cover density
  mapping. *Tropical Ecology*, 43(1), 39–47. Sin DOI.
  — Referencia de método: el índice de suelo desnudo (BSI) del paso 1.

- Stehman, S. V. (2014). Estimating area and map accuracy for stratified random
  sampling when the strata are different from the map classes. *International
  Journal of Remote Sensing*, 35(13), 4923–4939.
  https://doi.org/10.1080/01431161.2014.930207
  — Referencia de método: validar las variantes nuevas del paso 5 con las
  muestras ya sorteadas para otros mapas.

- Olofsson, P., Foody, G. M., Herold, M., Stehman, S. V., Woodcock, C. E. y
  Wulder, M. A. (2014). Good practices for estimating area and assessing accuracy
  of land change. *Remote Sensing of Environment*, 148, 42–57.
  https://doi.org/10.1016/j.rse.2014.02.015
  — Referencia de método: muestreo estratificado, exactitud y área con IC de las
  variantes en el Tp4 (paso 6).

- Small, D. (2011). Flattening gamma: radiometric terrain correction for SAR
  imagery. *IEEE Transactions on Geoscience and Remote Sensing*, 49(8),
  3081–3093. https://doi.org/10.1109/TGRS.2011.2120616
  — Referencia de método: por qué γ⁰ y no σ⁰; fundamenta la declaración de que
  NovaSAR entra en σ⁰.

## Fuentes de datos

- Hawker, L., Uhe, P., Paulo, L., Sosa, J., Savage, J., Sampson, C. y Neal, J.
  (2022). A 30 m global map of elevation with forests and buildings removed
  (FABDEM). *Environmental Research Letters*, 17(2), 024016.
  https://doi.org/10.1088/1748-9326/ac4d4f — Para qué: la pendiente de terreno del
  paso 5.
- Santoro, M. y Cartus, O. (2026). ESA Biomass Climate Change Initiative
  (Biomass_cci), v7.0. NERC EDS CEDA.
  https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903 — Para qué: la cobertura
  leñosa en el contexto del sitio.
- Proyecto MapBiomas Argentina, Colección 3 de los Mapas Anuales de Cobertura y Uso
  del Suelo, y capa de pérdida y vegetación secundaria, CC BY 4.0:
  https://argentina.mapbiomas.org
- INPE / CAST. CBERS-4A WPM L4, 15/06/2023, fusionado a 2 m, CC BY 4.0:
  https://data.inpe.br/stac/browser/collections/CB4A-WPM-L4-DN-1
- ESA. BIOMASS banda P L1B DGM (17/09/2026) y L2A FP_FH. ESA MAAP:
  https://catalog.maap.eo.esa.int
- CONAE. SAOCOM-1A TOPSAR Narrow A cuadripolar, 11/09/2023:
  https://catalog.saocom.conae.gov.ar
- Google y Google DeepMind. The AlphaEarth Foundations Satellite Embedding dataset
  (CC BY 4.0), copia en Source Cooperative: https://source.coop/tge-labs/aef
- USGS / NASA. Landsat 8 OLI/TIRS, Colección 2 Nivel 2, 14/09/2023. Microsoft
  Planetary Computer: https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2

- SSTL – CSIRO. NovaSAR-1 Stripmap GRD HH, escena 47974, 14/09/2023. Archivo del
  curso; CSIRO: https://data.novasar.csiro.au
- ESA – Copernicus. Sentinel-2 MSI L2A y Sentinel-1 IW GRD RTC. Microsoft
  Planetary Computer: https://planetarycomputer.microsoft.com
- ESA – Copernicus DEM GLO-30. Microsoft Planetary Computer.
