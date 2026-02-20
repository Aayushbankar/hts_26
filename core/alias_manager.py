"""
Alias Manager - handles all the fake data generation and replacement.

Tiers:
  REPLACE  - full swap with Faker (names, emails, etc.)
  PERTURB  - small noise (dates +-few days, money +-15%)
  PRESERVE - don't touch (medical terms, job titles, etc.)
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
        self._name_blocklist = {
            "gay", "sex", "rape", "drug", "crime", "kill", "die", "dead",
            "hell", "damn", "ass", "butt", "crap", "stupid", "idiot",
            "negro", "slave", "nazi", "porn", "nude", "anal", "nigga", "masturbation",
        }
        self._codenames = [
            "Aurora", "Falcon", "Horizon", "Nebula", "Compass",
            "Keystone", "Onyx", "Helix", "Mantis", "Eclipse",
            "Zenith", "Valkyrie", "Orion", "Tempest", "Cascade",
        ]
        self._product_suffixes = ["Pro", "Ultra", "Max", "X1", "One", "Suite"]
        self._email_domains = ["email.com", "mail.com", "inbox.org", "proton.me"]

    # --- public API ---

    def get_or_create(self, entity_text, label, tier="REPLACE"):
        """Get existing alias or create new one. Handles collision detection."""
        if entity_text in self.real_to_fake:
            return self.real_to_fake[entity_text]

        if tier == "PRESERVE":
            return entity_text

        if tier == "PERTURB":
            alias = self._perturb(label, entity_text)
        else:
            alias = self._generate_replacement(label, entity_text)

        # collision detection
        attempts = 0
        while alias in self.fake_to_real and self.fake_to_real[alias] != entity_text:
            alias = self._generate_replacement(label, entity_text) if tier == "REPLACE" else self._perturb(label, entity_text)
            attempts += 1
            if attempts > 10:
                alias = f"{alias} ({attempts})"
                break

        # store mapping
        # perturbed values don't go in the reverse map (they're noise, not identity)
        self.real_to_fake[entity_text] = alias
        if tier != "PERTURB":
            self.fake_to_real[alias] = entity_text
        return alias

    def sanitize_by_offsets(self, text, classified_entities):
        """Replace entities right-to-left using char offsets (avoids cascading errors)."""
        to_replace = [e for e in classified_entities if e.get("tier") != "PRESERVE"]
        to_replace.sort(key=lambda e: e["start"], reverse=True)

        for entity in to_replace:
            alias = self.get_or_create(
                entity["text"], entity["label"], entity.get("tier", "REPLACE")
            )
            text = text[:entity["start"]] + alias + text[entity["end"]:]

        return text

    def desanitize(self, text):
        """Reverse all aliases back to originals."""
        for fake, real in sorted(
            self.fake_to_real.items(), key=lambda x: len(x[0]), reverse=True
        ):
            text = text.replace(fake, real)
        return text

    def get_mapping(self):
        return dict(self.real_to_fake)

    def clear(self):
        self.real_to_fake = {}
        self.fake_to_real = {}

    # --- name generation (culturally aware) ---

    _SOUTH_ASIAN_LAST = ["Sharma", "Patel", "Kumar", "Singh", "Gupta", "Mehta", "Joshi", "Nair", "Reddy", "Iyer"]
    _SOUTH_ASIAN_FIRST = ["Arjun", "Priya", "Vikram", "Ananya", "Rohan", "Kavitha", "Sanjay", "Deepa", "Amit", "Neha"]
    _EAST_ASIAN_LAST = ["Chen", "Wang", "Li", "Zhang", "Liu", "Yang", "Huang", "Wu", "Lin", "Sun"]
    _EAST_ASIAN_FIRST = ["Wei", "Ming", "Jing", "Hui", "Lei", "Xin", "Yan", "Fang", "Jun", "Ting"]
    _KOREAN_LAST = ["Kim", "Park", "Lee", "Choi", "Jung", "Kang", "Yoon", "Shin", "Han", "Seo"]
    _KOREAN_FIRST = ["Joon", "Soo", "Hyun", "Min", "Ji", "Yeon", "Woo", "Eun", "Dong", "Hee"]
    _ARABIC_LAST = ["Al-Rashid", "Hassan", "Ibrahim", "Khalil", "Mansour", "Nasser", "Saleh", "Farouk"]
    _ARABIC_FIRST = ["Omar", "Fatima", "Ahmed", "Layla", "Tariq", "Nour", "Youssef", "Amira"]
    _HISPANIC_LAST = ["Rodriguez", "Garcia", "Martinez", "Lopez", "Hernandez", "Torres", "Ramirez", "Flores"]
    _HISPANIC_FIRST = ["Carlos", "Maria", "Diego", "Isabella", "Alejandro", "Valentina", "Mateo", "Sofia"]
    _JAPANESE_LAST = ["Tanaka", "Suzuki", "Watanabe", "Sato", "Yamamoto", "Nakamura", "Kobayashi", "Kato"]
    _JAPANESE_FIRST = ["Yuki", "Haruto", "Sakura", "Ren", "Hina", "Sota", "Mei", "Takumi"]

    def _detect_cultural_origin(self, name):
        """Try to figure out where a name is from so we can generate something similar."""
        clean = re.sub(r'^(Dr\.?|Mr\.?|Mrs\.?|Ms\.?|Prof\.?|General|Colonel|Judge|VP|CEO|CFO|CTO|Adv\.?)\s+', '', name, flags=re.IGNORECASE).strip()
        parts = clean.split()

        for part in parts:
            p = part.strip(",.")
            if p in ("Sharma", "Patel", "Kumar", "Singh", "Gupta", "Mehta", "Joshi", "Nair",
                      "Reddy", "Iyer", "Priya", "Rajesh", "Arjun", "Vikram", "Ananya",
                      "Deepa", "Kavitha", "Sanjay", "Amit", "Neha", "Rohan",
                      "Kapoor", "Agarwal", "Bansal", "Saxena", "Mishra", "Rao",
                      "Suresh", "Sunita", "Kamala", "Mohan", "Lakshmi", "Dinesh",
                      "Manish", "Pooja", "Ishita", "Karthik", "Meera", "Arun"):
                return "south_asian"
            if p in ("Chen", "Wang", "Li", "Zhang", "Liu", "Yang", "Huang", "Wu", "Lin",
                      "Sun", "Wei", "Ming", "Jing", "Hui", "Lei", "Xin", "Fang"):
                return "east_asian"
            if p in ("Kim", "Park", "Lee", "Choi", "Jung", "Kang", "Yoon", "Shin",
                      "Han", "Seo", "Joon", "Hyun", "Yeon", "Eun"):
                return "korean"
            if p in ("Al-Rashid", "Hassan", "Ibrahim", "Khalil", "Mansour",
                      "Omar", "Fatima", "Ahmed", "Layla", "Tariq", "Mohammed",
                      "Abdullah", "Nasser", "Saleh", "Farouk"):
                return "arabic"
            if p in ("Rodriguez", "Garcia", "Martinez", "Lopez", "Hernandez",
                      "Torres", "Ramirez", "Carlos", "Diego", "Isabella", "Alejandro"):
                return "hispanic"
            if p in ("Tanaka", "Suzuki", "Watanabe", "Sato", "Yamamoto",
                      "Nakamura", "Yuki", "Haruto", "Sakura"):
                return "japanese"
        return "default"

    def _generate_person_name(self, original):
        """Generate a culturally-appropriate fake name."""
        origin = self._detect_cultural_origin(original)

        pools = {
            "south_asian": (self._SOUTH_ASIAN_FIRST, self._SOUTH_ASIAN_LAST),
            "east_asian": (self._EAST_ASIAN_FIRST, self._EAST_ASIAN_LAST),
            "korean": (self._KOREAN_FIRST, self._KOREAN_LAST),
            "arabic": (self._ARABIC_FIRST, self._ARABIC_LAST),
            "hispanic": (self._HISPANIC_FIRST, self._HISPANIC_LAST),
            "japanese": (self._JAPANESE_FIRST, self._JAPANESE_LAST),
        }

        if origin in pools:
            first, last = pools[origin]
            return f"{random.choice(first)} {random.choice(last)}"
        return f"{self.fake.first_name()} {self.fake.last_name()}"

    # --- REPLACE tier ---

    def _generate_replacement(self, label, original=""):
        """Generate a realistic fake value based on entity type."""
        label = label.lower()

        if label == "person":
            return self._generate_person_name(original)

        elif label == "organization":
            name = self.fake.last_name()
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
            if re.search(r'\+91|\b91-', original):
                return f"+91-{random.randint(70000, 99999)}-{random.randint(10000, 99999)}"
            return f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

        elif label in ("ssn", "government id"):
            # figure out what kind of ID this is
            if re.match(r'^[A-Z]\d{7,8}$', original.strip()):
                # passport-style
                return f"{chr(random.randint(65, 90))}{random.randint(1000000, 99999999)}"
            elif re.match(r'^\d{4}[- ]?\d{4}[- ]?\d{4}$', original.strip()):
                # aadhaar-style
                return f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"

        elif label == "aadhaar":
            return f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

        elif label == "pan_card":
            letters = ''.join(chr(random.randint(65, 90)) for _ in range(5))
            return f"{letters}{random.randint(1000, 9999)}{chr(random.randint(65, 90))}"

        elif label == "phone_in":
            return f"+91-{random.randint(70000, 99999)}-{random.randint(10000, 99999)}"

        elif label == "credit_card":
            return f"XXXX-XXXX-XXXX-{random.randint(1000, 9999)}"

        elif label == "url":
            return f"https://example-{self.fake.last_name().lower()}.com/page"

        elif label == "ip_address":
            return f"{random.randint(10, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

        elif label == "project name":
            return f"Project {random.choice(self._codenames)}"

        elif label == "product name":
            return f"{self.fake.last_name()} {random.choice(self._product_suffixes)}"

        else:
            return self.fake.word().capitalize()

    # --- PERTURB tier ---

    def _perturb(self, label, original):
        """Small noise that preserves context."""
        label = label.lower()
        if label == "date":
            return self._perturb_date(original)
        elif label == "money amount":
            return self._perturb_money(original)
        elif label == "age":
            return self._perturb_age(original)
        elif label == "percentage":
            return self._perturb_percentage(original)
        return original

    def _perturb_date(self, original):
        """Shift date by +-3-7 days, keeping the same format."""
        text = original.strip()

        # skip complex date expressions
        if " and " in text.lower():
            return original
        if re.match(r'Q\d\s+\d{4}', text, re.IGNORECASE):
            return original
        if re.match(r'^FY\s?\d{4}$', text, re.IGNORECASE):
            return original
        if re.match(r'^\d{4}$', text):
            return original
        if re.match(r'^[A-Z][a-z]+ \d{4}$', text):
            return original

        try:
            parsed = dateutil_parser.parse(text, fuzzy=True)
        except (ValueError, OverflowError):
            return original

        shift = random.choice([-1, 1]) * random.randint(3, 7)
        shifted = parsed + timedelta(days=shift)

        # don't cross year boundary
        if shifted.year != parsed.year:
            shift = abs(shift) if parsed.month <= 6 else -abs(shift)
            shifted = parsed + timedelta(days=shift)

        # try to match original format
        if re.match(r'^[A-Z][a-z]+ \d{1,2}, \d{4}$', text):
            return shifted.strftime("%B %-d, %Y")
        elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', text):
            return shifted.strftime("%-m/%-d/%Y")
        elif re.match(r'^\d{4}-\d{2}-\d{2}$', text):
            return shifted.strftime("%Y-%m-%d")
        elif re.match(r'^\d{1,2}-\d{1,2}-\d{4}$', text):
            return shifted.strftime("%-d-%-m-%Y")
        else:
            return shifted.strftime("%B %-d, %Y")

    def _perturb_money(self, original):
        """Multiply amount by 0.85-1.15, keep scale word and currency symbol."""
        text = original.lower().strip()

        # find scale word (billion, lakh, crore, etc.)
        scale_word = ""
        original_scale_word = ""
        for word in ("trillion", "billion", "million", "thousand", "lakh", "crore"):
            if word in text:
                scale_word = word
                idx = text.find(word)
                original_scale_word = original.strip()[idx:idx + len(word)]
                break

        # check for K/k abbreviation
        k_suffix = ""
        if not scale_word and re.search(r'\d[Kk]\b', original):
            k_suffix = "K" if "K" in original else "k"

        # extract the number
        num_match = re.search(r'[\d,.]+', text)
        if not num_match:
            return original
        try:
            num = float(num_match.group().replace(",", ""))
        except ValueError:
            return original

        factor = random.uniform(0.85, 1.15)
        perturbed = num * factor

        # figure out currency symbol
        currency = ""
        for sym in ["$", "€", "£", "¥", "₹"]:
            if sym in original:
                currency = sym
                break

        # format output
        if scale_word:
            if perturbed == int(perturbed):
                return f"{currency}{int(perturbed)} {original_scale_word}"
            return f"{currency}{perturbed:.1f} {original_scale_word}"
        elif k_suffix:
            return f"{currency}{int(perturbed)}{k_suffix}"
        else:
            return f"{currency}{int(perturbed):,}"

    def _perturb_age(self, original):
        num_match = re.search(r'\d+', original)
        if not num_match:
            return original
        age = int(num_match.group())
        shift = random.choice([-1, 1]) * random.randint(2, 3)
        return original.replace(num_match.group(), str(max(1, age + shift)))

    def _perturb_percentage(self, original):
        num_match = re.search(r'[\d.]+', original)
        if not num_match:
            return original
        pct = float(num_match.group())
        new_pct = round(pct * random.uniform(0.85, 1.15), 1)
        if "." not in num_match.group():
            new_pct = int(round(new_pct))
        return original.replace(num_match.group(), str(new_pct))