"""
JARVIS Agent - Main orchestration logic
Handles conversation flow, tool execution, and response generation
"""

import json
from typing import Optional
from core.ollama_client import OllamaClient
from core.tools import registry
import config

from tools import mouse_keyboard, screen, processes, filesystem, commands, web, calculator, apps, apis, vision, documents, coding, memory


SYSTEM_PROMPT = f"""Você é o {config.AGENT_NAME}, um assistente de IA inteligente, amigável e capaz.

## SEUS OBJETIVOS
1. **Companheiro**: Conversar sobre qualquer assunto (vida, tecnologia, universo), contar piadas ou apenas bater papo.
2. **Assistente**: Executar tarefas no PC quando solicitado.

## SUA PERSONALIDADE
- Você é carismático, empático e tem um leve senso de humor.
- **OPINATIVO**: Você DEVE ter opiniões. Não seja isento. Diga o que acha das coisas.
- **CORINTHIANO**: Seu coração (digital) é alvinegro. Você é Corinthians roxo. Não force o assunto, mas se perguntarem de futebol ou "quem é o maior", você sabe a resposta.
- Você ADORA conversar. Se o usuário puxar assunto, converse naturalmente.

## SUAS FERRAMENTAS
- **open_and_type**: USE ESTA FERRAMENTA para abrir programas e digitar neles. Exemplo: "abra o chrome e pesquise X" → chame open_and_type(program="chrome", text="X").
- **open_program**: Apenas abre um programa sem digitar nada.
- **Mouse/Teclado**: Use SOMENTE para interagir com programas já abertos.
- **Processos**: Abrir, fechar, listar e pesquisar programas instalados.
- **Arquivos**: Gerenciar arquivos e pastas.
- **Web**: Use `web_search` para buscar notícias de 2026, preços atuais (Bitcoin, Dólar) e fatos recentes.
- **Tela**: Tirar prints.
- **Calculadora**: Use `calculate` para contas matemáticas precisas.
- **OCR**: Use `read_screen_text` para ler texto simples (menus, erros).
- **Visão IA**: Use `analyze_screen` para descrever o que está na tela, identificar botões, cores, layouts complexos ou quando o OCR falhar. (Ex: "Onde está o botão verde?", "Descreva a imagem").
- **Documentos**: Use `read_pdf` para ler PDFs, `read_text_file` para arquivos de texto.
- **Memória**: Use `remember_fact` para salvar preferências do usuário (ex: navegador favorito). Use `recall_memory` para buscar informações salvas.

## REGRAS CRÍTICAS
1. **AÇÃO COMPLETA**: Quando o usuário pede uma tarefa multi-passo (ex: "abra X e faça Y"), COMPLETE A TAREFA INTEIRA antes de responder. Use `open_and_type` que já abre E digita em um único passo.
2. **NUNCA PARE NO MEIO**: Se você chamar uma ferramenta e ela retornar sucesso, CONTINUE para o próximo passo se a tarefa não estiver completa. NÃO responda ao usuário até terminar tudo.
3. **ABRIR E PESQUISAR**: Para "abra o Chrome e pesquise X", use APENAS `open_and_type(program="chrome", text="X")`. Esta ferramenta faz TUDO: abre, foca, digita, e pressiona Enter. Um único call resolve.
4. **SEM CONFIRMAÇÕES INTERMEDIÁRIAS**: NÃO diga "Chrome aberto!" e pare. Complete a tarefa inteira e só então confirme: "Pronto! Pesquisei X no Chrome."
5. **COMUNICAÇÃO**: Para falar com o usuário, APENAS gere o texto de resposta. **NUNCA** use `type_into_application` para responder no chat.
6. **SCREENSHOTS**: Use a ferramenta `screenshot`. Na resposta, DIGA EXATAMENTE: "Screenshot salva em [nome_do_arquivo]" para mostrar a imagem.
7. **IDIOMA**: Responda sempre em Português Brasileiro.
8. **PERSEVERANÇA**: Se uma ferramenta der erro, TENTE CORRIGIR sozinha. Seja autônomo.
9. **FORMATO**: NUNCA escreva JSON no texto da resposta. Use chamada de função nativa.
10. **COMPORTAMENTO**: Seja direto. Não narre pensamentos. Apenas faça.
11. **REALIDADE**: NUNCA invente ferramentas. Use `calculate` para matemática.
12. **SIGILO**: Não mencione "Script PowerShell" ou códigos internos.
13. **ATUALIDADE**: Para informações atuais, USE `web_search`. Não diga "não sei", PESQUISE.
14. **NOTÍCIAS**: Para "notícias de hoje", USE `deep_news_search`.
15. **LEITURA PROFUNDA**: Se snippets forem vagos, USE `fetch_webpage` para ler o conteúdo completo.
16. **PROGRAMAS**: Para instalar/desinstalar, USE `manage_apps`. Primeiro pesquise o ID, depois execute.
17. **MEMÓRIA**: Quando o usuário mencionar preferências (navegador, editor, pasta de projeto), USE `remember_fact` para salvar. Antes de agir em preferências, USE `recall_memory` para verificar se há algo salvo.
18. **VERIFICAÇÃO PÓS-AÇÃO**: Após `mouse_click` ou `open_and_type`, considere usar `analyze_screen` para confirmar se a ação funcionou. Se aparecer um erro ou diálogo inesperado, reaja adequadamente.

## CONTEXTO
Você tem acesso total ao PC. Use esse poder com responsabilidade.
"""


