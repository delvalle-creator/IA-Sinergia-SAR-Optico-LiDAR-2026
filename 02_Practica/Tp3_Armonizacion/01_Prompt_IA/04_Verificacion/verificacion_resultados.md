# Verificación del Tp3 — protocolo

Primero se verifica **lo que la IA entregó** (los scripts), después **los resultados**
sobre `A2_IBICUY` y el caso de control de `F_BOVRIL`. Al final, la tabla de los tres
requisitos de la fusión, que es el producto central del práctico.

## A. Controles sobre los scripts

| N.º | Qué se controla | Cómo | Se acepta si… |
|---|---|---|---|
| A1 | Radar agregado en lineal | Leer `Tp3_01` | Usa `leer_en_grilla(..., "average")` sobre la pila lineal |
| A2 | SCL por moda | Leer `Tp3_01` | La SCL se lee con `"mode"` |
| A3 | Desplazamiento +1000 de Sentinel-2 | Leer `s2_reflectancia()` | Resta 1000 si la línea de base es ≥ 04.00 |
| A4 | Corregistro sobre bordes | Leer `bordes()` en `Tp3_02` | Sobel sobre dB suavizado (radar) o reflectancia (óptico) |
| A5 | Criterio de rigidez | Leer `Tp3_02` | Dos niveles: píxel (módulo y dispersión < 0,5 px, rango < 1 px) y rasgo o decisión (< 1 px, rango < 2 px); ventanas por mediana ± 3 MAD |
| A6 | LiDAR no rasterizado | Leer `Tp3_03` | Extrae el cubo en cada huella (círculo GEDI, rectángulo ATL08); no interpola; marca `plausible` |
| A7 | Alturas elipsoidales rotuladas | Columnas de la tabla de huellas | Las alturas de terreno llevan `_elips` |

## B. Controles sobre los resultados

1. **Misma grilla.** En QGIS, Propiedades > Información del cubo. *Se acepta si* el CRS
   es EPSG:32721, el píxel es el pedido (20 m) y todas las capas están en el mismo
   archivo.
2. **Unidades.** *Se acepta si* en `<SITIO>_cubo_20m_bandas.csv` cada capa tiene unidad
   (`gamma0 lineal`, `sigma0 lineal`, `reflectancia 0-1`, `m sobre EGM2008`) y las
   reflectancias están entre 0 y 1 (`Analysis` o Propiedades > Histograma).
3. **Máscara de nubes común.** *Se acepta si* las seis capas ópticas tienen el mismo
   `pixeles_validos_%`.
4. **Fechas documentadas.** *Se acepta si* `<SITIO>_diferencias_de_fecha.csv` tiene un
   renglón por cada par de entradas (sensor, fecha), con las fechas de NISAR por
   separado, y ninguna banda queda sin fecha (si queda, se corrige el `--extra` del Tp2).
5. **Corregistro L frente a S (NISAR).** *Se acepta si* CUMPLE para fusión de píxel. Si no hay banda S para
   el Delta, el control se hace entre NISAR L y Sentinel-1 RTC.
6. **Corregistro óptico frente a radar.** *Se acepta si* CUMPLE, o si el NO CUMPLE tiene
   una causa escrita (agua que cambió entre fechas, ventanas con pocas costas, nubes).
7. **Caso de control: NovaSAR 47974 frente a Sentinel-2 en Bovril.** *Se acepta si* la
   medición da **NO CUMPLE, no rígido**: hay que moverla unos 90 m al oeste
   (dx ≈ −4,6 px) y unos 480 m al sur (dy ≈ +24 px), con un dy que baja de unos +28 px en
   la fila norte de ventanas a +18 px en la sur (rango de unos 10 px). La componente
   este-oeste coincide con la presentación 02 (unos 80 m al oeste); la norte-sur, no
   (allí, 20 m al norte). Después de `--desplazamiento -92 -484` la mediana baja a menos
   de 1 px (0,25 px) pero la dispersión sigue en unos 4 px y el rango en unos 10 px:
   sigue sin cumplir. Si da CUMPLE antes
   de corregir, la medición está mal.
