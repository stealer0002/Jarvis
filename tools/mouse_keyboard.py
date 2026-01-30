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
def open_and_type(program: str, text: str, wait_seconds: float = 2, press_enter: bool = False) -> dict:
    """Open a program, wait for it to load, focus it, and type text into it."""
    try:
        import subprocess
        import time
        import ctypes
        from ctypes import wintypes
        
        # Import open_program logic
        from tools.processes import open_program as _open_program
        
        # Open the program
        result = _open_program(program)
        if not result.get("success"):
            return result
        
        # Wait for program to open
        time.sleep(wait_seconds)
        
        # Try to focus the window by searching for it
        program_lower = program.lower()
        
        # Map common program names to window title patterns
        # More specific window patterns - avoid conflicts
        window_patterns = {
            "notepad": ["Bloco de Notas", "Notepad", "Sem título - Bloco"],
            "chrome": ["- Google Chrome"],  # More specific to avoid "Comet" conflicts
            "firefox": ["Mozilla Firefox", "— Mozilla Firefox"],
            "edge": ["- Microsoft Edge", "Microsoft Edge"],
            "word": ["- Word", "- Microsoft Word"],
            "excel": ["- Excel", "- Microsoft Excel"],
            "vscode": ["- Visual Studio Code"],
            "discord": ["- Discord"],
            "spotify": ["Spotify"],
            "whatsapp": ["WhatsApp"],
            "telegram": ["Telegram"],
            "comet": ["Comet"],
        }
        
        # Get matching patterns for this program
        patterns = window_patterns.get(program_lower, [program])
        
        # Use Windows API to find and focus window
        user32 = ctypes.windll.user32
        
        # Get PID from the open_program result if available
        target_pid = result.get("pid")
        
        # EnumWindows callback to find matching window
        found_hwnd = None
        best_hwnd = None
        
        def get_window_pid(hwnd):
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            return pid.value
        
        def enum_callback(hwnd, lparam):
            nonlocal found_hwnd, best_hwnd
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd) + 1
                buffer = ctypes.create_unicode_buffer(length)
                user32.GetWindowTextW(hwnd, buffer, length)
                title = buffer.value
                title_lower = title.lower()
                
                # First priority: match by PID
                if target_pid:
                    window_pid = get_window_pid(hwnd)
                    if window_pid == target_pid:
                        found_hwnd = hwnd
                        return False  # Stop enumeration
                
                # Second priority: match by title pattern
                for pattern in patterns:
                    if pattern.lower() in title_lower:
                        best_hwnd = hwnd
                        # Don't stop - keep looking for exact PID match
                
            return True
        
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        
        # Retry loop to find window (max 15 attempts / ~7.5 seconds)
        for _ in range(15):
            try:
                found_hwnd = None
                best_hwnd = None
                user32.EnumWindows(EnumWindowsProc(enum_callback), 0)
                
                if not found_hwnd:
                    found_hwnd = best_hwnd
                
                if found_hwnd:
                    break
            except:
                pass
                
            time.sleep(0.5)
        
        # Use PID match if found, otherwise use title match
        if not found_hwnd:
            found_hwnd = best_hwnd
        
        # Force window activation with AttachThreadInput trick
        def force_focus_window(hwnd):
            """More aggressive window activation that bypasses Windows focus stealing prevention."""
            try:
                # Get foreground window's thread
                foreground = user32.GetForegroundWindow()
                foreground_thread = user32.GetWindowThreadProcessId(foreground, None)
                target_thread = user32.GetWindowThreadProcessId(hwnd, None)
                
                # Attach threads to allow focus change
                if foreground_thread != target_thread:
                    user32.AttachThreadInput(foreground_thread, target_thread, True)
                
                # Show and activate window
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                user32.BringWindowToTop(hwnd)
                user32.SetForegroundWindow(hwnd)
                user32.SetFocus(hwnd)
                
                # Detach threads
                if foreground_thread != target_thread:
                    user32.AttachThreadInput(foreground_thread, target_thread, False)
                
                return True
            except:
                return False
        
        if found_hwnd:
            force_focus_window(found_hwnd)
            time.sleep(0.5)  # Longer wait for focus
        else:
            # Fallback: use Alt+Tab to switch to last window
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.5)
        
        # Special handling for browsers - need to focus address bar or open new tab
        is_browser = program_lower in ["chrome", "firefox", "edge", "brave", "opera"]
        
        if is_browser:
            # Open new tab and focus address bar
            pyautogui.hotkey('ctrl', 't')  # New tab
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'l')  # Focus address bar
            time.sleep(0.2)
        
        # Type text using clipboard method (best for special chars)
        subprocess.run(
            ["powershell", "-Command", f"Set-Clipboard -Value '{text.replace(chr(39), chr(39)+chr(39))}'"],
            capture_output=True,
            timeout=5
        )
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')
        
        # For browsers, always press Enter to navigate
        if is_browser or press_enter:
            time.sleep(0.1)
            pyautogui.press('enter')
        
        preview = text[:50] + "..." if len(text) > 50 else text
        return {
            "success": True,
            "program": program,
            "text_typed": preview,
            "enter_pressed": is_browser or press_enter,
            "window_focused": found_hwnd is not None
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
