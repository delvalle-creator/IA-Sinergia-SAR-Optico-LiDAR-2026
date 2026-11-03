# Tp7 — Notas técnicas

> **Qué es este archivo.** Las decisiones técnicas del práctico y su fundamento,
> las limitaciones conocidas y los hallazgos con datos reales. No es el punto de
> entrada: para el recorrido, abra `00_LEEME.md`.

**Pregunta:** ¿hay deformación previa en la ladera, y con qué MDE se podría medir el volumen movilizado?
**Sitio:** `E1_DIAMANTE_BARRANCA` (−60,71 / −32,135 / −60,575 / −32,015, del `.kml`
de la escena COSMO-SkyMed Spotlight).

## Los datos y sus fechas

| Banda | Sensor | Producto | Fechas | Estado |
|---|---|---|---|---|
| X (3,1 cm) | COSMO-SkyMed | Himage 3 m, par InSAR | 15/10 y 19/10/2018 | Procesado en el curso 2023 **sin desenrollar** |
| X | COSMO-SkyMed | Spotlight 1 m (SLC) | 20/10/2018 | Su huella fija la ventana del sitio. Es un SLC en geometría de radar: para digitalizar se usa Pléiades de CONAE o un mosaico XYZ |
| X | COSMO-SkyMed | Himage | 12, 18, 28/10/2018 | Otras fechas del archivo (`EVENTOS["Tp7"]`) |
| C (5,55 cm) | Sentinel-1 | IW SLC, par del período | a elegir con `Tp7_01` | HyP3 o SNAP |
| C | Sentinel-1 | GRDH | 12/10/2018 | En el archivo (no se usa para InSAR) |
| L (23,5 cm) | SAOCOM | SLC | — | **No hay par en octubre de 2018** |
| — | IGN | MDE 5 m | verificar en metadatos | Archivo del curso |
| — | Copernicus DEM | GLO-30 | TanDEM-X 2011–2015 | Planetary Computer |
| — | ICESat-2 | ATL08 v007 | desde octubre de 2018 | `Tp1_05` |

## Decisiones y su fundamento

**El período manda.** El par X es del 15–19/10/2018. La búsqueda en C empieza el
15/09 y termina el 15/11/2018. La fusión de decisión supone que todas las bandas
miran el mismo intervalo; un par C de 2025 responde otra pregunta.

**Criterios del par.** Hasta 24 días (más coherencia) y línea de base
perpendicular hasta 150 m (menos fase topográfica residual), misma órbita relativa
y pasada. En 2018 volaban Sentinel-1A y 1B, pero sobre Diamante sólo hay adquisiciones cada 12 días (órbita 141, descendente).

**HyP3 con `looks="10x2"`.** El producto sale a unos 40 m de píxel (10 looks en
rango × 2 en azimut sobre el píxel del IW SLC). El script lo pasa a la grilla de
10 m por vecino más cercano (`--remuestreo_c`; promedio si la grilla es de 40 m o
más): no se interpola ni se afina por debajo del píxel nativo (regla 2), y cada 16
píxeles de 10 m comparten un valor. La X de 2 m se promedia (`average`) a la grilla.
La barranca tiene pocas decenas de metros de ancho; en banda C, la ladera queda
representada por muy pocos píxeles independientes.

**Desenrollado en geometría de radar.** SNAPHU trabaja sobre la fase en
geometría de adquisición; no conviene desenrollar el producto `_TC`
(ortorrectificado). Si no está el producto sin `_TC`, puede desenrollarse el `_TC`
como alternativa de menor calidad (así se hizo en el Desarrollo). Se
parte del interferograma filtrado sin `_TC`, se recorta (el tiempo de SNAPHU
crece con el tamaño), y se usa el modo `DEFO` con inicio `MCF`.

**Conversión fase–desplazamiento.** `d = −λ · fase / (4π)`, la de `Phase to
Displacement` de SNAP. λ: X 0,03123 m (9,6 GHz), C 0,05547 m (5,405 GHz),
L 0,2350 m (1,275 GHz). Un ciclo de fase (2π) equivale a λ/2: 1,56 cm en X,
2,77 cm en C, 11,75 cm en L.

**Convención de signo entre productos.** El script supone que los
desplazamientos que recibe tienen la misma convención de signo. SNAP y HyP3
documentan cada uno la suya: verifíquela en la documentación de cada producto
antes de fusionar. Si no coinciden, la intersección por signo elimina
deformación real.

