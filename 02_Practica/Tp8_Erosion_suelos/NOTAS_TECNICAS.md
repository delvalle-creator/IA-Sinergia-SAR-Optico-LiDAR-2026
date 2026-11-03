# Tp8 — Notas técnicas

> **Qué es este archivo.** Las decisiones técnicas del práctico y su fundamento,
> las limitaciones conocidas y los hallazgos con datos reales. Para el recorrido,
> abra `00_LEEME.md`.

**Pregunta:** ¿dónde hay suelo expuesto de forma persistente y qué parte de él muestra erosión visible?
**Sitio:** `F_BOVRIL` (−59,53 / −31,42 / −59,40 / −31,29).

## Los datos y sus fechas

| Sensor | Banda | Producto | Fecha | Unidad |
|---|---|---|---|---|
| Sentinel-2 | óptico | L2A, B02, B04, B08, B11, SCL | todo 2023 (par verificado: 10/09/2023) | reflectancia 0–1 |
| NovaSAR-1 | S (9,4 cm) | Stripmap GRD HH, 6 m, escena 47974 | 14/09/2023, 01:42 UTC | σ⁰ lineal |
| Sentinel-1 | C (5,5 cm) | IW GRD RTC, VV y VH | 14/09/2023 ± 6 días | γ⁰ lineal |
| FABDEM v1-2 (pendiente en `Tp8_03`) | — | 30 m, GLO-30 sin monte ni edificios | TanDEM-X 2011–2015 | m (EGM2008) |
| Copernicus DEM | — | GLO-30 (respaldo si falta FABDEM) | TanDEM-X 2011–2015 | m (EGM2008) |

## Decisiones y su fundamento

**Persistencia, no fecha.** La erosión se distingue de la labranza por cuántos
meses el suelo está expuesto. Un mes es desnudo si más de la mitad de sus
observaciones válidas lo fueron: así una escena con borde de nube no decide el mes.

**Umbrales del suelo desnudo.** NDVI < 0,25 y BSI > 0. El NDVI bajo descarta
vegetación verde; el BSI positivo exige que el SWIR y el rojo superen al NIR y al
azul, lo que en general separa el suelo del agua (en el agua el BSI suele ser
negativo). Son umbrales de
partida: `--ndvi_max` y `--bsi_min` permiten cambiarlos y se declaran. `Tp8_01`
guarda los histogramas de NDVI y BSI de una fecha con mucho suelo desnudo
(`--fecha_histograma`, por defecto 2023-11-07) con la línea de cada umbral
(regla 6 del proyecto): el NDVI tiene dos modas y 0,25 cae al borde de la baja;
el BSI no separa grupos y funciona sólo como segunda condición. BSI: Rikimaru et
al. (2002).

**Una versión por fecha.** El catálogo trae dos versiones de procesamiento de 55
de las 79 fechas de 2023. `Tp8_01` conserva una por fecha y tesela (la de
`s2:processing_baseline` más alta y, a igualdad, la procesada más tarde) e informa
cuántas descartó. Contar las dos cambia de clase el 2,3 % del sitio (la clase
persistente baja de 489 a 392 ha con las 68 fechas locales).

**Serie local.** `--local` lee la copia de `00_COMUN/08_Originales_crudos/PLANETARY/F_BOVRIL`
(68 fechas con el sitio casi entero despejado): el paso 1 corre sin internet.

**Nubes contadas en el sitio.** La nubosidad del catálogo es la de la tesela de
110 × 110 km; sólo preselecciona (`--nubes_max 60`). La que importa se cuenta con
la SCL dentro del sitio (clases válidas 4, 5, 6, 7 y 11).

**Línea de base 04.00.** Toda escena de 2023 trae +1000 en los DN de L2A; la
función común lo descuenta leyendo la línea de base de los metadatos.

**NovaSAR: σ⁰, no γ⁰.** El GRD de NovaSAR se calibra con σ⁰ = DN²/1E+05; el
producto no trae lo necesario para γ⁰. En el relieve suave de Bovril la
diferencia es chica, pero existe y se declara (Small, 2011).

**Agregación en potencia.** De 6 a 10 m se usa la media cuadrática de los DN, que
al cuadrado es la media de la potencia. Vecino más próximo descartaría potencia;
promediar en dB la sesgaría hacia abajo.

**Georreferencia de NovaSAR.** Sólo cuatro GCP de esquina: ajuste afín de toda la
franja. El desplazamiento se aplica con `--desplazamiento DX DY` (metros, este y
norte positivos). DX y DY son la CORRECCIÓN, no el error: si la banda S está 80 m
al este y 20 m al sur del óptico, se pasa `--desplazamiento -80 20`. Se mide, no
se supone.

**Textura = CV local en lineal.** En potencia, el speckle solo da CV = 1 para una
vista y 1/√L para L vistas. Un CV mayor que el de una zona homogénea del mismo
producto indica heterogeneidad real (bordes, cárcavas, alambrados). Por eso el
CV de S y el de C **no se comparan en valor absoluto**: tienen distinto número de
vistas. Se compara cuánto sube cada uno sobre su propio piso.

