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
create unique index if not exists survey_responses_respondent_name_key
  on public.survey_responses (respondent_name);

-- Allow anonymous insert (for the form) and read (for fetch script / dashboard)
alter table public.survey_responses enable row level security;

create policy "Allow anonymous insert"
  on public.survey_responses for insert
  to anon with check (true);

create policy "Allow anonymous select"
  on public.survey_responses for select
  to anon using (true);

-- Optional: allow update so resubmitting overwrites (handled in app by delete + insert or upsert)
-- Here we use unique index so duplicate names get a conflict; the form can send a single response per person.
