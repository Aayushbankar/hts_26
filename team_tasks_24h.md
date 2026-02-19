# 👥 Team Task Distribution: 24-Hour Hackathon Sprint

**Project:** Aegis (AI Privacy Shield)
**Timeline:** 24 Hours (No Sleep Option)

## 🎭 The Cast
1.  **Aayush (The Architect / Safety Net):** Handles the "Hard ML Stuff," Integration, and fixes whatever breaks.
2.  **Divya (The Designer / Frontend):** Uses AI to turn Canva/Figma designs into Next.js code.
    *   *Goal:* Make the app look "Enterprise & Trustworthy."
3.  **Aum (The Backend Support / Utility):** Uses AI to build simple Python endpoints and generate the "Pitch Assets."
    *   *Goal:* Ensure the backend server runs and the Demo Video looks real.

---

## 🕒 The 24-Hour Schedule

### Phase 1: Setup & Design (Hours 0-4)

| **Time** | **Aayush (Lead)**                                                                                       | **Divya (Frontend)**                                                                                            | **Aum (Backend)**                                                                                                   |
| :------- | :------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------ |
| **0-1h** | **Repo Setup:** Init Next.js + FastAPI. Set up GitHub repo and invite team.                             | **Inspiration:** Find 3 "Cybersecurity SaaS" designs on Dribbble/Pinterest. Pick a Color Palette (Dark Mode).   | **Environment:** Install Python, VS Code, Git. Clone the repo. Run `Hello World` in FastAPI.                        |
| **1-4h** | **Core Logic Start:** Initialize `TextAttack` script. Test if you can break `all-MiniLM-L6-v2` locally. | **Design (Figma/Canva):** Design the "Upload Page" and "Success Page." Don't code yet. Make it look scary good. | **Boilerplate:** Ask ChatGPT: *"Write a FastAPI main.py with a file upload endpoint."* Get it running on localhost. |

### Phase 2: The "Build" (Hours 4-14)

| **Time**   | **Aayush (Lead)**                                                                                 | **Divya (Frontend)**                                                                                                                       | **Aum (Backend)**                                                                                                                   |
| :--------- | :------------------------------------------------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------- |
| **4-8h**   | **The Poison Engine:** Write the `perturb_text()` function. This is the hardest part. Focus here. | **AI Coding:** Take screenshots of your Figma design. Upload to `v0.dev` or `ChatGPT`. Prompt: *"Turn this into Next.js + Tailwind code."* | **File Handling:** Write a script to "fake" the processing time. (e.g., `time.sleep(3)`). We need a "Progress Bar" endpoint.        |
| **8-12h**  | **PDF Reconstruction:** Figure out how to overlay the invisible text on the PDF.                  | **Refinement:** Paste the AI code into VS Code. Fix the broken buttons. Change colors to match your design.                                | **The "Hero File":** Create the *perfect* PDF for the demo. (e.g., "Top Secret Apple Merger.pdf"). A fake document that looks real. |
| **12-14h** | **Integration Check:** Connect Frontend (Divya) to Backend (Aum/Aayush). Fix CORS errors.         | **Polish:** Add "Glitch Effects" or "cool scanning animations" (use AI to generate CSS keyframes).                                         | **Test:** Try uploading a file to the local server 50 times. Find bugs.                                                             |

### Phase 3: The "Sales" Polish (Hours 14-20)

| **Time**   | **Aayush (Lead)**                                                                                  | **Divya (Frontend)**                                                                       | **Aum (Backend)**                                                                                |
| :--------- | :------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------- |
| **14-18h** | **The "Verify" Script:** Build the script that proves the file is poisoned (Local ChromaDB check). | **Landing Page:** Design a simple "Home Page" with a big "Protect Your IP" headline.       | **Docs:** Write a `README.md` with "How to Run". Take screenshots of the app for the submission. |
| **18-20h** | **Emergency Fixes:** If Aum's backend breaks, fix it. If Divya's CSS is misaligned, fix it.        | **Mobile Check:** Ensure it doesn't look broken on a phone (Judges might check on mobile). | **Scripting:** Write the specific script for the Live Demo. *"We will say X, then click Y."*     |

### Phase 4: The Final Stretch (Hours 20-24)

| **Time**   | **Aayush (Lead)**                                                            | **Divya (Frontend)**                                                                   | **Aum (Backend)**                                                                            |
| :--------- | :--------------------------------------------------------------------------- | :------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------- |
| **20-22h** | **Rehearsal:** Run the full demo 3 times. Ensure the "Poisoning" works live. | **Final Tweaks:** Change "Upload" button text to "Cloak Document." Make it sound cool. | **Submission:** Prepare the Devpost/GitHub submission text. "Problem, Solution, Tech Stack." |
| **22-24h** | **Buffer:** Sleep / Eat / Panic.                                             | **Relax:** You are done.                                                               | **Relax:** You are done.                                                                     |

---

## 🛠️ Tools & Prompts (Cheat Sheet)

### For Divya (Frontend)
*   **Tool:** `v0.dev` (by Vercel) or `ChatGPT-4 Vision`.
*   **Prompt:** *"I am uploading a design of a cyber-security dashboard. Please write the creating React (Next.js) code using Tailwind CSS to match this pixel-perfect. Use a dark theme with neon green accents."*
*   **Prompt 2:** *"Add a CSS animation to this button so it glows when I hover over it."*

### For Aum (Backend)
*   **Tool:** `ChatGPT-4` / `Cursor`.
*   **Prompt:** *"I need a FastAPI endpoint in Python that accepts a PDF file upload, saves it to a 'temp' folder, and returns a JSON response `{'status': 'success', 'filename': '...'}`. handle errors if the file is not a PDF."*
*   **Prompt 2:** *"Write a Python script to convert a PDF page to a PNG image using `pymupdf`."*
