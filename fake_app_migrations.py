"""Fake-apply initial migrations for books, borrowing, core, reviews so Django
knows the tables exist and doesn't try to re-create them.
"""
import sqlite3
from pathlib import Path
import datetime

DB_PATH = Path(__file__).resolve().parent / 'db.sqlite3'

MIGRATIONS = [
    ('books', '0001_initial'),
    ('books', '0002_initial'),
    ('borrowing', '0001_initial'),
    ('borrowing', '0002_initial'),
    ('core', '0001_initial'),
    ('core', '0002_initial'),
    ('reviews', '0001_initial'),
    ('reviews', '0002_initial'),
]

def fake_apply():
    if not DB_PATH.exists():
        print('Database file not found:', DB_PATH)
        return 2
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    for app, name in MIGRATIONS:
        cur.execute(
            "SELECT 1 FROM django_migrations WHERE app=? AND name=?",
            (app, name)
        )
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, ?)",
                (app, name, now)
            )
            print(f"Fake-applied: {app}.{name}")
        else:
            print(f"Already recorded: {app}.{name}")
    conn.commit()
    conn.close()
    return 0

if __name__ == '__main__':
    raise SystemExit(fake_apply())
