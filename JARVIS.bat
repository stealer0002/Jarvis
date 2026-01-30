@echo off
chcp 65001 >nul
title JARVIS - AI Desktop Agent
cd /d "%~dp0"
color 0A

:menu
cls
echo.
echo  ╔═══════════════════════════════════════════════════════╗
echo  ║                                                       ║
echo  ║       ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗        ║
echo  ║       ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝        ║
echo  ║       ██║███████║██████╔╝██║   ██║██║███████╗        ║
echo  ║  ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║        ║
echo  ║  ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║        ║
echo  ║   ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝        ║
echo  ║                                                       ║
echo  ║           Autonomous AI Desktop Agent                 ║
echo  ║                                                       ║
echo  ╚═══════════════════════════════════════════════════════╝
echo.
echo   Escolha o modo de inicializacao:
echo.
echo   [1] Local          - Acesso apenas neste PC (localhost:8000)
echo   [2] Rede Local     - Acesso de qualquer dispositivo na mesma rede
echo   [3] Acesso Remoto  - Criar tunnel publico (Cloudflare)
echo   [4] Verificar      - Testar se tudo esta funcionando
echo   [0] Sair
echo.
set /p choice="   Opcao: "

if "%choice%"=="1" goto local
if "%choice%"=="2" goto network
if "%choice%"=="3" goto remote
if "%choice%"=="4" goto check
if "%choice%"=="0" exit
goto menu

:check
cls
echo.
echo  [*] Verificando dependencias...
echo.

REM Check Python
echo  [1/4] Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo        [X] Python NAO ENCONTRADO!
    echo        Instale em: https://python.org
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo        [OK] Python %%i
)

REM Check venv
echo  [2/4] Ambiente Virtual...
if exist "venv\Scripts\python.exe" (
    echo        [OK] venv existe
) else (
    echo        [!] venv nao encontrado - sera criado na primeira execucao
)

REM Check Ollama
echo  [3/4] Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo        [X] Ollama NAO ESTA RODANDO!
    echo        Execute: ollama serve
) else (
    echo        [OK] Ollama ativo
)

REM Check Cloudflared
echo  [4/4] Cloudflare Tunnel...
if exist "%LOCALAPPDATA%\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe" (
    echo        [OK] cloudflared instalado
) else (
    echo        [!] cloudflared nao encontrado (opcional, para acesso remoto)
    echo        Instale com: winget install Cloudflare.cloudflared
)

echo.
echo  ========================================
pause
goto menu

:setup
REM Setup virtual environment and dependencies
if not exist "venv" (
    echo  [*] Criando ambiente virtual...
    python -m venv venv
)

echo  [*] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo  [*] Verificando dependencias...
pip install -r requirements.txt -q 2>nul

REM Check Ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [!] AVISO: Ollama nao esta rodando!
    echo  [!] Abrindo Ollama...
    start "" "ollama" serve
    timeout /t 3 /nobreak >nul
)
goto :eof

:local
cls
echo.
echo  ========================================
echo   JARVIS - Modo Local
echo  ========================================
echo.
call :setup
echo.
echo  [*] Iniciando servidor...
echo  [*] Acesse: http://localhost:8000
echo  [*] Abrindo navegador...
echo.
start "" "http://localhost:8000"
python main.py
pause
goto menu

:network
cls
echo.
echo  ========================================
echo   JARVIS - Modo Rede Local
echo  ========================================
echo.
call :setup

REM Get local IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "ip=%%a"
    goto :gotip
)
:gotip
set ip=%ip:~1%

echo.
echo  [*] Iniciando servidor...
echo.
echo  Acesse de qualquer dispositivo na mesma rede:
echo  -----------------------------------------------
echo   PC:      http://localhost:8000
echo   Mobile:  http://%ip%:8000
echo  -----------------------------------------------
echo.
echo  [*] Abrindo navegador...
start "" "http://localhost:8000"
python main.py
pause
goto menu

:remote
cls
echo.
echo  ========================================
echo   JARVIS - Modo Acesso Remoto
echo  ========================================
echo.

REM Check cloudflared
if not exist "%LOCALAPPDATA%\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe" (
    echo  [X] cloudflared nao encontrado!
    echo  [*] Instalando...
    winget install Cloudflare.cloudflared -h
)

