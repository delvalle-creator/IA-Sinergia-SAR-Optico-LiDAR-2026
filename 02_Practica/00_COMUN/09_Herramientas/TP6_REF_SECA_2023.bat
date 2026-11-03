@echo off
REM TP6_REF_SECA_2023 (Claude, 28/10/2026): Tp6_01 con referencia seca de 2023 (S1A orbita 68), con respaldo previo.
cd /d "%~dp0"
set "ACT="
for %%D in ("%USERPROFILE%\miniforge3" "%USERPROFILE%\miniconda3" "%USERPROFILE%\anaconda3" "%LOCALAPPDATA%\miniforge3" "%ProgramData%\miniforge3" "%ProgramData%\miniconda3" "%ProgramData%\anaconda3") do if not defined ACT if exist "%%~D\Scripts\activate.bat" set "ACT=%%~D\Scripts\activate.bat"
call "%ACT%" sar
set "LOG=%~dp0TP6_REF_SECA_2023.log"
set "P=D:\CURSOS_CEREGEO_2026\02_Practica"
set "R=%P%\_respaldo_corridas_20261028\Tp6"
echo INICIO %DATE% %TIME% > "%LOG%"
cd /d "%P%\Tp6_Inundaciones\03_Scripts"
python -u Tp6_01_serie_agua_C.py --pixel 20 --desde 2023-10-01 --hasta 2024-06-30 --fecha_umbral 2023-11-04 --umbral_vv -15 --referencia_seca 2023-05-20,2023-06-13,2023-07-07 >> "%LOG%" 2>&1
echo LISTO %DATE% %TIME% >> "%LOG%"
