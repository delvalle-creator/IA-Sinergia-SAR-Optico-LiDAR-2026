# Tp7 — Las cadenas InSAR de SNAP

En esta carpeta no hay grafos `.xml`: la interferometría del Tp7 se hace con los
menús de SNAP, paso a paso, para ver qué produce cada operador. Aquí está la
cadena completa de cada sensor, con el menú y el nombre del operador para la
línea de órdenes (`gpt`). Los nombres de operador corresponden a SNAP 9–10;
**verifique el nombre exacto en su versión con `gpt -h`** antes de armar un grafo.

En clase se usa sólo la parte final de la cadena B (desenrollado). La cadena A
queda como referencia: en clase la banda C viene de HyP3.

## A. Sentinel-1 IW SLC (TOPS), banda C

| # | Operador (`gpt`) | Menú de SNAP | Qué hace y por qué |
|---|---|---|---|
| 1 | `TOPSAR-Split` | `Radar > Sentinel-1 TOPS > S-1 TOPS Split` | Se queda con la subfranja (IW1, IW2 o IW3) y las ráfagas que cubren Diamante, y una polarización (VV). Achica todo lo que sigue |
| 2 | `Apply-Orbit-File` | `Radar > Apply Orbit File` | Órbitas precisas (POEORB). La fase depende de la posición del satélite al centímetro |
| 3 | `Back-Geocoding` | `Radar > Coregistration > S1 TOPS Coregistration > S-1 Back Geocoding` | Corregistra la segunda escena sobre la primera usando las órbitas y un MDE (Copernicus 30 m o SRTM 1 s) |
| 4 | `Enhanced-Spectral-Diversity` | `Radar > Coregistration > S1 TOPS Coregistration > S-1 Enhanced Spectral Diversity` | Corrige el error residual en azimut entre ráfagas; sin él aparecen saltos de fase en los bordes de ráfaga |
| 5 | `Interferogram` | `Radar > Interferometric > Products > Interferogram Formation` | Producto complejo de las dos escenas: fase interferométrica y **coherencia** (marque `Output Coherence`); resta la fase de tierra plana |
| 6 | `TOPSAR-Deburst` | `Radar > Sentinel-1 TOPS > S-1 TOPS Deburst` | Une las ráfagas en una sola imagen continua |
| 7 | `TopoPhaseRemoval` | `Radar > Interferometric > Products > Topographic Phase Removal` | Resta la fase debida al relieve con el MDE. Lo que queda es deformación + atmósfera + ruido |
| 8 | `Multilook` (opcional) | `Radar > Multilooking` | Promedia píxeles para bajar el ruido de fase (por ejemplo 4 × 1) |
| 9 | `GoldsteinPhaseFiltering` | `Radar > Interferometric > Filtering > Goldstein Phase Filtering` | Filtra la fase para que el desenrollado tenga menos saltos |
| 10 | `SnaphuExport` | `Radar > Interferometric > Unwrapping > Snaphu Export` | Escribe la fase, la coherencia y `snaphu.conf` para el programa externo |
| — | `snaphu` (fuera de SNAP) | ventana de órdenes | Desenrolla. La orden está en la cabecera de `snaphu.conf` |
| 11 | `SnaphuImport` | `Radar > Interferometric > Unwrapping > Snaphu Import` | Vuelve a meter la fase desenrollada en el producto de SNAP (`Unw_Phase_*`) |
| 12 | `PhaseToDisplacement` | `Radar > Interferometric > Products > Phase to Displacement` | `d = −λ · fase / (4π)`, en metros en la línea de visión |
| 13 | `Terrain-Correction` | `Radar > Geometric > Terrain Correction > Range-Doppler Terrain Correction` | Ortorrectifica a EPSG:32721, 10 m |

## B. COSMO-SkyMed Himage (stripmap), banda X

| # | Operador (`gpt`) | Menú de SNAP | Qué hace y por qué |
|---|---|---|---|
| — | (no se usa `Apply-Orbit-File`) | — | SNAP no tiene archivos de órbita precisa para COSMO-SkyMed: se usan los vectores de estado que trae el producto |
| 1 | `CreateStack` | `Radar > Coregistration > Stack Tools > Create Stack` | Apila las dos escenas (15/10 maestra, 19/10 esclava) por órbita |
| 2 | `Cross-Correlation` | `Radar > Coregistration > Stack Tools > Cross-Correlation` | Busca puntos homólogos por correlación de la amplitud |
| 3 | `Warp` | `Radar > Coregistration > Stack Tools > Warp` | Remuestrea la esclava sobre la maestra con el polinomio ajustado. Los tres pasos juntos están en `Radar > Coregistration > Coregistration` |
| 4 | `Interferogram` | `Radar > Interferometric > Products > Interferogram Formation` | Fase y coherencia |
| 5 | `TopoPhaseRemoval` | `Radar > Interferometric > Products > Topographic Phase Removal` | Resta el relieve (MDE externo del IGN o Copernicus 30 m) |
| 6 | `GoldsteinPhaseFiltering` | `Radar > Interferometric > Filtering > Goldstein Phase Filtering` | Filtrado de fase. El producto del curso 2023 llega hasta aquí (`..._ifg_dinsar_flt`) y después a `Terrain-Correction` (`_TC`) |
| 7 | `Subset` | `Raster > Subset` | Recorte a la barranca y su entorno estable: SNAPHU tarda en proporción al tamaño |
| 8 | `SnaphuExport` | `Radar > Interferometric > Unwrapping > Snaphu Export` | `DEFO`, `MCF`; carpeta sin espacios ni tildes |
| — | `snaphu` (fuera de SNAP) | ventana de órdenes | La orden de la cabecera de `snaphu.conf` |
| 9 | `SnaphuImport` | `Radar > Interferometric > Unwrapping > Snaphu Import` | Producto envuelto + `UnwPhase_*.snaphu.hdr` |
| 10 | `PhaseToDisplacement` | `Radar > Interferometric > Products > Phase to Displacement` | Desplazamiento LOS con λ = 3,123 cm. **Deja sólo la banda `displacement`** |
| 11 | `Terrain-Correction` | `Radar > Geometric > Terrain Correction > Range-Doppler Terrain Correction` | Dos corridas con los mismos parámetros (EPSG:32721, 10 m): una sobre la salida del nodo 10 (`displacement`) y otra sobre el recorte del nodo 7 (`coh_*`), porque la coherencia no pasa por el nodo 10 |
| 12 | (exportar) | `File > Export > GeoTIFF` | Un GeoTIFF por banda para `Tp7_02` (`E1_X_los_disp.tif`, `E1_X_coh.tif`) |

## Lo que pasó en el curso 2023, y por qué se rehace

El producto `*_Stack_ifg_dinsar_flt_TC.dim` del curso 2023 pasó por los pasos 1 a
6 y por `Terrain-Correction`. La banda `Unw_Phase` existe, pero **vale cero en
todo el sitio**: se hizo el `Snaphu Export`, y el resultado de `snaphu` nunca se
importó. El `Terrain-Correction` se aplicó igual, y la banda vacía viajó como si
fuera dato. Por eso se rehace desde el paso 7 de la cadena B, sobre el producto
**sin `_TC`**.

## Para anotar en la entrega

Producto de partida, recorte (filas y columnas o coordenadas), parámetros de
Snaphu Export (modo, método inicial, teselas, procesadores), la orden de
`snaphu` tal como la corrió, el MDE de `Terrain-Correction` y el tamaño de píxel.
