# 👥 Team Tasks: Silent-Protocol (24h Sprint)

**Project:** Silent-Protocol — The Context-Aware Privacy Proxy
**Team:** Aayush (Lead/ML), Divya (Frontend/Design), Aum (Backend/API)

---

## 🎭 Role Definitions

| Who        | Domain         | Skill Level            | AI Tool to Use      | Deliverable                                     |
| :--------- | :------------- | :--------------------- | :------------------ | :---------------------------------------------- |
| **Aayush** | Core ML + Glue | Expert                 | Cursor / This Chat  | `sanitizer.py`, `alias_manager.py`, Integration |
| **Divya**  | Frontend UI    | Beginner (Canva/Figma) | ChatGPT-4o / v0.dev | `index.html`, `style.css`, `script.js`          |
| **Aum**    | Backend API    | Beginner (Python)      | ChatGPT-4 / Cursor  | `main.py` (FastAPI), Groq connection            |

---

## 🕒 Hour-by-Hour Sprint

### Phase 1: Foundation (Hours 0–4)

#### Aayush (Hours 0–4)
- [ ] Create repo structure and push to GitHub
- [ ] Install GLiNER: `pip install gliner faker`
- [ ] Write a test script: input "Tim Cook works at Apple" → output detected entities
- [ ] Write `AliasManager` class (see `core_logic_blueprint.md`)
- [ ] Test: `sanitize("My name is Aayush")` → `"My name is James Mitchell"`

#### Divya (Hours 0–4)
- [ ] Browse Dribbble for "dark mode chat UI" inspiration
- [ ] Design the chat layout in Figma/Canva (2 screens: Chat + Debug Panel)
- [ ] **AI Prompt:** *"Create a dark-themed chat interface in plain HTML and CSS. It should have a sidebar showing 'entity aliases' and a main chat area with green user bubbles and gray AI bubbles. Include a header with a toggle switch labeled 'Silent Mode'. No React, no frameworks."*
- [ ] Get `index.html` + `style.css` rendering in Live Server

#### Aum (Hours 0–4)
- [ ] Install Python 3.11, VS Code, Git
- [ ] Clone the repo
- [ ] Get a free Groq API key from https://console.groq.com
- [ ] **AI Prompt:** *"Write a Python FastAPI server with one POST endpoint `/chat` that takes a JSON body `{"message": "..."}`, sends it to Groq API using the `groq` library with model `llama-3.1-70b-versatile`, and returns the response. Include CORS middleware. Show me the full code."*
- [ ] Test: `curl -X POST localhost:8000/chat -d '{"message":"Hello"}'` returns something

---

### Phase 2: Build (Hours 4–12)

#### Aayush (Hours 4–12)
- [ ] Build the full `Sanitizer` class (GLiNER + AliasManager + Faker)
- [ ] Test with 10 different prompts (legal, medical, financial)
- [ ] Write `desanitize()` function — reverse the alias mapping on LLM responses
- [ ] **Critical:** Handle edge cases (partial matches, case sensitivity)
- [ ] Integrate `Sanitizer` into Aum's FastAPI endpoint

#### Divya (Hours 4–12)
- [ ] Add JavaScript: capture user message on "Send" button click
- [ ] **AI Prompt:** *"Write JavaScript fetch code to send a POST request to `http://localhost:8000/chat` with JSON body `{message: userInput}` and display the response in a chat bubble."*
- [ ] Add the "Debug Panel" sidebar: show "What the AI Saw" (the sanitized prompt)
- [ ] Add CSS animations: typing indicator dots, message fade-in
- [ ] **Stretch:** Add a "Detected Entities" section showing colored entity tags

#### Aum (Hours 4–12)
- [ ] Add streaming support (Server-Sent Events) to the `/chat` endpoint
- [ ] **AI Prompt:** *"Convert my FastAPI `/chat` endpoint to use StreamingResponse with Server-Sent Events. The Groq response should stream token by token."*
- [ ] Add error handling: what if Groq is down? Return a friendly error JSON.
- [ ] Add a `/health` endpoint that returns `{"status": "ok"}`
- [ ] Test with Divya's frontend: can she see streamed responses?

---

### Phase 3: Integration & Polish (Hours 12–20)

#### Aayush (Hours 12–16)
- [ ] Wire everything: Frontend → FastAPI → Sanitizer → Groq → Desanitizer → Frontend
- [ ] Fix CORS issues, JSON parsing errors, encoding bugs
- [ ] Add the "debug" data to the API response: `{"response": "...", "sanitized_prompt": "...", "entities": [...]}`

#### Divya (Hours 12–16)
- [ ] Display `sanitized_prompt` in the Debug Panel
- [ ] Display detected entities as colored pills/tags
- [ ] **AI Prompt:** *"Create CSS for colored tag badges. 'person' tags should be blue, 'organization' tags should be purple, 'location' tags should be green."*

#### Aum (Hours 12–16)
- [ ] Write `README.md`: "How to Run" (3 steps: install, API key, run)
- [ ] Take screenshots of the working app for submission
- [ ] Help test: try breaking it with weird inputs

#### Everyone (Hours 16–20)
- [ ] Polish: Fix UI bugs, alignment issues, mobile responsiveness
- [ ] Pre-process "Hero Prompt" for the live demo (a compelling legal/financial scenario)
- [ ] Record a 3-minute demo video

---

### Phase 4: Ship (Hours 20–24)

#### Aayush (Hours 20–24)
- [ ] Final rehearsal: run the demo 3 times with the "Hero Prompt"
- [ ] Prepare backup plan: pre-recorded video if live demo fails

#### Divya (Hours 20–24)
- [ ] Final CSS polish: ensure the app looks premium
- [ ] Add a landing/intro screen: project name + one-liner + "Start Chatting" button

#### Aum (Hours 20–24)
- [ ] Write Devpost submission (Problem, Solution, Tech Stack, Challenges)
- [ ] Push final code to GitHub with clean commit messages

---

## 🎯 AI Prompts Cheat Sheet

### For Divya
| Task            | Prompt to Use                                                                                    |
| :-------------- | :----------------------------------------------------------------------------------------------- |
| **Chat UI**     | *"Create a dark chat interface in HTML/CSS. User messages green, AI gray. Include a sidebar."*   |
| **Animations**  | *"Add a typing indicator animation (3 bouncing dots) in CSS."*                                   |
| **Entity Tags** | *"Create colored badge components in CSS. Blue for person, purple for org, green for location."* |
| **Debug Panel** | *"Add a collapsible sidebar that shows 'sanitized text' with a blur-to-reveal hover effect."*    |

### For Aum
| Task               | Prompt to Use                                                                           |
| :----------------- | :-------------------------------------------------------------------------------------- |
| **FastAPI**        | *"Write a FastAPI POST endpoint `/chat` that calls Groq API and returns the response."* |
| **Streaming**      | *"Convert this endpoint to use StreamingResponse with SSE."*                            |
| **CORS**           | *"Add CORSMiddleware to my FastAPI app allowing all origins."*                          |
| **Error Handling** | *"Add try/except to this endpoint. Return `{error: message}` with status 500."*         |
