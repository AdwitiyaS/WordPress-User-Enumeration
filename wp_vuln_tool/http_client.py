import requests

DEFAULT_TIMEOUT = 10
USER_AGENT = "WP-UserEnum-Research/1.0 (authorized-security-testing)"


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    return session


def safe_get(session: requests.Session, url: str, **kwargs):
    try:
        return session.get(url, timeout=DEFAULT_TIMEOUT, **kwargs)
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def safe_post(session: requests.Session, url: str, **kwargs):
    try:
        return session.post(url, timeout=DEFAULT_TIMEOUT, **kwargs)
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}