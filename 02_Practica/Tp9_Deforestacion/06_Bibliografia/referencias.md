# Tp9 — Referencias

Artículos 2020–2026 con DOI verificado y referencias de método que el código usa.
Cada una, con una línea de para qué sirve en este práctico.

## Artículos

- Tang, X., Bratley, K. H., Cho, K., Bullock, E. L., Olofsson, P. y Woodcock,
  C. E. (2023). Near real-time monitoring of tropical forest disturbance by fusion
  of Landsat, Sentinel-2, and Sentinel-1 data. *Remote Sensing of Environment*,
  294, 113626. https://doi.org/10.1016/j.rse.2023.113626
  — Para qué: fusión óptico + banda C para detectar disturbios del bosque; el
  antecedente directo del paso 4 y de la comparación de variantes.

- Silva, C. A., Duncanson, L., Hancock, S. et al. (2021). Fusing simulated GEDI,
  ICESat-2 and NISAR data for regional aboveground biomass mapping. *Remote
  Sensing of Environment*, 253, 112234. https://doi.org/10.1016/j.rse.2020.112234
  — Para qué: por qué GEDI y la banda L de NISAR se complementan; fundamenta el
  uso de rh98 como referencia de estructura frente a la banda L (paso 2).

- Kacic, P., Thonfeld, F., Gessner, U. y Kuenzer, C. (2023). Forest structure
  characterization in Germany: novel products and analysis based on GEDI,
  Sentinel-1 and Sentinel-2 data. *Remote Sensing*, 15(8), 1969.
  https://doi.org/10.3390/rs15081969
  — Para qué: relación entre la estructura que mide GEDI y Sentinel-1 y 2; útil
  para leer las curvas de respuesta de C y del óptico (paso 2).

- Lang, N., Jetz, W., Schindler, K. y Wegner, J. D. (2023). A high-resolution
  canopy height model of the Earth. *Nature Ecology & Evolution*, 7(11),
  1778–1789. https://doi.org/10.1038/s41559-023-02206-6
  — Para qué: altura del dosel entrenada con GEDI y aplicada al óptico; muestra
  los límites del óptico para la estructura, que es lo que el paso 2 mide.

- Li, Y. y Xiao, X. (2025). Deep learning-based fusion of optical, radar, and
  LiDAR data for advancing land monitoring. *Sensors*, 25(16), 4991.
  https://doi.org/10.3390/s25164991
  — Para qué: limitaciones de cada sensor al fusionar óptico, radar y LiDAR;
  marco de la discusión de rasgos.

- Reiche, J., Mullissa, A., Slagter, B., Gou, Y., Tsendbazar, N.-E., Odongo-Braun, C.,
  Vollrath, A., Weisse, M. J., Stolle, F., Pickens, A., Donchyts, G., Clinton, N.,
  Gorelick, N. y Herold, M. (2021). Forest disturbance alerts for the Congo Basin using
  Sentinel-1. *Environmental Research Letters*, 16(2), 024005.
  https://doi.org/10.1088/1748-9326/abd0a8 (verificado en IOPscience y DOAJ)
  — Para qué: alertas de disturbio con banda C y por qué el cambio de VH solo detecta
  aperturas de copa (rasgo `dVH_C`, paso 4).

- Pötzschner, F., Baumann, M., Gasparri, N. I., Conti, G., Loto, D., Piquer-Rodriguez,
  M. y Kuemmerle, T. (2022). Ecoregion-wide, multi-sensor biomass mapping highlights a
  major underestimation of dry forests carbon stocks. *Remote Sensing of Environment*,
  269, 112849. https://doi.org/10.1016/j.rse.2021.112849
  — Para qué: bosques secos del Chaco con radar y óptico; los productos globales de
  biomasa los subestiman (contexto CCI del desarrollo).

Silva et al. (2021) usa datos simulados y Kacic et al. (2023) es de Alemania: su
pertinencia para el Espinal es indirecta (marco de la sinergia, no resultados
comparables).

## Referencias de método (anteriores a 2020, usadas por el código)

- Olofsson, P., Foody, G. M., Herold, M., Stehman, S. V., Woodcock, C. E. y
  Wulder, M. A. (2014). Good practices for estimating area and assessing accuracy
  of land change. *Remote Sensing of Environment*, 148, 42–57.
  https://doi.org/10.1016/j.rse.2014.02.015
  — Referencia de método: exactitud y área con IC de las variantes en el Tp4.

- Stehman, S. V. (2014). Estimating area and map accuracy for stratified random
  sampling when the strata are different from the map classes. *International Journal
  of Remote Sensing*, 35(13), 4923–4939. https://doi.org/10.1080/01431161.2014.930207
  — Referencia de método: exactitud de mapas con máscara o con otro entrenamiento
  evaluados con la muestra del Tp4, cuyos estratos ya no coinciden con sus clases.

