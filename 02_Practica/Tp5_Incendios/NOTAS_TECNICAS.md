# Tp5 — Notas técnicas

> **Qué es este archivo.** Las decisiones técnicas del práctico y su fundamento, las limitaciones conocidas y lo comprobado con datos reales. El punto de entrada es `00_LEEME.md`.

## Unidades

γ⁰ lineal en todo el radar. El cambio es 10·log₁₀(post/pre) con cada lado en lineal (`cociente_db`): se divide primero y se pasa a dB después. Restar dB es lo mismo **sólo** si cada dB vino de un promedio hecho en lineal; como el remuestreo a 20 m promedia, el orden importa. El óptico va en reflectancia de superficie (0 a 1), con el desplazamiento de +1000 descontado sólo en las escenas de línea de base ≥ 04.00 (no afecta a 2020, pero la función lo resuelve igual).

## Calibración de cada radar

- **Sentinel-1 RTC (Planetary Computer):** ya es γ⁰ con corrección del terreno. Se toman los valores ≤ 0 como sin dato.
- **ALOS-2, mosaico anual de JAXA:** γ⁰ = DN² · 10^(−8,3), es decir 10·log₁₀(DN²) − 83 dB. El cuadrado se calcula sobre el píxel original de 25 m, **antes** de remuestrear: se promedia potencia, no amplitud.
- **SAOCOM-1A:** con `00_COMUN\procesar_saocom.py` en SNAP: Calibration a σ⁰ (los SLC de CONAE ya vienen calibrados) → Multilook → Refined Lee → Terrain-Correction a 10 m, EPSG:32721; γ⁰ = σ⁰/cos θ con el ángulo de incidencia sobre el elipsoide. **Sin Terrain-Flattening**: con SAOCOM da entre 5 y 10 dB menos que ALOS-2 y NISAR. GeoTIFF de una banda en lineal.

## Georreferencia y grilla

EPSG:32721, bordes múltiplos de 20 m. Todo se lee directamente en esa grilla con `leer_en_grilla` (promedio para radar y reflectancia). El píxel de 20 m es un compromiso: el ALOS-2 es de 25 m y bajar a 10 m fabricaría detalle de banda L; subir a 25 m perdería el detalle del óptico y de la C sin necesidad. El aviso queda en la bitácora.

## Fechas

| Sensor | Antes | Después | Diferencia con el evento |
|---|---|---|---|
| Sentinel-1 | 16/07/2020 | 26/09/2020 | precisa |
| ALOS-2 | mosaico 2019 | mosaico 2020 | **imprecisa**: el mosaico anual combina pasadas de varios meses |
| SAOCOM-1A | 21/07/2020 | 25/10/2020 | precisa |
| Sentinel-2 | la elegida en Tp1_03 | 13/10/2020 | precisa, si no hay nubes ni humo |
| GEDI | 01/10/2019 a 31/03/2020 | 01/10/2020 a 31/03/2021 | misma estación antes y después (hasta el 27/10/2026, «después» no tenía fin y mezclaba 2021 a 2025) |

