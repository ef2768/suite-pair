"""
Suite Mate Grouping Algorithm
Splits 10 people into a 6-person and 4-person suite based on survey responses.
Considers: conflicts, top-5 preferences, suite size preference, lifestyle compatibility.
"""

import json
import itertools
import html
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


def anonymous_explanation(
    suite_6: set[str], suite_4: set[str], persons: dict[str, Person], breakdown: dict
) -> str:
    """
    Short, shareable explanation of why this option scores well, without naming individuals.
    Uses only aggregate counts so it can be shown to the whole group.
    """
    total_people = len(persons)

    def in_preferred_suite(name: str) -> bool:
        p = persons[name]
        return (name in suite_6 and p.prefer_6_strength >= p.prefer_4_strength) or (
            name in suite_4 and p.prefer_4_strength >= p.prefer_6_strength
        )

    def has_any_preferred_in_suite(name: str) -> bool:
        group = suite_6 if name in suite_6 else suite_4
        p = persons[name]
        return any(pref in group and pref != name for pref in p.top5_suitemates)

    preferred_count = sum(1 for n in persons if in_preferred_suite(n))
    with_pref_count = sum(1 for n in persons if has_any_preferred_in_suite(n))

    # Count mutual preference pairs that are kept together (A lists B and B lists A)
    mutual_pairs = 0
    names = sorted(persons.keys())
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            same_suite = (a in suite_6 and b in suite_6) or (a in suite_4 and b in suite_4)
            if not same_suite:
                continue
            if (
                b in persons[a].top5_suitemates
                and a in persons[b].top5_suitemates
            ):
                mutual_pairs += 1

    lines: list[str] = []
    lines.append(
        f"This option gives {preferred_count} out of {total_people} people their more preferred suite size."
    )
    lines.append(
        f"It also places {with_pref_count} out of {total_people} people with at least one of their top suitemate choices."
    )
    if mutual_pairs:
        lines.append(
            f"It keeps {mutual_pairs} mutual preference pair(s) together (pairs who ranked each other)."
        )
    lines.append(
        "Overall, higher scores favor options that respect more preferences and suite size priorities while still avoiding conflicts."
    )
    return " ".join(lines)


