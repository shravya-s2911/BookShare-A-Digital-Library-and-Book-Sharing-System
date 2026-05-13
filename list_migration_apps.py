import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'db.sqlite3'

def list_apps():
    if not DB_PATH.exists():
        print('Database not found:', DB_PATH)
        return 2
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT app, name, applied FROM django_migrations ORDER BY applied DESC")
    rows = cur.fetchall()
    apps = {}
    for app, name, applied in rows:
        apps.setdefault(app, []).append((name, applied))
    for app, items in apps.items():
        print(app, len(items))
        for name, applied in items[:5]:
            print('  ', name, applied)
    return 0

if __name__ == '__main__':
    raise SystemExit(list_apps())
