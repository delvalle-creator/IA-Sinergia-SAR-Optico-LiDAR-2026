# Tp2 — Preguntas, producto y rúbrica

Cada respuesta cita el archivo del que sale la cifra (por ejemplo,
`05_Resultados/04_Tablas/A2_IBICUY_respuesta_por_cubierta.csv`, fila `monte_o_bosque`,
banda `L_NISAR_gamma0_HV_...`). Respuestas cortas: el dato y la razón física. Las cifras son las de los polígonos
propios del grupo, no las del Desarrollo (que salen de los polígonos sorteados por el
docente).

Núcleo de la tarde: preguntas 1 a 9, 11 y 12. La 10 corresponde al paso 9 («para
profundizar»).

## Preguntas

1. **β⁰, σ⁰ y γ⁰.** ¿Por qué el grafo calibra a β⁰ y no a σ⁰? ¿Qué hace el Terrain
   Flattening con β⁰ y por qué el resultado (γ⁰) es comparable con el NISAR GCOV? En
   la pila de Ibicuy todo es γ⁰ (la P, sobre el elipsoide; no hay NovaSAR): ¿cómo se declara la P en la
   tabla de bandas? Si arma la de Concordia con
   `--novasar 47942`, ¿qué banda queda en σ⁰ y cómo se lo indica al lector?

2. **Lineal y dB.** Tome una clase de `A2_IBICUY_respuesta_por_cubierta.csv`. La
   `media_dB` se calculó promediando en lineal. ¿Por qué no se promedia en dB? ¿En qué
   sentido sesgaría el resultado y en qué clases el sesgo sería mayor (piense en el
   rango p10–p90)?

3. **El filtro.** Con los valores de la tabla de verificación (control 2), ¿qué hizo el
   filtro de speckle con la media y con el desvío de `Gamma0_VV`? En el paso 8, ¿cómo
   cambia el desvío pixel a pixel entre un par filtrado y uno sin filtrar? ¿Por qué el
   filtro no cambia el veredicto de la zona estable?

4. **El RGB.** En el RGB de la banda C, en el de la L y en el de la P, ¿de qué color se ve
   el monte y de qué color el pajonal? Proponga el mecanismo de dispersión compatible
   con cada color y la longitud de onda (5,5 cm, 24 cm y 69 cm). ¿Por qué la intensidad
   dual no alcanza para confirmarlo? Con el SAOCOM cuadripolar (`Tp2_05`), ¿qué
   diferencia HH − VV da lo estable y qué haría falta para confirmar el doble rebote?

5. **Sinergia: qué ve cada banda.** Con `A2_IBICUY_contraste_entre_clases.csv`, ¿qué
   banda y qué polarización separan mejor el monte del pajonal? ¿Y el agua calma del
   agua rizada (cuidado: si sus polígonos se eligieron con la C VV, su contraste en C VV
   no es un resultado)? Responda con el contraste en dB, no con el valor de cada clase.
   ¿Coinciden las bandas en el orden de las clases? Si no coinciden, ¿qué explicación
   física propone?

6. **Valores absolutos frente a contrastes.** La media del agua calma no es la misma en
   C, S y L. ¿Es un error de calibración? ¿Por qué se comparan contrastes y no valores
   entre sensores distintos?

7. **Control en zona estable.** Informe la diferencia de medias, el rango por polígono y
   el veredicto de cada par (los archivos `A2_IBICUY_control_zona_estable_….csv` que
   guardó en el paso 8 con `--sufijo`). Si algún par no cumple, ¿qué causa
   propone (humedad, órbita, normalización, corregistro, polígono mal elegido)? ¿Qué
   haría para distinguir entre ellas?

8. **Fusión, todavía no.** La pila tiene todas las bandas en la misma grilla. ¿Por qué
   eso no alcanza para hacer una fusión a nivel de píxel? ¿Qué falta comprobar y en qué
   práctico se comprueba?

