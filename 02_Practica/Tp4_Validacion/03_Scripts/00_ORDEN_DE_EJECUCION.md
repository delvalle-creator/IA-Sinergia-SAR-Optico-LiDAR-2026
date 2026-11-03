# Tp4 — Orden de ejecución

Todos los pasos **SE CORREN** en clase. Ninguno necesita SNAP. Los pasos 3 y 7 son **EN QGIS** (digitalizar y etiquetar), explicados clic por clic en `00_Guia_del_practico/00_LEEME.md`. La numeración es la de la guía.

| Paso | Script | Marca | Qué hace | Entrada | Salida | Tiempo |
|---|---|---|---|---|---|---|
| 1 | `Tp4_03_exactitud_y_area.py --autoprueba` | SE CORRE | Comprueba el estimador con el ejemplo de Olofsson et al. (2014) | nada | pantalla | 1 min |
| 2 | `Tp4_01_cobertura_de_control.py` | SE CORRE | Crea la capa para digitalizar y un primer mapa con JRC y MapBiomas (recortado con la máscara de copas de 2 m si está `<SITIO>_copa_CBERS4A_fraccion_20m.tif`) | sitio | `02_Subsets_SNAP_QGIS\<SITIO>_cobertura_control_<pixel>m.tif`; `04_Tablas_de_trabajo\control_digitalizado_<SITIO>.gpkg` | — |
| 3 | (QGIS) | EN QGIS | Digitalizar polígonos de control | teselas de alta resolución | `control_digitalizado_<SITIO>.gpkg` con polígonos | — |
| 4 | `Tp4_01_cobertura_de_control.py` | SE CORRE | Rehace el mapa con la prioridad digitalizado > JRC > MapBiomas recortado con las copas de 2 m | el GeoPackage digitalizado | el mismo GeoTIFF y `05_Resultados\04_Tablas\<SITIO>_cobertura_control_resumen.csv` | — |
| 5 | (a mano) | — | Tamaño de la muestra con la ecuación 13 de Olofsson et al. (2014), para entender lo que hace el paso 6 | exactitudes esperadas | cuenta en papel | — |
| 6 | `Tp4_02_muestreo_estratificado.py` | SE CORRE | Diseño de la muestra y puntos al azar | un mapa de clases enteras | `04_Tablas_de_trabajo\<NOMBRE>_puntos_a_etiquetar.gpkg`, `<NOMBRE>_llave_NO_ABRIR.csv`; `05_Resultados\04_Tablas\<NOMBRE>_diseno_muestral.csv` | — |
| 7 | (QGIS) | EN QGIS | Etiquetado al azar | el GeoPackage de puntos | el mismo GeoPackage con `clase_ref` completo | — |
| 8 | `Tp4_03_exactitud_y_area.py` | SE CORRE | Matriz de error, exactitudes y área con IC 95 % (con límites truncados en 0 y 1 e intervalo de Wilson) | puntos etiquetados, llave, diseño | `05_Resultados\04_Tablas\<NOMBRE>_exactitud_y_area.csv` | — |
| 9 | `Tp4_04_tabla_de_variantes.py` | SE CORRE | Tabla de variantes y comparación de IC en la clase de interés | las tablas del paso 8 de cada variante | `<Tp>\05_Resultados\04_Tablas\tabla_de_variantes_<clase>.csv` | — |
| 10 | `Tp4_05_mapbiomas_como_mapa.py`, `Tp4_02`, (QGIS), `Tp4_03` | SE CORRE + EN QGIS | MapBiomas 2025 como mapa real a validar, con CCI Biomass y banda P de contexto | `Tp1_Convergencia\02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\B_CONCORDIA_MapBiomas_*`, `_CCI_*`, `_BIOMASS_P_*` y el mapa de control | `02_Subsets_SNAP_QGIS\B_CONCORDIA_mapbiomas_2025_clases_curso_20m.tif`; `05_Resultados\04_Tablas\B_CONCORDIA_mapbiomas_2025_equivalencias.csv`, `_contexto_por_clase.csv` y `_clases_curso_20m_exactitud_y_area.csv` | — |
| 7 (control) | `Tp4_07_acuerdo_entre_interpretes.py` | SE CORRE + EN QGIS | Prepara los puntos para un segundo intérprete (sin etiquetas, orden nuevo) y mide acuerdo simple y kappa | GeoPackage etiquetado | `<NOMBRE>_segundo_interprete.gpkg`; `05_Resultados\04_Tablas\<NOMBRE>_acuerdo_entre_interpretes.csv` | — |
| 9 (alternativa) y 10 | `Tp4_06_muestra_comun.py` | SE CORRE | Una sola muestra para varias variantes o equivalencias (Stehman, 2014) | los mapas de las variantes | `<NOMBRE>_puntos_a_etiquetar.gpkg`, llave con la clase de cada mapa; `<NOMBRE>_muestra_comun_exactitud.csv` y `_diferencias.csv` | — |

