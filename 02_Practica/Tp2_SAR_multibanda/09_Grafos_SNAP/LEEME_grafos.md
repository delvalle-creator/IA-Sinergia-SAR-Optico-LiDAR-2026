# Los grafos de SNAP del Tp2

Tres grafos del Graph Builder (`Tools > GraphBuilder > Load`). Los tres llevan una
escena SAR a **γ⁰ lineal, en EPSG:32721 a 10 m, en BEAM-DIMAP**. Ninguno filtra el
speckle ni convierte a dB: esas dos operaciones se hacen después, en la interfaz, como
pasos aparte (ver la guía, pasos 2 y 3).

Los grafos no tienen variables `${...}`: están hechos para abrirse en el Graph Builder,
completar las pestañas Read, Subset y Write, y correr con **Run**. Para correrlos desde
la línea de órdenes con `gpt` habría que agregar esas variables.

| Grafo | Producto de entrada | Marca en el Tp2 |
|---|---|---|
| `Tp2_S1_GRD_a_gamma0.xml` | Sentinel-1 IW GRD (banda C, VV + VH) | **EN SNAP**: lo corre el grupo |
| `Tp2_S1_SLC_a_gamma0.xml` | Sentinel-1 IW SLC (banda C, con fase) | Queda para ver cómo se hace (no hay un SLC procesado del sitio) |
| `Tp2_SAOCOM_StripMap_a_gamma0.xml` | SAOCOM-1 L1A Stripmap (banda L, QP o DP) | Queda para ver cómo se hace. Los SAOCOM del Delta **YA VIENEN HECHOS** con `00_COMUN\procesar_saocom.py`, en `Tp5_Incendios\02_Subsets_SNAP_QGIS\SAOCOM_gamma0` |

---

## 1. `Tp2_S1_GRD_a_gamma0.xml` — Sentinel-1 GRD a γ⁰

Cadena de nodos:

```
Read → Apply-Orbit-File → ThermalNoiseRemoval → Calibration → Subset
     → Terrain-Flattening → Terrain-Correction → Write
```

| Nodo | Parámetros | Por qué |
|---|---|---|
| `Read` | archivo vacío: se elige en la pestaña | La escena GRD (`.zip` o `manifest.safe`) |
| `Apply-Orbit-File` | `Sentinel Precise (Auto Download)`, `polyDegree` 3, `continueOnFail` = true | La órbita precisa mejora la geolocalización. Si no hay red, sigue con la órbita de la anotación: **hay que declararlo** |
| `ThermalNoiseRemoval` | `removeThermalNoise` = true, `reIntroduceThermalNoise` = false, todas las polarizaciones | El ruido térmico levanta artificialmente la cruzada en las zonas oscuras (agua) |
| `Calibration` | `outputBetaBand` = true; σ⁰, γ⁰, dB y complejo desactivados; polarizaciones `VV,VH`; archivo auxiliar `Latest Auxiliary File` | El Terrain Flattening necesita **β⁰** de entrada |
| `Subset` | `geoRegion` vacío (se completa con el polígono del sitio y un margen), copia de metadatos, sin submuestreo | Procesar sólo el sitio ahorra tiempo y disco; el margen evita bordes sin dato |
| `Terrain-Flattening` | DEM `Copernicus 30m Global DEM`, remuestreo bilineal, `additionalOverlap` 0,1, `oversamplingMultiple` 1,0, sin imagen simulada | Normaliza por el área realmente iluminada: β⁰ → **γ⁰** (Small, 2011) |
| `Terrain-Correction` | DEM Copernicus 30 m; imagen y DEM bilineal; **10 m**; **EPSG:32721**; `alignToStandardGrid` = true con origen **5, 5**; `nodataValueAtSea` = false; guarda la banda de origen, el **ángulo de incidencia local** y la **máscara de inversión por relieve y sombra**; sin normalización radiométrica adicional | Proyecta al mapa (Range Doppler). El origen 5, 5 hace que los bordes de píxel caigan en múltiplos de 10 m, como la grilla del curso. No se normaliza de nuevo: ya lo hizo el Terrain Flattening |
| `Write` | **BEAM-DIMAP** | Conserva todos los metadatos originales; el GeoTIFF los perdería |

Bandas de salida: `Gamma0_VH`, `Gamma0_VV` (lineales), `localIncidenceAngle` y la
máscara de inversión y sombra. El ángulo local es **diagnóstico**, no una segunda
corrección.

Lo que este grafo no hace: no quita el ruido de borde de los GRD (operador
`Remove-GRD-Border-Noise`, que no está en la cadena); en el sitio, recortado lejos del
borde de la escena, no suele importar, pero si el sitio cae en el borde de la pasada se
ven franjas oscuras y hay que declararlo.

---

## 2. `Tp2_S1_SLC_a_gamma0.xml` — Sentinel-1 SLC a γ⁰

Cadena de nodos:

```
Read → Apply-Orbit-File → ThermalNoiseRemoval → Calibration → TOPSAR-Deburst
     → Subset → Multilook → Terrain-Flattening → Terrain-Correction → Write
```

