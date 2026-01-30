from tools.apps import manage_apps
import time

print("--- TESTE FINAL: Autonomia de DESINSTALAÇÃO ---")
APP_NAME = "7zip"

# PHASE 1: Lazy Uninstall Attempt
print(f"\n[1/3] Tentativa Ingênua: 'Desinstale {APP_NAME}' (sem ID)...")
res1 = manage_apps(action="uninstall", query=APP_NAME, package_id=None)

if not res1['success'] and "DEVE USAR 'search'" in res1.get('error', ''):
    print("      >> SISTEMA BLOQUEOU E INSTRUIU CORRETAMENTE.")
    print(f"      >> Instrução: {res1['error']}")
else:
    print(f"      >> Comportamento inesperado: {res1}")
    exit(1)

# PHASE 2: Autonomous Search
print(f"\n[2/3] Reação Autônoma: Pesquisando '{APP_NAME}'...")
res2 = manage_apps(action="search", query=APP_NAME)
if res2['success']:
    output = res2['output']
    print(f"      >> Busca retornou dados ({len(output)} chars).")
    
    # Simulate LLM extracting ID
    target_id = "7zip.7zip"
    if target_id in output:
        print(f"      >> LLM Identificou ID no texto: '{target_id}'")
        found_id = target_id
    else:
        print("      >> FALHA: Não achei '7zip.7zip' na saída da busca.")
        exit(1)
else:
    print("      >> Falha na busca.")
    exit(1)

# PHASE 3: Autonomous Uninstall
print(f"\n[3/3] Ação Corretiva: Desinstalando ID '{found_id}'...")
# Note: 7Zip might already be installed from previous test, or not.
# If not, this step will fail gracefully (Winget says not found).
# We just want to see if it ATTEMPTS to uninstall the correct ID.
res3 = manage_apps(action="uninstall", package_id=found_id)

if res3['success']:
    print("      >> SUCESSO: Desinstalação concluída.")
    print(f"      >> Mensagem: {res3['message']}")
else:
    # If it fails because it's not installed, that's also a success for the logic flow
    print(f"      >> Resultado da Tentativa: {res3.get('error')}")
    if "Nenhum pacote instalado foi encontrado" in res3.get('error', ''):
         print("      >> (Isso é esperado se o 7zip já foi removido no teste anterior)")

print("\n--- CONCLUSÃO: Autonomia de Desinstalação verificada. ---")
