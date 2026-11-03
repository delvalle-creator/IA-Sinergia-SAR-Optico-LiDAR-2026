# Tp5 — Referencias

## Artículos 2020–2026 (de la presentación del curso)

- Belenguer-Plomer, M. A., Tanase, M. A., Chuvieco, E. y Bovolo, F. (2021). CNN-based burned area mapping using radar and optical data. *Remote Sensing of Environment*, 260, 112468. https://doi.org/10.1016/j.rse.2021.112468
  Combina Sentinel-1 y Sentinel-2 para mapear área quemada: el mismo par de sensores de V1, V2 y V4, con otro algoritmo.
- Zhang, Q., Ge, L., Zhang, R., Metternicht, G. I., Du, Z., Kuang, J. y Xu, M. (2021). Deep-learning-based burned area mapping using the synergy of Sentinel-1&2 data. *Remote Sensing of Environment*, 264, 112575. https://doi.org/10.1016/j.rse.2021.112575
  Aprendizaje profundo sobre Sentinel-1 y Sentinel-2 juntos; útil para discutir qué aporta el radar cuando el óptico está limitado por nubes o humo.
- Li, Y. y Xiao, X. (2025). Deep learning-based fusion of optical, radar, and LiDAR data for advancing land monitoring. *Sensors*, 25(16), 4991. https://doi.org/10.3390/s25164991
  Revisión de la fusión óptico–radar–LiDAR y de las limitaciones de cada sensor; marco para el papel de GEDI como evidencia y no como variable del modelo.
- Zhang, R., Yang, Y., Li, Z., Li, P. y Wang, H. (2026). Optical and SAR image fusion: a review of theories, methods, and applications. *Remote Sensing*, 18(1), 73. https://doi.org/10.3390/rs18010073
  Niveles de fusión óptico–SAR (píxel, rasgo, decisión): fundamento de la elección de decisión en V3 y de rasgo en V4.

## Fuego en humedales con radar (2020–2026)

- Del Valle, H., Sione, W. F. y Aceñolaza, P. G. (2022). Wetland fire assessment and monitoring in the Paraná River Delta, using radar and optical data for burnt area mapping. *Fire*, 5(6), 190. https://doi.org/10.3390/fire5060190
  Área quemada en los humedales del Delta con Sentinel-1, SAOCOM y Sentinel-2: radar y óptico llegan a la misma exactitud (0,74) y la banda L de SAOCOM muestra mejor las cicatrices que la C. Es el caso del práctico.

## Referencia de método

- Olofsson, P., Foody, G. M., Herold, M., Stehman, S. V., Woodcock, C. E. y Wulder, M. A. (2014). Good practices for estimating area and assessing accuracy of land change. *Remote Sensing of Environment*, 148, 42–57. https://doi.org/10.1016/j.rse.2014.02.015
  **Referencia de método.** El estimador con que el Tp4 valida las cuatro variantes.

## Libro abierto (de la presentación del curso)

- Cardille, J. A., Crowley, M. A., Saah, D. y Clinton, N. E. (eds.) (2024). *Cloud-Based Remote Sensing with Google Earth Engine*. Springer. CC BY 4.0. https://doi.org/10.1007/978-3-031-26588-4
  Capítulos 20 (fusión de clasificaciones), 39 (SAR) y 46 (fuego activo).

## Citadas en el código (referencias de método)

- Key, C. H. y Benson, N. C. (2006). Landscape Assessment (LA): Sampling and analysis methods. En: *FIREMON: Fire Effects Monitoring and Inventory System*. USDA Forest Service, Rocky Mountain Research Station, General Technical Report RMRS-GTR-164-CD, LA-1–LA-55. (Informe técnico, sin DOI.)
  Origen del dNBR y del umbral de 0,27 que usa el código. https://www.fs.usda.gov/rm/pubs_series/rmrs/gtr/rmrs_gtr164.pdf
- Miller, J. D. y Thode, A. E. (2007). Quantifying burn severity in a heterogeneous landscape with a relative version of the delta Normalized Burn Ratio (dNBR). *Remote Sensing of Environment*, 109(1), 66–80. https://doi.org/10.1016/j.rse.2006.12.006
  Origen del RdNBR (paso 4).

