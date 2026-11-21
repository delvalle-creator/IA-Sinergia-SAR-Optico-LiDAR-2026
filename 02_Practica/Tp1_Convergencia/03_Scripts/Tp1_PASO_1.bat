@echo off
chcp 65001 >nul
title Tp1 - Paso 1: los sitios a vector
set "ACT="
for %%D in ("%USERPROFILE%\miniforge3" "%LOCALAPPDATA%\miniforge3" "%ProgramData%\miniforge3") do if not defined ACT if exist "%%~D\Scripts\activate.bat" set "ACT=%%~D\Scripts\activate.bat"
echo.
echo   ^> conda activate sar
call "%ACT%" sar
echo   ^> cd /d D:\CURSOS_CEREGEO_2026\02_Practica\Tp1_Convergencia\03_Scripts
cd /d "D:\CURSOS_CEREGEO_2026\02_Practica\Tp1_Convergencia\03_Scripts"
echo   ^> python Tp1_01_sitios_a_vector.py
echo.
python -u Tp1_01_sitios_a_vector.py
echo.
echo   Fin del paso 1.
cmd /k
