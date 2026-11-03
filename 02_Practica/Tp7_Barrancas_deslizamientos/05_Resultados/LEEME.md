# 05_Resultados — qué va a aparecer aquí

Los scripts crean las subcarpetas al correr.

| Subcarpeta / archivo | Quién lo escribe | Qué es |
|---|---|---|
| `04_Tablas/E1_pares_S1.csv` | `Tp7_01_pares_insar_C.py` | Pares Sentinel-1 consecutivos con días, línea de base y aptitud |
| `04_Tablas/E1_coherencia_y_desplazamiento.csv` | `Tp7_02_coherencia_y_deformacion.py` | Coherencia y desplazamiento por banda en ladera y referencia (sinergia) |
| `02_Rasters/E1_deformacion_confirmada.tif` | `Tp7_02_coherencia_y_deformacion.py` | Banda 1 `deformacion_confirmada` (+1, −1, 0); banda 2 `bandas_que_votaron` (fusión de decisión estricta: sin dato donde falta alguna banda) |
| `04_Tablas/E1_fusion_por_zona.csv` | `Tp7_02` con `--zonas` | Fracción observable y confirmados por zona de la ladera |
| `05_Graficos/E1_histogramas_umbrales.png` | `Tp7_02` | Histogramas del desplazamiento y la coherencia con la línea de cada umbral |
| `04_Tablas/E1_volumenes.csv` | `Tp7_03_cicatriz_y_volumen.py` | Área, dZ medio, volumen, volumen detectable e incertidumbre, % sobre 2 desvíos con el signo esperado y con el contrario, sesgo, ruido y NMAD, por forma y en la escarpa de control |
| `02_Rasters/E1_dz_despues_menos_antes.tif` | `Tp7_03` | dZ = después − antes con el sesgo restado |
| `04_Tablas/E1_atl08_20m_cicatriz.csv`, `05_Graficos/E1_icesat2_20m_transectas.png` | `Tp7_04_icesat2_20m_cicatriz.py` | Puntos de ICESat-2 cada 20 m frente al IGN |
| `04_Tablas/E1_velocidad_por_franja.csv`, `02_Rasters/E1_susceptibilidad_fisuras_hipotetica.tif` | `Tp7_05` (ampliación) | Velocidad por franja y susceptibilidad hipotética |
| `04_Tablas/E1_embeddings_cambio.csv` | `Tp7_06` (ampliación) | Semejanza de embeddings 2018–2025 por zona |
| `06_Control_calidad/Tp7_01_pares.log` | `Tp7_01` | Bitácora: lo mismo que se imprimió |
| `06_Control_calidad/Tp7_02_deformacion.log` | `Tp7_02` | Bitácora |
| `06_Control_calidad/Tp7_03_volumen.log` | `Tp7_03` | Bitácora |
| `06_Control_calidad/Tp7_04_icesat2_20m.log`, `Tp7_05_velocidad.log`, `Tp7_06_embeddings.log` | `Tp7_04` a `Tp7_06` | Bitácoras |

No edite estos archivos a mano: si algo cambia, vuelva a correr el script.
