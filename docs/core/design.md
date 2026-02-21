#  Core Logic Design Document: Silent-Protocol v2

**Owner:** Aayush
**Deliverables:** `sanitiser.py`, `alias_manager.py`, `pattern_scanner.py`, `entity_classifier.py`, `test_sanitizer.py`, `pitch_tests.py`
**Stack:** GLiNER (zero-shot NER) + Regex Pipeline + Faker (fake data) + python-dateutil

---

## 1. Overview

The Core Logic module is the **intellectual property** of Silent-Protocol. It is the "brain" that:
1. Detects sensitive entities in text via a **3-layer pipeline** (regex → NER → classification)
2. Classifies each entity into a **treatment tier** (REPLACE / PERTURB / PRESERVE)
3. Generates realistic fake replacements or controlled perturbations
4. Computes a **privacy scorecard** per prompt
5. Maintains consistent bidirectional mappings across a conversation
6. Reverses the mapping when restoring LLM responses

This module has **no dependency** on FastAPI, Groq, or the frontend. It works standalone. The backend imports it via `from core.sanitiser import Sanitizer`.

---

## 2. Module Architecture

```
User Prompt
    -
    ▼
--------------------
-  PatternScanner   -  Layer 1: Regex → email, phone, SSN, credit card, URL, IP
--------------------
        -
        ▼
--------------------
-  GLiNER NER       -  Layer 2: Zero-shot NER → 18 entity categories (threshold ≥ 0.6)
--------------------
        -
        ▼
--------------------
- EntityClassifier  -  Layer 3: Dedup overlaps, assign tier, compute privacy score
--------------------
        -
        ▼
--------------------
-  AliasManager     -  Offset-based R→L replacement, Faker generation, perturbation
--------------------
        -
        ▼
  (sanitized_text, entities, alias_map, privacy_score)
```

### File Structure

| File                   | Purpose                                                                                       | Lines |
| :--------------------- | :-------------------------------------------------------------------------------------------- | :---- |
| `sanitiser.py`         | Pipeline orchestrator — ties all layers together                                              | ~90   |
| `alias_manager.py`     | Tiered alias generation (REPLACE/PERTURB/PRESERVE), offset-based replacement, de-sanitization | ~370  |
| `pattern_scanner.py`   | Regex-based structured PII detection (Layer 1)                                                | ~50   |
| `entity_classifier.py` | Entity dedup, tier assignment, privacy scorecard (Layer 3)                                    | ~200  |
| `test_sanitizer.py`    | 7 automated tests for v2 API                                                                  | ~210  |
| `pitch_tests.py`       | 19 pitch-ready tests across 7 domains                                                         | ~430  |

Dependencies are one-way:
```
sanitiser.py → alias_manager.py
             → pattern_scanner.py
             → entity_classifier.py
```

---

## 3. Three-Tier Entity Treatment

This is Silent-Protocol's **key innovation**. Unlike competitors that treat all PII as binary (found → remove), we classify each entity into one of three treatment tiers:

###  REPLACE (Identity Data)
Entities that directly identify a person or organization. Fully replaced with realistic Faker-generated fakes.

| Label           | Example             | Replacement         |
| :-------------- | :------------------ | :------------------ |
| `person`        | Tim Cook            | James Carter        |
| `organization`  | Apple Inc           | Sparks Industries   |
| `location`      | Cupertino           | North David         |
| `email`         | tim@apple.com       | jcarter@example.com |
| `phone`         | +1-408-555-1234     | +1-555-0198         |
| `ssn`           | 123-45-6789         | 847-29-1053         |
| `credit_card`   | 4111-1111-1111-1111 | 5392-8471-0263-9184 |
| `government_id` | EIN 12-3456789      | EIN 84-7291053      |
| `url`           | https://apple.com   | https://example.com |
| `ip_address`    | 192.168.1.1         | 10.42.156.78        |
| `project_name`  | Project Titan       | Project Falcon      |
| `product_name`  | iPhone 16           | Carter Pro          |

###  PERTURB (Structural Data)
Data that provides important context but doesn't directly identify. Shifted by small, controlled amounts to preserve analytical utility.

| Label          | Example          | Perturbation                                    |
| :------------- | :--------------- | :---------------------------------------------- |
| `date`         | January 15, 2026 | January 19, 2026 (±3-7 days, format preserved)  |
| `money_amount` | $3.5 billion     | $3.2 billion (×0.85-1.15, scale word preserved) |
| `age`          | 45 years old     | 47 years old (±2-3 years)                       |
| `percentage`   | 23.5%            | 25.1% (×0.85-1.15)                              |

**Smart Perturbation Features:**
- Year boundary guard: Jan 1, 2026 never shifts to 2025
- Multi-currency: $, €, £, ¥, ₹ all supported
- Scale preservation: "billion" stays "billion"
- FY notation preserved: "FY2026" stays untouched
- Abstract dates preserved: "Q2 2025", "March 2025", "2025" stay untouched

###  PRESERVE (Domain-Critical Context)
Entities essential for LLM reasoning. Kept as-is — removing them would destroy analytic utility.

| Label                  | Example                  | Why Preserved                                 |
| :--------------------- | :----------------------- | :-------------------------------------------- |
| `medical_condition`    | Type 2 Diabetes          | LLM needs disease name to give medical advice |
| `drug_name`            | Metformin 500mg          | LLM needs drug info for interactions/dosing   |
| `symptom`              | chest pain               | LLM needs symptoms for diagnosis              |
| `medical_procedure`    | cardiac bypass           | LLM needs procedure context                   |
| `legal_concept`        | breach of fiduciary duty | Legal reasoning depends on this               |
| `financial_instrument` | Series B funding         | Financial analysis depends on this            |
| `regulatory_term`      | HIPAA compliance         | Compliance context must be preserved          |
| `job_title`            | Chief Financial Officer  | Role context matters for reasoning            |

