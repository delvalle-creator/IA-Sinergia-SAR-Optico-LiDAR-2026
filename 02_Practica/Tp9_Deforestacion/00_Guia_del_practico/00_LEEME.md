# Tp9 — Guía paso a paso

Viernes, 9 a 12 h. Sitio `C_FEDERAL`.
Grilla común EPSG:32721 (UTM 21 S), **20 m**.

Antes de empezar, en el **Miniforge Prompt**:

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp9_Deforestacion\03_Scripts
```

Distribución sugerida del tiempo:

| Horario | Paso |
|---|---|
| Antes de la clase | Leer el contexto (MapBiomas, CCI Biomass y banda P) del desarrollo: ampliación optativa |
| 9:00–9:10 | Paso 0. Comprobar insumos |
| 9:10–9:40 | Paso 1. Pila temporal y calibración cruzada |
| 9:40–10:10 | Paso 2. Qué estrato ve cada banda (sinergia) y degradación con GEDI |
| 10:10–10:55 | Paso 3. Entrenamiento en QGIS |
| 10:55–11:20 | Paso 4. Fusión de rasgos y control con GEDI |
| 11:20–12:00 | Paso 5. Tp4_02, lectura de variantes y preguntas (el etiquetado y Tp4_03 van fuera de horario) |

Rótulos de las secciones: **En clase** (pasos 0 a 4, control con SAOCOM y Tp4_02),
**Fuera de horario** (etiquetado, Tp4_03 y Tp4_04) y **Ampliación (optativa)**
(contexto MapBiomas, CCI y banda P; GEDI L2B y L4A; embeddings AlphaEarth; Sentinel-1
sin procesar). Las ampliaciones no entran en la rúbrica salvo la pregunta 11 (SAOCOM).

**Landsat 8 y 9.** Escenas de este práctico, la pasada más cercana a cada Sentinel-2 con el sitio cubierto y despejado: Federal, `C_FEDERAL_L8_20210807`, `C_FEDERAL_L8_20250919` y `C_FEDERAL_L9_20260914`: Landsat 8 del 07/08/2021 y del 19/09/2025 y Landsat 9 del 14/09/2026, para los Sentinel-2 del 06/08/2021, del 24/09/2025 y del 16/09/2026.

Son Colección 2, Nivel 2 de USGS (reflectancia y temperatura de superficie, píxel de 30 m), bajadas del Planetary Computer. Están en `02_Subsets_SNAP_QGIS\SNAP_DIMAP` y `QGIS_GeoTIFF`, con las bandas `SR_B1` a `SR_B7` (reflectancia), `ST_B10` (temperatura, K), `ST_QA`, `QA_PIXEL` y las virtuales `NDVI` y `ST_B10_C` (°C).

Landsat 9 da imágenes desde el 31/10/2021; antes sólo hay Landsat 8. Los dos llevan instrumentos gemelos (OLI y TIRS) y se comparan entre sí sin ajuste. Con Sentinel-2 no: el píxel es de 30 m contra 10 y 20 m, y las bandas no coinciden del todo (el infrarrojo cercano de Landsat, 865 nm, equivale a la B8A, no a la B08).

Fuente: USGS / NASA, Landsat 8 y Landsat 9 OLI/TIRS, Colección 2 Nivel 2, distribuido por Microsoft Planetary Computer, https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2

**Fusión Landsat + Sentinel-2.** El Landsat también viene afinado a 10 m con el detalle espacial del Sentinel-2 de la fecha más cercana: se lo interpola a la grilla de 10 m y se le suma el detalle fino de la banda Sentinel-2 de 10 m que más se le parece, escalado por una regresión entre los dos sensores (filtro pasa-altos con modulación por regresión, HPF). Trae las bandas `SR_B1` a `SR_B7` en reflectancia, `mascara_detalle` (1 = se agregó detalle; 0 = nube, sombra o falta de dato en alguna de las dos) y el `NDVI` virtual; el método y la calidad de cada banda están en los metadatos.

El control es el ERGAS: la imagen afinada se lleva de nuevo a 30 m y se compara con el Landsat original; por debajo de 3 la fusión es buena. Sirve para mirar e interpretar, con tres cuidados: un cambio real entre las dos fechas aparece como detalle falso; las bandas 6 y 7 (infrarrojo de onda corta) toman el detalle de una banda de 10 m de otra región del espectro y son las menos confiables; y la temperatura no se afina.

En este práctico: `C_FEDERAL_L8_20210807_fusion_S2_20210806_10m` (1 día; ERGAS 0,76; 70 % del sitio con detalle por las nubes), `C_FEDERAL_L8_20250919_fusion_S2_20250924_10m` (5 días; ERGAS 0,94; correlación entre los sensores de 0,4 a 0,7, así que agrega poco detalle) y `C_FEDERAL_L9_20260914_fusion_S2_20260916_10m` (2 días; ERGAS 0,77).

**Pléiades y Pléiades Neo de CONAE.** Referencia visual de muy alta resolución del casco urbano (Pléiades, 0,5 m; Pléiades Neo, 0,3 m), 2022-2023, del proyecto Impactar de CONAE. Es un servicio de mapas y necesita internet: en `02_Subsets_SNAP_QGIS\Pleiades_CONAE_WMS` hay un `.xml` por localidad que se arrastra a QGIS (instrucciones en el `LEEME.md` de esa carpeta). Sirve para mirar y digitalizar, no para calcular: es RGB color real, sin infrarrojo ni reflectancia, y la fecha exacta no está publicada, sólo el año.

En este práctico: Federal, Pléiades 2022 (`Federal_2022_Pleiades_CONAE.xml`); La Paz, Pléiades 2022, y Villaguay, Pléiades Neo 2023, en la franja La Paz-Villaguay.

Fuente: CONAE, proyecto Impactar; Pléiades y Pléiades Neo, Airbus Defence and Space. Servicio WMS: https://geotematico01.conae.gov.ar/geoserver/wms; catálogo: https://catalogos.conae.gov.ar/catalogo/catalogoGeoServiciosOGC.html

**CBERS-4A, cámara WPM (INPE).** Pancromática de 2 m y multiespectral de 8 m (azul, verde, rojo e infrarrojo cercano), producto L4 ortorrectificado, en números digitales. Cada escena viene en dos productos: `..._MS_8m` (las cuatro bandas originales) y `..._pansharpened_2m` (la pancromática y las cuatro bandas afinadas a 2 m por Brovey ponderado, el método por defecto de GDAL). Es un pansharpening clásico: pancromática y multiespectral del mismo satélite y del mismo instante; compárelo con la fusión Landsat + Sentinel-2, que combina dos sensores y dos fechas. El control es el mismo ERGAS (por debajo de 3, bueno). Los números digitales no son reflectancia y el Brovey altera la radiometría: sirve para mirar y digitalizar, no para calcular índices. Cubre una zona de 12 a 21 km, no el sitio entero, y la escena se eligió a ojo, sin nubes, porque el catálogo del INPE no informa la nubosidad.

En este práctico: Federal, ventana central de 16 × 16 km sobre el monte: `C_FEDERAL_CBERS4A_FEDERAL_20210802_...` (02/08/2021, 4 días antes del Sentinel-2; ERGAS 1,97) y `C_FEDERAL_CBERS4A_FEDERAL_20260905_...` (05/09/2026; ERGAS 1,02).

Fuente: INPE / CAST, CBERS-4A WPM L4, licencia CC BY 4.0. Catálogo STAC del INPE, colección CB4A-WPM-L4-DN-1, https://data.inpe.br/stac/browser/collections/CB4A-WPM-L4-DN-1

**Embeddings anuales AlphaEarth Foundations (Google y Google DeepMind).** 64 números por píxel de 10 m que resumen un año entero de Sentinel-1, Sentinel-2, Landsat, GEDI, clima y otras fuentes, aprendidos por un modelo de inteligencia artificial. Las dimensiones (`A00` a `A63`) no tienen significado físico propio: sirven para clasificar con pocas muestras, buscar zonas parecidas y detectar cambios entre años. Vienen en enteros de 8 bits tal como los entrega Google (`..._AlphaEarth_embeddings_<año>_10m`); para pasarlos a valores reales, valor = signo(DN) × (DN / 127,5)², y −128 es sin dato. El `..._CP1_CP2_CP3_RGB_8bit.tif` muestra las tres primeras componentes principales para mirar en QGIS; sus colores no tienen significado fijo. Resumen un año, no una fecha; 2026 todavía no existe y se usa 2025, el último.

En este práctico: Federal, 2021 y 2025 (2025 también en lugar de 2026).

Fuente: The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind (CC BY 4.0). Copia en Source Cooperative (Taylor Geospatial), https://source.coop/tge-labs/aef

---

## Paso 0. Comprobar insumos

**Qué y por qué.** El paso 1 lee la cobertura de control del Tp4 para calibrar
los sensores de banda L entre sí, y el paso 2 lee las huellas GEDI del Tp1. Si
faltan, conviene saberlo ahora.

Compruebe en el Explorador que existen:

- `..\..\Tp4_Validacion\02_Subsets_SNAP_QGIS\C_FEDERAL_cobertura_control_20m.tif`
- `..\..\Tp1_Convergencia\05_Resultados\03_Vectores\lidar_C_FEDERAL.gpkg`
- el `.tif` de ALOS-1 en `00_COMUN\08_Originales_crudos\ASF\C_FEDERAL\ALOS\AP_27336_FBS_F6560_RT1\` y el `.h5` de NISAR del 17/09/2026 en `00_COMUN\08_Originales_crudos\NISAR\`.

**Si falta la cobertura de control.** Desde `...\Tp4_Validacion\03_Scripts`:

```
python Tp4_01_cobertura_de_control.py --sitio C_FEDERAL --pixel 20
```

La zona estable del Tp9 usa la clase **3 (monte nativo)** y la **7 (urbano)**.
Para que la clase 3 sirva, el monte tiene que estar **confirmado sin cambio
2011–2026** en la imagen de muy alta resolución (con el historial de Google Earth
Pro, por ejemplo) y digitalizado en `control_digitalizado_C_FEDERAL.gpkg`. Si la
clase 3 vino de MapBiomas (banda 2 `fuente_control` del ráster), no está
confirmada: `Tp9_01` la deja fuera de la zona estable y lo dice en la bitácora
(desde el 23/10/2026). Si no digitalizó nada, la zona estable queda vacía y no se
calibra: digitalice o use `--solo_urbano` con polígonos urbanos.

**El control de partida del docente.** `control_digitalizado_C_FEDERAL.gpkg` trae
26 cuadrados de 100 m sorteados al azar (semilla 20261023): 14 de monte (copa de
la máscara CBERS-4A de 2 m ≥ 0,3 en 2021 y en 2026, con menos de 0,1 de
diferencia, bosque de MapBiomas en los 15 años 2011–2025 y revisión a ojo en las
dos imágenes CBERS; de 20 sorteados se descartaron 6 por bordes, claros o un
camino nuevo) y 12 urbanos (sorteo estratificado dentro de la clase 24 de
MapBiomas en los 15 años, revisados en el Sentinel-2 de 2026). El 2011 no se pudo
mirar en alta resolución: lo confirma sólo MapBiomas. Revíselos y agregue los
suyos.

---

## Paso 1. Pila temporal y calibración cruzada

**Qué y por qué.** Todas las capas en la misma grilla de 20 m, el radar en
**lineal** (γ⁰; σ⁰ en NovaSAR, que el producto no permite otra cosa):

| Capa | Fuente | Cómo entra |
|---|---|---|
| `L_ALOS2_2021_HH`, `_HV` | mosaico anual JAXA (Planetary Computer) | automático; DN → γ⁰ = DN² · 10^(−8,3), el cuadrado antes de remuestrear |
| `L_ALOS1_2011_HH` | ALOS PALSAR FBS RTC de ASF (γ⁰ en potencia) | `--alos1_hh` |
| `L_NISAR_2026_HH`, `_HV` | NISAR GCOV, frecuencia A, con la máscara del producto | `--nisar_h5` |
| `C_S1_2021_VV`, `_VH`, `C_S1_2026_VV`, `_VH` | Sentinel-1 RTC (Planetary Computer) | automático, `--fechas_c` |
| `S_NovaSAR_2023_sigma0_HH` | NovaSAR 50896 | automático, `--novasar` |
| `O_NDVI_2021`, `O_NDVI_2026` | Sentinel-2 L2A, sólo píxeles válidos de la SCL | automático, `--fechas_opt` |

Una capa entra sólo si tiene dato en más del 5 % del sitio.

**FBS es una sola polarización.** ALOS-1 FBS de 2011 es **sólo HH**; el HV de
2011 existe sólo en escenas FBD. La comparación histórica 2011–2021 se hace en
HH y se declara.

**Calibración cruzada.** ALOS-1, ALOS-2 y NISAR son instrumentos distintos.
Antes de restar sus γ⁰, se mide en la zona estable

`desfase = mediana(γ⁰_ALOS2_dB − γ⁰_otro_dB)`

y se corrige el otro producto multiplicando por 10^(desfase/10). La referencia es
ALOS-2 2021. El desfase se corrige. Lo que limita la interpretación es el residuo
después de corregir: Tp9_01 lo mide por separado en monte y en ciudad, en la mitad de
los cuadrados no usada para calibrar (semilla fija, `--semilla`). En Federal, el
desfase de NISAR HV es −1,60 dB en el monte y −0,45 dB en la ciudad: un ajuste único no
vale para todo el sitio. El cambio mínimo interpretable es aproximadamente el p75 del
residuo absoluto (columna `residuo_p75_abs_dB`).

**Orden:**

```
python Tp9_01_pila_temporal.py --pixel 20 --puntos_enlace todos --desplazamiento -60 10 ^
  --alos1_hh ..\..\00_COMUN\08_Originales_crudos\ASF\C_FEDERAL\ALOS\AP_27336_FBS_F6560_RT1\AP_27336_FBS_F6560_RT1_HH.tif ^
  --nisar_h5 ..\..\00_COMUN\08_Originales_crudos\NISAR\NISAR_L2_PR_GCOV_030_161_A_162_2005_DHDH_A_20260917T095508_20260917T095543_P05023_N_F_J_001.h5