## Contexto hidrológico y del evento

- Instituto Nacional del Agua (2020a, 2020b, 2020c). Escenario hidrológico de la Cuenca del Plata, agosto, septiembre y octubre de 2020. https://www.ina.gov.ar/archivos/alerta/Escenario2020_Agosto.pdf, ..._Septiembre.pdf, ..._Octubre.pdf
  Alturas del Paraná en Rosario (promedios de julio, agosto y septiembre de 2020) de la **Figura 13** del Desarrollo.
- La Capital (03/09/2020). Gracias a la lluvia: después de mucho tiempo, no hay fuego en las islas frente a Rosario. https://www.lacapital.com.ar/la-ciudad/gracias-la-lluvia-despues-mucho-tiempo-no-hay-fuego-las-islas-frente-rosario-n2607469.html
  Lluvia de fines de agosto (más de 35 mm en Rosario).

## Embeddings

- Brown, C. F., Kazmierski, M. R., Pasquarella, V. J. et al. (2025). AlphaEarth Foundations: An embedding field model for accurate and efficient global mapping from sparse label data. arXiv:2507.22291. https://arxiv.org/abs/2507.22291

## Fuentes de datos

- Sentinel-1 RTC y Sentinel-2 L2A: ESA – Copernicus, vía Microsoft Planetary Computer. https://planetarycomputer.microsoft.com
- ALOS-2 PALSAR-2, mosaicos anuales: JAXA, vía Microsoft Planetary Computer.
- SAOCOM-1A: CONAE (archivo del curso SAR CEREGEO 2023); catálogo SAOCOM. https://catalog.saocom.conae.gov.ar
- Landsat 8 OLI/TIRS Colección 2 Nivel 2 (19/07 y 07/10/2020, referencia independiente del paso 5): USGS / NASA. https://doi.org/10.5066/P9OGBGM6
- CCI Biomass v7: Santoro, M. y Cartus, O. (2026). ESA Biomass Climate Change Initiative (Biomass_cci), v7.0. NERC EDS CEDA. https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903
- MapBiomas Argentina, Colección 3 (cobertura 1985–2025) y Colección 1 de MapBiomas Fuego. https://argentina.mapbiomas.org (CC BY 4.0)
- BIOMASS banda P, L1B DGM: ESA, ESA MAAP. https://catalog.maap.eo.esa.int
- AlphaEarth Foundations Satellite Embedding dataset: Google y Google DeepMind (CC BY 4.0), copia en Source Cooperative. https://source.coop/tge-labs/aef
- GEDI L2A V003: NASA, LP DAAC / Earthdata. Aviso de la versión 3: https://www.earthdata.nasa.gov/data/alerts-outages/gedi-version-3-data-products-released

## GEDI L2B y L4A (cobertura, PAI y biomasa por huella)

- Cotrina-Sanchez, A., Torresani, M. y Corado, L. (2026). GEDIMetrics: a QGIS plugin for accessing and integrating multi-product GEDI spaceborne LiDAR data. *Earth Science Informatics*, 19, 205. https://doi.org/10.1007/s12145-026-02254-z
  *Para qué:* unión de GEDI L2A, L2B y L4A por shot_number; el desarrollo hace lo mismo con `00_COMUN/09_Herramientas/des_gedi_l2ab_l4a.py` sobre los gránulos del disco.
- NASA. GEDI L2B V003 (cobertura del dosel, PAI y FHD por huella). LP DAAC, NASA Earthdata. https://www.earthdata.nasa.gov/data/catalog/lpcloud-gedi02-b-003
- Dubayah, R. O., Armston, J., Kellner, J. R., Duncanson, L., Healey, S. P., Patterson, P. L., Hancock, S., Tang, H., Bruening, J. M., Hofton, M. A., Blair, J. B. y Luthcke, S. B. (2026). GEDI L4A Footprint Level Aboveground Biomass Density, Version 3. ORNL DAAC, Oak Ridge, Tennessee, EE. UU. https://doi.org/10.3334/ORNLDAAC/2508
