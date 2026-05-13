"""Drop admin-created tables that currently exist but are not recorded in django_migrations.
This avoids errors when re-applying admin migrations.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'db.sqlite3'

TABLES_TO_DROP = ('django_admin_log',)

def drop_tables():
    if not DB_PATH.exists():
        print('Database file not found:', DB_PATH)
        return 2
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for t in TABLES_TO_DROP:
        try:
            cur.execute(f"DROP TABLE IF EXISTS {t}")
            print(f'Dropped table if existed: {t}')
        except Exception as e:
            print('Error dropping', t, e)
    conn.commit()
    conn.close()
    return 0

if __name__ == '__main__':
    raise SystemExit(drop_tables())
