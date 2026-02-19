"""
Sanitizer: The orchestrator of the 3-layer anonymization pipeline.

Pipeline:
  Layer 1: PatternScanner (regex) → structured PII
  Layer 2: GLiNER NER (model)    → semantic PII + domain entities
  Layer 3: EntityClassifier      → dedup, tier assignment, privacy score
  Output:  AliasManager          → offset-based replacement + alias map
"""

from gliner import GLiNER

# Dual-mode imports: works as package (from core.sanitiser) AND standalone
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

        # Expanded labels: identity + structural + domain-critical
        self.labels = [
            # Tier 1: REPLACE (identity)
            "person", "organization", "location",
            "email address", "phone number",
            "project name", "product name",
            "government id",
            # Tier 2: PERTURB (structural)
            "date", "money amount",
            # Tier 3: PRESERVE (domain-critical)
            "medical condition", "drug name",
            "symptom", "medical procedure",
            "legal concept", "financial instrument",
            "regulatory term", "job title",
        ]

    def sanitize_prompt(self, user_prompt: str) -> tuple:
        """
        Run the full 3-layer anonymization pipeline.
        
        Returns:
            (sanitized_text, classified_entities, alias_map, privacy_score)
        """
        # Layer 1: Regex scan for structured PII
        regex_entities = self.pattern_scanner.scan(user_prompt)

        # Layer 2: GLiNER NER for semantic entities
        ner_entities = self.model.predict_entities(
            user_prompt,
            self.labels,
            threshold=0.6,  # Tuned to reduce false positives
        )
        # Add start/end offsets to NER entities (GLiNER already provides them)
        for e in ner_entities:
            e.setdefault("source", "ner")

        # Layer 3: Classify — merge, dedup, assign tiers
        classified = self.entity_classifier.classify(regex_entities, ner_entities)

        # Privacy scorecard
        privacy_score = self.entity_classifier.compute_privacy_score(classified)

        # Offset-based replacement (right-to-left)
        sanitized_text = self.alias_manager.sanitize_by_offsets(user_prompt, classified)

        return sanitized_text, classified, self.alias_manager.get_mapping(), privacy_score

    def desanitize_response(self, llm_response: str) -> str:
        """Reverse all aliases in the LLM response back to original values."""
        return self.alias_manager.desanitize(llm_response)

    def get_alias_map(self) -> dict:
        """Get the current real→fake mapping."""
        return self.alias_manager.get_mapping()

    def clear(self):
        """Reset all mappings for a new session."""
        self.alias_manager.clear()