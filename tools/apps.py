"""
Software Management Tools
Uses Windows Package Manager (winget) to manage applications.
"""

import subprocess
import shutil
from core.tools import tool

def _check_winget():
    """Check if winget is available."""
    return shutil.which("winget") is not None

@tool(
    name="manage_apps",
    description="Gerencia softwares no Windows (Instalar, Desinstalar, Buscar). Use para pedidos como 'Instale o Chrome', 'Remova o VLC'.",
    parameters={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Ação a realizar",
                "enum": ["search", "install", "uninstall", "list", "upgrade"]
            },
            "query": {
                "type": "string",
                "description": "Nome do programa (para search/list)"
            },
            "package_id": {
                "type": "string",
                "description": "ID exato do pacote (obrigatório para install/uninstall). Ex: 'Mozilla.Firefox'"
            }
        },
        "required": ["action"]
    }
)
def manage_apps(action: str, query: str = None, package_id: str = None) -> dict:
    """Manage Windows applications using winget."""
    if not _check_winget():
        return {
            "success": False, 
            "error": "O comando 'winget' não foi encontrado. Verifique se o App Installer está instalado na Microsoft Store."
        }

    try:
        if action == "search":
            if not query:
                return {"success": False, "error": "Forneça um 'query' para pesquisar."}
            
            # winget search <query>
            cmd = ["winget", "search", query]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0 and "No package found" not in result.stdout:
                 return {"success": False, "error": result.stderr or result.stdout}

            return {
                "success": True,
                "action": "search",
                "output": result.stdout[:2000] # Truncate heavily to save tokens
            }

        elif action == "list":
            # winget list <query>
            cmd = ["winget", "list"]
            if query:
                cmd.append(query)
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return {
                "success": True,
                "action": "list",
                "output": result.stdout[:2000]
            }

        elif action == "install":
            if not package_id:
                return {"success": False, "error": "Erro: ID ausente. O AGENTE DEVE USAR 'search' PRIMEIRO para encontrar o 'package_id'. Não pergunte ao usuário, PESQUISE."}
            
            # winget install --id <id> -e --accept-...
            cmd = [
                "winget", "install", 
                "--id", package_id, 
                "-e", # Exact match
                "--accept-source-agreements", 
                "--accept-package-agreements",
                "--no-upgrade" # Don't update if installed (unless upgrade requested)
            ]
            
            # This can take time, so we increase timeout
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return {"success": True, "action": "install", "message": f"Pacote {package_id} instalado com sucesso!"}
            else:
                return {"success": False, "action": "install", "error": result.stdout + "\n" + result.stderr}

        elif action == "uninstall":
            if not package_id:
                return {"success": False, "error": "Erro: ID ausente. O AGENTE DEVE USAR 'search' PRIMEIRO para encontrar o 'package_id'. Não pergunte ao usuário, PESQUISE."}
                
            cmd = ["winget", "uninstall", "--id", package_id, "-e"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return {"success": True, "action": "uninstall", "message": f"Pacote {package_id} desinstalado."}
            else:
                return {"success": False, "action": "uninstall", "error": result.stdout + "\n" + result.stderr}
                
        elif action == "upgrade":
            cmd = ["winget", "upgrade"]
            if package_id:
                cmd.extend(["--id", package_id, "-e"])
            else:
                cmd.append("--all")
            
            cmd.extend(["--accept-source-agreements", "--accept-package-agreements"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                return {"success": True, "action": "upgrade", "output": result.stdout[-1000:]}
            else:
                return {"success": False, "action": "upgrade", "error": result.stdout + "\n" + result.stderr}

        return {"success": False, "error": f"Ação desconhecida: {action}"}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "O comando demorou muito para responder (Timeout)."}
    except Exception as e:
        return {"success": False, "error": str(e)}
