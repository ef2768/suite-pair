# How to see the algorithm output (after you collect responses)

## 1. Merge all 10 responses into one file

Each person’s submission is a single JSON object, e.g.:

```json
{
  "Derek": {
    "prefer_6_strength": 4,
    "prefer_4_strength": 2,
    "top5_suitemates": ["Ethan", "Michael", "Luke", "Aryan", "Bill"],
    "conflicts": []
  }
}
```

- Open **survey_responses_template.json** and keep the `"people"` array at the top.
- Under `"responses"`, paste each person’s block (the `"Name": { ... }` part) so you have all 10 names.
- Save as **survey_responses.json** in this folder.

## 2. Point the script at your file

At the **bottom** of **grouping_algorithm.py**, set the input file to your merged responses:

```python
survey_file = Path(__file__).parent / "survey_responses.json"   # use your file
report_file = Path(__file__).parent / "pairing_report.md"
run(str(survey_file), str(report_file))
```

(Replace `survey_responses_template.json` with `survey_responses.json` if that’s the name you used.)

## 3. Run the script

In a terminal, in this project folder:

```bash
cd "c:\Users\ethan\OneDrive\Documents\room selection"
python grouping_algorithm.py
```

## 4. Where to see the output

You get the results in two places:

| Where | What you see |
|-------|-------------------------------|
| **Terminal / console** | Top 3 pairings: who’s in the 6-person suite, who’s in the 4-person suite, and the score breakdown for each option. |
| **pairing_report.md** | Same top 3, with a short justification for each (who got preferred suitemates, who got their preferred suite size, and the scores). Open this file in any text editor or in Cursor. |

The script creates/overwrites **pairing_report.md** in the same folder as the script. Open that file to read the full write-up and share or compare the three options.
