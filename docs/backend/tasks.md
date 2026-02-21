# ⚙️ Backend Tasks — Aum

**Total Estimated Time:** 8–10 hours
**Deliverables:** `backend/main.py`, `backend/requirements.txt`, `backend/.env`

---

## Task 1: Environment Setup (1 hour) 

- [ ] **1.1** Install Python 3.11 (confirm with `python --version`) (10 min)
- [ ] **1.2** Install VS Code and the Python extension (10 min)
- [ ] **1.3** Install Git (confirm with `git --version`) (5 min)
- [ ] **1.4** Clone the repo and navigate to `backend/` folder (5 min)
- [ ] **1.5** Create a virtual environment: `python -m venv venv` and activate it (10 min)
- [ ] **1.6** Create `requirements.txt` with all dependencies listed in the design doc (5 min)
- [ ] **1.7** Run `pip install -r requirements.txt` — this will take 5-10 min (the torch/transformers packages are large) (10 min)
- [ ] **1.8** Sign up at https://console.groq.com, create an API key, save it in `.env` file as `GROQ_API_KEY=gsk_xxx` (5 min)

** Checkpoint:** `python -c "import fastapi; import groq; print('OK')"` prints OK.

---

## Task 2: Basic FastAPI Server (1 hour)

- [ ] **2.1** Create `main.py` with a FastAPI app instance, title "Silent-Protocol API" (10 min)
- [ ] **2.2** Add CORS middleware allowing all origins, methods, and headers (10 min)
- [ ] **2.3** Create the `ChatRequest` Pydantic model with a `message` field (5 min)
- [ ] **2.4** Create a basic `POST /chat` endpoint that accepts `ChatRequest` and returns `{"response": "echo: " + message}` (10 min)
- [ ] **2.5** Run the server with `uvicorn main:app --reload --port 8000` (5 min)
- [ ] **2.6** Test in browser: open `http://localhost:8000/docs` — Swagger UI should show the `/chat` endpoint (5 min)
- [ ] **2.7** Test with curl: `curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"message":"Hello"}'` should return the echo response (15 min)

** Checkpoint:** Server running, Swagger docs visible, curl returns echo response.

---

## Task 3: Groq LLM Integration (1.5 hours)

- [ ] **3.1** Load the `.env` file using python-dotenv at the top of `main.py` (10 min)
- [ ] **3.2** Create a global Groq client instance using the API key from the environment (10 min)
- [ ] **3.3** In the `/chat` endpoint, replace the echo response with a real Groq chat completion call using model `llama-3.1-70b-versatile` (20 min)
- [ ] **3.4** Extract the response text from `completion.choices[0].message.content` (10 min)
- [ ] **3.5** Test: curl with `{"message": "What is the capital of France?"}` should return a real AI answer (10 min)
- [ ] **3.6** Add try/except around the Groq call. If it fails, return a JSON error with status 500 (20 min)
- [ ] **3.7** Test error handling: temporarily set a wrong API key, send a request, verify you get a clean error JSON (10 min)

** Checkpoint:** Server forwards messages to Groq and returns real AI responses. Errors are handled gracefully.

---

## Task 4: Supporting Endpoints (45 min)

- [ ] **4.1** Create `GET /health` endpoint that returns `{"status": "ok", "groq_configured": true/false}` (10 min)
- [ ] **4.2** Create `GET /aliases` endpoint that returns `{"aliases": {}, "total": 0}` — placeholder until Sanitizer is integrated (10 min)
- [ ] **4.3** Create `POST /reset` endpoint that returns `{"status": "reset", "message": "All aliases cleared"}` — placeholder (10 min)
- [ ] **4.4** Test all 3 endpoints via Swagger UI or curl (15 min)

** Checkpoint:** All 4 endpoints (`/chat`, `/health`, `/aliases`, `/reset`) respond correctly.

---

## Task 5: Sanitizer Integration (2 hours)

>  **This task depends on Aayush completing the core logic.** Wait for him to push `core/sanitizer.py` and `core/alias_manager.py` before starting.