**Geometría de visión.** El desplazamiento es en la línea de visión (LOS) de cada
satélite. La barranca de Diamante enfrenta el río; un movimiento de la ladera
hacia el río se acerca a un satélite y se aleja de otro según la pasada. Las dos
bandas de 2018 son **descendentes** (COSMO-SkyMed: PASS = DESCENDING, mirada a la
derecha, rumbo ≈ 197,5°, incidencia 59,6° en la ladera, 20:49 UTC; Sentinel-1:
rumbo 193°, incidencia 38,9°). `Tp7_02` aplica la regla de signo según la
geometría (`--signo`): con `vector` proyecta en cada LOS un movimiento hipotético
(`--mov_azimut 292.5 --mov_inclinacion 5`, hacia el ONO y un poco hacia abajo) y
exige que cada banda detecte con ese signo; 1 m de ese movimiento da −0,90 m en X
y −0,68 m en C. Con pasadas distintas o sin declarar (`auto`), no interpreta el
signo e informa la coincidencia de detección. La pasada, el rumbo y la incidencia
se pasan con `--pasada_x --rumbo_x --inc_x` (de SNAP) y se leen solos de HyP3. El `*_vert_disp.tif` de HyP3 supone movimiento vertical
puro, que en una barranca no es cierto: no se usa.

**Referencia del desplazamiento.** Mediana de la zona de referencia, sólo en
píxeles con coherencia ≥ 0,3. InSAR mide diferencias de fase; sin referencia, el
número absoluto no significa nada. La zona por defecto es un anillo de 500 m
alrededor de la ladera sin el agua: se quitan los píxeles con ocurrencia ≥ 50 %
en el JRC Global Surface Water (el río no es estable ni coherente). El JRC se lee
del Planetary Computer: sin conexión, el anillo queda completo y la bitácora lo
avisa. `--zona_estable <gpkg>` reemplaza el anillo por un polígono digitalizado
(en `Tp7_02` y en `Tp7_03`). El vector `E1_zona_referencia.gpkg` guarda el anillo
completo; el agua se quita al rasterizar. La coherencia media de referencia se
calcula sobre esa zona sin filtro de coherencia.

**Umbral de 10 mm.** Es del orden de la dispersión esperable por atmósfera en un
par de pocos días. Si el desvío en la referencia lo supera, la banda no detecta y
se dice. El umbral se cambia con `--umbral_m`, o se fija por banda como k veces la
NMAD de la referencia (`--umbral_k`), y se declara. `Tp7_02` dibuja los
histogramas con la línea de cada umbral (`E1_histogramas_umbrales.png`, regla 6).

**Fusión de decisión con `interseccion` estricta.** Máxima confianza:
`fusion_decision(..., "interseccion", minimo_votos=n)`, con n = número de bandas
con desplazamiento válido. Un píxel se decide sólo si las n bandas tienen dato
coherente allí; se marca +1 o −1 si todas coinciden en signo y superan el umbral,
0 si no (el signo, según la regla de geometría de arriba). Donde falta alguna banda, queda sin decidir. En la X, la fase de la componente 0 de SNAPHU (sin confianza) no se usa (`--x_componentes`). Una banda vacía (fase
desenrollada en cero) no entra a la fusión. La banda `bandas_que_votaron` dice
cuántas bandas tenían dato coherente en cada píxel, y la bitácora informa cuántos
píxeles de la ladera quedaron decididos. Es el nivel de fusión que más tolera
resoluciones y geometrías distintas (diapositiva 12), porque combina decisiones y
no valores.

**Bandas de 2018.** La diapositiva 30 plantea la sinergia con C y L («la banda L
conserva coherencia en la vegetación donde la C la pierde»). En octubre de 2018
la comparación es X (COSMO-SkyMed) frente a C (Sentinel-1): SAOCOM-1A se lanzó
ese mes y no hay par en L.

**Volumen.** `dZ = después − antes`, con el sesgo de la zona estable restado. Un
píxel es detectable si |dZ| supera dos desvíos del ruido de la zona estable. El
GLO-30 está sobre EGM2008; el IGN, sobre su sistema vertical (a verificar:
SRVN16). La diferencia de datum entra en el sesgo; la de resolución, no.

**ICESat-2.** `h_te_best_fit` es altura elipsoidal (WGS 84). Se convierte a
EGM2008 con PROJ (`alturas_a_egm2008`, grilla `us_nga_egm08_25`); si la grilla
falta, la función falla en lugar de devolver alturas sin convertir (en Entre Ríos
el error sería de unos 15 m). Se comparan sólo segmentos en tierra firme estable.

## Limitaciones conocidas

