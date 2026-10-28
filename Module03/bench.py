import sqlite3, statistics, time
from pathlib import Path

DB = Path(__file__).with_name("warehouse.db")
RUNS, BATCH = 5, 200
QUERIES = {
 "dashboard": ("""SELECT c.city, COUNT(DISTINCT c.customer_id), SUM(ol.qty*p.price) AS revenue
   FROM customer c JOIN orders o ON o.customer_id=c.customer_id
   JOIN order_line ol ON ol.order_id=o.order_id JOIN product p ON p.product_id=ol.product_id
   WHERE o.ordered_on >= '2025-01-01' AND o.ordered_on < '2026-01-01'
   GROUP BY c.city ORDER BY revenue DESC""", False),
 "single_day": ("""SELECT o.order_id, o.ordered_on, c.name FROM orders o
   JOIN customer c ON c.customer_id=o.customer_id WHERE o.ordered_on='2026-02-14'""", True),
 "product_filter": ("SELECT COUNT(*) FROM order_line WHERE product_id=42", True),
 "function_wrapped": ("""SELECT o.order_id, o.ordered_on, c.name FROM orders o
   JOIN customer c ON c.customer_id=o.customer_id WHERE date(o.ordered_on)='2026-02-14'""", True),
}
IDX = {
 "ix_orders_ordered_on": "CREATE INDEX ix_orders_ordered_on ON orders(ordered_on)",
 "ix_orderline_order": "CREATE INDEX ix_orderline_order ON order_line(order_id)",
 "ix_orderline_product": "CREATE INDEX ix_orderline_product ON order_line(product_id)",
}
CONFIGS = [("baseline", []), ("only ordered_on", ["ix_orders_ordered_on"]),
 ("only orderline_order", ["ix_orderline_order"]), ("only orderline_product", ["ix_orderline_product"]),
 ("cumul 1", ["ix_orders_ordered_on"]), ("cumul 2", ["ix_orders_ordered_on", "ix_orderline_order"]),
 ("cumul 3", list(IDX))]

conn = sqlite3.connect(DB)
def reset(ix):
    for n in IDX: conn.execute(f"DROP INDEX IF EXISTS {n}")
    for n in ix: conn.execute(IDX[n])
    conn.commit()
def t_ms(sql, fast):
    s = []
    for _ in range(RUNS):
        t = time.perf_counter()
        for _ in range(BATCH if fast else 1): conn.execute(sql).fetchall()
        s.append((time.perf_counter()-t)*1000/(BATCH if fast else 1))
    return statistics.median(s)

for label, ix in CONFIGS:
    reset(ix); print("\n##", label)
    for q, (sql, fast) in QUERIES.items():
        plan = [r[3] for r in conn.execute("EXPLAIN QUERY PLAN "+sql)]
        print(f"{q}: {t_ms(sql, fast):.3f} ms | {' / '.join(plan)}")
reset([])