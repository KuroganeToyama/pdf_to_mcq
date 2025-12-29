-- Database Schema for PDF to MCQ Web App
-- Run this in your Supabase SQL Editor

-- Drop existing tables (in reverse order of dependencies)
DROP TABLE IF EXISTS public.mcqs CASCADE;
DROP TABLE IF EXISTS public.mcq_sets CASCADE;
DROP TABLE IF EXISTS public.pdfs CASCADE;

-- Table: pdfs
create table public.pdfs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  title text not null,
  storage_path text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index on public.pdfs(user_id);

-- Table: mcq_sets
create table public.mcq_sets (
  id uuid primary key default gen_random_uuid(),
  pdf_id uuid not null references public.pdfs(id) on delete cascade,
  user_id uuid not null,
  model text not null,
  requested_count int not null check (requested_count between 1 and 500),
  status text not null check (status in ('queued','running','done','failed')),
  error text,
  created_at timestamptz not null default now(),
  completed_at timestamptz
);

-- Table: mcqs
create table public.mcqs (
  id uuid primary key default gen_random_uuid(),
  mcq_set_id uuid not null references public.mcq_sets(id) on delete cascade,
  idx int not null,
  question text not null,
  choice_a text not null,
  choice_b text not null,
  choice_c text not null,
  choice_d text not null,
  answer char(1) not null check (answer in ('A','B','C','D')),
  explanation text not null,
  difficulty text check (difficulty in ('easy','medium','hard')),
  bloom text,
  source_pages int[] not null default '{}',
  chunk_id text,
  fact_id text,
  flags text[] not null default '{}',
  created_at timestamptz not null default now(),
  unique(mcq_set_id, idx)
);
