@echo off
chcp 65001 >nul
title Tp1 - Paso 2: inventario local
set "ACT="
for %%D in ("%USERPROFILE%\miniforge3" "%LOCALAPPDATA%\miniforge3" "%ProgramData%\miniforge3") do if not defined ACT if exist "%%~D\Scripts\activate.bat" set "ACT=%%~D\Scripts\activate.bat"
set "T=D:\CURSOS_CEREGEO_2026\02_Practica\Tp1_Convergencia"
if not exist "D:\CURSOS_CEREGEO_2026\_to_delete\respaldo_Tp1_20261116" mkdir "D:\CURSOS_CEREGEO_2026\_to_delete\respaldo_Tp1_20261116"
copy /y "%T%\05_Resultados\04_Tablas\inventario_local.csv" "D:\CURSOS_CEREGEO_2026\_to_delete\respaldo_Tp1_20261116\" >nul
echo.
echo   ^> conda activate sar
call "%ACT%" sar
echo   ^> cd /d %T%\03_Scripts
cd /d "%T%\03_Scripts"
echo   ^> dir /b
dir /b *.py *.md
echo.
echo   ^> python Tp1_02_inventario_local.py
echo.
python -u Tp1_02_inventario_local.py
echo.
echo   Fin del paso 2.
cmd /k