**Las quemas no empezaron en julio.** En el Delta se vieron focos desde febrero de 2020; Naturalistas Santafesinos informó más de 530 km² quemados entre febrero y el 15/07/2020, y julio fue el peor mes, con 6741 focos (Universidad Nacional del Litoral, «Récord de quemas en medio de una pandemia», 19/08/2020, https://www.unl.edu.ar/noticias/news/view/récord_de_quemas_en_medio_de_una_pandemia). Las fechas «antes» del curso (Sentinel-1 del 16/07, Sentinel-2 del 15/07, SAOCOM del 21/07) caen en pleno pico: lo que ya se había quemado antes aparece igual en las dos fechas y **no** se detecta como cambio. El mapa mide lo quemado entre mediados de julio y octubre, no toda la temporada; el «antes» de GEDI (primavera y verano 2019-2020) es anterior a la temporada de quemas. Cuánto afecta al recorte A1 depende de qué parte de esos 530 km² cayó en él: se puede ver con MapBiomas Fuego (`A1_DELTA_QUEMAS_MapBiomas_fuego_mes_1999_2025` en `02_Subsets_SNAP_QGIS`, mes de la quema de 2020).

La fecha de cada píxel del mosaico ALOS-2 está en su banda `date` (días desde el 24/05/2014). Tp5_01 la lee, escribe el rango en la bitácora y, con `--alos2_desde`, deja sin dato los píxeles cuya pasada de 2020 es anterior a las quemas.

Corrida del 28/10/2026 con internet: en A1_DELTA_QUEMAS todo el mosaico es de una sola pasada por año, el 02/08/2019 y el 23/08/2020. La pasada de 2020 es anterior a las quemas de fines de agosto a octubre, por eso el ΔHV de ALOS-2 (mediana 0,07 dB) no las ve.

## Filtros

- Sentinel-2: SCL 4, 5, 6, 7 y 11 válidas; las demás (nubes, sombras, saturados) quedan sin dato. La nubosidad se cuenta en el sitio.
- Agua permanente: clase 1 de la cobertura de control → nunca quema. Sin cobertura, no se enmascara y se dice.
- GEDI: los filtros se aplicaron en el Tp1 (`l2a_quality_flag_rel3` = 1, `degrade_flag` = 0, `sensitivity` ≥ 0,95, `surface_flag` = 1). El campo de calidad de la versión 003 se llama `l2a_quality_flag_rel3`, no `quality_flag`.

## Por qué cada umbral

- **Otsu por defecto:** separa dos modas sin elegir a mano. Supone un histograma bimodal; si el área quemada es una parte chica del sitio, la moda «quemado» puede no verse y Otsu cae en cualquier lado. Por eso cada histograma queda guardado.
- **Umbrales manuales de partida (1 dB para C y SAOCOM, −2 dB para ALOS-2, 0,15 para el dNBR):** son puntos de partida para discutir, no valores calibrados. Se eligieron el 22/10/2026 con los datos del curso: entre julio y septiembre de 2020 la retrodispersión subió unos 3 a 4 dB en todo el sitio (lluvia de fines de agosto y rebrote), así que el fuego aparece como un menor aumento, no como una caída. Con 1 dB la C detecta la mitad de lo que MapBiomas Fuego da como quemado en agosto y septiembre, con un 20 % de falsas alarmas; el dNBR con 0,15 detecta el 79 % con un 10 %. Los ejemplos anteriores (−3 dB y 0,27) casi no detectaban quema en este sitio.
- **Cobertura de control de A1:** sólo tiene agua permanente (JRC); no hay pajonal ni monte digitalizados. Para la lectura por estructura se usa el CCI Biomass 2020 (pajonal < 15 Mg/ha, albardón ≥ 30 Mg/ha).
- **dNBR 0,27:** límite de severidad moderada-baja de Key y Benson, para bosques templados. En humedales se calibra con la referencia.

## Por qué decisión en V3 y rasgo en V4

La V3 combina decisiones porque cada radar se umbraliza en su propio rango (dB distintos en C y en L, con aumentos generales distintos entre fechas) y la pregunta es binaria; la V4 combina rasgos porque la severidad es graduada y el modelo tiene que ver los valores de ΔVH, ΔHV y dNBR, no sólo si cada uno superó un umbral. En las dos, las ventanas de fecha difieren (Sentinel-1 16/07–26/09; SAOCOM 21/07–25/10; Sentinel-2 15/07–13/10; ALOS-2 mosaicos anuales) y eso se declara: la diferencia de fechas no decide el nivel. Entra con variables derivadas (rasgos), no con bandas originales: es fusión de rasgo.

## El Random Forest

300 árboles, `class_weight="balanced"`, `min_samples_leaf=2`, semilla 2026, hasta 20 000 píxeles repartidos por igual entre las clases, sólo píxeles con dato en todas las capas. La exactitud fuera de bolsa se calcula con píxeles vecinos de los mismos polígonos: siempre es optimista y no se informa como exactitud.

## Limitaciones conocidas

1. **Mosaico anual ALOS-2:** fecha imprecisa (ver arriba) y 25 m.
2. **Lluvia y bajante, dos efectos con signo distinto.** La serie de 20 pasadas Sentinel-1 (órbita 68, 16/06 a 26/10/2020) muestra que no hay un aumento gradual: tres fechas (02/09, 26/09, 20/10) están 5 a 7 dB por encima de sus vecinas en todo el sitio, y el 26/09, la fecha «después» del curso, es una de ellas. Eso sube la señal en C y en L. La bajante del Paraná (Rosario: promedio 1,00 m en julio, 0,62 m en agosto, 1,14 m en septiembre, INA) baja el doble rebote en L y explica la diferencia entre los mosaicos ALOS-2 2019 y 2020, no el aumento del 26/09. Con `--c_pre_extra` y `--c_post_extra` (promedio lineal de pasadas) el aumento general baja de +3,7 a +2,4 dB.
3. **Referencia de 2020:** el etiquetado del Desarrollo usó el Sentinel-2, que también entra al mapa. Se controló con el dNBR de Landsat 8 (19/07 y 07/10/2020, umbral de Otsu 0,295): acuerdo del 81 % (κ 0,60) y la misma conclusión en la tabla de variantes (`A1_validacion_referencia_Landsat8.csv`).
4. **Variante «multisensor»:** es SAR (C + L) + óptico. GEDI no entra en el modelo (se usa en el paso 6 de la guía, `Tp5_04`). En la tabla de variantes se escribe lo que realmente entró.
5. **Una sola escena de Sentinel-1 por fecha:** `Tp5_01` toma la primera escena del día que devuelve el catálogo. Si el sitio quedara partido entre dos escenas del mismo día, faltaría una parte. Se ve en QGIS como un borde recto sin dato.
6. **GEDI:** pocas celdas con huellas antes y después (325 con la misma estación); un rh98 menor de 3 m es el piso del instrumento sobre terreno llano, no la altura del pajonal.
7. **Dominio de la V4:** la V4 exige las seis capas; además de la franja de SAOCOM pierde las nubes (1.315 ha) y los píxeles sin RdNBR (|NBR previo| < 0,05; 7.171 ha dentro de la franja). `Tp5_03 --sin_rdnbr` clasifica 57.800 ha sin mejorar el acuerdo con la referencia (0,846 frente a 0,872).

## Hallazgos con datos reales del curso

- Entrenamiento sorteado (22/10/2026): 35 polígonos de 100 m (875 píxeles); fuera de bolsa 0,986; importancias dNBR 0,341, RdNBR 0,329, ΔHV SAOCOM 0,155. Validación de la V4: perímetro 0,835 ± 0,061 (omisión 0,25, comisión 0,21), severidad 0,598 ± 0,065. El óptico solo (0,859 ± 0,058) y la V4 no se distinguen; con el entrenamiento ubicado a mano la V4 había dado 0,882 ± 0,053.

- El recorte `A1_DELTA_QUEMAS` es el de las escenas SAOCOM del curso SAR CEREGEO 2023, leído de sus `.dim`.
- El campo de calidad de GEDI L2A V003 es `l2a_quality_flag_rel3`.
- Ablación con validación cruzada por polígono (Orange `Tp5_D`): solo óptico 0,94, solo radar 0,67, todos 0,96; sin RdNBR 0,91.
- Las cifras de ΔVH, ΔHV, dNBR, umbrales y exactitudes las produce cada grupo; las del Desarrollo son una referencia, no un resultado que haya que reproducir.
