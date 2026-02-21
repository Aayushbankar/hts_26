"""
pitch tests for the demo - runs all our test scenarios across
multiple domains to show the 3-tier treatment in action

run: python pitch_tests.py
"""

from sanitiser import Sanitizer
import json

results = []
test_num = 0


def show_score(score):
    """print the privacy score in a readable way"""
    s = score
    print(f"\n  Privacy Score: {s['score']}/100")
    print(f"  Entities: {s['total_entities']} total ({s['replaced']} replaced, {s['perturbed']} perturbed, {s['preserved']} preserved)")
    print(f"  Risk Level: {s['risk_level']}")
    print(f"  HIPAA identifiers: {s['hipaa_identifiers_found']} found, {s['hipaa_identifiers_protected']} protected")


def run_test(domain, scenario, prompt, expect_preserved=None):
    """run one test case and check for leaks"""
    global test_num
    test_num += 1

    sanitized, entities, alias_map, privacy_score = sanitizer.sanitize_prompt(prompt)

    # check for leaks - replaced entities shouldnt appear in output
    replaced = [e for e in entities if e.get("tier") == "REPLACE"]
    leaked = [e["text"] for e in replaced if e["text"] in sanitized]

    # check preserved entities are still there
    preserved_ok = True
    if expect_preserved:
        for term in expect_preserved:
            if term not in sanitized:
                preserved_ok = False
                break

    passed = len(leaked) == 0 and len(replaced) > 0 and preserved_ok

    print(f"\n{'=' * 60}")
    print(f"TEST {test_num}: [{domain}] {scenario}")
    print(f"{'=' * 60}")
    print(f"ORIGINAL:")
    print(f"   {prompt}")
    print(f"\nSANITIZED (what AI sees):")
    print(f"   {sanitized}")

    print(f"\nENTITIES ({len(entities)}):")
    for e in entities:
        tier = e.get("tier", "?")
        alias = alias_map.get(e["text"], e["text"])
        score_str = f" ({e['score']:.0%})" if "score" in e else ""
        print(f"   [{tier:8s}] {e['text']:30s} -> {alias:30s} [{e['label']}]{score_str}")

    show_score(privacy_score)

    # check preserved terms
    if expect_preserved:
        print(f"\nCONTEXT PRESERVATION CHECK:")
        for term in expect_preserved:
            status = "KEPT" if term in sanitized else "LOST!!"
            print(f"   {status}: \"{term}\"")

    if passed:
        print(f"\nPASSED - {len(replaced)} entities replaced, zero leaks{', context preserved' if expect_preserved else ''}")
    elif len(replaced) == 0:
        print(f"\nWARNING - No REPLACE entities detected")
    elif not preserved_ok:
        print(f"\nFAILED - Domain-critical context was destroyed")
    else:
        print(f"\nFAILED - Leaked: {leaked}")

    results.append({
        "test": test_num,
        "domain": domain,
        "scenario": scenario,
        "total_entities": len(entities),
        "replaced": len(replaced),
        "leaked": len(leaked),
        "privacy_score": privacy_score["score"],
        "risk_level": privacy_score["risk_level"],
        "preserved_ok": preserved_ok,
        "passed": passed,
    })

    return passed


# setup
print("=" * 70)
print("  SILENT-PROTOCOL — Complete Pitch Dataset")
print("  3-Layer Detection • 3-Tier Treatment • Privacy Scorecard")
print("  Loading GLiNER model...")
print("=" * 70)

sanitizer = Sanitizer()
print("Model loaded!\n")


# ---- DOMAIN 1: MEDICAL ----

print("\n\n--- DOMAIN 1: MEDICAL (HIPAA-SENSITIVE) ---")
print("Drug names & conditions preserved — competitors destroy these!")

run_test("MEDICAL", "Prescription + Diagnosis",
    "Dr. Sarah Chen at Mayo Clinic prescribed Metformin 500mg for John Smith's "
    "Type 2 Diabetes. He reports chest pain and shortness of breath since "
    "January 15, 2026. Contact: john.smith@email.com, phone: +1-555-123-4567.",
    expect_preserved=["Metformin 500mg", "Type 2 Diabetes", "chest pain", "shortness of breath"]
)

