import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

# 1. Load your specific environment file (Fix for your current error)
load_dotenv("siliconsquad.env") 

# 2. Initialize the Groq client using the key from siliconsquad.env
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ ERROR: GROQ_API_KEY not found in siliconsquad.env")
client = Groq(api_key=api_key)

app = FastAPI(title="Silent-Protocol Backend")

# 3. CORS Setup: Allows your frontend to communicate with this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Data Models: Defines what the request and response look like
class ChatRequest(BaseModel):
    message: str

# 5. Health Check: Use this to verify the server is working
@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
        "env_file_used": "siliconsquad.env"
    }

# 6. Main Chat Endpoint: Sends your message to the AI
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Sends the user message to Groq LLM
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": request.message}],
            temperature=0.7,
            max_tokens=2048,
        )
        # Returns the AI's response text
        return {"response": completion.choices[0].message.content}
    
    except Exception as e:
        # If the API fails, this sends a clear error message instead of crashing
        raise HTTPException(status_code=500, detail=str(e))
    

# 7. Aliases Endpoint (Placeholder for Task 4.2)
@app.get("/aliases")
async def get_aliases():
    return {"aliases": {}, "total": 0}

# 8. Reset Endpoint (Placeholder for Task 4.3)
@app.post("/reset")
async def reset_session():
    return {"status": "reset", "message": "All aliases cleared"}