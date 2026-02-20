"""
Sanitizer - main orchestrator for the anonymization pipeline.

Pipeline:
  1. PatternScanner (regex)  -> structured PII
  2. GLiNER NER (model)      -> semantic entities  
  3. EntityClassifier         -> dedup + tier assignment + scoring
  4. AliasManager             -> offset-based replacement
"""

from gliner import GLiNER

try:
    from .alias_manager import AliasManager
    from .pattern_scanner import PatternScanner
    from .entity_classifier import EntityClassifier
except ImportError:
    from alias_manager import AliasManager
    from pattern_scanner import PatternScanner
    from entity_classifier import EntityClassifier


class Sanitizer:
    def __init__(self):
        self.model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
        self.alias_manager = AliasManager()
        self.pattern_scanner = PatternScanner()
        self.entity_classifier = EntityClassifier()

        # labels we want GLiNER to look for
        self.labels = [
            # identity (will be replaced)
            "person", "organization", "location",
            "email address", "phone number",
            "project name", "product name",
            "government id",
            # structural (will be perturbed slightly)
            "date", "money amount",
            # domain-critical (kept as-is)
            "medical condition", "drug name",
            "symptom", "medical procedure",
            "legal concept", "financial instrument",
            "regulatory term", "job title",
        ]

    def sanitize_prompt(self, user_prompt: str) -> tuple:
        """Run the full pipeline. Returns (sanitized_text, entities, alias_map, score)."""

        # layer 1 - regex
        regex_entities = self.pattern_scanner.scan(user_prompt)
        # print("DEBUG regex found:", [e.get('text') for e in regex_entities]) # too noisy

        # layer 2 - NER
        ner_entities = self.model.predict_entities(
            user_prompt, self.labels, threshold=0.6
        )
        for e in ner_entities:
            e.setdefault("source", "ner")
            
        # print(f"DEBUG ner found: {len(ner_entities)}")

        # layer 3 - classify and deduplicate
        classified = self.entity_classifier.classify(regex_entities, ner_entities)

        # layer 3.5 - intent override (so travel destinations etc. don't get replaced)
        classified = self.entity_classifier.apply_intent_overrides(classified, user_prompt)

        # scoring
        privacy_score = self.entity_classifier.compute_privacy_score(classified)

        # replace entities in the text
        sanitized_text = self.alias_manager.sanitize_by_offsets(user_prompt, classified)

        return sanitized_text, classified, self.alias_manager.get_mapping(), privacy_score

    def desanitize_response(self, llm_response: str) -> str:
        """Reverse aliases in LLM response back to originals."""
        return self.alias_manager.desanitize(llm_response)

    def get_alias_map(self) -> dict:
        return self.alias_manager.get_mapping()

    def clear(self):
        """Reset for new session."""
        self.alias_manager.clear()