@echo off
rem Corrida del docente del Tp1, pasos 4 (ASF), 5 (LiDAR) y 7 (matriz de convergencia),
rem para los seis sitios con la ventana y la fecha de evento de su practico.
rem El paso 3 (Planetary Computer) ya se corrio el 18/10/2026 con las mismas ventanas.
rem Uso, en el Miniforge Prompt con el entorno sar activado:
rem     D:\CURSOS_CEREGEO_2026\02_Practica\00_COMUN\09_Herramientas\Tp1_corrida_docente.bat
rem Si un sitio falla, sigue con el siguiente; cada script deja su bitacora en
rem Tp1_Convergencia\05_Resultados\06_Control_calidad.
cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp1_Convergencia\03_Scripts

echo.
echo ==================== B_CONCORDIA  (Tp6: pico de la crecida del Uruguay)
python Tp1_04_buscar_asf.py --sitio B_CONCORDIA --desde 2023-10-01 --hasta 2023-11-30
python Tp1_05_buscar_lidar.py --sitio B_CONCORDIA
python Tp1_07_matriz_convergencia.py --sitio B_CONCORDIA --evento 2023-11-04 --ventana 12

echo.
echo ==================== A1_DELTA_QUEMAS  (Tp5: optico posterior a las quemas)
python Tp1_04_buscar_asf.py --sitio A1_DELTA_QUEMAS --desde 2020-06-15 --hasta 2020-10-31
python Tp1_05_buscar_lidar.py --sitio A1_DELTA_QUEMAS
python Tp1_07_matriz_convergencia.py --sitio A1_DELTA_QUEMAS --evento 2020-10-13 --ventana 12

echo.
echo ==================== F_BOVRIL  (Tp8: NovaSAR-1 escena 47974)
python Tp1_04_buscar_asf.py --sitio F_BOVRIL --desde 2023-01-01 --hasta 2023-12-31
python Tp1_05_buscar_lidar.py --sitio F_BOVRIL
python Tp1_07_matriz_convergencia.py --sitio F_BOVRIL --evento 2023-09-14 --ventana 12

echo.
echo ==================== E1_DIAMANTE_BARRANCA  (Tp7: par InSAR COSMO-SkyMed 15 y 19/10/2018)
python Tp1_04_buscar_asf.py --sitio E1_DIAMANTE_BARRANCA --desde 2018-10-01 --hasta 2018-10-31
python Tp1_05_buscar_lidar.py --sitio E1_DIAMANTE_BARRANCA
python Tp1_07_matriz_convergencia.py --sitio E1_DIAMANTE_BARRANCA --evento 2018-10-15 --ventana 12

echo.
echo ==================== C_FEDERAL  (Tp9: NISAR banda L y BIOMASS)
python Tp1_04_buscar_asf.py --sitio C_FEDERAL --desde 2026-09-01 --hasta 2026-09-30
python Tp1_05_buscar_lidar.py --sitio C_FEDERAL
python Tp1_07_matriz_convergencia.py --sitio C_FEDERAL --evento 2026-09-17 --ventana 12

echo.
echo ==================== D_LAPAZ_VILLAGUAY  (Tp9: BIOMASS banda P)
python Tp1_04_buscar_asf.py --sitio D_LAPAZ_VILLAGUAY --desde 2026-09-01 --hasta 2026-09-30
python Tp1_05_buscar_lidar.py --sitio D_LAPAZ_VILLAGUAY
python Tp1_07_matriz_convergencia.py --sitio D_LAPAZ_VILLAGUAY --evento 2026-09-17 --ventana 12

echo.
echo ==================== Terminado
