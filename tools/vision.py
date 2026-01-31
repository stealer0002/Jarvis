from core.tools import tool
import pyautogui
import io
import base64
import os
import pytesseract
from core.ollama_client import OllamaClient


@tool(
    name="read_screen_text",
    description="Lê TODO o texto visível na tela usando OCR. Use quando precisar ler menus, erros ou conteúdo de janelas.",
    parameters={
        "type": "object",
        "properties": {
            "region": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Região opcional [left, top, width, height]. Se omitido, lê a tela inteira."
            }
        }
    }
)
def read_screen_text(region: list[int] = None) -> str:
    """Reads visible text from the screen using OCR."""
    try:
        # Check for Tesseract in common paths
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\stealer0002\AppData\Local\Tesseract-OCR\tesseract.exe"
        ]
        
        tesseract_cmd = None
        for path in tesseract_paths:
            if os.path.exists(path):
                tesseract_cmd = path
                break
        
        if not tesseract_cmd:
            return "Erro: Tesseract OCR não encontrado. Instale-o para usar este recurso."
            
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        # Capture screenshot
        screenshot = pyautogui.screenshot(region=tuple(region) if region else None)
        
        # Read text
        text = pytesseract.image_to_string(screenshot)
        
        if not text.strip():
            return "Nenhum texto detectado na tela."
            
        return text.strip()
    except Exception as e:
        return f"Erro ao ler tela: {str(e)}"


@tool(
    name="analyze_screen",
    description="Usa Visão Computacional (IA) para descrever o que está na tela. Útil para entender layouts, identificar ícones, cores ou erros que o OCR não pega.",
    parameters={
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "O que você quer saber sobre a tela? Ex: 'Descreva a janela de erro', 'Onde está o botão de login?'"
            }
        },
        "required": ["question"]
    }
)
async def analyze_screen(question: str) -> str:
    """Analyzes the screen using a local Vision Language Model (Moondream)."""
    try:
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        
        # Convert to base64
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Query Ollama (Moondream)
        client = OllamaClient()
        
        # Create a prompt specifically for the VLM
        messages = [
            {"role": "user", "content": question}
        ]
        
        # Use the modified chat method with image support
        # We assume 'moondream' is installed as per plan
        response = await client.chat(
            messages=messages,
            images=[img_str],
            model="moondream" 
        )
        
        if "message" in response:
            return response["message"]["content"]
        elif "error" in response:
            return f"Erro na IA Visual: {response['error']}"
        else:
            return "Erro desconhecido ao analisar a imagem."
            
    except Exception as e:
        return f"Erro ao analisar tela: {str(e)}"
