"""
Suite Mate Grouping Algorithm
Splits 10 people into a 6-person and 4-person suite based on survey responses.
Considers: conflicts, top-5 preferences, suite size preference, lifestyle compatibility.
"""

import json
import itertools
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Union

# Suite size constants
SUITE_6 = 6
SUITE_4 = 4
TOTAL = 10

# Scoring weights (tune as needed)
WEIGHT_PREFERENCE = 3.0   # Top-5 suitemate matches (rank-weighted)
WEIGHT_SUITE_SIZE = 2.0   # Getting preferred 6 vs 4


@dataclass
class Person:
    name: str
    prefer_6_strength: int  # 1-5
    prefer_4_strength: int  # 1-5
    top5_suitemates: list[str]
    conflicts: list[str]
    lifestyle: dict  # sleep_time (0-5), hosting_comfort (1-5)


def _parse_conflicts(raw: Union[list, str]) -> list:
    """Accept conflicts as list of names or single comma-separated string."""
    if isinstance(raw, str):
        return [c.strip() for c in raw.split(",") if c.strip()]
    return [c.strip() for c in raw if c and isinstance(c, str)]


def _parse_suite_strengths(r: dict) -> tuple[int, int]:
    """Get (prefer_6_strength, prefer_4_strength) from response; support legacy suite_preference."""
    s6 = r.get("prefer_6_strength")
    s4 = r.get("prefer_4_strength")
    if s6 is not None and s4 is not None:
        return (int(s6), int(s4))
    # Legacy: map suite_preference to 1-5 strengths
    legacy = r.get("suite_preference", "no_preference")
    mapping = {
        "strongly_prefer_6": (5, 1),
        "prefer_6": (4, 2),
        "no_preference": (3, 3),
        "prefer_4": (2, 4),
        "strongly_prefer_4": (1, 5),
    }
    return mapping.get(legacy, (3, 3))


