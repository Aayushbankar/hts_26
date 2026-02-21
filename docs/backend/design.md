# ⚙️ Backend Design Document: Silent-Protocol v2

**Owner:** Aum
**Deliverables:** `main.py`, `requirements.txt`, `.env`
**Stack:** Python 3.11 + FastAPI + Groq SDK
**Run Command:** `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

---

## 1. Overview

The backend is a FastAPI HTTP server that acts as the bridge between the frontend and the LLM. It:
1. Receives chat messages from the frontend via HTTP POST
2. Passes them through the Core Sanitizer (imported from `core/`)
3. Sends the sanitized text to Groq's LLM API
4. Receives the LLM response
5. Passes it back through the Sanitizer to restore original names
6. Returns everything (response + debug info + **privacy scorecard**) as JSON to the frontend

The backend does NOT handle any user authentication, database, file storage, or deployment logic.

---

## 2. Server Configuration

| Setting     | Value                        | Reasoning                                                 |
| :---------- | :--------------------------- | :-------------------------------------------------------- |
| Host        | `0.0.0.0`                    | Accepts connections from any local IP                     |
| Port        | `8000`                       | Standard dev port                                         |
| Auto-reload | Enabled (`--reload`)         | Restarts on code changes during development               |
| CORS        | Allow all origins (`*`)      | Frontend runs on a different port (Live Server uses 5500) |
| Docs URL    | `http://localhost:8000/docs` | FastAPI auto-generates interactive API docs (Swagger)     |

### CORS Middleware Configuration

