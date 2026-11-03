# Tp8 — Preguntas, producto y rúbrica

Cada respuesta cita el archivo (y la fila, columna o banda) del que sale la cifra.

## Preguntas

1. **La serie.** ¿Cuántas escenas Sentinel-2 de 2023 entraron, cuántas fechas
   distintas son y cuántas se descartaron por tener menos del 20 % del sitio útil
   (`F_escenas_opticas_2023.csv` y la bitácora)? ¿Cuál es la mediana de meses con observación?
   ¿En qué meses faltan observaciones y qué consecuencia tiene sobre la frecuencia?

2. **Labranza frente a erosión.** ¿Qué % del sitio quedó en 1–2 meses y qué % en
   6 o más (`Tp8_01_suelo_desnudo.log`)? Muestre tres lotes de cada clase sobre la
   imagen de alta resolución. ¿Qué hay en la clase de 6 o más meses que **no** es
   erosión (caminos, cascos, canteras, rastrojo)?

3. **El desfase de NovaSAR.** ¿Qué desplazamiento midió (hacia dónde está corrida la
   banda S y qué corrección pasó al script), sobre qué rasgos, y cuál fue el residuo
   después de corregir? ¿Coincide en todo el sitio o cambia de norte a sur?
   Justifique con al menos cuatro mediciones y diga con qué puntos de enlace lo
   midió (las 4 esquinas o los 84 del `metadata.xml`). ¿Qué habría pasado con la tabla de textura por
   clase sin corregirlo?

4. **Sinergia S frente a C.** Lea `F_textura_por_frecuencia.csv` contra el piso de
   speckle que midió en zonas homogéneas de cada producto (`--zonas_homogeneas`).
   ¿Alguna banda separa las clases por encima de su piso de speckle? Si alguna lo
   hace, ¿cuál, y por qué? Explíquelo con la longitud de onda (9,4 frente
   a 5,5 cm), la resolución (6 m de NovaSAR frente a unos 20 × 22 m de Sentinel-1 IW, aunque su píxel sea de 10 m) y la polarización (HH frente a VV y VH).

5. **Dos medidas de textura.** ¿El GLCM de SNAP (`Contrast`, `Homogeneity`) y el
   CV del script ordenan igual tres lotes elegidos? Si no, ¿cuál le parece más
   fácil de interpretar físicamente y por qué?

6. **Fusión de rasgos.** ¿Qué rasgos entraron, cuál fue la importancia de cada
   uno y cuál fue la exactitud fuera de bolsa (`Tp8_03_susceptibilidad.log`)? ¿Por
   qué esa exactitud no se informa como la exactitud del mapa? Con el workflow
   Tp8_D de Orange o con `--rasgos`, ¿cuánto cambia el AUC validado por polígono al
   agregar el radar a «óptico + pendiente»? ¿Por qué la importancia no mide el aporte
   de cada sensor?

7. **La pendiente.** El rasgo `pendiente_grados` viene de un MDE de 30 m. ¿Qué
   describe y qué no describe en una cárcava? Si estuvo entre los dos rasgos más
   importantes, ¿qué dice eso de su entrenamiento?

8. **Validación e incertidumbre.** Con el Tp4, ¿qué exactitud global, del usuario
   y del productor (con IC 95 %) tienen las variantes «solo óptico» y
   «multisensor»? ¿Está demostrada la mejora con esa muestra
   (`tabla_de_variantes_susceptible.csv`)? Si no llegó a hacerlo, diga qué
   tamaño de muestra se necesitaría con los valores por defecto del Tp4.

9. **Limitaciones.** Enumere tres limitaciones concretas (por ejemplo: σ⁰ y no γ⁰
   en NovaSAR; una sola fecha de banda S; humedad distinta entre S y C; NovaSAR
   cubre el 92,9 % del sitio y la variante multisensor evalúa el 89 %; entrenamiento
   equilibrado que infla la clase rara; rastrojo seco como suelo desnudo) y diga cómo cambiaría el
   mapa sin cada una.

10. **Contexto.** Con MapBiomas 1985–2025, la capa de pérdida de vegetación
   primaria y la banda P, ¿dónde esperaría hoy más erosión y por qué? Cruce el
   primer año de desmonte con sus polígonos de erosión y con los puntos etiquetados
   del paso 6, e informe la proporción con su intervalo.

11. **Diseño.** Proponga una definición operativa de la variable (erosión presente
   en una fecha, o susceptibilidad con horizonte) y un diseño de referencia: unidad,
   fecha, tamaño de muestra con una exactitud del usuario esperada realista (la del
   paso 6 fue de 0,07 a 0,09) y validación en lotes independientes.

## Producto a entregar

Mapa de suelo desnudo persistente (≥ 6 meses) con la verificación de cada mancha
en la imagen de 2 m (erosión, ciudad, camino, rastrojo, terraza u otro) y mapa de
susceptibilidad (multisensor), con la importancia de los rasgos, la exactitud del Tp4 si se
llegó, y la tabla de verificación completa. Cada figura lleva al pie la cita
**Fuente**.

## Rúbrica

| Criterio | Peso | Logrado | Parcial | No logrado |
|---|---|---|---|---|
| Frecuencia de suelo desnudo leída como persistencia | 15 % | Labranza y exposición persistente separadas y verificadas en la imagen | Mapa sin verificación | Una sola fecha o sin máscara de nubes |
| NovaSAR calibrado y corregistrado | 10 % | Desfase medido y aplicado; mediana del residuo < 1 píxel y ventanas con residuo de 1 a 2 píxeles declaradas y enmascaradas | Desfase aplicado sin medir | Sin corrección |
| Sinergia S–C interpretada contra el piso de speckle | 10 % | Comparación con zona homogénea y explicación física | Tabla sin piso | Valores absolutos comparados entre sensores |
| Entrenamiento sorteado y documentado | 10 % | Sorteo uniforme y estratificado con semilla, campo `dist_al_punto_m` y puntos salteados anotados | Polígonos sin registro del sorteo | Polígonos elegidos a ojo |
| Fusión de rasgos correcta y leída | 15 % | Rasgos, importancias, advertencia sobre la exactitud fuera de bolsa y aporte del radar medido con variantes validadas por polígono | Modelo corrido sin lectura | Exactitud de entrenamiento informada como del mapa |
| Validación (Tp4) o plan de validación | 15 % | IC de las dos variantes y conclusión sobre la mejora | Una variante validada | Sin validación ni plan |
| Contexto del sitio (pregunta 10) | 10 % | Cruce del año de desmonte con polígonos y puntos, con intervalo, leído como asociación | Contexto descripto sin cruce | Sin contexto |
| Limitaciones y diseño (preguntas 9 y 11) | 15 % | Tres limitaciones concretas con su efecto y un diseño de variable y muestra con tamaño justificado | Limitaciones genéricas o diseño sin tamaño | Ninguna |
