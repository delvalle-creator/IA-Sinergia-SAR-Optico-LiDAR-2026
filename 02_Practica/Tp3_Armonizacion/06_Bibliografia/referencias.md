# Tp3 — Referencias

Artículos 2020–2026 con DOI verificado (los de la presentación 01 del curso). Cada uno
con una línea de para qué sirve en este práctico.

## Artículos

- Kacic, P., Thonfeld, F., Gessner, U. y Kuenzer, C. (2023). Forest structure
  characterization in Germany: novel products and analysis based on GEDI, Sentinel-1
  and Sentinel-2 data. *Remote Sensing*, 15(8), 1969.
  https://doi.org/10.3390/rs15081969
  *Para qué:* el uso típico de la tabla de huellas del paso 4: extraer Sentinel-1 y
  Sentinel-2 en las huellas GEDI para extender la estructura medida a un mapa continuo
  (fusión de rasgo). Citado en el paso 4 del Desarrollo.

- Lang, N., Jetz, W., Schindler, K. y Wegner, J. D. (2023). A high-resolution canopy
  height model of the Earth. *Nature Ecology & Evolution*, 7(11), 1778–1789.
  https://doi.org/10.1038/s41559-023-02206-6
  *Para qué:* GEDI como referencia de altura y el óptico como predictor; muestra por
  qué la diferencia de fechas y el tamaño de la huella frente al píxel importan.

- Li, Y. y Xiao, X. (2025). Deep learning-based fusion of optical, radar, and LiDAR
  data for advancing land monitoring. *Sensors*, 25(16), 4991.
  https://doi.org/10.3390/s25164991
  *Para qué:* revisión de las condiciones de la fusión óptico-radar-LiDAR (registro,
  resolución, sincronía) que este práctico mide.

- Zhang, R., Yang, Y., Li, Z., Li, P. y Wang, H. (2026). Optical and SAR image fusion:
  a review of theories, methods, and applications. *Remote Sensing*, 18(1), 73.
  https://doi.org/10.3390/rs18010073
  *Para qué:* el corregistro óptico-SAR como problema propio (sensores que no se
  parecen pixel a pixel) y los niveles de fusión.

- Silva, C. A., Duncanson, L., Hancock, S. et al. (2021). Fusing simulated GEDI,
  ICESat-2 and NISAR data for regional aboveground biomass mapping. *Remote Sensing of
  Environment*, 253, 112234. https://doi.org/10.1016/j.rse.2020.112234
  *Para qué:* GEDI, ICESat-2 y banda L juntos; por qué las huellas LiDAR se usan como
  muestra y no como superficie.

## CCI Biomass

- Santoro, M. y Cartus, O. (2026). ESA Biomass Climate Change Initiative (Biomass_cci):
  Global datasets of forest above-ground biomass, v7.0. NERC EDS Centre for Environmental
  Data Analysis. https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903
  *Para qué:* biomasa de 100 m de referencia en el paso 5 bis y en el contexto; no es
  independiente del radar (se estima con banda C y L).

## Referencias metodológicas

Trabajos que fundamentan los métodos (no son de sinergia ni de fusión, y por eso no
siguen la regla 2020–2026).

- Guizar-Sicairos, M., Thurman, S. T. y Fienup, J. R. (2008). Efficient subpixel image
  registration algorithms. *Optics Letters*, 33(2), 156–158.
  https://doi.org/10.1364/OL.33.000156
  *Para qué:* la correlación de fase con sobremuestreo que usa `Tp3_02`
  (`phase_cross_correlation` de scikit-image).
- Townshend, J. R. G., Justice, C. O., Gurney, C. y McManus, J. (1992). The impact of
  misregistration on change detection. *IEEE Transactions on Geoscience and Remote
  Sensing*, 30(5), 1054–1060. https://doi.org/10.1109/36.175340
  *Para qué:* por qué el umbral de 1 píxel es laxo para una fusión de píxel.
- Dai, X. y Khorram, S. (1998). The effects of image misregistration on the accuracy of
  remotely sensed change detection. *IEEE Transactions on Geoscience and Remote
  Sensing*, 36(5), 1566–1577. https://doi.org/10.1109/36.718860
  *Para qué:* la tolerancia de 0,2 a 0,5 píxel que define el nivel «fusión de píxel».