`<NOMBRE>` es el nombre del archivo del mapa evaluado sin extensión (por ejemplo `A1_variante_multisensor`). Las bitácoras de los pasos 1 a 8 quedan en `Tp4_Validacion\05_Resultados\06_Control_calidad\`; la del paso 9, en la carpeta del práctico indicado con `--tp`.

## Las órdenes exactas

Desde el Miniforge Prompt:

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp4_Validacion\03_Scripts
```

**Paso 1.**

```
python Tp4_03_exactitud_y_area.py --autoprueba
```

**Pasos 2 y 4.** Argumentos: `--sitio` (obligatorio), `--pixel` (20 por defecto), `--sin_jrc` (opcional).

```
python Tp4_01_cobertura_de_control.py --sitio B_CONCORDIA --pixel 20
python Tp4_01_cobertura_de_control.py --sitio A1_DELTA_QUEMAS --pixel 20
```

**Paso 6.** Argumentos: `--mapa` (obligatorio), `--banda` (1), `--UA` (0.85), `--SE` (0.03), `--minimo` (30), `--semilla` (2026), `--sobrescribir` (sólo para reemplazar un GeoPackage que ya tiene puntos etiquetados; borra ese trabajo).

Ensayo del martes, sobre el mapa de control, con muestra chica:

```
python Tp4_02_muestreo_estratificado.py --mapa ..\02_Subsets_SNAP_QGIS\B_CONCORDIA_cobertura_control_20m.tif --banda 1 --SE 0.05 --minimo 10
```

Variantes del Tp5 y del Tp6 (valores por defecto):

```
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp5_Incendios\05_Resultados\02_Rasters\A1_variante_multisensor.tif --banda 1
python Tp4_02_muestreo_estratificado.py --mapa ..\..\Tp6_Inundaciones\05_Resultados\02_Rasters\B_variante_C_20231104.tif --banda 1
```

**Paso 8.** Argumentos: `--nombre`, `--nombres_clase` (opcional), `--autoprueba`.

```
python Tp4_03_exactitud_y_area.py --nombre B_CONCORDIA_cobertura_control_20m --nombres_clase "1=agua_permanente,2=humedal_pajonal,3=monte_nativo,4=plantacion_forestal,5=cultivo_pastura,6=suelo_desnudo,7=urbano,8=otra"
python Tp4_03_exactitud_y_area.py --nombre A1_variante_multisensor --nombres_clase "1=quemado,2=no_quemado"
python Tp4_03_exactitud_y_area.py --nombre B_variante_C_20231104 --nombres_clase "1=agua,2=no_agua"
```

**Paso 9.** Argumentos: `--tp` (obligatorio), `--clase` (obligatorio), `--variante` (una o más).

```
python Tp4_04_tabla_de_variantes.py --tp Tp5 --clase quemado ^
    --variante "Optico solo|Sentinel-2|A1_variante_optico" ^
    --variante "SAR solo (C)|Sentinel-1|A1_variante_C" ^
    --variante "SAR multibanda|C + L|A1_variante_CL" ^
    --variante "Multisensor|SAR (C + L) + optico|A1_variante_multisensor"
```

```
python Tp4_04_tabla_de_variantes.py --tp Tp6 --clase agua ^
    --variante "Optico solo|Sentinel-2|B_variante_optico_20231104" ^
    --variante "SAR solo (C)|Sentinel-1|B_variante_C_20231104" ^
    --variante "Multisensor|C + optico (+ L si hay)|B_variante_multisensor_20231104"
```

**Paso 10.**

```
python Tp4_05_mapbiomas_como_mapa.py --sitio B_CONCORDIA --anio 2025
python Tp4_02_muestreo_estratificado.py --mapa ..\02_Subsets_SNAP_QGIS\B_CONCORDIA_mapbiomas_2025_clases_curso_20m.tif --SE 0.05 --minimo 10
python Tp4_03_exactitud_y_area.py --nombre B_CONCORDIA_mapbiomas_2025_clases_curso_20m --nombres_clase "1=agua_permanente,2=humedal_pajonal,3=monte_nativo,4=plantacion_forestal,5=herbaceo_cultivo_pastura,6=suelo_desnudo,7=urbano,8=otra"
```

