# Tp8 — La textura de Haralick en SNAP

El único paso del Tp8 en SNAP es una comparación, y se hace con los menús; el
grafo `Tp8_GLCM_S.xml` (al final) hace lo mismo con `gpt`. Sirve para contrastar el coeficiente de
variación del script con la textura de Haralick, que es la que suele aparecer en
los artículos.

## La cadena

| # | Operador (`gpt`) | Menú de SNAP | Qué hace y por qué |
|---|---|---|---|
| 1 | (abrir) | `File > Open Product...` → `02_Subsets_SNAP_QGIS/F_textura_S_C_10m.tif` | Trae σ⁰ de NovaSAR y γ⁰ de Sentinel-1 ya en la grilla común y corregidos |
| 2 | `LinearToFromdB` | `Raster > Data Conversion > Linear to/from dB` sobre `S_NovaSAR_sigma0_HH` (y `C_S1_gamma0_VV`) | Crea una banda virtual en dB. La GLCM cuantiza niveles de gris: en lineal, la cola larga del radar concentra casi todo en pocos niveles |
| 3 | `GLCM` | `Raster > Image Analysis > Texture Analysis > Grey Level Co-occurrence Matrix` | Calcula `Contrast`, `Dissimilarity`, `Homogeneity`, `Energy`, `Entropy`, `GLCMMean`, `GLCMVariance`, `GLCMCorrelation` |
| 4 | (exportar) | `File > Export > GeoTIFF` | Para abrir en QGIS junto al CV del script |

Verifique el nombre de cada operador en su versión con `gpt -h`.

## Parámetros que conviene fijar y anotar

- **Ventana:** 5 × 5, la misma que `--ventana 5` del script, para que la escala
  espacial sea comparable.
- **Cuantizador y niveles:** anote los que use (por ejemplo, cuantizador
  probabilístico y 32 niveles). Cambian los valores absolutos.
- **Desplazamiento:** 1 píxel. Con más, se miden relaciones entre píxeles más
  separados.
- **Dirección:** todas (promedio), salvo que quiera ver la orientación de surcos.

## Qué comparar

En tres lotes de distinta clase de frecuencia (nunca, 1–2 meses, ≥ 6 meses),
mida `Contrast` y `Homogeneity` y el `S_CV_HH` del script. Si los dos métodos
ordenan los lotes igual, la textura es robusta al método. Si no, dígalo y diga
cuál interpreta mejor: el CV tiene una referencia física directa (el speckle de
una vista da 1); la GLCM depende de la cuantización.

## El grafo del desarrollo

`Tp8_GLCM_S.xml` (23/10/2026) hace la cadena con `gpt`: lee `F_textura_S_C_10m.tif`, crea
`S_NovaSAR_sigma0_HH_db` (BandMaths, 10·log10), calcula la GLCM (5 × 5, todas las direcciones,
cuantizador probabilístico, 32 niveles, desplazamiento 1; sólo `Contrast` y `Homogeneity`) y
escribe `05_Resultados/02_Rasters/F_GLCM_S_HH_dB_5x5.tif`. Se corre desde esta carpeta:

```
"C:\Program Files\esa-snap11\bin\gpt.exe" Tp8_GLCM_S.xml
```

SNAP 11 lee los nombres de banda del GeoTIFF (`S_NovaSAR_sigma0_HH`), no `band_1`.
