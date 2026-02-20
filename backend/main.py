import os
import sys
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

# ─────────────────────────────────────────────────────────
#  CORE INTEGRATION SETUP
# ─────────────────────────────────────────────────────────

# Add project root to sys.path to allow importing from 'core'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.sanitiser import Sanitizer
except ImportError as e:
    print(f"❌ CRITICAL ERROR: Could not import 'core.sanitiser'.\nError: {e}")
    print("Make sure you are running from the 'backend/' directory and 'core/' is a sibling.")
    sys.exit(1)


# ─────────────────────────────────────────────────────────
#  CONFIGURATION & STATE
# ─────────────────────────────────────────────────────────

# Load .env from project root
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(env_path)

# Initialize Groq Client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    # Check if user set it in the environment directly
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("⚠️  WARNING: GROQ_API_KEY not found in .env or environment variables.")
        print("   LLM calls will fail until configured.")

client = Groq(api_key=api_key)

# Initialize Core Sanitizer (Loads GLiNER model - takes ~5s on first run)
print("⏳ Initializing Silent-Protocol Core Engine (loading GLiNER)...")
sanitizer = Sanitizer()
print("✅ Core Engine Ready!")


app = FastAPI(
    title="Silent-Protocol Backend",
    description="Privacy-preserving AI proxy using 3-layer sanitization pipeline.",
    version="2.0.0"
)

# CORS Setup - Essential for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon/dev, allow all. Prod: restrict to frontend URL.
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────
#  DATA MODELS (v2 API)
# ─────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str

class EntityInfo(BaseModel):
    text: str
    label: str
    alias: str
    tier: str  # REPLACE, PERTURB, PRESERVE
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


# ─────────────────────────────────────────────────────────
#  API ENDPOINTS
# ─────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Verify backend is running and dependencies are loaded."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "core_loaded": True,
        "model_name": "gliner_medium-v2.1",
        "groq_configured": bool(api_key)
    }


@app.get("/aliases")
def get_aliases():
    """Get the current session's real -> fake mapping."""
    mapping = sanitizer.get_alias_map()
    return {
        "aliases": mapping,
        "total": len(mapping)
    }


@app.post("/reset")
def reset_session():
    """Clear all alias mappings for the current session."""
    sanitizer.clear()
    return {"status": "reset", "message": "All privacy mappings cleared."}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main pipeline: 
    1. Sanitize user prompt (PII removal/perturbation)
    2. Send sanitized text to LLM
    3. De-sanitize LLM response (restore real names)
    4. Return full privacy report
    """
    try:
        # Step 1: Sanitize (The Core Logic)
        # Returns 4-tuple: text, entities_list, alias_map, privacy_score_dict
        sanitized_text, entities, alias_map, privacy_score_dict = sanitizer.sanitize_prompt(request.message)

        # Step 2: Call LLM with SAFE text
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": sanitized_text}],
            temperature=0.7,
            max_tokens=2048,
        )
        llm_response_text = completion.choices[0].message.content

        # Step 3: De-sanitize (Restore real names in response)
        restored_response = sanitizer.desanitize_response(llm_response_text)

        # Step 4: Build Response Object
        
        # Convert raw entities dicts to Pydantic models
        entity_infos = []
        for e in entities:
            # Look up the alias used for this text
            # Default to text itself if not in map (e.g. PERTURB/PRESERVE types might not be in map)
            used_alias = alias_map.get(e["text"], e["text"])
            
            # For perturbed items (date/money), the "alias" is the perturbed string in the sanitized text.
            # But the alias_map primarily tracks REPLACE types.
            # We can infer the alias from the sanitized text if needed, but for the UI, 
            # we mainly care about REPLACE mappings. 
            
            entity_infos.append(EntityInfo(
                text=e["text"],
                label=e["label"],
                alias=used_alias,
                tier=e.get("tier", "UNKNOWN"),
                score=e.get("score", 1.0) # Regex entities might not have score, default to 1.0
            ))

        # Build Privacy Score object
        privacy_data = PrivacyScore(
            score=privacy_score_dict["score"],
            risk_level=privacy_score_dict["risk_level"],
            total_entities=privacy_score_dict["total_entities"],
            replaced=privacy_score_dict["replaced"],
            perturbed=privacy_score_dict["perturbed"],
            preserved=privacy_score_dict["preserved"],
            hipaa_identifiers_found=privacy_score_dict["hipaa_identifiers_found"],
            hipaa_identifiers_protected=privacy_score_dict["hipaa_identifiers_protected"]
        )

        return ChatResponse(
            response=restored_response,
            sanitized_prompt=sanitized_text,
            entities_detected=entity_infos,
            privacy_score=privacy_data,
            silent_mode=True
        )

    except Exception as e:
        print(f"❌ Error in /chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ─────────────────────────────────────────────────────────
#  DIRECT EXECUTION
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print()
    print("  🌐  API:   http://127.0.0.1:8000")
    print("  📖  Docs:  http://127.0.0.1:8000/docs")
    print("  💡  Frontend: open http://127.0.0.1:5500/frontend/ via Live Server")
    print()
    uvicorn.run(app, host="127.0.0.1", port=8000)