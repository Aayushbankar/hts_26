# 🧠 Core Logic Design Document: Silent-Protocol

**Owner:** Aayush
**Deliverables:** `sanitizer.py`, `alias_manager.py`, `test_sanitizer.py`
**Stack:** GLiNER (zero-shot NER) + Faker (fake data) + Python dicts

---

## 1. Overview

The Core Logic module is the **intellectual property** of Silent-Protocol. It is the "brain" that:
1. Detects sensitive entities in text (names, companies, locations, etc.)
2. Generates realistic fake replacements
3. Maintains consistent mappings across a conversation
4. Reverses the mapping when restoring LLM responses

This module has **no dependency** on FastAPI, Groq, or the frontend. It works standalone. The backend imports it.

---

## 2. Module Architecture

There are 2 main files:

**`alias_manager.py`** — Manages the bidirectional mapping between real entities and fake aliases. Uses the Faker library to generate contextual fakes.

**`sanitizer.py`** — Loads the GLiNER NER model, detects entities, and uses the AliasManager to sanitize/de-sanitize text.

**`test_sanitizer.py`** — A standalone test script to verify everything works before connecting to the backend.

The dependency is one-way: `sanitizer.py` imports from `alias_manager.py`. Nothing imports from `sanitizer.py` within this folder (the backend does).

---

## 3. File: `alias_manager.py`

### Class: AliasManager

**Purpose:** Maintains a session-persistent, bidirectional dictionary. When given a real entity and its type, it either returns the existing fake alias or generates a new one using Faker.

### Properties

| Property       | Type                         | Initial Value | Description                         |
| :------------- | :--------------------------- | :------------ | :---------------------------------- |
| `real_to_fake` | dictionary (string → string) | empty `{}`    | Maps real entity text to fake alias |
| `fake_to_real` | dictionary (string → string) | empty `{}`    | Maps fake alias back to real entity |
| `_faker`       | Faker instance               | new Faker()   | Used to generate fake values        |

### Method: `get_or_create(entity_text, entity_label) → string`

**Purpose:** Given a real entity and its type, return the alias. If it already exists, return the stored one. If not, generate a new one and store it.

**Inputs:**
- `entity_text` — The real entity string, e.g., "Apple Inc"
- `entity_label` — The type of entity, e.g., "organization"

**Returns:** The fake alias string, e.g., "Orion Corp"

**Logic:**
1. Check if `entity_text` already exists as a key in `real_to_fake`
2. If yes → return the stored alias (consistency)
3. If no → call `_generate_fake(entity_label)` to create a new fake
4. Store the mapping in both `real_to_fake` and `fake_to_real`
5. **Collision check:** If the generated fake already exists as a key in `fake_to_real` (meaning another entity was already assigned this value), regenerate until unique
6. Return the new fake

### Method: `_generate_fake(label) → string`

**Purpose:** Generate a contextually appropriate fake value based on the entity type.

**Faker Mapping Table:**

| Entity Label        | Faker Generator                               | Example Output           |
| :------------------ | :-------------------------------------------- | :----------------------- |
| `person`            | Random full name                              | "James Mitchell"         |
| `organization`      | Random company name                           | "Orion Corp"             |
| `location`          | Random city name                              | "Portland"               |
| `date`              | Random date within this year (ISO format)     | "2026-03-15"             |
| `email address`     | Random email                                  | "j.mitchell@example.com" |
| `phone number`      | Random phone number                           | "+1-555-0142"            |
| `project name`      | "Project " + random capitalized word          | "Project Falcon"         |
| `product name`      | Random word + "-" + random 3-digit number     | "Nexus-472"              |
| `money amount`      | "$" + random number between 1,000 and 999,999 | "$127,500"               |
| `medical condition` | Random word + "-Syndrome" or similar          | "Syndrome-X"             |
| `government id`     | "ID-" + random 6-digit number                 | "ID-847291"              |
| (any other)         | Random single word                            | "Alpha"                  |

### Method: `sanitize(text, entities) → string`

**Purpose:** Replace all real entities in the text with their aliases.

**Inputs:**
- `text` — The full prompt string
- `entities` — A list of detected entity objects, each with `text`, `label`, and `score` fields

**Returns:** The modified text with all entities replaced

**Algorithm (CRITICAL — order matters):**
1. Sort the entities list by the **length** of the `text` field, **longest first**
2. For each entity in the sorted list:
   a. Get the alias via `get_or_create(entity.text, entity.label)`
   b. Replace all occurrences of `entity.text` with the alias in the text string
3. Return the modified text

**Why sort by length?**
If we have both "Apple" and "Apple Inc" as entities:
- If we replace "Apple" first, it becomes "Orion Corp" inside "Orion Corp Inc" (BROKEN)
- If we replace "Apple Inc" first (longer), it becomes "Vega Industries", and then "Apple" alone becomes "Orion Corp" (CORRECT)

### Method: `desanitize(text) → string`

