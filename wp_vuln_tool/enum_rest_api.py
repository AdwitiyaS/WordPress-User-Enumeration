from wp_vuln_tool.http_client import get_session, safe_get


def enumerate_rest_api(target: str) -> dict:
    session = get_session()
    url = target.rstrip("/") + "/wp-json/wp/v2/users"
    response = safe_get(session, url)

    if isinstance(response, dict) and "error" in response:
        return {"technique": "rest_api", "success": False, "error": response["error"], "users": []}

    if response.status_code != 200:
        return {
            "technique": "rest_api",
            "success": False,
            "reason": f"HTTP {response.status_code}, endpoint not exposed or blocked",
            "users": [],
        }

    try:
        data = response.json()
    except ValueError:
        return {"technique": "rest_api", "success": False, "reason": "Response was not valid JSON", "users": []}

    if not isinstance(data, list):
        return {"technique": "rest_api", "success": False, "reason": "Unexpected response shape", "users": []}

    users = [{"id": u.get("id"), "username": u.get("slug"), "name": u.get("name")} for u in data]
    return {
        "technique": "rest_api",
        "success": len(users) > 0,
        "users": users,
        "evidence": f"GET {url} returned {len(users)} user objects without authentication",
    }