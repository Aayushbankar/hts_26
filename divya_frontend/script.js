document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    lucide.createIcons();

    const startBtn = document.getElementById('start-btn');
    const landingPage = document.getElementById('landing-page');
    const chatPage = document.getElementById('chat-page');
    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const emptyState = document.querySelector('.empty-state');
    const resetBtn = document.querySelector('.reset-btn');
    
    // Sidebar element
    const sidebarUl = document.querySelector('.chat-sidebar ul');

    // Page Switching Logic
    startBtn.addEventListener('click', () => {
        landingPage.classList.remove('active');
        chatPage.classList.add('active');
        
        // Adjust chat layout dynamically for messages
        const mainView = document.querySelector('.chat-main-view');
        mainView.style.justifyContent = 'flex-start';
        mainView.style.overflowY = 'auto'; // ensure scrolling if needed
        chatMessages.style.width = '100%';
        chatMessages.style.flex = '1';
        chatMessages.style.overflowY = 'auto';
        chatMessages.style.display = 'flex';
        chatMessages.style.flexDirection = 'column';
        chatMessages.style.gap = '15px';
        chatMessages.style.paddingTop = '20px';
    });

    // Handle appending messages with inline styling mimicking original design intention
    function appendMessage(text, role) {
        if(emptyState) emptyState.style.display = 'none';
        
        const div = document.createElement('div');
        div.style.padding = '12px 18px';
        div.style.borderRadius = '12px';
        div.style.maxWidth = '75%';
        div.style.color = 'white';
        div.style.fontFamily = 'monospace';
        div.style.lineHeight = '1.4';
        div.style.wordBreak = 'break-word';

        if(role === 'user') {
            div.style.backgroundColor = 'var(--accent-purple)';
            div.style.alignSelf = 'flex-end';
            div.style.borderBottomRightRadius = '0px';
            div.textContent = text;
        } else if(role === 'ai') {
            div.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
            div.style.alignSelf = 'flex-start';
            div.style.borderBottomLeftRadius = '0px';
            div.style.borderLeft = '4px solid var(--accent-green)';
            div.innerHTML = marked.parse(text); // Render markdown
            
            // Basic styling for internal markdown elements
            div.querySelectorAll('p').forEach(p => p.style.marginTop = '0.5em');
            div.querySelectorAll('p:first-child').forEach(p => p.style.marginTop = '0');
            div.querySelectorAll('pre, code').forEach(c => {
                c.style.backgroundColor = 'rgba(0,0,0,0.3)';
                c.style.padding = '0.2rem 0.4rem';
                c.style.borderRadius = '4px';
                c.style.fontFamily = 'monospace';
            });
            div.querySelectorAll('pre').forEach(p => p.style.padding = '1rem');
        } else if(role === 'error') {
            div.style.backgroundColor = '#4a1a1a';
            div.style.alignSelf = 'flex-start';
            div.style.color = '#ff6b6b';
            div.style.borderBottomLeftRadius = '0px';
            div.style.borderLeft = '4px solid #ff6b6b';
            div.textContent = text;
        }
        
        chatMessages.appendChild(div);
        
        // Scroll to bottom
        setTimeout(() => {
            const chatMainView = document.querySelector('.chat-main-view');
            chatMainView.scrollTop = chatMainView.scrollHeight;
        }, 10);
    }
    
    function updateSidebar(data) {
        // Generate new HTML for sidebar based on backend response
        const entitiesHtml = (data.entities_detected || []).map(ent => 
            `<div style="font-size: 0.9em; margin-top: 6px; padding-left: 15px; color: var(--accent-green);">[${ent.label}] ${ent.text}</div>`
        ).join('') || `<div style="font-size: 0.9em; margin-top: 6px; padding-left: 15px; color: var(--text-gray);">None</div>`;
        
        const aliasHtml = (data.entities_detected || [])
            .filter(ent => ent.alias && ent.alias !== ent.text)
            .map(ent => `<div style="font-size: 0.9em; margin-top: 6px; padding-left: 15px; color: #f1c40f;">${ent.text} &rarr; ${ent.alias}</div>`)
            .join('') || `<div style="font-size: 0.9em; margin-top: 6px; padding-left: 15px; color: var(--text-gray);">None</div>`;

        const aiSeesHtml = data.sanitized_prompt 
            ? `<div style="font-size: 0.9em; margin-top: 6px; padding-left: 15px; color: var(--text-gray); white-space: pre-wrap;">${data.sanitized_prompt}</div>`
            : '';

        sidebarUl.innerHTML = `
            <li><span class="bullet">•</span> What AI Sees${aiSeesHtml}</li>
            <li><span class="bullet">•</span> Entities Detected${entitiesHtml}</li>
            <li><span class="bullet">•</span> Alias Map${aliasHtml}</li>
        `;
    }

    // Connect to backend
    async function handleSend() {
        const text = userInput.value.trim();
        if(text !== "") {
            appendMessage(text, 'user');
            userInput.value = "";
            userInput.disabled = true;
            
            // show loading
            const loadingId = 'loading-' + Date.now();
            const loadingDiv = document.createElement('div');
            loadingDiv.id = loadingId;
            loadingDiv.style.alignSelf = 'flex-start';
            loadingDiv.style.color = 'var(--text-gray)';
            loadingDiv.style.fontFamily = 'monospace';
            loadingDiv.textContent = 'Encrypting...';
            chatMessages.appendChild(loadingDiv);
            
            try {
                const res = await fetch('http://127.0.0.1:8000/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                
                document.getElementById(loadingId)?.remove();
                appendMessage(data.response, 'ai');
                updateSidebar(data);
                
            } catch (err) {
                console.error(err);
                document.getElementById(loadingId)?.remove();
                appendMessage("Error: Could not reach backend.", 'error');
            }
            userInput.disabled = false;
            userInput.focus();
        }
    }

    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });
    
    resetBtn.addEventListener('click', async () => {
        try {
            await fetch('http://127.0.0.1:8000/reset', { method: 'POST' });
        } catch(e) {}
        chatMessages.innerHTML = '';
        if(emptyState) emptyState.style.display = 'block';
        sidebarUl.innerHTML = `
            <li><span class="bullet">•</span> What AI Sees</li>
            <li><span class="bullet">•</span> Entities Detected</li>
            <li><span class="bullet">•</span> Alias Map</li>
        `;
    });
});