run_test("MEDICAL", "Mental Health Referral",
    "Refer patient Emily Davis to the Behavioral Health unit at Johns Hopkins Hospital. "
    "She has been diagnosed with major depressive disorder and generalized anxiety disorder. "
    "Currently taking Sertraline 100mg. Her therapist Dr. Michael Brown notes "
    "recurring insomnia and panic attacks. Next appointment March 10, 2026.",
    expect_preserved=["major depressive disorder", "generalized anxiety disorder",
                      "Sertraline 100mg", "insomnia", "panic attacks"]
)

run_test("MEDICAL", "Surgical Consultation",
    "Patient Robert Williams, age 62, requires a knee replacement surgery at "
    "Cleveland Clinic. His orthopedic surgeon Dr. Lisa Park reviewed the MRI results "
    "showing severe osteoarthritis. He is currently on Ibuprofen 800mg and "
    "Hydrocodone 10mg for pain management. Surgery scheduled for February 28, 2026.",
    expect_preserved=["knee replacement", "MRI", "osteoarthritis", "Ibuprofen 800mg",
                      "Hydrocodone 10mg"]
)


# ---- DOMAIN 2: LEGAL ----

print("\n\n--- DOMAIN 2: LEGAL ---")
print("Legal concepts preserved, party names replaced")

run_test("LEGAL", "Breach of Contract",
    "Apple Inc has filed a breach of contract suit against Tim Cook's former "
    "business partner regarding the non-compete clause in their $3.5 billion deal. "
    "The case will be heard in Delaware by Judge Karen Mitchell on March 15, 2026.",
    expect_preserved=["breach of contract", "non-compete"]
)

run_test("LEGAL", "IP Infringement + NDA",
    "Draft a cease-and-desist letter from Samsung Electronics to Xiaomi Corporation "
    "regarding intellectual property infringement. The matter involves patent violations "
    "under the non-disclosure agreement signed on June 5, 2024. Samsung's general "
    "counsel James Park at the Seoul office will lead the litigation. "
    "Contact: j.park@samsung-legal.com.",
    expect_preserved=["intellectual property infringement", "non-disclosure agreement"]
)

run_test("LEGAL", "Employment + Indemnification",
    "Sarah Johnson's wrongful termination claim against Goldman Sachs involves "
    "a breach of the indemnification clause in her employment contract. "
    "Her attorney at Morgan Lewis filed the complaint citing fiduciary duty violations "
    "and failure to provide severance. Case number GS-2026-0047. "
    "Filed in the New York Southern District Court on January 22, 2026.",
    expect_preserved=["wrongful termination", "indemnification", "fiduciary duty"]
)


# ---- DOMAIN 3: FINANCIAL ----

print("\n\n--- DOMAIN 3: FINANCIAL ---")
print("Instruments preserved, amounts perturbed, names replaced")

run_test("FINANCIAL", "Series B + SAFE Agreement",
    "TechVenture Partners led a $25 million Series B round for Nexon Corp, "
    "with participation from Sequoia Capital. CEO Amanda Chen negotiated a "
    "SAFE agreement with a $150 million valuation cap. The board meeting in "
    "San Francisco is scheduled for April 2, 2026. Contact: a.chen@nexon.io.",
    expect_preserved=["Series B", "SAFE agreement"]
)

run_test("FINANCIAL", "IPO Filing + 401(k)",
    "Goldman Sachs will underwrite the IPO of DataSync Technologies, valued at "
    "$2.1 billion. CFO Michael Torres confirmed that the company's 401(k) plan "
    "will be restructured post-IPO. The SEC filing will be submitted from their "
    "New York headquarters by March 30, 2026.",
    expect_preserved=["IPO", "401(k)"]
)

run_test("FINANCIAL", "M&A + Convertible Note",
    "JPMorgan Chase is advising on the acquisition of CloudBase Inc by Amazon "
    "for $44 billion. The deal includes a $500 million convertible note issued "
    "by lead banker David Kim at the London office. The stock option pool worth "
    "$200 million will be distributed to existing shareholders. Closing date: "
    "June 15, 2026.",
    expect_preserved=["convertible note", "stock option"]
)


