# Tp4 · Guía paso a paso

Martes, 12 a 13 h y 14 a 18 h (de miércoles a viernes, la validación de las variantes se hace dentro de cada práctico específico). Sitio: `B_CONCORDIA` (y `A1_DELTA_QUEMAS` para el mapa de control que usa el Tp5).

Esta guía se sigue en orden. Cada paso dice qué se hace y por qué, dónde se hace, la orden o los menús exactos, qué debe observar, cómo sabe que salió bien y cuáles son los errores típicos.

Los menús de QGIS están escritos como aparecen en QGIS 3.x en español. Si su QGIS está en inglés, el nombre en inglés va entre paréntesis la primera vez.

## Antes de empezar

Abra el **Miniforge Prompt** (menú Inicio de Windows) y escriba:

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp4_Validacion\03_Scripts
```

`/d` hace falta porque el Miniforge Prompt arranca en `C:` y la práctica está en `D:`. Todas las órdenes de esta guía se escriben desde esa carpeta.

Compruebe la configuración común:

```
python ..\..\00_COMUN\configuracion_comun.py
```

Debe ver la carpeta de práctica, las carpetas de originales (`Originales`, `NISAR del Delta`, `NovaSAR-1`, `MapBiomas (bosques)`), la proyección `EPSG:32721, pixel 10 m` y la lista de sitios con su bbox. El Tp4 sólo necesita la línea `MapBiomas (bosques)`: en la computadora del aula apunta a la copia local `00_COMUN\08_Originales_crudos\LOCALES\MAPBIOMAS`. Si al lado dice `<-- NO EXISTE en este equipo`, el Tp4 igual funciona, sin esa fuente (con JRC y lo digitalizado).

---

## Paso 1 · Autoprueba del estimador — SE CORRE

**Qué y por qué.** Antes de confiar en un programa que calcula exactitud y área, se comprueba que reproduce un resultado publicado. Olofsson et al. (2014) publicaron un ejemplo numérico completo (un mapa de deforestación con cuatro clases). Si el programa da esas cifras, las fórmulas están bien escritas. Si no, no se usa.

**Dónde.** Miniforge Prompt.

```
python Tp4_03_exactitud_y_area.py --autoprueba
```

**Salida esperada.** Una tabla con cuatro clases (`deforestacion`, `ganancia`, `bosque_estable`, `no_bosque_estable`) y, al final:

```
AUTOPRUEBA: CORRECTA (coincide con el ejemplo publicado)
```

**Control.** En la fila `deforestacion`: área estimada cercana a 21.158 ha con IC95 cercano a 6.158 ha, exactitud del usuario 0,88 y del productor 0,75. Exactitud global 0,95. Son las cifras del artículo.

**Fíjese en esto**, que es la lección del práctico: el mapa del ejemplo dice 18.000 ha de deforestación (columna `area_mapa_ha`) y el estimador dice 21.158 ± 6.158 ha. El área que cuenta el mapa **no** es el área real: el mapa omite deforestación que el muestreo encuentra.

**Errores típicos.**
- `ModuleNotFoundError: No module named 'geopandas'`: no activó el entorno. Escriba `conda activate sar`.
- `AUTOPRUEBA: FALLA: NO USAR`: alguien modificó el script. No siga; avise al docente.

---

## Paso 2 · Primera corrida del mapa de control — SE CORRE

**Qué y por qué.** El curso no tiene un mapa de cobertura de control: se genera. Esta primera corrida hace dos cosas: crea la capa vacía para digitalizar y arma un primer mapa con las fuentes externas (JRC y MapBiomas). El píxel es de 20 m porque es el de los prácticos específicos (Tp5 y Tp6 corren a 20 m): el mapa de control tiene que tener la misma grilla que los mapas con los que se cruza.

**Dónde.** Miniforge Prompt.

```
python Tp4_01_cobertura_de_control.py --sitio B_CONCORDIA --pixel 20
python Tp4_01_cobertura_de_control.py --sitio A1_DELTA_QUEMAS --pixel 20
```

Sin internet:

```
python Tp4_01_cobertura_de_control.py --sitio B_CONCORDIA --pixel 20 --sin_jrc
```

**Salida esperada.**
- `Se creo la capa para digitalizar: ...\04_Tablas_de_trabajo\control_digitalizado_B_CONCORDIA.gpkg` y la lista de campos.
- `b) JRC GSW ocurrencia >= 90 %: N pixeles de agua permanente agregados.` En Concordia el río Uruguay y el embalse de Salto Grande deben aportar una cantidad grande de píxeles.
- `c) Mascara de copas de alta resolucion: <SITIO>_copa_CBERS4A_fraccion_20m.tif (monte solo si copa >= 0.50).` y `c) MapBiomas ...: N pixeles de bosque; M quedan con copa >= 0.50 en la imagen de 2 m.` MapBiomas es un producto de 30 m: un píxel con unos árboles, pasto y una casa puede quedar como bosque. Por eso su bosque se recorta con una máscara de copas hecha sobre la imagen de alta resolución CBERS-4A WPM del 15/07/2026 fusionado a 2 m (del Tp10): queda como monte sólo el píxel de 20 m con copas en al menos la mitad. En B_CONCORDIA, de 237.498 píxeles de bosque quedan 37.673. MapBiomas decide qué es monte nativo y qué plantación; la imagen de 2 m decide dónde hay árboles. Si el archivo de la máscara no está, el script lo avisa y usa MapBiomas sin recortar; `--monte_solo_mapbiomas` rehace esa versión para comparar.
- `c) MapBiomas ...: N pixeles de monte agregados (producto de terceros).` Sólo aparece si algún recorte de MapBiomas cae sobre el sitio. Los recortes siguen las escenas NovaSAR: la 47942 cubre el 39 % de B_CONCORDIA y ninguna escena del archivo cae sobre el Delta. En A1_DELTA_QUEMAS es esperable que MapBiomas no aporte nada.
- Una tabla resumen y la línea `Sin clase: X % del sitio (es normal: el control no necesita cubrir todo)`.

**Salidas.**
- `Tp4_Validacion\02_Subsets_SNAP_QGIS\B_CONCORDIA_cobertura_control_20m.tif`, con dos bandas: `clase_control` (0 = sin clase, 1 a 8) y `fuente_control` (1 digitalizado, 2 JRC, 3 MapBiomas recortado con las copas de 2 m).
- `Tp4_Validacion\05_Resultados\04_Tablas\B_CONCORDIA_cobertura_control_resumen.csv`.
- La bitácora `Tp4_Validacion\05_Resultados\06_Control_calidad\Tp4_01_B_CONCORDIA.log`.

**Control.** Abra el GeoTIFF en QGIS (paso 3) y verifique que el agua permanente cae sobre el río y el embalse, no sobre los bañados de la costa. JRC con ocurrencia ≥ 90 % es agua presente en nueve de cada diez observaciones Landsat entre 1984 y 2021: un bañado que se llena en las crecidas no llega a ese umbral, y no debe llegar, porque no es agua permanente.

**Errores típicos.**
- `b) No se pudo leer JRC GSW (...)`: no hay salida a internet hacia el Planetary Computer, o el proxy la bloquea. El script sigue sin JRC; vuelva a correr cuando tenga red. La lectura funcionó en la computadora del aula: en B_CONCORDIA agregó 422.856 píxeles. Si ese día falla, es la red, no un error suyo.
- `error: argument --sitio: invalid choice`: el nombre del sitio va exactamente como en `configuracion_comun.py` (mayúsculas y guion bajo).

---

## Paso 3 · Digitalizar los polígonos de control en QGIS — EN QGIS

**Qué y por qué.** La fuente de mayor prioridad es la interpretación propia. El grupo dibuja polígonos de clases **estables y bien conocidas** sobre imágenes de muy alta resolución (submétricas), que no son las imágenes que después se evalúan. Así el control no depende de Sentinel-1, Sentinel-2 ni de ningún radar del curso.

### 3.1 Agregar las teselas de alta resolución

1. Abra QGIS. Menú `Vista > Paneles > Navegador` (View > Panels > Browser) si el panel Navegador no está visible.
2. En el Navegador, busque `Teselas XYZ` (XYZ Tiles). Clic derecho > `Nueva conexión…`.
3. Para Esri World Imagery:
   - Nombre: `Esri World Imagery`
   - URL: `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`
   - Nivel de zoom máximo: `19`. Aceptar.
4. Para Google Satellite, repita con:
   - Nombre: `Google Satellite`
   - URL: `https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}`
   - Nivel de zoom máximo: `20`.
5. Doble clic sobre la conexión en el Navegador: se agrega como capa.
5b. Para el casco urbano de Concordia hay además una fuente **fechada**: arrastre a QGIS
   `Tp4_Validacion\02_Subsets_SNAP_QGIS\Pleiades_CONAE_WMS\Concordia_2023_Pleiades_CONAE.xml`
   (Pléiades Neo de CONAE, 0,3 m, 2023; sólo cubre la ciudad). En esa carpeta están también
   las capas de las demás localidades del curso. Las huellas LiDAR del sitio
   (`02_Subsets_SNAP_QGIS\LiDAR_B_CONCORDIA`) ayudan a confirmar monte y cultivo por su altura.
6. Abajo a la derecha de la ventana, haga clic en el SRC del proyecto y fíjelo en `EPSG:32721` (WGS 84 / UTM zone 21S). Así las distancias que mide son metros en la grilla del curso.

Tener **dos** fuentes sirve: si una muestra una fecha con nubes o con el río crecido, la otra suele mostrar otra fecha.

### 3.2 Abrir el mapa de control del paso 2

1. `Capa > Añadir capa > Añadir capa ráster…` (Layer > Add Layer > Add Raster Layer). Elija `B_CONCORDIA_cobertura_control_20m.tif`.
2. Clic derecho sobre la capa > `Propiedades… > Simbología`. Tipo de renderizador: `Paletizado/valores únicos` (Paletted/Unique values), banda 1 `clase_control`. Botón `Clasificar`. Borre la clase 0 o hágala transparente.
3. En `Propiedades… > Información` (Information) verá los metadatos FUENTE y PROCESO que escribió el script. Esa cita es la que va al pie de cualquier figura hecha con esta capa.

### 3.3 Abrir la capa para digitalizar

1. `Capa > Añadir capa > Añadir capa vectorial…` y elija `Tp4_Validacion\04_Tablas_de_trabajo\control_digitalizado_B_CONCORDIA.gpkg`, capa `control`.
2. Seleccione la capa y pulse `Conmutar edición` (el lápiz; Toggle Editing).
3. La capa es de polígonos, en `EPSG:32721`, con los campos `codigo` (entero), `clase`, `fuente_interpretacion`, `fecha_imagen` e `interprete`: el botón `Añadir polígono` (Add Polygon Feature) se habilita apenas se activa la edición.

### 3.4 Configurar el formulario para no equivocarse de código

1. Clic derecho sobre `control` > `Propiedades… > Formulario de atributos` (Attributes Form).
2. Elija el campo `codigo`. Tipo de control: `Mapa de valores` (Value Map). Cargue los ocho pares valor / descripción:

| Valor | Descripción |
|---|---|
| 1 | agua_permanente |
| 2 | humedal_pajonal |
| 3 | monte_nativo |
| 4 | plantacion_forestal |
| 5 | cultivo_pastura |
| 6 | suelo_desnudo |
| 7 | urbano |
| 8 | otra |

3. Aceptar. Ahora, al cerrar cada polígono, el formulario ofrece una lista y no se puede escribir un código inexistente.

### 3.5 Digitalizar

1. `Añadir polígono` (Ctrl + .). Clic izquierdo en cada vértice, clic derecho para cerrar.
2. En el formulario complete: `codigo` (de la lista), `clase` (el mismo nombre), `fuente_interpretacion` (por ejemplo `Esri World Imagery` o `Google Satellite`), `fecha_imagen` (la que muestre la imagen, si la conoce; si no, escriba `sin fecha`), `interprete` (su nombre).
3. `Guardar edición de la capa` (Save Layer Edits) cada diez polígonos.

**Protocolo de respuesta (definición operativa de cada clase, en el píxel de 20 m o en el cuadrado del polígono).** Se fija antes de sortear y vale para digitalizar y para etiquetar (Olofsson et al., 2014, diseño de respuesta). Los umbrales de monte siguen la leyenda de MapBiomas, para que la validación del paso 10 mida errores del mapa y no diferencias de definición.

| Código y clase | Criterio | Umbral | Casos dudosos y cómo se resuelven |
|---|---|---|---|
| 1 agua_permanente | Agua libre visible en las dos fuentes | Más de la mitad del píxel con agua | Bañado que a veces tiene agua: 2. Tajamar chico: 1 sólo si está lleno en las dos fuentes |
| 2 humedal_pajonal | Herbáceas o arbustos bajos en suelo inundable (bañado, cañada, borde de laguna) | Copas de árboles < 20 % | Pastizal ribereño sin señales de anegamiento: 5 |
| 3 monte_nativo | Árboles nativos de forma irregular, sin hileras ni bordes rectos | Copas ≥ 20 % (MapBiomas: bosque abierto 20 % a 65 %, cerrado > 65 %) | Espinal abierto con 20 % de copas o más: 3; con menos: 5 |
| 4 plantacion_forestal | Árboles en hileras o en bloques de bordes rectos, con cortafuegos | Cualquier cobertura dentro del bloque | Bloque cosechado o recién plantado: 4, con confianza media o baja |
| 5 cultivo_pastura | Herbáceo: lotes, pasturas y pastizales naturales | Copas < 20 % | Pastizal con árboles sueltos (< 20 %): 5. Frutal o cítrico: 5 |
| 6 suelo_desnudo | Suelo sin vegetación: loteos, playas, caminos de tierra, canteras | Vegetación < 5 % | Galpón o calle asfaltada: 7. Cosecha reciente de plantación: 4 |
| 7 urbano | Techos, calles y patios de la trama edificada | Edificación sobre más de la mitad del píxel | Casa rural aislada: 7 si el píxel cae en la construcción |
| 8 otra | Lo que no entra en 1 a 7 (túneles y mallas de arándanos) | — | Se anota en `observacion` qué es |

**Reglas de digitalización (y por qué).**
- **Polígonos ubicados por sorteo.** Los polígonos se ubican a partir de puntos sorteados, no donde la clase se ve más fácil, y se aceptan sólo en cubiertas homogéneas: el resultado es una muestra de sitios puros, no una muestra al azar del paisaje (por eso la exactitud del ensayo es optimista por diseño). `Vectorial > Herramientas de investigación > Puntos aleatorios en la extensión` (Random Points in Extent), con la extensión del sitio y 100 puntos. Recorra los puntos en el orden en que salieron (campo `id`) y trace un polígono alrededor de cada punto que caiga en una cubierta inequívoca, hasta completar el número pedido para cada clase; los puntos que caen en bordes o en cubiertas dudosas se saltean y se anotan. Elegir los lugares a ojo concentra los polígonos en los ejemplos más típicos y hace que el mapa parezca mejor de lo que es. Con 100 puntos uniformes las clases raras (las que ocupan pocas hectáreas: monte cerrado, suelo desnudo, severidad alta) casi nunca se completan. Para esas clases, haga un **sorteo estratificado**: convierta a polígono el estrato de la clase (`Ráster > Conversión > Poligonizar` sobre MapBiomas, o sobre el rango del índice que define la clase) y use `Vectorial > Herramientas de investigación > Puntos aleatorios dentro de polígonos`; recorra esos puntos también en el orden en que salieron, con la misma revisión en la imagen. Anote de qué sorteo salió cada polígono. Reglas que usó el Desarrollo: cuadrados de 200 m (60 m en suelo desnudo), al menos 500 m entre polígonos y una ventana pura de 220 m (100 m en suelo desnudo) en el sorteo por estrato.
- **Sólo clases estables.** Un lote que hoy es soja y el año pasado fue pastura es `cultivo_pastura` igual; un bañado que a veces es agua y a veces pajonal es `humedal_pajonal`, no `agua_permanente`. El control se usa con imágenes de 2020, 2023 y 2024: lo que cambia entre esas fechas no sirve como control.
- **Lejos de los bordes.** Deje al menos 60 m (tres píxeles de 20 m) entre el polígono y el límite de la cubierta. En el borde, el píxel de 20 m mezcla dos cubiertas y el radar además mezcla la geometría. Si en una clase rara no se puede (en el Desarrollo, los dos cuadrados de 60 m de suelo desnudo), se declara como excepción.
- **Varios polígonos por clase, repartidos en el sitio.** Diez polígonos chicos en distintos lugares valen más que uno grande: representan la variabilidad de la clase.
- **Ninguna clase “por descarte”.** Si no está seguro, no digitalice. El script no necesita que el control cubra todo el sitio.
- **No use Sentinel-2 ni el radar del curso como fuente** para este paso. Si lo hace, el control deja de ser independiente de lo que se evalúa.

**Salida esperada.** Polígonos de colores sobre el río, el embalse, la ciudad de Concordia, las plantaciones de eucalipto (clase 4, muy comunes en el departamento Concordia), monte en galería, lotes agrícolas.

**Errores típicos.**
- Polígonos con el campo `codigo` vacío: el script los descarta en silencio (sólo usa los códigos 1 a 8). Revise con la tabla de atributos (F6) que no haya `NULL`.
- Digitalizar en EPSG:3857 (el SRC de las teselas): no es un error, el script reproyecta, pero mida las distancias a los bordes en el SRC del proyecto (32721).

---

## Paso 4 · Segunda corrida del mapa de control — SE CORRE

```
python Tp4_01_cobertura_de_control.py --sitio B_CONCORDIA --pixel 20
```

**Salida esperada.** `a) Digitalizado: N poligonos, M pixeles.` y la tabla con las columnas `de_digitalizacion`, `de_JRC` y `de_MapBiomas`. Donde el grupo digitalizó, manda el polígono: un píxel que JRC llamaría agua pero el grupo digitalizó como pajonal queda como pajonal.

**Control.** En la tabla resumen, la suma de `de_digitalizacion + de_JRC + de_MapBiomas` de cada clase es igual a `pixeles`. La clase 1 debe venir casi toda de JRC salvo que el grupo haya digitalizado agua.

Repita para `A1_DELTA_QUEMAS` si el grupo digitalizó también en el Delta (lo necesita el Tp5_02 para separar pajonal de monte en la tabla de coincidencias).

---

## Paso 5 · El tamaño de la muestra, a mano

**Qué y por qué.** Antes de correr `Tp4_02`, calcule usted el tamaño de muestra. La fórmula (Olofsson et al., 2014, ecuación 13) es:

n = ( Σ Wᵢ · Sᵢ / S_O )²

con Wᵢ la proporción de área de la clase i en el mapa, Sᵢ = √(Uᵢ(1 − Uᵢ)) el desvío esperado con una exactitud del usuario Uᵢ, y S_O el error estándar que se busca para la exactitud global.

Con los valores por defecto del script (U = 0,85 para todas las clases, S_O = 0,03), Sᵢ = √(0,85 × 0,15) ≈ 0,357 para todas, la suma Σ Wᵢ Sᵢ vale 0,357 y n = (0,357 / 0,03)² ≈ 142 puntos, sea cual sea el número de clases. El script después exige al menos `--minimo` puntos por clase (30 por defecto): con 2 clases el mínimo es 60 y manda la fórmula; con 8 clases el mínimo es 240 y manda el mínimo.

Con Uᵢ distintos, Wᵢ sí cambia el resultado: con agua 0,95, monte 0,85 y 0,70 en las clases raras, y los Wᵢ del mapa de control, Σ Wᵢ Sᵢ = 0,230 y n = 21 con S_O = 0,05: pesa el agua, que es casi todo el mapa.

Con S_O = 0,05 y U = 0,85 en todas las clases, la fórmula da unos 51 puntos. Con S_O = 0,01, más de 1.000. **El tamaño de la muestra es una decisión sobre el intervalo de confianza que se quiere informar**, y se declara.

---

## Paso 6 · Ensayo del muestreo sobre el mapa de control — SE CORRE

**Qué y por qué.** El martes todavía no hay mapas de los Tp5 a Tp10. Para aprender la mecánica completa (diseño, etiquetado al azar, cálculo) se ensaya sobre el mapa de control. Se usa una muestra chica para que entre en la tarde.

```
python Tp4_02_muestreo_estratificado.py --mapa ..\02_Subsets_SNAP_QGIS\B_CONCORDIA_cobertura_control_20m.tif --banda 1 --SE 0.05 --minimo 10
```

**Salida esperada.**
- `Formula: n = (sum W_i S_i / S_O)^2 con U = 0.85 y S_O = 0.050  ->  n = 51` (el n de la ecuación, el mismo que calculó a mano en el paso 5).
- `Minimo: 10 puntos x 7 clases = 70 > 51: manda el minimo, n = 70` (con siete clases en el mapa de control, el mínimo por clase pesa más que la fórmula).
- La tabla de diseño con `clase_mapa`, `pixeles`, `W_i`, `superficie_ha`, `n_i`.
- `Puntos a etiquetar (SIN la clase del mapa): ...\B_CONCORDIA_cobertura_control_20m_puntos_a_etiquetar.gpkg`
- `Llave (no abrir hasta terminar de etiquetar): ...\B_CONCORDIA_cobertura_control_20m_llave_NO_ABRIR.csv`

El nombre que el script usa para todo (`<NOMBRE>`) es el nombre del archivo del mapa sin extensión. En este caso `B_CONCORDIA_cobertura_control_20m`.

**Control.** Compare su n del paso 5 con el de la bitácora. La suma de `n_i` puede diferir en uno o dos puntos del n de la fórmula por el redondeo del reparto.

**Advertencia sobre este ensayo.** El grupo que digitalizó el control **no** etiqueta estos puntos: lo hace otro grupo. Y aun así, quien etiqueta usa el mismo tipo de imagen con que se digitalizó, de modo que la exactitud que salga **no** es una validación del mapa de control. Es un ensayo de la mecánica y una medida de cuánto tarda el grupo en etiquetar la muestra (con `--SE 0.05 --minimo 10` salen entre 51 y 80 puntos, según el número de clases del mapa). Se declara así.

**Errores típicos.**
- `El mapa tiene 1 clase(s): para validar hacen falta al menos dos.`: eligió la banda 2 (`fuente_control`) o el mapa todavía no tiene clases.
- `YA EXISTE ...\<NOMBRE>_puntos_a_etiquetar.gpkg con N puntos etiquetados: NO se reescribe.`: el script protege el etiquetado. Si ese GeoPackage ya tiene algún `clase_ref` cargado, no lo toca y termina. Para un muestreo nuevo sobre el mismo mapa, copie antes el GeoPackage etiquetado a otro nombre y corra con `--sobrescribir` (esa opción sí reemplaza los puntos y borra el trabajo hecho). Un GeoPackage sin ninguna etiqueta se reescribe sin pedir nada.

---

## Paso 7 · Etiquetar al azar en QGIS, clic por clic — EN QGIS

**Por qué al azar y sin ver el mapa.** Si quien etiqueta ve la clase del mapa, en los puntos dudosos tiende a darle la razón al mapa. No es deshonestidad: es sesgo de confirmación, y se ha medido muchas veces. El resultado es una exactitud inflada que nadie puede detectar después. Por eso el GeoPackage que se etiqueta **no trae la clase del mapa**: está en la llave, que se une recién en el paso 8. **No abra la llave** (ni en Excel ni en QGIS) hasta terminar. Tampoco cargue en QGIS el mapa que se está evaluando.

### 7.1 Preparar el proyecto

1. Abra un proyecto **nuevo** de QGIS (`Proyecto > Nuevo`). Así no arrastra el mapa evaluado desde otro proyecto.
2. Fije el SRC del proyecto en `EPSG:32721`.
3. Agregue las teselas `Esri World Imagery` y `Google Satellite` (paso 3.1).
4. `Capa > Añadir capa > Añadir capa vectorial…` y elija `...\04_Tablas_de_trabajo\<NOMBRE>_puntos_a_etiquetar.gpkg`, capa `puntos`.
5. Verifique en el panel Capas que **no** está cargado el mapa evaluado ni el CSV de la llave.

### 7.2 Que cada punto se vea como el píxel que representa

El punto es el centro de un píxel de 20 m. Se etiqueta **el píxel**, no el punto.

1. Clic derecho sobre `puntos` > `Propiedades… > Simbología`.
2. Elija `Marcador simple` (Simple Marker). Forma: cuadrado. Tamaño: `20`, unidad: `Metros a escala de mapa` (Meters at Scale).
3. Color de relleno: transparente. Color de trazo: amarillo, grosor 0,6 mm.
4. `Etiquetas > Etiquetas simples` (Single Labels), Valor: `id`. Aceptar.

Ahora cada punto se ve como un cuadrado de 20 × 20 m con su número.

### 7.3 Configurar el formulario de etiquetado

1. `Propiedades… > Formulario de atributos`.
2. Campo `clase_ref`: tipo de control `Mapa de valores`. Cargue los códigos del mapa que se evalúa, **los mismos números**:
   - Ensayo del martes (mapa de control): los ocho códigos del paso 3.4.
   - Tp5 (variantes de quema): `1` quemado, `2` no quemado.
   - Tp6 (variantes de agua): `1` agua de inundación, `2` no.
3. Campo `confianza`: `Mapa de valores` con `alta`, `media`, `baja`.
4. Campos `imagen_usada` y `observacion`: `Edición de texto` (Text Edit).
5. Campo `id`: desmarque `Editable`. El `id` no se toca: es lo que une el punto con la llave.

### 7.4 Repartir el trabajo

Si son tres, repártanse los `id` en tercios según el total de puntos (por ejemplo, con 60 puntos: 1 a 20, 21 a 40, 41 a 60). En la tabla de atributos, el botón de filtro abajo a la izquierda permite `Filtro avanzado (expresión)` con, por ejemplo, `"id" >= 21 AND "id" <= 40`.

Además, **diez puntos los etiquetan dos personas por separado**. `python Tp4_07_acuerdo_entre_interpretes.py --preparar --nombre <NOMBRE>` deja esos puntos en `<NOMBRE>_segundo_interprete.gpkg`, sin etiquetas y en otro orden; la segunda persona los etiqueta con el mismo protocolo y `--medir` informa el acuerdo simple y el kappa de Cohen. El acuerdo entre intérpretes es el control de la referencia, no una exactitud del mapa.

### 7.5 Etiquetar, punto por punto

1. Seleccione `puntos` y pulse `Conmutar edición` (el lápiz).
2. `Abrir tabla de atributos` (F6). Abajo a la derecha, cambie a la **vista de formulario** (Switch to form view).
3. En la barra de la vista de formulario active el botón para **desplazar automáticamente el mapa al objeto actual** (Automatically pan to current feature) y el de **resaltar el objeto actual** (Highlight current feature). Ordene la lista por `id`.
4. Haga clic en el primer `id` de la lista. El mapa se mueve al punto.
5. Mire el cuadrado amarillo a escala 1:1.000 o 1:2.000. Cambie entre Esri y Google (encienda y apague la capa de arriba) si una de las dos tiene nubes o una fecha poco útil.
6. Complete:
   - `clase_ref`: la clase que ocupa **más de la mitad** del cuadrado, en la fecha que corresponde (ver 7.6).
   - `confianza`: `alta` si no duda; `media` si la clase es clara pero el píxel está cerca de un borde; `baja` si el píxel es mezcla o la imagen no es de la fecha del evento.
   - `imagen_usada`: fuente y fecha cuando la fuente la tiene, por ejemplo `Google Earth Pro, 12/10/2020`; las teselas Esri y Google no tienen fecha: `Esri World Imagery, sin fecha`.
   - `observacion`: cualquier cosa útil (“borde de lote”, “sombra de nube”, “bañado con agua”).
7. Pase al siguiente `id` de la lista.
8. Si **no puede decidir** (nube en las dos fuentes, imagen sin la fecha necesaria), deje `clase_ref` vacío y explíquelo en `observacion`. `Tp4_03` calcula con los puntos etiquetados y declara cuántos quedaron sin etiquetar. Un punto inventado es peor que un punto vacío.
9. `Guardar edición de la capa` cada diez puntos.
10. Al terminar, cierre la edición (lápiz) y guarde.

### 7.6 La fecha de la referencia: el punto delicado

Las teselas de Esri y Google muestran un mosaico **reciente**. Para clases estables (el ensayo con el mapa de control) alcanza. Para un evento no:

- **Tp5, quemas de 2020:** hace falta ver el Delta poco después de las quemas. Use Google Earth Pro, menú `Ver > Imágenes históricas` (el reloj), y elija la fecha más cercana posterior al evento; o el archivo histórico de Esri World Imagery Wayback (https://livingatlas.arcgis.com/wayback), que permite elegir versiones anteriores del mosaico. Anote la fecha en `imagen_usada`.
- **Tp6, crecidas de 2023 y 2024:** lo mismo, y además los productos de la Carta Internacional, activación 880 (inundación en Entre Ríos, mayo de 2024), si están disponibles.
- **Si la única imagen de la fecha es Sentinel-2**, la referencia **no es independiente** de la variante óptica, que se hizo con Sentinel-2. Se puede usar para las variantes de radar, pero la exactitud de la variante óptica queda sesgada a favor, y se declara.

### 7.7 Errores típicos del etiquetado

- Etiquetar con el mapa evaluado encendido “sólo para orientarse”: invalida la exactitud. No hay forma de corregirlo después; hay que volver a etiquetar.
- Escribir `quemado` en vez de `1`: con el `Mapa de valores` no pasa; sin él, `Tp4_03` falla al convertir a número.
- Usar un código que el mapa no tiene (por ejemplo `3` en un mapa de quema): `Tp4_03` no los excluye: los cuenta como error del mapa y avisa. Si son muchos, el mapa omite una clase entera: anótelo.
- No guardar antes de correr `Tp4_03`: el script lee lo que está en el archivo, no lo que está en la pantalla.

---

## Paso 8 · Exactitud y área — SE CORRE

**Qué y por qué.** Ahora sí se une la llave. El script arma la matriz de error (filas = clase del mapa, columnas = referencia) y la convierte a **proporción de área** pesando cada estrato por su Wᵢ. Ese peso es lo que permite estimar el área: los puntos de una clase chica representan poca superficie y los de una clase grande, mucha.

```
python Tp4_03_exactitud_y_area.py --nombre B_CONCORDIA_cobertura_control_20m --nombres_clase "1=agua_permanente,2=humedal_pajonal,3=monte_nativo,4=plantacion_forestal,5=cultivo_pastura,6=suelo_desnudo,7=urbano,8=otra"
```

**Salida esperada.**
- `Matriz de error en CONTEOS` y `Matriz de error en PROPORCION DE AREA (p_ij)`.
- `Exactitud y area por clase (IC del 95 %)`: por clase, `codigo` (el valor del mapa), `clase` (el nombre de `--nombres_clase`, o el código), `area_mapa_ha`, `area_estimada_ha`, `IC95_area_ha`, `exactitud_usuario` con `IC95_usuario`, `comision`, `exactitud_productor` con `IC95_productor`, `omision`.
- `Exactitud global: 0.xxx +/- 0.xxx   (n = ... puntos)`.
- Avisos, si los hay: puntos sin etiquetar o con clases que el mapa no tiene.

**Salida.** `Tp4_Validacion\05_Resultados\04_Tablas\<NOMBRE>_exactitud_y_area.csv`.

**Lectura de los resultados.**
- **Usuario** (1 − comisión): de lo que el mapa llama quemado, qué fracción lo está. Le importa a quien usa el mapa en el terreno.
- **Productor** (1 − omisión): de lo realmente quemado, qué fracción encontró el mapa. Le importa a quien estima el daño total.
- **Área estimada ± IC** frente a **área del mapa**: si el área del mapa queda fuera del intervalo, el mapa sesga el área, y la cifra que se informa es la estimada.

**Control.** La suma de `area_estimada_ha` de todas las clases es igual a la suma de `area_mapa_ha` (el área total no cambia; se redistribuye entre clases).

**Errores típicos.**
- `Falta --nombre (el mismo que uso Tp4_02).`
- `ValueError: Cada estrato necesita al menos 2 puntos etiquetados.`: alguna clase del mapa quedó con 0 o 1 punto etiquetado. Etiquete más puntos de esa clase.
- `FileNotFoundError` con `_diseno_muestral.csv`: el nombre no coincide con el del paso 2.

---

## Paso 9 · En cada práctico específico: validar las variantes — SE CORRE + EN QGIS

Del miércoles en adelante, cada práctico produce cuatro mapas (variantes). Cada uno se valida con **su propia muestra**, porque la muestra se estratifica con las clases de ese mapa. Ejemplo del Tp5:

```
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp5_Incendios\05_Resultados\02_Rasters\A1_variante_multisensor.tif --banda 1
```

(etiquetar en QGIS el GeoPackage `A1_variante_multisensor_puntos_a_etiquetar.gpkg`, con códigos 1 quemado y 2 no quemado)

```
python Tp4_03_exactitud_y_area.py --nombre A1_variante_multisensor --nombres_clase "1=quemado,2=no_quemado"
```

Repita para `A1_variante_optico`, `A1_variante_C` y `A1_variante_CL`. Con los valores por defecto son unos 140 puntos por variante: repártanse las variantes entre grupos.

Al final, la tabla de variantes:

```
python Tp4_04_tabla_de_variantes.py --tp Tp5 --clase quemado ^
    --variante "Optico solo|Sentinel-2|A1_variante_optico" ^
    --variante "SAR solo (C)|Sentinel-1|A1_variante_C" ^
    --variante "SAR multibanda|C + L|A1_variante_CL" ^
    --variante "Multisensor|SAR (C + L) + optico|A1_variante_multisensor"
