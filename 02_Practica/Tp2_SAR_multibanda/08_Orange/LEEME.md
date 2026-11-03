# Tp2 · Workflows de Orange Data Mining

Cinco workflows (`.ows`) armados para Orange Data Mining 3.40. Cada uno lee sus datos de la subcarpeta `datos`
con ruta relativa: se abren con `File > Open` y los widgets aparecen configurados (doble clic sobre cada uno para
ver el gráfico o la tabla).

| Workflow | Datos | Paso de la guía | Qué se ve |
|---|---|---|---|
| `Tp2_A_respuesta_por_cubierta.ows` | `Tp2_pixeles_por_cubierta.tab` (los datos del `.csv` con el color de cada clase en la cabecera) y `Tp2_media_por_poligono.tab` (la media de cada polígono, en lineal): 3.388 píxeles de los polígonos de cubiertas, γ⁰ en dB de las 14 bandas de la pila (con la banda P de BIOMASS) | 7 | Estadísticas, cajas por clase en C VV, C VH, L HV y P VH, dispersiones C frente a L y L frente a P |
| `Tp2_B_contraste_entre_clases.ows` | `Tp2_contrastes.csv`: `A2_IBICUY_contraste_entre_clases.csv` con el par de clases | 7 | Tabla dinámica par × banda y contraste absoluto por banda |
| `Tp2_C_RTC_frente_a_SNAP.ows` | `Tp2_RTC_frente_a_SNAP.tab` (con el color de cada clase): el mismo Sentinel-1 del 26/09/2026 en RTC, SNAP sin filtro y SNAP con Refined Lee | 8 | Dispersión RTC frente a SNAP y cajas de la diferencia por clase |
| `Tp2_E_bandas_por_clase_MapBiomas.ows` | `Tp2_pixeles_por_clase_MapBiomas.tab` (los mismos datos que el `.csv`, con los colores oficiales de MapBiomas en la cabecera, que Orange usa): hasta 3.000 píxeles por clase de MapBiomas Argentina 2025, con la cruzada de C, S, L y P en dB, la AGB 2024 del CCI Biomass y la altura FH de BIOMASS (sin dato en la clase de ríos y lagunas: agua enmascarada) | 9 | Cajas por clase en cada banda, biomasa CCI frente a la cruzada P |
| `Tp2_D_filtro_de_speckle.ows` | `Tp2_speckle_sin_y_con_filtro.csv`: VV y VH sin filtrar, con Refined Lee y con Gamma Map 7 × 7 en agua calma, pajonal y monte | 2 | Cajas por clase y filtro, distribución de VV |

Cuidado con las medias: Orange promedia los dB de cada píxel. La mediana sí es válida (no cambia al pasar de lineal
a dB); la media oficial de cada clase es la de `Tp2_03`, promediada en lineal.

Los CSV salen de la pila `A2_IBICUY_pila_gamma0_lineal.tif`, de `cubiertas_A2_IBICUY.gpkg` (28 polígonos sorteados al azar el 22/10/2026) y
de las tablas de `05_Resultados/04_Tablas`. Si el grupo digitaliza sus propias cubiertas, los valores cambian.

Cada clase de cubiertas tiene un color fijo, el mismo en QGIS (`cubiertas_A2_IBICUY.qml`), en
Orange y en las figuras del Desarrollo. La paleta va en la tercera fila de cada `.tab`
(`colors=[...]`, en el orden alfabético de las clases): agua calma #1f3a93, agua rizada #4fa3e0,
pajonal #e6c229, suelo desnudo #f4a6c6, monte #1b8a3a, urbano #d62728, estable #7f7f7f. Las clases de MapBiomas llevan su nombre y su color
oficiales. Todos los Box Plot comparan medianas. El Box Plot de abajo del workflow `Tp2_A`
dibuja las cuatro medias de polígono de cada clase: la unidad de muestreo es el polígono, por
eso el ANOVA del pie de las cajas de píxeles no es válido para comparar clases.