1. **El agua de la referencia depende de la conexión.** Sin acceso al JRC, el
   anillo incluye el río; la bitácora lo avisa y la solución es `--zona_estable`.
2. **Fusión estricta y coherencia baja.** Con la coherencia de la banda X en la
   ladera (≈ 0,41, cerca del mínimo de 0,3), buena parte de la ladera puede quedar
   sin decidir: la fusión no afirma nada donde una banda no tiene dato.
3. **Los MDE ya vienen recortados** en `02_Subsets_SNAP_QGIS\QGIS_GeoTIFF` (GLO-30,
   FABDEM, IGN 5 m y el mosaico IGN de 2018). El volumen se calcula a 30 m (el píxel del
   GLO-30): el IGN se promedia a esa grilla y el GLO-30 no se afina.
4. **El control de los segmentos de 100 m con ICESat-2 se hace en QGIS.** La guía
   da el procedimiento con la tabla LiDAR del sitio, que ya trae la cota del
   terreno en EGM2008 y en SRVN16 y los valores del GLO-30 y del FABDEM en cada
   segmento. Los puntos de 20 m sobre la cicatriz los compara `Tp7_04`.
5. **Fechas de los MDE: ninguno es posterior al evento.** El GLO-30 es de 2011–2015
   y el IGN de 5 m es un vuelo de 2013 (metadato `0009 - 2013 - Rio Parana - Sector
   3.5.pdf`); el «mosaico2018» es el mismo IGN armado en el curso de 2018. La diferencia
   entre ellos no es el volumen movilizado en 2018: el paso 5 es un ejercicio de método
   (sesgo, ruido, límite de detección). El GLO-30 y el IGN son modelos de superficie
   (con dosel); el FABDEM es de terreno: no se mezcla con el IGN.
6. **Servicios en red.** La consulta a ASF y al JRC y el pedido a HyP3 se corren
   una vez antes del curso, con conexión.

## Hallazgos con datos reales del curso

- El producto InSAR COSMO-SkyMed del curso 2023 (par 15/10–19/10/2018) tiene la
  banda `Unw_Phase` **toda en cero**: el desenrollado con SNAPHU nunca se importó.
  Hay que rehacerlo.
- Coherencia en banda X: **≈ 0,41 en la ladera de la barranca frente a 0,40 en el
  anillo de referencia**. Sin contraste: las dos zonas son mayormente ciudad.
  Por cobertura de MapBiomas 2018 (10 m): bosque cerrado X 0,37, C 0,34 (octubre)
  y 0,40 (septiembre); urbano X 0,41, C 0,79 y 0,86. La ventaja de la C viene de
  la ciudad y de la resolución, no de la longitud de onda.
- COSMO-SkyMed mostró en la presentación 02 desfases de georreferencia respecto
  de Sentinel-2 (entre los 129 y 1120 m medidos en COSMO, NovaSAR y SAOCOM): la
  georreferencia de la banda X se verifica antes de digitalizar o comparar.

## Corrección del 22/10/2026 (desarrollo docente)

- `Tp7_02_coherencia_y_deformacion.py` declaraba «banda vacía» sólo si el
  desplazamiento era cero en **todo** el sitio. La `Unw_Phase` del curso 2023 tiene
  11 píxeles distintos de cero en 5,8 millones (0,0009 %), así que la banda X se tomó
  como válida, con desplazamiento cero en toda la ladera, y la fusión informó
  «0 píxeles confirmados por las 2 bandas»: un resultado engañoso. Ahora se declara
  vacía la banda con menos de 1 % de píxeles distintos de cero (con coherencia).
- El porcentaje de la ladera coherente se calcula con la coherencia sola (antes
  daba 0 % en una banda sin desplazamiento), y la bitácora ya no muestra «nan»
  cuando la mediana es exactamente 0.
- Respaldo del script anterior: `03_Scripts\Tp7_02_coherencia_y_deformacion.py.bak_20261022t`.
- Resultados con el script corregido (par C 12/10–24/10/2018): coherencia X 0,42 en
  la ladera y 0,40 en la referencia; C 0,59 y 0,54; desplazamiento C mediano −4,0 mm
  con 2,9 mm de ruido en la referencia; una sola banda con desplazamiento, sin fusión.
  Par de control C 18/09–30/09/2018: coherencia 0,64 y 0,63, mediana 0,0 mm, ruido 5,1 mm.
- El `los_disp` de HyP3 trae un desfase arbitrario por par (mediana cerca de la
  barranca de 32 mm en septiembre y 72 mm en octubre): para mirarlo en QGIS se
  centra la rampa en la mediana local; Tp7_02 ya lo refiere al anillo.

