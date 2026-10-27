"""
Creates the MySQL database from .env if it doesn't exist yet.
Run:  python create_db.py
"""
import sys

import pymysql

from app.config import settings

try:
    conn = pymysql.connect(host=settings.db_host, port=settings.db_port, user=settings.db_user,
                           password=settings.db_password, charset="utf8mb4")
except pymysql.err.OperationalError as e:
    code = e.args[0]
    print(f"\n[X] Could not connect to MySQL at {settings.db_host}:{settings.db_port} as '{settings.db_user}'")
    if code == 1045:
        print("    Wrong username or password. Fix DB_USER / DB_PASSWORD in the .env file.")
    elif code in (2003, 2002):
        print("    MySQL server is not running. Start it (Services -> MySQL80 -> Start) and try again.")
    else:
        print(f"    {e}")
    sys.exit(1)

with conn.cursor() as cur:
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{settings.db_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
conn.commit()
conn.close()
print(f"[OK] Database '{settings.db_name}' is ready")