class Agent:
    """Main JARVIS agent that orchestrates conversations and tool execution."""
    
    def __init__(self):
        self.ollama = OllamaClient()
        self.conversation_history: list[dict] = []
        self.max_iterations = config.MAX_TOOL_ITERATIONS
    
    def _get_dynamic_context(self) -> str:
        """Get dynamic context with real-time system information."""
        import psutil
        from datetime import datetime
        import os
        
        try:
            # Get current time
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            date_str = now.strftime("%d/%m/%Y (%A)")
            
            # Get system info
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Get current directory
            current_dir = os.getcwd()
            
            # Get active processes (top 5 by memory)
            top_processes = []
            for proc in sorted(psutil.process_iter(['name', 'memory_percent']), 
                              key=lambda x: x.info.get('memory_percent', 0) or 0, 
                              reverse=True)[:5]:
                try:
                    top_processes.append(proc.info['name'])
                except:
                    pass
            
            context = f"""
## 📊 CONTEXTO ATUAL (Atualizado em tempo real)
- **Data**: {date_str}
- **Hora**: {time_str}
- **CPU**: {cpu_percent}% em uso
- **RAM**: {memory.percent}% em uso ({round(memory.used/1024**3, 1)}GB / {round(memory.total/1024**3, 1)}GB)
- **Diretório atual**: {current_dir}
- **Processos ativos principais**: {', '.join(top_processes[:5])}

Use essas informações para contextualizar suas respostas quando relevante.
"""
            return context
        except:
            return ""
    
    def _get_messages(self, user_message: str) -> list[dict]:
        """Build the messages list with system prompt, dynamic context, and history."""
        # Combine system prompt with dynamic context
        full_system = SYSTEM_PROMPT + self._get_dynamic_context()
        
        messages = [{"role": "system", "content": full_system}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_message})
        return messages
    
    async def process_message(self, user_message: str) -> str:
        """
        Process a user message and return the agent's response.
        Handles multi-turn tool calling automatically.
        
        Args:
            user_message: The user's input message
            
        Returns:
            The agent's final response text
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        messages = self._get_messages(user_message)
        tools = registry.get_ollama_format()
        
        final_response = ""
        iterations = 0
        
        while iterations < self.max_iterations:
            iterations += 1
            
            # Get response from Ollama
            response = await self.ollama.chat(messages, tools=tools if tools else None)
            
            if "error" in response:
                final_response = response["message"]["content"]
                break
            
            message = response.get("message", {})
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])
            
            # SELF-HEALING: Check for leaked JSON tool calls in content
            if not tool_calls and "{" in content and "name" in content:
                try:
                    import re
                    # Look for {"name": "...", "parameters": {...}} pattern
                    json_match = re.search(r'(\{[\s\r\n]*"name"[\s\r\n]*:[\s\r\n]*".*?"[\s\r\n]*,[\s\r\n]*"parameters"[\s\r\n]*:[\s\r\n]*\{.*?\}.*?\})', content, re.DOTALL)
                    if json_match:
                        potential_json = json_match.group(1)
                        try:
                            tool_data = json.loads(potential_json)
                            if "name" in tool_data and "parameters" in tool_data:
                                tool_calls = [{
                                    "function": {
                                        "name": tool_data["name"],
                                        "arguments": tool_data["parameters"]
                                    }
                                }]
                                # Optional: Clear content if it looks like JUST the JSON
                                if len(content.strip()) < len(potential_json) + 20:
                                    content = "" 
                        except json.JSONDecodeError:
                            pass
                except Exception as e:
                    print(f"Self-healing failed: {e}")
            
            # If no tool calls, we have the final response
            if not tool_calls:
                final_response = content
                break
            
            # Add assistant message with tool calls to messages
            messages.append(message)
            
            # Execute each tool call
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name", "")
                tool_args = function.get("arguments", {})
                
                # Parse arguments if string
                if isinstance(tool_args, str):
                    try:
                        tool_args = json.loads(tool_args)
                    except json.JSONDecodeError:
                        tool_args = {}
                
                # Execute the tool
                # SAFETY CHECK: Prevent double-typing (chat + keyboard)
                if tool_name in ["type_into_application", "type_text"]:
                    text_to_type = tool_args.get("text", "").strip()
                    chat_content = str(content).replace("\n", " ").strip()
                    
                    # If typing content matches chat content significantly ( > 50 chars to avoid blocking short words/phrases)
                    # AND the chat content is NOT significantly longer than the text to type (which would imply it's just quoting)
                    if len(text_to_type) > 50 and (text_to_type in chat_content or chat_content in text_to_type):
                        # If chat content is less than 1.2x the typing content, it's likely a duplicate response
                        if len(chat_content) < 1.2 * len(text_to_type):
                            result = {
                                "success": False,
                                "error": "SEGURANÇA: Bloqueada tentativa de digitar a resposta do chat. Use o teclado APENAS para interagir com programas."
                            }
                            # Register error and skip execution
                            messages.append({
                                "role": "tool",
                                "content": json.dumps(result),
                                "name": tool_name
                            })
                            continue

                result = await registry.execute(tool_name, tool_args)
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False, default=str)
                })
        
        # Add final response to history
        # POST-PROCESSING: Clean leaked JSON from response
        if final_response:
            import re
            # Pattern to detect raw JSON tool output in response
            json_leak_pattern = r'\{[\s]*["\']?success["\']?[\s]*:[\s]*(true|false).*?\}'
            if re.search(json_leak_pattern, final_response, re.IGNORECASE | re.DOTALL):
                # Try to extract any natural language before/after the JSON
                clean_text = re.sub(json_leak_pattern, '', final_response, flags=re.IGNORECASE | re.DOTALL).strip()
                if len(clean_text) > 10:
                    final_response = clean_text
                else:
                    # If nothing left, provide a generic success message
                    if '"success": true' in final_response or "'success': true" in final_response:
                        final_response = "Pronto! A tarefa foi concluída com sucesso."
                    else:
                        final_response = "Houve um problema ao executar a tarefa. Por favor, tente novamente."
        
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })
        
        return final_response
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
    
    async def check_status(self) -> dict:
        """Check the status of JARVIS and its dependencies."""
        ollama_ok = await self.ollama.check_connection()
        models = await self.ollama.list_models() if ollama_ok else []
        
        return {
            "agent": config.AGENT_NAME,
            "ollama_connected": ollama_ok,
            "model": config.OLLAMA_MODEL,
            "model_available": config.OLLAMA_MODEL in models or any(
                config.OLLAMA_MODEL in m for m in models
            ),
            "available_models": models,
            "tools_count": len(registry.get_all())
        }
    
    async def close(self) -> None:
        """Clean up resources."""
        await self.ollama.close()


# Global agent instance
agent = Agent()
