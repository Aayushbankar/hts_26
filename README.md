# Silent-Protocol

> Privacy-preserving AI proxy — sanitizes your prompts before they hit the LLM, then restores real names in the response.

**Hackathon Track:** open innovation 

---

## What it does

You type a prompt with personal info (names, emails, Aadhaar numbers, etc). Our pipeline:
1. Detects all PII using regex + GLiNER NERmodel
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
tree
.
├── backend
│   ├── main.py
│   └── __pycache__
│       └── main.cpython-313.pyc
├── cli_tester.py
├── core
│   ├── alias_manager.py
│   ├── core_explanation.md
│   ├── dataset.json
│   ├── entity_classifier.py
│   ├── __init__.py
│   ├── intent_classifier.py
│   ├── pattern_scanner.py
│   ├── pitch_tests.py
│   ├── __pycache__
│   │   ├── alias_manager.cpython-313.pyc
│   │   ├── entity_classifier.cpython-313.pyc
│   │   ├── __init__.cpython-313.pyc
│   │   ├── intent_classifier.cpython-313.pyc
│   │   ├── pattern_scanner.cpython-313.pyc
│   │   └── sanitiser.cpython-313.pyc
│   ├── README.md
│   ├── real_prompts.json
│   ├── sanitiser.py
│   ├── test_real_prompts.py
│   ├── test_report.txt
│   └── test_sanitizer.py
├── divya_frontend
│   ├── chat.html
│   ├── index.html
│   ├── new_desgin.jpeg
│   ├── refrence.html
│   ├── Screenshot 2026-02-19 141844.png
│   ├── Screenshot_2026-02-19_141844-removebg-preview.png
│   ├── Screenshot 2026-02-19 151825.png
│   ├── Screenshot_2026-02-19_180716-removebg-preview.png
│   ├── script.js
│   ├── style.css
│   └── upscalemedia-transformed (2).jpeg
├── docs
│   ├── aayush_tasks.md
│   ├── backend
│   │   ├── design.md
│   │   └── tasks.md
│   ├── core
│   │   ├── alias_manager.jpeg
│   │   ├── core_phase_1.md
│   │   ├── core_phase_2.md
│   │   ├── design.md
│   │   ├── entity_classification.jpeg
│   │   ├── pattern_scanner.jpeg
│   │   └── tasks.md
│   ├── frontend
│   │   ├── design.md
│   │   └── tasks.md
│   ├── insider_docs
│   │   ├── complete_project_audit.md
│   │   ├── pitch_deck_script.md
│   │   ├── round1_concept_proof.md
│   │   ├── round2_code_defense.md
│   │   ├── round3_code_defense.md
│   │   └── study_guide.md
│   └── preparation
│       ├── core_logic_blueprint.md
│       ├── leader_guide_kickoff.md
│       ├── privacy_proxy_master_plan.md
│       ├── proxy_team_tasks.md
│       └── srs_silent_protocol.md
├── experimental_frontend
│   ├── ideas
│   │   ├── idea_1.webp
│   │   ├── idea_2.webp
│   │   └── idea_3.webp
│   ├── index.html
│   ├── script.js
│   └── style.css
├── prompts.txt
├── README.md
└── requirements.txt

14 directories, 66 files
(.venv) incide@mx-elitebook:/mnt/shared_data/projects/hts_26
$ 
```

## Team

| Member | Role        | What they did                                    |
| ------ | ----------- | ------------------------------------------------ |
| Aayush | Core Engine | 3-layer pipeline, tiered treatment, alias system |
| Aum    | Backend     | FastAPI server, Groq integration                 |
| Divya  | Frontend    | designer + ui/ux                                 |

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