## Desenrollado, cicatriz y volumen (22/10/2026, corrida DES_Tp7_E)

- La fase X del curso 2023 se desenrolló con snaphu 2.0.7 desde Python (costo smooth,
  inicio MCF, 3 × 3 teselas, 4 min): `00_COMUN\09_Herramientas\desarrollo_docente\Tp7\E1_X_Unw_Phase_snaphu_15-19Oct2018.tif`.
  Menos de un ciclo de fase en el sitio; la grieta queda en la componente 0 (sin confianza).
  Con X y C, Tp7_02 decide 22 547 de 36 599 píxeles de la ladera y confirma 0.
- `04_Tablas_de_trabajo\E1_cicatriz_y_deposito.gpkg` tiene dos polígonos HIPOTÉTICOS del
  docente trazados sobre el MDE IGN 5 m (cicatriz: escarpa hasta 40 m de la grieta;
  depósito: banquina de 40 a 110 m). Respaldo de la capa vacía: `.bak_20261022v`.
- Tp7_03 (IGN 5 m → GLO-30, 30 m) da +6,2 m en los dos polígonos y 61 791 m³ de
  «depósito»: es un artefacto de resolución y pendiente (la diferencia es +5 a +10 m en
  toda la escarpa) entre dos MDE anteriores al evento. No es un volumen de 2018.
- Según las crónicas y Soffiantini y Brunetto (2023, RAGA 80 (2): 217–239) la barranca
  empezó a desprenderse el 20/09/2018: el par C 18/09–30/09 NO es anterior al evento.
  El movimiento fue sobre todo horizontal (≈ 1,4 m al ONO en 81 días), demasiado rápido
  para la fase de un par X de 4 días.

## Cicatriz y depósito sobre CBERS-4A (22/10/2026, corridas DES_Tp7_H y DES_Tp7_I)

- Los polígonos hipotéticos trazados sobre el MDE se reemplazaron por otros trazados sobre el CBERS-4A WPM del
  26/09/2026, fusionado a 2 m (`00_COMUN\09_Herramientas\desarrollo_docente\Tp7\cicatriz_sobre_cbers.py`).
  - Depósito: el claro de vegetación rala al pie de la escarpa, frente a la grieta. Tiene NDVI 0,17 (0,38 en el resto
    del talud), 5 031 m² y cota mediana 29 m, y queda al este del camino costero.
  - Cicatriz: la escarpa entre 5 m detrás de la grieta y el borde superior del claro, con 3 632 m², cota mediana 50 m
    y pendiente mediana 36 %.
  - La imagen es de 2026: el claro puede ser también un desmonte o un relleno posterior. Hay que confirmarlo con fotos
    de campo.
  - La versión anterior quedó como `E1_cicatriz_y_deposito.gpkg.bak_20261022h` y la primera de CBERS (que tocaba el
    camino) como `.bak_20261022i`.
- Tp7_03 (IGN 5 m → GLO-30, 30 m): la cicatriz da +4,24 m y el depósito +6,57 m, con 35 488 m³. Sigue siendo el
  artefacto de resolución y pendiente entre dos MDE anteriores al evento.
- ICESat-2 (`icesat2_cicatriz.py`): dos pasadas posteriores al evento, el 23/01/2024 y el 11/05/2025, pasan junto a
  los polígonos.
  - Dentro de los polígonos sólo hay segmentos del haz débil con terreno no válido.
  - El único segmento firme está a 29 m y da −6,6 m frente al IGN, con el sesgo restado.
  - En las laderas sin evento la diferencia va de −7,3 a −0,1 m, así que ICESat-2 no confirma la cicatriz.
- Proyecto de QGIS:
  - la grieta va en rojo con 2 mm de trazo y halo blanco;
  - la cicatriz va en naranja y el depósito en celeste;
  - hay un marcador nuevo, «3 Cicatriz y depósito»;
  - hay dos vistas nuevas, t7q_cic_cbers.png y t7q_cic_ign.png.
- ICESat-2 cada 20 m (`icesat2_20m_cicatriz.py`, h_te_best_fit_20m de ATL08 v007).
  - En el borde de la cicatriz da −13,4 m (haz fuerte, 2025) y −3,7 m (haz débil) frente al IGN.
  - En el depósito da +0,1 a +3,2 m (haz débil, 2024).
  - Es un indicio coherente con retroceso del borde y material al pie, dentro del error de las laderas (−9,2 a +0,8 m).
