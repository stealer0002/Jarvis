import asyncio
import websockets
import json

async def send_message(ws, content):
    print(f"\n[USER]: {content}")
    await ws.send(json.dumps({
        "type": "message",
        "content": content
    }))
    
    response_text = ""
    while True:
        try:
            response = await asyncio.wait_for(ws.recv(), timeout=180.0)
            data = json.loads(response)
            
            if data.get("type") == "message":
                chunk = data.get("content", "")
                response_text += chunk
                print(chunk, end="", flush=True)
                
                if data.get("is_final"):
                    print("\n[END MESSAGE]")
                    return response_text
            
            elif data.get("type") == "error":
                print(f"\n[ERROR]: {data.get('content')}")
                return None
                
        except asyncio.TimeoutError:
            print("\n[TIMEOUT] - Sem resposta em 60s")
            return response_text
        except Exception as e:
            print(f"\n[EXCEPTION]: {e}")
            return None

async def run_tests():
    uri = "ws://localhost:8000/ws"
    print(f"Conectando ao JARVIS em {uri}...")
    
    try:
        async with websockets.connect(uri) as ws:
            print("=== TESTE DE CONSTITUCIONALISMO ===")
            prompt = "Explique as principais diferenças entre o Constitucionalismo Liberal clássico e o Neoconstitucionalismo, focando no papel dos princípios versus regras. Dê sua opinião sincera sobre o ativismo judicial."
            
            await send_message(ws, prompt)
            
    except Exception as e:
        print(f"Falha na conexão: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())
