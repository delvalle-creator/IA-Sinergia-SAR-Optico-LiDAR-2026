# NISAR GCOV Reader

Complemento de QGIS que abre productos **NISAR GCOV (Nivel 2, HDF5)** y los
convierte a los formatos con los que se trabaja en el práctico.

**Autor: Héctor Francisco del Valle** (Universidad Nacional del Sur — CONICET). Es un complemento de su autoría, el mismo autor del curso. Versión
1.8.1, para QGIS 3.22 o posterior. Se distribuye con el curso.

---

## Por qué hace falta

SNAP 14 no trae lector de GCOV. Su lector de NISAR cubre el Nivel 1, no el
Nivel 2, de modo que el producto geocodificado —que es justamente el que ya
viene resuelto, con corrección radiométrica de terreno aplicada— no se puede
abrir.

El obstáculo es concreto: el driver HDF5 de GDAL lee los números pero no las
coordenadas, porque NISAR no guarda un geotransform sino dos arreglos aparte,
`xCoordinates` e `yCoordinates`. Un producto sin georreferencia no sirve para
nada.

Este complemento reconstruye esa georreferencia y escribe el producto como
GeoTIFF o como BEAM-DIMAP. No modifica el lector de Nivel 1 de SNAP ni ningún
otro complemento de QGIS: es un paquete separado.

---

## Qué contiene

```
nisar_gcov_reader\          el complemento de QGIS
    metadata.txt
    __init__.py
    nisar_gcov_plugin.py    la ventana
    nisar_gcov_core.py      el lector, que no depende de QGIS
    nisar_gcov_cli.py       el mismo lector por línea de comandos
    icon.png
GCOV_para_SNAP.bat          conversión a BEAM-DIMAP de un doble clic
NISAR_GCOV_Reader_v1.8.1.zip   el complemento empaquetado, para instalar
LEEME.md
```

---

## 1. Instalar en QGIS

Dos caminos, el que resulte más cómodo.

**Desde el ZIP.** QGIS → Complementos → Administrar e instalar complementos →
Instalar a partir de un ZIP → elegir `NISAR_GCOV_Reader_v1.8.1.zip`.

**A mano.** Copiar la carpeta `nisar_gcov_reader` completa dentro de:

```
C:\Users\SU_USUARIO\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
```

y después tildarlo en Complementos → Administrar e instalar complementos →
Instalados.

Queda un ícono en la barra y una entrada en **Ráster → NISAR GCOV → Abrir
producto NISAR GCOV…**

Se elige el `.h5`, el complemento lista las grillas (`frequencyA`,
`frequencyB`) y las capas que hay adentro —HHHH, HVHV, VVVV y las auxiliares
`mask`, `numberOfLooks`, `rtcGammaToSigmaFactor`—, se marca lo que se quiere,
se decide si se pasa a decibeles y se procesa. Los GeoTIFF quedan en la carpeta
de salida y se cargan solos en el proyecto.

---

## 2. Abrir en SNAP 14

El paquete convierte el GCOV a BEAM-DIMAP, que es el formato propio de SNAP:

1. Arrastrar el `.h5` sobre **`GCOV_para_SNAP.bat`**, o ejecutarlo y pegar la
   ruta.
2. Queda un `NOMBRE_frequencyA.dim` y su carpeta `.data`.
3. En SNAP: **File → Open Product** y abrir el `.dim`.

Las bandas conservan su nombre (`HHHH_db`, `HVHV_db`…), la proyección y el
tamaño de píxel. Desde ahí funcionan las herramientas normales de SNAP.

Si el `.dim` diera problema, la salida GeoTIFF también se abre con File → Open
Product.

---

## 3. Línea de comandos

Desde el **OSGeo4W Shell**:

```
python-qgis-ltr ...\nisar_gcov_cli.py ARCHIVO.h5 --info
python-qgis-ltr ...\nisar_gcov_cli.py ARCHIVO.h5 -o C:\salida --db
python-qgis-ltr ...\nisar_gcov_cli.py ARCHIVO.h5 -o C:\salida --db --dimap
python-qgis-ltr ...\nisar_gcov_cli.py ARCHIVO.h5 -o C:\salida --db --submuestreo 4
```

`--info` imprime la estructura interna del archivo. Es lo primero que conviene
correr cuando algo no sale como se espera.

---

## Detalles que importan

