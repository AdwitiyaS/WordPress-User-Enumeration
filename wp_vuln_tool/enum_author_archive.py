from wp_vuln_tool.http_client import get_session, safe_get


def enumerate_author_archive(target: str, max_id: int = 10) -> dict:
    session = get_session()
    base = target.rstrip("/")
    found = []
    evidence = []

    for author_id in range(1, max_id + 1):
        url = f"{base}/?author={author_id}"
        response = safe_get(session, url, allow_redirects=False)

        if isinstance(response, dict) and "error" in response:
            continue

        if response.status_code in (301, 302):
            location = response.headers.get("Location", "")
            username = location.rstrip("/").split("/")[-1]
            if username:
                found.append({"id": author_id, "username": username})
                evidence.append(f"?author={author_id} -> redirected to /author/{username}/")

    return {
        "technique": "author_archive",
        "success": len(found) > 0,
        "users": found,
        "evidence": "; ".join(evidence) if evidence else "No author IDs resolved to a redirect",
    }