import sqlite3, statistics, time
from pathlib import Path

DB = Path(__file__).with_name("warehouse.db")
RUNS = 3
QUERIES = {
 "group_by": """SELECT c.customer_id, c.name, COUNT(*) AS late_orders
   FROM orders o JOIN customer c ON c.customer_id = o.customer_id
   WHERE o.status = 'late'
   GROUP BY c.customer_id, c.name
   ORDER BY late_orders DESC, c.customer_id""",
 "subquery": """SELECT c.customer_id, c.name,
   (SELECT COUNT(*) FROM orders o
     WHERE o.customer_id = c.customer_id AND o.status = 'late') AS late_orders
   FROM customer c
   WHERE EXISTS (SELECT 1 FROM orders o
                  WHERE o.customer_id = c.customer_id AND o.status = 'late')
   ORDER BY late_orders DESC, c.customer_id""",
 "window": """SELECT DISTINCT c.customer_id, c.name,
   COUNT(*) OVER (PARTITION BY c.customer_id) AS late_orders
   FROM orders o JOIN customer c ON c.customer_id = o.customer_id
   WHERE o.status = 'late'
   ORDER BY late_orders DESC, c.customer_id""",
}

conn = sqlite3.connect(DB)

def run(label):
    print(f"\n=== {label} ===")
    results = {}
    for name, sql in QUERIES.items():
        plan = [r[3] for r in conn.execute("EXPLAIN QUERY PLAN " + sql)]
        times = []
        for _ in range(RUNS):
            t = time.perf_counter()
            rows = conn.execute(sql).fetchall()
            times.append((time.perf_counter() - t) * 1000)
        results[name] = rows
        print(f"{name}: median {statistics.median(times):.1f} ms, {len(rows)} rows")
        print("   plan:", " / ".join(plan))
    same = results["group_by"] == results["subquery"] == results["window"]
    print("all three return identical rows:", same)

conn.execute("DROP INDEX IF EXISTS ix_orders_cust_status")
run("no extra index")
conn.execute("CREATE INDEX ix_orders_cust_status ON orders(customer_id, status)")
run("with ix_orders_cust_status ON orders(customer_id, status)")
conn.execute("DROP INDEX ix_orders_cust_status")
conn.commit()