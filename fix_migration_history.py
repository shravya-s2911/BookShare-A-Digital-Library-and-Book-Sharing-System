"""Fix migration history by inserting users initial migration entry into sqlite django_migrations table.

Use only when Django reports an InconsistentMigrationHistory due to admin applied before users.
"""
import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path(__file__).resolve().parent / 'db.sqlite3'

def ensure_users_migration():
    if not DB_PATH.exists():
        print('Database file not found:', DB_PATH)
        return 2

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if users 0001_initial exists
    cur.execute("SELECT COUNT(1) FROM django_migrations WHERE app=? AND name=?", ('users', '0001_initial'))
    if cur.fetchone()[0] > 0:
        print('users.0001_initial already recorded in django_migrations')
        conn.close()
        return 0

    # Insert record
    applied = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    cur.execute("INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, ?)", ('users', '0001_initial', applied))
    conn.commit()
    conn.close()
    print('Inserted users.0001_initial into django_migrations')
    return 0


if __name__ == '__main__':
    raise SystemExit(ensure_users_migration())