```

Argumentos y valores por defecto: `--pixel 20`, `--alos1_hh` y `--alos1_hv`
(vacíos), `--nisar_h5` (vacío), `--fechas_c 2021-08-10 2026-09-14`,
`--fechas_opt 2021-08-06 2026-09-16`, `--anio_alos2 2021`, `--novasar 50896`,
`--solo_urbano` (apagado), `--desplazamiento 0 0`, `--puntos_enlace esquinas`,
`--semilla 20261027`.

**El desfase de NovaSAR.** La escena 50896 viene georreferenciada sólo con cuatro
puntos de esquina. Si midió su corrimiento con `Tp3_02` (que al final imprime la
orden lista `--desplazamiento DX DY`), páselo aquí: DX positivo = este, DY
positivo = norte, en metros (por ejemplo, 80 m al oeste y 20 m al norte es
`--desplazamiento -80 20`). Sin él, la bitácora avisa `AVISO: NovaSAR sin
--desplazamiento (georreferencia de 4 puntos). Medir con Tp3_02.` El desfase
importa en el paso 2: decide qué píxel de banda S cae en cada huella GEDI.

Con `--puntos_enlace todos` el programa usa los 84 puntos de enlace del
`metadata.xml` en lugar de las cuatro esquinas (como en el Tp8). Así el
corrimiento queda chico y rígido: medido contra el infrarrojo cercano del
Sentinel-2 del 16/09/2026 en 10 ventanas, 60 m al oeste en todas y entre 0 y 20 m
al norte, de ahí `--desplazamiento -60 10`. Con las cuatro esquinas el corrimiento
es de cientos de metros y cambia dentro de la escena.

**Qué debe observar.** Por bloque (Banda L, C, S, Óptico) cada capa con su % de dato.
NovaSAR 50896 debería rondar el 51 % (es lo que cubre del sitio). Después, la
zona estable usada (clases y píxeles) y el desfase de cada producto de banda L
respecto de ALOS-2. Al final, la ruta de la pila y el número de capas.

Salidas: `02_Subsets_SNAP_QGIS/C_pila_temporal_20m.tif` y
`05_Resultados/04_Tablas/C_calibracion_cruzada.csv` (`referencia`, `producto`, `zona`,
`desfase_dB`, `RIC_desfase_dB`, `pixeles_estables`, `residuo_p75_abs_dB`, `aplicado`, `aviso`).

**Control.**

1. Lea `C_calibracion_cruzada.csv`: ¿el desfase cambia entre monte y ciudad? Anote
   el rango intercuartil del desfase y el residuo (p75) de cada par.
2. En QGIS, abra la pila. `Propiedades > Simbología > Color multibanda`: R =
   `L_NISAR_2026_HV`, G = `L_ALOS2_2021_HV`, B = `L_ALOS2_2021_HV`, con la misma
   escala en las tres (fije mínimo y máximo a mano). Donde se perdió monte entre
   2021 y 2026, el HV cae en 2026: el píxel se ve cian. **Fije la escala a mano**:
   si cada canal se estira solo, el desfase entre sensores aparece como cambio.
3. Si no hubo cobertura de control, el script escribe «NO se calibra y se
   declara». No interprete diferencias de banda L sin calibrar.

**Errores típicos.**

- `NISAR: El granulo ... no cubre el sitio C_FEDERAL`: el `.h5` es de otra pasada.
- `NovaSAR: No encuentro el GRD de la escena 50896`: disco con otra letra
  (`set CURSO_SAR_NOVASAR=...`).
- `Sin Sentinel-1 RTC el ...` o `Sin Sentinel-2 el ...`: no hay escena ese día
  exacto. Pase otra fecha con `--fechas_c` o `--fechas_opt` y anótela.
- HTTP 403 a mitad de la corrida: venció la firma de las URL. Vuelva a correr.

---

## Paso 2. Qué estrato ve cada banda (SINERGIA) y degradación con GEDI

**Qué y por qué.** Cada banda interactúa con objetos de tamaño parecido a su
longitud de onda: la **C** (5,5 cm) con hojas y ramitas de la copa; la **S**
(9,4 cm) con ramas finas; la **L** (≈ 24 cm: ALOS-2 24,2 cm, NISAR 23,8 cm) con ramas
gruesas y troncos; la
**P** (69 cm) con troncos y suelo. GEDI mide la estructura (rh98 = altura bajo la
cual queda el 98 % de la energía devuelta). En cada huella GEDI válida se toma el
valor de cada capa y se mide:

- la **correlación de Spearman** (de rangos: no supone relación lineal) entre la
  banda (en dB) y rh98;
- la **curva de respuesta**: mediana de la banda por clase de altura (0–2, 2–5,
  5–8, 8–12, 12–16 y más de 16 m), con el número de huellas de cada clase. El rango
  de la curva usa sólo las clases con al menos 100 huellas (`--min_huellas_clase`).
  Donde la curva se aplana, la banda **satura**;
- el **intervalo de confianza de ρ** por remuestreo de celdas de 200 m (500
  repeticiones, semilla fija): con miles de huellas vecinas el p-valor no informa.

Compare las bandas en la misma polarización (L HV con C VH; L HH con C VV): si no, el
efecto de la longitud de onda se mezcla con el de la polarización.

Nada se fusiona: cada banda se evalúa por separado. El resultado justifica qué
rasgos entran al paso 4.

**Fecha.** Las huellas GEDI son de 2019–2023 y 2024–2025; la pila mezcla 2011,
2021, 2023 y 2026. Sólo se usan huellas a menos de `--dias_max` (730 días)
del 1 de julio del año de cada capa. **ALOS-1 2011 no tiene huellas GEDI
cercanas** (GEDI empezó en 2019): no se evalúa, y es lo esperable.

**Parte C — degradación.** GEDI no repite huellas. Se compara la mediana de rh98
por **celda de 200 m** entre el período 1 (hasta el 31/12/2022) y el período 2
(desde el 26/04/2024, cuando GEDI volvió a adquirir). Celda candidata a
degradación si: antes era monte (rh98 ≥ 5 m), bajó 3 m o más, y el NDVI no cambió
(|ΔNDVI| < 0,05). Exige al menos 2 huellas por período en la celda. El ΔNDVI por
defecto es 2026 − 2021 y el período 2 de GEDI termina el 28/06/2025: con `--ndvi_p2`
puede usar el Sentinel-2 del 24/09/2025 (`QGIS_GeoTIFF\C_FEDERAL_S2_20250924_NDVI.tif`);
declare cuál usó.

**Orden:**

```
python Tp9_02_sinergia_estratos.py --pixel 20
```

Argumentos y valores por defecto: `--pixel 20`, `--dias_max 730`, `--p_tif`
(`02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\C_FEDERAL_BIOMASS_P_20260812.tif`), `--p_fecha 2026-08-12`,
`--p_sitio C_FEDERAL`, `--p_en_db` (apagado), `--sin_p` (apagado), `--p1_hasta 2022-12-31`, `--p2_desde 2024-04-26`,
`--celda 200`, `--monte_min 5`, `--u_rh98 -3`, `--u_dndvi 0.05`, `--rh98_max 60`
(20 m es lo plausible en el Espinal), `--min_huellas_clase 100`, `--bootstrap 500`,
`--semilla 2026`, `--ndvi_p1` y `--ndvi_p2` (vacíos: primera y última capa NDVI de la pila).

**Parte B, banda P (BIOMASS de Federal).** La misma orden la hace sola: toma el
γ⁰ HH, HV, VH y VV del BIOMASS L1B del 12/08/2026 recortado al sitio
(`C_FEDERAL_BIOMASS_P_20260812.tif`) y lo compara con las **mismas huellas GEDI de
Federal** que la C y la L, con el mismo filtro de fecha (`--dias_max`, ahora
respecto del 12/08/2026). Ese GeoTIFF está en geometría de radar, sin proyectar: el
programa lo ubica con sus 121 puntos de control y lo dice en la bitácora. En QGIS
mírelo con el RGB `RGB_copol_cruzada_cociente\C_FEDERAL_BIOMASS_P_20260812_RGB_8bit.tif`
(R = HH, G = VH, B = HH/VH). La cruzada es VH: la HV de esta escena tiene interferencia
de radiofrecuencia sin corregir. Su corrimiento, medido por bordes contra el Sentinel-2,
es de unos 13 m (menos de un píxel). Con `--sin_p` se omite la parte B.

**Parte B con la franja D (opcional).** La franja La Paz – Villaguay tiene muchas
más huellas GEDI que Federal. Para usarlas, la banda P del 17/09/2026 ya está
reproyectada a la grilla del curso (EPSG:32721, 25 m), con la ubicación de cada
píxel tomada de la tabla del producto; cubre el 56 % de la franja:

```
python Tp9_02_sinergia_estratos.py --pixel 20 --p_tif ..\02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\D_LAPAZ_VILLAGUAY_BIOMASS_P_20260917_S1_UTM21S.tif --p_fecha 2026-09-17 --p_sitio D_LAPAZ_VILLAGUAY
```

El programa toma las huellas GEDI válidas de `lidar_D_LAPAZ_VILLAGUAY.gpkg` (Tp1).
La banda P queda evaluada en la franja D y la C y la L en Federal: se compara la
**forma** de las curvas, no los valores. Esta orden reescribe la tabla y la
bitácora de la parte B.

**Qué debe observar.**

1. «Huellas GEDI válidas dentro de la pila: N (fecha mínima a fecha máxima)».
2. Una línea por capa: huellas usadas, ρ de Spearman y rango de la curva (dB o
   NDVI); las capas con menos de 20 huellas cercanas: «no se evalúa».
3. La figura `05_Resultados/05_Graficos/C_curvas_de_respuesta.png`: radar de Federal y, si se corrió la parte B, un segundo panel con la banda P.
4. Parte C: huellas por período, celdas con ≥ 2 huellas en cada uno y número de
   candidatas a degradación.

Salidas: `05_Resultados/04_Tablas/C_sensibilidad_a_la_altura.csv`,
`05_Resultados/05_Graficos/C_curvas_de_respuesta.png`,
`05_Resultados/04_Tablas/C_delta_rh98_por_celda.csv` y
`02_Subsets_SNAP_QGIS/C_delta_rh98_20m.tif` (bandas `delta_rh98_m` y
`candidato_degradacion`).

**Control.**

1. En la figura, ¿qué curva sigue subiendo hasta las clases altas y cuál se
   aplana pronto? Eso es lo que dice la física; si sale al revés, revise fechas
   y número de huellas antes de concluir.
2. Una ρ alta con pocas huellas no vale lo mismo que con muchas: lea la columna
   `huellas`.
3. La caída de rh98 menor de 3 m está cerca del ruido del instrumento. GEDI no
   adquirió entre el 17/03/2023 y el 26/04/2024.
4. Abra `C_delta_rh98_20m.tif` en QGIS sobre el CBERS-4A de 2 m si la celda cae en
   la ventana central; si no, sobre Sentinel-2 de 10 m (o la fusión Landsat +
   Sentinel-2), y anote la resolución usada. Mire dos celdas candidatas. ¿Se ve
   raleo, picadas, extracción de leña?

**Errores típicos.**

- `Falta ...lidar_C_FEDERAL.gpkg`: corra `Tp1_05_buscar_lidar.py --sitio C_FEDERAL --descargar` (es largo: debería venir hecho).
- «No hay celdas con huellas en los dos períodos: ampliar --celda y declararlo».
  Pruebe `--celda 400` y dígalo.

---

## Paso 3. Entrenamiento (EN QGIS)

**Qué y por qué.** Cuatro clases:

| `codigo` | Clase | Qué es |
|---|---|---|
| 1 | pérdida | desmonte de un lote: hoy suelo o cultivo donde había monte |
| 2 | degradación | sigue habiendo cobertura arbórea, pero rala o raleada; incluye aperturas lineales nuevas (picadas, caminos, cortafuegos) |
| 3 | monte estable | monte sin cambio visible 2021–2026 |
| 4 | no bosque estable | cultivo, pastura, ciudad |

La clase 4 **debe incluir cultivos cosechados** entre fechas: un cultivo
cosechado baja el NDVI y no es desmonte. Es el control del práctico.

**La capa.** `04_Tablas_de_trabajo/entrenamiento_C.gpkg` (capa `entrenamiento`,
campos `codigo`, `clase` y `criterio`) trae 70 polígonos de partida hechos sobre
la imagen de alta resolución CBERS-4A fusionada a 2 m del 02/08/2021 y del
05/09/2026 (`02_Subsets_SNAP_QGIS\QGIS_GeoTIFF`), con sorteo al azar y revisión
a ojo en las dos fechas: 38 de monte estable, 26 de no bosque estable, 3 de
degradación (picadas nuevas en el monte) y 3 de pérdida (un desmonte junto a un
puesto y dos tramos de un camino nuevo de unos 25 m de ancho, con el contorno de la
máscara de cambio a 2 m). Regla: aperturas lineales (caminos, picadas, cortafuegos) =
degradación; desmonte de un lote = pérdida. Por esa regla los dos tramos del camino
pasaron a degradación (27/10/2026): la capa queda con 1 de pérdida y 5 de degradación.
El desarrollo muestra además una corrida con el entrenamiento ampliado del docente
(`entrenamiento_C_ampliado.gpkg`: 8 de pérdida sorteados en la pérdida de
MapBiomas 2022–2025 y 7 de degradación) y su tabla «antes / después». Los demás son cuadrados de 60 m. El campo `criterio` dice qué se
vio y `origen` de qué sorteo salió cada uno (100 puntos uniformes, completado
estratificado con la fracción de copa de 2 m, o búsqueda de aperturas nuevas).
Dentro de la ventana CBERS (16 × 16 km del centro de Federal) casi no hubo
desmonte entre 2021 y 2026: de los 100 puntos uniformes ninguno cayó en una
pérdida, y la mayoría de las «aperturas» automáticas eran caminos que ya estaban
o diferencias de iluminación. Por eso pérdida y degradación tienen tan pocos
polígonos: son el trabajo del grupo. Son un borrador, no verdad de campo: con
ellos `Tp9_03` da una exactitud fuera de bolsa de 0,89 (optimista). La capa vacía está en `entrenamiento_C_vacio.gpkg`: para empezar de
cero, cópiela sobre `entrenamiento_C.gpkg`. Si `entrenamiento_C.gpkg` no existe,
la primera corrida del paso 4 la crea vacía y termina; ya escribe las variantes
de un solo sensor:

```
python Tp9_03_fusion_perdida_degradacion.py --pixel 20
```

**En QGIS.** Abra la capa y `Conmutar edición`. Revise cada polígono con la
imagen de muy alta resolución (con su historial de fechas), el NDVI de 2021 y
2026 y el HV de banda L de la pila: borre los que estén mal (`Borrar
seleccionados`), corrija `codigo` y `clase` de los que sean de otra clase, mueva
los que toquen un borde (`Herramienta de vértices`) y agregue con `Añadir
polígono` los que falten, sobre todo de pérdida, de degradación y cultivos
cosechados en la clase 4 (los de partida casi no tienen). Fuera de la ventana
CBERS use la imagen de muy alta resolución de QGIS y el NDVI de la pila. Las
máscaras de copas de 2 m de las dos fechas
(`C_FEDERAL_copa_CBERS4A_2m_<fecha>.tif`) ayudan a ver dónde había árboles. En los polígonos que cambie o agregue, escriba en `criterio`
de dónde sale (por ejemplo, «grupo: Pléiades 2023 y NDVI»). Al menos 10
polígonos por clase, repartidos en el sitio. Guarde.

**Polígonos al azar.** Los polígonos que agregue se trazan al azar, no donde la clase se ve más fácil. `Vectorial > Herramientas de investigación > Puntos aleatorios en la extensión` (Random Points in Extent), con la extensión del sitio y 100 puntos. Recorra los puntos en el orden en que salieron (campo `id`) y trace un polígono alrededor de cada punto que caiga en una cubierta inequívoca, hasta completar el número pedido para cada clase; los puntos que caen en bordes o en cubiertas dudosas se saltean y se anotan. Elegir los lugares a ojo concentra los polígonos en los ejemplos más típicos y hace que el mapa parezca mejor de lo que es. Con 100 puntos uniformes las clases raras (las que ocupan pocas hectáreas: monte cerrado, suelo desnudo, severidad alta) casi nunca se completan. Para esas clases, haga un **sorteo estratificado**: convierta a polígono el estrato de la clase (`Ráster > Conversión > Poligonizar` sobre MapBiomas, o sobre el rango del índice que define la clase) y use `Vectorial > Herramientas de investigación > Puntos aleatorios dentro de polígonos`; recorra esos puntos también en el orden en que salieron, con la misma revisión en la imagen. Anote de qué sorteo salió cada polígono. Los 70 polígonos de partida ya están sorteados así: 100 puntos uniformes en la ventana CBERS, revisados a ojo en 2021 y 2026 (32 de monte, 10 de no bosque, 1 de degradación y 57 descartados por mezcla, arbustal ralo, borde o cambio dudoso), y un completado estratificado con la fracción de copa de 2 m para monte y no bosque; pérdida y degradación salen de una búsqueda de aperturas nuevas confirmadas a ojo. La lista de todos los puntos mirados está en `00_COMUN\09_Herramientas\desarrollo_docente\sorteos\Tp9\Tp9_puntos_revisados_CBERS.csv`.

**Errores típicos.** Pocos polígonos de degradación (es la clase difícil): mejor
pocos y seguros que muchos dudosos. Polígonos de una clase todos juntos en un
rincón. Dejar los polígonos de partida sin revisar ni agregar: con sólo 3 polígonos de
pérdida y 3 de degradación, todos en la ventana CBERS, el mapa no aprende esas
clases en el resto del sitio. Usar una capa de cobertura global (WorldCover,
MapBiomas) como polígonos sin mirarlos en la imagen de alta resolución: copia su
regla y su escala de 10 a 30 m.

---

## Paso 4. Pérdida y degradación (FUSIÓN DE RASGOS) y control con GEDI

**Qué y por qué.** Cada sensor aporta un rasgo de cambio o de nivel:

| Rasgo | Cálculo | Qué aporta |
|---|---|---|
| `dHV_L` | 10 log10(L_2026 / L_2021): NISAR HV frente a ALOS-2 HV. Si NISAR no trae HV, se calcula en HH y se llama `dHH_L` | Pérdida de volumen leñoso reciente |
| `HV_L_actual_dB` | NISAR 2026 en dB (`HH_L_actual_dB` si no hay HV) | Nivel actual: separa no-bosque de bosque perdido |
| `dHH_L_hist` | 10 log10(L_2021 / L_2011): ALOS-2 HH frente a ALOS-1 HH | Cambio histórico |
| `dVH_C` | 10 log10(VH_2026 / VH_2021) | Cambio de copa |
| `dNDVI` | NDVI_2026 − NDVI_2021 | Cambio de verdor |
| `NDVI_actual` | NDVI 2026 | Nivel actual |

Los cocientes se calculan en **lineal** y se expresan en dB. Δrh98 **no entra**
por defecto: sólo existe en las celdas con huellas y el mapa quedaría agujereado;
se usa como **control independiente**. Con `--rh98_como_rasgo` entra, y el mapa
se limita a esas celdas (se declara).

**Orden:**

```
python Tp9_03_fusion_perdida_degradacion.py --pixel 20 --u_ndvi -0.10 --u_hv -1.5
```

Valores por defecto: `--pixel 20`, `--u_ndvi -0.10`, `--u_hv -1.5`,
`--rh98_como_rasgo` apagado. Opciones nuevas para comparar (no cambian nada si no se
escriben): `--sin_equilibrar` (entrena sin equilibrar las clases; por defecto se
equilibran con el mismo número de píxeles por clase y `class_weight="balanced"`, lo que
infla la degradación), `--sin_historico` (sin `dHH_L_hist`; el mapa cubre también el
rincón sin ALOS-1), `--mascara_monte_2021` (las tres variantes valen «no» fuera del monte
de MapBiomas 2021), `--entrenamiento` (otra capa) y `--sufijo` (para no pisar las salidas).

**Qué debe observar.** Cómo se calculó cada rasgo, la exactitud fuera de bolsa
(OPTIMISTA), la importancia de cada rasgo, las hectáreas por clase y la tabla de
control: Δrh98 (mediana y media) por clase del mapa. Se espera Δrh98 negativo en
pérdida y degradación, cerca de cero en monte estable. El `count` son píxeles,
no celdas: cada celda GEDI cubre muchos píxeles.

Salidas en `05_Resultados/02_Rasters/`: `C_perdida_degradacion.tif` (bandas
`clase` y `probabilidad`), `C_variante_multisensor.tif` (1 pérdida o
degradación, 2 no), `C_variante_optico.tif` (ΔNDVI < −0,10), `C_variante_L.tif`
(`dHV_L` < −1,5 dB, o `dHH_L` si no hubo HV de NISAR); `05_Resultados/04_Tablas/C_control_gedi_por_clase.csv`;
`05_Resultados/05_Graficos/C_perdida_degradacion.png`.

**Control.**

1. Superponga `C_perdida_degradacion.tif` y `C_variante_optico.tif` sobre la
   imagen: los lotes agrícolas cosechados, ¿quedaron como «no bosque estable» en
   el mapa multisensor y como «pérdida» en la variante óptica?
2. Compare las celdas candidatas del paso 2 con la clase del mapa en esas celdas.
3. Las hectáreas por clase son **conteo de píxeles**, no área estimada: el área
   con su intervalo de confianza sale del Tp4.
4. El umbral `--u_hv -1.5` sólo tiene sentido si supera el residuo de la calibración
   en el monte; en Federal el desfase del monte en HV (1,60 dB) ya es mayor que 1,5 dB:
   la variante L puede marcar como pérdida una diferencia de calibración.

---

**Control con SAOCOM (EN QGIS).** El ΔHV del modelo compara dos sensores (NISAR 2026 y el mosaico ALOS-2 2021). CONAE entregó dos SAOCOM del mismo haz sobre Federal, 04/08/2021 y 11/09/2026, ya en γ⁰ lineal a 20 m: `02_Subsets_SNAP_QGIS\SAOCOM_gamma0\QGIS_GeoTIFF\C_FEDERAL_SAOCOM_L_<fecha>_QP_gamma0_Gamma0_HV.tif`.

1. Calculadora ráster: `10 * log10("..._20260911_..._Gamma0_HV@1") - 10 * log10("..._20210804_..._Gamma0_HV@1")`.
2. Mire el histograma (`Propiedades > Histograma`): la mediana no es 0. Entre las dos fechas todo el sitio subió unos 2,4 dB. SAOCOM-1A y 1B son gemelos (mismo haz, mismo procesamiento): no hace falta calibrarlos contra otro sensor, pero sí normalizar ese desfase restando la mediana del sitio, lo que supone que la mayor parte del sitio no cambió.
3. Compare con la pérdida y la degradación de su mapa: ¿los desmontes caen también en SAOCOM? ¿Y el salpicado de degradación?

Referencia del docente: con la mediana restada, cae más de 3 dB el 66 % de la pérdida del mapa multisensor, el 13 % de la degradación y el 3 % del monte estable; con NISAR frente a ALOS-2, el 96, el 54 y el 10 %. La comparación con NISAR frente a ALOS-2 no es un control: es el rasgo `dHV_L` con que se entrenó el mapa. La cifra la calcula una herramienta del docente (`00_COMUN\09_Herramientas\des_saocom_comparaciones.py`): el alumno lee `05_Resultados\04_Tablas\C_SAOCOM_cambio_HV_por_clase.csv` y no la corre.

**Referencia del docente del paso 4.** Mapa con los polígonos de partida: pérdida 506 ha, degradación 11.250 ha, monte estable 112.553 ha, no bosque estable 46.700 ha (conteo de píxeles); exactitud fuera de bolsa 0,890 (optimista); importancias dHV_L 0,239, dNDVI 0,219, HV_L_actual_dB 0,217, NDVI_actual 0,177, dHH_L_hist 0,090, dVH_C 0,058. Δrh98 mediano por clase: pérdida −0,33 m (296 píxeles en 39 celdas), degradación +0,27 m, monte estable +0,29 m, no bosque +0,33 m. Sin equilibrar: 663 ha de pérdida y 3.378 ha de degradación.

## Paso 5. Variantes para el Tp4

Desde `...\Tp4_Validacion\03_Scripts`, para cada variante (`C_variante_optico`,
`C_variante_L`, `C_variante_multisensor`):

```
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp9_Deforestacion\05_Resultados\02_Rasters\C_variante_multisensor.tif --banda 1
python Tp4_03_exactitud_y_area.py --nombre C_variante_multisensor --nombres_clase "1=perdida_o_degradacion,2=no"
python Tp4_04_tabla_de_variantes.py --tp Tp9 --clase perdida_o_degradacion ^
  --variante "Solo optico|Sentinel-2|C_variante_optico" ^
  --variante "Solo banda L|ALOS-2 + NISAR|C_variante_L" ^
  --variante "Multisensor|L + C + optico|C_variante_multisensor"
