@echo off
REM ETIQUETADO_28_10 (Claude, 28/10/2026): acuerdo entre interpretes del Tp4 y validacion del Tp10 con las etiquetas de dos interpretes. Con respaldo previo.
cd /d "%~dp0"
set "ACT="
for %%D in ("%USERPROFILE%\miniforge3" "%USERPROFILE%\miniconda3" "%USERPROFILE%\anaconda3" "%LOCALAPPDATA%\miniforge3" "%ProgramData%\miniforge3" "%ProgramData%\miniconda3" "%ProgramData%\anaconda3") do if not defined ACT if exist "%%~D\Scripts\activate.bat" set "ACT=%%~D\Scripts\activate.bat"
call "%ACT%" sar
set "LOG=%~dp0ETIQUETADO_28_10.log"
set "P=D:\CURSOS_CEREGEO_2026\02_Practica"
set "R=%P%\_respaldo_corridas_20261028"
echo INICIO %DATE% %TIME% > "%LOG%"
robocopy "%P%\Tp4_Validacion\05_Resultados\04_Tablas" "%R%\Tp4\05_Resultados_04_Tablas" /E /NFL /NDL /NJH /NP >> "%LOG%"
robocopy "%P%\Tp4_Validacion\05_Resultados\06_Control_calidad" "%R%\Tp4\05_Resultados_06_Control_calidad" /E /NFL /NDL /NJH /NP >> "%LOG%"
robocopy "%P%\Tp10_Impacto_urbano\05_Resultados\04_Tablas" "%R%\Tp10\05_Resultados_04_Tablas" /E /NFL /NDL /NJH /NP >> "%LOG%"
cd /d "%P%\Tp4_Validacion\03_Scripts"
echo === TP4_07 >> "%LOG%"
python -u Tp4_07_acuerdo_entre_interpretes.py --medir --nombre B_CONCORDIA_cobertura_control_20m >> "%LOG%" 2>&1
python -u Tp4_07_acuerdo_entre_interpretes.py --medir --nombre B_CONCORDIA_mapbiomas_2025_clases_curso_20m >> "%LOG%" 2>&1
echo === TP10 TP4_03 >> "%LOG%"
python -u Tp4_03_exactitud_y_area.py --nombre B_CONCORDIA_variante_optico --nombres_clase "1=urbano,2=no_urbano" >> "%LOG%" 2>&1
python -u Tp4_03_exactitud_y_area.py --nombre B_CONCORDIA_variante_C --nombres_clase "1=urbano,2=no_urbano" >> "%LOG%" 2>&1
python -u Tp4_03_exactitud_y_area.py --nombre B_CONCORDIA_variante_SAR_multibanda --nombres_clase "1=urbano,2=no_urbano" >> "%LOG%" 2>&1
python -u Tp4_03_exactitud_y_area.py --nombre B_CONCORDIA_variante_multisensor --nombres_clase "1=urbano,2=no_urbano" >> "%LOG%" 2>&1
python -u Tp4_03_exactitud_y_area.py --nombre B_CONCORDIA_variante_multisensor_con_S --nombres_clase "1=urbano,2=no_urbano" >> "%LOG%" 2>&1
echo === TP10 TP4_04 >> "%LOG%"
python -u Tp4_04_tabla_de_variantes.py --tp Tp10 --clase urbano --variante "Optico solo|Sentinel-2|B_CONCORDIA_variante_optico" --variante "SAR solo (C)|Sentinel-1|B_CONCORDIA_variante_C" --variante "SAR multibanda|C + L|B_CONCORDIA_variante_SAR_multibanda" --variante "Multisensor|C + L + optico|B_CONCORDIA_variante_multisensor" >> "%LOG%" 2>&1
echo === TP10_06 >> "%LOG%"
cd /d "%P%\Tp10_Impacto_urbano\03_Scripts"
python -u Tp10_06_dominio_huella_S.py >> "%LOG%" 2>&1
echo LISTO %DATE% %TIME% >> "%LOG%"
