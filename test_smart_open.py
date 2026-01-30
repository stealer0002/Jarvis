"""Test the improved open_program Iogic."""
from tools.processes import open_program
from tools.program_search import get_start_menu_apps

print("--- Teste de Abertura Inteligente ---\n")

# 1. Check if Start Menu apps are being found
print("[1] Verificando Menu Iniciar...")
apps = get_start_menu_apps()
print(f"    Encontrados {len(apps)} atalhos.")
if apps:
    print(f"    Exemplos: {[a['name'] for a in apps[:5]]}")

# 2. Test fuzzy matching logic (Simulation)
test_queries = ["notepad", "chrome", "edge", "calculadora", "word", "excel"]

print("\n[2] Simulando busca (Lógica interna)...")
for query in test_queries:
    print(f"\n    Buscando: '{query}'")
    
    # Logic from open_program
    query_lower = query.lower()
    best_match = None
    highest_score = 0
    
    for app in apps:
        app_name = app['name'].lower()
        score = 0
        if query_lower == app_name: score = 100
        elif query_lower in app_name: score = 70
        elif app_name in query_lower: score = 50
            
        if score > highest_score:
            highest_score = score
            best_match = app
            
    if best_match and highest_score >= 50:
        print(f"    ✅ MATCH: '{best_match['name']}' (Score: {highest_score})")
        print(f"       Path: {best_match['path']}")
    else:
        print(f"    ❌ Sem match direto no Menu Iniciar")

print("\n--- FIM ---")