---

## 4. File: `sanitiser.py`

### Class: Sanitizer

**Purpose:** The main orchestrator. Runs the 3-layer pipeline and delegates to specialized components.

### Construction (`__init__`)
1. Loads GLiNER model: `urchade/gliner_medium-v2.1`
2. Creates instances of `AliasManager`, `PatternScanner`, `EntityClassifier`
3. Defines 18 entity labels for GLiNER detection

### Method: `sanitize_prompt(user_prompt) → tuple`

**Input:** The user's raw prompt (string)

**Returns:** A 4-tuple:
1. `sanitized_text` (str) — all entities replaced/perturbed
2. `classified_entities` (list) — each entity dict with `text`, `label`, `tier`, `start`, `end`, `source`
3. `alias_map` (dict) — current real→fake mapping
4. `privacy_score` (dict) — privacy scorecard with `score`, `risk_level`, `replaced`, `perturbed`, `preserved`, HIPAA counts

**Pipeline Steps:**
1. Layer 1: `pattern_scanner.scan(prompt)` → regex entities with character offsets
2. Layer 2: `model.predict_entities(prompt, labels, threshold=0.6)` → NER entities
3. Layer 3: `entity_classifier.classify(regex_entities, ner_entities)` → deduplicated, tiered
4. Privacy: `entity_classifier.compute_privacy_score(classified)` → scorecard
5. Replacement: `alias_manager.sanitize_by_offsets(prompt, classified)` → R→L offset replacement

### Method: `desanitize_response(llm_response) → str`
Delegates to `alias_manager.desanitize()`. Unchanged from v1.

### Method: `get_alias_map() → dict`
Returns current `real_to_fake` dictionary.

### Method: `clear()`
Resets alias mappings without reloading the GLiNER model. Fast — use this for `/reset` instead of recreating the `Sanitizer` instance.

---

## 5. File: `alias_manager.py`

### Class: AliasManager

**Properties:**

| Property            | Type  | Description                   |
| :------------------ | :---- | :---------------------------- |
| `real_to_fake`      | dict  | Maps original → alias         |
| `fake_to_real`      | dict  | Maps alias → original         |
| `fake`              | Faker | Generates fake values         |
| `_name_blocklist`   | set   | Inappropriate names to filter |
| `_corp_suffixes`    | list  | Company name suffixes         |
| `_product_suffixes` | list  | Product name suffixes         |

### Key Methods:

**`get_or_create(entity_text, entity_label, tier)`** — Main entry point. Routes to `_generate_replacement()` for REPLACE, `_perturb()` for PERTURB, or returns original for PRESERVE.

**`sanitize_by_offsets(text, entities)`** — Offset-based right-to-left replacement. Sorts entities by `start` position descending, replaces from end to beginning to prevent cascading offset errors.

**`desanitize(text)`** — Replaces fake aliases back to real values. Sorts by length (longest first) to prevent substring collisions.

**`_generate_person_name(original)`** — Locale-aware name generation: detects South Asian, East Asian, Korean cultural origins and generates culturally-appropriate replacements.

**`_perturb_date(original)`** — Parses date → shifts ±3-7 days → reformats in original style. Guards against year boundary crossing.

**`_perturb_money(original)`** — Parses money → multiplies ×0.85-1.15 → preserves currency symbol and scale word.

---

## 6. File: `pattern_scanner.py`

### Class: PatternScanner

Pre-compiled regex patterns for structured PII that regex catches better than NER:

| Pattern       | Example Match            |
| :------------ | :----------------------- |
| `email`       | user@domain.com          |
| `phone`       | +1-408-555-1234          |
| `ssn`         | 123-45-6789              |
| `credit_card` | 4111-1111-1111-1111      |
| `url`         | https://example.com/path |
| `ip_address`  | 192.168.1.1              |

**Method: `scan(text) → list`** — Returns list of entity dicts with `text`, `label`, `start`, `end`, `source="regex"`.

---

## 7. File: `entity_classifier.py`

### Class: EntityClassifier

**Method: `classify(regex_entities, ner_entities) → list`**

1. Normalizes all entities to a common format
2. Applies false positive filtering (abbreviations like "SSN", "DOB" when flagged as government_id)
3. Strips trailing punctuation from entity text
4. Deduplicates overlapping spans (longest span wins, regex preferred for ties, ≥50% overlap threshold)
5. Assigns treatment tier based on label

**Method: `compute_privacy_score(entities) → dict`**

Returns a scorecard:
```python
{
    "score": 94,                        # 0-100, weighted by entity risk
    "risk_level": "LOW",                # LOW/MEDIUM/HIGH/CRITICAL
    "total_entities": 8,
    "replaced": 5,
    "perturbed": 2,
    "preserved": 1,
    "hipaa_identifiers_found": 6,
    "hipaa_identifiers_protected": 6
}
```

---

## 8. Dependencies

| Package           | Purpose                              |
| :---------------- | :----------------------------------- |
| `gliner`          | Zero-shot NER model                  |
| `faker`           | Fake data generation                 |
| `python-dateutil` | Robust date parsing for perturbation |
| `torch`           | Required by GLiNER                   |
| `transformers`    | Required by GLiNER                   |

---

## 9. Performance

| Operation                       | Latency                                  |
| :------------------------------ | :--------------------------------------- |
| GLiNER model load               | ~5 seconds (first run: downloads ~500MB) |
| `predict_entities()` per prompt | 100-300ms                                |
| Regex scan                      | < 1ms                                    |
| Entity classification + dedup   | < 1ms                                    |
| Alias replacement               | < 5ms                                    |
| **Total sanitize pipeline**     | **150-350ms**                            |
