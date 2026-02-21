"""
basic tests for the sanitizer
run: python test_sanitizer.py
"""

from sanitiser import Sanitizer

print("=" * 60)
print("Loading Sanitizer (GLiNER model)... this takes ~5 seconds")
print("=" * 60)

sanitizer = Sanitizer()
print("Model loaded!\n")


# TEST 1: Basic Sanitization
print("-" * 60)
print("TEST 1: Basic Sanitization + Privacy Scorecard")
print("-" * 60)

prompt = "Tim Cook and Sundar Pichai discussed the Apple-Google deal in Cupertino."
sanitized, entities, alias_map, privacy_score = sanitizer.sanitize_prompt(prompt)

print(f"Original:       {prompt}")
print(f"Sanitized:      {sanitized}")
print(f"Privacy Score:  {privacy_score['score']}/100 ({privacy_score['risk_level']})")
print(f"Entities:       {len(entities)} detected")
for e in entities:
    tier = e.get("tier", "?")
    print(f"  [{tier:8s}] {e['text']:20s} [{e['label']}]")

# replaced entities should NOT appear in sanitized text
replaced = [e for e in entities if e.get("tier") == "REPLACE"]
leaked = [e["text"] for e in replaced if e["text"] in sanitized]
if leaked:
    print(f"FAILED - Leaked: {leaked}")
else:
    print("PASSED - No real names in sanitized text!")

print()


# TEST 2: De-sanitization Round-Trip
print("-" * 60)
print("TEST 2: De-sanitization Round-Trip")
print("-" * 60)

prompt2 = "Tim Cook works at Apple."
sanitized2, entities2, map2, score2 = sanitizer.sanitize_prompt(prompt2)
print(f"Sanitized: {sanitized2}")

fake_tim = map2.get("Tim Cook", "Tim Cook")
fake_apple = map2.get("Apple", "Apple")
fake_response = f"{fake_tim} is the CEO of {fake_apple}."
print(f"Fake LLM response: {fake_response}")

restored = sanitizer.desanitize_response(fake_response)
print(f"Restored:  {restored}")

if "Tim Cook" in restored:
    print("PASSED - Real name restored!")
else:
    print("FAILED - Real name not restored!")

print()


# TEST 3: Consistency (same entity = same alias)
print("-" * 60)
print("TEST 3: Consistency")
print("-" * 60)

sanitizer2 = Sanitizer()

s1, _, map1, _ = sanitizer2.sanitize_prompt("Apple is great.")
s2, _, map2_2, _ = sanitizer2.sanitize_prompt("I love Apple products.")

alias1 = map1.get("Apple", None) or map2_2.get("Apple", None)
print(f"Alias for Apple: {alias1}")
print(f"Message 1: {s1}")
print(f"Message 2: {s2}")

if alias1 and alias1 in s1 and alias1 in s2:
    print("PASSED - Same alias used both times!")
else:
    print("FAILED - Alias changed between messages!")

print()


# TEST 4: No entities (passthrough)
print("-" * 60)
print("TEST 4: No entities")
print("-" * 60)

prompt4 = "What is the square root of 144?"
sanitized4, entities4, _, score4 = sanitizer.sanitize_prompt(prompt4)

print(f"Original:  {prompt4}")
print(f"Sanitized: {sanitized4}")
print(f"Score:     {score4['score']}/100 (risk: {score4['risk_level']})")

if sanitized4 == prompt4:
    print("PASSED - Text unchanged when no entities!")
else:
    print("FAILED - Text was modified!")

print()


# TEST 5: PRESERVE tier (medical context)
print("-" * 60)
print("TEST 5: PRESERVE tier - Medical context preserved")
print("-" * 60)

prompt5 = "Dr. Sarah Chen prescribed Metformin for John Smith's Type 2 Diabetes."
sanitized5, entities5, map5, score5 = sanitizer.sanitize_prompt(prompt5)

print(f"Original:  {prompt5}")
print(f"Sanitized: {sanitized5}")
print(f"Score:     {score5['score']}/100")

# names should be replaced
names_gone = all(name not in sanitized5 for name in ["Sarah Chen", "John Smith"])
# medical terms should be kept
context_kept = "Metformin" in sanitized5 or "Type 2 Diabetes" in sanitized5

print(f"Names replaced:    {'yes' if names_gone else 'NO'}")
print(f"Context preserved: {'yes' if context_kept else 'NO'}")

if names_gone and context_kept:
    print("PASSED - Privacy + utility!")
elif names_gone:
    print("PARTIAL - Names replaced but context lost too")
else:
    print("FAILED - Names leaked through!")

print()


# TEST 6: PERTURB tier (dates and money)
print("-" * 60)
print("TEST 6: PERTURB tier - Dates/Money adjusted, not replaced")
print("-" * 60)

prompt6 = "The $3.5 billion deal closes on January 15, 2026."
sanitized6, entities6, map6, score6 = sanitizer.sanitize_prompt(prompt6)

print(f"Original:  {prompt6}")
print(f"Sanitized: {sanitized6}")

# check money is perturbed (should say "billion" still)
has_billion = "billion" in sanitized6
print(f"Scale preserved (billion): {'yes' if has_billion else 'NO'}")

# check date is perturbed
has_2026 = "2026" in sanitized6 or "2025" in sanitized6
print(f"Year preserved: {'yes' if has_2026 else 'NO'}")

print()


# TEST 7: Regex detection (structured PII)
print("-" * 60)
print("TEST 7: Regex detection - SSN, Email, IP")
print("-" * 60)

prompt7 = "SSN: 456-78-9012, email: secret@company.com, IP: 10.0.0.1"
sanitized7, entities7, _, score7 = sanitizer.sanitize_prompt(prompt7)

print(f"Original:  {prompt7}")
print(f"Sanitized: {sanitized7}")

ssn_gone = "456-78-9012" not in sanitized7
email_gone = "secret@company.com" not in sanitized7
ip_gone = "10.0.0.1" not in sanitized7

print(f"SSN replaced:   {'yes' if ssn_gone else 'NO'}")
print(f"Email replaced: {'yes' if email_gone else 'NO'}")
print(f"IP replaced:    {'yes' if ip_gone else 'NO'}")

if ssn_gone and email_gone and ip_gone:
    print("PASSED - All structured PII caught by regex!")
else:
    print("FAILED - Some PII leaked!")


# done
print("\n" + "=" * 60)
print("ALL TESTS COMPLETE")
print("=" * 60)
