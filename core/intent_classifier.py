"""
intent_classifier.py - uses a small local LLM to figure out
which entities are part of the user's task vs their identity

basically we ask qwen to look at the prompt and tell us
"is Paris a travel destination or the user's home address?"

falls back gracefully if ollama isnt running
"""

import json
import httpx


# ollama runs on this by default
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b-instruct"
TIMEOUT = 15  # seconds, first call can be slow if model needs loading


class IntentClassifier:

    def __init__(self):
        self.available = False
        self._check_ollama()

    def _check_ollama(self):
        """see if ollama is actually running"""
        try:
            r = httpx.get("http://localhost:11434/api/tags", timeout=2)
            if r.status_code == 200:
                models = r.json().get("models", [])
                # check if our model is pulled
                model_names = [m["name"] for m in models]
                if MODEL_NAME in model_names:
                    self.available = True
                    print(f"[intent] ollama ready with {MODEL_NAME}")
                else:
                    print(f"[intent] ollama running but {MODEL_NAME} not found")
                    print(f"[intent] available models: {model_names}")
            else:
                print("[intent] ollama returned weird status:", r.status_code)
        except Exception as e:
            print(f"[intent] ollama not available: {e}")
            self.available = False

    def classify(self, prompt, entity_texts):
        """
        ask the local LLM to classify entities as task or identity
        
        returns something like:
        {"task": ["Paris", "Amsterdam"], "identity": ["Neha", "neha@gmail.com"]}
        
        if anything goes wrong just returns None (caller should fallback)
        """
        if not self.available:
            return None

        if not entity_texts:
            return {"task": [], "identity": []}

        # build the prompt for qwen
        entities_str = ", ".join(entity_texts)

        llm_prompt = f"""You are a privacy intent classifier. Given a user message and a list of detected entities, classify each entity as either:
- "task": the entity is part of what the user wants to DO (travel destination, product to compare, topic to learn about)
- "identity": the entity reveals WHO the user IS (their name, address, employer, ID number, email)

User message: "{prompt}"

Detected entities: [{entities_str}]

Return ONLY valid JSON in this exact format, nothing else:
{{"task": ["entity1", "entity2"], "identity": ["entity3", "entity4"]}}"""

        try:
            # call ollama
            resp = httpx.post(OLLAMA_URL, json={
                "model": MODEL_NAME,
                "prompt": llm_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # we want deterministic-ish answers
                    "num_predict": 256,   # dont need a long response
                }
            }, timeout=TIMEOUT)

            if resp.status_code != 200:
                print(f"[intent] ollama error: {resp.status_code}")
                return None

            raw_response = resp.json().get("response", "")
            # print(f"[intent] raw: {raw_response}")  # uncomment for debugging

            # try to parse the json from the response
            # sometimes the model wraps it in markdown code blocks
            result = self._parse_json_response(raw_response)
            return result

        except httpx.TimeoutException:
            print("[intent] ollama timed out, skipping")
            return None
        except Exception as e:
            print(f"[intent] error calling ollama: {e}")
            return None

    def _parse_json_response(self, text):
        """
        try to extract json from the LLM response
        models sometimes wrap it in ```json ... ``` or add extra text
        """
        # first try direct parse
        text = text.strip()
        try:
            parsed = json.loads(text)
            if "task" in parsed and "identity" in parsed:
                return parsed
        except json.JSONDecodeError:
            pass

        # try to find json block in markdown
        if "```" in text:
            # grab stuff between the backticks
            parts = text.split("```")
            for part in parts:
                clean = part.strip()
                # remove the "json" language tag if present
                if clean.startswith("json"):
                    clean = clean[4:].strip()
                try:
                    parsed = json.loads(clean)
                    if "task" in parsed and "identity" in parsed:
                        return parsed
                except json.JSONDecodeError:
                    continue

        # last resort: try to find { ... } in the text
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                parsed = json.loads(text[start:end + 1])
                if "task" in parsed and "identity" in parsed:
                    return parsed
            except json.JSONDecodeError:
                pass

        print(f"[intent] couldnt parse LLM response: {text[:100]}")
        return None


# quick test
if __name__ == "__main__":
    clf = IntentClassifier()
    if clf.available:
        print("\n--- test 1: travel ---")
        result = clf.classify(
            "Plan a trip to Paris and Amsterdam. My passport is K8472910.",
            ["Paris", "Amsterdam", "K8472910"]
        )
        print(f"result: {result}")

        print("\n--- test 2: identity ---")
        result = clf.classify(
            "I live in Mumbai and work at Infosys. My email is raj@infosys.com",
            ["Mumbai", "Infosys", "raj@infosys.com"]
        )
        print(f"result: {result}")

        print("\n--- test 3: comparison ---")
        result = clf.classify(
            "Compare Google Cloud vs AWS pricing for our startup",
            ["Google Cloud", "AWS"]
        )
        print(f"result: {result}")
    else:
        print("ollama not running, cant test")
