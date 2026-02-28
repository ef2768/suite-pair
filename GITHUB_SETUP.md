# Connect this project to GitHub

**Your repo:** https://github.com/ef2768/suite-pair

## 1. Create the repo on GitHub (if you haven’t)

1. Go to **https://github.com/new**
2. **Repository name:** `suite-pair` (use a hyphen; GitHub will use it in the URL)
3. Choose **Public**
4. **Do not** check "Add a README" (you already have one)
5. Click **Create repository**

## 2. Push this folder to GitHub

**Option A — Run the script (easiest)**  
Double‑click **`push_to_github.bat`** in this folder.  
(You need [Git for Windows](https://git-scm.com/download/win) installed.)

**Option B — Run commands yourself**  
Open **Git Bash** or **Command Prompt** in this folder, then run:

```bash
cd "c:\Users\ethan\OneDrive\Documents\room selection"

git init
git add .
git commit -m "Initial commit: suite survey and grouping algorithm"
git branch -M main
git remote add origin https://github.com/ef2768/suite-pair.git
git push -u origin main
```

If Git asks for a password, use your GitHub username and a **Personal Access Token** as the password ([create one here](https://github.com/settings/tokens)), not your account password.

**If you created the repo with a space in the name** (“suite pair”), use this remote instead:  
`https://github.com/ef2768/suite%20pair.git`

## 3. Later: save and push changes

```powershell
cd "c:\Users\ethan\OneDrive\Documents\room selection"
git add .
git commit -m "Describe what you changed"
git push
```

---

## Optional: Host the survey with GitHub Pages

After the repo is on GitHub:

1. In the repo, go to **Settings → Pages**
2. Under **Source**, choose **Deploy from a branch**
3. Branch: **main**, folder: **/docs** (not root) → Save
4. Your survey will be at: **`https://ef2768.github.io/suite-pair/`**  
   (It may take a few minutes the first time.)

The survey form is in the **docs** folder (**docs/index.html**). Using **/docs** as the Pages source makes the site show the survey.
