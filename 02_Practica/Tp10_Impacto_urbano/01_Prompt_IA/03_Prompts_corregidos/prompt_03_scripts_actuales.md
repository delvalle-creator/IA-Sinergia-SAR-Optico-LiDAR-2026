# Prompt 03 — el que corresponde a los scripts actuales del Tp10

Este prompt describe los seis programas de `03_Scripts` tal como están ahora (Tp10_01 a Tp10_06). Cada requisito numerado corresponde a algo que se puede verificar en el código o en la bitácora; la tabla del final dice cómo.

---

> ## Contexto
>
> Curso de posgrado sobre sinergia y fusión SAR – óptico – LiDAR para emergencias ambientales. Práctico Tp10: **¿cómo crece la ciudad y dónde se hunde el terreno?** Lo corren estudiantes que no programan, en Windows, desde el Miniforge Prompt con el entorno `sar`. Las rutas, los sitios (`B_CONCORDIA`, `E_PARANA_DIAMANTE`) y la grilla EPSG:32721 salen de `00_COMUN/configuracion_comun.py`; no los redefina. Comentarios y mensajes en castellano con tildes (UTF-8); parámetros arriba; semillas fijas; cada programa deja una bitácora en `05_Resultados/06_Control_calidad` y termina con «SIGUIENTE PASO».
>
> ## Requisitos
>
> 1. **Tp10_01 (sinergia).** Un mapa urbano por banda (C VV de Sentinel-1 RTC, S HH de NovaSAR 47942 en σ⁰, L HH de NISAR GCOV) con un umbral en dB documentado en su histograma (`--u_c`, `--u_s`, `--u_l`; `--otsu` opcional). NovaSAR se georreferencia por defecto con **todos** los puntos de enlace del `metadata.xml` (`--puntos_enlace todos`) y se corrige con `--desplazamiento DX DY` (DX positivo = este). Los tres mapas se comparan **sin fusionarlos** (tabla de coincidencias, sólo donde todas las bandas tienen dato). El detalle a 6, 10 y 20 m usa el mismo número de vistas y la misma unidad mínima de mapeo en las tres escalas (`--umm_m2`, por defecto 1.200 m²).
> 2. **Tp10_02 (fusión de rasgos).** Compuestos de temporada (Sentinel-1: media lineal de hasta 5 pasadas de una órbita; Sentinel-2: mediana sin nube, excluyendo el 04/09/2026, que es la referencia de la validación). Entrenamiento de píxeles estables de MapBiomas 2023-2025 **en proporción al paisaje** (mínimo 600 por clase). Un Random Forest (300 árboles, semilla 2026) por conjunto de capas: óptico, C, C + L, multisensor y multisensor con S (sólo en la huella). Se llama **fusión de rasgos** porque entran índices y textura. `--equilibrar` repite, para mostrarlo, el entrenamiento con el mismo peso por clase. La exactitud fuera de bolsa se rotula OPTIMISTA. La importancia de Gini se guarda con la aclaración de que no reparte el aporte de cada sensor.
> 3. **Tp10_03 (detección de cambios por comparación posterior a la clasificación).** Cada año (± 30 días del 01/11/2019 y del 01/10/2026, misma órbita relativa) se clasifica con el método del requisito 2 y el entrenamiento de MapBiomas de ese año. Un píxel cambia sólo si p ≥ `--p_min` (0,6) en las dos fechas y forma una mancha de al menos `--umm` píxeles; lo demás es «sin decidir». Declarar en la bitácora que esa exigencia es sólo para el cambio (asimetría). Guardar la matriz de transiciones (urbano 2019 × urbano 2026 × confiable). Avisar si la clase 4 supera `--aviso_clase4` (0,2) de la clase 2.
> 4. **Tp10_04 (red de pares de línea de base corta).** Buscar en ASF las SLC, elegir la órbita con más escenas, unir cada fecha con sus vecinas, marcar aptos (≤ 48 días, ≤ 150 m) y dibujar **todos** los pares (usados, aptos no usados, no aptos). No llamarla SBAS: la inversión SBAS no se hace.
> 5. **Tp10_05 (velocidad por apilado de tasas).** velocidad = Σ desplazamientos / Σ intervalos (explicar que pesa más los pares largos); referencia estable restada par por par; control en puntos fuera de la referencia con media, desvío, **error de la media** y el criterio |media| < 2 × error de la media. Marcar los pares con salto de desenrollado (más de `--frac_salto` de píxeles a más de `--salto_mm` de la mediana del par) y permitir `--descartar_saltos`. Avisar si la ventana no es un número entero de años (señal estacional). Bandas `velocidad_mm_por_anio` y `dispersion_entre_pares_mm_por_anio`.
> 6. **Tp10_06 (dominio común).** Evaluar las cinco variantes sólo en la huella de NovaSAR con el estimador de Stehman (2014), con los puntos de cada variante que caen en ella y el área de cada estrato dentro de la huella.

---

## Verificación (qué mirar para saber si el programa cumple el prompt)

| N.º | Requisito | Dónde se verifica | Qué tiene que aparecer |
|---|---|---|---|
| 1 | Puntos de enlace por defecto | `Tp10_01 --help` y bitácora | `todos`; «Georreferencia: puntos de enlace del metadata.xml» |
| 2 | Unidad mínima en el detalle | bitácora de Tp10_01 | «se descartan las manchas de menos de 1200 m² en las tres escalas» |
| 3 | Sinergia sin fusión | `B_CONCORDIA_coincidencias_urbano.csv` | sólo píxeles con dato en todas las bandas |
| 4 | Fusión de rasgos y entrenamiento proporcional | bitácora de Tp10_02 | «FUSIÓN DE RASGOS - Random Forest, entrenamiento proporcional» |
| 5 | Exactitud optimista rotulada | bitácora de Tp10_02 | «exactitud fuera de bolsa (OPTIMISTA)» |
| 6 | Asimetría declarada | bitácora de Tp10_03 | «Asimetría de la regla: p >= 0.60 se exige sólo para el cambio» |
| 7 | Matriz de transiciones | `B_CONCORDIA_expansion_matriz_transiciones.csv` | 8 filas (sí/no × sí/no × confiable) |
| 8 | Aviso de clase 4 al 20 % | bitácora de Tp10_03 | «AVISO: la clase 4 supera el 20 % de la clase 2» (en la corrida del docente, 28,5 %) |
| 9 | Red completa dibujada | `E_PARANA_DIAMANTE_red_sbas.png` | pares usados, aptos no usados y no aptos, con leyenda |
| 10 | Criterio del control | bitácora de Tp10_05 | «Criterio: \|media\| < 2 × error de la media (...): CUMPLE / NO CUMPLE» |
| 11 | Pares con salto | bitácora y `E_PARANA_DIAMANTE_pares_usados.csv` | «Pares sospechosos de salto de desenrollado: N de M»; columnas `par_sospechoso` y `usado` |
| 12 | Dominio común | `tabla_de_variantes_urbano_huella_S.csv` | las cinco variantes con comisión, omisión y área en la huella |

Un requisito que el código no cumple se anota en la bitácora de IA como corrección humana.
