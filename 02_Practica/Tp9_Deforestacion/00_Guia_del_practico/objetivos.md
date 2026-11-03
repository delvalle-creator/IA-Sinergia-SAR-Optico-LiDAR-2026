# Tp9 — Objetivos

## Objetivo general

Mapear la pérdida y la degradación del monte nativo del Espinal en Federal entre
2021 y 2026, usando 2011 (ALOS-1 HH) como referencia histórica, y **separar el
desmonte de los cultivos cosechados**; **evaluar si la degradación bajo el dosel
es detectable** con los datos disponibles.

## Objetivos específicos

1. Armar una pila temporal multibanda en una grilla común de 20 m, con el radar
   en γ⁰ lineal (σ⁰ en NovaSAR, declarado), y declarar la resolución nativa de
   cada producto.
2. Calibrar entre sí ALOS-1, ALOS-2 y NISAR en zonas estables y decidir, con el
   residuo que queda después de corregir el desfase, qué cambios son
   interpretables.
3. Determinar qué estrato ve cada banda (copa, ramas y troncos, troncos y suelo)
   con la correlación y la curva de respuesta frente a la altura GEDI rh98
   (**sinergia**), comparando en la misma polarización y respetando la distancia
   en fecha entre cada capa y las huellas.
4. Detectar candidatas a degradación como caída de rh98 por celda sin cambio de
   NDVI.
5. Combinar rasgos de cambio de cada sensor en un Random Forest de cuatro clases
   (**fusión de rasgos**) y preparar las variantes para el Tp4.
6. Usar Δrh98 como control complementario del mapa, contando celdas (no
   píxeles) y declarando que con menos de 3 m de caída no confirma ni descarta.
7. Contrastar el mapa con fuentes independientes de la fusión (SAOCOM 2021–2026,
   MapBiomas, GEDI L2B/L4A) y explicar coincidencias y discrepancias; con ellas,
   evaluar con evidencia independiente (GEDI, SAOCOM, validación del Tp4) si la
   clase degradación es distinguible del monte estable y declarar por qué no lo es.

## Qué debe entregar

- La tabla de calibración cruzada con el desfase y el residuo por zona, y su lectura.
- La tabla de sensibilidad a la altura y la figura de curvas de respuesta,
  interpretadas por banda.
- La tabla de celdas candidatas a degradación.
- El mapa de pérdida y degradación, la importancia de los rasgos, las tres
  variantes y la tabla de control con GEDI.
- La capa de entrenamiento con la fuente de cada polígono.
- La validación del Tp4 (o, si no se llegó, el diseño muestral listo).
- Las respuestas a las preguntas, citando el archivo de cada cifra.

## Criterio de evaluación

No se evalúa cuántas hectáreas «perdió» el monte, sino **que el grupo pueda
defender que un cultivo cosechado no es desmonte** y que cada cambio que informa
supera la dispersión del residuo después de corregir el desfase, medida en
controles independientes de los usados para calibrar. Una banda que no se pudo
evaluar por falta de huellas cercanas en fecha se declara, no se esconde.