Otra equivalencia de MapBiomas, evaluada con la misma muestra (editar en una planilla una copia de `05_Resultados\04_Tablas\B_CONCORDIA_mapbiomas_2025_equivalencias.csv`):

```
python Tp4_05_mapbiomas_como_mapa.py --sitio B_CONCORDIA --anio 2025 --equivalencias mi_equivalencia.csv --sufijo abiertos_herbaceo
python Tp4_06_muestra_comun.py --agregar_mapa ..\02_Subsets_SNAP_QGIS\B_CONCORDIA_mapbiomas_2025_abiertos_herbaceo_clases_curso_20m.tif --nombre B_CONCORDIA_mapbiomas_2025_clases_curso_20m --columna abiertos_herbaceo
python Tp4_06_muestra_comun.py --estimar --nombre B_CONCORDIA_mapbiomas_2025_clases_curso_20m --clase 3
```

**Paso 7, control de la referencia.**

```
python Tp4_07_acuerdo_entre_interpretes.py --preparar --nombre B_CONCORDIA_cobertura_control_20m
python Tp4_07_acuerdo_entre_interpretes.py --medir --nombre B_CONCORDIA_cobertura_control_20m
```

**Paso 9, alternativa recomendada para los Tp5 a Tp10: una sola muestra para las cuatro variantes.**

```
python Tp4_06_muestra_comun.py --disenar --nombre A1_muestra_comun_Tp5 --tp Tp5 ^
    --mapa "Optico solo|..\..\Tp5_Incendios\05_Resultados\02_Rasters\A1_variante_optico.tif" ^
    --mapa "SAR solo (C)|..\..\Tp5_Incendios\05_Resultados\02_Rasters\A1_variante_C.tif" ^
    --mapa "SAR multibanda|..\..\Tp5_Incendios\05_Resultados\02_Rasters\A1_variante_CL.tif" ^
    --mapa "Multisensor|..\..\Tp5_Incendios\05_Resultados\02_Rasters\A1_variante_multisensor.tif" ^
    --n 200 --reparto "todas=50,ninguna=50,desacuerdo=100"
python Tp4_06_muestra_comun.py --estimar --nombre A1_muestra_comun_Tp5 --clase 1
```

`--clase` acepta el código de la clase (`1`) o su nombre (`quemado`, si `Tp4_03` se corrió con `--nombres_clase "1=quemado,..."`).

## Qué hacer si falla

| Mensaje | Causa | Qué hacer |
|---|---|---|
| `AUTOPRUEBA: FALLA: NO USAR` | el script fue modificado | no seguir; avisar al docente |
| `b) No se pudo leer JRC GSW (...)` | sin red o el proxy bloquea el Planetary Computer | correr con `--sin_jrc` y repetir con red |
| `El mapa tiene 1 clase(s)...` | banda equivocada o mapa vacío | revisar `--banda` y el mapa en QGIS |
| `Falta --nombre (el mismo que uso Tp4_02).` | no se pasó `--nombre` | agregarlo |
| `ValueError: Cada estrato necesita al menos 2 puntos etiquetados.` | una clase quedó con 0 o 1 punto etiquetado | etiquetar más puntos de esa clase |
| `AVISO: N de M puntos sin etiquetar` | puntos con `clase_ref` vacío | completar o declarar |
| `Falta ...exactitud_y_area.csv (correr Tp4_02 y Tp4_03 ...)` | esa variante no se validó | correr los pasos 6 a 8 para esa variante |
| `La clase X no esta en ...` | `--clase` no es ni el código ni el nombre de la tabla | usar el código (`1`) o el nombre de `--nombres_clase` |
| `Una sola variante: no hay comparacion.` | `Tp4_04` con una sola `--variante` | es correcto en el ensayo; en los Tp5 a Tp10 agregar las otras variantes |
| `aproximacion normal inadecuada (n*p < 5): leer Wilson` | pocos aciertos o pocos errores en un estrato | leer las columnas `_inf`/`_sup` y el intervalo de Wilson |
| `YA EXISTE ... con N puntos etiquetados: NO se reescribe.` | `Tp4_02` protege un GeoPackage ya etiquetado | seguir con `Tp4_03`; para un muestreo nuevo, copiar el GeoPackage y correr con `--sobrescribir` |
| `PermissionError` al escribir el GeoPackage | QGIS lo tiene abierto | quitar la capa de QGIS y repetir |

**Un GeoPackage ya etiquetado no se pierde:** si se vuelve a correr `Tp4_02` sobre el mismo mapa, el programa lo detecta y no lo reescribe (`YA EXISTE ... NO se reescribe`). Para un muestreo nuevo, copie antes el GeoPackage etiquetado a otro nombre y corra con `--sobrescribir`.
