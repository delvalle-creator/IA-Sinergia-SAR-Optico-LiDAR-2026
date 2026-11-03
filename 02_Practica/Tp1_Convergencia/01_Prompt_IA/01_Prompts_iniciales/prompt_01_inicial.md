# Prompt inicial del Tp1 — el que se escribió primero

---

> Buscame imágenes Sentinel-1, Sentinel-2, NISAR y GEDI de Concordia para la
> inundación de noviembre de 2023 y decime cuáles sirven.

---

## Qué produjo

Un script que consultaba el catálogo con un rectángulo alrededor de Concordia,
filtraba Sentinel-2 por `eo:cloud_cover < 20` y devolvía una tabla prolija con
fecha, nombre y un «sirve: sí». Corría. Daba una lista.

## Los cinco defectos

**1. Confió en la nubosidad del catálogo.** `eo:cloud_cover` es la nubosidad de la
tesela Sentinel-2 entera, de 110 × 110 km. El sitio ocupa una fracción de esa
tesela. Una escena con 15 % de nubes puede tener el sitio completamente tapado, y una
con 60 % puede tenerlo despejado. La nubosidad que importa se cuenta dentro del sitio,
con la capa SCL.

**2. Tomó la huella como cobertura.** Daba por «útil» toda escena cuyo polígono
tocaba el rectángulo. Pero la huella es lo que **toca**, no lo que **cubre**: una
franja NovaSAR que roza el borde, o una NISAR cuyo borde trae muestras inválidas,
aparecen como útiles y no tienen dato sobre el sitio.

**3. Listó NISAR para noviembre de 2023.** NISAR no estaba en órbita. El script no
lo inventó a propósito: no encontró nada, y la redacción del prompt («decime cuáles
sirven») empujó a la IA a completar la tabla con lo que «debería» haber. Una tabla sin
la fila de NISAR, con la ausencia declarada, era la respuesta correcta.

**4. Interpretó «0 granulos GEDI» como un error de red y reintentó.** Entre el
17/03/2023 y el 26/04/2024 GEDI no adquirió datos. Cero es la respuesta. Reintentar
no la cambia; declararla, sí la vuelve útil.

**5. Tomó la fecha del archivo descargado y escribió la contraseña en el código.** La
fecha de modificación del archivo es la de la descarga, no la de la adquisición; la
fecha va de los metadatos y en UTC. Y para «bajar GEDI» pidió escribir el usuario y la
contraseña de NASA Earthdata en una variable del script, que después viaja a GitHub.

## La lección

El prompt pedía «cuáles sirven». La IA contestó, porque siempre contesta. Lo que
faltaba era decirle **cómo se verifica que una escena sirve**: dentro del sitio, con
el dato y no con la huella, con la fecha de los metadatos, y declarando lo que no hay.
