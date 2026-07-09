-- Gestão Efcaz — Schema Supabase
-- Execute no SQL Editor do painel Supabase

CREATE TABLE IF NOT EXISTS clients (
  id         BIGSERIAL PRIMARY KEY,
  name       TEXT NOT NULL,
  tier       TEXT NOT NULL DEFAULT 'B',
  status_cs  TEXT DEFAULT '',
  notes_cs   TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS tasks (
  id              BIGSERIAL PRIMARY KEY,
  tab             TEXT NOT NULL,
  title           TEXT NOT NULL,
  description     TEXT DEFAULT '',
  notes           TEXT DEFAULT '',
  priority        TEXT NOT NULL DEFAULT 'media',
  status          TEXT NOT NULL DEFAULT 'pending',
  attachment_path TEXT,
  attachment_name TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at    TIMESTAMPTZ,
  deadline        DATE,
  client_id       BIGINT REFERENCES clients(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS checklist_items (
  id       BIGSERIAL PRIMARY KEY,
  task_id  BIGINT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  text     TEXT NOT NULL,
  is_done  BOOLEAN NOT NULL DEFAULT FALSE,
  position INTEGER NOT NULL DEFAULT 0
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_tasks_tab_status ON tasks(tab, status);
CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON tasks(deadline);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_checklist_task_id ON checklist_items(task_id);

-- Seed de clientes da carteira Efcaz
INSERT INTO clients (name, tier) VALUES
  ('Zurich', 'A'), ('CSU Digital', 'A'), ('Bom Futuro', 'A'),
  ('Eucatex', 'A'), ('Norskan', 'A'), ('Soluções Terceirizadas', 'A'),
  ('Unimed Brasil', 'A'),
  ('Afonso França', 'B'), ('DATA Engenharia', 'B'), ('Geistlich', 'B'),
  ('Vinci Airports', 'B'), ('Hospital Adventista', 'B'), ('Bunker One', 'B'),
  ('Dock Brasil', 'B'), ('Cielo', 'B'), ('Sabarã', 'B'),
  ('Agência Work On', 'B'), ('Tarkett', 'B'), ('Premier Pet', 'B'),
  ('FPF', 'B'), ('Transportes Cavalinho', 'B'), ('Pacco', 'B'),
  ('Engesp', 'B'), ('Cebrace', 'B'), ('BRG', 'B'), ('Ponsse', 'B'),
  ('Killing SA', 'B'),
  ('Unimed Campo Grande', 'C'), ('Asso Marítima', 'C'),
  ('Amboretto', 'C'), ('Unimed Dourados', 'C'),
  ('Alumetaf', 'C'), ('Advtec', 'C')
ON CONFLICT DO NOTHING;

-- RLS (Row Level Security) — desabilita para app pessoal sem auth
ALTER TABLE tasks DISABLE ROW LEVEL SECURITY;
ALTER TABLE checklist_items DISABLE ROW LEVEL SECURITY;
ALTER TABLE clients DISABLE ROW LEVEL SECURITY;
