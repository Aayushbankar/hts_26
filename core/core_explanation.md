# Silent-Protocol Core: Teammate Study Guide

> Use this to understand every line so you can explain it to the judges.

---

## 1. The Big Picture (Architecture)

**"How does it work?"** explain this first:

1.  **Input**: User sends a prompt ("Dr. Sarah at Mayo Clinic...")
2.  **Layer 1 (Regex)**: `PatternScanner` catches structured data (SSN, Email, Phone, IP). It's fast and precise.
3.  **Layer 2 (AI)**: `GLiNER` model scans for semantic entities (Person, Org, Drug, Disease). It understands context.
4.  **Layer 3 (Classifier)**: `EntityClassifier` merges the two layers. If Regex says "Email" but AI says "Person", who wins? (Layer 3 decides). It also assigns the **Tier** (REPLACE / PERTURB / PRESERVE).
5.  **Layer 3.5 (Intent)**: `IntentClassifier` asks a local LLM (qwen2.5) — "is Paris a travel destination or the user's home?" If LLM is down, falls back to keyword heuristics.
6.  **Output (AliasManager)**: `AliasManager` takes the final list and replaces text in the prompt **from right to left** (offsets).
7.  **Result**: We get a sanitized string + a map to reverse it later.

---

## 2. File-by-File Walkthrough

### `sanitiser.py` (The Orchestrator)

*   **Imports**: Note the `try/except` block — this is so the code works both when you run it directly (`python sanitiser.py`) AND when its imported from backend (`from core.sanitiser import...`).
*   `self.model = GLiNER.from_pretrained(...)` loads the AI model. Takes ~5 seconds first time. We only load this ONCE when the server starts.
*   `sanitize_prompt()` is the main function. Calls regex -> NER -> classify -> intent -> score -> replace. Returns 4 things (text, entities, alias_map, score).

### `pattern_scanner.py` (Layer 1: Regex)

*   We compile regexes at class level for speed.
*   Patterns: email, phone (US + India), SSN, credit card, IP, URL, aadhaar, PAN card.
*   `scan()` runs all regexes and returns matches tagged with `source: "regex"` so Layer 3 knows they're high-confidence.

### `entity_classifier.py` (Layer 3: The Brain)

*   `classify()` does the heavy lifting:
    1.  Merges regex + NER entities
    2.  Filters false positives (e.g., "SSN" the abbreviation)
    3.  Deduplicates overlapping spans (keeps longer entity)
    4.  Assigns tier from TIER_MAP
    5.  Checks whitelists (Google, Apple, Mumbai, Paris etc. -> PRESERVE)
*   `apply_llm_intent_overrides()` calls local Qwen2.5 to classify task vs identity. Falls back to heuristic `apply_intent_overrides()` if Ollama is down.
*   `compute_privacy_score()` calculates 0-100 score based on risk weights.

### `alias_manager.py` (The Worker)

*   `sanitize_by_offsets` does replacement RIGHT-TO-LEFT. Why? If we replace "John" (4 chars) with "Christopher" (11 chars) at the beginning, all future offsets shift. Working backwards keeps early offsets valid.
*   `get_or_create` checks the `real_to_fake` dict first — if "Tim Cook" was already "James Carter", reuse it. Consistency across the conversation.
*   `_generate_person_name` is culturally + gender aware. "Priya" -> picks from south asian female pool (Kavitha, Deepa, etc), not "Karen" or "Mike".
*   `_perturb_date` shifts by +-3-7 days, guards year boundary.
*   `_perturb_money` multiplies by 0.85-1.15, keeps scale word (billion, lakh, crore) and currency symbol.

### `intent_classifier.py` (Layer 3.5: Local LLM)

*   Uses Qwen2.5 1.5B running locally via Ollama.
*   Asks the model: "given this prompt and these entities, which are task (travel, comparison) and which are identity (name, address)?"
*   Has a 3-level JSON parser because LLMs sometimes wrap responses in markdown code blocks.
*   If Ollama is down or times out, returns None and we fall back to heuristics.

---

## 3. Talking Points and Q&A

**Q: Why regex AND AI? Can't AI do it all?**
A: AI is smart but slow and sometimes misses exact formats like SSNs. Regex is precise for structured data. We need both — defense in depth.

**Q: Why 3 Tiers? Why not replace everything?**
A: If we replace "Diabetes" -> "[REDACTED]", the LLM cant give medical advice. If we replace "2026" -> "[REDACTED]", the advice is outdated. REPLACE = identities, PERTURB = dates/money, PRESERVE = domain context.

**Q: What if parsing fails?**
A: try/except blocks everywhere. If date parsing fails, we return the original value. If Ollama times out, we fall back to keyword rules. Never crashes.

**Q: How do you handle same entity appearing twice?**
A: `real_to_fake` dictionary. First time: generate alias. Second time: check dict, reuse same alias. Consistency.

**Q: What makes this better than Presidio?**
A: Presidio does `<PERSON_1>` masking. We do realistic fakes ("James Carter"), keep medical terms, and perturb dates/money mathematically instead of masking.

---

## 4. Things Judges Might Poke At

1.  **Right-to-left replacement**: "We sort by start index descending to avoid offset collision."
2.  **GLiNER loading**: "Model loads in __init__, thats why startup is 5 sec but each prompt is 0.2 sec."
3.  **Gender-aware names**: "We detect gender from known female name lists and Mrs/Ms prefix, then pick from the matching pool."
4.  **Whitelisting**: "45+ orgs and 28 cities that shouldn't be replaced even without the LLM."

---

## 5. Demo Script

1.  Run `python pitch_tests.py` in the terminal
2.  Show Test 1 — "See? Tim Cook -> James Carter. Simple."
3.  Show the medical test — "Look! Metformin stayed. Diabetes stayed. But Dr. Sarah is gone."
4.  Show the Hero Test — "This combines medical, legal, and financial all in one prompt."