# ---- DOMAIN 4: COMPLIANCE ----

print("\n\n--- DOMAIN 4: COMPLIANCE / REGULATORY ---")
print("Regulation names preserved")

run_test("COMPLIANCE", "GDPR + Data Breach",
    "Our Chief Privacy Officer Jennifer Walsh at Acme Corp discovered a "
    "data breach affecting 50,000 customers in the EU. Under GDPR Article 33, "
    "we must notify the supervisory authority within 72 hours. The incident "
    "originated from the Berlin datacenter on February 10, 2026. "
    "Contact the DPO at privacy@acme-corp.com.",
    expect_preserved=["GDPR"]
)

run_test("COMPLIANCE", "HIPAA + SOX Audit",
    "HealthFirst Systems failed their SOX compliance audit conducted by "
    "Deloitte. CEO Brian Martinez directed the compliance team led by "
    "VP Sarah Kim to address HIPAA violations found in the patient data "
    "handling process at their Austin facility. Report due March 1, 2026.",
    expect_preserved=["SOX", "HIPAA"]
)


# ---- DOMAIN 5: GOVERNMENT ----

print("\n\n--- DOMAIN 5: GOVERNMENT / DEFENSE ---")
print("Project names replaced, briefing details protected")

run_test("GOVERNMENT", "Defense Briefing",
    "Prepare a briefing document for Project Sentinel, overseen by General "
    "Robert Hayes at the Pentagon in Washington DC. The project involves "
    "collaboration with Lockheed Martin and a budget of $4.7 billion. "
    "The cybersecurity component is led by Colonel Diana Ross in coordination "
    "with CrowdStrike. Top Secret classification applies.",
)

run_test("GOVERNMENT", "Policy Draft",
    "Draft a cybersecurity policy for the Department of Homeland Security. "
    "Director Lisa Monaco has requested recommendations following the "
    "SolarWinds breach investigation led by Mandiant in Austin, Texas. "
    "Budget allocation: $350 million for FY2026. "
    "Contact: l.monaco@dhs.gov, phone: +1-202-555-0100.",
)


# ---- DOMAIN 6: CORPORATE / HR ----

print("\n\n--- DOMAIN 6: CORPORATE / HR ---")
print("Employee names replaced, job titles/roles preserved")

run_test("CORPORATE", "Performance Review",
    "Draft a performance review for Senior Software Engineer Priya Sharma at Google. "
    "She led Project Atlas which launched in Bangalore, India on April 2025. "
    "Her Engineering Manager Rajesh Patel and VP of Engineering Laura Chen "
    "both rated her as exceptional. Priya's SSN: 123-45-6789.",
    expect_preserved=[]
)

run_test("CORPORATE", "Restructuring Memo",
    "Write an internal memo: CEO Mark Zuckerberg announced that the Chief Technology "
    "Officer role at Meta will transition as the Reality Labs division in Menlo Park "
    "merges with the AI Research team. VP of Product Andrew Bosworth will lead the "
    "combined entity. Budget impact: $1.2 billion annually.",
)


# ---- DOMAIN 7: CROSS-DOMAIN TESTS ----

print("\n\n--- DOMAIN 7: CROSS-DOMAIN STRESS TESTS ---")
print("Prompts that combine multiple PII types and domains")

run_test("CROSS-DOMAIN", "Medical-Legal (Malpractice)",
    "Patient Maria Garcia is suing Dr. David Lee at Massachusetts General Hospital "
    "for malpractice. She was prescribed Warfarin 5mg for atrial fibrillation but "
    "experienced a hemorrhagic stroke due to improper dosage monitoring. "
    "Her attorney at Baker McKenzie filed for negligence and breach of duty. "
    "Insurance claim #MG-2026-1847. Contact: m.garcia@email.com.",
    expect_preserved=["Warfarin 5mg", "atrial fibrillation", "hemorrhagic stroke",
                      "malpractice", "negligence"]
)