- Dubayah, R., Blair, J. B., Goetz, S. et al. (2020). The Global Ecosystem Dynamics
  Investigation: High-resolution laser ranging of the Earth's forests and topography.
  *Science of Remote Sensing*, 1, 100002. https://doi.org/10.1016/j.srs.2020.100002
  *Para qué:* la huella de 25 m de GEDI y su error de geolocalización horizontal.
- Quegan, S., Le Toan, T., Chave, J. et al. (2019). The European Space Agency BIOMASS
  mission: Measuring forest above-ground biomass from space. *Remote Sensing of
  Environment*, 227, 44–60. https://doi.org/10.1016/j.rse.2019.03.032
  *Para qué:* la banda P de 435 MHz y su ancho de banda de 6 MHz (resolución de unos 50 a
  60 m en rango de terreno).
- Brown, C. F., Kazmierski, M. R., Pasquarella, V. J. et al. (2025). AlphaEarth
  Foundations: An embedding field model for accurate and efficient global mapping from
  sparse label data. arXiv:2507.22291. https://arxiv.org/abs/2507.22291
  *Para qué:* qué son los embeddings anuales que se usan en la Ampliación del Desarrollo.

## Fuentes de datos y documentación

- Pekel, J.-F., Cottam, A., Gorelick, N. y Belward, A. S. (2016). High-resolution mapping
  of global surface water and its long-term changes. *Nature*, 540(7633), 418–422.
  https://doi.org/10.1038/nature20584
  *Para qué:* la ocurrencia de agua de JRC Global Surface Water (1984–2021, leída del
  Microsoft Planetary Computer) que, junto con MapBiomas, enmascara el agua en la altura
  FH de BIOMASS (Figuras 32 y 33 del Desarrollo).

- NASA Earthdata (2026). GEDI Version 3 data products released (períodos 04/2019–03/2023
  y 04/2024–07/2025).
  https://www.earthdata.nasa.gov/data/alerts-outages/gedi-version-3-data-products-released
- NASA-JPL (2026). *NISAR Science Users' Handbook*, 2.ª edición.
  https://science.nasa.gov/mission/nisar/nisar-handbook/ (la página indica el DOI
  10.48577/jpl.UD4HV3).
- Microsoft Planetary Computer, colecciones `sentinel-2-l2a` y `cop-dem-glo-30`:
  https://planetarycomputer.microsoft.com
- scikit-image, `phase_cross_correlation` (documentación de la función usada en
  `Tp3_02`): https://scikit-image.org

## GEDI L2B y L4A (cobertura, PAI y biomasa por huella)

- Cotrina-Sanchez, A., Torresani, M. y Corado, L. (2026). GEDIMetrics: a QGIS plugin for accessing and integrating multi-product GEDI spaceborne LiDAR data. *Earth Science Informatics*, 19, 205. https://doi.org/10.1007/s12145-026-02254-z
  *Para qué:* el complemento de QGIS que baja, filtra, recorta y une por shot_number los productos GEDI L2A, L2B, L4A y L4C; el desarrollo hace la misma unión con `00_COMUN/09_Herramientas/des_gedi_l2ab_l4a.py` sobre los gránulos del disco, con los filtros del curso (sus filtros por defecto, con sensibilidad 0,90, no son los del curso).
- NASA. GEDI L2B V003 (cobertura del dosel, PAI y FHD por huella). LP DAAC, NASA Earthdata. https://www.earthdata.nasa.gov/data/catalog/lpcloud-gedi02-b-003
- Dubayah, R. O., Armston, J., Kellner, J. R., Duncanson, L., Healey, S. P., Patterson, P. L., Hancock, S., Tang, H., Bruening, J. M., Hofton, M. A., Blair, J. B. y Luthcke, S. B. (2026). GEDI L4A Footprint Level Aboveground Biomass Density, Version 3. ORNL DAAC, Oak Ridge, Tennessee, EE. UU. https://doi.org/10.3334/ORNLDAAC/2508
