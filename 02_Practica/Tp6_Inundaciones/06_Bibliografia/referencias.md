# Tp6 — Referencias

## Artículos 2020–2026 (de la presentación del curso)

- Konapala, G., Kumar, S. V. y Ahmad, S. K. (2021). Exploring Sentinel-1 and Sentinel-2 diversity for flood inundation mapping using deep learning. *ISPRS Journal of Photogrammetry and Remote Sensing*, 180, 163–173. https://doi.org/10.1016/j.isprsjprs.2021.08.016
  Compara qué aporta cada sensor, y su combinación, al mapeo de inundaciones: la misma pregunta que la sinergia C–óptico del paso 2 y la tabla de variantes.
- Zhang, R., Yang, Y., Li, Z., Li, P. y Wang, H. (2026). Optical and SAR image fusion: a review of theories, methods, and applications. *Remote Sensing*, 18(1), 73. https://doi.org/10.3390/rs18010073
  Niveles de fusión óptico–SAR; fundamento de la elección de la fusión de decisión.
- Li, Y. y Xiao, X. (2025). Deep learning-based fusion of optical, radar, and LiDAR data for advancing land monitoring. *Sensors*, 25(16), 4991. https://doi.org/10.3390/s25164991
  Limitaciones de cada sensor en la fusión óptico–radar–LiDAR; marco para el uso del LiDAR como control del MDE.

## Referencias de método

- Cohen, S., Brakenridge, G. R., Kettner, A., Bates, B., Nelson, J., McDonald, R., Huang, Y.-F., Munasinghe, D. y Zhang, J. (2018). Estimating floodwater depths from flood inundation maps and topography. *Journal of the American Water Resources Association*, 54(4), 847–858. https://doi.org/10.1111/1752-1688.12609
  **Referencia de método.** Es el artículo de FwDET 1.0 (Floodwater Depth Estimation Tool) y la idea de `Tp6_04`: profundidad = cota del borde − MDE.
- Cohen, S., Raney, A., Munasinghe, D. y otros (2019). The Floodwater Depth Estimation Tool (FwDET v2.0) for improved remote sensing analysis of coastal flooding. *Natural Hazards and Earth System Sciences*, 19, 2053–2065. https://doi.org/10.5194/nhess-19-2053-2019
  **Referencia de método.** FwDET 2.0: la versión que el docstring de `Tp6_04` cita junto con la 1.0; mejora la asignación de la cota del borde a cada píxel inundado.
- Olofsson, P., Foody, G. M., Herold, M., Stehman, S. V., Woodcock, C. E. y Wulder, M. A. (2014). Good practices for estimating area and assessing accuracy of land change. *Remote Sensing of Environment*, 148, 42–57. https://doi.org/10.1016/j.rse.2014.02.015
  **Referencia de método.** El estimador con que el Tp4 valida las variantes.

## Libro abierto y práctica paso a paso (de la presentación del curso)

- Cardille, J. A., Crowley, M. A., Saah, D. y Clinton, N. E. (eds.) (2024). *Cloud-Based Remote Sensing with Google Earth Engine*. Springer. CC BY 4.0. https://doi.org/10.1007/978-3-031-26588-4
  Capítulos 39 (SAR) y 42 (aguas superficiales).
- UN-SPIDER (2025). Recommended Practice: Flood Mapping Practice Using Sentinel-1 and Sentinel-2 Imagery. Sin DOI. https://un-spider.org/es/node/13488
  Mapeo de inundaciones con Sentinel-1 y Sentinel-2 paso a paso; se vincula directamente con los pasos 1 a 3.

## Otras referencias de método citadas en el Desarrollo

- Tsyganskaya, V., Martinis, S., Marzahn, P. y Ludwig, R. (2018). Detection of temporary flooded vegetation using Sentinel-1 time series data. *Remote Sensing*, 10(8), 1286. https://doi.org/10.3390/rs10081286
  **Referencia de método.** Detección de vegetación inundada temporalmente por el aumento de la retrodispersión respecto de la fecha seca: el fundamento de la regla R2 y de su prueba con SAOCOM.
