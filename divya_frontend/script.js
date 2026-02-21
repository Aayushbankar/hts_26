document.addEventListener('DOMContentLoaded', () => {
    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const idleState = document.getElementById('idle-state');
    const cursorLine = document.getElementById('cursor-line');
    const resetBtn = document.getElementById('reset-btn');
    const sidebarContent = document.getElementById('sidebar-content');
    const privacyBadge = document.getElementById('privacy-badge');
    const sidebarScore = document.getElementById('sidebar-score');

    let messageCount = 0;
    let isSending = false;

    userInput.focus();

    // hide idle state while typing
    userInput.addEventListener('input', () => {
        if (userInput.value.trim().length > 0 && messageCount === 0) {
            idleState.style.opacity = '0';
        } else if (userInput.value.trim().length === 0 && messageCount === 0) {
            idleState.style.opacity = '1';
        }
    });


    // ---- MESSAGES ----
    function appendMessage(text, role) {
        if (idleState) idleState.classList.add('hidden');
        if (cursorLine) cursorLine.remove();

        const wrapper = document.createElement('div');
        wrapper.style.display = 'flex';
        wrapper.style.flexDirection = 'column';
        wrapper.style.gap = '4px';

        const div = document.createElement('div');
        div.className = 'message ' + role;

        if (role === 'user') {
            div.textContent = text;
            wrapper.style.alignItems = 'flex-end';
        } else if (role === 'ai') {
            div.innerHTML = marked.parse(text);
            wrapper.style.alignItems = 'flex-start';
        } else if (role === 'error') {
            div.textContent = text;
            wrapper.style.alignItems = 'flex-start';
        }

        const time = document.createElement('div');
        time.className = 'msg-time';
        const now = new Date();
        time.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        wrapper.appendChild(div);
        wrapper.appendChild(time);
        chatMessages.appendChild(wrapper);

        setTimeout(() => { chatMessages.scrollTop = chatMessages.scrollHeight; }, 50);
        messageCount++;
    }


    // ---- TYPING INDICATOR ----
    function showTypingIndicator() {
        const wrapper = document.createElement('div');
        wrapper.id = 'typing-indicator';
        wrapper.className = 'typing-indicator';

        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            dot.className = 'typing-dot';
            dot.textContent = '•';
            dot.style.animation = `dotBounce 1s ease-in-out ${i * 0.15}s infinite`;
            wrapper.appendChild(dot);
        }

        const label = document.createElement('span');
        label.textContent = ' Processing...';
        label.style.marginLeft = '6px';
        wrapper.appendChild(label);

        chatMessages.appendChild(wrapper);
        setTimeout(() => { chatMessages.scrollTop = chatMessages.scrollHeight; }, 50);
    }

    function removeTypingIndicator() {
        const el = document.getElementById('typing-indicator');
        if (el) el.remove();
    }


    // ---- PRIVACY SCORE ----
    function updatePrivacyScore(scoreData) {
        if (!scoreData) return;
        sidebarScore.style.display = 'block';

        const score = scoreData.score || 0;
        const risk = scoreData.risk_level || 'NONE';

        document.getElementById('score-value').textContent = score;

        const fill = document.getElementById('score-bar-fill');
        fill.style.width = score + '%';

        let barColor = '#10b981', badgeBg = 'rgba(16,185,129,0.15)', badgeColor = '#10b981';
        if (risk === 'MEDIUM') { barColor = '#f4c430'; badgeBg = 'rgba(244,196,48,0.15)'; badgeColor = '#f4c430'; }
        else if (risk === 'HIGH') { barColor = '#ff9100'; badgeBg = 'rgba(255,145,0,0.15)'; badgeColor = '#ff9100'; }
        else if (risk === 'CRITICAL') { barColor = '#ff5252'; badgeBg = 'rgba(255,82,82,0.15)'; badgeColor = '#ff5252'; }

        fill.style.backgroundColor = barColor;

        const badge = document.getElementById('score-badge');
        badge.textContent = risk;
        badge.style.backgroundColor = badgeBg;
        badge.style.color = badgeColor;

        const details = document.getElementById('score-details');
        details.innerHTML = `${scoreData.replaced || 0} replaced · ${scoreData.perturbed || 0} perturbed · ${scoreData.preserved || 0} preserved<br>HIPAA: ${scoreData.hipaa_identifiers_protected || 0}/${scoreData.hipaa_identifiers_found || 0} protected`;

        privacyBadge.style.display = 'inline-block';
        privacyBadge.textContent = score + '/100 ' + risk;
        privacyBadge.style.backgroundColor = badgeBg;
        privacyBadge.style.color = badgeColor;
    }


    // ---- SIDEBAR ----
    function updateSidebar(data) {
        // sanitized prompt
        const aiSeesHtml = data.sanitized_prompt
            ? `<div style="font-size:12px; margin-top:8px; padding:10px 12px; background:rgba(0,0,0,0.3); border:1px solid rgba(0,229,255,0.06); border-radius:8px; color:var(--text-muted); white-space:pre-wrap; font-family:'JetBrains Mono',monospace; line-height:1.6; max-height:120px; overflow-y:auto;">${escapeHtml(data.sanitized_prompt)}</div>`
            : '';

        // entities with tier badges
        const entities = data.entities_detected || [];
        let entitiesHtml = '';
        if (entities.length > 0) {
            const tierColors = { 'REPLACE': '#ff5252', 'PERTURB': '#f4c430', 'PRESERVE': '#10b981' };
            const tierLabels = { 'REPLACE': 'R', 'PERTURB': 'P', 'PRESERVE': 'K' };
            entitiesHtml = '<div style="display:flex; flex-direction:column; gap:4px; margin-top:8px;">' + entities.map(ent => {
                const color = tierColors[ent.tier] || '#fff';
                const label = tierLabels[ent.tier] || '?';
                return `<div style="font-size:12px; padding:6px 8px; display:flex; align-items:center; gap:6px; background:rgba(0,0,0,0.15); border-radius:6px; border:1px solid rgba(255,255,255,0.03);">
                    <span style="display:inline-flex; width:18px; height:18px; border-radius:4px; background:${color}; color:#000; font-size:9px; font-weight:700; align-items:center; justify-content:center; flex-shrink:0; font-family:'JetBrains Mono',monospace;">${label}</span>
                    <span style="color:var(--text-primary); flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${escapeHtml(ent.text)}</span>
                    <span style="color:var(--text-dim); font-size:10px; font-family:'JetBrains Mono',monospace; flex-shrink:0;">${ent.label}</span>
                </div>`;
            }).join('') + '</div>';
        } else {
            entitiesHtml = `<div style="font-size:12px; margin-top:8px; color:var(--text-dim); font-style:italic;">None detected</div>`;
        }

        // legend
        const legendHtml = `<div style="display:flex; gap:12px; margin-top:10px; font-size:9px; color:var(--text-dim); font-family:'JetBrains Mono',monospace; letter-spacing:0.05em;">
            <span><span style="color:#ff5252;">●</span> Replace</span>
            <span><span style="color:#f4c430;">●</span> Perturb</span>
            <span><span style="color:#10b981;">●</span> Preserve</span>
        </div>`;

        // aliases
        const aliases = entities.filter(ent => ent.alias && ent.alias !== ent.text);
        let aliasHtml = '';
        if (aliases.length > 0) {
            aliasHtml = '<div style="display:flex; flex-direction:column; gap:4px; margin-top:8px;">' + aliases.map(ent =>
                `<div style="font-size:12px; padding:6px 8px; font-family:'JetBrains Mono',monospace; background:rgba(0,0,0,0.15); border-radius:6px; border:1px solid rgba(255,255,255,0.03);">
                    <span style="color:#ff5252; text-decoration:line-through; opacity:0.7;">${escapeHtml(ent.text)}</span>
                    <span style="color:var(--text-dim);"> → </span>
                    <span style="color:#10b981;">${escapeHtml(ent.alias)}</span>
                </div>`
            ).join('') + '</div>';
        } else {
            aliasHtml = `<div style="font-size:12px; margin-top:8px; color:var(--text-dim); font-style:italic;">No aliases</div>`;
        }

        sidebarContent.innerHTML = `
            <div class="sidebar-section">
                <div class="sidebar-section-title">What AI Sees</div>
                ${aiSeesHtml}
            </div>
            <div class="sidebar-section">
                <div class="sidebar-section-title">Entities (${entities.length})</div>
                ${entitiesHtml}${legendHtml}
            </div>
            <div class="sidebar-section">
                <div class="sidebar-section-title">Alias Map (${aliases.length})</div>
                ${aliasHtml}
            </div>
        `;

        updatePrivacyScore(data.privacy_score);
    }


    // ---- SEND ----
    async function handleSend() {
        const text = userInput.value.trim();
        if (text === '' || isSending) return;

        isSending = true;
        appendMessage(text, 'user');
        userInput.value = '';
        userInput.disabled = true;
        sendBtn.style.opacity = '0.5';
        sendBtn.style.pointerEvents = 'none';

        showTypingIndicator();

        try {
            const res = await fetch('http://127.0.0.1:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || 'Server error ' + res.status);
            }

            const data = await res.json();
            removeTypingIndicator();
            appendMessage(data.response, 'ai');
            updateSidebar(data);

        } catch (err) {
            console.error(err);
            removeTypingIndicator();
            appendMessage('Could not reach backend: ' + err.message, 'error');
        }

        userInput.disabled = false;
        sendBtn.style.opacity = '1';
        sendBtn.style.pointerEvents = 'auto';
        isSending = false;
        userInput.focus();
    }

    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
    });


    // ---- RESET ----
    resetBtn.addEventListener('click', async () => {
        if (messageCount > 0) {
            const ok = confirm('Clear chat history and reset aliases?');
            if (!ok) return;
        }

        try { await fetch('http://127.0.0.1:8000/reset', { method: 'POST' }); } catch(e) {}

        chatMessages.innerHTML = '<div class="cursor-line" id="cursor-line"></div>';
        messageCount = 0;

        if (idleState) {
            idleState.classList.remove('hidden');
            idleState.style.opacity = '1';
        }

        sidebarContent.innerHTML = `
            <div class="sidebar-section">
                <div class="sidebar-section-title">What AI Sees</div>
                <div style="font-size:12px; color:var(--text-dim); font-style:italic;">Send a message to see sanitized output</div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-section-title">Entities Detected</div>
                <div style="font-size:12px; color:var(--text-dim); font-style:italic;">No entities yet</div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-section-title">Alias Map</div>
                <div style="font-size:12px; color:var(--text-dim); font-style:italic;">No aliases yet</div>
            </div>
        `;

        sidebarScore.style.display = 'none';
        privacyBadge.style.display = 'none';
    });


    // ---- HELPERS ----
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