| Nodo | Parámetros | Por qué |
|---|---|---|
| `Read` | copia de metadatos, sin opciones avanzadas | La escena SLC |
| `Apply-Orbit-File` | igual que en el GRD | — |
| `ThermalNoiseRemoval` | quita el ruido, no lo reintroduce, `clipNegativeValues` = true | En SLC, después de restar el ruido pueden quedar intensidades negativas: se recortan |
| `Calibration` | β⁰, sin σ⁰ ni γ⁰, sin dB, sin complejo; todas las polarizaciones | La calibración va **antes** del deburst, sobre las ráfagas originales |
| `TOPSAR-Deburst` | todas las polarizaciones | Une las ráfagas del modo TOPS en una imagen continua |
| `Subset` | región geográfica vacía (se completa), copia de metadatos | Recorte del sitio después del deburst |
| `Multilook` | 2 vistas en rango, 1 en acimut, píxel cuadrado en el terreno, salida en intensidad | Reduce el speckle y lleva el píxel a un tamaño cercano al de la grilla antes de la corrección del terreno |
| `Terrain-Flattening` | Copernicus 30 m, bilineal, `nodataValueAtSea` = true, sin σ⁰ de salida | β⁰ → γ⁰ |
| `Terrain-Correction` | igual que en el GRD (10 m, EPSG:32721, origen 5, 5), guarda el ángulo local y la máscara de inversión y sombra | — |
| `Write` | BEAM-DIMAP | — |

Observaciones al leerlo:

- El grafo **no** tiene `TOPSAR-Split`: procesa las tres subfranjas y todas las
  ráfagas. Por eso tarda y por eso viene hecho.
- Con `grSquarePixel` = true, SNAP calcula las vistas en acimut a partir de las de
  rango para que el píxel quede cuadrado en el terreno; el valor de acimut escrito en
  el XML es orientativo.
- La salida es intensidad: la fase se pierde. Para interferometría (Tp7, Tp10) se usan
  otros grafos.

---

## 3. `Tp2_SAOCOM_StripMap_a_gamma0.xml` — SAOCOM-1 L1A a γ⁰

Cadena de nodos:

```
Read → Calibration → Subset → Multilook → Terrain-Flattening → Terrain-Correction → Write
```

| Nodo | Parámetros | Por qué |
|---|---|---|
| `Read` | la carpeta del producto (con su `.xemt`); SNAP 9 o posterior lee el formato | — |
| `Calibration` | β⁰, sin σ⁰ ni γ⁰, sin dB, sin complejo; **no fija polarizaciones** | Procesa las que traiga el producto: cuatro en cuadripolarizado (HH, HV, VH, VV), dos en dual |
| `Subset` | región geográfica vacía (se completa), copia de metadatos | Recorte antes del Terrain Flattening, como en Sentinel-1 |
| `Multilook` | 2 × 2 vistas, píxel cuadrado, intensidad | Reduce el speckle antes de la corrección |
| `Terrain-Flattening` | Copernicus 30 m, bilineal, superposición 0,1 | β⁰ → γ⁰ |
| `Terrain-Correction` | 10 m, EPSG:32721, origen 5, 5, ángulo local y máscara de inversión y sombra | — |
| `Write` | BEAM-DIMAP | — |

No hay nodo de órbita: el producto SAOCOM trae su órbita en los metadatos.

**Pasada ascendente frente a descendente.** El comentario del grafo lo advierte: dos
productos de pasada opuesta se procesan con este mismo grafo, pero sus salidas **no se
apilan ni se promedian**. La geometría de mirada es opuesta y γ⁰ en las laderas (y en
los bordes de los albardones del Delta) no es comparable. La pasada de cada escena del
archivo del curso está en el `.xemt` (`OrbitDirection`) y la lista `Tp1_02` en
`inventario_local.csv`, columna `pasada`. El comentario se refiere a las escenas
SAOCOM-1A del archivo del curso (Delta, julio a octubre de 2020, Stripmap QP y DP):
para apilarlas o promediarlas deben ser de la misma pasada; una escena de la pasada
opuesta se usa por separado y se declara.

---

## Lo que tienen en común, y lo que hay que completar a mano

- **Subset:** la región está vacía. En la pestaña Subset, **Geographic Coordinates**,
  pegue el polígono WKT del sitio con un margen de 0,02°. Para `A2_IBICUY`:
  `POLYGON((-59.32 -33.87, -59.08 -33.87, -59.08 -33.63, -59.32 -33.63, -59.32 -33.87))`.
- **Write:** nombre y carpeta (`Tp2_SAR_multibanda\02_Subsets_SNAP_QGIS`).
- **Copernicus DEM:** SNAP lo baja solo la primera vez; sin red, debe estar en la
  carpeta auxiliar de SNAP.
- **Nombre interno:** el atributo `id` de cada grafo termina en `_UTM21S`
  (`S1_GRD_a_gamma0_TF_UTM21S`, `S1_SLC_a_gamma0_TF_UTM21S`,
  `SAOCOM_L1A_a_gamma0_TF_UTM21S`). La proyección que se aplica es la del nodo
  `Terrain-Correction`, **EPSG:32721 (UTM 21 S)**: verifíquela en esa pestaña.
- **Bandas de salida de los tres:** γ⁰ lineal por polarización, `localIncidenceAngle`
  y la máscara de inversión por relieve y sombra.
- **Después de cada grafo:** speckle (`Radar > Speckle Filtering > Single Product
  Speckle Filter`, Refined Lee o Lee Sigma), bandas virtuales en dB (`Raster > Data
  Conversion > Linear to/from dB`), `File > Save Product` y exportación de una banda
  lineal por GeoTIFF (`File > Export > GeoTIFF`, botón Subset).
- Guarde el grafo con sus parámetros completos (`File > Save Graph`) junto al producto:
  es la constancia de lo que se hizo.
