# ⚙️ Backend Design Document: Silent-Protocol

**Owner:** Aum
**Deliverables:** `main.py`, `requirements.txt`, `.env`
**Stack:** Python 3.11 + FastAPI + Groq SDK
**Run Command:** `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

---

## 1. Overview

The backend is a FastAPI HTTP server that acts as the bridge between the frontend and the LLM. It:
1. Receives chat messages from the frontend via HTTP POST
2. Passes them through Aayush's Sanitizer (imported from `core/`)
3. Sends the sanitized text to Groq's LLM API
4. Receives the LLM response
5. Passes it back through the Sanitizer to restore original names
6. Returns everything (response + debug info) as JSON to the frontend

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

This is necessary because the frontend (served by Live Server on port 5500) and the backend (port 8000) are on different origins.

---

## 3. Global State

When the server starts, it initializes two global objects:

1. **Sanitizer instance** — Loaded once from `core/sanitizer.py`. This loads the GLiNER model into memory (~5 seconds on first startup, uses cache after that). This instance persists for the entire server session.

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
2. Call `sanitizer.sanitize_prompt(request.message)` → returns `(sanitized_text, entities_list)`
3. Send `sanitized_text` to Groq's chat completion API with model `llama-3.1-70b-versatile`, temperature `0.7`, max tokens `2048`
4. Get the raw LLM response text
5. Call `sanitizer.desanitize_response(raw_response)` → returns the text with real names restored
6. Build the entity info list: for each detected entity, include the original text, the label, and the alias it was replaced with
7. Return the full response object

**Success Response (200):**
A JSON object with:
- `response` (string): The final, de-sanitized response with real names
- `sanitized_prompt` (string): What the LLM actually received (with fake names)
- `entities_detected` (array): List of objects, each containing:
  - `text` (string): The original entity ("Apple Inc")
  - `label` (string): The entity type ("organization")
  - `alias` (string): The fake replacement ("Orion Corp")
- `silent_mode` (boolean): Whether sanitization was active (always `true` for MVP)

**Error Response (500):**
A JSON object with:
- `error` (string): Short error description
- `detail` (string): Full error message from the exception

**Error Handling:**
- Wrap the entire processing flow in a try/catch
- If the Groq API fails (network error, rate limit, etc.), return a 500 with a descriptive message
- If the Sanitizer fails (model error, unexpected input), return a 500 with a descriptive message
- Do not crash the server on any error — always return valid JSON

---

### 4.2 `GET /health` — Health Check

**Purpose:** Quick check that the server is running and its dependencies are loaded.

**Response (200):**
A JSON object with:
- `status` (string): Always "ok" if this endpoint responds
- `model_loaded` (boolean): Whether the GLiNER model is loaded in memory (`true` or `false`)
- `groq_configured` (boolean): Whether the GROQ_API_KEY environment variable is set

**No request body needed.**

---

### 4.3 `GET /aliases` — Current Alias Map

**Purpose:** Returns the current session's alias mapping. Useful for the debug panel and for verifying consistency.

**Response (200):**
A JSON object with:
- `aliases` (object): Key-value pairs where keys are real entity names and values are fake alias names. Example: `{"Apple Inc": "Orion Corp", "Tim Cook": "James Mitchell"}`
- `total` (integer): Number of aliases currently stored

---

### 4.4 `POST /reset` — Clear Session

**Purpose:** Clears all stored aliases and creates a fresh Sanitizer instance. Used when the user wants to start a new conversation.

**Processing Steps:**
1. Create a new Sanitizer instance (this also creates a new AliasManager with empty dictionaries)
2. Replace the global sanitizer variable with the new instance
3. Note: The GLiNER model is re-loaded. This takes ~5 seconds. (Optimization: cache the model and only reset the AliasManager. But for MVP, full reload is fine.)

**Response (200):**
- `status` (string): "reset"
- `message` (string): "All aliases cleared"

---

## 5. Data Models

The backend uses 4 Pydantic models for request/response validation:

### ChatRequest
| Field     | Type   | Required | Description             |
| :-------- | :----- | :------- | :---------------------- |
| `message` | string | Yes      | The user's chat message |

### EntityInfo
| Field   | Type   | Description                              |
| :------ | :----- | :--------------------------------------- |
| `text`  | string | Original entity text ("Apple Inc")       |
| `label` | string | Entity type ("organization")             |
| `alias` | string | The fake replacement used ("Orion Corp") |

### ChatResponse
| Field               | Type               | Description                              |
| :------------------ | :----------------- | :--------------------------------------- |
| `response`          | string             | Final response with real names restored  |
| `sanitized_prompt`  | string             | What the LLM actually saw                |
| `entities_detected` | list of EntityInfo | All detected entities with their aliases |
| `silent_mode`       | boolean            | Whether sanitization was active          |

### ErrorResponse
| Field    | Type   | Description           |
| :------- | :----- | :-------------------- |
| `error`  | string | Short error message   |
| `detail` | string | Full exception detail |

---

## 6. Groq LLM Integration

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

### How the LLM Call Works
- The Groq SDK is used (pip install `groq`)
- A chat completion is created with a single user message (the sanitized prompt)
- The response object contains `choices[0].message.content` which is the LLM's text response
- This text is then passed through the de-sanitizer

---

## 7. Import Structure

The backend imports from the `core/` directory (Aayush's code). Since `core/` is a sibling directory to `backend/`, the Python path needs to be extended to include the parent directory so that `from core.sanitizer import Sanitizer` works.

Alternative: Add `../core` to the system path at the top of `main.py`.

### What the backend imports from core:
- `Sanitizer` class from `core/sanitizer.py`
  - `.sanitize_prompt(text)` → returns tuple of (sanitized text, entity list)
  - `.desanitize_response(text)` → returns de-sanitized text
  - `.alias_manager.real_to_fake` → dictionary for building entity info
  - `.alias_manager.get_mapping()` → dictionary for the `/aliases` endpoint

---

## 8. Dependencies

### Python Packages

| Package             | Version | Purpose                                          |
| :------------------ | :------ | :----------------------------------------------- |
| `fastapi`           | 0.115.0 | Web framework                                    |
| `uvicorn[standard]` | 0.32.0  | ASGI server to run FastAPI                       |
| `groq`              | 0.11.0  | Groq API SDK                                     |
| `gliner`            | 0.2.7   | Zero-shot NER (used by core, installed here too) |
| `faker`             | 30.0.0  | Fake data generation (used by core)              |
| `python-dotenv`     | 1.0.1   | Load `.env` file for API key                     |

### Install Command
`pip install -r requirements.txt`

---

## 9. AI Prompts for Aum

### Prompt 1: Basic Server Setup
> "Write a Python FastAPI server with CORS middleware that allows all origins. It should have one POST endpoint called /chat that accepts a JSON body with a 'message' field, sends it to Groq API using the groq library with model llama-3.1-70b-versatile, and returns the response text. Load the API key from a .env file using python-dotenv. Include Pydantic models for request and response validation."

### Prompt 2: Health Endpoint
> "Add a GET endpoint at /health to my FastAPI server that returns a JSON object with status 'ok', whether a model variable is not None (model_loaded), and whether the GROQ_API_KEY environment variable is set (groq_configured)."

### Prompt 3: Error Handling
> "Add try/except error handling to my FastAPI /chat endpoint. If anything fails, return a JSON error response with HTTP status 500 containing an 'error' field and a 'detail' field. Use FastAPI's HTTPException."

### Prompt 4: Sanitizer Integration
> "I have a Sanitizer class imported from a core module. It has sanitize_prompt(text) which returns a tuple of (sanitized_text, entities_list) and desanitize_response(text) which returns cleaned text. Integrate it into my /chat endpoint so the message is sanitized before sending to Groq and the response is de-sanitized before returning to the frontend. Also return the sanitized_prompt and entity list in the response."
