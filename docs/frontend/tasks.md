#  Frontend Tasks — Divya

**Total Estimated Time:** 10–12 hours
**Deliverables:** `frontend/index.html`, `frontend/style.css`, `frontend/script.js`

---

## Task 1: Setup & Inspiration (1 hour)

- [ ] **1.1** Install VS Code and the "Live Server" extension (15 min)
- [ ] **1.2** Clone the GitHub repo and navigate to the `frontend/` folder (10 min)
- [ ] **1.3** Create 3 empty files: `index.html`, `style.css`, `script.js` (5 min)
- [ ] **1.4** Open `index.html` in Live Server to confirm it works (5 min)
- [ ] **1.5** Browse Dribbble/Pinterest for "dark mode chat UI" and "cybersecurity dashboard" designs — pick 2-3 references (25 min)

---

## Task 2: HTML Structure (1.5 hours)

- [ ] **2.1** Write the base HTML skeleton: `<!DOCTYPE>`, `<head>` with Google Fonts links (JetBrains Mono + Instrument Sans), `<body>` (15 min)
- [ ] **2.2** Build the Header section: logo area (lock icon + title), controls area (toggle switch placeholder + reset button) (20 min)
- [ ] **2.3** Build the Main layout: chat area `<main>` and debug panel `<aside>` side by side (15 min)
- [ ] **2.4** Build the Empty State inside the chat area: lock icon + title + subtitle centered (10 min)
- [ ] **2.5** Build the Input Bar: `<form>` with text input and send button at the bottom (15 min)
- [ ] **2.6** Build the Debug Panel: 3 sections with headers ("What AI Sees", "Entities Detected", "Alias Map") (15 min)

** Checkpoint:** Open in Live Server. You should see the full page layout (ugly but structured).

---

## Task 3: CSS — Base Theme & Layout (2 hours)

- [ ] **3.1** Define all CSS custom properties (variables) for colors, fonts, and spacing as described in the design doc (20 min)
- [ ] **3.2** Set global styles: body background, font-family, box-sizing, margin reset (10 min)
- [ ] **3.3** Style the Header: fixed position, height 56px, flex layout, border-bottom, logo glow effect (20 min)
- [ ] **3.4** Style the Main layout: flex container, chat area takes remaining space, debug panel fixed at 340px (15 min)
- [ ] **3.5** Style the Input Bar: fixed bottom, flex layout, input styling with focus ring, send button with green background (20 min)
- [ ] **3.6** Style the Debug Panel: background, left border, section padding, section headers, separator borders (20 min)
- [ ] **3.7** Style the Empty State: centered vertically and horizontally, icon size, text colors (15 min)

** Checkpoint:** Page should look like the wireframe in the design doc — dark theme, correct layout, correct fonts.

---

## Task 4: CSS — Chat Bubbles & Entity Tags (1.5 hours)

- [ ] **4.1** Style User message bubble: left green border, elevated background, role header + timestamp, padding, max-width 85% (20 min)
- [ ] **4.2** Style AI message bubble: left gray border, surface background, same header layout (15 min)
- [ ] **4.3** Style Error message bubble: left red border, red text (10 min)
- [ ] **4.4** Style Entity tag pills: rounded rectangle, per-type colors (mint, lavender, amber, blue, coral) with transparency backgrounds and borders (20 min)
- [ ] **4.5** Style Alias Map rows: monospace text, green arrow between real→fake names (15 min)
- [ ] **4.6** Style the custom Toggle Switch: track, knob, ON/OFF states, label (20 min)

** Checkpoint:** Add a couple of hardcoded test message divs to the HTML. They should render as proper styled bubbles.

---

## Task 5: CSS — Animations (45 min)

- [ ] **5.1** Message appear animation: fade-in + slide-up, 300ms (10 min)
- [ ] **5.2** Typing indicator: 3 bouncing dots in a row, sequential delay (15 min)
- [ ] **5.3** Entity tag pop-in: scale 0.8→1 + fade, 200ms (5 min)
- [ ] **5.4** Send button hover glow: green box-shadow on hover (5 min)
- [ ] **5.5** Input field focus transition: border color change + shadow (5 min)
- [ ] **5.6** Toggle switch slide animation: knob moves left/right, 150ms (5 min)

** Checkpoint:** Hover over the send button (glow), click the toggle (slides), see the dots bounce.

---

## Task 6: JavaScript — Core Logic (2 hours)

- [ ] **6.1** `sendMessage()`: read input → display user bubble → clear input → show typing indicator → fetch POST to `/chat` → hide indicator → display AI bubble → update debug panel. Handle errors. (40 min)
- [ ] **6.2** `displayMessage(text, type)`: create message `<div>` with header (role + timestamp) and body, append to chat area, auto-scroll to bottom (20 min)
- [ ] **6.3** `updateDebugPanel(data)`: set sanitized text in "What AI Sees", create entity tags in "Entities", add rows to "Alias Map" (cumulative) (20 min)
- [ ] **6.4** `showTypingIndicator()` / `hideTypingIndicator()`: add/remove the 3-dot animation div from chat area (10 min)
- [ ] **6.5** `resetSession()`: POST to `/reset`, clear chat, clear debug panel, show empty state (15 min)
- [ ] **6.6** `toggleSilentMode()`: toggle visual state (for MVP, cosmetic only) (10 min)
- [ ] **6.7** Wire up all event listeners: form submit, reset button click, toggle change (5 min)

** Checkpoint:** Type a message, see a user bubble appear, see typing dots, see an AI response (requires backend running). Debug panel updates.

---

## Task 7: Polish & Edge Cases (1.5 hours)

- [ ] **7.1** Test with long messages: ensure bubbles wrap text correctly, no overflow (15 min)
- [ ] **7.2** Test with empty input: send button should do nothing (5 min)
- [ ] **7.3** Test with server down: error message should appear gracefully (10 min)
- [ ] **7.4** Test rapid sending: typing indicator shouldn't stack (10 min)
- [ ] **7.5** Mobile responsiveness: debug panel collapses on narrow screens (20 min)
- [ ] **7.6** Final visual polish: spacing, alignment, font sizes, color consistency (30 min)

** Checkpoint:** The app looks premium and handles edge cases gracefully.

---

## Task 8: Landing/Intro Screen (30 min)

- [ ] **8.1** Add a simple intro overlay: project name "Silent-Protocol", one-liner tagline, "Start Chatting →" button (20 min)
- [ ] **8.2** Button click dismisses the overlay and reveals the chat interface (10 min)

---

## Summary Timeline

| Task                   | Hours         | Cumulative |
| :--------------------- | :------------ | :--------- |
| 1. Setup & Inspiration | 1.0           | 1.0        |
| 2. HTML Structure      | 1.5           | 2.5        |
| 3. CSS Base Theme      | 2.0           | 4.5        |
| 4. CSS Bubbles & Tags  | 1.5           | 6.0        |
| 5. CSS Animations      | 0.75          | 6.75       |
| 6. JavaScript          | 2.0           | 8.75       |
| 7. Polish              | 1.5           | 10.25      |
| 8. Intro Screen        | 0.5           | 10.75      |
| **Total**              | **~11 hours** |            |
