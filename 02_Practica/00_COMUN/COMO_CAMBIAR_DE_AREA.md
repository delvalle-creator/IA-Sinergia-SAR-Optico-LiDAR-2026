# Cómo repetir un práctico en otra área

Es la misma ruta de la presentación de introducción («Cómo reutilizar el
curso», diapositivas 47 a 56 de `01_Teoria/01_Introduccion_Curso.pdf`).

Casi todo sale de `00_COMUN/configuracion_comun.py`: cambiar de área es cambiar
ese archivo y repetir la cadena de prácticos. Los Tp1 a Tp4 ya aceptan
`--sitio`; los scripts de los prácticos específicos (Tp5 a Tp10) se escribieron
para un sitio y hay que adaptarlos (paso 4).

## Antes de empezar

- Un sitio de no más de unos 40 × 40 km: a 10 m de píxel son 16 millones de
  píxeles por capa.
- Un solo práctico (Tp5 a Tp10), el que más se parezca al problema propio.
- Un evento con una fecha o ventana «antes / después» bien definida y
  verificada con imágenes.
- Guardar una copia de `00_COMUN` y de la carpeta del práctico antes de tocar
  nada.
- Correr primero el práctico original en Entre Ríos: así se sabe cómo tiene
  que salir.
- Anotar en la bitácora cada línea cambiada: qué decía, qué dice y por qué.

## Paso 1 · Configurar el sitio y el evento

En `configuracion_comun.py`, diccionario `SITIOS`, una entrada nueva con una
letra que no usen los sitios del curso (G, H…), guion bajo y un nombre corto.
La caja va en grados (oeste, sur, este, norte, WGS 84):

```python
"G_MI_SITIO": {
    "nombre": "Descripción breve del lugar",
    "bbox": (-59.10, -32.50, -58.90, -32.30),
    "origen": "digitalizado sobre Sentinel-2",
    "practicos": ["Tp6"],
},
```

En `EVENTOS`, las fechas del evento y de las ventanas «antes» y «después».
Se escriben **después** de verificarlas con el Tp1 (paso 2):

```python
"Tp6": {"sitio": "G_MI_SITIO",
        "serie": ("AAAA-MM-DD", "AAAA-MM-DD"),
        "pico_1": "AAAA-MM-DD"},
```

Proyección: `EPSG = 32721` (UTM 21S) cubre Entre Ríos. Fuera de la zona 21
(entre 60° y 54° de longitud oeste) se cambia en el mismo archivo, por ejemplo
32720 (zona 20) o 32722 (zona 22), **para todo el proyecto**, no para un solo
práctico.

Comprobar: `python configuracion_comun.py` lista los sitios con su caja.

## Paso 2 · Convergencia de datos con el Tp1

Desde `Tp1_Convergencia\03_Scripts`, con el entorno sar activo:

```
python Tp1_01_sitios_a_vector.py
python Tp1_03_buscar_optico_y_C.py --sitio G_MI_SITIO --desde AAAA-MM-DD --hasta AAAA-MM-DD
python Tp1_04_buscar_asf.py --sitio G_MI_SITIO --desde AAAA-MM-DD --hasta AAAA-MM-DD
python Tp1_05_buscar_lidar.py --sitio G_MI_SITIO
python Tp1_07_matriz_convergencia.py --sitio G_MI_SITIO --evento AAAA-MM-DD
python Tp1_08_contexto_del_sitio.py --sitio G_MI_SITIO
```

La nubosidad se cuenta dentro del sitio, no en la tesela entera. El Tp1_07
dice si el sitio admite fusión o sólo sinergia: esa respuesta decide el resto.
Las fechas que salgan de acá son las que se escriben en `EVENTOS`.

## Paso 3 · Bajar y recortar los datos del sitio nuevo

A. Datos crudos, desde `00_COMUN` (sin `--confirmar` sólo muestra qué bajaría):

```
python datos_crudos.py planetary --sitios G_MI_SITIO --desde AAAA-MM-DD --hasta AAAA-MM-DD
python datos_crudos.py gedi --sitios G_MI_SITIO
python datos_crudos.py icesat2 --sitios G_MI_SITIO
python datos_crudos.py nisar --sitios G_MI_SITIO
```

Se agrega `--confirmar` cuando la lista sea la correcta. También hay `biomass`,
`cci` y `landsat`, según el tema. Hacen falta las cuentas de NASA Earthdata
(.netrc) y de ESA MAAP (para BIOMASS).

B. Subsets (.dim y GeoTIFF): en `armar_subsets.py`, diccionario `TRABAJOS`,
copiar la entrada del práctico original, cambiar sitio y fechas y borrar los
productos que no existan en el sitio nuevo. Luego:

