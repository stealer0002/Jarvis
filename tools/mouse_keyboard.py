"""
Mouse and Keyboard automation tools
Uses pyautogui for cross-platform support
"""

import pyautogui
from core.tools import tool

# Safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1  # Small delay between actions


@tool(
    name="mouse_click",
    description="Clica em uma posição específica da tela com movimento humano.",
    parameters={
        "type": "object",
        "properties": {
            "x": {
                "type": "integer",
                "description": "Coordenada X (horizontal) do clique"
            },
            "y": {
                "type": "integer",
                "description": "Coordenada Y (vertical) do clique"
            },
            "button": {
                "type": "string",
                "enum": ["left", "right", "middle"],
                "description": "Botão do mouse a usar (padrão: left)"
            },
            "clicks": {
                "type": "integer",
                "description": "Número de cliques (padrão: 1, use 2 para duplo clique)"
            }
        },
        "required": ["x", "y"]
    }
)
def mouse_click(x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
    """Click at a specific screen position with human-like movement."""
    try:
        import random
        import time
        
        # Move to position first with human-like movement
        curr_x, curr_y = pyautogui.position()
        dist = ((curr_x - x)**2 + (curr_y - y)**2)**0.5
        duration = max(0.15, min(dist / 800, 1.0)) + random.uniform(-0.05, 0.05)
        
        pyautogui.moveTo(x=x, y=y, duration=duration, tween=pyautogui.easeOutQuad)
        time.sleep(random.uniform(0.03, 0.1))  # Small pause before click
        
        pyautogui.click(x=x, y=y, button=button, clicks=clicks, interval=random.uniform(0.08, 0.15))
        return {
            "success": True,
            "action": f"Clique {button} em ({x}, {y})",
            "clicks": clicks
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="mouse_move",
    description="Move o cursor do mouse de forma natural (com aceleração e desaceleração).",
    parameters={
        "type": "object",
        "properties": {
            "x": {
                "type": "integer",
                "description": "Coordenada X de destino"
            },
            "y": {
                "type": "integer",
                "description": "Coordenada Y de destino"
            },
            "duration": {
                "type": "number",
                "description": "Duração do movimento. Se 0, calcula automaticamente baseado na distância."
            }
        },
        "required": ["x", "y"]
    }
)
def mouse_move(x: int, y: int, duration: float = 0) -> dict:
    """Move mouse with human-like easing."""
    try:
        import random
        
        # Calculate duration based on distance if not specified
        if duration == 0:
            curr_x, curr_y = pyautogui.position()
            dist = ((curr_x - x)**2 + (curr_y - y)**2)**0.5
            duration = max(0.15, min(dist / 800, 1.2))
            duration += random.uniform(-0.05, 0.05)
        
        # Use easeOutQuad for natural deceleration
        pyautogui.moveTo(x=x, y=y, duration=duration, tween=pyautogui.easeOutQuad)
        return {
            "success": True,
            "action": f"Mouse movido para ({x}, {y})"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="mouse_scroll",
    description="Rola a roda do mouse para cima ou para baixo.",
    parameters={
        "type": "object",
        "properties": {
            "amount": {
                "type": "integer",
                "description": "Quantidade de rolagem. Positivo = para cima, Negativo = para baixo"
            },
            "x": {
                "type": "integer",
                "description": "Coordenada X opcional para posicionar antes de rolar"
            },
            "y": {
                "type": "integer",
                "description": "Coordenada Y opcional para posicionar antes de rolar"
            }
        },
        "required": ["amount"]
    }
)
def mouse_scroll(amount: int, x: int = None, y: int = None) -> dict:
    """Scroll the mouse wheel."""
    try:
        pyautogui.scroll(amount, x=x, y=y)
        direction = "cima" if amount > 0 else "baixo"
        return {
            "success": True,
            "action": f"Scroll para {direction} ({abs(amount)} unidades)"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="type_into_application",
    description="Digita texto em um aplicativo externo (Notepad, Word, Browser). Suporta acentos e caracteres especiais. NÃO use para responder ao usuário no chat.",
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Texto a ser digitado no programa"
            },
            "use_clipboard": {
                "type": "boolean",
                "description": "Se True, usa clipboard (melhor para acentos). Padrão: True"
            }
        },
        "required": ["text"]
    }
)
def type_into_application(text: str, use_clipboard: bool = True) -> dict:
    """Type text using keyboard or clipboard (for special characters)."""
    try:
        import time
        
        if use_clipboard:
            # Use clipboard for better special character support
            import subprocess
            
            # Copy text to clipboard using PowerShell
            subprocess.run(
                ["powershell", "-Command", f"Set-Clipboard -Value '{text.replace(chr(39), chr(39)+chr(39))}'"],
                capture_output=True,
                timeout=5
            )
            
            # Small delay to ensure clipboard is set
            time.sleep(0.1)
            
            # Paste with Ctrl+V
            pyautogui.hotkey('ctrl', 'v')
        else:
            # Use direct typing (may fail with special characters)
            pyautogui.write(text, interval=0.02)
        
        preview = text[:50] + "..." if len(text) > 50 else text
        return {
            "success": True,
            "action": f"Digitado: '{preview}'",
            "length": len(text)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="open_and_type",
    description="Abre um programa e digita texto nele. Exemplo: abrir Notepad e escrever uma nota, abrir Chrome e pesquisar algo.",
    parameters={
        "type": "object",
        "properties": {
            "program": {
                "type": "string",
                "description": "Nome do programa a abrir (notepad, chrome, word, etc.)"
            },
            "text": {
                "type": "string",
                "description": "Texto a ser digitado após abrir o programa"
            },
            "wait_seconds": {
                "type": "number",
                "description": "Segundos para esperar o programa abrir. Padrão: 2"
            },
            "press_enter": {
                "type": "boolean",
                "description": "Se True, pressiona Enter após digitar. Útil para pesquisas."
            }
        },
        "required": ["program", "text"]
    }
)
@tool(
    name="open_and_type",
    description="Abre um programa, espera carregar, foca a janela e digita texto. Ideal para navegadores e pesquisas.",
    parameters={
        "type": "object",
        "properties": {
            "program": {
                "type": "string",
                "description": "Nome do programa a abrir (notepad, chrome, word, etc.)"
            },
            "text": {
                "type": "string",
                "description": "Texto a ser digitado após abrir o programa"
            },
            "wait_seconds": {
                "type": "number",
                "description": "Segundos para esperar o programa abrir. Padrão: 2"
            },
            "press_enter": {
                "type": "boolean",
                "description": "Se True, pressiona Enter após digitar. Útil para pesquisas."
            }
        },
        "required": ["program", "text"]
    }
)
def open_and_type(program: str, text: str, wait_seconds: float = 2, press_enter: bool = False) -> dict:
    """Abre (ou foca se já aberto) um programa e digita texto. Usa PID real para foco."""
    try:
        import subprocess
        import time
        import pyperclip
        import pyautogui
        
        # Import open_program logic
        from tools.processes import open_program as _open_program
        from tools.program_search import find_executable
        
        program_lower = program.lower()
        is_browser = program_lower in ["chrome", "firefox", "edge", "brave", "opera", "browser", "navegador"]
        
        # Helper to activate window via PowerShell (Robust for UWP/W11)
        # Matches by PID (int) or Title (str)
        def activate_window(start_input):
            cmd_arg = str(start_input)
            if isinstance(start_input, str):
                escaped = start_input.replace("'", "''")
                cmd_arg = f"'{escaped}'"
            
            cmd = f"(New-Object -ComObject WScript.Shell).AppActivate({cmd_arg})"
            try:
                res = subprocess.run(
                    ["powershell", "-c", cmd], 
                    capture_output=True, 
                    text=True,
                    check=False
                )
                return "True" in (res.stdout or "")
            except Exception:
                return False

        # Helper to get REAL PID of a process name (Handles Shim Launchers)
        # Returns the PID of the most recently started instance
        def get_real_pid(proc_name):
            try:
                cmd = f"Get-Process -Name {proc_name} -ErrorAction SilentlyContinue | Sort-Object StartTime -Descending | Select-Object -First 1 -ExpandProperty Id"
                res = subprocess.run(
                    ["powershell", "-c", cmd],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if res.stdout and res.stdout.strip().isdigit():
                    return int(res.stdout.strip())
            except Exception:
                pass
            return None

        # Map common aliases to actual Process Names for PID lookup
        process_names = {
            "notepad": "notepad",
            "bloco de notas": "notepad",
            "chrome": "chrome",
            "google chrome": "chrome",
            "firefox": "firefox",
            "edge": "msedge",
            "word": "winword",
            "excel": "excel",
            "calculator": "calc",
            "calc": "calc",
            "whatsapp": "whatsapp",
            "spotify": "spotify",
            "telegram": "telegram",
            "discord": "discord",
        }
        
        # Determine process name
        proc_name = process_names.get(program_lower)
        if not proc_name:
            # Try to guess or use program name
             proc_name = program_lower.replace(" ", "")

        # 1. Check if already running (Prevent Double Launch)
        # But we need to activate it to be sure.
        target_pid = get_real_pid(proc_name)
        already_open = False
        
        if target_pid:
            print(f"DEBUG: Found running process {proc_name} (PID {target_pid}). Activating...")
            if activate_window(target_pid):
                already_open = True
        
        # 2. Launch if not found
        if not already_open:
            print(f"DEBUG: Not found or failed to focus. Launching {program}...")
            result = _open_program(program)
            if not result.get("success"):
                return result
            
            # Wait for load (Shim exits, real app starts)
            time.sleep(wait_seconds)
            
            # 3. Find NEW PID
            # The launch result PID might be the shim (dead).
            # We scan for the newest instance again.
            target_pid = get_real_pid(proc_name)
            
            if target_pid:
                print(f"DEBUG: New process found (PID {target_pid}). Activating...")
                activate_window(target_pid)
                time.sleep(0.5)
            else:
                # Fallback: Try Title Patterns if PID lookup failed
                pass # Already handled by AppActivate in 'else' logic below? 
                # Actually, AppActivate accepts strings too.
        
        # 4. Browser Setup
        if is_browser:
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 't')
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.2)

        # 5. Type
        try:
            pyperclip.copy(text)
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.1)
        except Exception:
            pyautogui.write(text)

        # 6. Enter
        if is_browser or press_enter:
            time.sleep(0.2)
            pyautogui.press('enter')

        return {
            "success": True, 
            "program": program, 
            "text_typed": text[:50],
            "window_focused": target_pid is not None
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="press_key",
    description="Pressiona uma tecla específica. Use para Enter, Tab, Escape, setas, F1-F12, etc.",
    parameters={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Nome da tecla: enter, tab, escape, space, backspace, delete, up, down, left, right, f1-f12, etc."
            },
            "presses": {
                "type": "integer",
                "description": "Número de vezes para pressionar (padrão: 1)"
            }
        },
        "required": ["key"]
    }
)
def press_key(key: str, presses: int = 1) -> dict:
    """Press a specific key."""
    try:
        pyautogui.press(key, presses=presses)
        return {
            "success": True,
            "action": f"Tecla '{key}' pressionada {presses}x"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="hotkey",
    description="Pressiona uma combinação de teclas (atalho). Use para Ctrl+C, Alt+Tab, Ctrl+S, etc.",
    parameters={
        "type": "object",
        "properties": {
            "keys": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista de teclas para pressionar juntas. Ex: ['ctrl', 'c'] para Ctrl+C"
            }
        },
        "required": ["keys"]
    }
)
def hotkey(keys: list[str]) -> dict:
    """Press a key combination (hotkey)."""
    try:
        pyautogui.hotkey(*keys)
        combo = "+".join(keys)
        return {
            "success": True,
            "action": f"Atalho '{combo}' executado"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="mouse_drag",
    description="Arrasta o mouse de uma posição para outra. Use para mover janelas, selecionar texto, etc.",
    parameters={
        "type": "object",
        "properties": {
            "start_x": {
                "type": "integer",
                "description": "Coordenada X inicial"
            },
            "start_y": {
                "type": "integer",
                "description": "Coordenada Y inicial"
            },
            "end_x": {
                "type": "integer",
                "description": "Coordenada X final"
            },
            "end_y": {
                "type": "integer",
                "description": "Coordenada Y final"
            },
            "duration": {
                "type": "number",
                "description": "Duração do arrasto em segundos (padrão: 0.5)"
            }
        },
        "required": ["start_x", "start_y", "end_x", "end_y"]
    }
)
def mouse_drag(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> dict:
    """Drag the mouse from one position to another."""
    try:
        pyautogui.moveTo(start_x, start_y)
        pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
        return {
            "success": True,
            "action": f"Arrastado de ({start_x},{start_y}) para ({end_x},{end_y})"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="get_mouse_position",
    description="Retorna a posição atual do cursor do mouse.",
    parameters={
        "type": "object",
        "properties": {}
    }
)
def get_mouse_position() -> dict:
    """Get current mouse cursor position."""
    try:
        x, y = pyautogui.position()
        return {
            "success": True,
            "x": x,
            "y": y,
            "position": f"({x}, {y})"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
