# Tp2 — Orden de ejecución

Los scripts se corren desde esta carpeta, en el Miniforge Prompt:

```
conda activate sar
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp2_SAR_multibanda\03_Scripts
```

| Paso | Script o herramienta | Marca | Qué hace | Entrada | Salida | Tiempo aprox. |
|---|---|---|---|---|---|---|
| 0 | `..\..\Tp1_Convergencia\03_Scripts\Tp1_03_buscar_optico_y_C.py` | **AUXILIAR** | Elige la fecha de Sentinel-1 sobre el sitio | Planetary Computer | planilla del Tp1 | 5 min |
| 1 | `09_Grafos_SNAP\Tp2_S1_GRD_a_gamma0.xml` | **EN SNAP** | GRD → β⁰ → Terrain Flattening → Range Doppler, EPSG:32721, 10 m | `00_COMUN\08_Originales_crudos\S1_CRUDO\S1C_IW_GRDH_1SDV_20260926T091407_20260926T091432_009616_013235_EE65.zip` | `02_Subsets_SNAP_QGIS\<SITIO>_S1_<fecha>_gamma0.dim` | 15–30 min |
| 2 | `Radar > Speckle Filtering > Single Product Speckle Filter` | **EN SNAP** | Refined Lee o Lee Sigma, como paso aparte | producto del paso 1 | `..._gamma0_Spk.dim` | 5 min |
| 3 | `Raster > Data Conversion > Linear to/from dB` y `File > Export > GeoTIFF` | **EN SNAP** | Bandas virtuales en dB; una banda lineal por GeoTIFF | producto del paso 2 | `..._Gamma0_VV_Spk.tif`, `..._Gamma0_VH_Spk.tif` | 10 min |
| — | `00_COMUN\procesar_saocom.py` y `00_COMUN\procesar_s1_crudo.py` (grafos de SNAP) | **YA VIENE HECHO** | SAOCOM del Delta a γ⁰ (para el ejemplo de `A1_DELTA_QUEMAS`) y el Sentinel-1 del 26/09/2026 procesado por el docente (para comparar) | archivo del curso 2023; `S1_CRUDO` | `Tp5_Incendios\02_Subsets_SNAP_QGIS\SAOCOM_gamma0\`; `02_Subsets_SNAP_QGIS\S1_procesado_desde_crudo\` | 5 a 30 min por escena |
| 4 | `Tp2_01_pila_multibanda.py` | **SE CORRE** | Pila de radar en lineal sobre la grilla común | RTC, NISAR, NovaSAR, GeoTIFF de SNAP, BIOMASS banda P (`#1` HH, `#3` VH; el HV trae RFI de origen) | `02_Subsets_SNAP_QGIS\<SITIO>_pila_gamma0_lineal.tif` y `<SITIO>_pila_bandas.csv` | unos 30 s (medido: 27 a 37 s con 14 bandas) |
| 5 | `Tp2_02_rgb_copol_cruzada_cociente.py` | **SE CORRE** | RGB co-pol / cros-pol / cociente por sensor dual (por escena para mirar; con `--rango_fijo`, los mismos límites para comparar sensores) | la pila | `05_Resultados\02_Rasters\<SITIO>_RGB_<etiqueta>[_rango_fijo].tif` y PNG en `05_Graficos` | 1 min |
| 6 | digitalización | **EN QGIS** | Polígonos de cubierta, con la clase `estable` | RGB, imagen de fondo | `04_Tablas_de_trabajo\cubiertas_<SITIO>.gpkg` | 40 min |
| 7 | `Tp2_03_respuesta_por_cubierta.py` | **SE CORRE** | Respuesta por cubierta y banda; contrastes; cajas | pila y cubiertas | `<SITIO>_respuesta_por_cubierta.csv`, `<SITIO>_media_por_poligono.csv`, `<SITIO>_contraste_entre_clases.csv` (con la separabilidad M), `<SITIO>_cajas_por_banda.png` | 1 min |
| 8 | `Tp2_04_control_zona_estable.py` (y, para profundizar, `Tp2_05_saocom_por_cubierta.py`) | **SE CORRE** | Diferencia en zona estable < 1 dB, también por polígono y con intervalo del 95 % por remuestreo de polígonos | pila y clase `estable` (entre procesadores del mismo día, cubiertas homogéneas) | `<SITIO>_control_zona_estable[_sufijo].csv` | 1 min |
| 9 | QGIS y `08_Orange\Tp2_E_bandas_por_clase_MapBiomas.ows` | **EN QGIS + ORANGE** | Contexto del sitio: cobertura MapBiomas 2025 y biomasa CCI frente a cada banda | `QGIS_GeoTIFF\A2_IBICUY_MapBiomas_cobertura_1985_2025.tif`, `..._CCI_Biomass_v7_AGB.tif`, la pila | figuras y respuestas | 30 min |

