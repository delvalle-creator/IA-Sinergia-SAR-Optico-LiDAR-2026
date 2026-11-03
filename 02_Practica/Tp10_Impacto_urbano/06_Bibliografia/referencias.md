# Tp10 — Referencias

Sólo se listan referencias con DOI verificado de 2020–2026 (las de la presentación del curso) y las referencias de método anteriores a 2020 que el código usa, rotuladas como tales. Cada una dice para qué sirve en este práctico.

## Sinergia y fusión

- Zhang, R., Yang, Y., Li, Z., Li, P. y Wang, H. (2026). Optical and SAR image fusion: a review of theories, methods, and applications. *Remote Sensing*, 18(1), 73. https://doi.org/10.3390/rs18010073
  **Para qué:** bases físicas de la combinación óptico–SAR (estructura frente a material) y niveles de fusión. Es el marco de los pasos 6 y 7.

- Li, Y. y Xiao, X. (2025). Deep learning-based fusion of optical, radar, and LiDAR data for advancing land monitoring. *Sensors*, 25(16), 4991. https://doi.org/10.3390/s25164991
  **Para qué:** limitaciones de cada sensor y por qué un clasificador multisensor necesita las mismas capas en todos los píxeles (la razón de las versiones `con_S` y `sin_S`).

- Cardille, J. A., Crowley, M. A., Saah, D. y Clinton, N. E. (eds.) (2024). *Cloud-Based Remote Sensing with Google Earth Engine: Fundamentals and Applications*. Springer. CC BY 4.0. https://doi.org/10.1007/978-3-031-26588-4
  **Para qué:** capítulo 20 (fusión de clasificaciones, la idea de la fusión de decisión del paso 7) y capítulo 39 (SAR).

## Interferometría

- Mondini, A. C., Guzzetti, F., Chang, K.-T., Monserrat, O., Martha, T. R. y Manconi, A. (2021). Landslide failures detection and mapping using Synthetic Aperture Radar: past, present and future. *Earth-Science Reviews*, 216, 103574. https://doi.org/10.1016/j.earscirev.2021.103574
  **Para qué:** (contexto; para series de subsidencia, ver Morishita et al., 2020) revisión del uso del SAR (amplitud, coherencia e interferometría) para detectar movimientos del terreno. Se escribió para deslizamientos; aquí sirve de introducción a los límites de la interferometría por pérdida de coherencia, que deciden qué píxeles tienen velocidad en el paso 10.

## Interferometría, series temporales (2020–2026)

- Morishita, Y., Lazecky, M., Wright, T. J., Weiss, J. R., Elliott, J. R. y Hooper, A. (2020). LiCSBAS: an open-source InSAR time series analysis package integrated with the LiCSAR automated Sentinel-1 InSAR processor. *Remote Sensing*, 12(3), 424. https://doi.org/10.3390/rs12030424
  **Para qué:** cómo se arma una serie InSAR de Sentinel-1 con inversión de la red de pares, control de cierre de bucles y descarte de errores de desenrollado; es lo que el apilado de tasas del paso 10 no hace, y la referencia para el control de saltos que agrega Tp10_05.

## Biomasa y contexto (Tabla 2 y Figura 4 del Desarrollo)

- Santoro, M. y Cartus, O. (2026). *ESA Biomass Climate Change Initiative (Biomass_cci): Global datasets of forest above-ground biomass*, v7.0. NERC EDS Centre for Environmental Data Analysis. https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903
  **Para qué:** la biomasa aérea de 2024 y su desvío por clase de MapBiomas (contexto del sitio).

## Banda L

- NASA-JPL (2026). *NISAR Science Users' Handbook*, 2.ª edición. https://science.nasa.gov/mission/nisar/nisar-handbook/ (la página indica el DOI 10.48577/jpl.UD4HV3)
  **Para qué:** el producto GCOV (γ⁰, frecuencias A y B, máscara) y las aplicaciones urbanas y de deformación de la banda L.

## Referencias de método (anteriores a 2020, usadas por el código)

- **Referencia de método.** Franceschetti, G., Iodice, A. y Riccio, D. (2002). A canonical problem in electromagnetic backscattering from buildings. *IEEE Transactions on Geoscience and Remote Sensing*, 40(8), 1787–1801. https://doi.org/10.1109/TGRS.2002.802459
  **Para qué:** el modelo del diedro pared–suelo: por qué el retorno urbano depende de la orientación de las paredes respecto de la dirección de vuelo y por qué la HH y la VV responden distinto cerca del ángulo de Brewster (pasos 2 y 3).

- **Referencia de método.** Stehman, S. V. (2014). Estimating area and map accuracy for stratified random sampling when the strata are different from the map classes. *International Journal of Remote Sensing*, 35(13), 4923–4939. https://doi.org/10.1080/01431161.2014.930207
  **Para qué:** evaluar con una misma muestra un mapa distinto del que definió los estratos: el kNN con embeddings (ampliación del docente) y la comparación de variantes en la huella de NovaSAR (Tp10_06, paso 11).

