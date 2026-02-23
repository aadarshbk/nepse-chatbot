// static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const input = document.querySelector('input[name="message"]');
    const messagesContainer = document.querySelector('.messages');
    const submitBtn = document.querySelector('button[type="submit"]');

    // Auto-scroll to bottom on load
    scrollToBottom();

    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // Stop page reload

        const message = input.value.trim();
        if (!message) return;

        // 1. Add User Message to UI immediately
        appendMessage('You', message);
        input.value = '';
        setLoading(true);

        try {
            // 2. Send to Backend
            const formData = new FormData();
            formData.append('message', message);

            const response = await fetch('/chat', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest' // Tell backend we want JSON
                }
            });

            const data = await response.json();

            // 3. Add Bot Response to UI
            if (data.reply) {
                appendMessage('NepseBot', data.reply);
            } else {
                appendMessage('NepseBot', 'Error: No response from server.');
            }

        } catch (error) {
            console.error('Error:', error);
            appendMessage('NepseBot', 'Error: Could not connect to server.');
        } finally {
            setLoading(false);
            scrollToBottom();
        }
    });

    function appendMessage(sender, text) {
        const div = document.createElement('div');
        div.className = `message ${sender === 'You' ? 'user' : 'bot'}`;
        div.innerHTML = `
            <div class="sender">${sender}</div>
            <div class="text">${text.replace(/\n/g, '<br>')}</div>
        `;
        messagesContainer.appendChild(div);
        scrollToBottom();
    }

    function setLoading(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            submitBtn.innerText = '...';
            input.disabled = true;
        } else {
            submitBtn.disabled = false;
            submitBtn.innerText = 'Send';
            input.disabled = false;
            input.focus();
        }
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
});