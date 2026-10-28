import sqlite3, time
from pathlib import Path

db = Path(__file__).with_name("telemetry.db")
conn = sqlite3.connect(db)

queries = {
    "1. Readings per machine":
        "SELECT machine, COUNT(*) AS n FROM readings GROUP BY machine",
    "2. Peak vibration per machine":
        "SELECT machine, MAX(vib_rms) AS peak_vib FROM readings GROUP BY machine",
    "3. Readings above 2.0 alarm":
        "SELECT COUNT(*) FROM readings WHERE vib_rms > 2.0",
}

for name, sql in queries.items():
    t0 = time.perf_counter()
    rows = conn.execute(sql).fetchall()
    ms = (time.perf_counter() - t0) * 1000
    print(f"{name}  ({ms:.1f} ms)")
    for r in rows:
        print("   ", r)