- [ ] **5.1** Add the `core/` directory to the Python path so `from sanitizer import Sanitizer` works (15 min)
- [ ] **5.2** Create a global `Sanitizer` instance at module level (this loads the GLiNER model — takes ~5 seconds) (10 min)
- [ ] **5.3** In the `/chat` endpoint:
  - Call `sanitizer.sanitize_prompt(message)` before the Groq call to get `(sanitized_text, entities)` (15 min)
  - Send `sanitized_text` to Groq instead of the raw message (10 min)
  - Call `sanitizer.desanitize_response(raw_response)` on the Groq response (10 min)
  - Build the `entities_detected` list from the entity data (15 min)
- [ ] **5.4** Create all Pydantic response models: `EntityInfo`, `ChatResponse` as described in the design doc (15 min)
- [ ] **5.5** Return the full `ChatResponse` object with `response`, `sanitized_prompt`, `entities_detected`, and `silent_mode` fields (10 min)
- [ ] **5.6** Update `/aliases` to return `sanitizer.alias_manager.get_mapping()` (5 min)
- [ ] **5.7** Update `/reset` to create a new `Sanitizer()` instance (5 min)
- [ ] **5.8** Test end-to-end: send "Tim Cook works at Apple" and verify the response contains fake names in `sanitized_prompt` and real names in `response` (20 min)

** Checkpoint:** Full pipeline works. Debug info (sanitized prompt, entities, aliases) all present in API response.

---

## Task 6: Startup & Logging (30 min)

- [ ] **6.1** Add a startup event that prints confirmation: model loaded status, Groq key status (10 min)
- [ ] **6.2** Add print/log statements in the `/chat` flow: "Received message", "Sanitized → ...", "Groq responded", "Desanitized → ..." (15 min)
- [ ] **6.3** Test: watch the terminal output while sending a request — all steps should be logged (5 min)

** Checkpoint:** Console clearly logs each step of the pipeline when a request comes in.

---

## Task 7: Testing & Hardening (1.5 hours)

- [ ] **7.1** Test with an empty message `{"message": ""}` — should not crash (10 min)
- [ ] **7.2** Test with a very long message (500+ words) — should still work (10 min)
- [ ] **7.3** Test with no entities in the message ("What is 2+2?") — should pass through without sanitization (10 min)
- [ ] **7.4** Test with the frontend connected (Divya's code) — verify CORS works, JSON parses, responses display (20 min)
- [ ] **7.5** Test the reset flow: send a message with "Apple", note the alias, click reset, send "Apple" again — should get a different alias (15 min)
- [ ] **7.6** Test consistency: send 3 messages all mentioning "Apple" — same alias every time (15 min)
- [ ] **7.7** Write the "How to Run" section of `README.md` (15 min)
  - Step 1: `pip install -r requirements.txt`
  - Step 2: Add `GROQ_API_KEY` to `.env`
  - Step 3: `uvicorn main:app --reload --port 8000`

** Checkpoint:** All edge cases handled. README written. Ready for demo.

---

## Summary Timeline

| Task                     | Hours          | Cumulative | Dependency             |
| :----------------------- | :------------- | :--------- | :--------------------- |
| 1. Environment Setup     | 1.0            | 1.0        | None                   |
| 2. Basic FastAPI Server  | 1.0            | 2.0        | None                   |
| 3. Groq Integration      | 1.5            | 3.5        | Groq API key           |
| 4. Supporting Endpoints  | 0.75           | 4.25       | None                   |
| 5. Sanitizer Integration | 2.0            | 6.25       | **Aayush's core code** |
| 6. Startup & Logging     | 0.5            | 6.75       | After Task 5           |
| 7. Testing & Hardening   | 1.5            | 8.25       | After Task 5           |
| **Total**                | **~8.5 hours** |            |                        |

> **Note:** Tasks 1–4 can be done independently while Aayush builds the core logic. Task 5 onward requires Aayush's code.
