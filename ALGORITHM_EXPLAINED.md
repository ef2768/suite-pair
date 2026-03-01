# How the algorithm finds the optimal pairing

## In one sentence

It tries **every possible** 6-person / 4-person split, throws out any that break “conflict” rules, scores the rest, and returns the **top 3** by total score.

---

## Step 1: Enumerate all possible splits

There are **210** ways to choose 6 people from 10 (the other 4 are the 4-person suite). The algorithm loops over all 210 and treats each as one candidate pairing.

So it’s **exhaustive search**: no heuristics, no randomness. Every valid split is considered.

---

## Step 2: Filter by conflicts (hard constraint)

For each candidate split, it checks:

- In the **6-person suite**: is anyone in the same suite as a person they listed in “Prefer NOT to be with”?
- In the **4-person suite**: same check.

If **either** suite has such a pair, that entire split is **invalid** and discarded. Conflicts are never allowed in the same suite.

---

## Step 3: Score each valid split

For every split that passes the conflict check, it computes **two scores**, then combines them into one number.

### 1. Preference score (top-5 suitemates)

- For each person, look at their **top 5** list.
- For each listed person who is **in the same suite** as them, add points: **5** for 1st choice, **4** for 2nd, **3** for 3rd, **2** for 4th, **1** for 5th.
- Sum over everyone in both suites.

**Higher** = more people are with suitemates they wanted.

### 2. Suite size score (6 vs 4 preference)

- Everyone has two slider values: **prefer 6-person** (1–5) and **prefer 4-person** (1–5).
- For each person in the **6-person suite**, add their “prefer 6” value.
- For each person in the **4-person suite**, add their “prefer 4” value.
- Sum those.

**Higher** = more people are in the suite size they preferred.

---

## Step 4: Combine into one total and rank

The total score is a **weighted sum** of the two parts:

```
total = (3.0 × preference_score) + (2.0 × suite_size_score)
```

So **top-5 preferences** matter more (weight 3) than **suite size preference** (weight 2). You can change these weights at the top of `grouping_algorithm.py` (`WEIGHT_PREFERENCE`, `WEIGHT_SUITE_SIZE`).

All valid splits are **sorted by this total** (highest first). The algorithm returns the **top 3** and writes them to the console and to **pairing_report.md**.

---

## Summary

| What | How |
|------|-----|
| **Search** | Exhaustive: all 210 possible 6/4 splits. |
| **Hard rule** | No split where two people who conflict are in the same suite. |
| **Scoring** | Preference (top-5 matches) + suite size match. |
| **“Optimal”** | The split with the **highest total score** among valid ones; you also get 2nd and 3rd best. |

So the “optimal” pairing is simply: **the valid split with the highest weighted score**, and the next two runners-up.