def load_survey_data(path: str) -> tuple[list[str], dict[str, Person]]:
    """Load survey JSON and return (people_list, name -> Person)."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    people = data["people"]
    responses = data["responses"]
    persons = {}
    for name, r in responses.items():
        s6, s4 = _parse_suite_strengths(r)
        persons[name] = Person(
            name=name,
            prefer_6_strength=s6,
            prefer_4_strength=s4,
            top5_suitemates=r.get("top5_suitemates", []),
            conflicts=_parse_conflicts(r.get("conflicts", [])),
            lifestyle=r.get("lifestyle", {}),
        )
    return people, persons


def violates_conflicts(group: set[str], persons: dict[str, Person]) -> bool:
    """True if any pair in group has a conflict."""
    for a in group:
        for b in group:
            if a != b and b in persons[a].conflicts:
                return True
    return False


def preference_score(group: set[str], persons: dict[str, Person]) -> float:
    """Score from top-5 suitemate preferences. Higher = more preferences satisfied."""
    total = 0.0
    for name in group:
        p = persons[name]
        for rank, preferred in enumerate(p.top5_suitemates):
            if preferred in group and preferred != name:
                # Rank 0 = 5 points, rank 1 = 4, ... rank 4 = 1
                total += (5 - rank)
    return total  # Each match counted once per person who listed them


def suite_preference_score(suite_6: set[str], suite_4: set[str], persons: dict[str, Person]) -> float:
    """Score from people getting their preferred suite size (prefer_6/prefer_4 strength 1-5)."""
    total = 0.0
    for name in suite_6:
        total += persons[name].prefer_6_strength
    for name in suite_4:
        total += persons[name].prefer_4_strength
    return total


def score_pairing(suite_6: set[str], suite_4: set[str], persons: dict[str, Person]) -> tuple[float, dict]:
    """
    Return (total_score, breakdown_dict) for a valid 6/4 split.
    """
    pref = preference_score(suite_6, persons) + preference_score(suite_4, persons)
    suite_pref = suite_preference_score(suite_6, suite_4, persons)

    total = WEIGHT_PREFERENCE * pref + WEIGHT_SUITE_SIZE * suite_pref
    breakdown = {
        "preference_score": round(pref, 2),
        "suite_size_score": round(suite_pref, 2),
        "total": round(total, 2),
    }
    return total, breakdown


def generate_justification(
    suite_6: set[str], suite_4: set[str], persons: dict[str, Person], breakdown: dict
) -> str:
    """Human-readable justification for this pairing."""
    lines = []

    # Who's in which suite
    lines.append("**6-person suite:** " + ", ".join(sorted(suite_6)))
    lines.append("**4-person suite:** " + ", ".join(sorted(suite_4)))
    lines.append("")

    # Preference fulfillment
    lines.append("**Preference fulfillment:**")
    for name in sorted(suite_6 | suite_4):
        group = suite_6 if name in suite_6 else suite_4
        matches = [p for p in persons[name].top5_suitemates if p in group and p != name]
        if matches:
            lines.append(f"  - {name} is with preferred suitemates: {', '.join(matches)}")
    lines.append("")

    # Suite size (prefer_6_strength vs prefer_4_strength)
    got_6 = [n for n in suite_6 if persons[n].prefer_6_strength >= persons[n].prefer_4_strength]
    got_4 = [n for n in suite_4 if persons[n].prefer_4_strength >= persons[n].prefer_6_strength]
    lines.append("**Suite size preference:**")
    if got_6:
        lines.append(f"  - In 6-person (prefer 6): {', '.join(got_6)}")
    if got_4:
        lines.append(f"  - In 4-person (prefer 4): {', '.join(got_4)}")
    lines.append("")

    # Scores
    lines.append("**Scores:**")
    lines.append(f"  - Top-5 preference score: {breakdown['preference_score']}")
    lines.append(f"  - Suite size preference score: {breakdown['suite_size_score']}")
    lines.append(f"  - **Total score: {breakdown['total']}**")

    return "\n".join(lines)


def run(survey_path: str, output_path: Optional[str] = None) -> list[tuple[set[str], set[str], float, dict]]:
    """
    Load survey, enumerate valid 6/4 splits, score them, return top 3.
    If output_path is set, also write a markdown report there.
    """
    people, persons = load_survey_data(survey_path)
    if set(people) != set(persons.keys()):
        raise ValueError("Survey people list and responses keys must match.")

    candidates = []
    for suite_6 in itertools.combinations(people, SUITE_6):
        suite_6_set = set(suite_6)
        suite_4_set = set(people) - suite_6_set
        if violates_conflicts(suite_6_set, persons) or violates_conflicts(suite_4_set, persons):
            continue
        total, breakdown = score_pairing(suite_6_set, suite_4_set, persons)
        candidates.append((suite_6_set, suite_4_set, total, breakdown))

    if not candidates:
        print("No valid pairings found (conflicts may make it impossible).")
        return []

    candidates.sort(key=lambda x: -x[2])
    top3 = candidates[:3]

    # Console output
    print("=" * 60)
    print("TOP 3 SUITE PAIRINGS")
    print("=" * 60)
    for i, (s6, s4, total, breakdown) in enumerate(top3, 1):
        print(f"\n--- Option {i} (score: {breakdown['total']}) ---")
        print("6-person suite:", ", ".join(sorted(s6)))
        print("4-person suite:", ", ".join(sorted(s4)))
        print("Breakdown:", breakdown)

    # Markdown report
    if output_path:
        report = ["# Suite Pairing Results: Top 3 Options\n"]
        for i, (s6, s4, total, breakdown) in enumerate(top3, 1):
            report.append(f"## Option {i} — Score: {breakdown['total']}\n")
            report.append(generate_justification(s6, s4, persons, breakdown))
            report.append("\n---\n")
        Path(output_path).write_text("\n".join(report), encoding="utf-8")
        print(f"\nReport written to {output_path}")

    return top3


if __name__ == "__main__":
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    base = Path(__file__).parent
    report_file = base / "pairing_report.md"

    # If Supabase is configured, fetch latest responses first (automates Step 4)
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_ANON_KEY"):
        try:
            import fetch_responses
            fetch_responses.main()
        except Exception as e:
            print("Supabase fetch failed:", e)
            print("Falling back to existing survey_responses.json or template.\n")

    # Use survey_responses.json if it exists, else template
    survey_file = base / "survey_responses.json"
    if not survey_file.exists():
        survey_file = base / "survey_responses_template.json"

    run(str(survey_file), str(report_file))