- Martinis, S., Twele, A. y Voigt, S. (2009). Towards operational near real-time flood detection using a split-based automatic thresholding procedure on high resolution TerraSAR-X data. *Natural Hazards and Earth System Sciences*, 9, 303–314. https://doi.org/10.5194/nhess-9-303-2009
  **Referencia de método.** Otsu por partición en ventanas con agua y tierra: la alternativa al umbral manual cuando el histograma de todo el sitio es unimodal (paso 1).
- Hawker, L., Uhe, P., Paulo, L., Sosa, J., Savage, J., Sampson, C. y Neal, J. (2022). A 30 m global map of elevation with forests and buildings removed. *Environmental Research Letters*, 17, 024016. https://doi.org/10.1088/1748-9326/ac4d4f
  FABDEM: el modelo de terreno con que se repite la profundidad del paso 5 y el control del paso 6.

## Citadas en el código (referencias de método)

- Pekel, J.-F., Cottam, A., Gorelick, N. y Belward, A. S. (2016). High-resolution mapping of global surface water and its long-term changes. *Nature*, 540(7633), 418–422. https://doi.org/10.1038/nature20584
  Origen de JRC Global Surface Water (persistencia del agua); se usa en los pasos 1 y 5 para excluir el agua permanente.
- Peter, B. G., Cohen, S., Lucey, R., Munasinghe, D., Raney, A. y Brakenridge, G. R. (2022; publicado en línea en 2020). Google Earth Engine implementation of the Floodwater Depth Estimation Tool (FwDET-GEE) for rapid and large scale flood analysis. *IEEE Geoscience and Remote Sensing Letters*, 19, 1–5. https://doi.org/10.1109/LGRS.2020.3031190
  Versión de FwDET en la que se basa el cálculo de profundidad del paso 5.

## Fuentes de datos y de información

- Santoro, M. y Cartus, O. (2026). ESA Biomass Climate Change Initiative (Biomass_cci): Global datasets of forest above-ground biomass for the years 2005-2012 and 2015-2024, v7.0. NERC EDS Centre for Environmental Data Analysis. https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903 (Figura 7 del Desarrollo).
- JAXA EORC (2021). Calibration result of ALOS-2/PALSAR-2 JAXA standard products (factor de calibración −83,0 dB). https://www.eorc.jaxa.jp/ALOS-2/en/calval/calval_index.htm (procesamiento del ALOS-2 ScanSAR).
- La Nación (12/05/2024). Inundaciones en Concordia: más de 500 evacuados por la crecida del río Uruguay (553 evacuados; 13,7 m en el puerto el 12/05/2024 a las 7 h, según Hidrología de Salto Grande). https://www.lanacion.com.ar/sociedad/inundaciones-en-concordia-mas-de-500-evacuados-por-la-crecida-del-rio-uruguay-nid12052024/
- LT15 Concordia (25/07/2023). Una «crecida ordinaria» hará variar la altura del río Uruguay (el puerto de Concordia pasó de 5 m a 7,90 m a fines de julio de 2023). https://lt15concordia.com.ar/index.php/2023/07/25/una-crecida-ordinaria-hara-variar-la-altura-del-rio-uruguay/
- Conclusión (02/12/2023). Concordia: más de 1500 personas fueron afectadas por la crecida del río Uruguay (13,44 m en el puerto). https://www.conclusion.com.ar/?p=1097571

- Sentinel-1 RTC, Sentinel-2 L2A, JRC Global Surface Water y Copernicus DEM GLO-30, vía Microsoft Planetary Computer. https://planetarycomputer.microsoft.com
- ICESat-2 ATL08 v007: NASA, NSIDC / Earthdata.
- Carta Internacional Espacio y Grandes Catástrofes, activación 880: inundación en Entre Ríos, mayo de 2024. https://disasterscharter.org/es/activations/flood-in-argentina-activation-880-
- NovaSAR-1: SSTL – CSIRO (escenas del archivo del curso).
