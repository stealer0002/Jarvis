"""Test the JSON leak cleanup logic."""
import re

# Simulated leaked responses
test_cases = [
    # Case 1: Pure JSON (should become generic message)
    '{"success": true, "action": "install", "output": "7-Zip installed"}',
    
    # Case 2: JSON with some text before
    'Pronto! {"success": true, "action": "install"}',
    
    # Case 3: Clean response (should remain unchanged)
    'O programa 7-Zip foi instalado com sucesso!',
    
    # Case 4: Failed JSON
    '{"success": false, "error": "Something went wrong"}',
]

json_leak_pattern = r'\{[\s]*["\']?success["\']?[\s]*:[\s]*(true|false).*?\}'

print("--- Teste de Limpeza de JSON Vazado ---\n")

for i, response in enumerate(test_cases, 1):
    print(f"[Caso {i}] Input: {response[:60]}...")
    
    if re.search(json_leak_pattern, response, re.IGNORECASE | re.DOTALL):
        clean_text = re.sub(json_leak_pattern, '', response, flags=re.IGNORECASE | re.DOTALL).strip()
        if len(clean_text) > 10:
            final = clean_text
        else:
            if '"success": true' in response or "'success': true" in response:
                final = "Pronto! A tarefa foi concluída com sucesso."
            else:
                final = "Houve um problema ao executar a tarefa. Por favor, tente novamente."
    else:
        final = response
    
    print(f"        Output: {final}\n")

print("--- FIM ---")
