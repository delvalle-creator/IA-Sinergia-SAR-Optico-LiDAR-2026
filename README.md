# Sinergias multisensor y estrategias de fusión SAR-Óptico-LiDAR para evaluación de emergencias ambientales

**Curso de posgrado · Diamante (Entre Ríos), 2026**

**Héctor Francisco del Valle** · ORCID [0000-0002-3329-1057](https://orcid.org/0000-0002-3329-1057)

Centro Regional de Geomática (CeReGeo), Facultad de Ciencia y Tecnología (FCyT), Universidad Autónoma de Entre Ríos (UADER).

Laboratorio de Ecología, Meteorología y Gestión de Fuegos (LEMIV), Facultad de Ingeniería, Universidad Nacional de la Patagonia San Juan Bosco (UNPSJB).

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23929604.svg)](https://doi.org/10.5281/zenodo.23929604)

| | DOI |
|---|---|
| Todas las versiones (DOI de concepto) | [10.5281/zenodo.23929604](https://doi.org/10.5281/zenodo.23929604) |
| Versión 1.1.0 | [10.5281/zenodo.24019793](https://doi.org/10.5281/zenodo.24019793) |
| Versión 1.0.0 | [10.5281/zenodo.23929605](https://doi.org/10.5281/zenodo.23929605) |

## Desarrollo con inteligencia artificial

Este curso fue desarrollado en su mayor parte con la inteligencia artificial Claude (Anthropic) y con aportes de ChatGPT (OpenAI) y Copilot (Microsoft), en sus versiones Premium. La idea, la supervisión y la revisión de todo el material son del docente responsable, Héctor Francisco del Valle.

## Qué es

Un curso práctico (40 horas, cinco días) sobre el uso conjunto de radar de apertura sintética (bandas X, C, S, L y P), datos ópticos y LiDAR satelital (GEDI, ICESat-2) para evaluar emergencias ambientales en Entre Ríos: incendios en las islas del Delta, inundaciones del río Uruguay en Concordia, barrancas y deslizamientos en Diamante, erosión de suelos en Bovril, deforestación del monte y expansión urbana. El curso distingue en cada paso la **sinergia** (cada sensor produce su resultado y se interpretan juntos) de la **fusión** (un algoritmo combina los datos en un único producto, a nivel de píxel, de rasgo o de decisión).

## Por dónde empezar

1. `02_Practica/00_LEEME_PRIMERO.md`: organización del curso, cronograma y preparación del entorno de Miniforge.
2. `02_Practica/00_Guia_teorica_practica/Guia_teorico_practica_SAR_Optico_LiDAR.pdf`: la guía completa.
3. `01_Teoria`: las once presentaciones de teoría, en PDF (la 11, de mosaicos y productos globales para Entre Ríos).

Los archivos `.md` se leen formateados en GitHub, o en VS Code con `Ctrl+Shift+V`.

## Contenido

| Carpeta | Contenido |
|---|---|
| `01_Teoria` | Presentaciones de teoría (PDF) |
| `02_Practica/00_LEEME_PRIMERO.md` | Punto de entrada de la práctica |
| `02_Practica/00_Guia_teorica_practica` | Guía teórico-práctica (PDF) |
| `02_Practica/00_Desarrollo_docente` | Desarrollo resuelto de cada práctico (`Tp1_final.pdf` a `Tp10_final.pdf`) y proyectos de QGIS (`TpN_QGIS`) |
| `02_Practica/Guia sintetica` | Guía sintética de cada práctico (`Tp1_sintético.pdf` a `Tp10_sintético.pdf`) |
| `02_Practica/00_COMUN` | Programas comunes, entorno `entorno_sar.yml`, áreas de estudio, conexiones WMS de CONAE y herramientas |
| `02_Practica/Tp1_…` a `Tp10_…` | Guía, prompts de IA, scripts, tablas, bibliografía, preguntas, flujos de Orange y grafos de SNAP de cada práctico |
| `03_Trabajos_futuros` | Plan de vuelo con dron para la barranca de Diamante |

## Lo que no está en este repositorio

$${\color{red}\textbf{LOS DATOS SATELITALES NO ESTÁN EN GITHUB. SE ENTREGAN EN EL DISCO EXTERNO DEL CURSO.}}$$

**LOS DATOS SATELITALES NO ESTÁN EN GITHUB. SE ENTREGAN EN EL DISCO EXTERNO DEL CURSO.** Por el límite de tamaño de GitHub quedan fuera los datos originales sin procesar (`00_COMUN/08_Originales_crudos`), los recortes de cada práctico (`02_Subsets_SNAP_QGIS`), las tablas LiDAR completas (`00_COMUN/05_LiDAR_tablas`) y las capas y gráficos de `05_Resultados`. Las figuras de resultados están en los Desarrollos (`TpN_final.pdf`). Los proyectos de QGIS y los prácticos se ejecutan sobre la copia completa del disco externo. Los programas de descarga de cada práctico permiten volver a bajar los datos desde los portales oficiales.

## Programas

Miniforge (entorno `sar`), ESA SNAP 14, QGIS 3.44 LTR y Orange Data Mining 3.40.

El complemento **NISAR GCOV Reader** (`02_Practica/00_COMUN/09_Herramientas/NISAR_GCOV_Reader`) es de autoría de Héctor Francisco del Valle, autor de este curso.

## Licencia

El material del curso se distribuye con licencia [Creative Commons Atribución-NoComercial-CompartirIgual 4.0 Internacional (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es).

Las imágenes Pléiades y Pléiades Neo de `02_Practica/00_COMUN/10_Alta_resolucion_CONAE` son propiedad de CONAE (© Airbus Defence and Space) y están sujetas a su propia licencia: no se rigen por la licencia del curso. Los datos satelitales pertenecen a sus proveedores (NASA, ESA, CONAE, JAXA, ASI, ISRO, INPE, MapBiomas, entre otros), con sus propias condiciones de uso.

## Cómo citar

del Valle, H. F. (2026). *Sinergias multisensor y estrategias de fusión SAR-Óptico-LiDAR para evaluación de emergencias ambientales. Curso de posgrado, Diamante (Entre Ríos), 2026* (Versión 1.1.0) [Material de curso]. Zenodo. https://doi.org/10.5281/zenodo.24019793

También puede usar el botón **Cite this repository** de GitHub o el archivo `CITATION.cff`.
