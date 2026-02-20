"""
Real-world stress test for Silent-Protocol core engine.
Runs all 40 prompts from real_prompts.json and generates a detailed report.
"""

import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.sanitiser import Sanitizer

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "real_prompts.json")
REPORT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_report.txt")


def run():
    with open(DATA) as f:
        data = json.load(f)

    prompts = data["prompts"]
    print(f"⏳ Loading core engine...")
    t0 = time.time()
    sanitizer = Sanitizer()
    print(f"✅ Engine loaded in {time.time()-t0:.1f}s\n")

    lines = []
    stats = {"total": 0, "entities": 0, "replaced": 0, "perturbed": 0, "preserved": 0, "errors": 0}

    for p in prompts:
        pid = p["id"]
        cat = p["category"]
        prompt = p["prompt"]
        stats["total"] += 1

        header = f"\n{'='*80}\n[{pid}] {cat}\n{'='*80}"
        lines.append(header)
        print(header)

        try:
            t1 = time.time()
            sanitized, entities, alias_map, score = sanitizer.sanitize_prompt(prompt)
            elapsed = time.time() - t1

            lines.append(f"  Time: {elapsed:.3f}s")
            lines.append(f"  Entities found: {len(entities)}")
            stats["entities"] += len(entities)

            # Show each entity
            for e in entities:
                tier = e.get("tier", "?")
                alias = alias_map.get(e["text"], e["text"])
                marker = "🔴" if tier == "REPLACE" else "🟡" if tier == "PERTURB" else "🟢"
                line = f"    {marker} [{tier:8s}] {e['label']:20s} | '{e['text']}' → '{alias}'"
                lines.append(line)
                print(line)
                if tier == "REPLACE": stats["replaced"] += 1
                elif tier == "PERTURB": stats["perturbed"] += 1
                elif tier == "PRESERVE": stats["preserved"] += 1

            # Score
            lines.append(f"  Score: {score['score']}/100 ({score['risk_level']})")
            lines.append(f"  HIPAA: {score['hipaa_identifiers_protected']}/{score['hipaa_identifiers_found']}")

            # Show sanitized vs original (first 200 chars)
            lines.append(f"\n  ORIGINAL:  {prompt[:200]}...")
            lines.append(f"  SANITIZED: {sanitized[:200]}...")

            # Flag potential issues
            issues = []
            # Issue: common city names replaced (Paris, London, etc.)
            common_places = ["Paris", "London", "Amsterdam", "Barcelona", "Dubai",
                             "Tokyo", "Berlin", "Rome", "Singapore", "New York"]
            for place in common_places:
                if place in prompt and place not in sanitized:
                    issues.append(f"⚠️  Common city '{place}' was replaced — may break context")

            # Issue: product/company names that shouldn't be replaced
            known_products = ["Kubernetes", "Jira", "Shopify", "Stripe", "LinkedIn",
                              "YouTube", "Instagram", "WhatsApp", "Amazon", "Google",
                              "Apple", "Netflix", "Uber", "Slack", "Zoom"]
            for prod in known_products:
                if prod in prompt and prod not in sanitized:
                    issues.append(f"⚠️  Known product/platform '{prod}' was replaced")

            # Issue: medical terms that got replaced
            med_terms = ["Metformin", "Aspirin", "Clopidogrel", "ADHD", "diabetes",
                         "hypertension", "cancer", "stroke", "Alzheimer"]
            for term in med_terms:
                if term.lower() in prompt.lower() and term.lower() not in sanitized.lower():
                    issues.append(f"⚠️  Medical term '{term}' was REPLACED (should be PRESERVED)")

            if issues:
                lines.append(f"\n  🚩 ISSUES DETECTED ({len(issues)}):")
                for iss in issues:
                    lines.append(f"    {iss}")
                    print(f"  {iss}")
            else:
                lines.append(f"\n  ✅ No obvious issues")

            # Desanitize round-trip test
            restored = sanitizer.desanitize_response(sanitized)
            roundtrip_ok = True
            for real, fake in alias_map.items():
                if fake in restored:
                    roundtrip_ok = False
                    lines.append(f"    ⚠️  Roundtrip failed: '{fake}' still in restored text")
            if roundtrip_ok:
                lines.append(f"  ✅ Round-trip desanitization OK")

        except Exception as ex:
            stats["errors"] += 1
            err = f"  ❌ ERROR: {ex}"
            lines.append(err)
            print(err)

        # Reset between prompts to simulate fresh sessions
        sanitizer.clear()

    # Summary
    summary = f"""
{'='*80}
SUMMARY
{'='*80}
Total prompts tested: {stats['total']}
Total entities found: {stats['entities']}
  - REPLACE:  {stats['replaced']}
  - PERTURB:  {stats['perturbed']}
  - PRESERVE: {stats['preserved']}
Errors: {stats['errors']}
"""
    lines.append(summary)
    print(summary)

    with open(REPORT, "w") as f:
        f.write("\n".join(lines))
    print(f"📄 Full report saved to: {REPORT}")


if __name__ == "__main__":
    run()