- **Referencia de método.** Waldner, F., Jacques, D. C. y Löw, F. (2017). The impact of training class proportions on binary cropland classification. *Remote Sensing Letters*, 8(12), 1122–1131. https://doi.org/10.1080/2150704X.2017.1362124
  **Para qué:** por qué el entrenamiento del Random Forest tiene que estar en proporción al paisaje (paso 4): con el mismo número de ejemplos por clase, la clase chica (aquí, el urbano) se sobreestima.

- **Referencia de método.** Olofsson, P., Foody, G. M., Herold, M., Stehman, S. V., Woodcock, C. E. y Wulder, M. A. (2014). Good practices for estimating area and assessing accuracy of land change. *Remote Sensing of Environment*, 148, 42–57. https://doi.org/10.1016/j.rse.2014.02.015
  **Para qué:** el muestreo estratificado y el estimador de exactitud y área con IC del 95 % con que se validan las variantes (Tp4).

- **Referencia de método.** Small, D. (2011). Flattening gamma: radiometric terrain correction for SAR imagery. *IEEE Transactions on Geoscience and Remote Sensing*, 49(8), 3081–3093. https://doi.org/10.1109/TGRS.2011.2120616
  **Para qué:** la diferencia entre σ⁰ y γ⁰; por qué NovaSAR (σ⁰) no se compara en valor absoluto con Sentinel-1 RTC y NISAR (γ⁰) (respuesta 10 del Desarrollo).

- **Referencia de método.** De Zan, F., Parizzi, A., Prats-Iraola, P. y López-Dekker, P. (2014). A SAR interferometric model for soil moisture. *IEEE Transactions on Geoscience and Remote Sensing*, 52(1), 418–425. https://doi.org/10.1109/TGRS.2013.2241069
  **Para qué:** la humedad del suelo cambia la fase interferométrica; es una de las dos explicaciones de las manchas rurales de velocidad del paso 10 (ver NOTAS; Figura 16 y respuesta 9 del Desarrollo).

## Interferometría, sesgo de fase (2020–2026)

- Ansari, H., De Zan, F. y Parizzi, A. (2021). Study of systematic bias in measuring surface deformation with SAR interferometry. *IEEE Transactions on Geoscience and Remote Sensing*, 59(2), 1285–1301. https://doi.org/10.1109/TGRS.2020.3003421
  **Para qué:** el apilado de pares cortos arrastra un sesgo sistemático de fase (humedad, vegetación); explica por qué una «velocidad» de pares de 12 y 24 días puede no ser deformación (paso 10, Figura 16 y respuesta 9 del Desarrollo).

## Software

- Hogenson, K., Kristenson, H., Kennedy, J., Johnston, A., Rine, J., Logan, T., Zhu, J., Williams, F., Herrmann, J., Smale, J. y Meyer, F. (2020). *Hybrid Pluggable Processing Pipeline (HyP3): A cloud-native infrastructure for generic processing of SAR data* [software]. Zenodo. https://doi.org/10.5281/zenodo.4646138
  **Para qué:** la cita que pide ASF para los interferogramas INSAR_GAMMA del paso 8.

## Fuentes de datos

- ESA – Copernicus. Sentinel-1 RTC y Sentinel-2 L2A, a través de Microsoft Planetary Computer: https://planetarycomputer.microsoft.com
- SSTL – CSIRO. NovaSAR-1, escena 47942 (13/09/2023), archivo del curso: https://data.novasar.csiro.au
- NASA – ISRO. NISAR L2 GCOV, ASF DAAC: https://search.asf.alaska.edu
- ASF DAAC. HyP3, interferogramas INSAR_GAMMA: https://hyp3-docs.asf.alaska.edu
- Proyecto MapBiomas Argentina. Colección 3 de los Mapas Anuales de Cobertura y Uso del Suelo (1985–2025) y productos de pérdida de vegetación, licencia CC BY 4.0: https://argentina.mapbiomas.org (leyenda oficial: https://argentina.mapbiomas.org/wp-content/uploads/sites/8/2026/09/ARG-LegendCode-Col3.pdf)
- Google y Google DeepMind. AlphaEarth Foundations Satellite Embedding dataset, año 2025 (CC BY 4.0); copia en Source Cooperative: https://source.coop/tge-labs/aef
- ESA. BIOMASS banda P, L1B DGM y L2A (altura de bosque), ESA MAAP: https://catalog.maap.eo.esa.int
- USGS / NASA. Landsat 8 OLI/TIRS, Colección 2 Nivel 2 (temperatura de superficie), Microsoft Planetary Computer: https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2
- INPE / CAST. CBERS-4A cámara WPM, L4, licencia CC BY 4.0: https://data.inpe.br/stac/browser/collections/CB4A-WPM-L4-DN-1
- CONAE. SAOCOM-1B L1A SLC, catálogo SAOCOM: https://catalog.saocom.conae.gov.ar