- A futuro: hace falta un MDE posterior a 2018. Los MDE del curso (IGN 2013 y GLO-30 2011–2015) son anteriores al
  evento y su diferencia no mide lo que se movió. Se necesita un vuelo de dron o de LiDAR aerotransportado, o un par
  estéreo de Pléiades, de resolución igual o mejor que 5 m.

## Resultados con los scripts corregidos (27/10/2026)

- **Tp7_02** (X promediada de 2 a 10 m con sus componentes; C por vecino más
  cercano; regla de signo `vector`): X 0,41 / 0,40 de coherencia, 80,2 % de la
  ladera coherente, −0,5 mm, NMAD 1,4 mm; C de octubre 0,59 / 0,54, 78,4 %,
  −3,9 mm, NMAD 2,9 mm. Decide 15.104 de 36.599 píxeles (41,3 %; unas 944
  observaciones independientes de la C) y confirma 0 en la ladera y 0 en la
  referencia. El 55,5 % de la ladera está en la componente 0 de SNAPHU.
- Por zona (`E1_zonas_ladera.gpkg`): observable por las dos bandas 14,3 % de la
  escarpa, 4,0 % del pie, 45,6 % del bloque y 82,1 % de la ciudad; 0 confirmados.
- Control independiente (mitad sur del anillo): 0 confirmados de 5.513 decididos.
- A 40 m: 1.007 de 2.294 decididos (43,9 %), 0 confirmados. Sin signo: 0.
- Umbral de 2 NMAD (2,9 mm en X, 5,8 mm en C): 58 confirmados en la ladera y 1 en
  la referencia; con control independiente, 5 en la ladera y 18 en el control:
  a ese umbral la fusión confirma ruido.
- **Tp7_03** (GLO-30 «antes», IGN «después», 30 m): sesgo +0,83 m (desvío 2,06 m,
  NMAD 1,15 m). Cicatriz: 5 píxeles, −4,24 m, volumen detectable
  −16.210 ± 8.308 m³, 40 % sobre 2σ con el signo esperado y 0 % con el contrario.
  Depósito: 6 píxeles, −6,57 m, 0 % con el signo esperado y 100 % con el
  contrario. Escarpa de control: 27 % y 15 %. El patrón se repite: no detectable.
- **Tp7_04**: sesgo local del IGN −1,59 m (54 puntos); laderas sin evento −9,2 a
  +0,8 m (p10 y p90, 139 puntos); sólo el −13,5 m del haz fuerte de 2025 en el
  borde de la cicatriz queda claramente fuera.
- **Tp7_05** (ampliación): interior urbano −8,3 mm/año (NMAD 2,6) → umbral
  −13,6 mm/año; franja de 150 m −12,9 mm/año, 44 % bajo el umbral; a 100 m de la
  grieta −15,0 mm/año.
- **Tp7_06** (ampliación): umbral 0,926 (p10 de la ladera); depósito 29 % por
  debajo, cicatriz 2 %.

## Desenrollado en SNAP con snaphu (28/10/2026)

- Interferograma 15–19/10/2018 en geometría radar rehecho con gpt: 00_COMUN/09_Herramientas/Tp7_ifg_radar_2018.xml (TP7_IFG_RADAR.bat). Salida: 02_Subsets_SNAP_QGIS/SNAPHU_2018/E1_CSK_X_ifg_15-19Oct2018_radar.dim; recorte de la barranca E1_CSK_X_ifg_barranca_radar.dim (1.800 × 1.750 píxeles).
- snaphu 2.0.4 para Windows instalado desde step.esa.int en %USERPROFILE%\.snap\auxdata\snaphu\snaphu-v2.0.4_win64\bin (INSTALAR_SNAPHU2.bat). Corrida con TP7_CORRER_SNAPHU.bat: DEFO, MCF, una tesela, 17 min 50 s; bitácora snaphu_consola.log (código 0).
- Snaphu Import: E1_CSK_X_ifg_barranca_radar_unw.dim. Statistics: fase envuelta −3,1416 a 3,1416 (media 0,027); Unw_Phase −990,3 a 44,7 rad (mediana −515,2). Coherencia del recorte: mediana 0,13. El rango (165 ciclos, 2,6 m en la línea de vista) es acumulación de saltos de ciclo en zonas incoherentes, no deformación.
- Figuras 5 y 6 del Desarrollo (Fig_Tp7_SNAP_snaphu_export_import_300dpi.png y Fig_Tp7_SNAP_statistics_antes_despues_300dpi.png en 05_Resultados/05_Graficos/Figuras_del_desarrollo); guía (capítulo del Tp7): ruta del ejecutable y tiempo de la corrida.
