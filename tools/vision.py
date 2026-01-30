"""
Vision tools - OCR and screen text reading
Requires Tesseract-OCR installed on Windows
"""

from core.tools import tool
import pyautogui


@tool(
    name="read_screen_text",
    description="Lê texto visível na tela usando OCR. Útil para ler mensagens de erro, menus, ou qualquer texto na tela.",
    parameters={
        "type": "object",
        "properties": {
            "region": {
                "type": "object",
                "description": "Região da tela para ler (opcional). Se não especificado, lê a tela inteira.",
                "properties": {
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                    "width": {"type": "integer"},
                    "height": {"type": "integer"}
                }
            }
        }
    }
)
def read_screen_text(region: dict = None) -> dict:
    """Read text from screen using OCR."""
    try:
        import pytesseract
        
        # Try common Tesseract installation paths on Windows
        tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(__import__('os').getenv('USERNAME')),
        ]
        
        tesseract_found = False
        for path in tesseract_paths:
            if __import__('os').path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                tesseract_found = True
                break
        
        if not tesseract_found:
            return {
                "success": False, 
                "error": "Tesseract-OCR não encontrado. Instale via: winget install UB-Mannheim.TesseractOCR"
            }
        
        # Capture screenshot
        if region:
            screenshot = pyautogui.screenshot(region=(region['x'], region['y'], region['width'], region['height']))
        else:
            screenshot = pyautogui.screenshot()
        
        # Extract text
        text = pytesseract.image_to_string(screenshot, lang='por+eng')
        text = ' '.join(text.split())  # Normalize whitespace
        
        return {
            "success": True,
            "text": text[:3000] if len(text) > 3000 else text,
            "length": len(text)
        }
    except ImportError:
        return {"success": False, "error": "pytesseract não instalado. Use: pip install pytesseract"}
    except Exception as e:
        return {"success": False, "error": str(e)}
