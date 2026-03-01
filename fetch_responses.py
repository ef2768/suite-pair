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

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")

PEOPLE = [
    "Derek", "Michael", "Raiymbek", "Aryan", "Ethan",
    "Bill", "Kat", "Elson", "Luke", "Victor"
]


def fetch_via_rest():
    """Use requests to hit Supabase REST API (no supabase package needed)."""
    import urllib.request

    req = urllib.request.Request(
        SUPABASE_URL + "/rest/v1/survey_responses?select=*&order=created_at.desc",
        headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": "Bearer " + SUPABASE_ANON_KEY,
            "Accept": "application/json",
        },
        method="GET",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def main():
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("Set SUPABASE_URL and SUPABASE_ANON_KEY in your environment or .env file.")
        print("See SUPABASE_SETUP.md for instructions.")
        return

    print("Fetching responses from Supabase...")
    try:
        rows = fetch_via_rest()
    except Exception as e:
        print("Error fetching:", e)
        return

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


if __name__ == "__main__":
    main()
