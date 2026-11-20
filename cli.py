import json
from datetime import datetime, timezone
from config import get_target_url
from agent.orchestrator import run


def main():
    target = get_target_url()
    print(f"[*] Target: {target}")
    print("[*] Starting AI-driven enumeration...\n")

    results = run(target)

    print("=== Techniques Tried ===")
    for t in results["techniques_tried"]:
        print(f"- {t['technique']}: success={t['success']}")

    print("\n=== Users Found ===")
    for u in results["users"]:
        print(f"- {u.get('username')}")

    if results.get("bruteforce"):
        bf = results["bruteforce"]
        status = f" (password: {bf['password_found']})" if bf["success"] else ""
        print(f"\n=== Brute-force: {bf['username']} ===\nSuccess: {bf['success']}{status}")

    print("\n=== AI Summary Report ===")
    print(results["ai_summary"])

    results["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n[*] Structured results written to results.json")


if __name__ == "__main__":
    main()