9. **Ausencias y limitaciones.** ¿Qué bandas no entraron en la pila de Ibicuy (X,
   NovaSAR) y por qué? ¿Por qué el SAOCOM del 24/09/2026 se compara aparte en lugar de
   entrar en la pila? ¿Cuántos días separan la banda P de la L y de la C? Nombre dos limitaciones del procesamiento (por ejemplo,
   órbita de anotación si falló la precisa, sitio de ubicación aproximada, NovaSAR en
   σ⁰, fechas distintas entre C y L) que un lector del informe debería conocer.

10. **El contexto del sitio.** Con MapBiomas 2025 y el workflow `Tp2_E` de Orange, ¿qué
    banda separa mejor el bosque de las herbáceas inundables en todo el sitio (diferencia de
    medianas de la cruzada)? ¿Coincide con lo que dieron los polígonos del paso 7? ¿Qué biomasa
    da el CCI a las herbáceas inundables y por qué no se toma como verdad?

11. **Diseño para una emergencia.** Durante una crecida del Delta hay que mapear el bosque
    inundado en 48 horas. Con lo que midió en este práctico, ¿qué banda y qué polarización
    pediría, con qué fecha respecto del pico, y qué control haría antes de usarla?
    Justifique con dos cifras de sus tablas.

12. **La IA en este práctico.** Con `01_Prompt_IA`, ¿qué error traía la respuesta de la IA,
    qué control del protocolo de verificación (A1 a A9) lo detectó y cómo se corrigió?
    ¿Cuánto cambiaría la media del pajonal en L HV si se cometiera ese error?

## Producto a entregar

- La pila y su tabla de bandas, con sensor, longitud de onda y fecha de cada banda
  (las de SNAP, tal como se pasaron en `--extra`).
- El `.dim` de Sentinel-1 con bandas lineales y virtuales en dB.
- Los RGB, la tabla de respuesta por cubierta, la de contraste y la figura de cajas.
- La tabla del control en zona estable.
- Las cifras de los polígonos propios del grupo y una línea que las compare con las del
  Desarrollo (por ejemplo: «nuestro contraste monte–pajonal en L HV fue X dB frente a
  7,25 dB del Desarrollo, porque…»).
- Las respuestas a estas doce preguntas y la tabla de verificación.
- El registro del sorteo de los polígonos: de qué sorteo salió cada uno y el motivo de
  cada punto descartado.

## Rúbrica

| Criterio | Peso | Logrado | Parcial | No logrado |
|---|---|---|---|---|
| Cadena SNAP correcta (β⁰, Terrain Flattening, EPSG:32721, BEAM-DIMAP, speckle aparte) | 15 % | Completa y controlada | Completa sin controles | Falta un eslabón o va a σ⁰ |
| Unidades: lineal para operar, dB para ver; σ⁰ declarado | 15 % | Sin excepciones | Una excepción declarada | Promedios en dB o σ⁰ sin declarar |
| Pila y RGB (bandas, nombres, unidades, fuentes, ausencias) | 10 % | Pila completa, ausencias explicadas | Pila completa sin ausencias | Bandas sin unidad o sin fuente |
| Muestreo de cubiertas: sorteo documentado, motivo de cada punto descartado, clases raras por sorteo estratificado, criterios que no usan la banda evaluada | 10 % | Sorteo y criterios documentados | Sorteo sin motivos de descarte | Polígonos elegidos a ojo |
| Sinergia: interpretación física de la respuesta por cubierta | 20 % | Contrastes explicados por mecanismo y longitud de onda | Contrastes descriptos sin física | Valores absolutos comparados entre sensores |
| Control en zona estable | 15 % | Veredicto por par y causas propuestas | Veredicto sin análisis | Sin control |
| Contexto del sitio (paso 9): MapBiomas y CCI como referencias, no como verdad | 10 % | Contraste por clase y límites de cada producto | Cifras sin límites | MapBiomas o CCI tomados como verdad |
| Trazabilidad (cada cifra con su archivo) | 5 % | Todas citadas | Algunas citadas | Ninguna citada |
