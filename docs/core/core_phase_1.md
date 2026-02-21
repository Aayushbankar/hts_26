#  Phase 1 Checklist: Core Logic (AliasManager)

> **Goal:** Create a robust "Brain" that finds or generates fake names for real entities. It must remember mappings for the whole session.

---

##  Step 1: Initialize the Class
**File:** `core/alias_manager.py`

- [ ] **Import Requirements:**
  - Import `Faker` from `faker` library.
  - Create a module-level `fake = Faker()` instance.
- [ ] **Define Class:** `class AliasManager:`
- [ ] **Constructor `__init__`:**
  - Initialize `self.real_to_fake = {}` (empty dict)
  - Initialize `self.fake_to_real = {}` (empty dict)

> **Why?** We need two dictionaries so we can look up fakes quickly AND restore real names quickly.

---

## 🎭 Step 2: The Fake Generator
**Method:** `_generate_fake(self, label: str) -> str`

- [ ] **Create a Mapping Dictionary:** inside the method, map entity labels to Faker functions:
  - `"person"` → `fake.name()`
  - `"organization"` → `fake.company()`
  - `"location"` → `fake.city()`
  - `"date"` → `fake.date_this_year().isoformat()`
  - `"email address"` → `fake.email()`
  - `"phone number"` → `fake.phone_number()`
  - `"project name"` → return `f"Project {fake.word().capitalize()}"`
  - `"product name"` → return `f"{fake.word().capitalize()}-{fake.random_int(100, 999)}"`
  - `"money amount"` → return `f"${fake.random_int(1000, 999999):,}"`
  - Default fallback → `fake.word().capitalize()`
- [ ] **Return:** The result of the appropriate Faker function.

> **Why?** We want "Apple" to become "Orion Corp", not "James Mitchell". Context matters for the illusion.

---

## 🔗 Step 3: Get or Create Alias
**Method:** `get_or_create(self, entity_text: str, entity_label: str) -> str`

- [ ] **Check Existence:** If `entity_text` is already in `self.real_to_fake`, return the stored alias immediately.
- [ ] **Generate New:** If not, call `self._generate_fake(entity_label)`.
- [ ] **Collision Check (Crucial):**
  - While the generated fake is *already* a key in `self.fake_to_real` (meaning another entity uses it), generate a NEW one.
  - *This prevents two different people getting the same fake name.*
- [ ] **Store Mapping:**
  - `self.real_to_fake[entity_text] = fake_value`
  - `self.fake_to_real[fake_value] = entity_text`
- [ ] **Return:** The fake value.

---

## 🧹 Step 4: Sanitize (The Replacement Logic)
**Method:** `sanitize(self, text: str, entities: list) -> str`

- [ ] **Sort Entities:** Sort the `entities` list by length of `text` (descending/longest first).
  - *Code hint:* `sorted(entities, key=lambda x: len(x['text']), reverse=True)`
- [ ] **Loop & Replace:**
  - Iterate through sorted entities.
  - Get alias using `get_or_create`.
  - Replace in text: `text = text.replace(entity['text'], alias)`
- [ ] **Return:** The modified text.

> **Why Sort?** If you have "Apple" and "Apple Inc", you MUST replace "Apple Inc" first. Otherwise "Apple" gets replaced inside "Apple Inc" causing "Orion Corp Inc" (broken).

---

##  Step 5: Desanitize (Restore Real Names)
**Method:** `desanitize(self, text: str) -> str`

- [ ] **Sort Fakes:** Get all items from `self.fake_to_real`. Sort by length of the *fake name* (descending).
- [ ] **Loop & Replace:**
  - Iterate through sorted items.
  - Replace fake name with real name in text.
- [ ] **Return:** The restored text.

---

## 🧪 Step 6: Utility Methods
- [ ] **`get_mapping(self)`:** Return `self.real_to_fake` (for debug panel).
- [ ] **`clear(self)`:** Reset both dicts to `{}` (for reset button).

---

###  Ready to Code?
Open `core/alias_manager.py` and start with Step 1.