```
python armar_subsets.py Tp6              (informa)
python armar_subsets.py Tp6 --confirmar  (arma)
```

## Paso 4 · Adaptar el script del tema (Tp5 a Tp10)

Trabajar sobre una copia del script en la misma carpeta `03_Scripts` (por
ejemplo `Tp6_01_serie_agua_C_MiSitio.py`). Con Buscar y reemplazar (Ctrl+H) en
Notepad++ o VS Code se cambian cuatro cosas:

| Qué | Ejemplo original | Cambio |
|---|---|---|
| La constante `SITIO` | `SITIO = "B_CONCORDIA"` | `SITIO = "G_MI_SITIO"` |
| Nombres de archivo con el sitio | `"B_CONCORDIA_FABDEM_v"` | `"G_MI_SITIO_FABDEM_v"` |
| Fechas por defecto | `default="2023-11-04"` | `--pico AAAA-MM-DD` en la orden |
| Datos locales del docente | `--nisar_h5 D:\...\NISAR_...h5` | archivo propio, o se omite |

Las fechas conviene pasarlas en la orden y no editarlas dentro del archivo.

Qué cambiar en cada práctico:

| Práctico | Sitio fijo en el script | Fechas y argumentos | Datos que hay que reemplazar |
|---|---|---|---|
| Tp5 Incendios | `"A1_DELTA_QUEMAS"` en nombres de entrada y salida (Tp5_02 a Tp5_05); prefijo `A1_` | `--saocom_pre_hv` y `--saocom_post_hv`; óptico de octubre de 2020 | SAOCOM QP del curso 2023 (banda L local); huellas GEDI antes y después del fuego |
| Tp6 Inundaciones | `SITIO = "B_CONCORDIA"` en Tp6_01 a Tp6_05; prefijo `B_` | `--desde 2023-10-01`, `--hasta 2024-06-30`, `--pico 2023-11-04` | NovaSAR 47942; FABDEM y MapBiomas con nombre del sitio; ICESat-2 para controlar el MDE |
| Tp7 Barrancas | `SITIO = "E1_DIAMANTE_BARRANCA"`; prefijo `E1_` | `--desde 2018-09-15`, `--hasta 2018-11-15`; pares InSAR de Sentinel-1 2025-2026 | COSMO-SkyMed (banda X) del docente; cicatriz y escarpa digitalizadas; ICESat-2 a 20 m |
| Tp8 Erosión | `SITIO = "F_BOVRIL"`; prefijo `F_` (y `C_` en la textura) | Serie óptica de 2023; `--puntos_enlace` para NovaSAR | NovaSAR 47974; FABDEM y MapBiomas con nombre del sitio |
| Tp9 Deforestación | `SITIO = "C_FEDERAL"`; prefijo `C_` | `--anio_alos2 2021`; fechas ópticas de `EVENTOS` | L, C y NISAR (.h5), ALOS-1, NovaSAR 50896, BIOMASS banda P, MapBiomas; GEDI para el cambio de altura |
| Tp10 Urbano | `--sitio` con `choices=["B_CONCORDIA", "E_PARANA_DIAMANTE"]`: agregar el sitio nuevo a la lista | `--nisar_h5` con el archivo del 18/09/2026; pares SBAS | NISAR descendente y NovaSAR 47942; ciudad con crecimiento reciente |

El Tp7 exige un fenómeno puntual (barranca, ladera) y pares InSAR con buena
coherencia: no conviene en zonas con vegetación densa. Los Tp1 a Tp4 ya
aceptan `--sitio` y no hay que tocarlos, salvo Tp1_06b y Tp2_05, atados a
productos SAOCOM y ALOS-2 concretos.

## Paso 5 · Validar con el Tp4

Con los scripts Tp4_01 a Tp4_04: rehacer el mapa de control del sitio, el
muestreo, la matriz de confusión y el área corregida, y responder si la fusión
mejora al mejor sensor solo.

## Lo que no se traslada solo

1. Datos locales del docente: NovaSAR, COSMO-SkyMed, SAOCOM y los NISAR ya
   bajados cubren lugares concretos. En otra área hay que conseguir los propios
   o quitar ese sensor del análisis.
2. MapBiomas: sólo cubre Argentina (y países con su propia colección). Fuera
   de ella, ESA WorldCover o CCI Land Cover.
3. Capas digitalizadas: entrenamiento, control, cicatrices y escarpas son del
   sitio; se digitalizan de nuevo sobre imágenes del sitio nuevo.
4. Umbrales y calibraciones: los umbrales de agua, los desfases de NovaSAR y
   las curvas de respuesta se calcularon en Entre Ríos; se recalculan, no se
   copian.

Si falta un sensor, el práctico sigue: la variante sin ese sensor se compara
con las demás en el Tp4.
