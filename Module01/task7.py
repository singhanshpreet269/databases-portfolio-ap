import sqlite3

conn = sqlite3.connect("Module01/telemetry.db")

good = """
SELECT machine, AVG(spindle_load) AS avg_spindle_load
FROM readings
WHERE time(ts) >= '18:00:00'
GROUP BY machine
ORDER BY avg_spindle_load DESC
"""

sloppy = """
SELECT machine, AVG(spindle_load) AS avg_spindle_load
FROM readings
WHERE ts LIKE '%18%'
GROUP BY machine
ORDER BY avg_spindle_load DESC
"""

whole_night = """
SELECT machine, AVG(spindle_load) AS avg_spindle_load
FROM readings
WHERE time(ts) >= '18:00:00' OR time(ts) < '06:00:00'
GROUP BY machine
ORDER BY avg_spindle_load DESC
"""

def show(title, sql):
    print("\n==", title)
    for row in conn.execute(sql):
        print(row)

show("GENERATED QUERY", good)

print("\n== QUERY PLAN")
for row in conn.execute("EXPLAIN QUERY PLAN " + good):
    print(row)

show("SLOPPY LIKE VERSION", sloppy)
show("WHOLE NIGHT VERSION", whole_night)

print("\n== ROW COUNTS")
print("total rows:", conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0])
print("after 18:00:", conn.execute("SELECT COUNT(*) FROM readings WHERE time(ts) >= '18:00:00'").fetchone()[0])
print("LIKE '%18%':", conn.execute("SELECT COUNT(*) FROM readings WHERE ts LIKE '%18%'").fetchone()[0])