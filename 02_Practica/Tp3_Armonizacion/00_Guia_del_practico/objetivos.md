# Tp3 — Objetivos

## Objetivo general

Llevar SAR, óptico y LiDAR a una grilla y una fecha comparables y **demostrar**, con
mediciones, si se cumplen los tres requisitos de la fusión: misma grilla, corregistro
menor que un píxel y fechas compatibles.

## Objetivos específicos

1. Elegir la grilla común (EPSG:32721) con el espaciado más grueso de los productos que
   se fusionan a nivel de píxel y justificarla.
2. Agregar el radar en lineal (promedio de potencia), promediar las reflectancias y
   llevar la máscara de nubes por mayoría, sin «afinar» bandas gruesas; si un producto
   más grueso que la grilla entra al cubo (MDE, banda P), declararlo como
   sobremuestreado y no usarlo para detalles menores que su resolución.
3. Medir el desplazamiento residual entre sensores con correlación de fase sobre bordes
   y distinguir un corrimiento rígido de una deformación.
4. Documentar la diferencia de fecha entre cada par de sensores y entre cada huella
   LiDAR y cada capa.
5. Extraer los valores del cubo en las huellas GEDI y los segmentos ATL08 válidos,
   respetando el tamaño de cada huella.
6. Decidir, para cada par de sensores, si puede entrar a una fusión de píxel, de rasgo
   o sólo de decisión, y declararlo.
7. Ubicar las huellas y el cubo en la historia del sitio (MapBiomas, fuego, CCI Biomass)
   y decidir qué productos de contexto entran, a qué escala y con qué papel (estrato,
   contexto o ninguno).

## Qué se entrega

- El cubo y su tabla de capas.
- La tabla de diferencias de fecha.
- Las mediciones de corregistro con su veredicto.
- La tabla de huellas con los valores del cubo.
- La tabla de los tres requisitos por par de sensores, incluidos los dos pares nuevos de
  la pregunta 12.
- La tabla de verificación de `01_Prompt_IA/04_Verificacion/verificacion_resultados.md`.
- Las respuestas a `07_Preguntas_y_entrega/preguntas.md`.

## Criterio de evaluación

No se evalúa que todo «cumpla», sino que **cada requisito esté medido** y que la
decisión sobre qué se puede fusionar se siga de las mediciones. Un par que no cumple,
detectado y declarado, es un resultado del práctico. El Desarrollo del docente muestra el
razonamiento sobre los pares de Ibicuy y Bovril; la evaluación se hace sobre los pares
nuevos de la pregunta 12 (transferencia del método) y sobre la tabla de requisitos que
arma el grupo con ellos.
