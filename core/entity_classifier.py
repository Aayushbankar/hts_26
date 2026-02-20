"""
Entity Classifier - the brains of the pipeline.
Merges regex + NER results, deduplicates overlapping spans,
assigns tiers (REPLACE/PERTURB/PRESERVE), and scores privacy.
"""

import re


class EntityClassifier:

    # what tier each entity type gets
    TIER_MAP = {
        # replace with fake data
        "person": "REPLACE",
        "organization": "REPLACE",
        "location": "REPLACE",
        "email address": "REPLACE",
        "phone number": "REPLACE",
        "project name": "REPLACE",
        "product name": "REPLACE",
        "government id": "REPLACE",
        "email": "REPLACE",
        "phone": "REPLACE",
        "phone_in": "REPLACE",
        "ssn": "REPLACE",
        "credit_card": "REPLACE",
        "url": "REPLACE",
        "ip_address": "REPLACE",
        "aadhaar": "REPLACE",
        "pan_card": "REPLACE",

        # add small noise (dates shift a few days, money +-15%)
        "date": "PERTURB",
        "money amount": "PERTURB",
        "age": "PERTURB",
        "percentage": "PERTURB",

        # don't touch these - they're needed for the LLM to give useful answers
        "medical condition": "PRESERVE",
        "drug name": "PRESERVE",
        "symptom": "PRESERVE",
        "medical procedure": "PRESERVE",
        "legal concept": "PRESERVE",
        "financial instrument": "PRESERVE",
        "regulatory term": "PRESERVE",
        "job title": "PRESERVE",
    }

    # how risky each entity type is (for scoring)
    RISK_WEIGHTS = {
        "person": 10, "organization": 6, "location": 5,
        "email address": 9, "email": 9,
        "phone number": 8, "phone": 8, "phone_in": 9,
        "ssn": 10, "government id": 10, "credit_card": 10,
        "aadhaar": 10, "pan_card": 9,
        "url": 4, "ip_address": 5,
        "project name": 3, "product name": 3,
        "date": 4, "money amount": 5,
        "age": 6, "percentage": 2,
        # preserved entities have 0 risk (they're not PII in context)
        "medical condition": 0, "drug name": 0,
        "symptom": 0, "medical procedure": 0,
        "legal concept": 0, "financial instrument": 0,
        "regulatory term": 0, "job title": 0,
    }

    # things GLiNER sometimes misidentifies
    FALSE_POSITIVES = {
        "government id": {"ssn", "dob", "ein", "tin", "id", "itin", "vin"},
    }

    def classify(self, regex_entities: list[dict], ner_entities: list[dict]) -> list[dict]:
        """
        Merge regex + NER entities, deduplicate overlapping spans, assign tiers.
        When two overlap, keep the longer one. Same length = prefer regex.
        """
        all_entities = []

        for e in regex_entities:
            e.setdefault("source", "regex")
            e["text"] = e["text"].rstrip(".")
            all_entities.append(e)

        for e in ner_entities:
            e.setdefault("source", "ner")
            e["text"] = e["text"].rstrip(". ")
            all_entities.append(e)

        # filter false positives
        filtered = []
        for e in all_entities:
            label = e["label"].lower()
            text_lower = e["text"].lower().strip()
            fp_set = self.FALSE_POSITIVES.get(label, set())
            if text_lower in fp_set:
                continue
            filtered.append(e)

        # sort by span length desc (longest first wins dedup)
        filtered.sort(key=lambda e: e["end"] - e["start"], reverse=True)

        # greedy dedup - if >50% overlap with something we already kept, skip it
        kept = []
        occupied = set()

        for entity in filtered:
            span = set(range(entity["start"], entity["end"]))
            overlap = span & occupied
            if len(overlap) > len(span) * 0.5:
                continue
            label = entity["label"].lower()
            entity["tier"] = self.TIER_MAP.get(label, "REPLACE")
            kept.append(entity)
            occupied |= span

        return kept

    # --- intent detection ---
    # we don't want to replace "Paris" in "plan a trip to Paris"
    # but we DO want to replace "Mumbai" in "Flying out of Mumbai"

    # if prompt matches any of these, locations/orgs might be task-relevant
    TOPIC_PATTERNS = [
        re.compile(r'\b(?:trip|travel|fly|visit|tour|explore|itinerary|vacation|holiday)\b', re.I),
        re.compile(r'\b(?:flights?|hotels?|restaurants?|things to do|sightsee|backpack)\b', re.I),
        re.compile(r'\b(?:plan|book|reserve)\b.*\b(?:trip|travel|tour|vacation|flight)\b', re.I),
        re.compile(r'\b(?:integrate|install|setup|configure|deploy|migrate|switch)\b.*\b(?:to|from|with)\b', re.I),
        re.compile(r'\b(?:use|try|compare|review|rate|benchmark)\b', re.I),
        re.compile(r'\b(?:what is|explain|tell me about|how does|difference between)\b', re.I),
        re.compile(r'\b(?:weather|temperature|population|timezone|cost of living)\b.*\b(?:in|of|at)\b', re.I),
        re.compile(r'\b(?:rent|buy|property|apartment|house|flat)\b.*\b(?:in|at|near)\b', re.I),
    ]

    # if entity appears right after these, it IS identity info (don't override)
    IDENTITY_ANCHORS = [
        re.compile(r'\b(?:i live|i stay|my home|my address|based in|located in|residing in)\b', re.I),
        re.compile(r'\b(?:i work|my company|my employer|my office|our office|we are at)\b', re.I),
        re.compile(r'\b(?:born in|grew up in|from|native of)\b', re.I),
        re.compile(r'\b(?:flying out of|departing from|leaving from)\b', re.I),
    ]

    def _is_task_relevant(self, entity_text, entity_label, full_prompt):
        """
        Check if an entity is part of the user's task (preserve it)
        or their identity (replace it).
        
        Two steps:
          1. Is this a topic-related prompt? (travel, comparison, etc.)
          2. Is this entity anchored to identity? ("I live in X")
        """
        if entity_label not in ("location", "organization", "product name"):
            return False

        prompt_lower = full_prompt.lower()
        entity_lower = entity_text.lower()

        # step 1: is this a topic prompt at all?
        is_topic = any(p.search(prompt_lower) for p in self.TOPIC_PATTERNS)
        if not is_topic:
            return False

        # step 2: is this entity right after an identity phrase?
        entity_pos = prompt_lower.find(entity_lower)
        if entity_pos == -1:
            return False

        # look at the 40 chars before the entity for identity anchors
        before = prompt_lower[max(0, entity_pos - 40):entity_pos]
        for anchor in self.IDENTITY_ANCHORS:
            if anchor.search(before):
                return False  # this IS identity, don't override

        return True  # topic prompt + no identity anchor = task-relevant

    def apply_intent_overrides(self, entities, full_prompt):
        """Override tier to PRESERVE for entities that are part of the task."""
        for entity in entities:
            if entity.get("tier") == "REPLACE":
                if self._is_task_relevant(entity["text"], entity["label"], full_prompt):
                    entity["tier"] = "PRESERVE"
                    entity["intent_override"] = True
        return entities

    def compute_privacy_score(self, classified_entities: list[dict]) -> dict:
        """
        Privacy scorecard for a prompt.
        Score 0-100 based on how much risk is mitigated.
        """
        if not classified_entities:
            return {
                "score": 100, "risk_level": "NONE",
                "total_entities": 0, "replaced": 0,
                "perturbed": 0, "preserved": 0,
                "hipaa_identifiers_found": 0,
                "hipaa_identifiers_protected": 0,
            }

        replaced = sum(1 for e in classified_entities if e.get("tier") == "REPLACE")
        perturbed = sum(1 for e in classified_entities if e.get("tier") == "PERTURB")
        preserved = sum(1 for e in classified_entities if e.get("tier") == "PRESERVE")

        # HIPAA safe harbor identifiers
        hipaa_labels = {
            "person", "location", "date", "phone number", "phone", "phone_in",
            "email address", "email", "ssn", "government id",
            "credit_card", "url", "ip_address", "aadhaar", "pan_card",
        }

        hipaa_found = sum(1 for e in classified_entities if e["label"].lower() in hipaa_labels)
        hipaa_protected = sum(
            1 for e in classified_entities
            if e["label"].lower() in hipaa_labels and e.get("tier") in ("REPLACE", "PERTURB")
        )

        # score = % of total risk that we've mitigated
        total_risk = sum(self.RISK_WEIGHTS.get(e["label"].lower(), 5) for e in classified_entities)
        protected_risk = sum(
            self.RISK_WEIGHTS.get(e["label"].lower(), 5)
            for e in classified_entities
            if e.get("tier") in ("REPLACE", "PERTURB")
        )
        score = round((protected_risk / max(total_risk, 1)) * 100)

        if score >= 90: risk_level = "LOW"
        elif score >= 70: risk_level = "MEDIUM"
        elif score >= 50: risk_level = "HIGH"
        else: risk_level = "CRITICAL"

        return {
            "score": score, "risk_level": risk_level,
            "total_entities": len(classified_entities),
            "replaced": replaced, "perturbed": perturbed, "preserved": preserved,
            "hipaa_identifiers_found": hipaa_found,
            "hipaa_identifiers_protected": hipaa_protected,
        }
