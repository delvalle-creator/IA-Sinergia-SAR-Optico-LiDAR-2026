# Tp1 - Workflows de Orange Data Mining

Orange 3.40. Se abren con File > Open (o doble clic sobre el .ows si Orange esta asociado).
Cada workflow lee sus datos de la subcarpeta `datos` con ruta relativa: la carpeta 08_Orange se puede copiar
entera a otro equipo y sigue funcionando.

| Workflow | Datos | Que muestra |
|---|---|---|
| `Tp1_A_huella_frente_a_dato.ows` | `Tp1_inventario_huella_dato.csv` (30 combinaciones escena-sitio de NovaSAR-1 y NISAR) | Dispersion huella frente a pixeles con dato y caja de la diferencia por sensor (paso 2, pregunta 1) |
| `Tp1_B_nube_catalogo_frente_a_sitio.ows` | `Tp1_nubosidad_Sentinel2.csv` (17 teselas Sentinel-2 verificadas, oct-nov 2023) | Nube del catalogo frente a nube dentro del sitio (paso 3, pregunta 2) |
| `Tp1_C_LiDAR_valido_y_descartado.ows` | `Tp1_GEDI_muestra_30000.csv` y `Tp1_ATL08_muestra_30000.csv` | Estadisticas de las huellas, sensibilidad por motivo de descarte, altura rh98 de validas y descartadas, altura del dosel ATL08 y motivos de descarte (paso 5, pregunta 6) |
| `Tp1_D_CCI_Biomass_por_anio.ows` | `Tp1_CCI_por_anio.csv` y `Tp1_CCI_pixeles_muestra_20000.csv` | Biomasa por anio, 2015 frente a 2020 por pixel y desvio relativo de 2020 (productos de biomasa) |
| `Tp1_E_escenas_por_anio_y_banda.ows` | `Tp1_escenas_por_anio.csv` | Tabla dinamica de escenas verificadas por anio y banda (paso 7) |
| `Tp1_F_contexto_del_sitio.ows` | `Tp1_mapbiomas_area_por_clase_ancho.csv` y `Tp1_contexto_pixeles_muestra.csv` | Area por clase de MapBiomas 1985-2025 (Line Plot), cajas por clase de la biomasa CCI 2024, de la banda P VH y de la altura FH (sin agua: la clase de ríos y lagos queda sin FH), y CCI frente a P VH (paso 9, pregunta 11) |
| `Tp1_G_banda_L_antes_despues.ows` | `B_CONCORDIA_antes_despues_muestra.csv` (20 000 pixeles al azar de B_CONCORDIA) | Cambio de banda L (SAOCOM TNA, HH 11/11 menos 10/10/2023) y de banda C (Sentinel-1, VV 04/11 menos 23/10/2023) por zona y por clase de MapBiomas 2023, y C frente a L por pixel (paso 6 (g), preguntas 3, 7 y 10) |

Como se armaron los datos (todos salen de 05_Resultados del Tp1 y de 02_Subsets_SNAP_QGIS):

- Inventario: filas de `inventario_local.csv` con pixeles contados; `huella_menos_dato` = huella - dato.
- Nubosidad: filas Sentinel-2 por tesela de `planilla_MPC_B_CONCORDIA.csv` con las dos nubosidades medidas.
- GEDI: 15 000 huellas validas y 15 000 descartadas, al azar, de `lidar_B_CONCORDIA.gpkg` (capa gedi_l2a; 514 243
  huellas en total, 75 340 validas). La muestra esta equilibrada a proposito para comparar las dos clases; no
  representa la proporcion real (15 % validas). `sensibilidad` fuera de 0 a 1 (valores de relleno) se dejo vacia.
  `motivo_principal` es el primer motivo de descarte de la huella.
- ATL08: 30 000 segmentos al azar de la capa atl08 (138 526 en total).
- CCI Biomass: 20 000 pixeles al azar de `B_CONCORDIA_CCI_Biomass_v7_AGB.tif` con biomasa en algun anio;
  `SD_rel_2020_pct` = 100 x SD_2020 / AGB_2020; `clase_2020` agrupa AGB_2020. `Tp1_CCI_por_anio.csv` es la misma
  muestra en formato largo (anio, AGB > 0).
- Escenas: `matriz_convergencia_B_CONCORDIA.csv` sumada por anio y banda.
- Contexto del sitio: `B_CONCORDIA_mapbiomas_area_por_clase_y_anio.csv` de Tp1_08, una fila por clase (las de
  1000 ha o mas en algun anio) y una columna por anio, en miles de ha; y `B_CONCORDIA_contexto_pixeles_muestra.csv`
  de Tp1_08 tal cual (hasta 2000 pixeles por clase de MapBiomas 2025). La cruzada de P es VH: la HV del producto
  BIOMASS trae interferencia de radiofrecuencia sin corregir.

Las columnas con el prefijo `D#` en el encabezado del CSV (anio) son categoricas para Orange.

Los Box Plot de los workflows quedan en «No comparison» y sin anotaciones (revision del 27/10/2026): las pruebas t y
ANOVA que ofrece el widget no son apropiadas aqui (grupos desiguales, valores extremos, huellas vecinas que no son
independientes, o grupos armados con la misma variable que se compara). Orange tiene la interfaz en ingles: sus
graficos usan punto decimal (0.95 es 0,95). En Tp1_C, las validas van en azul y las descartadas en naranja, igual que
en el proyecto de QGIS.
- Banda L antes y durante: `B_CONCORDIA_antes_despues_muestra.csv` sale de `03_Scripts/Tp1_06b_banda_L_antes_despues.py`:
  20 000 pixeles de 20 m al azar con clase de MapBiomas 2023 y con dato en los dos pares; `zona` es agua permanente
  (JRC >= 90 %), agua de crecida de banda C del 04/11/2023 (mascara del Tp6) o tierra. Los cambios son despues menos
  antes, en dB. La L sube unos 3 dB en todo el sitio entre el 10/10 y el 11/11 (cambio general): se lee la zona
  inundada contra la tierra del mismo par, no contra cero.
