@echo off
title JARVIS - Cloudflare Tunnel
echo.
echo ========================================
echo   JARVIS - Acesso Remoto via Cloudflare
echo ========================================
echo.
echo Iniciando tunnel... Aguarde a URL aparecer!
echo.
echo A URL gerada pode ser acessada de QUALQUER lugar!
echo Compartilhe com cuidado - qualquer pessoa com a URL pode controlar seu PC.
echo.
echo Pressione Ctrl+C para parar o tunnel.
echo.
"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe" tunnel --url http://localhost:8000
pause
