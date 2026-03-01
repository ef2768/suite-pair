# Suite Mate Grouping

Splits **10 people** into one **6-person suite** and one **4-person suite** using survey data. The algorithm respects conflicts, top-5 suitemate preferences, suite size preference, and lifestyle compatibility.

## People

Derek, Michael, Raiymbek, Aryan, Ethan, Bill, Kat, Elson, Luke, Victor.

## Survey

1. **Send the survey** — Use `survey.md` (print or convert to Google Forms/Typeform). It collects:
   - **Suite size preference:** 6-person vs 4-person (strongly prefer / prefer / no preference).
   - **Top 5 suitemates:** Who they’d most like to be with (ranked 1–5).
   - **Conflicts:** People they do **not** want in the same suite (hard constraint).
   - **Lifestyle:** Sleep, noise, cleanliness, guests, social vs solo.

2. **Enter responses** — Fill `survey_responses_template.json` (or copy it to `survey_responses.json` and edit). For each person:
   - `suite_preference`: `"strongly_prefer_6"` | `"prefer_6"` | `"no_preference"` | `"prefer_4"` | `"strongly_prefer_4"`
   - `top5_suitemates`: list of up to 5 names (most preferred first).
   - `conflicts`: list of names they don’t want in the same suite (or one string: `"Name1, Name2"`).
   - `lifestyle`: object with `sleep`, `noise`, `cleanliness`, `guests`, `social` (use values from the template).

## Run the algorithm

**After you’ve collected responses:** see **HOW_TO_RUN_ALGORITHM.md** for merging responses and where to see the output.

```bash
python grouping_algorithm.py
```

By default it reads `survey_responses_template.json` and writes `pairing_report.md`. Use `survey_responses.json` (your merged file) once you have all 10 responses. To use your own file, edit the last two lines in `grouping_algorithm.py`:

```python
survey_file = Path(__file__).parent / "survey_responses.json"  # your file
report_file = Path(__file__).parent / "pairing_report.md"
run(str(survey_file), str(report_file))
```

Or call from code:

```python
from grouping_algorithm import run
top3 = run("survey_responses.json", "pairing_report.md")
# top3 is list of (suite_6_set, suite_4_set, total_score, breakdown)
```

## Output

- **Console:** Top 3 pairings with 6-person suite, 4-person suite, and score breakdown.
- **pairing_report.md:** Same top 3 with full justification (who got preferred suitemates, who got preferred suite size, lifestyle scores).

## How scoring works

1. **Conflicts:** Any pairing that puts two people who listed each other in “conflicts” in the same suite is **invalid** and discarded.
2. **Preference score:** For each person, if someone from their top-5 list is in their suite, they get points (rank 1 = 5 pts, rank 2 = 4 pts, …).
3. **Suite size score:** Points for being in the suite size they preferred (strong preference counts more).
4. **Lifestyle score:** Average compatibility between all pairs within each suite (sleep, noise, cleanliness, guests, social). Closer habits = higher score.

Weights (in `grouping_algorithm.py`): `WEIGHT_PREFERENCE = 3.0`, `WEIGHT_SUITE_SIZE = 2.0`, `WEIGHT_LIFESTYLE = 1.0`. You can change these to prioritize preferences vs lifestyle vs suite size.

## Files

| File | Purpose |
|------|--------|
| `survey.md` | Survey text for residents |
| `survey_responses_template.json` | Template + sample responses; copy and fill with real data |
| `grouping_algorithm.py` | Algorithm and scoring |
| `pairing_report.md` | Generated report (after running) |
| `README.md` | This file |
