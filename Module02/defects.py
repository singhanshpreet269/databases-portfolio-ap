import sqlite3
from pathlib import Path

conn = sqlite3.connect(Path(__file__).with_name("legacy.db"))

defects = {
    "Defect 1: orphan jobs (machine_name not in machine)":
        """SELECT m.job_id, m.machine_name
           FROM maint_job m
           LEFT JOIN machine x ON m.machine_name = x.machine_name
           WHERE x.machine_name IS NULL""",
    "Defect 2: duplicate part_no":
        """SELECT part_no, COUNT(*) AS copies
           FROM part GROUP BY part_no HAVING COUNT(*) > 1""",
    "Defect 3: unit_price is text (text comparison, not numeric)":
        "SELECT part_no, unit_price FROM part WHERE unit_price < '15'",
    "Defect 4: installed is not a date":
        """SELECT machine_name, installed FROM machine
           WHERE installed NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'""",
    "Defect 5: list in a column only joins when it holds one part":
        """SELECT j.job_id, p.description
           FROM maint_job j JOIN part p ON p.part_no = j.parts_used""",
}

for name, sql in defects.items():
    print(name)
    for row in conn.execute(sql).fetchall():
        print("   ", row)
    print()