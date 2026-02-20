/* ═══════════════════════════════════════════════════════════════
   Silent-Protocol — script.js
   Distributed Control Logic
   ═══════════════════════════════════════════════════════════════ */

const API = 'http://localhost:8000';

const LAYOUTS = {
    classified: 'layout-classified',
    messenger:  'layout-messenger',
    superchat:  'layout-superchat',
    phantom:    'layout-phantom',
    darkcom:    'layout-darkcom'
};

let currentTheme = localStorage.getItem('sp-theme') || 'classified';
let cumulativeAliases = {};
let waiting = false;
let silentMode = true; // Global state for silent mode

// ─── Layout-aware selectors ───
function q(attr) {
    const l = document.getElementById(LAYOUTS[currentTheme]);
    return l ? l.querySelectorAll(`[data-${attr}]`) : [];
}
function qAll(attr) {
    return document.querySelectorAll(`[data-${attr}]`);
}

// ═══ THEME / LAYOUT SWITCHING ═══

function setTheme(theme) {
    if (!LAYOUTS[theme]) theme = 'classified';
    
    // Hide all
    Object.values(LAYOUTS).forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';
    });
    
    // Show active
    const active = document.getElementById(LAYOUTS[theme]);
    if (active) active.style.display = 'flex';
    document.body.setAttribute('data-theme', theme);
    currentTheme = theme;
    localStorage.setItem('sp-theme', theme);

    // Sync all distributed theme switchers to reflect new theme
    document.querySelectorAll('[data-theme-switcher]').forEach(sel => {
        if (sel.value !== theme) sel.value = theme;
    });
    scrollChat();
}

// Attach event to all distributed theme switchers
document.querySelectorAll('[data-theme-switcher]').forEach(select => {
    select.addEventListener('change', e => setTheme(e.target.value));
});

// Init theme on load
setTheme(currentTheme);

// ═══ GLOBAL CONTROLS SYNC (Reset, Silent Mode, Score) ═══

// Sync silent toggles
document.querySelectorAll('[data-silent-toggle]').forEach(toggle => {
    toggle.addEventListener('change', e => {
        silentMode = e.target.checked;
        document.querySelectorAll('[data-silent-toggle]').forEach(t => t.checked = silentMode);
    });
});

// Attach event to all distributed reset buttons
document.querySelectorAll('[data-reset-btn]').forEach(btn => {
    btn.addEventListener('click', resetSession);
});

async function resetSession() {
    try { await fetch(`${API}/reset`, { method: 'POST' }); } catch(e) { console.error(e); }
    cumulativeAliases = {};
    qAll('messages').forEach(el => el.innerHTML = '');
    qAll('sanitized').forEach(el => el.textContent = 'Waiting for input...');
    qAll('entities').forEach(el => el.innerHTML = '<span class="placeholder">No entities yet</span>');
    qAll('aliases').forEach(el => el.innerHTML = '<span class="placeholder">No mappings yet</span>');
    qAll('scorecard').forEach(el => el.innerHTML = '');
    qAll('empty').forEach(el => el.style.display = 'flex');
    qAll('global-score').forEach(el => el.textContent = '--');
    qAll('entity-count').forEach(cnt => cnt.textContent = '0');
}


// ═══ HELPERS ═══

function ts() {
    return new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
}
function esc(str) {
    const d = document.createElement('div'); d.textContent = str; return d.innerHTML;
}
function scrollChat() {
    const selectors = {
        classified: '.cl-chat', messenger: '.ms-chat',
        superchat: '.sc-chat', phantom: '.ph-chat', darkcom: '.dk-chat'
    };
    const el = document.querySelector(selectors[currentTheme]);
    if (el) requestAnimationFrame(() => el.scrollTop = el.scrollHeight);
}


// ═══ MESSAGE RENDERING ═══

function addMessage(role, text) {
    q('empty').forEach(el => el.style.display = 'none');
    const html = `
        <div class="message ${role}">
            <div class="msg-head">
                <span class="msg-role">${role === 'user' ? 'YOU' : role === 'error' ? 'ERROR' : 'SILENT'}</span>
                <span class="msg-time">${ts()}</span>
            </div>
            <div class="msg-body">${esc(text)}</div>
        </div>`;
    q('messages').forEach(el => el.insertAdjacentHTML('beforeend', html));
    scrollChat();
}

function showTyping(show) {
    q('typing').forEach(el => {
        if (currentTheme === 'messenger' || currentTheme === 'darkcom') {
            el.style.display = show ? 'inline' : 'none';
        } else {
            el.style.display = show ? 'flex' : 'none';
        }
    });
    if (show) scrollChat();
}

// ═══ SCORECARD ═══

