import os
import sys
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

# add project root so we can import core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.sanitiser import Sanitizer
except ImportError as e:
    print(f"Could not import core.sanitiser: {e}")
    print("Make sure you're running from the backend/ dir and core/ is a sibling.")
    sys.exit(1)


# --- config ---

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(env_path)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("WARNING: GROQ_API_KEY not found. LLM calls will fail.")

client = Groq(api_key=api_key)

# load the sanitizer (this downloads GLiNER on first run, takes a few seconds)
print("Loading core engine...")
sanitizer = Sanitizer()
print("Core engine ready.")

# conversation history for multi-turn context
conversation_history: list[dict] = []


app = FastAPI(
    title="Silent-Protocol API",
    description="Privacy-preserving AI proxy with 3-layer sanitization",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- request/response models ---

class ChatRequest(BaseModel):
    message: str

class EntityInfo(BaseModel):
    text: str
    label: str
    alias: str
    tier: str
    score: float

class PrivacyScore(BaseModel):
    score: int
    risk_level: str
    total_entities: int
    replaced: int
    perturbed: int
    preserved: int
    hipaa_identifiers_found: int
    hipaa_identifiers_protected: int

class ChatResponse(BaseModel):
    response: str
    sanitized_prompt: str
    entities_detected: List[EntityInfo]
    privacy_score: PrivacyScore
    silent_mode: bool = True


# --- endpoints ---

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": "2.1.0",
        "core_loaded": True,
        "model_name": "gliner_medium-v2.1",
        "groq_configured": bool(api_key),
        "conversation_turns": len(conversation_history),
    }


@app.get("/aliases")
def get_aliases():
    mapping = sanitizer.get_alias_map()
    return {"aliases": mapping, "total": len(mapping)}


@app.post("/reset")
def reset_session():
    global conversation_history
    sanitizer.clear()
    conversation_history = []
    return {"status": "reset", "message": "Session cleared."}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main pipeline:
    1. Sanitize user message (strip PII)
    2. Send sanitized text to LLM with full conversation history
    3. De-sanitize LLM response (put real names back)
    4. Return everything for the frontend to display
    """
    try:
        # sanitize
        sanitized_text, entities, alias_map, score_dict = sanitizer.sanitize_prompt(request.message)

        # send to LLM with conversation context
        conversation_history.append({"role": "user", "content": sanitized_text})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation_history,
            temperature=0.7,
            max_tokens=2048,
        )
        llm_response = completion.choices[0].message.content

        conversation_history.append({"role": "assistant", "content": llm_response})

        # de-sanitize (swap fakes back to real names in the response)
        restored = sanitizer.desanitize_response(llm_response)

        # build response
        entity_infos = []
        for e in entities:
            used_alias = alias_map.get(e["text"], e["text"])
            entity_infos.append(EntityInfo(
                text=e["text"],
                label=e["label"],
                alias=used_alias,
                tier=e.get("tier", "UNKNOWN"),
                score=e.get("score", 1.0)
            ))

        privacy_data = PrivacyScore(**score_dict)

        return ChatResponse(
            response=restored,
            sanitized_prompt=sanitized_text,
            entities_detected=entity_infos,
            privacy_score=privacy_data,
            silent_mode=True
        )

    except Exception as e:
        print(f"Error in /chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print()
    print("  API:      http://127.0.0.1:8000")
    print("  Docs:     http://127.0.0.1:8000/docs")
    print("  Frontend: open http://127.0.0.1:5500/frontend/ via Live Server")
    print()
    uvicorn.run(app, host="127.0.0.1", port=8000)