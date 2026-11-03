# Verificación del Tp2 — protocolo

Primero se verifica **lo que la IA entregó** (grafos y scripts), después **los
resultados** sobre `A2_IBICUY`. Un control que no se cumple se anota, se explica y se
declara.

## A. Controles sobre los grafos y los scripts

| N.º | Qué se controla | Cómo | Se acepta si… |
|---|---|---|---|
| A1 | Calibración a β⁰ antes del Terrain Flattening | Graph Builder, pestaña Calibration de cada grafo | `outputBetaBand` marcado; σ⁰, γ⁰ y dB desmarcados |
| A2 | Proyección y grilla | Pestaña Terrain-Correction | EPSG:32721, 10 m, alineación a grilla estándar con origen 5, 5 |
| A3 | Formato de salida | Pestaña Write | BEAM-DIMAP |
| A4 | Sin speckle ni dB en los grafos | Lista de nodos | No hay nodo `Speckle-Filter` ni `LinearToFromdB` |
| A5 | Promedios en lineal | Leer `media_lineal_db()` y `Tp2_03` | Se promedia la potencia y recién después se pasa a dB |
| A6 | NISAR con máscara y frecuencia A | Leer `nisar_gcov_en_grilla()` | Lee `frequencyA` y pone sin dato la máscara 0 y 255 |
| A7 | NovaSAR en σ⁰ y P sobre el elipsoide, declarados | Leer `Tp2_01` y `<SITIO>_pila_bandas.csv` | La banda se llama `S_NovaSAR_sigma0_HH` y su unidad es `sigma0 lineal`; la P dice `gamma0 elipsoidal lineal` |
| A8 | Fuente dentro del archivo | En QGIS, Propiedades > Metadatos de la pila, o `gdalinfo` | Existen las etiquetas `FUENTE`, `PROCESO`, `UNIDADES` |
| A9 | Máscara de inversión y sombra | Pestaña Terrain-Correction de los tres grafos | Guardan el ángulo de incidencia local y la máscara de inversión y sombra (`saveLayoverShadowMask` = true) en GRD, SLC y SAOCOM |

## B. Controles sobre los resultados

1. **Producto de SNAP.** *Se acepta si* el `.dim` tiene `Gamma0_VV` y `Gamma0_VH` en
   lineal (positivos, mayoría < 1), las bandas `_db` virtuales, CRS UTM 21 S y
   píxel de 10 m.
2. **Efecto del filtro.** En una zona homogénea, media y desvío de `Gamma0_VV` antes y
   después del filtro. *Se acepta si* la media lineal cambia poco y el desvío baja.
3. **Bandas de la pila.** *Se acepta si* toda banda de `<SITIO>_pila_bandas.csv` tiene
   `pixeles_validos_%` ≥ 20 y cada banda que no entró figura en la bitácora con
   `-> NO entra` y su porcentaje.
4. **Ausencia de valores imposibles.** Con `Analysis > Statistics` de SNAP o con
   `gdalinfo -stats`, *se acepta si* no hay valores de γ⁰ ≤ 0 en la pila (el borde de
   NISAR, que sin máscara daría alrededor de −133 dB, quedó sin dato).
5. **RGB.** *Se acepta si* hay un RGB por sensor dual, con el agua calma en negro y la
   línea «Fuente:» al pie del PNG.
6. **Cubiertas.** *Se acepta si* cada clase tiene al menos 3 polígonos y 200 píxeles
   (la bitácora de `Tp2_03` no muestra `AVISO`) y existe la clase `estable`.
7. **Coherencia física.** *Se acepta si* el agua calma tiene la media más baja en cada
   banda y el grupo explica, para cada excepción, la causa física probable.
8. **Contraste C frente a L.** *Se acepta si* el grupo informa el contraste monte −
   pajonal (o monte − agua) en la cruzada de C y de L, con la cifra y el archivo.
9. **Zona estable entre fechas NISAR.** *Se acepta si* cada par `CUMPLE`
   (|diferencia de medias| < 1 dB), o si cada `NO CUMPLE` tiene una causa propuesta.
10. **SNAP frente a RTC del mismo día.** `--a C_S1_gamma0_VV --b C_SNAP_gamma0_VV`.
    *Se acepta si* la diferencia de medias en la zona estable es < 1 dB. Entre dos
    procesadores del mismo día se repite con `--clase monte_o_bosque pajonal agua_calma --sufijo ...`
    (cubiertas homogéneas) y se informa el rango por polígono y el intervalo por
    remuestreo de polígonos que escribe `Tp2_04`. El desvío pixel
    a pixel debe ser menor con el producto filtrado que entre dos sin filtrar.
11. **Corregistro entre bandas de NISAR.** *Referencia:* el par L y S de NISAR
    (si existe la banda S) debe quedar por debajo de medio píxel. Se mide en el Tp3; aquí sólo se comprueba visualmente que los bordes del río coinciden.

## Cifras que deben aparecer en las bitácoras

- `Tp2_01`: grilla del sitio; por banda, % con dato y media en dB; bandas que no
  entraron; número de bandas de la pila.
- `Tp2_02`: por sensor, los límites 2–98 % en dB de R, G y B (con `--rango_fijo`, los mismos
  límites para todos: R −25 a 0, G −32 a −8, B 0 a 15 dB).
- `Tp2_03`: tabla de medias por clase y banda; rango de las medias por polígono; avisos de
  clases con menos de 200 píxeles.
- `Tp2_04`: por par, número de píxeles, diferencia de medias, desvío y veredicto, y debajo
  la diferencia de cada polígono y el intervalo del 95 % por remuestreo de polígonos.

## Tabla para el grupo

| Control | Valor obtenido | Archivo | ¿Cumple? | Observación |
|---|---|---|---|---|
| 1. Rango de `Gamma0_VV` lineal (mín / máx) | | | | |
| 2. Desvío de `Gamma0_VV` sin filtro / con filtro (zona homogénea) | | | | |
| 3. Bandas en la pila / bandas que no entraron | | | | |
| 6. Píxeles de la clase con menos píxeles | | | | |
| 7. Media del agua calma en C, S y L (dB) | | | | |
| 8. Contraste monte − pajonal en VH (C) y HV (L) (dB) | | | | |
| 9. Peor diferencia entre fechas NISAR en zona estable (dB) | | | | |
| 10. Diferencia SNAP − RTC en zona estable (dB) y desvío | | | | |
