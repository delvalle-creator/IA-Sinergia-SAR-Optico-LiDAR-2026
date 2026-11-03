# Verificación de los resultados del Tp9

## A. Controles sobre lo que entregó la IA

| # | Control | Criterio de aceptación |
|---|---|---|
| 1 | ALOS-1 2011 | Sólo HH; ninguna capa `L_ALOS1_2011_HV` salvo que se pase una FBD |
| 2 | ALOS-2 mosaico | DN² · 10^(−8,3), el cuadrado antes de remuestrear |
| 3 | NISAR | Frecuencia A y máscara del producto aplicada |
| 4 | Unidades | Pila en lineal; cocientes en lineal expresados en dB |
| 5 | Calibración cruzada | Mediana de la diferencia en dB en zona estable; corrección multiplicativa en lineal |
| 6 | Fechas GEDI | Sólo huellas a menos de 730 días de cada capa |
| 7 | Δrh98 | Control independiente por defecto, no rasgo |
| 8 | Exactitud | La fuera de bolsa rotulada OPTIMISTA |

## B. Controles sobre los resultados

| # | Control | Criterio de aceptación | Dónde se lee |
|---|---|---|---|
| 1 | Cobertura de cada capa | Se informa; NovaSAR 50896 cerca del 51 % | `Tp9_01_pila.log` |
| 2 | Zona estable | Clases usadas y píxeles informados; la clase 3 confirmada por el grupo o `--solo_urbano` | `Tp9_01_pila.log` |
| 3 | Desfase entre sensores de banda L | Informado por zona (monte, ciudad, las dos) y corregido; el residuo después de corregir, medido en cuadrados no usados para calibrar, se informa | `C_calibracion_cruzada.csv` (`residuo_p75_abs_dB`) |
| 4 | Umbral de la variante L | El valor absoluto de `--u_hv` supera el residuo (p75) del monte; si no, se declara que la variante L puede marcar calibración como pérdida | comparación de 3 y la orden usada |
| 5 | Huellas por capa | ≥ 20 huellas cercanas en fecha; ALOS-1 2011 «no se evalúa» es lo esperado | `C_sensibilidad_a_la_altura.csv` |
| 6 | Saturación | Se dice en qué clase de altura se aplana cada curva; lo esperado por la física es que C se aplane antes que L, y si no ocurre se explica (fechas, huellas, estructura del Espinal) | `C_curvas_de_respuesta.png` |
| 7 | Degradación | Número de celdas con ≥ 2 huellas por período y candidatas informados | `Tp9_02_sinergia.log`, `C_delta_rh98_por_celda.csv` |
| 8 | Cultivos no son pérdida | Lotes cosechados verificados quedan en clase 4 del mapa multisensor | QGIS |
| 9 | Control con GEDI | Δrh98 mediano por clase leído contando celdas, no píxeles; con menos de 3 m de caída no confirma ni descarta | `C_control_gedi_por_clase.csv` (columna `celdas`) |
| 10 | Exactitud con muestra independiente | IC 95 % de las tres variantes | Tp4 (etiquetado fuera del horario si no se llega en clase) |

## Cifras que deben aparecer en la bitácora

- % de dato de cada capa de la pila y número de capas.
- Zona estable (clases y píxeles) y desfase de cada producto de banda L.
- Huellas GEDI válidas en la pila y su rango de fechas; ρ y rango de curva por capa.
- Huellas por período, celdas con huellas en ambos y candidatas a degradación.
- Exactitud fuera de bolsa (OPTIMISTA), importancia de rasgos, hectáreas por clase.
- Δrh98 por clase del mapa.

**Hallazgos del curso que se deben reproducir:** ALOS-1 FBS 2011 es sólo HH;
NovaSAR 50896 cubre el 51 % de `C_FEDERAL`; GEDI no tiene datos entre el
17/03/2023 y el 26/04/2024.

## Tabla para el grupo

| Capa | % con dato | Huellas GEDI usadas | ρ Spearman | Rango de la curva | ¿Satura? |
|---|---|---|---|---|---|
| L_ALOS1_2011_HH | | | | | |
| L_ALOS2_2021_HH | | | | | |
| L_ALOS2_2021_HV | | | | | |
| L_NISAR_2026_HH | | | | | |
| L_NISAR_2026_HV | | | | | |
| C_S1_2021_VH | | | | | |
| C_S1_2026_VH | | | | | |
| S_NovaSAR_2023_sigma0_HH | | | | | |
| O_NDVI_2026 | | | | | |
| P_BIOMASS_Gamma0_VH (Federal, 12/08/2026) | | | | | |

| Calibración cruzada | Desfase monte / ciudad (dB) | Residuo p75 (dB) | ¿Interpretable un cambio de 1,5 dB? |
|---|---|---|---|
| L_ALOS1_2011_HH respecto de L_ALOS2_2021_HH | | | |
| L_NISAR_2026_HH respecto de L_ALOS2_2021_HH | | | |
| L_NISAR_2026_HV respecto de L_ALOS2_2021_HV | | | |

| Mapa | Pérdida | Degradación | Monte estable | No bosque estable |
|---|---|---|---|---|
| Hectáreas (conteo de píxeles) | | | | |
| Δrh98 mediano (m) | | | | |
| Exactitud fuera de bolsa (OPTIMISTA) | | | | |