function renderScorecard(ps) {
    const score = ps.score ?? 0;
    const risk = ps.risk_level || '--';
    const barClass = risk === 'LOW' ? 'low' : risk === 'MEDIUM' ? 'medium' : 'high';
    const html = `<div style="display:flex;flex-direction:column;gap:6px;">
        <div class="sc-meter"><div class="sc-bar ${barClass}" style="width:${score}%"></div></div>
        <div style="display:flex;align-items:baseline;gap:4px">
            <span class="sc-big">${score}</span><span class="sc-label">/100 · ${risk}</span>
        </div>
        <div class="sc-row"><span class="sc-dot r"></span>Replaced: ${ps.replaced ?? 0}</div>
        <div class="sc-row"><span class="sc-dot p"></span>Perturbed: ${ps.perturbed ?? 0}</div>
        <div class="sc-row"><span class="sc-dot v"></span>Preserved: ${ps.preserved ?? 0}</div>
        <div class="sc-row"><span class="sc-dot h"></span>HIPAA: ${ps.hipaa_identifiers_protected ?? 0}/${ps.hipaa_identifiers_found ?? 0}</div>
    </div>`;
    q('scorecard').forEach(el => el.innerHTML = html);
    qAll('global-score').forEach(el => el.textContent = `${score}/100`);
}

// ═══ DEBUG STRIP DATA ═══

function updateDebug(data) {
    q('sanitized').forEach(el => el.textContent = data.sanitized_prompt || 'No data');

    const entities = data.entities_detected || [];
    qAll('entity-count').forEach(cnt => cnt.textContent = entities.length);
    
    q('entities').forEach(c => {
        if (!entities.length) { c.innerHTML = '<span class="placeholder">No entities</span>'; return; }
        c.innerHTML = '';
        entities.forEach(e => {
            const t = document.createElement('div');
            t.className = 'entity-tag';
            t.setAttribute('data-tier', e.tier || 'UNKNOWN');
            t.innerHTML = `<span>${esc(e.text)}</span><span class="tier-badge">${e.tier || '?'}</span>`;
            c.appendChild(t);
        });
    });

    entities.forEach(e => {
        if (e.text !== e.alias && e.tier === 'REPLACE') cumulativeAliases[e.text] = e.alias;
    });
    
    q('aliases').forEach(c => {
        const keys = Object.keys(cumulativeAliases);
        if (!keys.length) { c.innerHTML = '<span class="placeholder">No mappings</span>'; return; }
        c.innerHTML = '';
        keys.forEach(real => {
            const r = document.createElement('div');
            r.className = 'alias-row';
            r.innerHTML = `<span class="alias-real">${esc(real)}</span><span class="alias-arrow">→</span><span class="alias-fake">${esc(cumulativeAliases[real])}</span>`;
            c.appendChild(r);
        });
    });

    if (data.privacy_score) renderScorecard(data.privacy_score);
}

// ═══ CHAT SUBMISSION ═══

document.querySelectorAll('[data-form]').forEach(f => f.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = e.target.querySelector('[data-input]');
    const text = input.value.trim();
    if (!text || waiting) return;

    addMessage('user', text);
    input.value = '';
    
    // Focus back on the specific active input
    input.focus();
    
    waiting = true;
    showTyping(true);

    try {
        const res = await fetch(`${API}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text }) // backend ignores silent toggle logic anyway, but in reality we'd pass it.
        });
        showTyping(false);
        if (!res.ok) { throw new Error(`HTTP ${res.status}`); }
        const data = await res.json();
        addMessage('assistant', data.response || 'No response.');
        updateDebug(data);
    } catch (err) {
        showTyping(false);
        addMessage('error', `Error: ${err.message}`);
    } finally { waiting = false; }
}));

// ═══ MESSENGER TAB SWITCHING ═══

document.querySelectorAll('[data-ms-tab]').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.ms-tab').forEach(t => t.classList.remove('active', 'ms-tab-active'));
        document.querySelectorAll('.ms-tab-content').forEach(p => p.classList.remove('active'));
        tab.classList.add('active', 'ms-tab-active');
        const panel = document.querySelector(`[data-ms-panel="${tab.dataset.msTab}"]`);
        if (panel) panel.classList.add('active');
    });
});

// ═══ DARKCOM ICON CYCLING ═══

document.querySelectorAll('.dk-icon-top .dk-icon').forEach(icon => {
    icon.addEventListener('click', (e) => {
        document.querySelectorAll('.dk-icon-top .dk-icon').forEach(i => i.classList.remove('dk-icon-active'));
        e.target.classList.add('dk-icon-active');
    });
});

// ═══ KEYBOARD SHORTCUTS ═══

document.addEventListener('keydown', e => {
    if (e.ctrlKey && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        const themes = Object.keys(LAYOUTS);
        setTheme(themes[(themes.indexOf(currentTheme) + 1) % themes.length]);
    }
    if (e.ctrlKey && e.shiftKey && e.key === 'R') {
        e.preventDefault();
        resetSession();
    }
});

q('input')[0]?.focus();
