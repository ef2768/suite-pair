# How to set up the survey database (Supabase)

When this is set up, every survey submission is saved automatically. You can view responses in Supabase and pull them into one file to run the grouping algorithm.

---

## Quick checklist

1. Create a Supabase project and copy your **Project URL** and **anon public** key.
2. In Supabase, run the SQL below to create the table.
3. In **docs/index.html**, paste your URL and key into the config at the top of the `<script>`.
4. Push your site (e.g. to GitHub Pages) so the survey uses the new config.
5. When you want to run the algorithm: set `SUPABASE_URL` and `SUPABASE_ANON_KEY` locally, run `python fetch_responses.py`, then run `python grouping_algorithm.py` (pointed at **survey_responses.json**).

---

## Step 1: Create a Supabase project

1. Go to **[supabase.com](https://supabase.com)** and sign in (or create a free account).
2. Click **New project**.
3. Choose an organization (or create one), give the project a name (e.g. `suite-survey`), set a **database password** (save it somewhere), pick a region, and click **Create new project**. Wait until the project is ready.
4. In the left sidebar, go to **Settings** (gear) → **API**.
5. Copy and save:
   - **Project URL** (e.g. `https://abcdefgh.supabase.co`)
   - **anon public** key (under “Project API keys” — the long string labeled `anon` `public`)

---

## Step 2: Create the table

1. In the Supabase dashboard left sidebar, open **SQL Editor**.
2. Click **New query**.
3. Paste this entire block and click **Run** (or press Ctrl+Enter):

```sql
create table if not exists public.survey_responses (
  id uuid primary key default gen_random_uuid(),
  respondent_name text not null,
  prefer_6_strength int not null check (prefer_6_strength between 1 and 5),
  prefer_4_strength int not null check (prefer_4_strength between 1 and 5),
  top5_suitemates jsonb not null default '[]',
  conflicts jsonb not null default '[]',
  created_at timestamptz not null default now()
);

create unique index if not exists survey_responses_respondent_name_key
  on public.survey_responses (respondent_name);

alter table public.survey_responses enable row level security;

create policy "Allow anonymous insert"
  on public.survey_responses for insert to anon with check (true);

create policy "Allow anonymous select"
  on public.survey_responses for select to anon using (true);
```

4. You should see “Success.” The table **survey_responses** is now created. You can confirm under **Table Editor** in the left sidebar.

---

## Step 3: Connect the survey to Supabase

1. Open **docs/index.html** in this project (in Cursor or any editor).
2. Find the `<script>` section and near the top you’ll see:
   ```javascript
   const SUPABASE_URL = '';
   const SUPABASE_ANON_KEY = '';
   ```
3. Between the quotes, paste your **Project URL** into `SUPABASE_URL` and your **anon public** key into `SUPABASE_ANON_KEY`. Example:
   ```javascript
   const SUPABASE_URL = 'https://abcdefgh.supabase.co';
   const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';
   ```
4. Save the file.
5. Push the updated **docs** folder to GitHub (or wherever you host the survey) so the live survey uses this config. After that, every submission will be saved to Supabase. You can watch new rows appear under **Table Editor** → **survey_responses**.

## Step 4: Get responses and run the algorithm

When you’re ready to run the grouping algorithm on the collected responses:

1. **Set your Supabase credentials** so the fetch script can read from the database. Use one of these:

   **Option A — .env file (recommended)**  
   In this project folder, create a file named **.env** (it’s in .gitignore so it won’t be committed). Put in it:
   ```
   SUPABASE_URL=https://abcdefgh.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
   Use your real Project URL and anon key. To load `.env` automatically, run once: `pip install python-dotenv`

   **Option B — Terminal (Windows PowerShell)**  
   Before running the script each time:
   ```powershell
   $env:SUPABASE_URL = "https://abcdefgh.supabase.co"
   $env:SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   ```
   (On Mac/Linux use `export SUPABASE_URL=...` and `export SUPABASE_ANON_KEY=...`.)

2. **Download all responses into one file:**
   ```powershell
   cd "c:\Users\ethan\OneDrive\Documents\room selection"
   python fetch_responses.py
   ```
   This creates/overwrites **survey_responses.json** in this folder with all rows from `survey_responses`.

3. **Point the algorithm at that file:**  
   Open **grouping_algorithm.py** and at the bottom change the input file to **survey_responses.json**:
   ```python
   survey_file = Path(__file__).parent / "survey_responses.json"
   report_file = Path(__file__).parent / "pairing_report.md"
   run(str(survey_file), str(report_file))
   ```
   Save the file.

4. **Run the algorithm:**
   ```powershell
   python grouping_algorithm.py
   ```
   Check the terminal and **pairing_report.md** for the top 3 pairings.

## Receiving answers automatically

- **In Supabase:** New submissions show up in **Table Editor** → **survey_responses** as soon as someone submits. You can refresh the page to see new rows.
- **Email (optional):** Supabase doesn’t email you by default. You can use [Supabase Database Webhooks](https://supabase.com/docs/guides/database/webhooks) to call an external service (e.g. Zapier, n8n) that sends you an email on new rows.
- **In your project:** Run `python fetch_responses.py` whenever you want to pull the latest responses into **survey_responses.json** and then run the algorithm.

## Security note

The **anon** key is meant to be public (it’s in your form). The schema allows anyone to **insert** and **select** from `survey_responses`. That’s fine for a small, private survey link. If you want to restrict who can submit or read, use Supabase Auth and RLS policies.
