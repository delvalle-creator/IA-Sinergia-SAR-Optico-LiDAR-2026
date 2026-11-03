# Prompt inicial del Tp6 — el que se escribió primero

---

> Hacé un mapa de la inundación de Concordia de noviembre de 2023 con
> Sentinel-1 y Sentinel-2, y calculá la superficie inundada y la profundidad.

---

## Qué produjo

Un script que tomaba la escena Sentinel-1 del 04/11/2023, aplicaba un umbral
fijo de −15 dB a VV, le sumaba el agua de Sentinel-2 (NDWI > 0) y contaba
píxeles. Para la profundidad restaba al MDE la cota mínima del río. Corría. Daba
un número de hectáreas y un mapa de profundidades.

## Los cinco defectos

**1. Contó el río y el embalse como inundación.** Sin máscara de agua
permanente, el río Uruguay y el embalse de Salto Grande entraban como «agua de
la crecida». La superficie inundada quedaba dominada por agua que siempre está.

**2. Un umbral fijo, sin histograma.** −15 dB es un valor de manual que depende
del ángulo de incidencia, del viento y de la órbita. No se miró el histograma ni
se justificó. Y con un umbral por escena, una serie temporal cambia la definición
de agua de una fecha a otra. El problema no es el valor, sino que no se justificó:
en el práctico se llega también a −15 dB, pero con el histograma por grupo y el
agua de JRC (Figura 10 del Desarrollo).

**3. No dijo qué no ve.** El agua bajo el pajonal o el monte no es oscura en VV:
el doble rebote la hace brillante. Eso es tarea de la banda L. Para noviembre
de 2023 hay dos SAOCOM TNA (10/10 y 11/11) y un ALOS-2 ScanSAR (16/11), pero la
regla de doble rebote no se puede aplicar sin probarla. El script no lo mencionó:
el mapa parecía completo.

**4. Sumó sensores sin reglas y sin nubes.** El NDWI se aplicó también donde
había nubes (las nubes y sus sombras dan valores raros) y la combinación fue un
«o» implícito, sin escribir. Nadie podía saber qué decía cada píxel ni por qué.

**5. La profundidad usó una cota única y un MDE sin controlar.** Restar una sola
cota del río a todo el sitio ignora que el agua desciende aguas abajo. Y el
Copernicus DEM es un modelo de superficie: en el monte mide la copa, y la
«profundidad» allí es la altura de los árboles.

## La lección

El prompt pedía «la superficie y la profundidad». La IA dio dos números. Lo que
faltaba era **separar el agua de la crecida del agua de siempre**, decir qué agua
no ve cada sensor, escribir cómo se combinan las decisiones, y controlar el MDE
antes de creerle una profundidad.
