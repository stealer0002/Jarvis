/**
 * JARVIS Web Client
 * WebSocket-based chat interface
 */

class JarvisClient {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 2000;

        // DOM Elements
        this.elements = {
            status: document.getElementById('status'),
            welcome: document.getElementById('welcome'),
            messages: document.getElementById('messages'),
            chatContainer: document.getElementById('chat-container'),
            messageInput: document.getElementById('message-input'),
            sendBtn: document.getElementById('btn-send'),
            clearBtn: document.getElementById('btn-clear'),
            settingsBtn: document.getElementById('btn-settings'),
            modal: document.getElementById('status-modal'),
            modalClose: document.getElementById('modal-close'),
            statusContent: document.getElementById('status-content'),
        };

        this.init();
    }

    init() {
        this.connect();
        this.setupEventListeners();
        this.autoResizeTextarea();
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateStatus('Conectado', 'connected');
            console.log('WebSocket connected');
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };

        this.ws.onclose = () => {
            this.isConnected = false;
            this.updateStatus('Desconectado', 'error');
            this.scheduleReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateStatus('Erro de conexão', 'error');
        };
    }

    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            this.updateStatus(`Reconectando (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            setTimeout(() => this.connect(), this.reconnectDelay);
        }
    }

    updateStatus(text, state = '') {
        this.elements.status.textContent = text;
        this.elements.status.className = 'status ' + state;
    }

    setupEventListeners() {
        // Send message
        this.elements.sendBtn.addEventListener('click', () => this.sendMessage());

        // Enter to send (Shift+Enter for new line)
        this.elements.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Enable/disable send button based on input
        this.elements.messageInput.addEventListener('input', () => {
            this.elements.sendBtn.disabled = !this.elements.messageInput.value.trim();
        });

        // Clear conversation
        this.elements.clearBtn.addEventListener('click', () => this.clearConversation());

        // Settings/Status modal
        this.elements.settingsBtn.addEventListener('click', () => this.showStatusModal());
        this.elements.modalClose.addEventListener('click', () => this.hideModal());
        this.elements.modal.addEventListener('click', (e) => {
            if (e.target === this.elements.modal) this.hideModal();
        });

        // Suggestions
        document.querySelectorAll('.suggestion').forEach(btn => {
            btn.addEventListener('click', () => {
                this.elements.messageInput.value = btn.dataset.text;
                this.elements.sendBtn.disabled = false;
                this.elements.messageInput.focus();
            });
        });
    }

    autoResizeTextarea() {
        const textarea = this.elements.messageInput;
        textarea.addEventListener('input', () => {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
        });
    }

    sendMessage() {
        const text = this.elements.messageInput.value.trim();
        if (!text || !this.isConnected) return;

        // Hide welcome message
        this.elements.welcome.classList.add('hidden');

        // Add user message to UI
        this.addMessage(text, 'user');

        // Clear input
        this.elements.messageInput.value = '';
        this.elements.messageInput.style.height = 'auto';
        this.elements.sendBtn.disabled = true;

        // Show typing indicator
        this.showTypingIndicator();

        // Send to server
        this.ws.send(JSON.stringify({
            type: 'message',
            content: text
        }));
    }

    handleMessage(data) {
        switch (data.type) {
            case 'response':
                this.hideTypingIndicator();
                this.addMessage(data.content, 'assistant');
                break;
            case 'error':
                this.hideTypingIndicator();
                this.addMessage(`❌ Erro: ${data.content}`, 'assistant');
                break;
            case 'status':
                this.displayStatus(data.content);
                break;
            case 'typing':
                // Could show tool execution info here
                break;
        }
    }

    addMessage(text, role) {
        const message = document.createElement('div');
        message.className = `message ${role}`;

        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = this.formatMessage(text);

        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = new Date().toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
        });

        message.appendChild(content);
        message.appendChild(time);
        this.elements.messages.appendChild(message);

        // Scroll to bottom
        this.scrollToBottom();
    }

    formatMessage(text) {
        // Check for screenshot file references and convert to images
        // Pattern: screenshot saved at/em filename.png or filepath with screenshots folder
        let formatted = text;

        // Match screenshot filenames and create image tags
        const screenshotPattern = /(?:Screenshot salva em |screenshot[_\s]?\d*\.png|salva em )([a-zA-Z0-9_\-]+\.png)/gi;
        formatted = formatted.replace(screenshotPattern, (match, filename) => {
            return `<div class="chat-image"><img src="/screenshots/${filename}" alt="Screenshot" onclick="window.open('/screenshots/${filename}', '_blank')"><span class="image-caption">📸 ${filename} (clique para ampliar)</span></div>`;
        });

        // Also check for direct filename mentions like "test_screenshot.png"
        const directPattern = /\b(screenshot_\d{8}_\d{6}\.png)\b/gi;
        formatted = formatted.replace(directPattern, (match, filename) => {
            if (!formatted.includes(`/screenshots/${filename}`)) {
                return `<div class="chat-image"><img src="/screenshots/${filename}" alt="Screenshot" onclick="window.open('/screenshots/${filename}', '_blank')"><span class="image-caption">📸 ${filename}</span></div>`;
            }
            return match;
        });

        // Basic markdown-like formatting
        return formatted
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    showTypingIndicator() {
        const existing = document.querySelector('.typing-indicator');
        if (existing) return;

        const indicator = document.createElement('div');
        indicator.className = 'message assistant';
        indicator.innerHTML = `
            <div class="message-content typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        this.elements.messages.appendChild(indicator);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const indicator = document.querySelector('.typing-indicator');
        if (indicator) {
            indicator.closest('.message').remove();
        }
    }

    scrollToBottom() {
        this.elements.chatContainer.scrollTop = this.elements.chatContainer.scrollHeight;
    }

    clearConversation() {
        this.elements.messages.innerHTML = '';
        this.elements.welcome.classList.remove('hidden');

        // Notify server
        if (this.isConnected) {
            this.ws.send(JSON.stringify({ type: 'clear' }));
        }
    }

    async showStatusModal() {
        this.elements.modal.classList.add('active');
        this.elements.statusContent.innerHTML = 'Carregando...';

        if (this.isConnected) {
            this.ws.send(JSON.stringify({ type: 'status' }));
        } else {
            this.elements.statusContent.innerHTML = `
                <div class="status-item">
                    <label>Conexão</label>
                    <span class="value error">Desconectado</span>
                </div>
            `;
        }
    }

    displayStatus(status) {
        const ollamaStatus = status.ollama_connected ?
            '<span class="value success">Conectado</span>' :
            '<span class="value error">Desconectado</span>';

        const modelStatus = status.model_available ?
            '<span class="value success">Disponível</span>' :
            '<span class="value error">Não encontrado</span>';

        this.elements.statusContent.innerHTML = `
            <div class="status-item">
                <label>Agente</label>
                <span class="value">${status.agent}</span>
            </div>
            <div class="status-item">
                <label>Ollama</label>
                ${ollamaStatus}
            </div>
            <div class="status-item">
                <label>Modelo</label>
                <span class="value">${status.model}</span>
            </div>
            <div class="status-item">
                <label>Modelo Status</label>
                ${modelStatus}
            </div>
            <div class="status-item">
                <label>Ferramentas</label>
                <span class="value">${status.tools_count} disponíveis</span>
            </div>
            ${status.available_models?.length ? `
            <div class="status-item" style="flex-direction: column; align-items: flex-start; gap: 8px;">
                <label>Modelos Instalados</label>
                <span class="value" style="font-size: 0.85rem; word-break: break-all;">
                    ${status.available_models.join(', ')}
                </span>
            </div>
            ` : ''}
        `;
    }

    hideModal() {
        this.elements.modal.classList.remove('active');
    }
}

// Initialize client when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.jarvis = new JarvisClient();
});
