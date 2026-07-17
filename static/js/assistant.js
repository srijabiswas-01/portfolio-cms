(() => {
    const widget = document.getElementById('portfolioAssistant');
    if (!widget) return;

    const launcher = document.getElementById('assistantLauncher');
    const panel = document.getElementById('assistantPanel');
    const closeButton = document.getElementById('assistantClose');
    const clearButton = document.getElementById('assistantClear');
    const form = document.getElementById('assistantForm');
    const input = document.getElementById('assistantInput');
    const sendButton = document.getElementById('assistantSend');
    const messages = document.getElementById('assistantMessages');
    const suggestions = document.getElementById('assistantSuggestions');
    const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]').value;
    const storageKey = 'srija-assistant-session';

    const createSessionId = () => {
        if (window.crypto?.randomUUID) return window.crypto.randomUUID().replaceAll('-', '');
        return `${Date.now().toString(36)}${Math.random().toString(36).slice(2)}${Math.random().toString(36).slice(2)}`;
    };
    let sessionId = localStorage.getItem(storageKey) || createSessionId();
    localStorage.setItem(storageKey, sessionId);

    const setOpen = (open) => {
        widget.classList.toggle('is-open', open);
        panel.setAttribute('aria-hidden', String(!open));
        launcher.setAttribute('aria-expanded', String(open));
        if (open) setTimeout(() => input.focus(), 160);
    };

    const scrollMessages = () => {
        messages.scrollTo({ top: messages.scrollHeight, behavior: 'smooth' });
    };

    const appendMessage = (role, text, sources = []) => {
        const item = document.createElement('div');
        item.className = `assistant-message assistant-message-${role}`;
        const icon = document.createElement('div');
        icon.className = 'assistant-message-icon';
        icon.innerHTML = `<i class="bi bi-${role === 'user' ? 'person' : 'stars'}"></i>`;
        const content = document.createElement('div');
        content.className = 'assistant-message-content';
        const paragraph = document.createElement('p');
        paragraph.textContent = text;
        content.appendChild(paragraph);
        if (sources.length) {
            const sourceList = document.createElement('div');
            sourceList.className = 'assistant-sources';
            sources.forEach((source) => {
                const link = document.createElement('a');
                link.href = source.url;
                link.textContent = source.title;
                link.rel = 'noopener noreferrer';
                if (/^https?:\/\//i.test(source.url)) link.target = '_blank';
                sourceList.appendChild(link);
            });
            content.appendChild(sourceList);
        }
        item.append(icon, content);
        messages.appendChild(item);
        scrollMessages();
        return item;
    };

    const appendTyping = () => {
        const item = document.createElement('div');
        item.className = 'assistant-message assistant-message-bot assistant-typing';
        item.innerHTML = '<div class="assistant-message-icon"><i class="bi bi-stars"></i></div><div class="assistant-message-content"><span></span><span></span><span></span></div>';
        messages.appendChild(item);
        scrollMessages();
        return item;
    };

    const ask = async (question) => {
        question = question.trim();
        if (!question || sendButton.disabled) return;
        suggestions?.remove();
        appendMessage('user', question);
        input.value = '';
        input.style.height = '';
        sendButton.disabled = true;
        input.disabled = true;
        const typing = appendTyping();
        try {
            const response = await fetch(widget.dataset.chatUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ question, session_id: sessionId }),
            });
            const data = await response.json();
            typing.remove();
            if (!response.ok) throw new Error(data.error || 'The assistant could not answer right now.');
            appendMessage('bot', data.answer, data.sources || []);
        } catch (error) {
            typing.remove();
            appendMessage('bot', error.message || 'The assistant is temporarily unavailable.');
        } finally {
            sendButton.disabled = false;
            input.disabled = false;
            input.focus();
        }
    };

    launcher.addEventListener('click', () => setOpen(!widget.classList.contains('is-open')));
    closeButton.addEventListener('click', () => setOpen(false));
    form.addEventListener('submit', (event) => { event.preventDefault(); ask(input.value); });
    input.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); form.requestSubmit(); }
    });
    input.addEventListener('input', () => {
        input.style.height = 'auto';
        input.style.height = `${Math.min(input.scrollHeight, 110)}px`;
    });
    suggestions?.addEventListener('click', (event) => {
        const button = event.target.closest('[data-question]');
        if (button) ask(button.dataset.question);
    });
    clearButton.addEventListener('click', async () => {
        await fetch(widget.dataset.clearUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
            body: JSON.stringify({ session_id: sessionId }),
        }).catch(() => null);
        sessionId = createSessionId();
        localStorage.setItem(storageKey, sessionId);
        messages.querySelectorAll('.assistant-message:not(:first-child), .assistant-suggestions').forEach((item) => item.remove());
    });
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && widget.classList.contains('is-open')) setOpen(false);
    });
})();
