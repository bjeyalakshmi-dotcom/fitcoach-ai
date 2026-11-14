import sqlite3
import json
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id          TEXT PRIMARY KEY,
        name        TEXT,
        age         INTEGER,
        weight_kg   REAL,
        height_cm   REAL,
        goal        TEXT,          -- lose_weight | gain_muscle | maintain
        activity    TEXT,          -- sedentary | light | moderate | active | very_active
        restrictions TEXT,         -- JSON list e.g. ["gluten-free","vegetarian"]
        created_at  TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS plans (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     TEXT,
        week_start  TEXT,
        workout     TEXT,          -- JSON
        meals       TEXT,          -- JSON
        calories    REAL,
        protein_g   REAL,
        carbs_g     REAL,
        fat_g       REAL,
        created_at  TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS workout_logs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     TEXT,
        logged_at   TEXT DEFAULT (datetime('now')),
        exercises   TEXT,          -- JSON list
        duration_min INTEGER,
        skipped     INTEGER DEFAULT 0,
        skip_reason TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS meal_logs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     TEXT,
        logged_at   TEXT DEFAULT (datetime('now')),
        meals       TEXT,          -- JSON list
        total_kcal  REAL,
        protein_g   REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS health_signals (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id       TEXT,
        recorded_at   TEXT DEFAULT (datetime('now')),
        steps         INTEGER,
        heart_rate    REAL,
        sleep_hours   REAL,
        calories_burned REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS agent_memory (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     TEXT,
        agent       TEXT,
        key         TEXT,
        value       TEXT,
        updated_at  TEXT DEFAULT (datetime('now')),
        UNIQUE(user_id, agent, key) ON CONFLICT REPLACE,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS notifications (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     TEXT,
        sent_at     TEXT DEFAULT (datetime('now')),
        message     TEXT,
        type        TEXT           -- nudge | health_alert | plan_update
    );
    """)

    conn.commit()
    conn.close()


# ── CRUD helpers ──────────────────────────────────────────────────────────────

def get_user(user_id: str):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(row) if row else None


def save_user(data: dict):
    with get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO users
            (id, name, age, weight_kg, height_cm, goal, activity, restrictions)
            VALUES (:id,:name,:age,:weight_kg,:height_cm,:goal,:activity,:restrictions)
        """, data)


def get_latest_plan(user_id: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM plans WHERE user_id=? ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        ).fetchone()
        return dict(row) if row else None


def save_plan(user_id: str, plan: dict):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO plans (user_id, week_start, workout, meals, calories, protein_g, carbs_g, fat_g)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            user_id,
            plan["week_start"],
            json.dumps(plan["workout"]),
            json.dumps(plan["meals"]),
            plan["calories"],
            plan["protein_g"],
            plan["carbs_g"],
            plan["fat_g"],
        ))


def save_workout_log(user_id: str, log: dict):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO workout_logs (user_id, exercises, duration_min, skipped, skip_reason)
            VALUES (?,?,?,?,?)
        """, (
            user_id,
            json.dumps(log.get("exercises", [])),
            log.get("duration_min", 0),
            1 if log.get("skipped") else 0,
            log.get("skip_reason", ""),
        ))


def save_meal_log(user_id: str, log: dict):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO meal_logs (user_id, meals, total_kcal, protein_g)
            VALUES (?,?,?,?)
        """, (
            user_id,
            json.dumps(log.get("meals", [])),
            log.get("total_kcal", 0),
            log.get("protein_g", 0),
        ))


def save_health_signal(user_id: str, sig: dict):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO health_signals (user_id, steps, heart_rate, sleep_hours, calories_burned)
            VALUES (?,?,?,?,?)
        """, (user_id, sig.get("steps"), sig.get("heart_rate_bpm"),
              sig.get("sleep_hours"), sig.get("calories_burned")))


def get_recent_logs(user_id: str, days: int = 7):
    with get_conn() as conn:
        workouts = conn.execute("""
            SELECT * FROM workout_logs WHERE user_id=?
            AND logged_at >= datetime('now', ? || ' days')
            ORDER BY logged_at DESC
        """, (user_id, f"-{days}")).fetchall()

        meals = conn.execute("""
            SELECT * FROM meal_logs WHERE user_id=?
            AND logged_at >= datetime('now', ? || ' days')
            ORDER BY logged_at DESC
        """, (user_id, f"-{days}")).fetchall()

        signals = conn.execute("""
            SELECT * FROM health_signals WHERE user_id=?
            AND recorded_at >= datetime('now', ? || ' days')
            ORDER BY recorded_at DESC
        """, (user_id, f"-{days}")).fetchall()

        return {
            "workouts": [dict(r) for r in workouts],
            "meals":    [dict(r) for r in meals],
            "signals":  [dict(r) for r in signals],
        }


def get_memory(user_id: str, agent: str, key: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT value FROM agent_memory WHERE user_id=? AND agent=? AND key=?",
            (user_id, agent, key)
        ).fetchone()
        return json.loads(row["value"]) if row else None


def set_memory(user_id: str, agent: str, key: str, value):
    with get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO agent_memory (user_id, agent, key, value)
            VALUES (?,?,?,?)
        """, (user_id, agent, key, json.dumps(value)))


def save_notification(user_id: str, message: str, ntype: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO notifications (user_id, message, type) VALUES (?,?,?)",
            (user_id, message, ntype)
        )


def count_today_notifications(user_id: str) -> int:
    with get_conn() as conn:
        row = conn.execute("""
            SELECT COUNT(*) as cnt FROM notifications
            WHERE user_id=? AND date(sent_at)=date('now')
        """, (user_id,)).fetchone()
        return row["cnt"]
