"""
Gestão de Tarefas — Efcaz CS  v2.0
Funcionalidades: checklist, descrição, voz PT-BR, relatório HTML
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import shutil
import os
import sys
import time
import threading
import tempfile
import webbrowser
import json
from datetime import datetime, timedelta
import calendar as _cal

# ── Dependências de voz (opcionais) ──────────────────────────────────────────
try:
    import sounddevice as sd
    import speech_recognition as sr
    import numpy as np
    VOICE_OK = True
except ImportError:
    VOICE_OK = False

# ── Dependência de IA (opcional) ──────────────────────────────────────────────
try:
    import anthropic as _anthropic
    AI_OK = True
except ImportError:
    AI_OK = False

# ── Caminhos ──────────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH    = os.path.join(APP_DIR, "tasks.db")
ATTACH_DIR  = os.path.join(APP_DIR, "attachments")
CONFIG_PATH = os.path.join(APP_DIR, "config.json")
os.makedirs(ATTACH_DIR, exist_ok=True)


def _load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_config(data):
    cfg = _load_config()
    cfg.update(data)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f)


def _get_auth():
    """
    Retorna kwargs para anthropic.Anthropic().
    Prioridade: env ANTHROPIC_API_KEY → config.json → credenciais do Claude Code.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY") or _load_config().get("api_key", "")
    if api_key:
        return {"api_key": api_key}
    # Tenta usar o token OAuth do Claude Code (não requer chave separada)
    creds_path = os.path.join(os.path.expanduser("~"), ".claude", ".credentials.json")
    if os.path.exists(creds_path):
        try:
            with open(creds_path, encoding="utf-8") as f:
                creds = json.load(f)
            token = creds.get("claudeAiOauth", {}).get("accessToken", "")
            if token:
                return {"auth_token": token}
        except Exception:
            pass
    return {}

# ── Helpers de data ───────────────────────────────────────────────────────────

def _fmt_deadline(iso_date):
    """YYYY-MM-DD → DD/MM/YYYY para exibição."""
    if not iso_date:
        return ""
    try:
        return datetime.strptime(iso_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return iso_date


def _parse_deadline(display_date):
    """DD/MM/YYYY ou YYYY-MM-DD → YYYY-MM-DD para o banco. Retorna None se vazio/inválido."""
    s = (display_date or "").strip()
    if not s:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


# ── Paleta ────────────────────────────────────────────────────────────────────
TEAL      = "#0E8FA3"
TEAL_DARK = "#0b7a8c"

PRIORITY = {
    "alta":  {"label": "Alta",  "color": "#DC2626", "light": "#FEE2E2"},
    "media": {"label": "Média", "color": "#D97706", "light": "#FEF3C7"},
    "baixa": {"label": "Baixa", "color": "#059669", "light": "#D1FAE5"},
}


# ══════════════════════════════════════════════════════════════════════════════
#  EXTRAÇÃO DE TAREFAS VIA IA
# ══════════════════════════════════════════════════════════════════════════════

_EXTRACT_PROMPT = """\
Você é um assistente de organização de tarefas. Analise o texto abaixo e extraia TODAS as tarefas acionáveis.

Retorne APENAS um JSON array válido com objetos contendo exatamente estes campos:
- "title": título conciso e acionável (máx 80 chars)
- "priority": "alta" | "media" | "baixa"
- "notes": horário, cliente ou contexto relevante (ou "" se não houver)
- "tab": "profissional" | "pessoal"

Sem texto antes ou depois do JSON. Se não houver tarefas, retorne [].

Critérios de prioridade:
- hoje / amanhã / horário específico → "alta"
- prazo em dias → "media"
- sem prazo → "baixa"

Critérios de aba:
- trabalho / cliente / empresa / reunião / projeto → "profissional"
- compras / família / saúde / casa → "pessoal"
- dúvida → usar o destino padrão: {default_tab}

Ignore saudações, agradecimentos e informações sem ação.

Texto:
{text}"""


_REFINE_PROMPT = """\
Você é um assistente que aprimora textos em português brasileiro.
Corrija erros gramaticais, ajuste a pontuação e reescreva de forma clara, profissional e direta — sem perder o sentido original.
Retorne APENAS o texto aprimorado, sem introdução, sem explicação, sem aspas adicionais.

Texto:
{text}"""


def refine_text_ai(raw_text):
    auth = _get_auth()
    if not auth:
        raise ValueError("Nenhuma credencial encontrada.")
    client = _anthropic.Anthropic(**auth)
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": _REFINE_PROMPT.format(text=raw_text)}],
    )
    return msg.content[0].text.strip()


def extract_tasks_ai(raw_text, default_tab="profissional"):
    auth = _get_auth()
    if not auth:
        raise ValueError("Nenhuma credencial encontrada. Configure ANTHROPIC_API_KEY ou faça login no Claude Code.")
    client = _anthropic.Anthropic(**auth)
    prompt = _EXTRACT_PROMPT.format(text=raw_text, default_tab=default_tab)
    msg    = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(
            ln for ln in raw.split("\n") if not ln.strip().startswith("```")
        ).strip()
    items = json.loads(raw)
    cleaned = []
    for t in items:
        if not isinstance(t, dict) or not t.get("title"):
            continue
        cleaned.append({
            "title":    str(t.get("title", ""))[:80],
            "priority": t.get("priority") if t.get("priority") in ("alta", "media", "baixa") else "media",
            "notes":    str(t.get("notes", "")),
            "tab":      t.get("tab") if t.get("tab") in ("profissional", "pessoal") else default_tab,
        })
    return cleaned


# ══════════════════════════════════════════════════════════════════════════════
#  BANCO DE DADOS
# ══════════════════════════════════════════════════════════════════════════════

