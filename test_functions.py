import asyncio
import websockets
import json

async def test_jarvis():
    uri = 'ws://localhost:8000/ws'
    
    tests = [
        ("Info do Sistema", "quanto de RAM estou usando?"),
        ("Data e Hora", "que dia e hora sao agora?"),
        ("Pesquisa Web", "pesquise sobre python programming"),
        ("Screenshot", "tire um print da tela"),
    ]
    
    async with websockets.connect(uri) as ws:
        for name, prompt in tests:
            print(f"\n{'='*50}")
            print(f"TESTE: {name}")
            print(f"Prompt: {prompt}")
            print('='*50)
            
            await ws.send(json.dumps({'type': 'message', 'content': prompt}))
            
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=90)
                data = json.loads(response)
                content = data.get('content', str(data))
                print(f"Resposta:\n{content[:600]}")
                if len(content) > 600:
                    print("... [truncado]")
            except asyncio.TimeoutError:
                print("TIMEOUT - sem resposta em 90s")
            
            # Small delay between tests
            await asyncio.sleep(2)
    
    print("\n\n=== TESTES CONCLUIDOS ===")

if __name__ == "__main__":
    asyncio.run(test_jarvis())
