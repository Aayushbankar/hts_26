# 🛡️ AEGIS: The AI Privacy Shield (Master Plan)

> **One-Liner:** "The invisible firewall for your documents. Humans can read them; AI can't."

---

## 1. Problem Statement (The "Pain")
**The Status Quo:** Enterprises are blocking ChatGPT and Copilot because they are terrified of "Data Leakage."
*   **The Leak:** Employee uploads a PDF -> OpenAI trains on it (or RAG indexes it) -> Competitor asks ChatGPT about your trade secrets -> ChatGPT answers.
*   **The Gap:** Current DLP (Data Loss Prevention) tools are binary: Block access or Allow access. They cannot "sanitize" the meaning of a document without destroying its readability for humans.

## 2. The Solution ("Aegis")
**Aegis** is a "Cognitive Cloaking Layer." It is a middleware that modifies documents before they leave the secure perimeter.
*   **For Humans:** The document looks 100% identical. Text is readable.
*   **For AI Models:** The document is "poisoned."
    1.  **Summarization Fails:** The AI outputs gibberish or unrelated topics.
    2.  **RAG Search Fails:** The document becomes "invisible" to Vector Search (Embeddings are pushed to null space).

## 3. Methodology (The "Secret Sauce")
We use **Adversarial Machine Learning** techniques to attack the *Attention Mechanism* of Transformer models.

### Technique A: Universal Adversarial Triggers (UAT)
We inject optimized sequences of tokens (often hidden via zero-width characters or white-text) that act as "Hypnotic Triggers" for the LLM.
*   *Effect:* When the LLM attends to these tokens, its internal state collapses, preventing it from attending to the *actual* confidential information.

### Technique B: Gradient-Based Embedding Drift
We subtly perturb specific synonyms in the text to shift the semantic vector of the document.
*   *Effect:* If the document is about "Secret Project X", Aegis shifts its vector to match "Generic Cooking Recipe." When a user queries "Tell me about Project X", the RAG system finds nothing (Cosine Similarity < 0.2).

---

## 4. Architecture Flowmap

```mermaid
graph TD
    User[User/Employee] -->|Uploads Confidential PDF| Frontend[Aegis Dashboard (Next.js)]
    Frontend -->|Raw File| API[FastAPI Poison Engine]
    
    subgraph "The Poison Factory (Core Logic)"
        API --> Extractor[Text Extractor]
        Extractor --> Ranker[Saliency Ranker (Finds Critical Keywords)]
        Ranker --> Generator[UAT Generator (Injects Triggers)]
        Generator --> Attacker[Gradient Attacker (Shifts Embeddings)]
        Attacker --> Reconstructor[PDF Rebuilder (Visual Layer)]
    end
    
    Reconstructor -->|Cloaked PDF| Cloud[Public Cloud / ChatGPT]
    
    subgraph "The 'Glitch' Demo"
        Cloud -->|AI Tries to Read| AI_Brain[LLM / Vector DB]
        AI_Brain -->|Output| Fail[ERROR: 'I cannot summarize this content']
    end
```

---

## 5. Technical Stack (Enterprise MVP)

| Component       | Technology                    | Reasoning                                                         |
| :-------------- | :---------------------------- | :---------------------------------------------------------------- |
| **Frontend**    | **Vanilla HTML + CSS + JS**   | Simple, no build steps. Easy for Divya to edit.                   |
| **Backend API** | **FastAPI** (Python)          | Native support for PyTorch/ML libraries. Async speed.             |
| **ML Engine**   | **PyTorch** + **HuggingFace** | Access to `bert-base-uncased` and `all-MiniLM-L6-v2` for attacks. |
| **Attack Lib**  | **TextAttack** (Customized)   | We will build a custom "Recipe" on top of this framework.         |
| **Vector DB**   | **ChromaDB** (Local)          | Lightweight, fast vector store to *prove* the RAG failure.        |
| **PDF Tools**   | **PyMuPDF** / **ReportLab**   | Essential for reconstructing the "human-readable" layer.          |

---

## 6. Functional & Non-Functional Requirements

### Functional Requirements (FRs)
1.  **Upload:** User can upload PDF/DOCX up to 10MB.
2.  **Processing:** System must return a "Cloaked" file within 30 seconds.
3.  **Visual Fidelity:** Cloaked file must look 99% identical to the original (Human Review).
4.  **Verification:** System must provide a "Visibility Score" (0-100%) showing how much an AI can "see."

### Non-Functional Requirements (NFRs)
1.  **Latency:** Total processing time < 5s per page.
2.  **Stealth:** The injected triggers must not be flagged by standard spellcheckers (if possible).
3.  **Scalability:** The architecture acts as a stateless API (Serverless ready).

---

## 7. Development Timeline (48 Hours)

| Module             | Task                                            | Est. Time | Owner        |
| :----------------- | :---------------------------------------------- | :-------- | :----------- |
| **Initialization** | Setup Repo, Next.js, FastAPI, Docker            | 4 Hours   | Lead Dev     |
| **Core ML (A)**    | Implement `EmbeddingDrift` Algorithm (Python)   | 12 Hours  | ML Engineer  |
| **Core ML (B)**    | Implement `UniversalTrigger` Injection          | 10 Hours  | ML Engineer  |
| **Frontend UI**    | Build Dashboard, Upload, and "Split View"       | 8 Hours   | Frontend Dev |
| **PDF Engine**     | Rebuilding the visual layer (The "Magic Trick") | 8 Hours   | Backend Dev  |
| **Integration**    | Connecting UI to API, Error Handling            | 4 Hours   | All          |
| **Pitch Prep**     | Slide deck, Live Demo Rehearsal (The "Glitch")  | 2 Hours   | Lead         |

*Total: ~48 Hours (including sleep/eating constraints)*

---

## 8. The "Sellable" Pitch

*   **Hook:** "Every time your employee uploads a PDF to ChatGPT, you leak IP. Firewalls stop *files*; Aegis stops *meaning*."
*   **The Demo:** Show a side-by-side.
    *   *Left:* Original Contract. ChatGPT summarizes it perfectly.
    *   *Right:* Aegis Contract. Looks identical. ChatGPT says "This document appears to be about 18th-century gardening tactics."
*   **The Ask:** "We are building the SSL layer for the Age of AI."

---

## 9. Pros & Cons

### Pros
*   **High "Wow" Factor:** Visually demonstrating AI failing is powerful.
*   **Timely:** Solves the #1 Enterprise AI blocker (Privacy).
*   **Defensible Tech:** Adversarial ML is hard to replicate quickly.

### Cons
*   **Cat & Mouse Game:** AI models get smarter (e.g., OCR vision models might bypass text-layer attacks). *Mitigation: We focus on Text-Layer RAG for the MVP.*
*   **Ethical Risk:** Could be used by bad actors to hide malicious content. *Mitigation: Frame as "Defensive Use Only".*