def _db():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                tab             TEXT    NOT NULL,
                title           TEXT    NOT NULL,
                description     TEXT    DEFAULT '',
                notes           TEXT    DEFAULT '',
                priority        TEXT    NOT NULL DEFAULT 'media',
                status          TEXT    NOT NULL DEFAULT 'pending',
                attachment_path TEXT    DEFAULT NULL,
                attachment_name TEXT    DEFAULT NULL,
                created_at      TEXT    NOT NULL,
                completed_at    TEXT    DEFAULT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS checklist_items (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id  INTEGER NOT NULL,
                text     TEXT    NOT NULL,
                is_done  INTEGER NOT NULL DEFAULT 0,
                position INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                tier TEXT NOT NULL DEFAULT 'B'
            )
        """)
        # Migrações seguras para tabelas existentes
        for col, defval in [("description", "''"), ("completed_at", "NULL"), ("deadline", "NULL")]:
            try:
                db.execute(f"ALTER TABLE tasks ADD COLUMN {col} TEXT DEFAULT {defval}")
            except Exception:
                pass
        try:
            db.execute("ALTER TABLE tasks ADD COLUMN client_id INTEGER DEFAULT NULL")
        except Exception:
            pass
        for col, defval in [("status_cs", "''"), ("notes_cs", "''")]:
            try:
                db.execute(f"ALTER TABLE clients ADD COLUMN {col} TEXT DEFAULT {defval}")
            except Exception:
                pass
        # Pré-popula clientes da carteira se a tabela estiver vazia
        count = db.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
        if count == 0:
            _CLIENTS_SEED = [
                ("Zurich", "A"), ("CSU Digital", "A"), ("Bom Futuro", "A"),
                ("Eucatex", "A"), ("Norskan", "A"), ("Soluções Terceirizadas", "A"),
                ("Unimed Brasil", "A"),
                ("Afonso França", "B"), ("DATA Engenharia", "B"), ("Geistlich", "B"),
                ("Vinci Airports", "B"), ("Hospital Adventista", "B"), ("Bunker One", "B"),
                ("ISG", "B"), ("Dock Brasil", "B"), ("Cielo", "B"), ("Sabarã", "B"),
                ("Agência Work On", "B"), ("Tarkett", "B"), ("Premier Pet", "B"),
                ("FPF", "B"), ("Transportes Cavalinho", "B"), ("Pacco", "B"),
                ("Engesp", "B"), ("Cebrace", "B"), ("BRG", "B"), ("Ponsse", "B"),
                ("Killing SA", "B"),
                ("Unimed Campo Grande", "C"), ("Asso Marítima", "C"),
                ("Amboretto", "C"), ("Unimed Dourados", "C"),
                ("Alumetaf", "C"), ("Advtec", "C"),
            ]
            db.executemany("INSERT INTO clients (name, tier) VALUES (?, ?)", _CLIENTS_SEED)


# Clients ────────────────────────────────────────────────────────────────────

def db_get_clients():
    with _db() as db:
        return db.execute("SELECT * FROM clients ORDER BY tier, name").fetchall()


def db_add_client(name, tier="B"):
    with _db() as db:
        db.execute("INSERT INTO clients (name, tier) VALUES (?, ?)", (name, tier))


def db_delete_client(client_id):
    with _db() as db:
        db.execute("DELETE FROM clients WHERE id=?", (client_id,))


def db_update_client_notes(client_id, status_cs, notes_cs):
    with _db() as db:
        db.execute("UPDATE clients SET status_cs=?, notes_cs=? WHERE id=?",
                   (status_cs, notes_cs, client_id))


def db_get_client_stats():
    with _db() as db:
        clients = db.execute("SELECT * FROM clients ORDER BY tier, name").fetchall()
        result = []
        for c in clients:
            s = db.execute("""
                SELECT
                    SUM(CASE WHEN status='pending'     THEN 1 ELSE 0 END) AS pending,
                    SUM(CASE WHEN status='in_progress' THEN 1 ELSE 0 END) AS in_progress,
                    SUM(CASE WHEN status='done'        THEN 1 ELSE 0 END) AS done,
                    COUNT(*) AS total
                FROM tasks WHERE client_id=?
            """, (c["id"],)).fetchone()
            result.append((c, s))
        return result


# Tasks ─────────────────────────────────────────────────────────────────────

def total_count():
    with _db() as db:
        return db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]


def fetch_tasks(tab, show_done, prio_filter, client_id=None):
    status_c = "" if show_done else "AND status IN ('pending', 'in_progress')"
    prio_c   = "" if prio_filter == "todos" else f"AND priority = '{prio_filter}'"
    client_c = "" if client_id is None else "AND client_id = ?"
    sql = f"""
        SELECT * FROM tasks WHERE tab = ?
        {status_c} {prio_c} {client_c}
        ORDER BY
          CASE status   WHEN 'in_progress' THEN 0 WHEN 'pending' THEN 1 ELSE 2 END,
          CASE priority WHEN 'alta' THEN 0 WHEN 'media' THEN 1 ELSE 2 END,
          created_at ASC
    """
    with _db() as db:
        params = (tab, client_id) if client_id is not None else (tab,)
        return db.execute(sql, params).fetchall()


def fetch_tasks_in_progress():
    with _db() as db:
        return db.execute(
            "SELECT * FROM tasks WHERE status='in_progress' "
            "ORDER BY CASE priority WHEN 'alta' THEN 0 WHEN 'media' THEN 1 ELSE 2 END, created_at ASC"
        ).fetchall()


def fetch_done_tasks(prio_filter):
    prio_c = "" if prio_filter == "todos" else f"AND priority = '{prio_filter}'"
    sql = f"""
        SELECT * FROM tasks WHERE status = 'done'
        {prio_c}
        ORDER BY completed_at DESC, created_at DESC
    """
    with _db() as db:
        return db.execute(sql).fetchall()


def db_get_task(task_id):
    with _db() as db:
        return db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()


def db_add_task(tab, title, notes, priority, deadline=None):
    with _db() as db:
        db.execute(
            "INSERT INTO tasks (tab,title,description,notes,priority,status,created_at,deadline) VALUES (?,?,?,?,?,?,?,?)",
            (tab, title, "", notes or "", priority, "pending", datetime.now().isoformat(), deadline)
        )


def db_update_task(task_id, title, description, notes, priority, att_path, att_name, deadline=None, client_id=None):
    with _db() as db:
        db.execute(
            "UPDATE tasks SET title=?,description=?,notes=?,priority=?,attachment_path=?,attachment_name=?,deadline=?,client_id=? WHERE id=?",
            (title, description or "", notes or "", priority, att_path, att_name, deadline, client_id, task_id)
        )


def db_toggle(task_id, current_status):
    new = "done" if current_status == "pending" else "pending"
    cat = datetime.now().isoformat() if new == "done" else None
    with _db() as db:
        db.execute("UPDATE tasks SET status=?, completed_at=? WHERE id=?", (new, cat, task_id))


def db_complete(task_id):
    with _db() as db:
        db.execute("UPDATE tasks SET status='done', completed_at=? WHERE id=?",
                   (datetime.now().isoformat(), task_id))


def db_set_in_progress(task_id):
    with _db() as db:
        db.execute("UPDATE tasks SET status='in_progress', completed_at=NULL WHERE id=?", (task_id,))


def db_set_pending(task_id):
    with _db() as db:
        db.execute("UPDATE tasks SET status='pending', completed_at=NULL WHERE id=?", (task_id,))


def db_delete_task(task_id):
    with _db() as db:
        db.execute("DELETE FROM checklist_items WHERE task_id=?", (task_id,))
        db.execute("DELETE FROM tasks WHERE id=?", (task_id,))


# Checklist ─────────────────────────────────────────────────────────────────

def db_get_checklist(task_id):
    with _db() as db:
        return db.execute(
            "SELECT * FROM checklist_items WHERE task_id=? ORDER BY position, id", (task_id,)
        ).fetchall()


def db_add_checklist(task_id, text):
    with _db() as db:
        cur = db.execute(
            "INSERT INTO checklist_items (task_id,text,is_done,position) VALUES (?,?,0,"
            "(SELECT COALESCE(MAX(position),0)+1 FROM checklist_items WHERE task_id=?))",
            (task_id, text, task_id)
        )
        return cur.lastrowid


def db_toggle_checklist(item_id, is_done):
    with _db() as db:
        db.execute("UPDATE checklist_items SET is_done=? WHERE id=?", (1 if is_done else 0, item_id))


def db_delete_checklist(item_id):
    with _db() as db:
        db.execute("DELETE FROM checklist_items WHERE id=?", (item_id,))


def fetch_tasks_today():
    today = datetime.now().strftime("%Y-%m-%d")
    with _db() as db:
        return db.execute(
            "SELECT * FROM tasks WHERE status='pending' AND deadline=? "
            "ORDER BY CASE priority WHEN 'alta' THEN 0 WHEN 'media' THEN 1 ELSE 2 END",
            (today,)
        ).fetchall()


def fetch_tasks_overdue():
    today = datetime.now().strftime("%Y-%m-%d")
    with _db() as db:
        return db.execute(
            "SELECT * FROM tasks WHERE status='pending' AND deadline IS NOT NULL AND deadline < ? "
            "ORDER BY deadline ASC, CASE priority WHEN 'alta' THEN 0 WHEN 'media' THEN 1 ELSE 2 END",
            (today,)
        ).fetchall()


def fetch_tasks_for_date(iso_date):
    with _db() as db:
        return db.execute(
            "SELECT * FROM tasks WHERE deadline=? "
            "ORDER BY CASE status WHEN 'done' THEN 1 ELSE 0 END, "
            "CASE priority WHEN 'alta' THEN 0 WHEN 'media' THEN 1 ELSE 2 END",
            (iso_date,)
        ).fetchall()


def fetch_tasks_counts_for_month(year, month):
    prefix = f"{year:04d}-{month:02d}"
    with _db() as db:
        rows = db.execute(
            "SELECT deadline, COUNT(*) as cnt, "
            "SUM(CASE WHEN priority='alta' AND status!='done' THEN 1 ELSE 0 END) as alta "
            "FROM tasks WHERE deadline LIKE ? AND status!='done' GROUP BY deadline",
            (f"{prefix}-%",)
        ).fetchall()
    result = {}
    for r in rows:
        try:
            day = int(r["deadline"].split("-")[2])
            result[day] = (r["cnt"], r["alta"] or 0)
        except Exception:
            pass
    return result


# Relatório ─────────────────────────────────────────────────────────────────

def db_fetch_done(tab_filter, period_days):
    cutoff    = (datetime.now() - timedelta(days=period_days)).isoformat()
    tab_c     = "" if tab_filter == "todas" else f"AND tab = '{tab_filter}'"
    with _db() as db:
        tasks = db.execute(
            f"SELECT * FROM tasks WHERE status='done' AND completed_at >= ? {tab_c} ORDER BY tab, completed_at DESC",
            (cutoff,)
        ).fetchall()
        result = []
        for t in tasks:
            items = db.execute(
                "SELECT * FROM checklist_items WHERE task_id=? ORDER BY position, id", (t["id"],)
            ).fetchall()
            result.append((t, items))
        return result


def db_fetch_done_range(tab_filter, date_from_iso, date_to_iso):
    tab_c = "" if tab_filter == "todas" else f"AND tab = '{tab_filter}'"
    with _db() as db:
        tasks = db.execute(
            f"SELECT * FROM tasks WHERE status='done' "
            f"AND completed_at >= ? AND completed_at <= ? {tab_c} "
            f"ORDER BY tab, completed_at DESC",
            (date_from_iso, date_to_iso)
        ).fetchall()
        result = []
        for t in tasks:
            items = db.execute(
                "SELECT * FROM checklist_items WHERE task_id=? ORDER BY position, id",
                (t["id"],)
            ).fetchall()
            result.append((t, items))
        return result


# ══════════════════════════════════════════════════════════════════════════════
#  DETECÇÃO DE DISPOSITIVO DE ÁUDIO
# ══════════════════════════════════════════════════════════════════════════════

_AUDIO_DEVICE = None   # cache: (device_idx, rate, channels)

_OUTPUT_KEYWORDS = ("alto-falante", "speaker", "saída", "saida",
                    "output", "headphone", "mixagem", "stereo mix", "loopback")


def _detect_input_device():
    """Varre dispositivos de entrada, filtra saídas/loopback e retorna o primeiro
    que abre E entrega dados de áudio. Prefere WDM-KS > WASAPI > DirectSound > MME.
    Resultado é cacheado globalmente."""
    global _AUDIO_DEVICE
    if _AUDIO_DEVICE is not None:
        return _AUDIO_DEVICE

    devs = sd.query_devices()
    apis = sd.query_hostapis()
    API_PREF = {"Windows WDM-KS": 0, "Windows WASAPI": 1,
                "Windows DirectSound": 2, "MME": 3}

    candidates = []
    for i, d in enumerate(devs):
        if int(d["max_input_channels"]) < 1:
            continue
        name_lower = d["name"].lower()
        if any(kw in name_lower for kw in _OUTPUT_KEYWORDS):
            continue
        api_name = apis[d["hostapi"]]["name"]
        pref = API_PREF.get(api_name, 99)
        rate = int(d["default_samplerate"])
        ch   = min(int(d["max_input_channels"]), 2)
        candidates.append((pref, -rate, i, rate, ch))

    candidates.sort(key=lambda x: (x[0], x[1]))

    for _, _, idx, rate, ch in candidates:
        try:
            got = []
            def _cb(indata, f, t, s, _g=got): _g.append(True)
            st = sd.InputStream(device=idx, samplerate=rate, channels=ch,
                                dtype="int16", callback=_cb)
            st.start()
            deadline = time.time() + 0.25
            while time.time() < deadline and not got:
                time.sleep(0.02)
            st.stop()
            st.close()
            if got:
                _AUDIO_DEVICE = (idx, rate, ch)
                return _AUDIO_DEVICE
        except Exception:
            continue

    _AUDIO_DEVICE = (None, 44100, 2)   # fallback sem dispositivo confirmado
    return _AUDIO_DEVICE


# ══════════════════════════════════════════════════════════════════════════════
#  GRAVADOR DE VOZ
# ══════════════════════════════════════════════════════════════════════════════

class Recorder:
    def __init__(self):
        self._frames  = []
        self._active  = False
        self._stream  = None

    def start(self):
        global _AUDIO_DEVICE
        self._frames = []
        self._active = True
        try:
            idx, rate, ch = _detect_input_device()
            self._rate     = rate
            self._channels = ch
            self._stream   = sd.InputStream(
                device=idx, samplerate=rate, channels=ch,
                dtype="int16", callback=self._cb
            )
            self._stream.start()
        except ValueError:
            raise
        except Exception:
            # Cache pode estar apontando para dispositivo inválido — rescaneia uma vez
            _AUDIO_DEVICE = None
            try:
                idx, rate, ch = _detect_input_device()
                self._rate     = rate
                self._channels = ch
                self._stream   = sd.InputStream(
                    device=idx, samplerate=rate, channels=ch,
                    dtype="int16", callback=self._cb
                )
                self._stream.start()
            except Exception as e:
                self._active = False
                self._stream = None
                raise ValueError(f"Erro ao abrir microfone: {e}")

    def _cb(self, indata, frames, time_info, status):
        if self._active:
            self._frames.append(indata.tobytes())

    def stop_and_transcribe(self):
        self._active = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        raw = b"".join(self._frames)
        if not raw:
            raise ValueError("Nenhum áudio capturado. Verifique se o microfone está ativo.")
        # Converte estéreo → mono (Google SR requer mono)
        channels = getattr(self, "_channels", 1)
        if channels > 1:
            samples = np.frombuffer(raw, dtype=np.int16)
            raw = samples[::channels].copy().tobytes()
        rate = getattr(self, "_rate", 44100)
        recognizer = sr.Recognizer()
        audio = sr.AudioData(raw, rate, 2)
        try:
            return recognizer.recognize_google(audio, language="pt-BR")
        except sr.UnknownValueError:
            raise ValueError("Não foi possível entender o áudio. Fale mais devagar e claramente.")
        except sr.RequestError as e:
            raise ValueError(f"Serviço de voz indisponível (verifique a internet): {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  GRAVADOR STREAMING (chunks a cada 3s, transcrição em background)
# ══════════════════════════════════════════════════════════════════════════════

class StreamingRecorder:
    """Grava contínuo e transcreve em blocos de CHUNK_SECS segundos."""
    CHUNK_SECS = 3

    def __init__(self, on_text, on_error=None):
        self._on_text  = on_text    # callback(str)
        self._on_error = on_error   # callback(str)
        self._active   = False
        self._stream   = None
        self._frames   = []
        self._lock     = threading.Lock()
        self._timer    = None
        self._rate     = 44100
        self._channels = 1

    def start(self):
        global _AUDIO_DEVICE
        self._frames = []
        self._active = True
        idx, rate, ch = _detect_input_device()
        self._rate     = rate
        self._channels = ch
        try:
            self._stream = sd.InputStream(
                device=idx, samplerate=rate, channels=ch,
                dtype="int16", callback=self._cb
            )
            self._stream.start()
        except Exception:
            # Cache pode estar apontando para dispositivo inválido — rescaneia uma vez
            _AUDIO_DEVICE = None
            try:
                idx, rate, ch = _detect_input_device()
                self._rate     = rate
                self._channels = ch
                self._stream = sd.InputStream(
                    device=idx, samplerate=rate, channels=ch,
                    dtype="int16", callback=self._cb
                )
                self._stream.start()
            except Exception as e:
                self._active = False
                self._stream = None
                raise ValueError(f"Erro ao abrir microfone: {e}")
        self._schedule_chunk()

    def _cb(self, indata, frames, time_info, status):
        if self._active:
            with self._lock:
                self._frames.append(indata.tobytes())

    def _schedule_chunk(self):
        if self._active:
            t = threading.Timer(self.CHUNK_SECS, self._flush_chunk)
            t.daemon = True
            t.start()
            self._timer = t

    def _flush_chunk(self):
        if not self._active:
            return
        with self._lock:
            frames, self._frames = self._frames[:], []
        if frames:
            threading.Thread(target=self._transcribe, args=(frames,), daemon=True).start()
        self._schedule_chunk()

    def _transcribe(self, frames):
        raw = b"".join(frames)
        if not raw:
            return
        ch = self._channels
        if ch > 1:
            samples = np.frombuffer(raw, dtype=np.int16)
            raw = samples[::ch].copy().tobytes()
        try:
            rec   = sr.Recognizer()
            audio = sr.AudioData(raw, self._rate, 2)
            text  = rec.recognize_google(audio, language="pt-BR")
            if text and self._on_text:
                self._on_text(text)
        except sr.UnknownValueError:
            pass  # silêncio ou fala pouco clara — ignorar
        except sr.RequestError as e:
            if self._on_error:
                self._on_error(f"Serviço de voz indisponível: {e}")
        except Exception:
            pass

    def stop(self):
        self._active = False
        if self._timer:
            try:
                self._timer.cancel()
            except Exception:
                pass
            self._timer = None
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        with self._lock:
            frames, self._frames = self._frames[:], []
        if frames:
            threading.Thread(target=self._transcribe, args=(frames,), daemon=True).start()


# ══════════════════════════════════════════════════════════════════════════════
#  GERAÇÃO DE RELATÓRIO HTML
# ══════════════════════════════════════════════════════════════════════════════

_CSS = """
body{font-family:Calibri,Arial,sans-serif;margin:0;background:#f4f6f7;color:#333}
.hdr{background:#2D3748;color:#fff;padding:24px 40px}
.hdr h1{margin:0;font-size:24px}
.hdr p{margin:4px 0 0;opacity:.7;font-size:13px}
.body{padding:28px 40px}
.stats{display:flex;gap:16px;margin-bottom:28px}
.stat{background:#fff;border-radius:8px;padding:14px 22px;text-align:center;border-top:4px solid #718096;min-width:110px}
.stat .n{font-size:28px;font-weight:bold;color:#2D3748}
.stat .l{font-size:11px;color:#999;margin-top:2px}
.sec{font-size:12px;font-weight:bold;color:#aaa;text-transform:uppercase;letter-spacing:1px;
     margin:24px 0 10px;padding-bottom:6px;border-bottom:1px solid #e0e0e0}
.task{background:#fff;border-radius:8px;margin-bottom:8px;padding:14px 18px;border-left:4px solid #CBD5E0}
.task.alta{border-color:#4A5568}.task.media{border-color:#718096}.task.baixa{border-color:#A0AEC0}
.ttl{font-size:14px;font-weight:bold;margin-bottom:4px}
.desc,.note{font-size:12px;color:#666;margin-bottom:6px}
.note{font-style:italic}
.badge{display:inline-block;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:bold;
       color:#fff;margin-right:6px}
.alta{background:#4A5568}.media{background:#718096}.baixa{background:#A0AEC0}
ul.ck{list-style:none;padding:0;margin:6px 0 0}
ul.ck li{font-size:12px;color:#666;padding:2px 0}
ul.ck li.done{color:#4A5568}
ul.ck li.done::before{content:"☑  "}
ul.ck li.todo::before{content:"☐  "}
.meta{font-size:11px;color:#bbb;margin-top:8px}
.empty{text-align:center;color:#bbb;padding:50px;font-size:14px}
@media print{.hdr{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
"""


def generate_report_html(tab_filter, date_from, date_to, prev_count=None):
    tab_lbl = {"todas": "Todas as abas", "pessoal": "Pessoal", "profissional": "Profissional Efcaz"}

    from_iso = date_from.strftime("%Y-%m-%dT00:00:00")
    to_iso   = date_to.strftime("%Y-%m-%dT23:59:59")
    data     = db_fetch_done_range(tab_filter, from_iso, to_iso)

    now_str      = datetime.now().strftime("%d/%m/%Y às %H:%M")
    period_label = f"Relatório de Atividades: {date_from.strftime('%d/%m/%Y')} a {date_to.strftime('%d/%m/%Y')}"
    total        = len(data)
    n_alta       = sum(1 for t, _ in data if t["priority"] == "alta")
    n_prof       = sum(1 for t, _ in data if t["tab"] == "profissional")
    n_pes        = sum(1 for t, _ in data if t["tab"] == "pessoal")

    if prev_count is not None:
        diff = total - prev_count
        sign = "+" if diff >= 0 else ""
        arrow = "▲" if diff > 0 else ("▼" if diff < 0 else "─")
        comp_stat = (
            f'<div class="stat">'
            f'<div class="n">{arrow} {sign}{diff}</div>'
            f'<div class="l">vs período anterior<br>({prev_count} tarefas)</div>'
            f'</div>'
        )
    else:
        comp_stat = ""

    body = ""
    if not data:
        body = '<div class="empty">Nenhuma tarefa concluída no período selecionado.</div>'
    else:
        cur_tab = None
        for task, items in data:
            if task["tab"] != cur_tab:
                cur_tab   = task["tab"]
                sec_label = "Pessoal" if cur_tab == "pessoal" else "Profissional Efcaz"
                body += f'<div class="sec">{sec_label}</div>'

            p     = task["priority"]
            badge = f'<span class="badge {p}">{PRIORITY[p]["label"]}</span>'

            when = ""
            if task["completed_at"]:
                try:
                    dt   = datetime.fromisoformat(task["completed_at"])
                    when = f"Concluída em {dt.strftime('%d/%m/%Y às %H:%M')}"
                except Exception:
                    when = task["completed_at"] or ""

            desc = f'<div class="desc">{task["description"]}</div>' if task["description"] else ""
            note = f'<div class="note">{task["notes"]}</div>'        if task["notes"]       else ""

            ck = ""
            if items:
                ck = '<ul class="ck">'
                for it in items:
                    cls = "done" if it["is_done"] else "todo"
                    ck += f'<li class="{cls}">{it["text"]}</li>'
                ck += "</ul>"

            body += f"""
            <div class="task {p}">
              <div class="ttl">{badge}{task['title']}</div>
              {desc}{note}{ck}
              <div class="meta">{when}</div>
            </div>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="utf-8">
<title>Relatório — Efcaz CS</title>
<style>{_CSS}</style>
</head>
<body>
<div class="hdr">
  <h1>{period_label}</h1>
  <p>{tab_lbl.get(tab_filter, tab_filter)} &nbsp;·&nbsp; Gerado em {now_str}</p>
</div>
<div class="body">
  <div class="stats">
    <div class="stat"><div class="n">{total}</div><div class="l">Concluídas</div></div>
    <div class="stat"><div class="n">{n_alta}</div><div class="l">Prioridade Alta</div></div>
    <div class="stat"><div class="n">{n_prof}</div><div class="l">Profissional</div></div>
    <div class="stat"><div class="n">{n_pes}</div><div class="l">Pessoal</div></div>
    {comp_stat}
  </div>
  {body}
</div>
</body></html>"""


# ══════════════════════════════════════════════════════════════════════════════
#  DIÁLOGO — CALENDÁRIO / DATE PICKER
# ══════════════════════════════════════════════════════════════════════════════

class DatePickerDialog(ctk.CTkToplevel):
    _MONTHS = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
               "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    _DAYS   = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]

    def __init__(self, parent, initial_iso=None, on_select=None):
        super().__init__(parent)
        self.on_select = on_select
        self.title("Selecionar Data")
        self.geometry("308x330")
        self.resizable(False, False)
        self.after(100, self.lift)
        self.grab_set()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        today = datetime.now()
        self._today = (today.year, today.month, today.day)
        if initial_iso:
            try:
                d = datetime.strptime(initial_iso, "%Y-%m-%d")
                self._vy, self._vm = d.year, d.month
                self._sel = (d.year, d.month, d.day)
            except Exception:
                self._vy, self._vm = today.year, today.month
                self._sel = None
        else:
            self._vy, self._vm = today.year, today.month
            self._sel = None

        self._render()

    def _render(self):
        for w in self.winfo_children():
            w.destroy()

        # ── Cabeçalho com navegação de mês
        hdr = ctk.CTkFrame(self, fg_color=TEAL, corner_radius=0, height=44)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)
        hdr.grid_propagate(False)
        ctk.CTkButton(hdr, text="‹", width=44, height=44, corner_radius=0,
                      fg_color=TEAL, hover_color=TEAL_DARK, text_color="white",
                      font=ctk.CTkFont(size=18, weight="bold"),
                      command=self._prev).grid(row=0, column=0)
        ctk.CTkLabel(hdr, text=f"{self._MONTHS[self._vm-1]}  {self._vy}",
                     font=ctk.CTkFont(family="Calibri", size=13, weight="bold"),
                     text_color="white").grid(row=0, column=1)
        ctk.CTkButton(hdr, text="›", width=44, height=44, corner_radius=0,
                      fg_color=TEAL, hover_color=TEAL_DARK, text_color="white",
                      font=ctk.CTkFont(size=18, weight="bold"),
                      command=self._next).grid(row=0, column=2)

        # ── Linha de dias da semana
        wk = ctk.CTkFrame(self, fg_color="#e8f4f6", corner_radius=0, height=28)
        wk.grid(row=1, column=0, sticky="ew")
        wk.grid_propagate(False)
        for i, d in enumerate(self._DAYS):
            ctk.CTkLabel(wk, text=d, width=40, height=28,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color="#555").grid(row=0, column=i)

        # ── Grade de dias
        grid_f = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        grid_f.grid(row=2, column=0, sticky="nsew", padx=4, pady=4)

        weeks = _cal.monthcalendar(self._vy, self._vm)
        for r, week in enumerate(weeks):
            for c, day in enumerate(week):
                if day == 0:
                    ctk.CTkLabel(grid_f, text="", width=40, height=36).grid(row=r, column=c)
                    continue
                is_sel   = self._sel == (self._vy, self._vm, day)
                is_today = self._today == (self._vy, self._vm, day)
                if is_sel:
                    fg, tc, bw = TEAL, "white", 0
                elif is_today:
                    fg, tc, bw = "#e0f7fa", TEAL, 2
                else:
                    fg, tc, bw = "#f9f9f9", "#333", 0
                ctk.CTkButton(
                    grid_f, text=str(day), width=40, height=36,
                    fg_color=fg, hover_color=TEAL_DARK if is_sel else "#cceef3",
                    text_color=tc, corner_radius=4, border_width=bw, border_color=TEAL,
                    font=ctk.CTkFont(size=12, weight="bold" if (is_today or is_sel) else "normal"),
                    command=lambda d=day: self._pick(d)
                ).grid(row=r, column=c, padx=1, pady=1)

        # ── Rodapé
        ftr = ctk.CTkFrame(self, fg_color="#fafafa", corner_radius=0, height=38)
        ftr.grid(row=3, column=0, sticky="ew")
        ftr.grid_propagate(False)
        ctk.CTkFrame(ftr, fg_color="#e8e8e8", height=1).pack(fill="x", side="top")
        ctk.CTkButton(ftr, text="Sem prazo", height=30, width=120,
                      fg_color="#fee2e2", text_color="#dc2626", hover_color="#fecaca",
                      font=ctk.CTkFont(size=11), corner_radius=6,
                      command=self._clear).pack(side="left", padx=8, pady=4)
        ctk.CTkButton(ftr, text="Hoje", height=30, width=80,
                      fg_color="#e0f7fa", text_color=TEAL, hover_color="#cceef3",
                      font=ctk.CTkFont(size=11), corner_radius=6,
                      command=self._go_today).pack(side="right", padx=8, pady=4)

    def _prev(self):
        self._vm -= 1
        if self._vm < 1:
            self._vm = 12; self._vy -= 1
        self._render()

    def _next(self):
        self._vm += 1
        if self._vm > 12:
            self._vm = 1; self._vy += 1
        self._render()

    def _pick(self, day):
        iso = f"{self._vy:04d}-{self._vm:02d}-{day:02d}"
        if self.on_select:
            self.on_select(iso)
        self.destroy()

    def _clear(self):
        if self.on_select:
            self.on_select(None)
        self.destroy()

    def _go_today(self):
        y, m, d = self._today
        self._vy, self._vm = y, m
        self._sel = (y, m, d)
        iso = f"{y:04d}-{m:02d}-{d:02d}"
        if self.on_select:
            self.on_select(iso)
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  DIÁLOGO — RELATÓRIO
# ══════════════════════════════════════════════════════════════════════════════

class ReportDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gerar Relatório")
        self.geometry("460x370")
        self.resizable(False, False)
        self.after(100, self.lift)
        self.grab_set()

        today = datetime.now()
        # padrão: semana atual (segunda até hoje)
        monday = today - timedelta(days=today.weekday())
        self._date_from = monday.replace(hour=0,  minute=0,  second=0,  microsecond=0)
        self._date_to   = today.replace(hour=23, minute=59, second=59, microsecond=0)
        self.tab_v = tk.StringVar(value="todas")
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)

        # ── Atalhos rápidos ──────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Atalhos rápidos", anchor="w",
                     font=ctk.CTkFont(family="Calibri", size=12, weight="bold")
                     ).grid(row=0, column=0, padx=24, pady=(20, 6), sticky="w")
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.grid(row=1, column=0, padx=24, sticky="w")
        for lbl, fn in [("Esta Semana", self._set_week),
                        ("Últimos 15 dias", self._set_15),
                        ("Este Mês", self._set_month)]:
            ctk.CTkButton(sf, text=lbl, width=130, height=30,
                          fg_color="#e0f7fa", text_color=TEAL, hover_color="#cceef3",
                          font=ctk.CTkFont(family="Calibri", size=11),
                          corner_radius=6, command=fn).pack(side="left", padx=(0, 8))

        # ── Seletor personalizado ────────────────────────────────────────────
        ctk.CTkLabel(self, text="Período personalizado", anchor="w",
                     font=ctk.CTkFont(family="Calibri", size=12, weight="bold")
                     ).grid(row=2, column=0, padx=24, pady=(18, 6), sticky="w")
        df = ctk.CTkFrame(self, fg_color="transparent")
        df.grid(row=3, column=0, padx=24, sticky="w")

        ctk.CTkLabel(df, text="De", width=30,
                     font=ctk.CTkFont(size=12)).pack(side="left")
        self._btn_from = ctk.CTkButton(
            df, width=120, height=32, corner_radius=6,
            fg_color=TEAL, hover_color=TEAL_DARK, text_color="white",
            font=ctk.CTkFont(family="Calibri", size=12),
            command=self._pick_from)
        self._btn_from.pack(side="left", padx=(6, 20))

        ctk.CTkLabel(df, text="Até", width=30,
                     font=ctk.CTkFont(size=12)).pack(side="left")
        self._btn_to = ctk.CTkButton(
            df, width=120, height=32, corner_radius=6,
            fg_color=TEAL, hover_color=TEAL_DARK, text_color="white",
            font=ctk.CTkFont(family="Calibri", size=12),
            command=self._pick_to)
        self._btn_to.pack(side="left", padx=(6, 0))

        self._refresh_date_labels()

        # ── Aba ──────────────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Aba", anchor="w",
                     font=ctk.CTkFont(family="Calibri", size=12, weight="bold")
                     ).grid(row=4, column=0, padx=24, pady=(18, 6), sticky="w")
        tf = ctk.CTkFrame(self, fg_color="transparent")
        tf.grid(row=5, column=0, padx=24, sticky="w")
        for lbl, val in [("Todas", "todas"), ("Pessoal", "pessoal"), ("Profissional", "profissional")]:
            ctk.CTkRadioButton(tf, text=lbl, variable=self.tab_v, value=val,
                               font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 14))

        # ── Gerar ────────────────────────────────────────────────────────────
        ctk.CTkButton(self, text="Abrir Relatório no Navegador",
                      fg_color=TEAL, hover_color=TEAL_DARK, height=40,
                      font=ctk.CTkFont(family="Calibri", size=13, weight="bold"),
                      command=self._generate).grid(row=6, column=0, padx=24, pady=22, sticky="ew")

    def _refresh_date_labels(self):
        self._btn_from.configure(text=self._date_from.strftime("%d/%m/%Y"))
        self._btn_to.configure(text=self._date_to.strftime("%d/%m/%Y"))

    def _set_week(self):
        today = datetime.now()
        self._date_from = (today - timedelta(days=today.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0)
        self._date_to   = today.replace(hour=23, minute=59, second=59, microsecond=0)
        self._refresh_date_labels()

    def _set_15(self):
        today = datetime.now()
        self._date_from = (today - timedelta(days=14)).replace(
            hour=0, minute=0, second=0, microsecond=0)
        self._date_to   = today.replace(hour=23, minute=59, second=59, microsecond=0)
        self._refresh_date_labels()

    def _set_month(self):
        today = datetime.now()
        self._date_from = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self._date_to   = today.replace(hour=23, minute=59, second=59, microsecond=0)
        self._refresh_date_labels()

    def _pick_from(self):
        DatePickerDialog(self, initial_iso=self._date_from.strftime("%Y-%m-%d"),
                         on_select=self._on_from_picked)

    def _on_from_picked(self, iso):
        if iso:
            self._date_from = datetime.strptime(iso, "%Y-%m-%d").replace(
                hour=0, minute=0, second=0)
            self._refresh_date_labels()

    def _pick_to(self):
        DatePickerDialog(self, initial_iso=self._date_to.strftime("%Y-%m-%d"),
                         on_select=self._on_to_picked)

    def _on_to_picked(self, iso):
        if iso:
            self._date_to = datetime.strptime(iso, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59)
            self._refresh_date_labels()

    def _generate(self):
        delta      = (self._date_to.date() - self._date_from.date()).days + 1
        prev_to    = self._date_from - timedelta(days=1)
        prev_from  = prev_to - timedelta(days=delta - 1)
        prev_data  = db_fetch_done_range(
            self.tab_v.get(),
            prev_from.strftime("%Y-%m-%dT00:00:00"),
            prev_to.strftime("%Y-%m-%dT23:59:59"),
        )
        html = generate_report_html(
            self.tab_v.get(), self._date_from, self._date_to,
            prev_count=len(prev_data)
        )
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html",
                                          dir=APP_DIR, prefix="relatorio_")
        tmp.write(html.encode("utf-8"))
        tmp.close()
        webbrowser.open(f"file:///{tmp.name.replace(chr(92), '/')}")
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  DIÁLOGO — REVISÃO DE TAREFAS EXTRAÍDAS
# ══════════════════════════════════════════════════════════════════════════════

class ReviewDialog(ctk.CTkToplevel):
    _PRIO_DISPLAY = {"alta": "Alta", "media": "Média", "baixa": "Baixa"}
    _PRIO_REVERSE = {"Alta": "alta", "Média": "media", "Baixa": "baixa"}

    def __init__(self, parent, tasks, on_confirm):
        super().__init__(parent)
        self.on_confirm = on_confirm
        self._rows      = []   # (checked_var, title_entry, prio_var, tab_val)

        n = len(tasks)
        self.title("Revisar Tarefas Extraídas")
        self.geometry("700x560")
        self.minsize(580, 400)
        self.after(100, self.lift)
        self.grab_set()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Header ──
        hdr = ctk.CTkFrame(self, fg_color=TEAL, corner_radius=0)
        hdr.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            hdr,
            text=f"✨  {n} tarefa{'s' if n != 1 else ''} identificada{'s' if n != 1 else ''}",
            font=ctk.CTkFont(family="Calibri", size=15, weight="bold"),
            text_color="white",
        ).pack(side="left", padx=20, pady=14)
        ctk.CTkLabel(
            hdr, text="Ajuste e confirme antes de salvar.",
            font=ctk.CTkFont(size=11), text_color="white",
        ).pack(side="left", padx=(4, 0))

        # ── Lista rolável ──
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="#f5f5f5", corner_radius=0)
        self._scroll.grid(row=1, column=0, sticky="nsew")
        self._scroll.grid_columnconfigure(0, weight=1)
        for task in tasks:
            self._add_row(task)

        # ── Footer ──
        ftr = ctk.CTkFrame(self, fg_color="#fff", corner_radius=0, height=60)
        ftr.grid(row=2, column=0, sticky="ew")
        ftr.pack_propagate(False)
        ctk.CTkFrame(ftr, fg_color="#e8e8e8", height=1).pack(fill="x", side="top")

        self.lbl_sel = ctk.CTkLabel(ftr, text="", font=ctk.CTkFont(size=11),
                                     text_color="#666")
        self.lbl_sel.pack(side="left", padx=20)
        ctk.CTkButton(ftr, text="Cancelar", width=100, height=36,
                      fg_color="#e5e5e5", text_color="#444", hover_color="#d5d5d5",
                      command=self.destroy).pack(side="right", padx=(0, 14), pady=12)
        ctk.CTkButton(ftr, text="Salvar tarefas ✓", width=160, height=36,
                      fg_color=TEAL, hover_color=TEAL_DARK,
                      font=ctk.CTkFont(weight="bold"),
                      command=self._confirm).pack(side="right", pady=12)

        self._update_count()

    def _add_row(self, task):
        row = ctk.CTkFrame(self._scroll, fg_color="#fff", corner_radius=6,
                           border_width=1, border_color="#e4e4e4")
        row.pack(fill="x", padx=10, pady=(0, 6))
        row.grid_columnconfigure(1, weight=1)

        checked = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(row, text="", variable=checked,
                        checkbox_width=18, checkbox_height=18, width=28,
                        command=self._update_count,
                        ).grid(row=0, column=0, padx=(10, 4), pady=10)

        ent = ctk.CTkEntry(row, height=32, font=ctk.CTkFont(family="Calibri", size=12))
        ent.insert(0, task.get("title", ""))
        ent.grid(row=0, column=1, padx=(0, 8), pady=10, sticky="ew")

        prio_raw  = task.get("priority", "media")
        prio_disp = self._PRIO_DISPLAY.get(prio_raw, "Média")
        prio_var  = tk.StringVar(value=prio_disp)
        ctk.CTkOptionMenu(row, values=["Alta", "Média", "Baixa"], variable=prio_var,
                          width=90, height=30, font=ctk.CTkFont(size=11),
                          ).grid(row=0, column=2, padx=(0, 8), pady=10)

        tab_val  = task.get("tab", "profissional")
        tab_lbl  = "Prof."  if tab_val == "profissional" else "Pessoal"
        tab_fg   = "#dbeafe" if tab_val == "profissional" else "#fce7f3"
        tab_txt  = "#1d4ed8" if tab_val == "profissional" else "#be185d"
        tb = ctk.CTkFrame(row, fg_color=tab_fg, corner_radius=4, width=54, height=26)
        tb.grid(row=0, column=3, padx=(0, 6), pady=10)
        tb.pack_propagate(False)
        ctk.CTkLabel(tb, text=tab_lbl,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=tab_txt).pack(expand=True)

        date_var = tk.StringVar(value="")
        btn_date = ctk.CTkButton(
            row, text="📅 Prazo", width=90, height=26,
            fg_color="#f0f0f0", text_color="#666", hover_color="#e0e0e0",
            font=ctk.CTkFont(size=10), corner_radius=6,
        )
        btn_date.configure(command=lambda b=btn_date, d=date_var: self._pick_date(b, d))
        btn_date.grid(row=0, column=4, padx=(0, 10), pady=10)

        notes = task.get("notes", "").strip()
        if notes:
            ctk.CTkLabel(row, text=f"  {notes}",
                         font=ctk.CTkFont(size=10), text_color="#aaa", anchor="w",
                         ).grid(row=1, column=1, columnspan=4,
                                padx=(0, 10), pady=(0, 8), sticky="w")

        self._rows.append((checked, ent, prio_var, tab_val, date_var))

    def _pick_date(self, btn, date_var):
        def _on_select(iso):
            if iso:
                date_var.set(iso)
                d = datetime.strptime(iso, "%Y-%m-%d")
                btn.configure(text=f"📅 {d.strftime('%d/%m')}",
                              text_color=TEAL, fg_color="#e0f7fa", hover_color="#cceef3")
            else:
                date_var.set("")
                btn.configure(text="📅 Prazo", text_color="#666",
                              fg_color="#f0f0f0", hover_color="#e0e0e0")
        DatePickerDialog(self, initial_iso=date_var.get() or None, on_select=_on_select)

    def _update_count(self):
        sel = sum(1 for v, *_ in self._rows if v.get())
        n   = len(self._rows)
        self.lbl_sel.configure(
            text=f"{sel} de {n} tarefa{'s' if n != 1 else ''} selecionada{'s' if sel != 1 else ''}"
        )

    def _confirm(self):
        to_save = []
        for checked, ent, prio_var, tab_val, date_var in self._rows:
            if not checked.get():
                continue
            title = ent.get().strip()
            if not title:
                continue
            prio     = self._PRIO_REVERSE.get(prio_var.get(), "media")
            deadline = date_var.get() or None
            to_save.append({"title": title, "priority": prio, "tab": tab_val, "deadline": deadline})
        if to_save:
            self.on_confirm(to_save)
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  DIÁLOGO — DETALHE / EDIÇÃO DA TAREFA
# ══════════════════════════════════════════════════════════════════════════════

class TaskDetailDialog(ctk.CTkToplevel):
    def __init__(self, parent, task_id, on_save):
        super().__init__(parent)
        self.task_id      = task_id
        self.on_save      = on_save
        self.stream_rec   = None   # StreamingRecorder, criado ao iniciar gravação
        self.is_recording = False
        self._ck_widgets  = []   # (item_id, var, frame)

        task = db_get_task(task_id)
        self.att_path     = task["attachment_path"]
        self.att_name     = task["attachment_name"]
        self.sel_priority = task["priority"]
        self.deadline_iso = task["deadline"]
        self.sel_client_id = task["client_id"]
        self._task         = task
        self._clients      = db_get_clients()
        self._client_name_to_id = {c["name"]: c["id"] for c in self._clients}

        self.title("Detalhe da Tarefa")
        self.geometry("700x720")
        self.minsize(620, 620)
        self.after(100, self.lift)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)

        self._build(task)
        self._load_checklist()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self, t):
        # ── Action bar (topo fixo com todas as ações)
        act = ctk.CTkFrame(self, fg_color=TEAL, corner_radius=0, height=52)
        act.grid(row=0, column=0, sticky="ew")
        act.grid_propagate(False)
        ctk.CTkButton(
            act, text="🗑 Excluir", width=100, height=36,
            fg_color="#b91c1c", text_color="white", hover_color="#991b1b",
            font=ctk.CTkFont(size=12), corner_radius=6,
            command=self._delete
        ).pack(side="left", padx=10, pady=8)
        ctk.CTkButton(
            act, text="Marcar Concluída ✓", width=175, height=36,
            fg_color="#059669", hover_color="#047857", text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"), corner_radius=6,
            command=self._complete
        ).pack(side="right", padx=(0, 12), pady=8)
        is_ip = t["status"] == "in_progress"
        self.btn_andamento = ctk.CTkButton(
            act,
            text="↩ Voltar" if is_ip else "▶ Em andamento",
            width=150, height=36,
            fg_color="#e5e5e5" if is_ip else "#b45309",
            text_color="#555" if is_ip else "white",
            hover_color="#d0d0d0" if is_ip else "#92400e",
            font=ctk.CTkFont(size=12), corner_radius=6,
            command=self._toggle_andamento
        )
        self.btn_andamento.pack(side="right", padx=(0, 8), pady=8)
        self._is_in_progress = is_ip
        ctk.CTkButton(
            act, text="Salvar", width=90, height=36,
            fg_color="white", text_color=TEAL, hover_color="#e0f7fa",
            font=ctk.CTkFont(size=12, weight="bold"), corner_radius=6,
            command=self._save
        ).pack(side="right", padx=(0, 8), pady=8)
        ctk.CTkButton(
            act, text="Cancelar", width=90, height=36,
            fg_color=TEAL_DARK, text_color="white", hover_color="#0a6675",
            font=ctk.CTkFont(size=12), corner_radius=6,
            command=self._on_close
        ).pack(side="right", padx=(0, 8), pady=8)

        # ── Título
        ctk.CTkLabel(self, text="Título", anchor="w",
                     font=ctk.CTkFont(family="Calibri", size=12, weight="bold")
                     ).grid(row=1, column=0, padx=24, pady=(20, 4), sticky="w")
        self.ent_title = ctk.CTkEntry(self, height=36,
                                      font=ctk.CTkFont(family="Calibri", size=13))
        self.ent_title.insert(0, t["title"])
        self.ent_title.grid(row=2, column=0, padx=24, sticky="ew")

        # ── Prioridade
        pf = ctk.CTkFrame(self, fg_color="transparent")
        pf.grid(row=3, column=0, padx=24, pady=(12, 0), sticky="w")
        ctk.CTkLabel(pf, text="Prioridade:",
                     font=ctk.CTkFont(family="Calibri", size=12, weight="bold")
                     ).pack(side="left", padx=(0, 10))
        self.prio_btns = {}
        for p in ["alta", "media", "baixa"]:
            b = ctk.CTkButton(pf, text=PRIORITY[p]["label"], width=88, height=30, corner_radius=6,
                              command=lambda p=p: self._sel_prio(p))
            b.pack(side="left", padx=(0, 8))
            self.prio_btns[p] = b
        self._sel_prio(t["priority"])

        # ── Deadline
        dl_hdr = ctk.CTkFrame(self, fg_color="transparent")
        dl_hdr.grid(row=4, column=0, padx=24, pady=(12, 0), sticky="w")
        ctk.CTkLabel(dl_hdr, text="Data de Entrega:",
                     font=ctk.CTkFont(family="Calibri", size=12, weight="bold")
                     ).pack(side="left", padx=(0, 10))
        dl_text = f"📅  {_fmt_deadline(self.deadline_iso)}" if self.deadline_iso else "📅  Selecionar data"
        dl_fg   = "#d0f0f5" if self.deadline_iso else "#e5e5e5"
        dl_tc   = TEAL     if self.deadline_iso else "#555"
        self.btn_deadline = ctk.CTkButton(
            dl_hdr, text=dl_text, height=30, width=170,
            fg_color=dl_fg, text_color=dl_tc, hover_color="#cceef3" if self.deadline_iso else "#d5d5d5",
            font=ctk.CTkFont(family="Calibri", size=12), corner_radius=6,
            command=self._pick_date
        )
        self.btn_deadline.pack(side="left")

        # ── Cliente
        cl_hdr = ctk.CTkFrame(self, fg_color="transparent")
        cl_hdr.grid(row=5, column=0, padx=24, pady=(12, 0), sticky="w")
        ctk.CTkLabel(cl_hdr, text="Cliente:",
                     font=ctk.CTkFont(family="Calibri", size=12, weight="bold")
                     ).pack(side="left", padx=(0, 10))
        client_names = ["— Nenhum —"] + [c["name"] for c in self._clients]
        current_name = "— Nenhum —"
        if self.sel_client_id:
            for c in self._clients:
                if c["id"] == self.sel_client_id:
                    current_name = c["name"]
                    break
        self.client_var = tk.StringVar(value=current_name)
        ctk.CTkOptionMenu(
            cl_hdr, values=client_names, variable=self.client_var,
            width=220, height=30, font=ctk.CTkFont(family="Calibri", size=12),
            command=self._on_client_change
        ).pack(side="left")

        # ── Descrição + microfone + salvar nota
        desc_hdr = ctk.CTkFrame(self, fg_color="transparent")
        desc_hdr.grid(row=6, column=0, padx=24, pady=(14, 4), sticky="ew")
        desc_hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(desc_hdr, text="Descrição / O que foi feito", anchor="w",
                     font=ctk.CTkFont(family="Calibri", size=12, weight="bold")
                     ).grid(row=0, column=0, sticky="w")

        right_f = ctk.CTkFrame(desc_hdr, fg_color="transparent")
        right_f.grid(row=0, column=1, sticky="e")

        self.lbl_toast = ctk.CTkLabel(right_f, text="", font=ctk.CTkFont(size=11),
                                      text_color="#059669")
        self.lbl_toast.pack(side="left", padx=(0, 8))

        if VOICE_OK:
            self.lbl_voice = ctk.CTkLabel(right_f, text="", font=ctk.CTkFont(size=11),
                                          text_color="#0E8FA3")
            self.lbl_voice.pack(side="left", padx=(0, 6))
            self.btn_mic = ctk.CTkButton(
                right_f, text="🎤 Gravar", width=100, height=28,
                fg_color="#e5e5e5", text_color="#444", hover_color="#d0d0d0",
                font=ctk.CTkFont(size=11), corner_radius=6,
                command=self._toggle_voice
            )
            self.btn_mic.pack(side="left", padx=(0, 8))
        else:
            ctk.CTkLabel(right_f, text="(voz indisponível)",
                         font=ctk.CTkFont(size=10), text_color="#ccc"
                         ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            right_f, text="✓ Salvar nota", width=110, height=28,
            fg_color="#059669", hover_color="#047857", text_color="white",
            font=ctk.CTkFont(size=11, weight="bold"), corner_radius=6,
            command=self._save_desc
        ).pack(side="left")

        self.txt_desc = ctk.CTkTextbox(self, height=100, font=ctk.CTkFont(family="Calibri", size=12))
        self.txt_desc.insert("1.0", t["description"] or "")
        self.txt_desc.grid(row=7, column=0, padx=24, sticky="nsew")

        # ── Checklist
        ck_hdr = ctk.CTkFrame(self, fg_color="transparent")
        ck_hdr.grid(row=8, column=0, padx=24, pady=(14, 4), sticky="ew")
        ck_hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(ck_hdr, text="Checklist", anchor="w",
                     font=ctk.CTkFont(family="Calibri", size=12, weight="bold")
                     ).grid(row=0, column=0, sticky="w")

        add_f = ctk.CTkFrame(ck_hdr, fg_color="transparent")
        add_f.grid(row=0, column=1, sticky="e")
        self.ent_ck = ctk.CTkEntry(add_f, height=28, width=220,
                                   placeholder_text="Novo item...",
                                   font=ctk.CTkFont(family="Calibri", size=11))
        self.ent_ck.pack(side="left", padx=(0, 6))
        self.ent_ck.bind("<Return>", lambda e: self._add_ck_item())
        ctk.CTkButton(add_f, text="+ Adicionar", width=90, height=28,
                      fg_color=TEAL, hover_color=TEAL_DARK,
                      font=ctk.CTkFont(size=11), corner_radius=6,
                      command=self._add_ck_item).pack(side="left")

        self.ck_scroll = ctk.CTkScrollableFrame(self, height=130, fg_color="#fafafa",
                                                 corner_radius=6, border_width=1,
                                                 border_color="#e0e0e0")
        self.ck_scroll.grid(row=9, column=0, padx=24, sticky="ew")
        self.ck_scroll.grid_columnconfigure(0, weight=1)

        # ── Anexo
        att_f = ctk.CTkFrame(self, fg_color="transparent")
        att_f.grid(row=10, column=0, padx=24, pady=(12, 20), sticky="w")
        ctk.CTkButton(att_f, text="Anexar arquivo", width=120, height=28,
                      fg_color="#e5e5e5", text_color="#444", hover_color="#d5d5d5",
                      font=ctk.CTkFont(size=11),
                      command=self._pick_file).pack(side="left")
        self.lbl_att = ctk.CTkLabel(att_f,
                                    text=self._short(self.att_name) if self.att_name else "Nenhum arquivo",
                                    font=ctk.CTkFont(size=11), text_color="#888")
        self.lbl_att.pack(side="left", padx=10)
        self.btn_extract_pdf = ctk.CTkButton(
            att_f, text="📄 Extrair texto", width=120, height=28,
            fg_color="#e0f7fa", text_color=TEAL, hover_color="#cceef3",
            font=ctk.CTkFont(size=11), corner_radius=6,
            command=self._extract_pdf_text)
        if self.att_name and self.att_name.lower().endswith(".pdf"):
            self.btn_extract_pdf.pack(side="left", padx=(6, 0))

    # ── Cliente ───────────────────────────────────────────────────────────────

    def _on_client_change(self, name):
        self.sel_client_id = self._client_name_to_id.get(name)

    # ── Prioridade ────────────────────────────────────────────────────────────

    def _sel_prio(self, p):
        self.sel_priority = p
        for key, btn in self.prio_btns.items():
            if key == p:
                btn.configure(fg_color=PRIORITY[key]["color"], text_color="white")
            else:
                btn.configure(fg_color="#e5e5e5", text_color="#444")

    # ── Deadline ──────────────────────────────────────────────────────────────

    def _pick_date(self):
        DatePickerDialog(self, initial_iso=self.deadline_iso, on_select=self._set_deadline)

    def _set_deadline(self, iso):
        self.deadline_iso = iso
        if iso:
            self.btn_deadline.configure(
                text=f"📅  {_fmt_deadline(iso)}",
                fg_color="#d0f0f5", text_color=TEAL, hover_color="#cceef3"
            )
        else:
            self.btn_deadline.configure(
                text="📅  Selecionar data",
                fg_color="#e5e5e5", text_color="#555", hover_color="#d5d5d5"
            )

    # ── Checklist ─────────────────────────────────────────────────────────────

    def _load_checklist(self):
        for w in self.ck_scroll.winfo_children():
            w.destroy()
        self._ck_widgets.clear()
        items = db_get_checklist(self.task_id)
        if not items:
            ctk.CTkLabel(self.ck_scroll, text="Nenhum item ainda. Adicione acima.",
                         font=ctk.CTkFont(size=11), text_color="#bbb").pack(pady=10)
        for it in items:
            self._ck_row(it["id"], it["text"], bool(it["is_done"]))

    def _ck_row(self, item_id, text, is_done):
        row = ctk.CTkFrame(self.ck_scroll, fg_color="transparent")
        row.pack(fill="x", pady=2, padx=4)
        row.grid_columnconfigure(0, weight=1)

        var = tk.BooleanVar(value=is_done)
        chk = ctk.CTkCheckBox(
            row, text=text, variable=var,
            font=ctk.CTkFont(family="Calibri", size=12),
            checkbox_width=18, checkbox_height=18,
            command=lambda iid=item_id, v=var: db_toggle_checklist(iid, v.get())
        )
        chk.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            row, text="✕", width=24, height=24, corner_radius=4,
            fg_color="transparent", text_color="#ccc", hover_color="#fee2e2",
            command=lambda iid=item_id, r=row: self._del_ck(iid, r)
        ).grid(row=0, column=1, padx=(4, 0))

        self._ck_widgets.append((item_id, var, row))

    def _add_ck_item(self):
        text = self.ent_ck.get().strip()
        if not text:
            return
        item_id = db_add_checklist(self.task_id, text)
        # Remove "nenhum item" label if present
        for w in self.ck_scroll.winfo_children():
            if isinstance(w, ctk.CTkLabel):
                w.destroy()
        self._ck_row(item_id, text, False)
        self.ent_ck.delete(0, "end")

    def _del_ck(self, item_id, row_frame):
        db_delete_checklist(item_id)
        row_frame.destroy()
        # Se ficou vazio, mostra aviso
        remaining = [w for w in self.ck_scroll.winfo_children()
                     if isinstance(w, ctk.CTkFrame)]
        if not remaining:
            ctk.CTkLabel(self.ck_scroll, text="Nenhum item ainda. Adicione acima.",
                         font=ctk.CTkFont(size=11), text_color="#bbb").pack(pady=10)

    # ── Voz ───────────────────────────────────────────────────────────────────

    def _toggle_voice(self):
        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        self.is_recording = True
        self.btn_mic.configure(text="⏹ Parar", fg_color="#DC2626", text_color="white",
                               hover_color="#b91c1c")
        self.lbl_voice.configure(text="🔴 Gravando...", text_color="#DC2626")
        try:
            self.stream_rec = StreamingRecorder(
                on_text=self._stream_append,
                on_error=self._stream_error
            )
            self.stream_rec.start()
        except Exception as e:
            self.is_recording = False
            self.stream_rec = None
            self.btn_mic.configure(text="🎤 Gravar", fg_color="#e5e5e5",
                                   text_color="#444", hover_color="#d0d0d0")
            self.lbl_voice.configure(text=f"Erro mic: {e}", text_color="#DC2626")

    def _stop_recording(self):
        self.is_recording = False
        self.btn_mic.configure(text="🎤 Gravar", fg_color="#e5e5e5", text_color="#444",
                               hover_color="#d0d0d0")
        if self.stream_rec:
            self.stream_rec.stop()
            self.stream_rec = None
        self.lbl_voice.configure(text="✓ Pronto", text_color="#059669")
        self.after(2500, lambda: self.lbl_voice.configure(text="", text_color="#0E8FA3"))

    def _stream_append(self, text):
        def _do():
            try:
                current = self.txt_desc.get("1.0", "end-1c").strip()
                if current:
                    self.txt_desc.insert("end", " " + text)
                else:
                    self.txt_desc.insert("end", text)
            except Exception:
                pass
        try:
            self.after(0, _do)
        except Exception:
            pass

    def _stream_error(self, msg):
        def _do():
            try:
                self.lbl_voice.configure(text=f"⚠ {msg}", text_color="#DC2626")
                self.after(4000, lambda: self.lbl_voice.configure(text="", text_color="#0E8FA3"))
            except Exception:
                pass
        try:
            self.after(0, _do)
        except Exception:
            pass

    # ── Anexo ─────────────────────────────────────────────────────────────────

    def _extract_pdf_text(self):
        if not self.att_path or not os.path.exists(self.att_path):
            self._show_toast("⚠ Arquivo não encontrado", "#D97706")
            return
        try:
            import pdfplumber
            with pdfplumber.open(self.att_path) as pdf:
                n_pages = len(pdf.pages)
                parts = []
                for i, page in enumerate(pdf.pages, 1):
                    t = (page.extract_text() or "").strip()
                    if t:
                        parts.append(f"[Página {i}]\n{t}")
                texto = "\n\n".join(parts)
            if not texto.strip():
                self._show_toast("⚠ Nenhum texto detectado no PDF", "#D97706")
                return
            current = self.txt_desc.get("1.0", "end-1c").strip()
            self.txt_desc.insert("end", ("\n\n" if current else "") + texto)
            self._show_toast(f"✓ {n_pages} página(s) extraída(s)")
        except ImportError:
            self._show_toast("⚠ pdfplumber não instalado", "#D97706")
        except Exception as e:
            self._show_toast(f"Erro: {e}", "#DC2626")

    def _pick_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Documentos", "*.pdf *.xlsx *.xls *.csv *.png *.jpg *.jpeg *.docx *.pptx"),
                       ("Todos", "*.*")]
        )
        if not path:
            return
        fname = os.path.basename(path)
        dest  = os.path.join(ATTACH_DIR, fname)
        if os.path.exists(dest) and os.path.abspath(dest) != os.path.abspath(path):
            name, ext = os.path.splitext(fname)
            fname = f"{name}_{int(time.time())}{ext}"
            dest  = os.path.join(ATTACH_DIR, fname)
        shutil.copy2(path, dest)
        self.att_path = dest
        self.att_name = fname
        self.lbl_att.configure(text=self._short(fname), text_color="#444")
        if fname.lower().endswith(".pdf"):
            self.btn_extract_pdf.pack(side="left", padx=(6, 0))
        else:
            self.btn_extract_pdf.pack_forget()

    @staticmethod
    def _short(name):
        return name if not name or len(name) <= 38 else name[:35] + "..."

    # ── Salvar nota inline ────────────────────────────────────────────────────

    def _save_desc(self):
        desc = self.txt_desc.get("1.0", "end").strip()
        task = db_get_task(self.task_id)
        db_update_task(self.task_id, task["title"], desc, task["notes"] or "",
                       self.sel_priority, self.att_path, self.att_name,
                       self.deadline_iso, self.sel_client_id)
        self._show_toast("✓ Salvo")

    def _show_toast(self, msg, color="#059669"):
        self.lbl_toast.configure(text=msg, text_color=color)
        self.after(2500, lambda: self.lbl_toast.configure(text=""))

    # ── Ações finais ──────────────────────────────────────────────────────────

    def _save(self):
        title = self.ent_title.get().strip()
        if not title:
            messagebox.showwarning("Atenção", "O título é obrigatório.", parent=self)
            return
        desc = self.txt_desc.get("1.0", "end").strip()
        db_update_task(self.task_id, title, desc, "", self.sel_priority,
                       self.att_path, self.att_name, self.deadline_iso, self.sel_client_id)
        self.on_save()
        self.destroy()

    def _complete(self):
        title = self.ent_title.get().strip() or self._task["title"]
        desc  = self.txt_desc.get("1.0", "end").strip()
        db_update_task(self.task_id, title, desc, "", self.sel_priority,
                       self.att_path, self.att_name, self.deadline_iso, self.sel_client_id)
        db_complete(self.task_id)
        self.on_save()
        self.destroy()

    def _toggle_andamento(self):
        if self._is_in_progress:
            db_set_pending(self.task_id)
            self._is_in_progress = False
            self.btn_andamento.configure(
                text="▶ Em andamento", fg_color="#b45309",
                text_color="white", hover_color="#92400e")
        else:
            db_set_in_progress(self.task_id)
            self._is_in_progress = True
            self.btn_andamento.configure(
                text="↩ Voltar", fg_color="#e5e5e5",
                text_color="#555", hover_color="#d0d0d0")
        self.on_save()

    def _delete(self):
        if messagebox.askyesno("Confirmar", "Excluir esta tarefa permanentemente?", parent=self):
            db_delete_task(self.task_id)
            self.on_save()
            self.destroy()

    def _on_close(self):
        if self.stream_rec and self.is_recording:
            try:
                self.stream_rec.stop()
            except Exception:
                pass
        self.stream_rec = None
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  DIÁLOGO — NOVA TAREFA (entrada rápida)
# ══════════════════════════════════════════════════════════════════════════════

class AddTaskDialog(ctk.CTkToplevel):
    def __init__(self, parent, tab, on_save):
        super().__init__(parent)
        self.tab          = tab
        self.on_save      = on_save
        self.sel_priority = "media"
        self._deadline_iso = None

        label = "Pessoal" if tab == "pessoal" else "Profissional Efcaz"
        self.title(f"Nova Tarefa — {label}")
        self.geometry("480x380")
        self.resizable(False, False)
        self.after(100, self.lift)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Título da tarefa *", anchor="w",
                     font=ctk.CTkFont(family="Calibri", size=12, weight="bold")
                     ).grid(row=0, column=0, padx=24, pady=(24, 4), sticky="w")
        self.ent_title = ctk.CTkEntry(self, height=36,
                                      placeholder_text="Descreva a tarefa...",
                                      font=ctk.CTkFont(family="Calibri", size=13))
        self.ent_title.grid(row=1, column=0, padx=24, sticky="ew")
        self.ent_title.focus()
        self.ent_title.bind("<Return>", lambda e: self._save())

        ctk.CTkLabel(self, text="Prioridade *", anchor="w",
                     font=ctk.CTkFont(family="Calibri", size=12, weight="bold")
                     ).grid(row=2, column=0, padx=24, pady=(18, 6), sticky="w")
        pf = ctk.CTkFrame(self, fg_color="transparent")
        pf.grid(row=3, column=0, padx=24, sticky="w")
        self.prio_btns = {}
        for p in ["alta", "media", "baixa"]:
            b = ctk.CTkButton(pf, text=PRIORITY[p]["label"], width=100, height=34,
                              corner_radius=6, command=lambda p=p: self._sel_prio(p))
            b.pack(side="left", padx=(0, 10))
            self.prio_btns[p] = b
        self._sel_prio("media")

        # ── Deadline
        ctk.CTkLabel(self, text="Data de Entrega (opcional)", anchor="w",
                     font=ctk.CTkFont(family="Calibri", size=12, weight="bold")
                     ).grid(row=4, column=0, padx=24, pady=(18, 4), sticky="w")
        dl_f = ctk.CTkFrame(self, fg_color="transparent")
        dl_f.grid(row=5, column=0, padx=24, sticky="w")
        self.btn_deadline = ctk.CTkButton(
            dl_f, text="📅  Selecionar data", height=32, width=170,
            fg_color="#e5e5e5", text_color="#555", hover_color="#d5d5d5",
            font=ctk.CTkFont(family="Calibri", size=12), corner_radius=6,
            command=self._pick_date
        )
        self.btn_deadline.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(self, text="Dica: clique na tarefa criada para adicionar checklist e descrição.",
                     anchor="w", font=ctk.CTkFont(size=10), text_color="#aaa"
                     ).grid(row=6, column=0, padx=24, pady=(14, 0), sticky="w")

        bf = ctk.CTkFrame(self, fg_color="transparent")
        bf.grid(row=7, column=0, padx=24, pady=20, sticky="e")
        ctk.CTkButton(bf, text="Cancelar", width=100, height=36,
                      fg_color="#e5e5e5", text_color="#444", hover_color="#d5d5d5",
                      command=self.destroy).pack(side="left", padx=(0, 10))
        ctk.CTkButton(bf, text="Criar tarefa", width=120, height=36,
                      fg_color=TEAL, hover_color=TEAL_DARK,
                      command=self._save).pack(side="left")

    def _sel_prio(self, p):
        self.sel_priority = p
        for key, btn in self.prio_btns.items():
            if key == p:
                btn.configure(fg_color=PRIORITY[key]["color"], text_color="white")
            else:
                btn.configure(fg_color="#e5e5e5", text_color="#444")

    def _pick_date(self):
        DatePickerDialog(self, initial_iso=self._deadline_iso, on_select=self._set_deadline)

    def _set_deadline(self, iso):
        self._deadline_iso = iso
        if iso:
            self.btn_deadline.configure(
                text=f"📅  {_fmt_deadline(iso)}",
                fg_color="#d0f0f5", text_color=TEAL
            )
        else:
            self.btn_deadline.configure(
                text="📅  Selecionar data",
                fg_color="#e5e5e5", text_color="#555"
            )

    def _save(self):
        title = self.ent_title.get().strip()
        if not title:
            messagebox.showwarning("Atenção", "O título é obrigatório.", parent=self)
            return
        db_add_task(self.tab, title, "", self.sel_priority, self._deadline_iso)
        self.on_save()
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  JANELA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class TaskApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("Gestão Efcaz")
        self.geometry("1120x720")
        self.minsize(800, 520)

        self.current_tab    = "profissional"
        self.show_done      = False
        self.prio_filter    = "todos"
        self.client_filter_id = None
        self._db_count      = -1
        self._current_date  = datetime.now().strftime("%Y-%m-%d")
        self._cal_year      = datetime.now().year
        self._cal_month     = datetime.now().month
        self._cal_selected  = datetime.now().strftime("%Y-%m-%d")
        self.inbox_stream_rec = None   # StreamingRecorder, criado ao iniciar gravação
        self.inbox_is_recording = False

        self._build_ui()
        self._load()
        self._start_polling()
        if VOICE_OK:
            threading.Thread(target=_detect_input_device, daemon=True).start()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=TEAL, height=60, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="Gestão Efcaz",
                     font=ctk.CTkFont(family="Calibri", size=22, weight="bold"),
                     text_color="white").pack(side="left", padx=22)
        ctk.CTkButton(hdr, text="Relatório", width=110, height=32,
                      fg_color="white", text_color=TEAL,
                      hover_color="#e0f4f7", font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=6, command=self._open_report
                      ).pack(side="right", padx=18)

        # Tabs
        tbar = ctk.CTkFrame(self, fg_color="#ecf1f2", height=46, corner_radius=0)
        tbar.pack(fill="x")
        tbar.pack_propagate(False)
        self.btn_pes  = ctk.CTkButton(tbar, text="Pessoal", width=140, height=32,
                                       corner_radius=6,
                                       command=lambda: self._switch("pessoal"))
        self.btn_pes.pack(side="left", padx=(18, 6), pady=7)
        self.btn_prof = ctk.CTkButton(tbar, text="Profissional Efcaz", width=190, height=32,
                                       corner_radius=6,
                                       command=lambda: self._switch("profissional"))
        self.btn_prof.pack(side="left", padx=6, pady=7)
        ctk.CTkFrame(tbar, fg_color="#cdd8da", width=1, height=28).pack(
            side="left", padx=12, pady=9)
        self.btn_hoje = ctk.CTkButton(tbar, text="📅 Hoje", width=120, height=32,
                                       corner_radius=6,
                                       command=lambda: self._switch("hoje"))
        self.btn_hoje.pack(side="left", padx=(0, 6), pady=7)
        self.btn_atv = ctk.CTkButton(tbar, text="📋 Atividades", width=150, height=32,
                                      corner_radius=6,
                                      command=lambda: self._switch("atividades"))
        self.btn_atv.pack(side="left", padx=(0, 6), pady=7)
        self.btn_and = ctk.CTkButton(tbar, text="▶ Em andamento", width=165, height=32,
                                      corner_radius=6,
                                      command=lambda: self._switch("andamento"))
        self.btn_and.pack(side="left", padx=(0, 6), pady=7)
        self.btn_cal = ctk.CTkButton(tbar, text="📆 Calendário", width=140, height=32,
                                      corner_radius=6,
                                      command=lambda: self._switch("calendario"))
        self.btn_cal.pack(side="left", padx=(0, 6), pady=7)
        ctk.CTkFrame(tbar, fg_color="#cdd8da", width=1, height=28).pack(
            side="left", padx=12, pady=9)
        self.btn_inbox = ctk.CTkButton(tbar, text="📥 Entrada", width=130, height=32,
                                        corner_radius=6,
                                        command=lambda: self._switch("inbox"))
        self.btn_inbox.pack(side="left", padx=(0, 6), pady=7)
        self.btn_clientes = ctk.CTkButton(tbar, text="🏢 Clientes", width=130, height=32,
                                           corner_radius=6,
                                           command=lambda: self._switch("clientes"))
        self.btn_clientes.pack(side="left", padx=(0, 6), pady=7)

        # Filtros
        fbar = ctk.CTkFrame(self, fg_color="#fafafa", height=42, corner_radius=0)
        fbar.pack(fill="x")
        fbar.pack_propagate(False)
        ctk.CTkFrame(fbar, fg_color="#e4e4e4", height=1).pack(fill="x", side="bottom")

        ctk.CTkLabel(fbar, text="Filtrar:", font=ctk.CTkFont(size=11),
                     text_color="#888").pack(side="left", padx=(18, 10))
        self.fbtns = {}
        for key, lbl in [("todos", "Todos"), ("alta", "Alta"),
                         ("media", "Média"), ("baixa", "Baixa")]:
            b = ctk.CTkButton(fbar, text=lbl, width=72, height=26, corner_radius=4,
                              command=lambda k=key: self._set_filter(k))
            b.pack(side="left", padx=(0, 6))
            self.fbtns[key] = b

        ctk.CTkFrame(fbar, fg_color="#e4e4e4", width=1, height=20).pack(side="left", padx=8)
        ctk.CTkLabel(fbar, text="Cliente:", font=ctk.CTkFont(size=11),
                     text_color="#888").pack(side="left", padx=(0, 4))
        _all_clients = db_get_clients()
        self._client_names = ["Todos"] + [c["name"] for c in _all_clients]
        self._client_ids   = [None] + [c["id"] for c in _all_clients]
        self._client_var   = tk.StringVar(value="Todos")
        self.client_dropdown = ctk.CTkOptionMenu(
            fbar, values=self._client_names, variable=self._client_var,
            width=155, height=26, font=ctk.CTkFont(size=11),
            command=self._set_client_filter
        )
        self.client_dropdown.pack(side="left", padx=(0, 6))

        self.chk = ctk.CTkCheckBox(fbar, text="Mostrar concluídas",
                                   font=ctk.CTkFont(size=11),
                                   command=self._toggle_done)
        self.chk.pack(side="right", padx=18)

        # Lista
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="#f0f2f3", corner_radius=0)
        self.scroll.pack(fill="both", expand=True)
        self.scroll.grid_columnconfigure(0, weight=1)

        # Rodapé
        btm = ctk.CTkFrame(self, fg_color="#fff", height=58, corner_radius=0)
        btm.pack(fill="x", side="bottom")
        btm.pack_propagate(False)
        ctk.CTkFrame(btm, fg_color="#e8e8e8", height=1).pack(fill="x", side="top")
        ctk.CTkButton(btm, text="+ Nova Tarefa",
                      font=ctk.CTkFont(family="Calibri", size=14, weight="bold"),
                      fg_color=TEAL, hover_color=TEAL_DARK, height=38, width=190,
                      command=self._add_dialog).pack(side="left", padx=18, pady=10)
        self.lbl_count = ctk.CTkLabel(btm, text="",
                                       font=ctk.CTkFont(size=11), text_color="#999")
        self.lbl_count.pack(side="right", padx=18)

        self._update_tab_btns()
        self._update_filter_btns()

    # ── Estado ────────────────────────────────────────────────────────────────

    def _switch(self, tab):
        self.current_tab = tab
        self._update_tab_btns()
        self._load()

    def _set_filter(self, key):
        self.prio_filter = key
        self._update_filter_btns()
        self._load()

    def _set_client_filter(self, name):
        if name == "Todos":
            self.client_filter_id = None
        else:
            idx = self._client_names.index(name)
            self.client_filter_id = self._client_ids[idx]
        self._load()

    def _toggle_done(self):
        self.show_done = not self.show_done
        self._load()

    def _update_tab_btns(self):
        TAB_COLORS = {"atividades": "#059669", "inbox": "#7c3aed", "hoje": "#D97706",
                      "andamento": "#b45309", "clientes": "#1d4ed8", "calendario": TEAL}
        for tab, btn in [("pessoal", self.btn_pes), ("profissional", self.btn_prof),
                         ("hoje", self.btn_hoje), ("atividades", self.btn_atv),
                         ("andamento", self.btn_and), ("calendario", self.btn_cal),
                         ("inbox", self.btn_inbox), ("clientes", self.btn_clientes)]:
            if tab == self.current_tab:
                btn.configure(fg_color=TAB_COLORS.get(tab, TEAL), text_color="white")
            else:
                btn.configure(fg_color="#dde8ea", text_color="#444")

    def _update_filter_btns(self):
        for key, btn in self.fbtns.items():
            if key == self.prio_filter:
                color = TEAL if key == "todos" else PRIORITY[key]["color"]
                btn.configure(fg_color=color, text_color="white")
            else:
                btn.configure(fg_color="#e5e5e5", text_color="#444")

    # ── Lista de tarefas ──────────────────────────────────────────────────────

    def _load(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        if self.current_tab == "inbox":
            self.lbl_count.configure(text="")
            self._build_inbox_view()
            return

        if self.current_tab == "calendario":
            self._build_calendario_view()
            return

        if self.current_tab == "hoje":
            self._build_hoje_view()
            return

        if self.current_tab == "andamento":
            self._build_andamento_view()
            return

        if self.current_tab == "clientes":
            self._build_clientes_view()
            return

        if self.current_tab == "atividades":
            tasks = fetch_done_tasks(self.prio_filter)
            n = len(tasks)
            self.lbl_count.configure(
                text=f"{n} atividade{'s' if n != 1 else ''} concluída{'s' if n != 1 else ''}"
            )
            if not tasks:
                ctk.CTkLabel(self.scroll, text="Nenhuma atividade concluída ainda.",
                             font=ctk.CTkFont(size=13), text_color="#bbb").pack(pady=60)
                return
            for task in tasks:
                self._card_done(task)
            return

        tasks   = fetch_tasks(self.current_tab, self.show_done, self.prio_filter, self.client_filter_id)
        pending = sum(1 for t in tasks if t["status"] == "pending")
        self.lbl_count.configure(
            text=f"{pending} pendente{'s' if pending != 1 else ''} / {len(tasks)} total"
        )

        if not tasks:
            ctk.CTkLabel(self.scroll, text="Nenhuma tarefa aqui ainda.",
                         font=ctk.CTkFont(size=13), text_color="#bbb").pack(pady=60)
            return

        for task in tasks:
            self._card(task)

    def _card(self, task):
        is_done       = task["status"] == "done"
        is_in_progress = task["status"] == "in_progress"
        p             = PRIORITY[task["priority"]]

        border_color = "#fcd34d" if is_in_progress else "#e2e2e2"
        card = ctk.CTkFrame(self.scroll, fg_color="#fff", corner_radius=8,
                            border_width=2 if is_in_progress else 1,
                            border_color=border_color, cursor="hand2")
        card.pack(fill="x", padx=14, pady=4)
        card.grid_columnconfigure(1, weight=1)

        def _show_context(event, tid=task["id"], status=task["status"]):
            menu = tk.Menu(self, tearoff=0)
            if status == "in_progress":
                menu.add_command(label="↩ Voltar para pendente",
                                 command=lambda: self._toggle_in_progress(tid, status))
            else:
                menu.add_command(label="▶ Marcar como Em andamento",
                                 command=lambda: self._toggle_in_progress(tid, status))
            menu.tk_popup(event.x_root, event.y_root)
        card.bind("<Button-3>", _show_context)

        # Checkbox (toggle direto, sem abrir detalhe)
        var = tk.BooleanVar(value=is_done)
        chk = ctk.CTkCheckBox(
            card, text="", variable=var,
            checkbox_width=20, checkbox_height=20, width=28,
            command=lambda tid=task["id"], s=task["status"]: self._toggle(tid, s)
        )
        chk.grid(row=0, column=0, rowspan=2, padx=(14, 4), pady=14, sticky="n")

        # Badge de prioridade
        badge = ctk.CTkFrame(card, fg_color=p["color"], corner_radius=4, width=54, height=22)
        badge.grid(row=0, column=2, padx=6, pady=(14, 0), sticky="ne")
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=p["label"],
                     font=ctk.CTkFont(family="Calibri", size=10, weight="bold"),
                     text_color="white").pack(expand=True)

        # Badge "Em andamento"
        if is_in_progress:
            ap = ctk.CTkFrame(card, fg_color="#b45309", corner_radius=4, width=96, height=22)
            ap.grid(row=0, column=3, padx=4, pady=(14, 0), sticky="ne")
            ap.pack_propagate(False)
            ctk.CTkLabel(ap, text="▶ Em andamento",
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color="white").pack(expand=True)

        # Checklist progress badge (se existir)
        items     = db_get_checklist(task["id"])
        done_ck   = sum(1 for i in items if i["is_done"])
        total_ck  = len(items)
        if total_ck > 0:
            ck_color = "#059669" if done_ck == total_ck else "#888"
            ck_badge = ctk.CTkFrame(card, fg_color=ck_color, corner_radius=4,
                                    width=46, height=22)
            ck_badge.grid(row=0, column=4, padx=4, pady=(14, 0), sticky="ne")
            ck_badge.pack_propagate(False)
            ctk.CTkLabel(ck_badge, text=f"{done_ck}/{total_ck}",
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color="white").pack(expand=True)

        # Deadline badge
        dl = task["deadline"] if task["deadline"] else None
        if dl and not is_done:
            today = datetime.now().strftime("%Y-%m-%d")
            if dl < today:
                dl_color = "#DC2626"
                dl_text  = f"⚠ {_fmt_deadline(dl)}"
            elif dl == today:
                dl_color = "#D97706"
                dl_text  = "Hoje"
            else:
                dl_color = "#6b7280"
                dl_text  = _fmt_deadline(dl)
            dl_badge = ctk.CTkFrame(card, fg_color=dl_color, corner_radius=4, width=80, height=22)
            dl_badge.grid(row=0, column=5, padx=4, pady=(14, 0), sticky="ne")
            dl_badge.pack_propagate(False)
            ctk.CTkLabel(dl_badge, text=dl_text,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color="white").pack(expand=True)

        # Cliente badge
        if task["client_id"]:
            with _db() as _cx:
                _cl = _cx.execute("SELECT name FROM clients WHERE id=?", (task["client_id"],)).fetchone()
            if _cl:
                cl_name = _cl["name"][:18] + ("…" if len(_cl["name"]) > 18 else "")
                cl_badge = ctk.CTkFrame(card, fg_color="#dbeafe", corner_radius=4,
                                        width=max(60, len(cl_name)*7), height=22)
                cl_badge.grid(row=0, column=6, padx=4, pady=(14, 0), sticky="ne")
                cl_badge.pack_propagate(False)
                ctk.CTkLabel(cl_badge, text=cl_name,
                             font=ctk.CTkFont(size=10, weight="bold"),
                             text_color="#1d4ed8").pack(expand=True)

        # Título (clicável → abre detalhe)
        title_color = "#b0b0b0" if is_done else "#1a1a1a"
        title_lbl = ctk.CTkLabel(
            card, text=task["title"],
            font=ctk.CTkFont(family="Calibri", size=13, weight="bold"),
            text_color=title_color, anchor="w", cursor="hand2"
        )
        title_lbl.grid(row=0, column=1, padx=(4, 8), pady=(12, 0), sticky="ew")
        title_lbl.bind("<Button-1>", lambda e, tid=task["id"]: self._open_detail(tid))
        title_lbl.bind("<Button-3>", _show_context)
        card.bind("<Button-1>", lambda e, tid=task["id"]: self._open_detail(tid))

        row = 1
        if task["description"]:
            desc_short = task["description"][:80] + ("..." if len(task["description"]) > 80 else "")
            ctk.CTkLabel(card, text=desc_short,
                         font=ctk.CTkFont(family="Calibri", size=11),
                         text_color="#888", anchor="w").grid(
                row=row, column=1, columnspan=3, padx=(4, 14), pady=(0, 4), sticky="ew")
            row += 1

        if task["attachment_name"]:
            att = ctk.CTkButton(
                card, text=f"  {task['attachment_name'][:36]}", width=0, height=22,
                font=ctk.CTkFont(size=10), anchor="w",
                fg_color="#f0f0f0", text_color="#666", hover_color="#e5e5e5",
                corner_radius=4,
                command=lambda p=task["attachment_path"]: self._open_file(p)
            )
            att.grid(row=row, column=1, columnspan=3, padx=(4, 14), pady=(0, 10), sticky="w")

        if row == 1 and not task["attachment_name"]:
            card.grid_rowconfigure(1, minsize=4)

    def _card_done(self, task):
        p       = PRIORITY[task["priority"]]
        tab_lbl = "Pessoal" if task["tab"] == "pessoal" else "Profissional"

        card = ctk.CTkFrame(self.scroll, fg_color="#f6fef9", corner_radius=8,
                            border_width=1, border_color="#a7f3d0", cursor="hand2")
        card.pack(fill="x", padx=14, pady=4)
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(card, text="✓", font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#059669", width=32).grid(
            row=0, column=0, rowspan=2, padx=(14, 4), pady=12, sticky="n")

        title_lbl = ctk.CTkLabel(
            card, text=task["title"],
            font=ctk.CTkFont(family="Calibri", size=13, weight="bold"),
            text_color="#2d6a4f", anchor="w", cursor="hand2"
        )
        title_lbl.grid(row=0, column=1, padx=(4, 8), pady=(12, 0), sticky="ew")
        title_lbl.bind("<Button-1>", lambda e, tid=task["id"]: self._open_detail(tid))
        card.bind("<Button-1>",      lambda e, tid=task["id"]: self._open_detail(tid))

        # Badge prioridade (cor suavizada)
        badge = ctk.CTkFrame(card, fg_color=p["color"], corner_radius=4, width=54, height=22)
        badge.grid(row=0, column=2, padx=(0, 4), pady=(12, 0), sticky="ne")
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=p["label"],
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="white").pack(expand=True)

        # Badge aba de origem
        tb = ctk.CTkFrame(card, fg_color="#d1fae5", corner_radius=4, width=86, height=22)
        tb.grid(row=0, column=3, padx=(0, 6), pady=(12, 0), sticky="ne")
        tb.pack_propagate(False)
        ctk.CTkLabel(tb, text=tab_lbl,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#059669").pack(expand=True)

        # Botão Reativar
        ctk.CTkButton(
            card, text="↩ Reativar", width=96, height=28,
            fg_color="#e5e5e5", text_color="#555", hover_color="#d0d0d0",
            font=ctk.CTkFont(size=11), corner_radius=6,
            command=lambda tid=task["id"]: self._reactivate(tid)
        ).grid(row=0, column=4, padx=(0, 14), pady=(12, 0), sticky="ne")

        # Linha 2: descrição + data de conclusão
        desc_part = ""
        if task["description"]:
            desc_part = task["description"][:80] + ("..." if len(task["description"]) > 80 else "")
        when_part = ""
        if task["completed_at"]:
            try:
                dt        = datetime.fromisoformat(task["completed_at"])
                when_part = f"Concluída em {dt.strftime('%d/%m/%Y às %H:%M')}"
            except Exception:
                when_part = task["completed_at"] or ""
        meta = "  ·  ".join(p for p in [desc_part, when_part] if p)
        if meta:
            ctk.CTkLabel(card, text=meta,
                         font=ctk.CTkFont(family="Calibri", size=11),
                         text_color="#6b7280", anchor="w").grid(
                row=1, column=1, columnspan=4, padx=(4, 14), pady=(0, 10), sticky="ew")
        else:
            card.grid_rowconfigure(1, minsize=4)

    def _build_hoje_view(self):
        today_tasks   = fetch_tasks_today()
        overdue_tasks = fetch_tasks_overdue()
        n_today   = len(today_tasks)
        n_overdue = len(overdue_tasks)
        self.lbl_count.configure(
            text=f"{n_today} hoje · {n_overdue} atrasada{'s' if n_overdue != 1 else ''}"
        )

        if not today_tasks and not overdue_tasks:
            ctk.CTkLabel(
                self.scroll,
                text="Nenhuma tarefa com prazo definido para hoje.\n"
                     "Adicione uma Data de Entrega ao criar ou editar uma tarefa.",
                font=ctk.CTkFont(size=13), text_color="#bbb",
                justify="center"
            ).pack(pady=60)
            return

        if today_tasks:
            sec = ctk.CTkFrame(self.scroll, fg_color="transparent")
            sec.pack(fill="x", padx=14, pady=(12, 2))
            ctk.CTkLabel(sec, text="📅  Vencem Hoje",
                         font=ctk.CTkFont(family="Calibri", size=13, weight="bold"),
                         text_color="#D97706").pack(side="left")
            for task in today_tasks:
                self._card(task)

        if overdue_tasks:
            sec = ctk.CTkFrame(self.scroll, fg_color="transparent")
            sec.pack(fill="x", padx=14, pady=(16, 2))
            ctk.CTkLabel(sec, text="⚠  Atrasadas",
                         font=ctk.CTkFont(family="Calibri", size=13, weight="bold"),
                         text_color="#DC2626").pack(side="left")
            for task in overdue_tasks:
                self._card(task)

    def _build_calendario_view(self):
        _MONTHS = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                   "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
        _DAYS   = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]

        month_counts = fetch_tasks_counts_for_month(self._cal_year, self._cal_month)
        today_iso    = datetime.now().strftime("%Y-%m-%d")
        total_month  = sum(c for c, _ in month_counts.values())
        self.lbl_count.configure(
            text=f"{total_month} tarefa{'s' if total_month != 1 else ''} em {_MONTHS[self._cal_month-1]}"
        )

        # ── Wrapper centralizado ──────────────────────────────────────────────
        outer = ctk.CTkFrame(self.scroll, fg_color="transparent")
        outer.pack(fill="x", padx=20, pady=(14, 0))

        cal_f = ctk.CTkFrame(outer, fg_color="white", corner_radius=10,
                             border_width=1, border_color="#e0e0e0")
        cal_f.pack(anchor="center")

        # ── Cabeçalho de navegação ────────────────────────────────────────────
        def _prev():
            self._cal_month -= 1
            if self._cal_month < 1:
                self._cal_month = 12; self._cal_year -= 1
            self._load()

        def _next():
            self._cal_month += 1
            if self._cal_month > 12:
                self._cal_month = 1; self._cal_year += 1
            self._load()

        hdr = ctk.CTkFrame(cal_f, fg_color=TEAL, corner_radius=0, height=46)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkButton(hdr, text="‹", width=46, height=46, corner_radius=0,
                      fg_color=TEAL, hover_color=TEAL_DARK, text_color="white",
                      font=ctk.CTkFont(size=18, weight="bold"),
                      command=_prev).pack(side="left")
        ctk.CTkButton(hdr, text="›", width=46, height=46, corner_radius=0,
                      fg_color=TEAL, hover_color=TEAL_DARK, text_color="white",
                      font=ctk.CTkFont(size=18, weight="bold"),
                      command=_next).pack(side="right")
        ctk.CTkLabel(hdr, text=f"{_MONTHS[self._cal_month-1]}  {self._cal_year}",
                     font=ctk.CTkFont(family="Calibri", size=14, weight="bold"),
                     text_color="white").pack(expand=True)

        # Botão "Hoje" no header
        ctk.CTkButton(hdr, text="Hoje", width=56, height=28, corner_radius=6,
                      fg_color="white", text_color=TEAL, hover_color="#e0f7fa",
                      font=ctk.CTkFont(size=10, weight="bold"),
                      command=self._cal_go_today).place(relx=0.85, rely=0.5, anchor="center")

        # ── Linha dos dias da semana ──────────────────────────────────────────
        wk_f = ctk.CTkFrame(cal_f, fg_color="#e8f4f6", corner_radius=0, height=26)
        wk_f.pack(fill="x")
        wk_f.pack_propagate(False)
        for d in _DAYS:
            ctk.CTkLabel(wk_f, text=d, width=52, height=26,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color="#555").pack(side="left")

        # ── Grade de dias ─────────────────────────────────────────────────────
        grid_f = ctk.CTkFrame(cal_f, fg_color="white", corner_radius=0)
        grid_f.pack(fill="x", padx=4, pady=4)

        weeks = _cal.monthcalendar(self._cal_year, self._cal_month)
        sel   = self._cal_selected

        for week in weeks:
            row_f = ctk.CTkFrame(grid_f, fg_color="transparent")
            row_f.pack(fill="x")
            for day in week:
                if day == 0:
                    ctk.CTkLabel(row_f, text="", width=52, height=52).pack(side="left")
                    continue

                day_iso  = f"{self._cal_year:04d}-{self._cal_month:02d}-{day:02d}"
                is_today = (day_iso == today_iso)
                is_sel   = (day_iso == sel)
                cnt, alta = month_counts.get(day, (0, 0))

                if is_sel:
                    cell_fg, num_tc = TEAL, "white"
                elif is_today:
                    cell_fg, num_tc = "#e0f7fa", TEAL
                else:
                    cell_fg, num_tc = "#f9f9f9", "#1a1a1a"

                cell = ctk.CTkFrame(row_f, fg_color=cell_fg, corner_radius=6,
                                    width=50, height=50, cursor="hand2")
                cell.pack(side="left", padx=1, pady=1)
                cell.pack_propagate(False)

                num_lbl = ctk.CTkLabel(
                    cell, text=str(day),
                    font=ctk.CTkFont(size=12, weight="bold" if (is_today or is_sel or cnt > 0) else "normal"),
                    text_color=num_tc
                )
                num_lbl.pack(pady=(8, 0))

                if cnt > 0:
                    dot_color = ("#DC2626" if alta > 0 else TEAL) if not is_sel else "white"
                    dot_row = ctk.CTkFrame(cell, fg_color="transparent")
                    dot_row.pack()
                    for _ in range(min(cnt, 3)):
                        ctk.CTkFrame(dot_row, fg_color=dot_color, corner_radius=3,
                                     width=5, height=5).pack(side="left", padx=1)

                def _click(e, d=day_iso):
                    self._cal_select(d)
                cell.bind("<Button-1>", _click)
                for child in cell.winfo_children():
                    child.bind("<Button-1>", _click)

        # ── Separador ─────────────────────────────────────────────────────────
        ctk.CTkFrame(self.scroll, fg_color="#e0e0e0", height=1).pack(
            fill="x", padx=20, pady=(14, 0))

        # ── Tarefas do dia selecionado ────────────────────────────────────────
        if not sel:
            return

        try:
            d_obj = datetime.strptime(sel, "%Y-%m-%d")
        except Exception:
            return

        day_tasks = fetch_tasks_for_date(sel)
        n = len(day_tasks)

        sec_hdr = ctk.CTkFrame(self.scroll, fg_color="transparent")
        sec_hdr.pack(fill="x", padx=20, pady=(10, 4))
        ctk.CTkLabel(
            sec_hdr,
            text=f"📅  {d_obj.strftime('%d/%m/%Y')} — "
                 f"{n} tarefa{'s' if n != 1 else ''} com prazo neste dia",
            font=ctk.CTkFont(family="Calibri", size=13, weight="bold"),
            text_color="#1a1a1a"
        ).pack(side="left")

        if not day_tasks:
            ctk.CTkLabel(self.scroll, text="Nenhuma tarefa com prazo para este dia.",
                         font=ctk.CTkFont(size=12), text_color="#bbb").pack(pady=20)
        else:
            for task in day_tasks:
                self._card(task)

    def _cal_select(self, iso_date):
        self._cal_selected = iso_date
        y, m, _ = iso_date.split("-")
        self._cal_year  = int(y)
        self._cal_month = int(m)
        self._load()

    def _cal_go_today(self):
        today = datetime.now()
        self._cal_year     = today.year
        self._cal_month    = today.month
        self._cal_selected = today.strftime("%Y-%m-%d")
        self._load()

    # ── Ações ─────────────────────────────────────────────────────────────────

    def _toggle(self, task_id, current_status):
        db_toggle(task_id, current_status)
        self._load()

    def _reactivate(self, task_id):
        db_toggle(task_id, "done")
        self._load()

    def _toggle_in_progress(self, task_id, current_status):
        if current_status == "in_progress":
            db_set_pending(task_id)
        else:
            db_set_in_progress(task_id)
        self._load()

    def _build_andamento_view(self):
        tasks = fetch_tasks_in_progress()
        n = len(tasks)
        self.lbl_count.configure(text=f"{n} em andamento")
        if not tasks:
            ctk.CTkLabel(
                self.scroll,
                text="Nenhuma tarefa em andamento.\n\nClique com o botão direito em qualquer tarefa\npara marcá-la como em andamento.",
                font=ctk.CTkFont(size=13), text_color="#bbb", justify="center"
            ).pack(pady=80)
            return
        for task in tasks:
            self._card_andamento(task)

    def _card_andamento(self, task):
        p       = PRIORITY[task["priority"]]
        tab_lbl = "Pessoal" if task["tab"] == "pessoal" else "Profissional"

        card = ctk.CTkFrame(self.scroll, fg_color="#fffbeb", corner_radius=8,
                            border_width=2, border_color="#fcd34d", cursor="hand2")
        card.pack(fill="x", padx=14, pady=4)
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(card, text="▶", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#b45309", width=32).grid(
            row=0, column=0, rowspan=2, padx=(14, 4), pady=12, sticky="n")

        title_lbl = ctk.CTkLabel(
            card, text=task["title"],
            font=ctk.CTkFont(family="Calibri", size=13, weight="bold"),
            text_color="#1a1a1a", anchor="w", cursor="hand2"
        )
        title_lbl.grid(row=0, column=1, padx=(4, 8), pady=(12, 0), sticky="ew")
        title_lbl.bind("<Button-1>", lambda e, tid=task["id"]: self._open_detail(tid))
        card.bind("<Button-1>",      lambda e, tid=task["id"]: self._open_detail(tid))

        badge = ctk.CTkFrame(card, fg_color=p["color"], corner_radius=4, width=54, height=22)
        badge.grid(row=0, column=2, padx=(0, 4), pady=(12, 0), sticky="ne")
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=p["label"],
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="white").pack(expand=True)

        tb = ctk.CTkFrame(card, fg_color="#fef3c7", corner_radius=4, width=86, height=22)
        tb.grid(row=0, column=3, padx=(0, 4), pady=(12, 0), sticky="ne")
        tb.pack_propagate(False)
        ctk.CTkLabel(tb, text=tab_lbl,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#b45309").pack(expand=True)

        ctk.CTkButton(
            card, text="↩ Voltar", width=80, height=28,
            fg_color="#e5e5e5", text_color="#555", hover_color="#d0d0d0",
            font=ctk.CTkFont(size=11), corner_radius=6,
            command=lambda tid=task["id"]: self._toggle_in_progress(tid, "in_progress")
        ).grid(row=0, column=4, padx=(0, 6), pady=(12, 0), sticky="ne")

        ctk.CTkButton(
            card, text="Concluir ✓", width=96, height=28,
            fg_color="#059669", hover_color="#047857", text_color="white",
            font=ctk.CTkFont(size=11, weight="bold"), corner_radius=6,
            command=lambda tid=task["id"]: self._complete_from_andamento(tid)
        ).grid(row=0, column=5, padx=(0, 14), pady=(12, 0), sticky="ne")

        if task["description"]:
            desc_short = task["description"][:90] + ("..." if len(task["description"]) > 90 else "")
            ctk.CTkLabel(card, text=desc_short,
                         font=ctk.CTkFont(family="Calibri", size=11),
                         text_color="#888", anchor="w").grid(
                row=1, column=1, columnspan=5, padx=(4, 14), pady=(0, 10), sticky="ew")
        else:
            card.grid_rowconfigure(1, minsize=4)

    def _complete_from_andamento(self, task_id):
        db_complete(task_id)
        self._load()

    def _build_clientes_view(self):
        stats = db_get_client_stats()
        total_linked = sum(1 for _, s in stats if (s["total"] or 0) > 0)
        self.lbl_count.configure(text=f"{len(stats)} clientes · {total_linked} com tarefas")

        # Cabeçalho + botão novo cliente
        top = ctk.CTkFrame(self.scroll, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(12, 6))
        ctk.CTkLabel(top, text="Clientes da Carteira",
                     font=ctk.CTkFont(family="Calibri", size=14, weight="bold"),
                     text_color="#1a1a1a").pack(side="left")
        ctk.CTkButton(top, text="+ Novo Cliente", width=130, height=30,
                      fg_color="#1d4ed8", hover_color="#1e40af", text_color="white",
                      font=ctk.CTkFont(size=11, weight="bold"), corner_radius=6,
                      command=self._add_client_dialog).pack(side="right")

        TIER_COLOR = {"A": "#f59e0b", "B": "#3b82f6", "C": "#6b7280"}
        for client, s in stats:
            pending    = s["pending"]    or 0
            in_prog    = s["in_progress"] or 0
            done       = s["done"]       or 0
            total      = s["total"]      or 0

            card = ctk.CTkFrame(self.scroll, fg_color="#fff", corner_radius=8,
                                border_width=1, border_color="#e2e2e2")
            card.pack(fill="x", padx=14, pady=3)
            card.grid_columnconfigure(1, weight=1)

            # Tier badge
            tc = TIER_COLOR.get(client["tier"], "#6b7280")
            tb = ctk.CTkFrame(card, fg_color=tc, corner_radius=4, width=28, height=28)
            tb.grid(row=0, column=0, padx=(12, 8), pady=12, sticky="w")
            tb.pack_propagate(False)
            ctk.CTkLabel(tb, text=client["tier"],
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="white").pack(expand=True)

            # Nome + status + notas
            name_col = ctk.CTkFrame(card, fg_color="transparent")
            name_col.grid(row=0, column=1, padx=(0, 8), pady=(10, 8), sticky="ew")
            ctk.CTkLabel(name_col, text=client["name"],
                         font=ctk.CTkFont(family="Calibri", size=13, weight="bold"),
                         text_color="#1a1a1a", anchor="w").pack(fill="x")
            status_cs = client["status_cs"] or ""
            notes_cs  = client["notes_cs"]  or ""
            if status_cs:
                ctk.CTkLabel(name_col, text=status_cs,
                             font=ctk.CTkFont(size=10, weight="bold"),
                             text_color="#1d4ed8", anchor="w").pack(fill="x")
            if notes_cs:
                ctk.CTkLabel(name_col, text=notes_cs,
                             font=ctk.CTkFont(size=10),
                             text_color="#6b7280", anchor="w",
                             wraplength=420, justify="left").pack(fill="x")

            # Contadores de tarefas
            cnt_f = ctk.CTkFrame(card, fg_color="transparent")
            cnt_f.grid(row=0, column=2, padx=(0, 8), pady=12, sticky="e")
            if total == 0:
                ctk.CTkLabel(cnt_f, text="sem tarefas",
                             font=ctk.CTkFont(size=10), text_color="#ccc").pack(side="left")
            else:
                for count, label, fg, tc2 in [
                    (pending, "pendentes", "#e5e7eb", "#374151"),
                    (in_prog, "andamento", "#fef3c7", "#b45309"),
                    (done,    "concluídas", "#d1fae5", "#059669"),
                ]:
                    if count == 0:
                        continue
                    b = ctk.CTkFrame(cnt_f, fg_color=fg, corner_radius=4,
                                     width=max(32, len(str(count))*8+28), height=22)
                    b.pack(side="left", padx=(0, 4))
                    b.pack_propagate(False)
                    ctk.CTkLabel(b, text=f"{count} {label}",
                                 font=ctk.CTkFont(size=10, weight="bold"),
                                 text_color=tc2).pack(expand=True)

            # Botão Ver tarefas
            ctk.CTkButton(
                card, text="Ver tarefas", width=96, height=28,
                fg_color="#dbeafe", text_color="#1d4ed8", hover_color="#bfdbfe",
                font=ctk.CTkFont(size=11), corner_radius=6,
                command=lambda cid=client["id"], cname=client["name"]: self._filter_by_client(cid, cname)
            ).grid(row=0, column=3, padx=(0, 6), pady=12, sticky="e")

            # Botão Excluir (só se sem tarefas)
            if total == 0:
                ctk.CTkButton(
                    card, text="✕", width=28, height=28, corner_radius=4,
                    fg_color="transparent", text_color="#ccc", hover_color="#fee2e2",
                    command=lambda cid=client["id"]: self._delete_client(cid)
                ).grid(row=0, column=4, padx=(0, 10), pady=12, sticky="e")

    def _filter_by_client(self, client_id, client_name):
        self.client_filter_id = client_id
        self._client_var.set(client_name)
        self._switch("profissional")

    def _delete_client(self, client_id):
        db_delete_client(client_id)
        self._load()

    def _add_client_dialog(self):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Novo Cliente")
        dlg.geometry("380x220")
        dlg.resizable(False, False)
        dlg.after(100, dlg.lift)
        dlg.grab_set()
        dlg.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(dlg, text="Nome do cliente *", anchor="w",
                     font=ctk.CTkFont(family="Calibri", size=12, weight="bold")
                     ).grid(row=0, column=0, padx=24, pady=(24, 4), sticky="w")
        ent = ctk.CTkEntry(dlg, height=36, font=ctk.CTkFont(family="Calibri", size=13))
        ent.grid(row=1, column=0, padx=24, sticky="ew")
        ent.focus()

        ctk.CTkLabel(dlg, text="Tier", anchor="w",
                     font=ctk.CTkFont(family="Calibri", size=12, weight="bold")
                     ).grid(row=2, column=0, padx=24, pady=(16, 6), sticky="w")
        tier_var = tk.StringVar(value="B")
        tf = ctk.CTkFrame(dlg, fg_color="transparent")
        tf.grid(row=3, column=0, padx=24, sticky="w")
        for t in ["A", "B", "C"]:
            ctk.CTkRadioButton(tf, text=f"Tier {t}", variable=tier_var, value=t,
                               font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 16))

        bf = ctk.CTkFrame(dlg, fg_color="transparent")
        bf.grid(row=4, column=0, padx=24, pady=20, sticky="e")
        ctk.CTkButton(bf, text="Cancelar", width=100, height=36,
                      fg_color="#e5e5e5", text_color="#444",
                      command=dlg.destroy).pack(side="left", padx=(0, 10))

        def _save_client():
            name = ent.get().strip()
            if not name:
                return
            db_add_client(name, tier_var.get())
            # Atualiza dropdown de filtro
            _clients = db_get_clients()
            self._client_names = ["Todos"] + [c["name"] for c in _clients]
            self._client_ids   = [None] + [c["id"] for c in _clients]
            self.client_dropdown.configure(values=self._client_names)
            dlg.destroy()
            self._load()

        ctk.CTkButton(bf, text="Salvar", width=100, height=36,
                      fg_color="#1d4ed8", hover_color="#1e40af", text_color="white",
                      command=_save_client).pack(side="left")

    def _open_detail(self, task_id):
        TaskDetailDialog(self, task_id, on_save=self._load)

    def _open_file(self, path):
        if path and os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showwarning("Arquivo não encontrado",
                                   "O arquivo não foi localizado no disco.", parent=self)

    # ── Inbox — Entrada Rápida ─────────────────────────────────────────────────

    def _build_inbox_view(self):
        wrap = ctk.CTkFrame(self.scroll, fg_color="transparent")
        wrap.pack(fill="x", padx=30, pady=28)

        ctk.CTkLabel(wrap, text="📥 Entrada Rápida",
                     font=ctk.CTkFont(family="Calibri", size=20, weight="bold"),
                     text_color="#1a1a1a", anchor="w").pack(fill="x")
        ctk.CTkLabel(wrap,
                     text="Cole anotações brutas, resumo de reunião ou mensagens. "
                          "A IA identifica as tarefas e você confirma antes de salvar.",
                     font=ctk.CTkFont(size=12), text_color="#888", anchor="w",
                     wraplength=620, justify="left").pack(fill="x", pady=(4, 16))

        self.inbox_txt = ctk.CTkTextbox(
            wrap, height=230, font=ctk.CTkFont(family="Calibri", size=12),
            wrap="word", border_width=1, border_color="#d0d0d0")
        self.inbox_txt.pack(fill="x")

        # Toolbar: voz + otimizar
        if self.inbox_is_recording:
            self.inbox_is_recording = False
        tools_f = ctk.CTkFrame(wrap, fg_color="transparent")
        tools_f.pack(fill="x", pady=(6, 0))
        if VOICE_OK:
            self.lbl_inbox_voice = ctk.CTkLabel(tools_f, text="",
                                                 font=ctk.CTkFont(size=11), text_color="#0E8FA3")
            self.lbl_inbox_voice.pack(side="left", padx=(0, 6))
            self.btn_inbox_mic = ctk.CTkButton(
                tools_f, text="🎤 Gravar voz", width=130, height=30,
                fg_color="#e5e5e5", text_color="#444", hover_color="#d0d0d0",
                font=ctk.CTkFont(size=11), corner_radius=6,
                command=self._inbox_voice_toggle
            )
            self.btn_inbox_mic.pack(side="left", padx=(0, 10))
        if AI_OK:
            self.lbl_refine_status = ctk.CTkLabel(tools_f, text="",
                                                   font=ctk.CTkFont(size=11), text_color="#7c3aed")
            self.lbl_refine_status.pack(side="right")
            self.btn_refine = ctk.CTkButton(
                tools_f, text="✨ Otimizar texto", width=155, height=30,
                fg_color="#ede9fe", text_color="#7c3aed", hover_color="#ddd6fe",
                font=ctk.CTkFont(size=11, weight="bold"), corner_radius=6,
                command=self._refine_inbox_text
            )
            self.btn_refine.pack(side="right", padx=(10, 0))

        # Destino padrão
        opt_f = ctk.CTkFrame(wrap, fg_color="transparent")
        opt_f.pack(fill="x", pady=(12, 0))
        ctk.CTkLabel(opt_f, text="Destino padrão das tarefas:",
                     font=ctk.CTkFont(size=11), text_color="#666").pack(side="left")
        self.inbox_tab_var = tk.StringVar(value="profissional")
        for lbl, val in [("Profissional Efcaz", "profissional"), ("Pessoal", "pessoal")]:
            ctk.CTkRadioButton(opt_f, text=lbl, variable=self.inbox_tab_var, value=val,
                               font=ctk.CTkFont(size=11)).pack(side="left", padx=(14, 0))

        # Avisos de dependência / credenciais
        self.inbox_key_entry = None
        if not AI_OK:
            warn = ctk.CTkFrame(wrap, fg_color="#fff8e1", corner_radius=8,
                                 border_width=1, border_color="#fcd34d")
            warn.pack(fill="x", pady=(14, 0))
            ctk.CTkLabel(warn,
                         text="⚠  Biblioteca 'anthropic' não instalada. "
                              "Execute no terminal:  pip install anthropic",
                         font=ctk.CTkFont(size=11), text_color="#92400e",
                         ).pack(anchor="w", padx=14, pady=10)
        elif not _get_auth():
            key_f = ctk.CTkFrame(wrap, fg_color="#fff8e1", corner_radius=8,
                                  border_width=1, border_color="#fcd34d")
            key_f.pack(fill="x", pady=(14, 0))
            ctk.CTkLabel(key_f,
                         text="⚠  Credencial não encontrada. Insira sua Anthropic API Key:",
                         font=ctk.CTkFont(size=11), text_color="#92400e",
                         ).pack(anchor="w", padx=14, pady=(10, 4))
            krow = ctk.CTkFrame(key_f, fg_color="transparent")
            krow.pack(fill="x", padx=14, pady=(0, 10))
            krow.grid_columnconfigure(0, weight=1)
            self.inbox_key_entry = ctk.CTkEntry(
                krow, height=32, show="*",
                placeholder_text="sk-ant-...",
                font=ctk.CTkFont(size=11))
            self.inbox_key_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
            ctk.CTkButton(krow, text="Salvar chave", width=110, height=32,
                          fg_color=TEAL, hover_color=TEAL_DARK,
                          font=ctk.CTkFont(size=11),
                          command=self._save_api_key).grid(row=0, column=1)

        # Botões processar + salvar direto + status
        btn_f = ctk.CTkFrame(wrap, fg_color="transparent")
        btn_f.pack(fill="x", pady=(18, 0))
        self.btn_process = ctk.CTkButton(
            btn_f, text="✨ Organizar com IA", height=44, width=210,
            fg_color="#7c3aed", hover_color="#6d28d9",
            font=ctk.CTkFont(family="Calibri", size=13, weight="bold"),
            state="normal" if AI_OK else "disabled",
            command=self._process_inbox,
        )
        self.btn_process.pack(side="left")
        ctk.CTkButton(
            btn_f, text="💾 Salvar sem IA", height=44, width=170,
            fg_color="#e5e5e5", text_color="#444", hover_color="#d0d0d0",
            font=ctk.CTkFont(family="Calibri", size=13, weight="bold"),
            command=self._save_inbox_direct,
        ).pack(side="left", padx=(10, 0))
        self.inbox_status = ctk.CTkLabel(btn_f, text="", font=ctk.CTkFont(size=12),
                                          text_color="#888")
        self.inbox_status.pack(side="left", padx=14)

    def _process_inbox(self):
        raw = self.inbox_txt.get("1.0", "end").strip()
        if not raw:
            self.inbox_status.configure(
                text="⚠ Cole algum texto antes de processar.", text_color="#D97706")
            return

        # Salva chave manual se o usuário a preencheu
        if self.inbox_key_entry:
            manual_key = self.inbox_key_entry.get().strip()
            if manual_key:
                _save_config({"api_key": manual_key})

        if not _get_auth():
            self.inbox_status.configure(
                text="⚠ Nenhuma credencial encontrada.", text_color="#DC2626")
            return

        self.btn_process.configure(state="disabled", text="⏳ Processando...")
        self.inbox_status.configure(text="Consultando IA...", text_color="#7c3aed")
        default_tab = self.inbox_tab_var.get()

        def _run():
            try:
                tasks = extract_tasks_ai(raw, default_tab)
                self.after(0, lambda: self._show_review(tasks))
            except Exception as e:
                self.after(0, lambda err=e: self._inbox_error(str(err)))

        threading.Thread(target=_run, daemon=True).start()

    def _show_review(self, tasks):
        self.btn_process.configure(state="normal", text="✨ Organizar com IA")
        self.inbox_status.configure(text="")
        if not tasks:
            self.inbox_status.configure(
                text="Nenhuma tarefa identificada. Tente reformular o texto.",
                text_color="#D97706")
            return
        ReviewDialog(self, tasks, on_confirm=self._save_extracted)

    def _save_inbox_direct(self):
        raw = self.inbox_txt.get("1.0", "end").strip()
        if not raw:
            self.inbox_status.configure(
                text="⚠ Cole algum texto antes de salvar.", text_color="#D97706")
            return
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        title = lines[0][:80] if lines else raw[:80]
        notes = " ".join(lines[1:]) if len(lines) > 1 else ""
        default_tab = self.inbox_tab_var.get()
        task = {"title": title, "priority": "media", "notes": notes, "tab": default_tab}
        ReviewDialog(self, [task], on_confirm=self._save_extracted)

    def _inbox_error(self, msg):
        self.btn_process.configure(state="normal", text="✨ Organizar com IA")
        if "401" in msg or "authentication_error" in msg or "Invalid authentication" in msg:
            _save_config({"api_key": ""})
            self.inbox_status.configure(
                text="⚠ Credencial inválida ou expirada. Insira uma API Key válida.",
                text_color="#DC2626")
        else:
            self.inbox_status.configure(text=f"Erro: {msg}", text_color="#DC2626")

    def _save_extracted(self, tasks):
        for t in tasks:
            db_add_task(t["tab"], t["title"], t.get("notes", ""), t["priority"],
                        deadline=t.get("deadline"))
        target = getattr(self, "inbox_tab_var", None)
        self._switch(target.get() if target else "profissional")

    def _save_api_key(self):
        if not self.inbox_key_entry:
            return
        key = self.inbox_key_entry.get().strip()
        if key:
            _save_config({"api_key": key})
            self.inbox_status.configure(text="✓ Chave salva.", text_color="#059669")

    # ── Inbox — STT ────────────────────────────────────────────────────────────

    def _inbox_voice_toggle(self):
        if not self.inbox_is_recording:
            self._inbox_voice_start()
        else:
            self._inbox_voice_stop()

    def _inbox_voice_start(self):
        if not VOICE_OK:
            return
        self.inbox_is_recording = True
        self.btn_inbox_mic.configure(text="⏹ Parar", fg_color="#DC2626",
                                      text_color="white", hover_color="#b91c1c")
        self.lbl_inbox_voice.configure(text="🔴 Gravando...", text_color="#DC2626")
        try:
            self.inbox_stream_rec = StreamingRecorder(
                on_text=self._inbox_stream_append,
                on_error=self._inbox_stream_error
            )
            self.inbox_stream_rec.start()
        except Exception as e:
            self.inbox_is_recording = False
            self.inbox_stream_rec = None
            self.btn_inbox_mic.configure(text="🎤 Gravar voz", fg_color="#e5e5e5",
                                          text_color="#444", hover_color="#d0d0d0")
            self.lbl_inbox_voice.configure(text=f"Erro: {e}", text_color="#DC2626")

    def _inbox_voice_stop(self):
        self.inbox_is_recording = False
        self.btn_inbox_mic.configure(text="🎤 Gravar voz", fg_color="#e5e5e5",
                                      text_color="#444", hover_color="#d0d0d0")
        if self.inbox_stream_rec:
            self.inbox_stream_rec.stop()
            self.inbox_stream_rec = None
        self.lbl_inbox_voice.configure(text="✓ Pronto", text_color="#059669")
        self.after(3000, lambda: self.lbl_inbox_voice.configure(text="", text_color="#0E8FA3"))

    def _inbox_stream_append(self, text):
        def _do():
            try:
                current = self.inbox_txt.get("1.0", "end-1c").strip()
                if current:
                    self.inbox_txt.insert("end", " " + text)
                else:
                    self.inbox_txt.insert("end", text)
            except Exception:
                pass
        try:
            self.after(0, _do)
        except Exception:
            pass

    def _inbox_stream_error(self, msg):
        def _do():
            try:
                self.lbl_inbox_voice.configure(text=f"⚠ {msg}", text_color="#DC2626")
                self.after(4000, lambda: self.lbl_inbox_voice.configure(text="", text_color="#0E8FA3"))
            except Exception:
                pass
        try:
            self.after(0, _do)
        except Exception:
            pass

    # ── Inbox — Otimizar com IA ─────────────────────────────────────────────────

    def _refine_inbox_text(self):
        raw = self.inbox_txt.get("1.0", "end").strip()
        if not raw:
            self.lbl_refine_status.configure(text="⚠ Nada para otimizar.", text_color="#D97706")
            return
        if not _get_auth():
            self.lbl_refine_status.configure(text="⚠ Sem credencial.", text_color="#DC2626")
            return
        self.btn_refine.configure(state="disabled", text="⏳ Otimizando...")
        self.lbl_refine_status.configure(text="")

        def _run():
            try:
                refined = refine_text_ai(raw)
                self.after(0, lambda t=refined: self._refine_done(t))
            except Exception as e:
                self.after(0, lambda err=e: self._refine_error(str(err)))

        threading.Thread(target=_run, daemon=True).start()

    def _refine_done(self, refined):
        self.btn_refine.configure(state="normal", text="✨ Otimizar texto")
        self.inbox_txt.delete("1.0", "end")
        self.inbox_txt.insert("1.0", refined)
        self.lbl_refine_status.configure(text="✓ Texto otimizado", text_color="#059669")
        self.after(3000, lambda: self.lbl_refine_status.configure(text=""))

    def _refine_error(self, msg):
        self.btn_refine.configure(state="normal", text="✨ Otimizar texto")
        self.lbl_refine_status.configure(text=f"Erro: {msg}", text_color="#DC2626")

    def _add_dialog(self):
        tab = self.current_tab if self.current_tab not in ("atividades", "inbox") else "profissional"
        AddTaskDialog(self, tab, on_save=self._load)

    def _open_report(self):
        ReportDialog(self)

    # ── Polling (detecta tarefas adicionadas pelo Claude CLI) ─────────────────

    def _start_polling(self):
        def _poll():
            while True:
                time.sleep(4)
                try:
                    n = total_count()
                    today = datetime.now().strftime("%Y-%m-%d")
                    date_changed = today != self._current_date
                    if date_changed:
                        self._current_date = today
                    if n != self._db_count or date_changed:
                        self._db_count = n
                        if self.current_tab != "inbox":
                            self.after(0, self._load)
                except Exception:
                    pass
        threading.Thread(target=_poll, daemon=True).start()


# ══════════════════════════════════════════════════════════════════════════════
#  DIÁLOGO — CONFIGURAÇÃO INICIAL (primeira execução)
# ══════════════════════════════════════════════════════════════════════════════

class FirstRunSetupDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configuração — Gestão Efcaz")
        self.geometry("490x330")
        self.resizable(False, False)
        self.after(100, self.lift)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._skip)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(self, fg_color=TEAL, corner_radius=0)
        hdr.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(hdr, text="Bem-vindo ao Gestão Efcaz",
                     font=ctk.CTkFont(family="Calibri", size=16, weight="bold"),
                     text_color="white").pack(padx=20, pady=16)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, padx=26, pady=16, sticky="nsew")

        ctk.CTkLabel(body,
            text="Para usar as funções de IA (Entrada Rápida e transcrição de voz)\n"
                 "é necessária uma chave da API da Anthropic.",
            font=ctk.CTkFont(size=12), text_color="#555",
            justify="left", anchor="w", wraplength=440
        ).pack(fill="x")

        ctk.CTkLabel(body,
            text="Usuários do Claude Code não precisam fazer nada — já está configurado automaticamente.",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=TEAL,
            justify="left", anchor="w", wraplength=440
        ).pack(fill="x", pady=(6, 18))

        ctk.CTkLabel(body, text="Chave API Anthropic (opcional):",
                     font=ctk.CTkFont(size=12), anchor="w").pack(fill="x", pady=(0, 4))

        self._key_var = tk.StringVar()
        ctk.CTkEntry(body, textvariable=self._key_var, height=34,
                     placeholder_text="sk-ant-...",
                     font=ctk.CTkFont(family="Calibri", size=12), show="*"
                     ).pack(fill="x")

        self._status = ctk.CTkLabel(body, text="", font=ctk.CTkFont(size=11), text_color="#888")
        self._status.pack(pady=(6, 0), anchor="w")

        ftr = ctk.CTkFrame(self, fg_color="#f5f5f5", corner_radius=0, height=56)
        ftr.grid(row=2, column=0, sticky="ew")
        ftr.grid_propagate(False)
        ctk.CTkFrame(ftr, fg_color="#e0e0e0", height=1).pack(fill="x", side="top")
        ctk.CTkButton(ftr, text="Pular por agora", width=130, height=34,
                      fg_color="#e5e5e5", text_color="#666", hover_color="#d5d5d5",
                      font=ctk.CTkFont(size=11),
                      command=self._skip).pack(side="left", padx=16, pady=10)
        ctk.CTkButton(ftr, text="Salvar e continuar", width=160, height=34,
                      fg_color=TEAL, hover_color=TEAL_DARK, text_color="white",
                      font=ctk.CTkFont(family="Calibri", size=12, weight="bold"),
                      command=self._save).pack(side="right", padx=16, pady=10)

    def _save(self):
        key = self._key_var.get().strip()
        _save_config({"api_key": key, "setup_seen": True})
        self._status.configure(text="✓ Salvo!", text_color="#059669")
        self.after(700, self.destroy)

    def _skip(self):
        _save_config({"setup_seen": True})
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    init_db()
    app = TaskApp()
    cfg = _load_config()
    if not cfg.get("setup_seen"):
        app.after(600, lambda: FirstRunSetupDialog(app))
    app.mainloop()