The server must allow:
- **All origins** (any localhost port)
- **All HTTP methods** (GET, POST, OPTIONS)
- **All headers** (Content-Type, etc.)
- **Credentials** (though we don't use them)

---

## 3. Global State

When the server starts, it initializes two global objects:

1. **Sanitizer instance** — Loaded once from `core/sanitiser.py`. This loads the GLiNER model into memory (~5 seconds on first startup, uses cache after that). This instance persists for the entire server session.

2. **Groq client** — Initialized with the API key from the `.env` file. Used for all LLM calls.

Both are module-level globals. They are destroyed when the server stops.

### Startup Behavior
When the server starts, it should print a confirmation message to the console showing:
- Whether the GLiNER model loaded successfully
- Whether the Groq API key is configured

---

## 4. Endpoint Specifications

### 4.1 `POST /chat` — Main Chat Endpoint

**Purpose:** The primary endpoint. Accepts a message, sanitizes it, gets an LLM response, de-sanitizes it, and returns everything.

**Request Format:**
- Method: POST
- Content-Type: application/json
- Body: a JSON object with one field `message` (string, required)
- Example: `{"message": "Draft an NDA between Apple Inc and Samsung."}`

**Processing Steps (in order):**
1. Validate the request body (FastAPI does this automatically via the Pydantic model)
2. Call `sanitizer.sanitize_prompt(request.message)` → returns **4-tuple:**
   ```python
   sanitized_text, entities, alias_map, privacy_score = sanitizer.sanitize_prompt(request.message)
   ```
3. Send `sanitized_text` to Groq's chat completion API with model `llama-3.1-70b-versatile`, temperature `0.7`, max tokens `2048`
4. Get the raw LLM response text
5. Call `sanitizer.desanitize_response(raw_response)` → returns the text with real names restored
6. Build the entity info list: for each entity in `entities`, include the text, label, alias (from `alias_map`), tier, and score
7. Return the full response object including privacy scorecard

**Success Response (200):**
```json
{
    "response": "Apple should file the patent by March...",
    "sanitized_prompt": "Sparks Industries should file the patent by March...",
    "entities_detected": [
        {
            "text": "Apple",
            "label": "organization",
            "alias": "Sparks Industries",
            "tier": "REPLACE",
            "score": 0.97
        },
        {
            "text": "January 15, 2026",
            "label": "date",
            "alias": "January 19, 2026",
            "tier": "PERTURB",
            "score": 0.85
        },
        {
            "text": "Type 2 Diabetes",
            "label": "medical_condition",
            "alias": "Type 2 Diabetes",
            "tier": "PRESERVE",
            "score": 0.91
        }
    ],
    "privacy_score": {
        "score": 94,
        "risk_level": "LOW",
        "total_entities": 8,
        "replaced": 5,
        "perturbed": 2,
        "preserved": 1,
        "hipaa_identifiers_found": 6,
        "hipaa_identifiers_protected": 6
    },
    "silent_mode": true
}
```

**Error Response (500):**
```json
{
    "error": "LLM API Error",
    "detail": "Rate limit exceeded. Please try again."
}
```

**Error Handling:**
- Wrap the entire processing flow in a try/catch
- If the Groq API fails, return a 500 with a descriptive message
- If the Sanitizer fails, return a 500 with a descriptive message
- Do not crash the server on any error — always return valid JSON

---

### 4.2 `GET /health` — Health Check

**Response (200):**
```json
{
    "status": "ok",
    "model_loaded": true,
    "groq_configured": true
}
```

---

### 4.3 `GET /aliases` — Current Alias Map

**Response (200):**
```json
{
    "aliases": {
        "Apple Inc": "Sparks Industries",
        "Tim Cook": "James Carter"
    },
    "total": 2
}
```

---

### 4.4 `POST /reset` — Clear Session

**Processing Steps:**
1. Call `sanitizer.clear()` — this resets the alias mappings WITHOUT reloading the GLiNER model (instant, no 5-second wait)
2. Return success

>  **v2 Change:** In v1, reset created a new Sanitizer instance (5-second delay). Now use `sanitizer.clear()` for instant reset.

**Response (200):**
```json
{
    "status": "reset",
    "message": "All aliases cleared"
}
```

---

## 5. Data Models

### ChatRequest
| Field     | Type   | Required | Description             |
| :-------- | :----- | :------- | :---------------------- |
| `message` | string | Yes      | The user's chat message |

### EntityInfo (v2 — updated)
| Field   | Type   | Description                                         |
| :------ | :----- | :-------------------------------------------------- |
| `text`  | string | Original entity text ("Apple Inc")                  |
| `label` | string | Entity type ("organization")                        |
| `alias` | string | The replacement used ("Sparks Industries")          |
| `tier`  | string | Treatment tier: "REPLACE", "PERTURB", or "PRESERVE" |
| `score` | float  | Detection confidence (0.0-1.0)                      |

### PrivacyScore (v2 — NEW)
| Field                         | Type   | Description                            |
| :---------------------------- | :----- | :------------------------------------- |
| `score`                       | int    | 0-100 privacy score                    |
| `risk_level`                  | string | "LOW", "MEDIUM", "HIGH", or "CRITICAL" |
| `total_entities`              | int    | Total entities detected                |
| `replaced`                    | int    | Entities fully replaced                |
| `perturbed`                   | int    | Entities perturbed                     |
| `preserved`                   | int    | Entities preserved as-is               |
| `hipaa_identifiers_found`     | int    | HIPAA Safe Harbor identifiers found    |
| `hipaa_identifiers_protected` | int    | HIPAA identifiers that were protected  |

### ChatResponse (v2 — updated)
| Field               | Type             | Description                              |
| :------------------ | :--------------- | :--------------------------------------- |
| `response`          | string           | Final response with real names restored  |
| `sanitized_prompt`  | string           | What the LLM actually saw                |
| `entities_detected` | list[EntityInfo] | All detected entities with their aliases |
| `privacy_score`     | PrivacyScore     | **NEW:** Per-prompt privacy assessment   |
| `silent_mode`       | boolean          | Whether sanitization was active          |

### ErrorResponse
| Field    | Type   | Description           |
| :------- | :----- | :-------------------- |
| `error`  | string | Short error message   |
| `detail` | string | Full exception detail |

---

## 6. Import Structure

The backend imports from the `core/` directory. The core module uses dual-mode imports (try/except pattern) so it works both as a package and standalone.

### How to import in `main.py`:
```python
import sys
import os

# Add project root to path so we can import from core/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.sanitiser import Sanitizer
```

### What the backend uses from core:
```python
# Initialize once at module level
sanitizer = Sanitizer()

# In /chat endpoint:
sanitized_text, entities, alias_map, privacy_score = sanitizer.sanitize_prompt(message)
restored_text = sanitizer.desanitize_response(llm_response)

# Build entity info for response:
entity_info = []
for e in entities:
    entity_info.append({
        "text": e["text"],
        "label": e["label"],
        "alias": alias_map.get(e["text"], e["text"]),
        "tier": e["tier"],
        "score": e.get("score", 0.0),
    })

# In /aliases endpoint:
aliases = sanitizer.get_alias_map()

# In /reset endpoint:
sanitizer.clear()  # Instant reset, no model reload
```

---

## 7. Groq LLM Integration

### Configuration

| Parameter      | Value                               | Reasoning                                    |
| :------------- | :---------------------------------- | :------------------------------------------- |
| Model          | `llama-3.1-70b-versatile`           | Best quality on Groq's free tier             |
| Temperature    | `0.7`                               | Creative enough for drafting, not too random |
| Max Tokens     | `2048`                              | Long enough for documents                    |
| API Key Source | `.env` file variable `GROQ_API_KEY` | Loaded via python-dotenv                     |

### How to Get the API Key
1. Go to https://console.groq.com
2. Sign up (free, no credit card)
3. Go to API Keys → Create new key
4. Copy the key (starts with `gsk_`)
5. Create a `.env` file in the `backend/` folder with: `GROQ_API_KEY=gsk_your_key_here`

---

## 8. Dependencies

| Package             | Version | Purpose                                          |
| :------------------ | :------ | :----------------------------------------------- |
| `fastapi`           | 0.115.0 | Web framework                                    |
| `uvicorn[standard]` | 0.32.0  | ASGI server to run FastAPI                       |
| `groq`              | 0.11.0  | Groq API SDK                                     |
| `gliner`            | 0.2.7   | Zero-shot NER (used by core, installed here too) |
| `faker`             | 30.0.0  | Fake data generation (used by core)              |
| `python-dotenv`     | 1.0.1   | Load `.env` file for API key                     |
| `python-dateutil`   | latest  | Date parsing for perturbation (used by core)     |

### Install Command
`pip install -r requirements.txt`

---

## v1 → v2 Migration Summary

| What Changed               | v1                                       | v2                                                   |
| :------------------------- | :--------------------------------------- | :--------------------------------------------------- |
| `sanitize_prompt()` return | 2-tuple `(text, entities)`               | 4-tuple `(text, entities, alias_map, privacy_score)` |
| Entity dict fields         | `text`, `label`, `score`                 | + `tier`, `start`, `end`, `source`                   |
| EntityInfo model           | 3 fields                                 | 5 fields (+ `tier`, `score`)                         |
| ChatResponse               | 4 fields                                 | 5 fields (+ `privacy_score`)                         |
| `/reset` implementation    | `sanitizer = Sanitizer()` (5-sec reload) | `sanitizer.clear()` (instant)                        |
| New files                  | —                                        | `pattern_scanner.py`, `entity_classifier.py`         |
