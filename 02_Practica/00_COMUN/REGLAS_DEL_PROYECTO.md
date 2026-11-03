# Reglas del proyecto

Estas reglas valen para los diez prácticos. Los programas las cumplen; quien
escriba un programa nuevo (o le pida uno a una IA) debe cumplirlas también.

## 1. Un solo lugar para cada definición

- Sitios, eventos, grilla, rutas y nombres de carpetas se definen **una vez**,
  en `configuracion_comun.py`. Ningún práctico los redefine.
- Las funciones que usan varios prácticos están en `funciones_comunes.py`,
  `funciones_cambio.py` y `funciones_lidar.py`.

## 2. La grilla común

- **EPSG:32721 (UTM 21S)**. Píxel de 10 m por defecto; 20 m (o el que el
  práctico justifique) cuando un sensor más grueso lo exige.
- Los bordes de la grilla son múltiplos exactos del píxel: dos rásters del mismo
  sitio y el mismo píxel se apilan sin volver a remuestrear.
- Para pasar a un píxel más grueso se **promedia** (radar en potencia lineal,
  reflectancias); para clases y máscaras se usa el **vecino más cercano** o la
  moda. No se afina a un píxel más chico que el nativo para «ganar detalle».

## 3. Unidades del radar

- Todo se calcula en **γ⁰ lineal** (o σ⁰ cuando el producto no permite otra
  cosa, y el nombre de la banda lo dice: `S_NovaSAR_sigma0_HH`).
- Los **dB** sirven para mirar y para poner umbrales. Los promedios se hacen en
  lineal: el promedio de los dB no es el dB del promedio.
- Composición RGB de un producto de doble polarización: **co-polarizada /
  polarización cruzada / cociente**.
- Los productos de SNAP se guardan en **BEAM-DIMAP** (`.dim`) con los metadatos
  originales, bandas lineales y bandas virtuales en dB.

## 4. Fechas

- La fecha de un dato es la de sus **metadatos** (adquisición), nunca la del
  archivo en el disco.
- Toda combinación de sensores informa la **diferencia de días** entre ellos.
- Sentinel-2 L2A con línea de base de procesamiento 04.00 o posterior trae un
  desplazamiento de +1000 en los números digitales: se descuenta siempre.

## 5. Sinergia y fusión

- Se dice siempre cuál de las dos se hace.
- **Sinergia:** cada sensor produce su resultado; se comparan sin combinarlos.
- **Fusión:** un algoritmo produce un único producto, a nivel de píxel, de rasgo
  o de decisión. Requiere misma grilla, corregistro menor que un píxel
  (medido, Tp3) y fechas compatibles (declaradas).
- La exactitud «fuera de bolsa» del Random Forest es **optimista** (usa píxeles
  vecinos de los mismos polígonos). La exactitud que se informa es la del Tp4,
  con referencia independiente.

## 6. Umbrales

- Ningún umbral se escribe sin mostrar el histograma con la línea del umbral
  (`umbral_documentado`). Otsu necesita dos modas: si no las hay, el umbral es
  manual, se justifica y se anota.

## 7. Validación

- La exactitud se estima con muestreo aleatorio estratificado y el estimador de
  Olofsson et al. (2014): exactitud global, de usuario y de productor, y
  superficie con intervalo de confianza del 95 %.
- Quien etiqueta los puntos **no ve** el mapa evaluado. La llave se abre al
  final.
- La referencia no puede ser el mismo dato que entró al mapa.

## 8. Trazabilidad

- Cada ráster lleva en sus metadatos `FUENTE` (organismo, producto, fecha y hora,
  dirección del catálogo) y `PROCESO`.
- Cada programa escribe una bitácora en `05_Resultados/06_Control_calidad` con lo
  que hizo, cuántos datos entraron y salieron, y el paso siguiente.
- Cada figura lleva la cita de la fuente al pie.

## 9. Credenciales

- **Nunca** se escribe un usuario, una contraseña o un token en un programa ni
  en un documento. Se usa el archivo `.netrc` del usuario, una variable de
  entorno o la pregunta del programa al correr.

## 10. Honestidad

- Lo que no se pudo hacer, o lo que se hizo con un dato de otra fecha, se
  declara. Una limitación declarada suma; una escondida invalida el resto.
- Un valor cero en toda una banda no es estabilidad: es una banda vacía. Un
  mapa con la forma del relieve está midiendo el relieve.
