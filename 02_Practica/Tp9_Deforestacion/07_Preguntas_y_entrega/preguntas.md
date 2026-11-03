# Tp9 — Preguntas, producto y rúbrica

Cada respuesta cita el archivo (y la fila, columna o banda) del que sale la cifra.

## Preguntas

1. **La pila.** ¿Qué capas entraron y con qué % de dato (`Tp9_01_pila.log`)?
   ¿Por qué no hay `L_ALOS1_2011_HV`? ¿Qué parte del sitio no tiene banda S y por
   qué?

2. **Calibración cruzada.** ¿Qué zona estable usó (clases y píxeles) y qué
   desfase dio cada producto de banda L respecto de ALOS-2 2021
   en el monte y en la ciudad (`C_calibracion_cruzada.csv`), y qué residuo queda
   después de corregir? Con el residuo de la Tabla 4 del desarrollo, ¿qué umbral
   de cambio usaría para la variante L en el monte y por qué?

3. **Sinergia: qué estrato ve cada banda.** Ordene las capas por ρ de Spearman y
   por rango de la curva (`C_sensibilidad_a_la_altura.csv`). En
   `C_curvas_de_respuesta.png`, ¿en qué clase de altura se aplana cada banda?
   Explique el resultado con la longitud de onda (C 5,5 cm, S 9,4 cm, L ≈ 24 cm,
   P 69 cm) y la estructura del monte del Espinal.

4. **Fechas y huellas.** ¿Qué capas no se evaluaron por falta de huellas
   cercanas en fecha? ¿Por qué ALOS-1 2011 no puede compararse con GEDI? ¿Qué
   capa tiene la ρ con menos huellas, y cuánto vale esa ρ?

5. **Banda P.** Sobre las mismas huellas de Federal, ¿la curva de BIOMASS (VH)
   sigue subiendo donde la de banda C ya se aplanó? ¿Y frente a la L? ¿Cuántas
   huellas quedaron a menos de 730 días del 12/08/2026, y qué dice eso de la
   confianza en esa ρ?

6. **Degradación con GEDI.** ¿Cuántas celdas de 200 m tienen al menos 2 huellas
   en cada período y cuántas son candidatas a degradación
   (`C_delta_rh98_por_celda.csv`)? Mire dos en la mejor imagen disponible
   (CBERS-4A de 2 m dentro de la ventana; Sentinel-2 o Landsat afuera) y diga qué
   resolución usó: ¿qué se ve? ¿Por qué una caída de menos de 3 m no se interpreta?

7. **Fusión de rasgos.** ¿Qué rasgos entraron, cuál fue la importancia de cada
   uno y qué dice eso sobre lo que aporta cada sensor (`Tp9_03_fusion.log`)? ¿Por
   qué la exactitud fuera de bolsa no se informa como exactitud? ¿Qué rasgo sacaría
   primero en una ablación y qué espera que pase con la comisión?

8. **Cultivos no son desmonte.** Muestre dos lotes cosechados entre 2021 y 2026:
   ¿qué clase les dio la variante «solo óptico» y cuál el mapa multisensor? ¿Qué
   rasgo y qué clase de entrenamiento lo explican?

9. **Validación e incertidumbre.** ¿Qué dice `C_control_gedi_por_clase.csv`?
   ¿El Δrh98 por clase confirma el mapa? ¿Por qué el `count` no son celdas? Con el
   Tp4 (o, si no se llegó a etiquetar, el plan de validación), ¿qué intervalo de confianza esperaría para el
   área de pérdida con la muestra por defecto?

10. **Limitaciones.** Enumere tres limitaciones concretas (por ejemplo: HH en
    2011; fechas ópticas de invierno frente a primavera; 25 m de ALOS-2 llevado a
    20 m; σ⁰ en NovaSAR; huellas GEDI escasas y sin repetición; zona estable
    urbana con doble rebote) y diga cómo cambiarían el mapa.

11. **SAOCOM como control independiente.** Con el ΔHV de SAOCOM 2021–2026 (mediana
    del sitio restada), ¿qué porcentaje de la pérdida y de la degradación de su mapa
    cae más de 3 dB? ¿Coincide con MapBiomas? ¿Por qué la comparación con NISAR
    frente a ALOS-2 no es un control?

## Producto a entregar

Mapa de pérdida y degradación con la importancia de los rasgos, el control con
GEDI, la tabla de calibración cruzada y la tabla de verificación completa; la
exactitud de las variantes del Tp4 si se llegó (si no, el diseño muestral listo).
Cada figura lleva al pie la cita **Fuente**.

## Rúbrica

| Criterio | Peso | Logrado | Parcial | No logrado |
|---|---|---|---|---|
| Pila en lineal y polarizaciones correctas | 5 % | Capas y coberturas informadas; HH en 2011 declarado | Pila sin revisión de coberturas | HV de 2011 inventado o dB promediado |
| Calibración cruzada y umbral interpretable | 15 % | Zona estable justificada, desfase por zona leído y umbral comparado con el residuo en controles independientes | Desfases informados sin consecuencia | Sin calibración y sin declararlo |
| Sinergia: estrato que ve cada banda | 15 % | Curvas y ρ interpretadas con la física y con el número de huellas | Tabla sin interpretación | Capas comparadas con huellas de otra época |
| Entrenamiento | 15 % | Polígonos sorteados, fuera de la ventana CBERS, con criterio anotado y cultivos cosechados en clase 4 | Polígonos agregados a ojo o sólo en la ventana | Polígonos de partida sin revisar |
| Validación | 15 % | Diseño muestral, etiquetado a ciegas, exactitud y área con IC leídos | Exactitud sin IC o sin diseño | Exactitud fuera de bolsa como exactitud |
| Degradación con GEDI | 10 % | Celdas candidatas verificadas en imagen y límites declarados | Tabla sin verificación | No se hizo |
| Fusión de rasgos y control de cultivos | 15 % | Importancias leídas, cultivos verificados como clase 4, control GEDI leído | Mapa sin control | Exactitud fuera de bolsa informada como exactitud |
| Limitaciones e incertidumbre | 10 % | Tres limitaciones con su efecto y plan de validación | Limitaciones genéricas | Ninguna |
