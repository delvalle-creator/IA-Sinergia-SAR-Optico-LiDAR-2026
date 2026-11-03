# Tp9 — Notas técnicas

> **Qué es este archivo.** Las decisiones técnicas del práctico y su fundamento,
> las limitaciones conocidas y los hallazgos con datos reales. Para el recorrido,
> abra `00_LEEME.md`.

**Pregunta:** ¿dónde se perdió el monte entre 2021 y 2026 (2011 como referencia histórica), cómo se separa de la cosecha y es detectable la degradación bajo el dosel?
**Sitio:** `C_FEDERAL` (−59,02 / −30,99 / −58,62 / −30,59), también para la banda P.

## Los datos y sus fechas

| Banda | Sensor y producto | Fecha | Pol. | Resolución nativa | Unidad |
|---|---|---|---|---|---|
| L | ALOS-1 PALSAR FBS, RTC de ASF | 13/03/2011 | HH | 12,5 m | γ⁰ potencia |
| L | ALOS-2 PALSAR-2 mosaico anual JAXA | 2021 | HH, HV | 25 m | DN → γ⁰ |
| L | NISAR L2 GCOV, frecuencia A | 17/09/2026 | HH, HV | 20 m | γ⁰ |
| C | Sentinel-1 IW GRD RTC (órbita 68) | 10/08/2021, 14/09/2026 | VV, VH | píxel 10 m (resolución ≈ 20 × 22 m) | γ⁰ |
| S | NovaSAR-1 GRD, escena 50896 | 22/12/2023 | HH | 6 m | σ⁰ |
| P | BIOMASS L1B DGM, franja S2, traza 006, cuadro 284, ascendente | 12/08/2026 | HH, HV, VH, VV | 25 m × 22 m (rango en el terreno) | γ⁰ lineal (β⁰ × tan θ, en el GeoTIFF del curso) |
| Óptico | Sentinel-2 L2A, NDVI | 06/08/2021, 16/09/2026 | — | 10 m | NDVI |
| LiDAR | GEDI L2A V003 | 2019–2023, 2024–2025 | — | huella 25 m | rh98 en m |

`EVENTOS["Tp9"]` lista además fechas ópticas del 30/03/2016 y del 16/09/2026,
que los scripts no usan por defecto (`--fechas_opt` permite pasarlas).

## Decisiones y su fundamento

**Grilla de 20 m.** Es la de NISAR GCOV. Ir a 10 m inventaría detalle en NISAR y
en ALOS-2; ir a 25 m perdería el de Sentinel. ALOS-2 (25 m) llevado a 20 m con
`average` casi equivale a un vecino más próximo: no agrega información, y se
declara.

**ALOS-2 en potencia antes de remuestrear.** γ⁰ = DN² · 10^(−8,3) (la conversión
publicada por JAXA, 10·log10(DN²) − 83 dB). El cuadrado se calcula antes de
remuestrear para promediar potencia.

**ALOS-1 FBS es HH.** El HV de 2011 existe sólo en escenas FBD. El cambio
histórico 2011–2021 se mide en HH (`dHH_L_hist`), que responde más a la
interacción tronco-suelo y menos al volumen que el HV. Es una pérdida de
sensibilidad, y se declara. El producto RTC de ASF viene en γ⁰ de potencia (guía
de producto RTC de ASF), como lo supone el script.

**NISAR: frecuencia A y máscara.** Sin la máscara del producto, los bordes de la
pasada entran con valores de −133 dB o menos que arruinan cualquier promedio.

**Calibración cruzada.** Tres instrumentos con calibración, ángulo de incidencia
y procesamiento distintos. Desfase = mediana de la diferencia en dB en zona
estable, corregido multiplicando en lineal. Se usa la mediana porque es robusta
a los pocos píxeles que sí cambiaron dentro de la zona «estable». El desfase se
corrige; lo que limita la interpretación es el residuo después de corregir. Desde el
27/10/2026 `Tp9_01` reparte los cuadrados estables al azar en dos mitades (semilla
`--semilla`), calibra con una y mide el residuo en la otra, por separado en monte (3),
ciudad (7) y las dos. En Federal, para NISAR HV, el p75 del residuo absoluto es 2,64 dB
en el monte y 3,58 dB en la ciudad: un umbral de −1,5 dB píxel a píxel cae en el ruido.

**La zona estable.** Urbano (7) y monte confirmado sin cambio (3). El urbano tiene
doble rebote, muy sensible a la orientación de las calles respecto de la pasada:
dos sensores con geometrías distintas pueden diferir allí por geometría, no por
calibración. El monte confirmado es mejor referencia si de verdad no cambió.

