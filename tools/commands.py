"""
Command execution tools
For running shell commands and scripts
"""

import subprocess
import os
import re
from core.tools import tool


# ============ SECURITY GUARDRAILS ============
# Commands that should NEVER be executed
COMMAND_BLACKLIST = [
    # Destructive file operations
    r"format\s+[a-z]:",         # format C:
    r"del\s+/[sfq]",            # del /s /f /q
    r"rm\s+-rf",                # rm -rf
    r"rmdir\s+/[sq]",           # rmdir /s /q
    r"rd\s+/[sq]",              # rd /s /q
    
    # System critical
    r"shutdown",                # shutdown
    r"restart",                 # restart
    r"reg\s+delete",            # reg delete
    r"bcdedit",                 # boot config
    r"diskpart",                # disk partitioning
    
    # Network dangerous
    r"netsh\s+.*reset",         # network reset
    r"arp\s+-d",                # clear ARP cache
    
    # PowerShell dangerous
    r"Remove-Item\s+.*-Recurse.*-Force",
    r"Stop-Computer",
    r"Restart-Computer",
]

# Directories where file operations are safe
SAFE_DIRECTORIES = [
    os.path.expanduser("~\\Desktop"),
    os.path.expanduser("~\\Documents"),
    os.path.expanduser("~\\Downloads"),
    os.path.dirname(os.path.dirname(__file__)),  # Project folder
]


def _is_command_safe(command: str) -> tuple[bool, str]:
    """Check if command is safe to execute."""
    command_lower = command.lower()
    
    for pattern in COMMAND_BLACKLIST:
        if re.search(pattern, command_lower, re.IGNORECASE):
            return False, f"Comando bloqueado por segurança: padrão '{pattern}' detectado."
    
    return True, ""


@tool(
    name="run_command",
    description="Executa um comando no terminal/shell. Use para comandos como 'dir', 'ipconfig', 'pip install', etc. Comandos destrutivos são bloqueados automaticamente.",
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Comando a executar"
            },
            "cwd": {
                "type": "string",
                "description": "Diretório de trabalho opcional para executar o comando"
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout em segundos (padrão: 60)"
            }
        },
        "required": ["command"]
    }
)
def run_command(command: str, cwd: str = None, timeout: int = 60) -> dict:
    """Execute a shell command with safety checks."""
    
    # Security check
    is_safe, reason = _is_command_safe(command)
    if not is_safe:
        return {
            "success": False,
            "blocked": True,
            "error": reason,
            "hint": "Use comandos mais seguros ou peça ao usuário para executar manualmente."
        }
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout
        )
        
        return {
            "success": result.returncode == 0,
            "command": command,
            "return_code": result.returncode,
            "stdout": result.stdout.strip() if result.stdout else "",
            "stderr": result.stderr.strip() if result.stderr else ""
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Comando expirou após {timeout} segundos"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="run_powershell",
    description="Executa um script PowerShell. Mais poderoso que cmd para automação Windows.",
    parameters={
        "type": "object",
        "properties": {
            "script": {
                "type": "string",
                "description": "Script PowerShell a executar"
            },
            "cwd": {
                "type": "string",
                "description": "Diretório de trabalho opcional"
            }
        },
        "required": ["script"]
    }
)
def run_powershell(script: str, cwd: str = None) -> dict:
    """Execute a PowerShell script."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=120
        )
        
        return {
            "success": result.returncode == 0,
            "script": script[:100] + "..." if len(script) > 100 else script,
            "return_code": result.returncode,
            "stdout": result.stdout.strip() if result.stdout else "",
            "stderr": result.stderr.strip() if result.stderr else ""
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Script expirou após 120 segundos"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="get_environment_variable",
    description="Retorna o valor de uma variável de ambiente.",
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Nome da variável de ambiente"
            }
        },
        "required": ["name"]
    }
)
def get_environment_variable(name: str) -> dict:
    """Get an environment variable value."""
    try:
        value = os.environ.get(name)
        if value is not None:
            return {
                "success": True,
                "name": name,
                "value": value
            }
        else:
            return {
                "success": True,
                "name": name,
                "value": None,
                "message": f"Variável '{name}' não definida"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="get_current_directory",
    description="Retorna o diretório de trabalho atual.",
    parameters={
        "type": "object",
        "properties": {}
    }
)
def get_current_directory() -> dict:
    """Get the current working directory."""
    try:
        cwd = os.getcwd()
        return {
            "success": True,
            "path": cwd
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="open_url",
    description="Abre uma URL no navegador padrão.",
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL a abrir (ex: https://google.com)"
            }
        },
        "required": ["url"]
    }
)
def open_url(url: str) -> dict:
    """Open a URL in the default browser."""
    try:
        import webbrowser
        webbrowser.open(url)
        return {
            "success": True,
            "action": f"URL aberta: {url}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="get_system_info",
    description="Retorna informações detalhadas do sistema (CPU, RAM, Disco, OS).",
    parameters={
        "type": "object",
        "properties": {}
    }
)
def get_system_info() -> dict:
    """Get system information."""
    import psutil
    import platform
    from datetime import datetime
    
    try:
        # Memory
        mem = psutil.virtual_memory()
        
        # Disk
        disk = psutil.disk_usage('/')
        
        # CPU
        cpu_freq = psutil.cpu_freq()
        
        return {
            "success": True,
            "system": {
                "os": f"{platform.system()} {platform.release()}",
                "hostname": platform.node(),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "freq": f"{cpu_freq.current:.0f}MHz" if cpu_freq else "N/A"
            },
            "memory": {
                "total": f"{mem.total / (1024**3):.1f} GB",
                "available": f"{mem.available / (1024**3):.1f} GB",
                "used": f"{mem.used / (1024**3):.1f} GB",
                "percent": f"{mem.percent}%"
            },
            "disk": {
                "total": f"{disk.total / (1024**3):.1f} GB",
                "free": f"{disk.free / (1024**3):.1f} GB",
                "percent": f"{disk.percent}%"
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
