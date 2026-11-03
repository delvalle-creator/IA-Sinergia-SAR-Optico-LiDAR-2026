# Prompt inicial del Tp3 — el que se escribió primero

---

> Juntá en un solo raster de 10 m el Sentinel-2, la pila de radar del Tp2 y las
> alturas de GEDI, así después lo meto en un Random Forest.

---

## Qué produjo

Un script que reproyectaba todo a 10 m con interpolación bilineal, interpolaba las
huellas GEDI a una superficie continua (IDW), apilaba las capas y escribía un GeoTIFF
de muchas bandas. Corría. Daba un cubo listo para el clasificador.

## Los cinco defectos

**1. Llevó todo a 10 m.** NISAR GCOV es de 20 m y Sentinel-2 tiene bandas de 20 m
(B11, B12). Pasarlas a 10 m con bilineal **inventa** un detalle que el sensor nunca
vio, y el clasificador lo trata como información. La grilla común se elige con la
resolución **más gruesa** del análisis.

**2. Remuestreó el radar con bilineal, sin decir en qué unidad.** Si la pila estaba en
dB, la interpolación promedió logaritmos. Para agregar radar a un píxel más grueso se
promedia potencia, en lineal.

**3. Interpoló las huellas GEDI a una superficie.** GEDI muestrea: huellas de 25 m
separadas por decenas o cientos de metros. Una superficie interpolada fabrica alturas
donde no se midió nada, y además mezcla huellas de 2019 con huellas de 2025. Al LiDAR
no se lo rasteriza: se lleva el cubo a la huella.

**4. Ignoró las nubes.** Apiló las reflectancias de Sentinel-2 sin aplicar la SCL. El
clasificador iba a aprender que «nube» es una cubierta.

**5. No midió nada.** Ni si los sensores estaban corregistrados, ni cuántos días
separaban el óptico del radar, ni de qué fecha era cada huella. El cubo «estaba
alineado» porque todas las capas tenían el mismo número de filas y columnas. Eso es
misma grilla; no es corregistro.

## La lección

El prompt pedía «juntar en un raster». La IA juntó. Faltaba pedirle que **demostrara**
que lo que juntó se puede fusionar: misma grilla con la resolución correcta,
corregistro medido, fechas documentadas, y el LiDAR tratado como lo que es, una muestra.
