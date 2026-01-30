from tools.apps import manage_apps
import sys

print("--- TESTE DE AUTONOMIA: Simulação de 'Agente Preguiçoso' ---")
print("CENÁRIO: O Agente tenta instalar '7zip' sem passar o ID (preguiça).")

# 1. Intentional bad call
result = manage_apps(action="install", query="7zip", package_id=None)

print(f"\nResultado da Chamada: Success={result['success']}")
if not result['success']:
    error_msg = result.get('error', '')
    print(f"Mensagem de Erro Recebida:\n'{error_msg}'")
    
    # 2. Verify if the error message contains the specific instruction
    expected_instruction = "O AGENTE DEVE USAR 'search' PRIMEIRO"
    if expected_instruction in error_msg:
        print("\n[VERIFICADO] A ferramenta retornou a INSTRUÇÃO CORRETA.")
        print("Isso força o modelo a perceber o erro e buscar o ID.")
    else:
        print("\n[FALHA] A mensagem de erro não é instrutiva o suficiente.")
else:
    print("\n[FALHA] A ferramenta tentou instalar sem ID! Isso causa alucinação.")

print("\n--- Fim do Teste ---")