```

El etiquetado al azar de tres variantes no entra en este bloque de tres horas. En
clase, deje corrido al menos `Tp4_02` para la multisensor; el etiquetado y `Tp4_03`
se completan fuera del horario (repártanse una variante por grupo). Si no se llega,
la entrega lo declara: el mapa va sin exactitud. En «datos usados» de la
multisensor va lo que realmente entró al Random Forest: L + C + óptico (la banda S
sólo se evaluó en la sinergia del paso 2).

**Referencia del docente del paso 5.** La referencia es 1 si el píxel era monte en 2021 y en 2026 está desmontado, raleado o atravesado por una picada nueva; 2 en cualquier otro caso. Multisensor: exactitud global 0,904 ± 0,035; comisión 0,889 ± 0,104; omisión 0,821 ± 0,197; área 7.316 ± 5.932 ha. Ese área depende de 4 puntos positivos del estrato «no», cada uno de los cuales pesa 1.502 ha: con 75 y 75 puntos el IC empeoraría; lo que lo achica es engrosar el estrato «no». Sólo con confianza alta y media: comisión 0,963 ± 0,073 y área 5.991 ± 6.270 ha.

**Errores típicos del paso 5.** Leer la exactitud global: con una clase del 7 % del sitio, un mapa que no acierta ninguna pérdida da 0,93. Lea la comisión y la omisión de la clase de interés. Etiquetar los puntos propios: cada grupo etiqueta los puntos de otro grupo.

## Paso opcional. Del Sentinel-1 sin procesar a γ⁰ — EN SNAP (ampliación optativa)

**Qué y por qué.** Todos los Sentinel-1 de este práctico vienen ya corregidos: son el γ⁰ RTC del Planetary Computer. Este paso muestra de dónde sale ese γ⁰. Se parte del producto GRDH de nivel 1 tal como lo entrega ESA, el `.zip` con la carpeta `.SAFE` adentro (mediciones, anotaciones, calibración, ruido y órbita predicha), y se recorre en SNAP la misma cadena que usó el docente. El resultado del docente viene hecho y sirve para controlar el suyo.

**Insumos.** En `00_COMUN\08_Originales_crudos\S1_CRUDO\`: para Federal, `S1C_IW_GRDH_1SDV_20260914T091317_20260914T091342_009441_012C7A_AB47.zip`; para La Paz–Villaguay, ese mismo cuadro y el siguiente de la misma pasada, `S1C_IW_GRDH_1SDV_20260914T091342_20260914T091407_009441_012C7A_4769.zip` (Sentinel-1C IW GRDH, VV + VH, 14/09/2026). Se eligió esa pasada porque tiene Landsat 9 del mismo día y Sentinel-2 dos días después (16/09/2026), y es tres días anterior a NISAR (17/09/2026). La Paz–Villaguay necesita los dos cuadros: es el ejercicio de unión de cuadros.

**Lo que viene hecho.** `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo` de este práctico: `SNAP_DIMAP` (γ⁰ VV y VH lineales, bandas virtuales en dB y cociente VV/VH en dB, metadatos completos), `QGIS_GeoTIFF` (con `_metadatos.txt`), `RGB_copol_cruzada_cociente` (R = VV, G = VH, B = VV/VH) y `Grafos_SNAP` (el grafo XML). El detalle está en `LEEME_S1_crudo.md` de esa carpeta.

**Dónde.** SNAP Desktop. La primera vez SNAP baja la órbita precisa y el Copernicus DEM, así que necesita internet. Hay dos formas de hacerlo.

**Forma rápida: el grafo del docente.**

1. `Tools > GraphBuilder`, botón `Load`, y elija `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\Grafos_SNAP\Grafo_C_FEDERAL_S1_20260914_gamma0_desde_crudo.xml`.
2. Recorra las pestañas: cada una es un paso de la cadena, con los parámetros que se usaron.
3. En la pestaña `Write`, cambie el nombre y la carpeta de salida a `05_Resultados\02_Rasters`, para no pisar el producto del docente. Botón `Run`.

**Forma completa: paso a paso con los menús.** Cada operador escribe un producto intermedio. En la ventana de cada uno, pestaña `I/O Parameters`, deje como entrada el producto anterior y guarde en `05_Resultados\02_Rasters`.

1. `File > Open Product…` sobre el `.zip` (no hace falta descomprimirlo). Para La Paz–Villaguay, abra los dos.
2. `Radar > Radiometric > S-1 Thermal Noise Removal`: quita el ruido térmico del instrumento, que pesa en VH y en las superficies oscuras, como el agua.
3. `Radar > Sentinel-1 TOPS > S-1 Remove GRD Border Noise` (límite de borde 500, umbral 0,5): quita las franjas de valores falsos de los bordes de la escena.
4. Sólo La Paz–Villaguay: `Radar > Sentinel-1 TOPS > S-1 Slice Assembly` con los dos cuadros ya sin ruido. El ruido se quita antes de unir porque cada cuadro trae sus propios vectores de ruido.
5. `Radar > Apply Orbit File`, tipo `Sentinel Precise (Auto Download)`: reemplaza la órbita predicha por la precisa.
6. `Radar > Radiometric > Calibrate`: en `Processing Parameters` marque sólo `Output beta0 band`. El aplanado necesita β⁰, no σ⁰.
7. `Raster > Subset…`, pestaña `Geo Coordinates`: recorte al sitio. Recortar antes del aplanado ahorra mucho tiempo y memoria.
8. `Radar > Radiometric > Terrain Flattening`, DEM `Copernicus 30m Global DEM`, remuestreo bilineal: pasa de β⁰ a γ⁰, normalizado por el área iluminada. Es el paso más lento.
9. `Radar > Speckle Filtering > Single Product Speckle Filter`, filtro `Refined Lee`.
10. `Radar > Geometric > Terrain Correction > Range-Doppler Terrain Correction`: DEM `Copernicus 30m Global DEM`, píxel de 10 m, proyección UTM automática (`AUTO:42001`, que en este sitio es la zona 21 S, la de la grilla del curso), formato BEAM-DIMAP.
11. Bandas en dB: clic derecho sobre cada banda γ⁰ > `Linear to/from dB`. Crea bandas virtuales y deja intactas las lineales.
12. Cociente: `Raster > Band Maths…`, expresión `Gamma0_VV_db - Gamma0_VH_db` (en dB, la resta es el cociente VV/VH).
13. RGB: `Window > Open RGB Image Window`, con R = `Gamma0_VV_db`, G = `Gamma0_VH_db` y B = el cociente.

**Qué debe observar.**

- Un producto con `Gamma0_VV` y `Gamma0_VH` en lineal y sus bandas virtuales en dB.
- En `Metadata > Processing_Graph`, la lista de operadores en el orden en que se aplicaron. Ahí queda escrito todo lo que se le hizo al dato.
- En `Metadata > Abstracted_Metadata`, la misión, la fecha, la órbita y el ángulo de incidencia del original: el recorte no los pierde.
- Abierto junto al producto del docente (el `.dim` de `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\SNAP_DIMAP`), los dos se superponen en `World View` y se ven casi iguales.

**Comparación con el RTC del Planetary Computer.** El mismo día existe el γ⁰ RTC del Planetary Computer, en `02_Subsets_SNAP_QGIS\SNAP_DIMAP\C_FEDERAL_S1_C_20260914.dim` de este práctico. Diferencia mediana del γ⁰ de SNAP menos el RTC, en todo el sitio:

- Federal, VV: −1,08 dB (p5 a p95, −3,7 a +1,6 dB; correlación 0,68).
- Federal, VH: −1,43 dB (p5 a p95, −4,2 a +1,3 dB; correlación 0,73).
- La Paz–Villaguay (dos cuadros unidos): VV −0,97 dB (p5 a p95, −3,4 a +1,6 dB; correlación 0,83); VH −1,45 dB (−4,4 a +1,3 dB; correlación 0,88).

**Cómo se interpreta.**

- En VV, casi toda la diferencia es un desfase de normalización de `Terrain Flattening` de SNAP: su γ⁰ queda por debajo de σ⁰/cos θ aun en terreno plano. El desfase cambia con la escena y el ángulo de incidencia (−0,5 dB en Concordia, −1,0 dB en Federal). Su causa no está documentada.
- VH queda siempre más abajo que VV. Lo más probable es la remoción del ruido térmico, que pesa más cuanto más débil es la señal. No está verificado cómo trata el ruido el RTC del Planetary Computer.
- Consecuencia práctica: **nunca** calcule un cambio (Δ) entre una fecha procesada en SNAP y otra del RTC. Una diferencia de 1 a 3 dB entre cadenas de proceso es del mismo orden que la señal que se busca. Todas las fechas de una serie se procesan con la misma cadena.

**¿Hace falta el aplanado en un relieve plano?** En Federal se procesó también σ⁰ sin aplanar (`procesar_s1_crudo.py --sin_aplanar`) y se separó, píxel a píxel, lo que corresponde al ángulo de incidencia, al desfase de SNAP (−1,01 dB) y al relieve. Lo que agrega el relieve, por clase de pendiente del Copernicus DEM:

- 0 a 1° (70 % del sitio): mediana 0,00 dB; p5 a p95, −0,13 a +0,14 dB.
- 1 a 3° (28 %): +0,02 dB; −0,23 a +0,25 dB.
- 3 a 10° (2 %): +0,03 dB; −0,51 a +0,56 dB.
- Más de 10° (menos del 0,1 %): +0,12 dB; −1,82 a +1,95 dB.

En el relieve plano de Federal el aplanado no corrige nada por relieve. Su efecto es la normalización por el ángulo de incidencia (1,2 dB, con incidencia de 39 a 42°). Se aplica igual para que el producto quede en γ⁰, la misma magnitud que el RTC, NISAR GCOV y los demás recortes del curso. Tabla y figura: `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\C_FEDERAL_S1_20260914_gamma0_desde_crudo_aplanado_vs_sin_aplanar.csv` y `.png`.

**Cuidado con el Copernicus DEM.** Es un modelo de superficie: incluye árboles y edificios. En Federal casi no hay pendientes de terreno (FABDEM: 0,03 % del sitio con más de 3°), pero el Copernicus DEM marca los bordes de monte y las construcciones como pendientes de más de 10°, y SNAP les aplica el aplanado (hasta ±2 dB). En un práctico de deforestación esto importa: un borde de desmonte puede cambiar de valor por el aplanado y no por la cobertura.

**Errores típicos.**

- SNAP se queda en `Apply Orbit File` o en `Terrain Flattening` sin avanzar: está bajando la órbita o el DEM. Sin internet no puede; conéctese y repita.
- `Terrain Flattening` rechaza la entrada: la calibración no dejó la banda β⁰. Repita `Calibrate` con `Output beta0 band`.
- Falta de memoria o un proceso de horas: no recortó antes del aplanado. Haga el `Subset` antes.
- El producto no cubre el sitio: el recorte se definió por píxeles. Use la pestaña `Geo Coordinates`.
- La Paz–Villaguay sale cortado: no se unieron los dos cuadros. `S-1 Slice Assembly` necesita los dos productos de la misma pasada, consecutivos.
- QGIS no abre el `.zip`: es normal, el original es para SNAP. En QGIS use `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\QGIS_GeoTIFF`.

Fuente: ESA Copernicus, Sentinel-1C IW GRDH, 14/09/2026, S1C_IW_GRDH_1SDV_20260914T091317_20260914T091342_009441_012C7A_AB47 y S1C_IW_GRDH_1SDV_20260914T091342_20260914T091407_009441_012C7A_4769 (el segundo, sólo para La Paz–Villaguay). Distribuido por ASF DAAC, https://search.asf.alaska.edu. Procesado con ESA SNAP y Copernicus DEM GLO-30.

## Controles complementarios (ampliación optativa)

Herramientas del docente; el alumno lee el resultado y no las corre.

- **GEDI L2B y L4A** (`00_COMUN\09_Herramientas\des_gedi_l2ab_l4a.py`): cobertura, PAI y biomasa por huella, por clase del mapa y período. Salidas: `05_Resultados\04_Tablas\C_gedi_l2ab_l4a_resumen.csv` y `C_gedi_l2ab_l4a_IC_por_celdas.csv`. Referencia: todas las clases suben entre períodos (incluso el no bosque, +0,28 m): es una diferencia entre períodos de GEDI, no crecimiento; los IC por celdas de 200 m son más anchos que los de la salida.
- **Embeddings AlphaEarth 2021 y 2025**: cambio como 1 − coseno, con los vectores promediados a 20 m y renormalizados. Referencia: 1.523 ha de bosque de 2021 con cambio mayor que el p99 del bosque estable (0,122); sólo el 7,8 % coincide con la pérdida de MapBiomas 2022–2025. Sirven para encontrar lotes que cambiaron de uso, no para separar un desmonte de una cosecha.
- **Contexto MapBiomas, CCI Biomass y banda P**: para leer antes de la clase. La caída del bosque abierto 2011–2025 (12.353 ha) es mayor que la pérdida registrada (5.119 ha) porque incluye pasajes de bosque abierto a herbáceas. La CCI no se compara entre 2010 y 2015 (cambió el sensor).

## Cierre

Responda `07_Preguntas_y_entrega/preguntas.md`. Controle las bitácoras de
`05_Resultados/06_Control_calidad/`: `Tp9_01_pila.log`, `Tp9_02_sinergia.log`,
`Tp9_03_fusion.log`.
