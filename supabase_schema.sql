-- Run this in the Supabase SQL Editor (Dashboard → SQL Editor) to create the table.

create table if not exists public.survey_responses (
  id uuid primary key default gen_random_uuid(),
  respondent_name text not null,
  prefer_6_strength int not null check (prefer_6_strength between 1 and 5),
  prefer_4_strength int not null check (prefer_4_strength between 1 and 5),
  top5_suitemates jsonb not null default '[]',
  conflicts jsonb not null default '[]',
  created_at timestamptz not null default now()
);

-- One response per person (latest wins if they submit again)
-- PostgREST upsert requires a UNIQUE constraint (not just index) for on_conflict
alter table public.survey_responses
  add constraint survey_responses_respondent_name_key unique (respondent_name);

-- Allow anonymous insert/update (for form + upsert) and read (for fetch script / dashboard)
alter table public.survey_responses enable row level security;

create policy "Allow anonymous insert"
  on public.survey_responses for insert
  to anon with check (true);

create policy "Allow anonymous select"
  on public.survey_responses for select
  to anon using (true);

-- Required for upsert: merge-duplicates does ON CONFLICT DO UPDATE
create policy "Allow anonymous update"
  on public.survey_responses for update
  to anon using (true) with check (true);

-- Optional: allow update so resubmitting overwrites (handled in app by delete + insert or upsert)
-- Here we use unique index so duplicate names get a conflict; the form can send a single response per person.
