# Prompt inicial del Tp9 — el que se escribió primero

---

> Necesito un mapa de deforestación del monte de Federal entre 2011 y 2026. Tengo
> ALOS de 2011, ALOS-2 de 2021 y NISAR de 2026. Restá el HV entre fechas y donde
> baja mucho es desmonte. Usá también el NDVI.

---

## Qué produjo

Un script que leía las tres escenas de banda L, restaba HV de 2026 menos HV de
2011 en dB, umbralaba en −3 dB y hacía la intersección con una caída de NDVI.
Daba un mapa de «desmonte 2011–2026» y una superficie en hectáreas, sin
ninguna incertidumbre.

## Los cinco defectos

**1. Pidió HV de 2011 a una escena FBS.** ALOS-1 FBS es de una sola
polarización: HH. El HV de 2011 existe sólo en escenas FBD. El script leyó la
única banda del archivo como si fuera HV y comparó HH de 2011 con HV de 2026: una
diferencia de varios dB que no es cambio, es polarización.

**2. Restó tres instrumentos sin calibrarlos entre sí.** ALOS-1, ALOS-2 y NISAR
tienen calibraciones, ángulos de incidencia y procesamientos distintos. Sin medir
el desfase en una zona estable, una parte de la «pérdida» es la diferencia entre
sensores.

**3. Promedió y remuestreó en dB.** Llevó ALOS-2 de 25 m y ALOS-1 de 12,5 m a la
grilla promediando en dB. El promedio de los logaritmos no es el logaritmo del
promedio: sesga hacia abajo, y más donde hay más speckle.

**4. Confundió cosecha con desmonte.** Un lote de soja cosechado baja el NDVI y,
en banda L, también baja algo el HV. Sin una clase «no bosque estable» que
incluya cultivos, cada cosecha entre fechas salió como desmonte.

**5. No miró la degradación.** El monte raleado conserva cobertura y verdor: no
baja el NDVI. La pregunta del práctico pide pérdida **y** degradación; el script
sólo podía ver la primera.

## La lección

El prompt pedía «restar el HV». La resta siempre da un número. Lo que faltaba
era preguntar **si los dos HV existían, si venían del mismo instrumento y si lo
que bajó era monte**.
