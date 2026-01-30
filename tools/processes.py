"""
Process management tools
Uses psutil and subprocess for process control
"""

import psutil
import subprocess
import os
from core.tools import tool
from tools.program_search import find_executable, search_program, get_start_menu_apps


@tool(
    name="open_program",
    description="Abre um programa ou aplicativo pelo nome ou caminho. Use para iniciar Chrome, Notepad, WhatsApp, Discord, etc.",
    parameters={
        "type": "object",
        "properties": {
            "program": {
                "type": "string",
                "description": "Nome ou caminho do programa. Exemplos: 'notepad', 'chrome', 'whatsapp', 'discord', 'spotify'"
            },
            "arguments": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Argumentos opcionais para passar ao programa"
            }
        },
        "required": ["program"]
    }
)
def open_program(program: str, arguments: list[str] = None) -> dict:
    """Open a program or application."""
    import time
    from tools.program_search import find_executable, search_program
    
    try:
        # Common program aliases for Windows (including Store apps)
        aliases = {
            # Desktop apps
            "chrome": "chrome",
            "google chrome": "chrome",
            "firefox": "firefox",
            "edge": "msedge",
            "notepad": "notepad",
            "bloco de notas": "notepad",
            "calculadora": "calc",
            "calculator": "calc",
            "calc": "calc",
            "explorer": "explorer",
            "explorador": "explorer",
            "cmd": "cmd",
            "terminal": "wt",  # Windows Terminal
            "powershell": "powershell",
            "code": "code",
            "vscode": "code",
            "visual studio code": "code",
            "word": "winword",
            "excel": "excel",
            "powerpoint": "powerpnt",
            "paint": "mspaint",
            "obs": "obs64",
            "obs studio": "obs64",
            "steam": "steam",
            "epic games": "EpicGamesLauncher",
            "7zip": "7zFM",
            "7-zip": "7zFM",
            "7 zip": "7zFM",
        }
        
        # Windows Store apps use special URI schemes
        store_apps = {
            "whatsapp": "whatsapp://",
            "telegram": "tg://",
            "discord": "discord://",
            "spotify": "spotify://",
            "netflix": "netflix://",
            "xbox": "xbox://",
            "microsoft store": "ms-windows-store://",
            "loja": "ms-windows-store://",
            "configurações": "ms-settings://",
            "configuracoes": "ms-settings://",
            "settings": "ms-settings://",
            "fotos": "ms-photos://",
            "photos": "ms-photos://",
            "email": "mailto:",
            "calendar": "outlookcal://",
            "calendario": "outlookcal://",
        }
        
        program_lower = program.lower().strip()
        
        # Check if it's a Windows Store app
        if program_lower in store_apps:
            uri = store_apps[program_lower]
            result = subprocess.run(
                ["cmd", "/c", "start", "", uri],
                capture_output=True,
                timeout=10
            )
            time.sleep(1)
            return {
                "success": True,
                "action": f"Aplicativo '{program}' aberto via URI",
                "type": "store_app"
            }
        
        # Check for alias first
        actual_program = aliases.get(program_lower, None)
        
        # If no alias, try smart search
        if not actual_program:
            # 1. First implementation: Search Start Menu Shortcuts (Most reliable)
            start_menu_apps = get_start_menu_apps()
            
            # Fuzzy match strategy
            best_match = None
            highest_score = 0
            
            for app in start_menu_apps:
                app_name = app['name'].lower()
                score = 0
                
                if program_lower == app_name:
                    score = 100
                elif program_lower in app_name:
                    score = 70
                elif app_name in program_lower:
                    score = 50
                    
                if score > highest_score:
                    highest_score = score
                    best_match = app['path']  # Use the .lnk path directly
            
            if best_match and highest_score >= 50:
                actual_program = best_match
            else:
                # 2. Fallback: Try to find the executable directly
                found_exe = find_executable(program)
                if found_exe:
                    actual_program = found_exe
                else:
                    # Search for similar programs
                    matches = search_program(program)
                    if matches:
                        # Try to find executable for best match
                        for match in matches:
                            found_exe = find_executable(match['name'])
                            if found_exe:
                                actual_program = found_exe
                                break
                        
                        if not actual_program:
                            # Return suggestions if can't find exact match
                            suggestions = [m['name'] for m in matches[:5]]
                            return {
                                "success": False,
                                "error": f"Não encontrei o executável de '{program}'",
                                "suggestions": suggestions,
                                "hint": f"Programas similares encontrados: {', '.join(suggestions)}"
                            }
        
        if not actual_program:
            actual_program = program
        
        cmd = [actual_program] if isinstance(actual_program, str) else actual_program
        if arguments:
            cmd = [cmd] if isinstance(cmd, str) else list(cmd)
            cmd.extend(arguments)
        
        # First try: direct execution
        try:
            process = subprocess.Popen(
                cmd if isinstance(cmd, list) else [cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(0.5)
            if process.poll() is None:
                return {
                    "success": True,
                    "action": f"Programa '{program}' aberto",
                    "pid": process.pid
                }
        except FileNotFoundError:
            pass  # Try shell execution
        
        # Second try: shell execution (for programs in PATH)
        try:
            result = subprocess.run(
                f'start "" "{actual_program}"',
                shell=True,
                capture_output=True,
                timeout=5
            )
            time.sleep(0.5)
            
            # Verify if the program started by checking running processes
            for proc in psutil.process_iter(['name']):
                try:
                    if actual_program.lower() in proc.info['name'].lower():
                        return {
                            "success": True,
                            "action": f"Programa '{program}' aberto",
                            "pid": proc.pid
                        }
                except:
                    continue
            
            # If we got here, program might have started but we can't confirm
            return {
                "success": True,
                "action": f"Comando para abrir '{program}' executado",
                "note": "Verifique se o programa abriu na tela"
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Timeout ao tentar abrir '{program}'"}
        except Exception as e:
            return {"success": False, "error": f"Não foi possível abrir '{program}': {str(e)}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="search_installed_programs",
    description="Pesquisa programas instalados no computador por nome. Use ANTES de abrir um programa se não souber o nome exato.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Nome ou parte do nome do programa a pesquisar"
            }
        },
        "required": ["query"]
    }
)
def search_installed_programs(query: str) -> dict:
    """Search for installed programs by name."""
    from tools.program_search import search_program, get_start_menu_apps
    
    try:
        # Search in registry
        matches = search_program(query)
        
        # Also search in Start Menu
        start_menu = get_start_menu_apps()
        query_lower = query.lower()
        for app in start_menu:
            if query_lower in app['name'].lower():
                # Check if not already in matches
                if not any(query_lower in m['name'].lower() for m in matches):
                    matches.append({
                        "name": app['name'],
                        "location": app['path'],
                        "score": 25
                    })
        
        if matches:
            return {
                "success": True,
                "count": len(matches),
                "programs": [{"name": m["name"], "location": m.get("location", "")} for m in matches[:10]],
                "hint": "Use o nome exato do programa encontrado para abri-lo"
            }
        else:
            return {
                "success": True,
                "count": 0,
                "programs": [],
                "message": f"Nenhum programa encontrado com '{query}'"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="close_program",
    description="Fecha um programa pelo nome. Use para fechar Chrome, Notepad, jogos, etc.",
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Nome do processo a fechar (ex: 'chrome', 'notepad', 'firefox')"
            },
            "force": {
                "type": "boolean",
                "description": "Se True, força o fechamento (kill). Se False, tenta fechar graciosamente."
            }
        },
        "required": ["name"]
    }
)
def close_program(name: str, force: bool = False) -> dict:
    """Close a program by name."""
    try:
        name_lower = name.lower()
        killed = []
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                if name_lower in proc_name:
                    if force:
                        proc.kill()
                    else:
                        proc.terminate()
                    killed.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if killed:
            return {
                "success": True,
                "action": f"Fechado {len(killed)} processo(s)",
                "processes": killed
            }
        else:
            return {
                "success": True,
                "found": False,
                "message": f"Nenhum processo '{name}' encontrado"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="list_processes",
    description="Lista os processos em execução no sistema. Pode filtrar por nome.",
    parameters={
        "type": "object",
        "properties": {
            "filter": {
                "type": "string",
                "description": "Filtro opcional para buscar processos por nome"
            },
            "limit": {
                "type": "integer",
                "description": "Número máximo de processos a retornar (padrão: 20)"
            }
        }
    }
)
def list_processes(filter: str = None, limit: int = 20) -> dict:
    """List running processes."""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                if filter and filter.lower() not in info['name'].lower():
                    continue
                processes.append({
                    "pid": info['pid'],
                    "name": info['name'],
                    "cpu": round(info['cpu_percent'] or 0, 1),
                    "memory": round(info['memory_percent'] or 0, 1)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by memory usage and limit
        processes.sort(key=lambda x: x['memory'], reverse=True)
        processes = processes[:limit]
        
        return {
            "success": True,
            "count": len(processes),
            "processes": processes
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="get_system_info",
    description="Retorna informações completas do sistema: CPU, GPU, memória, disco, sistema operacional.",
    parameters={
        "type": "object",
        "properties": {}
    }
)
def get_system_info() -> dict:
    """Get complete system hardware and resource information."""
    try:
        import platform
        import subprocess
        
        # Basic usage stats
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('C:\\')
        
        # Get CPU model name (registry has the best name)
        cpu_model = "Desconhecido"
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            cpu_model = winreg.QueryValueEx(key, "ProcessorNameString")[0]
            winreg.CloseKey(key)
        except:
            # Fallback to platform
            try:
                cpu_model = platform.processor()
            except:
                pass
        
        # Get GPU info - prioritize nvidia-smi for accurate VRAM on NVIDIA GPUs
        gpu_info = []
        nvidia_gpus = {}
        
        # Try nvidia-smi first (accurate VRAM for NVIDIA)
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    parts = line.split(', ')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        vram_mb = int(parts[1].strip())
                        vram_gb = round(vram_mb / 1024, 1)
                        nvidia_gpus[name] = vram_gb
                        gpu_info.append({
                            "name": name,
                            "vram_gb": vram_gb
                        })
        except:
            pass
        
        # Fallback to Win32_VideoController for non-NVIDIA or if nvidia-smi failed
        if not gpu_info:
            try:
                result = subprocess.run(
                    ["powershell", "-Command", "Get-CimInstance -ClassName Win32_VideoController | Select-Object Name, AdapterRAM | ConvertTo-Json"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    import json
                    gpu_data = json.loads(result.stdout)
                    if isinstance(gpu_data, dict):
                        gpu_data = [gpu_data]
                    for gpu in gpu_data:
                        name = gpu.get("Name", "Desconhecido")
                        # Skip virtual adapters
                        if "virtual" in name.lower() or "parsec" in name.lower():
                            continue
                        vram_gb = round(gpu.get("AdapterRAM", 0) / (1024**3), 1) if gpu.get("AdapterRAM") else "N/A"
                        gpu_info.append({
                            "name": name,
                            "vram_gb": vram_gb
                        })
            except:
                pass
        
        # Get OS info
        os_info = f"{platform.system()} {platform.release()}"
        try:
            os_version = platform.version()
            os_info += f" (Build {os_version})"
        except:
            pass
        
        return {
            "success": True,
            "os": os_info,
            "cpu": {
                "model": cpu_model.strip() if cpu_model else "Desconhecido",
                "cores_physical": psutil.cpu_count(logical=False),
                "cores_logical": psutil.cpu_count(logical=True),
                "usage_percent": cpu_percent
            },
            "gpu": gpu_info if gpu_info else [{"name": "Não detectado", "vram_gb": "N/A"}],
            "memory": {
                "total_gb": round(memory.total / (1024**3), 1),
                "used_gb": round(memory.used / (1024**3), 1),
                "available_gb": round(memory.available / (1024**3), 1),
                "usage_percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 1),
                "used_gb": round(disk.used / (1024**3), 1),
                "free_gb": round(disk.free / (1024**3), 1),
                "usage_percent": round(disk.percent, 1)
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="get_active_window",
    description="Retorna informações sobre a janela ativa no momento.",
    parameters={
        "type": "object",
        "properties": {}
    }
)
def get_active_window() -> dict:
    """Get information about the currently active window."""
    try:
        import ctypes
        from ctypes import wintypes
        
        user32 = ctypes.windll.user32
        
        # Get foreground window handle
        hwnd = user32.GetForegroundWindow()
        
        # Get window title
        length = user32.GetWindowTextLengthW(hwnd) + 1
        buffer = ctypes.create_unicode_buffer(length)
        user32.GetWindowTextW(hwnd, buffer, length)
        title = buffer.value
        
        # Get window class name
        class_buffer = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, class_buffer, 256)
        class_name = class_buffer.value
        
        # Get window rectangle
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        
        # Get process ID
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        # Get process name
        process_name = ""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['pid'] == pid.value:
                    process_name = proc.info['name']
                    break
        except:
            pass
        
        return {
            "success": True,
            "title": title,
            "class": class_name,
            "process": process_name,
            "pid": pid.value,
            "position": {
                "x": rect.left,
                "y": rect.top,
                "width": rect.right - rect.left,
                "height": rect.bottom - rect.top
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
