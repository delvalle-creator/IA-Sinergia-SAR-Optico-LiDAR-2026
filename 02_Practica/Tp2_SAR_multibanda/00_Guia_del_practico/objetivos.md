# Tp2 — Objetivos

## Objetivo general

Llevar escenas SAR de distintas longitudes de onda a γ⁰ lineal comparable en una
grilla común, y explicar con argumentos físicos por qué la misma cubierta responde
distinto en cada banda y polarización.

## Objetivos específicos

1. Procesar en SNAP una escena Sentinel-1 GRD hasta γ⁰ con Terrain Flattening y
   corrección geométrica Range Doppler, en EPSG:32721 a 10 m, y guardarla en
   BEAM-DIMAP con sus metadatos originales.
2. Filtrar el speckle como paso aparte y comparar el producto filtrado con el
   original.
3. Mantener el radar en **lineal** para todo cálculo y usar el dB sólo para ver
   (bandas virtuales) y para umbralizar.
4. Reunir en una pila, sobre la grilla común, las bandas C, S y L disponibles (y P o X
   donde existan), con su unidad (γ⁰ normalizado por el terreno, γ⁰ sobre el elipsoide o σ⁰) declarada en
   el nombre y en la tabla de bandas.
5. Componer e interpretar el RGB copolarizada–cruzada–cociente de cada sensor de
   polarización dual.
6. Medir la respuesta de cada cubierta en cada banda y proponer el mecanismo de
   dispersión compatible con cada respuesta (superficial, doble rebote, volumen),
   sabiendo que la intensidad en polarización dual no alcanza para confirmarlo: la
   confirmación exige la fase HH − VV de un producto cuadripolar complejo. Con el SAOCOM
   cuadripolar (para profundizar), comparar HH, HV y VV por cubierta.
7. Controlar la calibración en una zona estable: diferencia entre fechas o entre
   procesamientos menor que 1 dB, informada también polígono por polígono.
8. Contrastar la respuesta de cada banda con productos de contexto (MapBiomas 2025,
   CCI Biomass) sin tomarlos como verdad de campo.

## Qué se entrega

- La pila en lineal y su tabla de bandas.
- El producto de SNAP en `.dim` con bandas lineales y virtuales en dB.
- Los RGB, la tabla de respuesta por cubierta, la de contraste entre clases y la
  figura de cajas.
- La tabla del control en zona estable con su veredicto.
- Las cifras de los polígonos propios del grupo, con una línea que las compare con las
  del Desarrollo (por ejemplo: «nuestro contraste monte–pajonal en L HV fue X dB frente
  a 7,25 dB del Desarrollo, porque…»).
- Las respuestas a `07_Preguntas_y_entrega/preguntas.md`.

## Criterio de evaluación

No se evalúa que la pila tenga muchas bandas, sino que **cada banda sea comparable**
(misma normalización, misma grilla, unidad declarada) y que las diferencias entre
bandas estén **explicadas por la física**, no descriptas. Una banda que no entra, con
el motivo escrito, vale tanto como una que entra.
