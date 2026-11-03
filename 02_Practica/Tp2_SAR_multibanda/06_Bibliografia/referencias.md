# Tp2 — Referencias

Artículos de sinergia y fusión 2020–2026 con DOI verificado (los de la presentación 01
del curso), las referencias de método (la original de cada método, aunque sea anterior
a 2020) y las de las misiones y productos que usa el práctico. Cada una con una línea
de para qué sirve en este práctico. Belenguer-Plomer et al. (2021), sobre áreas quemadas,
pasó al Tp5, donde es directamente pertinente.

## Referencia de método

- Small, D. (2011). Flattening gamma: radiometric terrain correction for SAR imagery.
  *IEEE Transactions on Geoscience and Remote Sensing*, 49(8), 3081–3093.
  https://doi.org/10.1109/TGRS.2011.2120616
  *Referencia de método.* Es el algoritmo del nodo `Terrain-Flattening`: por qué se
  calibra a β⁰ y se normaliza por el área iluminada para obtener γ⁰.

- Lee, J.-S. (1981). Refined filtering of image noise using local statistics.
  *Computer Graphics and Image Processing*, 15(4), 380–389.
  *Referencia de método.* El filtro Refined Lee del paso 2: promedia dentro de ventanas
  orientadas según los bordes. (Anterior a 2020: es la referencia original del método.)

- Lopes, A., Nezry, E., Touzi, R. y Laur, H. (1993). Structure detection and statistical
  adaptive speckle filtering in SAR images. *International Journal of Remote Sensing*,
  14(9), 1735–1758. https://doi.org/10.1080/01431169308953999
  *Referencia de método.* El filtro Gamma Map del paso 2: estimador de máximo a posteriori
  que supone una escena con distribución gamma y conserva mejor los reflectores puntuales.
  (Anterior a 2020: es la referencia original del método.)

- Schmidt, K., Tous Ramon, N. y Schwerdt, M. (2018). Radiometric accuracy and stability
  of Sentinel-1A determined using point targets. *International Journal of Microwave and
  Wireless Technologies*, 10(5–6), 538–546. https://doi.org/10.1017/S1759078718000016
  *Referencia de método.* La exactitud radiométrica absoluta especificada para Sentinel-1
  (1 dB, 3σ), que fundamenta el umbral de 1 dB del control en zona estable (paso 8).

- ESA. Sentinel-1 SAR Technical Guide, SAR instrument performance: exactitud
  radiométrica absoluta de 1,0 dB (3σ).
  https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-1-sar/sar-instrument/performance
  *Para qué:* el umbral de 1 dB del paso 8.

- Chapman, B. (2019). NISAR calibration and validation. 25.ª reunión del Kyoto & Carbon
  Initiative (JAXA). Calibración radiométrica: menos de 0,9 dB en la copolarizada y
  1,2 dB en la cruzada.
  https://www.eorc.jaxa.jp/ALOS/en/kyoto/feb2019_kc25/pdf/2-11_KC25_NISAR-CalVal_Chapman.pdf
  *Para qué:* el umbral de 1 dB del paso 8, para NISAR.

## Misiones y productos

- Quegan, S., Le Toan, T., Chave, J. et al. (2019). The European Space Agency BIOMASS
  mission: measuring forest above-ground biomass from space. *Remote Sensing of
  Environment*, 227, 44–60. https://doi.org/10.1016/j.rse.2019.03.032
  *Para qué:* la misión BIOMASS en banda P (paso 4) y por qué la onda de 69 cm responde a
  troncos y ramas gruesas.

- Santoro, M. y Cartus, O. (2026). ESA Biomass Climate Change Initiative (Biomass_cci):
  global datasets of forest above-ground biomass, v7.0. NERC EDS CEDA.
  https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903
  *Para qué:* el producto CCI Biomass del paso 9, una estimación hecha con radar C y L que
  no es independiente del radar del curso.

- Brown, C. F., Kazmierski, M. R., Pasquarella, V. J., Rucklidge, W. J., Samsikova, M.
  et al. (2025). AlphaEarth Foundations: an embedding field model for accurate and
  efficient global mapping from sparse label data. arXiv:2507.22291.
  https://arxiv.org/abs/2507.22291
  *Para qué:* los embeddings anuales de la ampliación del paso 9 (no se evalúa).

## Artículos

- Zhang, R., Yang, Y., Li, Z., Li, P. y Wang, H. (2026). Optical and SAR image
  fusion: a review of theories, methods, and applications. *Remote Sensing*, 18(1),
  73. https://doi.org/10.3390/rs18010073
  *Para qué:* el marco de lo que exige cualquier fusión posterior (Tp3 en adelante):
  misma grilla, corregistro medido y fechas compatibles; respalda la respuesta 8.

- Silva, C. A., Duncanson, L., Hancock, S. et al. (2021). Fusing simulated GEDI,
  ICESat-2 and NISAR data for regional aboveground biomass mapping. *Remote Sensing of
  Environment*, 253, 112234. https://doi.org/10.1016/j.rse.2020.112234
  *Para qué:* por qué la banda L de NISAR responde a la estructura leñosa (volumen) que
  la banda C no alcanza; útil para la pregunta 5.

- Konapala, G., Kumar, S. V. y Ahmad, S. K. (2021). Exploring Sentinel-1 and
  Sentinel-2 diversity for flood inundation mapping using deep learning. *ISPRS
  Journal of Photogrammetry and Remote Sensing*, 180, 163–173.
  https://doi.org/10.1016/j.isprsjprs.2021.08.016
  *Para qué:* qué aportan VV y VH de Sentinel-1 a la separación del agua; respalda la
  lectura del negro especular y del agua rizada en el RGB.

## Manuales y fuentes de datos

- NASA-JPL (2026). *NISAR Science Users' Handbook*, 2.ª edición.
  https://science.nasa.gov/mission/nisar/nisar-handbook/ (la página indica el DOI
  10.48577/jpl.UD4HV3). *Para qué:* estructura del GCOV, términos HHHH y HVHV,
  frecuencias A y B, máscara.
- ASF DAAC. NISAR instrument. https://nisar-docs.asf.alaska.edu/instrument
- CONAE (2026). SAOCOM: manual de usuario del catálogo. https://catalogos.conae.gov.ar
- Microsoft Planetary Computer, colección `sentinel-1-rtc`:
  https://planetarycomputer.microsoft.com
- ESA. SNAP (Sentinel Application Platform): https://step.esa.int
