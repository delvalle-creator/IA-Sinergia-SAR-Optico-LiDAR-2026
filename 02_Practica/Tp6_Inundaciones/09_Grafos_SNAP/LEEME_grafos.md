# 09_Grafos_SNAP — Tp6

Los scripts del Tp6 **no necesitan SNAP**: usan el Sentinel-1 RTC que ya viene corregido del Planetary Computer, y la banda L SAOCOM ya viene procesada.

SNAP sí aparece en el práctico de dos maneras: (1) el Sentinel-1 del 04/11/2023 procesado por el docente desde el GRDH sin procesar (`02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo`), con su grafo en `Grafos_SNAP` y su comparación con el RTC en `LEEME_S1_crudo.md`; se abre en SNAP para ver la cadena de operadores y comparar; (2) el NovaSAR del 13/09/2023 en `SNAP_DIMAP`, para mirar sus metadatos.

La banda L ya viene procesada: SAOCOM-1B del 10/10/2023 (seco) y del 11/11/2023 (crecida), TOPSAR Narrow A cuadripolar, misma órbita, en `02_Subsets_SNAP_QGIS\SAOCOM_gamma0` (ver su LEEME). Esta carpeta explica cómo se hizo, para poder rehacerlo con otro par de fechas.

## La cadena de operadores

La corre `00_COMUN\procesar_saocom_topsar.py`; el grafo de cada producto está en `02_Subsets_SNAP_QGIS\SAOCOM_gamma0\Grafos_SNAP` (SNAP: `Tools > Graph Builder > Load`). Antes del grafo, el programa une las ráfagas y las subfranjas del TOPSAR (el `TOPSAR-Deburst` de SNAP sólo sirve para Sentinel-1).

| Nodo | Operador | Parámetros que importan | Por qué |
|---|---|---|---|
| 1 | `Read` | producto L1A unido | SNAP 14 |
| 2 | `Subset` | región de B_CONCORDIA con 0,25° de margen | recortar antes de lo costoso |
| 3 | `Calibration` | σ⁰ | los L1A de CONAE ya vienen calibrados: DN² = σ⁰ |
| 4 | `Multilook` | píxel cuadrado sobre el terreno | menos speckle |
| 5 | `Speckle-Filter` | Refined Lee | menos speckle conservando bordes |
| 6 | `Terrain-Correction` | Copernicus DEM 30 m, 20 m, `EPSG:32721`, guardar el ángulo de incidencia sobre el elipsoide | grilla del curso |
| 7 | `Subset` y `Write` | sitio exacto, BEAM-DIMAP | conserva los metadatos |

γ⁰ = σ⁰ / cos θ, con θ el ángulo de incidencia sobre el elipsoide. No se usa `Terrain-Flattening`: con SAOCOM, en SNAP 14, da valores 5 a 10 dB por debajo de NISAR y del mosaico ALOS-2. En el relieve llano de Concordia la diferencia con un γ⁰ aplanado es chica.

Las dos escenas (evento y seca) tienen que ser de la **misma geometría** (misma órbita y modo): si no, el cociente mide la diferencia de geometría y no el agua. El 10/10 y el 11/11/2023 cumplen; el 31/10 y el 08/11/2023 son de otro haz (TNB) y cubren la mitad del sitio.

## Los archivos para Tp6_02

`--l_evento ..\02_Subsets_SNAP_QGIS\SAOCOM_gamma0\QGIS_GeoTIFF\B_CONCORDIA_SAOCOM_L_20231111_QP_gamma0_Gamma0_HH.tif` y `--l_referencia` con el `..._20231010_...`. Son γ⁰ lineal (no dB), una banda.

## Para mirar en SNAP

RGB copolarizada–cruzada–cociente (HH–HV–HH/HV) con `Window > Open RGB Image Window`: el monte inundado se ve magenta o blanco (doble rebote), el agua abierta, negra.
