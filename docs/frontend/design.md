#  Frontend Design Document: Silent-Protocol

**Owner:** Divya
**Deliverables:** `index.html`, `style.css`, `script.js`
**Stack:** Vanilla HTML + CSS + JavaScript (no frameworks)
**Preview Tool:** VS Code Live Server extension

---

## 1. Design Direction

### Aesthetic: "Classified Intelligence Terminal"

The app should feel like logging into a secure government terminal — dark, sharp, and deliberately intimidating in its precision. NOT a friendly chatbot. NOT a ChatGPT clone. This is a **defense-grade privacy tool** and it must look like one.

**Tone:** Refined brutalism meets intelligence agency dashboard.
**What makes it unforgettable:** The Debug Panel that shows what the AI *actually* saw (the sanitized version) next to what the user typed — this side-by-side is the entire demo selling point.

### Design Principles
1. **Dark & Dense:** No white backgrounds. Everything lives in near-black (#05060a).
2. **Monospace Code Feel:** All chat text and debug text in a monospace font. Not friendly — *trustworthy*.
3. **Green-on-Black Accents:** Neon green (#00ff88) as the primary accent. Signals "active, secure, go."
4. **Information Density:** The debug panel is not hidden. It's prominently visible at all times on desktop — it IS the product.

---

## 2. Typography

### Font Choices

| Role                | Font Family                        | Why                                                                              |
| :------------------ | :--------------------------------- | :------------------------------------------------------------------------------- |
| **Display/Headers** | **Instrument Sans** (Google Fonts) | Clean, modern, slightly technical feel. Distinct from generic Inter/Roboto.      |
| **Body/Mono**       | **JetBrains Mono** (Google Fonts)  | Purpose-built coding font. Excellent readability. Signals "technical precision." |

### Font Size Scale

| Element                        | Font            | Weight          | Size |
| :----------------------------- | :-------------- | :-------------- | :--- |
| App title ("Silent-Protocol")  | Instrument Sans | Bold (700)      | 24px |
| Section headers (panel titles) | Instrument Sans | Semi-Bold (600) | 16px |
| Chat message text              | JetBrains Mono  | Regular (400)   | 14px |
| Entity tag labels              | JetBrains Mono  | Medium (500)    | 12px |
| Input placeholder              | JetBrains Mono  | Regular (400)   | 14px |
| Debug panel text               | JetBrains Mono  | Regular (400)   | 12px |
| Button labels                  | Instrument Sans | Semi-Bold (600) | 14px |
| Timestamps                     | JetBrains Mono  | Regular (400)   | 11px |

---

## 3. Color System

### Background Colors (Darkest → Lightest)

| Name     | Hex       | Usage                                |
| :------- | :-------- | :----------------------------------- |
| Void     | `#05060a` | Page body, deepest background        |
| Surface  | `#0c0e14` | Chat area, debug panel backgrounds   |
| Elevated | `#141620` | Message bubbles, input field, cards  |
| Hover    | `#1c1f2e` | Hover states on buttons and elements |

### Text Colors

| Name    | Hex       | Usage                                   |
| :------ | :-------- | :-------------------------------------- |
| Primary | `#c8ccd8` | Main readable text                      |
| Muted   | `#5c6178` | Secondary info, timestamps, placeholder |
| Ghost   | `#2e3142` | Barely-visible hints, disabled states   |

### Accent Colors

| Name       | Hex                     | Usage                                                      |
| :--------- | :---------------------- | :--------------------------------------------------------- |
| Neon Green | `#00ff88`               | Primary accent: active states, send button, user indicator |
| Dim Green  | `#00cc6a`               | Borders, focus rings                                       |
| Green Glow | `#00ff88` at 8% opacity | Subtle glow behind active elements                         |

### Entity Tag Colors

| Entity Type  | Color      | Hex       |
| :----------- | :--------- | :-------- |
| Person       | Soft Mint  | `#6ee7b7` |
| Organization | Lavender   | `#a78bfa` |
| Location     | Warm Amber | `#fbbf24` |
| Date         | Sky Blue   | `#60a5fa` |
| All Others   | Coral      | `#f87171` |

Each entity tag should have its color at 10% opacity as background and 30% opacity as border.

### Utility Colors

| Name          | Hex                      | Usage                        |
| :------------ | :----------------------- | :--------------------------- |
| Border Subtle | `#1a1d2b`                | Panel dividers, card borders |
| Border Active | `#00ff88` at 20% opacity | Active/focus borders         |
| Danger Red    | `#ff3b3b`                | Error messages               |

---

## 4. Page Layout

### Overall Structure

The page is a fixed-viewport, three-section layout:
- **Header:** Fixed to top, 56px height
- **Main Area:** Split into Chat (left, fills remaining space) and Debug Panel (right, fixed 340px width)
- **Input Bar:** Fixed to bottom, 64px height

The main area sits between header and input bar, and scrolls independently.

### Desktop Layout (> 1024px)

```
------------------------------------------------------------------------
- HEADER (56px, fixed top, full width)                                 -
-  Left: Lock icon + "Silent-Protocol" + "v0.1" badge                  -
-  Right: Silent Mode toggle switch + "Reset Session" button           -
------------------------------------------------------------------------
-                                          -                           -
-  CHAT AREA                               -  DEBUG PANEL (340px)      -
-  (flex: 1, vertically scrollable)        -  (fixed width, scrollable)-
-                                          -                           -
-  Messages appear here as bubbles.        -  Section 1: "WHAT AI SEES"-
-  Auto-scrolls to bottom on new message.  -   Shows the sanitized     -
-                                          -   prompt text             -
-                                          -                           -
-                                          -  Section 2: "ENTITIES"    -
-                                          -   Colored pill tags for   -
-                                          -   each detected entity    -
-                                          -                           -
-                                          -  Section 3: "ALIAS MAP"   -
-                                          -   Table of real → fake    -
-                                          -   name mappings           -
-                                          -                           -
--------------------------------------------                           -
- INPUT BAR (64px, fixed bottom)           -                           -
-  Text input (fills space) + Send button  -                           -
------------------------------------------------------------------------
```

### Tablet (768px – 1024px)
- Debug Panel collapses to a sliding tab accessible from the right edge
- Chat area takes full width

### Mobile (< 768px)
- Debug Panel hidden entirely, accessible as a bottom sheet overlay
- Input bar uses full width

---

## 5. Component Specifications

### 5.1 Header Bar

| Property   | Value                                            |
| :--------- | :----------------------------------------------- |
| Height     | 56px                                             |
| Position   | Fixed top, full width                            |
| Background | Surface color with bottom border (Subtle border) |
| Z-index    | 100 (above all content)                          |

**Left Section:**
- Lock emoji () with a faint neon green text-shadow glow
- Title "Silent-Protocol" in Instrument Sans, Bold, 24px
- Version badge "v0.1" — tiny pill in muted text

**Right Section:**
- Toggle switch for "Silent Mode": 36px × 20px track, green when ON, gray when OFF, with label text to the left
- "Reset Session" button: ghost style (transparent background, muted border, muted text). On hover → border brightens.

### 5.2 Chat Message Bubbles

**User Messages:**
| Property      | Value                                                            |
| :------------ | :--------------------------------------------------------------- |
| Alignment     | Full width (not right-aligned, this is a terminal, not iMessage) |
| Left border   | 3px solid Neon Green                                             |
| Background    | Elevated color                                                   |
| Border radius | 0px top-left, 6px on other corners                               |
| Max width     | 85% of chat area                                                 |
| Padding       | 12px 16px                                                        |

**AI Messages:**
| Property        | Value                      |
| :-------------- | :------------------------- |
| Left border     | 3px solid Muted text color |
| Background      | Surface color              |
| Everything else | Same as user messages      |

**Both have a header row inside the bubble:**
- Left: role label (● YOU or ○ SILENT-PROTOCOL) in the respective accent color
- Right: timestamp (e.g., "12:05 PM") in muted text, 11px

**Error Messages:**
- Left border: Danger Red
- Text in Danger Red

### 5.3 Empty State (Before First Message)

When no messages exist, center this in the chat area:
- Large lock icon () at 48px
- Title: "Type a message. We'll handle the secrets." — Primary text color
- Subtitle: "Your data never reaches the AI. We replace sensitive information with realistic fakes before forwarding." — Muted text color
- Both centered vertically and horizontally

### 5.4 Typing Indicator

Three small circles (6px diameter) in neon green, spaced 8px apart. They animate in a sequential bouncing pattern:
- Each dot moves up 8px and back, with 0.15s delay between each dot
- Full cycle: 1.2 seconds
- Dots are at 40% opacity normally, peak at 100% opacity when at the top of the bounce

Appears at the bottom of the chat area while waiting for a response. Disappears when the response arrives.

### 5.5 Input Bar

| Property                     | Value                                                         |
| :--------------------------- | :------------------------------------------------------------ |
| Height                       | 64px                                                          |
| Position                     | Fixed bottom, full width (minus debug panel width on desktop) |
| Background                   | Surface color with top border                                 |
| Layout                       | Text input (fills remaining space) + Send button              |
| Padding                      | 12px                                                          |
| Gap between input and button | 8px                                                           |

**Text Input:**
- Background: Elevated color
- Border: 1px solid Subtle border
- On focus: border color changes to Dim Green, subtle green glow shadow
- Placeholder text: "Type your message..." in Muted color
- Font: JetBrains Mono, 14px
- Border radius: 6px
- Padding: 0 16px

**Send Button:**
- Background: Neon Green
- Text: Black (#000), "SEND →", Instrument Sans Semi-Bold 14px
- Border radius: 6px
- Padding: 0 20px
- On hover: gains a box-shadow glow in green at low opacity
- Min-width: 80px

### 5.6 Debug Panel

| Property    | Value                                             |
| :---------- | :------------------------------------------------ |
| Width       | 340px (fixed)                                     |
| Position    | Right side, full height between header and bottom |
| Background  | Void color (slightly darker than chat area)       |
| Left border | 1px solid Subtle border                           |
| Overflow    | Independently scrollable                          |

**Contains 3 sections, each separated by a subtle border-bottom:**

**Section 1: "📡 WHAT AI SEES"**
- Title: Instrument Sans, Semi-Bold, 16px, Muted color
- Content: monospace pre-formatted block showing the sanitized prompt
- Text color: Muted (dimmer than chat — this is "secondary" info)
- Updates every time a new message is sent

**Section 2: " ENTITIES DETECTED"**
- Title: same style as above
- Content: a vertical list of entity tag pills (see 5.7)
- Each tag shows: `[entity text]` + entity type label
- Updates with each new message

**Section 3: "🔗 ALIAS MAP"**
- Title: same style as above
- Content: a vertical list of rows in the format: `Real Name → Fake Name`
- The arrow (→) is styled in Neon Green
- This is cumulative (grows across the session)

### 5.7 Entity Tags

Small pill-shaped badges. Each entity type has its own color (see Section 3).

| Property   | Value                                      |
| :--------- | :----------------------------------------- |
| Shape      | Rounded rectangle, border-radius 4px       |
| Padding    | 2px horizontal, 8px vertical               |
| Font       | JetBrains Mono, 12px, Medium weight        |
| Background | Entity type color at 10% opacity           |
| Border     | 1px solid entity type color at 30% opacity |
| Text color | Entity type color at full opacity          |
| Layout     | Inline, wrapping, 4px gap between tags     |

**Format inside the tag:** `Apple Inc  ORG` — entity text, then space, then type abbreviation (PER, ORG, LOC, DATE, etc.) in slightly smaller text.

### 5.8 Toggle Switch

A custom-styled checkbox made to look like an iOS-style toggle.

| Property   | Value                                                     |
| :--------- | :-------------------------------------------------------- |
| Track size | 36px × 20px                                               |
| Knob size  | 16px circle                                               |
| OFF state  | Track: #2a2a3e (dark gray), Knob: left-aligned            |
| ON state   | Track: Neon Green, Knob: right-aligned, green glow        |
| Transition | 150ms ease                                                |
| Label      | "Silent Mode" text to the left of the toggle, Muted color |

---

## 6. Animations

| Animation             | Trigger                       | Duration  | Style                                                             |
| :-------------------- | :---------------------------- | :-------- | :---------------------------------------------------------------- |
| **Message Appear**    | New message added to chat     | 300ms     | Fade in (0→1 opacity) + slide up (8px→0 translateY) with ease-out |
| **Typing Dots**       | Waiting for API response      | 1.2s loop | 3 dots bounce upward sequentially, 0.15s stagger                  |
| **Entity Tag Pop**    | New entity detected           | 200ms     | Scale from 0.8→1 + fade in, with a slight overshoot (ease-back)   |
| **Debug Panel Slide** | Toggle panel on tablet/mobile | 250ms     | Slide in from right edge                                          |
| **Send Button Glow**  | Mouse hover on Send button    | 200ms     | Green box-shadow fades in                                         |
| **Toggle Slide**      | Click silent mode toggle      | 150ms     | Knob slides left↔right, track color transitions                   |
| **Focus Ring**        | Input field receives focus    | 150ms     | Border color transitions to green, subtle shadow appears          |

---

## 7. JavaScript Behavior

### 7.1 Message Sending Flow

**Trigger:** User submits the form (clicks Send or presses Enter)

**Steps:**
1. Read the text from the input field
2. If text is empty or whitespace only, do nothing
3. Display the text as a "user" message bubble in the chat
4. Clear the input field
5. Show the typing indicator at the bottom of the chat
6. Send an HTTP POST request to `http://localhost:8000/chat` with the message in JSON body format `{"message": "..."}`
7. When the response arrives, hide the typing indicator
8. Display the `response` field from the API as an "AI" message bubble
9. Call the debug panel update function with the full API response data
10. If the request fails (network error, server error), hide the typing indicator and display an error message bubble

### 7.2 Debug Panel Update

**Trigger:** Called after every successful API response

**Steps:**
1. Take the `sanitized_prompt` string from the response and display it in the "What AI Sees" section
2. Take the `entities_detected` array from the response:
   - For each entity, create an entity tag pill with the appropriate color based on the entity's `label` field
   - Display all tags in the "Entities Detected" section
3. Take the `entities_detected` array again:
   - For each entity, create a row showing `text → alias` (real name → fake name)
   - Display all rows in the "Alias Map" section
   - This section is **cumulative** — new entries add to existing ones (don't clear previous)

### 7.3 Silent Mode Toggle

**Trigger:** User clicks the toggle switch

**Behavior:**
- When OFF: the header could show a subtle red tint or warning indicator, and messages are sent without sanitization (future feature — for MVP, it's always ON)
- For the hackathon MVP, this toggle is **visual-only** (cosmetic). Sanitization always runs.

### 7.4 Session Reset

**Trigger:** User clicks the "Reset Session" button

**Steps:**
1. Send an HTTP POST to `http://localhost:8000/reset`
2. Clear all messages from the chat area
3. Clear all content from the debug panel (sanitized display, entity list, alias map)
4. Show the empty state again

### 7.5 Auto-Scroll

After every new message or typing indicator is added, the chat area must scroll to the bottom automatically so the latest content is always visible.

### 7.6 Timestamp Generation

Each message bubble displays a timestamp. Generate this client-side using the current time in 12-hour format (e.g., "12:05 PM"). No need for server timestamps.

---

## 8. API Integration Summary

The frontend communicates with the backend at `http://localhost:8000`. Here is what the frontend should expect:

### Sending a Message
- **URL:** `POST http://localhost:8000/chat`
- **Send:** `{"message": "user's text here"}`
- **Receive:** `{"response": "...", "sanitized_prompt": "...", "entities_detected": [...], "silent_mode": true}`
- The `entities_detected` array contains objects with `text`, `label`, and `alias` fields.

### Resetting the Session
- **URL:** `POST http://localhost:8000/reset`
- **Send:** nothing (empty body)
- **Receive:** `{"status": "reset", "message": "All aliases cleared"}`

### Checking Server Health (Optional)
- **URL:** `GET http://localhost:8000/health`
- **Receive:** `{"status": "ok", "model_loaded": true, "groq_configured": true}`

---

## 9. AI Prompts for Divya

These are copy-paste-ready prompts for Divya to use with ChatGPT/Claude to generate her code:

### Prompt 1: Full Page Layout
> "Create a single-page dark chat application in HTML, CSS, and JavaScript. Use JetBrains Mono from Google Fonts for all text and Instrument Sans for headers. The page has: a fixed header (56px) with title 'Silent-Protocol' and a toggle switch, a main area split into a left chat area and a right debug sidebar (340px wide), and a fixed bottom input bar (64px) with a text field and green send button. Background color: #05060a. No React, no frameworks, no Tailwind."

### Prompt 2: Chat Bubbles + Animations
> "Add chat message bubbles to my chat app. User messages have a 3px neon green (#00ff88) left border with dark (#141620) background. AI messages have a gray left border. Each bubble has a header row with the sender name and timestamp. Messages should fade in and slide up when they appear. Also add a typing indicator with 3 small bouncing green dots that appears while waiting for a response."

### Prompt 3: Debug Panel Content
> "In my chat app's right sidebar, add 3 sections separated by borders: First section titled '📡 WHAT AI SEES' with a monospace pre-formatted text block. Second section titled ' ENTITIES DETECTED' with colored pill-shaped tags (mint for person, lavender for organization, amber for location). Third section titled '🔗 ALIAS MAP' showing rows of 'Real Name → Fake Name' with the arrow in green."

### Prompt 4: JavaScript Fetch Logic
> "Add JavaScript to my chat app: when the form is submitted, POST to http://localhost:8000/chat with JSON body containing the message. The API returns response, sanitized_prompt, and entities_detected. Display the response as an AI bubble, show the sanitized_prompt in the debug panel, and create colored entity tags for each detected entity. Also add a reset button that POSTs to /reset and clears everything."
