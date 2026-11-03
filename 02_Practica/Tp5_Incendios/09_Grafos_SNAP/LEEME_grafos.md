# 09_Grafos_SNAP — Tp5

El único paso en SNAP del Tp5 es llevar el SAOCOM-1A StripMap del archivo del curso a γ⁰. **YA VIENE HECHO**: lo hizo el docente con `00_COMUN\procesar_saocom.py`, que escribe un grafo por escena en `02_Subsets_SNAP_QGIS\SAOCOM_gamma0\Grafos_SNAP` (se abre en SNAP con `Tools > GraphBuilder > Load`). La entrada son los recortes SLC del sitio (`02_Subsets_SNAP_QGIS\SNAP_DIMAP\A1_DELTA_QUEMAS_SAOCOM_L_<fecha>_<QP|DP>.dim`); los productos, sus GeoTIFF y los RGB están en `02_Subsets_SNAP_QGIS\SAOCOM_gamma0` (ver la guía, paso 0). El grafo general, para una escena completa, es el del Tp2: `Tp2_SAR_multibanda\09_Grafos_SNAP\Tp2_SAOCOM_StripMap_a_gamma0.xml`.

## La cadena de operadores (la de `procesar_saocom.py`)

| Nodo | Operador | Parámetros que importan | Por qué |
|---|---|---|---|
| 1 | `Read` | el recorte SLC del sitio (`.dim`) | ya está recortado: no hace falta `Subset` |
| 2 | `Calibration` | `outputSigmaBand=true`, `outputBetaBand=false`, todas las polarizaciones | los SLC de CONAE ya vienen calibrados: el píxel al cuadrado es σ⁰ |
| 3 | `Multilook` | 2 vistas en rango, píxel cuadrado en el terreno, salida en intensidad | reduce el speckle y pasa de complejo a potencia |
| 4 | `Speckle-Filter` | Refined Lee | la misma cadena que el Sentinel-1 procesado desde el crudo |
| 5 | `Terrain-Correction` | Copernicus 30 m, 10 m, `EPSG:32721`, con el ángulo de incidencia sobre el elipsoide | proyecta a la grilla del curso |
| 6 | `Write` | BEAM-DIMAP | conserva todos los metadatos |

El γ⁰ = σ⁰/cos θ (θ, ángulo de incidencia sobre el elipsoide) lo agrega `procesar_saocom.py` como banda virtual del `.dim` y como GeoTIFF. **No se usa el Terrain-Flattening de SNAP con SAOCOM**: da entre 5 y 10 dB menos que el mosaico ALOS-2 y que NISAR. En las islas, llanas, σ⁰/cos θ equivale al γ⁰ aplanado.

Nunca se llama γ⁰ a un σ⁰: el nombre de cada banda dice qué es (`Sigma0_*` en disco, `Gamma0_*` virtual).

## Para mirar en SNAP

Los RGB copolarizada–cruzada–cociente ya están hechos (`SAOCOM_gamma0\RGB_copol_cruzada_cociente`): HH–HV–HH/HV en los cuadripolares del 21/07 y del 25/10, VV–VH–VV/VH en el doble polarización del 07/09. Para armarlo en SNAP: `Window > Open RGB Image Window`, con R = `Gamma0_HH_db`, G = `Gamma0_HV_db` y B = `HH_HV_cociente_db` (bandas virtuales del `.dim`). El pajonal y el monte se ven verdes o amarillos (volumen); el agua calma, negra.
