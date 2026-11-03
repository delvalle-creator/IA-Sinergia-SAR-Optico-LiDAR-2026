# Prompt corregido — el que produjo los scripts del Tp4

---

> **Contexto.**
> Curso de posgrado «Sinergias multisensor y estrategias de fusión SAR-Óptico-LiDAR
> para evaluación de emergencias ambientales», Diamante (Entre Ríos), 2026.
> Python 3.11 en un entorno de Miniforge llamado `sar` (canal conda-forge:
> numpy, pandas, geopandas, pyogrio, rasterio, pyproj, pystac-client,
> planetary-computer). Windows; los estudiantes corren los scripts desde el
> Miniforge Prompt, dentro de `02_Practica\Tp4_Validacion\03_Scripts`.
>
> Todo el curso usa una única configuración, `02_Practica\00_COMUN\configuracion_comun.py`
> (SITIOS, EPSG, rutas, `ruta_tp()`), y funciones comunes en
> `00_COMUN\funciones_comunes.py` (`grilla_sitio()`, `leer_en_grilla()`,
> `jrc_ocurrencia()`, `guardar_tif()`, `Bitacora`). Los scripts **importan**
> esas funciones; no las reescriben. Cada script sube por el árbol de carpetas
> hasta encontrar `00_COMUN` y lo agrega a `sys.path`.
>
> Grilla común: EPSG:32721 (WGS 84 / UTM 21S), bordes alineados a múltiplos del
> píxel; 20 m en este práctico (el píxel de los prácticos específicos). Valor
> sin dato de los GeoTIFF: −9999.
>
> Sitios: `B_CONCORDIA` (−58,25, −31,50, −57,85, −31,10), sitio del Tp4, Tp6 y
> Tp10; `A1_DELTA_QUEMAS` (−59,96, −33,36, −59,72, −33,07), que el Tp5 necesita.
> Cualquier sitio de `SITIOS` debe aceptarse por argumento.
>
> Lo que **no** existe: un mapa de cobertura de referencia de Entre Ríos. Hay que
> generarlo. Lo que sí existe: JRC Global Surface Water en el Planetary Computer
> (colección `jrc-gsw`, activo `occurrence`, 0 a 100 %, sin cuenta) y rásteres de
> bosque de MapBiomas Argentina 2023 recortados a las escenas NovaSAR, en la
> carpeta raíz de NovaSAR (`MAPBIOMAS_BOSQUES`), con nombres
> `Bosques_MapBiomas_2023_*.tif`.
>
> **La pregunta del práctico:** ¿cuán confiable es un mapa de emergencia y cuánta
> área afectada hay realmente? Las herramientas se reutilizan en los Tp5 a Tp10
> para validar cada variante (óptico solo, SAR solo C, SAR multibanda, multisensor)
> y responder cuánto mejora la exactitud al sumar bandas y sensores.
>
> **Escriba cuatro scripts.**
>
> **`Tp4_01_cobertura_de_control.py` — mapa de cobertura de control.**
>
> 1. Argumentos: `--sitio` (obligatorio, una clave de `SITIOS`), `--pixel`
>    (float, 20 por defecto), `--sin_jrc` (no consultar JRC si no hay internet).
> 2. Ocho clases fijas con código entero: 1 agua_permanente, 2 humedal_pajonal,
>    3 monte_nativo, 4 plantacion_forestal, 5 cultivo_pastura, 6 suelo_desnudo,
>    7 urbano, 8 otra. 0 = sin clase.
> 3. Tres fuentes con **prioridad estricta**: la primera que tiene dato en un
>    píxel manda y las siguientes sólo llenan píxeles vacíos.
>    a) Polígonos digitalizados por el grupo: `Tp4_Validacion\04_Tablas_de_trabajo\control_digitalizado_<SITIO>.gpkg`,
>       capa `control`, campo entero `codigo`. Se reproyectan a la grilla y se
>       rasterizan; sólo se aceptan códigos 1 a 8.
>    b) Agua permanente: JRC GSW con ocurrencia **≥ 90 %** → clase 1, leída con
>       remuestreo por vecino más próximo. Si la lectura falla, se escribe el
>       motivo en la bitácora y se sigue sin JRC: nunca se aborta.
>    c) MapBiomas bosque: todo valor > 0 → clase 3, leído con remuestreo por
>       **moda** (es una clase, no se promedia). Se declara en la bitácora que es
>       un producto de terceros hecho con Landsat.
> 4. Si el GeoPackage digitalizado no existe, crearlo vacío, con tipo de geometría
>    **Polygon** declarado (si no, QGIS no habilita el dibujo), en EPSG:32721, capa
>    `control`, con los campos `codigo` (int32), `clase`, `fuente_interpretacion`,
>    `fecha_imagen`, `interprete`, y explicar en la bitácora qué va en cada campo.
> 5. Guardar un registro de la fuente de cada píxel (1 digitalizado, 2 JRC,
>    3 MapBiomas).
> 6. Salida: `Tp4_Validacion\02_Subsets_SNAP_QGIS\<SITIO>_cobertura_control_<pixel>m.tif`
>    con dos bandas con nombre: `clase_control` y `fuente_control`. En los
>    metadatos del GeoTIFF (con `guardar_tif`), la cita de las fuentes: digitalización
>    del grupo sobre imágenes de muy alta resolución; JRC Global Surface Water
>    (Pekel et al., 2016), https://global-surface-water.appspot.com; MapBiomas
>    Argentina colección de bosques 2023, https://argentina.mapbiomas.org; y el
>    proceso (“prioridad: digitalizado > JRC > MapBiomas”).
> 7. Tabla `Tp4_Validacion\05_Resultados\04_Tablas\<SITIO>_cobertura_control_resumen.csv`:
>    por clase, píxeles, superficie en ha y cuántos píxeles vienen de cada fuente.
> 8. Bitácora: el porcentaje del sitio sin clase, con la aclaración de que es
>    normal.
> 9. El docstring debe decir **qué no es** este mapa: no es la verdad de campo, y
>    la exactitud nunca se calcula contra él. Y debe listar sus tres usos:
>    estratificar el muestreo, definir zonas de control para los otros prácticos
>    (zona estable del Tp2, agua permanente del Tp6, zonas no quemadas del Tp5,
>    cultivos del Tp9) y comparar mapas.
>
> **`Tp4_02_muestreo_estratificado.py` — diseño de la muestra y puntos a ciegas.**
>
> 1. Argumentos: `--mapa` (GeoTIFF de enteros, obligatorio), `--banda` (1),
>    `--UA` (exactitud del usuario esperada, 0,85), `--SE` (error estándar buscado
>    para la exactitud global, 0,03), `--minimo` (puntos mínimos por clase, 30),
>    `--semilla` (2026, para que el diseño sea reproducible), `--sobrescribir`.
> 2. Clases = valores > 0 del mapa. Fuera: 0, el valor nodata del archivo y los
>    no finitos. Si hay menos de dos clases, salir con un mensaje claro.
> 3. Tamaño de la muestra con la ecuación 13 de Olofsson et al. (2014):
>    n = (Σ Wᵢ Sᵢ / S_O)², con Wᵢ = proporción de píxeles de la clase i y
>    Sᵢ = √(U (1 − U)). n no puede ser menor que `minimo` × número de clases.
> 4. Reparto: `minimo` puntos por clase y el resto en proporción al área; nunca más
>    puntos que píxeles en una clase.
> 5. Muestreo aleatorio sin reposición dentro de cada estrato; el punto es el
>    **centro del píxel**. Luego se mezcla el orden de todos los puntos y se
>    numeran con `id` desde 1, para que el orden no delate el estrato.
> 6. **El diseño a ciegas es no negociable.** Dos archivos separados:
>    - `Tp4_Validacion\04_Tablas_de_trabajo\<NOMBRE>_puntos_a_etiquetar.gpkg`, capa
>      `puntos`, con `id` y los campos vacíos `clase_ref`, `confianza`,
>      `imagen_usada`, `observacion`. **Sin la clase del mapa.**
>    - `Tp4_Validacion\04_Tablas_de_trabajo\<NOMBRE>_llave_NO_ABRIR.csv` con `id` y
>      `clase_mapa`.
>    `<NOMBRE>` es el nombre del archivo del mapa sin extensión.
>    **Proteger el etiquetado:** si el GeoPackage ya existe con algún `clase_ref`
>    cargado, no reescribirlo; avisar en la bitácora y salir. Sólo `--sobrescribir`
>    lo reemplaza.
> 7. El diseño (`clase_mapa`, `pixeles`, `W_i`, `superficie_ha`, `n_i`) en
>    `Tp4_Validacion\05_Resultados\04_Tablas\<NOMBRE>_diseno_muestral.csv`. Lo
>    necesita el paso 3 para los pesos.
> 8. La bitácora imprime la fórmula con los valores usados y el n resultante,
>    la tabla de diseño, y las instrucciones para QGIS: ocultar el mapa evaluado,
>    mirar sólo la imagen de referencia, completar `clase_ref` con el mismo código
>    de clases del mapa, `confianza` (alta/media/baja), `imagen_usada` y
>    `observacion`.
> 9. El docstring explica por qué estratificado (clases raras: el área quemada o
>    inundada suele ser del 1 al 10 % del sitio), por qué aleatorio (permite
>    estimar área e incertidumbre) y por qué a ciegas (sesgo de confirmación), y
>    cuántos puntos dan los valores por defecto (unos 140 para dos clases) frente
>    a S_O = 0,01 (más de 1.000), para que el grupo declare qué intervalo permite la
>    muestra que pudo etiquetar.
>
> **`Tp4_03_exactitud_y_area.py` — exactitud y área con el estimador estratificado.**
>
> 1. Argumentos: `--nombre` (el `<NOMBRE>` del paso 2), `--autoprueba`,
>    `--nombres_clase` (opcional, `"1=quemado,2=no_quemado"`).
> 2. Lee el GeoPackage etiquetado, la llave y el diseño; une por `id`.
> 3. Puntos sin `clase_ref`: se excluyen y **se declara cuántos**. Puntos con una
>    clase de referencia que el mapa no tiene: NO se excluyen (son errores del mapa:
>    entran como columnas de referencia sin estrato); se declara cuántos y cuáles, y
>    se advierte que muchos significan que el mapa omite una clase entera.
> 4. Estimador de Olofsson et al. (2014), con i = clase del mapa (estrato) y
>    j = referencia: Wᵢ = Aᵢ/A; p_ij = Wᵢ n_ij / nᵢ.; O = Σ p_ii; Uᵢ = p_ii / pᵢ.;
>    Pⱼ = p_jj / p.ⱼ; Âⱼ = A · p.ⱼ. Varianzas: V(O) = Σ Wᵢ² Uᵢ(1−Uᵢ)/(nᵢ.−1);
>    V(Uᵢ) = Uᵢ(1−Uᵢ)/(nᵢ.−1); V(p.ⱼ) = Σ Wᵢ² (n_ij/nᵢ.)(1−n_ij/nᵢ.)/(nᵢ.−1);
>    V(Pⱼ) según la ecuación 7 del artículo, con los conteos de píxeles Nᵢ. del mapa.
>    IC del 95 % = estimado ± 1,96 √V.
> 5. Cada estrato necesita al menos 2 puntos etiquetados (si no, la varianza no
>    existe): error con mensaje claro.
> 6. Imprimir la matriz en **conteos** y en **proporción de área**, la tabla por
>    clase (área del mapa, área estimada ± IC, usuario ± IC, comisión, productor
>    ± IC, omisión) y la exactitud global ± IC con el n.
> 7. Salida: `Tp4_Validacion\05_Resultados\04_Tablas\<NOMBRE>_exactitud_y_area.csv`,
>    una fila por clase, con `codigo` (el valor del mapa) y `clase` (el nombre de
>    `--nombres_clase`, o el código) y, repetidas en cada fila, `exactitud_global`,
>    `IC95_global`, `area_total_ha`, `n_total`.
> 8. **`--autoprueba` obligatoria:** reproduce el ejemplo numérico de Olofsson
>    et al. (2014): cuatro clases (deforestación, ganancia, bosque estable, no
>    bosque estable), matriz [[66,0,5,4],[0,55,8,12],[1,0,153,11],[2,1,9,313]],
>    píxeles [200.000, 150.000, 3.200.000, 6.450.000] de 30 m (0,09 ha). Debe dar
>    deforestación 21.158 ± 6.158 ha, usuario 0,88, productor 0,75, global 0,95.
>    Imprime `CORRECTA` o `FALLA: NO USAR` y sale con código 0 o 1.
>
> **`Tp4_04_tabla_de_variantes.py` — la tabla de resultados de cada grupo.**
>
> 1. Argumentos: `--tp` (el práctico, por ejemplo `Tp5`), `--clase` (nombre o
>    código de la clase de interés: se busca en las columnas `clase` y `codigo` de la
>    tabla del paso 3),
>    `--variante` repetible, cada una `"nombre|datos usados|<NOMBRE>"`.
> 2. Una fila por variante: `variante`, `datos_usados`, `exactitud_global ± IC`,
>    `omision ± IC`, `comision ± IC`, `area_estimada_ha ± IC`, `area_segun_mapa_ha`.
>    Es la tabla de la diapositiva 23 de la presentación 01.
> 3. Si falta la tabla de una variante, decirlo y seguir con las demás.
> 4. Decidir con la omisión y la comisión de la clase de interés (la exactitud
>    global, sólo como contexto): en cada medida, comparar la mejor variante con
>    cada una de las otras por la DIFERENCIA, con V(d) = V1 + V2: si el IC del 95 %
>    de la diferencia incluye el cero, escribir «la mejora no está demostrada con esta
>    muestra»; si no, «la diferencia es significativa al 95 %». Con una sola variante,
>    escribir «Una sola variante: no hay comparación».
>    Avisar si las áreas estimadas de dos variantes tienen IC que no se superponen.
> 5. Salida en el práctico que corresponde:
>    `<Tp>\05_Resultados\04_Tablas\tabla_de_variantes_<clase>.csv`, con su bitácora
>    en `<Tp>\05_Resultados\06_Control_calidad\`.
>
> **Para los cuatro scripts:**
>
> - Docstring en español al principio: qué hace, por qué así, entradas, salidas
>   con su ruta y una línea de uso con argumentos reales.
> - Todo lo que se imprime se guarda también en una bitácora `.log` con la misma
>   salida (`Bitacora`), en `Tp4_Validacion\05_Resultados\06_Control_calidad\`, con
>   fecha, versión de Python y ruta del intérprete.
> - Al terminar, imprimir la orden exacta del **siguiente paso**.
> - Tablas CSV en UTF-8 con BOM (`utf-8-sig`), para que Excel muestre bien las tildes.
> - Rutas siempre con `ruta_tp()`: nada escrito a mano.
>
> **Sinergia y fusión.** Este práctico no sinergiza ni fusiona: valida. Escriba en
> los docstrings que la exactitud de `Tp4_03` es la forma de validar una **fusión**
> (exactitud del producto), que la cobertura de control sirve para leer la
> **sinergia** por clase de cubierta, y que `Tp4_04` es donde se decide si la
> fusión mejoró algo.
>
> **Lo que NO debe hacer:**
>
> - No calcular la exactitud contra el mapa de control ni contra otro mapa automático.
> - No poner la clase del mapa en el archivo que se etiqueta.
> - No estimar el área contando píxeles del mapa: eso se informa al lado, como lo
>   que dice el mapa.
> - No calcular kappa.
> - No armar la matriz de error sólo en conteos con muestreo estratificado.
> - No usar los polígonos de entrenamiento de ningún práctico como referencia.
> - No inventar puntos ni rellenar `clase_ref` vacíos: se declaran.
> - No escribir credenciales en ningún archivo.

---

## La diferencia

El primero pedía **una exactitud**. Éste pide **un diseño de validación**: de
dónde sale la referencia, cómo se eligen los puntos, quién los etiqueta sin ver
el mapa, con qué estimador se pasa al área y cómo se prueba que el estimador
está bien escrito. Y deja dicho de antemano que la respuesta puede ser «con esta
muestra no se puede afirmar que la fusión mejore».
