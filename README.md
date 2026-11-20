# AI-Driven WordPress User Enumeration Tool

An AI-orchestrated security tool that enumerates WordPress user accounts and
attempts a brute-force login against the discovered admin account, built as
a take-home assignment demonstrating applied security testing with an AI
agent in the loop.

## Approach and rationale

The tool separates two concerns deliberately:

1. **Deterministic enumeration/brute-force logic** (plain Python, fully
   unit-tested) — this must be reliable, so it does not depend on an LLM.
2. **AI decision-making** — used only where judgment genuinely helps:
   deciding which fallback technique to try next when the primary one
   fails, and writing a plain-English summary of the findings for a
   security report.

This keeps the core attack logic deterministic and testable, while still
giving the AI component a real role in planning and reporting, as the
assignment's section 3.2 allows ("AI component may: plan which enumeration
approach to try next... produce a summary report of findings").

## Architecture

```
React-less CLI tool, single process:

cli.py
  -> config.py            (reads --target / TARGET_URL / .env)
  -> agent/orchestrator.py (coordinates the run)
       -> wp_vuln_tool/enum_rest_api.py        (technique 1, tried first)
       -> run_agent.AIAgent.chat()             (if technique 1 fails: "what next?")
       -> wp_vuln_tool/enum_author_archive.py  (technique 2, fallback)
       -> wp_vuln_tool/bruteforce.py           (brute-force against discovered admin)
       -> run_agent.AIAgent.chat()             (final plain-English summary)
  -> results.json         (structured output)
```

**Modules:**
- `wp_vuln_tool/http_client.py` — shared `requests` session with timeouts and
  exception handling, so network failures never crash the tool.
- `wp_vuln_tool/enum_rest_api.py` — queries `/wp-json/wp/v2/users`, the
  unauthenticated WordPress REST API endpoint that lists user objects by
  default.
- `wp_vuln_tool/enum_author_archive.py` — walks `?author=1..10`, reading the
  `Location` header of the 301/302 redirect to `/author/<username>/` to
  recover usernames even when the REST API is restricted.
- `wp_vuln_tool/enum_login_error.py` — bonus technique: distinguishes
  WordPress's default "unknown username" vs "incorrect password" login
  error messages to confirm a username exists.
- `wp_vuln_tool/bruteforce.py` — attempts a short list of common passwords
  against `wp-login.php` for a discovered username, with a 1-second
  courtesy delay between attempts, detecting success via the
  `wordpress_logged_in_*` cookie or redirect to `/wp-admin/`.
- `agent/orchestrator.py` — the agent loop. Runs REST API enumeration
  first; if it fails, asks the AI (via the [Hermes Agent](https://hermes-agent.nousresearch.com)
  library, routed to a free model through OpenRouter) which fallback
  technique to try; runs brute-force against the likely admin account;
  asks the AI to write the final summary.

## AI integration

Uses [Hermes Agent](https://github.com/NousResearch/hermes-agent) as a
Python library (`from run_agent import AIAgent`), configured with
`model="openrouter/free"` so it routes to a genuinely free model via
[OpenRouter](https://openrouter.ai) — no cost to run. The `terminal` and
`browser` toolsets are explicitly disabled since the agent here is only
used for two things: a planning decision (which technique to try next) and
a natural-language summary — not for executing actions itself. This keeps
the integration simple, predictable, and easy to reason about compared to
giving the agent open-ended tool-execution access.

## Setup and usage

### 1. Start the vulnerable test target

```bash
docker compose up -d
```

Then complete the WordPress install wizard at `http://localhost:8080`
(any site title, admin username `admin`, a deliberately weak password such
as `password123`). Set **Settings → Permalinks** to "Post name" (required
for author-archive routing to resolve), and create 2-3 extra users with at
least one published post each (needed for their author archives to
redirect).

### 2. Install dependencies

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Hermes Agent is installed separately as an editable package (its full
dependency set conflicts on an unrelated Pillow version pin unrelated to
the toolsets this project uses, so only its core package is installed):

```bash
git clone https://github.com/NousResearch/hermes-agent.git
pip install -e ./hermes-agent --no-deps
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in:

```
OPENROUTER_API_KEY=your-openrouter-key-here   # free signup at openrouter.ai, no card required
TARGET_URL=http://localhost:8080
```

### 4. Run

```bash
python cli.py --target http://localhost:8080
```

Also configurable via the `TARGET_URL` environment variable instead of
`--target`. Output is printed to the console and written as structured
JSON to `results.json`.

## How this was tested

- Each enumeration/brute-force module was run standalone against the real
  local WordPress instance described above before being wired into the
  agent, to separate "is the enumeration logic correct" from "is the agent
  calling things correctly."
- `tests/` contains automated unit tests using mocked HTTP responses
  (`pytest tests/ -v`), covering the REST API technique's success and
  failure paths and the author-archive redirect-parsing logic.
- The full pipeline was run end-to-end against the local Docker WordPress
  instance, confirming real username discovery via the REST API and a
  successful brute-force against the seeded weak admin password.

## Limitations and trade-offs

- The brute-force password list is intentionally small (10 common
  passwords) and rate-limited with a 1-second delay between attempts —
  appropriate for a demo/authorized test, not an exhaustive real-world
  list.
- Author-archive enumeration assumes pretty permalinks ("Post name"
  structure) are enabled; with plain permalinks, the redirect this
  technique relies on does not occur.
- The REST API technique won't find anything on a site that has
  deliberately restricted the `/wp-json/wp/v2/users` endpoint (common via
  security plugins) — the tool falls back to author-archive enumeration in
  that case, but no further fallback (e.g. login-error-based enumeration)
  is currently wired into the automatic flow; `enum_login_error.py` exists
  but is available as a standalone module rather than part of the default
  orchestrated run.
- Uses a free-tier LLM via OpenRouter's `openrouter/free` router rather
  than a specific named model, so response quality/consistency for the
  planning and summary steps is not guaranteed to match a paid frontier
  model.
- Only tested against a single, intentionally vulnerable, self-hosted
  WordPress instance, per the assignment's ethical requirements — never
  run against production or unauthorized targets.