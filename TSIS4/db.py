"""db.py — PostgreSQL integration via psycopg2."""
import sys
import os

# Must be set before psycopg2 is imported
os.environ["PGCLIENTENCODING"] = "UTF8"
os.environ["LC_ALL"]           = "C"
os.environ["LC_MESSAGES"]      = "C"
os.environ["LANG"]             = "C"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2
import psycopg2.extensions

# Monkey-patch psycopg2 string decoding to handle CP1251 Windows locale
_original_decode = None
try:
    import psycopg2.extensions as _ext

    def _cp1251_safe_decode(s, cur):
        if isinstance(s, bytes):
            try:
                return s.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    return s.decode("cp1251", errors="replace")
                except Exception:
                    return s.decode("ascii", errors="replace")
        return s

    psycopg2.extensions.register_type(
        psycopg2.extensions.new_type((25,), "TEXT", _cp1251_safe_decode)
    )
except Exception:
    pass


DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "snake_game",
    "user":     "postgres",
    "password": "gele123",
    "options":  "-c lc_messages=C -c client_encoding=UTF8",
}


def _safe_str(e) -> str:
    """Safely convert exception to string regardless of encoding."""
    parts = []
    for arg in e.args:
        if isinstance(arg, bytes):
            try:
                parts.append(arg.decode("cp1251", errors="replace"))
            except Exception:
                parts.append(repr(arg))
        elif isinstance(arg, str):
            try:
                # Python may have misread CP1251 bytes as latin-1
                parts.append(arg.encode("latin-1").decode("cp1251", errors="replace"))
            except Exception:
                parts.append(arg)
        else:
            parts.append(str(arg))
    return " | ".join(parts) if parts else "unknown error"


def get_connection():
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            options=DB_CONFIG["options"],
        )
        conn.set_client_encoding("UTF8")
        return conn
    except psycopg2.Error as e:
        raise Exception(_safe_str(e))
    except Exception as e:
        raise Exception(_safe_str(e))


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""


def init_db():
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute(SCHEMA_SQL)
        conn.commit()
        cur.close()
        conn.close()
        print("[DB] Connected and schema ready.")
        return True
    except Exception as e:
        print(f"[DB] init_db failed: {_safe_str(e)}")
        return False


def get_or_create_player(cur, username):
    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO players (username) VALUES (%s) RETURNING id",
        (username,)
    )
    row = cur.fetchone()
    return row[0] if row else None


def save_session(username, score, level):
    try:
        conn = get_connection()
        cur  = conn.cursor()
        pid  = get_or_create_player(cur, username)
        if pid is None:
            conn.rollback(); cur.close(); conn.close()
            return False
        cur.execute(
            "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
            (pid, score, level)
        )
        conn.commit()
        cur.close(); conn.close()
        print(f"[DB] Saved: {username} score={score} level={level}")
        return True
    except Exception as e:
        print(f"[DB] save_session failed: {_safe_str(e)}")
        return False


def get_personal_best(username):
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT COALESCE(MAX(gs.score), 0)
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            WHERE p.username = %s
        """, (username,))
        val = cur.fetchone()[0]
        cur.close(); conn.close()
        return int(val)
    except Exception as e:
        print(f"[DB] get_personal_best failed: {_safe_str(e)}")
        return 0


def get_leaderboard(limit=10):
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT p.username, gs.score, gs.level_reached,
                   TO_CHAR(gs.played_at, 'YYYY-MM-DD') as date
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            ORDER BY gs.score DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close(); conn.close()
        return [{"username": r[0], "score": r[1], "level": r[2], "date": r[3]}
                for r in rows]
    except Exception as e:
        print(f"[DB] get_leaderboard failed: {_safe_str(e)}")
        return []