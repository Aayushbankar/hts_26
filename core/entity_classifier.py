"""
Layer 3: Entity classification, deduplication, and privacy scoring.
Merges regex + NER results, resolves overlaps, assigns treatment tiers,
and computes a per-prompt privacy scorecard.
"""


class EntityClassifier:
    """Classify entities into tiers, deduplicate overlapping spans, compute privacy score."""

    # Tier assignment map — the core intelligence of the system
    TIER_MAP = {
        # ───── TIER 1: REPLACE (identity — full replacement) ─────
        "person": "REPLACE",
        "organization": "REPLACE",
        "location": "REPLACE",
        "email address": "REPLACE",
        "phone number": "REPLACE",
        "project name": "REPLACE",
        "product name": "REPLACE",
        "government id": "REPLACE",
        # Regex-detected labels
        "email": "REPLACE",
        "phone": "REPLACE",
        "ssn": "REPLACE",
        "credit_card": "REPLACE",
        "url": "REPLACE",
        "ip_address": "REPLACE",

        # ───── TIER 2: PERTURB (structural — small noise) ─────
        "date": "PERTURB",
        "money amount": "PERTURB",
        "age": "PERTURB",
        "percentage": "PERTURB",

        # ───── TIER 3: PRESERVE (domain-critical — don't touch) ─────
        "medical condition": "PRESERVE",
        "drug name": "PRESERVE",
        "symptom": "PRESERVE",
        "medical procedure": "PRESERVE",
        "legal concept": "PRESERVE",
        "financial instrument": "PRESERVE",
        "regulatory term": "PRESERVE",
        "job title": "PRESERVE",
    }

    # Risk weights for privacy scoring (higher = more sensitive)
    RISK_WEIGHTS = {
        "person": 10, "organization": 6, "location": 5,
        "email address": 9, "email": 9,
        "phone number": 8, "phone": 8,
        "ssn": 10, "government id": 10, "credit_card": 10,
        "url": 4, "ip_address": 5,
        "project name": 3, "product name": 3,
        "date": 4, "money amount": 5,
        "age": 6, "percentage": 2,
        "medical condition": 0, "drug name": 0,
        "symptom": 0, "medical procedure": 0,
        "legal concept": 0, "financial instrument": 0,
        "regulatory term": 0, "job title": 0,
    }

    # False positive filter: common abbreviations GLiNER misclassifies
    FALSE_POSITIVES = {
        "government id": {"ssn", "dob", "ein", "tin", "id", "itin", "vin"},
    }

    def classify(self, regex_entities: list[dict], ner_entities: list[dict]) -> list[dict]:
        """
        Merge regex + NER entities, deduplicate overlapping spans, assign tiers.
        
        Dedup rules:
          - When two entities overlap, keep the LONGER span
          - When same length, prefer regex (higher precision for structured PII)
        
        Returns list of dicts with added 'tier' key.
        """
        # Combine all entities
        all_entities = []
        for e in regex_entities:
            e.setdefault("source", "regex")
            # Strip trailing periods from regex matches (email ending in ".")
            e["text"] = e["text"].rstrip(".")
            all_entities.append(e)
        for e in ner_entities:
            e.setdefault("source", "ner")
            # Strip trailing periods/whitespace from NER matches
            e["text"] = e["text"].rstrip(". ")
            all_entities.append(e)

        # Filter out false positives
        filtered = []
        for e in all_entities:
            label = e["label"].lower()
            text_lower = e["text"].lower().strip()
            # Skip known false positives (e.g., "SSN" as government_id)
            fp_set = self.FALSE_POSITIVES.get(label, set())
            if text_lower in fp_set:
                continue
            filtered.append(e)

        # Sort by span length descending (longest first wins)
        filtered.sort(key=lambda e: e["end"] - e["start"], reverse=True)

        # Greedy dedup: keep longest, skip if overlaps with already-kept
        kept = []
        occupied = set()  # set of character positions already claimed

        for entity in filtered:
            span = set(range(entity["start"], entity["end"]))
            # Check overlap: if more than 50% of this span is already taken, skip it
            overlap = span & occupied
            if len(overlap) > len(span) * 0.5:
                continue
            # Assign tier
            label = entity["label"].lower()
            entity["tier"] = self.TIER_MAP.get(label, "REPLACE")
            kept.append(entity)
            occupied |= span

        return kept

    def compute_privacy_score(self, classified_entities: list[dict]) -> dict:
        """
        Compute a per-prompt privacy scorecard.
        
        Returns:
            {
                "score": 0-100 (100 = fully protected),
                "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
                "total_entities": N,
                "replaced": N,
                "perturbed": N,
                "preserved": N,
                "hipaa_identifiers_found": N,
                "hipaa_identifiers_protected": N,
            }
        """
        if not classified_entities:
            return {
                "score": 100,
                "risk_level": "NONE",
                "total_entities": 0,
                "replaced": 0,
                "perturbed": 0,
                "preserved": 0,
                "hipaa_identifiers_found": 0,
                "hipaa_identifiers_protected": 0,
            }

        replaced = sum(1 for e in classified_entities if e.get("tier") == "REPLACE")
        perturbed = sum(1 for e in classified_entities if e.get("tier") == "PERTURB")
        preserved = sum(1 for e in classified_entities if e.get("tier") == "PRESERVE")
        total = len(classified_entities)

        # HIPAA Safe Harbor identifiers we can detect
        hipaa_labels = {
            "person", "location", "date", "phone number", "phone",
            "email address", "email", "ssn", "government id",
            "credit_card", "url", "ip_address",
        }
        hipaa_found = sum(
            1 for e in classified_entities
            if e["label"].lower() in hipaa_labels
        )
        hipaa_protected = sum(
            1 for e in classified_entities
            if e["label"].lower() in hipaa_labels and e.get("tier") in ("REPLACE", "PERTURB")
        )

        # Calculate risk: sum of weights for unprotected entities
        total_risk = sum(
            self.RISK_WEIGHTS.get(e["label"].lower(), 5)
            for e in classified_entities
        )
        protected_risk = sum(
            self.RISK_WEIGHTS.get(e["label"].lower(), 5)
            for e in classified_entities
            if e.get("tier") in ("REPLACE", "PERTURB")
        )

        # Score: percentage of risk that is mitigated
        score = round((protected_risk / max(total_risk, 1)) * 100)

        # Risk level
        if score >= 90:
            risk_level = "LOW"
        elif score >= 70:
            risk_level = "MEDIUM"
        elif score >= 50:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        return {
            "score": score,
            "risk_level": risk_level,
            "total_entities": total,
            "replaced": replaced,
            "perturbed": perturbed,
            "preserved": preserved,
            "hipaa_identifiers_found": hipaa_found,
            "hipaa_identifiers_protected": hipaa_protected,
        }