**Tamaño.** Un GCOV completo puede tener unas 37.000 × 36.700 celdas: cada
polarización pesa alrededor de 5 GB en float32. Para una vista rápida o para
trabajar en clase conviene el submuestreo —una celda de cada cuatro son
dieciséis veces menos datos—. El diálogo muestra el tamaño estimado antes de
procesar.

**Decibeles.** El `10*log10` se aplica sólo a los términos de la diagonal
(HHHH, HVHV, VVVV), que son potencia gamma0. Los ceros y los negativos quedan
como NoData.

**Dual, compacto y cuadripolar.** Los términos de la diagonal salen como una
capa cada uno. Los términos complejos fuera de la diagonal, que sólo existen en
productos cuadripolares, salen como dos capas, `_real` e `_imag`, porque un
ráster de una banda no puede guardar un número complejo. Vienen destildados: si
no se va a hacer polarimetría, no hacen falta.

**Matriz C3 para SNAP**, sólo en cuadripolar. El tercer formato de salida
escribe un BEAM-DIMAP con las bandas nombradas `C11, C12_real, C12_imag,
C13_real, C13_imag, C22, C23_real, C23_imag, C33`, que es la nomenclatura con la
que SNAP reconoce una matriz de covarianza y habilita las descomposiciones
polarimétricas. Se escribe siempre en potencia lineal, nunca en decibeles.

Sobre esto hay una advertencia que conviene tener presente: SNAP asume el vector
de dispersión [HH, √2·HV, VV]. Si los términos vinieran publicados sin ese
factor √2, C22 y los términos cruzados quedarían con otra escala y las
descomposiciones cuantitativas saldrían sesgadas. Antes de usar esa salida para
medir hay que verificar la convención en la especificación del producto. Para
inspección visual y clasificación relativa no cambia nada. Las escenas de este
curso son duales HH/HV, de modo que no las alcanza.

**Georreferencia.** Se arma con `xCoordinates` e `yCoordinates` —que son centros
de celda, y se corrigen a esquina— y con el código EPSG declarado en el conjunto
`projection`. Si un producto no declarara EPSG, el diálogo lo avisa y el ráster
sale sin sistema de referencia.

**Sin dependencias nuevas.** Usa el GDAL que ya trae QGIS, por su interfaz
multidimensional. Si hay `h5py` instalado lo aprovecha, pero no es necesario.

---

## Comprobaciones del lector

La lectura se verificó sobre un producto con la estructura completa de un GCOV
—`/science/LSAR/GCOV/grids/frequencyA` con `xCoordinates`, `yCoordinates`,
`projection`/EPSG, HHHH, HVHV, VVVV, un término complejo y las capas
auxiliares—, y sobre las escenas reales de la ventana Esquel-Trevelin-Cholila:

- la estructura se detecta y el término complejo se descarta cuando no se pide;
- el EPSG se lee del producto, y el GeoTransform y el tamaño de píxel salen
  exactos;
- los dos caminos de lectura, GDAL y h5py, dan valores idénticos;
- el GeoTIFF y el BEAM-DIMAP dan valores idénticos;
- con submuestreo 1/3 el tamaño de píxel se triplica y la grilla sigue siendo
  coherente;
- los `.dim` de las escenas reales abren en SNAP 14 y sus bandas alimentan un
  grafo sin conversión intermedia.

---

## En este curso

- Los programas de los prácticos **no necesitan** este complemento: leen el
  `.h5` directamente con `nisar_gcov_en_grilla()` de `funciones_comunes.py`, que
  aplica la máscara del producto (0 = inválido, 255 = fuera de la pasada) y lleva
  el γ⁰ a la grilla común. El complemento sirve para **mirar** los GCOV en QGIS y
  para abrirlos en SNAP.
- Los NISAR del Delta (`00_COMUN\08_Originales_crudos\NISAR_DELTA`, que llena `datos_crudos.py nisar`) traen banda L (NASA, grupo
  `/science/LSAR`) y banda S (ISRO, grupo `/science/SSAR`). El complemento
  busca las grillas sin suponer la banda; con los productos de banda S del
  curso conviene correr primero `--info` para confirmar qué grupos lista.
- Sin aplicar la máscara aparecen, en los bordes de la pasada, valores de γ⁰
  del orden de −133 dB que no son terreno: en QGIS, cargue también la capa
  `mask` y use sólo los valores 1 a n.
