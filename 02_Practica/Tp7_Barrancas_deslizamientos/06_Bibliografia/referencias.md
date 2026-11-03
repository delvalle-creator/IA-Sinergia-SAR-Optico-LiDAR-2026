# Tp7 — Referencias

Artículos 2020–2026 con DOI verificado. Cada uno, con una línea de para qué
sirve en este práctico.

## Artículos

- Mondini, A. C., Guzzetti, F., Chang, K.-T., Monserrat, O., Martha, T. R. y
  Manconi, A. (2021). Landslide failures detection and mapping using Synthetic
  Aperture Radar: past, present and future. *Earth-Science Reviews*, 216, 103574.
  https://doi.org/10.1016/j.earscirev.2021.103574
  — Para qué: el marco del práctico. Qué se puede detectar con InSAR y con
  amplitud, por qué la coherencia limita la detección en laderas vegetadas, y por
  qué la banda más larga conserva coherencia (pasos 1 a 3).

- Li, Y. y Xiao, X. (2025). Deep learning-based fusion of optical, radar, and
  LiDAR data for advancing land monitoring. *Sensors*, 25(16), 4991.
  https://doi.org/10.3390/s25164991
  — Para qué: las limitaciones de cada sensor cuando se combinan óptico, radar y
  LiDAR; sostiene por qué aquí se elige fusión de decisión y no de píxel.

- Zhang, R., Yang, Y., Li, Z., Li, P. y Wang, H. (2026). Optical and SAR image
  fusion: a review of theories, methods, and applications. *Remote Sensing*,
  18(1), 73. https://doi.org/10.3390/rs18010073
  — Para qué: los niveles de fusión (píxel, rasgo, decisión) y sus requisitos de
  corregistro, para justificar el nivel elegido en el paso 3.

## Fuente geológica del sitio

- Soffiantini, J. y Brunetto, E. (2023). Retroceso de la barranca del río Paraná
  en la costa de la ciudad de Diamante, Entre Ríos. Evidencias geomecánicas,
  controles y evolución temporal del proceso de remoción en masa. *Revista de la
  Asociación Geológica Argentina*, 80(2), 217–239.
  https://revista.geologica.org.ar/raga/article/view/1656 (también en
  https://ri.conicet.gov.ar/handle/11336/221864)
  — Para qué: la fuente geológica central del práctico: mecanismo (expansión
  lateral), fechas y magnitudes del movimiento (preguntas 9 y 10).

## Referencias de método

- Chen, C. W. y Zebker, H. A. (2002). Phase unwrapping for large SAR
  interferograms: statistical segmentation and generalized network models.
  *IEEE Transactions on Geoscience and Remote Sensing*, 40(8), 1709–1719.
  https://doi.org/10.1109/TGRS.2002.802453
  — Para qué: el método de SNAPHU con teselas y componentes conexas (paso 2).
- Hawker, L., Uhe, P., Paulo, L., Sosa, J., Savage, J., Sampson, C. y Neal, J.
  (2022). A 30 m global map of elevation with forests and buildings removed.
  *Environmental Research Letters*, 17(2), 024016.
  https://doi.org/10.1088/1748-9326/ac4d4f
  — Para qué: FABDEM, el MDE de terreno usado en el control con ICESat-2 (paso 6).
- Hugonnet, R., Brun, F., Berthier, E., Dehecq, A., Mannerfelt, E. S., Eckert, N.
  y Farinotti, D. (2022). Uncertainty analysis of digital elevation models by
  spatial inference from stable terrain. *IEEE Journal of Selected Topics in
  Applied Earth Observations and Remote Sensing*, 15, 6456–6472.
  https://doi.org/10.1109/JSTARS.2022.3188922
  — Para qué: el límite de detección de una diferencia de MDE con error
  heterocedástico y autocorrelacionado, medido en terreno estable (paso 5).

## Fuentes periodísticas

Sirven para fechar y ubicar; las magnitudes se toman de Soffiantini y Brunetto (2023).

- Entre Ríos Ahora (09/10/2018). La falla en las barrancas de Diamante tiene una
  extensión de 150 metros. https://entreriosahora.com/la-falla-en-las-barrancas-de-diamante-tiene-una-extension-de-150-metros/
- La Arena (16/10/2018). Geólogos llegan a Diamante para hacer un diagnóstico del
  desmoronamiento. https://www.laarena.com.ar/el-pais/2018-10-16-19-8-55-geologos-llegan-a-diamante-para-hacer-un-diagnostico-del-desmoronamiento
- Elonce (05/05/2025). Inminente desbarrancamiento en Diamante: confirman que
  evalúan reubicar al Cristo Pescador. https://www.elonce.com/sociedad/inminente-desbarrancamiento-en-diamante-confirman-que-evaluan-reubicar-al-cristo-pescador.htm
- BAE Negocios (09/10/2018). Una grieta amenaza con tragarse un pueblo. BAE Negocios. https://www.baenegocios.com/amp/Una-grieta-amenaza-con-tragarse-un-pueblo-20181009-0023/

## Fuentes de datos y documentación

- ASF DAAC. Catálogo de Sentinel-1 y servicio HyP3 (procesador GAMMA).
  https://search.asf.alaska.edu — búsqueda de pares y productos InSAR (paso 1).
- ESA – Copernicus. Sentinel-1 IW SLC. Distribución por ASF DAAC.
- ASI – COSMO-SkyMed, escenas Himage y Spotlight de Diamante, octubre de 2018.
  Archivo del curso TelSAR 2018 (CEREGEO).
- IGN. Modelo digital de elevaciones de 5 m (Diamante). Archivo del curso.
- ESA – Copernicus DEM GLO-30. Microsoft Planetary Computer:
  https://planetarycomputer.microsoft.com
- NASA – ICESat-2 ATL08 versión 007. NSIDC DAAC, NASA Earthdata.
