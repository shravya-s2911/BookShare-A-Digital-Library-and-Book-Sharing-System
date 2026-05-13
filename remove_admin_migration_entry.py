"""Remove the admin.0001_initial entry from django_migrations.
Use this if admin was applied before users and you want to re-run migrations in correct order.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'db.sqlite3'

def remove_entry():
    if not DB_PATH.exists():
        print('Database file not found:', DB_PATH)
        return 2
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM django_migrations WHERE app=? AND name=?", ('admin', '0001_initial'))
    conn.commit()
    conn.close()
    print('Removed admin.0001_initial entry from django_migrations (if it existed)')
    return 0

if __name__ == '__main__':
    raise SystemExit(remove_entry())
