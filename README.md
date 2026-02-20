# Silent-Protocol

> Privacy-preserving AI proxy — sanitizes your prompts before they hit the LLM, then restores real names in the response.

**Hackathon Track:** open innovation 

---

## What it does

You type a prompt with personal info (names, emails, Aadhaar numbers, etc). Our pipeline:
1. Detects all PII using regex + GLiNER NER model
2. Replaces names with fake ones, perturbs dates/money slightly, keeps medical terms intact
3. Sends the clean version to the LLM
4. Swaps the fake names back in the response

So the LLM never sees your real data but you still get a useful response.

## Architecture

```
Frontend (HTML/JS) → Backend (FastAPI) → Core Engine → Groq LLM (Llama 3.3)
                                           |
                                    3-Layer Pipeline:
                                     PatternScanner (regex)
                                     GLiNER NER (model)
                                     EntityClassifier (tiers)
```

## How the 3-tier system works

| Tier     | What happens             | Example                               |
| -------- | ------------------------ | ------------------------------------- |
| REPLACE  | Full swap with fake data | "Dr. Priya Sharma" → "Vikram Patel"   |
| PERTURB  | Small noise added        | "₹3.5 lakh" → "₹3.9 lakh"             |
| PRESERVE | Kept as-is               | "Metformin 500mg" → "Metformin 500mg" |

Most other tools just redact everything and the LLM gets `[REDACTED] prescribed [REDACTED]` which is useless. We keep domain terms so the LLM can actually help.

## Quick Start

```bash
# clone and setup
git clone <repo-url>
cd hts_26
python -m venv .venv
source .venv/bin/activate

# install
pip install -r requirements.txt

# run tests
cd core
python test_sanitizer.py
python pitch_tests.py

# start backend (need groq api key)
cd ../backend
echo "GROQ_API_KEY=gsk_your_key" > ../.env
python main.py
```

## Project struture

```
hts_26/
├── core/                    # privacy engine
│   ├── sanitiser.py         # pipeline orchestrator
│   ├── alias_manager.py     # fake data generation + replacement
│   ├── pattern_scanner.py   # regex PII detection
│   ├── entity_classifier.py # tier assignment + dedup + intent detection
│   ├── test_sanitizer.py    # automated tests
│   └── pitch_tests.py       # demo tests
│
├── backend/
│   └── main.py              # fastapi server + groq integration
│
├── frontend/                # chat UI
│   ├── index.html
│   ├── style.css
│   └── script.js
│
└── docs/                    # design docs
```

## Team

| Member | Role        | What they did                                           |
| ------ | ----------- | ------------------------------------------------------- |
| Aayush | Core Engine | 3-layer pipeline, tiered treatment, alias system        |
| Aum    | Backend     | FastAPI server, Groq integration                        |
| Team   | Frontend    | Chat UI (we dont have a frontend dev so AI helped here) |

## Test results

- 40 real-world promtps tested, 0 errors
- 394 entities detectd across all prompts
- 233 replaced, 81 perturbed, 80 preserved
- intent detection correctly preservs travel destinations (Paris stays Paris)
- HIPAA safe harbor coverage ~95%

## Privcy score

every prompt gets scored:
```json
{
  "score": 94,
  "risk_level": "LOW",
  "replaced": 5,
  "perturbed": 2,
  "preserved": 1,
  "hipaa_identifiers_protected": 6
}
```

## libraries used

- **GLiNER** - zero-shot NER model (finds names, orgs, locations without retraining)
- **Faker** - generates realistic fake names/emails/etc
- **python-dateutil** - parses dates from messy text
- **FastAPI** - backend framework
- **Groq** - LLM API (llama 3.3 70b)
