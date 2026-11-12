@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

echo ================================================
echo   FILA DE REVIEWS - PREPARACAO MANUAL
echo ================================================
echo.
py -3 preparar_review.py
set RESULT=%ERRORLEVEL%
echo.
if not "%RESULT%"=="0" (
    echo O preparador terminou com erro. Codigo: %RESULT%
    echo.
    pause
)
exit /b %RESULT%