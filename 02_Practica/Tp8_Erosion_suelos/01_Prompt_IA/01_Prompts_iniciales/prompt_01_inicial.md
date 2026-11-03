# Prompt inicial del Tp8 — el que se escribió primero

---

> Quiero un mapa de erosión de suelos alrededor de Bovril. Usá Sentinel-2 para
> ver el suelo desnudo y el NovaSAR que tengo para la rugosidad, y clasificá con
> Random Forest.

---

## Qué produjo

Un script que tomaba **una** escena Sentinel-2 de septiembre de 2023, umbralaba
el NDVI, leía el `image_HH.tif` de NovaSAR, lo pasaba a dB, calculaba el desvío en
una ventana, apilaba todo y entrenaba un Random Forest. Daba un mapa de erosión
con una exactitud muy alta.

## Los cinco defectos

**1. Una sola fecha confunde labranza con erosión.** En septiembre medio
Entre Ríos está en barbecho o recién sembrado. Un lote labrado esa semana tiene
NDVI bajo igual que una cárcava. Lo que separa la erosión es la persistencia:
cuántos meses del año el suelo está expuesto.

**2. NovaSAR sin calibrar ni corregistrar.** Usó los números digitales, no
σ⁰ = DN²/CalibrationConstant. Y la escena viene georreferenciada con cuatro
puntos de esquina: con ellos el corrimiento es de cientos de metros y no rígido;
con los 84 puntos de enlace del `metadata.xml` la banda S queda 80 m al este y
20 m al sur, y se corrige con una traslación (`--desplazamiento -80 20`). Sin eso, la textura de un lote se asigna al vecino.

**3. La textura calculada en dB.** El desvío de los logaritmos no es la
variabilidad de la potencia: el speckle en dB tiene otra distribución y el
coeficiente de variación pierde su referencia física (1 para una vista,
1/√L para L vistas). La textura se calcula en potencia lineal.

**4. Llevó NovaSAR de 6 a 10 m con vecino más próximo.** Eso descarta potencia
en lugar de promediarla. Agregar SAR es promediar potencia.

**5. Informó la exactitud de entrenamiento.** Esa cifra salió de píxeles vecinos de
los mismos polígonos usados para entrenar. No dice nada de la exactitud del mapa.

## La lección

El prompt pedía «un mapa de erosión». Un mapa siempre sale, y con una exactitud
alta. Lo que faltaba era preguntar **qué separa la erosión de la labranza** y si
cada sensor estaba en la misma grilla y en las unidades correctas.
