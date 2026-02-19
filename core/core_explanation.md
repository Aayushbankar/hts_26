# 🧠 Silent-Protocol Core: Teammates Study Guide

> **Your 4-Hour Crash Course**: Use this guide to explain every line of code to Aum (Backend) and the Frontend team.

---

## 🏗️ 1. The Big Picture (Architecture)

**"How does it work?"** explain this first:

1.  **Input**: User sends a prompt ("Dr. Sarah at Mayo Clinic...")
2.  **Layer 1 (Regex)**: `PatternScanner` catches structured data (SSN, Email, Phone, IP). It's fast and precise.
3.  **Layer 2 (AI)**: `GLiNER` model scans for semantic entities (Person, Org, Drug, Disease). It understands context.
4.  **Layer 3 (Classifier)**: `EntityClassifier` merges the two layers. If Regex says "Email" but AI says "Person", who wins? (Layer 3 decides). It also assigns the **Tier** (REPLACE / PERTURB / PRESERVE).
5.  **Output (AliasManager)**: `AliasManager` takes the final list and replaces text in the prompt **from right to left** (offsets).
6.  **Result**: We get a sanitized string + a map to reverse it later.

---

## 📂 2. File-by-File Walkthrough

### 📄 `sanitiser.py` (The Orchestrator)

*   **Line 11-15**: Imports. Note the `try/except` block – this is a **hack** to make the code work both when you run it directly (`python sanitiser.py`) AND when Aum imports it in backend (`from core.sanitiser import...`).
*   **Line 19**: `self.model = GLiNER.from_pretrained(...)`. This loads the AI. It takes ~5 seconds the first time. **Crucial**: We only load this ONCE when the server starts, not for every request.
*   **Line 40**: `sanitize_prompt(self, user_prompt)`. The main function.
    *   **Step 1**: Run Regex (`scan`).
    *   **Step 2**: Run AI (`predict_entities`).
    *   **Step 3**: `classify` (Merge & Deduplicate).
    *   **Step 4**: `compute_privacy_score` (The 0-100 score).
    *   **Step 5**: `sanitize_by_offsets` (The actual text replacement).
*   **Return**: Returns 4 things! Text, Entities, AliasMap, PrivacyScore. Aum needs all 4.

### 📄 `pattern_scanner.py` (Layer 1: Regex)

*   **Line 8**: `__init__`. We compile regexes here. `re.compile` makes them faster because we use them thousands of times.
*   **Line 9-15**: The actual patterns.
    *   `EMAIL`: Standard email regex.
    *   `PHONE`: Looks for `+1-` or `(555)` formats.
    *   `SSN`: Checks for `XXX-XX-XXXX`.
    *   `CREDIT_CARD`: Looks for 13-19 digits, often with dashes/spaces.
    *   `IPV4`: Looks for `x.x.x.x`.
    *   `URL`: Looks for `http` or `www`.
*   **Line 28**: `scan(self, text)`. Runs all regexes one by one.
*   **Line 35**: **Crucial**: `entity.setdefault("source", "regex")`. We tag these as "regex" so Layer 3 knows they are high-confidence structured data.

### 📄 `entity_classifier.py` (Layer 3: The Brain)

*   **Line 35**: `classify(...)`.
    1.  **Normalize**: Converts everything to a standard dictionary format.
    2.  **Filter**: `_is_false_positive`.
        *   *Logic*: If regex finds "SSN" (the word) but marks it as an SSN entity, we ignore it. We only want the *number*.
        *   *Logic*: Removes trailing periods ("Hello.").
    3.  **Deduplicate**: `_deduplicate_overlaps`. **This is the hardest part.**
        *   *Problem*: Regex finds "John Smith" (as 2 words). AI finds "John Smith" (as Person). Who wins?
        *   *Algorithm*: **Interval Scheduling**. We sort by start position. If two entities overlap (share characters), we pick the **longer one**.
    4.  **Tier Assignment**: `_assign_tier`.
        *   Look up the label in our 3 lists (REPLACE, PERTURB, PRESERVE).
*   **Line 144**: `compute_privacy_score`.
    *   Starts at 100.
    *   Deducts points for every sensitive entity found.
    *   Adds points back if we successfully anonymized it.
    *   Checks specifically for HIPAA identifiers (Names, Dates, SSN, etc.).

### 📄 `alias_manager.py` (The Worker)

