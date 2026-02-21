# Silent-Protocol Core Engine

The privacy engine. Handles all the PII detection, replacement, and scoring.

## How to use

```python
from core.sanitiser import Sanitizer

sanitizer = Sanitizer()  # takes a few seconds to load the GLiNER model

# sanitize a prompt
text, entities, aliases, score = sanitizer.sanitize_prompt(
    "Dr. Priya Sharma prescribed Metformin 500mg for Tim Cook at Apple on January 15, 2026."
)

# text is now something like:
# "Dr. Kavitha Mehta prescribed Metformin 500mg for James Carter at ..."

# de-sanitize the LLM's response
restored = sanitizer.desanitize_response(llm_response)
```

## How the 3 tiers work

| Tier     | What happens        | Example                      |
| -------- | ------------------- | ---------------------------- |
| REPLACE  | swap with fake data | "Dr. Priya" -> "Dr. Kavitha" |
| PERTURB  | add small noise     | "Jan 15" -> "Jan 19"         |
| PRESERVE | keep as-is          | "Metformin 500mg" stays      |

Other tools just redact everything and the LLM gets "[REDACTED] prescribed [REDACTED]" which is useless.

## Detection pipeline

```
1. PatternScanner (regex)  -> emails, phones, SSNs, credit cards, etc
2. GLiNER NER (model)      -> names, orgs, locations, medical terms, etc (18 categories)
3. EntityClassifier         -> dedup overlaps, assign tiers, privacy score
3.5 IntentClassifier (LLM) -> ask local qwen2.5 "is this task or identity?"
```

## Entity types we handle

**REPLACE (12 types):** person, org, location, email, phone, ssn, credit card, gov id, url, ip, project name, product name

**PERTURB (4 types):** date (+-3-7 days), money (+-15%), age (+-2-3 yrs), percentage (+-15%)

**PRESERVE (8 types):** medical condition, drug name, symptom, medical procedure, legal concept, financial instrument, regulatory term, job title

## Files

```
core/
  sanitiser.py          - main pipeline orchestrator
  alias_manager.py      - fake data generation + replacement
  pattern_scanner.py    - regex PII detection
  entity_classifier.py  - dedup, tiers, intent, privacy score
  intent_classifier.py  - local LLM (qwen2.5 via ollama) for intent
  pitch_tests.py        - demo tests across 7 domains
  test_real_prompts.py  - 40 prompt stress test
  real_prompts.json     - test dataset
```

## Running tests

```bash
cd core
python pitch_tests.py       # demo tests
python test_real_prompts.py  # full 40-prompt test
```