El paso 7 se corre **dos veces**: la primera crea `cubiertas_<SITIO>.gpkg` vacío y se
detiene; la segunda, después de digitalizar, calcula.

## Las órdenes, con sus argumentos

```
python Tp2_01_pila_multibanda.py --sitio A2_IBICUY --fecha_c 2026-09-26
python Tp2_01_pila_multibanda.py --sitio A2_IBICUY --fecha_c 2026-09-26 ^
       --extra "C_SNAP_gamma0_VV=D:\CURSOS_CEREGEO_2026\02_Practica\Tp2_SAR_multibanda\02_Subsets_SNAP_QGIS\A2_IBICUY_S1_20260926_Gamma0_VV_Spk.tif|Sentinel-1 SNAP|5.6|2026-09-26|gamma0|D|68" ^
       --extra "C_SNAP_gamma0_VH=D:\CURSOS_CEREGEO_2026\02_Practica\Tp2_SAR_multibanda\02_Subsets_SNAP_QGIS\A2_IBICUY_S1_20260926_Gamma0_VH_Spk.tif|Sentinel-1 SNAP|5.6|2026-09-26|gamma0|D|68" ^
       --extra "P_BIOMASS_gamma0_HH=D:\CURSOS_CEREGEO_2026\02_Practica\Tp2_SAR_multibanda\02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\A2_IBICUY_BIOMASS_P_20261005.tif#1|BIOMASS|69.0|2026-10-05|gamma0E|A|6" ^
       --extra "P_BIOMASS_gamma0_VH=D:\CURSOS_CEREGEO_2026\02_Practica\Tp2_SAR_multibanda\02_Subsets_SNAP_QGIS\QGIS_GeoTIFF\A2_IBICUY_BIOMASS_P_20261005.tif#3|BIOMASS|69.0|2026-10-05|gamma0E|A|6"
python Tp2_01_pila_multibanda.py --sitio F_BOVRIL --novasar 47974 --fecha_c 2023-09-17
python Tp2_01_pila_multibanda.py --sitio F_BOVRIL --novasar 47974 --fecha_c 2023-09-17 --desplazamiento -92 -484
python Tp2_01_pila_multibanda.py --sitio A1_DELTA_QUEMAS --fecha_c 2020-07-16 ^
       --extra "L_SAOCOM_gamma0_HH=D:\CURSOS_CEREGEO_2026\02_Practica\Tp5_Incendios\02_Subsets_SNAP_QGIS\SAOCOM_gamma0\QGIS_GeoTIFF\A1_DELTA_QUEMAS_SAOCOM_L_20200721_QP_gamma0_Gamma0_HH.tif|SAOCOM-1A|23.5|2020-07-21|gamma0E" ^
       --extra "L_SAOCOM_gamma0_HV=D:\CURSOS_CEREGEO_2026\02_Practica\Tp5_Incendios\02_Subsets_SNAP_QGIS\SAOCOM_gamma0\QGIS_GeoTIFF\A1_DELTA_QUEMAS_SAOCOM_L_20200721_QP_gamma0_Gamma0_HV.tif|SAOCOM-1A|23.5|2020-07-21|gamma0E"
    (opcionales: --min_validos 20, el valor por defecto;
                 --desplazamiento DX DY en metros, sólo para NovaSAR, DX + = este, DY + = norte)

python Tp2_02_rgb_copol_cruzada_cociente.py --sitio A2_IBICUY
python Tp2_02_rgb_copol_cruzada_cociente.py --sitio A2_IBICUY --rango_fijo

python Tp2_03_respuesta_por_cubierta.py --sitio A2_IBICUY

python Tp2_04_control_zona_estable.py --sitio A2_IBICUY
python Tp2_04_control_zona_estable.py --sitio A2_IBICUY --a C_S1_gamma0_VV --b C_SNAP_gamma0_VV
python Tp2_04_control_zona_estable.py --sitio A2_IBICUY --a C_S1_gamma0_VH --b C_SNAP_gamma0_VH
python Tp2_04_control_zona_estable.py --sitio A2_IBICUY --a C_S1_gamma0_VV --b C_SNAP_gamma0_VV ^
       --clase monte_o_bosque pajonal agua_calma --sufijo C_S1_vs_SNAP_VV_homogeneas
    (--clase: una o varias clases; por defecto, estable. --sufijo: se agrega al nombre de la
     tabla y de la bitacora, para que una corrida no pise a la anterior)

python Tp2_05_saocom_por_cubierta.py --sitio A2_IBICUY      (para profundizar)
python Tp2_06_saocom_pauli_y_fase.py pol                     (para profundizar; lo corre el docente:
                                                              Pauli y fase HH–VV sobre el SLC de SAOCOM)
```

