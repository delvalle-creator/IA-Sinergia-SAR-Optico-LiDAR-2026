# Tp2 — Preprocesamiento SAR multibanda

**Pregunta:** ¿cómo llevar escenas en bandas C, S, L y P (y X donde la haya) a γ⁰
comparable, y qué ve cada banda sobre la misma cubierta?

**Sitio de práctica:** A2 · Delta, Ibicuy (`A2_IBICUY`, humedales), bbox WGS 84
(oeste, sur, este, norte) = −59,30, −33,85, −59,10, −33,65 (ubicación aproximada,
revisada en el Tp1). Alternativa con más superficie: `DELTA_NISAR` (−60,16, −33,83,
−58,72, −32,96), la de los NISAR GCOV del Delta de 2026.

**Horario:** lunes, 14 a 18 h. **Núcleo de la tarde:** pasos 0 a 8 y preguntas 1 a 9, 11 y 12.
**Para profundizar:** el SAOCOM cuadripolar del paso 8, el paso 9 (pregunta 10) y la ampliación
AlphaEarth (no se evalúa).

## Para qué sirve este práctico

Cada radar llega con su calibración, su normalización y su geometría. Si se los pone
uno al lado del otro sin igualar eso, las diferencias entre sensores son artificiales
(diapositiva 14: «mezclar σ⁰ y γ⁰ u órbitas distintas»). El Tp2 deja **una pila de
radar en la grilla común de 10 m (EPSG:32721), en γ⁰ LINEAL**, con el nombre de cada
banda normalizado y su fuente escrita dentro del archivo. Sobre esa pila se arma el RGB
copolarizada–cruzada–cociente, se mide la respuesta de cada cubierta en cada banda y
se controla la calibración en una zona estable.

## Qué hay en cada carpeta

| Carpeta | Qué hay |
|---|---|
| `00_Guia_del_practico/` | **Empiece por acá:** `00_LEEME.md` (paso a paso, con menús de SNAP y QGIS) y `objetivos.md` |
| `01_Prompt_IA/` | Prompt ingenuo, análisis, prompt corregido y verificación |
| `02_Subsets_SNAP_QGIS/` | Los productos de SNAP (`.dim` + `.data`), sus exportaciones a GeoTIFF y la pila `<SITIO>_pila_gamma0_lineal.tif` con su tabla de bandas |
| `03_Scripts/` | Los cinco scripts (el quinto, `Tp2_05`, para profundizar) y `00_ORDEN_DE_EJECUCION.md` |
| `04_Tablas_de_trabajo/` | `cubiertas_<SITIO>.gpkg`: los polígonos de cubierta que digitaliza el grupo |
| `05_Resultados/` | RGB, tablas de respuesta y de control, gráficos y bitácoras |
| `06_Bibliografia/` | `referencias.md` |
| `07_Preguntas_y_entrega/` | Preguntas, rúbrica y **lo que entrega el grupo** |
| `09_Grafos_SNAP/` | Tres grafos del Graph Builder (Sentinel-1 GRD, Sentinel-1 SLC, SAOCOM) y `LEEME_grafos.md` |
| `NOTAS_TECNICAS.md` | Decisiones técnicas y hallazgos con datos reales |

## Los pasos y los scripts

| Paso | Qué | Marca |
|---|---|---|
| 1 | Sentinel-1 GRD a γ⁰ con el grafo `Tp2_S1_GRD_a_gamma0.xml` | **EN SNAP** |
| 2 | Filtro de speckle (Refined Lee o Lee Sigma) como paso aparte | **EN SNAP** |
| 3 | Bandas virtuales en dB, guardado en `.dim` y exportación a GeoTIFF de cada banda lineal | **EN SNAP** |
| — | SAOCOM L1A del Delta a γ⁰ (`procesar_saocom.py`) y el Sentinel-1 del 26/09/2026 procesado por el docente | **YA VIENE HECHO** (los grafos quedan para ver cómo se hace) |
| 4 | `Tp2_01_pila_multibanda.py`: la pila en lineal sobre la grilla común | **SE CORRE** |
| 5 | `Tp2_02_rgb_copol_cruzada_cociente.py`: RGB co-pol / cros-pol / cociente | **SE CORRE** |
| 6 | Digitalizar las cubiertas en `cubiertas_<SITIO>.gpkg` | **EN QGIS** |
| 7 | `Tp2_03_respuesta_por_cubierta.py`: respuesta de cada cubierta en cada banda | **SE CORRE** |
| 8 | `Tp2_04_control_zona_estable.py`: diferencia en zona estable < 1 dB, por polígono; para profundizar, `Tp2_05_saocom_por_cubierta.py` (SAOCOM cuadripolar) | **SE CORRE** |