def generate_justification(
    suite_6: set[str], suite_4: set[str], persons: dict[str, Person], breakdown: dict
) -> str:
    """
    Human-readable justification for this pairing for the MARKDOWN REPORT.
    This version is intentionally anonymized (no individual names), so it is
    safe to share with the whole group.
    """
    lines = []

    # Anonymous, shareable explanation (no names)
    lines.append("**Why this option scores well (anonymous):**")
    lines.append(anonymous_explanation(suite_6, suite_4, persons, breakdown))
    lines.append("")

    # Overall scores (still anonymous)
    lines.append("**Scores driving this option:**")
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
    num_responses = len(persons)
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
    print(f"Survey responses recorded: {num_responses}")
    print("TOP 3 SUITE PAIRINGS")
    print("=" * 60)
    for i, (s6, s4, total, breakdown) in enumerate(top3, 1):
        print(f"\n--- Option {i} (score: {breakdown['total']}) ---")
        print("6-person suite:", ", ".join(sorted(s6)))
        print("4-person suite:", ", ".join(sorted(s4)))
        print("Breakdown:", breakdown)
        print("Explanation (anonymous):", anonymous_explanation(s6, s4, persons, breakdown))

    # Markdown report
    if output_path:
        report = [
            "# Suite Pairing Results: Top 3 Options\n",
            f"**Survey responses recorded:** {num_responses}\n",
        ]
        # HTML report (for sharing via devices / GitHub Pages)
        html_parts: list[str] = [
            "<!DOCTYPE html>",
            "<html lang=\"en\">",
            "<head>",
            "  <meta charset=\"utf-8\" />",
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />",
            "  <title>Suite Pairing Results</title>",
            "  <style>",
            "    :root {",
            "      --bg: #050816;",
            "      --bg-card: #0b1120;",
            "      --fg: #e5e7eb;",
            "      --accent: #22d3ee;",
            "      --muted: #9ca3af;",
            "    }",
            "    * { box-sizing: border-box; }",
            "    body {",
            "      margin: 0;",
            "      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;",
            "      background: radial-gradient(circle at top, #1e293b 0, #020617 45%, #000 100%);",
            "      color: var(--fg);",
            "    }",
            "    .container {",
            "      max-width: 800px;",
            "      margin: 0 auto;",
            "      padding: 24px 16px 32px;",
            "    }",
            "    h1 {",
            "      font-size: 1.8rem;",
            "      margin-bottom: 0.5rem;",
            "      text-align: center;",
            "    }",
            "    .subtitle {",
            "      text-align: center;",
            "      color: var(--muted);",
            "      margin-bottom: 1.5rem;",
            "      font-size: 0.95rem;",
            "    }",
            "    .option {",
            "      background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(15,23,42,0.8));",
            "      border-radius: 16px;",
            "      padding: 16px 18px 14px;",
            "      margin-bottom: 16px;",
            "      border: 1px solid rgba(148,163,184,0.25);",
            "      box-shadow: 0 18px 40px rgba(0,0,0,0.45);",
            "    }",
            "    .option h2 {",
            "      font-size: 1.2rem;",
            "      margin: 0 0 0.6rem;",
            "      color: var(--accent);",
            "    }",
            "    .pill-row {",
            "      display: flex;",
            "      flex-wrap: wrap;",
            "      gap: 6px;",
            "      margin: 0 0 0.75rem;",
            "      padding: 0;",
            "      list-style: none;",
            "    }",
            "    .pill-row li {",
            "      background: rgba(15,23,42,0.9);",
            "      border-radius: 999px;",
            "      padding: 4px 10px;",
            "      font-size: 0.78rem;",
            "      border: 1px solid rgba(148,163,184,0.45);",
            "    }",
            "    .section-label {",
            "      font-weight: 600;",
            "      font-size: 0.85rem;",
            "      margin-bottom: 0.25rem;",
            "      color: var(--muted);",
            "    }",
            "    .anon-text {",
            "      font-size: 0.9rem;",
            "      line-height: 1.45;",
            "      margin: 0.25rem 0 0.75rem;",
            "    }",
            "    .scores {",
            "      display: flex;",
            "      flex-wrap: wrap;",
            "      gap: 6px;",
            "      margin: 0;",
            "      padding: 0;",
            "      list-style: none;",
            "      font-size: 0.78rem;",
            "    }",
            "    .scores li {",
            "      background: rgba(15,23,42,0.9);",
            "      border-radius: 999px;",
            "      padding: 4px 10px;",
            "      border: 1px solid rgba(148,163,184,0.45);",
            "    }",
            "    .footer-note {",
            "      margin-top: 12px;",
            "      font-size: 0.78rem;",
            "      color: var(--muted);",
            "      text-align: center;",
            "    }",
            "  </style>",
            "</head>",
            "<body>",
            '  <main class="container">',
            "    <h1>Suite Pairing Results: Top 3 Options</h1>",
            f"    <p class=\"subtitle\">Survey responses recorded: {num_responses}</p>",
        ]

        for i, (s6, s4, total, breakdown) in enumerate(top3, 1):
            report.append(f"## Option {i} — Score: {breakdown['total']}\n")
            # Actual suite member list at the top
            report.append("**Suite composition:**")
            report.append(f"- 6-person suite: {', '.join(sorted(s6))}")
            report.append(f"- 4-person suite: {', '.join(sorted(s4))}")
            report.append("")
            # Anonymous, shareable explanation
            report.append(generate_justification(s6, s4, persons, breakdown))
            report.append("\n---\n")

            # Build HTML card for this option
            explanation = anonymous_explanation(s6, s4, persons, breakdown)
            s6_names = ", ".join(sorted(s6))
            s4_names = ", ".join(sorted(s4))
            html_parts.extend(
                [
                    '    <section class="option">',
                    f"      <h2>Option {i} — Score: {breakdown['total']}</h2>",
                    '      <div class="section-label">Suite composition</div>',
                    "      <ul class=\"pill-row\">",
                    f"        <li><strong>6-person:</strong> {html.escape(s6_names)}</li>",
                    f"        <li><strong>4-person:</strong> {html.escape(s4_names)}</li>",
                    "      </ul>",
                    '      <div class="section-label">Why this option scores well (anonymous)</div>',
                    f"      <p class=\"anon-text\">{html.escape(explanation)}</p>",
                    '      <div class="section-label">Scores</div>',
                    "      <ul class=\"scores\">",
                    f"        <li>Preference score: {breakdown['preference_score']}</li>",
                    f"        <li>Suite size score: {breakdown['suite_size_score']}</li>",
                    f"        <li>Total: {breakdown['total']}</li>",
                    "      </ul>",
                    "    </section>",
                ]
            )

        html_parts.extend(
            [
                '    <p class="footer-note">',
                "      Higher scores favour options that respect more preferences and suite size priorities while avoiding hard conflicts.",
                "    </p>",
                "  </main>",
                "</body>",
                "</html>",
            ]
        )

        Path(output_path).write_text("\n".join(report), encoding="utf-8")
        print(f"\nReport written to {output_path}")

        html_output_path = base / "docs" / "pairing_report.html"
        html_output_path.parent.mkdir(parents=True, exist_ok=True)
        html_output_path.write_text("\n".join(html_parts), encoding="utf-8")
        print(f"HTML report written to {html_output_path}")

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
    fetched = False
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_ANON_KEY"):
        try:
            import fetch_responses
            fetched = fetch_responses.main()
        except Exception as e:
            print("Supabase fetch failed:", e)

    # Use survey_responses.json if it exists, else template
    survey_file = base / "survey_responses.json"
    if not survey_file.exists():
        survey_file = base / "survey_responses_template.json"
    if not fetched and survey_file.exists():
        print(f"Using local data: {survey_file.name}\n")

    run(str(survey_file), str(report_file))