**Purpose:** Replace all fake aliases back with real entity values. Used on the LLM response.

**Input:** The LLM's response text containing fake names
**Returns:** The text with real names restored

**Algorithm (same sorting rule):**
1. Get all key-value pairs from `fake_to_real` dictionary
2. Sort them by the **length** of the fake name (key), **longest first**
3. For each (fake, real) pair, replace all occurrences of the fake with the real in the text
4. Return the modified text

### Method: `get_mapping() → dictionary`

**Purpose:** Return the current `real_to_fake` dictionary as-is. Used by the backend to include alias info in the API response.

### Method: `clear()`

**Purpose:** Reset both dictionaries to empty. Called when the user resets the session.

---

## 4. File: `sanitizer.py`

### Class: Sanitizer

**Purpose:** The main orchestrator. Loads the NER model, detects entities, and delegates aliasing to AliasManager.

### Properties

| Property        | Type                  | Description                  |
| :-------------- | :-------------------- | :--------------------------- |
| `model`         | GLiNER model instance | The loaded NER model         |
| `alias_manager` | AliasManager instance | Handles all alias operations |
| `labels`        | list of strings       | Entity types to detect       |

### Construction (`__init__`)

When a Sanitizer is created:
1. Load the GLiNER model: `urchade/gliner_medium-v2.1` from HuggingFace
   - First run: downloads ~500MB model (takes 1-2 minutes depending on internet)
   - Subsequent runs: uses cached model, loads in ~5 seconds
2. Create a new AliasManager instance
3. Define the labels list (see below)

### Entity Labels to Detect

The following labels are passed to GLiNER. These are the types of sensitive information we want to find:

| #    | Label               | What It Catches              | Example                 |
| :--- | :------------------ | :--------------------------- | :---------------------- |
| 1    | `person`            | Human names                  | Tim Cook, Sundar Pichai |
| 2    | `organization`      | Companies, institutions      | Apple, Google, MIT      |
| 3    | `location`          | Cities, countries, addresses | Cupertino, California   |
| 4    | `date`              | Dates and time references    | January 15, 2026        |
| 5    | `email address`     | Email addresses              | tim@apple.com           |
| 6    | `phone number`      | Phone numbers                | +1-408-555-1234         |
| 7    | `project name`      | Internal project codenames   | Project Titan           |
| 8    | `product name`      | Product/service names        | iPhone 16, Azure        |
| 9    | `money amount`      | Financial figures            | $2.5 million            |
| 10   | `medical condition` | Health-related info          | Type 2 Diabetes         |
| 11   | `government id`     | SSN, passport, tax IDs       | SSN 123-45-6789         |

### Detection Threshold

The GLiNER model returns a **confidence score** (0.0 to 1.0) for each detected entity. We only keep entities with a score ≥ **0.5**. This threshold balances:
- Too low (0.3): catches too many false positives
- Too high (0.8): misses entities that are obvious to humans

For the hackathon demo, 0.5 works well. In production, this would be configurable per entity type.

### Method: `sanitize_prompt(user_prompt) → (sanitized_text, entities)`

**Purpose:** Full detection + replacement pipeline.

**Input:** The user's raw prompt (string)
**Returns:** A tuple of:
1. The sanitized text (string) — all entities replaced with fakes
2. The list of detected entities — each with `text`, `label`, and `score` fields

**Steps:**
1. Run GLiNER on the prompt with the labels list and threshold 0.5
2. GLiNER returns a list of entity objects: `[{text: "Apple", label: "organization", score: 0.97}, ...]`
3. Pass the text and entity list to `alias_manager.sanitize()`
4. Return both the sanitized text and the entity list

### Method: `desanitize_response(llm_response) → restored_text`

**Purpose:** Reverse all aliases in the LLM's response.

**Input:** The LLM's raw response text (with fake names)
**Returns:** The text with real names restored

**Steps:**
1. Call `alias_manager.desanitize(llm_response)`
2. Return the result

### Method: `get_alias_map() → dictionary`

**Purpose:** Expose the current alias mapping for the API response.

**Returns:** The `real_to_fake` dictionary from the AliasManager

---

## 5. What is GLiNER?

### The Problem with Traditional NER
Traditional NER models (like SpaCy) can only detect a **fixed set** of entity types (PERSON, ORG, LOC, DATE). If you want to detect "project name" or "medical condition", you have to train a custom model — which takes hours and training data we don't have.

### How GLiNER Solves This
GLiNER is a **zero-shot** NER model. You give it any list of labels as plain English strings, and it detects those entities without any training. It was designed for exactly this use case.

| Feature                     | SpaCy NER                   | GLiNER                    |
| :-------------------------- | :-------------------------- | :------------------------ |
| Fixed labels                | Yes (PERSON, ORG, LOC only) | No — any label you define |
| Custom entities             | Requires training           | Just pass label strings   |
| Model size                  | ~50MB                       | ~500MB                    |
| Speed                       | Very fast (~10ms)           | Moderate (~100-300ms)     |
| Accuracy on standard labels | Very good                   | Good                      |
| Accuracy on custom labels   | Impossible without training | Good                      |

