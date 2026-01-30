"""
Screen capture and analysis tools
Uses pyautogui and PIL for screenshots
"""

import pyautogui
import base64
from io import BytesIO
from pathlib import Path
from datetime import datetime
from core.tools import tool

# Screenshots folder
SCREENSHOTS_DIR = Path(__file__).parent.parent / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)


@tool(
    name="screenshot",
    description="Captura uma screenshot da tela e salva como arquivo. Retorna o caminho do arquivo e dimensões.",
    parameters={
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Nome opcional do arquivo (sem extensão). Se não especificado, usa timestamp."
            },
            "region": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                    "width": {"type": "integer"},
                    "height": {"type": "integer"}
                },
                "description": "Região opcional para capturar (x, y, largura, altura). Se não especificado, captura a tela inteira."
            }
        }
    }
)
def screenshot(filename: str = None, region: dict = None) -> dict:
    """Capture a screenshot of the screen and save to file."""
    try:
        if region:
            img = pyautogui.screenshot(region=(
                region.get("x", 0),
                region.get("y", 0),
                region.get("width", 800),
                region.get("height", 600)
            ))
        else:
            img = pyautogui.screenshot()
        
        # Generate filename
        if not filename:
            filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S")
        
        filepath = SCREENSHOTS_DIR / f"{filename}.png"
        img.save(filepath, format="PNG")
        
        # Also generate base64 for potential use
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return {
            "success": True,
            "filepath": str(filepath.absolute()),
            "filename": f"{filename}.png",
            "width": img.width,
            "height": img.height,
            "message": f"Screenshot salva em {filepath.name}",
            "note_to_agent": f"IMPORTANTE: Na sua resposta final, VOCÊ DEVE DIZER EXATAMENTE: 'Screenshot salva em {filepath.name}' para que a imagem apareça no chat."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="get_screen_size",
    description="Retorna as dimensões da tela (largura e altura em pixels).",
    parameters={
        "type": "object",
        "properties": {}
    }
)
def get_screen_size() -> dict:
    """Get screen dimensions."""
    try:
        width, height = pyautogui.size()
        return {
            "success": True,
            "width": width,
            "height": height,
            "resolution": f"{width}x{height}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="locate_on_screen",
    description="Procura uma imagem na tela e retorna sua posição. Útil para encontrar botões ou ícones.",
    parameters={
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "Caminho para o arquivo de imagem a procurar"
            },
            "confidence": {
                "type": "number",
                "description": "Nível de confiança de 0 a 1 (padrão: 0.9). Valores menores são mais tolerantes."
            }
        },
        "required": ["image_path"]
    }
)
def locate_on_screen(image_path: str, confidence: float = 0.9) -> dict:
    """Locate an image on the screen."""
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            return {
                "success": True,
                "found": True,
                "x": center.x,
                "y": center.y,
                "width": location.width,
                "height": location.height
            }
        else:
            return {
                "success": True,
                "found": False,
                "message": "Imagem não encontrada na tela"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="get_pixel_color",
    description="Retorna a cor de um pixel específico da tela em RGB.",
    parameters={
        "type": "object",
        "properties": {
            "x": {
                "type": "integer",
                "description": "Coordenada X do pixel"
            },
            "y": {
                "type": "integer",
                "description": "Coordenada Y do pixel"
            }
        },
        "required": ["x", "y"]
    }
)
def get_pixel_color(x: int, y: int) -> dict:
    """Get the color of a pixel at a specific position."""
    try:
        img = pyautogui.screenshot(region=(x, y, 1, 1))
        r, g, b = img.getpixel((0, 0))
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        return {
            "success": True,
            "x": x,
            "y": y,
            "rgb": {"r": r, "g": g, "b": b},
            "hex": hex_color
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
