# Tp6 — Preguntas y entrega

Cada respuesta cita el archivo del que sale cada cifra.

## Preguntas

1. **El umbral.** ¿Qué umbral de VV quedó, con qué método y sobre cuántos valores? ¿Por qué se calcula una sola vez, en la fecha con Sentinel-1 y Sentinel-2 del mismo día (04/11/2023), y no en cada fecha? ¿Es esa fecha el pico de la serie? ¿Por qué se calcula fuera del agua permanente, y qué consecuencia tiene eso sobre Otsu? (`B_histograma_VV_pico.png`, `Tp6_01_serie.log`)
2. **Extensión y duración.** ¿Cuál fue la extensión máxima del agua de inundación, y cuál la persistente (agua en al menos dos fechas)? ¿Cuántas hectáreas tuvieron más de 30 días de agua con la duración mínima y con la máxima? ¿Con qué resolución temporal se mide la duración, y por qué? (`B_extension_y_duracion_C_20m.tif`, `B_serie_agua_C.csv`)
3. **Agua permanente y embalse.** ¿Qué porcentaje del sitio es agua permanente según JRC? Explique por qué el embalse rizado por el viento se aclara en VV y qué pasaría con el mapa si no se excluyera.
4. **Sinergia.** El 04/11/2023, ¿qué porcentaje del agua ven ambos sensores, cuánto sólo C y cuánto sólo el óptico? Explique físicamente dos casos de desacuerdo que haya mirado en QGIS. (`B_sinergia_agua.csv`)
5. **Lo que falta.** ¿Qué agua no ve ningún sensor disponible el 04/11/2023? ¿Qué aportaría la banda L, con qué mecanismo? Con los SAOCOM del 10/10 y el 11/11/2023, ¿por qué la regla fija de 3 dB marca medio sitio y qué queda con `--l_relativo --l_solo_lenoso`, restando la mediana del sitio o la de la propia clase leñosa (`--l_base clase`)? ¿Qué papel puede tener la escena NovaSAR del 13/09/2023?
6. **Fusión.** Escriba las reglas R1 a R5 con sus palabras. ¿Por qué es fusión de decisión y no de píxel? ¿Qué error favorece una unión? ¿Qué agua real puede borrar R5 con una referencia seca de 2026? (`Tp6_03_fusion.log`)
7. **Validación e incertidumbre.** Complete la tabla de variantes con exactitud global, omisión y comisión de agua y área estimada ± IC. ¿La multisensor mejora a la C sola? Calcule a mano el IC del 95 % de la diferencia de omisión: diferencia ± raíz(IC₁² + IC₂²). ¿Excluye el cero? ¿Por qué la variante óptica no es comparable en área cuando hay nubes? ¿Qué variantes favorece la referencia usada? (`tabla_de_variantes_agua.csv`)
8. **Profundidad.** Dé la mediana, el percentil 90 y el máximo, y el porcentaje de valores negativos, con los valores llevados a 0 y sin recortar, con el Copernicus DEM y con FABDEM. ¿Dónde están las mayores profundidades? ¿Son creíbles? (`Tp6_04_profundidad.log`, `Tp6_04_profundidad_fabdem.log`, `B_profundidad_*_20m.tif`)
9. **El MDE.** ¿Qué sesgo y qué RMSE tiene el Copernicus DEM frente a ICESat-2 por clase de la cobertura de control y por clase de MapBiomas 2023? ¿Cuántos segmentos hay en cada estratificación? ¿Cuánto sesgo y cuánto error por píxel hereda la profundidad de los bañados? ¿Qué habría pasado sin convertir ATL08 a EGM2008? (`B_control_mde_icesat2.csv`, `B_control_mde_icesat2_mapbiomas.csv`)
10. **Limitaciones.** Nombre al menos tres con su efecto (banda L con un solo par y un cambio general entre fechas; nubes en el óptico; revisita de 12 días; MDE de superficie de 2011–2015; la profundidad no se valida con hidrómetros; la referencia de validación es el mismo Sentinel-2 que entra en la óptica y en la multisensor; la referencia seca es posterior al evento).
11. **La segunda crecida.** Compare el agua en banda C del 04/11/2023 y del 14/05/2024: ¿qué superficie comparten, cuál aparece sólo en una crecida y por qué en mayo la decisión queda en un solo sensor? (`B_agua_C_por_fecha_20m.tif`, bandas `agua_20231104` y `agua_20240514`)
12. **Diseño.** Diseñe una referencia seca y una muestra de validación que permitan demostrar si la multisensor omite menos que la C (estratos, tamaño, fuente de referencia) y justifíquelo.

## Preguntas optativas (para profundizar)

- **A.** ¿Qué agrega el ALOS-2 del 16/11/2023 que no agregaba el SAOCOM? ¿Por qué no sirve para medir doble rebote?
- **B.** ¿Para qué sirven los embeddings AlphaEarth anuales en una inundación de semanas?
- **C.** ¿Por qué no se calcula un cambio entre una fecha procesada en SNAP y otra del RTC?
- **D.** En Orange (`Tp6_A`), ¿qué banda ordena primero el Rank y dónde corta el árbol? Compárelo con el −15 dB de VV.

## Producto a entregar

Mapas de extensión, duración y profundidad, con leyenda, fecha, fuentes e incertidumbre; la tabla de variantes con IC; la tabla de sinergia; el control del MDE; las respuestas.

## Rúbrica

| Criterio | Peso | Logrado | Parcial | No logrado |
|---|---|---|---|---|
| Serie de agua con umbral único y órbita única | 15 % | Histograma, umbral justificado, una órbita, una fila por fecha; duración mínima y máxima | Umbral sin revisar | Umbrales por fecha u órbitas mezcladas |
| Exclusión del agua permanente y del embalse | 10 % | Explicada físicamente y verificada en QGIS | Aplicada sin explicar | El río cuenta como inundación |
| Sinergia C–óptico y lo que falta | 15 % | Tabla interpretada; desacuerdos explicados; banda L probada y su resultado declarado con su efecto | Tabla sin interpretar | Sinergia confundida con fusión o L inventada |
| Fusión de decisión con reglas escritas | 15 % | Reglas R1 a R5 explicadas, con el agua que puede borrar R5; elección del nivel justificada | Reglas copiadas sin justificar | Combinación sin reglas |
| Validación con IC | 15 % | Tabla completa; IC de la diferencia calculado; conclusión acorde a los IC; límite de la variante óptica dicho; referencia independiente o sesgo declarado por variante; misma definición de agua en mapa y referencia | Conclusión exagerada | Área por conteo de píxeles |
| Profundidad y control del MDE | 15 % | Profundidad con su incertidumbre heredada (sesgo y RMSE); monte excluido o advertido | Profundidad sin control | Profundidad presentada como medida |
| La segunda crecida | 5 % | Superficie común y exclusiva cuantificada; ausencia del óptico declarada | Comparación sin cifras | No se compara |
| Comunicación | 10 % | Mapas con leyenda, fecha, fuentes e incertidumbre | Falta un elemento | Mapas sin fuente ni fecha |
