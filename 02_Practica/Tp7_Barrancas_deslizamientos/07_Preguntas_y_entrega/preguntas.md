# Tp7 — Preguntas, producto y rúbrica

Cada respuesta cita el archivo (y la fila o banda) del que sale la cifra.

## Preguntas

1. **El dato vacío.** ¿Qué valores tenía la banda `Unw_Phase` del producto del
   curso 2023 y qué escribió `Tp7_02` cuando la recibió? ¿Por qué un cero en
   todo el sitio no puede leerse como «barranca estable»?
   (`Tp7_02_deformacion.log` y estadísticas de SNAP.)

2. **El par en banda C.** ¿Qué par Sentinel-1 eligió (o usó de HyP3)? Dé fechas,
   días, línea de base perpendicular y pasada (`E1_pares_S1.csv`). ¿Coincide la
   pasada con la del par COSMO-SkyMed? ¿Qué consecuencia tiene para la regla de
   signo de la fusión?

3. **Sinergia de coherencias.** Compare la coherencia de X y C en el bosque
   cerrado de MapBiomas 2018 y en la zona urbana (`E1_coherencia_y_desplazamiento.csv`
   y `08_Orange/Tp7_A`). ¿Qué parte de la diferencia atribuye a la longitud de
   onda y qué parte a la resolución (2 m frente a 40 m), la polarización y el
   intervalo? ¿Qué esperaría en banda L?

4. **Ruido y detección.** Para cada banda, ¿el desvío en la zona de referencia
   es menor que el umbral de 10 mm? Si no lo es, ¿qué puede afirmar sobre la
   deformación de la ladera con esa banda?

5. **Fusión de decisión.** Escriba la regla exacta que aplicó el script. ¿Cuántos
   píxeles quedaron confirmados en la ladera y cuántos en la referencia, y cuántos
   en una zona de control independiente (`--control_independiente`)? ¿Qué
   fracción de la ladera quedó decidida (`Tp7_02_deformacion.log`;
   `E1_deformacion_confirmada.tif`, bandas 1 y 2)? ¿Por qué un píxel en el que
   tiene dato una sola banda queda sin decidir y no «confirmado»?

6. **La referencia.** ¿Cuántos píxeles de agua quitó el JRC del anillo
   (`Tp7_02_deformacion.log`)? ¿Qué pasaría con la «coherencia media de
   referencia» y con el sesgo entre MDE si el río quedara dentro? ¿Usó el anillo
   o una zona estable digitalizada (`--zona_estable`), y por qué?

7. **Volumen y su límite de detección.** Dé el sesgo restado, el ruido, el
   volumen de la cicatriz y del depósito, el volumen detectable con su
   incertidumbre y el porcentaje de píxeles sobre dos desvíos con el signo
   esperado y con el contrario (`E1_volumenes.csv`). ¿Se repite el patrón en la
   escarpa de control? ¿Es detectable el volumen con estos MDE? Los dos (GLO-30
   2011–2015 e IGN 2013) son anteriores al evento: ¿qué mide entonces esa
   diferencia? ¿Qué MDE haría falta para medir el volumen de 2018, y con qué
   resolución, dado el ancho de la cicatriz (unos 55 m)?

8. **Control con ICESat-2.** ¿Cuántos segmentos ATL08 válidos cayeron en tierra
   firme estable (fuera de la ladera, del anillo urbano y del río)? ¿Qué sesgo,
   desvío y NMAD dio cada MDE contra ellos, con la cota de ICESat-2 en el sistema
   vertical de cada MDE (EGM2008 para GLO-30 y FABDEM; SRVN16 para el IGN)? ¿Le
   alcanza ese control para confiar en el MDE de la barranca misma?

9. **Limitaciones.** Enumere tres limitaciones de este análisis que no se pueden
   resolver con los datos del curso (por ejemplo: LOS frente a movimiento real
   de una ladera que se desplaza hacia el río; ausencia de banda L en 2018;
   pixel de 40 m de HyP3 frente al ancho de la barranca) y diga cómo cambiarían
   la respuesta.

10. **Registros locales.** La diapositiva 30 pide «confirmar los eventos con
    registros locales antes de elegir las fechas». ¿Qué registro encontró
    (municipio, prensa, Defensa Civil) y coincide con el período del par X?
    ¿Qué toma de la prensa y qué de una fuente revisada por pares?

11. **Diseño.** Diseñe el relevamiento que haría falta para medir el próximo
    evento (sensor, banda, geometría, revisita, MDE posterior, GNSS) y justifique
    cada elección con los límites medidos en este práctico.

### Preguntas de ampliación (optativas, fuera de la evaluación)

- **Velocidad 2025–2026** (`Tp7_05`, con la velocidad del Tp10). ¿La franja de
  150 m del borde baja más que el interior, y la diferencia supera el error
  estimado de la velocidad?
- **Embeddings AlphaEarth** (`Tp7_06`). ¿El depósito cambió entre 2018 y 2025
  más que el resto del talud, y qué otra causa podría explicarlo?

## Producto a entregar

Mapa de deformación confirmada (todas las bandas de acuerdo, con las bandas que
votaron) e inventario de evidencias: cicatriz y depósito trazados con su fuente,
diferencia de MDE con su límite de detección y la declaración de por qué no es el
volumen de 2018, más la tabla de verificación completa. Cada figura lleva al pie
la cita **Fuente**.

## Rúbrica

| Criterio | Peso | Logrado | Parcial | No logrado |
|---|---|---|---|---|
| Desenrollado de la banda X rehecho y controlado | 20 % | Fase desenrollada distinta de cero, componentes conexas revisadas, píxeles de la componente 0 enmascarados, parámetros de SNAPHU anotados y georreferencia verificada | Desenrollado hecho sin controles | Se usó la banda vacía o no se hizo |
| Elección del par C con criterios escritos y registros locales confrontados con las fechas de los pares | 10 % | Fechas, línea de base y pasada justificadas; fecha del evento con su fuente y su consecuencia para cada par | Par elegido sin justificar la pasada o registros citados sin confrontar | Par de otro período |
| Sinergia: coherencia y desplazamiento por banda interpretados con la física | 20 % | Diferencia entre bandas separada en longitud de onda, resolución, cobertura e intervalo | Tabla presentada sin interpretación | Valores mezclados entre bandas |
| Fusión de decisión correcta y controlada | 15 % | Regla escrita con la geometría de cada banda, fracción de ladera decidida informada, control independiente verificado | Regla escrita sin el control | Se promediaron desplazamientos |
| Cicatriz y depósito trazados con criterios escritos y fuente; volumen con sesgo, ruido y detectabilidad | 20 % | Protocolo de trazado escrito y campo fuente completo; zona estable en tierra, sesgo restado, signo esperado y escarpa de control, «detectable/no detectable» fundado | Volumen con sesgo pero sin detectabilidad, o polígonos sin criterios | Volumen sin control o polígonos sin fuente |
| Control con ICESat-2 y limitaciones declaradas | 15 % | Cota de ICESat-2 en el sistema vertical de cada MDE (EGM2008 para GLO-30 y FABDEM, SRVN16 para el IGN), sesgo por MDE, tres limitaciones concretas | Control sin conversión de altura o limitaciones genéricas | Sin control ni limitaciones |
