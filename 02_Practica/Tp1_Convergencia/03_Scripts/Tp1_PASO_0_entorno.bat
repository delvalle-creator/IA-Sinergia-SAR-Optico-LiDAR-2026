@echo off
chcp 65001 >nul
title Tp1 - Paso 0: el entorno de trabajo
set "ACT="
for %%D in ("%USERPROFILE%\miniforge3" "%LOCALAPPDATA%\miniforge3" "%ProgramData%\miniforge3") do if not defined ACT if exist "%%~D\Scripts\activate.bat" set "ACT=%%~D\Scripts\activate.bat"
call "%ACT%"
echo.
echo   ^> conda env list
call conda env list
echo   ^> conda activate sar
call conda activate sar
echo   ^> cd /d D:\CURSOS_CEREGEO_2026\02_Practica\00_COMUN
cd /d "D:\CURSOS_CEREGEO_2026\02_Practica\00_COMUN"
echo   ^> python comprobar_entorno.py
echo.
python -u comprobar_entorno.py
echo.
echo   Fin del paso 0.
cmd /k
