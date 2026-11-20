from wp_vuln_tool.http_client import get_session, safe_post


def check_username_exists(target: str, username: str) -> dict:
    session = get_session()
    url = target.rstrip("/") + "/wp-login.php"
    response = safe_post(
        session,
        url,
        data={"log": username, "pwd": "definitely-wrong-password-xyz", "wp-submit": "Log In"},
    )

    if isinstance(response, dict) and "error" in response:
        return {"technique": "login_error", "username": username, "exists": None, "error": response["error"]}

    body = response.text.lower()
    if "the password you entered" in body or "incorrect password" in body:
        return {"technique": "login_error", "username": username, "exists": True}
    if "invalid username" in body or "is not registered" in body or "unknown email address" in body:
        return {"technique": "login_error", "username": username, "exists": False}

    return {"technique": "login_error", "username": username, "exists": None, "reason": "Could not classify response"}