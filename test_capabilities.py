import asyncio
import websockets
import json
import sys

async def send_message(ws, content):
    print(f"\n[USER]: {content}")
    await ws.send(json.dumps({
        "type": "message",
        "content": content
    }))
    
    response_text = ""
    while True:
        try:
            response = await asyncio.wait_for(ws.recv(), timeout=30.0)
            data = json.loads(response)
            
            if data.get("type") == "message":
                chunk = data.get("content", "")
                response_text += chunk
                print(chunk, end="", flush=True)
                
                if data.get("is_final"):
                    print("\n[END MESSAGE]")
                    return response_text
            
            elif data.get("type") == "tool_call":
                print(f"\n[TOOL CALL]: {data.get('tool_name')} args={data.get('tool_args')}")
                # Simulate tool success if needed, but server executes it actually.
                # Just observing here.
                
            elif data.get("type") == "error":
                print(f"\n[ERROR]: {data.get('content')}")
                return None
                
        except asyncio.TimeoutError:
            print("\n[TIMEOUT] - Sem resposta em 30s")
            return response_text
        except Exception as e:
            print(f"\n[EXCEPTION]: {e}")
            return None

async def run_tests():
    uri = "ws://localhost:8000/ws"
    print(f"Combinando com JARVIS em {uri}...")
    
    try:
        async with websockets.connect(uri) as ws:
            print("=== TESTE 1: Conversa Complexa e Personalidade ===")
            await send_message(ws, "Explique o Paradoxo de Fermi usando uma analogia com futebol (e seja sincero sobre qual time é o melhor exemplo).")
            
            print("\n\n=== TESTE 2: Ação de Escrita (Verificar Duplicidade) ===")
            await send_message(ws, "Abra o Bloco de Notas e escreva 'Teste de Verificação JARVIS'.")
            
            print("\n\n=== TESTE 3: Pesquisa de Programa ===")
            await send_message(ws, "Encontre onde está instalado o 'calc' ou calculadora no sistema.")
            
    except Exception as e:
        print(f"Falha na conexão: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())
