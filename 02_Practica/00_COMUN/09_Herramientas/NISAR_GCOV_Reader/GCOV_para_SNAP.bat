@echo off
REM ---------------------------------------------------------------
REM  NISAR GCOV -> producto que SNAP 14 abre sin tocar su lector L1
REM  Arrastra el archivo .h5 sobre este .bat, o ejecutalo y pega la ruta.
REM ---------------------------------------------------------------
setlocal

set "PLUGIN=%~dp0nisar_gcov_reader"

REM --- buscar el Python de QGIS/OSGeo4W (trae GDAL ya configurado) -----
set "PYQGIS="
for %%P in (
  "C:\OSGeo4W\bin\python-qgis-ltr.bat"
  "C:\OSGeo4W\bin\python-qgis.bat"
  "C:\Program Files\QGIS 3.44.11\bin\python-qgis-ltr.bat"
  "C:\Program Files\QGIS 3.44\bin\python-qgis-ltr.bat"
) do if exist %%P set "PYQGIS=%%P"

if "%PYQGIS%"=="" (
  echo No se encontro el Python de QGIS/OSGeo4W.
  echo Edita este .bat y agrega la ruta de python-qgis-ltr.bat
  pause
  exit /b 1
)

set "H5=%~1"
if "%H5%"=="" set /p H5=Ruta del archivo GCOV .h5:

echo.
echo Usando: %PYQGIS%
echo Archivo: %H5%
echo.

call %PYQGIS% "%PLUGIN%\nisar_gcov_cli.py" "%H5%" --db --dimap
echo.
echo Abri el archivo .dim resultante en SNAP con File ^> Open Product
pause
