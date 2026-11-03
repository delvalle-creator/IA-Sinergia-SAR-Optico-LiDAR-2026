@echo off
REM Productos que la auditoria del 20/10/2026 encontro faltantes (Tp1, Tp2, Tp5, Tp10)
cd /d "%~dp0"
set "ACT="
for %%D in ("%USERPROFILE%\miniforge3" "%USERPROFILE%\miniconda3" "%USERPROFILE%\anaconda3" "%LOCALAPPDATA%\miniforge3" "%ProgramData%\miniforge3" "%ProgramData%\miniconda3" "%ProgramData%\anaconda3") do if not defined ACT if exist "%%~D\Scripts\activate.bat" set "ACT=%%~D\Scripts\activate.bat"
if not defined ACT (
  echo No encontre conda. Abra el Miniforge Prompt, escriba: conda activate sar
  echo y despues: python "%~dp0correcciones_auditoria_datos.py"
  pause
  exit /b 1
)
call "%ACT%" sar
python correcciones_auditoria_datos.py
pause