**Spearman y curvas de respuesta.** Spearman no supone una relación lineal entre
dB y altura, que no la hay cuando la banda satura. La curva por clases de altura
muestra dónde se aplana. Se exigen 20 huellas como mínimo por capa y 100 por clase
de altura para que la clase entre al «rango de la curva»; el n de cada clase queda en
el CSV y en la figura. En lugar del p-valor (siempre 0 con decenas de miles de huellas
vecinas) se informa el IC del 95 % de ρ por remuestreo de celdas de 200 m. Las huellas
con rh98 mayor que `--rh98_max` (60 m; 20 m es lo plausible en el Espinal) se descartan
y se cuentan. Las bandas se comparan en la misma polarización.

**Distancia en fecha.** 730 días desde el 1 de julio del año de la capa. Un monte
puede desmontarse en días: una huella de 2019 no describe un píxel de 2025.

**Degradación como Δrh98 por celda.** GEDI no repite huellas: se agregan en
celdas de 200 m y se comparan medianas por período, con al menos 2 huellas por
período. El umbral de −3 m está por encima del ruido de rh98 en vegetación baja,
y el de |ΔNDVI| < 0,05 exige que el óptico no vea el cambio: degradación bajo el
dosel, no desmonte. El ΔNDVI por defecto (2026 − 2021) no coincide con las fechas de
las huellas (el período 2 termina el 28/06/2025); `--ndvi_p1`/`--ndvi_p2` permiten usar
otras capas o GeoTIFF (por ejemplo el Sentinel-2 del 24/09/2025: las candidatas pasan
de 3 a 1).

**Δrh98 como control, no como rasgo.** Si entra al modelo, el mapa queda sólo
donde hay huellas. Es un control complementario: se cuentan celdas (Tp9_03 las
informa), no píxeles, y con menos de 3 m de caída no confirma ni descarta.

**Cocientes en lineal.** `cociente_db` calcula 10·log10(post/pre) con cada lado
en lineal: es lo mismo que restar dB sólo si nada se promedió antes en dB.

**Fusión de rasgos.** Cada sensor aporta variables derivadas de cambio y de
nivel; el Random Forest las combina en un producto de cuatro clases. La clase 4
y `NDVI_actual` existen para que la cosecha no se confunda con desmonte.

**Entrenamiento equilibrado.** `fusion_pixel_o_rasgo` usa por defecto
`equilibrar=True`: el mismo número de píxeles por clase y `class_weight="balanced"`.
Equivale a suponer que la degradación es tan frecuente como el monte estable e infla
la clase rara. `--sin_equilibrar` (27/10/2026) entrena con los píxeles en su
proporción: la degradación baja de 11.250 a 3.378 ha. La bitácora dice cuál se usó.

**Rasgo histórico.** `dHH_L_hist` (2011–2021) describe el pasado y deja sin dato el
2,4 % del sitio sin ALOS-1. `--sin_historico` lo saca: el mapa cubre todo el sitio.

**Regla de clases.** Aperturas lineales (caminos, picadas, cortafuegos) = degradación;
desmonte de un lote = pérdida.

**Variantes en igualdad.** `--mascara_monte_2021` pone «no» fuera del monte de
MapBiomas 2021 (clases 3, 4 y 6) en las tres variantes.

**Georreferencia de NovaSAR.** La escena 50896 trae sólo cuatro GCP de esquina.
`Tp9_01` aplica la traslación medida con `--desplazamiento DX DY` (metros, DX
positivo = este, DY positivo = norte; la misma convención que imprime `Tp3_02`).
Desde el 23/10/2026 acepta `--puntos_enlace todos`: georreferencia con los 84
puntos de enlace del `metadata.xml`. Con ellos el corrimiento es rígido, -60 10
(medido por bordes contra Sentinel-2 B08 en 10 ventanas de 9 × 8 km).

**Zona estable.** `Tp9_01` usa la clase 3 sólo donde la digitalizó el grupo
(banda 2 `fuente_control` = 1); el monte que vino de MapBiomas queda afuera y la
bitácora lo informa. Con menos de 100 píxeles estables no calibra y lo declara.
Con el control del docente (14 cuadrados de monte y 12 urbanos, 650 píxeles) los
desfases son: ALOS-1 HH +1,74 dB, NISAR HH −1,59 dB, NISAR HV −1,13 dB. En HV el
desfase depende de la zona: −1,60 dB en el monte y −0,45 dB en la ciudad (doble
rebote y orientación de las manzanas); el que se aplica es la mediana de las dos.

