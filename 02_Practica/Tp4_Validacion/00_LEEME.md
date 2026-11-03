# Tp4 · Validación e incertidumbre

**Pregunta del práctico:** ¿cuán confiable es un mapa de emergencia y cuánta área afectada hay realmente?

El Tp4 es un práctico **general**: se hace una vez y se reutiliza en todos los específicos. Cada mapa que produzcan los Tp5 a Tp10 (óptico solo, SAR solo, SAR multibanda, multisensor) se valida con las herramientas de esta carpeta. Sin el Tp4, ninguna variante del curso tiene exactitud ni intervalo de confianza: sólo tiene píxeles contados.

## Horario

- Martes 12 a 13 h y 14 a 18 h: mapa de cobertura de control (Tp4_01), autoprueba del estimador (Tp4_03), diseño del muestreo (Tp4_02) y un ensayo completo de etiquetado al azar.
- Miércoles a viernes, dentro de cada práctico específico: Tp4_02, etiquetado, Tp4_03 y Tp4_04 sobre las variantes de ese práctico.

## Sitio

B · Concordia – Salto Grande (`B_CONCORDIA`, bbox −58,25, −31,50, −57,85, −31,10). Es el sitio del Tp1, del Tp6 y del Tp10. El mismo mapa de control se genera también para `A1_DELTA_QUEMAS` (−59,96, −33,36, −59,72, −33,07), porque el Tp5 lo necesita para separar la sinergia por cubierta y enmascarar las lagunas.

Otros dos prácticos leen la cobertura de control y la piden a 20 m: `Tp9_01` (`C_FEDERAL_cobertura_control_20m.tif`, zona estable para la calibración cruzada de la banda L; el monte confirmado sin cambio 2011–2026 se digitaliza como clase 3) y `Tp10_01` (`B_CONCORDIA_cobertura_control_20m.tif`, opcional, mejora la tabla de coincidencias). Se arman en esos prácticos con `Tp4_01_cobertura_de_control.py --sitio C_FEDERAL --pixel 20` y `--sitio B_CONCORDIA --pixel 20`; ninguna viene hecha.

## Lo central: no existe un mapa de control, se genera

El curso **no tiene** un mapa de cobertura de Entre Ríos que sirva de control. El grupo lo arma con `Tp4_01`, con tres fuentes en orden de prioridad (la primera que tiene dato manda):

1. polígonos digitalizados por el grupo sobre imágenes de muy alta resolución;
2. agua permanente de JRC Global Surface Water (ocurrencia ≥ 90 %);
3. bosque de MapBiomas Argentina 2023, donde el archivo del curso lo tiene recortado, y sólo donde la imagen de alta resolución CBERS-4A WPM del 15/07/2026 fusionado a 2 m muestra copas en al menos la mitad del píxel de 20 m (máscara `02_Subsets_SNAP_QGIS\B_CONCORDIA_copa_CBERS4A_fraccion_20m.tif`). Fuera de esa imagen no hay monte en el control.

Ocho clases de control: 1 agua_permanente, 2 humedal_pajonal, 3 monte_nativo, 4 plantacion_forestal, 5 cultivo_pastura, 6 suelo_desnudo, 7 urbano, 8 otra.

**El mapa de control NO es la verdad de campo.** Sirve para estratificar, para definir zonas de control (zona estable, agua permanente, zonas no quemadas, cultivos) y para comparar. La exactitud de un mapa se calcula **siempre** con una muestra etiquetada al azar (`Tp4_02` y `Tp4_03`), nunca contra el mapa de control.

## Carpetas

| Carpeta | Qué hay |
|---|---|
| `00_Guia_del_practico/` | **Empiece por acá.** `objetivos.md` y la guía paso a paso `00_LEEME.md`, con el etiquetado en QGIS explicado clic por clic |
| `01_Prompt_IA/` | El prompt ingenuo y sus defectos, el análisis de la respuesta, el prompt corregido que produjo los scripts y el protocolo de verificación |
| `02_Subsets_SNAP_QGIS/` | La cobertura de control en GeoTIFF: `<SITIO>_cobertura_control_<pixel>m.tif` (la escribe `Tp4_01`) |
| `03_Scripts/` | Los cuatro scripts y `00_ORDEN_DE_EJECUCION.md` |
| `04_Tablas_de_trabajo/` | Lo que el grupo digitaliza y etiqueta: `control_digitalizado_<SITIO>.gpkg`, `<NOMBRE>_puntos_a_etiquetar.gpkg` y la llave `<NOMBRE>_llave_NO_ABRIR.csv` |
| `05_Resultados/` | Tablas (`04_Tablas/`) y bitácoras (`06_Control_calidad/`) |
| `06_Bibliografia/` | Referencias del práctico |
| `07_Preguntas_y_entrega/` | Las preguntas, la rúbrica y lo que entrega el grupo |

## Los siete scripts

