# You've pushed to GitHub — what to do next

## 1. Turn on GitHub Pages (get your survey link)

1. Open your repo: **https://github.com/ef2768/suite-pair**
2. Click **Settings** (top menu of the repo).
3. In the left sidebar, click **Pages**.
4. Under **Build and deployment** → **Source**, choose **Deploy from a branch**.
5. Under **Branch**, pick **main**, folder **/ (root)**.
6. Click **Save**.

After a minute or two, your survey will be live at:

**https://ef2768.github.io/suite-pair/**

(If your repo name has a space, the URL will use `suite%20pair` instead of `suite-pair`.)

---

## 2. Send the link to everyone

Share **https://ef2768.github.io/suite-pair/** with:

Derek, Michael, Raiymbek, Aryan, Ethan, Bill, Kat, Elson, Luke, Victor.

Tell them:

- Open the link and fill out the form.
- When done, click **Copy to clipboard** (or **Download .json**).
- Send you the pasted text or the file (e.g. in a group chat or email).

---

## 3. When you have all 10 responses

Each response will look like:

```json
{
  "Derek": {
    "suite_preference": "prefer_6",
    "top5_suitemates": ["Ethan", "Michael", ...],
    "conflicts": [],
    "lifestyle": { "sleep": "normal", ... }
  }
}
```

1. Open **survey_responses_template.json** and copy its structure (the `"people"` list and the outer `"responses"` object).
2. Paste each person’s block into that **responses** object so you have all 10 names.
3. Save as **survey_responses.json** in this folder.

---

## 4. Run the grouping algorithm

1. Edit **grouping_algorithm.py**: near the bottom, change  
   `survey_responses_template.json`  
   to  
   `survey_responses.json`.
2. In a terminal in this folder, run:

   ```bash
   python grouping_algorithm.py
   ```

3. Check the console for the top 3 pairings and open **pairing_report.md** for the full write-up.

---

**Summary**

| Step | Action |
|------|--------|
| 1 | Repo **Settings → Pages** → Deploy from branch **main** |
| 2 | Share **https://ef2768.github.io/suite-pair/** |
| 3 | Merge all 10 JSON responses into **survey_responses.json** |
| 4 | Point the script at **survey_responses.json** and run it |
