# Prompt inicial del Tp7 — el que se escribió primero

---

> Tengo un interferograma COSMO-SkyMed de la barranca de Diamante y puedo bajar
> Sentinel-1. Hacé un mapa de deformación de la barranca combinando las dos
> bandas y calculá cuánto volumen se cayó con el MDE.

---

## Qué produjo

Un script que abría la banda `Unw_Phase` del producto de SNAP, la convertía a
milímetros, bajaba un par Sentinel-1 cualquiera de 2024, promediaba los dos
desplazamientos y restaba el Copernicus DEM del MDE del IGN. Corría de punta a
punta. Daba un mapa «estable» y un volumen.

## Los cinco defectos

**1. Tomó la banda `Unw_Phase` vacía como dato.** La fase desenrollada del
producto del curso 2023 vale cero en todo el sitio porque el desenrollado con
SNAPHU nunca se importó. El script la convirtió a desplazamiento y concluyó «la
barranca no se mueve». Cero no es estabilidad: es una banda sin contenido.

**2. Mezcló períodos.** El par X es del 15 y 19 de octubre de 2018; el par C,
de 2024. Fusionar dos bandas que miran momentos distintos no confirma nada:
responde dos preguntas distintas a la vez.

**3. Promedió desplazamientos de geometrías distintas.** Cada satélite mide en
SU línea de visión. Un movimiento hacia el río puede acercar la ladera a un
satélite que mira desde el oeste y alejarla del que mira desde el este. Promediar
LOS de pasadas distintas puede cancelar una señal real.

**4. No refirió el desplazamiento a una zona estable ni filtró por coherencia.**
La interferometría mide diferencias. Sin una referencia, el desplazamiento
absoluto no significa nada; sin filtro de coherencia, el agua del Paraná entra
como «deformación».

**5. Calculó el volumen sin medir el sesgo entre MDE.** El IGN de 5 m y el GLO-30
difieren en datum vertical, resolución y fecha. Restarlos sin descontar el sesgo
de una zona estable atribuye a la barranca decímetros que son del datum.

## La lección

El prompt pedía «un mapa de deformación». Un mapa siempre sale. Lo que faltaba
era preguntar **si cada banda tenía dato, del mismo período y en la misma
geometría**, y cuánto de lo que se ve está por encima del ruido.