Herramientas del docente que aparecen en el Desarrollo (`00_COMUN\09_Herramientas\des_embeddings.py`,
`des_saocom_comparaciones.py` y, en esta carpeta, `Tp2_06_saocom_pauli_y_fase.py`): **las corrió el docente; el alumno sólo mira el resultado**. No
son pasos del práctico.

La fecha `2026-09-26` es la de la escena GRD que dejó el docente: si eligió otra en el paso 0, use la suya. El `^` al final
de una línea es la continuación de línea del símbolo del sistema de Windows; si
escribe todo en una sola línea, no hace falta.

Forma de `--extra`: `"nombre_de_banda=ruta.tif|sensor|lambda_cm|AAAA-MM-DD|unidad|pasada|traza"`,
una vez por banda. Unidad: `gamma0` (normalizado por el terreno), `gamma0E` (γ⁰ sobre el
elipsoide: BIOMASS L1B, SAOCOM del curso) o `sigma0`. Pasada `A` o `D` y traza, de los
metadatos (SNAP: `Abstracted_Metadata`, `PASS` y `REL_ORBIT`). Todo lo que sigue a la ruta
es opcional para el programa, pero se pone siempre: sin ellos la banda queda con sensor
`SNAP`, sin fecha, con «unidad sin declarar» y sin pasada, el Tp3 no la ubica en la tabla
de fechas y el paso 8 marca sus pares como «geometría no verificada».

Reglas para el nombre de la banda: `<banda>_<sensor>_<gamma0|sigma0>_<pol>`, con la
polarización al final (`_VV`, `_VH`, `_HH`, `_HV`) para que el paso 5 encuentre la
gemela. Si el GeoTIFF está en dB, agregue `_db` al final del nombre: el programa lo
pasa a lineal en su grilla original y después lo promedia a la grilla común.

`--desplazamiento DX DY` corrige NovaSAR (georreferenciado con sólo cuatro puntos de
esquina) con lo que mide `Tp3_02`: DX positivo mueve la capa hacia el este, DY
positivo hacia el norte. Para la 47974, lo medido en el Tp3 es 92 m al oeste y 484 m
al sur: `--desplazamiento -92 -484`.

## Variables de entorno (sólo si hacen falta)

```
set CURSO_SAR_NISAR_DELTA=<carpeta con BANDA_L_NASA y BANDA_S_ISRO>
set CURSO_SAR_NOVASAR=E:\IMÁGENES NOVASAR-1 2023 2024\ENTRE RIOS-SANTA FE
```

Son los valores por defecto del código; se cambian sólo si los datos están en otra unidad.

## Qué hacer si falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `No such file ... _pila_gamma0_lineal.tif` en los pasos 5 a 8 | No se corrió el paso 4 con ese sitio | Correr `Tp2_01` con el mismo `--sitio` |
| `No se reunio ninguna banda con datos suficientes` | Ninguna banda cubre el 20 % del sitio | Revisar sitio y fecha; NISAR y NovaSAR no cubren todos los sitios |
| `El catalogo no tiene Sentinel-1 RTC ese dia` | Fecha sin pasada o sin red | Otra fecha del paso 0; si no hay red, declararlo |
| `FileNotFoundError ... GRD de la escena` | NovaSAR no está en el equipo o el número es otro | Ver la variable `CURSO_SAR_NOVASAR` y `NOVASAR_ESCENAS` en `configuracion_comun.py` |
| Un sensor dual sale en gris en el paso 5 | Nombres sin la polarización al final | Corregir el nombre en `--extra` y correr de nuevo el paso 4 |
| `AVISO: sin fecha` en el paso 4 | El `--extra` no lleva `|sensor|lambda_cm|AAAA-MM-DD` | Completar la orden y correr de nuevo el paso 4 |
| `AVISO: sin --desplazamiento` | NovaSAR entró sin corregir | Medir con `Tp3_02` y agregar `--desplazamiento DX DY` |
| `KeyError` en el paso 8 | `--a` o `--b` no existe en la pila | Copiar el nombre exacto de `<SITIO>_pila_bandas.csv` |
| `No hay poligonos de clase 'estable'` | Falta digitalizar la clase | Paso 6 |
| `PermissionError` | El CSV o el TIF están abiertos en Excel o QGIS | Cerrarlos (en QGIS, quitar la capa) y volver a correr |
| SNAP: `No valid orbit file found` | Sin red al servidor de órbitas | El grafo sigue con la órbita de la anotación; declararlo |
| SNAP: falla la descarga del DEM | Sin red | El docente deja el DEM en la carpeta auxiliar de SNAP |
