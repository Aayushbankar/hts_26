# Silent-Protocol Core Module

> The privacy engine that makes LLMs safe for sensitive data.

## Quick Start

```python
from core.sanitiser import Sanitizer

sanitizer = Sanitizer()  # Loads GLiNER model (~5 sec first run)

# Sanitize a prompt
text, entities, aliases, score = sanitizer.sanitize_prompt(
    "Dr. Priya Sharma prescribed Metformin 500mg for Tim Cook at Apple on January 15, 2026."
)

print(text)
# → "Dr. Kavitha Mehta prescribed Metformin 500mg for James Carter at Sparks Industries on January 19, 2026."

print(score)
# → {"score": 100, "risk_level": "LOW", ...}

# De-sanitize an LLM response  
restored = sanitizer.desanitize_response(llm_response)
```

## Three-Tier Treatment (Our Key Innovation)

| Tier           | Treatment                    | Example            | Result                |
| :------------- | :--------------------------- | :----------------- | :-------------------- |
| 🔴 **REPLACE**  | Full identity replacement    | "Dr. Priya Sharma" | → "Dr. Kavitha Mehta" |
| 🟡 **PERTURB**  | Small controlled noise       | "January 15, 2026" | → "January 19, 2026"  |
| 🟢 **PRESERVE** | Keep as-is (domain-critical) | "Metformin 500mg"  | → "Metformin 500mg"   |

**Why?** Competitors replace everything blindly — the LLM gets `"Dr. [REDACTED] prescribed [REDACTED]"` and can't help. We preserve what the LLM needs.

## Detection Pipeline (3 Layers)

```
1. PatternScanner (regex)  → emails, phones, SSNs, credit cards, URLs, IPs
2. GLiNER NER (model)      → 18 entity categories, threshold ≥ 0.6
3. EntityClassifier         → dedup overlaps, assign tier, compute privacy score
```

## API Reference

### `Sanitizer.sanitize_prompt(user_prompt: str) → tuple`

Returns **4 values:**

| #    | Name             | Type       | Description                                                |
| :--- | :--------------- | :--------- | :--------------------------------------------------------- |
| 1    | `sanitized_text` | str        | Prompt with entities replaced/perturbed                    |
| 2    | `entities`       | list[dict] | Each: `{text, label, tier, start, end, source, score}`     |
| 3    | `alias_map`      | dict       | Current `{real: fake}` mapping                             |
| 4    | `privacy_score`  | dict       | `{score, risk_level, replaced, perturbed, preserved, ...}` |

### `Sanitizer.desanitize_response(llm_response: str) → str`

Replaces all fake aliases back to original values.

### `Sanitizer.get_alias_map() → dict`

Returns current real→fake mapping.

### `Sanitizer.clear()`

Resets all mappings. Does NOT reload GLiNER model (instant).

## Entity Categories

### 🔴 REPLACE (12 types)
`person`, `organization`, `location`, `email`, `phone`, `ssn`, `credit_card`, `government_id`, `url`, `ip_address`, `project_name`, `product_name`

### 🟡 PERTURB (4 types)
`date` (±3-7 days), `money_amount` (×0.85-1.15), `age` (±2-3 years), `percentage` (×0.85-1.15)

### 🟢 PRESERVE (8 types)
`medical_condition`, `drug_name`, `symptom`, `medical_procedure`, `legal_concept`, `financial_instrument`, `regulatory_term`, `job_title`

## Smart Features

- **Locale-aware names:** "Priya Sharma" → "Kavitha Mehta" (not "Lisa Smith")
- **Year boundary guard:** Jan 1 never shifts to Dec 31 of previous year
- **Multi-currency:** $, €, £, ¥, ₹ all preserved
- **Scale preservation:** "$3.5 billion" → "$3.2 billion" (not "$247,891")
- **FY notation:** "FY2026" stays "FY2026"
- **False positive filter:** "SSN" the abbreviation is not treated as a government ID
- **Company blocklist:** Inappropriate Faker names are filtered out
- **Offset-based replacement:** Right-to-left by character position — no substring collisions

## Privacy Scorecard

Every prompt gets a quantified risk assessment:

```python
{
    "score": 94,              # 0-100 (higher = more private)
    "risk_level": "LOW",      # LOW/MEDIUM/HIGH/CRITICAL
    "total_entities": 8,
    "replaced": 5,
    "perturbed": 2,
    "preserved": 1,
    "hipaa_identifiers_found": 6,
    "hipaa_identifiers_protected": 6
}
```

## File Structure

```
core/
├── sanitiser.py          # Pipeline orchestrator (imports all below)
├── alias_manager.py      # Alias generation, perturbation, replacement
├── pattern_scanner.py    # Regex PII detection (Layer 1)
├── entity_classifier.py  # Dedup, tier assignment, privacy score (Layer 3)
├── __init__.py           # Package marker
├── requirements.txt      # Dependencies
├── test_sanitizer.py     # 7 automated tests
├── pitch_tests.py        # 19 pitch-ready tests
└── README.md             # This file
```

## Dependencies

```
gliner
faker
python-dateutil
torch
transformers
```

## Running Tests

```bash
cd core
python test_sanitizer.py   # 7 automated tests
python pitch_tests.py      # 19 pitch-ready tests across 7 domains
```

## HIPAA Safe Harbor Alignment

Maps to 14/18 HIPAA identifiers (all text-applicable ones):

| HIPAA Identifier | Our Entity Type | Treatment |
| :--------------- | :-------------- | :-------- |
| Names            | person          | REPLACE   |
| Geographic data  | location        | REPLACE   |
| Dates            | date            | PERTURB   |
| Phone numbers    | phone           | REPLACE   |
| Email addresses  | email           | REPLACE   |
| SSN              | ssn             | REPLACE   |
| Account numbers  | credit_card     | REPLACE   |
| URLs             | url             | REPLACE   |
| IP addresses     | ip_address      | REPLACE   |
| Ages             | age             | PERTURB   |
