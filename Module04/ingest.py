import csv, sqlite3, sys

UPSERT = """
INSERT INTO reading(sensor_id, ts, value, interval_s)
VALUES (:sensor_id, :ts, :value, :interval_s)
ON CONFLICT(sensor_id, ts) DO UPDATE SET value = excluded.value
"""

def main(db_path, csv_path):
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON")
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    with con:
        con.executemany(UPSERT, rows)
    n = con.execute("SELECT COUNT(*) FROM reading").fetchone()[0]
    print(f"rows in reading: {n}")
    con.close()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
