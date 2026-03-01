"""
Fetch all survey responses from Supabase and write survey_responses.json
in the format expected by grouping_algorithm.py.

Uses env vars: SUPABASE_URL, SUPABASE_ANON_KEY (or create .env with these).
Optional: pip install python-dotenv to load .env automatically.
"""

import json
import os
from pathlib import Path

# Load .env if present (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://zphepmydpdpwjkrekga.supabase.co").rstrip("/")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpwaGVwbXlkcGRxd3prcmVrZ2FzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIzMjg4NDMsImV4cCI6MjA4NzkwNDg0M30.r523_F9uJldlM_1XQPdKiO42dLGINiBM5ACBhE5e6Cc")

PEOPLE = [
    "Derek", "Michael", "Raiymbek", "Aryan", "Ethan",
    "Bill", "Kat", "Elson", "Luke", "Victor"
]


def fetch_via_rest():
    """Use requests to hit Supabase REST API (no supabase package needed)."""
    import urllib.request
    import urllib.error

    url = SUPABASE_URL + "/rest/v1/survey_responses?select=*&order=created_at.desc"
    req = urllib.request.Request(
        url,
        headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": "Bearer " + SUPABASE_ANON_KEY,
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        try:
            err_json = json.loads(body) if body else {}
            msg = err_json.get("message", err_json.get("error_description", body))
        except json.JSONDecodeError:
            msg = body or str(e)
        raise RuntimeError(f"Supabase returned {e.code} {e.reason}: {msg}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}") from e

    if not isinstance(data, list):
        raise RuntimeError(f"Expected a list of rows from Supabase, got {type(data).__name__}: {data}")
    return data


def main():
    """Fetch from Supabase and write survey_responses.json. Returns True on success, False otherwise."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("Set SUPABASE_URL and SUPABASE_ANON_KEY in your environment or .env file.")
        print("See SUPABASE_SETUP.md for instructions.")
        return False

    print("Fetching responses from Supabase...")
    try:
        rows = fetch_via_rest()
    except Exception as e:
        print("Error fetching:", e)
        print("(Using existing survey_responses.json or template if present.)")
        return False

    # Build responses dict: one entry per person (latest if duplicates)
    responses = {}
    for row in rows:
        name = row.get("respondent_name")
        if not name or name in responses:
            continue
        responses[name] = {
            "prefer_6_strength": row.get("prefer_6_strength", 3),
            "prefer_4_strength": row.get("prefer_4_strength", 3),
            "top5_suitemates": row.get("top5_suitemates") or [],
            "conflicts": row.get("conflicts") or [],
        }

    out = {
        "people": PEOPLE,
        "responses": responses,
    }

    out_path = Path(__file__).parent / "survey_responses.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Saved {len(responses)} response(s) to {out_path.name}")
    if len(responses) < len(PEOPLE):
        missing = set(PEOPLE) - set(responses.keys())
        print(f"Still missing: {', '.join(sorted(missing))}")
    return True


if __name__ == "__main__":
    main()