**Variante con Δrh98 como rasgo.** `--rh98_como_rasgo` necesita polígonos de
entrenamiento dentro de las celdas con huellas en los dos períodos. Los 70 de
partida no caen en ninguna: el programa ahora lo dice y termina sin pisar el mapa
(antes cortaba con un error de Python).
La banda S no entra a la fusión, pero sí a las curvas de respuesta del paso 2,
donde un desfase de decenas de metros cambia qué píxel cae en cada huella.

**Nombre del rasgo de cambio en L.** Si NISAR trae HV, el rasgo es `dHV_L` (y el
nivel, `HV_L_actual_dB`); si sólo trae HH, se calcula en HH y se llama `dHH_L`
(`HH_L_actual_dB`), con un aviso en la bitácora: HH es menos sensible a la
biomasa. La variante `C_variante_L.tif` usa el que exista.

**Por qué cada banda ve un estrato.** La bitácora de `Tp9_02` lo explica con la
física: la onda de 5,5 cm (C) interactúa con hojas y ramitas de la copa; la de
24 cm (L), con ramas y troncos. Si C se aplana a pocos metros de altura y L sigue
subiendo, es lo esperado.

## Limitaciones conocidas

1. **La clase 3 de la cobertura de control puede no estar «confirmada».**
   `Tp4_01` llena la clase 3 también con MapBiomas cuando el grupo no digitalizó
   nada; `Tp9_01` la toma como «monte confirmado sin cambio 2011–2026» sin mirar
   la fuente. La guía pide revisar la banda `fuente_control` o usar `--solo_urbano`.
2. **La banda S no es rasgo del Random Forest.** `Tp9_03` usa L, C y óptico; la S
   sólo se evalúa en la sinergia.
3. **Fechas de estaciones distintas.** 06/08/2021 (invierno) frente a
   16/09/2026 (fin del invierno): parte del ΔNDVI y del ΔVH es fenología y estado
   de los cultivos, no cambio del monte. Las tres bandas de la fusión miden el mismo
   intervalo (2021 → 2026): ΔHV de L (ALOS-2 2021 → NISAR 17/09/2026), ΔVH de C
   (10/08/2021 → 14/09/2026) y ΔNDVI (06/08/2021 → 16/09/2026). Con las fechas de
   2025 (`--fechas_c 2021-08-10 2025-09-24 --fechas_opt 2021-08-06 2025-09-24`) la
   L mediría un año más que C y óptico, y un desmonte de 2025–2026 aparecería sólo
   en la L: si se usan, se declara.
4. **Hectáreas por conteo de píxeles.** Lo que imprime `Tp9_03` no es área
   estimada; el área con IC sale del Tp4.
5. **BIOMASS.** El script lee el GeoTIFF del curso (`C_FEDERAL_BIOMASS_P_20260812.tif`),
   que está en geometría de radar con puntos de control: lo ubica con ellos (WarpedVRT
   de GDAL). El γ⁰ se calculó sobre el elipsoide (β⁰ × tan θ, sin corrección por
   pendiente), aceptable en Federal, que es plano. Las huellas GEDI más cercanas son de
   2024–2025: con `--dias_max 730` entran sólo las de agosto de 2024 en adelante.
6. **Corridas de referencia.** Las órdenes con Planetary Computer, ASF y CMR se
   corrieron el 23/10/2026 en la computadora del curso (corridas DES_Tp9_A a
   DES_Tp9_D); las opciones nuevas del 27/10/2026 se corrieron sobre esa pila.
7. **Validación.** La referencia de 2021 es de 30 m (Landsat) en el 29 % de los puntos:
   no ve picadas, y la omisión de la degradación puede ser mayor. Los puntos del
   desarrollo los etiquetó quien hizo los mapas; en el curso cada grupo etiqueta los de
   otro grupo. El área de pérdida o degradación depende de 4 puntos del estrato «no».

## Hallazgos con datos reales del curso

- ALOS-1 PALSAR FBS de 2011 es **sólo HH**: el HV de 2011 existe sólo en escenas FBD.
- NovaSAR 50896 (22/12/2023) cubre el **51 %** de `C_FEDERAL` (y no cubre
  Concordia, aunque tenga la misma hora de pasada que la 47942).
- NISAR: sin la máscara del producto aparecen valores de **−133 dB** en los
  bordes de la pasada.
- GEDI L2A V003: el campo de calidad es `l2a_quality_flag_rel3` (no
  `quality_flag`); **no hay adquisiciones entre el 17/03/2023 y el 26/04/2024**.
