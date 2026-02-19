# 🚀 Aayush's Complete Task List — Silent-Protocol

**Role:** Lead Engineer + Core Logic + Team Glue
**Total Estimated Time:** ~16 hours (core work + team lead duties)

---

## Phase 0: Repo & Project Setup (1 hour)

> You do this FIRST, before anyone else touches anything.

- [ ] **0.1** Create the project folder structure (5 min)
  - `/backend` (Aum's workspace)
  - `/frontend` (Divya's workspace)
  - `/core` (your workspace)
  - `/docs` (already done ✅)
- [ ] **0.2** Initialize Git repo and push to GitHub (10 min)
- [ ] **0.3** Invite Divya and Aum as collaborators on GitHub (5 min)
- [ ] **0.4** Create `backend/requirements.txt` with all dependencies (5 min)
- [ ] **0.5** Create `backend/.env.example` with `GROQ_API_KEY=your_key_here` as template (5 min)
- [ ] **0.6** Create `frontend/index.html` + `frontend/style.css` + `frontend/script.js` as empty starter files (5 min)
- [ ] **0.7** Create `core/__init__.py` (empty, so Python can import from it) (2 min)
- [ ] **0.8** Create a basic `README.md` with project name, one-liner, and "How to Run" skeleton (10 min)
- [ ] **0.9** Push everything, share repo link with team (5 min)
- [ ] **0.10** Walk Divya through: clone → open `frontend/` → start Live Server (5 min)
- [ ] **0.11** Walk Aum through: clone → create venv → pip install → get Groq key → save `.env` (5 min)

**✅ Checkpoint:** Both teammates have the repo cloned and can see their starter files.

---

## Phase 1: Core Logic — AliasManager (1.5 hours)

- [ ] **1.1** Create `core/alias_manager.py` with the `AliasManager` class (10 min)
- [ ] **1.2** Implement `__init__()`: empty `real_to_fake`, `fake_to_real` dicts, Faker instance (5 min)
- [ ] **1.3** Implement `_generate_fake(label)`: the Faker mapping table for all 11 entity types + default fallback (20 min)
- [ ] **1.4** Implement `get_or_create(entity_text, entity_label)`: check existing → generate if new → store both ways → handle collisions (20 min)
- [ ] **1.5** Implement `sanitize(text, entities)`: sort by length (longest first!) → loop → replace (15 min)
- [ ] **1.6** Implement `desanitize(text)`: sort fake_to_real by fake length (longest first!) → loop → replace (10 min)
- [ ] **1.7** Implement `get_mapping()` and `clear()` (5 min)
- [ ] **1.8** Quick manual test: create instance, add "Apple"→ORG twice → confirm same alias (5 min)

**✅ Checkpoint:** AliasManager works standalone. Aliases are consistent, bidirectional, and collision-free.

---

## Phase 2: Core Logic — Sanitizer (1 hour)

- [ ] **2.1** Install GLiNER and Faker: `pip install gliner faker` (5 min)
- [ ] **2.2** First-run: download the GLiNER model (~500MB). Wait for it to cache. (10 min)
- [ ] **2.3** Create `core/sanitizer.py` with the `Sanitizer` class (10 min)
- [ ] **2.4** Implement `__init__()`: load GLiNER model, create AliasManager, define labels list (10 min)
- [ ] **2.5** Implement `sanitize_prompt(user_prompt)`: run `predict_entities()` → pass to `alias_manager.sanitize()` → return (sanitized_text, entities) (15 min)
- [ ] **2.6** Implement `desanitize_response(llm_response)`: delegate to `alias_manager.desanitize()` (5 min)
- [ ] **2.7** Implement `get_alias_map()`: delegate to `alias_manager.get_mapping()` (5 min)

**✅ Checkpoint:** `Sanitizer("Tim Cook works at Apple")` → returns sanitized text with 0 real names.

---

## Phase 3: Test Script (45 min)

- [ ] **3.1** Create `core/test_sanitizer.py` (5 min)
- [ ] **3.2** Test 1 — Basic: sanitize a sentence with 3+ entities, verify none leak through (10 min)
- [ ] **3.3** Test 2 — Desanitize: sanitize → simulate LLM response → desanitize → verify real names restored (10 min)
- [ ] **3.4** Test 3 — Consistency: sanitize "Apple" in two messages → same alias (10 min)
- [ ] **3.5** Test 4 — Partial match: "Apple Inc" vs "Apple" — verify longest-first sorting works (10 min)
- [ ] **3.6** Run all tests → fix any failures → commit and push (5 min)

**✅ Checkpoint:** `python test_sanitizer.py` → "ALL TESTS PASSED". Push to Git. Tell Aum to pull.

---

## Phase 4: Quality Testing with Real Prompts (1 hour)

- [ ] **4.1** Legal prompt: "Draft NDA between Apple and Samsung, signed by Tim Cook in Cupertino" (10 min)
- [ ] **4.2** Medical prompt: "Patient John Smith diagnosed with Diabetes at Mayo Clinic, email john@email.com" (10 min)
- [ ] **4.3** Financial prompt: "Goldman Sachs acquired Apex for $2.3B, CEO Sarah Chen in New York" (10 min)
- [ ] **4.4** No-entity prompt: "What is 2+2?" — should pass through unchanged (5 min)
- [ ] **4.5** Multi-turn: sanitize 3 messages mentioning "Apple" → same alias all 3 times (10 min)
- [ ] **4.6** Document any entity types GLiNER misses → decide if regex fallback needed (15 min)

**✅ Checkpoint:** Core logic handles all prompt types. Known limitations documented.

---

## ☕ CHECK-IN 1 — Review Teammates (30 min)

> Stop your work. Check on Divya and Aum.

- [ ] **C1.1** Git pull → check Divya's HTML/CSS progress → give feedback (10 min)
- [ ] **C1.2** Git pull → check Aum's FastAPI server → test his `/chat` echo endpoint (10 min)
- [ ] **C1.3** Fix any issues they're stuck on (10 min)

---

## Phase 5: Backend Integration (1.5 hours)

> Plug YOUR Sanitizer into AUM's FastAPI server.

- [ ] **5.1** Help Aum add the Python path so `from core.sanitizer import Sanitizer` works in `main.py` (10 min)
- [ ] **5.2** Add the global `Sanitizer()` instance at module level in `main.py` (5 min)
- [ ] **5.3** Modify Aum's `/chat` endpoint: sanitize before Groq, desanitize after Groq (15 min)
- [ ] **5.4** Add `EntityInfo` and `ChatResponse` Pydantic models if Aum hasn't already (10 min)
- [ ] **5.5** Return full response payload: `response` + `sanitized_prompt` + `entities_detected` + `silent_mode` (10 min)
- [ ] **5.6** Update `/aliases` endpoint to return real alias map (5 min)
- [ ] **5.7** Update `/reset` endpoint to create fresh Sanitizer instance (5 min)
- [ ] **5.8** Test with curl: send "Tim Cook works at Apple" → verify response has fake names in `sanitized_prompt` and real names in `response` (15 min)
- [ ] **5.9** Fix any bugs → push (15 min)

**✅ Checkpoint:** API returns full sanitized/desanitized pipeline. Curl confirms it.

---

## ☕ CHECK-IN 2 — Team Sync (30 min)

- [ ] **C2.1** Git pull all branches / merge if needed (10 min)
- [ ] **C2.2** Review Divya's frontend — is the chat layout styled? (5 min)
- [ ] **C2.3** Review Aum's backend — is error handling solid? (5 min)
- [ ] **C2.4** Fix anything broken (10 min)

---

## Phase 6: Frontend Integration (1.5 hours)

> Wire Divya's frontend to the backend.

- [ ] **6.1** Open Divya's `script.js` — verify her `fetch` call matches the API contract (10 min)
- [ ] **6.2** Fix CORS or JSON parsing issues if any (15 min)
- [ ] **6.3** Verify: type a message → see user bubble + AI response bubble (10 min)
- [ ] **6.4** Verify: debug panel shows `sanitized_prompt` text (10 min)
- [ ] **6.5** Verify: debug panel shows colored entity tags (10 min)
- [ ] **6.6** Verify: alias map accumulates across messages (10 min)
- [ ] **6.7** Verify: reset clears everything (5 min)
- [ ] **6.8** Fix any rendering, timing, or data format bugs (20 min)

**✅ Checkpoint:** Full app works end-to-end. Type → sanitize → LLM → desanitize → display.

---

## Phase 7: Polish & Edge Cases (1.5 hours)

- [ ] **7.1** Test empty message — should not crash (5 min)
- [ ] **7.2** Test very long message (500+ words) — should work (10 min)
- [ ] **7.3** Test server-down scenario — frontend shows error gracefully (10 min)
- [ ] **7.4** Test rapid message sending — no race conditions (10 min)
- [ ] **7.5** Help Divya with any CSS alignment / mobile responsiveness issues (15 min)
- [ ] **7.6** Add startup logging in `main.py`: print model status, Groq key status (10 min)
- [ ] **7.7** Final visual review: does the app look premium? Does the debug panel pop? (15 min)
- [ ] **7.8** Clean up any console errors, warnings, or leftover debug prints (15 min)

**✅ Checkpoint:** App is polished. No crashes. Looks good.

---

## Phase 8: Demo Preparation (1 hour)

- [ ] **8.1** Choose the Hero Prompt — a compelling scenario with 4+ entities (10 min)
- [ ] **8.2** Test the Hero Prompt 3 times — ensure consistent entity detection (15 min)
- [ ] **8.3** Pre-write the 60-second pitch from the master plan (10 min)
- [ ] **8.4** Record a backup demo video in case live demo fails (15 min)
- [ ] **8.5** Full dry-run with team: Divya opens app, you narrate, Aum monitors terminal (10 min)

**✅ Checkpoint:** Demo rehearsed. Backup video recorded. Pitch memorized.

---

## Phase 9: Submission (30 min)

- [ ] **9.1** Help Aum finish the README.md: project description, setup steps, tech stack, screenshots (15 min)
- [ ] **9.2** Help Aum write the Devpost/submission text (10 min)
- [ ] **9.3** Final git push with clean commit messages (5 min)

---

## Summary Timeline

| Phase                   | Hours           | Cumulative | You Also Need          |
| :---------------------- | :-------------- | :--------- | :--------------------- |
| 0. Repo Setup           | 1.0             | 1.0        | —                      |
| 1. AliasManager         | 1.5             | 2.5        | —                      |
| 2. Sanitizer            | 1.0             | 3.5        | —                      |
| 3. Test Script          | 0.75            | 4.25       | —                      |
| 4. Quality Testing      | 1.0             | 5.25       | —                      |
| ☕ Check-in 1            | 0.5             | 5.75       | Divya + Aum's progress |
| 5. Backend Integration  | 1.5             | 7.25       | Aum's basic server     |
| ☕ Check-in 2            | 0.5             | 7.75       | —                      |
| 6. Frontend Integration | 1.5             | 9.25       | Divya's chat UI        |
| 7. Polish               | 1.5             | 10.75      | —                      |
| 8. Demo Prep            | 1.0             | 11.75      | Everyone               |
| 9. Submission           | 0.5             | 12.25      | —                      |
| **Total**               | **~12.5 hours** |            |                        |

> **Your parallel work:** Phases 0–4 are 100% independent — you don't need anyone. Check-in 1 happens around hour 6. Phases 5–6 need Aum and Divya's code. Phases 7–9 need everyone together.
