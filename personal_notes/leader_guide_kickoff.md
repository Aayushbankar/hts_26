# 👨‍✈️ Team Leader's Guide: The Kick-Off Meeting (Aegis)

**Objective:** You have 1 hour to get Divya and Aum set up, confident, and working.
**Your Role:** You are the Architect. They are the Builders. You define *what* to build; they find out *how* (using AI).

---

## 1. The "Pep Talk" (5 Minutes)
**Context:** They are newbies. They are nervous.
**Say this:**
> "We are building a tool that 'poisons' documents so AI can't steal them. It sounds complex, but we have a cheat code: **We are using AI to build it.**"
> "Divya, you own the Look. If it looks cool, we win."
> "Aum, you own the Engine. If it runs, we win."
> "I will glue it all together. Just focus on your specific tasks."

---

## 2. The Setup Phase (15 Minutes)
*Do this together on one screen before they split up.*

1.  **Create the Folder Structure** (You do this on your machine & push to Git):
    ```text
    /aegis-project
      /backend       <-- Aum's domain (FastAPI)
      /frontend      <-- Divya's domain (index.html, style.css)
      /notebooks     <-- Your domain (text_attack.ipynb)
    ```
2.  **GitHub Invite:** Add them as collaborators. Ensure they can `git clone` and `git push`.
3.  **VS Code:** Ensure they both have VS Code installed with the "Live Server" extension (for Divya) and "Python" extension (for Aum).

---

## 3. Assigning Specific Tasks (The "Orders")

### 👉 To Divya (Frontend)
**Your Goal:** "Make it look like a scary, high-tech FBI dashboard."
1.  **Design First:** Open Canva or Figma. Create a dark mode interface.
    *   Big Green "Upload" box in the center.
    *   A "Terminal-style" log at the bottom.
2.  **AI Transformation:** specific instructions:
    *   "Take a screenshot of your design."
    *   "Go to ChatGPT-4o or v0.dev."
    *   "Prompt: *'Turn this image into a single HTML file with embedded CSS. Use a distinct dark theme. No React, just plain HTML/CSS.'*"
3.  **Deliverable:** A folder with `index.html`, `style.css`, `script.js`.

### 👉 To Aum (Backend)
**Your Goal:** "Build a Python server that accepts a file."
1.  **FastAPI Basics:** "Don't worry about the complex logic yet. Just get the server running."
2.  **AI Transformation:** specific instructions:
    *   "Go to ChatGPT."
    *   "Prompt: *'Write a simple Python FastAPI server that runs on port 8000. It should have one endpoint `/upload` that accepts a PDF file and saves it to a folder called `uploads`. Give me the code.'*"
3.  **Deliverable:** A `main.py` file that runs without errors.

---

## 4. Your Workflow (The "Safety Net")
While they struggle with the basics (first 2 hours):
1.  **Don't code yet.** Walk around (or screen share) and unblock them.
2.  **Fix Git errors.** They *will* have merge conflicts. You fix them.
3.  **Encourage.** If Divya's CSS is broken, say "Ask Claude to fix the alignment." If Aum's Python crashes, say "Paste the error into ChatGPT."

---

## 5. The "Check-In" (Every 2 Hours)
*   **Stop working.**
*   **Merge code.** (You pull their changes to your 'main' branch).
*   **Show progress.** "Look, Divya's button now talks to Aum's server!" (Even if it just prints 'Hello').

**Ready? Go lead them.**
