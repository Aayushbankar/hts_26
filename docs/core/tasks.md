# 🧠 Core Logic Tasks — Aayush

**Total Estimated Time:** 8–10 hours
**Deliverables:** `core/sanitizer.py`, `core/alias_manager.py`, `core/test_sanitizer.py`

---

## Task 1: Environment & Model Setup (1 hour)

- [ ] **1.1** Create the `core/` directory in the repo (5 min)
- [ ] **1.2** Install dependencies: `pip install gliner faker` (5 min)
- [ ] **1.3** Run the GLiNER model download — first import triggers a ~500MB download from HuggingFace. Open a Python shell, import GLiNER, and call `from_pretrained("urchade/gliner_medium-v2.1")`. Wait for it to finish. (10 min)
- [ ] **1.4** Test the model works: pass a sample sentence and the labels list, confirm entities are returned (15 min)
- [ ] **1.5** Test Faker works: generate a fake name, fake company, fake city. Confirm output is realistic. (5 min)
- [ ] **1.6** Decide on the entity labels list (11 labels as per design doc) and the detection threshold (0.5) (5 min)
- [ ] **1.7** Test GLiNER with each label individually — send a sentence containing that entity type and confirm detection. Note any labels that perform poorly and adjust threshold. (15 min)

**✅ Checkpoint:** GLiNER model cached. Can detect entities. Faker generates convincing fakes.

---

## Task 2: AliasManager Class (1.5 hours)

- [ ] **2.1** Create `core/alias_manager.py` with the `AliasManager` class skeleton: `__init__`, properties `real_to_fake`, `fake_to_real`, `_faker` (10 min)
- [ ] **2.2** Implement `_generate_fake(label)`: the mapping table from entity label to Faker method. Handle all 11 label types + a default fallback. (20 min)
- [ ] **2.3** Implement `get_or_create(entity_text, entity_label)`: check if alias exists → return it, otherwise generate + store in both dicts. Add collision detection (if generated fake already maps to another entity, regenerate). (20 min)
- [ ] **2.4** Implement `sanitize(text, entities)`: sort entities by text length (longest first), loop through and replace each with its alias. (15 min)
- [ ] **2.5** Implement `desanitize(text)`: sort `fake_to_real` items by fake length (longest first), loop through and replace. (10 min)
- [ ] **2.6** Implement `get_mapping()` and `clear()` utility methods. (5 min)
- [ ] **2.7** Manual test: create an AliasManager instance, call `get_or_create` with "Apple" → ORG, call again with "Apple" → should return the same alias. Call with "Google" → ORG → should return a DIFFERENT alias. (10 min)

**✅ Checkpoint:** AliasManager works standalone. Aliases are consistent and bidirectional.

---

## Task 3: Sanitizer Class (1 hour)

- [ ] **3.1** Create `core/sanitizer.py` with the `Sanitizer` class skeleton: `__init__`, properties `model`, `alias_manager`, `labels` (10 min)
- [ ] **3.2** In `__init__`: load the GLiNER model, create an AliasManager instance, define the labels list (10 min)
- [ ] **3.3** Implement `sanitize_prompt(user_prompt)`: call GLiNER's `predict_entities()` with the prompt, labels, and threshold → pass results to `alias_manager.sanitize()` → return both sanitized text and entity list (15 min)
- [ ] **3.4** Implement `desanitize_response(llm_response)`: delegate to `alias_manager.desanitize()` (5 min)
- [ ] **3.5** Implement `get_alias_map()`: delegate to `alias_manager.get_mapping()` (5 min)
- [ ] **3.6** Manual test: create a Sanitizer, sanitize "Tim Cook works at Apple in Cupertino", print the output, confirm 3 entities replaced (15 min)

**✅ Checkpoint:** Full sanitize→desanitize pipeline works. Entity detection + alias replacement verified.

---

## Task 4: Test Script (1 hour)

- [ ] **4.1** Create `core/test_sanitizer.py` as a standalone runnable script (5 min)
- [ ] **4.2** Write Test 1 — Basic Sanitization: input a sentence with 3+ entities. Verify all are detected and none appear in the sanitized output. Print original, sanitized, entities, and mapping. (15 min)
- [ ] **4.3** Write Test 2 — De-sanitization: sanitize a sentence, then simulate an LLM response using the fake aliases, de-sanitize it, verify real names are restored. (15 min)
- [ ] **4.4** Write Test 3 — Consistency: sanitize two different sentences both containing "Apple". Verify the alias is the same both times. (10 min)
- [ ] **4.5** Write Test 4 — Partial Match Edge Case: input "Apple Inc bought Samsung Electronics in San Francisco." Verify "Apple" doesn't get replaced inside "Apple Inc" incorrectly. (10 min)
- [ ] **4.6** Run all tests. Fix any failures. (5 min)

**✅ Checkpoint:** `python test_sanitizer.py` prints "ALL TESTS PASSED". Push to Git.

---

## Task 5: Prompt-Quality Testing (1.5 hours)

