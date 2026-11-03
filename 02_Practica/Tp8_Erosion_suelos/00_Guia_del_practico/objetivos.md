# Tp8 — Objetivos

## Objetivo general

Identificar el suelo expuesto de forma persistente y la parte que muestra erosión
visible en el entorno de Bovril combinando una serie óptica, dos bandas SAR de distinta resolución y la
pendiente, y **separar la erosión de la labranza normal**.

## Objetivos específicos

1. Calcular la frecuencia anual de suelo desnudo (meses por año) con la serie
   Sentinel-2 de 2023, usando sólo los píxeles sin nube de cada escena.
2. Calibrar y corregistrar la escena NovaSAR-1 de banda S (σ⁰ = DN²/1E+05,
   desplazamiento medido) y llevarla a la grilla común promediando potencia.
3. Medir la textura (coeficiente de variación local, en potencia lineal) de la
   banda S y de la banda C por separado, y compararlas por clase de frecuencia de
   suelo desnudo (**sinergia**).
4. Combinar suelo desnudo, texturas y pendiente en un Random Forest (**fusión de
   rasgos**) para obtener un índice de susceptibilidad, y medir qué aportó el radar
   comparando variantes con y sin él (mismo Random Forest, mismos polígonos,
   validación por polígono), sin confundir la importancia con el aporte.
5. Preparar las variantes «solo óptico» y «multisensor» para validarlas con el
   Tp4, y declarar las limitaciones de cada una.

## Qué debe entregar

- El mapa de suelo desnudo persistente con la verificación de cada mancha en la
  imagen de 2 m (labranza frente a exposición persistente).
- La tabla de textura S frente a C por clase, interpretada.
- El índice de susceptibilidad, la importancia de los rasgos y las dos variantes.
- La capa de entrenamiento con la fuente de cada polígono.
- Las respuestas a las preguntas, citando el archivo de cada cifra.

## Criterio de evaluación

No se evalúa la superficie que dé «susceptible», sino **que el grupo pueda decir
por qué un lote recién labrado no es un foco de erosión** y qué aportó cada
sensor. Una exactitud fuera de bolsa alta no prueba nada: la que cuenta es la del
Tp4.
