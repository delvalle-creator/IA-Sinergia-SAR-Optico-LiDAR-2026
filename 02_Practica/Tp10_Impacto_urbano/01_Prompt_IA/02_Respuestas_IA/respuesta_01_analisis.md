# Qué contestó la IA, y qué había que mirarle

## La respuesta

Un programa prolijo: lectura de las cuatro fuentes, `np.stack` de todas las bandas, `RandomForestClassifier` entrenado con polígonos, `predict` sobre 2019 y sobre 2026, diferencia de los dos mapas. Para la subsidencia, `desplazamiento = fase × λ / (4π)` sobre un par de Sentinel-1. Con comentarios, con gráficos y con una exactitud altísima impresa al final.

## Lo que había que detectar

**El `fillna(0)` antes del `stack`.** Una línea. Rellena con cero las bandas que faltan: la banda S fuera de la huella de NovaSAR y las bandas S y L en 2019. El programa no protesta; el mapa sale completo. Ése es el problema: un mapa completo con datos que no existen.

**La exactitud altísima.** Se calculó con `oob_score_` o con una partición al azar de los píxeles de entrenamiento. Los píxeles vecinos de un mismo polígono se parecen entre sí: validar con ellos mide la memoria del clasificador, no la calidad del mapa. Es el último error de la tabla de la diapositiva 14.

**La fecha de cada capa no figuraba en ningún lado.** Ni en el ráster, ni en la bitácora, ni en el gráfico. Imposible saber que había tres años entre NovaSAR y NISAR sin abrir los metadatos a mano.

**El interferograma sin referencia.** La fase desenrollada de un par empieza en un punto arbitrario. Restar una constante cambia todo el mapa de milímetros y el programa no la restaba: el «cero» era el que eligió el desenrollador.

## Cómo se detectó

**Mirando la variante de 2019.** El mapa de 2019 tenía un borde recto, el mismo de la escena NovaSAR de 2023. Una ciudad no crece con la forma de una franja de satélite.

**Pidiendo la importancia de cada capa.** `S_HH` y `L_HV` estaban arriba. En 2019 esas capas eran ceros: el clasificador había aprendido a separar «hay sensor» de «no hay sensor».

**Comparando dos pares de interferograma.** Dos pares de fechas parecidas daban velocidades de signo opuesto en el centro de Paraná. Sin referencia, cada uno tenía su propio cero.

## La regla

**Si el mapa tiene la forma de la escena, está midiendo la escena.** Y si una fusión se aplica a una fecha en la que uno de los sensores no existía, no es fusión: es relleno.