- [ ] **5.1** Test with a **legal** prompt: "Draft an NDA between Apple Inc and Samsung Electronics regarding Project Titan. Tim Cook and JY Lee will sign in Cupertino, California." — verify all 5+ entities detected (15 min)
- [ ] **5.2** Test with a **medical** prompt: "Patient John Smith, 45, diagnosed with Type 2 Diabetes at Mayo Clinic in Rochester. Contact: john.smith@email.com, +1-555-0199." — verify person, org, location, medical condition, email, phone all caught (15 min)
- [ ] **5.3** Test with a **financial** prompt: "Goldman Sachs acquired Apex Technologies for $2.3 billion. CEO Sarah Chen approved the deal from New York." — verify money amount, org, person, location (15 min)
- [ ] **5.4** Test with a **no-entity** prompt: "What is the square root of 144?" — verify zero entities detected, text passes through unchanged (5 min)
- [ ] **5.5** Test with a **multi-turn** conversation: sanitize 3 messages in sequence, all mentioning "Apple". Verify the same alias is used across all 3. (15 min)
- [ ] **5.6** Identify any entity types that GLiNER consistently misses. Document them as known limitations. (15 min)
- [ ] **5.7** If any entity types are unreliable, consider adding regex fallback patterns for emails, phone numbers, and dates. (15 min)

**✅ Checkpoint:** Sanitizer handles legal, medical, and financial prompts. Known limitations documented.

---

## Task 6: Integration with Backend (1.5 hours)

> ⚠️ **Coordinate with Aum.** He needs your code pushed to Git first.

- [ ] **6.1** Ensure `core/` folder has an `__init__.py` file (even if empty) so Python can import from it (5 min)
- [ ] **6.2** Push `sanitizer.py`, `alias_manager.py`, and `test_sanitizer.py` to Git (5 min)
- [ ] **6.3** Help Aum import Sanitizer into `main.py` — the path issue (`sys.path.append("../core")` or similar) will likely need debugging (15 min)
- [ ] **6.4** Test the full flow through the API: send a curl request to `/chat` with a prompt containing entities. Verify the response JSON has `response` (real names), `sanitized_prompt` (fake names), and `entities_detected` (list) (20 min)
- [ ] **6.5** Test `/aliases` endpoint: confirm it returns the current alias map after a chat message (10 min)
- [ ] **6.6** Test `/reset` endpoint: confirm aliases are cleared and new ones are generated on next message (10 min)
- [ ] **6.7** Fix any bugs found during integration (30 min buffer)

**✅ Checkpoint:** Backend API returns correct sanitized/desanitized data. All endpoints work with real Sanitizer.

---

## Task 7: Frontend Integration Support (1 hour)

> ⚠️ **Coordinate with Divya.** She will call you when her JS is ready to connect.

- [ ] **7.1** Help Divya test the `/chat` endpoint from her JavaScript fetch code. Debug CORS, JSON parsing, or response format issues. (20 min)
- [ ] **7.2** Verify the debug panel receives and renders `sanitized_prompt` and `entities_detected` correctly (15 min)
- [ ] **7.3** Verify alias map accumulates correctly across multiple messages (10 min)
- [ ] **7.4** Verify reset clears everything in both backend and frontend (10 min)
- [ ] **7.5** Fix any pipeline bugs end-to-end (5 min buffer)

**✅ Checkpoint:** Full app works: type message → see response → debug panel shows sanitized version + entities + alias map.

---

## Task 8: Demo Preparation (1 hour)

- [ ] **8.1** Choose the "Hero Prompt" for the live demo — a compelling legal/financial scenario with 4+ entities (10 min)
- [ ] **8.2** Pre-test the Hero Prompt 3 times: ensure entities are consistently detected and aliases are convincing (15 min)
- [ ] **8.3** Prepare a backup: if the live demo fails, have a pre-recorded terminal session showing the sanitization output (15 min)
- [ ] **8.4** Prepare the 60-second pitch script (from the master plan) (10 min)
- [ ] **8.5** Do a full dry-run with the team: Divya opens the frontend, you narrate, Aum handles the terminal (10 min)

**✅ Checkpoint:** Demo rehearsed. Backup ready. Pitch memorized.

---

## Summary Timeline

| Task                            | Hours          | Cumulative | Dependency           |
| :------------------------------ | :------------- | :--------- | :------------------- |
| 1. Environment & Model Setup    | 1.0            | 1.0        | None                 |
| 2. AliasManager Class           | 1.5            | 2.5        | None                 |
| 3. Sanitizer Class              | 1.0            | 3.5        | After Task 2         |
| 4. Test Script                  | 1.0            | 4.5        | After Task 3         |
| 5. Prompt-Quality Testing       | 1.5            | 6.0        | After Task 4         |
| 6. Integration with Backend     | 1.5            | 7.5        | Aum's Tasks 1–4 done |
| 7. Frontend Integration Support | 1.0            | 8.5        | Divya's Task 6 done  |
| 8. Demo Preparation             | 1.0            | 9.5        | Everything done      |
| **Total**                       | **~9.5 hours** |            |                      |

> **Critical Path:** Tasks 1–5 are independent. Task 6 needs Aum's basic server. Task 7 needs Divya's JS. Task 8 needs everything.
