"""Local storage for Stage Ladder: one SQLite file, no network.

Multi-user: every account has its own profile and its own runs.
"""
import hashlib
import hmac
import json
import os
import re
import sqlite3
import threading
from datetime import datetime

_lock = threading.RLock()
_con = None

PROFILE_DEFAULTS = {
    "alias": "",
    "event_name": "",
    "event_date": "",
    "filler_goal": 6.0,
    "tone": "Gentle",
    "never_say": "",
    "comfort": 1,
}

USERNAME_RE = re.compile(r"^[a-z0-9._-]{3,30}$")
MIN_PASSWORD = 4

HERE = os.path.dirname(os.path.abspath(__file__))


def init(path="stage_ladder.db"):
    """Open (or create) the local database. Relative paths live next to the app, not the terminal folder."""
    global _con
    if not os.path.isabs(path):
        path = os.path.join(HERE, path)
    _con = sqlite3.connect(path, check_same_thread=False)
    _con.row_factory = sqlite3.Row
    with _lock:
        _con.execute(
            """CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created TEXT, topic TEXT, rung INTEGER, duration REAL,
                words INTEGER, wpm INTEGER, fillers INTEGER,
                fillers_per_min REAL, longest_pause REAL,
                feedback TEXT, coach_source TEXT, questions TEXT, detail TEXT)"""
        )
        _con.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                pw_hash TEXT, pw_salt TEXT, created TEXT)"""
        )
        _con.execute(
            """CREATE TABLE IF NOT EXISTS profiles (
                user_id INTEGER PRIMARY KEY,
                alias TEXT, event_name TEXT, event_date TEXT,
                filler_goal REAL, tone TEXT, never_say TEXT, comfort INTEGER)"""
        )
        _con.execute("DELETE FROM runs WHERE coach_source = 'demo'")
        if "user_id" not in {r["name"] for r in _con.execute("PRAGMA table_info(runs)")}:
            _con.execute("ALTER TABLE runs ADD COLUMN user_id INTEGER")
        _con.execute("CREATE INDEX IF NOT EXISTS runs_user ON runs(user_id)")
        _migrate_single_user()
        _con.commit()


def _migrate_single_user():
    """Older versions had one profile (table 'profile') and one optional PIN. Keep that data as an account."""
    has_old = _con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='profile'").fetchone()
    if not has_old or _con.execute("SELECT 1 FROM users LIMIT 1").fetchone():
        return
    old = _con.execute("SELECT * FROM profile WHERE id = 1").fetchone()
    if not old:
        return
    cols = old.keys()
    base = re.sub(r"[^a-z0-9._-]", "", (old["alias"] or "").lower())[:30]
    username = base if len(base) >= 3 else "player1"
    pw_hash = old["pin_hash"] if "pin_hash" in cols else None
    pw_salt = old["pin_salt"] if "pin_salt" in cols else None
    cur = _con.execute("INSERT INTO users (username, pw_hash, pw_salt, created) VALUES (?,?,?,?)",
                       (username, pw_hash, pw_salt, datetime.now().isoformat(timespec="seconds")))
    uid = cur.lastrowid
    _con.execute(
        """INSERT INTO profiles (user_id, alias, event_name, event_date, filler_goal, tone, never_say, comfort)
           VALUES (?,?,?,?,?,?,?,?)""",
        (uid, old["alias"], old["event_name"], old["event_date"], old["filler_goal"],
         old["tone"], old["never_say"], old["comfort"]))
    _con.execute("UPDATE runs SET user_id = ? WHERE user_id IS NULL", (uid,))


# ---------- accounts ----------
def _hash(pw, salt):
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 150_000).hex()


def norm_username(name):
    return (name or "").strip().lower()


def valid_username(name):
    return bool(USERNAME_RE.match(norm_username(name)))


def username_taken(name):
    with _lock:
        return _con.execute("SELECT 1 FROM users WHERE username = ?", (norm_username(name),)).fetchone() is not None


def create_user(username, password):
    """Create an account and return its id. The caller has already validated the inputs."""
    salt = os.urandom(16)
    with _lock:
        cur = _con.execute("INSERT INTO users (username, pw_hash, pw_salt, created) VALUES (?,?,?,?)",
                           (norm_username(username), _hash(password, salt), salt.hex(),
                            datetime.now().isoformat(timespec="seconds")))
        _con.commit()
        return cur.lastrowid


def check_login(username, password):
    """Return the user id when username and password match, otherwise None."""
    with _lock:
        row = _con.execute("SELECT id, pw_hash, pw_salt FROM users WHERE username = ?",
                           (norm_username(username),)).fetchone()
    if not row:
        _hash(password or "", b"\0" * 16)  # same cost whether or not the user exists
        return None
    if not row["pw_hash"]:  # account migrated from the old single-user version that had no PIN
        return row["id"] if not password else None
    ok = hmac.compare_digest(row["pw_hash"], _hash(password or "", bytes.fromhex(row["pw_salt"])))
    return row["id"] if ok else None


def set_password(uid, password):
    salt = os.urandom(16)
    with _lock:
        _con.execute("UPDATE users SET pw_hash = ?, pw_salt = ? WHERE id = ?", (_hash(password, salt), salt.hex(), uid))
        _con.commit()


def get_username(uid):
    with _lock:
        row = _con.execute("SELECT username FROM users WHERE id = ?", (uid,)).fetchone()
    return row["username"] if row else ""


def user_exists(uid):
    with _lock:
        return uid is not None and _con.execute("SELECT 1 FROM users WHERE id = ?", (uid,)).fetchone() is not None


def delete_user(uid):
    """Remove one account with its profile and runs. Other users are untouched."""
    with _lock:
        _con.execute("DELETE FROM runs WHERE user_id = ?", (uid,))
        _con.execute("DELETE FROM profiles WHERE user_id = ?", (uid,))
        _con.execute("DELETE FROM users WHERE id = ?", (uid,))
        _con.commit()


# ---------- profile (per user) ----------
def get_profile(uid):
    with _lock:
        row = _con.execute("SELECT * FROM profiles WHERE user_id = ?", (uid,)).fetchone()
    p = dict(PROFILE_DEFAULTS)
    if row:
        p.update({k: row[k] for k in PROFILE_DEFAULTS if row[k] is not None})
    return p


def save_profile(uid, **fields):
    p = get_profile(uid)
    p.update({k: v for k, v in fields.items() if k in PROFILE_DEFAULTS})
    with _lock:
        _con.execute(
            """INSERT INTO profiles (user_id, alias, event_name, event_date, filler_goal, tone, never_say, comfort)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET alias=excluded.alias, event_name=excluded.event_name,
               event_date=excluded.event_date, filler_goal=excluded.filler_goal, tone=excluded.tone,
               never_say=excluded.never_say, comfort=excluded.comfort""",
            (uid, p["alias"], p["event_name"], p["event_date"], p["filler_goal"],
             p["tone"], p["never_say"], p["comfort"]),
        )
        _con.commit()
    return p


# ---------- runs (per user) ----------
def add_run(uid, topic, rung, m, feedback, source, questions):
    with _lock:
        cur = _con.execute(
            """INSERT INTO runs (user_id, created, topic, rung, duration, words, wpm, fillers,
               fillers_per_min, longest_pause, feedback, coach_source, questions, detail)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (uid, datetime.now().isoformat(timespec="seconds"), topic, rung, m["duration"],
             m["words"], m["wpm"], m["fillers"], m["fillers_per_min"], m["longest_pause"],
             feedback, source, json.dumps(questions), json.dumps(m)),
        )
        _con.commit()
        return cur.lastrowid


def list_runs(uid):
    with _lock:
        rows = _con.execute("SELECT * FROM runs WHERE user_id = ? ORDER BY id", (uid,)).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["questions"] = json.loads(d["questions"] or "[]")
        d["detail"] = json.loads(d["detail"] or "{}")
        out.append(d)
    return out
