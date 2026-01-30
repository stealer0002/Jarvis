@echo off
title JARVIS - AI Assistant
cd /d "%~dp0"

echo.
echo =============================================
echo        JARVIS - AI Desktop Agent
echo =============================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [*] Criando ambiente virtual...
    python -m venv venv
)

REM Activate virtual environment
echo [*] Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Install dependencies if needed
echo [*] Verificando dependencias...
pip install -r requirements.txt -q

REM Check if Ollama is running
echo [*] Verificando Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [!] AVISO: Ollama nao parece estar rodando!
    echo [!] Inicie o Ollama antes de usar o JARVIS.
    echo [!] Execute: ollama serve
    echo.
)

REM Start the server
echo [*] Iniciando JARVIS...
echo.
python main.py

pause
