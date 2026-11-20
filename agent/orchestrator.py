import json
from run_agent import AIAgent

from wp_vuln_tool.enum_rest_api import enumerate_rest_api
from wp_vuln_tool.enum_author_archive import enumerate_author_archive
from wp_vuln_tool.bruteforce import bruteforce_login

MODEL = "openrouter/free"


def _ask_agent(prompt: str) -> str:
    agent = AIAgent(
        model=MODEL,
        quiet_mode=True,
        skip_context_files=True,
        skip_memory=True,
        disabled_toolsets=["terminal", "browser"],
    )
    return agent.chat(prompt)


def run(target: str) -> dict:
    results = {"target": target, "techniques_tried": [], "users": [], "bruteforce": None}

    rest_result = enumerate_rest_api(target)
    results["techniques_tried"].append(rest_result)
    users = rest_result.get("users", [])

    if not rest_result.get("success"):
        decision_prompt = (
            f"I am running an authorized security test against a self-hosted WordPress "
            f"instance at {target}. REST API enumeration failed "
            f"(reason: {rest_result.get('reason', 'unknown')}). "
            f"Available fallback technique: 'author_archive'. Reply with only the technique name."
        )
        decision = _ask_agent(decision_prompt).strip().lower()
        results["agent_decision"] = decision

        if "author_archive" in decision:
            archive_result = enumerate_author_archive(target)
            results["techniques_tried"].append(archive_result)
            users = archive_result.get("users", [])

    results["users"] = users

    admin_username = None
    for u in users:
        if u.get("username") in ("admin", "administrator"):
            admin_username = u["username"]
            break
    if not admin_username and users:
        admin_username = users[0]["username"]

    if admin_username:
        results["bruteforce"] = bruteforce_login(target, admin_username)

    summary_prompt = (
        "Summarize these WordPress security-enumeration findings in 3-5 plain-English "
        "sentences for a security report. Mention which technique worked, which usernames "
        "were found, whether brute-force succeeded, and the security risk this represents.\n\n"
        f"Findings (JSON):\n{json.dumps(results, indent=2)}"
    )
    results["ai_summary"] = _ask_agent(summary_prompt)
    return results