call :setup

echo.
echo  [1/2] Iniciando servidor JARVIS...
start /min powershell -WindowStyle Hidden -Command "cd '%~dp0'; & '.\venv\Scripts\python.exe' main.py"

timeout /t 3 /nobreak >nul

echo  [2/2] Criando tunnel Cloudflare...
echo.
echo  Aguarde... Capturando URL do tunnel...
echo.

REM Create temp file for output
set "tempfile=%TEMP%\jarvis_tunnel.log"
set "cloudflared=%LOCALAPPDATA%\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe"

REM Start cloudflared hidden with PowerShell - only logs to file
start /min powershell -WindowStyle Hidden -Command "& '%cloudflared%' tunnel --url http://localhost:8000 2>&1 | Tee-Object -FilePath '%tempfile%'"

REM Wait for URL to appear in output (check every 2 seconds for 30 seconds max)
set "tunnel_url="
set /a attempts=0

:waitforurl
timeout /t 2 /nobreak >nul
set /a attempts+=1

REM Search for the tunnel URL in the temp file using PowerShell
for /f "tokens=*" %%a in ('powershell -Command "if (Test-Path '%tempfile%') { Select-String -Path '%tempfile%' -Pattern 'https://.*trycloudflare.com' -AllMatches | ForEach-Object { $_.Matches.Value } | Select-Object -First 1 }" 2^>nul') do (
    set "tunnel_url=%%a"
)

if not "%tunnel_url%"=="" goto :showurl
if %attempts% lss 15 goto waitforurl

REM Fallback: show raw output if URL not captured
echo  [!] Nao foi possivel capturar a URL automaticamente.
echo  [!] Verifique a janela do Cloudflare Tunnel.
goto :tunnelwait

:showurl
cls
echo.
echo  ╔═══════════════════════════════════════════════════════════════════╗
echo  ║                                                                   ║
echo  ║   ████████╗██╗   ██╗███╗   ██╗███╗   ██╗███████╗██╗              ║
echo  ║   ╚══██╔══╝██║   ██║████╗  ██║████╗  ██║██╔════╝██║              ║
echo  ║      ██║   ██║   ██║██╔██╗ ██║██╔██╗ ██║█████╗  ██║              ║
echo  ║      ██║   ██║   ██║██║╚██╗██║██║╚██╗██║██╔══╝  ██║              ║
echo  ║      ██║   ╚██████╔╝██║ ╚████║██║ ╚████║███████╗███████╗         ║
echo  ║      ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚══════╝         ║
echo  ║                                                                   ║
echo  ║                    ACESSO REMOTO ATIVO!                           ║
echo  ║                                                                   ║
echo  ╚═══════════════════════════════════════════════════════════════════╝
echo.
echo.
echo   ┌─────────────────────────────────────────────────────────────────┐
echo   │                                                                 │
echo   │   SEU LINK DO JARVIS:                                           │
echo   │                                                                 │
echo   │   %tunnel_url%
echo   │                                                                 │
echo   └─────────────────────────────────────────────────────────────────┘
echo.
echo.
echo   [!] ATENCAO: Qualquer pessoa com esse link pode controlar seu PC!
echo.
echo   [*] Abrindo navegador...
start "" "%tunnel_url%"
echo.
echo   Pressione qualquer tecla para ENCERRAR o tunnel e o servidor...
echo.

:tunnelwait
pause >nul

REM Cleanup - kill by process name (more reliable)
echo.
echo  [*] Encerrando processos...
del "%tempfile%" 2>nul

REM Kill cloudflared
taskkill /im cloudflared.exe /f >nul 2>&1

REM Kill Python processes that are running main.py (JARVIS server)
for /f "tokens=2" %%p in ('wmic process where "commandline like '%%main.py%%'" get processid 2^>nul ^| findstr /r "[0-9]"') do (
    taskkill /pid %%p /f >nul 2>&1
)

REM Fallback: kill by window title
taskkill /fi "WINDOWTITLE eq Cloudflare Tunnel*" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq JARVIS Server*" /f >nul 2>&1

echo  [*] Tunnel e servidor encerrados.
timeout /t 2 /nobreak >nul
goto menu
