# 👨‍✈️ Leader's Kickoff Script (Silent-Protocol)

**Time needed:** 15 minutes with team, then everyone splits.

---

## The 60-Second Pitch to Your Team

> "We're building a **privacy wrapper for ChatGPT.**
> The user types a message with real names and secrets.
> Our tool detects those secrets, replaces them with fakes,
> sends the fake version to the AI, gets the answer,
> and puts the real names back in.
>
> **The AI never sees the truth. The user gets the full answer.**
>
> Divya — you build the chat window.
> Aum — you build the API that talks to the AI.
> I build the brain that swaps the names."

---

## Setup Checklist (Do This Together)

```text
/silent-protocol
  /backend          ← Aum works here
    main.py
    requirements.txt
  /frontend         ← Divya works here
    index.html
    style.css
    script.js
  /core             ← Aayush works here
    sanitizer.py
    alias_manager.py
```

1. Create repo → push → invite both as collaborators
2. Divya: install "Live Server" extension in VS Code
3. Aum: run `pip install fastapi uvicorn groq` and get Groq API key
4. You: run `pip install gliner faker`

---

## The "Check-In" Rule

**Every 2 hours:**
1. Everyone stops coding
2. Git pull + merge
3. Quick screen share: "Show me what you have"
4. You fix any broken connections

**The Integration Moment (Hour 10–12):**
This is when Divya's UI talks to Aum's API through your sanitizer for the first time. **Be ready — things will break.** That's normal.

---

## If Things Go Wrong

| Problem                  | Solution                                                   |
| :----------------------- | :--------------------------------------------------------- |
| Divya's CSS looks bad    | "Paste the HTML into ChatGPT and ask it to fix the layout" |
| Aum's server crashes     | "Paste the full error into ChatGPT and ask for a fix"      |
| GLiNER misses an entity  | Add it manually to the alias map for the demo              |
| Groq API is slow/down    | Switch to OpenAI API (same code, different client)         |
| Nothing works at Hour 20 | Use the pre-recorded demo video as backup                  |
