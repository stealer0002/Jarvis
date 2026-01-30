# JARVIS Configuration

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"  # Recommended for function calling

# Server settings
HOST = "0.0.0.0"  # Allow access from any device on network
PORT = 8000

# Agent settings
AGENT_NAME = "JARVIS"
AGENT_LANGUAGE = "pt-BR"
MAX_TOOL_ITERATIONS = 15  # Max tool calls per request