NISAR GCOV llega ya en γ⁰ y georreferenciado: no pasa por SNAP. NovaSAR-1 se calibra
en Python (σ⁰ = DN² / 1E+05). Ambos los lee directamente `Tp2_01` desde el disco del
curso.

## Sinergia y fusión en el Tp2

- **Apilar no es fusionar.** La pila del paso 4 es la condición previa de una fusión
  a nivel de píxel, pero ningún algoritmo combina todavía las bandas en un producto.
- **El RGB del paso 5 no es una fusión multisensor**: combina las polarizaciones de
  **un solo** sensor para verlas juntas. Es una herramienta de interpretación y no se
  usa para medir.
- **El paso 7 es SINERGIA.** Cada banda produce su propia respuesta por cubierta; el
  grupo las compara y explica por qué difieren (superficie, doble rebote, volumen;
  penetración según la longitud de onda). El resultado es una interpretación, no un
  producto único, y se valida por **coherencia física** entre bandas.
- **El paso 8 es un control de calibración**, condición para que tanto la sinergia
  como una fusión posterior tengan sentido.

## Qué se entrega

1. La pila `02_Subsets_SNAP_QGIS/<SITIO>_pila_gamma0_lineal.tif` y su tabla
   `<SITIO>_pila_bandas.csv`.
2. El producto de SNAP en `.dim` (γ⁰ lineal filtrado, con sus bandas virtuales en dB y
   los metadatos originales).
3. Los RGB de `05_Resultados/02_Rasters/` y `05_Graficos/`.
4. `cubiertas_<SITIO>.gpkg`, la tabla de respuesta por cubierta, la de contraste y la
   figura de cajas.
5. La tabla del control en zona estable.
6. Las cifras de los polígonos propios del grupo comparadas, en una línea, con las del
   Desarrollo.
7. Las respuestas de `07_Preguntas_y_entrega/preguntas.md`.

## Qué tiene que estar listo antes (YA VIENE HECHO)

- El Tp1 corrido: los sitios en `00_COMUN/01_AOI/` y la búsqueda de fechas.
- SNAP 9 o posterior, con la caja de herramientas Sentinel-1 y la de radar.
- La escena Sentinel-1 IW GRD del 26/09/2026 sobre Ibicuy, para el paso 1:
  `00_COMUN\08_Originales_crudos\S1_CRUDO\S1C_IW_GRDH_1SDV_20260926T091407_20260926T091432_009616_013235_EE65.zip`
  (bajada por el docente de ASF con `datos_crudos.py s1_crudo` el 21/10/2026; 978 MB), y la misma escena ya
  procesada por el docente en `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo`, para
  comparar.
- Los NISAR GCOV del Delta en `00_COMUN\08_Originales_crudos\NISAR_DELTA` (`BANDA_L_NASA` y, si
  existe, `BANDA_S_ISRO`), del 17, 18 y 30/09/2026, bajados por el docente con
  `datos_crudos.py nisar`. **No se copian** a la carpeta del práctico.
- Los SAOCOM-1A de 2020 del Delta, ya procesados a γ⁰ por el docente
  (`Tp5_Incendios\02_Subsets_SNAP_QGIS\SAOCOM_gamma0`), para el ejemplo de la pila
  sobre `A1_DELTA_QUEMAS` (no cubren Ibicuy).
- NovaSAR-1 en `E:\IMÁGENES NOVASAR-1 2023 2024\ENTRE RIOS-SANTA FE` (sólo si se
  trabaja `F_BOVRIL` o `B_CONCORDIA`; no cubre Ibicuy).

## Lo que conviene saber de entrada

- Sobre Ibicuy, la pila reúne C (Sentinel-1), S y L (NISAR) y P (BIOMASS L1B del
  05/10/2026, γ⁰ sobre el elipsoide, declarada `gamma0E`). La X (COSMO-SkyMed) es de
  Diamante y NovaSAR no cubre Ibicuy: **si no cubren el sitio, no entran, y la ausencia se declara**. La
  comparación «en todas las bandas» es en todas las que existen sobre el sitio.
- La consulta al Planetary Computer (Sentinel-1 RTC) necesita red hacia ese servicio. Si
  en clase no responde, la pila se arma con NISAR y con el Sentinel-1 procesado en SNAP, y
  se declara.
