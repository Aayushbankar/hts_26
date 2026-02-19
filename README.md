# 🔇 Silent-Protocol

> **Privacy-preserving AI proxy** — Sanitize sensitive prompts before they reach the LLM, get useful responses back with real names restored.

**Hackathon Track:** Generative AI — Problem Statement GS06

---

## 🧩 Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  Core   │────▶│  Groq LLM    │
│  (HTML/JS)   │◀────│  (FastAPI)   │◀────│ Engine  │◀────│ (Llama 3.1)  │
└─────────────┘     └──────────────┘     └─────────┘     └──────────────┘
                                              │
                                    ┌─────────┴──────────┐
                                    │  3-Layer Pipeline   │
                                    │  PatternScanner     │
                                    │  GLiNER NER         │
                                    │  EntityClassifier   │
                                    └────────────────────┘
```

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd hts_26

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r core/requirements.txt

# 4. Run tests
cd core
python test_sanitizer.py    # 7 automated tests
python pitch_tests.py       # 19 pitch-ready tests across 7 domains

# 5. Start backend (requires Groq API key)
cd ../backend
echo "GROQ_API_KEY=gsk_your_key_here" > .env
uvicorn main:app --reload --port 8000
```

## 🔑 Key Innovation: 3-Tier Treatment

| Tier           | Treatment          | Example                                  |
| :------------- | :----------------- | :--------------------------------------- |
| 🔴 **REPLACE**  | Full identity swap | "Dr. Priya Sharma" → "Dr. Kavitha Mehta" |
| 🟡 **PERTURB**  | Controlled noise   | "$3.5 billion" → "$3.2 billion"          |
| 🟢 **PRESERVE** | Keep as-is         | "Metformin 500mg" → "Metformin 500mg"    |

Competitors redact everything → LLM gets `"[REDACTED] prescribed [REDACTED]"` → useless response.
We preserve what the LLM needs → useful, private, accurate responses.

## 📁 Project Structure

```
hts_26/
├── core/                        # 🧠 Privacy engine (Aayush)
│   ├── sanitiser.py             #   Pipeline orchestrator
│   ├── alias_manager.py         #   Alias generation + replacement
│   ├── pattern_scanner.py       #   Regex PII detection (Layer 1)
│   ├── entity_classifier.py     #   Tier assignment + dedup (Layer 3)
│   ├── __init__.py              #   Package exports
│   ├── requirements.txt         #   Python dependencies
│   ├── dataset.json             #   46 test prompts (testing + real-world)
│   ├── test_sanitizer.py        #   7 automated tests
│   ├── pitch_tests.py           #   19 pitch demo tests
│   └── README.md                #   Core module docs
│
├── backend/                     # ⚙️ FastAPI server (Aum)
│   ├── main.py                  #   API endpoints
│   ├── requirements.txt         #   Backend dependencies
│   └── .env                     #   Groq API key (gitignored)
│
├── frontend/                    # 🎨 Web UI (Team)
│   ├── index.html               #   Main page
│   ├── style.css                #   Styles
│   └── script.js                #   Client logic
│
├── docs/                        # 📚 Documentation
│   ├── aayush_tasks.md          #   Task tracking
│   ├── core/                    #   Core design docs
│   │   ├── design.md            #     Core architecture + API
│   │   ├── tasks.md             #     Core task list
│   │   ├── core_phase_1.md      #     Phase 1 specs
│   │   └── core_phase_2.md      #     Phase 2 specs
│   ├── backend/                 #   Backend design docs
│   │   ├── design.md            #     Backend API contract
│   │   └── tasks.md             #     Backend task list
│   ├── frontend/                #   Frontend design docs
│   │   ├── design.md            #     UI/UX specs
│   │   └── tasks.md             #     Frontend task list
│   └── preparation/             #   Planning docs
│       ├── privacy_proxy_master_plan.md
│       ├── core_logic_blueprint.md
│       ├── srs_silent_protocol.md
│       ├── proxy_team_tasks.md
│       └── leader_guide_kickoff.md
│
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 👥 Team

| Member | Role        | Component                                    |
| :----- | :---------- | :------------------------------------------- |
| Aayush | Core Engine | `core/` — 3-layer pipeline, tiered treatment |
| Aum    | Backend     | `backend/` — FastAPI + Groq integration      |
| Team   | Frontend    | `frontend/` — Chat UI                        |

## 📊 Test Results

- **19/19** pitch tests passed (0 data leaks)
- **153** entities detected across 7 domains
- **100/100** average privacy score
- **14/18** HIPAA Safe Harbor identifiers covered

## 🛡️ Privacy Scorecard

Every prompt gets a quantified risk assessment:
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
