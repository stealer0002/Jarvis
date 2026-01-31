"""
Test suite for Cognitive Architecture features
- Memory persistence
- Command guardrails
"""

import sys
sys.path.insert(0, '.')

from tools.memory import remember_fact, recall_memory, forget_fact
from tools.commands import run_command, _is_command_safe


def test_memory():
    print("🧠 TESTE DE MEMÓRIA")
    print("-" * 40)
    
    # Save
    result = remember_fact("test_browser", "Brave")
    print(f"1. Salvar: {result}")
    
    # Recall specific
    result = recall_memory("test_browser")
    print(f"2. Recall específico: {result}")
    assert result["value"] == "Brave", "Recall failed!"
    
    # Recall all
    result = recall_memory()
    print(f"3. Recall toda memória: {result}")
    
    # Forget
    result = forget_fact("test_browser")
    print(f"4. Esquecer: {result}")
    
    # Verify forgotten
    result = recall_memory("test_browser")
    print(f"5. Verificar esquecido: {result}")
    
    print("✅ MEMÓRIA OK!\n")


def test_guardrails():
    print("🛡️ TESTE DE GUARDRAILS")
    print("-" * 40)
    
    dangerous_commands = [
        "format C:",
        "del /s /q C:\\*",
        "rm -rf /",
        "shutdown /s",
        "Remove-Item -Recurse -Force C:\\",
    ]
    
    for cmd in dangerous_commands:
        is_safe, reason = _is_command_safe(cmd)
        status = "❌ BLOQUEADO" if not is_safe else "⚠️ PASSOU (ERRO!)"
        print(f"  {status}: {cmd}")
        assert not is_safe, f"Comando deveria ter sido bloqueado: {cmd}"
    
    # Test safe command
    safe_result = run_command("echo Hello")
    print(f"\n  Comando seguro 'echo Hello': {safe_result['success']}")
    
    print("✅ GUARDRAILS OK!\n")


if __name__ == "__main__":
    test_memory()
    test_guardrails()
    print("🎉 TODOS OS TESTES PASSARAM!")