| Paso | Script | Marca | Qué hace |
|---|---|---|---|
| 1 | `Tp4_01_cobertura_de_control.py` | **SE CORRE** + **EN QGIS** | Genera el mapa de cobertura de control (digitalizado > JRC > MapBiomas recortado con las copas de 2 m) |
| 2 | `Tp4_02_muestreo_estratificado.py` | **SE CORRE** + **EN QGIS** | Diseña la muestra estratificada y deja los puntos para etiquetar al azar, con la llave aparte |
| 3 | `Tp4_03_exactitud_y_area.py` | **SE CORRE** | Matriz de error, exactitudes y área con IC del 95 % (Olofsson et al., 2014). `--autoprueba` reproduce el ejemplo publicado |
| 4 | `Tp4_04_tabla_de_variantes.py` | **SE CORRE** | Tabla de variantes: compara los IC y dice si la mejora está demostrada |
| 5 | `Tp4_05_mapbiomas_como_mapa.py` | **SE CORRE** + **EN QGIS** | Paso 10: lleva MapBiomas 2025 a las clases del curso para validarlo como un mapa real, con el CCI Biomass y la banda P de BIOMASS como contexto; `--equivalencias` lee otra equivalencia de un CSV |
| 6 | `Tp4_06_muestra_comun.py` | **SE CORRE** | Una sola muestra para varias variantes o equivalencias (Stehman, 2014): diseño, estimación y diferencias pareadas |
| 7 | `Tp4_07_acuerdo_entre_interpretes.py` | **SE CORRE** + **EN QGIS** | Prepara los puntos para un segundo intérprete y mide el acuerdo simple y el kappa de Cohen |

Ningún paso del Tp4 usa SNAP.

## Sinergia y fusión en este práctico

El Tp4 no hace sinergia ni fusión: **valida** los productos de ambas.

- La **fusión** se valida con la exactitud del producto final. Eso es exactamente lo que calcula `Tp4_03`.
- La **sinergia** se valida por coherencia física entre sensores. El Tp4 aporta la cobertura de control, que permite leer la tabla de coincidencias por clase (Tp5_02).
- `Tp4_04` es el lugar donde se ve si fusionar valió la pena: si el IC del 95 % de la diferencia entre la variante multisensor y la de un solo sensor incluye el cero, la mejora **no está demostrada** con esa muestra. Con una sola muestra para las cuatro variantes (`Tp4_06_muestra_comun.py`, Stehman, 2014) la diferencia se estima pareada.

## Qué se entrega

1. El mapa de control del sitio y su tabla resumen (superficie y fuente por clase).
2. Los puntos etiquetados (GeoPackage completo) y la bitácora de cada paso.
3. La tabla de exactitud y área de cada mapa validado (incluido MapBiomas 2025, paso 10), y la tabla de variantes.
4. Las respuestas de `07_Preguntas_y_entrega/preguntas.md`.

## Qué tiene que estar listo antes

- El entorno `sar` de Miniforge (`00_COMUN/entorno_sar.yml`).
- Conexión a internet para leer JRC del Planetary Computer. Sin red, `Tp4_01 --sin_jrc` sigue sin esa fuente.
- **YA VIENE HECHO:** los rásteres de bosque de MapBiomas 2023 recortados a las escenas NovaSAR, en la carpeta raíz de NovaSAR (`E:\IMÁGENES NOVASAR-1 2023 2024`) o, en la computadora del aula, en la copia local `00_COMUN\08_Originales_crudos\LOCALES\MAPBIOMAS`. Sólo cubren donde hay escenas NovaSAR.
- **YA VIENE HECHO:** las capas Pléiades / Pléiades Neo de CONAE de las localidades del curso (`02_Subsets_SNAP_QGIS\Pleiades_CONAE_WMS`, fechadas en 2022–2023; necesitan internet) y las huellas LiDAR de Concordia (`02_Subsets_SNAP_QGIS\LiDAR_B_CONCORDIA`).
- QGIS 3.x con conexión a internet para las teselas de alta resolución (Google Satellite o Esri World Imagery).
- Para los Tp5 a Tp10: los mapas de variantes de cada práctico, en `<Tp>/05_Resultados/02_Rasters/`.

## Lo que se dice desde el principio

- El estimador de `Tp4_03` está probado: con `--autoprueba` reproduce el ejemplo numérico de Olofsson et al. (2014).
- La lectura de JRC desde el Planetary Computer funcionó en la computadora del aula: en B_CONCORDIA agregó 422.856 píxeles de agua permanente y en A1_DELTA_QUEMAS 87.462. Si la red del aula está lenta o inestable ese día, `Tp4_01 --sin_jrc` sigue sin esa fuente.
- El ciclo completo (control, muestreo, etiquetado al azar de 70 puntos, exactitud y área, tabla de variantes) se corrió de punta a punta en esa computadora; las cifras están en el «Desarrollo del Tp4» (`02_Practica\00_Desarrollo_docente`).
- La imagen de alta resolución que muestra QGIS es **reciente**. Sirve para clases estables, no para un incendio de 2020 o una crecida de 2023: para eso hacen falta imágenes fechadas (ver la guía).
