# 05_Resultados — qué va a aparecer aquí

Los scripts crean las subcarpetas al correr.

| Subcarpeta / archivo | Quién lo escribe | Qué es |
|---|---|---|
| `04_Tablas/F_escenas_opticas_2023.csv` | `Tp8_01` | Cada escena Sentinel-2: fecha, id, % útil, si se usó y % de suelo desnudo |
| `04_Tablas/F_textura_por_frecuencia.csv` | `Tp8_02` | CV mediano de cada banda por clase de frecuencia de suelo desnudo (sinergia) |
| `02_Rasters/F_variante_optico.tif` | `Tp8_03` | Solo óptico: 1 si ≥ 6 meses desnudo, 2 si no |
| `02_Rasters/F_susceptibilidad.tif` | `Tp8_03` | Índice de susceptibilidad 0–1 (fusión de rasgos) |
| `02_Rasters/F_variante_multisensor.tif` | `Tp8_03` | 1 si susceptibilidad ≥ umbral, 2 si no |
| `06_Control_calidad/Tp8_01_suelo_desnudo.log`, `Tp8_02_textura.log`, `Tp8_03_susceptibilidad.log` | los tres scripts | Bitácoras |

No edite estos archivos a mano: si algo cambia, vuelva a correr el script.
