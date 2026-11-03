# Prompt inicial del Tp2 — el que se escribió primero

---

> Tengo Sentinel-1, NovaSAR y NISAR del Delta. Pasalos todos a dB, apilalos y
> decime qué banda ve mejor el pajonal.

---

## Qué produjo

Un grafo de SNAP con `Calibration` a σ⁰ en dB, un `Terrain-Correction` y un script que
convertía todo a dB, remuestreaba a 10 m con interpolación bilineal, apilaba y
calculaba el promedio de cada banda sobre el pajonal. Corría. Daba una tabla con un
ganador.

## Los cinco defectos

**1. Promedió en dB.** El promedio de los logaritmos no es el logaritmo del promedio.
Con el speckle, la distribución de γ⁰ es muy asimétrica: promediar en dB sesga la
media hacia abajo, y el sesgo crece con la varianza. Dos bandas con distinto speckle
quedan sesgadas distinto, y la comparación entre ellas se contamina.

**2. Remuestreó NISAR y NovaSAR con bilineal sobre dB.** Llevar NovaSAR de 6 m a 10 m
exige **agregar potencia** (promedio en lineal, o la media cuadrática de los números
digitales antes de calibrar). La interpolación bilineal en dB ni agrega ni conserva la
potencia.

**3. Mezcló σ⁰ y γ⁰ sin decirlo.** Sentinel-1 quedó en σ⁰ (calibración sin Terrain
Flattening), NISAR GCOV viene en γ⁰ y NovaSAR sólo puede calibrarse a σ⁰ fuera de
SNAP. En la tabla las tres columnas se llamaban «backscatter». La diferencia entre
σ⁰ y γ⁰ depende del ángulo de incidencia: se confunde con la respuesta de la cubierta.

**4. No aplicó la máscara de NISAR.** El borde de la franja entró con valores de
alrededor de −133 dB, y el promedio del pajonal que tocaba el borde se desplomó.

**5. Contestó «qué banda ve mejor» con el valor absoluto.** Ganó la banda con γ⁰ más
alto sobre el pajonal. Pero «ver» una cubierta es **separarla** de las demás: lo que
importa es el contraste con el agua, el monte o el suelo, no el valor solo.

## La lección

El prompt pedía «pasar a dB y apilar». La IA obedeció. Faltaba decirle **en qué unidad
se opera** (lineal), **cómo se agrega** (potencia), **qué normalización tiene cada
banda** (y declararla), y que la pregunta se responde con contrastes.