**Ventana de 5 píxeles.** 50 m a 10 m de píxel: lo mínimo para estimar un CV con 25
muestras; es mucho más que el ancho de una cárcava (5 a 15 m) y por eso la textura
describe bordes de lote, no cárcavas. Se exige más del 60 % de la ventana con
dato.

**Pendiente de un MDE de 30 m.** Describe la ladera, no la cárcava. Entra como
rasgo porque la erosión hídrica necesita pendiente, no porque resuelva el detalle.

**Fusión de rasgos.** Cada sensor aporta una variable derivada (frecuencia, CV,
pendiente) y el Random Forest las combina en un producto. Requiere la misma
grilla y el corregistro < 1 píxel: por eso el desfase de NovaSAR es condición, no
detalle.

**Susceptibilidad.** Es la probabilidad de la clase 1 que da el Random Forest (`predict_proba` de scikit-learn): el promedio, entre los árboles, de la proporción de la clase 1 en la hoja donde cae el píxel (con `min_samples_leaf=2` no es una fracción de votos). Es un
**índice**, no una probabilidad calibrada de erosión.

**Fechas de S y C.** `Tp8_02` usa la escena Sentinel-1 RTC más cercana a
`--fecha_c` dentro de ± 6 días (`s1_rtc_mas_cercana`). La fecha de NovaSAR sale
de la tabla de escenas de la configuración común (`NOVASAR_ESCENAS`) para la
escena pedida con `--novasar`: con ella se escribe la cita de fuente y la
diferencia de días S–C de la bitácora.

**Año de la serie.** Los pasos 2 y 3 leen
`F_frecuencia_suelo_desnudo_<anio>_<pixel>m.tif` con `--anio` (2023 por defecto):
si el paso 1 se corre con otro año, se pasa el mismo `--anio` a los tres.

## Limitaciones conocidas

1. **Piso de speckle.** `Tp8_02 --zonas_homogeneas <gpkg>` calcula el CV del piso
   con la misma ventana en cada polígono y lo escribe como última fila de
   `F_textura_por_frecuencia.csv`, con el ENL (1/CV²) en la bitácora. Las zonas
   tienen que ser homogéneas también a la resolución de C (20 × 22 m): lotes
   grandes con cultivo parejo, no agua (en S y en la VH de C está cerca del ruido).
   Con 12 zonas de `zonas_homogeneas.gpkg`: S 0,25–0,32, VV 0,28–0,38, VH 0,29–0,38.
2. **Rastrojo seco.** Con siembra directa, el rastrojo tiene NDVI bajo y puede dar
   BSI positivo: puede contarse como suelo desnudo.
3. **Cobertura de NovaSAR.** La escena cubre el 92,9 % del sitio; con las ventanas
   de textura (más del 60 % con dato) y la banda C, el dominio de la variante
   multisensor es el 89 % (16.587 ha): el 11 % oriental queda sin susceptibilidad.
6. **Entrenamiento equilibrado.** `Tp8_03` entrena por defecto con el mismo peso por
   clase (`--equilibrar si`): con una clase rara la probabilidad queda inflada y el
   umbral 0,5 marca de más (2.616 ha con 0,5; 326 ha con 0,9).
7. **Importancia ≠ aporte.** La importancia dice cuánto usó el modelo cada rasgo.
   El aporte del radar se mide comparando `--rasgos meses_suelo_desnudo
   pendiente_grados` con todos los rasgos, validando por polígono (Tp8_D en Orange).
4. **Una sola fecha de banda S y de banda C.** La textura depende de la humedad y
   del estado del lote ese día.
5. **Pruebas.** Los tres scripts se corrieron en la computadora del curso el
   23/10/2026 (desarrollo del docente, corridas DES_Tp8_A a I): el paso 1 lee 145
   escenas Sentinel-2 de 2023 (134 usadas, 79 fechas distintas) y es el más largo de
   la tarde. Las variantes de `Tp8_03`, el piso en zonas homogéneas y la serie local
   se corrieron el 28/10/2026.

## Hallazgos con datos reales del curso

- NovaSAR 47974 (14/09/2023) cubre el **92,9 %** de `F_BOVRIL` (medido con
  `Tp1_02_inventario_local.py` sobre el GRD).
- Con los 84 puntos de enlace del `metadata.xml` (`--puntos_enlace todos`), la banda S
  está corrida **80 m al este y 20 m al sur** de Sentinel-2, igual en las 14 ventanas
  con dato (dos de las 16 caen fuera de la NovaSAR): se corrige con
  `--desplazamiento -80 20`, como midió el docente en la clase teórica. Con los 4
  puntos de esquina del `image_HH.tif` (el valor por defecto) la banda S está corrida
  unos 90 m al este y de 560 m (norte del sitio) a 330 m (sur) al norte: no es una
  traslación (corrección mediana −90 m y −490 m).
- `CalibrationConstant = 1E+05` en el `metadata.xml` de las cinco escenas NovaSAR
  del archivo.
