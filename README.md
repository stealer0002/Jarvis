# JARVIS - Autonomous AI Desktop Agent

Um assistente de IA autônomo que controla seu PC, acessível de qualquer dispositivo via web.

## 🚀 Quick Start

1. **Certifique-se que o Ollama está rodando:**
   ```bash
   ollama pull llama3.1
   ollama serve
   ```

2. **Inicie o JARVIS:**
   ```bash
   # Windows - duplo clique em:
   start.bat
   
   # Ou manualmente:
   pip install -r requirements.txt
   python main.py
   ```

3. **Acesse:**
   - **Local:** http://localhost:8000
   - **Celular:** http://[IP-DO-SEU-PC]:8000
   
   Para encontrar seu IP: `ipconfig | findstr IPv4`

## 🛠️ Ferramentas Disponíveis

| Categoria | Ferramentas |
|-----------|-------------|
| 🖱️ Mouse/Teclado | click, move, scroll, type, hotkey, drag |
| 🖥️ Tela | screenshot, screen size, locate image, pixel color |
| ⚙️ Processos | open/close program, list processes, system info |
| 📁 Arquivos | read/write/move/copy/delete files, list directory |
| 💻 Comandos | run command, PowerShell, open URL |

## 💬 Exemplos de Uso

- "Abra o Chrome e vá para o YouTube"
- "Tire uma screenshot da tela"
- "Liste os arquivos da pasta Downloads"
- "Feche todos os processos do notepad"
- "Crie um arquivo teste.txt com 'Olá mundo'"
- "Qual o uso de CPU e memória do sistema?"

## ⚠️ Modo Autônomo

O JARVIS executa ações automaticamente sem pedir confirmação. Use com cuidado!

## 📱 Acesso Remoto (Celular)

1. Garanta que PC e celular estão na mesma rede WiFi
2. Encontre o IP do PC: `ipconfig`
3. Acesse `http://[IP]:8000` no navegador do celular
