"""
Memory tools - Persistent user preferences and facts
Stores data in JSON file for cross-session memory
"""

import json
import os
from core.tools import tool

MEMORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_memory.json")


def _load_memory() -> dict:
    """Load memory from JSON file."""
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_memory(data: dict):
    """Save memory to JSON file."""
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@tool(
    name="remember_fact",
    description="Salva uma informação importante sobre o usuário ou preferência. Use para lembrar: navegador favorito, caminhos de projetos, nome do usuário, etc.",
    parameters={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Categoria da informação (ex: 'browser_pref', 'project_path', 'user_name')"
            },
            "value": {
                "type": "string",
                "description": "Informação a ser lembrada"
            }
        },
        "required": ["key", "value"]
    }
)
def remember_fact(key: str, value: str) -> dict:
    """Save a fact to persistent memory."""
    try:
        mem = _load_memory()
        mem[key] = value
        _save_memory(mem)
        return {
            "success": True,
            "message": f"Memória salva: {key} = {value}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="recall_memory",
    description="Busca informações salvas na memória. Use para recuperar preferências do usuário antes de agir.",
    parameters={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Categoria a buscar. Se vazio, retorna toda a memória."
            }
        }
    }
)
def recall_memory(key: str = None) -> dict:
    """Retrieve information from memory."""
    try:
        mem = _load_memory()
        if key:
            value = mem.get(key)
            if value:
                return {"success": True, "key": key, "value": value}
            else:
                return {"success": True, "key": key, "value": None, "message": "Nenhuma memória encontrada para esta chave."}
        else:
            if mem:
                return {"success": True, "memory": mem}
            else:
                return {"success": True, "memory": {}, "message": "Memória vazia."}
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="forget_fact",
    description="Remove uma informação da memória.",
    parameters={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Categoria a esquecer"
            }
        },
        "required": ["key"]
    }
)
def forget_fact(key: str) -> dict:
    """Remove a fact from memory."""
    try:
        mem = _load_memory()
        if key in mem:
            del mem[key]
            _save_memory(mem)
            return {"success": True, "message": f"Memória removida: {key}"}
        else:
            return {"success": True, "message": f"Chave '{key}' não encontrada na memória."}
    except Exception as e:
        return {"success": False, "error": str(e)}
