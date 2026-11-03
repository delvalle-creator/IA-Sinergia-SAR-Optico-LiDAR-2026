# Tp4 — Preguntas y entrega

Cada respuesta cita el archivo del que sale cada cifra.

## Preguntas

1. **El mapa de control.** ¿Qué porcentaje del sitio quedó sin clase y qué porcentaje de cada clase viene de la digitalización, de JRC y de MapBiomas? ¿Por qué el agua permanente se define con ocurrencia ≥ 90 % y no con ≥ 50 %? (`<SITIO>_cobertura_control_resumen.csv`, bitácora `Tp4_01_<SITIO>.log`)
2. **El tamaño de la muestra.** Calcule a mano el n de su diseño con la ecuación 13 y compárelo con el de la bitácora de `Tp4_02`. ¿Cuántos puntos haría falta etiquetar para llevar S_O a 0,01? ¿Qué decide usted, y qué intervalo informa en consecuencia? (`<NOMBRE>_diseno_muestral.csv`)
3. **Al azar y sin ver el mapa.** Explique con un ejemplo concreto de su sitio cómo el conocimiento de la clase del mapa habría cambiado su etiqueta en un punto dudoso. ¿Cuántos puntos marcó con `confianza = baja`, y en qué clase del mapa cayeron (se averigua después, con la llave)?
4. **Validación e incertidumbre.** Para la clase de interés de su mapa (en el ensayo, la plantación; en los Tp5 y Tp6, quemado o agua), dé el área según el mapa y el área estimada con su IC 95 %. ¿El área del mapa cae dentro del intervalo? Si no, ¿el mapa sobrestima o subestima, y qué error domina, omisión o comisión? (`<NOMBRE>_exactitud_y_area.csv`)
5. **Usuario y productor.** ¿Por qué la exactitud global puede ser alta aunque la clase de interés esté mal mapeada? Muéstrelo con sus números.
6. **Fusión.** Con dos versiones de un mapa (en el ensayo, el mapa de control con y sin el recorte de copas; en un práctico específico, la variante multisensor y una de un solo sensor), ¿la diferencia de exactitud o de omisión tiene un IC del 95 % que excluye el cero (d = O₁ − O₂, V(d) = V₁ + V₂)? Si no lo excluye, ¿qué tamaño de muestra habría hecho falta para decidirlo? (`tabla_de_variantes_<clase>.csv`)
7. **Sinergia.** ¿Para qué usó el Tp5 (o el Tp6) la cobertura de control? Dé un ejemplo de una lectura de la tabla de coincidencias que sólo es posible gracias a ella.
8. **Independencia de la referencia.** ¿Qué imágenes usó para etiquetar los puntos (en el ensayo, las teselas usadas y su fecha si la tienen; en un evento, fuente y fecha)? ¿Hay alguna variante cuya validación quedó sesgada porque la referencia comparte sensor con ella? Declárelo.
9. **Limitaciones.** Nombre tres limitaciones de su validación (por ejemplo: imágenes de referencia sin la fecha del evento, puntos sin etiquetar, mezcla de clases en el píxel de 20 m, mapa de control incompleto, MapBiomas como producto de terceros) y diga cómo afecta cada una a las cifras.

10. **Un mapa real: MapBiomas 2025.** Con el paso 10: ¿cuál es la exactitud global de MapBiomas 2025 en B_CONCORDIA, con la equivalencia de clases del curso, y qué clases sostienen o hunden ese número (usuario y productor)? ¿Qué clase sobrestima y cuál subestima el mapa, según el área estimada con su IC? ¿Qué dicen el CCI Biomass 2024 y la banda P VH de cada clase, y por qué no pueden usarse como referencia? ¿Cuánto depende la exactitud de la equivalencia de clases y del protocolo de respuesta? ¿Para qué clases usaría MapBiomas como contexto en los Tp5 a Tp10? (`B_CONCORDIA_mapbiomas_2025_clases_curso_20m_exactitud_y_area.csv`, `B_CONCORDIA_mapbiomas_2025_contexto_por_clase.csv`, `_muestra_comun_exactitud.csv`)
11. **Diseño de una muestra.** Proponga la muestra para el mapa de quema del Tp5 (estratos, n por estrato y justificación), sabiendo que la clase quemado ocupa ≈ 30 % del sitio y que se van a comparar cuatro variantes. (`Tp4_06_muestra_comun.py --disenar`)

## Producto a entregar

- El mapa de control de B_CONCORDIA (y de A1_DELTA_QUEMAS si se digitalizó), con figura, leyenda y cita de fuente.
- Los GeoPackage etiquetados y las tablas de exactitud y área (incluida la de MapBiomas 2025).
- La tabla de variantes de cada práctico específico en el que participó el grupo.
- Las respuestas y la tabla de verificación completa.

## Rúbrica

| Criterio | Peso | Logrado | Parcial | No logrado |
|---|---|---|---|---|
| Mapa de control con fuentes declaradas y clases estables | 10 % | Prioridad de fuentes respetada, polígonos lejos de bordes, tabla por fuente | Mapa sin tabla o con clases inestables | Sin mapa o con el mapa usado como verdad |
| Diseño de la muestra | 15 % | n calculado a mano y coincidente; decisión de S_O declarada; diseño propio de la pregunta 11 justificado | n del script sin justificar | Muestra no estratificada o no aleatoria |
| Etiquetado al azar | 20 % | Sin mapa ni llave a la vista; protocolo de respuesta aplicado; confianza, fuente y fecha (o «sin fecha») en cada punto; acuerdo entre intérpretes medido (Tp4_07) | Etiquetado completo sin registro de fuente o sin acuerdo medido | Llave abierta antes de tiempo o mapa visible |
| Exactitud y área con IC | 20 % | Usuario, productor, global y área con IC, bien interpretados | Cifras correctas mal interpretadas | Área por conteo de píxeles o sin IC |
| Comparación de variantes | 5 % | Conclusión por la diferencia y su IC | Conclusión por solapamiento de IC o que exagera la mejora | Sin comparación |
| Validación de un mapa de terceros (paso 10) | 15 % | Exactitud y área de MapBiomas con IC, dependencia de la equivalencia declarada, contexto (CCI, banda P) no usado como referencia | Cifras correctas sin discutir la equivalencia | Sin validar o con el CCI o la banda P como referencia |
| Limitaciones e independencia de la referencia | 15 % | Declaradas con su efecto en las cifras | Declaradas sin efecto | No declaradas |