run_test("CROSS-DOMAIN", "Financial-Compliance (AML)",
    "Our Anti-Money Laundering team at Wells Fargo flagged suspicious transactions "
    "from customer account held by Zhang Wei, totaling $8.5 million over 3 months. "
    "Compliance Officer Rachel Torres filed a Suspicious Activity Report under the "
    "Bank Secrecy Act. The transactions originated from wire transfers through HSBC "
    "in Hong Kong. IP address of last login: 103.45.67.89. SSN: 987-65-4321.",
    expect_preserved=["Anti-Money Laundering"]
)


# ---- HERO PROMPT for live demo ----

print("\n\n--- HERO PROMPT - Use this in your live demo! ---")

run_test("HERO DEMO", "Cross-Domain Sensitive Prompt",
    "Dr. Sarah Chen at Stanford Medical Center prescribed Metformin 500mg and "
    "Lisinopril 10mg for patient John Smith's Type 2 Diabetes and hypertension. "
    "He also has a pending breach of contract lawsuit against his former employer "
    "Apex Technologies, valued at $3.5 billion. His attorney at Sullivan & Cromwell "
    "is handling the non-compete clause dispute. John's SSN: 456-78-9012, "
    "email: john.smith@personal.com, phone: +1-650-555-0199. "
    "Next appointment: January 15, 2026.",
    expect_preserved=["Metformin 500mg", "Lisinopril 10mg", "Type 2 Diabetes",
                      "hypertension", "breach of contract", "non-compete"]
)


# ---- ROUND-TRIP TEST ----

print("\n\n--- ROUND-TRIP TEST - Prove de-sanitization works ---")

rt_sanitizer = Sanitizer()
rt_prompt = (
    "Tim Cook and Sundar Pichai met at Apple headquarters in Cupertino "
    "to discuss a partnership worth $500 million on January 20, 2026."
)
rt_sanitized, rt_entities, rt_map, rt_score = rt_sanitizer.sanitize_prompt(rt_prompt)

# build fake LLM response using aliases
fake_names = list(rt_map.values())[:2]
rt_fake_response = f"The meeting between {' and '.join(fake_names)} was productive. Both parties agreed to proceed."
rt_restored = rt_sanitizer.desanitize_response(rt_fake_response)

print(f"\nOriginal prompt:      {rt_prompt}")
print(f"What AI received:     {rt_sanitized}")
print(f"AI responded:         {rt_fake_response}")
print(f"User sees (restored): {rt_restored}")

real_names_back = any(name in rt_restored for name in rt_map.keys())
if real_names_back:
    print(f"\nROUND-TRIP PASSED - Real names restored!")
else:
    print(f"\nROUND-TRIP FAILED - Real names NOT restored")


# ---- FINAL REPORT ----

print(f"\n\n{'=' * 60}")
print("  FINAL REPORT")
print(f"{'=' * 60}")

total = len(results)
passed = sum(1 for r in results if r["passed"])
warned = sum(1 for r in results if r["total_entities"] == 0)
failed = total - passed - warned

print(f"\n  Total Tests:  {total}")
print(f"  Passed:       {passed}")
print(f"  Warnings:     {warned} (no entities detected)")
print(f"  Failed:       {failed}")

total_entities = sum(r["total_entities"] for r in results)
total_replaced = sum(r["replaced"] for r in results)
total_leaks = sum(r["leaked"] for r in results)
avg_score = sum(r["privacy_score"] for r in results) / max(len(results), 1)

print(f"\n  Total Entities Detected:  {total_entities}")
print(f"  Total Entities Replaced:  {total_replaced}")
print(f"  Total Data Leaks:         {total_leaks}")
print(f"  Average Privacy Score:    {avg_score:.0f}/100")

print(f"\n  Domains Covered: MEDICAL, LEGAL, FINANCIAL, COMPLIANCE,")
print(f"                   GOVERNMENT, CORPORATE, CROSS-DOMAIN")

print(f"\n  Full Alias Map ({len(sanitizer.get_alias_map())} entries):")
for real, fake in sorted(sanitizer.get_alias_map().items()):
    print(f"    {real:35s} -> {fake}")

print("\n" + "=" * 60)
print("  Done. Use the Hero Prompt for your live demo!")
print("=" * 60)
