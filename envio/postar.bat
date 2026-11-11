@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
python postar_tudo.py manifesto.json
echo.
echo Fim. Detalhes em postar.log
pause
