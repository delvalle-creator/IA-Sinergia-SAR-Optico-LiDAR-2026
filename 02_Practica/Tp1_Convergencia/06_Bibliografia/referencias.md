# Tp1 — Referencias

Artículos 2020–2026 con DOI verificado (los de la presentación 01 del curso). Cada
uno con una línea de para qué sirve en este práctico.

## Artículos

- Zhang, R., Yang, Y., Li, Z., Li, P. y Wang, H. (2026). Optical and SAR image
  fusion: a review of theories, methods, and applications. *Remote Sensing*, 18(1),
  73. https://doi.org/10.3390/rs18010073
  *Para qué:* las condiciones de una fusión óptico-SAR (corregistro, fechas,
  resolución) que el grado de convergencia anticipa; incluye un catálogo de datos
  abiertos.

- Li, Y. y Xiao, X. (2025). Deep learning-based fusion of optical, radar, and LiDAR
  data for advancing land monitoring. *Sensors*, 25(16), 4991.
  https://doi.org/10.3390/s25164991
  *Para qué:* qué aporta y qué limita cada sensor (óptico, radar, LiDAR) al combinarlos;
  sirve para justificar por qué cada fila de la matriz importa.

- Silva, C. A., Duncanson, L., Hancock, S. et al. (2021). Fusing simulated GEDI,
  ICESat-2 and NISAR data for regional aboveground biomass mapping. *Remote Sensing of
  Environment*, 253, 112234. https://doi.org/10.1016/j.rse.2020.112234
  *Para qué:* ejemplo de convergencia «completa» planificada (LiDAR + banda L) y de
  por qué el muestreo por huellas condiciona lo que se puede fusionar.

- Konapala, G., Kumar, S. V. y Ahmad, S. K. (2021). Exploring Sentinel-1 and
  Sentinel-2 diversity for flood inundation mapping using deep learning. *ISPRS
  Journal of Photogrammetry and Remote Sensing*, 180.
  https://doi.org/10.1016/j.isprsjprs.2021.08.016
  *Para qué:* por qué el par óptico-radar del mismo día (el del 04/11/2023) vale para
  la inundación del Tp6, y qué pasa cuando el óptico falta.

- Cotrina-Sanchez, A., Torresani, M. y Corado, L. (2026). GEDIMetrics: a QGIS plugin
  for accessing and integrating multi-product GEDI spaceborne LiDAR data. *Earth
  Science Informatics*, 19, 205. https://doi.org/10.1007/s12145-026-02254-z
  *Para qué:* el complemento de QGIS que baja, filtra, recorta y une por shot_number
  los productos GEDI L2A, L2B, L4A y L4C; sirve para contrastar la rama GEDI del
  paso 5 con una herramienta distinta del script (sus filtros por defecto, con
  sensibilidad 0,90, no son los del curso).

- Potapov, P., Li, X., Hernandez-Serna, A. y otros (2021). Mapping global forest canopy
  height through integration of GEDI and Landsat data. *Remote Sensing of Environment*,
  253, 112165. https://doi.org/10.1016/j.rse.2020.112165
  *Para qué:* el criterio de sensibilidad 0,90 que usa GEDIMetrics por defecto (el
  curso usa 0,95), paso 5.

- Tang, H., Stoker, J. M., Luthcke, S., Armston, J., Lee, K., Blair, B. y Hofton, M.
  (2023). Evaluating and mitigating the impact of systematic geolocation error on canopy
  height measurement performance of GEDI. *Remote Sensing of Environment*, 291, 113571.
  https://doi.org/10.1016/j.rse.2023.113571
  *Para qué:* el error de posición de las huellas GEDI (unos 10 m en la versión 002;
  menor en la 003, pero del orden de un píxel de Sentinel-2), paso 5.

- Pekel, J.-F., Cottam, A., Gorelick, N. y Belward, A. S. (2016). High-resolution mapping
  of global surface water and its long-term changes. *Nature*, 540, 418–422.
  https://doi.org/10.1038/nature20584
  *Para qué:* JRC Global Surface Water, el agua permanente del paso 6b y la máscara de
  agua de la altura FH (paso 9). No es el filtro de agua de GEDI, que usa la persistencia
  de agua de Landsat del propio L2A.

- Brown, C. F., Kazmierski, M. R., Pasquarella, V. J., Rucklidge, W. J., Samsikova, M. y
  otros (2025). AlphaEarth Foundations: an embedding field model for accurate and
  efficient global mapping from sparse label data. arXiv:2507.22291.
  https://arxiv.org/abs/2507.22291
  *Para qué:* el método de los embeddings anuales AlphaEarth (ampliación del docente).

## Manuales y fuentes de datos (sin DOI de artículo)

- NASA-JPL (2026). *NISAR Science Users' Handbook*, 2.ª edición.
  https://science.nasa.gov/mission/nisar/nisar-handbook/ (la página indica el DOI
  10.48577/jpl.UD4HV3). *Para qué:* estructura del GCOV, frecuencias A y B, máscara.
- NASA Earthdata (2026). GEDI Version 3 data products released (períodos 04/2019–03/2023
  y 04/2024–07/2025).
  https://www.earthdata.nasa.gov/data/alerts-outages/gedi-version-3-data-products-released
  *Para qué:* el receso de GEDI y el cambio de versión.
- ASF DAAC. NISAR instrument (banda L global; banda S principalmente sobre India).
  https://nisar-docs.asf.alaska.edu/instrument
- CONAE (2026). SAOCOM: manual de usuario del catálogo. https://catalogos.conae.gov.ar
- ESA BIOMASS: liberación progresiva de los productos (nivel 1 desde el 12/12/2025; nivel 2A de altura del bosque, FH, y de suelo cancelado, GN, el 30/06/2026; ver `LEEME_CCI_BIOMASS_sitios.md`).
  https://lcluc.umd.edu/announcements/esas-biomass-forest-carbon-maps-progressive-release
- Carta Internacional Espacio y Grandes Catástrofes. Activación 880: inundación en
  Entre Ríos, mayo de 2024.
  https://disasterscharter.org/es/activations/flood-in-argentina-activation-880-
- Santoro, M. y Cartus, O. (2026). ESA Biomass Climate Change Initiative (Biomass_cci),
  v7.0. NERC EDS CEDA. https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903
  *Para qué:* la biomasa aérea y su desvío (2010 a 2024) del contexto del sitio.
- ESA Biomass Climate Change Initiative (2025). Product Validation and Intercomparison
  Report (PVIR), versión 7.0.
  https://climate.esa.int/documents/3356/Product_Validation_Intercomparison_Report_PVIR_V7.0.pdf
  *Para qué:* la referencia para contrastar dos hipótesis del Tp1: la caída de 2010 a 2015
  (cambio de sensor) y la biomasa asignada a las herbáceas inundables.
- Proyecto MapBiomas Argentina. Colección 3 de los mapas anuales de cobertura y uso del
  suelo (1985–2025) y Colección 1 de MapBiomas Fuego. https://argentina.mapbiomas.org
  (CC BY 4.0). *Para qué:* el contexto del sitio (paso 9) y las clases del paso 6b.
- Microsoft Planetary Computer (catálogo STAC, sin cuenta):
  https://planetarycomputer.microsoft.com
- Corado, L. y Godinho, S. (2026). GEDI-Pipeline QGIS Plugin, versión 0.1.
  https://github.com/leonelluiscorado/gedi-pipeline-qgis-plugin
  *Para qué:* bajar y recortar un producto GEDI por vez, incluido el L1B con las
  formas de onda crudas, para revisar las huellas dudosas del paso 5.