```

En «datos usados» se escribe lo que realmente entró al modelo: la variante multisensor del Tp5 es SAR (C + L) + óptico; GEDI no entra en el modelo (se usa como evidencia aparte en el Tp5).

El `^` al final de la línea es la continuación de línea del Miniforge Prompt de Windows. Cada `--variante` es `nombre|datos usados|nombre usado en Tp4_02 y Tp4_03`.

**Salida esperada.** Una fila por variante con `exactitud_global`, `omision`, `comision` y `area_estimada_ha`, cada una con su ±. Después, tres bloques —OMISION de la clase, COMISION de la clase y exactitud global (contexto)— con la mejor variante y, para cada otra, una línea como:

```
   frente a A1_variante_optico (x.xxx +/- x.xxx): diferencia +x.xxx +/- x.xxx -> no demostrada con esta muestra
```

Al final, el área estimada de cada variante con su IC (y un `AVISO` si dos áreas son incompatibles) y la línea de lectura: «una variante MEJORA a otra en la clase ... si la DIFERENCIA de omision o de comision, con su propio IC del 95 %, no incluye el cero.»

**Salida.** `Tp5_Incendios\05_Resultados\04_Tablas\tabla_de_variantes_quemado.csv` (en la carpeta del práctico indicado con `--tp`).

**La clase.** `--clase` acepta el código de la clase o su nombre. La tabla de `Tp4_03` tiene una columna `codigo` (el valor del mapa) y una columna `clase` (el nombre de `--nombres_clase`, o el mismo código si no se usó). `--clase 1` funciona siempre; `--clase quemado` funciona si `Tp4_03` se corrió con `--nombres_clase "1=quemado,2=no_quemado"`.

**Errores típicos.**
- `Falta ...\A1_variante_C_exactitud_y_area.csv (correr Tp4_02 y Tp4_03 con --nombre A1_variante_C).`: esa variante no se validó todavía.
- `La clase quemado no esta en ...`: esa tabla se hizo sin `--nombres_clase`; use `--clase 1` o vuelva a correr `Tp4_03` con los nombres.
- `No hay variantes para comparar.`: ninguna variante tiene su tabla.

**Lectura de la comparación.** La decisión se toma con la **omisión y la comisión de la clase de interés** (lo que importa en una emergencia: área afectada que falta o que sobra); la exactitud global se muestra sólo como contexto, porque una clase mayoritaria bien clasificada la sube aunque la clase de interés empeore. Para cada medida, el script compara la mejor variante con cada una de las otras por la **diferencia**, con su propio IC del 95 % (muestras independientes: V(d) = V1 + V2). Si ese intervalo incluye el cero, la mejora **no está demostrada** con esta muestra; no prueba que las variantes sean iguales. Que los IC de cada variante se superpongan no alcanza para decidir: dos IC que se superponen pueden corresponder a una diferencia significativa, y el programa lo avisa. Sólo se compara cada variante con la mejor; la diferencia entre otros dos pares se calcula aparte con la misma fórmula.

---

**Alternativa recomendada: una sola muestra para las cuatro variantes.** Con `Tp4_02` cada variante necesita su muestra. Stehman (2014) mostró que una sola muestra estratificada sirve para varios mapas aunque los estratos no sean sus clases: estratos = combinaciones de las variantes (todas quemado, ninguna, desacuerdo), con más puntos en el desacuerdo, y estimación con la fórmula de estratos distintos de las clases. `Tp4_06_muestra_comun.py --disenar` arma la muestra y `--estimar` da las exactitudes de cada variante y sus diferencias pareadas. Con los cuatro mapas del Tp5 son 200 puntos (50, 50 y 100).

## Paso 10 · Un mapa real: validar MapBiomas 2025 — SE CORRE + EN QGIS

**(a) Para qué.** El ensayo de los pasos 6 a 8 se hizo sobre el mapa de control, que es la referencia del propio
grupo. Este paso valida un mapa de terceros que el curso usa como contexto desde el Tp1: la cobertura 2025 de
MapBiomas Argentina (Colección 3). Se lo trata como a cualquier mapa: muestreo estratificado por sus clases, etiquetado
al azar y estimador de Olofsson. La biomasa del CCI Biomass 2024 y la banda P de BIOMASS (VH y HH; la HV trae
interferencia de radiofrecuencia sin corregir) acompañan como **contexto**, nunca como referencia.

**(b) La equivalencia de clases.** `Tp4_05` lleva MapBiomas a las clases del curso y a la grilla de 20 m del mapa de
control: bosques cerrados, abiertos e inundables → 3 monte_nativo; silvicultura → 4 plantacion_forestal; herbáceas
inundables → 2 humedal_pajonal; herbáceas, pastura, cultivos temporarios y perennes (cítricos, arándanos) →
5 herbaceo_cultivo_pastura (incluye las herbáceas naturales; mosaico de usos, 21, también va a 5); otras áreas no vegetadas y minería (30) → 6 suelo_desnudo; áreas urbanas → 7 urbano; ríos y lagos →
1 agua_permanente. La clase 8 (otra: túneles) no existe en MapBiomas. La tabla queda en
`05_Resultados\04_Tablas\B_CONCORDIA_mapbiomas_2025_equivalencias.csv`; con `Tp4_05 --equivalencias` se ensaya otra editando ese CSV. La exactitud que se obtiene es la de MapBiomas traducido a la leyenda del curso, no la de su leyenda oficial.

**(c) Las órdenes.**

```
python Tp4_05_mapbiomas_como_mapa.py --sitio B_CONCORDIA --anio 2025
python Tp4_02_muestreo_estratificado.py --mapa ..\02_Subsets_SNAP_QGIS\B_CONCORDIA_mapbiomas_2025_clases_curso_20m.tif --SE 0.05 --minimo 10
```

Se etiquetan los 70 puntos de `04_Tablas_de_trabajo\B_CONCORDIA_mapbiomas_2025_clases_curso_20m_puntos_a_etiquetar.gpkg`
exactamente como en el paso 7 (sin el mapa a la vista y sin abrir la llave). Conviene mirar cada punto a dos escalas: de
cerca (300 m) para la cubierta del píxel y de lejos (1 a 2 km) para el contexto: un bloque rectangular con cortafuegos
es plantación aunque de cerca las copas parezcan monte. Después:

```
python Tp4_03_exactitud_y_area.py --nombre B_CONCORDIA_mapbiomas_2025_clases_curso_20m --nombres_clase "1=agua_permanente,2=humedal_pajonal,3=monte_nativo,4=plantacion_forestal,5=herbaceo_cultivo_pastura,6=suelo_desnudo,7=urbano,8=otra"
```

En Orange: `08_Orange\Tp4_C_mapbiomas_2025_validado.ows`.

**(d) Resultados del desarrollo.** MapBiomas cubre el 68,3 % de B_CONCORDIA (117.657 ha; la margen uruguaya queda sin dato): 46 % herbáceo, cultivo y pastura, 24 % plantación, 12 % monte, 9 % agua, 4 % humedal, 3,5 % urbano, 1 % suelo. Mediana del CCI 2024 por clase del mapa: plantación 69 Mg/ha, monte 36, humedal 28, el resto 0. Mediana de la banda P VH: urbano −14,2 dB, monte −16,8, plantación −16,9, humedal −18,4, suelo −20,7, herbáceo −20,8, agua −29,3. Con 70 puntos (el de túneles no se excluye: cuenta como error del estrato de suelo desnudo): exactitud global **0,568 ± 0,167**. Usuario: agua 1,00, plantación 0,80, urbano 0,70, herbáceo 0,50, suelo 0,20, monte 0,20, humedal 0,10. Productor: suelo 1,00, agua 0,94, herbáceo 0,74, plantación 0,60, monte 0,27, urbano 0,21, humedal 0,07. Área estimada: herbáceo 36.384 ± 18.381 ha (mapa 54.187), plantación 38.069 ± 16.548 ha (mapa 28.460), urbano 13.933 ± 14.217 ha (mapa 4.101), suelo 225 ± 295 ha (mapa 1.127, fuera del intervalo), otra 113 ± 221 ha. Con otras equivalencias (bosques abiertos o herbáceas inundables a herbáceo) la exactitud va de 0,585 a 0,609, sin diferencias demostradas. Con confianza alta coinciden 22 de 27 puntos; con baja, 1 de 16.

**(e) Controles.** La suma de las áreas estimadas es la del mapa (117.656,5 ha). Un punto de una clase que el mapa no tiene (túneles) no se excluye: entra como columna de referencia sin estrato, baja el usuario del suelo desnudo y suma área a la clase otra.

**(f) Errores típicos.**
- Dejar a la vista el mapa de MapBiomas al etiquetar: se usa el tema de mapa «Paso 10 - etiquetado al azar de
  MapBiomas (Esri)».
- Tomar el CCI o la banda P como referencia: son contexto; la referencia es la imagen de alta resolución.
- Leer la exactitud global sola: en este mapa la sostienen agua y plantación; monte y humedal están mal.
- Tratar una plantación cosechada entre las dos fechas de Esri y Google como suelo desnudo: el uso sigue siendo
  plantación; se anota con confianza media o baja.
