"""
Alias Manager: Tiered alias generation with offset-based replacement.

Tiers:
  REPLACE  — Full Faker-based identity replacement
  PERTURB  — Small noise (dates ±3-7 days, money ±10-15%)
  PRESERVE — Return original unchanged (domain-critical context)

Key features:
  - Offset-based right-to-left replacement (no cascading errors)
  - Collision detection (no two reals → same fake)
  - Session-consistent (same input → same output within a session)
  - Bidirectional mapping for de-sanitization
"""

from faker import Faker
import random
import re
from dateutil import parser as dateutil_parser
from datetime import timedelta


class AliasManager:
    def __init__(self):
        self.real_to_fake = {}
        self.fake_to_real = {}
        self.fake = Faker()

        self._corp_suffixes = [
            "Corp", "Technologies", "Systems", "Industries",
            "Group", "Solutions", "Labs", "Dynamics",
            "Holdings", "Partners", "Ventures", "Inc",
        ]
        # Blocklist: Faker sometimes generates inappropriate last names for companies
        self._name_blocklist = {
            "gay", "sex", "rape", "drug", "crime", "kill", "die", "dead",
            "hell", "damn", "ass", "butt", "crap", "stupid", "idiot",
            "negro", "slave", "nazi", "porn", "nude", "anal", "nigga" , "rape", "masturbation" ,
        }
        self._codenames = [
            "Aurora", "Falcon", "Horizon", "Nebula", "Compass",
            "Keystone", "Onyx", "Helix", "Mantis", "Eclipse",
            "Zenith", "Valkyrie", "Orion", "Tempest", "Cascade",
        ]
        self._product_suffixes = ["Pro", "Ultra", "Max", "X1", "One", "Suite"]
        self._email_domains = ["email.com", "mail.com", "inbox.org", "proton.me"]

    # ────────────────────────────────────────────
    #  PUBLIC API
    # ────────────────────────────────────────────

    def get_or_create(self, entity_text: str, label: str, tier: str = "REPLACE") -> str:
        """
        Get existing alias or create a new one.
        Routes to correct handler based on tier.
        Includes collision detection.
        """
        # Already mapped?
        if entity_text in self.real_to_fake:
            return self.real_to_fake[entity_text]

        # PRESERVE tier: return original unchanged
        if tier == "PRESERVE":
            return entity_text

        # Generate alias based on tier
        if tier == "PERTURB":
            alias = self._perturb(label, entity_text)
        else:  # REPLACE
            alias = self._generate_replacement(label, entity_text)

        # Collision detection: ensure no two reals map to the same fake
        attempts = 0
        while alias in self.fake_to_real and self.fake_to_real[alias] != entity_text:
            alias = self._generate_replacement(label, entity_text) if tier == "REPLACE" else self._perturb(label, entity_text)
            attempts += 1
            if attempts > 10:
                # Fallback: append a suffix to make unique
                alias = f"{alias} ({attempts})"
                break

        # Store bidirectional mapping
        self.real_to_fake[entity_text] = alias
        self.fake_to_real[alias] = entity_text
        return alias

    def sanitize_by_offsets(self, text: str, classified_entities: list[dict]) -> str:
        """
        Replace entities in text using character offsets (right-to-left).
        This avoids cascading offset errors that happen with str.replace().
        """
        # Filter out PRESERVE tier (don't touch them)
        to_replace = [e for e in classified_entities if e.get("tier") != "PRESERVE"]

        # Sort by start position DESCENDING (right-to-left)
        to_replace.sort(key=lambda e: e["start"], reverse=True)

        for entity in to_replace:
            alias = self.get_or_create(
                entity["text"],
                entity["label"],
                entity.get("tier", "REPLACE"),
            )
            start = entity["start"]
            end = entity["end"]
            text = text[:start] + alias + text[end:]

        return text

    def desanitize(self, text: str) -> str:
        """Reverse all aliases back to original values."""
        # Sort by fake length descending to avoid substring issues
        for fake, real in sorted(
            self.fake_to_real.items(),
            key=lambda x: len(x[0]),
            reverse=True,
        ):
            text = text.replace(fake, real)
        return text

    def get_mapping(self) -> dict:
        return dict(self.real_to_fake)

    def clear(self):
        self.real_to_fake = {}
        self.fake_to_real = {}

    # ────────────────────────────────────────────
    #  TIER 1: REPLACE (full identity replacement)
    # ────────────────────────────────────────────

    # Locale-aware name pools for cultural consistency
    _SOUTH_ASIAN_LAST = ["Sharma", "Patel", "Kumar", "Singh", "Gupta", "Mehta", "Joshi", "Nair", "Reddy", "Iyer"]
    _SOUTH_ASIAN_FIRST = ["Arjun", "Priya", "Vikram", "Ananya", "Rohan", "Kavitha", "Sanjay", "Deepa", "Amit", "Neha"]
    _EAST_ASIAN_LAST = ["Chen", "Wang", "Li", "Zhang", "Liu", "Yang", "Huang", "Wu", "Lin", "Sun"]
    _EAST_ASIAN_FIRST = ["Wei", "Ming", "Jing", "Hui", "Lei", "Xin", "Yan", "Fang", "Jun", "Ting"]
    _KOREAN_LAST = ["Kim", "Park", "Lee", "Choi", "Jung", "Kang", "Yoon", "Shin", "Han", "Seo"]
    _KOREAN_FIRST = ["Joon", "Soo", "Hyun", "Min", "Ji", "Yeon", "Woo", "Eun", "Dong", "Hee"]

    def _detect_cultural_origin(self, name: str) -> str:
        """Detect the likely cultural origin of a name for locale-aware replacement."""
        # Strip titles
        clean = re.sub(r'^(Dr\.?|Mr\.?|Mrs\.?|Ms\.?|Prof\.?|General|Colonel|Judge|VP|CEO|CFO|CTO)\s+', '', name, flags=re.IGNORECASE).strip()
        parts = clean.split()
        
        for part in parts:
            p = part.strip(",.")
            if p in ("Sharma", "Patel", "Kumar", "Singh", "Gupta", "Mehta", "Joshi", "Nair",
                      "Reddy", "Iyer", "Priya", "Rajesh", "Arjun", "Vikram", "Ananya",
                      "Deepa", "Kavitha", "Sanjay", "Amit", "Neha", "Rohan"):
                return "south_asian"
            if p in ("Chen", "Wang", "Li", "Zhang", "Liu", "Yang", "Huang", "Wu", "Lin",
                      "Sun", "Wei", "Ming", "Jing", "Hui", "Lei", "Xin", "Fang"):
                return "east_asian"
            if p in ("Kim", "Park", "Lee", "Choi", "Jung", "Kang", "Yoon", "Shin",
                      "Han", "Seo", "Joon", "Hyun", "Yeon", "Eun"):
                return "korean"
        return "default"

    def _generate_person_name(self, original: str) -> str:
        """Generate a culturally-appropriate fake name."""
        origin = self._detect_cultural_origin(original)
        
        if origin == "south_asian":
            return f"{random.choice(self._SOUTH_ASIAN_FIRST)} {random.choice(self._SOUTH_ASIAN_LAST)}"
        elif origin == "east_asian":
            return f"{random.choice(self._EAST_ASIAN_FIRST)} {random.choice(self._EAST_ASIAN_LAST)}"
        elif origin == "korean":
            return f"{random.choice(self._KOREAN_FIRST)} {random.choice(self._KOREAN_LAST)}"
        else:
            return f"{self.fake.first_name()} {self.fake.last_name()}"


    def _generate_replacement(self, label: str, original: str = "") -> str:
        """Generate a realistic fake value for identity entities."""
        label = label.lower()

        if label == "person":
            return self._generate_person_name(original)

        elif label == "organization":
            name = self.fake.last_name()
            # Regenerate if inappropriate
            while name.lower() in self._name_blocklist:
                name = self.fake.last_name()
            return f"{name} {random.choice(self._corp_suffixes)}"

        elif label == "location":
            city = self.fake.city()
            while len(city.split()) > 2:
                city = self.fake.city()
            return city

        elif label in ("email address", "email"):
            first = self.fake.first_name().lower()
            last = self.fake.last_name().lower()
            return f"{first}.{last}@{random.choice(self._email_domains)}"

        elif label in ("phone number", "phone"):
            return f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

        elif label in ("ssn", "government id"):
            return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"

        elif label == "credit_card":
            return f"XXXX-XXXX-XXXX-{random.randint(1000, 9999)}"

        elif label == "url":
            slug = self.fake.last_name().lower()
            return f"https://example-{slug}.com/page"

        elif label == "ip_address":
            return f"{random.randint(10, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

        elif label == "project name":
            return f"Project {random.choice(self._codenames)}"

        elif label == "product name":
            return f"{self.fake.last_name()} {random.choice(self._product_suffixes)}"

        else:
            return self.fake.word().capitalize()

    # ────────────────────────────────────────────
    #  TIER 2: PERTURB (small controlled noise)
    # ────────────────────────────────────────────

    def _perturb(self, label: str, original: str) -> str:
        """Apply small, context-preserving perturbation."""
        label = label.lower()

        if label == "date":
            return self._perturb_date(original)
        elif label == "money amount":
            return self._perturb_money(original)
        elif label == "age":
            return self._perturb_age(original)
        elif label == "percentage":
            return self._perturb_percentage(original)
        else:
            return original  # Unknown perturb type: preserve

    def _perturb_date(self, original: str) -> str:
        """
        Parse date → shift ±3-7 days → reformat in the same style.
        Handles: "January 15, 2026", "March 2025", "01/15/2026"
        """
        text = original.strip()

        # Compound dates like "March and July 2025" — too abstract, preserve
        if " and " in text.lower():
            return original

        # Quarter notation "Q2 2025" — preserve
        if re.match(r'Q\d\s+\d{4}', text, re.IGNORECASE):
            return original

        # Fiscal year notation "FY2026", "FY 2026" — preserve
        if re.match(r'^FY\s?\d{4}$', text, re.IGNORECASE):
            return original

        # Year-only "2025" — preserve
        if re.match(r'^\d{4}$', text):
            return original

        # Month + Year only "April 2025" — preserve (no specific day to shift)
        if re.match(r'^[A-Z][a-z]+ \d{4}$', text):
            return original

        try:
            parsed = dateutil_parser.parse(text, fuzzy=True)
        except (ValueError, OverflowError):
            return original  # Can't parse → preserve

        # Shift by ±3-7 days, but guard against year/month boundary crossing
        shift = random.choice([-1, 1]) * random.randint(3, 7)
        shifted = parsed + timedelta(days=shift)
        # Year boundary guard: if shift crosses year, flip direction
        if shifted.year != parsed.year:
            shift = abs(shift) if parsed.month <= 6 else -abs(shift)
            shifted = parsed + timedelta(days=shift)

        # Try to match original format
        if re.match(r'^[A-Z][a-z]+ \d{1,2}, \d{4}$', text):
            # "January 15, 2026"
            return shifted.strftime("%B %-d, %Y")
        elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', text):
            # "01/15/2026"
            return shifted.strftime("%-m/%-d/%Y")
        elif re.match(r'^\d{4}-\d{2}-\d{2}$', text):
            # "2026-01-15" (ISO)
            return shifted.strftime("%Y-%m-%d")
        elif re.match(r'^\d{1,2}-\d{1,2}-\d{4}$', text):
            # "15-01-2026"
            return shifted.strftime("%-d-%-m-%Y")
        else:
            # Default: "Month Day, Year"
            return shifted.strftime("%B %-d, %Y")

    def _perturb_money(self, original: str) -> str:
        """
        Parse money amount → multiply ×0.85-1.15 → reformat with same scale word.
        Handles: "$3.5 billion", "$44 million", "$2,300"
        """
        text = original.lower().strip()

        # Determine scale word
        scale_word = ""
        scale_map = {
            "trillion": 1, "billion": 1, "million": 1, "thousand": 1,
        }
        for word in scale_map:
            if word in text:
                scale_word = word
                break

        # Extract the number
        num_match = re.search(r'[\d,.]+', text)
        if not num_match:
            return original  # Can't parse

        try:
            num = float(num_match.group().replace(",", ""))
        except ValueError:
            return original

        # Perturb: multiply by 0.85-1.15
        factor = random.uniform(0.85, 1.15)
        perturbed = num * factor

        # Determine currency symbol (multi-currency support)
        currency = ""
        for sym in ["$", "€", "£", "¥", "₹"]:
            if sym in original:
                currency = sym
                break

        # Format based on original style
        if scale_word:
            # "$3.5 billion" → "$3.9 billion"
            if perturbed == int(perturbed):
                return f"{currency}{int(perturbed)} {scale_word}"
            else:
                return f"{currency}{perturbed:.1f} {scale_word}"
        else:
            # "$2,300" → "$2,484"
            return f"{currency}{int(perturbed):,}"

    def _perturb_age(self, original: str) -> str:
        """Parse age → shift ±2-3 years."""
        num_match = re.search(r'\d+', original)
        if not num_match:
            return original
        age = int(num_match.group())
        shift = random.choice([-1, 1]) * random.randint(2, 3)
        new_age = max(1, age + shift)
        return original.replace(num_match.group(), str(new_age))

    def _perturb_percentage(self, original: str) -> str:
        """Parse percentage → multiply ×0.85-1.15."""
        num_match = re.search(r'[\d.]+', original)
        if not num_match:
            return original
        pct = float(num_match.group())
        factor = random.uniform(0.85, 1.15)
        new_pct = round(pct * factor, 1)
        # Keep integer if original was integer
        if "." not in num_match.group():
            new_pct = int(round(new_pct))
        return original.replace(num_match.group(), str(new_pct))