"""Remove migration entries for local apps that depend on the custom users app.
This makes it possible to apply the users migrations first, then re-apply these apps.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'db.sqlite3'
APPS_TO_REMOVE = ('books', 'borrowing', 'core', 'reviews', 'admin')

def remove_entries():
    if not DB_PATH.exists():
        print('Database file not found:', DB_PATH)
        return 2
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for app in APPS_TO_REMOVE:
        cur.execute("DELETE FROM django_migrations WHERE app=?", (app,))
        print(f'Removed entries for app: {app}')
    conn.commit()
    conn.close()
    print('Done')
    return 0

if __name__ == '__main__':
    raise SystemExit(remove_entries())
