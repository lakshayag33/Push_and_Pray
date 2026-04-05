/**
 * Chatbot UI logic for VitalSync.
 * Manages conversation state, sends messages to /api/chat,
 * and renders chat bubbles.
 */

(function () {
    const messagesEl = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const urgentAlert = document.getElementById('urgent-alert');

    // Conversation history maintained in browser memory
    let conversation = [];

    /**
     * Append a chat bubble to the messages area.
     */
    function addMessage(role, text) {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${role}`;

        const content = document.createElement('div');
        content.className = 'bubble-content';
        content.innerHTML = `<p class="mb-0">${escapeHtml(text)}</p>`;

        const time = document.createElement('span');
        time.className = 'bubble-time';
        time.textContent = formatTime(new Date());

        bubble.appendChild(content);
        bubble.appendChild(time);
        messagesEl.appendChild(bubble);
        scrollToBottom();
    }

    /**
     * Show typing indicator.
     */
    function showTyping() {
        const typing = document.createElement('div');
        typing.className = 'chat-bubble assistant';
        typing.id = 'typing-indicator';
        typing.innerHTML = `
            <div class="bubble-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        messagesEl.appendChild(typing);
        scrollToBottom();
    }

    /**
     * Remove typing indicator.
     */
    function hideTyping() {
        const typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
    }

    /**
     * Scroll messages to bottom.
     */
    function scrollToBottom() {
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    /**
     * Escape HTML entities.
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Format time as HH:MM AM/PM.
     */
    function formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    /**
     * Send message to API and handle response.
     */
    async function sendMessage(message) {
        // Add user message to UI
        addMessage('user', message);
        conversation.push({ role: 'user', content: message });

        // Show typing
        showTyping();
        chatInput.disabled = true;

        try {
            // Get CSRF token from the page
            const csrfMeta = document.querySelector('input[name="csrf_token"]');
            const csrfToken = csrfMeta ? csrfMeta.value : '';

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    message: message,
                    conversation: conversation,
                }),
            });

            hideTyping();

            if (!response.ok) {
                throw new Error('Failed to get response');
            }

            const data = await response.json();
            const reply = data.reply || "I'm sorry, I couldn't process that. Please try again.";

            addMessage('assistant', reply);
            conversation.push({ role: 'assistant', content: reply });

            // Handle urgency
            if (data.urgent) {
                urgentAlert.classList.remove('d-none');
            }
        } catch (error) {
            hideTyping();
            addMessage('assistant', "I'm having trouble connecting right now. Please try again in a moment.");
            console.error('Chat error:', error);
        } finally {
            chatInput.disabled = false;
            chatInput.focus();
        }
    }

    // Form submit handler
    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;
        chatInput.value = '';
        sendMessage(message);
    });

    // Focus input on load
    chatInput.focus();
})();
