@echo off
chcp 65001 >nul
title Tp1 - Paso 6
set "ACT="
for %%D in ("%USERPROFILE%\miniforge3" "%LOCALAPPDATA%\miniforge3") do if not defined ACT if exist "%%~D\Scripts\activate.bat" set "ACT=%%~D\Scripts\activate.bat"
set "T=D:\CURSOS_CEREGEO_2026\02_Practica\Tp1_Convergencia"
set "R=D:\CURSOS_CEREGEO_2026\_to_delete\respaldo_Tp1_20261116\paso_6"
if not exist "%R%" mkdir "%R%"
robocopy "%T%\05_Resultados\04_Tablas" "%R%" *B_CONCORDIA* /NFL /NDL /NJH /NJS /NP >nul
call "%ACT%" sar
cd /d "%T%\03_Scripts"
echo.
echo   ^> python -u Tp1_06_escenas_por_pedido.py --sitio B_CONCORDIA --desde 2025-11-01
echo.
python -u Tp1_06_escenas_por_pedido.py --sitio B_CONCORDIA --desde 2025-11-01
echo.
echo   Fin del paso 6.
cmd /k
