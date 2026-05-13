"""Remove all entries for the 'admin' app from django_migrations.
This lets Django re-apply admin migrations after users migrations run.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'db.sqlite3'

def remove_entries():
    if not DB_PATH.exists():
        print('Database file not found:', DB_PATH)
        return 2
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM django_migrations WHERE app=?", ('admin',))
    conn.commit()
    conn.close()
    print('Removed all admin entries from django_migrations (if any existed)')
    return 0

if __name__ == '__main__':
    raise SystemExit(remove_entries())
