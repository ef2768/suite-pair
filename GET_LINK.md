# How to get a shareable link for the survey

Send this link to Derek, Michael, Raiymbek, Aryan, Ethan, Bill, Kat, Elson, Luke, and Victor so they can fill out the survey on their phones or computers.

---

## Option 1: Netlify Drop (fastest, ~2 minutes)

1. Go to **https://app.netlify.com/drop**
2. Sign in with GitHub, email, or create a free account.
3. Create a **zip** of your survey page:
   - Put **only** `index.html` in a new folder (e.g. `survey-deploy`).
   - Right‑click the folder → **Compress** (Mac) or **Send to → Compressed folder** (Windows).
4. **Drag the zip file** onto the Netlify Drop page.
5. Netlify will give you a link like **`https://random-name-12345.netlify.app`**. That’s your survey link—send it to everyone.

People open the link, fill the form, then use **Copy to clipboard** or **Download .json** and send that response to you (e.g. in a group chat or email).

---

## Option 2: GitHub Pages (free, link doesn’t expire)

1. Create a **new repository** on GitHub (e.g. `suite-survey`).
2. Upload **`index.html`** to the root of that repo (no need for other files).
3. In the repo: **Settings → Pages**.
4. Under **Source**, choose **Deploy from a branch**.
5. Branch: **main** (or **master**), folder: **/ (root)**. Save.
6. After a minute or two, your survey will be at:
   **`https://YOUR_USERNAME.github.io/suite-survey/`**

Send that URL to the group.

---

## Option 3: Google Forms (instant link, manual data entry later)

1. Go to **https://forms.google.com** and create a new blank form.
2. Add questions to match the survey (your name = dropdown with the 10 names; suite preference = multiple choice; top 5 = 5 dropdowns; conflicts = short answer; lifestyle = multiple choice for each; notes = paragraph).
3. Click **Send** → copy the form link. Send that link to everyone.
4. Responses will appear in the **Responses** tab. You’ll need to copy the data into `survey_responses.json` by hand (or export to CSV and convert). The custom form (`index.html`) outputs JSON that matches the algorithm; Google Forms does not, so use Option 1 or 2 if you want to avoid manual entry.

---

## After everyone responds

Each person will send you a JSON snippet (or a `.json` file). Merge all 10 into one `survey_responses.json` file under a single `"responses"` object, using the structure in `survey_responses_template.json`. Then run:

```bash
python grouping_algorithm.py
```

(Update the script to use `survey_responses.json` instead of the template if needed.)
