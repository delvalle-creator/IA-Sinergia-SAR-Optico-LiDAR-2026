# Cómo repetir un práctico en otra área

Los programas no tienen coordenadas escritas adentro: todo sale de
`configuracion_comun.py`. Para trabajar en otro lugar hay que tocar ese archivo y
nada más.

## 1. Agregar el sitio

En el diccionario `SITIOS`, una entrada nueva con su caja en grados (oeste, sur,
este, norte, WGS 84) y el origen de las coordenadas:

```python
"G_MI_SITIO": {
    "nombre": "Descripción breve del lugar",
    "bbox": (-59.10, -32.50, -58.90, -32.30),
    "origen": "digitalizado sobre Sentinel-2 del 2026-09-16",
    "practicos": ["Tp6"],
},
```

Conviene que el sitio no pase de unos 40 × 40 km: a 10 m son 16 millones de
píxeles por capa.

## 2. Verificar que la proyección sirve

La grilla común es UTM 21S (EPSG:32721), que cubre Entre Ríos. Fuera de la zona
21 (entre 60° y 54° de longitud oeste) hay que cambiar `EPSG` en el mismo archivo
(por ejemplo 32720 para la zona 20) **para todo el proyecto**, no para un solo
práctico.

## 3. Agregar el evento

En `EVENTOS`, las fechas del evento y las ventanas «antes» y «después». Las
fechas de escenas que se escriban allí tienen que estar **verificadas** con el
Tp1 (cobertura dentro del sitio y nubosidad contada en el sitio, no en la tesela).

## 4. Correr el Tp1 para el sitio nuevo

```
python Tp1_01_sitios_a_vector.py
python Tp1_03_buscar_optico_y_C.py --sitio G_MI_SITIO --desde AAAA-MM-DD --hasta AAAA-MM-DD
python Tp1_04_buscar_asf.py --sitio G_MI_SITIO ...
python Tp1_05_buscar_lidar.py --sitio G_MI_SITIO ...
python Tp1_07_matriz_convergencia.py --sitio G_MI_SITIO --evento AAAA-MM-DD
```

El grado de convergencia que dé el Tp1_07 dice si se puede fusionar o sólo hacer
sinergia.

## 5. Los programas que tienen el sitio fijo

Los prácticos específicos (Tp5 a Tp10) tienen una constante `SITIO` al
principio, o una opción `--sitio`. Donde es una constante, se cambia esa línea y
se declara en la bitácora.

## 6. Lo que no se traslada solo

- Los datos locales (NovaSAR, COSMO-SkyMed, NISAR del docente) cubren lugares
  concretos: en otra área hay que conseguir los propios.
- Las capas digitalizadas (entrenamiento, control, cicatrices) son del sitio:
  se digitalizan de nuevo.
- El mapa de control del Tp4 se rehace para el sitio nuevo.
