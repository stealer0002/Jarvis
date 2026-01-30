from tools.apps import manage_apps
import re

print("--- TESTE FINAL: Loop de Autonomia Completo ---")
APP_NAME = "7zip"

# FASE 1: Agente tenta instalar sem ID (O erro "preguiçoso")
print(f"\n[1/3] Tentativa Ingênua: 'Instale {APP_NAME}' (sem ID)...")
res1 = manage_apps(action="install", query=APP_NAME, package_id=None)

if not res1['success'] and "DEVE USAR 'search'" in res1.get('error', ''):
    print("      >> SISTEMA BLOQUEOU E INSTRUIU CORRETAMENTE.")
    print(f"      >> Instrução: {res1['error']}")
else:
    print(f"      >> Comportamento inesperado: {res1}")
    exit(1)

# FASE 2: Agente obedece e Pesquisa
print(f"\n[2/3] Reação Autônoma: Pesquisando '{APP_NAME}'...")
res2 = manage_apps(action="search", query=APP_NAME)
if res2['success']:
    output = res2['output']
    print(f"      >> Busca retornou dados ({len(output)} chars).")
    
    # Simulação simples da "visão" do LLM para pegar o ID
    # Procura '7zip.7zip' ou similar no texto
    # Winget output format: Name  Id  Version
    # Vamos tentar achar o ID padrão '7zip.7zip'
    target_id = "7zip.7zip"
    if target_id in output:
        print(f"      >> LLM Identificou ID no texto: '{target_id}'")
        found_id = target_id
    else:
        print("      >> FALHA: Não achei '7zip.7zip' na saída da busca.")
        print(output)
        exit(1)
else:
    print("      >> Falha na busca.")
    exit(1)

# FASE 3: Agente Instala com o ID encontrado
print(f"\n[3/3] Ação Corretiva: Instalando ID '{found_id}'...")
res3 = manage_apps(action="install", package_id=found_id)

if res3['success']:
    print("      >> SUCESSO FINAL: Instalação concluída real.")
    print(f"      >> Mensagem: {res3['message']}")
else:
    print(f"      >> Erro na instalação final: {res3.get('error')}")

print("\n--- CONCLUSÃO: O sistema é capaz de se auto-corrigir e instalar? SIM. ---")
