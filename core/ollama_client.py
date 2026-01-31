"""
Ollama API Client for JARVIS
Handles communication with local Ollama server
"""

import httpx
import json
from typing import Optional, AsyncGenerator
import config


class OllamaClient:
    """Async client for Ollama API with tool/function calling support."""
    
    def __init__(self):
        self.base_url = config.OLLAMA_BASE_URL
        self.model = config.OLLAMA_MODEL
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def chat(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        images: Optional[list[str]] = None,
        stream: bool = False,
        model: Optional[str] = None
    ) -> dict:
        """
        Send a chat request to Ollama with optional tool definitions and images.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions for function calling
            images: Optional list of base64 encoded images (for vision models)
            stream: Whether to stream the response
            model: Override default model (e.g. for using 'moondream')
            
        Returns:
            Response dict from Ollama
        """
        payload = {
            "model": model or self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "num_ctx": 8192  # Increased context for longer documents (PDFs, etc.)
            }
        }
        
        if tools:
            payload["tools"] = tools
        
        # Add images to the last message if provided
        # Ollama API expects 'images' field inside the message object
        if images and messages:
            messages[-1]["images"] = images
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {
                "error": str(e),
                "message": {
                    "role": "assistant",
                    "content": f"Erro ao conectar com Ollama: {e}"
                }
            }
    
    async def chat_stream(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None
    ) -> AsyncGenerator[dict, None]:
        """
        Stream a chat response from Ollama.
        
        Args:
            messages: List of message dicts
            tools: Optional tool definitions
            
        Yields:
            Response chunks from Ollama
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }
        
        if tools:
            payload["tools"] = tools
        
        async with self.client.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json=payload
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue
    
    async def check_connection(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except httpx.HTTPError:
            return False
    
    async def list_models(self) -> list[str]:
        """Get list of available models."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except httpx.HTTPError:
            return []
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
