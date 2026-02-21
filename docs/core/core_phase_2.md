<!-- #  Phase 2 Checklist: Sanitizer (The Detective) -->

> **Goal:** Build the class that uses GLiNER AI to FIND entities in text, then hands them to AliasManager to replace them.

> **File:** `core/sanitiser.py`

---

##  Step 1: Imports

- [ ] Import `GLiNER` from `gliner`
- [ ] Import `AliasManager` from `alias_manager`

> **Why two imports?**
> - `GLiNER` = the AI model that reads text and finds names/companies/locations
> - `AliasManager` = YOUR class from Phase 1 that replaces them with fakes

---

##  Step 2: Class + Constructor (`__init__`)

- [ ] **Define class:** `class Sanitizer:`
- [ ] **Load the AI model:**
  - `self.model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")`
  - This downloads the model the first time (~500MB), then uses cache
- [ ] **Create your AliasManager:**
  - `self.alias_manager = AliasManager()`
  - This is a fresh empty notebook — no aliases stored yet
- [ ] **Define what to look for:**
  - `self.labels` = a list of 11 strings: the types of sensitive info we detect
  - The labels are: `"person"`, `"organization"`, `"location"`, `"date"`, `"email address"`, `"phone number"`, `"project name"`, `"product name"`, `"money amount"`, `"medical condition"`, `"government id"`

> **How it works together:**
> ```
> User types: "Tim Cook works at Apple in Cupertino"
>                   ↓
>            GLiNER (self.model) scans the text
>                   ↓
>            Finds: [Tim Cook → person, Apple → org, Cupertino → location]
>                   ↓
>            AliasManager replaces each one with a fake
>                   ↓
>            Output: "James Mitchell works at Orion Corp in Portland"
> ```

---

## 🔍 Step 3: `sanitize_prompt(self, user_prompt)`

**What it does:** Takes the user's raw message → finds all entities → replaces them → returns both.

- [ ] **Call GLiNER to detect entities:**
  - `entities = self.model.predict_entities(user_prompt, self.labels, threshold=0.5)`
  - This returns a list of dicts like: `[{"text": "Apple", "label": "organization", "score": 0.97}]`
  - `threshold=0.5` means: only include entities the AI is at least 50% sure about
- [ ] **Call AliasManager to replace them:**
  - `sanitized_text = self.alias_manager.sanitize(user_prompt, entities)`
  - This is YOUR code from Phase 1 — it sorts longest-first, replaces each entity
- [ ] **Return BOTH values as a tuple:**
  - `return sanitized_text, entities`
  - We return `entities` too because the backend needs the list for the debug panel

> **Why a tuple?** The backend needs TWO things:
> 1. The cleaned text (to send to the AI)
> 2. The entity list (to show in the debug panel)

---

##  Step 4: `desanitize_response(self, llm_response)`

**What it does:** Takes the AI's response (which has fake names) → puts real names back.

- [ ] **Call AliasManager's desanitize:**
  - `return self.alias_manager.desanitize(llm_response)`
- [ ] That's it. One line. AliasManager already knows the mapping from Phase 1.

> **Example:**
> ```
> AI said:    "Orion Corp should file the patent by March..."
> After this: "Apple should file the patent by March..."
> ```

---

##  Step 5: `get_alias_map(self)`

**What it does:** Returns the current notebook of real→fake mappings. Used by the `/aliases` API endpoint.

- [ ] **Call AliasManager's get_mapping:**
  - `return self.alias_manager.get_mapping()`
- [ ] Also one line.

---

##  Done Checklist

When you're finished, your file should have:
- [ ] 2 import lines
- [ ] 1 class with `__init__` that sets up 3 things (model, alias_manager, labels)
- [ ] `sanitize_prompt()` — 3 lines (detect, replace, return)
- [ ] `desanitize_response()` — 1 line
- [ ] `get_alias_map()` — 1 line

**Total: ~30 lines of code.** Much shorter than `alias_manager.py`!

---

###  Ready to Code?
Open `core/sanitiser.py` and start with Step 1 (imports).
