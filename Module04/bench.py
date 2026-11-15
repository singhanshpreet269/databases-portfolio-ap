import sqlite3, time, shutil

def run(db, drop_trigger):
    shutil.copy("Module04/edge.db", db)
    con = sqlite3.connect(db)
    con.execute("PRAGMA foreign_keys = ON")
    if drop_trigger:
        con.execute("DROP TRIGGER trg_vib_alarm")
    rows = [(2, f"2027-01-01 {i//3600:02d}:{i//60%60:02d}:{i%60:02d}", 2.5, 1)
            for i in range(10_000)]
    t = time.perf_counter()
    with con:
        con.executemany(
            "INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (?,?,?,?)", rows)
    dt = time.perf_counter() - t
    con.close()
    return dt

for _ in range(3):
    print("with trigger   :", round(run("Module04/bench_a.db", False), 4))
    print("without trigger:", round(run("Module04/bench_b.db", True), 4))
