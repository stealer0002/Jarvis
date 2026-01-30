@echo off
title JARVIS - Servidor + Tunnel
echo.
echo ========================================
echo   JARVIS - Modo Acesso Remoto
echo ========================================
echo.

REM Inicia o servidor JARVIS em segundo plano
echo [1/2] Iniciando servidor JARVIS...
start "JARVIS Server" /min cmd /c "cd /d %~dp0 && venv\Scripts\python.exe main.py"

REM Aguarda o servidor iniciar
timeout /t 3 /nobreak > nul

REM Inicia o tunnel
echo [2/2] Iniciando Cloudflare Tunnel...
echo.
echo Aguarde a URL aparecer abaixo:
echo -----------------------------------------------
"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe" tunnel --url http://localhost:8000
