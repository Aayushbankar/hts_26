import json
import os
import sys
import time

# Add the backend path to allow importing the FastAPI app for direct TestClient testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

try:
    from fastapi.testclient import TestClient
    from main import app
except ImportError:
    print("❌ Error: Could not import backend. Please run this script from the project root.")
    sys.exit(1)

# Initialize FastAPI Test Client (simulates frontend requests without needing uvicorn running)
client = TestClient(app)

# ANSI Colors
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"

def print_header(title):
    print(f"\n{C_CYAN}{C_BOLD}{'='*80}{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}  {title}{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}{'='*80}{C_RESET}")

def run_prompt_test(test_id, name_or_scenario, prompt_text, expected_behavior="", wait_time=0.5):
    """Sends a single prompt to the backend and prints the result beautifully."""
    # Reset session before each independent test
    client.post("/reset")

    print(f"\n{C_BOLD}[{test_id}] {name_or_scenario}{C_RESET}")
    print(f"  {C_BLUE}Prompt:{C_RESET} {prompt_text}")
    
    if expected_behavior:
        print(f"  {C_YELLOW}Expected:{C_RESET} {expected_behavior}")

    start_time = time.time()
    response = client.post("/chat", json={"message": prompt_text})
    latency = time.time() - start_time

    if response.status_code != 200:
        print(f"  {C_RED}❌ ERROR {response.status_code}:{C_RESET} {response.text}")
        return False

    res = response.json()
    sanitized = res.get("sanitized_prompt", "")
    restored = res.get("response", "")
    entities = res.get("entities_detected", [])
    score_data = res.get("privacy_score", {})
    score = score_data.get("score", 0)

    print(f"  {C_GREEN}Sanitized (To LLM):{C_RESET} {sanitized}")
    print(f"  {C_CYAN}Restored (To User):{C_RESET} {restored[:150]}..." if len(restored) > 150 else f"  {C_CYAN}Restored (To User):{C_RESET} {restored}")
    
    # Print entities neatly
    if entities:
        print(f"  {C_BOLD}Entities Detected ({len(entities)}):{C_RESET}")
        for e in entities:
            tier = e["tier"]
            color = C_RED if tier == "REPLACE" else (C_YELLOW if tier == "PERTURB" else C_GREEN)
            print(f"    {color}[{tier}]{C_RESET} {e['label']:15s} | {e['text']:25s} -> {e['alias']}")
    else:
        print(f"  {C_BOLD}Entities Detected (0){C_RESET}")

    score_color = C_GREEN if score >= 85 else (C_YELLOW if score >= 50 else C_RED)
    print(f"  {C_BOLD}Privacy Score:{C_RESET} {score_color}{score}/100{C_RESET} | Latency: {latency:.2f}s")
    
    time.sleep(wait_time)
    return True

def run_all_tests():
    dataset_path = os.path.join(os.path.dirname(__file__), "core", "dataset.json")
    if not os.path.exists(dataset_path):
        print(f"{C_RED}Dataset not found at {dataset_path}{C_RESET}")
        return

    with open(dataset_path, "r") as f:
        ds = json.load(f)

    print_header(f"Silent-Protocol CLI Test Environment")
    print(f"Loaded {ds['_meta']['total_prompts']} prompts from dataset.json Version {ds['_meta']['version']}")

    # 1. Run Part A (Testing Scenarios)
    print_header("PART A: TESTING SCENARIOS")
    testing_groups = ds["part_a_testing"]
    for group_key, tests in testing_groups.items():
        if group_key.startswith("_"): continue
        print(f"\n{C_BOLD}--- {group_key.upper().replace('_', ' ')} ---{C_RESET}")
        for test in tests:
            # Check if this test uses prompt_1 / prompt_2 (Consistency test T17)
            if "prompt_1" in test:
                run_prompt_test(test["id"] + "A", test["test_name"] + " (Call 1)", test["prompt_1"])
                run_prompt_test(test["id"] + "B", test["test_name"] + " (Call 2)", test["prompt_2"])
            else:
                run_prompt_test(test["id"], test["test_name"], test["prompt"], test.get("expected_behavior", ""))

    # 2. Run Part B (Real World)
    print_header("PART B: REAL WORLD SCENARIOS")
    rw_groups = ds["part_b_real_world"]
    for group_key, tests in rw_groups.items():
        if group_key.startswith("_"): continue
        print(f"\n{C_BOLD}--- INDUSTRY: {group_key.upper().replace('_', ' ')} ---{C_RESET}")
        for test in tests:
            run_prompt_test(test["id"], test["scenario"], test["prompt"])

    # 3. Run Hero Prompts
    print_header("HERO DEMO PROMPTS")
    heroes = ds["hero_prompts"]
    for key, hero in heroes.items():
        if key.startswith("_"): continue
        run_prompt_test(hero["id"], hero["name"], hero["prompt"], "HERO PROMTP - Full Pipeline Test")

    print_header("CLI TESTS COMPLETE")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        print_header("Silent-Protocol Interactive Dev Env")
        client.post("/reset")
        while True:
            try:
                user_msg = input(f"\n{C_BLUE}You (Enter to exit): {C_RESET}")
                if not user_msg.strip():
                    break
                run_prompt_test("INT", "Interactive Test", user_msg, wait_time=0)
            except KeyboardInterrupt:
                break
    else:
        run_all_tests()
        print(f"\nRun {C_CYAN}python cli_tester.py interactive{C_RESET} to test your own prompts!")
