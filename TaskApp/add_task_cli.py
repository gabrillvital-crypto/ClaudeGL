"""
CLI usado pelo Claude para adicionar tarefas ao app de gestão.

Uso:
    python add_task_cli.py --tab profissional --title "Texto da tarefa" --priority alta --notes "Observação opcional"

Parâmetros:
    --tab        pessoal | profissional   (padrão: profissional)
    --title      Título da tarefa (obrigatório)
    --priority   alta | media | baixa     (padrão: media)
    --notes      Observação/contexto      (opcional)
"""

import argparse
import sqlite3
import os
import sys
import io
from datetime import datetime

# Fix Windows console encoding for special characters (UTF-8 throughout)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "tasks.db")


def _ensure_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            tab             TEXT    NOT NULL,
            title           TEXT    NOT NULL,
            notes           TEXT    DEFAULT '',
            priority        TEXT    NOT NULL DEFAULT 'media',
            status          TEXT    NOT NULL DEFAULT 'pending',
            attachment_path TEXT    DEFAULT NULL,
            attachment_name TEXT    DEFAULT NULL,
            created_at      TEXT    NOT NULL
        )
    """)
    conn.commit()
    return conn


def add_task(tab, title, notes, priority):
    conn = _ensure_db()
    conn.execute(
        "INSERT INTO tasks (tab,title,notes,priority,status,created_at) VALUES (?,?,?,?,?,?)",
        (tab, title.strip(), (notes or "").strip(), priority, "pending", datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def list_tasks(tab=None):
    conn = _ensure_db()
    if tab:
        rows = conn.execute(
            "SELECT id, tab, title, priority, status, created_at FROM tasks WHERE tab=? AND status='pending' ORDER BY CASE priority WHEN 'alta' THEN 0 WHEN 'media' THEN 1 ELSE 2 END",
            (tab,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, tab, title, priority, status, created_at FROM tasks WHERE status='pending' ORDER BY tab, CASE priority WHEN 'alta' THEN 0 WHEN 'media' THEN 1 ELSE 2 END"
        ).fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Adicionar tarefa ao app de gestão")
    parser.add_argument("--tab",      choices=["pessoal", "profissional"], default="profissional")
    parser.add_argument("--title",    default="", help="Título da tarefa")
    parser.add_argument("--priority", choices=["alta", "media", "baixa"], default="media")
    parser.add_argument("--notes",    default="", help="Observações opcionais")
    parser.add_argument("--list",     action="store_true", help="Listar tarefas pendentes")

    args = parser.parse_args()

    if not args.list and not args.title:
        parser.error("--title é obrigatório para adicionar uma tarefa.")

    if args.list:
        rows = list_tasks(None if args.tab == "profissional" else args.tab)
        if not rows:
            print("Nenhuma tarefa pendente.")
        else:
            for r in rows:
                print(f"[{r[3].upper():5}] [{r[1]}] {r[2]}")
    else:
        add_task(args.tab, args.title, args.notes, args.priority)
        label = "Profissional Efcaz" if args.tab == "profissional" else "Pessoal"
        print(f"Tarefa adicionada ao app.")
        print(f"  Aba:       {label}")
        print(f"  Prioridade: {args.priority.capitalize()}")
        print(f"  Título:    {args.title}")
        if args.notes:
            print(f"  Notas:     {args.notes}")