*   **Line 17**: `__init__`. Sets up `Faker` (for fake names) and `_name_blocklist` (to avoid bad fake names).
*   **Line 82**: `sanitize_by_offsets`. **Explain this visualization**:
    *   Text: `Hello [John]!` (John is at index 6-10)
    *   We slice: `text[:start]` + `replacement` + `text[end:]`
    *   **Critical**: We MUST do this **Reverse (Right-to-Left)**.
    *   *Why?* If we replace "John" (4 chars) with "Christopher" (11 chars) at the *beginning*, all the future offsets shift by +7. By working backwards, the early offsets stay valid.
*   **Line 132**: `_generate_replacement`.
    *   **Tier 1 (REPLACE)**:
        *   `person`: Uses `_generate_person_name`.
        *   `email`: Generates `fake_email`.
        *   Checks `real_to_fake` map first! If "Tim Cook" was already "James Carter", **reuse it**. Consistency!
*   **Line 299**: `_generate_person_name` (**New!**).
    *   **Cultural Awareness**: Checks the original name against lists of common Indian/Chinese/Korean names.
    *   *Example*: If input is "Priya", it picks from `_SOUTH_ASIAN_FIRST` (e.g., "Kavitha"). It doesn't turn "Priya" into "Karen".
*   **Line 214**: `_perturb_date`.
    *   Parses date with `dateutil`.
    *   Adds random `random.randint(-7, 7)` days.
    *   **Year Guard**: If the shift pushes into a new year (Dec 31 -> Jan 2), it reverses direction.
*   **Line 268**: `_perturb_money`.
    *   Multiplies by `0.85` to `1.15`.
    *   Preserves `billion`/`million` scale words.
    *   Preserves currency symbol (`$`, `€`, `₹`).

---

## 🙋 3. Talking Points & Q&A

**Q: Why do we need Layer 1 (Regex)? Can't AI do it all?**
A: AI is smart but slow and sometimes misses exact formats like SSNs or specific ID patterns. Regex is dumb but 100% precise for structured data. We need **both** for defense-in-depth.

**Q: Why 3 Tiers? Why not just replace everything?**
A: If we replace "Diabetes" with "Condition A", the LLM can't give medical advice. If we replace "2026" with "2020", the advice is outdated.
*   **REPLACE**: Identities (Who).
*   **PERTURB**: Structure (When/How much).
*   **PRESERVE**: Domain Context (What).

**Q: What if the code crashes in production?**
A: The `Sanitizer` is built to be robust. `try/except` blocks in date parsing and number parsing ensure that if perturbation fails, we simply return the **original value** (Safety fallback) rather than crashing the chat.

**Q: How do we handle "Tim Cook" appearing twice?**
A: `AliasManager` keeps a `real_to_fake` dictionary.
1.  See "Tim Cook". Check dict. Not found? Generate "James Carter". Save to dict.
2.  See "Tim Cook" again. Check dict. Found "James Carter". Use it.
3.  This ensures consistency across the whole conversation.

**Q: What makes this better than Microsoft Presidio ($0)?**
A: Presidio uses "hash-based" replacement (Hashed string) or simple masking (`<PERSON>`).
We provide:
1.  **Realistic Fakes**: "James Carter" works better with LLMs than `<PERSON_1>`.
2.  **Context Preservation**: We keep medical/legal terms. Presidio often scrubs them.
3.  **Perturbation**: We shift dates/money mathematically. Presidio just masks them. Confusing the LLM.

---

## ⚔️ 4. Code "Gotchas" to Explain

1.  **Inverse Replacement**: "I sort entities by `start` index in `descending` order in `alias_manager.py` line 92. This is to avoid offset collision strings."
2.  **Privacy Score Calculation**: "I start at 100. I deduct 15 points for every exposed HIPAA identifier (Name/SSN). I add 15 points back if we successfully tier-1 replace it using Faker. The score clamps between 0-100."
3.  **GLiNER Loading**: "The model download happens in `__init__`. That's why startup takes 5 seconds, but processing a prompt only takes 0.2 seconds."

---

## 🎬 5. Demo Script for Teammates

1.  Run `python pitch_tests.py` in the terminal.
2.  Show them **Test 1**. "See? Tim Cook -> James Carter. Simple."
3.  Show them **Test 11 (Medical)**. "Look! 'Metformin' stayed. 'Diabetes' stayed. But 'Dr. Sarah' is gone. The LLM can still treat the patient!"
4.  Show them **Test 14 (Compliance)**. "GDPR stayed. HIPAA stayed. We didn't break the context."
5.  Show them **Hero Test**. "This combines everything. Legal, Medical, Financial all in one prompt."
