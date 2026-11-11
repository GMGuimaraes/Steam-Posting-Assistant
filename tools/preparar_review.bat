@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

echo ================================================
echo   STEAM REVIEW DRAFT HELPER - MANUAL WORKFLOW
echo ================================================
echo.
py -3 preparar_review.py
set RESULT=%ERRORLEVEL%
echo.
if not "%RESULT%"=="0" (
    echo The helper finished with error code: %RESULT%
) else (
    echo Queue paused or completed. See the messages above.
)
echo.
pause
exit /b %RESULT%
