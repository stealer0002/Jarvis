from tools.mouse_keyboard import open_and_type
import time

print("Iniciando teste de Foco Real com AppActivate...")
try:
    # Test text with special characters to verify clipboard
    text = "Teste Final: Ação e Reação! 123 @#$"
    
    print(f"Tentando abrir Notepad e digitar: '{text}'")
    result = open_and_type("notepad", text, wait_seconds=3)
    
    print("\nRESULTADO:")
    print(f"Sucesso: {result.get('success')}")
    print(f"Janela Focada: {result.get('window_focused')}")
    print(f"Texto Digitado (preview): {result.get('text_typed')}")
    
    if not result.get('success'):
        print(f"Erro: {result.get('error')}")

except Exception as e:
    print(f"CRASH NO TESTE: {e}")
