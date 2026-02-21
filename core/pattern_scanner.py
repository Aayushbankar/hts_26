"""
pattern_scanner.py - regex layer for finding structured PII
like emails, phone numbers, credit cards, aadhaar etc.
that the NER model usually misses
"""

import re


class PatternScanner:

    PATTERNS = {
        # standard stuff
        "email": re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+'),
        "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        "credit_card": re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
        "url": re.compile(r'https?://[\w./\-?=&#]+'),
        "ip_address": re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),

        # phone (US/intl format)
        "phone": re.compile(
            r'(?:\+?\d{1,3}[\s.-]?)?'
            r'\(?\d{3}\)?'
            r'[\s.-]?\d{3}'
            r'[\s.-]?\d{4}'
        ),

        # indian PII
        "aadhaar": re.compile(r'\b\d{4}[\s-]\d{4}[\s-]\d{4}\b'),
        "pan_card": re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b'),
        "phone_in": re.compile(r'(?:\+91[\s.-]?)[6-9]\d{4}[\s.-]?\d{5}'),
    }

    def scan(self, text: str) -> list[dict]:
        """scan text for all patterns, returns list of matches"""
        entities = []
        for label, pattern in self.PATTERNS.items():
            for match in pattern.finditer(text):
                entities.append({
                    "text": match.group(),
                    "label": label,
                    "start": match.start(),
                    "end": match.end(),
                    "source": "regex",
                })
        return entities
