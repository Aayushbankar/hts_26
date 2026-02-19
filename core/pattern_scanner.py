"""
Layer 1: Regex-based PII detection for structured patterns.
Catches what NER models miss: emails, phones, SSNs, credit cards, URLs, IPs.
Returns entities in GLiNER-compatible format for seamless merging.
"""

import re


class PatternScanner:
    """High-precision regex scanner for structured PII patterns."""

    # Compiled patterns for performance
    PATTERNS = {
        "email": re.compile(
            r'[\w.+-]+@[\w-]+\.[\w.]+'
        ),
        "phone": re.compile(
            r'(?:\+?\d{1,3}[\s.-]?)?'   # optional country code
            r'\(?\d{3}\)?'                # area code
            r'[\s.-]?\d{3}'              # first 3 digits
            r'[\s.-]?\d{4}'              # last 4 digits
        ),
        "ssn": re.compile(
            r'\b\d{3}-\d{2}-\d{4}\b'
        ),
        "credit_card": re.compile(
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        ),
        "url": re.compile(
            r'https?://[\w./\-?=&#]+'
        ),
        "ip_address": re.compile(
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        ),
    }

    def scan(self, text: str) -> list[dict]:
        """
        Scan text for structured PII patterns.
        
        Returns list of dicts matching GLiNER output format:
            [{"text": "...", "label": "...", "start": N, "end": N}]
        """
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