- Small, D. (2011). Flattening gamma: radiometric terrain correction for SAR
  imagery. *IEEE Transactions on Geoscience and Remote Sensing*, 49(8),
  3081–3093. https://doi.org/10.1109/TGRS.2011.2120616
  — Referencia de método: γ⁰ frente a σ⁰; fundamenta por qué se declara que
  NovaSAR entra en σ⁰ mientras el resto de la pila está en γ⁰.

## Fuentes de datos

- JAXA – ASF DAAC. ALOS PALSAR FBS RTC, 13/03/2011. https://search.asf.alaska.edu
- JAXA. ALOS-2 PALSAR-2 mosaico anual 2021. Microsoft Planetary Computer:
  https://planetarycomputer.microsoft.com
- NASA – ISRO. NISAR L2 GCOV, 17/09/2026. ASF DAAC: https://search.asf.alaska.edu
- ESA – Copernicus. Sentinel-1 IW GRD RTC y Sentinel-2 MSI L2A. Microsoft
  Planetary Computer.
- SSTL – CSIRO. NovaSAR-1 GRD HH, escena 50896, 22/12/2023. https://data.novasar.csiro.au
- ESA. BIOMASS L1B DGM, 12/08/2026, franja S2, traza 006, cuadro 284 (Federal); L2A FP_FH y FP_GN del 28/07 al 09/08/2026. ESA MAAP: https://catalog.maap.eo.esa.int
- NASA. GEDI L2A versión 003. LP DAAC, NASA Earthdata.
- CONAE. SAOCOM-1A y SAOCOM-1B L1A SLC TOPSAR Narrow A (TNAQP), HH HV VH VV, 04/08/2021
  (EOL1ASARSAO1A15725989) y 11/09/2026 (EOL1ASARSAO1B15520854). Catálogo SAOCOM:
  https://catalog.saocom.conae.gov.ar
- INPE / CAST. CBERS-4A cámara WPM, L4, 02/08/2021 y 05/09/2026, fusionado a 2 m
  (Brovey ponderado), licencia CC BY 4.0.
  https://data.inpe.br/stac/browser/collections/CB4A-WPM-L4-DN-1
- Proyecto MapBiomas Argentina. Colección 3 de los Mapas Anuales de Cobertura y Uso del
  Suelo (cobertura 1985–2025 y pérdida de vegetación 1987–2025), licencia CC BY 4.0.
  https://argentina.mapbiomas.org
- The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and
  Google DeepMind (CC BY 4.0). Copia en Source Cooperative:
  https://source.coop/tge-labs/aef (años 2021 y 2025).
- USGS / NASA. Landsat 8 OLI, Colección 2 Nivel 2, 07/08/2021, y Landsat 9 OLI,
  14/09/2026. Microsoft Planetary Computer:
  https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2

## Biomasa de referencia (ESA CCI Biomass)

- Santoro, M. y Cartus, O. (2026). ESA Biomass Climate Change Initiative (Biomass_cci): Global datasets of forest above-ground biomass for the years 2005-2012 and 2015-2024, v7.0. NERC EDS Centre for Environmental Data Analysis. https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903
  — Para qué: biomasa aérea de referencia externa para la tendencia del monte, con su desvío por píxel. La diferencia 2010 → 2015 es un efecto del cambio de sensor: la tendencia se lee de 2015 en adelante. Recortes en `00_COMUN/08_Originales_crudos/CCI_BIOMASS`.
- Pötzschner et al. (2022): ver «Artículos»; los productos globales de biomasa subestiman fuertemente los bosques secos del Chaco y el Espinal comparte ese riesgo.

## GEDI L2B y L4A (cobertura, PAI y biomasa por huella)

- Cotrina-Sanchez, A., Torresani, M. y Corado, L. (2026). GEDIMetrics: a QGIS plugin for accessing and integrating multi-product GEDI spaceborne LiDAR data. *Earth Science Informatics*, 19, 205. https://doi.org/10.1007/s12145-026-02254-z
  *Para qué:* unión de GEDI L2A, L2B y L4A por shot_number; el desarrollo hace lo mismo con `00_COMUN/09_Herramientas/des_gedi_l2ab_l4a.py` sobre los gránulos del disco.
- NASA. GEDI L2B V003 (cobertura del dosel, PAI y FHD por huella). LP DAAC, NASA Earthdata. https://www.earthdata.nasa.gov/data/catalog/lpcloud-gedi02-b-003
- Dubayah, R. O., Armston, J., Kellner, J. R., Duncanson, L., Healey, S. P., Patterson, P. L., Hancock, S., Tang, H., Bruening, J. M., Hofton, M. A., Blair, J. B. y Luthcke, S. B. (2026). GEDI L4A Footprint Level Aboveground Biomass Density, Version 3. ORNL DAAC, Oak Ridge, Tennessee, EE. UU. https://doi.org/10.3334/ORNLDAAC/2508
