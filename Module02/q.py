import sqlite3, sys
from pathlib import Path

conn = sqlite3.connect(Path(__file__).with_name("legacy.db"))
cur = conn.execute(sys.argv[1])
print([d[0] for d in cur.description])
for row in cur.fetchall():
    print(row)