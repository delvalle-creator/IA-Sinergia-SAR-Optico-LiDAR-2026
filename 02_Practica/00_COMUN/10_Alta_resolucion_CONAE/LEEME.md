# Pléiades y Pléiades Neo de CONAE en las localidades del curso

Imágenes de muy alta resolución de CONAE (proyecto Impactar), **sólo para mirar y digitalizar**: son mosaicos RGB color real ya armados, sin infrarrojo ni reflectancia, servidos por internet (WMS). CONAE no ofrece la descarga de los datos por este servicio; los datos multiespectrales requieren un convenio con CONAE (atencion.usuario@conae.gov.ar). Cada capa cubre el casco urbano de la localidad; la fecha exacta no está publicada, sólo el año.

**Cómo usarlas en QGIS** (hace falta internet):

1. Arrastre el archivo `.xml` de la localidad a la ventana de QGIS (o `Capa > Añadir capa > Añadir capa ráster…` / `Layer > Add Layer > Add Raster Layer…`). QGIS la abre como una capa ráster común.
2. O cargue la conexión: `Capa > Añadir capa > Añadir capa WMS/WMTS…` (`Add WMS/WMTS Layer…`), botón `Cargar` (`Load`), archivo `CONAE_Impactar_conexion_WMS_QGIS.xml` de `00_COMUN\10_Alta_resolucion_CONAE`; `Conectar` y elija la capa por su nombre.

Están en EPSG:3857 (el servicio no ofrece la UTM 21 S); QGIS las reproyecta al vuelo sobre la grilla del curso.

| Archivo | Localidad | Satélite | Capa del servicio |
|---|---|---|---|
| `Concordia_2023_Pleiades_CONAE.xml` | Concordia y General Roca, 2023 | Pléiades Neo | `Localidades:EntreRios_Concordia_2023` |
| `GranParana_2022_Pleiades_CONAE.xml` | Gran Paraná (Paraná, Oro Verde, San Benito, Colonia Avellaneda, Sauce Montrull, Sauce Pinto), 2022 | Pléiades | `Localidades:EntreRios_GranParana_2022` |
| `Diamante_2022_Pleiades_CONAE.xml` | Diamante, 2022 | Pléiades | `Localidades:EntreRios_Diamante_2022` |
| `Federal_2022_Pleiades_CONAE.xml` | Federal, 2022 | Pléiades | `Localidades:EntreRios_Federal_2022` |
| `LaPaz_2022_Pleiades_CONAE.xml` | La Paz, 2022 | Pléiades | `Localidades:EntreRios_LaPaz_2022` |
| `Villaguay_2023_Pleiades_CONAE.xml` | Villaguay, 2023 | Pléiades Neo | `Localidades:EntreRios_Villaguay_2023` |
| `Ibicuy_2023_Pleiades_CONAE.xml` | Ibicuy, 2023 | Pléiades | `Localidades:EntreRios_Ibicuy_2023` |
| `Victoria_2022_Pleiades_CONAE.xml` | Victoria, 2022 | Pléiades | `Localidades:EntreRios_Victoria_2022` |
| `VillaParanacito_2022_Pleiades_CONAE.xml` | Villa Paranacito, 2022 | Pléiades | `Localidades:EntreRios_VillaParanacito_2022` |

Bovril no tiene capa. Sitios por práctico: Tp1: Concordia y General Roca; Tp2: Ibicuy; Tp3: Ibicuy; Tp6: Concordia y General Roca; Tp7: Diamante, Gran Paraná (Paraná); Tp9: Federal, La Paz, Villaguay; Tp10: Concordia y General Roca, Gran Paraná (Paraná), Diamante.

## Imágenes de muestra (`_prueba`)

Los nueve PNG de `_prueba` son capturas de esas capas WMS, una por localidad, para ver qué cubre cada una sin conexión. **Las imágenes son propiedad de CONAE y están sujetas a su licencia** (Pléiades y Pléiades Neo © Airbus Defence and Space, distribuidas por CONAE). Se incluyen sólo con fines didácticos y no se rigen por la licencia del curso: no pueden redistribuirse ni usarse con otros fines sin la autorización de CONAE.

Fuente: CONAE, proyecto Impactar. Mosaicos RGB color real de Pléiades (0,5 m) y Pléiades Neo (0,3 m), Airbus Defence and Space, Pléiades y Pléiades Neo, 2022-2023. Servicio WMS/WMTS: https://geotematico01.conae.gov.ar/geoserver/wms; catálogo: https://catalogos.conae.gov.ar/catalogo/catalogoGeoServiciosOGC.html; visor: https://geoportal.conae.gov.ar/mapstore/visor-alta.html#/viewer/openlayers/geoservicios_impactar
