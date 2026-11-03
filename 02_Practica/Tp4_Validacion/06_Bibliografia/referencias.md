# Tp4 — Referencias

## Referencia de método

- Olofsson, P., Foody, G. M., Herold, M., Stehman, S. V., Woodcock, C. E. y Wulder, M. A. (2014). Good practices for estimating area and assessing accuracy of land change. *Remote Sensing of Environment*, 148, 42–57. https://doi.org/10.1016/j.rse.2014.02.015
  **Referencia de método.** Es el estimador de `Tp4_03` (ecuaciones de área, exactitudes y varianzas), la ecuación 13 del tamaño de muestra de `Tp4_02`, el diseño de respuesta (protocolo de la Tabla 3 del Desarrollo) y el ejemplo numérico que reproduce `--autoprueba`.
- Olofsson, P., Arévalo, P., Espejo, A. B., Green, C., Lindquist, E., McRoberts, R. E. y Sanz, M. J. (2020). Mitigating the effects of omission errors on area and area change estimates. *Remote Sensing of Environment*, 236, 111492. https://doi.org/10.1016/j.rse.2019.111492
  Trata el caso de la plantación del ensayo: una omisión en estratos grandes infla el área estimada de una clase chica y su intervalo. Se cita en las respuestas 4 y 6 y en la pregunta 11.
- Stehman, S. V. (2014). Estimating area and map accuracy for stratified random sampling when the strata are different from the map classes. *International Journal of Remote Sensing*, 35, 4923–4939. https://doi.org/10.1080/01431161.2014.930207
  **Referencia de método** de `Tp4_06_muestra_comun.py`: una sola muestra para varias variantes (paso 9) y otra equivalencia de MapBiomas sobre la misma muestra (paso 10).

## Artículos 2020–2026 (de la presentación del curso)

- Tang, X., Bratley, K. H., Cho, K., Bullock, E. L., Olofsson, P. y Woodcock, C. E. (2023). Near real-time monitoring of tropical forest disturbance by fusion of Landsat, Sentinel-2, and Sentinel-1 data. *Remote Sensing of Environment*, 294, 113626. https://doi.org/10.1016/j.rse.2023.113626
  Fusiona tres sensores para detectar disturbios del bosque; uno de sus autores es el de la referencia de método. Sirve como ejemplo de un producto de fusión cuya exactitud se informa con una referencia independiente, que es lo que pide la tabla de `Tp4_04`. Se cita en el paso 9 del Desarrollo.
- Zhang, R., Yang, Y., Li, Z., Li, P. y Wang, H. (2026). Optical and SAR image fusion: a review of theories, methods, and applications. *Remote Sensing*, 18(1), 73. https://doi.org/10.3390/rs18010073
  Revisión de la fusión óptico–SAR; útil para situar los niveles de fusión (píxel, rasgo, decisión) cuyas variantes valida el Tp4. Se cita en la respuesta 6 del Desarrollo.

## Libro abierto (de la presentación del curso)

- Cardille, J. A., Crowley, M. A., Saah, D. y Clinton, N. E. (eds.) (2024). *Cloud-Based Remote Sensing with Google Earth Engine: Fundamentals and Applications*. Springer. CC BY 4.0. https://doi.org/10.1007/978-3-031-26588-4
  Capítulo 20 (fusión de clasificaciones): cómo combinar mapas y por qué el producto combinado se valida como cualquier otro.

## Fuentes de datos

- JRC Global Surface Water, ocurrencia de agua 1984–2021. https://global-surface-water.appspot.com (leída del Microsoft Planetary Computer, colección `jrc-gsw`: https://planetarycomputer.microsoft.com).
- Pekel, J.-F., Cottam, A., Gorelick, N. y Belward, A. S. (2016). High-resolution mapping of global surface water and its long-term changes. *Nature*, 540, 418–422. https://doi.org/10.1038/nature20584 (origen de JRC Global Surface Water; DOI verificado).
- MapBiomas Argentina, colección de bosques 2023, y Colección 3 de los mapas anuales de cobertura y uso del suelo, cobertura 2025 (descripción de la leyenda en el sitio). https://argentina.mapbiomas.org (CC BY 4.0)
- Santoro, M. y Cartus, O. (2026). ESA Biomass Climate Change Initiative (Biomass_cci), v7.0, AGB 2024. NERC EDS CEDA. https://doi.org/10.5285/6429d1aafe1e43b9b414e4a5a7f8b903
- ESA, BIOMASS banda P (435 MHz), L1B DGM del 22/07/2026. ESA MAAP, https://catalog.maap.eo.esa.int
- INPE/CAST, CBERS-4A WPM L4 del 15/07/2026 fusionado a 2 m (CC BY 4.0). https://data.inpe.br/stac/browser/collections/CB4A-WPM-L4-DN-1
- CONAE, Pléiades Neo 2023, 0,3 m, servicio WMS de las localidades del curso.
- ESA Copernicus, Sentinel-2B MSI L2A del 04/11/2023 (fondo de los mapas del Desarrollo). https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a
- NASA/NSIDC, ICESat-2 ATL08 versión 007 (control de la máscara de copas). https://nsidc.org/data/atl08
- Esri World Imagery (teselas XYZ) y Esri World Imagery Wayback (versiones históricas): https://livingatlas.arcgis.com/wayback
- Carta Internacional Espacio y Grandes Catástrofes, activación 880: inundación en Entre Ríos, mayo de 2024. https://disasterscharter.org/es/activations/flood-in-argentina-activation-880-
