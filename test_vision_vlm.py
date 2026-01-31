
import asyncio
from tools.vision import analyze_screen
from core.ollama_client import OllamaClient

async def test_vlm():
    print("🧪 Iniciando teste de Visão (Moondream)...")
    
    # 1. Check if model is available
    client = OllamaClient()
    models = await client.list_models()
    if "moondream:latest" not in models:
        print(f"⚠️ Aviso: 'moondream:latest' não encontrado na lista: {models}")
        # Assuming user pulled 'moondream' which maps to latest
    
    # 2. Test Analysis
    print("📸 Analisando a tela agora...")
    description = await analyze_screen("Descreva o que você vê nesta imagem.")
    
    print("\n📝 RESPOSTA DA IA:")
    print("-" * 50)
    print(description)
    print("-" * 50)
    
    if "Erro" in description and len(description) < 100:
        print("❌ TESTE FALHOU")
    else:
        print("✅ TESTE PASSOU (Resposta recebida)")

if __name__ == "__main__":
    asyncio.run(test_vlm())