8. **Signo.** *Se acepta si* el grupo escribe cada desplazamiento con la regla única
   («hay que mover la capa X m al este; la imagen está corrida X m al oeste») y lo
   contrasta con el caso de control.
9. **Huellas en el cubo.** *Se acepta si* toda huella de la tabla tiene `n_<capa>` > 0
   en al menos una capa de radar, y las huellas caen sobre tierra o vegetación al
   verlas en QGIS.
10. **Fechas LiDAR.** *Se acepta si* el grupo informa la mediana de `dias_<capa>` de la
    bitácora de `Tp3_03` para la capa de radar y la óptica, y dice si es compatible con
    el fenómeno.
11. **Alturas.** *Se acepta si* nadie compara `elev_lowestmode_elips` con `MDE_GLO30_m`
    sin convertir a EGM2008 (ondulación del geoide de 16,9 m en Ibicuy).
12. **Plausibilidad.** *Se acepta si* la tabla de huellas tiene la columna `plausible`
    y ninguna cifra del grupo usa huellas con `plausible = 0`.

## Cifras que deben aparecer en las bitácoras

- `Tp3_01`: grilla (CRS, píxel, columnas × filas); por capa de radar, fecha y % con
  dato; teselas Sentinel-2 y % de píxeles útiles; diferencias de fecha por par.
- `Tp3_02` (una por par, `Tp3_02_<SITIO>_<mov>_vs_<ref>.log`): ventanas válidas y usadas;
  dx, dy, corr_antes y corr_despues por ventana; mediana en píxeles y metros; dispersión;
  veredicto; si no es rígido, dy por fila y dx por columna de ventanas.
- `Tp3_02`: además, módulo, dispersión, rango, la frase de signo y el veredicto de dos
  niveles; las cifras con todas las ventanas.
- `Tp3_03`: huellas válidas por producto; forma de extracción; huellas con valores;
  plausibles y no plausibles por motivo; píxeles por huella; mediana de días LiDAR-capa.

## Tabla de los tres requisitos (el producto central)

Una fila por par de capas que el grupo piensa combinar en los Tp5 a Tp10.

| Par (ref / mov) | Misma grilla | Corregistro: mediana (px) / dispersión (px) / veredicto | Diferencia de fechas (días) | ¿Compatible para este fenómeno? | Nivel de fusión posible |
|---|---|---|---|---|---|
| OPT_S2_B08 / L_NISAR_gamma0_HV_… | | | | | |
| L_NISAR_gamma0_HH_… / S_NISAR_gamma0_HH_… | | | | | |
| OPT_S2_B08 / C_S1_gamma0_VV | | | | | |
| OPT_S2_B08 / C_SNAP_gamma0_VV | | | | | |
| OPT_S2_B08 / S_NovaSAR_sigma0_HH (Bovril) | | | | | |
| OPT_S2_B08 / P_BIOMASS_gamma0_VH | | | | | |
| GEDI rh98 / L_NISAR_gamma0_HV_… | (huella) | (error de geolocalización de GEDI, unos 10 m, no medido) | | | |
| Pregunta 12: OPT_S2_B08 / S_NISAR_gamma0_HH_20260930 | | | | | |
| Pregunta 12: C_SNAP_gamma0_VV / P_BIOMASS_gamma0_HH | | | | | |

## Tabla para el grupo

| Control | Valor obtenido | Archivo | ¿Cumple? | Observación |
|---|---|---|---|---|
| 1. CRS y píxel del cubo | | | | |
| 3. % útil de las capas ópticas | | | | |
| 5. L frente a S: mediana y dispersión (px) | | | | |
| 6. Óptico frente a L: mediana y dispersión (px) | | | | |
| 7. NovaSAR frente a S2: dx, dy (m) | | | | |
| 9. Huellas GEDI / ATL08 con valores del cubo | | | | |
| 10. Mediana de días LiDAR-radar / LiDAR-óptico | | | | |
