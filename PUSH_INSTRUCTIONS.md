# How to push updates to GitHub

**Latest:** Suite preference is now two sliders (6-person and 4-person, 1–5). Lifestyle is sleep time + hosting comfort. Push to update the live survey. Do this in **Git Bash** or **Command Prompt** (in the project folder).

---

## Step 1: Open a terminal in this folder

- **Option A:** In File Explorer, go to `c:\Users\ethan\OneDrive\Documents\room selection`, then **right‑click** in the folder → **Open in Terminal** (or **Git Bash here** if you have it).
- **Option B:** Open **Command Prompt** or **Git Bash**, then run:
  ```bash
  cd "c:\Users\ethan\OneDrive\Documents\room selection"
  ```

---

## Step 2: Add, commit, and push

Copy and paste these commands **one at a time** (or all together):

```bash
git add docs/
git add .
git status
git commit -m "Add docs folder so GitHub Pages shows the survey"
git push
```

- **`git add docs/`** — stages the new docs folder (with the survey).
- **`git add .`** — stages any other changed files (e.g. NEXT_STEPS.md).
- **`git status`** — shows what will be committed (optional).
- **`git commit -m "..."`** — creates the commit.
- **`git push`** — sends it to GitHub.

If it asks for a username/password, use your GitHub username and a [Personal Access Token](https://github.com/settings/tokens) as the password.

---

## Step 3: Set GitHub Pages to use the docs folder

1. Go to **https://github.com/ef2768/suite-pair**
2. Click **Settings** → **Pages** (left sidebar).
3. Under **Build and deployment** → **Source**, choose **Deploy from a branch**.
4. **Branch:** `main`
5. **Folder:** select **/docs** (not “/ (root)”).
6. Click **Save**.

After a minute or two, **https://ef2768.github.io/suite-pair/** will show the survey.
