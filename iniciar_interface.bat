@echo off
cd /d "%~dp0"
where pyw >nul 2>&1
if %ERRORLEVEL%==0 (
    start "" pyw -3 launcher_gui.py
) else (
    start "" pythonw launcher_gui.py
)
