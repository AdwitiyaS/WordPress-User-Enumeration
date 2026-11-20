import os
import argparse
from dotenv import load_dotenv

load_dotenv()


def get_target_url() -> str:
    parser = argparse.ArgumentParser(description="AI-driven WordPress user enumeration tool")
    parser.add_argument("--target", help="Target WordPress URL, e.g. http://localhost:8080")
    args, _ = parser.parse_known_args()

    target = args.target or os.environ.get("TARGET_URL")
    if not target:
        raise SystemExit("No target URL provided. Use --target or set TARGET_URL in .env")
    if not target.startswith(("http://", "https://")):
        raise SystemExit("Target URL must start with http:// or https://")
    return target