### Why We Chose GLiNER Over Alternatives

| Alternative        | Why We Didn't Use It                                                                   |
| :----------------- | :------------------------------------------------------------------------------------- |
| SpaCy NER          | Can't detect "project name" or "product name"                                          |
| Microsoft Presidio | Very heavy, complex config, overkill for MVP                                           |
| Regex              | Catches emails/phones but can't distinguish "Apple" the company from "apple" the fruit |
| Fine-tuned BERT    | No time to train in 24h                                                                |
| GPT-4 for NER      | Too slow, costs money, adds a second API call                                          |

---

## 6. File: `test_sanitizer.py`

This is a **standalone** test script that verifies the pipeline works before connecting to the backend. It should be runnable with `python test_sanitizer.py`.

### Test 1: Basic Sanitization
- Input: "Tim Cook and Sundar Pichai discussed the Apple-Google deal in Cupertino."
- Expected: All 5 entities (Tim Cook, Sundar Pichai, Apple, Google, Cupertino) detected and replaced
- Verification: None of the original entity texts appear in the sanitized output
- Print: Original, sanitized, entity list, and mapping dictionary

### Test 2: De-sanitization
- Input: First sanitize "Tim Cook works at Apple."
- Then simulate an LLM response that uses the alias for Tim Cook
- De-sanitize that response
- Verification: "Tim Cook" appears in the restored output

### Test 3: Consistency
- Sanitize "Apple is great."
- Record the alias given to "Apple"
- Sanitize "I love Apple products."
- Record the alias given to "Apple" again
- Verification: Both aliases are identical (same entity always gets same alias)

### Test 4: Edge Case — Long Entity Names
- Input: "Apple Inc bought Samsung Electronics in San Francisco."
- Verification: "Apple" does not get partially replaced inside other entities
- This validates the sort-by-length algorithm

### Overall Pass Criteria
All 4 tests must pass. Print a success message at the end.

---

## 7. Edge Cases & Handling Strategy

| #    | Edge Case                   | Example                                                 | Current Handling                                     | Priority                 |
| :--- | :-------------------------- | :------------------------------------------------------ | :--------------------------------------------------- | :----------------------- |
| 1    | Partial match               | "Apple" inside "Appleton"                               | Sort entities longest-first before replacing         | P0 (must fix)            |
| 2    | Alias collision             | Two entities get same fake name                         | Regenerate until unique                              | P0                       |
| 3    | Case variation              | "apple" vs "Apple"                                      | GLiNER is case-aware. Replace is exact-match.        | P2 (accept for MVP)      |
| 4    | Multiple mentions           | "Apple" appears 5 times in prompt                       | str.replace replaces ALL occurrences, same alias     | P0 (works automatically) |
| 5    | Overlapping spans           | "New York" + "New York City"                            | GLiNER outputs non-overlapping spans                 | P1 (monitor)             |
| 6    | Empty prompt                | User sends ""                                           | Return empty string, no entities                     | P1                       |
| 7    | No entities found           | "What is 2+2?"                                          | Pass through directly, entities list is empty        | P0 (works automatically) |
| 8    | Entity in response          | LLM says "Orion Corp was founded in..."                 | desanitize() replaces it. Hallucinated details stay. | P2 (acceptable)          |
| 9    | Fake name appears naturally | LLM coincidentally uses a word that's also a fake alias | Very rare. Accept for MVP.                           | P3 (ignore)              |

---

## 8. Performance Expectations

| Operation                         | Expected Latency | Notes                                          |
| :-------------------------------- | :--------------- | :--------------------------------------------- |
| GLiNER model initial load         | ~5 seconds       | One time on server startup. Cached after that. |
| `predict_entities()` per prompt   | 100–300ms        | Depends on prompt length. Longer = slower.     |
| `sanitize()` string replacement   | < 5ms            | Simple string operations, negligible           |
| `desanitize()` string replacement | < 5ms            | Same as above                                  |
| **Total sanitize pipeline**       | **150–350ms**    | Dominated by GLiNER inference                  |

For the hackathon demo, the user will perceive a total round-trip of ~2-4 seconds (sanitize + Groq LLM inference + desanitize). This is acceptable.

---

## 9. Dependencies

| Package        | Version  | Purpose                                           |
| :------------- | :------- | :------------------------------------------------ |
| `gliner`       | 0.2.7    | Zero-shot NER model (the core ML component)       |
| `faker`        | 30.0.0   | Generates realistic fake names, companies, etc.   |
| `torch`        | ≥ 2.0.0  | Required by GLiNER (auto-installed as dependency) |
| `transformers` | ≥ 4.36.0 | Required by GLiNER (auto-installed as dependency) |

Note: `torch` and `transformers` are large packages (~2GB total). First `pip install` will take a few minutes.
