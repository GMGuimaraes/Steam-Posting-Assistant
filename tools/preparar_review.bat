@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
py -3 preparar_review.py
echo.
echo Revise o rascunho e publique manualmente, se desejar.
pause
